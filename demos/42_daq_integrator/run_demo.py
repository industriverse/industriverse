import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())

def run():
    print("\n" + "="*60)
    print(" DEMO 42: LOW-COST DAQ INTEGRATOR")
    print("="*60 + "\n")

    print("Detecting Edge Hardware...")
    time.sleep(0.5)
    print("Found: NVIDIA Jetson Nano (Simulated)")
    print("Found: USB-DAQ-100 (Simulated)")

    print("\nStarting High-Frequency Sampling (10kHz)...")
    
    # Simulate buffer filling
    buffer_size = 1024
    for i in range(3):
        print(f"Buffer {i+1}/{3} Filled ({buffer_size} samples)")
        # Simulate processing delay
        time.sleep(0.2)
        print("  -> Pushed to Ingestion Pipeline")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: EDGE SAMPLING ACTIVE")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
