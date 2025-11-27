import torch
from src.ebm_lib.priors.qctherm_v1 import prior as thermal_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Thermal Runaway Predictor Demo ===")
    
    # Initial State: Surface Cold, Subsurface Hot (Hidden Defect)
    # [Surface, Subsurface]
    x0 = torch.tensor([[30.0, 120.0]], dtype=torch.float32)
    e0 = thermal_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Hidden Defect)")
    
    # Optimization: Restore Correlation (or detect anomaly)
    # In a real predictor, we wouldn't change the state, we'd flag it.
    # But here we show the "healthy" state the system SHOULD be in.
    print("\nRunning Anomaly Resolution...")
    x_opt = langevin_step(x0, thermal_prior.energy, steps=200, step_size=0.1)
    e_opt = thermal_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Healthy)")
    
    if e_opt < e0:
        print("\nSUCCESS: Thermal anomaly resolved.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
