"""
Tests for AR/VR Integration Adapter (Week 18-19 Day 5).

Tests AR/VR environment management, capsule spawn orchestration, and interaction handling.
"""

import pytest
from unittest.mock import AsyncMock, Mock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from overseer_system.integration.ar_vr_integration_adapter import ARVRIntegrationAdapter


@pytest.mark.unit
def test_adapter_initialization(mock_event_bus):
    """Test adapter initialization."""
    adapter = ARVRIntegrationAdapter(event_bus=mock_event_bus)

    assert adapter is not None
    assert adapter.event_bus == mock_event_bus
    assert len(adapter.ar_environments) == 0
    assert len(adapter.ar_capsule_instances) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_ar_environment(mock_event_bus, sample_ar_environment):
    """Test AR environment registration."""
    adapter = ARVRIntegrationAdapter(event_bus=mock_event_bus)

    result = await adapter.register_ar_environment(
        environment_id=sample_ar_environment["environment_id"],
        environment_type=sample_ar_environment["environment_type"],
        user_id=sample_ar_environment["user_id"],
        session_id=sample_ar_environment["session_id"],
        capabilities=sample_ar_environment["capabilities"]
    )

    assert result is not None
    assert result["environment_id"] == sample_ar_environment["environment_id"]
    assert sample_ar_environment["environment_id"] in adapter.ar_environments


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_ar_environment(mock_event_bus, sample_ar_environment):
    """Test AR environment retrieval."""
    adapter = ARVRIntegrationAdapter(event_bus=mock_event_bus)

    # Register environment
    await adapter.register_ar_environment(
        environment_id=sample_ar_environment["environment_id"],
        environment_type=sample_ar_environment["environment_type"],
        user_id=sample_ar_environment["user_id"],
        session_id=sample_ar_environment["session_id"]
    )

    # Retrieve environment
    env = adapter.get_ar_environment(sample_ar_environment["environment_id"])

    assert env is not None
    assert env["environment_id"] == sample_ar_environment["environment_id"]


@pytest.mark.unit
@pytest.mark.asyncio
async def test_orchestrate_ar_capsule_spawn(mock_event_bus, sample_spatial_anchor):
    """Test AR capsule spawn orchestration."""
    # Create mock dependencies
    mock_registry = Mock()
    mock_registry.get_capsule = AsyncMock(return_value={
        "lifecycle_context": {
            "capsule_id": "test-capsule-123",
            "stage": "active"
        },
        "application_instance": {
            "instance": {
                "morphology": {
                    "visual_properties": {"color": "#00FF00"}
                }
            }
        }
    })

    mock_ar_vr_manager = Mock()
    mock_ar_vr_manager.spawn_capsule = AsyncMock(return_value={
        "success": True,
        "ar_instance_id": "ar-instance-123"
    })

    adapter = ARVRIntegrationAdapter(
        event_bus=mock_event_bus,
        capsule_coordinator=Mock(unified_registry=mock_registry)
    )
    adapter.ar_vr_manager = mock_ar_vr_manager

    # Register environment first
    await adapter.register_ar_environment(
        environment_id="test-env-123",
        environment_type="mobile_ar",
        user_id="user-456",
        session_id="session-789"
    )

    # Orchestrate spawn
    result = await adapter.orchestrate_ar_capsule_spawn(
        capsule_id="test-capsule-123",
        environment_id="test-env-123",
        spatial_anchor=sample_spatial_anchor
    )

    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_ar_interaction_hand_tracking(mock_event_bus, sample_ar_environment):
    """Test handling hand tracking interaction."""
    adapter = ARVRIntegrationAdapter(event_bus=mock_event_bus)

    # Register environment
    await adapter.register_ar_environment(**sample_ar_environment)

    # Handle interaction
    result = await adapter.handle_ar_interaction_event({
        "environment_id": sample_ar_environment["environment_id"],
        "interaction_type": "hand_tracking",
        "interaction_data": {
            "gesture": "pinch",
            "hand": "right",
            "target_position": {"x": 1.0, "y": 2.0, "z": 3.0}
        }
    })

    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_ar_interaction_gaze_input(mock_event_bus, sample_ar_environment):
    """Test handling gaze input interaction."""
    adapter = ARVRIntegrationAdapter(event_bus=mock_event_bus)

    # Register environment
    await adapter.register_ar_environment(**sample_ar_environment)

    # Handle interaction
    result = await adapter.handle_ar_interaction_event({
        "environment_id": sample_ar_environment["environment_id"],
        "interaction_type": "gaze_input",
        "interaction_data": {
            "gaze_direction": {"x": 0.0, "y": 0.0, "z": 1.0},
            "gaze_origin": {"x": 0.0, "y": 1.7, "z": 0.0}
        }
    })

    assert result is not None


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_ar_interaction_voice_command(mock_event_bus, sample_ar_environment):
    """Test handling voice command interaction."""
    adapter = ARVRIntegrationAdapter(event_bus=mock_event_bus)

    # Register environment
    await adapter.register_ar_environment(**sample_ar_environment)

    # Handle interaction
    result = await adapter.handle_ar_interaction_event({
        "environment_id": sample_ar_environment["environment_id"],
        "interaction_type": "voice_command",
        "interaction_data": {
            "command": "select capsule",
            "confidence": 0.95
        }
    })

    assert result is not None


