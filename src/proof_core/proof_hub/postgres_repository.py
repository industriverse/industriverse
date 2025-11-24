import json
import os
from typing import Any, Dict, List, Optional

from .proof_repository import StoredProof


class PostgresProofRepository:
    """
    Postgres-backed proof repository.
    This is a thin layer that expects psycopg2 to be installed and a DSN at PROOF_DB_DSN.
    If psycopg2 is unavailable, construction should be avoided and SQLite used instead.
    """

    def __init__(self, dsn: Optional[str] = None):
        import psycopg2  # type: ignore

        self.dsn = dsn or os.environ.get("PROOF_DB_DSN")
        if not self.dsn:
            raise ValueError("PROOF_DB_DSN must be set for Postgres backend")
        self.conn = psycopg2.connect(self.dsn)
        self._init_db()

    def _init_db(self):
        with self.conn, self.conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS proofs (
                    proof_id TEXT PRIMARY KEY,
                    utid TEXT,
                    domain TEXT,
                    inputs_json JSONB,
                    outputs_json JSONB,
                    metadata_json JSONB
                )
                """
            )

    def store(self, proof: Dict[str, Any]) -> StoredProof:
        item = StoredProof(
            proof_id=proof.get("proof_id"),
            utid=proof.get("utid"),
            domain=proof.get("domain"),
            inputs=proof.get("inputs", {}),
            outputs=proof.get("outputs", {}),
            metadata=proof.get("metadata", {}),
        )
        with self.conn, self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO proofs (proof_id, utid, domain, inputs_json, outputs_json, metadata_json)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (proof_id) DO UPDATE SET
                    utid = EXCLUDED.utid,
                    domain = EXCLUDED.domain,
                    inputs_json = EXCLUDED.inputs_json,
                    outputs_json = EXCLUDED.outputs_json,
                    metadata_json = EXCLUDED.metadata_json
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
    ) -> List[StoredProof]:
        clauses = []
        params: List[Any] = []
        if utid:
            clauses.append("utid = %s")
            params.append(utid)
        if domain:
            clauses.append("domain = %s")
            params.append(domain)
        if proof_hash:
            clauses.append("metadata_json->>'proof_hash' = %s")
            params.append(proof_hash)
        if status:
            clauses.append("metadata_json->>'status' = %s")
            params.append(status)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = f"""
        SELECT proof_id, utid, domain, inputs_json, outputs_json, metadata_json
        FROM proofs {where}
        ORDER BY proof_id DESC
        LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        items: List[StoredProof] = []
        with self.conn, self.conn.cursor() as cur:
            cur.execute(sql, params)
            for row in cur.fetchall():
                inputs = row[3] or {}
                outputs = row[4] or {}
                metadata = row[5] or {}
                if not self._energy_in_range(metadata, min_energy, max_energy):
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
        with self.conn, self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT proof_id, utid, domain, inputs_json, outputs_json, metadata_json
                FROM proofs WHERE proof_id = %s
                """,
                (proof_id,),
            )
            row = cur.fetchone()
            if not row:
                return None
            return StoredProof(
                proof_id=row[0],
                utid=row[1],
                domain=row[2],
                inputs=row[3] or {},
                outputs=row[4] or {},
                metadata=row[5] or {},
            )

    def update_status(self, proof_id: str, status: str, anchors: Optional[List[Dict[str, Any]]] = None):
        anchors = anchors or []
        with self.conn, self.conn.cursor() as cur:
            cur.execute("SELECT metadata_json FROM proofs WHERE proof_id = %s", (proof_id,))
            row = cur.fetchone()
            if not row:
                return False
            metadata = row[0] or {}
            metadata["status"] = status
            if anchors:
                metadata["anchors"] = anchors
            cur.execute(
                "UPDATE proofs SET metadata_json = %s WHERE proof_id = %s",
                (json.dumps(metadata), proof_id),
            )
        return True

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
