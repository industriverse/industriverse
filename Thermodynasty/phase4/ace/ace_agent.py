#!/usr/bin/env python3
"""
ace_agent.py
ACE (Aspiration-Calibration-Execution) Cognitive Architecture - Phase 4 Core

Implements the three-layer cognitive architecture for Next Vector Prediction:
1. Aspiration:  Goal setting and target state selection
2. Calibration: Confidence estimation and uncertainty quantification
3. Execution:   NVP model inference with thermodynamic constraints

The ACE agent wraps the NVP model with metacognitive capabilities:
- Aspires to achieve specific prediction goals (target energy states)
- Calibrates its confidence before and after predictions
- Executes predictions through the NVP engine
- Self-corrects through Socratic error analysis
"""

from typing import Dict, Tuple, Optional, List, Any
from dataclasses import dataclass, field
import numpy as np
import jax
import jax.numpy as jnp
from jax import random
from pathlib import Path

from ..nvp.nvp_model import NVPModel, NVPConfig, create_train_state
from ..nvp.trainer import Trainer, TrainingConfig


@dataclass
class AspirationConfig:
    """Configuration for Aspiration Layer."""
    # Goal-setting parameters
    target_energy_fidelity: float = 0.95  # Target energy conservation
    target_entropy_coherence: float = 0.90  # Target entropy preservation
    target_rmse: float = 0.1  # Target prediction error

    # Planning horizon
    prediction_steps: int = 1  # How many steps ahead to predict
    max_retries: int = 3  # Maximum Socratic correction attempts

    # Confidence thresholds
    min_confidence: float = 0.7  # Minimum confidence to accept prediction
    high_confidence: float = 0.9  # Threshold for high confidence


@dataclass
class CalibrationConfig:
    """Configuration for Calibration Layer."""
    # Uncertainty estimation
    num_samples: int = 10  # Monte Carlo samples for uncertainty
    use_ensemble: bool = True  # Use shadow ensemble
    ensemble_size: int = 3  # Number of models in ensemble

    # Confidence metrics
    confidence_method: str = "entropy"  # "entropy" or "variance"
    calibration_temperature: float = 1.0  # Temperature scaling for confidence

    # BFT consensus (Byzantine Fault Tolerance)
    bft_threshold: float = 0.66  # 2/3 majority for consensus
    bft_max_disagreement: float = 0.2  # Maximum allowed prediction variance


@dataclass
class ExecutionConfig:
    """Configuration for Execution Layer."""
    # NVP model
    nvp_config: NVPConfig = field(default_factory=NVPConfig)
    input_shape: Tuple[int, int] = (256, 256)  # Default input shape (H, W)

    # Inference parameters
    deterministic: bool = False  # Use mean prediction or sample from distribution
    use_gradients: bool = True  # Use gradient information
    temperature: float = 1.0  # Sampling temperature

    # Thermodynamic constraints
    enforce_energy_conservation: bool = True
    enforce_entropy_monotonicity: bool = True
    conservation_tolerance: float = 0.05  # 5% energy drift allowed
    entropy_threshold: float = 0.0  # Minimum entropy increase


@dataclass
class ACEConfig:
    """Complete ACE Agent configuration."""
    aspiration: AspirationConfig = field(default_factory=AspirationConfig)
    calibration: CalibrationConfig = field(default_factory=CalibrationConfig)
    execution: ExecutionConfig = field(default_factory=ExecutionConfig)

    # Agent metadata
    agent_id: str = "ace_agent_001"
    domain: str = "general"
    seed: int = 42


@dataclass
class PredictionResult:
    """Result of ACE agent prediction."""
    # Predictions
    energy_pred: np.ndarray  # Predicted energy map (H, W)
    uncertainty: np.ndarray  # Prediction uncertainty (H, W)

    # Confidence metrics
    confidence: float  # Overall prediction confidence [0, 1]
    energy_fidelity: float  # Energy conservation fidelity
    entropy_coherence: float  # Entropy coherence with target

    # Metadata
    num_retries: int = 0  # Number of Socratic corrections
    execution_time: float = 0.0  # Inference time (seconds)
    aspiration_met: bool = False  # Whether goals were achieved

    # Diagnostic info
    calibration_metrics: Dict[str, float] = field(default_factory=dict)
    ensemble_predictions: Optional[List[np.ndarray]] = None


