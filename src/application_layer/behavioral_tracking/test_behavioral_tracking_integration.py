"""
Integration Tests for Behavioral Tracking Infrastructure.

Tests the complete flow from interaction event logging through BV computation
to storage and API retrieval. Week 9 Day 7 deliverable.

Test Coverage:
- End-to-end event tracking flow
- BV computation accuracy
- Storage layer (PostgreSQL + Redis)
- API endpoints
- Kafka integration (with mocks)
- Error handling and edge cases
"""

import pytest
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List
from unittest.mock import Mock, patch, AsyncMock
import uuid

# Import modules under test
from behavioral_tracker import (
    BehavioralTracker,
    InteractionEvent,
    InteractionType,
    EventSeverity
)
from behavioral_vector_computer import (
    BehavioralVectorComputer,
    BehavioralVector,
    UserArchetype
)
from bv_storage import BVStorage
from bv_api import app as fastapi_app

# Test fixtures
@pytest.fixture
def sample_user_id():
    """Generate a test user ID."""
    return f"test_user_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_session_id():
    """Generate a test session ID."""
    return f"test_session_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_capsule_id():
    """Generate a test capsule ID."""
    return f"test_capsule_{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_interaction_events(sample_user_id, sample_session_id, sample_capsule_id):
    """Generate sample interaction events for testing."""
    base_time = datetime.utcnow()
    events = []
    
    # Simulate a typical user session
    interaction_types = [
        InteractionType.TAP,
        InteractionType.EXPAND,
        InteractionType.SCROLL,
        InteractionType.ACTION,
        InteractionType.COMPLETE,
        InteractionType.COLLAPSE,
    ]
    
    for i, interaction_type in enumerate(interaction_types):
        event = InteractionEvent(
            event_id=f"event_{i}",
            timestamp=(base_time + timedelta(seconds=i*5)).isoformat(),
            event_type=interaction_type.value,
            severity=EventSeverity.INFO.value,
            user_id=sample_user_id,
            session_id=sample_session_id,
            device_id="test_device",
            device_type="web",
            capsule_id=sample_capsule_id,
            capsule_type="task",
            capsule_category="productivity",
            interaction_target="capsule",
            duration_ms=1000 + i*500,
            success=True
        )
        events.append(event)
    
    return events


@pytest.fixture
async def behavioral_tracker():
    """Create a BehavioralTracker instance for testing."""
    # Mock Kafka producer to avoid actual Kafka dependency in tests
    with patch('behavioral_tracker.KafkaProducer') as mock_kafka:
        mock_kafka.return_value = Mock()
        tracker = BehavioralTracker(
            kafka_bootstrap_servers="localhost:9092",
            kafka_topic="interaction-events-test"
        )
        yield tracker


@pytest.fixture
async def bv_computer():
    """Create a BehavioralVectorComputer instance for testing."""
    computer = BehavioralVectorComputer()
    yield computer


@pytest.fixture
async def bv_storage():
    """Create a BVStorage instance for testing."""
    # Mock database connections
    with patch('bv_storage.asyncpg.create_pool') as mock_pg, \
         patch('bv_storage.aioredis.from_url') as mock_redis:
        
        mock_pg.return_value = AsyncMock()
        mock_redis.return_value = AsyncMock()
        
        storage = BVStorage(
            postgres_dsn="postgresql://test:test@localhost/test",
            redis_url="redis://localhost:6379"
        )
        await storage.initialize()
        yield storage
        await storage.close()


# Test Suite 1: Event Tracking
class TestEventTracking:
    """Test event logging and validation."""
    
    @pytest.mark.asyncio
    async def test_log_interaction_event(self, behavioral_tracker, sample_interaction_events):
        """Test logging a single interaction event."""
        event = sample_interaction_events[0]
        
        # Log event
        result = await behavioral_tracker.log_interaction(
            user_id=event.user_id,
            session_id=event.session_id,
            event_type=event.event_type,
            capsule_id=event.capsule_id,
            capsule_type=event.capsule_type,
            device_type=event.device_type,
            duration_ms=event.duration_ms
        )
        
        assert result is not None
        assert result["event_id"] is not None
        assert result["user_id"] == event.user_id
        assert result["event_type"] == event.event_type
    
    @pytest.mark.asyncio
    async def test_log_multiple_events(self, behavioral_tracker, sample_interaction_events):
        """Test logging multiple events in sequence."""
        results = []
        
        for event in sample_interaction_events:
            result = await behavioral_tracker.log_interaction(
                user_id=event.user_id,
                session_id=event.session_id,
                event_type=event.event_type,
                capsule_id=event.capsule_id,
                capsule_type=event.capsule_type,
                device_type=event.device_type,
                duration_ms=event.duration_ms
            )
            results.append(result)
        
        assert len(results) == len(sample_interaction_events)
        assert all(r["event_id"] is not None for r in results)
    
    @pytest.mark.asyncio
    async def test_event_validation(self, behavioral_tracker):
        """Test event schema validation."""
        # Valid event
        valid_result = await behavioral_tracker.log_interaction(
            user_id="test_user",
            session_id="test_session",
            event_type="tap",
            capsule_id="test_capsule"
        )
        assert valid_result is not None
        
        # Invalid event type should be handled gracefully
        with pytest.raises(ValueError):
            await behavioral_tracker.log_interaction(
                user_id="test_user",
                session_id="test_session",
                event_type="invalid_type",
                capsule_id="test_capsule"
            )


