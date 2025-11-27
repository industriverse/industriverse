
import torch
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class SurfacePrior(EnergyPrior):
    name = "surface_v1"
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        # Placeholder physics for surface
        # x: [batch, features]
        target = torch.zeros_like(x)
        # Simple quadratic potential (harmonic oscillator)
        return 0.5 * (x - target).pow(2).sum(dim=-1)

prior = SurfacePrior()
prior.register()
