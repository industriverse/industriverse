import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class HVACPrior(EnergyPrior):
    name = "heat_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        HVAC Optimizer Prior.
        x: [batch, 2] -> [Indoor_Temp, Power_Usage]
        
        Energy = Comfort Deviation + Power Consumption
        """
        temp = x[..., 0]
        power = x[..., 1]
        
        # 1. Comfort (Target 22 C)
        e_comfort = (temp - 22.0).pow(2)
        
        # 2. Power Consumption (Minimize)
        # But we need power to change temp. 
        # In a static optimization, this just minimizes power.
        # Realistically, T is a function of Power.
        # Here we assume a simple relation: T_next = T_curr + k * Power - Loss
        # But for EBM, we just define the "desirable state".
        # Desirable: Temp=22 AND Power=Low.
        e_power = 0.1 * power.pow(2)
        
        return e_comfort + e_power

prior = HVACPrior()
prior.register()
