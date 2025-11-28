import sys
import os
import time
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.thermodynamic_layer.signal_processing import PowerTraceConverter

def run():
    print("\n" + "="*60)
    print(" DEMO 32: PLC INGESTION PIPELINE")
    print("="*60 + "\n")

    print("Connecting to Mock PLC (Modbus TCP)...")
    time.sleep(0.5)
    print("Connection Established: PLC_FACTORY_01")

    converter = PowerTraceConverter()

    for i in range(3):
        print(f"\n--- Polling Cycle {i+1} ---")
        # Simulate reading registers
        registers = [random.randint(1000, 1050) for _ in range(10)]
        print(f"Read Registers (40001-40010): {registers}")
        
        # Convert to Energy Vector
        res = converter.process(registers)
        print(f"Thermodynamic State: E={res['E_total']:.2f} | S={res['Entropy']:.2f}")
        
        time.sleep(0.5)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: PLC DATA INGESTED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
