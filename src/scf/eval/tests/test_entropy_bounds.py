import torch
import logging

LOG = logging.getLogger("SCF.Eval.Entropy")

def test_entropy_bounds(output_tensor: torch.Tensor, min_entropy: float = 0.0, max_entropy: float = 10.0) -> int:
    """
    Checks if the output state's entropy is within physical bounds.
    Returns 1 if violated, 0 if passed.
    """
    # Mock entropy calculation: Shannon entropy of softmaxed distribution
    # In real physics, this would be S = -Tr(rho log rho) or similar
    
    probs = torch.softmax(output_tensor, dim=-1)
    entropy = -torch.sum(probs * torch.log(probs + 1e-9), dim=-1).mean().item()
    
    if entropy < min_entropy or entropy > max_entropy:
        LOG.warning(f"Entropy bounds violation: {entropy:.4f} not in [{min_entropy}, {max_entropy}]")
        return 1
        
    return 0
