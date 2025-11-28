import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class ElectronicsPrior(EnergyPrior):
    name = "electronics_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Power Converter Prior.
        x: [batch, 3] -> [Switching_Freq, Duty_Cycle, Output_Ripple]
        
        Energy = Efficiency Loss + Ripple
        """
        sw_freq = x[..., 0] # kHz
        duty = x[..., 1]    # 0-1
        ripple = x[..., 2]  # mV
        
        # 1. Switching Loss (Proportional to Freq)
        e_sw = 0.01 * sw_freq.pow(2)
        
        # 2. Output Ripple (Minimize)
        e_ripple = 0.1 * ripple.pow(2)
        
        # 3. Duty Cycle Target (e.g., for 12V -> 5V buck, D=0.41)
        e_duty = (duty - 0.41).pow(2) * 100.0
        
        return e_sw + e_ripple + e_duty

prior = ElectronicsPrior()
prior.register()
