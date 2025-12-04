import torch
import logging

LOG = logging.getLogger("SCF.StabilityFilter")

class StabilityFilter:
    def is_stable(self, output_tensor: torch.Tensor, threshold=10.0) -> bool:
        # Check for NaNs/Infs
        if torch.isnan(output_tensor).any() or torch.isinf(output_tensor).any():
            LOG.info("Rejected: NaN/Inf detected")
            return False
            
        # Check variance (reject flatlining or exploding)
        var = torch.var(output_tensor)
        if var < 1e-6:
            LOG.info("Rejected: Low variance (collapse)")
            return False
        if var > threshold:
            LOG.info("Rejected: High variance (instability)")
            return False
            
        return True
