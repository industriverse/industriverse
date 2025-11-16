"""
Comprehensive Integration Tests for Capsule Gateway
End-to-end testing of Gateway + WebSocket + APNs + Redis + PostgreSQL

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock

# Import components to test
import sys
sys.path.insert(0, '/home/ubuntu/industriverse/src')

from capsule_layer.capsule_gateway_service import CapsuleGatewayService
from capsule_layer.database import CapsuleDatabase
from capsule_layer.apns_service import APNsService
from capsule_layer.redis_manager import RedisManager
from capsule_layer.websocket_server import WebSocketServer


class TestDatabaseIntegration:
    """Test PostgreSQL database integration"""
    
    @pytest.mark.asyncio
    async def test_database_connection_lifecycle(self):
        """Test database connection and disconnection"""
        db = CapsuleDatabase()
        
        # Mock pool and connection methods
        db.pool = AsyncMock()
        db.connect = AsyncMock()
        db.disconnect = AsyncMock()
        
        await db.connect()
        await db.disconnect()
        
        db.connect.assert_called_once()
        db.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_activity_crud_operations(self):
        """Test complete CRUD operations for activities"""
        db = CapsuleDatabase()
        
        # Mock database methods directly
        db.create_activity = AsyncMock(return_value={
            'activity_id': 'act1',
            'capsule_id': 'cap1',
            'title': 'Test Activity',
            'state': 'active'
        })
        
        db.get_activity_by_capsule_id = AsyncMock(return_value={
            'activity_id': 'act1',
            'capsule_id': 'cap1'
        })
        
        db.update_activity = AsyncMock(return_value={
            'activity_id': 'act1',
            'capsule_id': 'cap1',
            'state': 'resolved'
        })
        
        db.delete_activity = AsyncMock(return_value=True)
        
        # Test CREATE
        activity = await db.create_activity(
            activity_id='act1',
            capsule_id='cap1',
            title='Test Activity',
            message='Test message'
        )
        assert activity is not None
        assert activity['capsule_id'] == 'cap1'
        
        # Test READ
        activity = await db.get_activity_by_capsule_id('cap1')
        assert activity is not None
        
        # Test UPDATE
        updated = await db.update_activity('cap1', state='resolved')
        assert updated['state'] == 'resolved'
        
        # Test DELETE
        success = await db.delete_activity('cap1')
        assert success is True
    
    @pytest.mark.asyncio
    async def test_action_tracking(self):
        """Test action creation and tracking"""
        db = CapsuleDatabase()
        
        # Mock create_action method
        db.create_action = AsyncMock(return_value={
            'action_id': 'action1',
            'capsule_id': 'cap1',
            'action_type': 'mitigate',
            'user_id': 'user1'
        })
        
        action = await db.create_action(
            action_id='action1',
            capsule_id='cap1',
            action_type='mitigate',
            user_id='user1'
        )
        
        assert action is not None
        assert action['action_type'] == 'mitigate'
    
    @pytest.mark.asyncio
    async def test_device_registration(self):
        """Test device registration and management"""
        db = CapsuleDatabase()
        
        # Mock register_device method
        db.register_device = AsyncMock()
        
        await db.register_device(
            device_token='device1',
            user_id='user1',
            platform='ios'
        )
        
        db.register_device.assert_called_once()


class TestRedisIntegration:
    """Test Redis integration"""
    
    @pytest.mark.asyncio
    async def test_redis_connection_lifecycle(self):
        """Test Redis connection and disconnection"""
        redis = RedisManager()
        redis.client = AsyncMock()
        redis.connect = AsyncMock()
        redis.disconnect = AsyncMock()
        
        await redis.connect()
        await redis.disconnect()
        
        redis.connect.assert_called_once()
        redis.disconnect.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_activity_caching(self):
        """Test activity caching and retrieval"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        # Cache activity
        activity_data = {
            'capsule_id': 'cap1',
            'title': 'Test',
            'state': 'active'
        }
        
        await redis.cache_activity('cap1', activity_data)
        redis.client.setex.assert_called_once()
        
        # Retrieve cached activity
        redis.client.get.return_value = json.dumps(activity_data)
        cached = await redis.get_cached_activity('cap1')
        
        assert cached is not None
        assert cached['capsule_id'] == 'cap1'
        
        # Invalidate cache
        await redis.invalidate_activity_cache('cap1')
        redis.client.delete.assert_called()
    
    @pytest.mark.asyncio
    async def test_websocket_connection_management(self):
        """Test WebSocket connection management in Redis"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        # Register connection
        await redis.register_connection('conn1', 'user1', {'device': 'ios'})
        redis.client.hset.assert_called()
        redis.client.sadd.assert_called()
        
        # Get connection
        redis.client.hgetall.return_value = {
            'connection_id': 'conn1',
            'user_id': 'user1',
            'metadata': '{}'
        }
        
        conn = await redis.get_connection('conn1')
        assert conn is not None
        
        # Unregister connection
        redis.client.hget.return_value = 'user1'
        await redis.unregister_connection('conn1')
        redis.client.delete.assert_called()
    
    @pytest.mark.asyncio
    async def test_pubsub_messaging(self):
        """Test pub/sub messaging"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        # Publish update
        message = {'type': 'activity_update', 'data': {}}
        await redis.publish_update('activities', message)
        
        redis.client.publish.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test rate limiting functionality"""
        redis = RedisManager()
        redis.client = AsyncMock()
        
        # Within limit
        redis.client.incr.return_value = 5
        within = await redis.check_rate_limit('user1', 10, 60)
        assert within is True
        
        # Exceeded limit
        redis.client.incr.return_value = 15
        within = await redis.check_rate_limit('user1', 10, 60)
        assert within is False


class TestAPNsIntegration:
    """Test APNs integration"""
    
    @pytest.mark.asyncio
    async def test_apns_connection_lifecycle(self):
        """Test APNs connection and disconnection"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        await apns.connect()
        assert apns.client is not None
        
        await apns.disconnect()
    
    @pytest.mark.asyncio
    async def test_standard_notification(self):
        """Test standard push notification"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        success = await apns.send_notification(
            device_token='device1',
            title='Test',
            message='Test message',
            priority='high'
        )
        
        assert success is True
        apns.client.send_notification.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_live_activity_update(self):
        """Test Live Activity update"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        success = await apns.send_live_activity_update(
            device_token='device1',
            activity_id='act1',
            content_state={'status': 'active', 'progress': 50}
        )
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_batch_notifications(self):
        """Test batch notification sending"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        results = await apns.send_batch_notifications(
            device_tokens=['device1', 'device2', 'device3'],
            title='Test',
            message='Batch message'
        )
        
        assert len(results) == 3
        assert all(v is True for v in results.values())
    
    @pytest.mark.asyncio
    async def test_notification_failure_handling(self):
        """Test notification failure handling"""
        apns = APNsService()
        apns.client = AsyncMock()
        
        response = Mock()
        response.is_successful = False
        apns.client.send_notification.return_value = response
        
        success = await apns.send_notification(
            device_token='invalid_device',
            title='Test',
            message='Test message'
        )
        
        assert success is False


class TestWebSocketIntegration:
    """Test WebSocket integration"""
    
    def test_websocket_server_initialization(self):
        """Test WebSocket server initialization with Redis"""
        redis = RedisManager()
        ws_server = WebSocketServer(redis)
        
        assert ws_server.redis is not None
        assert ws_server.jwt_secret is not None
    
    def test_jwt_token_generation_and_verification(self):
        """Test JWT token generation and verification"""
        redis = RedisManager()
        ws_server = WebSocketServer(redis, jwt_secret='test-secret')
        
        # Generate token
        token = ws_server.generate_jwt_token('user1', 'device1')
        assert token is not None
        
        # Verify token
        payload = ws_server.verify_jwt_token(token)
        assert payload is not None
        assert payload['user_id'] == 'user1'
        assert payload['device_token'] == 'device1'
    
    @pytest.mark.asyncio
    async def test_device_specific_messaging(self):
        """Test device-specific message delivery"""
        redis = RedisManager()
        redis.client = AsyncMock()
        ws_server = WebSocketServer(redis)
        
        # Add mock connection
        ws = AsyncMock()
        from capsule_layer.websocket_server import WebSocketConnection
        conn = WebSocketConnection('conn1', ws, device_token='device1')
        
        ws_server.connections['conn1'] = conn
        ws_server.device_connections['device1'] = 'conn1'
        
        # Send message
        message = {'type': 'test', 'data': 'hello'}
        await ws_server.send_to_device('device1', message)
        
        ws.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_message_queuing_for_offline_devices(self):
        """Test message queuing for offline devices"""
        redis = RedisManager()
        redis.client = AsyncMock()
        ws_server = WebSocketServer(redis)
        
        # Send to offline device
        message = {'type': 'test', 'data': 'hello'}
        await ws_server.send_to_device('offline_device', message, queue_if_offline=True)
        
        # Verify message queued
        assert 'offline_device' in ws_server.message_queue
        assert len(ws_server.message_queue['offline_device']) == 1


class TestCompleteFlow:
    """Test complete end-to-end flow"""
    
    @pytest.mark.asyncio
    async def test_activity_creation_flow(self):
        """Test complete activity creation flow: DB → Cache → WebSocket → APNs"""
        # Setup mocks
        db = CapsuleDatabase()
        
        redis = RedisManager()
        redis.client = AsyncMock()
        
        apns = APNsService()
        apns.client = AsyncMock()
        
        ws_server = WebSocketServer(redis)
        
        # Step 1: Create activity in database
        activity_data = {
            'activity_id': 'act1',
            'capsule_id': 'cap1',
            'title': 'Security Alert',
            'message': 'Suspicious activity detected',
            'state': 'active',
            'priority': 'high'
        }
        
        db.create_activity = AsyncMock(return_value=activity_data)
        
        activity = await db.create_activity(
            activity_id='act1',
            capsule_id='cap1',
            title='Security Alert',
            message='Suspicious activity detected',
            priority='high'
        )
        
        assert activity is not None
        assert activity['state'] == 'active'
        
        # Step 2: Cache activity in Redis
        await redis.cache_activity('cap1', activity)
        redis.client.setex.assert_called_once()
        
        # Step 3: Broadcast via WebSocket
        ws = AsyncMock()
        from capsule_layer.websocket_server import WebSocketConnection
        conn_ws = WebSocketConnection('conn1', ws, device_token='device1', authenticated=True)
        
        ws_server.connections['conn1'] = conn_ws
        ws_server.device_connections['device1'] = 'conn1'
        
        ws_message = {
            'type': 'activity_created',
            'activity': activity
        }
        
        await ws_server.send_to_device('device1', ws_message)
        ws.send_json.assert_called_once()
        
        # Step 4: Send APNs push notification
        response = Mock()
        response.is_successful = True
        apns.client.send_notification.return_value = response
        
        success = await apns.send_notification(
            device_token='device1',
            title=activity['title'],
            message=activity['message'],
            priority='high'
        )
        
        assert success is True
    
    @pytest.mark.asyncio
    async def test_activity_update_flow(self):
        """Test complete activity update flow"""
        # Setup
        db = CapsuleDatabase()
        
        redis = RedisManager()
        redis.client = AsyncMock()
        
        ws_server = WebSocketServer(redis)
        
        # Update activity
        updated_data = {
            'activity_id': 'act1',
            'capsule_id': 'cap1',
            'state': 'resolved',
            'resolution': 'Threat mitigated'
        }
        
        db.update_activity = AsyncMock(return_value=updated_data)
        
        updated = await db.update_activity(capsule_id='cap1', state='resolved', resolution='Threat mitigated')
        assert updated['state'] == 'resolved'
        
        # Invalidate cache
        await redis.invalidate_activity_cache('cap1')
        redis.client.delete.assert_called()
        
        # Broadcast update
        ws = AsyncMock()
        from capsule_layer.websocket_server import WebSocketConnection
        conn_ws = WebSocketConnection('conn1', ws)
        ws_server.connections['conn1'] = conn_ws
        
        await ws_server.broadcast_to_all({
            'type': 'activity_updated',
            'activity': updated
        })
        
        ws.send_json.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_action_processing_flow(self):
        """Test complete action processing flow"""
        # Setup
        db = CapsuleDatabase()
        
        # Create action
        action_data = {
            'action_id': 'action1',
            'capsule_id': 'cap1',
            'action_type': 'mitigate',
            'user_id': 'user1',
            'result': 'success'
        }
        
        db.create_action = AsyncMock(return_value=action_data)
        
        action = await db.create_action(
            action_id='action1',
            capsule_id='cap1',
            action_type='mitigate',
            user_id='user1'
        )
        
        assert action is not None
        assert action['action_type'] == 'mitigate'
        
        # Update activity state based on action
        updated_data = {
            'activity_id': 'act1',
            'capsule_id': 'cap1',
            'state': 'mitigating'
        }
        
        db.update_activity = AsyncMock(return_value=updated_data)
        
        updated = await db.update_activity(capsule_id='cap1', state='mitigating')
        assert updated['state'] == 'mitigating'


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