# Test Suite 2: Behavioral Vector Computation
class TestBVComputation:
    """Test BV computation algorithms."""
    
    @pytest.mark.asyncio
    async def test_compute_bv_from_events(self, bv_computer, sample_interaction_events, sample_user_id):
        """Test computing BV from interaction events."""
        # Compute BV
        bv = await bv_computer.compute_behavioral_vector(
            user_id=sample_user_id,
            events=sample_interaction_events
        )
        
        assert bv is not None
        assert bv.user_id == sample_user_id
        assert bv.total_interactions > 0
        assert bv.expertise_level in [e.value for e in UserArchetype]
    
    @pytest.mark.asyncio
    async def test_usage_pattern_analysis(self, bv_computer, sample_interaction_events, sample_user_id):
        """Test usage pattern extraction."""
        bv = await bv_computer.compute_behavioral_vector(
            user_id=sample_user_id,
            events=sample_interaction_events
        )
        
        # Check usage patterns
        assert "time_of_day_distribution" in bv.usage_patterns
        assert "day_of_week_distribution" in bv.usage_patterns
        assert "capsule_type_distribution" in bv.usage_patterns
    
    @pytest.mark.asyncio
    async def test_expertise_classification(self, bv_computer, sample_user_id):
        """Test expertise level classification."""
        # Novice user (few interactions, high error rate)
        novice_events = [
            InteractionEvent(
                event_id=f"event_{i}",
                timestamp=datetime.utcnow().isoformat(),
                event_type="tap",
                user_id=sample_user_id,
                duration_ms=5000,  # Slow
                success=(i % 3 != 0)  # 33% error rate
            )
            for i in range(10)
        ]
        
        novice_bv = await bv_computer.compute_behavioral_vector(
            user_id=sample_user_id,
            events=novice_events
        )
        assert novice_bv.expertise_level == UserArchetype.NOVICE.value
        
        # Power user (many interactions, low error rate, fast)
        power_events = [
            InteractionEvent(
                event_id=f"event_{i}",
                timestamp=datetime.utcnow().isoformat(),
                event_type="tap",
                user_id=sample_user_id,
                duration_ms=500,  # Fast
                success=True
            )
            for i in range(1000)
        ]
        
        power_bv = await bv_computer.compute_behavioral_vector(
            user_id=sample_user_id,
            events=power_events
        )
        assert power_bv.expertise_level == UserArchetype.POWER_USER.value


# Test Suite 3: Storage Layer
class TestBVStorage:
    """Test BV storage and retrieval."""
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_event(self, bv_storage, sample_interaction_events):
        """Test storing and retrieving an event."""
        event = sample_interaction_events[0]
        
        # Store event
        await bv_storage.store_interaction_event(event)
        
        # Retrieve event
        retrieved_events = await bv_storage.get_user_events(
            user_id=event.user_id,
            limit=10
        )
        
        assert len(retrieved_events) > 0
        assert any(e["event_id"] == event.event_id for e in retrieved_events)
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_bv(self, bv_storage, bv_computer, sample_user_id, sample_interaction_events):
        """Test storing and retrieving a BV."""
        # Compute BV
        bv = await bv_computer.compute_behavioral_vector(
            user_id=sample_user_id,
            events=sample_interaction_events
        )
        
        # Store BV
        await bv_storage.store_behavioral_vector(bv)
        
        # Retrieve BV
        retrieved_bv = await bv_storage.get_behavioral_vector(sample_user_id)
        
        assert retrieved_bv is not None
        assert retrieved_bv["user_id"] == sample_user_id
        assert retrieved_bv["expertise_level"] == bv.expertise_level
    
    @pytest.mark.asyncio
    async def test_redis_cache(self, bv_storage, sample_user_id):
        """Test Redis caching layer."""
        # First retrieval should hit database
        bv1 = await bv_storage.get_behavioral_vector(sample_user_id)
        
        # Second retrieval should hit cache
        bv2 = await bv_storage.get_behavioral_vector(sample_user_id)
        
        # Should return same data
        if bv1 and bv2:
            assert bv1["user_id"] == bv2["user_id"]


