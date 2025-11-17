"""
Tests for WorldModel Service
"""

import pytest
import numpy as np
from src.capsule_layer.services.world_model.world_model_service import (
    create_world_model,
    DomainType,
    SimulationConfig,
    PhysicsState
)

@pytest.mark.asyncio
async def test_world_model_creation():
    """Test world model service creation"""
    world_model = create_world_model()
    assert world_model is not None
    assert world_model.total_simulations == 0

@pytest.mark.asyncio
async def test_resist_simulation():
    """Test photoresist diffusion simulation"""
    world_model = create_world_model()
    
    # Create initial state
    grid_size = (32, 32)
    initial_grid = np.random.rand(*grid_size)
    initial_state = PhysicsState(
        domain=DomainType.RESIST_CHEMISTRY,
        spatial_grid=initial_grid
    )
    
    # Create config
    config = SimulationConfig(
        domain=DomainType.RESIST_CHEMISTRY,
        grid_size=grid_size,
        time_steps=50,
        dt=0.01,
        physics_params={
            "diffusion_coeff": 0.1,
            "reaction_rate": 0.01
        }
    )
    
    # Run simulation
    result = await world_model.simulate(config, initial_state)
    
    assert result is not None
    assert result.simulation_id is not None
    assert result.final_state is not None
    assert len(result.trajectory) > 0
    assert len(result.energy_trajectory) > 0

@pytest.mark.asyncio
async def test_plasma_simulation():
    """Test plasma dynamics simulation"""
    world_model = create_world_model()
    
    grid_size = (32, 32)
    initial_grid = np.random.rand(*grid_size)
    initial_state = PhysicsState(
        domain=DomainType.PLASMA,
        spatial_grid=initial_grid
    )
    
    config = SimulationConfig(
        domain=DomainType.PLASMA,
        grid_size=grid_size,
        time_steps=50,
        dt=0.01,
        physics_params={"viscosity": 0.01}
    )
    
    result = await world_model.simulate(config, initial_state)
    
    assert result is not None
    assert result.final_state.velocity is not None

@pytest.mark.asyncio
async def test_rollout():
    """Test multi-step rollout prediction"""
    world_model = create_world_model()
    
    grid_size = (16, 16)
    initial_grid = np.random.rand(*grid_size)
    initial_state = PhysicsState(
        domain=DomainType.RESIST_CHEMISTRY,
        spatial_grid=initial_grid
    )
    
    config = SimulationConfig(
        domain=DomainType.RESIST_CHEMISTRY,
        grid_size=grid_size,
        time_steps=20,
        dt=0.01,
        physics_params={}
    )
    
    trajectory = await world_model.rollout(config, initial_state, horizon=30)
    
    assert len(trajectory) > 0

@pytest.mark.asyncio
async def test_statistics():
    """Test statistics tracking"""
    world_model = create_world_model()
    
    grid_size = (16, 16)
    initial_grid = np.random.rand(*grid_size)
    initial_state = PhysicsState(
        domain=DomainType.RESIST_CHEMISTRY,
        spatial_grid=initial_grid
    )
    
    config = SimulationConfig(
        domain=DomainType.RESIST_CHEMISTRY,
        grid_size=grid_size,
        time_steps=20,
        dt=0.01,
        physics_params={}
    )
    
    await world_model.simulate(config, initial_state)
    
    stats = world_model.get_statistics()
    assert stats["total_simulations"] == 1
    assert stats["total_time_steps"] == 20
