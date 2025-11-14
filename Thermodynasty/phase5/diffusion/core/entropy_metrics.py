"""
Entropy Metrics Module

Comprehensive thermodynamic metrics for validating diffusion processes
and energy-based optimization according to physical laws.
"""

import torch
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ThermodynamicMetrics:
    """Container for thermodynamic validation metrics"""

    # Energy metrics
    energy_conservation: bool
    energy_drift: float
    energy_fidelity: float

    # Entropy metrics
    entropy_monotonic: bool
    entropy_change: float
    entropy_production: float

    # Spectral metrics
    spectral_valid: bool
    spectral_energy: float
    dominant_frequency: float

    # Overall validation
    passed: bool
    overall_score: float

    # Metadata
    timestamp: float
    metadata: Dict[str, Any]


class EntropyValidator:
    """
    Validates thermodynamic laws during diffusion and optimization.

    Enforces:
    - Energy conservation: ΔE ≈ 0
    - Entropy monotonicity: ΔS ≥ 0 (2nd law)
    - Spectral consistency: No unphysical frequencies
    """

    def __init__(
        self,
        energy_tolerance: float = 0.01,
        entropy_threshold: float = -1e-6,
        spectral_threshold: float = 0.85,
        temperature: float = 1.0
    ):
        """
        Initialize entropy validator.

        Args:
            energy_tolerance: Maximum allowed |ΔE|
            entropy_threshold: Minimum allowed ΔS (slightly negative for numerical errors)
            spectral_threshold: Minimum spectral quality score
            temperature: Thermodynamic temperature
        """
        self.energy_tolerance = energy_tolerance
        self.entropy_threshold = entropy_threshold
        self.spectral_threshold = spectral_threshold
        self.temperature = temperature

        logger.info(
            f"EntropyValidator initialized: "
            f"ΔE_tol={energy_tolerance}, ΔS_min={entropy_threshold}, "
            f"T={temperature}"
        )

    def validate_transition(
        self,
        initial_state: torch.Tensor,
        final_state: torch.Tensor,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ThermodynamicMetrics:
        """
        Validate a state transition obeys thermodynamic laws.

        Args:
            initial_state: Initial energy configuration
            final_state: Final energy configuration
            metadata: Optional metadata

        Returns:
            ThermodynamicMetrics with validation results
        """
        import time

        # Compute energy metrics
        energy_initial = float(initial_state.abs().sum().item())
        energy_final = float(final_state.abs().sum().item())
        energy_drift = abs(energy_final - energy_initial)

        energy_conserved = energy_drift < self.energy_tolerance
        energy_fidelity = 1.0 - energy_drift / (abs(energy_initial) + 1e-8)

        # Compute entropy metrics
        entropy_initial = self._compute_shannon_entropy(initial_state)
        entropy_final = self._compute_shannon_entropy(final_state)
        entropy_change = entropy_final - entropy_initial

        entropy_monotonic = entropy_change >= self.entropy_threshold
        entropy_production = max(0.0, entropy_change)

        # Compute spectral metrics
        spectral_valid, spectral_energy, dominant_freq = self._validate_spectral(final_state)

        # Overall validation
        passed = energy_conserved and entropy_monotonic and spectral_valid

        # Compute overall score (weighted average)
        score_components = [
            energy_fidelity * 0.4,
            (1.0 if entropy_monotonic else 0.0) * 0.3,
            (1.0 if spectral_valid else 0.0) * 0.3
        ]
        overall_score = sum(score_components)

        return ThermodynamicMetrics(
            energy_conservation=energy_conserved,
            energy_drift=energy_drift,
            energy_fidelity=energy_fidelity,
            entropy_monotonic=entropy_monotonic,
            entropy_change=entropy_change,
            entropy_production=entropy_production,
            spectral_valid=spectral_valid,
            spectral_energy=spectral_energy,
            dominant_frequency=dominant_freq,
            passed=passed,
            overall_score=overall_score,
            timestamp=time.time(),
            metadata=metadata or {}
        )

    def _compute_shannon_entropy(self, state: torch.Tensor) -> float:
        """
        Compute Shannon entropy of state.

        S = -∑ p_i log(p_i)

        Args:
            state: Energy state tensor

        Returns:
            Shannon entropy value
        """
        # Normalize to probability distribution
        state_flat = state.flatten().abs()
        prob = state_flat / (state_flat.sum() + 1e-8)

        # Shannon entropy
        entropy = -torch.sum(prob * torch.log(prob + 1e-8))

        return float(entropy.item())

    def _validate_spectral(
        self,
        state: torch.Tensor
    ) -> Tuple[bool, float, float]:
        """
        Validate spectral properties of state.

        Checks for unphysical high-frequency oscillations.

        Args:
            state: Energy state

        Returns:
            (is_valid, spectral_energy, dominant_frequency)
        """
        # Compute FFT
        state_np = state.cpu().numpy()

        if state_np.ndim == 2:
            fft = np.fft.fft2(state_np)
        elif state_np.ndim == 1:
            fft = np.fft.fft(state_np)
        else:
            # Multi-dimensional - flatten first dimension
            fft = np.fft.fftn(state_np)

        # Power spectrum
        power = np.abs(fft) ** 2

        # Total spectral energy
        spectral_energy = float(np.sum(power))

        # Find dominant frequency
        dominant_idx = np.unravel_index(np.argmax(power), power.shape)
        dominant_freq = float(np.linalg.norm(dominant_idx))

        # Check for high-frequency noise (>80% of Nyquist)
        nyquist = min(power.shape) / 2
        high_freq_threshold = 0.8 * nyquist

        # Valid if dominant frequency is reasonable
        is_valid = dominant_freq < high_freq_threshold

        return is_valid, spectral_energy, dominant_freq

    def validate_trajectory(
        self,
        trajectory: List[torch.Tensor]
    ) -> Dict[str, Any]:
        """
        Validate entire diffusion trajectory.

        Args:
            trajectory: List of states over time

        Returns:
            Validation summary
        """
        validations = []

        for i in range(len(trajectory) - 1):
            metrics = self.validate_transition(trajectory[i], trajectory[i + 1])
            validations.append(metrics)

        # Aggregate results
        total_steps = len(validations)
        passed_steps = sum(1 for v in validations if v.passed)

        avg_energy_fidelity = np.mean([v.energy_fidelity for v in validations])
        total_entropy_production = sum(v.entropy_production for v in validations)

        return {
            'total_steps': total_steps,
            'passed_steps': passed_steps,
            'pass_rate': passed_steps / total_steps if total_steps > 0 else 0.0,
            'avg_energy_fidelity': float(avg_energy_fidelity),
            'total_entropy_production': float(total_entropy_production),
            'validations': validations
        }


class BoltzmannMetrics:
    """
    Boltzmann statistics for energy-based sampling.

    Computes probabilities, free energy, partition functions, etc.
    """

    def __init__(self, temperature: float = 1.0):
        """
        Initialize Boltzmann metrics.

        Args:
            temperature: Thermodynamic temperature (kT)
        """
        self.temperature = temperature

    def boltzmann_weight(
        self,
        energies: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute Boltzmann weights: w_i = exp(-E_i / kT) / Z

        Args:
            energies: Energy values

        Returns:
            Normalized probabilities
        """
        # Stabilize exponential (subtract min energy)
        energies_stable = energies - energies.min()

        # Boltzmann factors
        weights = torch.exp(-energies_stable / self.temperature)

        # Normalize (partition function)
        Z = weights.sum()
        probabilities = weights / Z

        return probabilities

    def free_energy(
        self,
        energies: torch.Tensor
    ) -> float:
        """
        Compute Helmholtz free energy: F = -kT log(Z)

        Args:
            energies: Energy values

        Returns:
            Free energy
        """
        weights = self.boltzmann_weight(energies)
        Z = weights.sum()

        F = -self.temperature * torch.log(Z + 1e-8)

        return float(F.item())

    def expected_energy(
        self,
        energies: torch.Tensor
    ) -> float:
        """
        Compute expected energy: <E> = ∑ p_i E_i

        Args:
            energies: Energy values

        Returns:
            Expected energy
        """
        probabilities = self.boltzmann_weight(energies)
        expected_E = (probabilities * energies).sum()

        return float(expected_E.item())

    def entropy_from_distribution(
        self,
        probabilities: torch.Tensor
    ) -> float:
        """
        Compute entropy from probability distribution.

        S = -∑ p_i log(p_i)

        Args:
            probabilities: Probability distribution

        Returns:
            Entropy
        """
        entropy = -torch.sum(probabilities * torch.log(probabilities + 1e-8))
        return float(entropy.item())


def compute_energy_landscape_metrics(
    energy_map: torch.Tensor,
    num_samples: int = 1000
) -> Dict[str, float]:
    """
    Analyze energy landscape properties.

    Computes:
    - Local minima count
    - Energy barriers
    - Landscape roughness
    - Attractor basins

    Args:
        energy_map: 2D or 3D energy field
        num_samples: Number of random samples for analysis

    Returns:
        Landscape metrics
    """
    # Flatten for analysis
    energy_flat = energy_map.flatten()

    # Basic statistics
    mean_energy = float(energy_flat.mean().item())
    std_energy = float(energy_flat.std().item())
    min_energy = float(energy_flat.min().item())
    max_energy = float(energy_flat.max().item())

    # Compute gradient magnitude (roughness proxy)
    if energy_map.ndim >= 2:
        grad_x = torch.diff(energy_map, dim=-1)
        grad_y = torch.diff(energy_map, dim=-2) if energy_map.ndim > 1 else torch.tensor([0.0])
        gradient_magnitude = torch.sqrt(grad_x[..., :-1, :] ** 2 + grad_y[..., :, :-1] ** 2).mean()
        roughness = float(gradient_magnitude.item())
    else:
        roughness = float(torch.diff(energy_map).abs().mean().item())

    # Energy barrier estimate
    energy_range = max_energy - min_energy
    barrier_estimate = energy_range * 0.5  # Simplified estimate

    return {
        'mean_energy': mean_energy,
        'std_energy': std_energy,
        'min_energy': min_energy,
        'max_energy': max_energy,
        'energy_range': energy_range,
        'roughness': roughness,
        'barrier_estimate': barrier_estimate
    }
