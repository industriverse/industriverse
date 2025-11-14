"""
Tests for diffusion training pipeline
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import tempfile
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from phase5.diffusion.training import (
    DiffusionTrainer,
    TrainingConfig,
    EnergyMapDataset,
    SyntheticEnergyDataset,
    create_dataloader,
    MetricsLogger,
    ThermodynamicValidator,
    EarlyStopping
)
from phase5.diffusion import DiffusionModel, DiffusionConfig


class TestSyntheticDataset:
    """Test synthetic energy dataset generation"""

    def test_gaussian_mixture_generation(self):
        """Test Gaussian mixture energy map generation"""
        dataset = SyntheticEnergyDataset(
            num_samples=10,
            resolution=(64, 64),
            energy_type='gaussian_mixture'
        )

        assert len(dataset) == 10

        sample = dataset[0]
        assert 'energy_map' in sample
        assert sample['energy_map'].shape == (1, 64, 64)
        assert sample['domain'] == 'synthetic'

    def test_harmonic_generation(self):
        """Test harmonic potential generation"""
        dataset = SyntheticEnergyDataset(
            num_samples=5,
            resolution=(32, 32),
            energy_type='harmonic'
        )

        sample = dataset[0]
        energy_map = sample['energy_map'].squeeze()

        # Harmonic potential should be quadratic from center
        assert energy_map.shape == (32, 32)
        assert energy_map.min() >= 0  # Energy should be positive

    def test_reproducibility(self):
        """Test that same index produces same sample"""
        dataset = SyntheticEnergyDataset(
            num_samples=10,
            resolution=(64, 64),
            energy_type='gaussian_mixture'
        )

        sample1 = dataset[5]
        sample2 = dataset[5]

        # Should be identical due to seeded generation
        assert torch.allclose(sample1['energy_map'], sample2['energy_map'])


class TestDataLoader:
    """Test data loader creation"""

    def test_dataloader_creation(self):
        """Test creating PyTorch DataLoader"""
        dataset = SyntheticEnergyDataset(
            num_samples=32,
            resolution=(64, 64)
        )

        dataloader = create_dataloader(
            dataset,
            batch_size=8,
            shuffle=True,
            num_workers=0  # Use 0 for testing
        )

        batch = next(iter(dataloader))
        assert batch['energy_map'].shape == (8, 1, 64, 64)

    def test_batch_size(self):
        """Test different batch sizes"""
        dataset = SyntheticEnergyDataset(num_samples=20)

        for batch_size in [1, 4, 8]:
            dataloader = create_dataloader(
                dataset,
                batch_size=batch_size,
                num_workers=0
            )

            batch = next(iter(dataloader))
            assert batch['energy_map'].shape[0] == batch_size


class TestTrainingConfig:
    """Test training configuration"""

    def test_default_config(self):
        """Test default training configuration"""
        config = TrainingConfig()

        assert config.num_epochs == 100
        assert config.batch_size == 32
        assert config.learning_rate == 1e-4
        assert config.timesteps == 1000

    def test_custom_config(self):
        """Test custom configuration"""
        config = TrainingConfig(
            num_epochs=50,
            batch_size=16,
            learning_rate=5e-4,
            timesteps=500
        )

        assert config.num_epochs == 50
        assert config.batch_size == 16
        assert config.learning_rate == 5e-4
        assert config.timesteps == 500


class TestDiffusionTrainer:
    """Test diffusion model trainer"""

    @pytest.fixture
    def setup_trainer(self):
        """Setup trainer with minimal configuration"""
        # Create synthetic dataset
        dataset = SyntheticEnergyDataset(
            num_samples=16,
            resolution=(32, 32)
        )

        dataloader = create_dataloader(
            dataset,
            batch_size=4,
            num_workers=0
        )

        # Create diffusion model
        diffusion_config = DiffusionConfig(
            timesteps=100,
            noise_schedule='linear',
            device='cpu'
        )
        model = DiffusionModel(diffusion_config)

        # Create training config
        training_config = TrainingConfig(
            num_epochs=2,
            batch_size=4,
            learning_rate=1e-4,
            timesteps=100,
            device='cpu',
            save_every_n_epochs=1,
            log_every_n_steps=5,
            validate_every_n_steps=10
        )

        # Create trainer
        trainer = DiffusionTrainer(
            model=model,
            train_dataloader=dataloader,
            config=training_config
        )

        return trainer

    def test_trainer_initialization(self, setup_trainer):
        """Test trainer initializes correctly"""
        trainer = setup_trainer

        assert trainer.model is not None
        assert trainer.optimizer is not None
        assert trainer.scheduler is not None
        assert trainer.current_epoch == 0
        assert trainer.global_step == 0

    def test_training_step(self, setup_trainer):
        """Test single training step"""
        trainer = setup_trainer

        # Get a batch
        batch = next(iter(trainer.train_dataloader))

        # Perform training step
        loss, metrics = trainer._training_step(batch)

        assert isinstance(loss.item(), float)
        assert loss.item() >= 0

    def test_short_training(self, setup_trainer):
        """Test training for 2 epochs"""
        trainer = setup_trainer

        # Train
        metrics_history = trainer.train()

        # Should have 2 epochs
        assert len(metrics_history) == 2

        # Should have decreasing loss (generally)
        assert 'train' in metrics_history[0]
        assert 'loss' in metrics_history[0]['train']


class TestTrainingCallbacks:
    """Test training callbacks"""

    def test_metrics_logger(self):
        """Test metrics logging callback"""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = Path(tmpdir) / 'metrics.json'

            logger = MetricsLogger(log_path=str(log_path))

            # Simulate epoch end
            metrics = {
                'epoch': 0,
                'train': {'loss': 0.5},
                'val': {'loss': 0.6}
            }

            logger.on_epoch_end(0, metrics, None)

            # Check file was created
            assert log_path.exists()

    def test_thermodynamic_validator_callback(self):
        """Test thermodynamic validation callback"""
        validator = ThermodynamicValidator(
            validation_frequency=10,
            energy_tolerance=0.01
        )

        # Simulate batch end with good metrics
        metrics = {
            'energy_fidelity': 0.99,
            'entropy_valid': 1.0
        }

        validator.on_batch_end(10, metrics, None)

        # Should have no violations
        assert len(validator.violations) == 0

    def test_early_stopping(self):
        """Test early stopping callback"""
        early_stop = EarlyStopping(patience=3, min_delta=0.01)

        # Simulate improving epochs
        for i in range(3):
            metrics = {'val': {'loss': 1.0 - i * 0.1}}
            early_stop.on_epoch_end(i, metrics, None)

        assert not early_stop.should_stop

        # Simulate stagnant epochs
        for i in range(3, 7):
            metrics = {'val': {'loss': 0.7}}
            early_stop.on_epoch_end(i, metrics, None)

        # Should trigger early stopping
        assert early_stop.should_stop


class TestCheckpointing:
    """Test model checkpointing"""

    def test_checkpoint_save_load(self):
        """Test saving and loading checkpoints"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create trainer
            dataset = SyntheticEnergyDataset(num_samples=8, resolution=(32, 32))
            dataloader = create_dataloader(dataset, batch_size=4, num_workers=0)

            diffusion_config = DiffusionConfig(timesteps=100, device='cpu')
            model = DiffusionModel(diffusion_config)

            training_config = TrainingConfig(
                num_epochs=1,
                checkpoint_dir=tmpdir,
                device='cpu'
            )

            trainer = DiffusionTrainer(
                model=model,
                train_dataloader=dataloader,
                config=training_config
            )

            # Save checkpoint
            metrics = {'epoch': 0, 'train': {'loss': 0.5}}
            trainer._save_checkpoint(0, metrics)

            # Check checkpoint exists
            checkpoint_files = list(Path(tmpdir).glob('checkpoint_*.pt'))
            assert len(checkpoint_files) > 0

            # Load checkpoint
            checkpoint_path = checkpoint_files[0]
            trainer.load_checkpoint(str(checkpoint_path))

            assert trainer.current_epoch == 0
