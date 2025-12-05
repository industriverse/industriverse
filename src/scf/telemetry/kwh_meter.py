import time
import random

class KWhMeter:
    """
    Software-based Energy Meter.
    Estimates power consumption based on load.
    In production, this would query NVIDIA DCGM or IPMI.
    """
    def __init__(self, baseline_power_w: float = 50.0, max_power_w: float = 300.0):
        self.baseline_power = baseline_power_w
        self.max_power = max_power_w
        self.last_check = time.time()
        self.cumulative_kwh = 0.0

    def measure(self, load_percent: float = 0.0) -> float:
        """
        Estimate current power usage (Watts) and update cumulative kWh.
        Args:
            load_percent: 0.0 to 1.0 (e.g. GPU utilization)
        """
        current_time = time.time()
        duration_hours = (current_time - self.last_check) / 3600.0
        
        # Linear interpolation of power based on load
        current_power_w = self.baseline_power + (self.max_power - self.baseline_power) * load_percent
        
        # Add noise to simulate real fluctuations
        current_power_w *= random.uniform(0.95, 1.05)
        
        # Update kWh
        kwh_consumed = (current_power_w * duration_hours) / 1000.0
        self.cumulative_kwh += kwh_consumed
        
        self.last_check = current_time
        return current_power_w

    def get_total_kwh(self) -> float:
        return self.cumulative_kwh
