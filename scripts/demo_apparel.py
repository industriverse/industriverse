import torch
from src.ebm_lib.priors.apparel_v1 import prior as apparel_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Apparel Tensioner Demo ===")
    
    # Initial State: Uneven tension (Wrinkles)
    # [T1, T2, T3, T4]
    x0 = torch.tensor([[2.0, 8.0, 3.0, 7.0]], dtype=torch.float32)
    e0 = apparel_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Wrinkled)")
    
    # Optimization: Equalize tension
    print("\nRunning Tension Optimization...")
    x_opt = langevin_step(x0, apparel_prior.energy, steps=200, step_size=0.1)
    e_opt = apparel_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Smooth)")
    
    if e_opt < e0:
        print("\nSUCCESS: Fabric tension optimized.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
