import torch
from src.ebm_lib.priors.lifecycle_v1 import prior as yield_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Yield Forecaster Demo ===")
    
    # Initial State: High Variance, Mean Shift (Low Yield)
    # [Variance, Mean_Shift]
    x0 = torch.tensor([[2.0, 1.5]], dtype=torch.float32)
    e0 = yield_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Low Yield)")
    
    # Optimization: Six Sigma Control
    print("\nRunning Process Control...")
    x_opt = langevin_step(x0, yield_prior.energy, steps=200, step_size=0.01)
    e_opt = yield_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (High Yield)")
    
    if e_opt < e0:
        print("\nSUCCESS: Yield forecast improved.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
