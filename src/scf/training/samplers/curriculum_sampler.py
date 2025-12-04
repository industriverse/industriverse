import torch
from torch.utils.data import WeightedRandomSampler
from typing import List, Dict

class CurriculumSampler:
    def create_sampler(self, fossils: List[Dict[str, Any]], bias="entropy_high") -> WeightedRandomSampler:
        weights = []
        for f in fossils:
            ent = f.get("entropy_gradient", 0.5)
            if isinstance(ent, list): ent = ent[0]
            
            if bias == "entropy_high":
                w = ent
            elif bias == "entropy_low":
                w = 1.0 - ent
            elif bias == "novelty":
                w = f.get("novelty_score", 0.5)
            else:
                w = 1.0
            weights.append(max(0.01, float(w))) # Avoid 0 weight
            
        return WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)
