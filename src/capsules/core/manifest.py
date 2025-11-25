"""
Manifest models for Sovereign Capsules.
Defines the schema for PRIN, Safety, and Routing configurations.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PRINConfig(BaseModel):
    """Directive 04: PRIN Class Definition"""
    physics_class: str
    regularity_score: float
    intelligence_level: str
    narrative_role: str
    domain: str

class SafetyBudget(BaseModel):
    """Directive 06: Runtime Safety Budgets"""
    max_entropy: float
    stability_threshold: float
    compute_budget_flops: float
    thermal_budget_joules: float
    safety_invariants: List[str]
    max_horizon_steps: int

class MeshRouting(BaseModel):
    """Directive 09: Mesh Routing Rules"""
    upstream_capsules: List[str]
    downstream_capsules: List[str]
    entropy_spillover_targets: List[str]
    coupling_factors: Dict[str, float]

class UTIDPattern(BaseModel):
    """Directive 08: UTID Patterns"""
    required_credentials: List[str]
    reputation_min: float
    lineage_signature: str

class CapsuleManifest(BaseModel):
    """Aggregated manifest for a Sovereign Capsule"""
    capsule_id: str
    version: str
    prin: PRINConfig
    safety: SafetyBudget
    routing: MeshRouting
    utid: UTIDPattern
