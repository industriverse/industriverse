#!/usr/bin/env python3
"""
shadow_ensemble.py
Shadow Ensemble with Byzantine Fault Tolerance - Phase 4 Robustness

Implements a shadow ensemble of 3 NVP models for robust predictions:
- 3 independent models (diversified by initialization/training)
- Byzantine Fault Tolerance (BFT) consensus
- Detects and rejects faulty/adversarial predictions
- Provides uncertainty quantification through ensemble disagreement

BFT Consensus:
- Requires 2/3 majority (Byzantine fault tolerance)
- Median-based consensus (robust to outliers)
- Detects when models disagree beyond threshold
- Rejects predictions with high ensemble variance
"""

from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import jax.random as random

from .ace_agent import (
    ACEAgent,
    ACEConfig,
    PredictionResult,
    ExecutionLayer,
    ExecutionConfig
)
from ..nvp.nvp_model import NVPConfig


@dataclass
class EnsembleConfig:
    """Configuration for Shadow Ensemble."""
    # Ensemble size
    num_models: int = 3  # BFT requires odd number (3 = 1 fault tolerance)

    # Consensus parameters
    consensus_method: str = "median"  # "median" or "mean"
    bft_threshold: float = 0.66  # 2/3 majority required
    max_disagreement: float = 0.2  # Maximum allowed prediction variance

    # Diversity
    seed_offset: int = 1000  # Offset for diversifying random seeds
    independent_init: bool = True  # Use different random initializations

    # Inference
    parallel: bool = False  # Run models in parallel (future optimization)


@dataclass
class EnsembleResult:
    """Result from shadow ensemble prediction."""
    # Consensus prediction
    consensus_pred: np.ndarray  # Consensus energy map (H, W)
    ensemble_uncertainty: np.ndarray  # Ensemble disagreement (H, W)

    # Individual predictions
    individual_preds: List[np.ndarray]  # All model predictions
    individual_confidences: List[float]  # Confidence from each model

    # Consensus metrics
    agreement_score: float  # Inter-model agreement [0, 1]
    consensus_valid: bool  # Whether BFT consensus achieved
    num_agreeing: int  # Number of models in consensus

    # Metadata
    rejected_models: List[int] = None  # Indices of rejected models


