import torch
import h5py
import numpy as np
from src.thermo_sdk.thermo_sdk.energy_prior import EnergyPrior, PRIOR_REGISTRY

class FusionPrior(EnergyPrior):
    name = "fusion_v1"
    
    def __init__(self, target_pos=None):
        super().__init__()
        # Default target if none provided
        self.default_target = torch.tensor([1.0, 1.0, 1.0]) # x, y, z
        self.target_field = None # Keep this as it's used in energy method
        # The hdf5_path loading logic is removed from __init__ as per the change.
            
    def load_calibration(self, path):
        """Load real MHD data to set the target stable state."""
        try:
            with h5py.File(path, 'r') as f:
                # Load a 2D slice of the magnetic field at t=50 (stable), z=128
                # Shape: (1, 100, 256, 256, 256, 3)
                # We take [0, 50, 128, :, :, :] -> (256, 256, 3)
                # For demo simplicity, we downsample to (32, 32, 3)
                b_field = f['t1_fields/magnetic_field'][0, 50, 128, ::8, ::8, :]
                self.target_field = torch.tensor(b_field, dtype=torch.float32)
                print(f"Loaded calibration data from {path}. Shape: {self.target_field.shape}")
        except Exception as e:
            print(f"Failed to load calibration: {e}")

    def load_energy_map(self):
        """Override to also set target_field from the loaded map."""
        super().load_energy_map()
        if self.ground_truth is not None:
            self.target_field = torch.tensor(self.ground_truth, dtype=torch.float32)

    def energy(self, x: torch.Tensor) -> torch.Tensor:
        """
        Fusion Plasma Confinement Prior (calibrated).
        x: [batch, 32, 32, 3] -> Magnetic Field B_x, B_y, B_z
        """
        # If no calibration, fallback to simple potential
        if self.target_field is None:
            return 0.5 * x.pow(2).sum(dim=-1).mean()
            
        # 1. Deviation from Stable MHD State (Ground Truth)
        target = self.target_field.to(x.device)
        if x.shape[0] > 1 and len(x.shape) > len(target.shape):
             target = target.expand(x.shape[0], -1, -1, -1)
             
        e_deviation = (x - target).pow(2).sum(dim=-1).mean(dim=(-1, -2))
        
        # 2. Divergence Penalty (Maxwell: div B = 0)
        # Simple discrete divergence
        div_x = x[..., 1:, :, 0] - x[..., :-1, :, 0]
        div_y = x[..., :, 1:, 1] - x[..., :, :-1, 1]
        # Pad to match shapes
        e_div = (div_x[..., :, :-1] + div_y[..., :-1, :]).pow(2).mean(dim=(-1, -2))
        
        return e_deviation + 1.0 * e_div

prior = FusionPrior()
prior.register()
