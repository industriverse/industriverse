import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.coherence.iacp_protocol import IACPProtocol
from src.coherence.agent_interface import CoherentAgent
from src.unification.unified_substrate_model import USMSignal, SignalType, USMEntropy

class SafetyAgent(CoherentAgent):
    def vote_on_proposal(self, proposal_id, description):
        # Safety Agent hates risk
        return "RISKY" not in description

class MarketAgent(CoherentAgent):
    def vote_on_proposal(self, proposal_id, description):
        # Market Agent loves profit (mock logic)
        return True

def verify_iacp_society():
    print("🏙️ INITIALIZING AGENT SOCIETY (IACP)...")
    protocol = IACPProtocol()
    
    # 1. Spawn Agents
    discoverer = CoherentAgent("DISCOVERER_01", "DISCOVERY", protocol)
    guardian = SafetyAgent("GUARDIAN_01", "DEFENSE", protocol)
    trader = MarketAgent("TRADER_01", "MARKET", protocol)
    
    # 2. Interaction: Discoverer sends a "High Entropy" signal (Bad Idea)
    print("\n--- Interaction 1: Bad Signal ---")
    bad_entropy = USMEntropy(shannon_index=0.9) # High Disorder
    bad_signal = USMSignal(type=SignalType.SCIENTIFIC, source_id=discoverer.identity.id, entropy_delta=bad_entropy)
    
    msg = discoverer.send_message(guardian.identity.id, bad_signal, "DATA_SHARE")
    guardian.receive_message(msg)
    
    # Check Trust Impact
    trust_score = protocol.trust_ledger[discoverer.identity.id]
    print(f"   📉 Discoverer Trust Score: {trust_score:.3f} (Expected < 0.5)")
    
    # 3. Consensus: Voting on a Risky Proposal
    print("\n--- Interaction 2: Consensus Vote ---")
    proposal_desc = "EXECUTE_RISKY_EXPERIMENT"
    
    votes = {
        discoverer.identity.id: True, # Discoverer votes for themselves
        guardian.identity.id: guardian.vote_on_proposal("PROP_1", proposal_desc), # Should be False
        trader.identity.id: trader.vote_on_proposal("PROP_1", proposal_desc) # Should be True
    }
    
    # Guardian (High Trust) vs Discoverer (Low Trust) + Trader (Med Trust)
    # Guardian starts at 0.5, Discoverer dropped to ~0.475, Trader at 0.5
    # YES = 0.475 + 0.5 = 0.975
    # NO = 0.5
    # Result should be YES (Risky experiment passes due to Trader support)
    
    result = protocol.consensus_vote("PROP_1", votes)
    
    if result:
        print("   ✅ Consensus Reached (Proposal Passed)")
    else:
        print("   ❌ Consensus Failed (Proposal Rejected)")
        
    print("\n✅ IACP Verification Complete.")

if __name__ == "__main__":
    verify_iacp_society()
