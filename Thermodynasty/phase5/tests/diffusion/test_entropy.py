"""
Tests for entropy metrics and thermodynamic validation
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from phase5.diffusion.core.entropy_metrics import (
    EntropyValidator,
    BoltzmannMetrics,
    ThermodynamicMetrics,
    compute_energy_landscape_metrics
)


class TestEntropyValidator:
    """Test entropy validator"""

    @pytest.fixture
    def validator(self):
        """Create entropy validator"""
        return EntropyValidator(
            energy_tolerance=0.01,
            entropy_threshold=-1e-6,
            spectral_threshold=0.85,
            temperature=1.0
        )

    def test_initialization(self, validator):
        """Test validator initializes correctly"""
        assert validator.energy_tolerance == 0.01
        assert validator.entropy_threshold == -1e-6
        assert validator.spectral_threshold == 0.85
        assert validator.temperature == 1.0

    def test_energy_conservation_pass(self, validator):
        """Test energy conservation validation passes"""
        # Create states with conserved energy
        initial = torch.randn(64, 64)
        final = initial * 1.001  # 0.1% change (within tolerance)

        metrics = validator.validate_transition(initial, final)

        assert isinstance(metrics, ThermodynamicMetrics)
        assert metrics.energy_conserved is True

    def test_energy_conservation_fail(self, validator):
        """Test energy conservation validation fails"""
        # Create states with non-conserved energy
        initial = torch.randn(64, 64)
        final = initial * 2.0  # 100% change (exceeds tolerance)

        metrics = validator.validate_transition(initial, final)

        assert metrics.energy_conserved is False
        assert not metrics.passed

    def test_entropy_monotonicity_pass(self, validator):
        """Test entropy monotonicity validation passes"""
        # Create states with increasing entropy
        initial = torch.ones(64, 64) * 0.5  # Low entropy (uniform)
        final = torch.randn(64, 64)  # Higher entropy (random)

        metrics = validator.validate_transition(initial, final)

        # Entropy should increase
        assert metrics.entropy_change >= validator.entropy_threshold

    def test_single_state_validation(self, validator):
        """Test validating a single state"""
        state = torch.randn(64, 64)

        metrics = validator.validate_single_state(state)

        assert isinstance(metrics, ThermodynamicMetrics)
        assert hasattr(metrics, 'energy_drift')
        assert hasattr(metrics, 'entropy_change')

    def test_spectral_validation(self, validator):
        """Test spectral validation"""
        # Create smooth state (should pass)
        x = torch.linspace(-1, 1, 64)
        y = torch.linspace(-1, 1, 64)
        X, Y = torch.meshgrid(x, y, indexing='ij')
        smooth_state = torch.exp(-(X**2 + Y**2))

        metrics = validator.validate_single_state(smooth_state)

        # Smooth state should pass spectral validation
        assert metrics.spectral_valid is True


class TestBoltzmannMetrics:
    """Test Boltzmann metrics computation"""

    def test_boltzmann_weight_computation(self):
        """Test Boltzmann weight calculation"""
        energies = torch.tensor([0.0, 1.0, 2.0, 3.0])
        temperature = 1.0

        # Compute Boltzmann weights: exp(-E/kT)
        weights = torch.exp(-energies / temperature)

        # Weights should decrease with energy
        assert weights[0] > weights[1] > weights[2] > weights[3]

        # Weights should sum to <= number of samples (before normalization)
        assert weights.sum() > 0

    def test_partition_function(self):
        """Test partition function calculation"""
        energies = torch.tensor([0.0, 1.0, 2.0])
        temperature = 1.0

        # Partition function Z = sum(exp(-E/kT))
        Z = torch.exp(-energies / temperature).sum()

        # Z should be positive
        assert Z > 0

        # Z should be >= 1 (for E >= 0)
        assert Z >= 1.0

    def test_free_energy_computation(self):
        """Test free energy calculation"""
        energies = torch.tensor([0.0, 1.0, 2.0, 3.0])
        temperature = 1.0

        # Free energy F = -kT ln(Z)
        Z = torch.exp(-energies / temperature).sum()
        F = -temperature * torch.log(Z)

        # Free energy should be negative (for this case)
        assert F < 0

    def test_boltzmann_sampling(self):
        """Test Boltzmann-weighted sampling"""
        energies = torch.tensor([0.0, 10.0, 20.0])  # Low, medium, high energy
        temperature = 1.0

        # Compute probabilities
        weights = torch.exp(-energies / temperature)
        probs = weights / weights.sum()

        # Lowest energy should have highest probability
        assert probs[0] > probs[1] > probs[2]

        # Probabilities should sum to 1
        assert torch.allclose(probs.sum(), torch.tensor(1.0))


class TestThermodynamicMetrics:
    """Test thermodynamic metrics dataclass"""

    def test_metrics_creation(self):
        """Test creating thermodynamic metrics"""
        metrics = ThermodynamicMetrics(
            energy_drift=0.005,
            energy_conserved=True,
            entropy_change=0.1,
            entropy_monotonic=True,
            spectral_valid=True,
            passed=True
        )

        assert metrics.energy_drift == 0.005
        assert metrics.energy_conserved is True
        assert metrics.entropy_change == 0.1
        assert metrics.passed is True

    def test_failed_validation(self):
        """Test failed validation metrics"""
        metrics = ThermodynamicMetrics(
            energy_drift=0.5,
            energy_conserved=False,
            entropy_change=-0.1,
            entropy_monotonic=False,
            spectral_valid=True,
            passed=False
        )

        assert not metrics.passed
        assert not metrics.energy_conserved
        assert not metrics.entropy_monotonic


class TestEnergyLandscapeMetrics:
    """Test energy landscape analysis"""

    def test_landscape_metrics_computation(self):
        """Test computing energy landscape metrics"""
        # Create simple energy landscape
        x = torch.linspace(-2, 2, 64)
        y = torch.linspace(-2, 2, 64)
        X, Y = torch.meshgrid(x, y, indexing='ij')

        # Quadratic potential with minimum at origin
        energy_landscape = X**2 + Y**2

        metrics = compute_energy_landscape_metrics(energy_landscape)

        assert 'min_energy' in metrics
        assert 'max_energy' in metrics
        assert 'mean_energy' in metrics
        assert 'energy_variance' in metrics

        # Minimum should be at origin (near 0)
        assert metrics['min_energy'] < 0.1

    def test_landscape_with_multiple_minima(self):
        """Test landscape with multiple local minima"""
        x = torch.linspace(-3, 3, 64)
        y = torch.linspace(-3, 3, 64)
        X, Y = torch.meshgrid(x, y, indexing='ij')

        # Double-well potential
        energy_landscape = (X**2 - 1)**2 + Y**2

        metrics = compute_energy_landscape_metrics(energy_landscape)

        # Should have non-zero minimum
        assert metrics['min_energy'] >= 0

        # Variance should be positive
        assert metrics['energy_variance'] > 0


class TestEntropyCalculations:
    """Test entropy calculation methods"""

    def test_shannon_entropy_uniform(self):
        """Test Shannon entropy for uniform distribution"""
        # Uniform distribution has maximum entropy
        uniform = torch.ones(64, 64) / (64 * 64)

        # Compute Shannon entropy: H = -sum(p * log(p))
        entropy = -(uniform * torch.log(uniform + 1e-10)).sum()

        # Should be close to log(N)
        max_entropy = np.log(64 * 64)
        assert abs(entropy.item() - max_entropy) < 0.1

    def test_shannon_entropy_delta(self):
        """Test Shannon entropy for delta distribution"""
        # Delta distribution has minimum entropy
        delta = torch.zeros(64, 64)
        delta[32, 32] = 1.0

        # Compute Shannon entropy
        # Should be 0 for delta function
        nonzero = delta > 0
        if nonzero.any():
            entropy = -(delta[nonzero] * torch.log(delta[nonzero])).sum()
        else:
            entropy = torch.tensor(0.0)

        # Should be very close to 0
        assert entropy.item() < 0.01

    def test_entropy_monotonicity(self):
        """Test that diffusion increases entropy"""
        # Initial concentrated state
        initial = torch.zeros(64, 64)
        initial[30:34, 30:34] = 1.0
        initial = initial / initial.sum()

        # Final diffused state
        final = torch.ones(64, 64) / (64 * 64)

        # Compute entropies
        def compute_entropy(state):
            nonzero = state > 1e-10
            if nonzero.any():
                return -(state[nonzero] * torch.log(state[nonzero])).sum()
            return torch.tensor(0.0)

        entropy_initial = compute_entropy(initial)
        entropy_final = compute_entropy(final)

        # Entropy should increase
        assert entropy_final > entropy_initial


class TestValidationEdgeCases:
    """Test edge cases in validation"""

    def test_zero_state(self):
        """Test validation with zero state"""
        validator = EntropyValidator()

        zero_state = torch.zeros(64, 64)

        # Should not crash
        metrics = validator.validate_single_state(zero_state)

        assert isinstance(metrics, ThermodynamicMetrics)

    def test_negative_energies(self):
        """Test validation with negative energies"""
        validator = EntropyValidator()

        negative_state = -torch.abs(torch.randn(64, 64))

        # Should not crash
        metrics = validator.validate_single_state(negative_state)

        assert isinstance(metrics, ThermodynamicMetrics)

    def test_very_large_energies(self):
        """Test validation with very large energies"""
        validator = EntropyValidator()

        large_state = torch.randn(64, 64) * 1000

        # Should not crash
        metrics = validator.validate_single_state(large_state)

        assert isinstance(metrics, ThermodynamicMetrics)

    def test_identical_states(self):
        """Test validation with identical initial and final states"""
        validator = EntropyValidator()

        state = torch.randn(64, 64)

        metrics = validator.validate_transition(state, state.clone())

        # Energy should be perfectly conserved
        assert metrics.energy_conserved is True
        assert metrics.energy_drift < 1e-6

        # Entropy change should be zero
        assert abs(metrics.entropy_change) < 1e-6


class TestTemperatureDependence:
    """Test temperature dependence of metrics"""

    def test_boltzmann_weight_temperature(self):
        """Test Boltzmann weight depends on temperature"""
        energy = torch.tensor(1.0)

        # High temperature
        weight_high_T = torch.exp(-energy / 10.0)

        # Low temperature
        weight_low_T = torch.exp(-energy / 0.1)

        # Higher temperature should give larger weight
        assert weight_high_T > weight_low_T

    def test_validator_temperature_sensitivity(self):
        """Test validator behavior at different temperatures"""
        high_temp_validator = EntropyValidator(temperature=10.0)
        low_temp_validator = EntropyValidator(temperature=0.1)

        state = torch.randn(64, 64)

        # Both should validate
        metrics_high = high_temp_validator.validate_single_state(state)
        metrics_low = low_temp_validator.validate_single_state(state)

        assert isinstance(metrics_high, ThermodynamicMetrics)
        assert isinstance(metrics_low, ThermodynamicMetrics)
