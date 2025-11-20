#!/usr/bin/env python3
"""
test_integration_s4.py
Integration Tests for Session S4 Production Pipeline

Tests the complete production workflow:
- Training script components
- Inference script components
- Batch inference utilities
- End-to-end integration
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil

from phase4.ace import (
    ACEAgent,
    ACEConfig,
    AspirationConfig,
    CalibrationConfig,
    ExecutionConfig,
    SocraticACEAgent,
    SocraticConfig,
    EnsembleACEAgent,
    EnsembleConfig,
    BatchInferenceEngine,
    BatchInferenceConfig,
    batch_predict,
    compare_predictions
)
from phase4.nvp.nvp_model import NVPConfig


class TestBatchInferenceUtilities:
    """Tests for batch inference utilities."""

    @pytest.fixture
    def ace_agent(self):
        """Create test ACE agent."""
        config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.7,
                min_confidence=0.5
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        return ACEAgent(config)

    @pytest.fixture
    def test_sequences(self):
        """Create test energy sequences."""
        # 3 sequences of 5 timesteps each, 32x32
        sequences = [
            np.random.rand(5, 32, 32) for _ in range(3)
        ]
        return sequences

    def test_batch_inference_config(self):
        """Test batch inference configuration."""
        config = BatchInferenceConfig(
            batch_size=8,
            show_progress=False,
            verbose=False
        )

        assert config.batch_size == 8
        assert config.show_progress is False
        assert config.skip_on_error is True

    def test_batch_inference_engine_initialization(self, ace_agent):
        """Test batch inference engine initialization."""
        config = BatchInferenceConfig(show_progress=False)
        engine = BatchInferenceEngine(ace_agent, config)

        assert engine.agent is ace_agent
        assert engine.config == config
        assert isinstance(engine.stats, dict)

    def test_process_single_sequence(self, ace_agent, test_sequences):
        """Test processing a single sequence."""
        config = BatchInferenceConfig(show_progress=False, verbose=False)
        engine = BatchInferenceEngine(ace_agent, config)

        sequence = test_sequences[0]
        predictions, uncertainties, results = engine.process_sequence(
            sequence,
            use_socratic=False,
            target_available=True
        )

        # Should predict T-1 timesteps
        assert len(predictions) == len(sequence) - 1
        assert len(uncertainties) == len(sequence) - 1
        assert len(results) == len(sequence) - 1

        # Check shapes
        for pred, unc in zip(predictions, uncertainties):
            assert pred.shape == (32, 32)
            assert unc.shape == (32, 32)

    def test_process_batch(self, ace_agent, test_sequences):
        """Test batch processing."""
        config = BatchInferenceConfig(show_progress=False, verbose=False)
        engine = BatchInferenceEngine(ace_agent, config)

        result = engine.process_batch(
            test_sequences,
            use_socratic=False,
            save_targets=True
        )

        # Check result structure
        assert len(result.predictions) == len(test_sequences)
        assert len(result.uncertainties) == len(test_sequences)
        assert result.targets is not None
        assert len(result.targets) == len(test_sequences)

        # Check statistics
        assert result.total_predictions > 0
        assert result.successful_predictions >= 0
        assert 0.0 <= result.mean_confidence <= 1.0
        assert 0.0 <= result.mean_fidelity <= 1.0
        assert result.throughput > 0.0

    def test_batch_predict_convenience(self, ace_agent, test_sequences):
        """Test convenience batch_predict function."""
        config = BatchInferenceConfig(show_progress=False)

        result = batch_predict(
            ace_agent,
            test_sequences,
            config=config,
            use_socratic=False
        )

        assert result.total_predictions > 0
        assert len(result.predictions) == len(test_sequences)

    def test_compare_predictions(self):
        """Test prediction comparison metrics."""
        # Create synthetic predictions and targets
        predictions = np.random.rand(5, 32, 32)
        targets = predictions + np.random.randn(5, 32, 32) * 0.1  # Add noise

        metrics = compare_predictions(predictions, targets)

        # Check all metrics present
        assert 'rmse' in metrics
        assert 'mae' in metrics
        assert 'energy_error' in metrics
        assert 'correlation' in metrics
        assert 'psnr' in metrics

        # Check reasonable ranges
        assert metrics['rmse'] > 0.0
        assert metrics['mae'] > 0.0
        assert 0.0 <= metrics['correlation'] <= 1.0

    def test_batch_inference_with_error_handling(self, ace_agent):
        """Test error handling in batch inference."""
        config = BatchInferenceConfig(
            show_progress=False,
            skip_on_error=True
        )
        engine = BatchInferenceEngine(ace_agent, config)

        # Create sequences with invalid shape
        bad_sequences = [
            np.random.rand(3, 32, 32),  # Valid
            np.random.rand(2, 16, 16),  # Different size - will work but different
        ]

        # Should handle gracefully with skip_on_error=True
        result = engine.process_batch(bad_sequences, use_socratic=False)

        # Should complete without exception
        assert result.total_predictions >= 0

    def test_batch_result_save(self, ace_agent, test_sequences):
        """Test saving batch results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            config = BatchInferenceConfig(show_progress=False)
            engine = BatchInferenceEngine(ace_agent, config)

            result = engine.process_batch(test_sequences, use_socratic=False)

            # Save results
            engine.save_results(result, output_dir)

            # Check files created
            assert (output_dir / 'batch_stats.json').exists()
            assert len(list(output_dir.glob('predictions_*.npz'))) == len(test_sequences)


