"""
Qdrant client wrapper.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest


class QdrantWrapper:
    def __init__(self, url: str):
        self.client = QdrantClient(url=url)

    def recreate_collection(self, name: str, size: int, distance: str = "Cosine") -> None:
        self.client.recreate_collection(
            collection_name=name,
            vectors_config=rest.VectorParams(size=size, distance=rest.Distance(distance)),
        )

    def upsert(self, collection: str, vectors: List[List[float]], payloads: List[Dict[str, Any]], ids: Optional[List[str]] = None) -> None:
        self.client.upsert(
            collection_name=collection,
            points=rest.Batch(
                ids=ids,
                vectors=vectors,
                payloads=payloads,
            ),
        )

    def search(self, collection: str, query: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        result = self.client.search(collection_name=collection, query_vector=query, limit=top_k)
        return [hit.dict() for hit in result]
