"""
Behavioral Vector REST API.

This module provides REST API endpoints for retrieving and managing Behavioral Vectors.
Part of Week 9: Behavioral Tracking Infrastructure (Day 5-6).

Endpoints:
- GET /api/v1/behavioral-vectors/{user_id} - Get BV for a user
- POST /api/v1/behavioral-vectors/{user_id}/compute - Compute BV for a user
- GET /api/v1/behavioral-vectors/archetype/{archetype} - Get BVs by archetype
- GET /api/v1/behavioral-vectors/{user_id}/ux-config - Get adaptive UX config
- POST /api/v1/interaction-events - Log interaction event
- GET /api/v1/interaction-events/{user_id} - Get user interaction events
- DELETE /api/v1/behavioral-vectors/{user_id}/cache - Invalidate cache
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Query, Path, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Behavioral Vector API",
    description="API for Behavioral Vectors and interaction tracking",
    version="1.0.0"
)


# ==============================================================================
# Request/Response Models
# ==============================================================================

class InteractionEventRequest(BaseModel):
    """Request model for logging interaction events."""
    capsule_id: str
    event_type: str
    interaction_data: Dict[str, Any] = Field(default_factory=dict)
    user_id: str = "anonymous"
    session_id: str = ""
    device_id: str = ""
    device_type: str = "web"


class ComputeBVRequest(BaseModel):
    """Request model for computing Behavioral Vector."""
    time_window_days: int = Field(default=30, ge=1, le=365)
    force_recompute: bool = False


class BVResponse(BaseModel):
    """Response model for Behavioral Vector."""
    user_id: str
    computed_at: str
    version: int
    usage_patterns: Dict[str, Any]
    preferences: Dict[str, Any]
    expertise_level: Dict[str, Any]
    engagement_metrics: Dict[str, Any]
    adaptive_ux_config: Dict[str, Any]
    metadata: Dict[str, Any]


class UXConfigResponse(BaseModel):
    """Response model for adaptive UX configuration."""
    user_id: str
    recommended_layout: str
    recommended_density: str
    recommended_features: list
    recommended_shortcuts: list
    capsule_priority_weights: Dict[str, float]
    expertise_archetype: str
    last_updated: str


# ==============================================================================
# API Endpoints
# ==============================================================================

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "Behavioral Vector API",
        "version": "1.0.0",
        "endpoints": {
            "get_bv": "/api/v1/behavioral-vectors/{user_id}",
            "compute_bv": "/api/v1/behavioral-vectors/{user_id}/compute",
            "get_by_archetype": "/api/v1/behavioral-vectors/archetype/{archetype}",
            "get_ux_config": "/api/v1/behavioral-vectors/{user_id}/ux-config",
            "log_event": "/api/v1/interaction-events",
            "get_events": "/api/v1/interaction-events/{user_id}",
            "invalidate_cache": "/api/v1/behavioral-vectors/{user_id}/cache"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get(
    "/api/v1/behavioral-vectors/{user_id}",
    response_model=BVResponse,
    summary="Get Behavioral Vector for a user",
    tags=["Behavioral Vectors"]
)
async def get_bv(
    user_id: str = Path(..., description="User identifier")
):
    """
    Retrieve the Behavioral Vector for a specific user.

    Returns the computed BV including usage patterns, preferences,
    expertise level, and adaptive UX recommendations.
    """
    try:
        from .bv_storage import get_bv_storage

        storage = get_bv_storage()
        bv = await storage.get_bv(user_id)

        if not bv:
            raise HTTPException(
                status_code=404,
                detail=f"Behavioral Vector not found for user {user_id}"
            )

        return BVResponse(**bv)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving BV: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/v1/behavioral-vectors/{user_id}/compute",
    response_model=BVResponse,
    summary="Compute Behavioral Vector for a user",
    tags=["Behavioral Vectors"]
)
async def compute_bv(
    user_id: str = Path(..., description="User identifier"),
    request: ComputeBVRequest = Body(...)
):
    """
    Compute or recompute the Behavioral Vector for a user.

    Analyzes interaction events from the specified time window
    and generates a comprehensive behavioral profile.
    """
    try:
        from .behavioral_tracker import get_behavioral_tracker
        from .behavioral_vector_computer import get_bv_computer
        from .bv_storage import get_bv_storage

        # Get services
        tracker = get_behavioral_tracker()
        computer = get_bv_computer()
        storage = get_bv_storage()

        # Get user events
        start_time = datetime.utcnow() - timedelta(days=request.time_window_days)
        events = tracker.get_user_events(
            user_id,
            limit=10000,
            start_time=start_time
        )

        if not events:
            raise HTTPException(
                status_code=404,
                detail=f"No interaction events found for user {user_id}"
            )

        # Get session data
        session_summary = tracker.get_session_summary(user_id)
        sessions = {session_summary["session_id"]: session_summary} if session_summary.get("session_id") else {}

        # Compute BV
        bv = computer.compute(
            user_id=user_id,
            events=events,
            sessions=sessions,
            time_window_days=request.time_window_days
        )

        # Store BV
        await storage.store_bv(bv)

        bv_dict = bv.to_dict()
        return BVResponse(**bv_dict)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error computing BV: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/api/v1/behavioral-vectors/archetype/{archetype}",
    summary="Get Behavioral Vectors by archetype",
    tags=["Behavioral Vectors"]
)
async def get_bvs_by_archetype(
    archetype: str = Path(
        ...,
        description="User archetype",
        regex="^(novice|intermediate|advanced|expert|power_user)$"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of results")
):
    """
    Retrieve Behavioral Vectors for users of a specific archetype.

    Useful for analyzing patterns across user groups.
    """
    try:
        from .bv_storage import get_bv_storage

        storage = get_bv_storage()
        bvs = await storage.get_bvs_by_archetype(archetype, limit)

        return {
            "archetype": archetype,
            "count": len(bvs),
            "behavioral_vectors": bvs
        }

    except Exception as e:
        logger.error(f"Error retrieving BVs by archetype: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/api/v1/behavioral-vectors/{user_id}/ux-config",
    response_model=UXConfigResponse,
    summary="Get adaptive UX configuration",
    tags=["Adaptive UX"]
)
async def get_ux_config(
    user_id: str = Path(..., description="User identifier")
):
    """
    Get the adaptive UX configuration recommendations for a user.

    Returns layout, density, feature, and shortcut recommendations
    based on the user's behavioral profile.
    """
    try:
        from .bv_storage import get_bv_storage

        storage = get_bv_storage()
        bv = await storage.get_bv(user_id)

        if not bv:
            raise HTTPException(
                status_code=404,
                detail=f"Behavioral Vector not found for user {user_id}"
            )

        ux_config = bv['adaptive_ux_config']
        expertise_level = bv['expertise_level']

        return UXConfigResponse(
            user_id=user_id,
            recommended_layout=ux_config['recommended_layout'],
            recommended_density=ux_config['recommended_density'],
            recommended_features=ux_config['recommended_features'],
            recommended_shortcuts=ux_config['recommended_shortcuts'],
            capsule_priority_weights=ux_config['capsule_priority_weights'],
            expertise_archetype=expertise_level['archetype'],
            last_updated=bv['computed_at']
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving UX config: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post(
    "/api/v1/interaction-events",
    summary="Log interaction event",
    tags=["Interaction Events"]
)
async def log_interaction_event(
    event: InteractionEventRequest = Body(...)
):
    """
    Log a capsule interaction event for behavioral tracking.

    Events are used to compute Behavioral Vectors and drive
    adaptive UX personalization.
    """
    try:
        from .behavioral_tracker import get_behavioral_tracker
        from .capsule_interaction_handler import CapsuleInteractionHandler

        # Get tracker (with interaction handler if available)
        tracker = get_behavioral_tracker()

        # Create capsule object from request
        capsule = {
            "capsule_id": event.capsule_id,
            "capsule_type": "custom",  # Can be inferred from capsule_id
        }

        # Track interaction
        response = tracker.track_interaction(
            capsule=capsule,
            interaction_type=event.event_type,
            data=event.interaction_data,
            user_id=event.user_id,
            session_id=event.session_id,
            device_id=event.device_id,
            device_type=event.device_type
        )

        return {
            "status": "logged",
            "event_id": response.get("_tracking", {}).get("event_id"),
            "tracked": response.get("_tracking", {}).get("tracked", False)
        }

    except Exception as e:
        logger.error(f"Error logging interaction event: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/api/v1/interaction-events/{user_id}",
    summary="Get user interaction events",
    tags=["Interaction Events"]
)
async def get_interaction_events(
    user_id: str = Path(..., description="User identifier"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    capsule_type: Optional[str] = Query(None, description="Filter by capsule type"),
    days: int = Query(30, ge=1, le=365, description="Days of history to retrieve")
):
    """
    Retrieve interaction events for a user.

    Useful for debugging, analytics, and understanding user behavior.
    """
    try:
        from .behavioral_tracker import get_behavioral_tracker

        tracker = get_behavioral_tracker()

        # Calculate start time
        start_time = datetime.utcnow() - timedelta(days=days)

        # Get events
        events = tracker.get_user_events(
            user_id=user_id,
            limit=limit,
            event_type=event_type,
            capsule_type=capsule_type,
            start_time=start_time
        )

        # Convert to dicts
        event_dicts = [e.to_dict() for e in events]

        return {
            "user_id": user_id,
            "count": len(event_dicts),
            "events": event_dicts
        }

    except Exception as e:
        logger.error(f"Error retrieving interaction events: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.delete(
    "/api/v1/behavioral-vectors/{user_id}/cache",
    summary="Invalidate BV cache",
    tags=["Cache Management"]
)
async def invalidate_cache(
    user_id: str = Path(..., description="User identifier")
):
    """
    Invalidate the cached Behavioral Vector for a user.

    Forces the next retrieval to fetch from database.
    """
    try:
        from .bv_storage import get_bv_storage

        storage = get_bv_storage()
        success = await storage.invalidate_cache(user_id)

        if success:
            return {"status": "invalidated", "user_id": user_id}
        else:
            return {"status": "no_cache_available", "user_id": user_id}

    except Exception as e:
        logger.error(f"Error invalidating cache: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get(
    "/api/v1/behavioral-vectors/{user_id}/engagement",
    summary="Get user engagement metrics",
    tags=["Analytics"]
)
async def get_engagement_metrics(
    user_id: str = Path(..., description="User identifier"),
    time_window_minutes: int = Query(30, ge=1, le=1440, description="Time window for engagement calculation")
):
    """
    Calculate real-time engagement score for a user.

    Returns engagement metrics based on recent interaction patterns.
    """
    try:
        from .behavioral_tracker import get_behavioral_tracker

        tracker = get_behavioral_tracker()
        engagement_score = tracker.calculate_engagement_score(
            user_id,
            time_window_minutes
        )

        session_summary = tracker.get_session_summary(user_id)

        return {
            "user_id": user_id,
            "engagement_score": engagement_score,
            "time_window_minutes": time_window_minutes,
            "session_summary": session_summary
        }

    except Exception as e:
        logger.error(f"Error calculating engagement: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ==============================================================================
# Error Handlers
# ==============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )


# ==============================================================================
# Startup/Shutdown Events
# ==============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Behavioral Vector API starting up...")
    # Initialize services if needed
    logger.info("Behavioral Vector API ready")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Behavioral Vector API shutting down...")
    # Cleanup services
    from .bv_storage import get_bv_storage
    storage = get_bv_storage()
    await storage.close()
    logger.info("Behavioral Vector API stopped")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
