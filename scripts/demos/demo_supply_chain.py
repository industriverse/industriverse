import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.supply_chain.cognitive_supply_chain import CognitiveSupplyChain
from src.supply_chain.predictive_logistics import PredictiveLogistics
from src.unification.unified_substrate_model import USMSignal, USMEntropy

def print_header(text):
    print(f"\n{'='*60}")
    print(f"   {text}")
    print(f"{'='*60}")

def demo_supply_chain():
    print_header("DEMO: THE COGNITIVE SUPPLY CHAIN")
    print("Scenario: Autonomous Rerouting (Suez Canal Event)")
    
    # 1. Initialize Network
    chain = CognitiveSupplyChain()
    
    # Nodes
    port_asia = chain.add_node("Port_Singapore", "PORT")
    port_eu = chain.add_node("Port_Rotterdam", "PORT")
    
    # Routes
    route_suez = chain.add_route(port_asia, port_eu, 14.0) # Fast
    route_cape = chain.add_route(port_asia, port_eu, 24.0) # Slow but Safe
    
    print(f"   Route A (Suez): {route_suez} (14 Days)")
    print(f"   Route B (Cape): {route_cape} (24 Days)")
    
    # 2. Normal Operations
    print_header("PHASE 1: NORMAL OPERATIONS")
    best_route = chain.find_route(port_asia, port_eu)
    print(f"   🚢 Shipment 001 Assigned to: {best_route.id} (Status: {best_route.status})")
    
    # 3. The Event
    print_header("PHASE 2: GEOPOLITICAL INSTABILITY DETECTED")
    predictor = PredictiveLogistics(chain)
    
    # Inject Signal: High Social Entropy in Region
    print(">> INJECTING SIGNAL: High Social Entropy (Conflict Risk)...")
    sig = USMSignal(entropy=USMEntropy(0.85, "SOCIAL"))
    
    # 4. Reaction
    predictor.analyze_signals([sig])
    
    # 5. Rerouting
    print_header("PHASE 3: AUTONOMOUS REROUTING")
    # Verify Suez is blocked
    if chain.routes[route_suez].status == "BLOCKED":
        print(f"   ⚠️ Route A (Suez) is now BLOCKED.")
    
    # Find new route
    new_route = chain.find_route(port_asia, port_eu)
    if new_route and new_route.id == route_cape:
        print(f"   ✅ Shipment 002 Rerouted to: {new_route.id} (Cape of Good Hope)")
    else:
        print("   ❌ Rerouting Failed.")
        
    print_header("DEMO COMPLETE: RESILIENCE ACHIEVED")

if __name__ == "__main__":
    demo_supply_chain()