class TestSocraticBatchInference:
    """Tests for batch inference with Socratic correction."""

    @pytest.fixture
    def socratic_agent(self):
        """Create Socratic ACE agent."""
        ace_config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.6,
                min_confidence=0.4
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        socratic_config = SocraticConfig(
            max_iterations=2,
            verbose=False
        )

        return SocraticACEAgent(ace_config, socratic_config)

    def test_batch_inference_with_socratic(self, socratic_agent):
        """Test batch inference with Socratic correction."""
        sequences = [np.random.rand(4, 32, 32) for _ in range(2)]

        config = BatchInferenceConfig(show_progress=False)
        engine = BatchInferenceEngine(socratic_agent, config)

        result = engine.process_batch(
            sequences,
            use_socratic=True,  # Enable Socratic correction
            save_targets=True
        )

        # Should complete successfully
        assert result.total_predictions > 0
        assert len(result.predictions) == len(sequences)


class TestEnsembleBatchInference:
    """Tests for batch inference with ensemble."""

    @pytest.fixture
    def ensemble_agent(self):
        """Create Ensemble ACE agent."""
        ace_config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.6,
                min_confidence=0.4
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        ensemble_config = EnsembleConfig(
            num_models=3,
            consensus_method="median"
        )

        return EnsembleACEAgent(ace_config, ensemble_config)

    def test_batch_inference_with_ensemble(self, ensemble_agent):
        """Test batch inference with ensemble."""
        sequences = [np.random.rand(4, 32, 32) for _ in range(2)]

        config = BatchInferenceConfig(show_progress=False)
        engine = BatchInferenceEngine(ensemble_agent, config)

        result = engine.process_batch(sequences, use_socratic=False)

        # Should complete with ensemble predictions
        assert result.total_predictions > 0

        # Check that ensemble information is captured
        for res in result.results:
            if hasattr(res, 'ensemble_predictions'):
                assert res.ensemble_predictions is not None


