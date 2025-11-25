from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import os
import threading
import json

DEFAULT_STORE_PATH = os.environ.get("PROOF_STORE_PATH", "data/proofs.jsonl")


@dataclass
class StoredProof:
    proof_id: str
    utid: str
    domain: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    metadata: Dict[str, Any]


class ProofRepository:
    """
    Thread-safe proof store with basic filtering.
    Persists to JSONL so data survives process restarts without database setup.
    """

    def __init__(self, store_path: str = DEFAULT_STORE_PATH):
        self._lock = threading.Lock()
        self._items: List[StoredProof] = []
        self.store_path = store_path
        self._ensure_store()
        self._load_existing()

    def store(self, proof: Dict[str, Any]) -> StoredProof:
        item = StoredProof(
            proof_id=proof.get("proof_id"),
            utid=proof.get("utid"),
            domain=proof.get("domain"),
            inputs=proof.get("inputs", {}),
            outputs=proof.get("outputs", {}),
            metadata=proof.get("metadata", {}),
        )
        with self._lock:
            self._items.append(item)
            self._append_to_disk(item)
        return item

    def list(
        self,
        utid: Optional[str] = None,
        domain: Optional[str] = None,
        min_energy: Optional[float] = None,
        max_energy: Optional[float] = None,
        proof_hash: Optional[str] = None,
        status: Optional[str] = None,
        anchor_chain: Optional[str] = None,
        anchor_tx: Optional[str] = None,
        evidence_contains: Optional[str] = None,
        parent_proof_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[StoredProof]:
        with self._lock:
            filtered = [
                item
                for item in self._items
                if (utid is None or item.utid == utid)
                and (domain is None or item.domain == domain)
                and (proof_hash is None or item.metadata.get("proof_hash") == proof_hash)
                and (status is None or item.metadata.get("status") == status)
                and (anchor_chain is None or any(a.get("chain") == anchor_chain for a in item.metadata.get("anchors", [])))
                and (anchor_tx is None or any(a.get("tx") == anchor_tx for a in item.metadata.get("anchors", [])))
                and (evidence_contains is None or (item.metadata.get("evidence") and evidence_contains in str(item.metadata.get("evidence"))))
                and (parent_proof_id is None or item.metadata.get("parent_proof_id") == parent_proof_id)
                and self._energy_in_range(item, min_energy, max_energy)
            ]
            return filtered[offset : offset + limit]

    def update_status(self, proof_id: str, status: str, anchors: Optional[List[Dict[str, Any]]] = None, extra: Optional[Dict[str, Any]] = None) -> bool:
        anchors = anchors or []
        with self._lock:
            for item in self._items:
                if item.proof_id == proof_id:
                    item.metadata["status"] = status
                    if anchors:
                        item.metadata["anchors"] = anchors
                    if extra:
                        item.metadata.update(extra)
                    self._rewrite_store()
                    return True
        return False

    def _rewrite_store(self):
        try:
            with open(self.store_path, "w") as f:
                for item in self._items:
                    f.write(json.dumps(asdict(item)) + "\n")
        except Exception:
            pass

    def _energy_in_range(self, item: StoredProof, min_energy: Optional[float], max_energy: Optional[float]) -> bool:
        if min_energy is None and max_energy is None:
            return True
        energy = item.metadata.get("energy_joules")
        if energy is None:
            return False
        try:
            energy = float(energy)
        except (TypeError, ValueError):
            return False
        if min_energy is not None and energy < min_energy:
            return False
        if max_energy is not None and energy > max_energy:
            return False
        return True

    def _ensure_store(self) -> None:
        os.makedirs(os.path.dirname(self.store_path), exist_ok=True) if os.path.dirname(self.store_path) else None
        if not os.path.exists(self.store_path):
            open(self.store_path, "a").close()

    def _append_to_disk(self, item: StoredProof) -> None:
        try:
            with open(self.store_path, "a") as f:
                f.write(json.dumps(asdict(item)) + "\n")
        except Exception:
            # non-fatal: keep in-memory copy
            pass

    def _load_existing(self) -> None:
        if not os.path.exists(self.store_path):
            return
        try:
            with open(self.store_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    data = json.loads(line)
                    self._items.append(
                        StoredProof(
                            proof_id=data.get("proof_id"),
                            utid=data.get("utid"),
                            domain=data.get("domain"),
                            inputs=data.get("inputs", {}),
                            outputs=data.get("outputs", {}),
                            metadata=data.get("metadata", {}),
                        )
                    )
        except Exception:
            # If loading fails, start fresh but do not crash the app
            self._items = []
