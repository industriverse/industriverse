import random
import time

class AletheiaTruthLayer:
    """
    The Truth Layer. Validates Model Predictions against Physical Reality.
    """
    def __init__(self):
        self.drift_threshold = 0.15

    def observe_reality(self, task_id):
        """
        Mocks reading from Sensors/VisualTwin.
        Returns a 'Physics State' vector.
        """
        # In prod, this hits the IoT/Camera API.
        # Mock: Random fluctuations around a baseline.
        return {
            "temperature": 500 + random.uniform(-20, 20),
            "vibration": 0.05 + random.uniform(-0.01, 0.05),
            "visual_entropy": random.uniform(0.1, 0.3)
        }

    def validate(self, task, prediction):
        """
        Compares Prediction vs Reality.
        Returns (is_valid, drift_score, message).
        """
        print(f"[Aletheia] 👁️ Observing Reality for {task['name']}...")
        reality = self.observe_reality(task['id'])
        
        # Calculate Drift (Euclidean distance simplified)
        pred_temp = prediction.get("temperature", 500)
        real_temp = reality["temperature"]
        
        drift = abs(pred_temp - real_temp) / pred_temp
        
        print(f"[Aletheia] Prediction: {pred_temp:.1f} | Reality: {real_temp:.1f} | Drift: {drift:.4f}")

        if drift > self.drift_threshold:
            return False, drift, f"Physics Violation! Drift {drift:.2%} > {self.drift_threshold:.2%}"
        
        return True, drift, "Validated."
