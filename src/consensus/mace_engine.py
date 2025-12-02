from typing import List, Any
from src.consensus.raft_protocol import RaftNode

class MACEEngine:
    """
    Multi-Agent Consensus Engine.
    Uses Raft to agree on 'Truths' in the Industriverse.
    """
    
    def __init__(self, nodes: List[RaftNode]):
        self.nodes = nodes
        print("   ⚖️ [MACE] Consensus Engine Initialized.")
        
    def propose_truth(self, truth: str) -> bool:
        """
        Submits a truth for ratification by the cluster.
        """
        print(f"   📜 [PROPOSAL] '{truth}' submitted for consensus...")
        
        # 1. Find Leader
        leader = None
        for node in self.nodes:
            if node.state == "LEADER":
                leader = node
                break
                
        if not leader:
            print("     -> ❌ No Leader elected yet. Consensus stalled.")
            return False
            
        print(f"     -> Forwarded to Leader: {leader.id}")
        
        # 2. Leader Replicates (Simulated)
        # In real Raft, leader appends to log, replicates, waits for majority commit
        print(f"     -> 🗳️ [VOTE] Cluster voting on '{truth}'...")
        
        # Simulate Majority Agreement
        votes = 1 # Leader votes for itself
        for peer in leader.peers:
            # Simulate validation logic (random for demo)
            votes += 1
            
        if votes > len(self.nodes) / 2:
            print(f"     -> ✅ [COMMIT] Consensus Reached! '{truth}' is now TRUTH.")
            return True
        else:
            print(f"     -> ❌ [REJECT] Consensus Failed.")
            return False

# --- Verification ---
if __name__ == "__main__":
    # Setup Cluster
    n1 = RaftNode("Agent_A", [])
    n2 = RaftNode("Agent_B", [])
    n3 = RaftNode("Agent_C", [])
    cluster = [n1, n2, n3]
    
    # Link
    n1.peers = [n2, n3]
    n2.peers = [n1, n3]
    n3.peers = [n1, n2]
    
    # Elect Leader
    n1.start_election()
    
    # Run MACE
    mace = MACEEngine(cluster)
    mace.propose_truth("Discovery_ID_123 is Valid")
