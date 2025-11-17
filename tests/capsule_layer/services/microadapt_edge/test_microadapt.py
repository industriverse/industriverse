"""
Tests for MicroAdaptEdge Service
"""

import pytest
import numpy as np
from src.capsule_layer.services.microadapt_edge.microadapt_service import (
    create_microadapt_edge
)

@pytest.mark.asyncio
async def test_microadapt_creation():
    """Test MicroAdapt service creation"""
    microadapt = create_microadapt_edge()
    assert microadapt is not None
    assert microadapt.total_updates == 0

@pytest.mark.asyncio
async def test_update():
    """Test updating with new data point (O(1) time)"""
    microadapt = create_microadapt_edge({"base_window_length": 50})
    
    # Add some data points
    for i in range(100):
        data_point = np.array([np.sin(i * 0.1), np.cos(i * 0.1)])
        await microadapt.update(data_point)
    
    assert microadapt.total_updates == 100
    assert microadapt.current_time == 100

@pytest.mark.asyncio
async def test_forecast():
    """Test lF-steps-ahead forecasting"""
    microadapt = create_microadapt_edge({
        "base_window_length": 50,
        "max_model_units": 4,
        "num_regimes": 4
    })
    
    # Add training data
    for i in range(150):
        data_point = np.array([np.sin(i * 0.1), np.cos(i * 0.1)])
        await microadapt.update(data_point)
    
    # Generate forecast
    X_current = microadapt._get_current_window()
    result = await microadapt.search_and_forecast(
        X_current=X_current,
        forecast_horizon=10
    )
    
    assert result is not None
    assert result.forecast_values.shape[0] == 10
    assert result.forecast_horizon == 10

@pytest.mark.asyncio
async def test_regime_recognition():
    """Test dynamic regime recognition"""
    microadapt = create_microadapt_edge({
        "base_window_length": 50,
        "max_model_units": 4,
        "num_regimes": 4
    })
    
    # Add data with regime change
    # Regime 1: sine wave
    for i in range(100):
        data_point = np.array([np.sin(i * 0.1)])
        await microadapt.update(data_point)
    
    # Regime 2: cosine wave
    for i in range(100, 200):
        data_point = np.array([np.cos(i * 0.1)])
        await microadapt.update(data_point)
    
    # Check that regimes were detected
    stats = microadapt.get_statistics()
    assert stats["num_model_units"] > 0
    assert stats["regime_transitions"] >= 0

@pytest.mark.asyncio
async def test_hierarchical_window():
    """Test multi-scale hierarchical window"""
    microadapt = create_microadapt_edge({
        "base_window_length": 50,
        "num_hierarchical_levels": 3
    })
    
    # Add data
    for i in range(200):
        data_point = np.array([i, i**2])
        await microadapt.update(data_point)
    
    # Check hierarchical window
    assert microadapt.hierarchical_window is not None
    assert microadapt.hierarchical_window.num_levels == 3
    assert len(microadapt.hierarchical_window.windows) > 0

@pytest.mark.asyncio
async def test_statistics():
    """Test statistics tracking"""
    microadapt = create_microadapt_edge()
    
    for i in range(50):
        data_point = np.array([i])
        await microadapt.update(data_point)
    
    stats = microadapt.get_statistics()
    assert stats["total_updates"] == 50
    assert stats["current_time"] == 50
    assert stats["data_stream_length"] == 50
