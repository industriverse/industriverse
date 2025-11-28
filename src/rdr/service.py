"""
RDR service skeleton using persistence and infra clients.
"""

from __future__ import annotations

import logging
from typing import Callable, Dict

from .ingestion import IngestQueue, PerspectiveExtractor, EmbeddingIndexer, process_batch
from .persistence import InMemoryRDRStore
from ..infra.db import get_postgres_client
from ..infra.vector_client import get_vector_client
from ..infra.graph_client import get_graph_client

logger = logging.getLogger(__name__)


class RDRService:
    def __init__(self, fetch_text_fn: Callable[[str], str], emit_hypothesis_fn: Callable, emit_twin_event_fn: Callable):
        self.store = InMemoryRDRStore()
        self.queue = IngestQueue()
        self.pg = get_postgres_client()
        self.vector = get_vector_client()
        self.graph = get_graph_client()
        self.extractor = PerspectiveExtractor()
        self.indexer = EmbeddingIndexer(vector_client=self.vector, graph_client=self.graph)
        self.fetch_text_fn = fetch_text_fn
        self.emit_hypothesis_fn = emit_hypothesis_fn
        self.emit_twin_event_fn = emit_twin_event_fn

    def ingest(self, item: Dict) -> None:
        self.store.enqueue_ingest(item)
        self.queue.enqueue(item)

    def run_batch(self, batch_size: int = 10) -> None:
        process_batch(
            queue=self.queue,
            extractor=self.extractor,
            indexer=self.indexer,
            fetch_text_fn=self.fetch_text_fn,
            emit_hypothesis_fn=self.emit_hypothesis_fn,
            emit_twin_event_fn=self.emit_twin_event_fn,
            batch_size=batch_size,
        )
