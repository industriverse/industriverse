import sys
import os
import json
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from vision.visual_twin import VisualTwin
from models.mfem_core import MultiModalFusionEncoder

def test_mfem_integration():
    print("🚀 Starting MFEM Integration Test...")
    
    # 1. Initialize Components
    twin = VisualTwin()
    encoder = MultiModalFusionEncoder()
    
    # 2. Get Real Visual Data
    stream = twin.get_video_stream(worker_id="worker_006") # Using new batch data
    if not stream:
        print("❌ No stream found for worker_006.")
        return
        
    visual_data = twin.perceive(stream[0])
    print(f"👁️  Visual State: {json.dumps(visual_data['state_vector'])}")
    
    # 3. Simulate Telemetry (Mock Sensor Data)
    telemetry_data = {
        "timestamp": time.time(),
        "rpm": 4500,
        "load": 0.75,
        "vibration": 0.015,
        "power_watts": 1200
    }
    print(f"📡 Telemetry: {json.dumps(telemetry_data)}")
    
    # 4. Fuse Data (MFEM)
    print("⚡ Fusing Modalities...")
    fused_state = encoder.encode(visual_data, telemetry_data)
    
    print(f"✅ MFEM Result:")
    print(f"   - Embedding Size: {len(fused_state['embedding_vector'])}")
    print(f"   - Energy Estimate: {fused_state['energy_state_joules']} Joules")
    print(f"   - Coherence: {fused_state['coherence_score']}")

if __name__ == "__main__":
    test_mfem_integration()
