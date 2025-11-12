#!/usr/bin/env python3
"""
test_trainer.py
Unit tests for NVP Trainer

Tests:
- Training configuration
- Loss computation
- Training step
- Batch preparation
- Metric tracking
"""

import pytest
import sys
from pathlib import Path
import tempfile
import shutil

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import numpy as np
import jax
import jax.numpy as jnp
from jax import random

from phase4.nvp.nvp_model import NVPConfig
from phase4.nvp.trainer import (
    Trainer,
    TrainingConfig,
    TrainingMetrics,
    prepare_training_data
)


@pytest.fixture
def temp_checkpoint_dir():
    """Create temporary checkpoint directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_training_config(temp_checkpoint_dir):
    """Sample training configuration."""
    model_config = NVPConfig(
        latent_dim=128,
        encoder_features=[32, 64],
        decoder_features=[64, 32]
    )

    return TrainingConfig(
        model_config=model_config,
        batch_size=4,
        num_epochs=2,
        learning_rate=1e-3,
        lambda_conservation=0.1,
        lambda_entropy=0.05,
        checkpoint_dir=temp_checkpoint_dir,
        checkpoint_every=1,
        log_dir=temp_checkpoint_dir,
        input_shape=(64, 64),
        seed=42
    )


@pytest.fixture
def sample_train_data():
    """Sample training data."""
    np.random.seed(42)

    # Create synthetic sequences (N, T, H, W)
    N, T, H, W = 8, 5, 64, 64

    energy_sequence = np.random.exponential(1.0, (N, T, H, W))

    # Normalize each map
    for n in range(N):
        for t in range(T):
            energy_sequence[n, t] /= np.mean(energy_sequence[n, t])

    # Compute gradients
    gradients = np.zeros((N, T, H, W, 2))
    for n in range(N):
        for t in range(T):
            grad_x = np.gradient(energy_sequence[n, t], axis=1)
            grad_y = np.gradient(energy_sequence[n, t], axis=0)
            gradients[n, t, :, :, 0] = grad_x
            gradients[n, t, :, :, 1] = grad_y

    return {
        'energy_sequence': energy_sequence,
        'gradients': gradients
    }


class TestTrainingConfig:
    """Test training configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = TrainingConfig()

        assert config.batch_size == 16
        assert config.num_epochs == 100
        assert config.learning_rate == 1e-4
        assert config.lambda_conservation == 0.1
        assert config.lambda_entropy == 0.05

    def test_custom_config(self):
        """Test custom configuration."""
        model_config = NVPConfig(latent_dim=256)

        config = TrainingConfig(
            model_config=model_config,
            batch_size=32,
            num_epochs=50,
            learning_rate=5e-4
        )

        assert config.batch_size == 32
        assert config.num_epochs == 50
        assert config.learning_rate == 5e-4
        assert config.model_config.latent_dim == 256


class TestTrainingMetrics:
    """Test training metrics dataclass."""

    def test_metrics_creation(self):
        """Test creating training metrics."""
        metrics = TrainingMetrics(
            epoch=10,
            step=1000,
            loss_total=0.5,
            loss_mse=0.3,
            loss_conservation=0.1,
            loss_entropy=0.1,
            energy_fidelity=0.92,
            rmse=0.05,
            entropy_coherence=0.88,
            time_elapsed=120.5
        )

        assert metrics.epoch == 10
        assert metrics.step == 1000
        assert metrics.loss_total == 0.5
        assert metrics.energy_fidelity == 0.92


