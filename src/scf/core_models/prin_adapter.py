from typing import Any, Dict
from src.thermodynamic_layer.prin_validator import PRINValidator

class PRINAdapter:
    """
    Adapts the PRIN (Physical Reality Integration) Validator for the SCF.
    Used by the ReviewEngine to score code/hypotheses.
    """
    def __init__(self):
        self.validator = PRINValidator()

    def validate(self, physics_score: float, coherence_score: float, novelty_score: float) -> Dict[str, Any]:
        """
        Calculates the PRIN score.
        """
        score = self.validator.validate(physics_score, coherence_score, novelty_score)
        return {
            "value": score.value,
            "verdict": score.verdict,
            "components": score.components
        }
