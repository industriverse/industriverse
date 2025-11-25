import secrets
from typing import Dict, Any, Optional
from .schema import ConsensusRequest, ConsensusResult
from .agent_swarm import AgentSwarm
from .consensus_engine import ConsensusEngine
from src.proof_core.integrity_layer import record_reasoning_edge

class TUMIXService:
    """
    Orchestrates the Tool-Use Mixture (TUMIX) consensus loop.
    """
    
    def __init__(self):
        self.swarm = AgentSwarm()
        self.engine = ConsensusEngine()

    async def request_consensus(self, intent_id: str, proposal: str, context: Dict[str, Any] = None) -> ConsensusResult:
        """
        Trigger a swarm debate on a proposal.
        """
        request_id = f"req-{secrets.token_hex(4)}"
        
        # 1. Collect votes from the swarm
        votes = await self.swarm.collect_votes(proposal)
        
        # 2. Calculate consensus
        result = self.engine.calculate_consensus(
            request_id=request_id,
            votes=votes,
            required_majority=0.6
        )

        utid = context.get("utid") if context else "UTID:REAL:unknown"
        await record_reasoning_edge(
            utid=utid or "UTID:REAL:unknown",
            domain="tumix_consensus",
            node_id="tumix_service",
            inputs={"proposal": proposal, "votes": votes},
            outputs={"consensus": result.dict() if hasattr(result, "dict") else str(result)},
            metadata={"status": "completed"},
        )
        
        return result
