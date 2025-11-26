import torch
import torch.nn as nn
import abc

class BaseEBDM(nn.Module, abc.ABC):
    """
    Base class for Energy-Based Diffusion Models (EBDM).
    Integrates thermodynamic priors into the diffusion score function.
    """
    def __init__(self, energy_prior_path=None):
        super().__init__()
        self.energy_prior = None
        if energy_prior_path:
            self.load_energy_prior(energy_prior_path)

    def load_energy_prior(self, path):
        """Load the energy map/tensor from disk."""
        # In a real implementation, this would load .npy/.pt
        print(f"Loading energy prior from {path}")
        self.energy_prior = path 

    @abc.abstractmethod
    def score_network(self, x, t):
        """The learned score function s_theta(x, t)."""
        pass

    def energy_gradient(self, x):
        """Compute -grad(E)(x). Override this with domain-specific physics."""
        # Default: return 0 if no analytic energy function provided
        return torch.zeros_like(x)

    def forward(self, x, t):
        """
        Returns the total score: learned_score + energy_pullback.
        """
        learned_score = self.score_network(x, t)
        physics_pull = self.energy_gradient(x)
        
        # Combine: score = score_fn - grad(E)
        # Note: The sign depends on formulation. Here assuming score ~ grad(log p) ~ -grad(E)
        return learned_score + physics_pull
