import logging
from typing import List, Dict

LOG = logging.getLogger("SCF.FossilHeatmap")

class FossilHeatmapAnalytics:
    def analyze_batch(self, fossils: List[Dict]) -> Dict[str, float]:
        if not fossils:
            return {}
            
        entropies = [f.get("entropy_gradient", 0) for f in fossils]
        # Handle vector vs scalar entropy
        scalar_entropies = []
        for e in entropies:
            if isinstance(e, list):
                scalar_entropies.append(sum(e)/len(e))
            else:
                scalar_entropies.append(e)
                
        return {
            "entropy_mean": sum(scalar_entropies) / len(scalar_entropies),
            "entropy_min": min(scalar_entropies),
            "entropy_max": max(scalar_entropies),
            "count": len(fossils)
        }
