import torch
from src.ebm_lib.priors.battery_v1 import prior as battery_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Battery Safety System Demo ===")
    
    # Initial State: High Temp, Voltage Mismatch (Runaway Risk)
    # [Voltage, Temp, SoC]
    x0 = torch.tensor([[4.2, 50.0, 0.8]], dtype=torch.float32)
    e0 = battery_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Runaway Risk)")
    
    # Optimization: Cool down and stabilize voltage
    # Clip SoC to [0, 1], Voltage to [2.5, 4.5], Temp to [0, 100]
    print("\nRunning Safety Control...")
    x_opt = langevin_step(x0, battery_prior.energy, steps=200, step_size=0.05, clip=(0.0, 100.0))
    e_opt = battery_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Safe)")
    
    if e_opt < e0:
        print("\nSUCCESS: Battery stabilized.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
