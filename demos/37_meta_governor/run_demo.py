import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())

from src.overseer_system.energy_governor import MetaGovernor

def run():
    print("\n" + "="*60)
    print(" DEMO 37: META-GOVERNOR SENSITIVITY TUNER")
    print("="*60 + "\n")

    meta = MetaGovernor(base_sensitivity=0.8)
    print(f"Initial Sensitivity: {meta.sensitivity:.2f}")

    scenarios = [
        {"desc": "Calm Night Shift", "volatility": 0.1},
        {"desc": "Morning Shift Start", "volatility": 0.4},
        {"desc": "Cyberattack Detected (Chaos)", "volatility": 0.9},
        {"desc": "Post-Attack Recovery", "volatility": 0.3}
    ]

    for s in scenarios:
        time.sleep(0.5)
        print(f"\n--- Scenario: {s['desc']} (Vol: {s['volatility']}) ---")
        new_sens = meta.update(s['volatility'])
        
        if new_sens < 0.4:
            print("  -> Action: LOWERING Sensitivity to prevent False Alarms.")
        elif new_sens > 0.8:
            print("  -> Action: RAISING Sensitivity to catch subtle anomalies.")
        else:
            print("  -> Action: Maintaining balanced posture.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: SENSITIVITY TUNED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
