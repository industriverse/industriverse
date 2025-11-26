import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from src.thermodynamic_layer.signal_processing import ConservationEnforcer

def run():
    print("\n" + "="*60)
    print(" DEMO 23: CONSERVATION ENFORCER MICROSERVICE")
    print("="*60 + "\n")

    enforcer = ConservationEnforcer(tolerance=0.1)

    print("--- Scenario 1: Valid Transaction ---")
    e_in = 100.0
    e_out = 95.0
    e_stored = 5.0
    print(f"Input: {e_in}J | Output: {e_out}J | Stored: {e_stored}J")
    if enforcer.check(e_in, e_out, e_stored):
        print("✅ Conservation Holds. Transaction Approved.")
    else:
        print("❌ Violation Detected.")

    print("\n--- Scenario 2: Physics Violation (Injection Attack) ---")
    e_in = 100.0
    e_out = 95.0
    e_stored = 10.0 # Extra 5J appearing from nowhere
    print(f"Input: {e_in}J | Output: {e_out}J | Stored: {e_stored}J")
    if enforcer.check(e_in, e_out, e_stored):
        print("✅ Conservation Holds.")
    else:
        print("❌ VIOLATION DETECTED: Energy Created from Nothing! (Delta > Tolerance)")
        print("   Action Blocked.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: PHYSICS ENFORCED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
