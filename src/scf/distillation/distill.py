import torch
import argparse
import os
from pathlib import Path
from torch.utils.data import DataLoader

from src.scf.models.ebdm import EBDM
from src.scf.models.bitnet import BitNet_Student
from src.scf.training.distiller import DistillationTrainer
from src.scf.dataloading.fossil_streamer import FossilStreamer

def run_distillation(teacher_path: str, vault_path: str, epochs: int = 10):
    print("⚗️  Initializing Distillation Pipeline...")
    
    # 1. Load Teacher (EBDM)
    print(f"   Loading Teacher from: {teacher_path}")
    teacher = EBDM(input_dim=4, output_dim=4)
    # In a real scenario, we would load state_dict here.
    # For now, we assume the teacher is initialized (or we load if file exists)
    if os.path.exists(teacher_path):
        teacher.load_state_dict(torch.load(teacher_path))
        print("   ✅ Teacher weights loaded.")
    else:
        print("   ⚠️  Teacher weights not found. Using random initialization (for testing).")
    
    # 2. Initialize Student (BitNet)
    print("   Initializing Student: BitNet (1.58-bit ready)")
    student = BitNet_Student(input_dim=4, hidden_dim=16, output_dim=4)
    
    # 3. Setup Data
    print(f"   Streaming Fossils from: {vault_path}")
    dataset = FossilStreamer(vault_path, batch_size=32, max_files=100)
    dataloader = DataLoader(dataset, batch_size=None)
    
    # 4. Setup Trainer
    trainer = DistillationTrainer(teacher, student, alpha=0.5, temperature=2.0)
    
    # 5. Training Loop
    print(f"   Starting Distillation for {epochs} epochs...")
    for epoch in range(epochs):
        metrics = trainer.train_epoch(dataloader, epoch)
        if metrics:
            print(f"   [Epoch {epoch}] Loss: {metrics['loss']:.4f} (Hard: {metrics['hard_loss']:.4f}, Soft: {metrics['soft_loss']:.4f}) | Energy: {metrics['kwh_used']:.6f} kWh")
        else:
            print(f"   [Epoch {epoch}] No data processed.")
            
    # 6. Save Student
    save_path = "model_zoo/student_latest.pt"
    os.makedirs("model_zoo", exist_ok=True)
    torch.save(student.state_dict(), save_path)
    print(f"✅ Distillation Complete. Student saved to: {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--teacher", type=str, default="model_zoo/production/latest.pt", help="Path to Teacher checkpoint")
    parser.add_argument("--vault", type=str, default="/Volumes/Expansion/fossil_vault", help="Path to Fossil Vault")
    parser.add_argument("--epochs", type=int, default=5, help="Number of epochs")
    args = parser.parse_args()
    
    # Handle env var for vault if not passed
    vault = os.environ.get("VAULT_PATH", args.vault)
    
    run_distillation(args.teacher, vault, args.epochs)
