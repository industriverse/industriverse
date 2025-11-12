#!/usr/bin/env python3
"""
test_nvp_model.py
Unit tests for NVP Model

Tests:
- Model architecture
- Forward pass shapes
- Energy conservation loss
- Entropy smoothness loss
- Thermodynamic constraints
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import jax
import jax.numpy as jnp
from jax import random
import numpy as np

from phase4.nvp.nvp_model import (
    NVPModel,
    NVPConfig,
    ResidualBlock,
    Encoder,
    Decoder,
    create_train_state,
    compute_energy_conservation_loss,
    compute_entropy,
    compute_entropy_smoothness_loss
)


@pytest.fixture
def rng():
    """Random key fixture."""
    return random.PRNGKey(42)


@pytest.fixture
def sample_config():
    """Sample NVP configuration."""
    return NVPConfig(
        latent_dim=128,
        encoder_features=[32, 64],
        decoder_features=[64, 32],
        use_residual=True,
        use_batch_norm=True,
        dropout_rate=0.1
    )


@pytest.fixture
def sample_inputs(rng):
    """Sample input tensors."""
    batch_size = 4
    H, W = 64, 64

    energy_t = random.normal(rng, (batch_size, H, W, 1))
    grad_x = random.normal(rng, (batch_size, H, W, 1))
    grad_y = random.normal(rng, (batch_size, H, W, 1))

    return energy_t, grad_x, grad_y


class TestNVPConfig:
    """Test NVP configuration."""

    def test_default_config(self):
        """Test default configuration values."""
        config = NVPConfig()

        assert config.latent_dim == 512
        assert config.encoder_features == [64, 128, 256]
        assert config.decoder_features == [256, 128, 64]
        assert config.use_residual is True
        assert config.use_batch_norm is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = NVPConfig(
            latent_dim=256,
            encoder_features=[32, 64],
            dropout_rate=0.2
        )

        assert config.latent_dim == 256
        assert config.encoder_features == [32, 64]
        assert config.dropout_rate == 0.2


class TestResidualBlock:
    """Test ResidualBlock module."""

    def test_forward_pass(self, rng):
        """Test forward pass through residual block."""
        block = ResidualBlock(features=64)

        x = random.normal(rng, (4, 32, 32, 64))
        params = block.init(rng, x, training=False)
        output = block.apply(params, x, training=False)

        assert output.shape == x.shape

    def test_residual_connection(self, rng):
        """Test that residual connection is working."""
        block = ResidualBlock(features=64, dropout_rate=0.0)

        x = jnp.ones((1, 16, 16, 64))
        params = block.init(rng, x, training=False)
        output = block.apply(params, x, training=False)

        # Output should not be identical to input due to conv layers
        assert not jnp.allclose(output, x)

    def test_feature_projection(self, rng):
        """Test feature projection when input/output dims differ."""
        block = ResidualBlock(features=128)

        x = random.normal(rng, (2, 16, 16, 64))
        params = block.init(rng, x, training=False)
        output = block.apply(params, x, training=False)

        # Output should have projected features
        assert output.shape == (2, 16, 16, 128)


class TestEncoder:
    """Test Encoder module."""

    def test_forward_pass(self, rng):
        """Test encoder forward pass."""
        encoder = Encoder(features=[32, 64])

        x = random.normal(rng, (4, 64, 64, 1))
        params = encoder.init(rng, x, training=False)
        output = encoder.apply(params, x, training=False)

        # Encoder should downsample by 2^len(features)
        expected_H = 64 // (2 ** 2)  # 16
        expected_W = 64 // (2 ** 2)  # 16
        expected_C = 64  # Last feature dim

        assert output.shape == (4, expected_H, expected_W, expected_C)

    def test_downsampling(self, rng):
        """Test that encoder downsamples correctly."""
        encoder = Encoder(features=[16, 32, 64])

        x = random.normal(rng, (1, 128, 128, 1))
        params = encoder.init(rng, x, training=False)
        output = encoder.apply(params, x, training=False)

        # 3 layers with stride=2 each: 128 → 64 → 32 → 16
        assert output.shape[1] == 16
        assert output.shape[2] == 16


class TestDecoder:
    """Test Decoder module."""

    def test_forward_pass(self, rng):
        """Test decoder forward pass."""
        decoder = Decoder(features=[64, 32], output_channels=1)

        x = random.normal(rng, (4, 16, 16, 64))
        params = decoder.init(rng, x, training=False)
        output = decoder.apply(params, x, training=False)

        # Decoder should upsample by 2^len(features)
        expected_H = 16 * (2 ** 2)  # 64
        expected_W = 16 * (2 ** 2)  # 64

        assert output.shape == (4, expected_H, expected_W, 1)

    def test_upsampling(self, rng):
        """Test that decoder upsamples correctly."""
        decoder = Decoder(features=[128, 64, 32], output_channels=1)

        x = random.normal(rng, (1, 8, 8, 128))
        params = decoder.init(rng, x, training=False)
        output = decoder.apply(params, x, training=False)

        # 3 layers with stride=2 each: 8 → 16 → 32 → 64
        assert output.shape[1] == 64
        assert output.shape[2] == 64
        assert output.shape[3] == 1


class TestNVPModel:
    """Test NVPModel."""

    def test_model_initialization(self, rng, sample_config):
        """Test model initialization."""
        model = NVPModel(sample_config)

        # Initialize with dummy inputs
        energy_t = jnp.ones((1, 64, 64, 1))
        grad_x = jnp.ones((1, 64, 64, 1))
        grad_y = jnp.ones((1, 64, 64, 1))

        params = model.init(rng, energy_t, grad_x, grad_y, training=False)

        assert 'params' in params

    def test_forward_pass_shape(self, rng, sample_config, sample_inputs):
        """Test that forward pass returns correct shapes."""
        model = NVPModel(sample_config)

        energy_t, grad_x, grad_y = sample_inputs

        params = model.init(rng, energy_t, grad_x, grad_y, training=False)
        mean, log_var = model.apply(params, energy_t, grad_x, grad_y, training=False)

        # Output should match input shape
        assert mean.shape == energy_t.shape
        assert log_var.shape == energy_t.shape

    def test_predict_deterministic(self, rng, sample_config, sample_inputs):
        """Test deterministic prediction."""
        model = NVPModel(sample_config)

        energy_t, grad_x, grad_y = sample_inputs

        params = model.init(rng, energy_t, grad_x, grad_y, training=False)

        # Predict without sampling
        pred1 = model.apply(params, energy_t, grad_x, grad_y, method=model.predict)
        pred2 = model.apply(params, energy_t, grad_x, grad_y, method=model.predict)

        # Should be deterministic (same result)
        assert jnp.allclose(pred1, pred2)

    def test_predict_stochastic(self, rng, sample_config, sample_inputs):
        """Test stochastic prediction with sampling."""
        model = NVPModel(sample_config)

        energy_t, grad_x, grad_y = sample_inputs

        params = model.init(rng, energy_t, grad_x, grad_y, training=False)

        # Predict with different random keys
        rng1, rng2 = random.split(rng)

        pred1 = model.apply(
            params, energy_t, grad_x, grad_y, rng=rng1,
            method=model.predict
        )
        pred2 = model.apply(
            params, energy_t, grad_x, grad_y, rng=rng2,
            method=model.predict
        )

        # Should be stochastic (different results)
        assert not jnp.allclose(pred1, pred2)

    def test_output_values_finite(self, rng, sample_config, sample_inputs):
        """Test that outputs are finite."""
        model = NVPModel(sample_config)

        energy_t, grad_x, grad_y = sample_inputs

        params = model.init(rng, energy_t, grad_x, grad_y, training=False)
        mean, log_var = model.apply(params, energy_t, grad_x, grad_y, training=False)

        assert jnp.all(jnp.isfinite(mean))
        assert jnp.all(jnp.isfinite(log_var))


class TestTrainState:
    """Test train state creation."""

    def test_create_train_state(self, rng, sample_config):
        """Test creating train state."""
        state = create_train_state(
            rng,
            sample_config,
            learning_rate=1e-4,
            input_shape=(64, 64)
        )

        assert state is not None
        assert hasattr(state, 'params')
        assert hasattr(state, 'opt_state')
        assert hasattr(state, 'step')

    def test_train_state_step_increment(self, rng, sample_config):
        """Test that train state step increments."""
        state = create_train_state(rng, sample_config, input_shape=(64, 64))

        assert state.step == 0

        # Dummy gradient update
        grads = jax.tree.map(lambda x: jnp.zeros_like(x), state.params)
        state = state.apply_gradients(grads=grads)

        assert state.step == 1


class TestEnergyConservationLoss:
    """Test energy conservation loss function."""

    def test_perfect_conservation(self):
        """Test loss is zero for perfect conservation."""
        E_pred = jnp.ones((4, 32, 32, 1)) * 2.0
        E_target = jnp.ones((4, 32, 32, 1)) * 2.0

        loss = compute_energy_conservation_loss(E_pred, E_target)

        assert jnp.isclose(loss, 0.0, atol=1e-6)

    def test_conservation_violation(self):
        """Test loss is non-zero for violation."""
        E_pred = jnp.ones((4, 32, 32, 1)) * 2.0
        E_target = jnp.ones((4, 32, 32, 1)) * 1.0  # 50% difference

        loss = compute_energy_conservation_loss(E_pred, E_target)

        # Relative error should be ~1.0 (100%)
        assert loss > 0.9 and loss < 1.1

    def test_small_violation(self):
        """Test loss for small violation."""
        E_pred = jnp.ones((4, 32, 32, 1)) * 1.05
        E_target = jnp.ones((4, 32, 32, 1)) * 1.0  # 5% difference

        loss = compute_energy_conservation_loss(E_pred, E_target)

        # Should be approximately 0.05
        assert jnp.isclose(loss, 0.05, atol=0.01)


class TestEntropyComputation:
    """Test entropy computation."""

    def test_entropy_positive(self, rng):
        """Test that entropy is always positive."""
        E = random.exponential(rng, (4, 32, 32, 1))

        entropy = compute_entropy(E)

        assert jnp.all(entropy > 0)

    def test_uniform_distribution_high_entropy(self):
        """Test that uniform distribution has high entropy."""
        # Uniform energy distribution
        E_uniform = jnp.ones((1, 32, 32, 1))

        # Concentrated energy distribution
        E_concentrated = jnp.zeros((1, 32, 32, 1))
        E_concentrated = E_concentrated.at[0, 16, 16, 0].set(32 * 32)

        S_uniform = compute_entropy(E_uniform)[0]
        S_concentrated = compute_entropy(E_concentrated)[0]

        # Uniform should have higher entropy
        assert S_uniform > S_concentrated

    def test_entropy_shape(self, rng):
        """Test entropy output shape."""
        E = random.exponential(rng, (8, 64, 64, 1))

        entropy = compute_entropy(E)

        # Should return one entropy value per batch element
        assert entropy.shape == (8,)


class TestEntropySmoothnessLoss:
    """Test entropy smoothness loss."""

    def test_no_violation(self):
        """Test zero loss when entropy increases."""
        # E_pred has higher entropy (more uniform)
        E_pred = jnp.ones((4, 32, 32, 1))

        # E_target has lower entropy (concentrated)
        E_target = jnp.zeros((4, 32, 32, 1))
        E_target = E_target.at[:, 16, 16, 0].set(32 * 32)

        loss = compute_entropy_smoothness_loss(E_pred, E_target, threshold=0.1)

        # No violation (entropy increased)
        assert jnp.isclose(loss, 0.0, atol=1e-4)

    def test_entropy_violation(self):
        """Test non-zero loss when entropy decreases significantly."""
        # E_pred has lower entropy (concentrated)
        E_pred = jnp.zeros((4, 32, 32, 1))
        E_pred = E_pred.at[:, 16, 16, 0].set(32 * 32)

        # E_target has higher entropy (uniform)
        E_target = jnp.ones((4, 32, 32, 1))

        loss = compute_entropy_smoothness_loss(E_pred, E_target, threshold=0.1)

        # Should have violation (entropy decreased)
        assert loss > 0


class TestThermodynamicConstraints:
    """Test thermodynamic constraint enforcement."""

    def test_energy_bounded(self, rng, sample_config, sample_inputs):
        """Test that predicted energy remains bounded."""
        model = NVPModel(sample_config)

        energy_t, grad_x, grad_y = sample_inputs

        params = model.init(rng, energy_t, grad_x, grad_y, training=False)
        mean, _ = model.apply(params, energy_t, grad_x, grad_y, training=False)

        # Energy should be finite and bounded
        assert jnp.all(jnp.isfinite(mean))
        assert jnp.all(jnp.abs(mean) < 1000)  # Reasonable bound

    def test_gradient_flow(self, rng, sample_config, sample_inputs):
        """Test that gradients flow through the model."""
        model = NVPModel(sample_config)

        energy_t, grad_x, grad_y = sample_inputs

        params = model.init(rng, energy_t, grad_x, grad_y, training=False)

        def loss_fn(params):
            mean, _ = model.apply(params, energy_t, grad_x, grad_y, training=False)
            return jnp.mean(mean ** 2)

        grads = jax.grad(loss_fn)(params)

        # Check that gradients exist and are finite
        def check_grads(grad_tree):
            leaves = jax.tree_util.tree_leaves(grad_tree)
            return all(jnp.all(jnp.isfinite(leaf)) for leaf in leaves)

        assert check_grads(grads)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
