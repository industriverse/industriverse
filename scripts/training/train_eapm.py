import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src"))

from models.eapm_core import EgocentricActionProjector

def train_eapm_stub():
    print("🚀 Starting EAPM Training Simulation...")
    
    # 1. Initialize Model
    model = EgocentricActionProjector()
    
    # 2. Load Data Batch
    print("📂 Loading training batch from Egocentric-10K...")
    batch_files = model.get_training_batch(batch_size=10)
    print(f"   Loaded {len(batch_files)} video samples.")
    
    if not batch_files:
        print("❌ No data found. Aborting.")
        return

    # 3. Simulate Training Loop
    print("🧠 Training Epoch 1/5...")
    for i, video_path in enumerate(batch_files):
        # Simulate forward pass
        prediction = model.predict_operator_action(video_path)
        
        # Simulate loss calculation
        loss = 1.0 - prediction['safety_score']
        
        print(f"   [{i+1}/{len(batch_files)}] Sample: {prediction['source_video']} | Action: {prediction['predicted_action']} | Loss: {loss:.4f}")
        time.sleep(0.1) # Simulate compute time
        
    print("✅ EAPM Primed. Model ready for full training.")

if __name__ == "__main__":
    train_eapm_stub()
