import torch
from src.scf.training.loss.physics_coupler import PhysicsConstrainedLoss

class CoTrainingEngine:
    def __init__(self, ebdm, tnn, optimizer):
        self.ebdm = ebdm
        self.tnn = tnn
        self.optimizer = optimizer
        self.loss_fn = PhysicsConstrainedLoss()

    def train_step(self, batch):
        self.optimizer.zero_grad()
        
        # 1. EBDM Reconstruct / Denoise
        x = batch["ebdm_ready_tensor"]
        noise_level = torch.rand(x.size(0), 1).to(x.device)
        # Mock EBDM forward (normally returns score)
        score = self.ebdm(x, noise_level)
        ebdm_loss = ((score - torch.randn_like(x))**2).mean() # Simplified score matching
        
        # 2. TNN Eval (Physics Check)
        # TNN predicts energy/entropy of the reconstructed state
        # We want the EBDM to produce states that TNN likes (low energy violation)
        # For this to work, we need a differentiable path from EBDM output to TNN input.
        # Here we assume EBDM output IS the state TNN evaluates.
        tnn_pred = self.tnn(score) # Mock flow
        tnn_penalty = torch.abs(tnn_pred).mean() # Minimize predicted violation
        
        # 3. Combined Loss
        loss = self.loss_fn(ebdm_loss, tnn_penalty)
        
        loss.backward()
        self.optimizer.step()
        
        return loss.item(), ebdm_loss.item(), tnn_penalty.item()
