from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import enum

class CapsuleCategory(str, enum.Enum):
    HIGH_ENERGY = "Category A - High-energy, dynamic systems"
    FLOW_HEAT = "Category B - Flow, heat, pressure"
    SWARM_LOGISTICS = "Category C - Swarm, logistics, active matter"
    MULTI_PHYSICS = "Category D - High-complexity multi-physics"

class PRINConfig(BaseModel):
    alpha: float = Field(..., description="Weight for P_physics")
    beta: float = Field(..., description="Weight for P_coherence")
    gamma: float = Field(..., description="Weight for P_novelty")
    approve_threshold: float = 0.75
    review_threshold: float = 0.60

class SafetyBudget(BaseModel):
    soft_energy_limit_j: float
    hard_energy_limit_j: float
    entropy_threshold: Optional[float] = None

class MeshRoutingRules(BaseModel):
    nats_request_subject: str
    nats_result_subject: str
    priority_level: str = "normal"
    require_proof_gating: bool = True

class CapsuleBlueprint(BaseModel):
    """
    Canonical Blueprint for a Sovereign Capsule in the Discovery Loop V16.
    Every capsule must implement this contract.
    """
    name: str
    capsule_id: str
    category: CapsuleCategory
    description: str
    
    # Physics & Thermodynamics
    physics_topology: str
    domain_equations: List[str]
    energy_prior_file: str
    
    # Validation & Safety
    prin_config: PRINConfig
    safety_budget: SafetyBudget
    
    # Identity & Proof
    utid_pattern: str
    proof_schema: Dict[str, Any]
    
    # Operations
    mesh_rules: MeshRoutingRules
    agent_roles: Dict[str, str] = Field(
        default_factory=lambda: {
            "UserLM": "Interface & Documentation",
            "RND1": "Design & Optimization",
            "ACE": "Reasoning & Safety",
            "TUMIX": "Consensus & Verification"
        }
    )
    
    inputs: List[str] = Field(default_factory=list)
    outputs: List[str] = Field(default_factory=list)

    @validator('capsule_id')
    def validate_capsule_id(cls, v):
        if not v.startswith('capsule:'):
            raise ValueError('capsule_id must start with "capsule:"')
        return v
