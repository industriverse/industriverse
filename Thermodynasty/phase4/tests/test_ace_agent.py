#!/usr/bin/env python3
"""
test_ace_agent.py
Tests for ACE (Aspiration-Calibration-Execution) Agent - Phase 4
"""

import pytest
import numpy as np
import jax
import jax.numpy as jnp
from jax import random
from pathlib import Path
import tempfile

from phase4.ace.ace_agent import (
    ACEAgent,
    ACEConfig,
    AspirationConfig,
    CalibrationConfig,
    ExecutionConfig,
    AspirationLayer,
    CalibrationLayer,
    ExecutionLayer,
    PredictionResult
)
from phase4.nvp.nvp_model import NVPConfig


class TestAspirationLayer:
    """Tests for Aspiration Layer."""

    def test_aspiration_initialization(self):
        """Test aspiration layer initialization."""
        config = AspirationConfig(
            target_energy_fidelity=0.95,
            target_entropy_coherence=0.90,
            min_confidence=0.7
        )
        layer = AspirationLayer(config)

        assert layer.goals['energy_fidelity'] == 0.95
        assert layer.goals['entropy_coherence'] == 0.90
        assert layer.goals['confidence'] == 0.7

    def test_set_goal(self):
        """Test goal setting."""
        layer = AspirationLayer(AspirationConfig())

        layer.set_goal('energy_fidelity', 0.98)
        assert layer.goals['energy_fidelity'] == 0.98

    def test_assess_achievement_success(self):
        """Test achievement assessment when goals met."""
        layer = AspirationLayer(AspirationConfig(
            target_energy_fidelity=0.90,
            target_entropy_coherence=0.85,
            min_confidence=0.7
        ))

        result = PredictionResult(
            energy_pred=np.zeros((64, 64)),
            uncertainty=np.zeros((64, 64)),
            confidence=0.85,
            energy_fidelity=0.92,
            entropy_coherence=0.88
        )

        achievements = layer.assess_achievement(result)

        assert achievements['energy_fidelity'] is True
        assert achievements['entropy_coherence'] is True
        assert achievements['confidence'] is True
        assert achievements['overall'] is True

    def test_assess_achievement_failure(self):
        """Test achievement assessment when goals not met."""
        layer = AspirationLayer(AspirationConfig(
            target_energy_fidelity=0.95,
            min_confidence=0.8
        ))

        result = PredictionResult(
            energy_pred=np.zeros((64, 64)),
            uncertainty=np.zeros((64, 64)),
            confidence=0.75,  # Below threshold
            energy_fidelity=0.90,  # Below threshold
            entropy_coherence=0.90
        )

        achievements = layer.assess_achievement(result)

        assert achievements['energy_fidelity'] is False
        assert achievements['confidence'] is False
        assert achievements['overall'] is False

    def test_adjust_goals(self):
        """Test goal adjustment after failure."""
        layer = AspirationLayer(AspirationConfig(
            target_energy_fidelity=0.95,
            target_entropy_coherence=0.90
        ))

        original_fidelity = layer.goals['energy_fidelity']
        original_coherence = layer.goals['entropy_coherence']

        result = PredictionResult(
            energy_pred=np.zeros((64, 64)),
            uncertainty=np.zeros((64, 64)),
            confidence=0.5,
            energy_fidelity=0.7,
            entropy_coherence=0.7,
            aspiration_met=False
        )

        layer.adjust_goals(result, factor=0.9)

        # Goals should be relaxed
        assert layer.goals['energy_fidelity'] < original_fidelity
        assert layer.goals['entropy_coherence'] < original_coherence

        # But not below minimums
        assert layer.goals['energy_fidelity'] >= 0.7
        assert layer.goals['entropy_coherence'] >= 0.7


