import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class BatteryPrior(EnergyPrior):
    name = "battery_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Battery Safety System Prior.
        x: [batch, 3] -> [Voltage, Temperature, SoC]
        
        Energy = Nernst Deviation + Thermal Runaway Risk
        """
        voltage = x[..., 0]
        temp = x[..., 1]
        soc = x[..., 2] # State of Charge (0-1)
        
        # 1. Nernst Equation (Simplified)
        # V_ocv approx 3.0 + 1.0 * SoC
        v_target = 3.0 + 1.0 * soc
        e_nernst = (voltage - v_target).pow(2)
        
        # 2. Thermal Runaway Risk (Exponential Penalty)
        # Critical Temp ~ 60 C (333 K). Let's use Celsius for simplicity here.
        # If Temp > 45, energy skyrockets.
        e_thermal = torch.exp((temp - 45.0) * 0.5)
        
        # 3. SoC Limits (0 to 1)
        e_soc = torch.relu(soc - 1.0) * 100.0 + torch.relu(0.0 - soc) * 100.0
        
        return e_nernst + e_thermal + e_soc

prior = BatteryPrior()
prior.register()
