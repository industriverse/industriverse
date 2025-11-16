"""
Enhanced WebSocket Server
Production-ready WebSocket server with authentication, heartbeat, and device-specific broadcasting

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import asyncio
import json
import time
import jwt
import os
from typing import Dict, Set, Optional, List
from dataclasses import dataclass, field
from fastapi import WebSocket, WebSocketDisconnect, status
from datetime import datetime, timedelta

from .redis_manager import RedisManager


@dataclass
class WebSocketConnection:
    """WebSocket connection metadata"""
    connection_id: str
    websocket: WebSocket
    user_id: Optional[str] = None
    device_token: Optional[str] = None
    device_type: str = "unknown"  # ios, android, web
    authenticated: bool = False
    connected_at: float = field(default_factory=time.time)
    last_ping: float = field(default_factory=time.time)
    last_pong: float = field(default_factory=time.time)
    metadata: Dict = field(default_factory=dict)


class WebSocketServer:
    """
    Production WebSocket Server
    
    Features:
    - JWT authentication
    - Heartbeat/ping-pong mechanism
    - Device-specific broadcasting
    - Connection pooling and management
    - Message queuing for offline devices
    - Automatic reconnection handling
    """
    
    def __init__(
        self,
        redis: RedisManager,
        jwt_secret: Optional[str] = None,
        jwt_algorithm: str = "HS256",
        heartbeat_interval: int = 30,
        heartbeat_timeout: int = 60
    ):
        """
        Initialize WebSocket server
        
        Args:
            redis: Redis manager for session management
            jwt_secret: JWT secret key (default: from env)
            jwt_algorithm: JWT algorithm (default: HS256)
            heartbeat_interval: Heartbeat interval in seconds (default: 30)
            heartbeat_timeout: Heartbeat timeout in seconds (default: 60)
        """
        self.redis = redis
        self.jwt_secret = jwt_secret or os.getenv('JWT_SECRET', 'industriverse-secret-key')
        self.jwt_algorithm = jwt_algorithm
        self.heartbeat_interval = heartbeat_interval
        self.heartbeat_timeout = heartbeat_timeout
        
        # Connection pools
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[str, Set[str]] = {}  # user_id -> connection_ids
        self.device_connections: Dict[str, str] = {}  # device_token -> connection_id
        
        # Message queue for offline devices
        self.message_queue: Dict[str, List[Dict]] = {}  # device_token -> messages
        
        # Heartbeat task
        self.heartbeat_task: Optional[asyncio.Task] = None
        
        print("✅ WebSocket Server initialized")
    
    def generate_jwt_token(
        self,
        user_id: str,
        device_token: Optional[str] = None,
        expires_in: int = 86400
    ) -> str:
        """
        Generate JWT token for WebSocket authentication
        
        Args:
            user_id: User identifier
            device_token: Device token (optional)
            expires_in: Token expiration in seconds (default: 24 hours)
            
        Returns:
            JWT token string
        """
        payload = {
            'user_id': user_id,
            'device_token': device_token,
            'exp': datetime.utcnow() + timedelta(seconds=expires_in),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """
        Verify JWT token
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload if valid, None otherwise
        """
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            print("❌ JWT token expired")
            return None
        except jwt.InvalidTokenError as e:
            print(f"❌ Invalid JWT token: {e}")
            return None
    
    async def handle_connection(
        self,
        websocket: WebSocket,
        connection_id: str
    ):
        """
        Handle WebSocket connection
        
        Args:
            websocket: WebSocket connection
            connection_id: Unique connection identifier
        """
        connection = WebSocketConnection(
            connection_id=connection_id,
            websocket=websocket
        )
        
        try:
            await websocket.accept()
            
            # Store connection
            self.connections[connection_id] = connection
            
            # Register in Redis
            await self.redis.register_connection(connection_id)
            
            print(f"✅ WebSocket connected: {connection_id}")
            
            # Send welcome message
            await self._send_message(connection, {
                'type': 'connected',
                'connection_id': connection_id,
                'timestamp': time.time(),
                'message': 'Please authenticate with JWT token'
            })
            
            # Start heartbeat for this connection
            asyncio.create_task(self._connection_heartbeat(connection))
            
            # Handle messages
            while True:
                try:
                    data = await websocket.receive_text()
                    await self._handle_message(connection, data)
                
                except WebSocketDisconnect:
                    break
                except Exception as e:
                    print(f"❌ Error handling message: {e}")
                    break
        
        finally:
            await self._disconnect(connection)
    
    async def _handle_message(self, connection: WebSocketConnection, data: str):
        """Handle incoming WebSocket message"""
        try:
            message = json.loads(data)
            message_type = message.get('type')
            
            if message_type == 'auth':
                await self._handle_auth(connection, message)
            
            elif message_type == 'ping':
                await self._handle_ping(connection)
            
            elif message_type == 'pong':
                await self._handle_pong(connection)
            
            elif message_type == 'subscribe':
                await self._handle_subscribe(connection, message)
            
            elif message_type == 'unsubscribe':
                await self._handle_unsubscribe(connection, message)
            
            else:
                await self._send_message(connection, {
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                })
        
        except json.JSONDecodeError:
            await self._send_message(connection, {
                'type': 'error',
                'message': 'Invalid JSON'
            })
        except Exception as e:
            print(f"❌ Error handling message: {e}")
            await self._send_message(connection, {
                'type': 'error',
                'message': str(e)
            })
    
    async def _handle_auth(self, connection: WebSocketConnection, message: Dict):
        """Handle authentication message"""
        token = message.get('token')
        
        if not token:
            await self._send_message(connection, {
                'type': 'auth_error',
                'message': 'Token required'
            })
            return
        
        # Verify token
        payload = self.verify_jwt_token(token)
        
        if not payload:
            await self._send_message(connection, {
                'type': 'auth_error',
                'message': 'Invalid or expired token'
            })
            return
        
        # Update connection
        connection.user_id = payload.get('user_id')
        connection.device_token = payload.get('device_token')
        connection.device_type = message.get('device_type', 'unknown')
        connection.authenticated = True
        connection.metadata = message.get('metadata', {})
        
        # Add to user connections
        if connection.user_id:
            if connection.user_id not in self.user_connections:
                self.user_connections[connection.user_id] = set()
            self.user_connections[connection.user_id].add(connection.connection_id)
        
        # Add to device connections
        if connection.device_token:
            self.device_connections[connection.device_token] = connection.connection_id
        
        # Update Redis
        await self.redis.register_connection(
            connection.connection_id,
            user_id=connection.user_id,
            metadata={
                'device_token': connection.device_token,
                'device_type': connection.device_type,
                **connection.metadata
            }
        )
        
        print(f"✅ Authenticated: {connection.connection_id} (user: {connection.user_id})")
        
        # Send success
        await self._send_message(connection, {
            'type': 'auth_success',
            'user_id': connection.user_id,
            'connection_id': connection.connection_id,
            'timestamp': time.time()
        })
        
        # Send queued messages
        if connection.device_token and connection.device_token in self.message_queue:
            queued = self.message_queue[connection.device_token]
            for msg in queued:
                await self._send_message(connection, msg)
            del self.message_queue[connection.device_token]
            print(f"📬 Sent {len(queued)} queued messages to {connection.device_token}")
    
    async def _handle_ping(self, connection: WebSocketConnection):
        """Handle ping message"""
        connection.last_ping = time.time()
        await self._send_message(connection, {
            'type': 'pong',
            'timestamp': time.time()
        })
    
    async def _handle_pong(self, connection: WebSocketConnection):
        """Handle pong message"""
        connection.last_pong = time.time()
    
    async def _handle_subscribe(self, connection: WebSocketConnection, message: Dict):
        """Handle subscribe message"""
        channels = message.get('channels', [])
        
        # Store subscriptions in metadata
        if 'subscriptions' not in connection.metadata:
            connection.metadata['subscriptions'] = set()
        
        connection.metadata['subscriptions'].update(channels)
        
        await self._send_message(connection, {
            'type': 'subscribed',
            'channels': list(connection.metadata['subscriptions']),
            'timestamp': time.time()
        })
    
    async def _handle_unsubscribe(self, connection: WebSocketConnection, message: Dict):
        """Handle unsubscribe message"""
        channels = message.get('channels', [])
        
        if 'subscriptions' in connection.metadata:
            connection.metadata['subscriptions'].difference_update(channels)
        
        await self._send_message(connection, {
            'type': 'unsubscribed',
            'channels': channels,
            'timestamp': time.time()
        })
    
    async def _connection_heartbeat(self, connection: WebSocketConnection):
        """Heartbeat for a specific connection"""
        while connection.connection_id in self.connections:
            try:
                # Check if connection is alive
                time_since_pong = time.time() - connection.last_pong
                
                if time_since_pong > self.heartbeat_timeout:
                    print(f"⚠️  Connection timeout: {connection.connection_id}")
                    await self._disconnect(connection)
                    break
                
                # Send ping
                await self._send_message(connection, {
                    'type': 'ping',
                    'timestamp': time.time()
                })
                
                await asyncio.sleep(self.heartbeat_interval)
            
            except Exception as e:
                print(f"❌ Heartbeat error: {e}")
                break
    
    async def _send_message(self, connection: WebSocketConnection, message: Dict):
        """Send message to a connection"""
        try:
            await connection.websocket.send_json(message)
        except Exception as e:
            print(f"❌ Error sending message to {connection.connection_id}: {e}")
            await self._disconnect(connection)
    
    async def _disconnect(self, connection: WebSocketConnection):
        """Disconnect a connection"""
        connection_id = connection.connection_id
        
        # Remove from connections
        if connection_id in self.connections:
            del self.connections[connection_id]
        
        # Remove from user connections
        if connection.user_id and connection.user_id in self.user_connections:
            self.user_connections[connection.user_id].discard(connection_id)
            if not self.user_connections[connection.user_id]:
                del self.user_connections[connection.user_id]
        
        # Remove from device connections
        if connection.device_token and connection.device_token in self.device_connections:
            del self.device_connections[connection.device_token]
        
        # Unregister from Redis
        await self.redis.unregister_connection(connection_id)
        
        print(f"✅ WebSocket disconnected: {connection_id}")
    
    async def broadcast_to_all(self, message: Dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        
        for connection_id, connection in self.connections.items():
            try:
                await self._send_message(connection, message)
            except Exception as e:
                print(f"❌ Error broadcasting to {connection_id}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected
        for connection in disconnected:
            await self._disconnect(connection)
    
    async def broadcast_to_user(self, user_id: str, message: Dict):
        """Broadcast message to all connections of a specific user"""
        if user_id not in self.user_connections:
            print(f"⚠️  No connections for user: {user_id}")
            return
        
        connection_ids = list(self.user_connections[user_id])
        
        for connection_id in connection_ids:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                await self._send_message(connection, message)
    
    async def send_to_device(self, device_token: str, message: Dict, queue_if_offline: bool = True):
        """
        Send message to a specific device
        
        Args:
            device_token: Device token
            message: Message to send
            queue_if_offline: Queue message if device is offline (default: True)
        """
        if device_token in self.device_connections:
            connection_id = self.device_connections[device_token]
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                await self._send_message(connection, message)
                return
        
        # Device offline
        if queue_if_offline:
            if device_token not in self.message_queue:
                self.message_queue[device_token] = []
            self.message_queue[device_token].append(message)
            print(f"📬 Queued message for offline device: {device_token}")
    
    async def broadcast_to_devices(self, device_tokens: List[str], message: Dict):
        """Broadcast message to multiple devices"""
        for device_token in device_tokens:
            await self.send_to_device(device_token, message)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.connections)
    
    def get_authenticated_count(self) -> int:
        """Get number of authenticated connections"""
        return sum(1 for c in self.connections.values() if c.authenticated)
    
    def get_user_connection_count(self, user_id: str) -> int:
        """Get number of connections for a specific user"""
        return len(self.user_connections.get(user_id, set()))
    
    def is_device_online(self, device_token: str) -> bool:
        """Check if a device is online"""
        return device_token in self.device_connections
    
    def get_statistics(self) -> Dict:
        """Get WebSocket server statistics"""
        return {
            'total_connections': len(self.connections),
            'authenticated_connections': self.get_authenticated_count(),
            'unique_users': len(self.user_connections),
            'unique_devices': len(self.device_connections),
            'queued_messages': sum(len(msgs) for msgs in self.message_queue.values()),
            'timestamp': time.time()
        }
