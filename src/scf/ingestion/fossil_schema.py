import hashlib
import json
from typing import Dict, Any, Optional
from pydantic import BaseModel

class Fossil(BaseModel):
    """
    Standardized Physics Fossil Schema.
    Enforces structure and provenance for the Energy Atlas.
    """
    id: str
    source: str
    timestamp: float
    data: Dict[str, Any]
    meta: Dict[str, Any]
    prev_hash: Optional[str] = None
    hash: Optional[str] = None

    def compute_hash(self) -> str:
        """
        Computes the SHA-256 hash of the fossil content (excluding the hash field itself).
        This forms the basis of the ZKP Hash Chain.
        """
        # Create a dictionary of the fields to hash
        payload = self.model_dump(exclude={'hash'})
        # Sort keys for deterministic hashing
        payload_str = json.dumps(payload, sort_keys=True, default=str)
        return hashlib.sha256(payload_str.encode('utf-8')).hexdigest()

    def sign(self):
        """
        Computes and sets the hash for this fossil.
        """
        self.hash = self.compute_hash()
