from dataclasses import dataclass
from typing import List, Dict, Optional

@dataclass
class ComputeZone:
    zone_id: str
    energy_cost_per_kwh: float
    carbon_intensity: float
    available_capacity: float

class EntropyArbitrageSolver:
    """
    Identifies the optimal compute zone for a workload based on cost and carbon.
    """
    def __init__(self):
        self.zones: Dict[str, ComputeZone] = {}

    def register_zone(self, zone: ComputeZone):
        self.zones[zone.zone_id] = zone

    def find_optimal_zone(self, required_capacity: float, optimize_for: str = 'COST') -> Optional[str]:
        """
        Find the best zone.
        optimize_for: 'COST' or 'CARBON'
        """
        candidates = [z for z in self.zones.values() if z.available_capacity >= required_capacity]
        
        if not candidates:
            return None
            
        if optimize_for == 'COST':
            best_zone = min(candidates, key=lambda z: z.energy_cost_per_kwh)
        elif optimize_for == 'CARBON':
            best_zone = min(candidates, key=lambda z: z.carbon_intensity)
        else:
            raise ValueError("Invalid optimization criteria")
            
        print(f"🌍 Arbitrage Result: Move to {best_zone.zone_id} ({optimize_for})")
        return best_zone.zone_id
