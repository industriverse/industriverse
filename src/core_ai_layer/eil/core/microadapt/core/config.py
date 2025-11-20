"""MicroAdaptEdge Configuration Module"""
import os
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class MicroAdaptConfig:
    """Configuration for MicroAdaptEdge framework"""

    # Hierarchy configuration
    hierarchy_levels: int = 3
    window_sizes: List[int] = field(default_factory=lambda: [60, 600, 3600])

    # Model unit configuration
    max_model_units: int = 100
    initial_model_units: int = 10
    top_k: int = 5
    replacement_rate: float = 0.1

    # Algorithm parameters
    fitness_threshold: float = 0.5
    lm_max_iterations: int = 100
    lm_tolerance: float = 1e-6
    alpha: float = 0.1  # Growth rate for logistic model

    def __post_init__(self):
        """Load from environment and validate"""
        # Load from environment if set
        if os.getenv('MICROADAPT_HIERARCHY_LEVELS'):
            self.hierarchy_levels = int(os.getenv('MICROADAPT_HIERARCHY_LEVELS'))

        if os.getenv('MICROADAPT_WINDOW_SIZES'):
            window_str = os.getenv('MICROADAPT_WINDOW_SIZES')
            self.window_sizes = [int(w.strip()) for w in window_str.split(',')]

        if os.getenv('MICROADAPT_MAX_MODEL_UNITS'):
            self.max_model_units = int(os.getenv('MICROADAPT_MAX_MODEL_UNITS'))

        if os.getenv('MICROADAPT_INITIAL_MODEL_UNITS'):
            self.initial_model_units = int(os.getenv('MICROADAPT_INITIAL_MODEL_UNITS'))

        if os.getenv('MICROADAPT_TOP_K'):
            self.top_k = int(os.getenv('MICROADAPT_TOP_K'))

        if os.getenv('MICROADAPT_REPLACEMENT_RATE'):
            self.replacement_rate = float(os.getenv('MICROADAPT_REPLACEMENT_RATE'))

        # Validate configuration
        if len(self.window_sizes) != self.hierarchy_levels:
            print(f"Warning: Adjusting hierarchy_levels from {self.hierarchy_levels} to {len(self.window_sizes)} to match window_sizes")
            self.hierarchy_levels = len(self.window_sizes)

        if self.top_k > self.max_model_units:
            print(f"Warning: top_k ({self.top_k}) cannot exceed max_model_units ({self.max_model_units}), adjusting...")
            self.top_k = min(self.top_k, self.max_model_units)

# Global config instance
config = MicroAdaptConfig()
