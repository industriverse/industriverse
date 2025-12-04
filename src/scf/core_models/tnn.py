import torch
import torch.nn as nn

class TNN(nn.Module):
    def __init__(self, in_dim=1024, hidden=2048):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.GELU(),
            nn.Linear(hidden, hidden//2),
            nn.GELU(),
            nn.Linear(hidden//2, 1)  # predicts Joules or J/s
        )
    def forward(self, x):
        return self.net(x).squeeze(-1)
