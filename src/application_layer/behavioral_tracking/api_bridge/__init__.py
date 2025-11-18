"""
Behavioral Tracking API Bridge
Week 17 Day 2: Unified Behavioral Tracking Integration

This package provides the API bridge connecting Week 16 TypeScript/JavaScript frontends
to the Week 9 Python behavioral tracking backend.

Components:
- behavioral_tracking_client.py: Python client for database operations
- behavioral_tracking_api.py: FastAPI REST endpoints
- BehavioralTrackingClient.ts: TypeScript/JavaScript client

Usage:
    # Start API server
    python behavioral_tracking_api.py

    # Use from TypeScript
    import BehavioralTrackingClient from './BehavioralTrackingClient';
    const client = new BehavioralTrackingClient('http://localhost:8001');
    await client.trackInteraction({...});
"""

from .behavioral_tracking_client import (
    BehavioralTrackingClient,
    InteractionEventCreate,
    BehavioralVectorResponse,
    UserSessionResponse,
    EngagementScoreResponse
)

__all__ = [
    "BehavioralTrackingClient",
    "InteractionEventCreate",
    "BehavioralVectorResponse",
    "UserSessionResponse",
    "EngagementScoreResponse"
]

__version__ = "1.0.0"
__author__ = "Industriverse Team"
