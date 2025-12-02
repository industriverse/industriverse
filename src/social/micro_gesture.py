import numpy as np
import random
from dataclasses import dataclass

@dataclass
class GestureTelemetry:
    timestamp: float
    scroll_velocity_px_s: float
    touch_pressure: float
    dwell_time_ms: float
    jitter_variance: float

class MicroGestureAnalyzer:
    """
    SPI Module 11: Micro-Gesture Interaction Analyzer (MGIA).
    Detects non-human UI interaction patterns (Bots/Scripts).
    Humans have 'Micro-Pauses' and 'Jitter'. Bots are smooth and constant.
    """
    def __init__(self):
        self.human_jitter_threshold = 0.05
        
    def analyze_session(self, gestures: list[GestureTelemetry]) -> float:
        """
        Returns 'Bot Probability' (0.0 to 1.0).
        """
        if not gestures:
            return 0.0
            
        # 1. Check Velocity Consistency (Bots often scroll at constant speed)
        velocities = [g.scroll_velocity_px_s for g in gestures]
        vel_variance = np.var(velocities)
        
        # 2. Check Jitter (Humans shake slightly)
        avg_jitter = np.mean([g.jitter_variance for g in gestures])
        
        # 3. Check Dwell Time Regularity
        dwells = [g.dwell_time_ms for g in gestures]
        dwell_variance = np.var(dwells)
        
        print(f"👆 [MGIA] Session Analysis:")
        print(f"   - Velocity Var: {vel_variance:.4f}")
        print(f"   - Avg Jitter: {avg_jitter:.4f}")
        print(f"   - Dwell Var: {dwell_variance:.4f}")
        
        score = 0.0
        if vel_variance < 10.0: # Too smooth
            score += 0.4
        if avg_jitter < 0.01: # Too precise
            score += 0.4
        if dwell_variance < 5.0: # Robotic timing
            score += 0.2
            
        return min(score, 1.0)
        
    def simulate_bot_scroll(self) -> list[GestureTelemetry]:
        """
        Generates perfectly smooth, robotic scrolling.
        """
        return [
            GestureTelemetry(i*1.0, 500.0, 1.0, 100.0, 0.0) 
            for i in range(10)
        ]