@pytest.mark.unit
def test_translate_interaction_to_command():
    """Test interaction to command translation."""
    adapter = ARVRIntegrationAdapter()

    command = adapter._translate_interaction_to_command(
        interaction_type="hand_tracking",
        interaction_data={"gesture": "pinch"},
        capsule_id="test-capsule-123"
    )

    assert command is not None
    assert "capsule_id" in command
    assert "action" in command


@pytest.mark.unit
@pytest.mark.asyncio
async def test_deregister_ar_environment(mock_event_bus, sample_ar_environment):
    """Test AR environment deregistration."""
    adapter = ARVRIntegrationAdapter(event_bus=mock_event_bus)

    # Register environment
    await adapter.register_ar_environment(**sample_ar_environment)

    # Deregister environment
    result = await adapter.deregister_ar_environment(
        sample_ar_environment["environment_id"]
    )

    assert result is True
    assert sample_ar_environment["environment_id"] not in adapter.ar_environments


@pytest.mark.unit
def test_get_statistics():
    """Test statistics retrieval."""
    adapter = ARVRIntegrationAdapter()

    stats = adapter.get_statistics()

    assert "total_environments" in stats
    assert "active_environments" in stats
    assert "total_ar_capsule_instances" in stats
    assert stats["total_environments"] == 0


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_ar_capsule_workflow(mock_event_bus, sample_ar_environment, sample_spatial_anchor):
    """Test complete AR capsule spawn and interaction workflow."""
    # Setup mocks
    mock_registry = Mock()
    mock_registry.get_capsule = AsyncMock(return_value={
        "lifecycle_context": {"capsule_id": "test-capsule-123", "stage": "active"},
        "application_instance": {
            "instance": {"morphology": {"visual_properties": {"color": "#00FF00"}}}
        }
    })

    adapter = ARVRIntegrationAdapter(
        event_bus=mock_event_bus,
        capsule_coordinator=Mock(unified_registry=mock_registry)
    )

    # 1. Register environment
    await adapter.register_ar_environment(**sample_ar_environment)

    # 2. Verify environment
    env = adapter.get_ar_environment(sample_ar_environment["environment_id"])
    assert env is not None

    # 3. Handle interaction
    interaction_result = await adapter.handle_ar_interaction_event({
        "environment_id": sample_ar_environment["environment_id"],
        "interaction_type": "hand_tracking",
        "interaction_data": {"gesture": "tap"}
    })
    assert interaction_result is not None

    # 4. Deregister environment
    dereg_result = await adapter.deregister_ar_environment(
        sample_ar_environment["environment_id"]
    )
    assert dereg_result is True
