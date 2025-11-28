import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class CastingPrior(EnergyPrior):
    name = "casting_v1"
    
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Metallurgy Casting Prior.
        x: [batch, 2] -> [Cooling_Rate, Nucleation_Rate]
        
        Energy = Deviation from Hall-Petch Optimal
        Goal: Fine grain structure (High Nucleation, Fast Cooling) but avoid cracks.
        """
        cooling_rate = x[..., 0]
        nucleation_rate = x[..., 1]
        
        # Hall-Petch Relation: Strength ~ 1/sqrt(grain_size)
        # Grain size ~ Cooling_Rate^(-n)
        # We want to maximize Cooling Rate (within limits) and Nucleation
        
        # Target: Cooling Rate = 50 K/s, Nucleation = 1000 sites/s
        e_cool = (cooling_rate - 50.0).pow(2)
        e_nuc = (nucleation_rate - 1000.0).pow(2)
        
        # Crack Formation Penalty: If Cooling Rate > 80, cracks form
        e_crack = torch.relu(cooling_rate - 80.0) * 1000.0
        
        return e_cool + e_nuc + e_crack

prior = CastingPrior()
prior.register()
