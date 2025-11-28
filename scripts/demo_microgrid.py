import torch
from src.ebm_lib.priors.microgrid_v1 import prior as microgrid_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Microgrid Balancer Demo ===")
    
    # Initial State: Gen < Load, Freq sagging (Blackout Risk)
    # [Gen, Load, Freq]
    x0 = torch.tensor([[80.0, 100.0, 59.5]], dtype=torch.float32)
    e0 = microgrid_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Blackout Risk)")
    
    # Optimization: Balance Load and Restore Freq
    print("\nRunning Load Balancing...")
    x_opt = langevin_step(x0, microgrid_prior.energy, steps=200, step_size=0.1)
    e_opt = microgrid_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Balanced)")
    
    if e_opt < e0:
        print("\nSUCCESS: Grid balanced.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
