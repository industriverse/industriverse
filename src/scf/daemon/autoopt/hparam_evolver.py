import random
from typing import Dict, Any

class HParamEvolver:
    def evolve(self, current_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mutates hyperparameters for the next week's run.
        """
        new_params = current_params.copy()
        
        # Mutate Learning Rate
        if random.random() < 0.3:
            new_params["lr"] *= random.choice([0.8, 0.9, 1.1, 1.2])
            
        # Mutate Weight Decay
        if random.random() < 0.3:
            new_params["weight_decay"] *= random.choice([0.5, 2.0])
            
        return new_params
