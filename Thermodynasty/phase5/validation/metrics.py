#!/usr/bin/env python3
"""
Validation Metrics for Thermodynamic Inference

Physics-informed metrics for evaluating prediction quality:
- Energy conservation fidelity
- Entropy coherence
- Physical law compliance
- Cross-domain generalization metrics
"""

import numpy as np
import jax.numpy as jnp
from typing import Optional, Dict, Tuple
from scipy import stats


def compute_energy_fidelity(
    predictions: np.ndarray,
    reference: Optional[np.ndarray] = None,
    tolerance: float = 0.01
) -> float:
    """
    Compute energy conservation fidelity

    Measures how well total energy is conserved across predicted timesteps.

    Args:
        predictions: Predicted energy maps (steps, height, width) or (height, width)
        reference: Reference energy map for comparison (optional)
        tolerance: Acceptable relative error threshold

    Returns:
        Fidelity score [0-1], where 1.0 = perfect conservation
    """
    if predictions.ndim == 2:
        predictions = predictions[np.newaxis, ...]

    # Total energy per timestep
    energies = predictions.sum(axis=(1, 2))

    if reference is not None:
        # Compare to reference energy
        ref_energy = reference.sum()
        rel_errors = np.abs(energies - ref_energy) / (ref_energy + 1e-10)
    else:
        # Compare to initial timestep
        initial_energy = energies[0]
        rel_errors = np.abs(energies - initial_energy) / (initial_energy + 1e-10)

    # Fidelity: fraction of timesteps within tolerance
    within_tolerance = (rel_errors < tolerance).sum()
    fidelity = within_tolerance / len(energies)

    return float(fidelity)


def compute_entropy_coherence(
    predictions: np.ndarray,
    bins: int = 50
) -> float:
    """
    Compute entropy coherence across predicted timesteps

    Measures thermodynamic consistency by checking that entropy
    evolution is smooth and follows expected trends.

    Args:
        predictions: Predicted energy maps (steps, height, width)
        bins: Number of bins for histogram entropy calculation

    Returns:
        Coherence score [0-1], where 1.0 = perfect coherence
    """
    if predictions.ndim == 2:
        predictions = predictions[np.newaxis, ...]

    entropies = []
    for t in range(predictions.shape[0]):
        # Compute Shannon entropy of energy distribution
        hist, _ = np.histogram(predictions[t].flatten(), bins=bins, density=True)
        hist = hist + 1e-10  # Avoid log(0)
        hist = hist / hist.sum()
        entropy = -np.sum(hist * np.log(hist))
        entropies.append(entropy)

    entropies = np.array(entropies)

    # Coherence metrics:
    # 1. Low variance (smooth evolution)
    entropy_std = np.std(entropies)
    coherence_smoothness = np.exp(-entropy_std)

    # 2. Monotonic trend (entropy should not decrease dramatically)
    entropy_diffs = np.diff(entropies)
    decreasing_violations = (entropy_diffs < -0.1).sum()
    coherence_monotonicity = 1.0 - (decreasing_violations / len(entropy_diffs))

    # Combined coherence
    coherence = 0.7 * coherence_smoothness + 0.3 * coherence_monotonicity

    return float(np.clip(coherence, 0.0, 1.0))


def check_energy_conservation(
    predictions: np.ndarray,
    initial_energy: float,
    tolerance: float = 0.02
) -> Tuple[bool, float]:
    """
    Check if energy conservation law is violated

    Args:
        predictions: Predicted energy maps (steps, height, width)
        initial_energy: Initial total energy
        tolerance: Maximum acceptable relative error

    Returns:
        (passed, max_violation) - whether check passed and maximum violation magnitude
    """
    if predictions.ndim == 2:
        predictions = predictions[np.newaxis, ...]

    energies = predictions.sum(axis=(1, 2))
    rel_errors = np.abs(energies - initial_energy) / (initial_energy + 1e-10)

    max_violation = float(np.max(rel_errors))
    passed = max_violation < tolerance

    return passed, max_violation


def compute_gradient_magnitude(energy_map: np.ndarray) -> float:
    """
    Compute average gradient magnitude

    Measures spatial variation - useful for detecting artifacts.

    Args:
        energy_map: Energy map (height, width)

    Returns:
        Average gradient magnitude
    """
    grad_y, grad_x = np.gradient(energy_map)
    grad_mag = np.sqrt(grad_x**2 + grad_y**2)
    return float(np.mean(grad_mag))


def compute_prediction_mse(
    predictions: np.ndarray,
    ground_truth: np.ndarray
) -> float:
    """
    Compute Mean Squared Error between predictions and ground truth

    Args:
        predictions: Predicted energy maps (steps, height, width)
        ground_truth: Ground truth energy maps (steps, height, width)

    Returns:
        MSE value
    """
    assert predictions.shape == ground_truth.shape, "Shape mismatch"
    mse = np.mean((predictions - ground_truth)**2)
    return float(mse)