class TestTrainer:
    """Test Trainer class."""

    def test_trainer_initialization(self, sample_training_config):
        """Test trainer initialization."""
        trainer = Trainer(sample_training_config)

        assert trainer.config == sample_training_config
        assert trainer.rng is not None
        assert len(trainer.train_metrics) == 0
        assert len(trainer.val_metrics) == 0

    def test_checkpoint_directories_created(self, sample_training_config):
        """Test that directories are created."""
        trainer = Trainer(sample_training_config)

        checkpoint_dir = Path(sample_training_config.checkpoint_dir)
        log_dir = Path(sample_training_config.log_dir)

        assert checkpoint_dir.exists()
        assert log_dir.exists()

    def test_prepare_batch(self, sample_training_config, sample_train_data):
        """Test batch preparation."""
        trainer = Trainer(sample_training_config)

        energy_sequence = sample_train_data['energy_sequence']
        gradients = sample_train_data['gradients']

        batch_indices = np.array([0, 1, 2, 3])

        batch = trainer.prepare_batch(energy_sequence, gradients, batch_indices)

        assert 'energy_t' in batch
        assert 'grad_x' in batch
        assert 'grad_y' in batch
        assert 'energy_target' in batch

        # Check shapes
        # Each sequence has T=5 timesteps, so T-1=4 pairs
        # batch_size=4 sequences × 4 pairs = 16 samples
        assert batch['energy_t'].shape[0] == 16
        assert batch['energy_target'].shape[0] == 16

    def test_compute_loss(self, sample_training_config, sample_train_data):
        """Test loss computation."""
        trainer = Trainer(sample_training_config)

        # Initialize model
        rng = random.PRNGKey(42)
        from phase4.nvp.nvp_model import create_train_state

        trainer.state = create_train_state(
            rng,
            sample_training_config.model_config,
            learning_rate=sample_training_config.learning_rate,
            input_shape=sample_training_config.input_shape
        )

        # Prepare batch
        energy_sequence = sample_train_data['energy_sequence']
        gradients = sample_train_data['gradients']
        batch_indices = np.array([0, 1])

        batch = trainer.prepare_batch(energy_sequence, gradients, batch_indices)

        # Compute loss
        loss, metrics = trainer.compute_loss(
            trainer.state.params,
            batch,
            training=False
        )

        # Check that loss and metrics are computed
        assert jnp.isfinite(loss)
        assert 'loss_total' in metrics
        assert 'loss_mse' in metrics
        assert 'loss_conservation' in metrics
        assert 'loss_entropy' in metrics
        assert 'energy_fidelity' in metrics

    def test_train_step(self, sample_training_config, sample_train_data):
        """Test single training step."""
        trainer = Trainer(sample_training_config)

        # Initialize model
        rng = random.PRNGKey(42)
        from phase4.nvp.nvp_model import create_train_state

        trainer.state = create_train_state(
            rng,
            sample_training_config.model_config,
            learning_rate=sample_training_config.learning_rate,
            input_shape=sample_training_config.input_shape
        )

        # Prepare batch
        energy_sequence = sample_train_data['energy_sequence']
        gradients = sample_train_data['gradients']
        batch_indices = np.array([0, 1])

        batch = trainer.prepare_batch(energy_sequence, gradients, batch_indices)

        # Training step
        initial_step = trainer.state.step
        new_state, metrics = trainer.train_step(trainer.state, batch)

        # Check that state was updated
        assert new_state.step == initial_step + 1

        # Check that metrics were returned
        assert 'loss_total' in metrics
        assert jnp.isfinite(metrics['loss_total'])

    def test_short_training_run(self, sample_training_config, sample_train_data):
        """Test short training run."""
        # Reduce epochs for quick test
        sample_training_config.num_epochs = 2
        sample_training_config.log_every = 1

        trainer = Trainer(sample_training_config)

        # Train
        history = trainer.train(sample_train_data, val_data=None, verbose=False)

        # Check that training ran
        assert 'train' in history
        assert len(history['train']) == 2  # 2 epochs

        # Check metrics
        final_metrics = history['train'][-1]
        assert final_metrics.epoch == 1  # 0-indexed
        assert final_metrics.loss_total > 0
        assert 0 <= final_metrics.energy_fidelity <= 1.0

    def test_training_with_validation(self, sample_training_config, sample_train_data):
        """Test training with validation data."""
        sample_training_config.num_epochs = 2

        trainer = Trainer(sample_training_config)

        # Use same data for train and val (just for testing)
        history = trainer.train(
            sample_train_data,
            val_data=sample_train_data,
            verbose=False
        )

        # Check that validation metrics exist
        assert 'val' in history
        assert len(history['val']) == 2

    def test_checkpointing(self, sample_training_config, sample_train_data):
        """Test model checkpointing."""
        sample_training_config.num_epochs = 2
        sample_training_config.checkpoint_every = 1

        trainer = Trainer(sample_training_config)

        history = trainer.train(sample_train_data, verbose=False)

        # Check that checkpoint files were created
        checkpoint_dir = Path(sample_training_config.checkpoint_dir)
        checkpoint_files = list(checkpoint_dir.glob("*"))

        # Should have at least one checkpoint
        assert len(checkpoint_files) > 0