class TestProductionWorkflow:
    """Integration tests for complete production workflow."""

    def test_end_to_end_single_agent(self):
        """Test end-to-end workflow with single ACE agent."""
        # 1. Create agent
        config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.7,
                min_confidence=0.5
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        agent = ACEAgent(config)

        # 2. Create test data
        sequences = [np.random.rand(5, 32, 32) for _ in range(3)]

        # 3. Run batch inference
        result = batch_predict(
            agent,
            sequences,
            config=BatchInferenceConfig(show_progress=False)
        )

        # 4. Verify results
        assert result.total_predictions > 0
        assert result.mean_confidence > 0.0
        assert result.mean_fidelity > 0.0

        # 5. Compare with targets
        for pred, target in zip(result.predictions, result.targets):
            metrics = compare_predictions(pred, target)
            assert metrics['rmse'] >= 0.0
            # Correlation can be negative for untrained models
            assert -1.0 <= metrics['correlation'] <= 1.0

    def test_end_to_end_socratic(self):
        """Test end-to-end workflow with Socratic agent."""
        ace_config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.6,
                min_confidence=0.4
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        socratic_config = SocraticConfig(max_iterations=2, verbose=False)
        agent = SocraticACEAgent(ace_config, socratic_config)

        sequences = [np.random.rand(4, 32, 32) for _ in range(2)]

        result = batch_predict(
            agent,
            sequences,
            config=BatchInferenceConfig(show_progress=False),
            use_socratic=True
        )

        assert result.total_predictions > 0

    def test_end_to_end_ensemble(self):
        """Test end-to-end workflow with ensemble agent."""
        ace_config = ACEConfig(
            aspiration=AspirationConfig(
                target_energy_fidelity=0.6,
                min_confidence=0.4
            ),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        ensemble_config = EnsembleConfig(num_models=3)
        agent = EnsembleACEAgent(ace_config, ensemble_config)

        sequences = [np.random.rand(4, 32, 32) for _ in range(2)]

        result = batch_predict(
            agent,
            sequences,
            config=BatchInferenceConfig(show_progress=False)
        )

        assert result.total_predictions > 0

    def test_performance_tracking(self):
        """Test performance tracking across batch inference."""
        config = ACEConfig(
            aspiration=AspirationConfig(min_confidence=0.5),
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        agent = ACEAgent(config)

        sequences = [np.random.rand(10, 32, 32)]  # Longer sequence

        result = batch_predict(
            agent,
            sequences,
            config=BatchInferenceConfig(show_progress=False)
        )

        # Check performance metrics
        assert result.throughput > 0.0
        assert result.mean_latency > 0.0
        assert result.total_time > 0.0

        # Sanity check: throughput = predictions / time
        expected_throughput = result.total_predictions / result.total_time
        assert abs(result.throughput - expected_throughput) < 0.01


class TestRobustness:
    """Tests for robustness and edge cases."""

    def test_empty_sequence_handling(self):
        """Test handling of empty sequence list."""
        config = ACEConfig(
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        agent = ACEAgent(config)

        result = batch_predict(
            agent,
            [],  # Empty list
            config=BatchInferenceConfig(show_progress=False)
        )

        assert result.total_predictions == 0
        assert len(result.predictions) == 0

    def test_single_timestep_sequence(self):
        """Test sequence with only 2 timesteps (1 prediction)."""
        config = ACEConfig(
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        agent = ACEAgent(config)

        # Sequence with only 2 timesteps
        sequences = [np.random.rand(2, 32, 32)]

        result = batch_predict(
            agent,
            sequences,
            config=BatchInferenceConfig(show_progress=False)
        )

        # Should predict exactly 1 timestep
        assert result.total_predictions == 1
        assert result.predictions[0].shape == (1, 32, 32)

    def test_variable_sequence_lengths(self):
        """Test sequences with different lengths."""
        config = ACEConfig(
            execution=ExecutionConfig(
                nvp_config=NVPConfig(latent_dim=32),
                input_shape=(32, 32)
            )
        )
        agent = ACEAgent(config)

        # Different length sequences
        sequences = [
            np.random.rand(3, 32, 32),
            np.random.rand(5, 32, 32),
            np.random.rand(4, 32, 32)
        ]

        result = batch_predict(
            agent,
            sequences,
            config=BatchInferenceConfig(show_progress=False)
        )

        # Should handle all sequences
        assert len(result.predictions) == 3
        assert result.predictions[0].shape[0] == 2  # 3-1
        assert result.predictions[1].shape[0] == 4  # 5-1
        assert result.predictions[2].shape[0] == 3  # 4-1
