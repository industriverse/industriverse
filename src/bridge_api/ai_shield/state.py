import time
from typing import Optional, Dict, Any


class ShieldState:
    """
    Minimal AI Shield state tracker for Pulse rendering.
    """

    def __init__(self):
        self.state = {
            "status": "stable",
            "last_event_ts": time.time(),
            "metrics": {},
        }

    def update(self, status: str, metrics: Optional[Dict[str, Any]] = None):
        self.state["status"] = status
        self.state["last_event_ts"] = time.time()
        if metrics:
            self.state["metrics"] = metrics
        if status == "quarantine":
            self.state["metrics"]["quarantine"] = True
        return self.state

    def get(self):
        return self.state


shield_state = ShieldState()
