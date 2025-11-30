import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.vision.visual_twin import VisualTwin

def verify_phase_112():
    print("==================================================")
    print("🧪 Phase 112 Verification: Challenges 4 & 9")
    print("==================================================")

    # 1. Verify VisualTwin Multi-Modal Ingestion (Challenge #4)
    print("\n👁️  1. Testing VisualTwin Multi-Modal Ingestion...")
    twin = VisualTwin()
    
    # Simulate Sensor Data
    telemetry_samples = [
        {"temperature": 22.5, "vibration": 0.01, "acoustic": "normal"},
        {"temperature": 45.0, "vibration": 0.15, "acoustic": "high_pitch"}, # Anomaly
        {"temperature": 23.0, "vibration": 0.02, "acoustic": "normal"}
    ]

    for sample in telemetry_samples:
        twin.ingest_multimodal(sample)
        state = twin.get_state()
        print(f"   Twin State Updated: {state['telemetry']}")

    # 2. Verify DysonSphere Component Existence (Challenge #9)
    print("\n🔮 2. Verifying DysonSphere UI Component...")
    component_path = "src/frontend/components/DysonSphere.jsx"
    if os.path.exists(component_path):
        print(f"   ✅ Component found at {component_path}")
        with open(component_path, 'r') as f:
            content = f.read()
            if "const DysonSphere" in content and "canvasRef" in content:
                print("   ✅ Component structure looks valid (React/Canvas).")
            else:
                print("   ❌ Component content seems invalid.")
    else:
        print(f"   ❌ Component NOT found at {component_path}")

    print("\n==================================================")
    print("✅ Verification Complete.")
    print("==================================================")

if __name__ == "__main__":
    verify_phase_112()
