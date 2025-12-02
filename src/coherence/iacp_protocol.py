from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time
import uuid
from src.unification.unified_substrate_model import USMSignal, SignalType

@dataclass
class AgentIdentity:
    id: str
    role: str # DISCOVERY, DEFENSE, MARKET
    capabilities: List[str]
    reputation: float = 0.5 # 0.0 -> 1.0

@dataclass
class IACPMessage:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str = ""
    recipient_id: str = "BROADCAST"
    type: str = "INFO" # PROPOSAL, VOTE, INFO, ALERT
    payload: Optional[USMSignal] = None
    timestamp: float = field(default_factory=time.time)

class IACPProtocol:
    """
    The Inter-Agent Coherence Protocol (IACP).
    Manages Trust, Identity, and Consensus for the Agent Society.
    """
    
    def __init__(self):
        self.registry: Dict[str, AgentIdentity] = {}
        self.trust_ledger: Dict[str, float] = {} # AgentID -> TrustScore
        
    def register_agent(self, identity: AgentIdentity):
        """
        Registers a new agent in the society.
        """
        print(f"   🤝 [IACP] Registering Agent: {identity.id} ({identity.role})")
        self.registry[identity.id] = identity
        self.trust_ledger[identity.id] = identity.reputation
        
    def calculate_trust(self, agent_id: str, interaction_signal: USMSignal) -> float:
        """
        Updates trust based on the quality of a signal.
        """
        current_trust = self.trust_ledger.get(agent_id, 0.5)
        
        # Logic: High Entropy signals reduce trust, Low Entropy (Ordered) signals increase it.
        if interaction_signal.entropy_delta:
            score = interaction_signal.entropy_delta.get_composite_score()
            if score > 0.7: # High Disorder
                current_trust *= 0.95 # Penalty
            elif score < 0.3: # High Order
                current_trust = min(1.0, current_trust * 1.05) # Reward
                
        self.trust_ledger[agent_id] = current_trust
        return current_trust

    def consensus_vote(self, proposal_id: str, votes: Dict[str, bool]) -> bool:
        """
        Determines consensus based on reputation-weighted voting.
        """
        yes_weight = 0.0
        no_weight = 0.0
        
        for agent_id, vote in votes.items():
            weight = self.trust_ledger.get(agent_id, 0.0)
            if vote:
                yes_weight += weight
            else:
                no_weight += weight
                
        result = yes_weight > no_weight
        print(f"   🗳️ [IACP] Consensus {proposal_id}: YES={yes_weight:.2f} NO={no_weight:.2f} -> {'PASSED' if result else 'REJECTED'}")
        return result

# --- Verification ---
if __name__ == "__main__":
    protocol = IACPProtocol()
    
    # Register Agents
    a1 = AgentIdentity("AGENT_A", "DISCOVERY", ["SEARCH"], 0.8)
    a2 = AgentIdentity("AGENT_B", "MARKET", ["TRADE"], 0.4)
    protocol.register_agent(a1)
    protocol.register_agent(a2)
    
    # Vote
    votes = {"AGENT_A": True, "AGENT_B": False}
    protocol.consensus_vote("PROP_001", votes)
