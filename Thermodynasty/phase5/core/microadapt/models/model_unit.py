"""Model Unit Data Structures"""
import numpy as np
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import uuid
from datetime import datetime

@dataclass
class ModelUnitParameters:
    """Parameters for differential dynamical system model unit"""
    p: np.ndarray  # Latent dynamics drift (d_s x 1)
    Q: np.ndarray  # Latent dynamics diffusion (d_s x d_s)
    u: np.ndarray  # Observation projection offset (d_x x 1)
    V: np.ndarray  # Observation projection matrix (d_x x d_s)
    s_star: np.ndarray  # Initial condition (d_s x 1)

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'p': self.p.tolist(),
            'Q': self.Q.tolist(),
            'u': self.u.tolist(),
            'V': self.V.tolist(),
            's_star': self.s_star.tolist()
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'ModelUnitParameters':
        """Create from dictionary"""
        return cls(
            p=np.array(data['p']),
            Q=np.array(data['Q']),
            u=np.array(data['u']),
            V=np.array(data['V']),
            s_star=np.array(data['s_star'])
        )

@dataclass
class ModelUnit:
    """Model Unit representing a regime/pattern in the data stream"""
    unit_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    parameters: ModelUnitParameters = None
    pattern_type: str = "unknown"
    fitness_score: float = 0.0
    usage_count: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_used: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    cluster_name: Optional[str] = None

    def predict_energy(self, window_data: np.ndarray) -> float:
        """Predict energy state using model unit's differential equations"""
        # x̂(t) = u + V·s(t)
        # This is a simplified prediction; full implementation uses ODE solver
        s_t = self.parameters.s_star  # Use initial condition as approximation
        x_hat = self.parameters.u + self.parameters.V @ s_t
        return float(np.mean(x_hat))

    def predict_entropy(self, window_data: np.ndarray) -> float:
        """Predict entropy state"""
        # Entropy based on variance of predicted states
        s_t = self.parameters.s_star
        variance = np.trace(self.parameters.Q)
        return float(variance)

    def predict_energy_derivative(self, window_data: np.ndarray) -> float:
        """Predict energy derivative dE/dt"""
        # ds(t)/dt = p + Q·s(t)
        s_t = self.parameters.s_star
        ds_dt = self.parameters.p + self.parameters.Q @ s_t
        dx_dt = self.parameters.V @ ds_dt
        return float(np.mean(dx_dt))

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage"""
        return {
            'unit_id': self.unit_id,
            'parameters': self.parameters.to_dict() if self.parameters else None,
            'pattern_type': self.pattern_type,
            'fitness_score': self.fitness_score,
            'usage_count': self.usage_count,
            'created_at': self.created_at.isoformat(),
            'last_used': self.last_used.isoformat(),
            'last_updated': self.last_updated.isoformat(),
            'cluster_name': self.cluster_name
        }
