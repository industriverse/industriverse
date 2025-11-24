import time
from typing import Dict, Any


class EntropyTracker:
    """
    Tracks recent entropy readings to detect spikes over time.
    """

    def __init__(self):
        self.history = []

    def record(self, entropy: float):
        self.history.append((time.time(), entropy))
        # Keep last 100 readings
        if len(self.history) > 100:
            self.history = self.history[-100:]

    def spike_detected(self, threshold: float) -> bool:
        if len(self.history) < 2:
            return False
        # Compare last reading with average of previous
        last_ts, last_entropy = self.history[-1]
        prev = [e for _, e in self.history[:-1]]
        avg_prev = sum(prev) / len(prev)
        return (last_entropy - avg_prev) > threshold
