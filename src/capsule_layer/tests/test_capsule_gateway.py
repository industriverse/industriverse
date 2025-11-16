"""
Tests for Capsule Gateway Service
Production-ready test suite

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import json

# Import components to test
import sys
sys.path.insert(0, '/home/ubuntu/industriverse/src')

from capsule_layer.database import CapsuleDatabase
from capsule_layer.apns_service import APNsService
from capsule_layer.redis_manager import RedisManager


class TestCapsuleDatabase:
    """Test PostgreSQL database operations"""
    
    def test_database_initialization(self):
        """Test database initialization"""
        db = CapsuleDatabase()
        
        assert db.host is not None
        assert db.port is not None
        assert db.database is not None
        assert db.user is not None
    
    def test_database_connection_string(self):
        """Test database connection parameters"""
        db = CapsuleDatabase(
            host='testhost',
            port=5433,
            database='testdb',
            user='testuser'
        )
        
        assert db.host == 'testhost'
        assert db.port == 5433
        assert db.database == 'testdb'
        assert db.user == 'testuser'


class TestAPNsService:
    """Test APNs push notification service"""
    
    def test_apns_initialization(self):
        """Test APNs service initialization"""
        apns = APNsService()
        
        assert apns.topic is not None
        assert isinstance(apns.use_sandbox, bool)
    
    def test_apns_configuration(self):
        """Test APNs configuration"""
        apns = APNsService(
            topic='com.test.app',
            use_sandbox=True
        )
        
        assert apns.topic == 'com.test.app'
        assert apns.use_sandbox is True
    
    @pytest.mark.asyncio
    async def test_send_notification_without_client(self):
        """Test sending notification without connected client"""
        apns = APNsService()
        apns.client = None
        
        success = await apns.send_notification(
            device_token='test_token',
            title='Test',
            message='Test message'
        )
        
        # Should return False when client not connected
        assert success is False
    
    @pytest.mark.asyncio
    async def test_send_notification_with_mock_client(self):
        """Test sending notification with mocked client"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        # Mock successful response
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        success = await apns.send_notification(
            device_token='test_token',
            title='Test',
            message='Test message'
        )
        
        assert success is True
        apns.client.send_notification.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_send_batch_notifications(self):
        """Test sending batch notifications"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        results = await apns.send_batch_notifications(
            device_tokens=['token1', 'token2', 'token3'],
            title='Test',
            message='Test message'
        )
        
        assert len(results) == 3
        assert all(v is True for v in results.values())
    
    @pytest.mark.asyncio
    async def test_send_live_activity_update(self):
        """Test sending Live Activity update"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        success = await apns.send_live_activity_update(
            device_token='test_token',
            activity_id='test_activity',
            content_state={'status': 'active'}
        )
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_end_live_activity(self):
        """Test ending a Live Activity"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        success = await apns.end_live_activity(
            device_token='test_token',
            activity_id='test_activity',
            final_content_state={'status': 'resolved'}
        )
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_notification_priority_levels(self):
        """Test different notification priority levels"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        # Test critical priority
        success = await apns.send_notification(
            device_token='test_token',
            title='Critical',
            message='Critical message',
            priority='critical'
        )
        assert success is True
        
        # Test high priority
        success = await apns.send_notification(
            device_token='test_token',
            title='High',
            message='High message',
            priority='high'
        )
        assert success is True


class TestRedisManager:
    """Test Redis session manager"""
    
    def test_redis_initialization(self):
        """Test Redis manager initialization"""
        redis = RedisManager()
        
        assert redis.host is not None
        assert redis.port is not None
        assert redis.db == 0
    
    def test_redis_configuration(self):
        """Test Redis configuration"""
        redis = RedisManager(
            host='testhost',
            port=6380,
            db=1
        )
        
        assert redis.host == 'testhost'
        assert redis.port == 6380
        assert redis.db == 1
    
    @pytest.mark.asyncio
    async def test_register_connection(self):
        """Test registering a WebSocket connection"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        await redis.register_connection('test_conn', 'test_user')
        
        redis.client.hset.assert_called_once()
        redis.client.sadd.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unregister_connection(self):
        """Test unregistering a connection"""
        redis = RedisManager()
        redis.client = AsyncMock()
        redis.client.hget.return_value = 'test_user'
        
        await redis.unregister_connection('test_conn')
        
        redis.client.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_connection(self):
        """Test getting connection info"""
        redis = RedisManager()
        redis.client = AsyncMock()
        redis.client.hgetall.return_value = {
            'connection_id': 'test_conn',
            'user_id': 'test_user',
            'metadata': '{}'
        }
        
        conn = await redis.get_connection('test_conn')
        
        assert conn is not None
        assert conn['connection_id'] == 'test_conn'
    
    @pytest.mark.asyncio
    async def test_cache_activity(self):
        """Test caching activity data"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        await redis.cache_activity('test_capsule', {'data': 'test'})
        
        redis.client.setex.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_cached_activity(self):
        """Test getting cached activity"""
        redis = RedisManager()
        redis.client = AsyncMock()
        redis.client.get.return_value = '{"data": "test"}'
        
        activity = await redis.get_cached_activity('test_capsule')
        
        assert activity is not None
        assert activity['data'] == 'test'
    
    @pytest.mark.asyncio
    async def test_invalidate_cache(self):
        """Test cache invalidation"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        await redis.invalidate_activity_cache('test_capsule')
        
        redis.client.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_publish_update(self):
        """Test publishing update to channel"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        await redis.publish_update('test_channel', {'type': 'update'})
        
        redis.client.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting"""
        redis = RedisManager()
        redis.client = AsyncMock()
        redis.client.incr.return_value = 5
        
        within_limit = await redis.check_rate_limit('test_key', 10, 60)
        
        assert within_limit is True
    
    @pytest.mark.asyncio
    async def test_rate_limit_exceeded(self):
        """Test rate limit exceeded"""
        redis = RedisManager()
        redis.client = AsyncMock()
        redis.client.incr.return_value = 15
        
        within_limit = await redis.check_rate_limit('test_key', 10, 60)
        
        assert within_limit is False
    
    @pytest.mark.asyncio
    async def test_session_creation(self):
        """Test session creation"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        await redis.create_session('test_session', 'test_user', {'key': 'value'})
        
        redis.client.hset.assert_called_once()
        redis.client.expire.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_session_deletion(self):
        """Test session deletion"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        await redis.delete_session('test_session')
        
        redis.client.delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_user_connections(self):
        """Test getting user connections"""
        redis = RedisManager()
        redis.client = AsyncMock()
        redis.client.smembers.return_value = {'conn1', 'conn2'}
        
        connections = await redis.get_user_connections('test_user')
        
        assert len(connections) == 2


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
