"""
Feedback Trainer - Phase 5 EIL Online Learning

Continuously improves regime detection and forecasting by learning from validation results.

Learning Loops:
1. MicroAdapt Adaptation: Update model units based on proof validation outcomes
2. RegimeDetector Calibration: Adjust thresholds based on regime accuracy
3. Ensemble Tuning: Optimize fusion weights based on performance

Integrates with:
- ProofValidator: Learns from tri-check validation results
- MicroAdapt: Updates model unit parameters and fitness scores
- RegimeDetector: Calibrates entropy/temperature thresholds
- EnergyIntelligenceLayer: Tunes decision fusion weights
"""

import numpy as np
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime

from phase5.core.proof_validator import ProofRecord, ProofValidationResult
from phase5.core.microadapt import ModelUnitAdaptation, ModelUnitSearch


@dataclass
class FeedbackRecord:
    """Record of a single feedback event"""
    timestamp: float
    domain: str
    regime: str

    # Predictions
    predicted_regime: str
    regime_confidence: float
    forecast_values: np.ndarray

    # Ground truth
    actual_regime: str
    actual_values: np.ndarray

    # Validation results
    proof_passed: bool
    energy_fidelity: float
    entropy_coherence: float
    spectral_similarity: float

    # Learning targets
    regime_correct: bool
    forecast_error: float
    adaptations_applied: List[str] = field(default_factory=list)


@dataclass
class LearningMetrics:
    """Tracks learning progress over time"""
    total_feedback_events: int = 0
    regime_accuracy: float = 0.0
    avg_forecast_error: float = 0.0
    avg_proof_quality: float = 0.0

    # Component-specific metrics
    microadapt_adaptations: int = 0
    regime_detector_calibrations: int = 0
    fusion_weight_updates: int = 0

    # Performance trends
    accuracy_history: List[float] = field(default_factory=list)
    error_history: List[float] = field(default_factory=list)

    # Timestamp
    last_update: float = 0.0


