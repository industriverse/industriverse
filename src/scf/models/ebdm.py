import torch
import torch.nn as nn

class EBDM(nn.Module):
    """
    Energy-Based Diffusion Model (Tiny).
    A lightweight MLP designed to predict the next physics state (entropy evolution).
    Optimized for low-parameter count and high inference efficiency.
    """
    def __init__(self, input_dim: int = 4, hidden_dim: int = 64, output_dim: int = 4):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.SiLU(), # Swish activation (smooth gradients for physics)
            nn.Linear(hidden_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Predicts the next state given the current state.
        Input: [Batch, Features] (e.g., Temp, Power, Entropy, Time)
        Output: [Batch, Features] (Predicted Next State)
        """
        return self.net(x)

class EBDM_Student(nn.Module):
    """
    Compressed version of EBDM for Edge Deployment.
    ~10x fewer parameters than the Teacher.
    """
    def __init__(self, input_dim: int = 4, hidden_dim: int = 16, output_dim: int = 4):
        super().__init__()
        # Thinner network (16 hidden vs 64)
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.SiLU(),
            nn.Linear(hidden_dim, output_dim) # One less layer? Or just thinner. Let's keep depth, reduce width.
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)
