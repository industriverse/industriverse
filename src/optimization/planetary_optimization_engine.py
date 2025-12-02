from typing import List, Dict, Any
from dataclasses import dataclass
import uuid

@dataclass
class InefficiencyHotspot:
    id: str
    location: str
    type: str # THERMAL_WASTE, IDLE_COMPUTE, LOGISTICS_DELAY
    magnitude: float # 0.0 to 1.0
    exergy_gap: float # Potential Joule Value
    
class PlanetaryOptimizationEngine:
    """
    The Global Scanner.
    Identifies inefficiencies across the planetary substrate.
    """
    
    def __init__(self):
        self.hotspots: List[InefficiencyHotspot] = []
        
    def scan_resource_clusters(self, clusters: List[Dict[str, Any]]) -> List[InefficiencyHotspot]:
        """
        Analyzes resource clusters to find waste.
        """
        print(f"   🌍 [OPTIMIZER] Scanning {len(clusters)} Resource Clusters...")
        new_hotspots = []
        
        for cluster in clusters:
            # Logic: High Entropy + High Energy Input = Waste
            entropy = cluster.get("entropy", 0.0)
            energy_input = cluster.get("energy_input", 0.0)
            utilization = cluster.get("utilization", 1.0)
            
            if utilization < 0.5:
                # Idle Resource
                hotspot = InefficiencyHotspot(
                    id=str(uuid.uuid4()),
                    location=cluster.get("location", "UNKNOWN"),
                    type="IDLE_RESOURCE",
                    magnitude=1.0 - utilization,
                    exergy_gap=energy_input * (1.0 - utilization) * 100.0
                )
                new_hotspots.append(hotspot)
                print(f"     -> ⚠️ Found Hotspot: IDLE_RESOURCE at {hotspot.location} (Gap: {hotspot.exergy_gap:.2f}J)")
                
            elif entropy > 0.8 and energy_input > 50.0:
                # Thermal Waste
                hotspot = InefficiencyHotspot(
                    id=str(uuid.uuid4()),
                    location=cluster.get("location", "UNKNOWN"),
                    type="THERMAL_WASTE",
                    magnitude=entropy,
                    exergy_gap=energy_input * entropy * 50.0
                )
                new_hotspots.append(hotspot)
                print(f"     -> ⚠️ Found Hotspot: THERMAL_WASTE at {hotspot.location} (Gap: {hotspot.exergy_gap:.2f}J)")
                
        self.hotspots.extend(new_hotspots)
        return new_hotspots

# --- Verification ---
if __name__ == "__main__":
    engine = PlanetaryOptimizationEngine()
    clusters = [
        {"location": "Factory_A", "entropy": 0.9, "energy_input": 100.0, "utilization": 0.9}, # Waste
        {"location": "Server_Farm_B", "entropy": 0.1, "energy_input": 200.0, "utilization": 0.2} # Idle
    ]
    engine.scan_resource_clusters(clusters)
