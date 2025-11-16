"""
Tests for Energy Atlas Service

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from src.core_ai_layer.service_mesh.energy_atlas.energy_atlas_service import (
    EnergyAtlasService,
    EnergyMapMetadata,
    EnergyMapQuery,
    EnergyMapStatus
)


@pytest.fixture
def temp_storage_dir():
    """Create temporary storage directory"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def energy_atlas(temp_storage_dir):
    """Create Energy Atlas Service"""
    return EnergyAtlasService(
        storage_dir=temp_storage_dir,
        metadata_file=temp_storage_dir / "metadata.json"
    )


@pytest.fixture
def sample_energy_map():
    """Create sample energy map"""
    return np.random.rand(128, 128)


def test_energy_atlas_initialization(temp_storage_dir):
    """Test Energy Atlas Service initialization"""
    eas = EnergyAtlasService(storage_dir=temp_storage_dir)
    
    assert eas.storage_dir == temp_storage_dir
    assert eas.storage_dir.exists()
    assert len(eas.registry) == 0


def test_register_energy_map(energy_atlas, sample_energy_map):
    """Test registering an energy map"""
    metadata = energy_atlas.register_energy_map(
        utid="UTID:energy:test:001",
        energy_array=sample_energy_map,
        dataset_name="test_dataset",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    assert metadata.utid == "UTID:energy:test:001"
    assert metadata.dataset_name == "test_dataset"
    assert metadata.shape == sample_energy_map.shape
    assert metadata.formula == "E = 0.5*v^2"
    assert metadata.timestep == 10
    assert metadata.status == "registered"


def test_register_energy_map_creates_file(energy_atlas, sample_energy_map):
    """Test that registering creates storage file"""
    metadata = energy_atlas.register_energy_map(
        utid="UTID:energy:test:002",
        energy_array=sample_energy_map,
        dataset_name="test_dataset",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    storage_path = Path(metadata.storage_path)
    assert storage_path.exists()
    assert storage_path.suffix == ".npz"


def test_register_energy_map_calculates_statistics(energy_atlas, sample_energy_map):
    """Test that statistics are calculated correctly"""
    metadata = energy_atlas.register_energy_map(
        utid="UTID:energy:test:003",
        energy_array=sample_energy_map,
        dataset_name="test_dataset",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    assert metadata.energy_range[0] == pytest.approx(sample_energy_map.min(), rel=1e-6)
    assert metadata.energy_range[1] == pytest.approx(sample_energy_map.max(), rel=1e-6)
    assert metadata.energy_mean == pytest.approx(sample_energy_map.mean(), rel=1e-6)
    assert metadata.energy_std == pytest.approx(sample_energy_map.std(), rel=1e-6)


def test_get_energy_map(energy_atlas, sample_energy_map):
    """Test retrieving an energy map"""
    # Register map
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:004",
        energy_array=sample_energy_map,
        dataset_name="test_dataset",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Retrieve map
    result = energy_atlas.get_energy_map("UTID:energy:test:004")
    
    assert result is not None
    energy_array, metadata = result
    assert np.array_equal(energy_array, sample_energy_map)
    assert metadata.utid == "UTID:energy:test:004"


def test_get_energy_map_not_found(energy_atlas):
    """Test retrieving non-existent energy map"""
    result = energy_atlas.get_energy_map("UTID:energy:nonexistent")
    
    assert result is None


def test_query_energy_maps_by_dataset(energy_atlas, sample_energy_map):
    """Test querying energy maps by dataset name"""
    # Register multiple maps
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:005",
        energy_array=sample_energy_map,
        dataset_name="dataset_a",
        formula="E = 0.5*v^2",
        timestep=10
    )
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:006",
        energy_array=sample_energy_map,
        dataset_name="dataset_b",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Query by dataset
    query = EnergyMapQuery(dataset_name="dataset_a")
    results = energy_atlas.query_energy_maps(query)
    
    assert len(results) == 1
    assert results[0].dataset_name == "dataset_a"


def test_query_energy_maps_by_shape(energy_atlas):
    """Test querying energy maps by shape"""
    # Register maps with different shapes
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:007",
        energy_array=np.random.rand(64, 64),
        dataset_name="small",
        formula="E = 0.5*v^2",
        timestep=10
    )
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:008",
        energy_array=np.random.rand(256, 256),
        dataset_name="large",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Query by minimum shape
    query = EnergyMapQuery(min_shape=(128, 128))
    results = energy_atlas.query_energy_maps(query)
    
    assert len(results) == 1
    assert results[0].dataset_name == "large"


def test_query_energy_maps_by_energy(energy_atlas):
    """Test querying energy maps by energy range"""
    # Register maps with different energy values
    low_energy = np.full((64, 64), 0.1)
    high_energy = np.full((64, 64), 0.9)
    
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:009",
        energy_array=low_energy,
        dataset_name="low",
        formula="E = 0.5*v^2",
        timestep=10
    )
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:010",
        energy_array=high_energy,
        dataset_name="high",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Query by minimum energy
    query = EnergyMapQuery(min_energy=0.5)
    results = energy_atlas.query_energy_maps(query)
    
    assert len(results) == 1
    assert results[0].dataset_name == "high"


def test_query_energy_maps_by_status(energy_atlas, sample_energy_map):
    """Test querying energy maps by status"""
    # Register and validate one map
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:011",
        energy_array=sample_energy_map,
        dataset_name="validated",
        formula="E = 0.5*v^2",
        timestep=10
    )
    energy_atlas.validate_energy_map("UTID:energy:test:011")
    
    # Register another without validation
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:012",
        energy_array=sample_energy_map,
        dataset_name="not_validated",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Query by status
    query = EnergyMapQuery(status="validated")
    results = energy_atlas.query_energy_maps(query)
    
    assert len(results) == 1
    assert results[0].status == "validated"


