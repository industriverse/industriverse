import torch
import logging

LOG = logging.getLogger("SCF.Eval.Stability")

def test_stability(model, input_tensor: torch.Tensor, noise_scale: float = 0.01) -> float:
    """
    Perturbs input with noise and measures output divergence.
    Returns stability score (1.0 = perfect, 0.0 = unstable).
    """
    model.eval()
    with torch.no_grad():
        # Base output
        # Assuming model takes (x, noise_level) for EBDM
        noise_level = torch.zeros(input_tensor.size(0), 1).to(input_tensor.device)
        out_base = model(input_tensor, noise_level)
        
        # Perturbed output
        perturbation = torch.randn_like(input_tensor) * noise_scale
        out_perturbed = model(input_tensor + perturbation, noise_level)
        
        # Relative change
        diff = (out_base - out_perturbed).norm() / (out_base.norm() + 1e-9)
        
        # Stability score: 1.0 if diff is small, drops as diff grows
        score = max(0.0, 1.0 - diff.item())
        
        if score < 0.9:
            LOG.warning(f"Low stability score: {score:.4f} (diff: {diff.item():.4f})")
            
        return score
