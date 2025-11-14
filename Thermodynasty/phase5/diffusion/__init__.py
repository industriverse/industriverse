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
from .core.entropy_metrics import (
    EntropyValidator,
    BoltzmannMetrics,
    ThermodynamicMetrics,
    compute_energy_landscape_metrics
)
from .training import (
    DiffusionTrainer,
    TrainingConfig,
    EnergyMapDataset,
    SyntheticEnergyDataset,
    MolecularEnergyDataset,
    PlasmaEnergyDataset,
    EnterpriseEnergyDataset,
    EnergyMapConfig,
    create_dataloader,
    TrainingCallback,
    MetricsLogger,
    ThermodynamicValidator as ThermodynamicValidatorCallback,
    EarlyStopping,
    ProgressBar,
    SampleGenerator,
    GradientMonitor,
    WandbLogger,
    LearningRateScheduler
)
from .domains import (
    MolecularDiffusion,
    MolecularConfig,
    MolecularEnergyField,
    PlasmaDiffusion,
    PlasmaConfig,
    PlasmaEnergyField,
    EnterpriseDiffusion,
    EnterpriseConfig,
    EnterpriseEnergyField
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

    # Entropy & validation
    'EntropyValidator',
    'BoltzmannMetrics',
    'ThermodynamicMetrics',
    'compute_energy_landscape_metrics',

    # Training pipeline
    'DiffusionTrainer',
    'TrainingConfig',
    'EnergyMapDataset',
    'SyntheticEnergyDataset',
    'MolecularEnergyDataset',
    'PlasmaEnergyDataset',
    'EnterpriseEnergyDataset',
    'EnergyMapConfig',
    'create_dataloader',
    'TrainingCallback',
    'MetricsLogger',
    'ThermodynamicValidatorCallback',
    'EarlyStopping',
    'ProgressBar',
    'SampleGenerator',
    'GradientMonitor',
    'WandbLogger',
    'LearningRateScheduler',

    # Domain capsules
    'MolecularDiffusion',
    'MolecularConfig',
    'MolecularEnergyField',
    'PlasmaDiffusion',
    'PlasmaConfig',
    'PlasmaEnergyField',
    'EnterpriseDiffusion',
    'EnterpriseConfig',
    'EnterpriseEnergyField',
]

__version__ = "0.5.0-alpha"
