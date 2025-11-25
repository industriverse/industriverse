from typing import List, Dict, Any
from src.overseer.nanochat.agent import NanochatAgent

class NanochatSwarm:
    def __init__(self, size: int = 5):
        self.agents = [NanochatAgent(role=f"sentry_{i}") for i in range(size)]

    def heartbeat_sync(self) -> bool:
        """
        Check if all agents are responsive and aligned.
        """
        responses = [a.ping() for a in self.agents]
        # In a real system, we'd check for consensus drift here
        return all(r["status"] == "active" for r in responses)

    def consensus_check(self, context: Dict[str, Any]) -> float:
        """
        Aggregate threat scores from all agents.
        """
        utid = context.get("utid", "UTID:REAL:unknown")
        scores = [a.analyze_with_proof(context, utid=utid) for a in self.agents]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return avg_score
