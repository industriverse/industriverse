from typing import Any, Dict, Protocol
from src.ebm_lib.base import EnergyPrior

class EBDM(Protocol):
    """
    Protocol for Energy-Based Diffusion Models in the SCF.
    """
    def energy(self, state: Dict[str, Any]) -> float:
        ...
    
    def grad(self, state: Dict[str, Any]) -> Dict[str, Any]:
        ...

class EBDMAdapter:
    """
    Adapts the existing EnergyPrior from ebm_lib to the SCF EBDM interface.
    """
    def __init__(self, prior: EnergyPrior):
        self.prior = prior

    def energy(self, state: Dict[str, Any]) -> float:
        return self.prior.energy(state)

    def grad(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return self.prior.grad(state)
