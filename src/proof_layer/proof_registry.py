import json
import os
import logging
from typing import Optional, List
from datetime import datetime
from .proof_schema import CapsuleProof

logger = logging.getLogger(__name__)

class ProofRegistry:
    """
    Registry for storing and retrieving Capsule Proofs.
    Currently backed by a local JSONL file, scalable to SQL/NoSQL.
    """
    
    def __init__(self, storage_path: str = "data/proofs.jsonl"):
        self.storage_path = storage_path
        self._ensure_storage()

    def _ensure_storage(self):
        directory = os.path.dirname(self.storage_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)

    def register_proof(self, proof: CapsuleProof) -> str:
        """
        Register a proof in the registry.
        Returns the proof_id.
        """
        # Serialize with pydantic
        # Note: using json() for Pydantic v1 compatibility, or model_dump_json for v2
        try:
            data = proof.json()
        except AttributeError:
            data = proof.model_dump_json()
            
        with open(self.storage_path, "a") as f:
            f.write(data + "\n")
            
        logger.info(f"Registered proof: {proof.proof_id}")
        return proof.proof_id

    def get_proof(self, proof_id: str) -> Optional[CapsuleProof]:
        """
        Retrieve a proof by ID. (Inefficient linear scan for now)
        """
        if not os.path.exists(self.storage_path):
            return None
            
        with open(self.storage_path, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if data.get("proof_id") == proof_id:
                        return CapsuleProof(**data)
                except Exception:
                    continue
        return None