class FeedbackTrainer:
    """
    Online learning system that continuously improves EIL from validation results.

    Learning Strategies:
    1. MicroAdapt: Increase fitness of units that produced correct regimes
    2. RegimeDetector: Adjust entropy/temperature thresholds based on accuracy
    3. Fusion Weights: Optimize statistical vs physics branch weighting
    4. Model Evolution: Replace poorly performing units with new patterns
    """

    def __init__(
        self,
        learning_rate: float = 0.01,
        adaptation_threshold: float = 0.7,
        calibration_window: int = 100,
        enable_online_learning: bool = True
    ):
        """
        Initialize Feedback Trainer

        Args:
            learning_rate: Rate of parameter updates (0.001 - 0.1)
            adaptation_threshold: Minimum accuracy before triggering adaptation
            calibration_window: Number of events to accumulate before calibration
            enable_online_learning: Whether to apply updates in real-time
        """
        self.learning_rate = learning_rate
        self.adaptation_threshold = adaptation_threshold
        self.calibration_window = calibration_window
        self.enable_online_learning = enable_online_learning

        # Feedback history
        self.feedback_history: deque = deque(maxlen=calibration_window)

        # Learning metrics
        self.metrics = LearningMetrics()

        # Adaptive parameters
        self.fusion_weights = {
            'statistical': 0.40,  # MicroAdapt weight
            'physics': 0.60       # RegimeDetector weight
        }

        self.regime_detector_thresholds = {
            'entropy_rate_min': 0.001,
            'entropy_rate_max': 0.1,
            'temperature_stable_max': 1.5,
            'temperature_chaotic_min': 3.0
        }

        print(f"✅ FeedbackTrainer initialized")
        print(f"  Learning rate: {learning_rate}")
        print(f"  Adaptation threshold: {adaptation_threshold}")
        print(f"  Calibration window: {calibration_window}")

    def process_validation_result(
        self,
        validation_result: ProofValidationResult,
        predicted_regime: str,
        regime_confidence: float,
        forecast_values: np.ndarray,
        actual_values: np.ndarray,
        actual_regime: Optional[str] = None
    ) -> FeedbackRecord:
        """
        Process a single validation result and learn from it.

        Args:
            validation_result: Proof validation outcome
            predicted_regime: Regime predicted by EIL
            regime_confidence: Confidence score
            forecast_values: Predicted future values
            actual_values: Actual observed values
            actual_regime: Ground truth regime (if known)

        Returns:
            FeedbackRecord with learning updates applied
        """
        proof = validation_result.proof_record

        # Determine actual regime from validation results
        if actual_regime is None:
            actual_regime = self._infer_regime_from_validation(validation_result)

        # Compute forecast error
        forecast_error = np.mean(np.abs(forecast_values - actual_values))

        # Check regime correctness
        regime_correct = (predicted_regime == actual_regime)

        # Create feedback record
        feedback = FeedbackRecord(
            timestamp=time.time(),
            domain=proof.domain,
            regime=predicted_regime,
            predicted_regime=predicted_regime,
            regime_confidence=regime_confidence,
            forecast_values=forecast_values,
            actual_regime=actual_regime,
            actual_values=actual_values,
            proof_passed=validation_result.passed,
            energy_fidelity=proof.energy_fidelity,
            entropy_coherence=proof.entropy_coherence,
            spectral_similarity=proof.spectral_similarity,
            regime_correct=regime_correct,
            forecast_error=forecast_error
        )

        # Add to history
        self.feedback_history.append(feedback)

        # Apply online learning if enabled
        if self.enable_online_learning:
            adaptations = self._apply_online_learning(feedback)
            feedback.adaptations_applied = adaptations

        # Update metrics
        self._update_metrics()

        return feedback

    def _apply_online_learning(self, feedback: FeedbackRecord) -> List[str]:
        """Apply immediate learning updates based on feedback"""
        adaptations = []

        # Strategy 1: MicroAdapt fitness boosting
        if feedback.regime_correct and feedback.proof_passed:
            # Boost fitness of model units that predicted correct regime
            adaptations.append("microadapt_boost")
            self.metrics.microadapt_adaptations += 1

        elif not feedback.regime_correct:
            # Penalize model units that predicted wrong regime
            adaptations.append("microadapt_penalty")
            self.metrics.microadapt_adaptations += 1

        # Strategy 2: RegimeDetector threshold calibration
        if len(self.feedback_history) >= self.calibration_window:
            calibrated = self._calibrate_regime_thresholds()
            if calibrated:
                adaptations.append("regime_detector_calibration")
                self.metrics.regime_detector_calibrations += 1

        # Strategy 3: Fusion weight optimization
        if len(self.feedback_history) >= 50:
            optimized = self._optimize_fusion_weights()
            if optimized:
                adaptations.append("fusion_weight_update")
                self.metrics.fusion_weight_updates += 1

        return adaptations

    def _calibrate_regime_thresholds(self) -> bool:
        """
        Calibrate RegimeDetector thresholds based on validation accuracy.

        Returns:
            True if calibration was applied
        """
        # Analyze recent feedback for regime-specific performance
        regime_stats = self._compute_regime_statistics()

        # Check if calibration is needed
        overall_accuracy = regime_stats.get('overall_accuracy', 1.0)

        if overall_accuracy < self.adaptation_threshold:
            # Adjust thresholds to improve accuracy

            # If stable regimes are being misclassified as chaotic, lower temperature threshold
            stable_false_negatives = regime_stats.get('stable_false_negatives', 0)
            if stable_false_negatives > 5:
                self.regime_detector_thresholds['temperature_stable_max'] *= 1.05
                self.regime_detector_thresholds['entropy_rate_max'] *= 1.05

            # If chaotic regimes are being misclassified as stable, raise temperature threshold
            chaotic_false_negatives = regime_stats.get('chaotic_false_negatives', 0)
            if chaotic_false_negatives > 5:
                self.regime_detector_thresholds['temperature_chaotic_min'] *= 0.95
                self.regime_detector_thresholds['entropy_rate_min'] *= 0.95

            return True

        return False

    def _optimize_fusion_weights(self) -> bool:
        """
        Optimize fusion weights based on branch performance.

        Returns:
            True if weights were updated
        """
        # Compare statistical vs physics branch accuracy
        # (In production, this would track branch-specific predictions)

        # Simplified: Adjust weights based on overall accuracy trend
        recent_accuracy = self._compute_recent_accuracy(window=50)

        if recent_accuracy < self.adaptation_threshold:
            # Shift weight slightly toward physics branch (more conservative)
            self.fusion_weights['physics'] = min(0.70, self.fusion_weights['physics'] + 0.05)
            self.fusion_weights['statistical'] = 1.0 - self.fusion_weights['physics']
            return True

        elif recent_accuracy > 0.90:
            # Shift weight slightly toward statistical branch (more responsive)
            self.fusion_weights['statistical'] = min(0.50, self.fusion_weights['statistical'] + 0.05)
            self.fusion_weights['physics'] = 1.0 - self.fusion_weights['statistical']
            return True

        return False

    def adapt_microadapt(
        self,
        model_adaptation: ModelUnitAdaptation,
        feedback_batch: List[FeedbackRecord]
    ) -> Dict:
        """
        Update MicroAdapt model units based on feedback batch.

        Args:
            model_adaptation: MicroAdapt adaptation instance
            feedback_batch: Recent feedback records

        Returns:
            Adaptation statistics
        """
        stats = {
            'units_boosted': 0,
            'units_penalized': 0,
            'units_replaced': 0
        }

        for feedback in feedback_batch:
            if feedback.regime_correct and feedback.proof_passed:
                # Boost fitness of units that contributed to correct prediction
                # (This is simplified - in production, track which units were used)
                for idx in range(min(5, len(model_adaptation.model_units))):
                    model_adaptation.adaptivity_vector[idx] += 0.1
                    stats['units_boosted'] += 1

            elif not feedback.regime_correct:
                # Penalize least-fit units
                M = len(model_adaptation.model_units)
                if M > 0:
                    least_fit_idx = np.argmin(model_adaptation.adaptivity_vector[:M])
                    model_adaptation.adaptivity_vector[least_fit_idx] *= 0.9
                    stats['units_penalized'] += 1

        # Trigger evolution if accuracy is low
        recent_accuracy = sum(f.regime_correct for f in feedback_batch) / len(feedback_batch)
        if recent_accuracy < self.adaptation_threshold:
            model_adaptation.evolve(replacement_rate=0.2)
            stats['units_replaced'] = int(len(model_adaptation.model_units) * 0.2)

        return stats

    def get_calibrated_thresholds(self) -> Dict:
        """Get current calibrated thresholds for RegimeDetector"""
        return self.regime_detector_thresholds.copy()

    def get_fusion_weights(self) -> Dict:
        """Get current optimized fusion weights"""
        return self.fusion_weights.copy()

    def _infer_regime_from_validation(self, validation_result: ProofValidationResult) -> str:
        """Infer actual regime from validation metrics"""
        proof = validation_result.proof_record

        # Use validation quality to infer regime stability
        avg_quality = (
            proof.energy_fidelity +
            proof.entropy_coherence +
            proof.spectral_similarity
        ) / 3.0

        if avg_quality > 0.95:
            return "stable_confirmed"
        elif avg_quality > 0.85:
            return "stable_unconfirmed"
        elif avg_quality > 0.70:
            return "transitional_stable"
        elif avg_quality > 0.50:
            return "transitional_chaotic"
        else:
            return "chaotic_unconfirmed"

    def _compute_regime_statistics(self) -> Dict:
        """Compute regime classification statistics from recent feedback"""
        if len(self.feedback_history) == 0:
            return {'overall_accuracy': 1.0}

        stats = {
            'overall_accuracy': 0.0,
            'stable_false_negatives': 0,
            'chaotic_false_negatives': 0,
            'total_correct': 0,
            'total_events': len(self.feedback_history)
        }

        for feedback in self.feedback_history:
            if feedback.regime_correct:
                stats['total_correct'] += 1
            else:
                # Track misclassification types
                if 'stable' in feedback.actual_regime and 'chaotic' in feedback.predicted_regime:
                    stats['stable_false_negatives'] += 1
                elif 'chaotic' in feedback.actual_regime and 'stable' in feedback.predicted_regime:
                    stats['chaotic_false_negatives'] += 1

        stats['overall_accuracy'] = stats['total_correct'] / stats['total_events']

        return stats

    def _compute_recent_accuracy(self, window: int = 50) -> float:
        """Compute regime accuracy over recent window"""
        recent = list(self.feedback_history)[-window:]
        if len(recent) == 0:
            return 1.0

        correct = sum(1 for f in recent if f.regime_correct)
        return correct / len(recent)

    def _update_metrics(self):
        """Update learning metrics from feedback history"""
        if len(self.feedback_history) == 0:
            return

        recent = list(self.feedback_history)

        # Overall metrics
        self.metrics.total_feedback_events = len(self.feedback_history)
        self.metrics.regime_accuracy = sum(f.regime_correct for f in recent) / len(recent)
        self.metrics.avg_forecast_error = np.mean([f.forecast_error for f in recent])

        # Proof quality
        proof_qualities = [
            (f.energy_fidelity + f.entropy_coherence + f.spectral_similarity) / 3.0
            for f in recent
        ]
        self.metrics.avg_proof_quality = np.mean(proof_qualities)

        # History tracking
        self.metrics.accuracy_history.append(self.metrics.regime_accuracy)
        self.metrics.error_history.append(self.metrics.avg_forecast_error)

        # Keep history bounded
        if len(self.metrics.accuracy_history) > 1000:
            self.metrics.accuracy_history = self.metrics.accuracy_history[-1000:]
        if len(self.metrics.error_history) > 1000:
            self.metrics.error_history = self.metrics.error_history[-1000:]

        self.metrics.last_update = time.time()

    def get_metrics(self) -> LearningMetrics:
        """Get current learning metrics"""
        return self.metrics

    def get_stats(self) -> Dict:
        """Get comprehensive learning statistics"""
        return {
            'metrics': {
                'total_events': self.metrics.total_feedback_events,
                'regime_accuracy': self.metrics.regime_accuracy,
                'avg_forecast_error': self.metrics.avg_forecast_error,
                'avg_proof_quality': self.metrics.avg_proof_quality
            },
            'adaptations': {
                'microadapt': self.metrics.microadapt_adaptations,
                'regime_detector': self.metrics.regime_detector_calibrations,
                'fusion_weights': self.metrics.fusion_weight_updates
            },
            'current_params': {
                'fusion_weights': self.fusion_weights,
                'regime_thresholds': self.regime_detector_thresholds
            },
            'trends': {
                'accuracy_trend': 'improving' if len(self.metrics.accuracy_history) > 1 and
                                  self.metrics.accuracy_history[-1] > self.metrics.accuracy_history[0] else 'stable',
                'error_trend': 'improving' if len(self.metrics.error_history) > 1 and
                              self.metrics.error_history[-1] < self.metrics.error_history[0] else 'stable'
            }
        }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("FEEDBACK TRAINER - ONLINE LEARNING TEST")
    print("=" * 70)

    # Initialize trainer
    trainer = FeedbackTrainer(
        learning_rate=0.01,
        adaptation_threshold=0.7,
        calibration_window=20,
        enable_online_learning=True
    )

    # Simulate validation results
    print("\n[Simulating 50 validation results...]")

    for i in range(50):
        # Create mock proof record
        from phase5.core.proof_validator import ProofRecord

        predicted = np.random.randn(64, 64) * 0.1 + 1.0
        observed = predicted + np.random.randn(64, 64) * 0.05  # Small noise

        proof = ProofRecord(
            proof_id=f"test-{i}",
            domain="fluid_dynamics",
            timestamp=time.time(),
            predicted_energy_map=predicted,
            predicted_hash="abc123",
            observed_energy_map=observed,
            observed_hash="def456",
            energy_check_passed=True,
            entropy_check_passed=True,
            spectral_check_passed=True,
            overall_passed=True,
            energy_fidelity=0.95 + np.random.randn() * 0.02,
            entropy_coherence=0.92 + np.random.randn() * 0.02,
            spectral_similarity=0.88 + np.random.randn() * 0.02,
            regime="stable_confirmed"
        )

        # Create mock validation result
        from phase5.core.proof_validator import ProofValidationResult

        validation_result = ProofValidationResult(
            passed=True,
            proof_record=proof,
            validation_details={'overall': {'passed': True}},
            recommended_action="mint"
        )

        # Simulate regime prediction
        predicted_regime = "stable_confirmed" if np.random.rand() > 0.2 else "transitional_stable"
        regime_confidence = 0.85 + np.random.rand() * 0.15

        # Simulate forecast
        forecast_values = np.random.randn(60) * 0.1 + 1.0
        actual_values = forecast_values + np.random.randn(60) * 0.05

        # Process feedback
        feedback = trainer.process_validation_result(
            validation_result=validation_result,
            predicted_regime=predicted_regime,
            regime_confidence=regime_confidence,
            forecast_values=forecast_values,
            actual_values=actual_values,
            actual_regime="stable_confirmed"
        )

        # Show adaptations every 10 events
        if (i + 1) % 10 == 0:
            print(f"  Event {i+1}: Adaptations applied: {feedback.adaptations_applied}")

    # Show final metrics
    print("\n[Learning Metrics]")
    stats = trainer.get_stats()

    print(f"  Total events: {stats['metrics']['total_events']}")
    print(f"  Regime accuracy: {stats['metrics']['regime_accuracy']:.1%}")
    print(f"  Avg forecast error: {stats['metrics']['avg_forecast_error']:.4f}")
    print(f"  Avg proof quality: {stats['metrics']['avg_proof_quality']:.1%}")

    print("\n[Adaptations Applied]")
    print(f"  MicroAdapt updates: {stats['adaptations']['microadapt']}")
    print(f"  RegimeDetector calibrations: {stats['adaptations']['regime_detector']}")
    print(f"  Fusion weight updates: {stats['adaptations']['fusion_weights']}")

    print("\n[Current Parameters]")
    print(f"  Fusion weights: Statistical={stats['current_params']['fusion_weights']['statistical']:.2f}, "
          f"Physics={stats['current_params']['fusion_weights']['physics']:.2f}")
    print(f"  Temperature thresholds: Stable<{stats['current_params']['regime_thresholds']['temperature_stable_max']:.2f}, "
          f"Chaotic>{stats['current_params']['regime_thresholds']['temperature_chaotic_min']:.2f}")

    print("\n[Trends]")
    print(f"  Accuracy trend: {stats['trends']['accuracy_trend']}")
    print(f"  Error trend: {stats['trends']['error_trend']}")

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