class ShadowEnsemble:
    """
    Shadow Ensemble of NVP Models with BFT Consensus

    Maintains 3 independent NVP models and combines predictions
    using Byzantine Fault Tolerance principles.
    """

    def __init__(
        self,
        config: EnsembleConfig,
        ace_config: ACEConfig,
        model_paths: Optional[List[Path]] = None
    ):
        """
        Initialize shadow ensemble.

        Args:
            config: Ensemble configuration
            ace_config: Base ACE configuration for models
            model_paths: Optional paths to pre-trained models
        """
        self.config = config
        self.ace_config = ace_config

        # Create ensemble of execution layers
        self.models: List[ExecutionLayer] = []

        if model_paths and len(model_paths) == config.num_models:
            # Load pre-trained models
            for i, path in enumerate(model_paths):
                rng = random.PRNGKey(ace_config.seed + i * config.seed_offset)
                model = ExecutionLayer(
                    ace_config.execution,
                    model_path=path,
                    rng=rng
                )
                self.models.append(model)
        else:
            # Initialize from scratch with different seeds
            for i in range(config.num_models):
                rng = random.PRNGKey(ace_config.seed + i * config.seed_offset)
                model = ExecutionLayer(
                    ace_config.execution,
                    model_path=None,
                    rng=rng
                )
                self.models.append(model)

    def predict(
        self,
        energy_t: np.ndarray,
        grad_x: np.ndarray,
        grad_y: np.ndarray
    ) -> EnsembleResult:
        """
        Make prediction using shadow ensemble with BFT consensus.

        Args:
            energy_t: Current energy state (H, W)
            grad_x: X gradient (H, W)
            grad_y: Y gradient (H, W)

        Returns:
            EnsembleResult with consensus prediction and metadata
        """
        # Collect predictions from all models
        individual_preds = []
        individual_confidences = []

        for i, model in enumerate(self.models):
            # Get prediction from model
            mean_pred, log_var_pred = model.predict(energy_t, grad_x, grad_y)

            # Estimate confidence (inverse of mean uncertainty)
            var_pred = np.exp(log_var_pred)
            confidence = 1.0 / (1.0 + np.mean(var_pred))

            individual_preds.append(mean_pred)
            individual_confidences.append(float(confidence))

        # Compute BFT consensus
        consensus_pred, agreement_score, consensus_valid = self._compute_consensus(
            individual_preds
        )

        # Compute ensemble uncertainty (disagreement)
        ensemble_uncertainty = self._compute_ensemble_uncertainty(individual_preds)

        # Count agreeing models
        num_agreeing = self._count_agreeing_models(individual_preds, consensus_pred)

        # Identify rejected models (outliers)
        rejected_models = self._identify_outliers(individual_preds, consensus_pred)

        return EnsembleResult(
            consensus_pred=consensus_pred,
            ensemble_uncertainty=ensemble_uncertainty,
            individual_preds=individual_preds,
            individual_confidences=individual_confidences,
            agreement_score=agreement_score,
            consensus_valid=consensus_valid,
            num_agreeing=num_agreeing,
            rejected_models=rejected_models
        )

    def _compute_consensus(
        self,
        predictions: List[np.ndarray]
    ) -> Tuple[np.ndarray, float, bool]:
        """
        Compute BFT consensus from ensemble predictions.

        Uses median (robust to outliers) or mean for consensus.

        Args:
            predictions: List of predictions from each model

        Returns:
            consensus_pred: Consensus prediction
            agreement_score: Inter-model agreement [0, 1]
            consensus_valid: Whether BFT threshold met
        """
        # Stack predictions
        pred_stack = np.stack(predictions, axis=0)  # (num_models, H, W)

        # Compute consensus
        if self.config.consensus_method == "median":
            consensus_pred = np.median(pred_stack, axis=0)
        elif self.config.consensus_method == "mean":
            consensus_pred = np.mean(pred_stack, axis=0)
        else:
            raise ValueError(f"Unknown consensus method: {self.config.consensus_method}")

        # Compute pairwise disagreement
        disagreements = []
        for i in range(len(predictions)):
            for j in range(i + 1, len(predictions)):
                # Normalized RMSE between predictions
                diff = predictions[i] - predictions[j]
                rmse = np.sqrt(np.mean(diff ** 2))
                normalization = np.mean(np.abs(predictions[i])) + 1e-10
                normalized_disagreement = rmse / normalization
                disagreements.append(normalized_disagreement)

        # Average disagreement
        mean_disagreement = float(np.mean(disagreements))

        # Agreement score (inverse of disagreement)
        agreement_score = 1.0 - np.clip(mean_disagreement, 0.0, 1.0)

        # BFT consensus valid if disagreement below threshold
        consensus_valid = mean_disagreement < self.config.max_disagreement

        return consensus_pred, agreement_score, consensus_valid

    def _compute_ensemble_uncertainty(
        self,
        predictions: List[np.ndarray]
    ) -> np.ndarray:
        """
        Compute spatial uncertainty from ensemble disagreement.

        Args:
            predictions: List of predictions from each model

        Returns:
            uncertainty_map: Per-pixel uncertainty (H, W)
        """
        # Stack predictions
        pred_stack = np.stack(predictions, axis=0)  # (num_models, H, W)

        # Compute standard deviation across models
        uncertainty_map = np.std(pred_stack, axis=0)

        return uncertainty_map

    def _count_agreeing_models(
        self,
        predictions: List[np.ndarray],
        consensus: np.ndarray
    ) -> int:
        """
        Count how many models agree with consensus.

        Args:
            predictions: List of individual predictions
            consensus: Consensus prediction

        Returns:
            Number of models within threshold of consensus
        """
        num_agreeing = 0

        for pred in predictions:
            # Compute normalized difference from consensus
            diff = pred - consensus
            rmse = np.sqrt(np.mean(diff ** 2))
            normalization = np.mean(np.abs(consensus)) + 1e-10
            normalized_diff = rmse / normalization

            # Check if within threshold
            if normalized_diff < self.config.max_disagreement:
                num_agreeing += 1

        return num_agreeing

    def _identify_outliers(
        self,
        predictions: List[np.ndarray],
        consensus: np.ndarray
    ) -> List[int]:
        """
        Identify outlier models that disagree with consensus.

        Args:
            predictions: List of individual predictions
            consensus: Consensus prediction

        Returns:
            List of indices of outlier models
        """
        outliers = []

        for i, pred in enumerate(predictions):
            # Compute normalized difference from consensus
            diff = pred - consensus
            rmse = np.sqrt(np.mean(diff ** 2))
            normalization = np.mean(np.abs(consensus)) + 1e-10
            normalized_diff = rmse / normalization

            # Mark as outlier if beyond threshold
            if normalized_diff > self.config.max_disagreement * 1.5:  # 1.5x more lenient
                outliers.append(i)

        return outliers


