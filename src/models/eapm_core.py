import json
import os
import random
import time
from typing import Dict, List, Any

class EgocentricActionProjector:
    """
    Model Family 5: Egocentric Action Projection Model (EAPM).
    
    Purpose:
    Predicts operator actions and aligns machine intent with human motion.
    Uses Egocentric-10K dataset as the ground truth for human-in-the-loop dynamics.
    """
    def __init__(self, index_path="data/egocentric_index.json"):
        self.index_path = index_path
        self.index = {}
        self.load_index()
        
    def load_index(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, 'r') as f:
                self.index = json.load(f)
            print(f"EAPM: Loaded index with {len(self.index.get('factory_001', {}).get('workers', {}))} workers.")
        else:
            print("EAPM: Index not found. Running in mock mode.")

    def predict_operator_action(self, video_chunk_path: str) -> Dict[str, Any]:
        """
        Input: Path to a video chunk (simulating real-time feed).
        Output: Predicted action vector and safety score.
        """
        # In a real implementation, this would run a Video Transformer or I3D model.
        # For priming, we simulate the output based on the file existence.
        
        if not os.path.exists(video_chunk_path):
            return {"action": "UNKNOWN", "safety_score": 0.0}
            
        # Mock Inference Logic
        actions = ["WELDING", "ASSEMBLY", "INSPECTION", "IDLE", "WALKING"]
        predicted_action = random.choice(actions)
        
        # Simulate "unsafe" conditions randomly for testing
        safety_score = random.uniform(0.7, 1.0)
        if predicted_action == "WELDING":
            safety_score = random.uniform(0.5, 0.9) # Higher risk
            
        return {
            "timestamp": time.time(),
            "source_video": os.path.basename(video_chunk_path),
            "predicted_action": predicted_action,
            "action_vector": [random.random() for _ in range(5)], # Mock embedding
            "safety_score": safety_score,
            "operator_aligned": safety_score > 0.8
        }

    def get_training_batch(self, batch_size=5) -> List[str]:
        """
        Returns a list of video paths for training.
        """
        all_chunks = []
        workers = self.index.get("factory_001", {}).get("workers", {})
        for w_id, w_data in workers.items():
            all_chunks.extend(w_data.get("chunks", []))
            
        if not all_chunks:
            return []
            
        return random.sample(all_chunks, min(batch_size, len(all_chunks)))

if __name__ == "__main__":
    eapm = EgocentricActionProjector()
    batch = eapm.get_training_batch(1)
    if batch:
        print(f"Predicting action for: {batch[0]}")
        result = eapm.predict_operator_action(batch[0])
        print(json.dumps(result, indent=2))
