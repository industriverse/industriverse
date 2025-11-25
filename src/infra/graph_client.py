"""
Graph DB client placeholder for Neo4j.
"""

from __future__ import annotations

import logging
from typing import Any, Dict

from .config import load_graph_config

logger = logging.getLogger(__name__)


class GraphClient:
    def __init__(self, uri: str, user: str | None = None, password: str | None = None):
        self.uri = uri
        self.user = user
        self.password = password

    def upsert(self, node_id: str, metadata: Dict[str, Any]) -> None:
        logger.info("Upserting node %s at %s (stub)", node_id, self.uri)


def get_graph_client() -> GraphClient:
    cfg = load_graph_config()
    return GraphClient(cfg.uri, cfg.user, cfg.password)
