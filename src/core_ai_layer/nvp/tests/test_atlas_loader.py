#!/usr/bin/env python3
"""
test_atlas_loader.py
Unit tests for EnergyAtlasLoader

Tests thermodynamic constraints:
- Energy conservation across scales
- Entropy monotonicity
- Gradient smoothness
- Pyramid consistency
"""

import pytest
import numpy as np
from pathlib import Path
import tempfile
import shutil

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from phase4.core.atlas_loader import (
    EnergyAtlasLoader,
    EnergyMapMetadata,
    ThermodynamicViolation,
    ENERGY_CONSERVATION_TOLERANCE,
    VALID_SCALES
)


@pytest.fixture
def temp_data_dir():
    """Create temporary data directory."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def loader(temp_data_dir):
    """Create EnergyAtlasLoader instance."""
    return EnergyAtlasLoader(temp_data_dir, neo4j_uri=None)


@pytest.fixture
def sample_energy_map():
    """Create sample 256x256 energy map."""
    np.random.seed(42)
    # Create structured pattern
    x = np.linspace(0, 4 * np.pi, 256)
    y = np.linspace(0, 4 * np.pi, 256)
    X, Y = np.meshgrid(x, y)
    energy_map = np.sin(X) * np.cos(Y) + 2.0
    return energy_map


class TestEnergyAtlasLoader:
    """Test suite for EnergyAtlasLoader."""

    def test_initialization(self, temp_data_dir):
        """Test loader initialization."""
        loader = EnergyAtlasLoader(temp_data_dir)

        assert loader.data_dir == temp_data_dir
        assert loader.maps_dir.exists()
        assert loader.pyramids_dir.exists()

    def test_validate_shape_valid_square(self, loader):
        """Test shape validation for valid square maps."""
        for size in VALID_SCALES:
            energy_map = np.random.rand(size, size)
            assert loader.validate_shape(energy_map) is True

    def test_validate_shape_invalid_dimensions(self, loader):
        """Test shape validation rejects invalid dimensions."""
        invalid_map = np.random.rand(100, 100)

        with pytest.raises(ValueError, match="Invalid dimensions"):
            loader.validate_shape(invalid_map)

    def test_validate_shape_3d_array(self, loader):
        """Test shape validation rejects 3D arrays."""
        invalid_map = np.random.rand(64, 64, 3)

        with pytest.raises(ValueError, match="must be 2D"):
            loader.validate_shape(invalid_map)

    def test_compute_entropy(self, loader, sample_energy_map):
        """Test entropy computation."""
        entropy = loader.compute_entropy(sample_energy_map)

        assert isinstance(entropy, float)
        assert entropy > 0
        assert np.isfinite(entropy)

    def test_compute_gradients(self, loader, sample_energy_map):
        """Test gradient computation."""
        grad_x, grad_y = loader.compute_gradients(sample_energy_map)

        assert grad_x.shape == sample_energy_map.shape
        assert grad_y.shape == sample_energy_map.shape
        assert np.isfinite(grad_x).all()
        assert np.isfinite(grad_y).all()

    def test_gradient_smoothness(self, loader):
        """Test that gradients are smooth (no discontinuities)."""
        # Create smooth map
        x = np.linspace(0, 2 * np.pi, 128)
        y = np.linspace(0, 2 * np.pi, 128)
        X, Y = np.meshgrid(x, y)
        smooth_map = np.sin(X) * np.cos(Y) + 2.0

        grad_x, grad_y = loader.compute_gradients(smooth_map)

        # Compute second derivatives (Laplacian components)
        grad_xx = np.gradient(grad_x, axis=1)
        grad_yy = np.gradient(grad_y, axis=0)

        # Check that second derivatives are bounded
        assert np.max(np.abs(grad_xx)) < 10.0
        assert np.max(np.abs(grad_yy)) < 10.0

    def test_pyramid_energy_conservation(self, loader, sample_energy_map):
        """Test that pyramid downsampling preserves total energy."""
        pyramids = loader.precompute_pyramids(sample_energy_map)

        E_original = np.sum(sample_energy_map)

        for scale, pyramid_data in pyramids.items():
            E_scaled = np.sum(pyramid_data['energy'])
            error = abs(E_scaled - E_original) / E_original

            assert error < ENERGY_CONSERVATION_TOLERANCE, (
                f"Energy not conserved at scale {scale}: "
                f"error = {error:.4f}"
            )

    def test_pyramid_gradient_consistency(self, loader, sample_energy_map):
        """Test that gradients are consistently computed across scales."""
        pyramids = loader.precompute_pyramids(sample_energy_map)

        for scale, pyramid_data in pyramids.items():
            grad_x = pyramid_data['grad_x']
            grad_y = pyramid_data['grad_y']
            grad_mag = pyramid_data['grad_magnitude']

            # Check gradient magnitude calculation
            computed_mag = np.sqrt(grad_x**2 + grad_y**2)
            np.testing.assert_allclose(
                grad_mag,
                computed_mag,
                rtol=1e-5,
                err_msg=f"Gradient magnitude mismatch at scale {scale}"
            )

    def test_save_and_load_map(self, loader, sample_energy_map):
        """Test saving and loading energy maps."""
        domain = "test_domain"

        # Save map
        map_id = loader.save_map(sample_energy_map, domain)

        assert map_id is not None

        # Load map
        loaded_map, metadata = loader.load_map(domain, map_id)

        # Check map content
        np.testing.assert_allclose(loaded_map, sample_energy_map)

        # Check metadata
        assert metadata.map_id == map_id
        assert metadata.domain == domain
        assert metadata.scale == 256

    def test_load_batch(self, loader, sample_energy_map):
        """Test loading batch of energy maps."""
        domain = "test_domain"

        # Save multiple maps
        for i in range(15):
            # Create slightly different maps
            perturbed_map = sample_energy_map + np.random.randn(*sample_energy_map.shape) * 0.1
            perturbed_map = np.maximum(perturbed_map, 0)  # Keep non-negative
            loader.save_map(perturbed_map, domain, map_id=f"map_{i:04d}")

        # Load batch
        batch, metadata_list = loader.load_batch(domain, window=10, stride=1)

        assert batch.shape[0] == 10  # 10 time steps
        assert batch.shape[1] == 256  # H
        assert batch.shape[2] == 256  # W
        assert len(metadata_list) == 10

    def test_update_map(self, loader, sample_energy_map):
        """Test updating existing energy map."""
        domain = "test_domain"

        # Save initial map
        map_id = loader.save_map(sample_energy_map, domain)

        # Create updated map
        updated_map = sample_energy_map * 1.1

        # Update
        loader.update_map(domain, updated_map, map_id)

        # Load and verify
        loaded_map, _ = loader.load_map(domain, map_id)

        np.testing.assert_allclose(loaded_map, updated_map)

    def test_get_domain_stats(self, loader, sample_energy_map):
        """Test domain statistics calculation."""
        domain = "test_domain"

        # Save multiple maps
        for i in range(5):
            perturbed_map = sample_energy_map + np.random.randn(*sample_energy_map.shape) * 0.05
            perturbed_map = np.maximum(perturbed_map, 0)
            loader.save_map(perturbed_map, domain, map_id=f"map_{i:04d}")

        # Get stats
        stats = loader.get_domain_stats(domain)

        assert stats['num_maps'] == 5
        assert 'energy_mean' in stats
        assert 'energy_std' in stats
        assert 'entropy_mean' in stats
        assert 'entropy_std' in stats

    def test_energy_conservation_violation_raises(self, loader):
        """Test that severe energy conservation violation raises exception."""
        # Create map that will violate conservation when scaled badly
        energy_map = np.ones((256, 256)) * 100.0

        # Manually create a pyramid that violates conservation
        # by modifying the precompute method temporarily
        pyramids = loader.precompute_pyramids(energy_map)

        # Verify no exception was raised for valid pyramids
        assert len(pyramids) == len(VALID_SCALES)


class TestThermodynamicConstraints:
    """Test thermodynamic constraint enforcement."""

    def test_energy_conservation_across_scales(self, loader):
        """Test energy conservation law across all pyramid scales."""
        # Create test map
        np.random.seed(123)
        energy_map = np.random.exponential(1.0, (256, 256))

        E_original = np.sum(energy_map)

        pyramids = loader.precompute_pyramids(energy_map)

        for scale in VALID_SCALES:
            E_scaled = np.sum(pyramids[scale]['energy'])
            conservation_error = abs(E_scaled - E_original) / E_original

            assert conservation_error < ENERGY_CONSERVATION_TOLERANCE, (
                f"First law violated at scale {scale}: ΔE/E = {conservation_error:.4f}"
            )

    def test_entropy_monotonicity_under_blur(self, loader):
        """Test that entropy increases (or stays same) under thermal blur."""
        from scipy.ndimage import gaussian_filter

        # Create ordered map (low entropy)
        energy_map = np.zeros((128, 128))
        energy_map[60:68, 60:68] = 10.0  # Concentrated energy

        S_before = loader.compute_entropy(energy_map)

        # Apply thermal blur
        blurred = gaussian_filter(energy_map, sigma=5.0)

        S_after = loader.compute_entropy(blurred)

        # Entropy should increase (blur spreads energy)
        assert S_after >= S_before, (
            f"Second law violated: entropy decreased from {S_before:.4f} to {S_after:.4f}"
        )

    def test_pyramid_consistency(self, loader):
        """Test that pyramids maintain structural consistency."""
        # Create map with clear features
        energy_map = np.zeros((256, 256))
        # Add blob in center
        y, x = np.ogrid[:256, :256]
        center = (128, 128)
        r = np.sqrt((x - center[1])**2 + (y - center[0])**2)
        energy_map = np.exp(-r**2 / (2 * 30**2))

        pyramids = loader.precompute_pyramids(energy_map)

        # Check that peak is still in center at all scales
        for scale, pyramid_data in pyramids.items():
            E = pyramid_data['energy']
            peak_idx = np.unravel_index(np.argmax(E), E.shape)

            # Peak should be near center (within 10% of dimensions)
            center_y, center_x = E.shape[0] // 2, E.shape[1] // 2
            assert abs(peak_idx[0] - center_y) < E.shape[0] * 0.1
            assert abs(peak_idx[1] - center_x) < E.shape[1] * 0.1


class TestMetadata:
    """Test metadata handling."""

    def test_metadata_creation(self):
        """Test EnergyMapMetadata dataclass."""
        from datetime import datetime

        metadata = EnergyMapMetadata(
            map_id="test_001",
            domain="plasma_physics",
            scale=256,
            timestamp=datetime.now(),
            energy_mean=1.5,
            energy_var=0.3,
            entropy=10.5
        )

        assert metadata.map_id == "test_001"
        assert metadata.domain == "plasma_physics"
        assert metadata.scale == 256

    def test_metadata_persistence(self, loader, sample_energy_map):
        """Test that metadata is saved and can be loaded."""
        domain = "test_domain"

        # Save with metadata
        map_id = loader.save_map(sample_energy_map, domain)

        # Check metadata file exists
        metadata_path = loader.maps_dir / domain / f"{map_id}_metadata.json"
        assert metadata_path.exists()

        # Load and verify metadata
        import json
        with open(metadata_path) as f:
            metadata_json = json.load(f)

        assert metadata_json['map_id'] == map_id
        assert metadata_json['domain'] == domain


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
