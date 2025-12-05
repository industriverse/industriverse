import torch
from torch.utils.data import DataLoader
from src.scf.models.ebdm import EBDM, EBDM_Student
from src.scf.training.distiller import DistillationTrainer
from src.scf.dataloading.fossil_streamer import FossilStreamer

VAULT_PATH = "/Volumes/Expansion/fossil_vault"

def main():
    print("⚗️  Starting Model Distillation (Teacher -> Student)...")
    
    # 1. Setup Data
    dataset = FossilStreamer(VAULT_PATH, batch_size=32, max_files=50)
    dataloader = DataLoader(dataset, batch_size=None)
    
    # 2. Setup Models
    # Teacher (Simulating a larger, pre-trained model)
    teacher = EBDM(input_dim=4, hidden_dim=64, output_dim=4)
    # Student (Compressed model)
    student = EBDM_Student(input_dim=4, hidden_dim=16, output_dim=4)
    
    print(f"   Teacher Params: {sum(p.numel() for p in teacher.parameters())}")
    print(f"   Student Params: {sum(p.numel() for p in student.parameters())}")
    
    # 3. Setup Distiller
    distiller = DistillationTrainer(teacher, student, alpha=0.5, temperature=3.0)
    
    # 4. Train Loop
    epochs = 3
    print(f"   Distilling for {epochs} epochs...")
    
    for epoch in range(epochs):
        metrics = distiller.train_epoch(dataloader, epoch)
        if metrics:
            print(f"   [Epoch {epoch}] Loss: {metrics['loss']:.4f} | Soft: {metrics['soft_loss']:.4f} | Energy: {metrics['kwh_used']:.6f} kWh")
        
    print("✅ Distillation Complete.")
    print(f"   Log saved to: {distiller.log_path}")

if __name__ == "__main__":
    main()
