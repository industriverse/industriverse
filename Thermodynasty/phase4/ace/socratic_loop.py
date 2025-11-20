#!/usr/bin/env python3
"""
socratic_loop.py
Socratic Self-Correction Loop - Phase 4 Metacognition

Implements the Socratic method for self-correction:
1. Make prediction
2. Analyze errors
3. Identify failure modes
4. Refine goals/strategy
5. Retry with adjusted approach

The Socratic Loop enables the ACE agent to learn from mistakes and
improve predictions through iterative refinement.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import numpy as np

from .ace_agent import ACEAgent, PredictionResult, ACEConfig


class FailureMode(Enum):
    """Types of prediction failures the agent can identify."""
    ENERGY_DRIFT = "energy_drift"  # Total energy not conserved
    HIGH_UNCERTAINTY = "high_uncertainty"  # Low confidence prediction
    ENTROPY_VIOLATION = "entropy_violation"  # Entropy decreased (unphysical)
    POOR_SPATIAL_FIT = "poor_spatial_fit"  # High RMSE, wrong features
    LOW_CONFIDENCE = "low_confidence"  # Below confidence threshold
    CONSENSUS_FAILURE = "consensus_failure"  # Ensemble disagreement


@dataclass
class ErrorAnalysis:
    """Results of Socratic error analysis."""
    failure_modes: List[FailureMode]
    severity: Dict[FailureMode, float]  # 0-1 scale
    root_causes: Dict[FailureMode, str]  # Human-readable explanations
    suggested_fixes: Dict[FailureMode, str]  # Recommended actions


@dataclass
class SocraticConfig:
    """Configuration for Socratic Loop."""
    # Analysis thresholds
    energy_drift_threshold: float = 0.1  # 10% energy drift triggers analysis
    uncertainty_threshold: float = 0.3  # High uncertainty threshold
    confidence_threshold: float = 0.7  # Minimum acceptable confidence

    # Refinement strategy
    max_iterations: int = 3  # Maximum Socratic retries
    goal_relaxation_factor: float = 0.9  # How much to relax goals (90% of original)
    learning_rate: float = 0.1  # How aggressively to adjust

    # Diagnostic verbosity
    verbose: bool = False


class SocraticLoop:
    """
    Socratic Self-Correction Loop

    Implements iterative refinement through error analysis:
    - Identifies what went wrong
    - Suggests corrections
    - Adjusts goals/strategy
    - Retries prediction
    """

    def __init__(self, config: SocraticConfig):
        self.config = config
        self.iteration_history: List[ErrorAnalysis] = []

    def analyze_failure(
        self,
        result: PredictionResult,
        target: Optional[np.ndarray] = None
    ) -> ErrorAnalysis:
        """
        Perform Socratic analysis of prediction failure.

        Args:
            result: Prediction result to analyze
            target: Ground truth (if available)

        Returns:
            ErrorAnalysis with identified issues and fixes
        """
        failure_modes = []
        severity = {}
        root_causes = {}
        suggested_fixes = {}

        # 1. Check energy conservation
        if result.energy_fidelity < (1.0 - self.config.energy_drift_threshold):
            failure_modes.append(FailureMode.ENERGY_DRIFT)
            drift = 1.0 - result.energy_fidelity
            severity[FailureMode.ENERGY_DRIFT] = min(1.0, drift / self.config.energy_drift_threshold)
            root_causes[FailureMode.ENERGY_DRIFT] = (
                f"Energy conservation violated: {drift:.1%} drift. "
                f"Predicted total energy differs from input."
            )
            suggested_fixes[FailureMode.ENERGY_DRIFT] = (
                "Apply energy rescaling post-hoc or increase λ_conservation weight."
            )

        # 2. Check prediction uncertainty
        mean_uncertainty = result.calibration_metrics.get('mean_uncertainty', 0.0)
        if mean_uncertainty > self.config.uncertainty_threshold:
            failure_modes.append(FailureMode.HIGH_UNCERTAINTY)
            severity[FailureMode.HIGH_UNCERTAINTY] = min(1.0, mean_uncertainty / self.config.uncertainty_threshold)
            root_causes[FailureMode.HIGH_UNCERTAINTY] = (
                f"High prediction uncertainty: {mean_uncertainty:.3f}. "
                f"Model unsure about prediction."
            )
            suggested_fixes[FailureMode.HIGH_UNCERTAINTY] = (
                "Increase training data, reduce model capacity, or use ensemble."
            )

        # 3. Check confidence
        if result.confidence < self.config.confidence_threshold:
            failure_modes.append(FailureMode.LOW_CONFIDENCE)
            confidence_gap = self.config.confidence_threshold - result.confidence
            severity[FailureMode.LOW_CONFIDENCE] = min(1.0, confidence_gap / self.config.confidence_threshold)
            root_causes[FailureMode.LOW_CONFIDENCE] = (
                f"Low confidence: {result.confidence:.3f} < {self.config.confidence_threshold:.3f}. "
                f"Model not confident in prediction."
            )
            suggested_fixes[FailureMode.LOW_CONFIDENCE] = (
                "Relax acceptance threshold or gather more training data."
            )

        # 4. Check entropy coherence (if computed)
        if result.entropy_coherence > 0:  # Only if target provided
            if result.entropy_coherence < 0.8:  # Threshold for entropy issues
                failure_modes.append(FailureMode.ENTROPY_VIOLATION)
                severity[FailureMode.ENTROPY_VIOLATION] = 1.0 - result.entropy_coherence
                root_causes[FailureMode.ENTROPY_VIOLATION] = (
                    f"Entropy coherence low: {result.entropy_coherence:.3f}. "
                    f"Thermodynamic structure not preserved."
                )
                suggested_fixes[FailureMode.ENTROPY_VIOLATION] = (
                    "Increase λ_entropy weight or check for unphysical predictions."
                )

        # 5. Check spatial fit (if target provided)
        if target is not None:
            rmse = float(np.sqrt(np.mean((result.energy_pred - target) ** 2)))
            if rmse > 0.3:  # Threshold for poor spatial fit
                failure_modes.append(FailureMode.POOR_SPATIAL_FIT)
                severity[FailureMode.POOR_SPATIAL_FIT] = min(1.0, rmse / 0.5)
                root_causes[FailureMode.POOR_SPATIAL_FIT] = (
                    f"High RMSE: {rmse:.3f}. Spatial features not captured."
                )
                suggested_fixes[FailureMode.POOR_SPATIAL_FIT] = (
                    "Increase model capacity or train longer."
                )

        analysis = ErrorAnalysis(
            failure_modes=failure_modes,
            severity=severity,
            root_causes=root_causes,
            suggested_fixes=suggested_fixes
        )

        self.iteration_history.append(analysis)
        return analysis

    def refine_strategy(
        self,
        agent: ACEAgent,
        analysis: ErrorAnalysis,
        iteration: int
    ):
        """
        Refine agent strategy based on error analysis.

        Adjusts goals, constraints, or inference parameters to
        improve next prediction attempt.

        Args:
            agent: ACE agent to refine
            analysis: Error analysis from previous attempt
            iteration: Current iteration number
        """
        if self.config.verbose:
            print(f"\n[Socratic Loop Iteration {iteration}]")
            print(f"Identified {len(analysis.failure_modes)} failure modes:")
            for mode in analysis.failure_modes:
                print(f"  - {mode.value}: {analysis.root_causes[mode]}")
                print(f"    Severity: {analysis.severity[mode]:.2f}")
                print(f"    Fix: {analysis.suggested_fixes[mode]}")

        # Apply refinements based on dominant failure modes
        for mode in analysis.failure_modes:
            severity = analysis.severity[mode]

            if mode == FailureMode.ENERGY_DRIFT:
                # Strengthen energy conservation constraint
                if severity > 0.5:
                    if self.config.verbose:
                        print(f"  → Enforcing strict energy conservation")
                    # Handle both ACEAgent and EnsembleACEAgent
                    if hasattr(agent, 'execution'):
                        agent.execution.config.enforce_energy_conservation = True
                    elif hasattr(agent, 'ensemble'):
                        # For EnsembleACEAgent, update all models in ensemble
                        for model in agent.ensemble.models:
                            model.config.enforce_energy_conservation = True

            elif mode == FailureMode.HIGH_UNCERTAINTY:
                # Relax confidence requirements (accept less certain predictions)
                if severity > 0.7:
                    new_threshold = agent.aspiration.config.min_confidence * 0.8
                    agent.aspiration.config.min_confidence = max(0.5, new_threshold)
                    if self.config.verbose:
                        print(f"  → Relaxed confidence threshold to {agent.aspiration.config.min_confidence:.2f}")

            elif mode == FailureMode.LOW_CONFIDENCE:
                # Relax acceptance criteria
                factor = 1.0 - (severity * self.config.learning_rate)
                agent.aspiration.goals['confidence'] *= factor
                if self.config.verbose:
                    print(f"  → Adjusted confidence goal to {agent.aspiration.goals['confidence']:.2f}")

            elif mode == FailureMode.ENTROPY_VIOLATION:
                # Relax entropy coherence requirement
                if severity > 0.5:
                    factor = 1.0 - (severity * self.config.learning_rate)
                    agent.aspiration.goals['entropy_coherence'] *= factor
                    if self.config.verbose:
                        print(f"  → Relaxed entropy goal to {agent.aspiration.goals['entropy_coherence']:.2f}")

            elif mode == FailureMode.POOR_SPATIAL_FIT:
                # Relax fidelity requirements
                if severity > 0.6:
                    factor = 1.0 - (severity * self.config.learning_rate * 0.5)
                    agent.aspiration.goals['energy_fidelity'] *= factor
                    if self.config.verbose:
                        print(f"  → Adjusted fidelity goal to {agent.aspiration.goals['energy_fidelity']:.2f}")

    def predict_with_correction(
        self,
        agent: ACEAgent,
        energy_t: np.ndarray,
        grad_x: np.ndarray,
        grad_y: np.ndarray,
        energy_target: Optional[np.ndarray] = None
    ) -> Tuple[PredictionResult, List[ErrorAnalysis]]:
        """
        Make prediction with Socratic self-correction.

        Iteratively attempts prediction, analyzes failures, refines strategy,
        and retries until success or max iterations reached.

        Args:
            agent: ACE agent
            energy_t: Current energy state
            grad_x: X gradient
            grad_y: Y gradient
            energy_target: Optional target for metrics

        Returns:
            best_result: Best prediction achieved
            analysis_history: List of error analyses from each attempt
        """
        analysis_history = []
        best_result = None
        best_score = -1.0

        for iteration in range(self.config.max_iterations):
            if self.config.verbose:
                print(f"\n{'='*60}")
                print(f"Socratic Iteration {iteration + 1}/{self.config.max_iterations}")
                print(f"{'='*60}")

            # Make prediction
            result = agent.predict(energy_t, grad_x, grad_y, energy_target)
            result.num_retries = iteration

            # Track best result (by composite score)
            score = self._compute_composite_score(result)
            if score > best_score:
                best_score = score
                best_result = result

            if self.config.verbose:
                print(f"\nPrediction Results:")
                print(f"  Confidence: {result.confidence:.3f}")
                print(f"  Energy Fidelity: {result.energy_fidelity:.3f}")
                print(f"  Entropy Coherence: {result.entropy_coherence:.3f}")
                print(f"  Aspiration Met: {result.aspiration_met}")

            # Check if goals achieved
            if result.aspiration_met:
                if self.config.verbose:
                    print(f"\n✓ Goals achieved on iteration {iteration + 1}")
                return result, analysis_history

            # Analyze failure
            analysis = self.analyze_failure(result, energy_target)
            analysis_history.append(analysis)

            # Refine strategy for next iteration
            if iteration < self.config.max_iterations - 1:
                self.refine_strategy(agent, analysis, iteration + 1)

        if self.config.verbose:
            print(f"\n⚠ Max iterations reached. Returning best result (score: {best_score:.3f})")

        return best_result, analysis_history

    def _compute_composite_score(self, result: PredictionResult) -> float:
        """
        Compute composite score for ranking predictions.

        Args:
            result: Prediction result

        Returns:
            Composite score [0, 1] (higher is better)
        """
        # Weighted combination of metrics
        score = (
            0.3 * result.confidence +
            0.3 * result.energy_fidelity +
            0.2 * result.entropy_coherence +
            0.2 * (1.0 if result.aspiration_met else 0.0)
        )
        return float(score)

    def generate_report(self) -> str:
        """
        Generate human-readable report of Socratic iterations.

        Returns:
            Formatted report string
        """
        if not self.iteration_history:
            return "No Socratic iterations performed yet."

        report = []
        report.append("=" * 60)
        report.append("SOCRATIC LOOP ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"\nTotal Iterations: {len(self.iteration_history)}")

        for i, analysis in enumerate(self.iteration_history):
            report.append(f"\n--- Iteration {i + 1} ---")

            if not analysis.failure_modes:
                report.append("✓ No failures detected")
            else:
                report.append(f"Identified {len(analysis.failure_modes)} failure modes:")
                for mode in analysis.failure_modes:
                    report.append(f"\n  {mode.value.upper()}")
                    report.append(f"    Severity: {analysis.severity[mode]:.2f}")
                    report.append(f"    Cause: {analysis.root_causes[mode]}")
                    report.append(f"    Fix: {analysis.suggested_fixes[mode]}")

        report.append("\n" + "=" * 60)
        return "\n".join(report)


class SocraticACEAgent(ACEAgent):
    """
    ACE Agent with integrated Socratic Loop.

    Extends base ACE Agent with self-correction capabilities.
    """

    def __init__(
        self,
        ace_config: ACEConfig,
        socratic_config: SocraticConfig,
        model_path: Optional = None
    ):
        super().__init__(ace_config, model_path)
        self.socratic_loop = SocraticLoop(socratic_config)

    def predict_with_correction(
        self,
        energy_t: np.ndarray,
        grad_x: np.ndarray,
        grad_y: np.ndarray,
        energy_target: Optional[np.ndarray] = None
    ) -> Tuple[PredictionResult, List[ErrorAnalysis]]:
        """
        Make prediction with Socratic self-correction.

        Wrapper around SocraticLoop.predict_with_correction() for convenience.
        """
        return self.socratic_loop.predict_with_correction(
            self, energy_t, grad_x, grad_y, energy_target
        )

    def generate_socratic_report(self) -> str:
        """Generate report of Socratic iterations."""
        return self.socratic_loop.generate_report()
