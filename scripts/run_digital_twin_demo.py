import sys
import os
import argparse
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.getcwd())

from src.core.digital_twin.service import DigitalTwinService

def run_demo(twin_type: str, horizon: int):
    print("\n" + "="*60)
    print(f" DEMO: ADVANCED DIGITAL TWIN ({twin_type.upper()})")
    print("="*60 + "\n")

    service = DigitalTwinService()
    twin_id = f"{twin_type}_demo_{int(time.time())}"

    # 1. Create Twin
    print(f"[1/3] Initializing Digital Twin: {twin_id}...")
    twin = service.create_twin(twin_id, twin_type, {"location": "Sector 7"})
    print(f"      Initial State: {twin['current_state']}")

    # 2. Run Shadow Projection
    print(f"\n[2/3] Running Shadow Projection (Horizon: {horizon}m)...")
    projections = service.run_shadow_projection(twin_id, horizon_minutes=horizon)
    
    # Print a few sample points
    print("      Projection Sample:")
    for p in projections[::10]: # Print every 10th minute
        print(f"      T+{int((p.timestamp - datetime.now()).total_seconds()/60)}m: {p.status} | {p.metrics}")

    # 3. Generate Visualization
    print(f"\n[3/3] Generating 3D Gaussian Splat Visualization...")
    artifact_path = service.generate_visualization(twin_id)
    print(f"      Artifact Generated: {artifact_path}")

    print("\n" + "="*60)
    print(" DEMO COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Digital Twin Demo")
    parser.add_argument("--type", type=str, default="fusion_reactor", help="Twin Type (fusion_reactor, grid_substation)")
    parser.add_argument("--horizon", type=int, default=60, help="Projection Horizon in minutes")
    args = parser.parse_args()

    run_demo(args.type, args.horizon)
