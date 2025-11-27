import torch
from src.ebm_lib.priors.fusion_v1 import prior as fusion_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Fusion Stabilization Demo ===")
    
    # 1. Initial State (High Energy / Unstable)
    # [beta, leakage, temperature]
    x0 = torch.tensor([[0.05, 0.05, 1.2e7]], dtype=torch.float32)
    e0 = fusion_prior.energy(x0).item()
    print(f"Initial State: {x0.numpy()}")
    print(f"Initial Energy: {e0:.4f} (Unstable)")
    
    # 2. Optimization (Langevin Sampling)
    print("\nRunning Thermodynamic Optimization...")
    x_opt = langevin_step(x0, fusion_prior.energy, steps=100, step_size=1e-3)
    e_opt = fusion_prior.energy(x_opt).item()
    
    # 3. Final State (Low Energy / Stable)
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Stable)")
    
    if e_opt < e0:
        print("\nSUCCESS: Energy reduced (Entropy minimized).")
    else:
        print("\nFAILURE: Energy did not decrease.")

if __name__ == "__main__":
    run_demo()