class AspirationLayer:
    """
    Aspiration Layer: Goal Setting and Target State Selection

    Defines what the agent WANTS to achieve:
    - Target energy conservation levels
    - Desired prediction accuracy
    - Confidence requirements
    """

    def __init__(self, config: AspirationConfig):
        self.config = config
        self.goals = {
            'energy_fidelity': config.target_energy_fidelity,
            'entropy_coherence': config.target_entropy_coherence,
            'rmse': config.target_rmse,
            'confidence': config.min_confidence
        }

    def set_goal(self, goal_name: str, value: float):
        """Update a specific goal."""
        if goal_name in self.goals:
            self.goals[goal_name] = value
        else:
            raise ValueError(f"Unknown goal: {goal_name}")

    def assess_achievement(self, result: PredictionResult) -> Dict[str, bool]:
        """
        Assess whether goals were achieved.

        Args:
            result: Prediction result with metrics

        Returns:
            Dictionary of goal achievements (True/False)
        """
        achievements = {
            'energy_fidelity': result.energy_fidelity >= self.goals['energy_fidelity'],
            'entropy_coherence': result.entropy_coherence >= self.goals['entropy_coherence'],
            'confidence': result.confidence >= self.goals['confidence']
        }

        # Overall achievement: all goals met
        achievements['overall'] = all(achievements.values())

        return achievements

    def adjust_goals(self, result: PredictionResult, factor: float = 0.9):
        """
        Adjust goals based on performance (for Socratic refinement).

        If goals are too ambitious, relax them slightly.

        Args:
            result: Previous prediction result
            factor: Relaxation factor (0.9 = 10% easier)
        """
        if not result.aspiration_met:
            # Relax goals slightly if not met
            self.goals['energy_fidelity'] *= factor
            self.goals['entropy_coherence'] *= factor
            self.goals['confidence'] *= factor

            # Ensure minimum thresholds
            self.goals['energy_fidelity'] = max(0.7, self.goals['energy_fidelity'])
            self.goals['entropy_coherence'] = max(0.7, self.goals['entropy_coherence'])
            self.goals['confidence'] = max(0.5, self.goals['confidence'])


class CalibrationLayer:
    """
    Calibration Layer: Confidence Estimation and Uncertainty Quantification

    Assesses how confident the agent SHOULD BE in its predictions:
    - Estimates prediction uncertainty
    - Computes confidence scores
    - Enables BFT consensus for ensemble
    """

    def __init__(self, config: CalibrationConfig, rng: jax.random.PRNGKey):
        self.config = config
        self.rng = rng

    def estimate_uncertainty(
        self,
        mean_pred: jnp.ndarray,
        log_var_pred: jnp.ndarray
    ) -> Tuple[np.ndarray, float]:
        """
        Estimate prediction uncertainty from model outputs.

        Args:
            mean_pred: Mean prediction (H, W, 1)
            log_var_pred: Log variance prediction (H, W, 1)

        Returns:
            uncertainty_map: Spatial uncertainty (H, W)
            confidence: Scalar confidence score [0, 1]
        """
        # Uncertainty = standard deviation
        std_pred = jnp.exp(0.5 * log_var_pred)
        uncertainty_map = np.array(std_pred[:, :, 0])

        # Confidence based on inverse uncertainty
        if self.config.confidence_method == "entropy":
            # Lower entropy (more peaked distribution) = higher confidence
            epsilon = 1e-10
            normalized_std = std_pred / (jnp.mean(std_pred) + epsilon)
            entropy = -jnp.sum(normalized_std * jnp.log(normalized_std + epsilon))
            # Normalize entropy to [0, 1] and invert
            max_entropy = jnp.log(float(normalized_std.size))
            confidence = float(1.0 - entropy / max_entropy)
        else:  # variance method
            # Lower variance = higher confidence
            mean_var = float(jnp.mean(jnp.exp(log_var_pred)))
            confidence = float(1.0 / (1.0 + mean_var))

        # Apply temperature scaling
        confidence = confidence ** (1.0 / self.config.calibration_temperature)
        confidence = np.clip(confidence, 0.0, 1.0)

        return uncertainty_map, confidence

    def ensemble_consensus(
        self,
        predictions: List[np.ndarray]
    ) -> Tuple[np.ndarray, float, bool]:
        """
        BFT (Byzantine Fault Tolerance) consensus from ensemble predictions.

        Args:
            predictions: List of predictions from shadow ensemble

        Returns:
            consensus_pred: Consensus prediction (median or mean)
            agreement: Agreement score [0, 1]
            consensus_valid: Whether consensus threshold met
        """
        if len(predictions) < self.config.ensemble_size:
            raise ValueError(f"Expected {self.config.ensemble_size} predictions, got {len(predictions)}")

        # Stack predictions
        pred_stack = np.stack(predictions, axis=0)  # (ensemble_size, H, W)

        # Compute consensus as median (robust to outliers)
        consensus_pred = np.median(pred_stack, axis=0)

        # Compute pairwise agreement
        disagreements = []
        for i in range(len(predictions)):
            for j in range(i + 1, len(predictions)):
                # Normalized L2 distance
                diff = predictions[i] - predictions[j]
                disagreement = np.sqrt(np.mean(diff ** 2)) / (np.mean(np.abs(predictions[i])) + 1e-10)
                disagreements.append(disagreement)

        # Average disagreement
        mean_disagreement = float(np.mean(disagreements))

        # Agreement score (inverse of disagreement)
        agreement = 1.0 - np.clip(mean_disagreement, 0.0, 1.0)

        # BFT consensus valid if disagreement below threshold
        consensus_valid = mean_disagreement < self.config.bft_max_disagreement

        return consensus_pred, agreement, consensus_valid


