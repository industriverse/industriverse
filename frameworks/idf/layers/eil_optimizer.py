import numpy as np
import logging
from typing import Dict, Any, Optional
from ..core.energy_field import EnergyField
from ..core.diffusion_dynamics import DiffusionDynamics
from ..core.entropy_metrics import EntropyMetrics

logger = logging.getLogger(__name__)

class EILOptimizer:
    """
    Energy Intelligence Layer (EIL) Optimizer.
    Uses diffusion dynamics to find optimal (low-energy) configurations.
    """
    
    def __init__(self, map_name: str = "default_map"):
        self.field = EnergyField(map_name)
        # Low temperature for optimization (annealing)
        self.dynamics = DiffusionDynamics(self.field, learning_rate=0.05, temperature=0.01)
        
    def optimize_configuration(self, initial_config: Optional[np.ndarray] = None, steps: int = 500) -> Dict[str, Any]:
        """
        Run diffusion to optimize the configuration.
        """
        if initial_config is None:
            # Start from random noise
            initial_config = np.random.rand(*self.field.shape)
            
        # Run diffusion
        trajectory = self.dynamics.sample_trajectory(initial_config, steps=steps)
        final_config = trajectory[-1]
        
        # Calculate metrics
        start_energy = self.field.get_energy(initial_config)
        final_energy = self.field.get_energy(final_config)
        entropy = EntropyMetrics.calculate_trajectory_entropy(trajectory, self.field)
        
        return {
            "initial_config": initial_config.tolist(),
            "final_config": final_config.tolist(),
            "start_energy": start_energy,
            "final_energy": final_energy,
            "energy_delta": final_energy - start_energy,
            "trajectory_entropy": entropy,
            "converged": bool(abs(final_energy - self.field.get_energy(trajectory[-2])) < 1e-4)
        }

    def generate_diversity(self, count: int = 5) -> list:
        """
        Generate multiple diverse high-quality configurations.
        Uses higher temperature to explore basins.
        """
        results = []
        # Higher temp for exploration
        explorer = DiffusionDynamics(self.field, learning_rate=0.05, temperature=0.2)
        
        for _ in range(count):
            start = np.random.rand(*self.field.shape)
            traj = explorer.sample_trajectory(start, steps=200)
            final = traj[-1]
            energy = self.field.get_energy(final)
            results.append({"config": final.tolist(), "energy": energy})
            
        # Sort by energy
        results.sort(key=lambda x: x["energy"])
        return results
