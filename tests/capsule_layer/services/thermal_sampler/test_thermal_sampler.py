"""
Tests for ThermalSampler Service
"""

import pytest
import numpy as np
from src.capsule_layer.services.thermal_sampler.thermal_sampler_service import (
    create_thermal_sampler
)

@pytest.mark.asyncio
async def test_thermal_sampler_creation():
    """Test thermal sampler service creation"""
    sampler = create_thermal_sampler()
    assert sampler is not None
    assert sampler.total_samples == 0

@pytest.mark.asyncio
async def test_simple_sampling():
    """Test simple thermal sampling"""
    sampler = create_thermal_sampler()
    
    # Create energy landscape
    from src.capsule_layer.services.thermal_sampler.thermal_sampler_service import ProblemType, EnergyLandscape, Constraint
    
    landscape_id = sampler.create_landscape(
        problem_type=ProblemType.COMBINATORIAL,
        dimensions=2,
        constraints=[],
        bounds=[(0.0, 10.0), (0.0, 10.0)]
    )
    results = await sampler.sample(landscape_id, num_samples=10)
    
    assert results is not None
    assert len(results) > 0

@pytest.mark.asyncio
async def test_constrained_sampling():
    """Test thermal sampling with constraints"""
    sampler = create_thermal_sampler()
    
    from src.capsule_layer.services.thermal_sampler.thermal_sampler_service import ProblemType, EnergyLandscape, Constraint
    
    constraint = Constraint(
        name="sum_constraint",
        type="inequality",
        weight=1.0,
        function="x + y <= 10"
    )
    
    landscape_id = sampler.create_landscape(
        problem_type=ProblemType.COMBINATORIAL,
        dimensions=2,
        constraints=[constraint],
        bounds=[(0.0, 10.0), (0.0, 10.0)]
    )
    results = await sampler.sample(landscape_id, num_samples=10)
    
    assert results is not None
    assert len(results) > 0

@pytest.mark.asyncio
async def test_statistics():
    """Test statistics tracking"""
    sampler = create_thermal_sampler()
    
    from src.capsule_layer.services.thermal_sampler.thermal_sampler_service import ProblemType, EnergyLandscape
    
    landscape_id = sampler.create_landscape(
        problem_type=ProblemType.COMBINATORIAL,
        dimensions=1,
        constraints=[],
        bounds=[(0.0, 10.0)]
    )
    await sampler.sample(landscape_id, num_samples=10)
    
    stats = sampler.get_statistics()
    assert stats["total_samples"] >= 10
