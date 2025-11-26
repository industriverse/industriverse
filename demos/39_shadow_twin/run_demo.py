import sys
import os
import time
import copy

# Add project root to path
sys.path.append(os.getcwd())

def run():
    print("\n" + "="*60)
    print(" DEMO 39: SHADOW TWIN GENERATOR")
    print("="*60 + "\n")

    physical_asset = {
        "id": "TURBINE_001",
        "rpm": 3000,
        "temp": 120,
        "vibration": 0.5
    }
    print(f"Physical Asset State: {physical_asset}")

    print("\nForking Shadow Twin for Simulation...")
    time.sleep(0.5)
    
    # Create deep copy
    shadow_twin = copy.deepcopy(physical_asset)
    shadow_twin["id"] = "TURBINE_001_SHADOW"
    shadow_twin["mode"] = "SIMULATION"
    
    print(f"Shadow Twin Created: {shadow_twin}")

    print("\nRunning Stress Test on Shadow Twin (Safe Mode)...")
    shadow_twin["rpm"] = 4500 # Overspeed test
    
    if shadow_twin["rpm"] > 4000:
        print("  -> Shadow Twin Failure Detected at 4500 RPM.")
        print("  -> Physical Asset Unharmed.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: TWIN SIMULATED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
