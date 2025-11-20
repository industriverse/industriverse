"""Regime Assignment Data Structures"""
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

@dataclass
class RegimeAssignment:
    """Regime assignment result from ModelUnitSearch"""
    regime_id: str
    probabilities: np.ndarray  # Probability distribution over regimes
    top_k_indices: List[int]  # Indices of top-K model units
    model_unit_ids: List[str]  # IDs of top-K model units
    confidence: float  # Overall confidence of assignment
    fitness_scores: np.ndarray  # Fitness scores for all model units
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict:
        """Convert to dictionary for API/storage"""
        return {
            'regime_id': self.regime_id,
            'probabilities': self.probabilities.tolist(),
            'top_k_indices': self.top_k_indices,
            'model_unit_ids': self.model_unit_ids,
            'confidence': float(self.confidence),
            'fitness_scores': self.fitness_scores.tolist(),
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class RegimeTransition:
    """Regime change event"""
    transition_id: str
    from_regime: str
    to_regime: str
    transition_time: datetime
    energy_delta: float
    entropy_delta: float
    confidence: float
    trigger_type: str = "automatic"  # automatic, manual, threshold

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'transition_id': self.transition_id,
            'from_regime': self.from_regime,
            'to_regime': self.to_regime,
            'transition_time': self.transition_time.isoformat(),
            'energy_delta': self.energy_delta,
            'entropy_delta': self.entropy_delta,
            'confidence': self.confidence,
            'trigger_type': self.trigger_type
        }
