import sys
import os
import time
import random

# Add project root to path
sys.path.append(os.getcwd())

from src.thermodynamic_layer.signal_processing import UniversalNormalizer

def run():
    print("\n" + "="*60)
    print(" DEMO 33: BIOSENSOR DATA INGESTION")
    print("="*60 + "\n")

    normalizer = UniversalNormalizer()

    print("Initializing Secure Bio-Link...")
    time.sleep(0.5)
    print("Device Connected: GLUCOSE_MONITOR_X7")

    # Simulate stream
    for i in range(3):
        raw_val = 80 + random.random() * 40 # mg/dL
        print(f"Reading: {raw_val:.1f} mg/dL")
        
        # Normalize
        norm = normalizer.normalize(raw_val, "bio", context={"max_conc": 200})
        print(f"Normalized Signal: {norm:.4f}")
        
        if norm > 0.6:
            print("⚠️ ALERT: High Glucose Event")
            
        time.sleep(0.5)

    print("\n" + "="*60)
    print(" DEMO COMPLETE: BIO-DATA SECURED")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
