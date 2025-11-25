import random
from typing import List, Deque
from collections import deque
from datetime import datetime, timedelta
from .schema import TelemetryVector, PredictionResult

class NVPPredictor:
    """
    Next Vector Predictor (NVP) Prototype.
    Currently uses a simple moving average + trend extrapolation for demonstration.
    In production, this would be a Transformer or Diffusion model.
    """
    
    def __init__(self, context_window: int = 10):
        self.context_window = context_window
        self.history: Deque[TelemetryVector] = deque(maxlen=context_window)
        
    def add_observation(self, vector: TelemetryVector):
        self.history.append(vector)
        
    def predict_next(self, horizon_seconds: float = 1.0) -> PredictionResult:
        if len(self.history) < 2:
            # Not enough data, return last or default
            last = self.history[-1] if self.history else None
            if not last:
                raise ValueError("No history to predict from")
            
            return PredictionResult(
                timestamp=datetime.now() + timedelta(seconds=horizon_seconds),
                predicted_vector=last,
                confidence_interval=[0.1] * 5,
                failure_probability=0.0
            )
            
        # Simple linear extrapolation
        last = self.history[-1]
        prev = self.history[-2]
        
        # Calculate gradients
        dt = (last.timestamp - prev.timestamp).total_seconds()
        if dt <= 0: dt = 1.0 # Avoid div by zero
        
        grad_v = (last.voltage - prev.voltage) / dt
        grad_i = (last.current - prev.current) / dt
        grad_t = (last.temperature_c - prev.temperature_c) / dt
        grad_u = (last.utilization - prev.utilization) / dt
        grad_e = (last.error_rate - prev.error_rate) / dt
        
        # Extrapolate
        next_v = last.voltage + grad_v * horizon_seconds
        next_i = last.current + grad_i * horizon_seconds
        next_t = last.temperature_c + grad_t * horizon_seconds
        next_u = max(0.0, min(1.0, last.utilization + grad_u * horizon_seconds))
        next_e = max(0.0, last.error_rate + grad_e * horizon_seconds)
        
        # Add some "thermodynamic noise" (simulated uncertainty)
        noise_scale = 0.01
        next_v += random.gauss(0, noise_scale)
        
        predicted = TelemetryVector(
            timestamp=last.timestamp + timedelta(seconds=horizon_seconds),
            node_id=last.node_id,
            voltage=next_v,
            current=next_i,
            temperature_c=next_t,
            utilization=next_u,
            error_rate=next_e
        )
        
        # Simple failure probability model based on Arrhenius-like temperature scaling
        # P_fail ~ exp(-Ea/kT) -> simplified to sigmoid of T
        # Critical temp assumed around 85C
        t_critical = 85.0
        k = 0.1
        fail_prob = 1.0 / (1.0 + 2.718 ** (-k * (next_t - t_critical)))
        
        return PredictionResult(
            timestamp=predicted.timestamp,
            predicted_vector=predicted,
            confidence_interval=[0.05, 0.05, 0.5, 0.02, 0.01], # Mocked CI
            failure_probability=fail_prob
        )
