import sys
import os
import time
import random

# Add project root to path
sys.path.append(os.getcwd())

def run():
    print("\n" + "="*60)
    print(" DEMO 46: WAFER FAB THERMAL/CAMERA COMBO")
    print("="*60 + "\n")

    print("Initializing Sensor Fusion...")
    print("  [1] Optical Camera (4K)")
    print("  [2] Thermal Imager (60Hz)")
    
    time.sleep(0.5)
    
    print("\nScanning Wafer Batch #992...")
    
    # Simulate defect detection
    defects = []
    if random.random() > 0.5:
        defects.append({"loc": (120, 450), "temp": 85.4, "type": "Hotspot"})
    
    if defects:
        for d in defects:
            print(f"🚨 DEFECT DETECTED at {d['loc']}")
            print(f"   Thermal Signature: {d['temp']}C (Threshold: 80C)")
            print("   Action: Mark for Review")
    else:
        print("✅ Wafer Clean. No thermal anomalies.")

    print("\n" + "="*60)
    print(" DEMO COMPLETE: SENSOR FUSION ACTIVE")
    print("="*60 + "\n")

if __name__ == "__main__":
    run()
