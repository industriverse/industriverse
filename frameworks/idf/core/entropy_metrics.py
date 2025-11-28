import numpy as np
from typing import List
from .energy_field import EnergyField

class EntropyMetrics:
    """
    Calculates thermodynamic metrics for diffusion trajectories.
    """
    
    @staticmethod
    def calculate_trajectory_entropy(trajectory: List[np.ndarray], field: EnergyField) -> float:
        """
        Calculate the Shannon entropy of the trajectory distribution.
        Approximated by the spread of visited states on the energy map.
        """
        # Convert list to array
        points = np.array(trajectory)
        
        # Simple histogram entropy
        # Discretize domain into 10x10 bins
        H, _, _ = np.histogram2d(points[:, 0], points[:, 1], bins=10, range=[[0, 1], [0, 1]])
        
        # Normalize to probability
        P = H / np.sum(H)
        
        # Shannon Entropy: -Sum(p * log(p))
        # Filter zero probabilities
        P_nz = P[P > 0]
        entropy = -np.sum(P_nz * np.log(P_nz))
        
        return float(entropy)

    @staticmethod
    def calculate_energy_drift(trajectory: List[np.ndarray], field: EnergyField) -> float:
        """
        Calculate the change in energy from start to end.
        Should be negative (downhill) for optimization.
        """
        start_energy = field.get_energy(trajectory[0])
        end_energy = field.get_energy(trajectory[-1])
        return end_energy - start_energy
