import numpy as np
import logging
from typing import Tuple, Optional, Dict
import sys
import os

# Add src to path to import thermodynamic_layer
sys.path.append(os.path.join(os.path.dirname(__file__), "../../../src"))

from thermodynamic_layer.energy_atlas import EnergyAtlas

logger = logging.getLogger(__name__)

class EnergyField:
    """
    Differentiable abstraction of an Energy Map.
    Wraps EnergyAtlas to provide gradient access for diffusion.
    """
    
    def __init__(self, map_name: str, atlas: Optional[EnergyAtlas] = None):
        self.map_name = map_name
        self.atlas = atlas or EnergyAtlas()
        self.data = self.atlas.get_map(map_name)
        
        if self.data is None:
            logger.warning(f"Energy map {map_name} not found. Using synthetic.")
            self.data = self.atlas._generate_synthetic_mock(map_name)
            
        self.shape = self.data.shape
        # Pre-compute gradients for static maps (simple finite difference)
        self.grad_x, self.grad_y = np.gradient(self.data)

    def get_energy(self, x: np.ndarray) -> float:
        """
        Get energy at continuous coordinate x (normalized 0-1).
        Uses bilinear interpolation.
        """
        # Map 0-1 to pixel coordinates
        h, w = self.shape
        i = np.clip(x[0] * (h - 1), 0, h - 1)
        j = np.clip(x[1] * (w - 1), 0, w - 1)
        
        # Integer parts
        i0, j0 = int(i), int(j)
        i1, j1 = min(i0 + 1, h - 1), min(j0 + 1, w - 1)
        
        # Weights
        di, dj = i - i0, j - j0
        
        # Bilinear interp
        e00 = self.data[i0, j0]
        e10 = self.data[i1, j0]
        e01 = self.data[i0, j1]
        e11 = self.data[i1, j1]
        
        energy = (e00 * (1 - di) * (1 - dj) +
                  e10 * di * (1 - dj) +
                  e01 * (1 - di) * dj +
                  e11 * di * dj)
                  
        return float(energy)

    def get_gradient(self, x: np.ndarray) -> np.ndarray:
        """
        Get energy gradient at continuous coordinate x.
        """
        h, w = self.shape
        i = np.clip(x[0] * (h - 1), 0, h - 1)
        j = np.clip(x[1] * (w - 1), 0, w - 1)
        
        i0, j0 = int(i), int(j)
        
        gx = self.grad_x[i0, j0]
        gy = self.grad_y[i0, j0]
        
        return np.array([gx, gy])

    def get_boltzmann_weight(self, x: np.ndarray, temperature: float = 1.0) -> float:
        """
        Calculate exp(-E/kT).
        """
        E = self.get_energy(x)
        return np.exp(-E / temperature)
