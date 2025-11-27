import torch
from src.ebm_lib.priors.wafer_v1 import prior as wafer_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Wafer Thermal Controller Demo ===")
    
    # Initial State: Uneven heating (Thermal Stress)
    # [Zone1, Zone2, Zone3, Zone4, Zone5]
    x0 = torch.tensor([[900.0, 1100.0, 950.0, 1050.0, 1000.0]], dtype=torch.float32)
    e0 = wafer_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Warping Risk)")
    
    # Optimization: Uniformity and Target Matching
    print("\nRunning Thermal Profiling...")
    x_opt = langevin_step(x0, wafer_prior.energy, steps=500, step_size=0.01)
    e_opt = wafer_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Uniform)")
    
    if e_opt < e0:
        print("\nSUCCESS: Wafer temperature uniform.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
