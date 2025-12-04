import torch
import torch.nn as nn

class PhysicsConstrainedLoss(nn.Module):
    def __init__(self, lambda_tnn=0.5, lambda_pde=0.1, lambda_sym=0.1):
        super().__init__()
        self.lambda_tnn = lambda_tnn
        self.lambda_pde = lambda_pde
        self.lambda_sym = lambda_sym

    def forward(self, ebdm_loss, tnn_score, pde_residual=0.0, symmetry_violation=0.0):
        """
        TotalLoss = EBDM_loss 
                  + λ1 * TNN_energy_conservation_penalty 
                  + λ2 * PDE_residual 
                  + λ3 * symmetry_loss
        """
        # TNN score is typically "energy violation", so we want to minimize it
        return ebdm_loss + (self.lambda_tnn * tnn_score) + (self.lambda_pde * pde_residual) + (self.lambda_sym * symmetry_violation)
