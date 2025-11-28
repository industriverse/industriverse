import torch
from src.ebm_lib.priors.heat_v1 import prior as heat_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== HVAC Optimizer Demo ===")
    
    # Initial State: Too hot, High Power
    # [Temp, Power]
    x0 = torch.tensor([[26.0, 100.0]], dtype=torch.float32)
    e0 = heat_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Wasteful)")
    
    # Optimization: Comfort + Efficiency
    print("\nRunning HVAC Control...")
    x_opt = langevin_step(x0, heat_prior.energy, steps=200, step_size=0.1)
    e_opt = heat_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Optimal)")
    
    if e_opt < e0:
        print("\nSUCCESS: HVAC optimized.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
