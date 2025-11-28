import numpy as np
import logging
from typing import List, Dict, Any
from .energy_field import EnergyField

logger = logging.getLogger(__name__)

class DiffusionDynamics:
    """
    Implements Energy-Based Diffusion (Langevin Dynamics).
    x_{t+1} = x_t - eta * grad_E(x_t) + sqrt(2 * eta * T) * noise
    """
    
    def __init__(self, field: EnergyField, learning_rate: float = 0.01, temperature: float = 1.0):
        self.field = field
        self.eta = learning_rate
        self.temp = temperature

    def step(self, x_t: np.ndarray) -> np.ndarray:
        """
        Perform one diffusion step.
        """
        grad = self.field.get_gradient(x_t)
        noise = np.random.randn(*x_t.shape)
        
        # Langevin update
        # Drift term: -eta * grad
        drift = -self.eta * grad
        
        # Diffusion term: sqrt(2 * eta * T) * noise
        diffusion = np.sqrt(2 * self.eta * self.temp) * noise
        
        x_next = x_t + drift + diffusion
        
        # Clip to domain [0, 1]
        x_next = np.clip(x_next, 0.0, 1.0)
        
        return x_next

    def sample_trajectory(self, x_init: np.ndarray, steps: int = 100) -> List[np.ndarray]:
        """
        Generate a full diffusion trajectory from x_init.
        """
        trajectory = [x_init]
        x_curr = x_init.copy()
        
        for _ in range(steps):
            x_curr = self.step(x_curr)
            trajectory.append(x_curr.copy())
            
        return trajectory

    def find_equilibrium(self, x_init: np.ndarray, max_steps: int = 1000, tol: float = 1e-4) -> np.ndarray:
        """
        Run diffusion until convergence (equilibrium).
        """
        x_curr = x_init.copy()
        for i in range(max_steps):
            x_prev = x_curr.copy()
            x_curr = self.step(x_curr)
            
            # Check convergence (if noise is low enough, or just drift is small)
            # For pure optimization, we might set temp=0
            if np.linalg.norm(x_curr - x_prev) < tol:
                logger.debug(f"Converged in {i} steps.")
                break
                
        return x_curr
