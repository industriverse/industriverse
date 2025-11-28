import torch
from src.ebm_lib.priors.electronics_v1 import prior as electronics_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Power Converter Demo ===")
    
    # Initial State: High Ripple, Wrong Duty
    # [Sw_Freq, Duty, Ripple]
    x0 = torch.tensor([[100.0, 0.6, 50.0]], dtype=torch.float32)
    e0 = electronics_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Inefficient)")
    
    # Optimization: Minimize Loss & Ripple, Fix Duty
    # Clip Duty to [0, 1]
    print("\nRunning Converter Optimization...")
    x_opt = langevin_step(x0, electronics_prior.energy, steps=500, step_size=0.001, clip=(0.0, 1000.0))
    e_opt = electronics_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Efficient)")
    
    if e_opt < e0:
        print("\nSUCCESS: Converter optimized.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
