import hashlib
from typing import Dict, Any


def tokenize_proof(proof: Dict[str, Any]) -> str:
    """
    Create a tokenization hash for a proof for exchange/ledger purposes.
    """
    payload = f"{proof.get('proof_id')}|{proof.get('metadata', {}).get('proof_hash')}|{proof.get('utid')}"
    return hashlib.sha256(payload.encode()).hexdigest()
