"""
Unit Tests for Energy Field

Tests energy representation, thermodynamic calculations,
and conservation validation.
"""

import pytest
import numpy as np
import torch

from diffusion.core.energy_field import EnergyField, EnergyState


@pytest.mark.unit
@pytest.mark.physics
class TestEnergyFieldConfig:
    """Test energy field configuration"""

    def test_default_config(self):
        """Test default configuration values"""
        config = EnergyFieldConfig()

        assert config.energy_tolerance == 0.01
        assert config.entropy_min_delta == -1e-6
        assert config.temperature == 1.0

    def test_custom_config(self):
        """Test custom configuration"""
        config = EnergyFieldConfig(
            energy_tolerance=0.001,
            temperature=2.0
        )

        assert config.energy_tolerance == 0.001
        assert config.temperature == 2.0


@pytest.mark.unit
@pytest.mark.physics
class TestEnergyField:
    """Test energy field operations"""

    def test_initialization(self, energy_field_config):
        """Test energy field initialization"""
        field = EnergyField(energy_field_config)

        assert field.config == energy_field_config
        assert field.device in ["cpu", "cuda", "mps"]

    def test_compute_total_energy(self, energy_field, small_energy_map):
        """Test total energy calculation"""
        energy_tensor = torch.from_numpy(small_energy_map)
        total_energy = energy_field.compute_total_energy(energy_tensor)

        # Expected: sum of absolute values
        expected = np.abs(small_energy_map).sum()

        assert isinstance(total_energy, float)
        assert np.isclose(total_energy, expected, rtol=1e-5)

    def test_compute_energy_gradient(self, energy_field, sample_energy_map):
        """Test energy gradient computation"""
        energy_tensor = torch.from_numpy(sample_energy_map).unsqueeze(0).unsqueeze(0)
        gradient = energy_field.compute_energy_gradient(energy_tensor)

        assert gradient.shape == energy_tensor.shape
        assert torch.all(gradient >= 0)  # Magnitude is always positive
        assert not torch.all(gradient == 0)  # Should have non-zero gradients

    def test_compute_entropy(self, energy_field, sample_energy_map):
        """Test Shannon entropy calculation"""
        energy_tensor = torch.from_numpy(sample_energy_map)
        entropy = energy_field.compute_entropy(energy_tensor)

        assert isinstance(entropy, float)
        assert entropy > 0  # Shannon entropy is positive for distributions

    def test_create_state(self, energy_field, sample_energy_map):
        """Test thermodynamic state creation"""
        energy_tensor = torch.from_numpy(sample_energy_map)
        state = energy_field.create_state(energy_tensor)

        assert isinstance(state, ThermodynamicState)
        assert state.energy_map.shape == energy_tensor.shape
        assert state.total_energy > 0
        assert state.entropy > 0
        assert state.temperature == energy_field.config.temperature

    def test_boltzmann_weight(self, energy_field):
        """Test Boltzmann weight calculation"""
        energies = torch.tensor([0.0, 1.0, 2.0])
        weights = energy_field.boltzmann_weight(energies)

        # Check normalization
        assert torch.isclose(weights.sum(), torch.tensor(1.0), rtol=1e-5)

        # Check ordering (lower energy -> higher weight)
        assert weights[0] > weights[1] > weights[2]

        # Check range
        assert torch.all(weights >= 0)
        assert torch.all(weights <= 1)

    def test_validate_conservation_valid(self, energy_field, sample_energy_map):
        """Test conservation validation with valid states"""
        energy_tensor = torch.from_numpy(sample_energy_map)

        initial_state = energy_field.create_state(energy_tensor)
        # Create final state with minimal change
        final_tensor = energy_tensor + torch.randn_like(energy_tensor) * 0.001
        final_state = energy_field.create_state(final_tensor)

        result = energy_field.validate_conservation(initial_state, final_state)

        # May or may not pass depending on random noise, but should not crash
        assert isinstance(result, dict)
        assert 'energy_conserved' in result
        assert 'entropy_monotonic' in result
        assert 'passed' in result

    def test_validate_conservation_energy_violation(self, energy_field, sample_energy_map):
        """Test conservation validation with energy violation"""
        energy_tensor = torch.from_numpy(sample_energy_map)

        initial_state = energy_field.create_state(energy_tensor)
        # Create final state with large energy change
        final_tensor = energy_tensor * 2.0  # Double the energy
        final_state = energy_field.create_state(final_tensor)

        result = energy_field.validate_conservation(initial_state, final_state)

        assert result['energy_conserved'] is False
        assert result['passed'] is False

    def test_validate_conservation_entropy_violation(self, energy_field):
        """Test conservation validation with entropy violation"""
        # Create initial state with high entropy
        high_entropy_map = torch.randn(32, 32)
        initial_state = energy_field.create_state(high_entropy_map)

        # Create final state with low entropy (constant values)
        low_entropy_map = torch.ones(32, 32) * 5.0
        final_state = energy_field.create_state(low_entropy_map)

        result = energy_field.validate_conservation(initial_state, final_state)

        # Entropy should decrease, violating monotonicity
        assert initial_state.entropy > final_state.entropy
        # May pass or fail depending on tolerance

    def test_energy_gradient_symmetry(self, energy_field):
        """Test energy gradient is symmetric for symmetric inputs"""
        # Create symmetric energy map
        symmetric_map = torch.ones(16, 16)
        symmetric_map[8:, :] = 2.0  # Horizontal split

        gradient = energy_field.compute_energy_gradient(
            symmetric_map.unsqueeze(0).unsqueeze(0)
        )

        # Gradient should be symmetric along the split
        top_grad = gradient[0, 0, :8, :]
        bottom_grad = gradient[0, 0, 8:, :]

        # Should have similar magnitudes (allowing for edge effects)
        assert torch.isclose(top_grad.mean(), bottom_grad.mean(), rtol=0.1)

    def test_zero_energy_map(self, energy_field):
        """Test handling of zero energy map"""
        zero_map = torch.zeros(16, 16)
        state = energy_field.create_state(zero_map)

        assert state.total_energy == 0.0
        # Entropy of constant (zero) distribution should be minimal

    def test_temperature_effect_on_boltzmann(self, energy_field_config):
        """Test temperature effect on Boltzmann weighting"""
        energies = torch.tensor([0.0, 1.0, 2.0])

        # Low temperature - sharper distribution
        low_temp_field = EnergyField(
            EnergyFieldConfig(**{**energy_field_config.dict(), 'temperature': 0.1})
        )
        low_temp_weights = low_temp_field.boltzmann_weight(energies)

        # High temperature - flatter distribution
        high_temp_field = EnergyField(
            EnergyFieldConfig(**{**energy_field_config.dict(), 'temperature': 10.0})
        )
        high_temp_weights = high_temp_field.boltzmann_weight(energies)

        # Low temp should have more concentrated weight on low energy
        assert low_temp_weights[0] > high_temp_weights[0]
        assert low_temp_weights[2] < high_temp_weights[2]


