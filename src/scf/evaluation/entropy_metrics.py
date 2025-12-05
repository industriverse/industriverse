import torch
import torch.nn as nn
import torch.nn.functional as F

class EntropyLoss(nn.Module):
    """
    Physics-Informed Loss Function.
    Penalizes predictions that violate thermodynamic laws (e.g., high entropy production).
    L_total = L_mse + lambda * L_entropy
    """
    def __init__(self, lambda_entropy: float = 0.1):
        super().__init__()
        self.lambda_entropy = lambda_entropy

    def forward(self, pred: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        # 1. Standard Reconstruction Loss (MSE)
        mse_loss = F.mse_loss(pred, target)
        
        # 2. Entropy Penalty
        # We approximate entropy as the variance of the prediction (spread of energy)
        # In a real physics model, this would use the specific dS/dt formula.
        # Here: Minimize variance (encourage ordered states)
        entropy_proxy = torch.var(pred, dim=1).mean()
        
        # Total Loss
        total_loss = mse_loss + (self.lambda_entropy * entropy_proxy)
        
        return total_loss, mse_loss, entropy_proxy
