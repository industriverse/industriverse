import sys
import os
import numpy as np

# Add project root to path
sys.path.append(os.getcwd())

from src.thermodynamic_layer.signal_processing import PowerTraceConverter

def run():
    print("\n" + "="*60)
    print(" DEMO 29: NOISE FINGERPRINT EXTRACTOR")
    print("="*60 + "\n")

    converter = PowerTraceConverter()

    print("--- Device A (Legitimate Sensor) ---")
    # Simulate Gaussian noise
    trace_a = np.random.normal(10, 0.5, 100) 
    res_a = converter.process(trace_a)
    fingerprint_a = res_a['Entropy']
    print(f"Device A Entropy Fingerprint: {fingerprint_a:.4f}")

    print("\n--- Device B (Counterfeit Sensor) ---")
    # Simulate Uniform noise (cheaper electronics often have different noise profiles)
    trace_b = np.random.uniform(9, 11, 100)
    res_b = converter.process(trace_b)
    fingerprint_b = res_b['Entropy']
    print(f"Device B Entropy Fingerprint: {fingerprint_b:.4f}")

    print("\n--- Analysis ---")
    diff = abs(fingerprint_a - fingerprint_b)
    print(f"Fingerprint Divergence: {diff:.4f}")
    
    if diff > 0.1:
        print("✅ DETECTED: Device B has a distinct noise signature (Likely Counterfeit).")
    else:
        print("❌ Inconclusive.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: FINGERPRINT EXTRACTED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
