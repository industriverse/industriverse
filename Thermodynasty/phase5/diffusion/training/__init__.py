"""
Phase 5 Diffusion Training Pipeline

Complete training infrastructure for energy-based diffusion models.
"""

from .dataset import (
    EnergyMapDataset,
    SyntheticEnergyDataset,
    MolecularEnergyDataset,
    PlasmaEnergyDataset,
    EnterpriseEnergyDataset,
    EnergyMapConfig,
    create_dataloader
)

from .trainer import (
    DiffusionTrainer,
    TrainingConfig
)

from .callbacks import (
    TrainingCallback,
    CallbackList,
    MetricsLogger,
    ThermodynamicValidator,
    EarlyStopping,
    ProgressBar,
    SampleGenerator,
    GradientMonitor,
    WandbLogger,
    LearningRateScheduler
)

__all__ = [
    # Datasets
    'EnergyMapDataset',
    'SyntheticEnergyDataset',
    'MolecularEnergyDataset',
    'PlasmaEnergyDataset',
    'EnterpriseEnergyDataset',
    'EnergyMapConfig',
    'create_dataloader',

    # Training
    'DiffusionTrainer',
    'TrainingConfig',

    # Callbacks
    'TrainingCallback',
    'CallbackList',
    'MetricsLogger',
    'ThermodynamicValidator',
    'EarlyStopping',
    'ProgressBar',
    'SampleGenerator',
    'GradientMonitor',
    'WandbLogger',
    'LearningRateScheduler',
]
