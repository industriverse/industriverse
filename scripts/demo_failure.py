import torch
from src.ebm_lib.priors.failure_v1 import prior as failure_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Failure Predictor Demo ===")
    
    # Initial State: High Entropy, High Vibration (Failure Imminent)
    # [Entropy, Vibration]
    x0 = torch.tensor([[0.8, 2.5]], dtype=torch.float32)
    e0 = failure_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Failure Imminent)")
    
    # Optimization: Return to Safe Envelope
    print("\nRunning Prognostics Control...")
    x_opt = langevin_step(x0, failure_prior.energy, steps=200, step_size=0.01)
    e_opt = failure_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Safe)")
    
    if e_opt < e0:
        print("\nSUCCESS: Failure risk mitigated.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
