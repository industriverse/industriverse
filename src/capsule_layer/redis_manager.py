"""
Redis Session Manager
Production-ready Redis integration for WebSocket connection management

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import redis.asyncio as redis
import json
import os
from typing import Dict, List, Optional, Any


class RedisManager:
    """
    Production Redis manager for WebSocket sessions and caching
    
    Uses redis-py async for high-performance operations
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        db: int = 0,
        password: str = None
    ):
        """
        Initialize Redis manager
        
        Args:
            host: Redis host (default: from env or localhost)
            port: Redis port (default: from env or 6379)
            db: Redis database number (default: 0)
            password: Redis password (default: from env)
        """
        self.host = host or os.getenv('REDIS_HOST', 'localhost')
        self.port = port or int(os.getenv('REDIS_PORT', '6379'))
        self.db = db
        self.password = password or os.getenv('REDIS_PASSWORD')
        
        self.client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.client = await redis.from_url(
                f"redis://{self.host}:{self.port}/{self.db}",
                password=self.password,
                encoding="utf-8",
                decode_responses=True,
                max_connections=100
            )
            
            # Test connection
            await self.client.ping()
            
            print(f"✅ Connected to Redis: {self.host}:{self.port}")
            
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()
            print("✅ Disconnected from Redis")
    
    # WebSocket connection management
    
    async def register_connection(
        self,
        connection_id: str,
        user_id: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Register a WebSocket connection"""
        key = f"ws:connection:{connection_id}"
        data = {
            "connection_id": connection_id,
            "user_id": user_id or "anonymous",
            "metadata": json.dumps(metadata or {}),
            "connected_at": str(int(await self._get_timestamp()))
        }
        
        await self.client.hset(key, mapping=data)
        await self.client.expire(key, 86400)  # 24 hour TTL
        
        # Add to user's connection set
        if user_id:
            await self.client.sadd(f"ws:user:{user_id}", connection_id)
    
    async def unregister_connection(self, connection_id: str):
        """Unregister a WebSocket connection"""
        # Get user_id before deleting
        key = f"ws:connection:{connection_id}"
        user_id = await self.client.hget(key, "user_id")
        
        # Delete connection
        await self.client.delete(key)
        
        # Remove from user's connection set
        if user_id and user_id != "anonymous":
            await self.client.srem(f"ws:user:{user_id}", connection_id)
    
    async def get_connection(self, connection_id: str) -> Optional[Dict]:
        """Get connection information"""
        key = f"ws:connection:{connection_id}"
        data = await self.client.hgetall(key)
        
        if data:
            if "metadata" in data:
                data["metadata"] = json.loads(data["metadata"])
            return data
        return None
    
    async def get_user_connections(self, user_id: str) -> List[str]:
        """Get all connection IDs for a user"""
        return list(await self.client.smembers(f"ws:user:{user_id}"))
    
    async def get_all_connections(self) -> List[str]:
        """Get all active connection IDs"""
        keys = await self.client.keys("ws:connection:*")
        return [key.split(":")[-1] for key in keys]
    
    async def get_connection_count(self) -> int:
        """Get total number of active connections"""
        keys = await self.client.keys("ws:connection:*")
        return len(keys)
    
    # Activity caching
    
    async def cache_activity(
        self,
        capsule_id: str,
        activity_data: Dict,
        ttl: int = 3600
    ):
        """Cache activity data"""
        key = f"activity:cache:{capsule_id}"
        await self.client.setex(
            key,
            ttl,
            json.dumps(activity_data)
        )
    
    async def get_cached_activity(self, capsule_id: str) -> Optional[Dict]:
        """Get cached activity data"""
        key = f"activity:cache:{capsule_id}"
        data = await self.client.get(key)
        
        if data:
            return json.loads(data)
        return None
    
    async def invalidate_activity_cache(self, capsule_id: str):
        """Invalidate activity cache"""
        key = f"activity:cache:{capsule_id}"
        await self.client.delete(key)
    
    # Pub/Sub for real-time updates
    
    async def publish_update(self, channel: str, message: Dict):
        """Publish update to a channel"""
        await self.client.publish(channel, json.dumps(message))
    
    async def subscribe(self, channel: str):
        """Subscribe to a channel"""
        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)
        return pubsub
    
    # Rate limiting
    
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check rate limit
        
        Args:
            key: Rate limit key (e.g., user_id, ip_address)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds
            
        Returns:
            True if within limit, False if exceeded
        """
        rate_key = f"rate_limit:{key}"
        
        # Increment counter
        count = await self.client.incr(rate_key)
        
        # Set expiry on first request
        if count == 1:
            await self.client.expire(rate_key, window_seconds)
        
        return count <= max_requests
    
    async def get_rate_limit_remaining(
        self,
        key: str,
        max_requests: int
    ) -> int:
        """Get remaining requests in rate limit window"""
        rate_key = f"rate_limit:{key}"
        count = await self.client.get(rate_key)
        
        if count:
            return max(0, max_requests - int(count))
        return max_requests
    
    # Session management
    
    async def create_session(
        self,
        session_id: str,
        user_id: str,
        data: Dict,
        ttl: int = 3600
    ):
        """Create a user session"""
        key = f"session:{session_id}"
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "data": json.dumps(data),
            "created_at": str(int(await self._get_timestamp()))
        }
        
        await self.client.hset(key, mapping=session_data)
        await self.client.expire(key, ttl)
    
    async def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        key = f"session:{session_id}"
        data = await self.client.hgetall(key)
        
        if data:
            if "data" in data:
                data["data"] = json.loads(data["data"])
            return data
        return None
    
    async def delete_session(self, session_id: str):
        """Delete a session"""
        key = f"session:{session_id}"
        await self.client.delete(key)
    
    async def extend_session(self, session_id: str, ttl: int = 3600):
        """Extend session TTL"""
        key = f"session:{session_id}"
        await self.client.expire(key, ttl)
    
    # Statistics
    
    async def get_statistics(self) -> Dict:
        """Get Redis statistics"""
        info = await self.client.info()
        
        connection_count = await self.get_connection_count()
        
        return {
            "redis_version": info.get("redis_version"),
            "uptime_seconds": info.get("uptime_in_seconds"),
            "connected_clients": info.get("connected_clients"),
            "used_memory_human": info.get("used_memory_human"),
            "total_connections_received": info.get("total_connections_received"),
            "total_commands_processed": info.get("total_commands_processed"),
            "websocket_connections": connection_count
        }
    
    # Helper methods
    
    async def _get_timestamp(self) -> float:
        """Get current timestamp"""
        import time
        return time.time()
