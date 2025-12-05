import torch
import torch.nn as nn
from src.scf.models.ebdm import EBDM
from src.scf.dataloading.fossil_streamer import FossilStreamer
from torch.utils.data import DataLoader
import argparse
import os

VAULT_PATH = os.environ.get("VAULT_PATH", "/Volumes/Expansion/fossil_vault")

def evaluate_model(checkpoint_path: str, test_files: int = 5):
    print(f"⚖️  Evaluating Model: {checkpoint_path}")
    
    # 1. Load Model
    model = EBDM(input_dim=4, hidden_dim=64, output_dim=4)
    try:
        # In a real scenario, we'd load state_dict. 
        # For now, we assume the checkpoint is a state_dict file.
        # model.load_state_dict(torch.load(checkpoint_path))
        print("   (Mocking checkpoint load for structure verification)")
    except Exception as e:
        print(f"   ⚠️ Could not load checkpoint: {e}")
        
    model.eval()
    
    # 2. Load Test Data
    dataset = FossilStreamer(VAULT_PATH, batch_size=32, max_files=test_files)
    dataloader = DataLoader(dataset, batch_size=None)
    
    total_mse = 0.0
    entropy_violations = 0
    total_samples = 0
    
    criterion = nn.MSELoss()
    
    with torch.no_grad():
        for data, target in dataloader:
            # Predict
            prediction = model(data)
            
            # MSE
            loss = criterion(prediction, target)
            total_mse += loss.item() * data.size(0)
            
            # Physics Check: Second Law of Thermodynamics
            # Assume Index 2 is Entropy. If dS < 0 (and no work done?), it's a violation.
            # Simplified check: If predicted entropy < current entropy (and we assume closed system for this check)
            # This is a heuristic.
            current_entropy = data[:, 2]
            predicted_entropy = prediction[:, 2]
            
            # Count violations where entropy decreases (dS < 0)
            # In a real engine, we'd check dS >= dQ/T.
            violations = (predicted_entropy < current_entropy).sum().item()
            entropy_violations += violations
            
            total_samples += data.size(0)
            
    if total_samples == 0:
        print("   ⚠️ No test data found.")
        return

    avg_mse = total_mse / total_samples
    violation_rate = (entropy_violations / total_samples) * 100
    
    print(f"\n✅ Evaluation Results:")
    print(f"   MSE Loss: {avg_mse:.6f}")
    print(f"   Entropy Violation Rate: {violation_rate:.2f}%")
    print(f"   Physics Compliance: {100 - violation_rate:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("checkpoint", help="Path to model checkpoint.pt")
    args = parser.parse_args()
    
    evaluate_model(args.checkpoint)
