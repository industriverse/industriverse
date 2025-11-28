import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())

from src.overseer_system.energy_governor import EnergyGovernor

def run():
    print("\n" + "="*60)
    print(" DEMO 48: CONTAINER ENERGY BUDGET ENFORCER")
    print("="*60 + "\n")

    # Simulate a Kubernetes Admission Controller logic
    pod_governor = EnergyGovernor(max_joules_budget=1000.0)

    pods = [
        {"id": "pod-nginx-01", "est_joules": 200},
        {"id": "pod-redis-01", "est_joules": 300},
        {"id": "pod-ml-training-01", "est_joules": 800} # Too expensive
    ]

    print("Intercepting Pod Creation Requests...")
    
    for pod in pods:
        time.sleep(0.5)
        print(f"Request: Create {pod['id']} (Est. {pod['est_joules']}J)")
        
        if pod_governor.request_action(pod['id'], pod['est_joules']):
            print("  ✅ ADMITTED: Pod scheduled.")
        else:
            print("  ❌ DENIED: Energy Budget Exceeded. Pod rejected.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: RUNTIME ENFORCEMENT")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
