import time
from dataclasses import dataclass

@dataclass
class BioMetrics:
    timestamp: float
    device_temp_c: float
    user_motion_intensity: float # 0.0 (Sleep) to 1.0 (Running)
    ambient_light_lux: float

class BioThermalMonitor:
    """
    Detects 'Device Fever': High internal heat vs Low external motion.
    This indicates background processing (Surveillance) during user rest.
    """
    def __init__(self):
        self.fever_threshold_c = 35.0 # Above this is 'Hot'
        self.rest_threshold = 0.1     # Below this is 'Still'
        
    def check_for_fever(self, metrics: BioMetrics) -> float:
        """
        Returns a 'Fever Score' (0.0 to 1.0).
        """
        is_hot = metrics.device_temp_c > self.fever_threshold_c
        is_still = metrics.user_motion_intensity < self.rest_threshold
        is_dark = metrics.ambient_light_lux < 10.0 # Likely in pocket or night
        
        if is_hot and is_still:
            print(f"🌡️ [BioThermal] FEVER DETECTED! Temp: {metrics.device_temp_c}C, Motion: {metrics.user_motion_intensity}")
            score = 0.8
            if is_dark:
                print("   🌑 Context: Dark/Night (High Confidence)")
                score += 0.2
            return min(score, 1.0)
            
        return 0.0