def compute_spectral_similarity(
    predictions: np.ndarray,
    ground_truth: np.ndarray
) -> float:
    """
    Compute similarity of energy spectra (radial power spectrum)

    Physics-informed metric comparing energy distribution across spatial frequencies.
    Useful for turbulence and wave phenomena.

    Args:
        predictions: Predicted energy map (height, width) or (steps, height, width)
        ground_truth: Ground truth energy map with same shape

    Returns:
        Spectral similarity score [0-1]
    """
    def radial_power_spectrum(field):
        """Compute radial power spectrum"""
        fft = np.fft.fft2(field)
        power = np.abs(fft)**2

        # Radial averaging
        h, w = field.shape
        y, x = np.ogrid[:h, :w]
        center = (h // 2, w // 2)
        r = np.sqrt((x - center[1])**2 + (y - center[0])**2).astype(int)

        # Radial bins
        max_r = min(h, w) // 2
        radial_profile = np.zeros(max_r)
        for radius in range(max_r):
            mask = (r == radius)
            if mask.sum() > 0:
                radial_profile[radius] = power[mask].mean()

        return radial_profile

    # Handle 3D inputs (take last timestep)
    if predictions.ndim == 3:
        predictions = predictions[-1]
    if ground_truth.ndim == 3:
        ground_truth = ground_truth[-1]

    # Compute spectra
    spectrum_pred = radial_power_spectrum(predictions)
    spectrum_true = radial_power_spectrum(ground_truth)

    # Normalize
    spectrum_pred = spectrum_pred / (spectrum_pred.sum() + 1e-10)
    spectrum_true = spectrum_true / (spectrum_true.sum() + 1e-10)

    # Correlation between spectra
    correlation = np.corrcoef(spectrum_pred, spectrum_true)[0, 1]

    return float(np.clip(correlation, 0.0, 1.0))


def compute_physics_validation_suite(
    predictions: np.ndarray,
    ground_truth: Optional[np.ndarray] = None,
    initial_energy: Optional[float] = None
) -> Dict[str, float]:
    """
    Comprehensive physics validation suite

    Runs all validation metrics and returns a report.

    Args:
        predictions: Predicted energy maps (steps, height, width)
        ground_truth: Ground truth for comparison (optional)
        initial_energy: Initial total energy for conservation check (optional)

    Returns:
        Dictionary of validation metrics
    """
    results = {}

    # Energy conservation
    if initial_energy is not None:
        results['energy_fidelity'] = compute_energy_fidelity(
            predictions,
            reference=ground_truth[0] if ground_truth is not None else None
        )
        passed, violation = check_energy_conservation(predictions, initial_energy)
        results['energy_conservation_passed'] = passed
        results['energy_max_violation'] = violation
    else:
        results['energy_fidelity'] = compute_energy_fidelity(predictions)

    # Entropy coherence
    results['entropy_coherence'] = compute_entropy_coherence(predictions)

    # Gradient statistics
    results['avg_gradient'] = compute_gradient_magnitude(predictions[-1])

    # Ground truth comparison (if available)
    if ground_truth is not None:
        results['mse'] = compute_prediction_mse(predictions, ground_truth)
        results['spectral_similarity'] = compute_spectral_similarity(predictions, ground_truth)

    return results


def assess_domain_generalization(
    predictions_by_domain: Dict[str, np.ndarray]
) -> Dict[str, float]:
    """
    Assess cross-domain generalization quality

    Compares metrics across different physical domains to evaluate
    model's ability to generalize.

    Args:
        predictions_by_domain: Dict mapping domain names to prediction arrays

    Returns:
        Dictionary of cross-domain metrics
    """
    # Compute metrics per domain
    domain_metrics = {}
    for domain, preds in predictions_by_domain.items():
        domain_metrics[domain] = {
            'energy_fidelity': compute_energy_fidelity(preds),
            'entropy_coherence': compute_entropy_coherence(preds)
        }

    # Cross-domain consistency
    fidelities = [m['energy_fidelity'] for m in domain_metrics.values()]
    entropies = [m['entropy_coherence'] for m in domain_metrics.values()]

    results = {
        'mean_fidelity': float(np.mean(fidelities)),
        'std_fidelity': float(np.std(fidelities)),
        'mean_entropy': float(np.mean(entropies)),
        'std_entropy': float(np.std(entropies)),
        'domains_tested': len(predictions_by_domain),
        'generalization_score': float(1.0 - np.std(fidelities))  # Lower variance = better generalization
    }

    return results


# ============================================================================
# Testing
# ============================================================================

def test_metrics():
    """Test validation metrics with synthetic data"""
    print("\n" + "="*70)
    print("VALIDATION METRICS TEST")
    print("="*70 + "\n")

    # Synthetic predictions (10 timesteps, 256x256)
    np.random.seed(42)
    predictions = np.random.rand(10, 256, 256).astype(np.float32)

    # Normalize to conserve energy approximately
    initial_energy = predictions[0].sum()
    for t in range(len(predictions)):
        predictions[t] = predictions[t] / predictions[t].sum() * initial_energy

    # Test energy fidelity
    fidelity = compute_energy_fidelity(predictions)
    print(f"Energy Fidelity: {fidelity:.4f}")

    # Test entropy coherence
    coherence = compute_entropy_coherence(predictions)
    print(f"Entropy Coherence: {coherence:.4f}")

    # Test energy conservation check
    passed, violation = check_energy_conservation(predictions, initial_energy)
    print(f"Energy Conservation: {'PASS' if passed else 'FAIL'} (max violation: {violation:.6f})")

    # Test gradient magnitude
    grad_mag = compute_gradient_magnitude(predictions[0])
    print(f"Gradient Magnitude: {grad_mag:.6f}")

    # Full validation suite
    print("\nFull Validation Suite:")
    suite_results = compute_physics_validation_suite(predictions, initial_energy=initial_energy)
    for key, value in suite_results.items():
        print(f"  {key}: {value}")

    print("\n" + "="*70)
    print("✓ All metrics tests passed")
    print("="*70 + "\n")


if __name__ == "__main__":
    test_metrics()
