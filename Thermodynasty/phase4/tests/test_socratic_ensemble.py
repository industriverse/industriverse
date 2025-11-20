#!/usr/bin/env python3
"""
test_socratic_ensemble.py
Tests for Socratic Loop and Shadow Ensemble - Phase 4
"""

import pytest
import numpy as np
from jax import random

from phase4.ace.ace_agent import (
    ACEAgent,
    ACEConfig,
    AspirationConfig,
    CalibrationConfig,
    ExecutionConfig,
    PredictionResult
)
from phase4.ace.socratic_loop import (
    SocraticLoop,
    SocraticConfig,
    SocraticACEAgent,
    FailureMode,
    ErrorAnalysis
)
from phase4.ace.shadow_ensemble import (
    ShadowEnsemble,
    EnsembleConfig,
    EnsembleResult,
    EnsembleACEAgent
)
from phase4.nvp.nvp_model import NVPConfig


class TestSocraticLoop:
    """Tests for Socratic self-correction loop."""

    def test_socratic_loop_initialization(self):
        """Test Socratic loop initialization."""
        config = SocraticConfig(
            max_iterations=3,
            energy_drift_threshold=0.1
        )
        loop = SocraticLoop(config)

        assert loop.config.max_iterations == 3
        assert len(loop.iteration_history) == 0

    def test_analyze_failure_energy_drift(self):
        """Test failure analysis for energy drift."""
        config = SocraticConfig(energy_drift_threshold=0.1)
        loop = SocraticLoop(config)

        # Create result with poor energy fidelity
        result = PredictionResult(
            energy_pred=np.ones((64, 64)),
            uncertainty=np.zeros((64, 64)),
            confidence=0.8,
            energy_fidelity=0.7,  # 30% drift - exceeds threshold
            entropy_coherence=0.9
        )

        analysis = loop.analyze_failure(result)

        assert FailureMode.ENERGY_DRIFT in analysis.failure_modes
        assert FailureMode.ENERGY_DRIFT in analysis.severity
        assert analysis.severity[FailureMode.ENERGY_DRIFT] > 0.0

    def test_analyze_failure_high_uncertainty(self):
        """Test failure analysis for high uncertainty."""
        config = SocraticConfig(uncertainty_threshold=0.2)
        loop = SocraticLoop(config)

        result = PredictionResult(
            energy_pred=np.ones((64, 64)),
            uncertainty=np.ones((64, 64)) * 0.5,  # High uncertainty
            confidence=0.9,
            energy_fidelity=0.95,
            entropy_coherence=0.9,
            calibration_metrics={'mean_uncertainty': 0.5}
        )

        analysis = loop.analyze_failure(result)

        assert FailureMode.HIGH_UNCERTAINTY in analysis.failure_modes
        assert 'uncertainty' in analysis.root_causes[FailureMode.HIGH_UNCERTAINTY].lower()

    def test_analyze_failure_low_confidence(self):
        """Test failure analysis for low confidence."""
        config = SocraticConfig(confidence_threshold=0.7)
        loop = SocraticLoop(config)

        result = PredictionResult(
            energy_pred=np.ones((64, 64)),
            uncertainty=np.zeros((64, 64)),
            confidence=0.5,  # Below threshold
            energy_fidelity=0.95,
            entropy_coherence=0.9
        )

        analysis = loop.analyze_failure(result)

        assert FailureMode.LOW_CONFIDENCE in analysis.failure_modes
        assert analysis.severity[FailureMode.LOW_CONFIDENCE] > 0.0

    def test_analyze_failure_entropy_violation(self):
        """Test failure analysis for entropy violation."""
        config = SocraticConfig()
        loop = SocraticLoop(config)

        result = PredictionResult(
            energy_pred=np.ones((64, 64)),
            uncertainty=np.zeros((64, 64)),
            confidence=0.9,
            energy_fidelity=0.95,
            entropy_coherence=0.6  # Low coherence
        )

        analysis = loop.analyze_failure(result)

        assert FailureMode.ENTROPY_VIOLATION in analysis.failure_modes

    def test_analyze_failure_poor_spatial_fit(self):
        """Test failure analysis for poor spatial fit."""
        config = SocraticConfig()
        loop = SocraticLoop(config)

        # Create prediction far from target
        pred = np.ones((64, 64)) * 0.5
        target = np.ones((64, 64)) * 2.0  # Very different

        result = PredictionResult(
            energy_pred=pred,
            uncertainty=np.zeros((64, 64)),
            confidence=0.9,
            energy_fidelity=0.95,
            entropy_coherence=0.9
        )

        analysis = loop.analyze_failure(result, target)

        assert FailureMode.POOR_SPATIAL_FIT in analysis.failure_modes

    def test_refine_strategy(self):
        """Test strategy refinement based on analysis."""
        config = SocraticConfig(verbose=False)
        loop = SocraticLoop(config)

        ace_config = ACEConfig(
            aspiration=AspirationConfig(min_confidence=0.8),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        agent = ACEAgent(ace_config)

        # Create failure analysis
        analysis = ErrorAnalysis(
            failure_modes=[FailureMode.LOW_CONFIDENCE],
            severity={FailureMode.LOW_CONFIDENCE: 0.8},
            root_causes={FailureMode.LOW_CONFIDENCE: "Test"},
            suggested_fixes={FailureMode.LOW_CONFIDENCE: "Test"}
        )

        original_confidence_goal = agent.aspiration.goals['confidence']

        # Refine strategy
        loop.refine_strategy(agent, analysis, iteration=1)

        # Confidence goal should be adjusted
        assert agent.aspiration.goals['confidence'] != original_confidence_goal

    def test_predict_with_correction_success(self):
        """Test prediction with correction that succeeds."""
        socratic_config = SocraticConfig(max_iterations=2, verbose=False)
        loop = SocraticLoop(socratic_config)

        ace_config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.6,  # Easy to achieve
                min_confidence=0.3
            ),
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )
        agent = ACEAgent(ace_config)

        energy_t = np.random.rand(32, 32)
        grad_x = np.random.rand(32, 32)
        grad_y = np.random.rand(32, 32)

        result, history = loop.predict_with_correction(
            agent, energy_t, grad_x, grad_y
        )

        assert result is not None
        assert result.energy_pred.shape == (32, 32)
        assert isinstance(history, list)

    def test_generate_report(self):
        """Test Socratic report generation."""
        config = SocraticConfig()
        loop = SocraticLoop(config)

        # Add some history
        analysis = ErrorAnalysis(
            failure_modes=[FailureMode.ENERGY_DRIFT],
            severity={FailureMode.ENERGY_DRIFT: 0.5},
            root_causes={FailureMode.ENERGY_DRIFT: "Test cause"},
            suggested_fixes={FailureMode.ENERGY_DRIFT: "Test fix"}
        )
        loop.iteration_history.append(analysis)

        report = loop.generate_report()

        assert isinstance(report, str)
        assert "SOCRATIC LOOP" in report
        assert "energy_drift" in report.lower()


