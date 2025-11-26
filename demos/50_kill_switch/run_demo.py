import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())

from src.overseer_system.energy_governor import EnergyGovernor

def run():
    print("\n" + "="*60)
    print(" DEMO 50: THE KILL SWITCH (FINAL SAFETY LAYER)")
    print("="*60 + "\n")

    # The ultimate governor
    global_governor = EnergyGovernor(max_joules_budget=1000000.0)

    print("System Status: NORMAL")
    print("Monitoring Global Entropy...")
    
    entropy_levels = [0.1, 0.2, 0.5, 0.9, 2.5] # 2.5 is catastrophic
    
    for e in entropy_levels:
        time.sleep(0.5)
        print(f"Global Entropy: {e}")
        
        if e > 2.0:
            print("\n🚨 CATASTROPHIC ENTROPY DETECTED!")
            print("INITIATING EMERGENCY SHUTDOWN PROTOCOL...")
            
            # Simulate shutting down all subsystems
            subsystems = ["Network_Layer", "Compute_Cluster", "Physical_Actuators"]
            for sys in subsystems:
                print(f"  -> Killing {sys}...")
                time.sleep(0.2)
                print(f"  -> {sys} OFFLINE.")
            
            print("\nSYSTEM HALTED. SAFETY PRESERVED.")
            break

    print("\n" + "="*60)
    print(" DEMO COMPLETE: SYSTEM SECURED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