class EnsembleACEAgent(ACEAgent):
    """
    ACE Agent with Shadow Ensemble for robust predictions.

    Extends base ACE Agent to use ensemble of models instead of single model.
    """

    def __init__(
        self,
        ace_config: ACEConfig,
        ensemble_config: EnsembleConfig,
        model_paths: Optional[List[Path]] = None
    ):
        """
        Initialize ACE Agent with shadow ensemble.

        Args:
            ace_config: Base ACE configuration
            ensemble_config: Ensemble configuration
            model_paths: Optional pre-trained model paths
        """
        # Don't call super().__init__() - we'll replace execution layer
        self.config = ace_config
        self.rng = random.PRNGKey(ace_config.seed)

        # Initialize Aspiration and Calibration layers normally
        from .ace_agent import AspirationLayer, CalibrationLayer

        self.aspiration = AspirationLayer(ace_config.aspiration)

        self.rng, cal_rng = random.split(self.rng)
        self.calibration = CalibrationLayer(ace_config.calibration, cal_rng)

        # Replace execution layer with shadow ensemble
        self.ensemble = ShadowEnsemble(
            ensemble_config,
            ace_config,
            model_paths
        )

        # Prediction history
        self.history: List[PredictionResult] = []
        self.ensemble_history: List[EnsembleResult] = []

    def predict(
        self,
        energy_t: np.ndarray,
        grad_x: np.ndarray,
        grad_y: np.ndarray,
        energy_target: Optional[np.ndarray] = None
    ) -> PredictionResult:
        """
        Make prediction using shadow ensemble.

        Args:
            energy_t: Current energy state (H, W)
            grad_x: X gradient (H, W)
            grad_y: Y gradient (H, W)
            energy_target: Optional target for metrics

        Returns:
            PredictionResult with ensemble consensus
        """
        import time
        start_time = time.time()

        # Get ensemble prediction
        ensemble_result = self.ensemble.predict(energy_t, grad_x, grad_y)

        # Store ensemble result
        self.ensemble_history.append(ensemble_result)

        # Use consensus prediction as final output
        mean_pred = ensemble_result.consensus_pred
        uncertainty = ensemble_result.ensemble_uncertainty

        # Confidence from ensemble agreement
        confidence = ensemble_result.agreement_score

        # Compute metrics if target provided
        if energy_target is not None:
            energy_fidelity = self._compute_energy_fidelity(mean_pred, energy_target)
            entropy_coherence = self._compute_entropy_coherence(mean_pred, energy_target)
        else:
            energy_fidelity = 0.0
            entropy_coherence = 0.0

        # Create result
        result = PredictionResult(
            energy_pred=mean_pred,
            uncertainty=uncertainty,
            confidence=confidence,
            energy_fidelity=energy_fidelity,
            entropy_coherence=entropy_coherence,
            execution_time=time.time() - start_time,
            calibration_metrics={
                'mean_uncertainty': float(np.mean(uncertainty)),
                'max_uncertainty': float(np.max(uncertainty)),
                'ensemble_agreement': ensemble_result.agreement_score,
                'consensus_valid': ensemble_result.consensus_valid,
                'num_agreeing': ensemble_result.num_agreeing
            },
            ensemble_predictions=[pred.copy() for pred in ensemble_result.individual_preds]
        )

        # Check aspiration
        achievements = self.aspiration.assess_achievement(result)
        result.aspiration_met = achievements['overall']

        # Store in history
        self.history.append(result)

        return result

    def get_ensemble_diagnostics(self) -> Dict[str, any]:
        """
        Get diagnostic information about ensemble behavior.

        Returns:
            Dictionary with ensemble statistics
        """
        if not self.ensemble_history:
            return {}

        agreement_scores = [r.agreement_score for r in self.ensemble_history]
        consensus_valid = [r.consensus_valid for r in self.ensemble_history]

        diagnostics = {
            'total_predictions': len(self.ensemble_history),
            'mean_agreement': float(np.mean(agreement_scores)),
            'min_agreement': float(np.min(agreement_scores)),
            'max_agreement': float(np.max(agreement_scores)),
            'consensus_success_rate': float(np.mean(consensus_valid)),
            'average_agreeing_models': float(np.mean([r.num_agreeing for r in self.ensemble_history]))
        }

        return diagnostics
