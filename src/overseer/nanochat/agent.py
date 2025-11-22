import uuid
import time
from typing import Dict, Any

class NanochatAgent:
    def __init__(self, role: str):
        self.id = str(uuid.uuid4())[:8]
        self.role = role
        self.status = "active"
        self.last_heartbeat = time.time()

    def ping(self) -> Dict[str, Any]:
        self.last_heartbeat = time.time()
        return {
            "id": self.id,
            "role": self.role,
            "status": self.status,
            "timestamp": self.last_heartbeat
        }

    def analyze(self, context: Dict[str, Any]) -> float:
        """
        Analyze context and return a threat score (0.0 - 1.0).
        """
        # Mock logic: if context contains "attack", high score
        if "attack" in str(context).lower():
            return 0.9
        return 0.1
