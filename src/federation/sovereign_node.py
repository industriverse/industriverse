from typing import Dict, List, Any
import uuid

class SovereignNode:
    """
    An independent node in the Sovereign Compute Federation.
    Represents a Nation, Corporation, or Autonomous Zone running the stack.
    """
    
    def __init__(self, name: str, node_type: str = "STANDARD"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.node_type = node_type # STANDARD, CORE, EDGE
        
        # Resources
        self.available_compute = 100.0 # PetaFLOPS (Mock)
        self.available_energy = 1000.0 # MWh (Mock)
        
        # Policy
        self.allies: List[str] = [] # List of trusted Node IDs
        self.trade_policy = "OPEN" # OPEN, RESTRICTED, ISOLATED
        
    def register_ally(self, node_id: str):
        """
        Adds a node to the trusted ally list.
        """
        if node_id not in self.allies:
            self.allies.append(node_id)
            print(f"   🤝 [{self.name}] Registered Ally: {node_id}")
            
    def can_trade_with(self, node_id: str) -> bool:
        """
        Checks if trade is allowed based on policy.
        """
        if self.trade_policy == "OPEN":
            return True
        elif self.trade_policy == "RESTRICTED":
            return node_id in self.allies
        return False

# --- Verification ---
if __name__ == "__main__":
    node_a = SovereignNode("Nation_A")
    node_b = SovereignNode("Nation_B")
    
    node_a.trade_policy = "RESTRICTED"
    print(f"Can A trade with B? {node_a.can_trade_with(node_b.id)}")
    
    node_a.register_ally(node_b.id)
    print(f"Can A trade with B now? {node_a.can_trade_with(node_b.id)}")
