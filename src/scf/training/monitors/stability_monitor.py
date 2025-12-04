import torch
import logging

LOG = logging.getLogger("SCF.StabilityMonitor")

class StabilityMonitor:
    def check_gradients(self, model):
        total_norm = 0.0
        for p in model.parameters():
            if p.grad is not None:
                param_norm = p.grad.data.norm(2)
                total_norm += param_norm.item() ** 2
        total_norm = total_norm ** 0.5
        
        if total_norm > 100.0: # Threshold
            LOG.warning("Exploding gradients detected: norm=%f", total_norm)
            return False
        return True

    def check_loss(self, loss_val):
        if torch.isnan(torch.tensor(loss_val)) or torch.isinf(torch.tensor(loss_val)):
            LOG.error("Loss is NaN or Inf!")
            return False
        return True
