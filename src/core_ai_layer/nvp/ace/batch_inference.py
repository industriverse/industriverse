#!/usr/bin/env python3
"""
batch_inference.py
Batch Inference Utilities for ACE Agents

Provides efficient batch processing, result aggregation, and performance tracking
for production inference workflows.
"""

from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass, field
import numpy as np
import time
from pathlib import Path
import json

from .ace_agent import ACEAgent, PredictionResult


@dataclass
class BatchInferenceConfig:
    """Configuration for batch inference."""
    # Processing
    batch_size: int = 16  # Process this many predictions at once
    show_progress: bool = True
    verbose: bool = False

    # Error handling
    skip_on_error: bool = True  # Continue on errors
    max_retries: int = 3

    # Output
    save_intermediate: bool = False  # Save after each sequence
    output_dir: Optional[Path] = None


@dataclass
class BatchResult:
    """Results from batch inference."""
    # Predictions
    predictions: List[np.ndarray]  # List of (T, H, W) arrays
    uncertainties: List[np.ndarray]
    targets: Optional[List[np.ndarray]] = None

    # Per-prediction results
    results: List[PredictionResult] = field(default_factory=list)

    # Aggregate statistics
    total_predictions: int = 0
    successful_predictions: int = 0
    failed_predictions: int = 0
    total_time: float = 0.0

    # Metrics
    mean_confidence: float = 0.0
    std_confidence: float = 0.0
    mean_fidelity: float = 0.0
    std_fidelity: float = 0.0
    mean_entropy: float = 0.0
    std_entropy: float = 0.0
    aspiration_rate: float = 0.0

    # Performance
    throughput: float = 0.0  # predictions/sec
    mean_latency: float = 0.0  # sec/prediction

    # Errors
    errors: List[Tuple[int, str]] = field(default_factory=list)  # (index, error_msg)


