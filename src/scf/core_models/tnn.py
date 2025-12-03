from typing import Any, Dict, List
from src.tnn.predictor import TNNPredictor

class TNNInterface:
    """
    Interface for Thermodynamic Neural Networks in the SCF.
    Wraps the existing TNNPredictor.
    """
    def __init__(self):
        self.predictor = TNNPredictor()

    def simulate(self, code_artifact: Any, steps: int = 10) -> Dict[str, Any]:
        """
        Runs a simulation of the code artifact using the TNN.
        """
        # Extract hypothesis/intent from artifact if possible, or use a default
        hypothesis = getattr(code_artifact, "intent", "generic_optimization")
        
        energy = self.predictor.predict_energy(hypothesis)
        trajectory = self.predictor.predict_trajectory(hypothesis, steps)
        
        return {
            "final_energy": energy,
            "trajectory": trajectory,
            "stability": 1.0 / (energy + 0.1) # Inverse energy as stability proxy
        }
