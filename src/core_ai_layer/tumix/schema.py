from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class AgentRole(Enum):
    CRITIC = "critic"
    OPTIMIST = "optimist"
    REALIST = "realist"
    SECURITY = "security"

class AgentVote(BaseModel):
    """A vote from a single agent in the swarm"""
    agent_id: str
    role: AgentRole
    vote: str  # "approve", "reject", "abstain"
    confidence: float
    reasoning: str
    timestamp: datetime = Field(default_factory=datetime.now)

class ConsensusRequest(BaseModel):
    """Request for swarm consensus"""
    request_id: str
    intent_id: str
    proposal: str
    context: Dict[str, Any] = Field(default_factory=dict)
    required_majority: float = 0.6

class ConsensusResult(BaseModel):
    """Result of the consensus process"""
    request_id: str
    status: str  # "consensus_reached", "dissent", "failed"
    final_decision: str  # "approved", "rejected"
    truth_score: float  # 0.0 to 1.0
    votes: List[AgentVote]
    synthesis: str
    timestamp: datetime = Field(default_factory=datetime.now)
