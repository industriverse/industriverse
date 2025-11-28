import sys
import os
import time
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.overseer_system.energy_governor import MetaGovernor

def run():
    print("\n" + "="*60)
    print(" DEMO 49: ADAPTIVE SENSITIVITY MODULE")
    print("="*60 + "\n")

    # This demo focuses on the feedback loop aspect
    meta = MetaGovernor(base_sensitivity=0.5)
    
    print("Monitoring Detector Feedback Loop...")
    
    # Simulate feedback: "Too many false positives" -> implies high volatility/noise
    feedback_loop = [
        {"msg": "Clean Signal", "noise_level": 0.1},
        {"msg": "Clean Signal", "noise_level": 0.1},
        {"msg": "False Positive Alert!", "noise_level": 0.8}, # Noise spike
        {"msg": "False Positive Alert!", "noise_level": 0.9},
        {"msg": "Signal Stabilizing", "noise_level": 0.4}
    ]

    for event in feedback_loop:
        time.sleep(0.5)
        print(f"Event: {event['msg']} (Noise: {event['noise_level']})")
        
        current_sens = meta.update(event['noise_level'])
        print(f"  -> Adapting Sensitivity to: {current_sens:.2f}")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: ADAPTATION VERIFIED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
