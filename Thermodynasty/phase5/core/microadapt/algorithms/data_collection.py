"""DynamicDataCollection: Multi-scale Hierarchical Window Decomposition"""
import numpy as np
from collections import deque
from typing import List, Dict, Deque, Optional
from ..models.window import HierarchicalWindow, WindowSet
from ..core.config import config

class DynamicDataCollection:
    """
    Decomposes data stream into multi-scale hierarchical windows.

    Formula: X_C = X_C^1 + X_C^2 + ... + X_C^H
    where each level captures different time scales.
    """

    def __init__(self, hierarchy_levels: Optional[int] = None, window_sizes: Optional[List[int]] = None):
        # Use config values if not provided
        self.hierarchy_levels = hierarchy_levels if hierarchy_levels is not None else config.hierarchy_levels
        self.window_sizes = window_sizes if window_sizes is not None else config.window_sizes

        # Ensure window_sizes is set
        if self.window_sizes is None:
            self.window_sizes = [60, 600, 3600]  # Default: 1min, 10min, 1hr

        # Ensure hierarchy_levels matches window_sizes length
        if len(self.window_sizes) != self.hierarchy_levels:
            self.hierarchy_levels = len(self.window_sizes)

        # History buffers for each level
        self.history: Dict[int, Deque] = {
            level: deque(maxlen=self.window_sizes[level-1])
            for level in range(1, self.hierarchy_levels + 1)
        }

    def add_data_point(self, value: float, timestamp: float = None):
        """Add a single data point to all hierarchy levels"""
        for level in range(1, self.hierarchy_levels + 1):
            self.history[level].append(value)

    def decompose(self, current_data: np.ndarray = None) -> WindowSet:
        """
        Decompose current window into multi-scale hierarchical components.

        Args:
            current_data: Optional new data to add before decomposition

        Returns:
            WindowSet containing all hierarchical windows
        """
        if current_data is not None:
            for value in current_data:
                self.add_data_point(float(value))

        windows = []

        for level in range(1, self.hierarchy_levels + 1):
            if len(self.history[level]) == 0:
                continue

            # Convert deque to numpy array
            level_data = np.array(list(self.history[level]))

            # Simplified decomposition: each level gets raw data
            # In production, implement proper multi-scale decomposition
            # For now, just apply different smoothing at each level
            if level == 1:
                # Level 1: Raw data (high frequency)
                filtered_data = level_data
            elif level == 2:
                # Level 2: Light smoothing (medium frequency)
                filtered_data = self._moving_average(level_data, window_size=3)
            else:
                # Level 3+: Heavy smoothing (low frequency)
                filtered_data = self._moving_average(level_data, window_size=5)

            window = HierarchicalWindow(
                level=level,
                window_size=self.window_sizes[level-1],
                data=filtered_data
            )
            windows.append(window)

        return WindowSet(windows=windows)

    def _moving_average(self, data: np.ndarray, window_size: int = 5) -> np.ndarray:
        """Apply moving average filter"""
        if len(data) < window_size:
            return data

        # Use numpy convolve for moving average
        weights = np.ones(window_size) / window_size
        smoothed = np.convolve(data, weights, mode='valid')

        # Pad to maintain original length
        pad_size = len(data) - len(smoothed)
        if pad_size > 0:
            # Pad with edge values
            smoothed = np.pad(smoothed, (pad_size, 0), mode='edge')

        return smoothed

    def get_current_state(self) -> Dict:
        """Get current state of all hierarchy levels"""
        return {
            level: {
                'size': len(self.history[level]),
                'mean': np.mean(list(self.history[level])) if len(self.history[level]) > 0 else 0.0,
                'std': np.std(list(self.history[level])) if len(self.history[level]) > 0 else 0.0
            }
            for level in range(1, self.hierarchy_levels + 1)
        }
