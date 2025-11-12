#!/usr/bin/env python3
"""
test_synthetic_generator.py
Unit tests for Synthetic Energy Map Generator

Tests thermodynamic constraints:
- Energy conservation under perturbations
- Entropy monotonicity (2nd law)
- Physical validity of generated sequences
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from phase4.data.synthetic_generator import (
    generate_sequence,
    generate_base_pattern,
    apply_rotation,
    apply_gaussian_noise,
    apply_thermal_blur,
    apply_translation,
    apply_energy_scaling,
    compute_entropy,
    validate_energy_conservation,
    validate_entropy_increase,
    PerturbationConfig,
    ThermodynamicViolation,
    ENERGY_CONSERVATION_TOLERANCE
)


@pytest.fixture
def sample_energy_map():
    """Create sample 128x128 energy map."""
    np.random.seed(42)
    x = np.linspace(0, 2 * np.pi, 128)
    y = np.linspace(0, 2 * np.pi, 128)
    X, Y = np.meshgrid(x, y)
    energy_map = np.sin(X) * np.cos(Y) + 2.0
    return energy_map


class TestEnergyConservation:
    """Test energy conservation under various perturbations."""

    def test_rotation_conserves_energy(self, sample_energy_map):
        """Test that rotation preserves total energy."""
        E_before = np.sum(sample_energy_map)

        rotated = apply_rotation(sample_energy_map, angle=45.0)

        E_after = np.sum(rotated)
        error = abs(E_after - E_before) / E_before

        assert error < ENERGY_CONSERVATION_TOLERANCE, (
            f"Rotation violated energy conservation: ΔE/E = {error:.4f}"
        )

    def test_noise_conserves_energy(self, sample_energy_map):
        """Test that Gaussian noise preserves total energy."""
        E_before = np.sum(sample_energy_map)

        noisy = apply_gaussian_noise(sample_energy_map, sigma=0.1)

        E_after = np.sum(noisy)
        error = abs(E_after - E_before) / E_before

        assert error < ENERGY_CONSERVATION_TOLERANCE, (
            f"Noise violated energy conservation: ΔE/E = {error:.4f}"
        )

    def test_thermal_blur_conserves_energy(self, sample_energy_map):
        """Test that thermal blur preserves total energy."""
        E_before = np.sum(sample_energy_map)

        blurred = apply_thermal_blur(sample_energy_map, sigma=3.0)

        E_after = np.sum(blurred)
        error = abs(E_after - E_before) / E_before

        assert error < ENERGY_CONSERVATION_TOLERANCE, (
            f"Thermal blur violated energy conservation: ΔE/E = {error:.4f}"
        )

    def test_translation_conserves_energy(self, sample_energy_map):
        """Test that translation preserves total energy."""
        E_before = np.sum(sample_energy_map)

        translated = apply_translation(sample_energy_map, shift_x=10, shift_y=5)

        E_after = np.sum(translated)

        # Translation with periodic boundary should conserve exactly
        np.testing.assert_allclose(E_after, E_before, rtol=1e-10)

    def test_scaling_changes_energy_correctly(self, sample_energy_map):
        """Test that scaling changes energy by correct factor."""
        E_before = np.sum(sample_energy_map)

        scale_factor = 1.5
        scaled = apply_energy_scaling(sample_energy_map, scale=scale_factor)

        E_after = np.sum(scaled)
        expected_energy = E_before * scale_factor

        np.testing.assert_allclose(E_after, expected_energy, rtol=1e-10)

    def test_validate_energy_conservation_accepts_valid(self, sample_energy_map):
        """Test validation accepts maps with conserved energy."""
        E_before = sample_energy_map.copy()
        E_after = sample_energy_map.copy() * 1.01  # 1% change

        # Should not raise
        assert validate_energy_conservation(E_before, E_after, tolerance=0.05)

    def test_validate_energy_conservation_rejects_violation(self, sample_energy_map):
        """Test validation rejects severe violations."""
        E_before = sample_energy_map.copy()
        E_after = sample_energy_map.copy() * 2.0  # 100% change

        with pytest.raises(ThermodynamicViolation):
            validate_energy_conservation(E_before, E_after, tolerance=0.05)


class TestEntropyBehavior:
    """Test entropy behavior under perturbations."""

    def test_compute_entropy_positive(self, sample_energy_map):
        """Test that entropy is always positive."""
        entropy = compute_entropy(sample_energy_map)

        assert entropy > 0
        assert np.isfinite(entropy)

    def test_thermal_blur_increases_entropy(self):
        """Test that thermal diffusion increases entropy."""
        # Create low-entropy map (concentrated energy)
        energy_map = np.zeros((128, 128))
        energy_map[60:68, 60:68] = 10.0

        S_before = compute_entropy(energy_map)

        blurred = apply_thermal_blur(energy_map, sigma=5.0)

        S_after = compute_entropy(blurred)

        # Blur should increase entropy
        assert S_after > S_before, (
            f"Thermal blur should increase entropy: "
            f"S_before={S_before:.4f}, S_after={S_after:.4f}"
        )

    def test_validate_entropy_increase_accepts_valid(self, sample_energy_map):
        """Test validation accepts entropy-increasing transforms."""
        E_before = sample_energy_map.copy()
        E_after = apply_thermal_blur(E_before, sigma=2.0)

        # Should not raise
        assert validate_entropy_increase(E_before, E_after)

    def test_sequence_entropy_monotonic(self, sample_energy_map):
        """Test that generated sequences have monotonic or stable entropy."""
        config = PerturbationConfig(
            enable_rotation=True,
            enable_noise=True,
            enable_thermal_blur=True,
            enable_translation=True
        )

        sequence, metadata = generate_sequence(
            sample_energy_map,
            n_steps=10,
            config=config,
            return_metadata=True
        )

        # Extract entropies
        entropies = [m['entropy'] for m in metadata]

        # Check that entropy doesn't decrease significantly
        for i in range(1, len(entropies)):
            delta_S = entropies[i] - entropies[i-1]
            # Allow small numerical decreases
            assert delta_S >= -0.01, (
                f"Significant entropy decrease at step {i}: ΔS = {delta_S:.4f}"
            )


class TestBasePatterns:
    """Test base pattern generation."""

    def test_generate_turbulent_pattern(self):
        """Test turbulent pattern generation."""
        pattern = generate_base_pattern(size=128, pattern_type='turbulent')

        assert pattern.shape == (128, 128)
        assert pattern.min() >= 0  # Energy is non-negative
        assert np.isfinite(pattern).all()

    def test_generate_laminar_pattern(self):
        """Test laminar pattern generation."""
        pattern = generate_base_pattern(size=128, pattern_type='laminar')

        assert pattern.shape == (128, 128)
        assert np.isfinite(pattern).all()

    def test_generate_vortex_pattern(self):
        """Test vortex pattern generation."""
        pattern = generate_base_pattern(size=128, pattern_type='vortex')

        assert pattern.shape == (128, 128)
        assert np.isfinite(pattern).all()

    def test_generate_random_pattern(self):
        """Test random pattern generation."""
        pattern = generate_base_pattern(size=128, pattern_type='random')

        assert pattern.shape == (128, 128)
        assert pattern.min() >= 0
        assert np.isfinite(pattern).all()

    def test_pattern_energy_normalized(self):
        """Test that patterns have normalized mean energy."""
        for pattern_type in ['turbulent', 'laminar', 'vortex', 'random']:
            pattern = generate_base_pattern(size=128, pattern_type=pattern_type)

            # Mean should be around 1.0
            mean_energy = np.mean(pattern)
            assert 0.5 < mean_energy < 1.5, (
                f"{pattern_type} pattern has mean {mean_energy:.2f}, expected ~1.0"
            )


class TestPerturbations:
    """Test individual perturbation functions."""

    def test_rotation_maintains_shape(self, sample_energy_map):
        """Test that rotation maintains array shape."""
        rotated = apply_rotation(sample_energy_map, angle=30.0)

        assert rotated.shape == sample_energy_map.shape

    def test_rotation_deterministic(self, sample_energy_map):
        """Test that rotation with same angle gives same result."""
        rotated1 = apply_rotation(sample_energy_map, angle=45.0)
        rotated2 = apply_rotation(sample_energy_map, angle=45.0)

        np.testing.assert_allclose(rotated1, rotated2)

    def test_noise_is_random(self, sample_energy_map):
        """Test that noise produces different results."""
        np.random.seed(42)
        noisy1 = apply_gaussian_noise(sample_energy_map, sigma=0.1)

        np.random.seed(43)
        noisy2 = apply_gaussian_noise(sample_energy_map, sigma=0.1)

        # Should be different
        assert not np.allclose(noisy1, noisy2)

    def test_noise_magnitude_scales_with_sigma(self, sample_energy_map):
        """Test that noise magnitude increases with sigma."""
        low_noise = apply_gaussian_noise(sample_energy_map, sigma=0.05)
        high_noise = apply_gaussian_noise(sample_energy_map, sigma=0.2)

        # Measure deviation from original
        dev_low = np.std(low_noise - sample_energy_map)
        dev_high = np.std(high_noise - sample_energy_map)

        assert dev_high > dev_low

    def test_thermal_blur_smooths_gradients(self):
        """Test that thermal blur reduces maximum gradient magnitude."""
        # Create map with sharp gradients
        energy_map = np.zeros((128, 128))
        energy_map[:, :64] = 1.0
        energy_map[:, 64:] = 2.0

        # Compute max gradient before
        grad_x_before = np.gradient(energy_map, axis=1)
        grad_y_before = np.gradient(energy_map, axis=0)
        grad_mag_before = np.sqrt(grad_x_before**2 + grad_y_before**2)
        max_grad_before = np.max(grad_mag_before)

        # Apply blur to smooth
        blurred = apply_thermal_blur(energy_map, sigma=5.0)

        # Compute max gradient after
        grad_x_after = np.gradient(blurred, axis=1)
        grad_y_after = np.gradient(blurred, axis=0)
        grad_mag_after = np.sqrt(grad_x_after**2 + grad_y_after**2)
        max_grad_after = np.max(grad_mag_after)

        # Blur should reduce maximum gradient (smoothing)
        assert max_grad_after < max_grad_before
        # Should reduce by at least 50%
        assert max_grad_after < max_grad_before * 0.5

    def test_translation_shifts_correctly(self):
        """Test that translation shifts map correctly."""
        # Create map with feature at known location
        energy_map = np.zeros((64, 64))
        energy_map[20, 20] = 10.0

        # Translate by (5, 5)
        translated = apply_translation(energy_map, shift_x=5, shift_y=5)

        # Feature should now be at (25, 25)
        assert translated[25, 25] == pytest.approx(10.0, rel=0.01)


class TestSequenceGeneration:
    """Test time series sequence generation."""

    def test_generate_sequence_shape(self, sample_energy_map):
        """Test that generated sequence has correct shape."""
        n_steps = 10
        sequence, _ = generate_sequence(sample_energy_map, n_steps=n_steps)

        assert sequence.shape[0] == n_steps
        assert sequence.shape[1:] == sample_energy_map.shape

    def test_generate_sequence_metadata(self, sample_energy_map):
        """Test that metadata is generated correctly."""
        n_steps = 5
        sequence, metadata = generate_sequence(
            sample_energy_map,
            n_steps=n_steps,
            return_metadata=True
        )

        assert len(metadata) == n_steps
        assert all('energy_mean' in m for m in metadata)
        assert all('entropy' in m for m in metadata)
        assert all('step' in m for m in metadata)

    def test_sequence_energy_conservation(self, sample_energy_map):
        """Test that energy is conserved throughout sequence."""
        sequence, metadata = generate_sequence(
            sample_energy_map,
            n_steps=10,
            return_metadata=True
        )

        # Check conservation at each step
        for m in metadata:
            error = m.get('energy_conservation_error', 0.0)
            assert error < ENERGY_CONSERVATION_TOLERANCE, (
                f"Energy conservation violated at step {m['step']}: error = {error:.4f}"
            )

    def test_sequence_with_all_perturbations(self, sample_energy_map):
        """Test sequence with all perturbations enabled."""
        config = PerturbationConfig(
            enable_rotation=True,
            enable_noise=True,
            enable_thermal_blur=True,
            enable_translation=True,
            enable_scaling=False  # Don't scale to preserve energy exactly
        )

        sequence, metadata = generate_sequence(
            sample_energy_map,
            n_steps=5,
            config=config,
            return_metadata=True
        )

        # Check that perturbations were applied
        for m in metadata[1:]:  # Skip first step (no perturbations)
            assert len(m['perturbations']) > 0

    def test_sequence_with_no_perturbations(self, sample_energy_map):
        """Test sequence with no perturbations (should be constant)."""
        config = PerturbationConfig(
            enable_rotation=False,
            enable_noise=False,
            enable_thermal_blur=False,
            enable_translation=False,
            enable_scaling=False
        )

        sequence, _ = generate_sequence(
            sample_energy_map,
            n_steps=5,
            config=config
        )

        # All frames should be identical
        for t in range(1, sequence.shape[0]):
            np.testing.assert_allclose(sequence[t], sequence[0])


class TestPerturbationConfig:
    """Test perturbation configuration."""

    def test_default_config(self):
        """Test default perturbation configuration."""
        config = PerturbationConfig()

        assert config.enable_rotation is True
        assert config.enable_noise is True
        assert config.enable_thermal_blur is True
        assert config.noise_sigma > 0

    def test_custom_config(self):
        """Test custom perturbation configuration."""
        config = PerturbationConfig(
            rotation_range=(0, 90),
            noise_sigma=0.05,
            thermal_blur_sigma=1.0,
            enable_rotation=False
        )

        assert config.rotation_range == (0, 90)
        assert config.noise_sigma == 0.05
        assert config.thermal_blur_sigma == 1.0
        assert config.enable_rotation is False


class TestPhysicalValidity:
    """Test physical validity of generated data."""

    def test_no_negative_energies(self, sample_energy_map):
        """Test that generated sequences contain no negative energies."""
        sequence, _ = generate_sequence(sample_energy_map, n_steps=10)

        assert np.all(sequence >= 0), "Negative energies detected"

    def test_no_infinite_values(self, sample_energy_map):
        """Test that sequences contain no infinite values."""
        sequence, _ = generate_sequence(sample_energy_map, n_steps=10)

        assert np.isfinite(sequence).all(), "Infinite values detected"

    def test_energy_bounded(self, sample_energy_map):
        """Test that energy values remain bounded."""
        sequence, _ = generate_sequence(sample_energy_map, n_steps=10)

        max_energy = np.max(sequence)
        min_energy = np.min(sequence)

        # Energy shouldn't explode
        assert max_energy < 1000.0, f"Energy too high: {max_energy}"
        assert min_energy >= 0, f"Negative energy: {min_energy}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
