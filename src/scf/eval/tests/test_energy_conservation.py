import torch
import logging

LOG = logging.getLogger("SCF.Eval.Energy")

def test_energy_conservation(input_tensor: torch.Tensor, output_tensor: torch.Tensor, tolerance: float = 1e-3) -> float:
    """
    Checks if energy is conserved between input and output states.
    Returns the violation amount (0.0 if within tolerance).
    """
    # Assuming the tensor represents energy states directly or we sum over dimensions
    # For a closed system, sum(E_in) should approx sum(E_out)
    
    e_in = input_tensor.sum().item()
    e_out = output_tensor.sum().item()
    
    diff = abs(e_in - e_out)
    
    if diff > tolerance:
        LOG.warning(f"Energy violation: |{e_in:.4f} - {e_out:.4f}| = {diff:.4f} > {tolerance}")
        return diff
    
    return 0.0
