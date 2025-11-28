from abc import ABC, abstractmethod
import numpy as np

class EnergyPrior(ABC):
    """
    Abstract Base Class for Industriverse Energy Priors.
    
    This defines the interface for thermodynamic constraints.
    Implementations are available in the Enterprise Edition.
    """
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight

    @abstractmethod
    def energy(self, state: np.ndarray) -> float:
        """
        Calculates the energy (unlikelihood) of a given state.
        Lower energy = higher physical validity.
        """
        pass

    @abstractmethod
    def gradient(self, state: np.ndarray) -> np.ndarray:
        """
        Calculates the gradient of energy with respect to the state.
        Used for Langevin Dynamics and EBDM guidance.
        """
        pass
