"""
Tests for Enhanced WebSocket Server
Production-ready test suite

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch
import jwt

# Import components to test
import sys
sys.path.insert(0, '/home/ubuntu/industriverse/src')

from capsule_layer.websocket_server import WebSocketServer, WebSocketConnection
from capsule_layer.redis_manager import RedisManager


class TestWebSocketServer:
    """Test WebSocket server functionality"""
    
    def test_server_initialization(self):
        """Test WebSocket server initialization"""
        redis = RedisManager()
        server = WebSocketServer(redis)
        
        assert server.redis is not None
        assert server.jwt_secret is not None
        assert server.heartbeat_interval == 30
        assert server.heartbeat_timeout == 60
        assert len(server.connections) == 0
    
    def test_server_custom_configuration(self):
        """Test WebSocket server with custom configuration"""
        redis = RedisManager()
        server = WebSocketServer(
            redis=redis,
            jwt_secret='test-secret',
            jwt_algorithm='HS512',
            heartbeat_interval=15,
            heartbeat_timeout=30
        )
        
        assert server.jwt_secret == 'test-secret'
        assert server.jwt_algorithm == 'HS512'
        assert server.heartbeat_interval == 15
        assert server.heartbeat_timeout == 30
    
    def test_generate_jwt_token(self):
        """Test JWT token generation"""
        redis = RedisManager()
        server = WebSocketServer(redis, jwt_secret='test-secret')
        
        token = server.generate_jwt_token('test_user', 'test_device')
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_verify_jwt_token(self):
        """Test JWT token verification"""
        redis = RedisManager()
        server = WebSocketServer(redis, jwt_secret='test-secret')
        
        # Generate token
        token = server.generate_jwt_token('test_user', 'test_device')
        
        # Verify token
        payload = server.verify_jwt_token(token)
        
        assert payload is not None
        assert payload['user_id'] == 'test_user'
        assert payload['device_token'] == 'test_device'
        assert 'exp' in payload
        assert 'iat' in payload
    
    def test_verify_invalid_token(self):
        """Test verification of invalid token"""
        redis = RedisManager()
        server = WebSocketServer(redis, jwt_secret='test-secret')
        
        # Try to verify invalid token
        payload = server.verify_jwt_token('invalid_token')
        
        assert payload is None
    
    def test_verify_expired_token(self):
        """Test verification of expired token"""
        redis = RedisManager()
        server = WebSocketServer(redis, jwt_secret='test-secret')
        
        # Generate token with 0 expiration (already expired)
        token = server.generate_jwt_token('test_user', expires_in=-1)
        
        # Try to verify expired token
        payload = server.verify_jwt_token(token)
        
        assert payload is None
    
    def test_verify_token_wrong_secret(self):
        """Test verification with wrong secret"""
        redis = RedisManager()
        server1 = WebSocketServer(redis, jwt_secret='secret1')
        server2 = WebSocketServer(redis, jwt_secret='secret2')
        
        # Generate token with server1
        token = server1.generate_jwt_token('test_user')
        
        # Try to verify with server2 (wrong secret)
        payload = server2.verify_jwt_token(token)
        
        assert payload is None
    
    def test_connection_count(self):
        """Test connection counting"""
        redis = RedisManager()
        server = WebSocketServer(redis)
        
        assert server.get_connection_count() == 0
        
        # Add mock connections
        conn1 = WebSocketConnection('conn1', AsyncMock())
        conn2 = WebSocketConnection('conn2', AsyncMock())
        
        server.connections['conn1'] = conn1
        server.connections['conn2'] = conn2
        
        assert server.get_connection_count() == 2
    
    def test_authenticated_count(self):
        """Test authenticated connection counting"""
        redis = RedisManager()
        server = WebSocketServer(redis)
        
        # Add mock connections
        conn1 = WebSocketConnection('conn1', AsyncMock(), authenticated=True)
        conn2 = WebSocketConnection('conn2', AsyncMock(), authenticated=False)
        conn3 = WebSocketConnection('conn3', AsyncMock(), authenticated=True)
        
        server.connections['conn1'] = conn1
        server.connections['conn2'] = conn2
        server.connections['conn3'] = conn3
        
        assert server.get_authenticated_count() == 2
    
    def test_user_connection_count(self):
        """Test user connection counting"""
        redis = RedisManager()
        server = WebSocketServer(redis)
        
        # Add user connections
        server.user_connections['user1'] = {'conn1', 'conn2'}
        server.user_connections['user2'] = {'conn3'}
        
        assert server.get_user_connection_count('user1') == 2
        assert server.get_user_connection_count('user2') == 1
        assert server.get_user_connection_count('user3') == 0
    
    def test_device_online_status(self):
        """Test device online status checking"""
        redis = RedisManager()
        server = WebSocketServer(redis)
        
        # Add device connection
        server.device_connections['device1'] = 'conn1'
        
        assert server.is_device_online('device1') is True
        assert server.is_device_online('device2') is False
    
    def test_statistics(self):
        """Test server statistics"""
        redis = RedisManager()
        server = WebSocketServer(redis)
        
        # Add mock data
        conn1 = WebSocketConnection('conn1', AsyncMock(), user_id='user1', authenticated=True)
        conn2 = WebSocketConnection('conn2', AsyncMock(), user_id='user2', authenticated=True)
        
        server.connections['conn1'] = conn1
        server.connections['conn2'] = conn2
        server.user_connections['user1'] = {'conn1'}
        server.user_connections['user2'] = {'conn2'}
        server.device_connections['device1'] = 'conn1'
        server.message_queue['device2'] = [{'msg': 1}, {'msg': 2}]
        
        stats = server.get_statistics()
        
        assert stats['total_connections'] == 2
        assert stats['authenticated_connections'] == 2
        assert stats['unique_users'] == 2
        assert stats['unique_devices'] == 1
        assert stats['queued_messages'] == 2
        assert 'timestamp' in stats
    
    @pytest.mark.asyncio
    async def test_broadcast_to_all(self):
        """Test broadcasting to all connections"""
        redis = RedisManager()
        redis.client = AsyncMock()
        server = WebSocketServer(redis)
        
        # Add mock connections
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        
        conn1 = WebSocketConnection('conn1', ws1)
        conn2 = WebSocketConnection('conn2', ws2)
        
        server.connections['conn1'] = conn1
        server.connections['conn2'] = conn2
        
        # Broadcast message
        message = {'type': 'test', 'data': 'hello'}
        await server.broadcast_to_all(message)
        
        # Verify both connections received message
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)
    
    @pytest.mark.asyncio
    async def test_broadcast_to_user(self):
        """Test broadcasting to specific user"""
        redis = RedisManager()
        redis.client = AsyncMock()
        server = WebSocketServer(redis)
        
        # Add mock connections
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        ws3 = AsyncMock()
        
        conn1 = WebSocketConnection('conn1', ws1, user_id='user1')
        conn2 = WebSocketConnection('conn2', ws2, user_id='user1')
        conn3 = WebSocketConnection('conn3', ws3, user_id='user2')
        
        server.connections['conn1'] = conn1
        server.connections['conn2'] = conn2
        server.connections['conn3'] = conn3
        
        server.user_connections['user1'] = {'conn1', 'conn2'}
        server.user_connections['user2'] = {'conn3'}
        
        # Broadcast to user1
        message = {'type': 'test', 'data': 'hello'}
        await server.broadcast_to_user('user1', message)
        
        # Verify only user1's connections received message
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)
        ws3.send_json.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_send_to_device_online(self):
        """Test sending to online device"""
        redis = RedisManager()
        redis.client = AsyncMock()
        server = WebSocketServer(redis)
        
        # Add mock connection
        ws = AsyncMock()
        conn = WebSocketConnection('conn1', ws, device_token='device1')
        
        server.connections['conn1'] = conn
        server.device_connections['device1'] = 'conn1'
        
        # Send message
        message = {'type': 'test', 'data': 'hello'}
        await server.send_to_device('device1', message)
        
        # Verify device received message
        ws.send_json.assert_called_once_with(message)
        
        # Verify message not queued
        assert 'device1' not in server.message_queue
    
    @pytest.mark.asyncio
    async def test_send_to_device_offline(self):
        """Test sending to offline device (queuing)"""
        redis = RedisManager()
        redis.client = AsyncMock()
        server = WebSocketServer(redis)
        
        # Send message to offline device
        message = {'type': 'test', 'data': 'hello'}
        await server.send_to_device('device1', message, queue_if_offline=True)
        
        # Verify message queued
        assert 'device1' in server.message_queue
        assert len(server.message_queue['device1']) == 1
        assert server.message_queue['device1'][0] == message
    
    @pytest.mark.asyncio
    async def test_send_to_device_offline_no_queue(self):
        """Test sending to offline device without queuing"""
        redis = RedisManager()
        redis.client = AsyncMock()
        server = WebSocketServer(redis)
        
        # Send message to offline device (no queue)
        message = {'type': 'test', 'data': 'hello'}
        await server.send_to_device('device1', message, queue_if_offline=False)
        
        # Verify message not queued
        assert 'device1' not in server.message_queue
    
    @pytest.mark.asyncio
    async def test_broadcast_to_devices(self):
        """Test broadcasting to multiple devices"""
        redis = RedisManager()
        redis.client = AsyncMock()
        server = WebSocketServer(redis)
        
        # Add mock connections
        ws1 = AsyncMock()
        ws2 = AsyncMock()
        
        conn1 = WebSocketConnection('conn1', ws1, device_token='device1')
        conn2 = WebSocketConnection('conn2', ws2, device_token='device2')
        
        server.connections['conn1'] = conn1
        server.connections['conn2'] = conn2
        server.device_connections['device1'] = 'conn1'
        server.device_connections['device2'] = 'conn2'
        
        # Broadcast to devices
        message = {'type': 'test', 'data': 'hello'}
        await server.broadcast_to_devices(['device1', 'device2', 'device3'], message)
        
        # Verify online devices received message
        ws1.send_json.assert_called_once_with(message)
        ws2.send_json.assert_called_once_with(message)
        
        # Verify offline device message queued
        assert 'device3' in server.message_queue


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
