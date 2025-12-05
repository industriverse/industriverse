from dataclasses import dataclass
from typing import List, Optional
import time

@dataclass
class EntropyEvent:
    event_type: str # 'THERMAL_RUNAWAY', 'WASTE_PERIOD', 'OPTIMAL_STATE'
    severity: float # 0.0 to 1.0
    timestamp: float
    details: str

class EntropyEventDetector:
    """
    Monitors the system for thermodynamic anomalies.
    """
    def __init__(self, 
                 entropy_threshold: float = 0.8, 
                 temp_threshold: float = 90.0):
        self.entropy_threshold = entropy_threshold
        self.temp_threshold = temp_threshold
        self.history = []

    def detect(self, current_state: dict, entropy_rate: float) -> Optional[EntropyEvent]:
        """
        Analyze current state and entropy rate to detect events.
        """
        event = None
        
        # 1. Thermal Runaway Detection
        # High Temp + High Entropy Rate (Disorder increasing rapidly)
        temp = current_state.get('temp', 0)
        if temp > self.temp_threshold and entropy_rate > self.entropy_threshold:
            event = EntropyEvent(
                event_type='THERMAL_RUNAWAY',
                severity=1.0,
                timestamp=time.time(),
                details=f"Temp {temp}C > {self.temp_threshold}C AND dS/dt {entropy_rate} > {self.entropy_threshold}"
            )

        # 2. Waste Period Detection
        # Low Temp (Idle) but High Entropy Rate (Inefficiency)
        elif temp < 40.0 and entropy_rate > 0.5:
             event = EntropyEvent(
                event_type='WASTE_PERIOD',
                severity=0.5,
                timestamp=time.time(),
                details=f"System Idle (Temp {temp}C) but High Entropy (dS/dt {entropy_rate})"
            )
            
        if event:
            self.history.append(event)
            print(f"🚨 EVENT DETECTED: {event.event_type} (Severity: {event.severity})")
            
        return event