class BatchInferenceEngine:
    """
    Batch Inference Engine for ACE Agents

    Efficiently processes multiple energy sequences with result aggregation,
    error handling, and performance tracking.
    """

    def __init__(
        self,
        agent: ACEAgent,
        config: BatchInferenceConfig = None
    ):
        """
        Initialize batch inference engine.

        Args:
            agent: ACE agent for inference
            config: Batch inference configuration
        """
        self.agent = agent
        self.config = config or BatchInferenceConfig()

        # Statistics tracking
        self.stats = {
            'confidence': [],
            'energy_fidelity': [],
            'entropy_coherence': [],
            'aspiration_met': [],
            'execution_time': []
        }

    def process_sequence(
        self,
        sequence: np.ndarray,
        use_socratic: bool = False,
        target_available: bool = True
    ) -> Tuple[List[np.ndarray], List[np.ndarray], List[PredictionResult]]:
        """
        Process a single energy sequence.

        Args:
            sequence: Energy sequence (T, H, W)
            use_socratic: Use Socratic correction if agent supports it
            target_available: Whether to use targets for metrics

        Returns:
            predictions: List of predicted energy states
            uncertainties: List of uncertainty maps
            results: List of PredictionResult objects
        """
        T, H, W = sequence.shape

        predictions = []
        uncertainties = []
        results = []

        for t in range(T - 1):
            energy_t = sequence[t]
            energy_target = sequence[t + 1] if target_available else None

            # Compute gradients
            grad_x = np.gradient(energy_t, axis=1)
            grad_y = np.gradient(energy_t, axis=0)

            # Make prediction
            try:
                if use_socratic and hasattr(self.agent, 'predict_with_correction'):
                    # Socratic correction
                    result, history = self.agent.predict_with_correction(
                        energy_t, grad_x, grad_y, energy_target
                    )
                else:
                    # Standard prediction
                    result = self.agent.predict(energy_t, grad_x, grad_y, energy_target)

                predictions.append(result.energy_pred)
                uncertainties.append(result.uncertainty)
                results.append(result)

                # Track statistics
                self.stats['confidence'].append(result.confidence)
                self.stats['energy_fidelity'].append(result.energy_fidelity)
                self.stats['entropy_coherence'].append(result.entropy_coherence)
                self.stats['aspiration_met'].append(result.aspiration_met)
                self.stats['execution_time'].append(result.execution_time)

            except Exception as e:
                if not self.config.skip_on_error:
                    raise

                # Create dummy result on error
                predictions.append(np.zeros_like(energy_t))
                uncertainties.append(np.ones_like(energy_t))

                error_result = PredictionResult(
                    energy_pred=np.zeros_like(energy_t),
                    uncertainty=np.ones_like(energy_t),
                    confidence=0.0,
                    energy_fidelity=0.0,
                    entropy_coherence=0.0,
                    aspiration_met=False,
                    num_retries=0,
                    execution_time=0.0
                )
                results.append(error_result)

                if self.config.verbose:
                    print(f"  Error at t={t}: {e}")

        return predictions, uncertainties, results

    def process_batch(
        self,
        sequences: List[np.ndarray],
        use_socratic: bool = False,
        save_targets: bool = True
    ) -> BatchResult:
        """
        Process a batch of energy sequences.

        Args:
            sequences: List of energy sequences (each T, H, W)
            use_socratic: Use Socratic correction if available
            save_targets: Save ground truth targets

        Returns:
            BatchResult with predictions and statistics
        """
        if self.config.show_progress:
            print(f"\nProcessing {len(sequences)} sequences...")

        start_time = time.time()

        all_predictions = []
        all_uncertainties = []
        all_targets = [] if save_targets else None
        all_results = []

        for seq_idx, sequence in enumerate(sequences):
            if self.config.show_progress:
                print(f"  Sequence {seq_idx + 1}/{len(sequences)} "
                      f"(shape: {sequence.shape})", end='')

            seq_start = time.time()

            try:
                # Process sequence
                predictions, uncertainties, results = self.process_sequence(
                    sequence,
                    use_socratic=use_socratic,
                    target_available=True
                )

                all_predictions.append(np.stack(predictions, axis=0))
                all_uncertainties.append(np.stack(uncertainties, axis=0))
                all_results.extend(results)

                if save_targets:
                    # Extract targets (t+1 for each t)
                    targets = [sequence[t + 1] for t in range(len(sequence) - 1)]
                    all_targets.append(np.stack(targets, axis=0))

                seq_time = time.time() - seq_start

                if self.config.show_progress:
                    print(f" ✓ ({seq_time:.2f}s, {len(predictions)} predictions)")

                # Save intermediate results if requested
                if self.config.save_intermediate and self.config.output_dir:
                    self._save_sequence_result(
                        seq_idx,
                        predictions,
                        uncertainties,
                        targets if save_targets else None
                    )

            except Exception as e:
                if not self.config.skip_on_error:
                    raise

                error_msg = f"Failed to process sequence {seq_idx}: {e}"
                print(f" ✗ {error_msg}")

                # Add to error list
                if self.config.show_progress:
                    print(f"    (skipping and continuing...)")

        total_time = time.time() - start_time

        # Compute aggregate statistics
        result = self._compute_batch_statistics(
            all_predictions,
            all_uncertainties,
            all_targets,
            all_results,
            total_time
        )

        if self.config.show_progress:
            self._print_summary(result)

        return result

    def _compute_batch_statistics(
        self,
        predictions: List[np.ndarray],
        uncertainties: List[np.ndarray],
        targets: Optional[List[np.ndarray]],
        results: List[PredictionResult],
        total_time: float
    ) -> BatchResult:
        """Compute aggregate statistics from batch results."""

        total_predictions = len(results)
        successful_predictions = sum(1 for r in results if r.aspiration_met)

        # Extract metrics
        confidences = [r.confidence for r in results]
        fidelities = [r.energy_fidelity for r in results]
        entropies = [r.entropy_coherence for r in results]
        aspirations = [r.aspiration_met for r in results]
        exec_times = [r.execution_time for r in results]

        return BatchResult(
            predictions=predictions,
            uncertainties=uncertainties,
            targets=targets,
            results=results,
            total_predictions=total_predictions,
            successful_predictions=successful_predictions,
            failed_predictions=total_predictions - successful_predictions,
            total_time=total_time,
            mean_confidence=float(np.mean(confidences)) if confidences else 0.0,
            std_confidence=float(np.std(confidences)) if confidences else 0.0,
            mean_fidelity=float(np.mean(fidelities)) if fidelities else 0.0,
            std_fidelity=float(np.std(fidelities)) if fidelities else 0.0,
            mean_entropy=float(np.mean(entropies)) if entropies else 0.0,
            std_entropy=float(np.std(entropies)) if entropies else 0.0,
            aspiration_rate=float(np.mean(aspirations)) if aspirations else 0.0,
            throughput=total_predictions / total_time if total_time > 0 else 0.0,
            mean_latency=float(np.mean(exec_times)) if exec_times else 0.0
        )

    def _print_summary(self, result: BatchResult):
        """Print batch inference summary."""
        print("\n" + "="*60)
        print("BATCH INFERENCE SUMMARY")
        print("="*60)
        print(f"Total Predictions:     {result.total_predictions}")
        print(f"Successful:            {result.successful_predictions} "
              f"({result.aspiration_rate:.1%})")
        print(f"Total Time:            {result.total_time:.2f}s")
        print(f"Throughput:            {result.throughput:.2f} pred/sec")
        print(f"Mean Latency:          {result.mean_latency*1000:.2f}ms")
        print(f"\nMetrics:")
        print(f"  Confidence:          {result.mean_confidence:.4f} ± {result.std_confidence:.4f}")
        print(f"  Energy Fidelity:     {result.mean_fidelity:.4f} ± {result.std_fidelity:.4f}")
        print(f"  Entropy Coherence:   {result.mean_entropy:.4f} ± {result.std_entropy:.4f}")
        print("="*60)

    def _save_sequence_result(
        self,
        seq_idx: int,
        predictions: List[np.ndarray],
        uncertainties: List[np.ndarray],
        targets: Optional[List[np.ndarray]]
    ):
        """Save intermediate sequence result."""
        if not self.config.output_dir:
            return

        output_path = self.config.output_dir / f"seq_{seq_idx:04d}.npz"

        save_dict = {
            'predictions': np.stack(predictions, axis=0),
            'uncertainties': np.stack(uncertainties, axis=0)
        }

        if targets is not None:
            save_dict['targets'] = np.stack(targets, axis=0)

        np.savez_compressed(output_path, **save_dict)

    def save_results(
        self,
        result: BatchResult,
        output_dir: Path
    ):
        """
        Save batch inference results to disk.

        Args:
            result: BatchResult to save
            output_dir: Output directory
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        # Save aggregate statistics as JSON
        stats = {
            'total_predictions': result.total_predictions,
            'successful_predictions': result.successful_predictions,
            'failed_predictions': result.failed_predictions,
            'total_time': result.total_time,
            'throughput': result.throughput,
            'mean_latency': result.mean_latency,
            'mean_confidence': result.mean_confidence,
            'std_confidence': result.std_confidence,
            'mean_fidelity': result.mean_fidelity,
            'std_fidelity': result.std_fidelity,
            'mean_entropy': result.mean_entropy,
            'std_entropy': result.std_entropy,
            'aspiration_rate': result.aspiration_rate
        }

        with open(output_dir / 'batch_stats.json', 'w') as f:
            json.dump(stats, f, indent=2)

        # Save predictions
        for i, pred in enumerate(result.predictions):
            pred_path = output_dir / f"predictions_{i:04d}.npz"
            save_dict = {
                'predictions': pred,
                'uncertainties': result.uncertainties[i]
            }
            if result.targets is not None:
                save_dict['targets'] = result.targets[i]
            np.savez_compressed(pred_path, **save_dict)

        print(f"\n✓ Results saved to {output_dir}")


def batch_predict(
    agent: ACEAgent,
    sequences: List[np.ndarray],
    config: Optional[BatchInferenceConfig] = None,
    use_socratic: bool = False
) -> BatchResult:
    """
    Convenience function for batch prediction.

    Args:
        agent: ACE agent
        sequences: List of energy sequences
        config: Batch inference configuration
        use_socratic: Use Socratic correction

    Returns:
        BatchResult with predictions and statistics
    """
    engine = BatchInferenceEngine(agent, config)
    return engine.process_batch(sequences, use_socratic=use_socratic)


def compare_predictions(
    predictions: np.ndarray,
    targets: np.ndarray
) -> Dict[str, float]:
    """
    Compare predictions against ground truth targets.

    Args:
        predictions: Predicted energy states (T, H, W)
        targets: Target energy states (T, H, W)

    Returns:
        Dictionary of comparison metrics
    """
    # RMSE
    rmse = float(np.sqrt(np.mean((predictions - targets) ** 2)))

    # MAE
    mae = float(np.mean(np.abs(predictions - targets)))

    # Energy conservation error
    pred_total = np.sum(predictions, axis=(1, 2))
    target_total = np.sum(targets, axis=(1, 2))
    energy_error = float(np.mean(np.abs(pred_total - target_total) / (target_total + 1e-10)))

    # Correlation
    pred_flat = predictions.flatten()
    target_flat = targets.flatten()
    correlation = float(np.corrcoef(pred_flat, target_flat)[0, 1])

    # Peak signal-to-noise ratio (PSNR)
    mse = np.mean((predictions - targets) ** 2)
    max_val = np.max(targets)
    psnr = float(20 * np.log10(max_val / (np.sqrt(mse) + 1e-10)))

    return {
        'rmse': rmse,
        'mae': mae,
        'energy_error': energy_error,
        'correlation': correlation,
        'psnr': psnr
    }