class ExecutionLayer:
    """
    Execution Layer: NVP Model Inference

    Performs the actual prediction using the trained NVP model:
    - Loads trained model state
    - Runs forward inference
    - Applies thermodynamic constraints
    """

    def __init__(
        self,
        config: ExecutionConfig,
        model_path: Optional[Path] = None,
        rng: Optional[jax.random.PRNGKey] = None
    ):
        self.config = config
        self.rng = rng if rng is not None else random.PRNGKey(42)

        # Initialize NVP model
        self.model = NVPModel(config.nvp_config)

        # Create train state (will load checkpoint if provided)
        self.state = create_train_state(
            self.rng,
            config.nvp_config,
            learning_rate=1e-4,  # Dummy value for inference
            input_shape=config.input_shape
        )

        # Load checkpoint if provided
        if model_path is not None:
            self.load_checkpoint(model_path)

    def load_checkpoint(self, checkpoint_path: Path):
        """Load trained model weights."""
        from flax.training import checkpoints
        self.state = checkpoints.restore_checkpoint(
            ckpt_dir=str(checkpoint_path.parent),
            target=self.state,
            prefix=checkpoint_path.stem
        )

    def predict(
        self,
        energy_t: np.ndarray,
        grad_x: np.ndarray,
        grad_y: np.ndarray
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Execute NVP prediction.

        Args:
            energy_t: Current energy state (H, W)
            grad_x: X gradient (H, W)
            grad_y: Y gradient (H, W)

        Returns:
            mean_pred: Predicted energy (H, W)
            log_var_pred: Log variance (H, W)
        """
        # Convert to JAX arrays with batch dimension
        energy_jax = jnp.array(energy_t[None, :, :, None])  # (1, H, W, 1)
        grad_x_jax = jnp.array(grad_x[None, :, :, None])
        grad_y_jax = jnp.array(grad_y[None, :, :, None])

        # Forward pass
        if hasattr(self.state, 'batch_stats') and self.state.batch_stats is not None:
            mean_pred, log_var_pred = self.state.apply_fn(
                {'params': self.state.params, 'batch_stats': self.state.batch_stats},
                energy_jax,
                grad_x_jax,
                grad_y_jax,
                training=False
            )
        else:
            mean_pred, log_var_pred = self.state.apply_fn(
                {'params': self.state.params},
                energy_jax,
                grad_x_jax,
                grad_y_jax,
                training=False
            )

        # Remove batch dimension and channel dimension
        mean_pred = np.array(mean_pred[0, :, :, 0])
        log_var_pred = np.array(log_var_pred[0, :, :, 0])

        # Apply thermodynamic constraints if enabled
        if self.config.enforce_energy_conservation:
            mean_pred = self._enforce_energy_conservation(mean_pred, energy_t)

        return mean_pred, log_var_pred

    def _enforce_energy_conservation(
        self,
        prediction: np.ndarray,
        reference: np.ndarray
    ) -> np.ndarray:
        """
        Enforce energy conservation by rescaling prediction.

        Args:
            prediction: Predicted energy map
            reference: Reference energy map (previous state)

        Returns:
            Corrected prediction with conserved energy
        """
        pred_total = np.sum(prediction)
        ref_total = np.sum(reference)

        if pred_total > 0:
            # Scale to match reference total energy
            correction_factor = ref_total / pred_total
            corrected = prediction * correction_factor
            return corrected
        else:
            return prediction


class ACEAgent:
    """
    Complete ACE (Aspiration-Calibration-Execution) Agent

    Integrates the three layers into a cohesive cognitive architecture.
    """

    def __init__(
        self,
        config: ACEConfig,
        model_path: Optional[Path] = None
    ):
        self.config = config
        self.rng = random.PRNGKey(config.seed)

        # Initialize layers
        self.aspiration = AspirationLayer(config.aspiration)

        self.rng, cal_rng = random.split(self.rng)
        self.calibration = CalibrationLayer(config.calibration, cal_rng)

        self.rng, exec_rng = random.split(self.rng)
        self.execution = ExecutionLayer(config.execution, model_path, exec_rng)

        # Prediction history
        self.history: List[PredictionResult] = []

    def predict(
        self,
        energy_t: np.ndarray,
        grad_x: np.ndarray,
        grad_y: np.ndarray,
        energy_target: Optional[np.ndarray] = None
    ) -> PredictionResult:
        """
        Make a prediction using the full ACE architecture.

        Args:
            energy_t: Current energy state (H, W)
            grad_x: X gradient (H, W)
            grad_y: Y gradient (H, W)
            energy_target: Optional target for metrics (H, W)

        Returns:
            PredictionResult with prediction and metadata
        """
        import time
        start_time = time.time()

        # EXECUTION: Run NVP model
        mean_pred, log_var_pred = self.execution.predict(energy_t, grad_x, grad_y)

        # CALIBRATION: Estimate uncertainty and confidence
        mean_jax = jnp.array(mean_pred[:, :, None])
        logvar_jax = jnp.array(log_var_pred[:, :, None])
        uncertainty, confidence = self.calibration.estimate_uncertainty(mean_jax, logvar_jax)

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
                'max_uncertainty': float(np.max(uncertainty))
            }
        )

        # ASPIRATION: Check if goals met
        achievements = self.aspiration.assess_achievement(result)
        result.aspiration_met = achievements['overall']

        # Store in history
        self.history.append(result)

        return result

    def _compute_energy_fidelity(
        self,
        pred: np.ndarray,
        target: np.ndarray
    ) -> float:
        """Compute energy conservation fidelity."""
        pred_total = np.sum(pred)
        target_total = np.sum(target)

        if target_total > 0:
            fidelity = 1.0 - abs(pred_total - target_total) / target_total
            return float(np.clip(fidelity, 0.0, 1.0))
        else:
            return 0.0

    def _compute_entropy_coherence(
        self,
        pred: np.ndarray,
        target: np.ndarray
    ) -> float:
        """Compute entropy coherence."""
        from ..nvp.nvp_model import compute_entropy

        # Add batch and channel dimensions for compute_entropy
        pred_jax = jnp.array(pred[None, :, :, None])
        target_jax = jnp.array(target[None, :, :, None])

        S_pred = compute_entropy(pred_jax)[0]
        S_target = compute_entropy(target_jax)[0]

        if S_target > 0:
            coherence = 1.0 - abs(S_pred - S_target) / S_target
            return float(np.clip(coherence, 0.0, 1.0))
        else:
            return 0.0
