import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class GridPrior(EnergyPrior):
    name = "grid_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Grid Frequency Lock Prior.
        x: [batch, 2] -> [Frequency, RoCoF] (Rate of Change of Freq)
        
        Energy = Frequency Deviation + RoCoF (Inertia)
        """
        freq = x[..., 0]
        rocof = x[..., 1]
        
        # 1. Frequency Deviation (Target 60 Hz)
        e_freq = (freq - 60.0).pow(2) * 100.0
        
        # 2. RoCoF (Minimize change rate -> Emulate Inertia)
        e_rocof = rocof.pow(2) * 10.0
        
        return e_freq + e_rocof

prior = GridPrior()
prior.register()
