import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.optimization.planetary_optimization_engine import PlanetaryOptimizationEngine
from src.optimization.inefficiency_marketplace import InefficiencyMarketplace, SolverBid

def verify_planetary_optimization():
    print("🌍 INITIALIZING PLANETARY OPTIMIZATION SIMULATION...")
    
    # 1. The Engine
    engine = PlanetaryOptimizationEngine()
    
    # Mock Clusters
    clusters = [
        {"location": "Steel_Mill_01", "entropy": 0.85, "energy_input": 1000.0, "utilization": 0.9}, # Thermal Waste
        {"location": "Data_Center_05", "entropy": 0.1, "energy_input": 500.0, "utilization": 0.3}, # Idle Compute
        {"location": "Solar_Farm_99", "entropy": 0.05, "energy_input": 200.0, "utilization": 0.95} # Efficient
    ]
    
    # 2. Scan
    print("\n--- Step 1: Global Scan ---")
    hotspots = engine.scan_resource_clusters(clusters)
    
    if len(hotspots) != 2:
        print(f"❌ Expected 2 hotspots, found {len(hotspots)}")
        sys.exit(1)
        
    # 3. The Marketplace
    print("\n--- Step 2: Marketplace Listing ---")
    market = InefficiencyMarketplace()
    for h in hotspots:
        market.list_opportunity(h)
        
    # 4. Bidding
    print("\n--- Step 3: Solver Bidding ---")
    # Bid on Thermal Waste
    waste_id = next(h.id for h in hotspots if h.type == "THERMAL_WASTE")
    market.submit_bid(waste_id, SolverBid("THERMAL_DAC_V1", 0.4, 50.0))
    market.submit_bid(waste_id, SolverBid("THERMAL_DAC_V2", 0.7, 60.0)) # Winner
    
    # Bid on Idle Compute
    idle_id = next(h.id for h in hotspots if h.type == "IDLE_RESOURCE")
    market.submit_bid(idle_id, SolverBid("COMPUTE_BROKER_DAC", 0.95, 10.0))
    
    # 5. Matching
    print("\n--- Step 4: Market Clearing ---")
    matches = market.match_market()
    
    if len(matches) != 2:
        print(f"❌ Expected 2 matches, found {len(matches)}")
        sys.exit(1)
        
    # Verify Winners
    winners = [m[1].solver_id for m in matches]
    if "THERMAL_DAC_V2" in winners and "COMPUTE_BROKER_DAC" in winners:
        print("\n✅ Planetary Optimization Verification Complete. Market is Efficient.")
    else:
        print(f"❌ Unexpected winners: {winners}")
        sys.exit(1)

if __name__ == "__main__":
    verify_planetary_optimization()
