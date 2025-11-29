import sys
import os
import json

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from vision.visual_twin import VisualTwin
from core_ai_layer.sam_service import SAMPerceptionService

def test_feed():
    print("🚀 Starting Perception Feed Test...")
    
    # 1. Initialize Visual Twin (Real Mode)
    twin = VisualTwin()
    if not twin.is_loaded:
        print("❌ Visual Twin failed to load index.")
        return

    # 2. Get Stream
    stream = twin.get_video_stream(worker_id="worker_001")
    if not stream:
        print("❌ No stream found for worker_001.")
        return
    
    video_path = stream[0]
    print(f"🎥 Retrieved Video Chunk: {video_path}")
    
    # 3. Perceive (Twin Layer)
    perception = twin.perceive(video_path)
    print(f"👁️  Visual Twin Perception: {json.dumps(perception['state_vector'])}")
    
    # 4. Segment (SAM Layer)
    sam = SAMPerceptionService()
    print("🧠 Sending to SAM 3 for 'hand_object_interaction' segmentation...")
    
    # We pass the video path as the 'image_id' for this mock adapter
    segments = sam.segment_concept(video_path, "hand_object_interaction")
    
    print(f"✅ SAM 3 Result: Found {len(segments)} segments.")
    for seg in segments:
        print(f"   - {seg['label']} (Conf: {seg['confidence']})")

if __name__ == "__main__":
    test_feed()
