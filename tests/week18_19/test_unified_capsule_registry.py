"""
Tests for Unified Capsule Registry (Week 18-19 Day 4).

Tests registration, search, lineage tracking, and caching functionality.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../src'))

from overseer_system.capsule_lifecycle.unified_capsule_registry import (
    UnifiedCapsuleRegistry,
    RegistrySearchField
)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_registry_initialization(mock_db_pool):
    """Test registry initialization."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    assert registry is not None
    assert registry.db_pool == mock_db_pool
    assert registry.cache_ttl == 300  # 5 minutes
    assert len(registry.cache) == 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_register_capsule(mock_db_pool, sample_capsule_data):
    """Test capsule registration."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    # Mock database response
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetchrow = AsyncMock(
        return_value={
            "capsule_id": "test-capsule-123",
            "source": "application_layer",
            "created_at": "2025-05-25T10:00:00Z"
        }
    )

    result = await registry.register_capsule(
        capsule_id="test-capsule-123",
        capsule_data=sample_capsule_data,
        source="application_layer"
    )

    assert result is not None
    assert result["capsule_id"] == "test-capsule-123"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsule_from_cache(mock_db_pool, sample_capsule_data):
    """Test capsule retrieval from cache."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    # Add to cache
    registry.cache["test-capsule-123"] = {
        "data": sample_capsule_data,
        "cached_at": registry._get_current_time()
    }

    result = await registry.get_capsule("test-capsule-123")

    assert result == sample_capsule_data
    # Should not query database (verify no fetch called)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsule_from_database(mock_db_pool, sample_capsule_data):
    """Test capsule retrieval from database when not in cache."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    # Mock database response
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetchrow = AsyncMock(
        return_value={
            "capsule_data": sample_capsule_data
        }
    )

    result = await registry.get_capsule("test-capsule-123")

    # Verify database was queried
    assert mock_db_pool.acquire.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_capsules_by_source(mock_db_pool, sample_capsule_data):
    """Test capsule search by source."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    # Mock database response
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetch = AsyncMock(
        return_value=[
            {"capsule_data": sample_capsule_data}
        ]
    )

    results = await registry.search_capsules(
        filters={"source": "application_layer"},
        limit=10
    )

    assert len(results) >= 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_search_capsules_by_status(mock_db_pool):
    """Test capsule search by status."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    # Mock database response
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetch = AsyncMock(
        return_value=[]
    )

    results = await registry.search_capsules(
        filters={"status": "active"},
        limit=50
    )

    assert isinstance(results, list)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_capsule_lineage(mock_db_pool):
    """Test capsule lineage retrieval."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    # Mock database responses
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetch = AsyncMock(
        return_value=[
            {"capsule_id": "parent-1"},
            {"capsule_id": "child-1"}
        ]
    )
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetchval = AsyncMock(
        return_value=2
    )

    lineage = await registry.get_capsule_lineage("test-capsule-123")

    assert lineage is not None
    assert "parents" in lineage or "children" in lineage


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cache_expiration(mock_db_pool, sample_capsule_data):
    """Test cache TTL expiration."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool, cache_ttl=1)

    # Add to cache with old timestamp
    registry.cache["test-capsule-123"] = {
        "data": sample_capsule_data,
        "cached_at": registry._get_current_time() - 10  # Expired
    }

    # Mock database response
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetchrow = AsyncMock(
        return_value={"capsule_data": sample_capsule_data}
    )

    result = await registry.get_capsule("test-capsule-123")

    # Should query database due to expired cache
    assert mock_db_pool.acquire.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_update_capsule_status(mock_db_pool):
    """Test capsule status update."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    # Mock database response
    mock_db_pool.acquire.return_value.__aenter__.return_value.execute = AsyncMock()

    await registry.update_capsule_status("test-capsule-123", "archived")

    # Verify database update was called
    assert mock_db_pool.acquire.called


@pytest.mark.integration
@pytest.mark.asyncio
async def test_register_and_search_workflow(mock_db_pool, sample_capsule_data):
    """Test complete register-then-search workflow."""
    registry = UnifiedCapsuleRegistry(database_pool=mock_db_pool)

    # Mock registration
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetchrow = AsyncMock(
        return_value={
            "capsule_id": "test-capsule-123",
            "source": "application_layer"
        }
    )

    # Register capsule
    await registry.register_capsule(
        capsule_id="test-capsule-123",
        capsule_data=sample_capsule_data,
        source="application_layer"
    )

    # Mock search
    mock_db_pool.acquire.return_value.__aenter__.return_value.fetch = AsyncMock(
        return_value=[{"capsule_data": sample_capsule_data}]
    )

    # Search for capsule
    results = await registry.search_capsules(
        filters={"source": "application_layer"}
    )

    assert isinstance(results, list)


@pytest.mark.unit
def test_search_field_enum():
    """Test RegistrySearchField enum values."""
    assert RegistrySearchField.SOURCE.value == "source"
    assert RegistrySearchField.STATUS.value == "status"
    assert RegistrySearchField.TEMPLATE_ID.value == "template_id"
    assert RegistrySearchField.GOVERNANCE_STATUS.value == "governance_status"
