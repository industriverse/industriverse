
import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class AssemblyPrior(EnergyPrior):
    name = "assembly_v1"
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        # Placeholder physics for assembly
        # x: [batch, features]
        target = torch.zeros_like(x)
        # Simple quadratic potential (harmonic oscillator)
        return 0.5 * (x - target).pow(2).sum(dim=-1)

prior = AssemblyPrior()
prior.register()
