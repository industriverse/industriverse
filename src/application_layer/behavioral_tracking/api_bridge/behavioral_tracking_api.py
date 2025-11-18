"""
Behavioral Tracking REST API
Week 17 Day 2: API Bridge FastAPI Endpoints

This module exposes RESTful HTTP endpoints for the behavioral tracking system.
These endpoints can be called from TypeScript/JavaScript frontends (Week 16 capsule-pins-pwa)
or any other HTTP client.
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import logging

from .behavioral_tracking_client import (
    BehavioralTrackingClient,
    InteractionEventCreate,
    BehavioralVectorResponse,
    UserSessionResponse,
    EngagementScoreResponse
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Industriverse Behavioral Tracking API",
    description="API for tracking user behavioral patterns and generating adaptive UX configurations",
    version="1.0.0 (Week 17)",
    docs_url="/api/v1/behavioral/docs",
    redoc_url="/api/v1/behavioral/redoc"
)

# Add CORS middleware (for frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Dependency Injection
# =============================================================================

async def get_behavioral_client() -> BehavioralTrackingClient:
    """
    Dependency injection for behavioral tracking client.

    In production, this should:
    1. Get database pool from connection pool manager
    2. Get Redis client from cache manager
    3. Reuse connections across requests
    """
    # TODO: Implement proper connection pooling
    # For now, create a new client (to be replaced with singleton)
    from asyncpg import create_pool
    import aioredis

    db_pool = await create_pool(
        host='localhost',
        port=5432,
        database='industriverse',
        user='industriverse',
        password='changeme',
        min_size=5,
        max_size=20
    )

    redis_client = await aioredis.create_redis_pool(
        'redis://localhost:6379/0',
        minsize=5,
        maxsize=10
    )

    return BehavioralTrackingClient(database_pool=db_pool, redis_client=redis_client)


# =============================================================================
# API Endpoints
# =============================================================================

@app.get("/api/v1/behavioral/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "behavioral-tracking-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/behavioral/interactions", status_code=201)
async def track_interaction(
    event: InteractionEventCreate,
    client: BehavioralTrackingClient = Depends(get_behavioral_client)
):
    """
    Track a user interaction event.

    This endpoint receives interaction events from frontends (web, mobile, desktop)
    and stores them in the behavioral tracking database.

    **Example Request:**
    ```json
    {
        "event_type": "click",
        "user_id": "user123",
        "session_id": "sess456",
        "capsule_id": "cap789",
        "capsule_type": "alert",
        "device_type": "web",
        "interaction_data": {
            "button": "acknowledge"
        }
    }
    ```

    **Example Response:**
    ```json
    {
        "event_id": "uuid-here",
        "status": "tracked",
        "timestamp": "2025-11-18T12:00:00Z"
    }
    ```
    """
    try:
        result = await client.track_interaction(event)
        return result
    except Exception as e:
        logger.error(f"Failed to track interaction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/behavioral/vectors/{user_id}", response_model=BehavioralVectorResponse)
async def get_behavioral_vector(
    user_id: str = Path(..., description="User identifier"),
    client: BehavioralTrackingClient = Depends(get_behavioral_client)
):
    """
    Get behavioral vector for a user.

    Returns the computed behavioral profile including:
    - Usage patterns
    - Preferences
    - Expertise level
    - Engagement metrics
    - Adaptive UX configuration

    **Example Response:**
    ```json
    {
        "user_id": "user123",
        "computed_at": "2025-11-18T12:00:00Z",
        "version": 5,
        "usage_patterns": {
            "avg_session_duration": 600,
            "interaction_frequency": "high"
        },
        "expertise_level": {
            "level": "intermediate",
            "score": 0.7
        },
        "engagement_metrics": {
            "score": 0.85,
            "confidence": 0.9
        },
        "adaptive_ux_config": {
            "tooltips": false,
            "shortcuts": true,
            "complexity": "moderate"
        }
    }
    ```
    """
    try:
        bv = await client.get_behavioral_vector(user_id)

        if not bv:
            raise HTTPException(
                status_code=404,
                detail=f"No behavioral vector found for user {user_id}"
            )

        return bv
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get behavioral vector: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/behavioral/vectors/{user_id}/compute", response_model=BehavioralVectorResponse)
async def compute_behavioral_vector(
    user_id: str = Path(..., description="User identifier"),
    client: BehavioralTrackingClient = Depends(get_behavioral_client)
):
    """
    Compute (or recompute) behavioral vector for a user.

    This analyzes the user's interaction history and generates a fresh
    behavioral profile. Typically called:
    - After significant interaction activity
    - When adaptive UX needs to be updated
    - Periodically (e.g., daily)

    **Example Response:**
    Same as GET /vectors/{user_id}, but with updated computed_at timestamp
    """
    try:
        bv = await client.compute_behavioral_vector(user_id)
        return bv
    except Exception as e:
        logger.error(f"Failed to compute behavioral vector: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/behavioral/vectors/{user_id}/engagement", response_model=EngagementScoreResponse)
async def get_engagement_score(
    user_id: str = Path(..., description="User identifier"),
    client: BehavioralTrackingClient = Depends(get_behavioral_client)
):
    """
    Get engagement score for a user.

    Returns a single engagement score (0.0-1.0) with confidence level
    and contributing factors.

    **Example Response:**
    ```json
    {
        "user_id": "user123",
        "engagement_score": 0.85,
        "confidence": 0.9,
        "last_computed": "2025-11-18T12:00:00Z",
        "factors": {
            "session_frequency": 0.9,
            "interaction_diversity": 0.8,
            "task_completion_rate": 0.85
        }
    }
    ```
    """
    try:
        score = await client.get_engagement_score(user_id)
        return score
    except Exception as e:
        logger.error(f"Failed to get engagement score: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/behavioral/sessions/{session_id}", response_model=UserSessionResponse)
async def get_session(
    session_id: str = Path(..., description="Session identifier"),
    client: BehavioralTrackingClient = Depends(get_behavioral_client)
):
    """
    Get session details.

    Returns information about a specific user session including:
    - Event count
    - Duration
    - Interaction type distribution
    - Capsules visited

    **Example Response:**
    ```json
    {
        "session_id": "sess456",
        "user_id": "user123",
        "started_at": "2025-11-18T10:00:00Z",
        "last_interaction_at": "2025-11-18T10:30:00Z",
        "event_count": 45,
        "unique_capsules_count": 12,
        "duration_minutes": 30.5,
        "interaction_type_distribution": {
            "click": 30,
            "expand": 10,
            "acknowledge": 5
        },
        "active": true
    }
    ```
    """
    try:
        session = await client.get_user_session(session_id)

        if not session:
            raise HTTPException(
                status_code=404,
                detail=f"Session {session_id} not found"
            )

        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/behavioral/interactions/{user_id}")
async def get_user_interactions(
    user_id: str = Path(..., description="User identifier"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    start_date: Optional[datetime] = Query(None, description="Start date filter"),
    end_date: Optional[datetime] = Query(None, description="End date filter"),
    client: BehavioralTrackingClient = Depends(get_behavioral_client)
):
    """
    Get interaction history for a user.

    Supports pagination and date filtering.

    **Query Parameters:**
    - `limit`: Max results (1-1000, default 100)
    - `offset`: Offset for pagination (default 0)
    - `start_date`: Filter interactions after this date (ISO 8601)
    - `end_date`: Filter interactions before this date (ISO 8601)

    **Example Request:**
    ```
    GET /api/v1/behavioral/interactions/user123?limit=50&offset=0&start_date=2025-11-01T00:00:00Z
    ```

    **Example Response:**
    ```json
    [
        {
            "event_id": "uuid1",
            "timestamp": "2025-11-18T12:00:00Z",
            "event_type": "click",
            "capsule_id": "cap789",
            "success": true
        },
        ...
    ]
    ```
    """
    try:
        interactions = await client.get_user_interactions(
            user_id=user_id,
            limit=limit,
            offset=offset,
            start_date=start_date,
            end_date=end_date
        )

        return {
            "user_id": user_id,
            "count": len(interactions),
            "limit": limit,
            "offset": offset,
            "interactions": interactions
        }
    except Exception as e:
        logger.error(f"Failed to get user interactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v1/behavioral/vectors/{user_id}/cache")
async def clear_cache(
    user_id: str = Path(..., description="User identifier"),
    client: BehavioralTrackingClient = Depends(get_behavioral_client)
):
    """
    Clear cached behavioral data for a user.

    Forces next request to fetch fresh data from database.

    **Example Response:**
    ```json
    {
        "status": "cleared",
        "user_id": "user123"
    }
    ```
    """
    try:
        result = await client.clear_cache(user_id)
        return result
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Server Startup
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
