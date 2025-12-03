from typing import Any, Dict
from src.core.nvp.nvp_predictor import NVPPredictor, TelemetryVector

class NVPAdapter:
    """
    Adapts the NVP (Next Vector Predictor) for use in the SCF.
    Provides short-term telemetry forecasting.
    """
    def __init__(self):
        self.predictor = NVPPredictor()

    def predict_trajectory(self, current_state: Dict[str, Any], horizon: float = 1.0) -> Dict[str, Any]:
        """
        Predicts the next telemetry state vector.
        """
        # Convert dict state to TelemetryVector if needed
        # For now, we assume the predictor handles its own history or we feed it
        # This is a simplified adapter
        try:
            prediction = self.predictor.predict_next(horizon)
            return {
                "predicted_vector": prediction.predicted_vector,
                "failure_prob": prediction.failure_probability
            }
        except ValueError:
            return {"error": "Insufficient history for NVP prediction"}
