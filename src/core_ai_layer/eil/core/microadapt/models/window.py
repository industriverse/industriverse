"""Hierarchical Window Data Structures"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class HierarchicalWindow:
    """Multi-scale hierarchical window decomposition"""
    level: int  # 1, 2, 3, ... (1=shortest, H=longest)
    window_size: int  # in seconds
    data: np.ndarray  # Time-series data for this level
    timestamp: datetime = field(default_factory=datetime.utcnow)

    @property
    def mean(self) -> float:
        """Mean value of this window"""
        return float(np.mean(self.data))

    @property
    def variance(self) -> float:
        """Variance of this window"""
        return float(np.var(self.data))

    @property
    def std(self) -> float:
        """Standard deviation of this window"""
        return float(np.std(self.data))

@dataclass
class WindowSet:
    """Complete set of hierarchical windows for current time point"""
    windows: List[HierarchicalWindow] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def get_level(self, level: int) -> HierarchicalWindow:
        """Get window at specific level"""
        for window in self.windows:
            if window.level == level:
                return window
        raise ValueError(f"No window found at level {level}")

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'windows': [
                {
                    'level': w.level,
                    'window_size': w.window_size,
                    'mean': w.mean,
                    'variance': w.variance,
                    'std': w.std
                }
                for w in self.windows
            ],
            'timestamp': self.timestamp.isoformat()
        }
