"""
Schemas and data classes for RDR ingestion pipeline (Phase 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class IngestRequest:
    source: str  # e.g., arxiv, client-upload
    uri: str
    tags: List[str]
    priority: int = 0


@dataclass
class PerspectiveRecord:
    paper_id: str
    perspectives: Dict[str, str]
    embedding_id: Optional[str]
    cluster_id: Optional[str]
    novelty_score: Optional[float]
    created_at: datetime


@dataclass
class TrendRecord:
    window_start: datetime
    window_end: datetime
    cluster_id: str
    delta: float
    summary: str
