import uuid
import time
from typing import Dict, Any
import asyncio

from src.proof_core.integrity_layer import record_reasoning_edge

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

    def analyze_with_proof(self, context: Dict[str, Any], utid: str = "UTID:REAL:unknown") -> float:
        score = self.analyze(context)
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(
                record_reasoning_edge(
                    utid=utid,
                    domain="nanochat_analysis",
                    node_id=self.id,
                    inputs={"context": context},
                    outputs={"score": score, "role": self.role},
                    metadata={"status": "completed"},
                )
            )
        except Exception:
            pass
        return score
