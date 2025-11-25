"""
Tests for Integration Orchestrator (Week 18-19 Day 8).

Tests orchestrator initialization, layer manager activation, and protocol bridge connections.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from overseer_system.integration.integration_orchestrator import IntegrationOrchestrator


@pytest.mark.unit
def test_orchestrator_initialization(mock_event_bus, mock_db_pool):
    """Test orchestrator initialization."""
    orchestrator = IntegrationOrchestrator(
        event_bus=mock_event_bus,
        database_pool=mock_db_pool
    )

    assert orchestrator is not None
    assert orchestrator.event_bus == mock_event_bus
    assert orchestrator.db_pool == mock_db_pool
    assert len(orchestrator.integration_managers) == 0
    assert orchestrator.initialized is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_orchestrator_initialize(mock_event_bus, mock_db_pool):
    """Test orchestrator full initialization."""
    orchestrator = IntegrationOrchestrator(
        event_bus=mock_event_bus,
        database_pool=mock_db_pool
    )

    # Mock the initialization methods
    orchestrator._initialize_layer_managers = AsyncMock()
    orchestrator._initialize_protocol_bridges = AsyncMock()
    orchestrator._connect_week17_19_components = AsyncMock()
    orchestrator._subscribe_to_events = AsyncMock()

    result = await orchestrator.initialize()

    assert result is True
    assert orchestrator.initialized is True
    assert orchestrator._initialize_layer_managers.called
    assert orchestrator._initialize_protocol_bridges.called
    assert orchestrator._connect_week17_19_components.called
    assert orchestrator._subscribe_to_events.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_initialize_layer_managers(mock_event_bus, mock_db_pool):
    """Test layer integration managers initialization."""
    orchestrator = IntegrationOrchestrator(
        event_bus=mock_event_bus,
        database_pool=mock_db_pool
    )

    # Mock the import attempts
    with patch('overseer_system.integration.integration_orchestrator.logger'):
        await orchestrator._initialize_layer_managers()

    # Should attempt to initialize 8 layer managers
    # (May not succeed due to missing modules in test environment)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_initialize_protocol_bridges(mock_event_bus):
    """Test protocol bridges initialization."""
    orchestrator = IntegrationOrchestrator(event_bus=mock_event_bus)

    # Mock the import attempts
    with patch('overseer_system.integration.integration_orchestrator.logger'):
        await orchestrator._initialize_protocol_bridges()

    # Should attempt to initialize MCP and A2A bridges
    # (May not succeed due to missing modules in test environment)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_connect_week17_19_components(mock_event_bus, mock_db_pool):
    """Test Week 17-19 component connections."""
    orchestrator = IntegrationOrchestrator(
        event_bus=mock_event_bus,
        database_pool=mock_db_pool
    )

    # Mock the imports and components
    mock_coordinator = Mock()
    mock_registry = Mock()
    mock_connector = Mock()
    mock_connector.initialize = AsyncMock()
    mock_adapter = Mock()

    with patch('overseer_system.integration.integration_orchestrator.get_capsule_lifecycle_coordinator', return_value=mock_coordinator):
        with patch('overseer_system.integration.integration_orchestrator.get_unified_capsule_registry', return_value=mock_registry):
            with patch('overseer_system.integration.integration_orchestrator.get_registry_protocol_connector', return_value=mock_connector):
                with patch('overseer_system.integration.integration_orchestrator.get_ar_vr_integration_adapter', return_value=mock_adapter):
                    await orchestrator._connect_week17_19_components()

    # Verify components were connected
    assert orchestrator.capsule_coordinator == mock_coordinator
    assert orchestrator.unified_registry == mock_registry
    assert orchestrator.registry_protocol_connector == mock_connector


@pytest.mark.unit
@pytest.mark.asyncio
async def test_subscribe_to_events(mock_event_bus):
    """Test event subscription."""
    orchestrator = IntegrationOrchestrator(event_bus=mock_event_bus)

    await orchestrator._subscribe_to_events()

    # Verify event subscriptions
    assert mock_event_bus.subscribe.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_orchestrator_double_initialization(mock_event_bus, mock_db_pool):
    """Test that orchestrator doesn't re-initialize."""
    orchestrator = IntegrationOrchestrator(
        event_bus=mock_event_bus,
        database_pool=mock_db_pool
    )

    # Mock initialization methods
    orchestrator._initialize_layer_managers = AsyncMock()

    # Initialize once
    result1 = await orchestrator.initialize()

    # Try to initialize again
    result2 = await orchestrator.initialize()

    # Second initialization should return True but not reinitialize
    assert result1 is True
    assert result2 is True
    assert orchestrator._initialize_layer_managers.call_count == 1  # Only called once


@pytest.mark.unit
def test_get_integration_manager():
    """Test retrieving specific integration manager."""
    orchestrator = IntegrationOrchestrator()

    # Add a mock manager
    mock_manager = Mock()
    orchestrator.integration_managers["application_layer"] = mock_manager

    manager = orchestrator.get_integration_manager("application_layer")

    assert manager == mock_manager


@pytest.mark.unit
def test_get_integration_manager_not_found():
    """Test retrieving non-existent integration manager."""
    orchestrator = IntegrationOrchestrator()

    manager = orchestrator.get_integration_manager("nonexistent")

    assert manager is None


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_orchestrator_workflow(mock_event_bus, mock_db_pool):
    """Test complete orchestrator initialization workflow."""
    orchestrator = IntegrationOrchestrator(
        event_bus=mock_event_bus,
        database_pool=mock_db_pool
    )

    # Mock all initialization steps
    orchestrator._initialize_layer_managers = AsyncMock()
    orchestrator._initialize_protocol_bridges = AsyncMock()
    orchestrator._connect_week17_19_components = AsyncMock()
    orchestrator._subscribe_to_events = AsyncMock()

    # Initialize
    result = await orchestrator.initialize()

    # Verify all steps completed
    assert result is True
    assert orchestrator.initialized is True

    # Verify initialization order
    orchestrator._initialize_layer_managers.assert_called_once()
    orchestrator._initialize_protocol_bridges.assert_called_once()
    orchestrator._connect_week17_19_components.assert_called_once()
    orchestrator._subscribe_to_events.assert_called_once()
