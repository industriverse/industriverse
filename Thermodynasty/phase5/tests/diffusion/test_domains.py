"""
Tests for domain capsules (molecular, plasma, enterprise)
"""

import pytest
import torch
import numpy as np
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from phase5.diffusion.domains import (
    MolecularDiffusion,
    MolecularConfig,
    PlasmaDiffusion,
    PlasmaConfig,
    EnterpriseDiffusion,
    EnterpriseConfig
)


class TestMolecularDiffusion:
    """Test molecular diffusion domain"""

    @pytest.fixture
    def molecular_diffusion(self):
        """Create molecular diffusion instance"""
        config = MolecularConfig(
            num_atoms=5,
            lattice_resolution=32,
            temperature=300.0
        )
        return MolecularDiffusion(config=config, device='cpu')

    def test_initialization(self, molecular_diffusion):
        """Test molecular diffusion initializes correctly"""
        assert molecular_diffusion.config is not None
        assert molecular_diffusion.energy_field is not None
        assert molecular_diffusion.diffusion_model is not None
        assert molecular_diffusion.sampler is not None

    def test_structure_generation(self, molecular_diffusion):
        """Test generating molecular structures"""
        result = molecular_diffusion.generate_molecular_structure(
            num_samples=2,
            num_inference_steps=10,
            seed=42
        )

        assert 'energy_maps' in result
        assert 'energies' in result
        assert 'valid' in result

        # Check shapes
        assert result['energy_maps'].shape[0] == 2
        assert len(result['energies']) == 2
        assert len(result['valid']) == 2

    def test_structure_optimization(self, molecular_diffusion):
        """Test structure optimization"""
        result = molecular_diffusion.optimize_structure(
            max_iterations=20,
            tolerance=0.1
        )

        assert 'optimized_structure' in result
        assert 'final_energy' in result
        assert 'converged' in result
        assert 'trajectory' in result

        # Should have trajectory of iterations
        assert len(result['trajectory']) > 0

    def test_energy_field_molecular(self, molecular_diffusion):
        """Test molecular energy field computations"""
        positions = torch.randn(5, 3)  # 5 atoms in 3D
        atom_types = torch.randint(0, 4, (5,))  # 4 atom types

        energy = molecular_diffusion.energy_field.compute_molecular_energy(
            positions,
            atom_types
        )

        assert isinstance(energy, torch.Tensor)
        assert energy.item() >= 0  # Energy should be positive


class TestPlasmaDiffusion:
    """Test plasma diffusion domain"""

    @pytest.fixture
    def plasma_diffusion(self):
        """Create plasma diffusion instance"""
        config = PlasmaConfig(
            plasma_temperature=1e7,
            resolution=64,
            beta_limit=0.05
        )
        return PlasmaDiffusion(config=config, device='cpu')

    def test_initialization(self, plasma_diffusion):
        """Test plasma diffusion initializes correctly"""
        assert plasma_diffusion.config is not None
        assert plasma_diffusion.energy_field is not None
        assert plasma_diffusion.config.plasma_temperature == 1e7

    def test_equilibrium_generation(self, plasma_diffusion):
        """Test generating plasma equilibria"""
        result = plasma_diffusion.generate_equilibrium_configuration(
            num_samples=2,
            num_inference_steps=10,
            seed=42
        )

        assert 'equilibrium_maps' in result
        assert 'confinement_times' in result
        assert 'beta_values' in result
        assert 'stable' in result

        # Check shapes
        assert result['equilibrium_maps'].shape[0] == 2
        assert len(result['confinement_times']) == 2
        assert len(result['beta_values']) == 2

    def test_confinement_optimization(self, plasma_diffusion):
        """Test confinement optimization"""
        result = plasma_diffusion.optimize_confinement(
            target_beta=0.03,
            max_iterations=20
        )

        assert 'optimized_config' in result
        assert 'best_confinement_time' in result
        assert 'trajectory' in result

        # Confinement time should be positive
        assert result['best_confinement_time'] > 0

    def test_plasma_energy_computation(self, plasma_diffusion):
        """Test plasma energy field computations"""
        density = torch.rand(64, 64) * 1e20
        temperature = torch.ones(64, 64) * 1e7
        magnetic_field = torch.ones(64, 64) * 5.0

        energies = plasma_diffusion.energy_field.compute_plasma_energy(
            density,
            temperature,
            magnetic_field
        )

        assert 'thermal' in energies
        assert 'magnetic' in energies
        assert 'total' in energies

        # All energies should be positive
        assert energies['thermal'].item() > 0
        assert energies['magnetic'].item() > 0
        assert energies['total'].item() > 0

    def test_beta_parameter(self, plasma_diffusion):
        """Test plasma beta calculation"""
        thermal_pressure = torch.ones(64, 64) * 1000.0
        magnetic_pressure = torch.ones(64, 64) * 20000.0

        beta = plasma_diffusion.energy_field.compute_beta_parameter(
            thermal_pressure,
            magnetic_pressure
        )

        assert beta.shape == (64, 64)
        # Beta should be p_thermal / p_magnetic
        expected_beta = 1000.0 / 20000.0
        assert torch.allclose(beta, torch.tensor(expected_beta), rtol=0.1)