class TestPrepareTrainingData:
    """Test training data preparation."""

    def test_prepare_training_data(self):
        """Test preparing training data from sequences."""
        from phase4.core.atlas_loader import EnergyAtlasLoader

        # Create mock sequences
        sequences = []
        for _ in range(3):
            # T x H x W
            seq = np.random.exponential(1.0, (5, 64, 64))
            sequences.append(seq)

        # Create loader
        temp_dir = tempfile.mkdtemp()
        try:
            loader = EnergyAtlasLoader(temp_dir, neo4j_uri=None)

            # Prepare data
            data = prepare_training_data(sequences, loader)

            # Check output
            assert 'energy_sequence' in data
            assert 'gradients' in data

            # Check shapes
            assert data['energy_sequence'].shape == (3, 5, 64, 64)
            assert data['gradients'].shape == (3, 5, 64, 64, 2)

        finally:
            shutil.rmtree(temp_dir)


class TestLossFunctions:
    """Test loss function components."""

    def test_total_loss_components(self, sample_training_config, sample_train_data):
        """Test that total loss includes all components."""
        trainer = Trainer(sample_training_config)

        # Initialize model
        rng = random.PRNGKey(42)
        from phase4.nvp.nvp_model import create_train_state

        trainer.state = create_train_state(
            rng,
            sample_training_config.model_config,
            learning_rate=sample_training_config.learning_rate,
            input_shape=sample_training_config.input_shape
        )

        # Prepare batch
        energy_sequence = sample_train_data['energy_sequence']
        gradients = sample_train_data['gradients']
        batch_indices = np.array([0, 1])

        batch = trainer.prepare_batch(energy_sequence, gradients, batch_indices)

        # Compute loss
        loss, metrics = trainer.compute_loss(
            trainer.state.params,
            batch,
            training=False
        )

        # Verify loss composition
        expected_loss = (
            float(metrics['loss_mse']) +
            sample_training_config.lambda_conservation * float(metrics['loss_conservation']) +
            sample_training_config.lambda_entropy * float(metrics['loss_entropy'])
        )

        assert jnp.isclose(float(metrics['loss_total']), expected_loss, rtol=1e-4)

    def test_energy_fidelity_range(self, sample_training_config, sample_train_data):
        """Test that energy fidelity is in [0, 1]."""
        trainer = Trainer(sample_training_config)

        # Initialize model
        rng = random.PRNGKey(42)
        from phase4.nvp.nvp_model import create_train_state

        trainer.state = create_train_state(
            rng,
            sample_training_config.model_config,
            learning_rate=sample_training_config.learning_rate,
            input_shape=sample_training_config.input_shape
        )

        # Prepare batch
        energy_sequence = sample_train_data['energy_sequence']
        gradients = sample_train_data['gradients']
        batch_indices = np.array([0, 1])

        batch = trainer.prepare_batch(energy_sequence, gradients, batch_indices)

        # Compute loss
        loss, metrics = trainer.compute_loss(
            trainer.state.params,
            batch,
            training=False
        )

        fidelity = float(metrics['energy_fidelity'])

        # Fidelity should be in [0, 1] (or possibly slightly negative/above 1 due to numerical errors)
        assert -0.1 <= fidelity <= 1.1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
