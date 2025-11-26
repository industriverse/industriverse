import sys
import os
import time
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.overseer_system.energy_governor import EnergyGovernor

def run():
    print("\n" + "="*60)
    print(" DEMO 36: GPU THROTTLING DECISION ENGINE")
    print("="*60 + "\n")

    # Budget of 500 Joules
    governor = EnergyGovernor(max_joules_budget=500.0)

    tasks = [
        {"name": "Train_LLM_Layer1", "cost": 150},
        {"name": "Inference_Batch_A", "cost": 50},
        {"name": "Train_LLM_Layer2", "cost": 200},
        {"name": "Data_Preprocess", "cost": 80},
        {"name": "Train_LLM_Layer3", "cost": 150} # Should fail
    ]

    print("Submitting Compute Jobs to Governor...")
    for task in tasks:
        time.sleep(0.5)
        approved = governor.request_action(task["name"], task["cost"])
        
        if approved:
            print(f"  -> Executing {task['name']} on GPU Cluster...")
        else:
            print(f"  -> THROTTLED: {task['name']} queued for next window.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: COMPUTE GOVERNED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
