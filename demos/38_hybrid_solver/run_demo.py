import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

from src.expansion_packs.tse.hybrid_solver import HybridSolver

def run():
    print("\n" + "="*60)
    print(" DEMO 38: PDE + NEURAL HYBRID SOLVER")
    print("="*60 + "\n")

    solver = HybridSolver(grid_size=10, diffusion_coeff=0.2)
    
    # Initial state: Step function
    init_state = [0, 0, 0, 10, 10, 10, 10, 0, 0, 0]
    solver.initialize(init_state)
    print(f"T=0.0: {np.round(solver.state, 1)}")

    print("\nRunning Simulation (Classical Diffusion + Neural Correction)...")
    for i in range(5):
        state = solver.step(dt=0.5)
        print(f"T={(i+1)*0.5:.1f}: {np.round(state, 1)}")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: HYBRID PHYSICS SOLVED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
