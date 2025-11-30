import random

class DriftCanceller:
    """
    Challenge #1: Zero-Drift Manufacturing.
    Compensates for thermal and kinematic drift in real-time.
    """
    def __init__(self):
        self.thermal_coefficient = 0.0005 # mm per degree C
        self.correction_vector = [0.0, 0.0, 0.0]

    def estimate_drift(self, telemetry):
        """
        Estimates drift based on sensor readings.
        Input: telemetry dict (temp, vibration, etc.)
        Output: drift_vector [dx, dy, dz]
        """
        temp_delta = telemetry.get("temperature", 20) - 20.0 # Baseline 20C
        vibration = telemetry.get("vibration", 0.0)
        
        # Thermal expansion model
        drift_mag = temp_delta * self.thermal_coefficient
        
        # Vibration noise adds random jitter
        jitter = vibration * 0.1
        
        return [drift_mag + jitter, drift_mag * 0.5 + jitter, jitter]

    def compute_correction(self, drift_vector):
        """
        Computes the inverse vector to cancel drift.
        """
        return [-x for x in drift_vector]

    def apply_correction(self, target_pose, telemetry):
        """
        Adjusts the target pose to account for drift.
        """
        drift = self.estimate_drift(telemetry)
        correction = self.compute_correction(drift)
        
        # Apply correction
        corrected_pose = [
            target_pose[0] + correction[0],
            target_pose[1] + correction[1],
            target_pose[2] + correction[2]
        ]
        
        self.correction_vector = correction
        return corrected_pose, drift
