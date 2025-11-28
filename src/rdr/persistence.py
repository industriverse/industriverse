"""
Persistence adapters for RDR (Phase 3 hardening).

Production guidance:
- Replace in-memory stubs with real Postgres/Qdrant/Neo4j clients.
- Add auth/SSL to DB connections.
- Add migrations for schemas documented in docs/rdr-persistence-plan.md.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class InMemoryRDRStore:
    def __init__(self) -> None:
        self.ingest_queue: list[Dict[str, Any]] = []
        self.perspectives: Dict[str, Dict[str, Any]] = {}
        self.trends: list[Dict[str, Any]] = []
        self.hypotheses: list[Dict[str, Any]] = []

    # Ingest
    def enqueue_ingest(self, item: Dict[str, Any]) -> None:
        self.ingest_queue.append(item)
        logger.debug("Enqueued ingest: %s", item.get("uri"))

    def dequeue_ingest(self, batch: int = 10) -> list[Dict[str, Any]]:
        items = self.ingest_queue[:batch]
        self.ingest_queue = self.ingest_queue[batch:]
        return items

    # Perspectives
    def save_perspective(self, paper_id: str, record: Dict[str, Any]) -> None:
        self.perspectives[paper_id] = record

    # Trends
    def save_trend(self, record: Dict[str, Any]) -> None:
        self.trends.append(record)

    # Hypotheses
    def add_hypothesis(self, record: Dict[str, Any]) -> None:
        self.hypotheses.append(record)

    def next_hypothesis(self) -> Optional[Dict[str, Any]]:
        if not self.hypotheses:
            return None
        return self.hypotheses.pop(0)
