import numpy as np
import random

class HarmonicPostingDetector:
    """
    SPI Module 1: Harmonic Posting Detector (HPD).
    Uses FFT to find synchronized botnet activity in timestamp data.
    """
    def __init__(self):
        pass
        
    def analyze_timestamps(self, timestamps: list) -> float:
        """
        Returns a 'Coordination Score' (0.0 to 1.0).
        High score = Artificial/Bot (Perfectly periodic).
        Low score = Organic/Human (Noisy).
        """
        if len(timestamps) < 10:
            return 0.0
            
        # Convert to inter-arrival times
        sorted_ts = sorted(timestamps)
        deltas = np.diff(sorted_ts)
        
        # Simple variance check (Real FFT would be used in prod)
        # Bots often have very low variance in posting intervals (e.g., exactly every 5 mins)
        variance = np.var(deltas)
        
        print(f"🤖 [HPD] Analyzing {len(timestamps)} posts. Variance: {variance:.4f}")
        
        if variance < 0.1: # Extremely regular
            return 0.95
        elif variance < 1.0:
            return 0.7
        else:
            return 0.1 # Organic
            
    def simulate_bot_attack(self, count: int, interval: float) -> list:
        """
        Generates a perfectly periodic timestamp sequence.
        """
        start = 1000.0
        return [start + (i * interval) for i in range(count)]
