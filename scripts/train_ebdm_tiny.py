from torch.utils.data import DataLoader
from src.scf.models.ebdm import EBDM
from src.scf.training.trainer import SovereignTrainer
from src.scf.dataloading.fossil_streamer import FossilStreamer
import time
import os

VAULT_PATH = os.environ.get("VAULT_PATH", "/Volumes/Expansion/fossil_vault")

def main():
    print("🚀 Starting First Sovereign Run (EBDM-Tiny)...")
    
    # 1. Setup Data (Streaming)
    # We use the Streamer directly as the dataset
    dataset = FossilStreamer(VAULT_PATH, batch_size=32, max_files=100) # Limit files for quick test
    # For IterableDataset, we use DataLoader just for collation if needed, but Streamer yields batches
    # So we can iterate dataset directly or wrap in DataLoader with batch_size=None
    dataloader = DataLoader(dataset, batch_size=None) 
    print(f"   Streaming from: {VAULT_PATH}")
    
    # 2. Setup Model
    model = EBDM(input_dim=4, output_dim=4)
    print("   Model Initialized: EBDM-Tiny")
    
    # 3. Setup Trainer
    trainer = SovereignTrainer(model)
    
    # 4. Train Loop
    epochs = 5
    print(f"   Training for {epochs} epochs...")
    
    for epoch in range(epochs):
        metrics = trainer.train_epoch(dataloader, epoch)
        print(f"   [Epoch {epoch}] Loss: {metrics['loss']:.4f} | Entropy Penalty: {metrics['entropy_penalty']:.4f} | Energy: {metrics['kwh_used']:.6f} kWh")
        
    print("✅ Training Complete.")
    print(f"   Log saved to: {trainer.log_path}")

if __name__ == "__main__":
    main()
