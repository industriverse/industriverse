import sys
import os
import random
import time

# Add project root to path
sys.path.append(os.getcwd())

from src.thermodynamic_layer.signal_processing import PowerTraceConverter

def run():
    print("\n" + "="*60)
    print(" DEMO 22: POWER TRACE TO E(t) PIPELINE")
    print("="*60 + "\n")

    converter = PowerTraceConverter(sampling_rate_hz=1000)

    print("Simulating raw power trace ingestion (10ms window)...")
    
    # Simulate a noisy sine wave (Power consumption)
    raw_trace = [10 + 5*random.random() for _ in range(100)]
    print(f"Raw Trace Sample: {raw_trace[:5]} ...")

    print("\nProcessing through Thermodynamic Pipeline...")
    start_time = time.time()
    result = converter.process(raw_trace)
    duration = (time.time() - start_time) * 1000

    print(f"Pipeline Latency: {duration:.3f}ms")
    print("\n--- Thermodynamic Energy Vector E(t) ---")
    print(f"E_total (Joules):      {result['E_total']:.4f}")
    print(f"dE/dt (Volatility):    {result['dE_dt_volatility']:.4f}")
    print(f"Entropy (Shannon):     {result['Entropy']:.4f}")
    
    print("\n" + "="*60)
    print(" DEMO COMPLETE: SIGNAL EXTRACTED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
