import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class ApparelPrior(EnergyPrior):
    name = "apparel_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Apparel Tensioner Prior.
        x: [batch, 4] -> Tensions at 4 corners of fabric.
        
        Energy = Variance (Uneven Tension) + Deviation from Optimal
        """
        # 1. Uneven Tension (Wrinkles/Tearing)
        mean_tension = x.mean(dim=-1, keepdim=True)
        e_variance = (x - mean_tension).pow(2).sum(dim=-1)
        
        # 2. Optimal Tension Target (e.g., 5.0 N)
        e_target = (x - 5.0).pow(2).sum(dim=-1)
        
        return e_variance + e_target

prior = ApparelPrior()
prior.register()
