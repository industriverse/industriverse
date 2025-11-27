import torch
from src.ebm_lib.priors.motor_v1 import prior as motor_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Motor Harmonics Solver Demo ===")
    
    # Initial State: Inefficient currents (High Id) and wrong torque (Wrong Iq)
    # [Id, Iq, Speed]
    # Target Torque ~ 10.0 => Iq should be ~ 6.66 (since k=1.5)
    # Id should be 0.0
    x0 = torch.tensor([[2.0, 0.0, 100.0]], dtype=torch.float32)
    e0 = motor_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Inefficient/Ripple)")
    
    # Optimization: Minimize Id (heat) and match Torque
    print("\nRunning Harmonic Elimination...")
    x_opt = langevin_step(x0, motor_prior.energy, steps=200, step_size=0.05)
    e_opt = motor_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Optimized)")
    
    # Check physics
    id_final = x_opt[0, 0].item()
    iq_final = x_opt[0, 1].item()
    torque = 1.5 * iq_final
    
    print(f"  > Final Id (Heat): {id_final:.4f} (Target: 0.0)")
    print(f"  > Final Torque:    {torque:.4f} (Target: 10.0)")
    
    if e_opt < e0 and abs(id_final) < 0.5:
        print("\nSUCCESS: Motor efficiency optimized.")
    else:
        print("\nFAILURE: Optimization failed.")

if __name__ == "__main__":
    run_demo()
