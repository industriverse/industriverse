import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

# Using HybridSolver as the engine for flow prediction
from src.expansion_packs.tse.hybrid_solver import HybridSolver

def run():
    print("\n" + "="*60)
    print(" DEMO 28: DISSIPATIVE FLOW FIELD PREDICTOR")
    print("="*60 + "\n")

    print("Initializing Flow Field (1D Heat/Energy Distribution)...")
    solver = HybridSolver(grid_size=10, diffusion_coeff=0.5)
    
    # Initial state: Hotspot in the middle
    initial_state = [0, 0, 0, 0, 10.0, 10.0, 0, 0, 0, 0]
    solver.initialize(initial_state)
    print(f"T=0.0s: {np.round(solver.state, 2)}")

    print("\nPredicting E(t + delta) using NVP/PDE Hybrid...")
    
    for t in range(1, 6):
        new_state = solver.step(dt=0.2)
        print(f"T={t*0.2:.1f}s: {np.round(new_state, 2)}")

    print("\nPrediction: Energy dissipating outwards as expected.")
    print("\n" + "="*60)
    print(" DEMO COMPLETE: FLOW FIELD PREDICTED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
