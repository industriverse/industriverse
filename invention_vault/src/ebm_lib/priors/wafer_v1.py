import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class WaferPrior(EnergyPrior):
    name = "wafer_v1"
    
    def __init__(self, target_temp=1000.0):
        super().__init__()
        self.target_temp = target_temp

    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Wafer Thermal Controller Prior.
        x: [batch, 5] -> Temperatures at 5 zones across the wafer.
        
        Energy = Deviation from Target + Non-Uniformity (Gradient)
        """
        # 1. Deviation from Target Temperature (Process Requirement)
        e_target = (x - self.target_temp).pow(2).mean(dim=-1)
        
        # 2. Non-Uniformity (Thermal Stress)
        # Minimize difference between adjacent zones to prevent warping
        # x[:, 1:] - x[:, :-1] computes differences
        gradients = x[..., 1:] - x[..., :-1]
        e_gradient = 10.0 * gradients.pow(2).mean(dim=-1)
        
        return e_target + e_gradient

prior = WaferPrior()
prior.register()