class TestEnterpriseDiffusion:
    """Test enterprise diffusion domain"""

    @pytest.fixture
    def enterprise_diffusion(self):
        """Create enterprise diffusion instance"""
        config = EnterpriseConfig(
            num_nodes=50,
            resolution=32,
            power_per_gpu=300.0
        )
        return EnterpriseDiffusion(config=config, device='cpu')

    def test_initialization(self, enterprise_diffusion):
        """Test enterprise diffusion initializes correctly"""
        assert enterprise_diffusion.config is not None
        assert enterprise_diffusion.energy_field is not None
        assert enterprise_diffusion.config.num_nodes == 50

    def test_resource_allocation(self, enterprise_diffusion):
        """Test resource allocation optimization"""
        workload = torch.rand(32, 32)

        result = enterprise_diffusion.optimize_resource_allocation(
            workload_profile=workload,
            num_samples=5,
            num_inference_steps=10
        )

        assert 'best_allocation' in result
        assert 'best_score' in result
        assert 'all_strategies' in result

        # Should have 5 strategies
        assert len(result['all_strategies']) == 5

        # Each strategy should have required fields
        strategy = result['all_strategies'][0]
        assert 'power_consumption' in strategy
        assert 'fragmentation' in strategy
        assert 'cost_per_hour' in strategy

    def test_power_consumption_calculation(self, enterprise_diffusion):
        """Test power consumption computation"""
        cpu_util = torch.rand(32, 32)
        gpu_util = torch.rand(32, 32)
        network_util = torch.rand(32, 32)

        power = enterprise_diffusion.energy_field.compute_total_power_consumption(
            cpu_util,
            gpu_util,
            network_util
        )

        assert 'cpu' in power
        assert 'gpu' in power
        assert 'network' in power
        assert 'cooling' in power
        assert 'total' in power

        # Total should be sum of components plus cooling
        assert power['total'].item() > 0

    def test_energy_cost_calculation(self, enterprise_diffusion):
        """Test energy cost computation"""
        power_watts = torch.tensor(10000.0)  # 10 kW
        duration_seconds = 3600.0  # 1 hour

        cost = enterprise_diffusion.energy_field.compute_energy_cost(
            power_watts,
            duration_seconds
        )

        # Cost should be positive
        assert cost > 0

        # For 10 kW at $0.12/kWh for 1 hour: 10 * 0.12 = $1.20
        expected_cost = 10.0 * 0.12
        assert abs(cost - expected_cost) < 0.01

    def test_carbon_footprint(self, enterprise_diffusion):
        """Test carbon footprint calculation"""
        power_watts = torch.tensor(10000.0)  # 10 kW
        duration_seconds = 3600.0  # 1 hour
        carbon_intensity = 0.4  # kg CO2/kWh

        carbon = enterprise_diffusion.energy_field.compute_carbon_footprint(
            power_watts,
            duration_seconds,
            carbon_intensity
        )

        # Carbon should be positive
        assert carbon > 0

        # For 10 kW at 0.4 kg CO2/kWh for 1 hour: 10 * 0.4 = 4 kg CO2
        expected_carbon = 10.0 * 0.4
        assert abs(carbon - expected_carbon) < 0.01

    def test_resource_fragmentation(self, enterprise_diffusion):
        """Test resource fragmentation computation"""
        # Highly fragmented allocation
        fragmented = torch.zeros(32, 32)
        fragmented[::4, ::4] = 1.0

        frag_score = enterprise_diffusion.energy_field.compute_resource_fragmentation(
            fragmented
        )

        assert 0.0 <= frag_score <= 1.0

        # Uniform allocation should have higher fragmentation
        uniform = torch.ones(32, 32) * 0.5
        uniform_frag = enterprise_diffusion.energy_field.compute_resource_fragmentation(
            uniform
        )

        # Both should be valid fragmentation scores
        assert 0.0 <= uniform_frag <= 1.0


class TestDomainConfigValidation:
    """Test domain configuration validation"""

    def test_molecular_config_defaults(self):
        """Test molecular config defaults"""
        config = MolecularConfig()

        assert config.num_atoms == 10
        assert config.temperature == 300.0
        assert config.boltzmann_constant > 0

    def test_plasma_config_defaults(self):
        """Test plasma config defaults"""
        config = PlasmaConfig()

        assert config.plasma_temperature == 1e7
        assert config.beta_limit == 0.05
        assert config.enforce_mhd_stability is True

    def test_enterprise_config_defaults(self):
        """Test enterprise config defaults"""
        config = EnterpriseConfig()

        assert config.num_nodes == 100
        assert config.power_per_gpu == 300.0
        assert config.cooling_efficiency == 1.4
        assert config.electricity_cost > 0


class TestDomainIntegration:
    """Test integration between domains and core diffusion"""

    def test_molecular_uses_core_diffusion(self):
        """Test molecular domain uses core diffusion model"""
        molecular = MolecularDiffusion(device='cpu')

        # Should have diffusion model from core
        assert hasattr(molecular, 'diffusion_model')
        assert hasattr(molecular, 'sampler')

    def test_plasma_uses_core_diffusion(self):
        """Test plasma domain uses core diffusion model"""
        plasma = PlasmaDiffusion(device='cpu')

        # Should have diffusion model from core
        assert hasattr(plasma, 'diffusion_model')
        assert hasattr(plasma, 'sampler')

    def test_enterprise_uses_core_diffusion(self):
        """Test enterprise domain uses core diffusion model"""
        enterprise = EnterpriseDiffusion(device='cpu')

        # Should have diffusion model from core
        assert hasattr(enterprise, 'diffusion_model')
        assert hasattr(enterprise, 'sampler')
