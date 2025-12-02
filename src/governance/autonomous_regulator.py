from typing import Dict, Any, List
import time

class RegulatoryOrder:
    def __init__(self, id: str, action: str, reason: str, target: str):
        self.id = id
        self.action = action # THROTTLE, FREEZE, SANCTION
        self.reason = reason
        self.target = target
        self.timestamp = time.time()

class AutonomousRegulator:
    """
    The Sovereign Regulator.
    Enforces economic and safety limits to prevent runaway scenarios.
    """
    
    def __init__(self):
        self.orders: List[RegulatoryOrder] = []
        # Limits
        self.max_daily_entropy_delta = 10.0
        self.max_resource_burn_rate = 0.8 # 80% of capacity
        
    def evaluate_state(self, organism_state: Any) -> List[RegulatoryOrder]:
        """
        Checks the organism's state against regulatory limits.
        """
        new_orders = []
        print(f"   ⚖️ [REGULATOR] Evaluating State (Entropy: {organism_state.entropy:.2f})")
        
        # 1. Entropy Check (Stability)
        if organism_state.entropy > self.max_daily_entropy_delta:
            order = RegulatoryOrder(
                id=f"REG_{int(time.time())}_01",
                action="THROTTLE",
                reason="Entropy Limit Breached",
                target="DAEMON"
            )
            new_orders.append(order)
            print(f"     -> 🛑 ORDER ISSUED: Throttle Daemon (High Entropy)")
            
        # 2. Resource Burn Check (Sustainability)
        # Mock calculation of burn rate
        burn_rate = (100.0 - organism_state.energy) / 100.0 
        if burn_rate > self.max_resource_burn_rate:
            order = RegulatoryOrder(
                id=f"REG_{int(time.time())}_02",
                action="FREEZE",
                reason="Unsustainable Burn Rate",
                target="FOUNDRY"
            )
            new_orders.append(order)
            print(f"     -> 🛑 ORDER ISSUED: Freeze Foundry (High Burn)")
            
        self.orders.extend(new_orders)
        return new_orders

# --- Verification ---
if __name__ == "__main__":
    class MockState:
        entropy = 12.0
        energy = 10.0
        
    regulator = AutonomousRegulator()
    orders = regulator.evaluate_state(MockState())
    print(f"Orders Issued: {len(orders)}")
