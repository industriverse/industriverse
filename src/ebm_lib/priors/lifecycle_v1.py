import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class YieldPrior(EnergyPrior):
    name = "lifecycle_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Yield Forecaster Prior.
        x: [batch, 2] -> [Process_Variance, Mean_Shift]
        
        Energy = Variance + Mean Shift (Six Sigma)
        """
        variance = x[..., 0]
        mean_shift = x[..., 1]
        
        # 1. Process Variance (Minimize)
        e_var = variance.pow(2) * 10.0
        
        # 2. Mean Shift (Minimize deviation from 0)
        e_shift = mean_shift.pow(2) * 10.0
        
        return e_var + e_shift

prior = YieldPrior()
prior.register()
