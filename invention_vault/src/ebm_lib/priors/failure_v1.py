import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class FailurePrior(EnergyPrior):
    name = "failure_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Failure Predictor Prior.
        x: [batch, 2] -> [Entropy_Rate, Vibration_Energy]
        
        Energy = Deviation from Safe Operating Envelope
        """
        entropy_rate = x[..., 0]
        vibration = x[..., 1]
        
        # 1. Entropy Rate (accumulating disorder)
        # Safe limit: 0.5 bits/s
        e_entropy = torch.relu(entropy_rate - 0.5) * 100.0
        
        # 2. Vibration Energy (Safe limit: 1.0 g)
        e_vib = torch.relu(vibration - 1.0) * 50.0
        
        # 3. Regularization (Prefer lower values)
        e_reg = 0.1 * entropy_rate.pow(2) + 0.1 * vibration.pow(2)
        
        return e_entropy + e_vib + e_reg

prior = FailurePrior()
prior.register()
