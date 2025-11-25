"""
Telemetry models for Shadow Twin contract.
"""

from typing import Any, Dict, Optional
from pydantic import BaseModel

class CapsuleStatusEvent(BaseModel):
    uri: str
    utid: Optional[str] = None
    status: str  # resolving|executing|executed|error
    latency_ms: float = 0.0
    resolution_source: str = "local"

class CapsuleProofEvent(BaseModel):
    uri: str
    utid: str
    proof_hash: str
    entropy_delta: float
    timestamp: float

class CapsuleCreditFlowEvent(BaseModel):
    uri: str
    utid: str
    execution_cost: float
    author_split: float = 0.0
    executor_split: float = 0.0
    mesh_split: float = 0.0
    balance_after: float = 0.0

class RDRNodeEvent(BaseModel):
    id: str
    label: str
    uri: Optional[str] = None
    embedding_id: Optional[str] = None
    cluster_id: Optional[str] = None
    novelty_score: float = 0.0

class RDREdgeEvent(BaseModel):
    source: str
    target: str
    type: str
    weight: float = 1.0

class TelemetryEnvelope(BaseModel):
    topic: str
    payload: Dict[str, Any]
    timestamp: float
