from typing import Dict, List
import hashlib


def utid_to_embedding(utid: str) -> List[float]:
    """
    Produce a simple deterministic embedding for a UTID for downstream similarity search.
    This is a placeholder; replace with semantic or learned embeddings later.
    """
    digest = hashlib.sha256(utid.encode()).digest()
    # Map first few bytes into a small vector
    return [b / 255.0 for b in digest[:16]]


def utid_batch_embeddings(utids: List[str]) -> List[List[float]]:
    return [utid_to_embedding(u) for u in utids]
