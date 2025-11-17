"""
Behavioral Tracking Module for Capsule Interactions.

This module provides behavioral tracking and analysis capabilities
for adaptive UX personalization. Part of Week 9: Behavioral Tracking Infrastructure.

Components:
- BehavioralTracker: Main tracking service
- InteractionEvent: Event schema and validation
- Kafka integration for event streaming
- Session analytics and engagement scoring
"""

from .behavioral_tracker import (
    BehavioralTracker,
    InteractionEvent,
    InteractionType,
    EventSeverity,
    get_behavioral_tracker
)

__all__ = [
    "BehavioralTracker",
    "InteractionEvent",
    "InteractionType",
    "EventSeverity",
    "get_behavioral_tracker"
]

__version__ = "1.0.0"