class TestCalibrationLayer:
    """Tests for Calibration Layer."""

    def test_calibration_initialization(self):
        """Test calibration layer initialization."""
        rng = random.PRNGKey(42)
        config = CalibrationConfig(
            num_samples=10,
            confidence_method="entropy"
        )
        layer = CalibrationLayer(config, rng)

        assert layer.config.num_samples == 10
        assert layer.config.confidence_method == "entropy"

    def test_estimate_uncertainty_entropy_method(self):
        """Test uncertainty estimation with entropy method."""
        rng = random.PRNGKey(42)
        config = CalibrationConfig(confidence_method="entropy")
        layer = CalibrationLayer(config, rng)

        # Low variance = high confidence
        mean_pred = jnp.ones((64, 64, 1))
        log_var_pred = jnp.ones((64, 64, 1)) * -5  # Low variance

        uncertainty, confidence = layer.estimate_uncertainty(mean_pred, log_var_pred)

        assert uncertainty.shape == (64, 64)
        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.5  # Should be confident with low variance

    def test_estimate_uncertainty_variance_method(self):
        """Test uncertainty estimation with variance method."""
        rng = random.PRNGKey(42)
        config = CalibrationConfig(confidence_method="variance")
        layer = CalibrationLayer(config, rng)

        # High variance = low confidence
        mean_pred = jnp.ones((64, 64, 1))
        log_var_pred = jnp.ones((64, 64, 1)) * 2  # High variance

        uncertainty, confidence = layer.estimate_uncertainty(mean_pred, log_var_pred)

        assert 0.0 <= confidence <= 1.0
        assert confidence < 0.5  # Should not be confident with high variance

    def test_ensemble_consensus(self):
        """Test BFT consensus from ensemble."""
        rng = random.PRNGKey(42)
        config = CalibrationConfig(
            ensemble_size=3,
            bft_max_disagreement=0.2
        )
        layer = CalibrationLayer(config, rng)

        # Create 3 similar predictions
        pred1 = np.ones((64, 64)) * 1.0
        pred2 = np.ones((64, 64)) * 1.05  # 5% difference
        pred3 = np.ones((64, 64)) * 0.98  # 2% difference

        predictions = [pred1, pred2, pred3]

        consensus, agreement, valid = layer.ensemble_consensus(predictions)

        assert consensus.shape == (64, 64)
        assert 0.0 <= agreement <= 1.0
        assert agreement > 0.8  # Should have high agreement
        assert valid is True  # Should achieve consensus

    def test_ensemble_consensus_disagreement(self):
        """Test consensus failure with disagreeing ensemble."""
        rng = random.PRNGKey(42)
        config = CalibrationConfig(
            ensemble_size=3,
            bft_max_disagreement=0.1  # Strict threshold
        )
        layer = CalibrationLayer(config, rng)

        # Create divergent predictions
        pred1 = np.ones((64, 64)) * 1.0
        pred2 = np.ones((64, 64)) * 1.5  # 50% different
        pred3 = np.ones((64, 64)) * 0.7  # 30% different

        predictions = [pred1, pred2, pred3]

        consensus, agreement, valid = layer.ensemble_consensus(predictions)

        assert agreement < 0.7  # Lower than high agreement
        assert valid is False  # Should fail strict consensus threshold


class TestExecutionLayer:
    """Tests for Execution Layer."""

    def test_execution_initialization(self):
        """Test execution layer initialization."""
        config = ExecutionConfig(
            nvp_config=NVPConfig(latent_dim=64),
            deterministic=True
        )
        rng = random.PRNGKey(42)

        layer = ExecutionLayer(config, model_path=None, rng=rng)

        assert layer.config.deterministic is True
        assert layer.state is not None

    def test_predict_shape(self):
        """Test prediction output shapes."""
        config = ExecutionConfig(
            nvp_config=NVPConfig(latent_dim=64),
            input_shape=(64, 64)  # Match test input size
        )
        rng = random.PRNGKey(42)
        layer = ExecutionLayer(config, model_path=None, rng=rng)

        # Create input
        energy_t = np.random.rand(64, 64)
        grad_x = np.random.rand(64, 64)
        grad_y = np.random.rand(64, 64)

        # Predict
        mean_pred, log_var_pred = layer.predict(energy_t, grad_x, grad_y)

        assert mean_pred.shape == (64, 64)
        assert log_var_pred.shape == (64, 64)
        assert np.all(np.isfinite(mean_pred))
        assert np.all(np.isfinite(log_var_pred))

    def test_predict_positive_energy(self):
        """Test that predictions are positive (due to softplus)."""
        config = ExecutionConfig(
            nvp_config=NVPConfig(latent_dim=64),
            input_shape=(64, 64)
        )
        rng = random.PRNGKey(42)
        layer = ExecutionLayer(config, model_path=None, rng=rng)

        energy_t = np.random.rand(64, 64)
        grad_x = np.zeros((64, 64))
        grad_y = np.zeros((64, 64))

        mean_pred, _ = layer.predict(energy_t, grad_x, grad_y)

        # All predictions should be positive (softplus activation)
        assert np.all(mean_pred >= 0.0)

    def test_energy_conservation_enforcement(self):
        """Test energy conservation enforcement."""
        config = ExecutionConfig(
            nvp_config=NVPConfig(latent_dim=64),
            input_shape=(64, 64),
            enforce_energy_conservation=True
        )
        rng = random.PRNGKey(42)
        layer = ExecutionLayer(config, model_path=None, rng=rng)

        energy_t = np.ones((64, 64))  # Total energy = 4096
        grad_x = np.zeros((64, 64))
        grad_y = np.zeros((64, 64))

        mean_pred, _ = layer.predict(energy_t, grad_x, grad_y)

        # Total energy should be conserved (within tolerance)
        pred_total = np.sum(mean_pred)
        ref_total = np.sum(energy_t)

        energy_error = abs(pred_total - ref_total) / ref_total
        assert energy_error < 0.01  # Within 1%


