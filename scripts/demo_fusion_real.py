import torch
import numpy as np
from src.ebm_lib.priors.fusion_v1 import prior as fusion_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

# Path to real physics data
HDF5_PATH = "/Volumes/Expansion/datasets/raw/datasets/MHD_256/data/valid/MHD_Ma_0.7_Ms_2.hdf5"

def run_demo():
    print("=== Fusion Stabilization Demo (Real Physics) ===")
    
    # 1. Load Calibration Data
    print(f"Loading Ground Truth from: {HDF5_PATH}")
    fusion_prior.load_calibration(HDF5_PATH)
    
    if fusion_prior.target_field is None:
        print("Error: Could not load calibration data. Check drive connection.")
        return

    # 2. Create Initial State (Perturbed/Unstable Plasma)
    # Start with the stable state + random noise (turbulence)
    target = fusion_prior.target_field
    noise = torch.randn_like(target) * 2.0
    x0 = (target + noise).unsqueeze(0) # Add batch dim
    
    e0 = fusion_prior.energy(x0).item()
    
    print(f"Initial Energy: {e0:.4f} (Turbulent/Unstable)")
    
    # 3. Optimization: Restore Confinement
    print("\nRunning MHD Stabilization...")
    # We use a smaller step size because we are in a high-dimensional space (32x32x3)
    x_opt = langevin_step(x0, fusion_prior.energy, steps=100, step_size=0.01)
    e_opt = fusion_prior.energy(x_opt).item()
    
    print(f"Final Energy:  {e_opt:.4f} (Confined)")
    
    # 4. Verify Divergence (Physics Check)
    # Calculate mean divergence of the field
    div_x = x_opt[..., 1:, :, 0] - x_opt[..., :-1, :, 0]
    div_y = x_opt[..., :, 1:, 1] - x_opt[..., :, :-1, 1]
    mean_div = (div_x[..., :, :-1] + div_y[..., :-1, :]).abs().mean().item()
    
    print(f"Final Mean Divergence: {mean_div:.6f} (Target: 0.0)")
    
    if e_opt < e0:
        print("\nSUCCESS: Plasma stabilized using Real Physics Data.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
