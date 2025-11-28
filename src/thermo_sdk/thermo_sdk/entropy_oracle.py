import numpy as np

def shannon_entropy(probs: np.ndarray) -> float:
    """Calculate Shannon Entropy in bits."""
    p = probs.copy()
    p = p[p > 0]
    return -(p * np.log2(p)).sum()
