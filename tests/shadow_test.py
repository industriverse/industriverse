import sys
import os
import io
from contextlib import redirect_stdout

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.twin.shadow_runtime import ShadowRuntime

def test_shadow_runtime():
    print("\n--- Testing Shadow Twin Runtime ---")
    
    runtime = ShadowRuntime()
    program = [{"op": "OP_MOVE", "params": {"x": 100, "y": 50}}]
    
    # Capture output to verify behavior
    f = io.StringIO()
    with redirect_stdout(f):
        runtime.run_shadow_loop(program)
        
    output = f.getvalue()
    print(output) # Print to real stdout for visibility
    
    # Verification
    if "Starting Shadow Twin" in output:
        print("✅ Runtime started.")
    else:
        print("❌ Runtime failed to start.")
        
    if "System Nominal" in output:
        print("✅ Nominal state detected.")
    else:
        print("❌ Nominal state NOT detected.")
        
    if "ANOMALY DETECTED" in output:
        print("✅ Anomaly detected (Drift Simulation successful).")
    else:
        print("❌ Anomaly NOT detected (Drift failed).")

if __name__ == "__main__":
    test_shadow_runtime()
