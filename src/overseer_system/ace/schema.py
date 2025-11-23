from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class StepType(str, Enum):
    REASONING = "reasoning"
    TOOL_USE = "tool_use"
    OUTPUT = "output"
    SYSTEM = "system"

class Outcome(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    UNKNOWN = "unknown"

class LogMetrics(BaseModel):
    latency_ms: float = 0.0
    tokens: int = 0
    confidence: float = 0.0
    cost: float = 0.0

class TrajectoryLog(BaseModel):
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    step_type: StepType
    content: str
    context_hash: Optional[str] = None
    outcome: Outcome = Outcome.UNKNOWN
    metrics: LogMetrics = Field(default_factory=LogMetrics)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ContextPlaybookItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    domain: str
    trigger: str
    strategy: str
    source_trace_id: Optional[str] = None
    confidence_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ReflectionPattern(BaseModel):
    type: str # e.g., "failure_mode", "success_strategy"
    description: str
    frequency: float
    suggested_fix: Optional[str] = None
    affected_domains: List[str] = Field(default_factory=list)

class ReflectionSummary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    period_start: datetime
    period_end: datetime
    analyzed_traces_count: int
    identified_patterns: List[ReflectionPattern] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
