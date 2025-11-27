import torch
import numpy as np
import os
from typing import Dict

PRIOR_REGISTRY = {}

class EnergyPrior:
    name = "base_prior"
    
    def __init__(self):
        self.ground_truth = None
        self.load_energy_map()

    def load_energy_map(self):
        """Auto-load .npz energy map if it exists."""
        map_path = f"src/ebm_lib/energy_maps/{self.name}.npz"
        if os.path.exists(map_path):
            try:
                data = np.load(map_path)
                self.ground_truth = torch.tensor(data['energy_map'], dtype=torch.float32)
                # print(f"[{self.name}] Loaded Energy Map from {map_path}")
            except Exception as e:
                print(f"[{self.name}] Failed to load map: {e}")

    def energy(self, x: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    def grad(self, x: torch.Tensor) -> torch.Tensor:
        """Compute gradient of energy with respect to x."""
        x = x.clone().requires_grad_(True)
        e = self.energy(x).sum()
        g = torch.autograd.grad(e, x)[0]
        return g

    def register(self):
        PRIOR_REGISTRY[self.name] = self
