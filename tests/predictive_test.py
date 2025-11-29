import sys
import os
import json
import io
from contextlib import redirect_stdout

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation.simulation_oracle import SimulationOracle
from src.twin.shadow_runtime import ShadowRuntime

def test_predictive_twin():
    print("\n--- Testing Predictive Twin Engine ---")
    
    oracle = SimulationOracle()
    
    # 1. Test Single Prediction (1 Hour Horizon)
    print("\n[1] Testing 1-Hour Horizon Prediction...")
    current_state = {"temp": 20.0, "power": 100.0}
    pred = oracle.predict_horizon(current_state, 3600)
    
    print(f"  Input: {current_state}")
    print(f"  Output: {pred}")
    
    if pred['horizon_s'] == 3600:
        print("✅ Horizon Correct.")
    else:
        print("❌ Horizon Mismatch.")
        
    if pred['confidence'] < 1.0:
        print("✅ Confidence Decay Verified.")
    else:
        print("❌ Confidence Decay Failed.")
        
    if pred['predicted_temp'] > 20.0:
        print("✅ Temperature Rise Verified (Heating).")
    else:
        print("❌ Temperature Rise Failed.")

    # 2. Test Runtime Loop (Short Duration)
    print("\n[2] Testing Predictive Runtime Loop...")
    runtime = ShadowRuntime()
    
    f = io.StringIO()
    with redirect_stdout(f):
        runtime.run_predictive_loop(current_state, duration_s=2)
        
    output = f.getvalue()
    print(output)
    
    if "Starting Predictive Twin" in output:
        print("✅ Runtime Started.")
    else:
        print("❌ Runtime Failed to Start.")
        
    if "+3600s:" in output:
        print("✅ 1-Hour Prediction Logged.")
    else:
        print("❌ 1-Hour Prediction Missing.")

if __name__ == "__main__":
    test_predictive_twin()
