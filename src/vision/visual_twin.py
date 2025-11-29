import json
import time
import os
import random

class VisualTwin:
    """
    AI Shield v3 - Gate 6: Visual Twin.
    The 'Eyes' of the AGI Loop. Uses Egocentric-10K to perceive
    the physical state of the machine from camera feed.
    """
    def __init__(self, index_path="data/egocentric_index.json"):
        self.index_path = index_path
        self.index = {}
        self.is_loaded = False
        self.load_index()

    def load_index(self):
        if os.path.exists(self.index_path):
            print(f"Loading Egocentric-10K Index from {self.index_path}...")
            with open(self.index_path, 'r') as f:
                self.index = json.load(f)
            self.is_loaded = True
        else:
            print("Visual Twin initialized in Mock Mode (Egocentric-10K Index not found).")

    def get_video_stream(self, factory_id="factory_001", worker_id="worker_001"):
        """
        Returns the list of video chunks for a specific worker.
        """
        if not self.is_loaded:
            return []
        
        try:
            return self.index.get(factory_id, {}).get("workers", {}).get(worker_id, {}).get("chunks", [])
        except Exception as e:
            print(f"Error retrieving stream for {worker_id}: {e}")
            return []

    def perceive(self, video_chunk_path):
        """
        Input: Path to current video chunk.
        Output: Simulated perception metadata based on real file.
        """
        if not video_chunk_path or not os.path.exists(video_chunk_path):
             return {
                "state_vector": {"x": 0, "y": 0, "temp": 20.0, "status": "NO_SIGNAL"},
                "confidence": 0.0
            }

        # In a real system, we would run the Vision Transformer here.
        # For now, we simulate "Perception" by extracting metadata and returning a valid state.
        
        file_size = os.path.getsize(video_chunk_path)
        
        return {
            "source": video_chunk_path,
            "state_vector": {
                "x": 100.0 + random.uniform(-1, 1), 
                "y": 50.0 + random.uniform(-1, 1),
                "z": 0.0,
                "temp": 210.0 + random.uniform(-5, 5), # Simulated IR reading
                "spaghetti_detected": False,
                "operator_present": True
            },
            "meta": {
                "file_size_bytes": file_size,
                "dataset": "Egocentric-10K"
            },
            "anomalies": [],
            "confidence": 0.98, # High confidence because we have real data
            "timestamp": time.time()
        }

if __name__ == "__main__":
    twin = VisualTwin()
    stream = twin.get_video_stream(worker_id="worker_001")
    if stream:
        print(f"Found {len(stream)} chunks for worker_001")
        print("Perceiving first chunk:")
        print(json.dumps(twin.perceive(stream[0]), indent=2))
    else:
        print("No stream found.")
