import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())

from src.thermodynamic_layer.signal_processing import ConservationEnforcer

def run():
    print("\n" + "="*60)
    print(" DEMO 40: SUPPLY CHAIN LEAK SIMULATOR")
    print("="*60 + "\n")

    enforcer = ConservationEnforcer(tolerance=0.5)

    nodes = ["Supplier_A", "Logistics_Hub", "Factory_Gate"]
    inventory = 1000.0 # Units

    print(f"Tracking Inventory Flow: {inventory} units")

    for i, node in enumerate(nodes):
        time.sleep(0.5)
        print(f"\n--- Node: {node} ---")
        
        # Simulate leak at Logistics Hub
        loss = 0.0
        if node == "Logistics_Hub":
            loss = 50.0 # Theft/Damage
            print("  ⚠️ EVENT: Unaccounted Loss Detected (-50 units)")
        
        output = inventory - loss
        
        # Check conservation (Input vs Output + Known Loss)
        # Here we pretend the loss is UNKNOWN to the system initially
        if enforcer.check(inventory, output, 0.0):
            print("  ✅ Balance Verified.")
        else:
            print(f"  ❌ LEAK DETECTED: {inventory - output} units missing!")
        
        inventory = output

    print("\n" + "="*60)
    print(" DEMO COMPLETE: LEAK ISOLATED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
