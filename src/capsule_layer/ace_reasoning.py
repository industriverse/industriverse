from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import logging
from datetime import datetime

from .capsule_blueprint import CapsuleBlueprint, SafetyBudget
from src.thermodynamic_layer.prin_validator import PRINValidator, PRINScore

logger = logging.getLogger(__name__)

class ACEReflection(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence_score: float
    reasoning_trace: str
    safety_check_passed: bool

class ACEReasoningTemplate:
    """
    Agentic Context Engineering (ACE) Reasoning Template.
    Standardizes the cognitive loop for all 27 Sovereign Capsules.
    """
    
    def __init__(self, capsule: CapsuleBlueprint):
        self.capsule = capsule
        self.prin_validator = PRINValidator.from_config(capsule.prin_config)
        self.safety_budget = capsule.safety_budget
        self.current_energy_usage_j = 0.0
        self.reflection_history: List[ACEReflection] = []

    def check_safety_budget(self, estimated_cost_j: float) -> bool:
        """
        Check if the operation fits within the safety budget.
        Returns True if safe, False if budget exceeded.
        """
        if self.current_energy_usage_j + estimated_cost_j > self.safety_budget.hard_energy_limit_j:
            logger.error(f"HARD BUDGET EXCEEDED for {self.capsule.capsule_id}: "
                         f"{self.current_energy_usage_j + estimated_cost_j} > {self.safety_budget.hard_energy_limit_j}")
            return False
            
        if self.current_energy_usage_j + estimated_cost_j > self.safety_budget.soft_energy_limit_j:
            logger.warning(f"SOFT BUDGET EXCEEDED for {self.capsule.capsule_id}. Proceeding with caution.")
            # In a real system, this might trigger a lower-fidelity mode
            
        return True

    def record_usage(self, cost_j: float):
        """Record energy usage."""
        self.current_energy_usage_j += cost_j

    def validate_hypothesis(self, hypothesis: Dict[str, Any], 
                          p_physics: float, 
                          p_coherence: float, 
                          p_novelty: float) -> PRINScore:
        """
        Validate a generated hypothesis using PRIN.
        """
        score = self.prin_validator.validate(p_physics, p_coherence, p_novelty)
        
        # Log reflection
        reflection = ACEReflection(
            confidence_score=score.value,
            reasoning_trace=f"PRIN validation: {score.verdict} (Physics={p_physics}, Coherence={p_coherence})",
            safety_check_passed=score.verdict != "REJECT"
        )
        self.reflection_history.append(reflection)
        
        return score

    def generate_prompt_context(self) -> str:
        """
        Generate the system prompt context based on the capsule's topology and constraints.
        """
        return f"""
You are the Sovereign Intelligence for Capsule: {self.capsule.name} ({self.capsule.capsule_id}).
Category: {self.capsule.category.value}

Your Physics Topology: {self.capsule.physics_topology}
Governing Equations: {', '.join(self.capsule.domain_equations)}

Safety Constraints:
- Soft Energy Limit: {self.capsule.safety_budget.soft_energy_limit_j} J
- Hard Energy Limit: {self.capsule.safety_budget.hard_energy_limit_j} J

Objective: Generate valid hypotheses that align with the thermodynamic energy prior of this domain.
"""
