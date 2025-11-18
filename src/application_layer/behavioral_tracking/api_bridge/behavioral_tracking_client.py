"""
Behavioral Tracking Client
Week 17 Day 2: API Bridge for Unified Behavioral Tracking

This module provides a client interface for TypeScript/JavaScript applications
to interact with the Python-based behavioral tracking backend.

It exposes RESTful endpoints that can be called from the Week 16 capsule-pins-pwa
or any other frontend application.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator
import logging
import json

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models (Pydantic for validation)
# =============================================================================

class InteractionEventCreate(BaseModel):
    """Model for creating an interaction event."""

    event_id: Optional[str] = Field(default=None, description="Event ID (auto-generated if not provided)")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)
    event_type: str = Field(..., description="Type of interaction (click, tap, expand, etc.)")
    severity: str = Field(default="info", description="Event severity")

    # User context
    user_id: str = Field(..., description="User identifier")
    session_id: str = Field(..., description="Session identifier")
    device_id: Optional[str] = None
    device_type: str = Field(default="web", description="Device type (web, ios, android, desktop)")

    # Capsule context
    capsule_id: Optional[str] = None
    capsule_type: Optional[str] = None
    capsule_category: Optional[str] = None

    # Interaction details
    interaction_target: str = Field(default="capsule")
    action_id: Optional[str] = None
    component_id: Optional[str] = None

    # Timing metrics
    duration_ms: Optional[int] = None
    time_since_last_interaction_ms: Optional[int] = None

    # Interaction data
    interaction_data: Dict[str, Any] = Field(default_factory=dict)

    # Result
    success: bool = True
    error_message: Optional[str] = None

    # Behavioral context
    context: Dict[str, Any] = Field(default_factory=dict)

    @validator('event_type')
    def validate_event_type(cls, v):
        valid_types = [
            'tap', 'click', 'expand', 'collapse', 'pin', 'unpin',
            'drag', 'resize', 'action', 'complete', 'dismiss',
            'acknowledge', 'decision', 'scroll', 'hover', 'swipe'
        ]
        if v not in valid_types:
            raise ValueError(f'event_type must be one of {valid_types}')
        return v

    @validator('severity')
    def validate_severity(cls, v):
        valid_severities = ['debug', 'info', 'warning', 'error']
        if v not in valid_severities:
            raise ValueError(f'severity must be one of {valid_severities}')
        return v

    @validator('device_type')
    def validate_device_type(cls, v):
        valid_device_types = ['web', 'ios', 'android', 'desktop', 'wearable']
        if v not in valid_device_types:
            raise ValueError(f'device_type must be one of {valid_device_types}')
        return v


class BehavioralVectorResponse(BaseModel):
    """Model for behavioral vector response."""

    user_id: str
    computed_at: datetime
    version: int

    usage_patterns: Dict[str, Any]
    preferences: Dict[str, Any]
    expertise_level: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    adaptive_ux_config: Dict[str, Any]
    metadata: Dict[str, Any]

    created_at: datetime
    updated_at: datetime


class UserSessionResponse(BaseModel):
    """Model for user session response."""

    session_id: str
    user_id: str
    started_at: datetime
    last_interaction_at: Optional[datetime]
    ended_at: Optional[datetime]
    device_id: Optional[str]
    device_type: Optional[str]

    event_count: int
    unique_capsules_count: int
    duration_minutes: Optional[float]

    interaction_type_distribution: Dict[str, Any]
    capsule_types_visited: List[str]

    active: bool
    created_at: datetime
    updated_at: datetime


class EngagementScoreResponse(BaseModel):
    """Model for engagement score response."""

    user_id: str
    engagement_score: float
    confidence: float
    last_computed: datetime
    factors: Dict[str, Any]


# =============================================================================
# Behavioral Tracking Client
# =============================================================================

class BehavioralTrackingClient:
    """
    Client for interacting with behavioral tracking system.

    This client can be used by:
    - TypeScript/JavaScript frontends (via HTTP API)
    - Python services within the Industriverse framework
    - External applications
    """

    def __init__(self, database_pool=None, redis_client=None):
        """
        Initialize the behavioral tracking client.

        Args:
            database_pool: PostgreSQL connection pool
            redis_client: Redis client for caching
        """
        self.db_pool = database_pool
        self.redis = redis_client

        logger.info("BehavioralTrackingClient initialized")

    async def track_interaction(self, event: InteractionEventCreate) -> Dict[str, Any]:
        """
        Track a user interaction event.

        Args:
            event: Interaction event data

        Returns:
            Event tracking result
        """
        import uuid

        # Generate event ID if not provided
        if not event.event_id:
            event.event_id = str(uuid.uuid4())

        # Store event in database
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO behavioral.interaction_events (
                    event_id, timestamp, event_type, severity,
                    user_id, session_id, device_id, device_type,
                    capsule_id, capsule_type, capsule_category,
                    interaction_target, action_id, component_id,
                    duration_ms, time_since_last_interaction_ms,
                    interaction_data, success, error_message, context
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10,
                    $11, $12, $13, $14, $15, $16, $17, $18, $19, $20
                )
            """,
                event.event_id, event.timestamp, event.event_type, event.severity,
                event.user_id, event.session_id, event.device_id, event.device_type,
                event.capsule_id, event.capsule_type, event.capsule_category,
                event.interaction_target, event.action_id, event.component_id,
                event.duration_ms, event.time_since_last_interaction_ms,
                json.dumps(event.interaction_data), event.success,
                event.error_message, json.dumps(event.context)
            )

        # Update session
        await self._update_session(event.user_id, event.session_id, event.event_type)

        # Publish to Kafka (for real-time processing)
        await self._publish_to_kafka(event)

        logger.info(f"Tracked interaction: {event.event_id} for user {event.user_id}")

        return {
            "event_id": event.event_id,
            "status": "tracked",
            "timestamp": event.timestamp.isoformat()
        }

    async def _update_session(self, user_id: str, session_id: str, event_type: str):
        """Update user session statistics."""
        async with self.db_pool.acquire() as conn:
            # Check if session exists
            session = await conn.fetchrow("""
                SELECT * FROM behavioral.user_sessions
                WHERE session_id = $1
            """, session_id)

            if session:
                # Update existing session
                await conn.execute("""
                    UPDATE behavioral.user_sessions
                    SET
                        last_interaction_at = NOW(),
                        event_count = event_count + 1,
                        interaction_type_distribution =
                            jsonb_set(
                                interaction_type_distribution,
                                ARRAY[$1],
                                to_jsonb(COALESCE((interaction_type_distribution->>$1)::int, 0) + 1)
                            )
                    WHERE session_id = $2
                """, event_type, session_id)
            else:
                # Create new session
                await conn.execute("""
                    INSERT INTO behavioral.user_sessions (
                        session_id, user_id, started_at, last_interaction_at,
                        event_count, interaction_type_distribution
                    ) VALUES (
                        $1, $2, NOW(), NOW(), 1, $3::jsonb
                    )
                """, session_id, user_id, json.dumps({event_type: 1}))

    async def _publish_to_kafka(self, event: InteractionEventCreate):
        """Publish event to Kafka for real-time processing."""
        try:
            # Import Kafka producer (lazy import)
            from kafka import KafkaProducer

            producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )

            # Publish to behavioral-events topic
            producer.send('behavioral-events', event.dict())
            producer.flush()

            logger.debug(f"Published event {event.event_id} to Kafka")
        except Exception as e:
            logger.warning(f"Failed to publish to Kafka: {e}")
            # Continue anyway - Kafka is optional

    async def get_behavioral_vector(self, user_id: str) -> Optional[BehavioralVectorResponse]:
        """
        Get behavioral vector for a user.

        Args:
            user_id: User identifier

        Returns:
            Behavioral vector or None if not found
        """
        # Check cache first
        cache_key = f"bv:{user_id}"
        if self.redis:
            cached = await self.redis.get(cache_key)
            if cached:
                logger.debug(f"Behavioral vector cache hit for {user_id}")
                return BehavioralVectorResponse(**json.loads(cached))

        # Fetch from database
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM behavioral.behavioral_vectors
                WHERE user_id = $1
                ORDER BY computed_at DESC
                LIMIT 1
            """, user_id)

            if not row:
                logger.warning(f"No behavioral vector found for user {user_id}")
                return None

            bv = BehavioralVectorResponse(
                user_id=row['user_id'],
                computed_at=row['computed_at'],
                version=row['version'],
                usage_patterns=row['usage_patterns'],
                preferences=row['preferences'],
                expertise_level=row['expertise_level'],
                engagement_metrics=row['engagement_metrics'],
                adaptive_ux_config=row['adaptive_ux_config'],
                metadata=row['metadata'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )

            # Cache for 30 minutes
            if self.redis:
                await self.redis.setex(cache_key, 1800, bv.json())

            return bv

    async def compute_behavioral_vector(self, user_id: str) -> BehavioralVectorResponse:
        """
        Compute behavioral vector for a user.

        This analyzes the user's interaction history and generates
        a behavioral profile for adaptive UX.

        Args:
            user_id: User identifier

        Returns:
            Computed behavioral vector
        """
        from .behavioral_vector_computer import BehavioralVectorComputer

        computer = BehavioralVectorComputer(self.db_pool)
        bv_data = await computer.compute(user_id)

        # Store in database
        async with self.db_pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO behavioral.behavioral_vectors (
                    user_id, computed_at, version, usage_patterns, preferences,
                    expertise_level, engagement_metrics, adaptive_ux_config, metadata
                ) VALUES (
                    $1, $2, $3, $4, $5, $6, $7, $8, $9
                )
                ON CONFLICT (user_id) DO UPDATE SET
                    computed_at = EXCLUDED.computed_at,
                    version = behavioral.behavioral_vectors.version + 1,
                    usage_patterns = EXCLUDED.usage_patterns,
                    preferences = EXCLUDED.preferences,
                    expertise_level = EXCLUDED.expertise_level,
                    engagement_metrics = EXCLUDED.engagement_metrics,
                    adaptive_ux_config = EXCLUDED.adaptive_ux_config,
                    metadata = EXCLUDED.metadata,
                    updated_at = NOW()
            """,
                user_id, datetime.utcnow(), 1,
                json.dumps(bv_data['usage_patterns']),
                json.dumps(bv_data['preferences']),
                json.dumps(bv_data['expertise_level']),
                json.dumps(bv_data['engagement_metrics']),
                json.dumps(bv_data['adaptive_ux_config']),
                json.dumps(bv_data['metadata'])
            )

        # Invalidate cache
        if self.redis:
            await self.redis.delete(f"bv:{user_id}")

        logger.info(f"Computed behavioral vector for user {user_id}")

        return await self.get_behavioral_vector(user_id)

    async def get_user_session(self, session_id: str) -> Optional[UserSessionResponse]:
        """
        Get user session details.

        Args:
            session_id: Session identifier

        Returns:
            Session details or None if not found
        """
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT * FROM behavioral.user_sessions
                WHERE session_id = $1
            """, session_id)

            if not row:
                return None

            return UserSessionResponse(
                session_id=row['session_id'],
                user_id=row['user_id'],
                started_at=row['started_at'],
                last_interaction_at=row['last_interaction_at'],
                ended_at=row['ended_at'],
                device_id=row['device_id'],
                device_type=row['device_type'],
                event_count=row['event_count'],
                unique_capsules_count=row['unique_capsules_count'],
                duration_minutes=row['duration_minutes'],
                interaction_type_distribution=row['interaction_type_distribution'],
                capsule_types_visited=row['capsule_types_visited'],
                active=row['active'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )

    async def get_engagement_score(self, user_id: str) -> EngagementScoreResponse:
        """
        Get engagement score for a user.

        Args:
            user_id: User identifier

        Returns:
            Engagement score and factors
        """
        bv = await self.get_behavioral_vector(user_id)

        if not bv:
            # Return default low engagement
            return EngagementScoreResponse(
                user_id=user_id,
                engagement_score=0.1,
                confidence=0.0,
                last_computed=datetime.utcnow(),
                factors={"reason": "no_behavioral_vector"}
            )

        # Extract engagement score from behavioral vector
        engagement_metrics = bv.engagement_metrics

        return EngagementScoreResponse(
            user_id=user_id,
            engagement_score=float(engagement_metrics.get('score', 0.5)),
            confidence=float(engagement_metrics.get('confidence', 0.8)),
            last_computed=bv.computed_at,
            factors=engagement_metrics.get('factors', {})
        )

    async def clear_cache(self, user_id: str) -> Dict[str, Any]:
        """
        Clear cached behavioral data for a user.

        Args:
            user_id: User identifier

        Returns:
            Cache clear result
        """
        if self.redis:
            cache_key = f"bv:{user_id}"
            await self.redis.delete(cache_key)
            logger.info(f"Cleared behavioral vector cache for {user_id}")
            return {"status": "cleared", "user_id": user_id}
        else:
            return {"status": "no_cache", "user_id": user_id}

    async def get_user_interactions(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Get interaction history for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of results
            offset: Offset for pagination
            start_date: Start date filter
            end_date: End date filter

        Returns:
            List of interaction events
        """
        query = """
            SELECT * FROM behavioral.interaction_events
            WHERE user_id = $1
        """

        params = [user_id]
        param_idx = 2

        if start_date:
            query += f" AND timestamp >= ${param_idx}"
            params.append(start_date)
            param_idx += 1

        if end_date:
            query += f" AND timestamp <= ${param_idx}"
            params.append(end_date)
            param_idx += 1

        query += f" ORDER BY timestamp DESC LIMIT ${param_idx} OFFSET ${param_idx + 1}"
        params.extend([limit, offset])

        async with self.db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)

            return [dict(row) for row in rows]
