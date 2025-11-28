import redis.asyncio as redis
import os
import logging
import json
from typing import Optional, Callable, Awaitable

logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.client: Optional[redis.Redis] = None
        self.pubsub = None

    async def connect(self):
        """Connect to Redis."""
        try:
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            await self.client.ping()
            logger.info("Connected to Redis.")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")

    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Disconnected from Redis.")

    async def set(self, key: str, value: str, expire: int = 3600):
        """Set a key with expiration."""
        if self.client:
            await self.client.set(key, value, ex=expire)

    async def get(self, key: str) -> Optional[str]:
        """Get a key."""
        if self.client:
            return await self.client.get(key)
        return None

    async def publish(self, channel: str, message: dict):
        """Publish a message to a channel."""
        if self.client:
            await self.client.publish(channel, json.dumps(message))

    async def subscribe(self, channel: str, handler: Callable[[dict], Awaitable[None]]):
        """Subscribe to a channel and handle messages."""
        if not self.client:
            return

        self.pubsub = self.client.pubsub()
        await self.pubsub.subscribe(channel)
        
        logger.info(f"Subscribed to Redis channel: {channel}")
        
        async for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    await handler(data)
                except json.JSONDecodeError:
                    logger.error(f"Failed to decode Redis message: {message['data']}")

redis_manager = RedisManager()
