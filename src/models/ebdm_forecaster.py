import math
import random

class EBDMForecaster:
    """
    Challenge #7: Ultra-Early Failure Prediction.
    Energy-Based Diffusion Model (EBDM) for detecting entropy climbs.
    
    Theory:
    System State x has Energy E(x).
    Probability P(x) ~ exp(-E(x)).
    High Energy = Low Probability = Anomaly/Failure.
    """
    def __init__(self):
        self.baseline_energy = 10.0 # Normal operating energy
        self.failure_threshold = 25.0 # Energy level indicating imminent failure

    def calculate_energy(self, telemetry):
        """
        Calculates the 'Energy' of the current system state.
        Higher Energy = Higher Disorder (Entropy).
        """
        temp = telemetry.get('temperature', 20.0)
        vib = telemetry.get('vibration', 0.0)
        
        # Energy Function E(x)
        # E = k1 * (T - T_ref)^2 + k2 * Vib^2
        energy = 0.05 * (temp - 20.0)**2 + 500.0 * (vib**2)
        
        # Add some stochastic noise (Thermal fluctuations)
        energy += random.uniform(-0.5, 0.5)
        
        return max(0.0, energy)

    def predict_failure_probability(self, energy):
        """
        Converts Energy to Failure Probability using a sigmoid.
        """
        # P(Failure) = 1 / (1 + exp(-(E - Threshold)))
        try:
            prob = 1.0 / (1.0 + math.exp(-(energy - self.failure_threshold)))
        except OverflowError:
            prob = 1.0 if energy > self.failure_threshold else 0.0
            
        return prob

    def analyze(self, telemetry):
        """
        Analyzes telemetry and returns a forecast.
        """
        energy = self.calculate_energy(telemetry)
        prob = self.predict_failure_probability(energy)
        
        status = "NOMINAL"
        if prob > 0.8:
            status = "CRITICAL_FAILURE_IMMINENT"
        elif prob > 0.4:
            status = "WARNING_ENTROPY_CLIMB"
            
        return {
            "energy_score": round(energy, 2),
            "failure_probability": round(prob, 4),
            "status": status
        }
