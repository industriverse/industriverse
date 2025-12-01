import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.orchestration.drift_canceller import DriftCanceller
from src.vision.visual_twin import VisualTwin

def run_solution():
    print("############################################################")
    print("#   GENESIS GENERATED SOLUTION                             #")
    print("#   Request: fix thermal drift")
    print("############################################################")

    # Initialize Modules
    canceller = DriftCanceller()
twin = VisualTwin()

    print("🔵 Starting Execution Loop...")
    for i in range(3):
        print(f"\n[Step {i+1}]")
    # DriftCanceller Logic
    correction, drift = canceller.apply_correction([100, 50, 25], {'temperature': 35.0})
    print(f'[DriftCanceller] Applied Correction: {correction}')
    # VisualTwin Logic
    twin.ingest_multimodal({'temperature': 35.0, 'vibration': 0.02})
        time.sleep(0.5)

    print("\n✅ Execution Complete.")

if __name__ == "__main__":
    run_solution()
