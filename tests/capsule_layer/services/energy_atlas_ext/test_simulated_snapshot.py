"""
Tests for SimulatedSnapshot Service
"""

import pytest
import numpy as np
from src.capsule_layer.services.energy_atlas_ext.simulated_snapshot_service import (
    create_simulated_snapshot_service,
    SnapshotType
)

@pytest.mark.asyncio
async def test_simulated_snapshot_creation():
    """Test simulated snapshot service creation"""
    service = create_simulated_snapshot_service()
    assert service is not None
    assert service.total_snapshots == 0

@pytest.mark.asyncio
async def test_register_simulator():
    """Test simulator registration"""
    service = create_simulated_snapshot_service()
    
    simulator_id = service.register_simulator(
        simulator_type="world_model",
        version="1.0.0",
        domain="lithography",
        physics_params={"diffusion_coeff": 0.1}
    )
    
    assert simulator_id is not None
    assert len(service.simulators) == 1

@pytest.mark.asyncio
async def test_store_snapshot():
    """Test storing simulated snapshot"""
    service = create_simulated_snapshot_service()
    
    # Register simulator first
    simulator_id = service.register_simulator(
        simulator_type="world_model",
        version="1.0.0",
        domain="lithography",
        physics_params={}
    )
    
    # Store snapshot
    energy_map = np.random.rand(32, 32)
    snapshot_id = await service.store_snapshot(
        snapshot_type=SnapshotType.WORLD_MODEL_SIM,
        simulator_id=simulator_id,
        energy_map=energy_map
    )
    
    assert snapshot_id is not None
    assert service.total_snapshots == 1

@pytest.mark.asyncio
async def test_calibration():
    """Test calibration against real measurement"""
    service = create_simulated_snapshot_service()
    
    simulator_id = service.register_simulator(
        simulator_type="world_model",
        version="1.0.0",
        domain="lithography",
        physics_params={}
    )
    
    # Store simulated snapshot
    sim_energy_map = np.random.rand(32, 32)
    sim_snapshot_id = await service.store_snapshot(
        snapshot_type=SnapshotType.WORLD_MODEL_SIM,
        simulator_id=simulator_id,
        energy_map=sim_energy_map
    )
    
    # Calibrate against "real" measurement
    real_energy_map = sim_energy_map + np.random.randn(32, 32) * 0.1
    calibration = await service.calibrate(
        sim_snapshot_id=sim_snapshot_id,
        real_snapshot_id="real-001",
        real_energy_map=real_energy_map
    )
    
    assert calibration is not None
    assert "mae" in calibration.error_metrics
    assert "scale_factor" in calibration.correction_factors

@pytest.mark.asyncio
async def test_statistics():
    """Test statistics tracking"""
    service = create_simulated_snapshot_service()
    
    simulator_id = service.register_simulator(
        simulator_type="thermal_sampler",
        version="1.0.0",
        domain="energy",
        physics_params={}
    )
    
    energy_map = np.random.rand(16, 16)
    await service.store_snapshot(
        snapshot_type=SnapshotType.THERMAL_SIM,
        simulator_id=simulator_id,
        energy_map=energy_map
    )
    
    stats = service.get_statistics()
    assert stats["total_snapshots"] == 1
    assert stats["total_simulators"] == 1
