import torch
from src.ebm_lib.priors.pcbmfg_v1 import prior as pcb_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== PCB Reflow Optimizer Demo ===")
    
    # Initial State: Too hot, too fast (Defect Risk)
    # [Ramp, Soak, Reflow, Cool]
    x0 = torch.tensor([[5.0, 200.0, 260.0, 10.0]], dtype=torch.float32)
    e0 = pcb_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Defect Risk)")
    
    # Optimization: Match IPC Standard
    print("\nRunning Reflow Optimization...")
    x_opt = langevin_step(x0, pcb_prior.energy, steps=200, step_size=0.1)
    e_opt = pcb_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (IPC Compliant)")
    
    if e_opt < e0:
        print("\nSUCCESS: Reflow profile optimized.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