class TestSocraticACEAgent:
    """Tests for integrated Socratic ACE Agent."""

    def test_socratic_ace_agent_initialization(self):
        """Test Socratic ACE agent initialization."""
        ace_config = ACEConfig(
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )
        socratic_config = SocraticConfig(max_iterations=3)

        agent = SocraticACEAgent(ace_config, socratic_config)

        assert agent.socratic_loop is not None
        assert agent.socratic_loop.config.max_iterations == 3

    def test_socratic_ace_agent_predict_with_correction(self):
        """Test integrated prediction with correction."""
        ace_config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.5,
                min_confidence=0.3
            ),
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )
        socratic_config = SocraticConfig(max_iterations=2, verbose=False)

        agent = SocraticACEAgent(ace_config, socratic_config)

        energy_t = np.random.rand(32, 32)
        grad_x = np.random.rand(32, 32)
        grad_y = np.random.rand(32, 32)

        result, history = agent.predict_with_correction(energy_t, grad_x, grad_y)

        assert result is not None
        assert isinstance(history, list)


class TestShadowEnsemble:
    """Tests for Shadow Ensemble with BFT."""

    def test_shadow_ensemble_initialization(self):
        """Test ensemble initialization."""
        ensemble_config = EnsembleConfig(num_models=3)
        ace_config = ACEConfig(
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )

        ensemble = ShadowEnsemble(ensemble_config, ace_config)

        assert len(ensemble.models) == 3
        assert ensemble.config.num_models == 3

    def test_ensemble_predict(self):
        """Test ensemble prediction."""
        ensemble_config = EnsembleConfig(num_models=3)
        ace_config = ACEConfig(
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )

        ensemble = ShadowEnsemble(ensemble_config, ace_config)

        energy_t = np.random.rand(32, 32)
        grad_x = np.random.rand(32, 32)
        grad_y = np.random.rand(32, 32)

        result = ensemble.predict(energy_t, grad_x, grad_y)

        assert isinstance(result, EnsembleResult)
        assert result.consensus_pred.shape == (32, 32)
        assert result.ensemble_uncertainty.shape == (32, 32)
        assert len(result.individual_preds) == 3
        assert len(result.individual_confidences) == 3

    def test_ensemble_consensus_valid(self):
        """Test valid BFT consensus."""
        ensemble_config = EnsembleConfig(
            num_models=3,
            max_disagreement=0.5  # Lenient
        )
        ace_config = ACEConfig(
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )

        ensemble = ShadowEnsemble(ensemble_config, ace_config)

        energy_t = np.ones((32, 32)) * 0.5
        grad_x = np.zeros((32, 32))
        grad_y = np.zeros((32, 32))

        result = ensemble.predict(energy_t, grad_x, grad_y)

        # With same input, models should produce similar outputs
        assert 0.0 <= result.agreement_score <= 1.0
        # Consensus should be achievable with lenient threshold
        assert result.num_agreeing >= 2  # At least 2/3 agree

    def test_ensemble_uncertainty_shape(self):
        """Test ensemble uncertainty computation."""
        ensemble_config = EnsembleConfig(num_models=3)
        ace_config = ACEConfig(
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )

        ensemble = ShadowEnsemble(ensemble_config, ace_config)

        energy_t = np.random.rand(32, 32)
        grad_x = np.random.rand(32, 32)
        grad_y = np.random.rand(32, 32)

        result = ensemble.predict(energy_t, grad_x, grad_y)

        # Uncertainty should be spatial map
        assert result.ensemble_uncertainty.shape == (32, 32)
        assert np.all(result.ensemble_uncertainty >= 0.0)


