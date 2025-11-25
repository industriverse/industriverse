from typing import Dict, Optional
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class PRINScore(BaseModel):
    value: float
    components: Dict[str, float]
    verdict: str  # APPROVE, REVIEW, REJECT

class PRINValidator:
    """
    Physical Reality Integration (PRIN) Validator.
    Validates hypotheses using the canonical formula:
    PRIN = alpha * P_physics + beta * P_coherence + gamma * P_novelty
    """
    
    def __init__(self, alpha: float = 0.55, beta: float = 0.30, gamma: float = 0.15,
                 approve_threshold: float = 0.75, review_threshold: float = 0.60):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.approve_threshold = approve_threshold
        self.review_threshold = review_threshold
        
        # Validate weights sum to approx 1.0
        total = alpha + beta + gamma
        if abs(total - 1.0) > 0.01:
            logger.warning(f"PRIN weights do not sum to 1.0 (sum={total})")

    def validate(self, p_physics: float, p_coherence: float, p_novelty: float) -> PRINScore:
        """
        Calculate PRIN score and determine verdict.
        
        Args:
            p_physics: Probability under energy prior (0.0 - 1.0)
            p_coherence: Agent-rated internal model confidence (0.0 - 1.0)
            p_novelty: Novelty score (0.0 - 1.0)
            
        Returns:
            PRINScore object containing the result.
        """
        prin_value = (self.alpha * p_physics) + (self.beta * p_coherence) + (self.gamma * p_novelty)
        
        if prin_value >= self.approve_threshold:
            verdict = "APPROVE"
        elif prin_value >= self.review_threshold:
            verdict = "REVIEW"
        else:
            verdict = "REJECT"
            
        return PRINScore(
            value=round(prin_value, 4),
            components={
                "P_physics": p_physics,
                "P_coherence": p_coherence,
                "P_novelty": p_novelty
            },
            verdict=verdict
        )

    @classmethod
    def from_config(cls, config: 'PRINConfig') -> 'PRINValidator': # type: ignore
        """Factory method to create validator from a configuration object."""
        return cls(
            alpha=config.alpha,
            beta=config.beta,
            gamma=config.gamma,
            approve_threshold=config.approve_threshold,
            review_threshold=config.review_threshold
        )
