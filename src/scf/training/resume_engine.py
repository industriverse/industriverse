import os
import torch
import json
import time
from typing import Dict, Optional

class ResumeEngine:
    """
    Manages training checkpoints and auto-resumption.
    Ensures fault tolerance for long-running training jobs.
    """
    def __init__(self, checkpoint_dir: str = "checkpoints"):
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)

    def save_checkpoint(self, 
                        model_state: Dict, 
                        optimizer_state: Dict, 
                        epoch: int, 
                        step: int, 
                        metrics: Dict,
                        filename: str = "latest_checkpoint.pt"):
        """
        Save a training checkpoint.
        """
        path = os.path.join(self.checkpoint_dir, filename)
        
        # Atomic save: write to temp then rename
        temp_path = path + ".tmp"
        
        checkpoint = {
            'model_state': model_state,
            'optimizer_state': optimizer_state,
            'epoch': epoch,
            'step': step,
            'metrics': metrics,
            'timestamp': time.time()
        }
        
        torch.save(checkpoint, temp_path)
        os.replace(temp_path, path)
        print(f"💾 Checkpoint saved: {path} (Epoch {epoch}, Step {step})")

    def load_checkpoint(self, filename: str = "latest_checkpoint.pt") -> Optional[Dict]:
        """
        Load the latest checkpoint if it exists.
        """
        path = os.path.join(self.checkpoint_dir, filename)
        if not os.path.exists(path):
            print("⚠️ No checkpoint found. Starting from scratch.")
            return None
            
        try:
            checkpoint = torch.load(path)
            print(f"♻️  Resuming from checkpoint: {path} (Epoch {checkpoint['epoch']})")
            return checkpoint
        except Exception as e:
            print(f"❌ Failed to load checkpoint: {e}")
            return None

    def get_latest_epoch(self) -> int:
        checkpoint = self.load_checkpoint()
        return checkpoint['epoch'] if checkpoint else 0
