from typing import Dict, Optional
from src.scale.planetary_resource_manager import PlanetaryResourceManager, Region

class GlobalLoadBalancer:
    """
    The Traffic Controller of the Sovereign Cloud.
    Routes workloads to the optimal region based on strategy.
    """
    
    def __init__(self, resource_manager: PlanetaryResourceManager):
        self.mgr = resource_manager
        
    def route_task(self, task_name: str, required_load: float, strategy: str = "LOWEST_LOAD") -> Optional[str]:
        """
        Finds the best region for a task.
        """
        print(f"   ⚖️ [BALANCER] Routing Task '{task_name}' (Load: {required_load:.2f})...")
        
        best_region: Optional[Region] = None
        
        if strategy == "LOWEST_LOAD":
            # Find region with lowest current load that can fit the task
            candidates = [r for r in self.mgr.regions.values() if r.current_load + required_load <= 1.0]
            if candidates:
                best_region = min(candidates, key=lambda r: r.current_load)
                
        elif strategy == "HIGHEST_CAPACITY":
             # Find region with highest total compute
            candidates = [r for r in self.mgr.regions.values() if r.current_load + required_load <= 1.0]
            if candidates:
                best_region = max(candidates, key=lambda r: r.capacity_compute)
                
        if best_region:
            best_region.allocate(required_load)
            print(f"     -> ✅ Routed to {best_region.name} (New Load: {best_region.current_load*100:.1f}%)")
            return best_region.name
        else:
            print("     -> ❌ No suitable region found.")
            return None

# --- Verification ---
if __name__ == "__main__":
    mgr = PlanetaryResourceManager()
    mgr.register_region("US_EAST", 100.0, 100.0)
    mgr.register_region("ASIA_PACIFIC", 100.0, 100.0)
    
    lb = GlobalLoadBalancer(mgr)
    
    # Fill up US_EAST
    lb.route_task("Task_1", 0.8) # US_EAST (0.8)
    
    # Next task should go to ASIA_PACIFIC
    lb.route_task("Task_2", 0.5)