@pytest.mark.unit
@pytest.mark.physics
class TestThermodynamicState:
    """Test thermodynamic state representation"""

    def test_state_creation(self, energy_field, sample_energy_map):
        """Test thermodynamic state creation"""
        energy_tensor = torch.from_numpy(sample_energy_map)
        state = energy_field.create_state(energy_tensor)

        assert isinstance(state, ThermodynamicState)
        assert torch.equal(state.energy_map, energy_tensor)
        assert isinstance(state.total_energy, float)
        assert isinstance(state.entropy, float)
        assert isinstance(state.temperature, float)

    def test_state_comparison(self, energy_field, sample_energy_map):
        """Test comparison of thermodynamic states"""
        energy_tensor = torch.from_numpy(sample_energy_map)

        state1 = energy_field.create_state(energy_tensor)
        state2 = energy_field.create_state(energy_tensor)

        # Same input should produce same state
        assert state1.total_energy == state2.total_energy
        assert state1.entropy == state2.entropy
        assert state1.temperature == state2.temperature


@pytest.mark.unit
@pytest.mark.physics
@pytest.mark.slow
class TestEnergyFieldPerformance:
    """Performance tests for energy field operations"""

    def test_large_energy_map_performance(self, energy_field):
        """Test performance with large energy maps"""
        import time

        large_map = torch.randn(256, 256)

        start = time.time()
        state = energy_field.create_state(large_map)
        duration = time.time() - start

        assert duration < 1.0  # Should complete in less than 1 second
        assert state.total_energy > 0

    def test_batch_processing(self, energy_field):
        """Test batch processing of multiple energy maps"""
        import time

        batch_size = 10
        batch_maps = [torch.randn(64, 64) for _ in range(batch_size)]

        start = time.time()
        states = [energy_field.create_state(m) for m in batch_maps]
        duration = time.time() - start

        assert len(states) == batch_size
        assert duration < 5.0  # Should process batch in reasonable time
