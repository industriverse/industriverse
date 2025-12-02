from typing import Dict, Any, Tuple
from src.federation.sovereign_node import SovereignNode

class FederationProtocol:
    """
    The Diplomatic Layer.
    Handles handshakes and resource trading between Sovereign Nodes.
    """
    
    @staticmethod
    def handshake(initiator: SovereignNode, target: SovereignNode) -> bool:
        """
        Establishes a connection between two nodes.
        """
        print(f"   📡 [FEDERATION] Handshake: {initiator.name} -> {target.name}")
        # In a real system, this would involve cryptographic challenge-response
        return True
        
    @staticmethod
    def request_resources(
        requester: SovereignNode, 
        provider: SovereignNode, 
        resource_type: str, 
        amount: float
    ) -> Tuple[bool, str]:
        """
        Executes a resource trade request.
        """
        print(f"   🔄 [TRADE] {requester.name} requests {amount} {resource_type} from {provider.name}")
        
        # 1. Policy Check
        if not provider.can_trade_with(requester.id):
            return False, "Trade Policy Violation (Not an Ally)"
            
        # 2. Availability Check
        if resource_type == "COMPUTE":
            if provider.available_compute >= amount:
                provider.available_compute -= amount
                requester.available_compute += amount
                return True, "Compute Allocated"
            else:
                return False, "Insufficient Compute"
                
        elif resource_type == "ENERGY":
            if provider.available_energy >= amount:
                provider.available_energy -= amount
                requester.available_energy += amount
                return True, "Energy Allocated"
            else:
                return False, "Insufficient Energy"
                
        return False, "Unknown Resource Type"

# --- Verification ---
if __name__ == "__main__":
    n1 = SovereignNode("Node_1")
    n2 = SovereignNode("Node_2")
    
    # Open Trade
    success, msg = FederationProtocol.request_resources(n1, n2, "COMPUTE", 10.0)
    print(f"Trade 1: {success} ({msg})")
    
    # Restricted Trade
    n2.trade_policy = "RESTRICTED"
    success, msg = FederationProtocol.request_resources(n1, n2, "COMPUTE", 10.0)
    print(f"Trade 2: {success} ({msg})")
