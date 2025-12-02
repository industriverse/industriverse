import numpy as np

class AttentionAccelerationDetector:
    """
    SPI Module 3: Attention Acceleration Detector (AAD).
    Detects 'Non-Physical Acceleration' in view counts/likes.
    Organic virality follows Logistic Growth. Paid/Bot virality is Step-Function.
    """
    def __init__(self):
        self.max_organic_acceleration = 2.0 # Views per second^2 (Heuristic)
        
    def analyze_growth_curve(self, time_series: list[tuple[float, int]]) -> float:
        """
        Input: List of (timestamp, view_count).
        Returns: 'Manipulation Score' (0.0 to 1.0).
        """
        if len(time_series) < 3:
            return 0.0
            
        # Calculate 2nd Derivative (Acceleration)
        # v = dViews/dt
        # a = dv/dt
        
        accelerations = []
        for i in range(2, len(time_series)):
            t0, v0 = time_series[i-2]
            t1, v1 = time_series[i-1]
            t2, v2 = time_series[i]
            
            vel1 = (v1 - v0) / (t1 - t0)
            vel2 = (v2 - v1) / (t2 - t1)
            
            acc = (vel2 - vel1) / (t2 - t1)
            accelerations.append(acc)
            
        max_acc = max(np.abs(accelerations))
        print(f"📈 [AAD] Max Acceleration: {max_acc:.2f} views/s²")
        
        if max_acc > self.max_organic_acceleration * 10:
            print("   🚨 ALERT: Impossible Acceleration! (Bot Injection?)")
            return 1.0
        elif max_acc > self.max_organic_acceleration:
            return 0.6
        else:
            return 0.0
