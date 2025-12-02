from typing import List, Dict, Optional
from src.optimization.planetary_optimization_engine import InefficiencyHotspot

class SolverBid:
    def __init__(self, solver_id: str, proposed_efficiency: float, cost: float):
        self.solver_id = solver_id
        self.proposed_efficiency = proposed_efficiency
        self.cost = cost
        
class InefficiencyMarketplace:
    """
    The Exchange for Entropy.
    Matches Inefficiency Hotspots with Optimization Solvers.
    """
    
    def __init__(self):
        self.listings: Dict[str, InefficiencyHotspot] = {}
        self.bids: Dict[str, List[SolverBid]] = {} # HotspotID -> Bids
        
    def list_opportunity(self, hotspot: InefficiencyHotspot):
        """
        Lists a hotspot on the market.
        """
        print(f"   📈 [MARKET] New Listing: {hotspot.type} at {hotspot.location} (Value: {hotspot.exergy_gap:.2f}J)")
        self.listings[hotspot.id] = hotspot
        self.bids[hotspot.id] = []
        
    def submit_bid(self, hotspot_id: str, bid: SolverBid):
        """
        Accepts a bid from a solver.
        """
        if hotspot_id in self.listings:
            self.bids[hotspot_id].append(bid)
            print(f"     -> 💰 Bid Received from {bid.solver_id}: Eff={bid.proposed_efficiency:.2f}, Cost={bid.cost}")
            
    def match_market(self):
        """
        Executes the matching logic.
        """
        print("   🤝 [MARKET] Matching Orders...")
        matches = []
        
        for hotspot_id, bid_list in self.bids.items():
            if not bid_list:
                continue
                
            # Simple Logic: Maximize (Efficiency / Cost)
            best_bid = max(bid_list, key=lambda b: b.proposed_efficiency / (b.cost + 0.1))
            hotspot = self.listings[hotspot_id]
            
            print(f"     -> ✅ MATCH: {hotspot.location} assigned to {best_bid.solver_id}")
            matches.append((hotspot, best_bid))
            
            # Remove listing
            del self.listings[hotspot_id]
            
        return matches

# --- Verification ---
if __name__ == "__main__":
    from src.optimization.planetary_optimization_engine import InefficiencyHotspot
    
    market = InefficiencyMarketplace()
    h = InefficiencyHotspot("H1", "Grid_Node_X", "THERMAL_WASTE", 0.8, 500.0)
    market.list_opportunity(h)
    
    market.submit_bid("H1", SolverBid("DAC_OPTIMIZER_V1", 0.5, 10.0))
    market.submit_bid("H1", SolverBid("DAC_OPTIMIZER_V2", 0.9, 12.0)) # Better value
    
    market.match_market()
