"""
Tests for Registry Protocol Connector (Week 18-19 Day 9).

Tests MCP integration, A2A integration, and event bus integration.
"""

import pytest
from unittest.mock import AsyncMock, Mock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from overseer_system.capsule_lifecycle.registry_protocol_connector import (
    RegistryProtocolConnector,
    get_registry_protocol_connector
)


@pytest.mark.unit
def test_connector_initialization(mock_db_pool, mock_mcp_bridge, mock_a2a_bridge, mock_event_bus):
    """Test connector initialization."""
    # Create mock registry
    mock_registry = Mock()

    connector = RegistryProtocolConnector(
        unified_registry=mock_registry,
        mcp_bridge=mock_mcp_bridge,
        a2a_bridge=mock_a2a_bridge,
        event_bus=mock_event_bus
    )

    assert connector is not None
    assert connector.registry == mock_registry
    assert connector.mcp_bridge == mock_mcp_bridge
    assert connector.a2a_bridge == mock_a2a_bridge
    assert connector.event_bus == mock_event_bus
    assert connector.stats["mcp_queries"] == 0
    assert connector.stats["a2a_discoveries"] == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_mcp_integration_init(mock_mcp_bridge):
    """Test MCP integration initialization."""
    mock_registry = Mock()
    connector = RegistryProtocolConnector(
        unified_registry=mock_registry,
        mcp_bridge=mock_mcp_bridge
    )

    await connector.initialize()

    # Verify MCP handlers were registered
    assert mock_mcp_bridge.register_context_provider.called
    assert mock_mcp_bridge.register_resource_handler.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_a2a_integration_init(mock_a2a_bridge):
    """Test A2A integration initialization."""
    mock_registry = Mock()
    connector = RegistryProtocolConnector(
        unified_registry=mock_registry,
        a2a_bridge=mock_a2a_bridge
    )

    await connector.initialize()

    # Verify A2A handlers were registered
    assert mock_a2a_bridge.register_discovery_handler.called
    assert mock_a2a_bridge.register_bid_validator.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_provide_capsule_context(sample_capsule_data):
    """Test MCP capsule context provision."""
    mock_registry = Mock()
    mock_registry.get_capsule = AsyncMock(return_value=sample_capsule_data)

    connector = RegistryProtocolConnector(unified_registry=mock_registry)

    context = await connector._provide_capsule_context("test-capsule-123")

    assert context["type"] == "capsule"
    assert context["capsule_id"] == "test-capsule-123"
    assert "lifecycle_context" in context
    assert connector.stats["mcp_queries"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_provide_capsule_context_not_found():
    """Test MCP capsule context when capsule not found."""
    mock_registry = Mock()
    mock_registry.get_capsule = AsyncMock(return_value=None)

    connector = RegistryProtocolConnector(unified_registry=mock_registry)

    context = await connector._provide_capsule_context("nonexistent")

    assert context["error"] == "capsule_not_found"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_provide_capsule_list_context(sample_capsule_data):
    """Test MCP capsule list context provision."""
    mock_registry = Mock()
    mock_registry.search_capsules = AsyncMock(return_value=[sample_capsule_data])

    connector = RegistryProtocolConnector(unified_registry=mock_registry)

    context = await connector._provide_capsule_list_context({"status": "active"})

    assert context["type"] == "capsule_list"
    assert context["count"] == 1
    assert len(context["capsules"]) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_provide_capsule_lineage_context():
    """Test MCP capsule lineage context provision."""
    mock_registry = Mock()
    mock_registry.get_capsule_lineage = AsyncMock(return_value={
        "generation": 2,
        "parents": ["parent-1"],
        "children": ["child-1"],
        "total_ancestors": 1,
        "total_descendants": 1
    })

    connector = RegistryProtocolConnector(unified_registry=mock_registry)

    context = await connector._provide_capsule_lineage_context("test-capsule-123")

    assert context["type"] == "capsule_lineage"
    assert context["generation"] == 2
    assert len(context["parents"]) == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_handle_a2a_agent_discovery(sample_capsule_data):
    """Test A2A agent discovery."""
    mock_registry = Mock()
    mock_registry.search_capsules = AsyncMock(return_value=[sample_capsule_data])

    connector = RegistryProtocolConnector(unified_registry=mock_registry)

    agents = await connector._handle_a2a_agent_discovery({
        "capabilities": ["data_processing"],
        "status": "active"
    })

    assert isinstance(agents, list)
    assert connector.stats["a2a_discoveries"] == 1


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_a2a_bid_success(sample_capsule_data):
    """Test successful A2A bid validation."""
    mock_registry = Mock()
    mock_registry.get_capsule = AsyncMock(return_value=sample_capsule_data)

    connector = RegistryProtocolConnector(unified_registry=mock_registry)

    valid = await connector._validate_a2a_bid_against_registry({
        "agent_id": "test-capsule-123"
    })

    assert valid is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_a2a_bid_not_found():
    """Test A2A bid validation when agent not found."""
    mock_registry = Mock()
    mock_registry.get_capsule = AsyncMock(return_value=None)

    connector = RegistryProtocolConnector(unified_registry=mock_registry)

    valid = await connector._validate_a2a_bid_against_registry({
        "agent_id": "nonexistent"
    })

    assert valid is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validate_a2a_bid_inactive_agent(sample_capsule_data):
    """Test A2A bid validation with inactive agent."""
    inactive_capsule = sample_capsule_data.copy()
    inactive_capsule["lifecycle_context"]["stage"] = "archived"

    mock_registry = Mock()
    mock_registry.get_capsule = AsyncMock(return_value=inactive_capsule)

    connector = RegistryProtocolConnector(unified_registry=mock_registry)

    valid = await connector._validate_a2a_bid_against_registry({
        "agent_id": "test-capsule-123"
    })

    assert valid is False


@pytest.mark.unit
def test_translate_a2a_query_to_registry_filters():
    """Test A2A query to registry filter translation."""
    connector = RegistryProtocolConnector()

    filters = connector._translate_a2a_query_to_registry_filters({
        "status": "active",
        "governance_status": "validated",
        "source": "application_layer"
    })

    assert filters["status"] == "active"
    assert filters["governance_status"] == "validated"
    assert filters["source"] == "application_layer"
    assert connector.stats["protocol_translations"] == 1


@pytest.mark.unit
def test_translate_capsule_to_a2a_agent(sample_capsule_data):
    """Test capsule to A2A agent format translation."""
    connector = RegistryProtocolConnector()

    agent = connector._translate_capsule_to_a2a_agent(sample_capsule_data)

    assert agent is not None
    assert agent["agent_id"] == "test-capsule-123"
    assert agent["type"] == "capsule_agent"
    assert agent["status"] == "active"
    assert agent["governance_status"] == "validated"
    assert agent["trust_score"] == 85


@pytest.mark.unit
@pytest.mark.asyncio
async def test_event_publishing(mock_event_bus):
    """Test event publishing to event bus."""
    connector = RegistryProtocolConnector(event_bus=mock_event_bus)

    await connector._publish_event("test.event", {"data": "value"})

    assert mock_event_bus.publish.called
    assert connector.stats["events_published"] == 1


@pytest.mark.unit
def test_get_statistics():
    """Test statistics retrieval."""
    connector = RegistryProtocolConnector()

    stats = connector.get_statistics()

    assert "mcp_queries" in stats
    assert "a2a_discoveries" in stats
    assert "events_published" in stats
    assert "protocol_translations" in stats
    assert "has_registry" in stats
    assert stats["has_registry"] is False


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_mcp_workflow(mock_mcp_bridge, sample_capsule_data):
    """Test complete MCP integration workflow."""
    mock_registry = Mock()
    mock_registry.get_capsule = AsyncMock(return_value=sample_capsule_data)

    connector = RegistryProtocolConnector(
        unified_registry=mock_registry,
        mcp_bridge=mock_mcp_bridge
    )

    await connector.initialize()

    # Simulate MCP query
    context = await connector._provide_capsule_context("test-capsule-123")

    assert context["type"] == "capsule"
    assert mock_mcp_bridge.register_context_provider.called


@pytest.mark.integration
@pytest.mark.asyncio
async def test_full_a2a_workflow(mock_a2a_bridge, sample_capsule_data):
    """Test complete A2A integration workflow."""
    mock_registry = Mock()
    mock_registry.search_capsules = AsyncMock(return_value=[sample_capsule_data])
    mock_registry.get_capsule = AsyncMock(return_value=sample_capsule_data)

    connector = RegistryProtocolConnector(
        unified_registry=mock_registry,
        a2a_bridge=mock_a2a_bridge
    )

    await connector.initialize()

    # Simulate A2A discovery
    agents = await connector._handle_a2a_agent_discovery({"status": "active"})

    # Simulate A2A bid validation
    valid = await connector._validate_a2a_bid_against_registry({
        "agent_id": "test-capsule-123"
    })

    assert isinstance(agents, list)
    assert valid is True
    assert mock_a2a_bridge.register_discovery_handler.called