class TestEnsembleACEAgent:
    """Tests for ACE Agent with Shadow Ensemble."""

    def test_ensemble_ace_agent_initialization(self):
        """Test ensemble ACE agent initialization."""
        ace_config = ACEConfig(
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )
        ensemble_config = EnsembleConfig(num_models=3)

        agent = EnsembleACEAgent(ace_config, ensemble_config)

        assert agent.ensemble is not None
        assert len(agent.ensemble.models) == 3

    def test_ensemble_ace_agent_predict(self):
        """Test prediction with ensemble."""
        ace_config = ACEConfig(
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )
        ensemble_config = EnsembleConfig(num_models=3)

        agent = EnsembleACEAgent(ace_config, ensemble_config)

        energy_t = np.random.rand(32, 32)
        grad_x = np.random.rand(32, 32)
        grad_y = np.random.rand(32, 32)

        result = agent.predict(energy_t, grad_x, grad_y)

        assert result.energy_pred.shape == (32, 32)
        assert result.ensemble_predictions is not None
        assert len(result.ensemble_predictions) == 3

    def test_ensemble_diagnostics(self):
        """Test ensemble diagnostic metrics."""
        ace_config = ACEConfig(
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )
        ensemble_config = EnsembleConfig(num_models=3)

        agent = EnsembleACEAgent(ace_config, ensemble_config)

        # Make a few predictions
        for _ in range(3):
            energy_t = np.random.rand(32, 32)
            grad_x = np.random.rand(32, 32)
            grad_y = np.random.rand(32, 32)
            agent.predict(energy_t, grad_x, grad_y)

        diagnostics = agent.get_ensemble_diagnostics()

        assert 'total_predictions' in diagnostics
        assert diagnostics['total_predictions'] == 3
        assert 'mean_agreement' in diagnostics
        assert 'consensus_success_rate' in diagnostics


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_socratic_with_ensemble(self):
        """Test Socratic loop with ensemble predictions."""
        # This tests the full stack: Ensemble → ACE → Socratic
        ace_config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.5,
                min_confidence=0.3
            ),
            execution=ExecutionConfig(nvp_config=NVPConfig(latent_dim=32), input_shape=(32, 32))
        )
        ensemble_config = EnsembleConfig(num_models=3)
        socratic_config = SocraticConfig(max_iterations=2, verbose=False)

        # Create ensemble agent
        agent = EnsembleACEAgent(ace_config, ensemble_config)

        # Wrap with Socratic loop
        loop = SocraticLoop(socratic_config)

        energy_t = np.random.rand(32, 32)
        grad_x = np.random.rand(32, 32)
        grad_y = np.random.rand(32, 32)

        # Predict with correction
        result, history = loop.predict_with_correction(
            agent, energy_t, grad_x, grad_y
        )

        assert result is not None
        assert result.ensemble_predictions is not None
        assert len(result.ensemble_predictions) == 3

    def test_full_metacognitive_stack(self):
        """Test complete metacognitive architecture."""
        # Build the full stack from bottom up
        ace_config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.6,
                target_entropy_coherence=0.7,
                min_confidence=0.5
            ),
            calibration=CalibrationConfig(
                confidence_method="entropy",
                ensemble_size=3
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(
                    latent_dim=32,
                    encoder_features=[16, 32],
                    decoder_features=[32, 16]
                ),
                input_shape=(32, 32),
                enforce_energy_conservation=True
            )
        )

        ensemble_config = EnsembleConfig(
            num_models=3,
            consensus_method="median",
            max_disagreement=0.3
        )

        socratic_config = SocraticConfig(
            max_iterations=2,
            energy_drift_threshold=0.15,
            verbose=False
        )

        # Create integrated agent
        agent = EnsembleACEAgent(ace_config, ensemble_config)
        loop = SocraticLoop(socratic_config)

        # Test prediction
        energy_t = np.ones((32, 32)) * 0.5
        grad_x = np.random.rand(32, 32) * 0.1
        grad_y = np.random.rand(32, 32) * 0.1
        target = np.ones((32, 32)) * 0.6

        result, history = loop.predict_with_correction(
            agent, energy_t, grad_x, grad_y, target
        )

        # Verify all layers engaged
        assert result.energy_pred.shape == (32, 32)
        assert result.confidence > 0.0
        assert result.ensemble_predictions is not None
        assert len(history) >= 0  # May have iterations

        # Verify thermodynamic constraints
        assert np.all(result.energy_pred >= 0.0)  # Positive energy
        assert np.all(np.isfinite(result.energy_pred))  # No NaN/Inf
