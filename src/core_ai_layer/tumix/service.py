import secrets
from typing import Dict, Any, Optional
from .schema import ConsensusRequest, ConsensusResult
from .agent_swarm import AgentSwarm
from .consensus_engine import ConsensusEngine

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
        
        return result