def test_query_energy_maps_limit(energy_atlas, sample_energy_map):
    """Test query result limit"""
    # Register multiple maps
    for i in range(10):
        energy_atlas.register_energy_map(
            utid=f"UTID:energy:test:{i+100}",
            energy_array=sample_energy_map,
            dataset_name="test",
            formula="E = 0.5*v^2",
            timestep=10
        )
    
    # Query with limit
    query = EnergyMapQuery(dataset_name="test", limit=5)
    results = energy_atlas.query_energy_maps(query)
    
    assert len(results) == 5


def test_validate_energy_map(energy_atlas, sample_energy_map):
    """Test validating an energy map"""
    # Register map
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:013",
        energy_array=sample_energy_map,
        dataset_name="test",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Validate
    success = energy_atlas.validate_energy_map("UTID:energy:test:013")
    
    assert success
    metadata = energy_atlas.registry["UTID:energy:test:013"]
    assert metadata.status == "validated"
    assert metadata.validated_at is not None


def test_validate_energy_map_invalid(energy_atlas):
    """Test validating non-existent energy map"""
    success = energy_atlas.validate_energy_map("UTID:energy:nonexistent")
    
    assert not success


def test_validate_energy_map_with_nan(energy_atlas):
    """Test validating energy map with NaN values"""
    # Create map with NaN
    invalid_map = np.random.rand(64, 64)
    invalid_map[0, 0] = np.nan
    
    # Register map
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:014",
        energy_array=invalid_map,
        dataset_name="invalid",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Validate should fail
    success = energy_atlas.validate_energy_map("UTID:energy:test:014")
    
    assert not success
    metadata = energy_atlas.registry["UTID:energy:test:014"]
    assert metadata.status == "failed"


def test_archive_energy_map(energy_atlas, sample_energy_map):
    """Test archiving an energy map"""
    # Register map
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:015",
        energy_array=sample_energy_map,
        dataset_name="test",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Archive
    success = energy_atlas.archive_energy_map("UTID:energy:test:015")
    
    assert success
    metadata = energy_atlas.registry["UTID:energy:test:015"]
    assert metadata.status == "archived"


def test_delete_energy_map(energy_atlas, sample_energy_map):
    """Test deleting an energy map"""
    # Register map
    metadata = energy_atlas.register_energy_map(
        utid="UTID:energy:test:016",
        energy_array=sample_energy_map,
        dataset_name="test",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    storage_path = Path(metadata.storage_path)
    assert storage_path.exists()
    
    # Delete
    success = energy_atlas.delete_energy_map("UTID:energy:test:016")
    
    assert success
    assert "UTID:energy:test:016" not in energy_atlas.registry
    assert not storage_path.exists()


def test_event_handler_registration(energy_atlas):
    """Test event handler registration"""
    events_received = []
    
    def handler(event_data):
        events_received.append(event_data)
    
    energy_atlas.register_event_handler("energy_map.created", handler)
    
    # Register a map to trigger event
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:017",
        energy_array=np.random.rand(64, 64),
        dataset_name="test",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    assert len(events_received) == 1
    assert events_received[0]["utid"] == "UTID:energy:test:017"


def test_get_statistics(energy_atlas, sample_energy_map):
    """Test getting energy atlas statistics"""
    # Register multiple maps
    for i in range(5):
        energy_atlas.register_energy_map(
            utid=f"UTID:energy:test:{i+200}",
            energy_array=sample_energy_map,
            dataset_name="test",
            formula="E = 0.5*v^2",
            timestep=10
        )
    
    stats = energy_atlas.get_statistics()
    
    assert stats["total_maps"] == 5
    assert stats["total_size"] > 0
    assert stats["avg_size"] > 0
    assert "status_counts" in stats


def test_get_dataset_statistics(energy_atlas, sample_energy_map):
    """Test getting dataset statistics"""
    # Register maps from different datasets
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:018",
        energy_array=sample_energy_map,
        dataset_name="dataset_a",
        formula="E = 0.5*v^2",
        timestep=10
    )
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:019",
        energy_array=sample_energy_map,
        dataset_name="dataset_a",
        formula="E = 0.5*v^2",
        timestep=10
    )
    energy_atlas.register_energy_map(
        utid="UTID:energy:test:020",
        energy_array=sample_energy_map,
        dataset_name="dataset_b",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    stats = energy_atlas.get_dataset_statistics()
    
    assert "dataset_a" in stats
    assert "dataset_b" in stats
    assert stats["dataset_a"]["count"] == 2
    assert stats["dataset_b"]["count"] == 1


def test_registry_persistence(temp_storage_dir, sample_energy_map):
    """Test that registry persists across instances"""
    # Create first instance and register map
    eas1 = EnergyAtlasService(storage_dir=temp_storage_dir)
    eas1.register_energy_map(
        utid="UTID:energy:test:021",
        energy_array=sample_energy_map,
        dataset_name="test",
        formula="E = 0.5*v^2",
        timestep=10
    )
    
    # Create second instance
    eas2 = EnergyAtlasService(storage_dir=temp_storage_dir)
    
    # Should load existing registry
    assert "UTID:energy:test:021" in eas2.registry


def test_register_with_metadata(energy_atlas, sample_energy_map):
    """Test registering with additional metadata"""
    metadata_dict = {
        "author": "test_user",
        "description": "Test energy map",
        "tags": ["test", "sample"]
    }
    
    map_metadata = energy_atlas.register_energy_map(
        utid="UTID:energy:test:022",
        energy_array=sample_energy_map,
        dataset_name="test",
        formula="E = 0.5*v^2",
        timestep=10,
        metadata=metadata_dict
    )
    
    assert map_metadata.metadata == metadata_dict
