import json
import os
import sqlite3
import threading
from dataclasses import asdict
from typing import Any, Dict, List, Optional

from .proof_repository import StoredProof

DEFAULT_DB_PATH = os.environ.get("PROOF_DB_PATH", "data/proofs.db")


class SQLiteProofRepository:
    """
    SQLite-backed proof repository for durability without external services.
    """

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True) if os.path.dirname(db_path) else None
        self._lock = threading.Lock()
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS proofs (
                    proof_id TEXT PRIMARY KEY,
                    utid TEXT,
                    domain TEXT,
                    inputs_json TEXT,
                    outputs_json TEXT,
                    metadata_json TEXT
                )
                """
            )
            conn.commit()

    def store(self, proof: Dict[str, Any]) -> StoredProof:
        item = StoredProof(
            proof_id=proof.get("proof_id"),
            utid=proof.get("utid"),
            domain=proof.get("domain"),
            inputs=proof.get("inputs", {}),
            outputs=proof.get("outputs", {}),
            metadata=proof.get("metadata", {}),
        )
        with self._lock, self._get_conn() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO proofs (proof_id, utid, domain, inputs_json, outputs_json, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    item.proof_id,
                    item.utid,
                    item.domain,
                    json.dumps(item.inputs),
                    json.dumps(item.outputs),
                    json.dumps(item.metadata),
                ),
            )
            conn.commit()
        return item

    def list(
        self,
        utid: Optional[str] = None,
        domain: Optional[str] = None,
        min_energy: Optional[float] = None,
        max_energy: Optional[float] = None,
        proof_hash: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        anchor_chain: Optional[str] = None,
        anchor_tx: Optional[str] = None,
        evidence_contains: Optional[str] = None,
    ) -> List[StoredProof]:
        clauses = []
        params: List[Any] = []
        if utid:
            clauses.append("utid = ?")
            params.append(utid)
        if domain:
            clauses.append("domain = ?")
            params.append(domain)
        if proof_hash:
            clauses.append("json_extract(metadata_json, '$.proof_hash') = ?")
            params.append(proof_hash)
        if status:
            clauses.append("json_extract(metadata_json, '$.status') = ?")
            params.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"SELECT proof_id, utid, domain, inputs_json, outputs_json, metadata_json FROM proofs {where} ORDER BY rowid DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        items: List[StoredProof] = []
        with self._lock, self._get_conn() as conn:
            for row in conn.execute(sql, params):
                inputs = json.loads(row[3])
                outputs = json.loads(row[4])
                metadata = json.loads(row[5])
                if not self._energy_in_range(metadata, min_energy, max_energy):
                    continue
                if anchor_chain is not None:
                    anchors = metadata.get("anchors", [])
                    if not any(a.get("chain") == anchor_chain for a in anchors):
                        continue
                if anchor_tx is not None:
                    anchors = metadata.get("anchors", [])
                    if not any(a.get("tx") == anchor_tx for a in anchors):
                        continue
                if evidence_contains is not None:
                    if evidence_contains not in str(metadata.get("evidence", "")):
                        continue
                items.append(
                    StoredProof(
                        proof_id=row[0],
                        utid=row[1],
                        domain=row[2],
                        inputs=inputs,
                        outputs=outputs,
                        metadata=metadata,
                    )
                )
        return items

    def get(self, proof_id: str) -> Optional[StoredProof]:
        with self._lock, self._get_conn() as conn:
            row = conn.execute(
                "SELECT proof_id, utid, domain, inputs_json, outputs_json, metadata_json FROM proofs WHERE proof_id = ?",
                (proof_id,),
            ).fetchone()
            if not row:
                return None
            return StoredProof(
                proof_id=row[0],
                utid=row[1],
                domain=row[2],
                inputs=json.loads(row[3]),
                outputs=json.loads(row[4]),
                metadata=json.loads(row[5]),
            )

    def update_status(self, proof_id: str, status: str, anchors: Optional[List[Dict[str, Any]]] = None, extra: Optional[Dict[str, Any]] = None):
        anchors = anchors or []
        extra = extra or {}
        with self._lock, self._get_conn() as conn:
            row = conn.execute("SELECT metadata_json FROM proofs WHERE proof_id = ?", (proof_id,)).fetchone()
            if not row:
                return False
            metadata = json.loads(row[0] or "{}")
            metadata["status"] = status
            if anchors:
                metadata["anchors"] = anchors
            metadata.update(extra)
            conn.execute("UPDATE proofs SET metadata_json = ? WHERE proof_id = ?", (json.dumps(metadata), proof_id))
            conn.commit()
        return True

    def lifecycle_transition(self, proof_id: str, target_status: str) -> bool:
        """
        Simple lifecycle: queued -> processing -> verified -> validated
        """
        valid = ["queued", "processing", "verified", "validated"]
        if target_status not in valid:
            return False
        return self.update_status(proof_id, status=target_status)

    def _energy_in_range(self, metadata: Dict[str, Any], min_energy: Optional[float], max_energy: Optional[float]) -> bool:
        if min_energy is None and max_energy is None:
            return True
        energy = metadata.get("energy_joules")
        if energy is None:
            return False
        try:
            energy_val = float(energy)
        except (TypeError, ValueError):
            return False
        if min_energy is not None and energy_val < min_energy:
            return False
        if max_energy is not None and energy_val > max_energy:
            return False
        return True
