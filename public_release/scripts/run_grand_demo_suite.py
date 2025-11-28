import sys
import os
import time

# Add root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.tnn.predictor import TNNPredictor
from src.generative_layer.ebdm import EBDMGenerator

def main():
    print("="*60)
    print("       INDUSTRIVERSE PUBLIC DEMO SUITE")
    print("="*60)
    print("Initializing Client SDK...")
    
    tnn = TNNPredictor()
    ebdm = EBDMGenerator()
    
    print("\n[1] Testing Connection to Thermodynamic Engine...")
    time.sleep(1)
    energy = tnn.predict_energy([0.5, 0.5])
    print(f"    > Received Energy Estimate: {energy:.4f} (Mock)")
    
    print("\n[2] Requesting Generative Design (Fusion Reactor)...")
    time.sleep(1)
    design = ebdm.generate("Stable Tokamak Configuration")
    print(f"    > Received Design Candidate: {design.shape} (Mock)")
    
    print("\n" + "="*60)
    print("DEMO COMPLETE")
    print("To run the full 50-Demo Suite with real physics validation,")
    print("please contact sales@industriverse.com for Enterprise Access.")
    print("="*60)

if __name__ == "__main__":
    main()
