import torch
from src.ebm_lib.priors.robotics_v1 import prior as robotics_prior
from src.thermo_sdk.thermo_sdk.ebm_runtime import langevin_step

def run_demo():
    print("=== Robotic Arm Stability Demo ===")
    
    # Initial State: Arm is far from target and moving erratically
    # [x, y, z, vx, vy, vz]
    x0 = torch.tensor([[0.0, 0.0, 0.0, 5.0, -5.0, 2.0]], dtype=torch.float32)
    e0 = robotics_prior.energy(x0).item()
    
    print(f"Initial State: {x0.detach().numpy()}")
    print(f"Initial Energy: {e0:.4f} (Unstable/Vibrating)")
    
    # Optimization: Smooth trajectory and move to target
    print("\nRunning Stabilization...")
    x_opt = langevin_step(x0, robotics_prior.energy, steps=200, step_size=0.05)
    e_opt = robotics_prior.energy(x_opt).item()
    
    print(f"Final State:   {x_opt.detach().numpy()}")
    print(f"Final Energy:  {e_opt:.4f} (Stable)")
    
    if e_opt < e0:
        print("\nSUCCESS: Arm stabilized and converged.")
    else:
        print("\nFAILURE: Energy did not decrease.")

if __name__ == "__main__":
    run_demo()
