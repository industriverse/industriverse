from abc import ABC, abstractmethod
from typing import Dict
import torch

PRIOR_REGISTRY: Dict[str, "EnergyPrior"] = {}

class EnergyPrior(ABC):
    name: str = "base"

    @abstractmethod
    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """Return scalar energy for configuration x"""
        pass

    def grad(self, x: torch.Tensor) -> torch.Tensor:
        """Compute gradient of energy with respect to x."""
        x = x.clone().requires_grad_(True)
        e = self.energy(x).sum()
        g = torch.autograd.grad(e, x)[0]
        return g

    def register(self):
        PRIOR_REGISTRY[self.name] = self
