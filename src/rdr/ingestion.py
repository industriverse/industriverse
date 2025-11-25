"""
RDR ingestion skeleton.

Pipeline (Phase 3):
- enqueue ingest requests
- fetch + store metadata
- run perspective extraction
- embed + cluster
- emit hypotheses and twin updates
"""

from __future__ import annotations

import logging
from typing import Iterable, Optional

from .schemas import IngestRequest, PerspectiveRecord, TrendRecord

logger = logging.getLogger(__name__)


class IngestQueue:
    def __init__(self) -> None:
        self._queue: list[IngestRequest] = []

    def enqueue(self, req: IngestRequest) -> None:
        self._queue.append(req)
        logger.debug("Enqueued ingest request: %s", req)

    def dequeue_batch(self, size: int = 10) -> list[IngestRequest]:
        batch = self._queue[:size]
        self._queue = self._queue[size:]
        return batch


class PerspectiveExtractor:
    def __init__(self, llm=None) -> None:
        self.llm = llm

    def extract(self, text: str) -> dict[str, str]:
        """
        Placeholder: plug in LLM prompt that returns perspectives.
        """
        if not self.llm:
            return {}
        return self.llm.generate_perspectives(text)


class EmbeddingIndexer:
    def __init__(self, vector_client=None, graph_client=None) -> None:
        self.vector = vector_client
        self.graph = graph_client

    def index(self, paper_id: str, embedding: list[float], metadata: dict) -> Optional[str]:
        """
        Placeholder: store embedding and return embedding id.
        """
        if not self.vector:
            return None
        return self.vector.store(paper_id, embedding, metadata)

    def upsert_graph_node(self, node_id: str, metadata: dict) -> None:
        if self.graph:
            self.graph.upsert(node_id, metadata)


def process_batch(
    queue: IngestQueue,
    extractor: PerspectiveExtractor,
    indexer: EmbeddingIndexer,
    fetch_text_fn,
    emit_hypothesis_fn,
    emit_twin_event_fn,
    batch_size: int = 10,
) -> None:
    """
    Pull a batch, process, and emit downstream events.
    """
    for req in queue.dequeue_batch(batch_size):
        text = fetch_text_fn(req.uri)
        perspectives = extractor.extract(text)
        embedding_id = indexer.index(req.uri, [], {"tags": req.tags})
        record = PerspectiveRecord(
            paper_id=req.uri,
            perspectives=perspectives,
            embedding_id=embedding_id,
            cluster_id=None,
            novelty_score=None,
            created_at=None,  # fill with real timestamp in impl
        )
        emit_hypothesis_fn(record)
        emit_twin_event_fn("rdr.node", {"id": req.uri, "label": req.uri, "embedding_id": embedding_id})
