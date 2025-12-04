import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
import glob

# Configuration
BATCH_SIZE = 32
EMBEDDING_DIM = 256
HIDDEN_DIM = 512
LAYERS = 4
EPOCHS = 10
LEARNING_RATE = 1e-4

class FossilDataset(Dataset):
    def __init__(self, vault_path):
        self.files = glob.glob(os.path.join(vault_path, "*.ndjson"))
        self.data = []
        print(f"📚 Loading Fossils from {vault_path}...")
        # Lazy loading or partial loading for demo
        for fpath in self.files[:100]: # Limit for demo speed
            with open(fpath, 'r') as f:
                for line in f:
                    try:
                        self.data.append(json.loads(line))
                    except: pass
        print(f"   Loaded {len(self.data)} samples.")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        # Mock Feature Extraction: Convert 'data' dict to tensor
        # In reality, this would use the specific schema of the fossil
        # For now, we generate a random embedding to simulate "Energy State"
        return torch.randn(EMBEDDING_DIM), torch.randn(1) # Input, Target (dS/dt)

class GenN1(nn.Module):
    """
    Generation N-1: The Physics Predictor.
    Predicts the next thermodynamic state (Entropy Gradient).
    """
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(EMBEDDING_DIM, HIDDEN_DIM),
            nn.ReLU(),
            nn.Linear(HIDDEN_DIM, HIDDEN_DIM),
            nn.ReLU(),
            nn.Linear(HIDDEN_DIM, 1) # Predicts dS/dt
        )

    def forward(self, x):
        return self.network(x)

def train():
    print("🔥 Igniting GenN-1 Training...")
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"   Device: {device}")
    if device.type == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")

    dataset = FossilDataset("fossil_vault") # Expects local folder on RunPod
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)
    
    model = GenN1().to(device)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.MSELoss()

    for epoch in range(EPOCHS):
        total_loss = 0
        for batch_idx, (data, target) in enumerate(dataloader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_loss = total_loss / len(dataloader)
        print(f"   Epoch {epoch+1}/{EPOCHS} | Loss: {avg_loss:.6f}")

    print("✅ Training Complete. Saving Model...")
    torch.save(model.state_dict(), "gen_n1_checkpoint.pt")

if __name__ == "__main__":
    train()
