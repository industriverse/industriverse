"""
Vector DB client placeholder for Qdrant/Weaviate.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from .config import load_vector_config

logger = logging.getLogger(__name__)


class VectorClient:
    def __init__(self, url: str, api_key: str | None = None):
        self.url = url
        self.api_key = api_key

    def store(self, item_id: str, embedding: list[float], metadata: Dict[str, Any]) -> str:
        logger.info("Storing embedding id=%s at %s (stub)", item_id, self.url)
        return item_id

    def query(self, embedding: list[float], top_k: int = 10) -> list[Dict[str, Any]]:
        return []


def get_vector_client() -> VectorClient:
    cfg = load_vector_config()
    return VectorClient(cfg.url, cfg.api_key)
