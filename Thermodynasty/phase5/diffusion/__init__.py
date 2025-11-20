"""
Phase 5 Energy-Based Diffusion Engine

Core module for thermodynamic diffusion models that respect
energy conservation and entropy monotonicity.
"""

from .core.energy_field import EnergyField, EnergyState
from .core.diffusion_dynamics import (
    DiffusionModel,
    ForwardDiffusion,
    ReverseDiffusion,
    DiffusionConfig
)
from .core.energy_scheduler import (
    BoltzmannScheduler,
    LinearScheduler,
    CosineScheduler
)
from .core.sampler import (
    EnergyGuidedSampler,
    DDPMSampler,
    DDIMSampler
)

__all__ = [
    # Energy representation
    'EnergyField',
    'EnergyState',

    # Diffusion dynamics
    'DiffusionModel',
    'ForwardDiffusion',
    'ReverseDiffusion',
    'DiffusionConfig',

    # Schedulers
    'BoltzmannScheduler',
    'LinearScheduler',
    'CosineScheduler',

    # Samplers
    'EnergyGuidedSampler',
    'DDPMSampler',
    'DDIMSampler',
]

__version__ = "0.5.0-alpha"
