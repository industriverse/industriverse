import sys
import os

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.dgm_engine.core.quantum_cnc_engine import QuantumCNCEngine
from src.twin.shadow_runtime import ShadowRuntime

def test_simulation():
    print("\n--- Testing Simulation Upgrades ---")
    
    # 1. Test Quantum Simulator (Simulated Annealing)
    print("\n[1] Testing Quantum Simulator (TSP)...")
    engine = QuantumCNCEngine()
    
    # Define 5 cities in a line: (0,0), (1,0), (2,0), (3,0), (4,0)
    # Optimal path length is 4.0
    waypoints = [(0,0), (4,0), (2,0), (1,0), (3,0)]
    
    optimized_path = engine.optimize_toolpath(waypoints, {})
    print(f"  Optimized Path: {optimized_path}")
    
    # Calculate length
    import math
    length = 0
    for i in range(len(optimized_path)-1):
        p1 = optimized_path[i]
        p2 = optimized_path[i+1]
        length += math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)
        
    print(f"  Path Length: {length}")
    
    if length <= 4.01: # Allow tiny float error
        print("✅ Quantum Simulator Found Optimal Path.")
    else:
        print(f"❌ Quantum Simulator Suboptimal (Length: {length}).")

    # 2. Test Telemetry Replay
    print("\n[2] Testing Telemetry Replay...")
    runtime = ShadowRuntime()
    
    # Test deterministic fallback (since no H5 file exists yet)
    print("  Running Deterministic Replay (Fallback)...")
    runtime.run_replay_loop(h5_path="non_existent.h5")
    print("✅ Replay Loop Executed.")

if __name__ == "__main__":
    test_simulation()
