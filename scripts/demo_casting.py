import torch
from src.ebm_lib.priors.casting_v1 import prior as casting_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Metallurgy Casting Demo ===")
    
    # Initial State: Cooling too fast (Crack Risk)
    # [Cooling_Rate, Nucleation_Rate]
    x0 = torch.tensor([[100.0, 500.0]], dtype=torch.float32)
    e0 = casting_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Crack Risk)")
    
    # Optimization: Optimal Microstructure
    print("\nRunning Solidification Control...")
    x_opt = langevin_step(x0, casting_prior.energy, steps=200, step_size=0.5)
    e_opt = casting_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Strong Alloy)")
    
    if e_opt < e0:
        print("\nSUCCESS: Microstructure optimized.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
