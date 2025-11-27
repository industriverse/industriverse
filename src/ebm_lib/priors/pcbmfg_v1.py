import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class PCBPrior(EnergyPrior):
    name = "pcbmfg_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        PCB Reflow Optimizer Prior.
        x: [batch, 4] -> [Ramp_Rate, Soak_Temp, Reflow_Temp, Cool_Rate]
        
        Energy = Deviation from Ideal Reflow Profile (IPC-J-STD-020)
        """
        ramp_rate = x[..., 0]
        soak_temp = x[..., 1]
        reflow_temp = x[..., 2]
        cool_rate = x[..., 3]
        
        # Ideal Targets
        # Ramp: < 3 C/s (Target 2.0)
        # Soak: 150-200 C (Target 175)
        # Reflow: 240-250 C (Target 245)
        # Cool: < 6 C/s (Target 4.0)
        
        e_ramp = (ramp_rate - 2.0).pow(2)
        e_soak = (soak_temp - 175.0).pow(2)
        e_reflow = (reflow_temp - 245.0).pow(2)
        e_cool = (cool_rate - 4.0).pow(2)
        
        # Penalty for exceeding limits (Soft constraints)
        e_limit = torch.relu(ramp_rate - 3.0) * 100.0 + \
                  torch.relu(cool_rate - 6.0) * 100.0
        
        return e_ramp + e_soak + e_reflow + e_cool + e_limit

prior = PCBPrior()
prior.register()
