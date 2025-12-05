import torch
from typing import Dict, Optional

class FeatureNormalizer:
    """
    Standardizes input features to a 0-1 range (Min-Max Scaling).
    Critical for training stability with diverse physical units (e.g. Watts vs Degrees).
    """
    def __init__(self, feature_ranges: Dict[str, tuple]):
        """
        Args:
            feature_ranges: Dict mapping feature name to (min, max) tuple.
                            Example: {'temp': (0, 100), 'power': (0, 500)}
        """
        self.feature_ranges = feature_ranges

    def normalize(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Normalize a dictionary of features.
        """
        normalized = {}
        for key, value in features.items():
            if key in self.feature_ranges:
                min_val, max_val = self.feature_ranges[key]
                # Avoid division by zero
                if max_val - min_val == 0:
                    normalized[key] = 0.0
                else:
                    # Clip to range then scale
                    clipped = max(min_val, min(value, max_val))
                    normalized[key] = (clipped - min_val) / (max_val - min_val)
            else:
                # Pass through if not defined (or could raise warning)
                normalized[key] = value
        return normalized

    def denormalize(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        Convert back to original units (for interpretation/action).
        """
        denormalized = {}
        for key, value in features.items():
            if key in self.feature_ranges:
                min_val, max_val = self.feature_ranges[key]
                denormalized[key] = value * (max_val - min_val) + min_val
            else:
                denormalized[key] = value
        return denormalized

    def normalize_tensor(self, x: torch.Tensor, feature_order: list) -> torch.Tensor:
        """
        Normalize a tensor where columns correspond to features in `feature_order`.
        """
        # Create min/max tensors
        mins = torch.tensor([self.feature_ranges[f][0] for f in feature_order], device=x.device)
        maxs = torch.tensor([self.feature_ranges[f][1] for f in feature_order], device=x.device)
        
        # Clamp and Scale
        x_clamped = torch.clamp(x, min=mins, max=maxs)
        return (x_clamped - mins) / (maxs - mins + 1e-6)
