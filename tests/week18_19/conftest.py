"""
Pytest configuration and shared fixtures for Week 18-19 tests.

Provides shared test fixtures for:
- Database connection pools
- Event bus mocks
- Protocol bridge mocks
- Common test data
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, MagicMock


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db_pool():
    """Mock database connection pool."""
    pool = AsyncMock()

    # Mock acquire context manager
    conn = AsyncMock()
    conn.execute = AsyncMock()
    conn.fetch = AsyncMock(return_value=[])
    conn.fetchrow = AsyncMock(return_value=None)

    pool.acquire = AsyncMock()
    pool.acquire.return_value.__aenter__ = AsyncMock(return_value=conn)
    pool.acquire.return_value.__aexit__ = AsyncMock(return_value=None)

    return pool


@pytest.fixture
def mock_event_bus():
    """Mock event bus."""
    event_bus = Mock()
    event_bus.publish = AsyncMock()
    event_bus.subscribe = Mock()
    return event_bus


@pytest.fixture
def mock_mcp_bridge():
    """Mock MCP protocol bridge."""
    mcp_bridge = Mock()
    mcp_bridge.register_context_provider = AsyncMock()
    mcp_bridge.register_resource_handler = AsyncMock()
    return mcp_bridge


@pytest.fixture
def mock_a2a_bridge():
    """Mock A2A protocol bridge."""
    a2a_bridge = Mock()
    a2a_bridge.register_discovery_handler = AsyncMock()
    a2a_bridge.register_bid_validator = AsyncMock()
    return a2a_bridge


@pytest.fixture
def sample_capsule_data():
    """Sample capsule data for testing."""
    return {
        "lifecycle_context": {
            "capsule_id": "test-capsule-123",
            "source": "application_layer",
            "stage": "active",
            "template_id": "test-template-1",
            "created_at": "2025-05-25T10:00:00Z",
            "generation": 1
        },
        "application_instance": {
            "name": "Test Capsule",
            "instance": {
                "capabilities": ["data_processing", "analytics"]
            }
        },
        "infrastructure_instance": {
            "name": "test-capsule-infra",
            "security": {
                "trust_score": 85
            }
        },
        "governance": {
            "validated_at": "2025-05-25T10:01:00Z",
            "policies_validated": ["security", "compliance"]
        }
    }


@pytest.fixture
def sample_ar_environment():
    """Sample AR environment data for testing."""
    return {
        "environment_id": "test-env-123",
        "environment_type": "mobile_ar",
        "user_id": "user-456",
        "session_id": "session-789",
        "capabilities": ["hand_tracking", "gaze_input"],
        "active": True
    }


@pytest.fixture
def sample_spatial_anchor():
    """Sample spatial anchor data for testing."""
    return {
        "anchor_id": "anchor-123",
        "position": {"x": 1.5, "y": 2.0, "z": 3.0},
        "rotation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
        "environment_id": "test-env-123"
    }