class TestACEAgent:
    """Tests for complete ACE Agent."""

    @pytest.fixture
    def ace_config(self):
        """Create test ACE configuration."""
        return ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.80,
                target_entropy_coherence=0.75,
                min_confidence=0.6
            ),
            calibration=CalibrationConfig(
                num_samples=5,
                confidence_method="entropy"
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(
                    latent_dim=64,
                    encoder_features=[32, 64],
                    decoder_features=[64, 32]
                ),
                input_shape=(64, 64)
            ),
            seed=42
        )

    def test_ace_agent_initialization(self, ace_config):
        """Test ACE agent initialization."""
        agent = ACEAgent(ace_config)

        assert agent.aspiration is not None
        assert agent.calibration is not None
        assert agent.execution is not None
        assert len(agent.history) == 0

    def test_ace_agent_predict(self, ace_config):
        """Test full ACE prediction."""
        agent = ACEAgent(ace_config)

        # Create test inputs
        energy_t = np.random.rand(64, 64)
        grad_x = np.random.rand(64, 64)
        grad_y = np.random.rand(64, 64)
        energy_target = np.random.rand(64, 64)

        # Make prediction
        result = agent.predict(energy_t, grad_x, grad_y, energy_target)

        # Check result structure
        assert result.energy_pred.shape == (64, 64)
        assert result.uncertainty.shape == (64, 64)
        assert 0.0 <= result.confidence <= 1.0
        assert 0.0 <= result.energy_fidelity <= 1.0
        assert result.execution_time > 0

        # Check history
        assert len(agent.history) == 1

    def test_ace_agent_metrics_with_target(self, ace_config):
        """Test metric computation with target."""
        agent = ACEAgent(ace_config)

        # Create inputs where prediction should match target well
        energy_t = np.ones((64, 64)) * 0.5
        grad_x = np.zeros((64, 64))
        grad_y = np.zeros((64, 64))
        energy_target = np.ones((64, 64)) * 0.7  # Similar to input

        result = agent.predict(energy_t, grad_x, grad_y, energy_target)

        # Metrics should be computed
        assert result.energy_fidelity > 0.0
        assert result.entropy_coherence >= 0.0

    def test_ace_agent_multiple_predictions(self, ace_config):
        """Test multiple sequential predictions."""
        agent = ACEAgent(ace_config)

        for i in range(3):
            energy_t = np.random.rand(64, 64)
            grad_x = np.random.rand(64, 64)
            grad_y = np.random.rand(64, 64)

            result = agent.predict(energy_t, grad_x, grad_y)
            assert result is not None

        # History should track all predictions
        assert len(agent.history) == 3

    def test_prediction_result_structure(self, ace_config):
        """Test PredictionResult dataclass structure."""
        agent = ACEAgent(ace_config)

        energy_t = np.ones((64, 64))
        grad_x = np.zeros((64, 64))
        grad_y = np.zeros((64, 64))

        result = agent.predict(energy_t, grad_x, grad_y)

        # Check all required fields present
        assert hasattr(result, 'energy_pred')
        assert hasattr(result, 'uncertainty')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'energy_fidelity')
        assert hasattr(result, 'entropy_coherence')
        assert hasattr(result, 'num_retries')
        assert hasattr(result, 'execution_time')
        assert hasattr(result, 'aspiration_met')
        assert hasattr(result, 'calibration_metrics')


class TestIntegration:
    """Integration tests for ACE components."""

    def test_aspiration_calibration_integration(self):
        """Test integration between aspiration and calibration layers."""
        rng = random.PRNGKey(42)
        aspiration = AspirationLayer(AspirationConfig(min_confidence=0.7))
        calibration = CalibrationLayer(CalibrationConfig(), rng)

        # Create low-confidence prediction
        mean_pred = jnp.ones((64, 64, 1))
        log_var_pred = jnp.ones((64, 64, 1)) * 3  # High variance

        uncertainty, confidence = calibration.estimate_uncertainty(mean_pred, log_var_pred)

        # Create result
        result = PredictionResult(
            energy_pred=np.array(mean_pred[:, :, 0]),
            uncertainty=uncertainty,
            confidence=confidence,
            energy_fidelity=0.85,
            entropy_coherence=0.80
        )

        # Aspiration should recognize low confidence
        achievements = aspiration.assess_achievement(result)

        if confidence < 0.7:
            assert achievements['confidence'] is False

    def test_full_ace_pipeline(self):
        """Test complete ACE pipeline end-to-end."""
        config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.75,
                min_confidence=0.5
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32),
                enforce_energy_conservation=True
            ),
            seed=42
        )

        agent = ACEAgent(config)

        # Simulate multi-step prediction
        energy_states = [np.random.rand(32, 32) for _ in range(5)]

        for i in range(len(energy_states) - 1):
            # Compute gradients
            grad_x = np.gradient(energy_states[i], axis=1)
            grad_y = np.gradient(energy_states[i], axis=0)

            # Predict next state
            result = agent.predict(
                energy_states[i],
                grad_x,
                grad_y,
                energy_states[i + 1]
            )

            # Check basic validity
            assert result.energy_pred.shape == energy_states[i].shape
            assert np.all(np.isfinite(result.energy_pred))

        # Check history
        assert len(agent.history) == 4