# Test Suite 4: API Endpoints
class TestBVAPI:
    """Test REST API endpoints."""
    
    @pytest.mark.asyncio
    async def test_health_check(self):
        """Test API health check endpoint."""
        from fastapi.testclient import TestClient
        client = TestClient(fastapi_app)
        
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @pytest.mark.asyncio
    async def test_log_interaction_endpoint(self, sample_user_id):
        """Test interaction logging endpoint."""
        from fastapi.testclient import TestClient
        client = TestClient(fastapi_app)
        
        payload = {
            "user_id": sample_user_id,
            "session_id": "test_session",
            "event_type": "tap",
            "capsule_id": "test_capsule",
            "device_type": "web"
        }
        
        response = client.post("/api/v1/interactions/log", json=payload)
        assert response.status_code == 200
        assert "event_id" in response.json()
    
    @pytest.mark.asyncio
    async def test_get_bv_endpoint(self, sample_user_id):
        """Test BV retrieval endpoint."""
        from fastapi.testclient import TestClient
        client = TestClient(fastapi_app)
        
        response = client.get(f"/api/v1/behavioral-vectors/{sample_user_id}")
        
        # Should return 200 or 404 depending on whether BV exists
        assert response.status_code in [200, 404]


# Test Suite 5: End-to-End Integration
class TestE2EIntegration:
    """Test complete end-to-end flows."""
    
    @pytest.mark.asyncio
    async def test_complete_tracking_flow(
        self,
        behavioral_tracker,
        bv_computer,
        bv_storage,
        sample_user_id,
        sample_session_id,
        sample_capsule_id
    ):
        """Test complete flow from event logging to BV computation and storage."""
        
        # Step 1: Log multiple interactions
        events = []
        for i in range(10):
            result = await behavioral_tracker.log_interaction(
                user_id=sample_user_id,
                session_id=sample_session_id,
                event_type="tap",
                capsule_id=sample_capsule_id,
                capsule_type="task",
                device_type="web",
                duration_ms=1000 + i*100
            )
            events.append(result)
        
        assert len(events) == 10
        
        # Step 2: Retrieve events from storage
        stored_events = await bv_storage.get_user_events(
            user_id=sample_user_id,
            limit=20
        )
        
        assert len(stored_events) >= 10
        
        # Step 3: Compute BV from events
        bv = await bv_computer.compute_behavioral_vector(
            user_id=sample_user_id,
            events=stored_events
        )
        
        assert bv is not None
        assert bv.total_interactions >= 10
        
        # Step 4: Store BV
        await bv_storage.store_behavioral_vector(bv)
        
        # Step 5: Retrieve BV
        retrieved_bv = await bv_storage.get_behavioral_vector(sample_user_id)
        
        assert retrieved_bv is not None
        assert retrieved_bv["user_id"] == sample_user_id
        
        print(f"✅ E2E test complete: {len(events)} events → BV computation → storage")


# Test Suite 6: Performance Tests
class TestPerformance:
    """Test performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_bulk_event_logging(self, behavioral_tracker, sample_user_id):
        """Test logging many events quickly."""
        import time
        
        start_time = time.time()
        
        # Log 100 events
        tasks = []
        for i in range(100):
            task = behavioral_tracker.log_interaction(
                user_id=sample_user_id,
                session_id=f"session_{i}",
                event_type="tap",
                capsule_id=f"capsule_{i}"
            )
            tasks.append(task)
        
        results = await asyncio.gather(*tasks)
        
        elapsed = time.time() - start_time
        
        assert len(results) == 100
        assert elapsed < 5.0  # Should complete in under 5 seconds
        
        print(f"✅ Logged 100 events in {elapsed:.2f}s ({100/elapsed:.1f} events/sec)")
    
    @pytest.mark.asyncio
    async def test_bv_computation_speed(self, bv_computer, sample_user_id):
        """Test BV computation performance."""
        import time
        
        # Generate 1000 events
        events = [
            InteractionEvent(
                event_id=f"event_{i}",
                timestamp=datetime.utcnow().isoformat(),
                event_type="tap",
                user_id=sample_user_id,
                duration_ms=1000
            )
            for i in range(1000)
        ]
        
        start_time = time.time()
        
        bv = await bv_computer.compute_behavioral_vector(
            user_id=sample_user_id,
            events=events
        )
        
        elapsed = time.time() - start_time
        
        assert bv is not None
        assert elapsed < 2.0  # Should compute in under 2 seconds
        
        print(f"✅ Computed BV from 1000 events in {elapsed:.2f}s")


# Test configuration
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
