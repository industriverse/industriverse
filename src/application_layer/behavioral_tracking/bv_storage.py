"""
Behavioral Vector Storage Service.

This module provides storage and caching for Behavioral Vectors.
Integrates PostgreSQL for persistent storage and Redis for fast caching.
Part of Week 9: Behavioral Tracking Infrastructure (Day 5-6).

Components:
- PostgreSQLStore: PostgreSQL storage backend
- RedisCache: Redis caching layer
- BVStorageService: Unified storage service with caching
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)


class PostgreSQLStore:
    """PostgreSQL storage backend for Behavioral Vectors."""

    def __init__(self, connection_pool=None, db_config: Optional[Dict[str, Any]] = None):
        """
        Initialize PostgreSQL store.

        Args:
            connection_pool: Async PostgreSQL connection pool (asyncpg)
            db_config: Database configuration dict
        """
        self.pool = connection_pool
        self.db_config = db_config or {}

        if not self.pool and self.db_config:
            # Initialize pool if config provided
            asyncio.create_task(self._init_pool())

        logger.info("PostgreSQL store initialized")

    async def _init_pool(self):
        """Initialize connection pool."""
        try:
            import asyncpg

            self.pool = await asyncpg.create_pool(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5432),
                database=self.db_config.get('database', 'industriverse'),
                user=self.db_config.get('user', 'postgres'),
                password=self.db_config.get('password', ''),
                min_size=self.db_config.get('min_pool_size', 5),
                max_size=self.db_config.get('max_pool_size', 20),
                command_timeout=60
            )

            logger.info("PostgreSQL connection pool created")
        except ImportError:
            logger.warning("asyncpg not installed, PostgreSQL storage disabled")
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL connection pool: {e}")

    async def store_bv(self, bv: Any) -> bool:
        """
        Store or update a Behavioral Vector.

        Args:
            bv: BehavioralVector object

        Returns:
            Success status
        """
        if not self.pool:
            logger.warning("PostgreSQL pool not available")
            return False

        try:
            bv_dict = bv.to_dict() if hasattr(bv, 'to_dict') else bv

            async with self.pool.acquire() as conn:
                # Check if BV exists
                existing = await conn.fetchrow(
                    "SELECT id FROM behavioral.behavioral_vectors WHERE user_id = $1",
                    bv_dict['user_id']
                )

                if existing:
                    # Update existing BV
                    await conn.execute("""
                        UPDATE behavioral.behavioral_vectors
                        SET
                            computed_at = $2,
                            version = $3,
                            usage_patterns = $4,
                            preferences = $5,
                            expertise_level = $6,
                            engagement_metrics = $7,
                            adaptive_ux_config = $8,
                            metadata = $9,
                            updated_at = NOW()
                        WHERE user_id = $1
                    """,
                        bv_dict['user_id'],
                        bv_dict['computed_at'],
                        bv_dict['version'],
                        json.dumps(bv_dict['usage_patterns']),
                        json.dumps(bv_dict['preferences']),
                        json.dumps(bv_dict['expertise_level']),
                        json.dumps(bv_dict['engagement_metrics']),
                        json.dumps(bv_dict['adaptive_ux_config']),
                        json.dumps(bv_dict['metadata'])
                    )
                else:
                    # Insert new BV
                    await conn.execute("""
                        INSERT INTO behavioral.behavioral_vectors
                        (user_id, computed_at, version, usage_patterns, preferences,
                         expertise_level, engagement_metrics, adaptive_ux_config, metadata)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                    """,
                        bv_dict['user_id'],
                        bv_dict['computed_at'],
                        bv_dict['version'],
                        json.dumps(bv_dict['usage_patterns']),
                        json.dumps(bv_dict['preferences']),
                        json.dumps(bv_dict['expertise_level']),
                        json.dumps(bv_dict['engagement_metrics']),
                        json.dumps(bv_dict['adaptive_ux_config']),
                        json.dumps(bv_dict['metadata'])
                    )

                logger.info(f"Stored BV for user {bv_dict['user_id']}")
                return True

        except Exception as e:
            logger.error(f"Error storing BV: {e}")
            return False

    async def get_bv(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a Behavioral Vector by user ID.

        Args:
            user_id: User identifier

        Returns:
            BV dictionary or None if not found
        """
        if not self.pool:
            logger.warning("PostgreSQL pool not available")
            return None

        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow("""
                    SELECT
                        user_id, computed_at, version, usage_patterns,
                        preferences, expertise_level, engagement_metrics,
                        adaptive_ux_config, metadata
                    FROM behavioral.behavioral_vectors
                    WHERE user_id = $1
                """, user_id)

                if not row:
                    return None

                # Parse JSONB fields
                bv = {
                    'user_id': row['user_id'],
                    'computed_at': row['computed_at'].isoformat() if row['computed_at'] else None,
                    'version': row['version'],
                    'usage_patterns': json.loads(row['usage_patterns']) if isinstance(row['usage_patterns'], str) else row['usage_patterns'],
                    'preferences': json.loads(row['preferences']) if isinstance(row['preferences'], str) else row['preferences'],
                    'expertise_level': json.loads(row['expertise_level']) if isinstance(row['expertise_level'], str) else row['expertise_level'],
                    'engagement_metrics': json.loads(row['engagement_metrics']) if isinstance(row['engagement_metrics'], str) else row['engagement_metrics'],
                    'adaptive_ux_config': json.loads(row['adaptive_ux_config']) if isinstance(row['adaptive_ux_config'], str) else row['adaptive_ux_config'],
                    'metadata': json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                }

                logger.debug(f"Retrieved BV for user {user_id}")
                return bv

        except Exception as e:
            logger.error(f"Error retrieving BV: {e}")
            return None

    async def get_bvs_by_archetype(self, archetype: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get Behavioral Vectors by user archetype.

        Args:
            archetype: User archetype (novice, intermediate, advanced, expert, power_user)
            limit: Maximum number of BVs to return

        Returns:
            List of BV dictionaries
        """
        if not self.pool:
            return []

        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT
                        user_id, computed_at, version, usage_patterns,
                        preferences, expertise_level, engagement_metrics,
                        adaptive_ux_config, metadata
                    FROM behavioral.behavioral_vectors
                    WHERE expertise_level->>'archetype' = $1
                    ORDER BY computed_at DESC
                    LIMIT $2
                """, archetype, limit)

                bvs = []
                for row in rows:
                    bv = {
                        'user_id': row['user_id'],
                        'computed_at': row['computed_at'].isoformat() if row['computed_at'] else None,
                        'version': row['version'],
                        'usage_patterns': json.loads(row['usage_patterns']) if isinstance(row['usage_patterns'], str) else row['usage_patterns'],
                        'preferences': json.loads(row['preferences']) if isinstance(row['preferences'], str) else row['preferences'],
                        'expertise_level': json.loads(row['expertise_level']) if isinstance(row['expertise_level'], str) else row['expertise_level'],
                        'engagement_metrics': json.loads(row['engagement_metrics']) if isinstance(row['engagement_metrics'], str) else row['engagement_metrics'],
                        'adaptive_ux_config': json.loads(row['adaptive_ux_config']) if isinstance(row['adaptive_ux_config'], str) else row['adaptive_ux_config'],
                        'metadata': json.loads(row['metadata']) if isinstance(row['metadata'], str) else row['metadata']
                    }
                    bvs.append(bv)

                return bvs

        except Exception as e:
            logger.error(f"Error getting BVs by archetype: {e}")
            return []

    async def store_interaction_event(self, event: Any) -> bool:
        """
        Store an interaction event.

        Args:
            event: InteractionEvent object

        Returns:
            Success status
        """
        if not self.pool:
            return False

        try:
            event_dict = event.to_dict() if hasattr(event, 'to_dict') else event

            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO behavioral.interaction_events
                    (event_id, timestamp, event_type, severity, user_id, session_id,
                     device_id, device_type, capsule_id, capsule_type, capsule_category,
                     interaction_target, action_id, component_id, duration_ms,
                     time_since_last_interaction_ms, interaction_data, success,
                     error_message, context)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14,
                            $15, $16, $17, $18, $19, $20)
                """,
                    event_dict['event_id'],
                    event_dict['timestamp'],
                    event_dict['event_type'],
                    event_dict['severity'],
                    event_dict['user_id'],
                    event_dict['session_id'],
                    event_dict.get('device_id'),
                    event_dict.get('device_type', 'web'),
                    event_dict.get('capsule_id'),
                    event_dict.get('capsule_type'),
                    event_dict.get('capsule_category'),
                    event_dict.get('interaction_target'),
                    event_dict.get('action_id'),
                    event_dict.get('component_id'),
                    event_dict.get('duration_ms'),
                    event_dict.get('time_since_last_interaction_ms'),
                    json.dumps(event_dict.get('interaction_data', {})),
                    event_dict.get('success', True),
                    event_dict.get('error_message'),
                    json.dumps(event_dict.get('context', {}))
                )

                return True

        except Exception as e:
            logger.error(f"Error storing interaction event: {e}")
            return False

    async def close(self):
        """Close the connection pool."""
        if self.pool:
            await self.pool.close()
            logger.info("PostgreSQL connection pool closed")


class RedisCache:
    """Redis caching layer for Behavioral Vectors."""

    def __init__(self, redis_client=None, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis cache.

        Args:
            redis_client: Redis client instance
            redis_url: Redis connection URL
        """
        self.redis = redis_client
        self.redis_url = redis_url
        self.key_prefix = "bv:"
        self.ttl_seconds = 3600  # 1 hour default TTL

        if not self.redis:
            self._init_redis()

        logger.info("Redis cache initialized")

    def _init_redis(self):
        """Initialize Redis client."""
        try:
            import redis

            self.redis = redis.from_url(
                self.redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )

            # Test connection
            self.redis.ping()
            logger.info("Redis connection established")
        except ImportError:
            logger.warning("redis-py not installed, Redis caching disabled")
            self.redis = None
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis = None

    def get(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get BV from cache.

        Args:
            user_id: User identifier

        Returns:
            BV dictionary or None if not found
        """
        if not self.redis:
            return None

        try:
            key = f"{self.key_prefix}{user_id}"
            cached = self.redis.get(key)

            if cached:
                logger.debug(f"Cache HIT for user {user_id}")
                return json.loads(cached)

            logger.debug(f"Cache MISS for user {user_id}")
            return None

        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None

    def set(self, user_id: str, bv: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set BV in cache.

        Args:
            user_id: User identifier
            bv: BV dictionary
            ttl: Time-to-live in seconds (None = use default)

        Returns:
            Success status
        """
        if not self.redis:
            return False

        try:
            key = f"{self.key_prefix}{user_id}"
            ttl = ttl or self.ttl_seconds

            self.redis.setex(
                key,
                ttl,
                json.dumps(bv)
            )

            logger.debug(f"Cached BV for user {user_id} (TTL: {ttl}s)")
            return True

        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False

    def delete(self, user_id: str) -> bool:
        """
        Delete BV from cache.

        Args:
            user_id: User identifier

        Returns:
            Success status
        """
        if not self.redis:
            return False

        try:
            key = f"{self.key_prefix}{user_id}"
            self.redis.delete(key)
            logger.debug(f"Deleted cache for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False

    def clear_all(self) -> bool:
        """
        Clear all BV caches.

        Returns:
            Success status
        """
        if not self.redis:
            return False

        try:
            pattern = f"{self.key_prefix}*"
            keys = self.redis.keys(pattern)

            if keys:
                self.redis.delete(*keys)
                logger.info(f"Cleared {len(keys)} BV caches")

            return True

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False


class BVStorageService:
    """Unified storage service with PostgreSQL and Redis."""

    def __init__(
        self,
        pg_pool=None,
        pg_config: Optional[Dict[str, Any]] = None,
        redis_client=None,
        redis_url: str = "redis://localhost:6379",
        enable_cache: bool = True
    ):
        """
        Initialize BV storage service.

        Args:
            pg_pool: PostgreSQL connection pool
            pg_config: PostgreSQL configuration
            redis_client: Redis client
            redis_url: Redis connection URL
            enable_cache: Whether to enable Redis caching
        """
        self.pg_store = PostgreSQLStore(pg_pool, pg_config)
        self.cache = RedisCache(redis_client, redis_url) if enable_cache else None
        self.enable_cache = enable_cache

        logger.info("BV Storage Service initialized")

    async def store_bv(self, bv: Any) -> bool:
        """
        Store BV with cache-aside pattern.

        Args:
            bv: BehavioralVector object

        Returns:
            Success status
        """
        # Store in PostgreSQL
        success = await self.pg_store.store_bv(bv)

        if success and self.cache:
            # Update cache
            bv_dict = bv.to_dict() if hasattr(bv, 'to_dict') else bv
            self.cache.set(bv_dict['user_id'], bv_dict)

        return success

    async def get_bv(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get BV with cache-aside pattern.

        Args:
            user_id: User identifier

        Returns:
            BV dictionary or None if not found
        """
        # Try cache first
        if self.cache:
            cached_bv = self.cache.get(user_id)
            if cached_bv:
                return cached_bv

        # Cache miss, get from PostgreSQL
        bv = await self.pg_store.get_bv(user_id)

        if bv and self.cache:
            # Populate cache
            self.cache.set(user_id, bv)

        return bv

    async def invalidate_cache(self, user_id: str) -> bool:
        """
        Invalidate cache for a user.

        Args:
            user_id: User identifier

        Returns:
            Success status
        """
        if not self.cache:
            return True

        return self.cache.delete(user_id)

    async def store_interaction_event(self, event: Any) -> bool:
        """
        Store interaction event.

        Args:
            event: InteractionEvent object

        Returns:
            Success status
        """
        return await self.pg_store.store_interaction_event(event)

    async def get_bvs_by_archetype(self, archetype: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get BVs by user archetype.

        Args:
            archetype: User archetype
            limit: Maximum number of BVs

        Returns:
            List of BV dictionaries
        """
        return await self.pg_store.get_bvs_by_archetype(archetype, limit)

    async def close(self):
        """Close storage connections."""
        await self.pg_store.close()
        logger.info("BV Storage Service closed")


# Singleton instance
_bv_storage_instance = None


def get_bv_storage(
    pg_pool=None,
    pg_config: Optional[Dict[str, Any]] = None,
    redis_client=None,
    redis_url: str = "redis://localhost:6379",
    enable_cache: bool = True
) -> BVStorageService:
    """
    Get or create the singleton BVStorageService instance.

    Args:
        pg_pool: PostgreSQL connection pool
        pg_config: PostgreSQL configuration
        redis_client: Redis client
        redis_url: Redis connection URL
        enable_cache: Whether to enable caching

    Returns:
        BVStorageService instance
    """
    global _bv_storage_instance

    if _bv_storage_instance is None:
        _bv_storage_instance = BVStorageService(
            pg_pool=pg_pool,
            pg_config=pg_config,
            redis_client=redis_client,
            redis_url=redis_url,
            enable_cache=enable_cache
        )

    return _bv_storage_instance
