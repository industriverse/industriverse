from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class IntentType(Enum):
    QUERY = "query"
    COMMAND = "command"
    CREATION = "creation"
    OPTIMIZATION = "optimization"

class UserIntent(BaseModel):
    """Structured intent from UserLM"""
    intent_id: str
    raw_input: str
    intent_type: IntentType
    goal: str
    constraints: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)

class ContextPlaybook(BaseModel):
    """A collection of strategies and context for a specific domain"""
    playbook_id: str
    domain: str
    strategies: List[str]
    anti_patterns: List[str]
    success_rate: float
    last_updated: datetime

class ReflectionLog(BaseModel):
    """Log entry for ACE reflection"""
    log_id: str
    intent_id: str
    playbook_id: Optional[str]
    outcome: str  # "success", "failure", "partial"
    user_satisfaction: float  # 0.0 to 1.0
    reflection_notes: str
    timestamp: datetime

class ACERequest(BaseModel):
    request_id: str
    context: Dict[str, Any]
    intent: str
    utid: Optional[str] = None

class ReflectionResult(BaseModel):
    intent: str
    context_analysis: str
    suggested_strategies: List[str]

class ACEResponse(BaseModel):
    request_id: str
    reflection: ReflectionResult
    selected_playbook: Optional[ContextPlaybook]
    timestamp: datetime
