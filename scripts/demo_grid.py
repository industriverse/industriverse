import torch
from src.ebm_lib.priors.grid_v1 import prior as grid_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Grid Frequency Lock Demo ===")
    
    # Initial State: Freq Drift, High RoCoF
    # [Freq, RoCoF]
    x0 = torch.tensor([[59.2, 0.5]], dtype=torch.float32)
    e0 = grid_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Unstable)")
    
    # Optimization: Lock Freq, Minimize RoCoF
    print("\nRunning Inertia Emulation...")
    x_opt = langevin_step(x0, grid_prior.energy, steps=1000, step_size=0.001)
    e_opt = grid_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Locked)")
    
    if e_opt < e0:
        print("\nSUCCESS: Grid frequency locked.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
