from dataclasses import dataclass, field
from typing import Dict, List
import uuid

@dataclass
class Region:
    """
    A geographic cluster of sovereign resources.
    """
    id: str
    name: str # e.g., "US_EAST", "ASIA_SOUTH"
    capacity_compute: float # PetaFLOPS
    capacity_energy: float # MWh
    current_load: float = 0.0 # 0.0 to 1.0
    
    def allocate(self, load: float) -> bool:
        if self.current_load + load <= 1.0:
            self.current_load += load
            return True
        return False

class PlanetaryResourceManager:
    """
    The Global Overseer of Physical Assets.
    Manages resource clusters across the planet.
    """
    
    def __init__(self):
        self.regions: Dict[str, Region] = {}
        
    def register_region(self, name: str, compute: float, energy: float):
        region = Region(str(uuid.uuid4()), name, compute, energy)
        self.regions[name] = region
        print(f"   🌍 [PLANETARY] Registered Region: {name} (Compute: {compute}PF, Energy: {energy}MWh)")
        
    def get_status(self):
        print("\n   📊 [PLANETARY STATUS]")
        for r in self.regions.values():
            print(f"     -> {r.name}: Load {r.current_load*100:.1f}%")

# --- Verification ---
if __name__ == "__main__":
    mgr = PlanetaryResourceManager()
    mgr.register_region("US_EAST", 1000.0, 5000.0)
    mgr.register_region("EU_WEST", 800.0, 4000.0)
    mgr.get_status()
