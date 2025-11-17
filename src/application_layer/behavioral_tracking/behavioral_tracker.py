"""
Behavioral Tracker for Capsule Interactions.

This module tracks user interactions with capsules to build behavioral profiles
and enable adaptive UX personalization. Part of Week 9: Behavioral Tracking Infrastructure.

Features:
- Event logging for all capsule interactions
- Event schema validation
- Kafka topic integration for streaming events
- User behavioral pattern analysis
- Duration tracking and engagement metrics
"""

import logging
import json
import uuid
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """Enumeration of interaction types."""
    TAP = "tap"
    CLICK = "click"
    EXPAND = "expand"
    COLLAPSE = "collapse"
    PIN = "pin"
    UNPIN = "unpin"
    DRAG = "drag"
    RESIZE = "resize"
    ACTION = "action"
    COMPLETE = "complete"
    DISMISS = "dismiss"
    ACKNOWLEDGE = "acknowledge"
    DECISION = "decision"
    SCROLL = "scroll"
    HOVER = "hover"
    SWIPE = "swipe"


class EventSeverity(Enum):
    """Severity levels for interaction events."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class InteractionEvent:
    """Schema for capsule interaction events."""

    # Event identity
    event_id: str
    timestamp: str
    event_type: str  # InteractionType
    severity: str = "info"

    # User context
    user_id: str = "anonymous"
    session_id: str = ""
    device_id: str = ""
    device_type: str = "web"  # web, ios, android, desktop

    # Capsule context
    capsule_id: str = ""
    capsule_type: str = "status"  # task, workflow, alert, status, decision
    capsule_category: str = ""

    # Interaction details
    interaction_target: str = "capsule"  # capsule, action, component
    action_id: Optional[str] = None
    component_id: Optional[str] = None

    # Timing metrics
    duration_ms: Optional[int] = None
    time_since_last_interaction_ms: Optional[int] = None

    # Interaction data
    interaction_data: Dict[str, Any] = None

    # Result
    success: bool = True
    error_message: Optional[str] = None

    # Behavioral context
    context: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.interaction_data is None:
            self.interaction_data = {}
        if self.context is None:
            self.context = {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    def validate(self) -> tuple[bool, Optional[str]]:
        """
        Validate event schema.

        Returns:
            tuple: (is_valid, error_message)
        """
        # Required fields
        if not self.event_id:
            return False, "event_id is required"

        if not self.timestamp:
            return False, "timestamp is required"

        if not self.event_type:
            return False, "event_type is required"

        # Validate event_type
        valid_event_types = [e.value for e in InteractionType]
        if self.event_type not in valid_event_types:
            return False, f"event_type must be one of {valid_event_types}"

        # Validate severity
        valid_severities = [s.value for s in EventSeverity]
        if self.severity not in valid_severities:
            return False, f"severity must be one of {valid_severities}"

        # Validate device_type
        valid_device_types = ["web", "ios", "android", "desktop", "wearable"]
        if self.device_type not in valid_device_types:
            return False, f"device_type must be one of {valid_device_types}"

        # Validate capsule_type
        valid_capsule_types = ["task", "workflow", "alert", "status", "decision", "custom"]
        if self.capsule_type not in valid_capsule_types:
            return False, f"capsule_type must be one of {valid_capsule_types}"

        # Validate interaction_target
        valid_targets = ["capsule", "action", "component"]
        if self.interaction_target not in valid_targets:
            return False, f"interaction_target must be one of {valid_targets}"

        # Validate timing metrics
        if self.duration_ms is not None and self.duration_ms < 0:
            return False, "duration_ms must be non-negative"

        if self.time_since_last_interaction_ms is not None and self.time_since_last_interaction_ms < 0:
            return False, "time_since_last_interaction_ms must be non-negative"

        return True, None


class BehavioralTracker:
    """
    Tracks user behavioral patterns from capsule interactions.

    This class wraps the CapsuleInteractionHandler to log and analyze
    all user interactions for adaptive UX personalization.
    """

    def __init__(self, interaction_handler=None, kafka_enabled: bool = False):
        """
        Initialize the Behavioral Tracker.

        Args:
            interaction_handler: Reference to CapsuleInteractionHandler
            kafka_enabled: Whether to enable Kafka streaming
        """
        self.interaction_handler = interaction_handler
        self.kafka_enabled = kafka_enabled

        # In-memory event storage (for development)
        self.events: List[InteractionEvent] = []
        self.max_events_in_memory = 10000

        # User session tracking
        self.user_sessions: Dict[str, Dict[str, Any]] = {}

        # Last interaction timestamp per user
        self.last_interaction_time: Dict[str, datetime] = {}

        # Kafka producer (to be initialized if enabled)
        self.kafka_producer = None
        self.kafka_topic = "capsule-interactions"

        if self.kafka_enabled:
            self._init_kafka()

        logger.info("Behavioral Tracker initialized")

    def _init_kafka(self):
        """Initialize Kafka producer for event streaming."""
        try:
            # Import Kafka client
            from kafka import KafkaProducer

            self.kafka_producer = KafkaProducer(
                bootstrap_servers=['localhost:9092'],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )

            logger.info(f"Kafka producer initialized for topic: {self.kafka_topic}")
        except ImportError:
            logger.warning("kafka-python not installed, Kafka streaming disabled")
            self.kafka_enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.kafka_enabled = False

    def track_interaction(
        self,
        capsule: Dict[str, Any],
        interaction_type: str,
        data: Dict[str, Any],
        user_id: str = "anonymous",
        session_id: str = "",
        device_id: str = "",
        device_type: str = "web"
    ) -> Dict[str, Any]:
        """
        Track a capsule interaction event.

        Args:
            capsule: Capsule data
            interaction_type: Type of interaction
            data: Interaction data
            user_id: User identifier
            session_id: Session identifier
            device_id: Device identifier
            device_type: Device type (web, ios, android, desktop)

        Returns:
            Interaction response
        """
        # Record start time
        start_time = datetime.utcnow()

        # Calculate time since last interaction
        time_since_last = None
        if user_id in self.last_interaction_time:
            time_since_last = int((start_time - self.last_interaction_time[user_id]).total_seconds() * 1000)

        # Update last interaction time
        self.last_interaction_time[user_id] = start_time

        # Delegate to interaction handler if available
        response = {}
        success = True
        error_message = None

        if self.interaction_handler:
            try:
                response = self.interaction_handler.handle_interaction(capsule, interaction_type, data)
                success = response.get("success", True)
                if not success:
                    error_message = response.get("error", "Unknown error")
            except Exception as e:
                logger.error(f"Error in interaction handler: {e}")
                success = False
                error_message = str(e)
                response = {"error": str(e)}

        # Calculate duration
        end_time = datetime.utcnow()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Determine interaction target
        target = data.get("target", "capsule")
        action_id = None
        component_id = None

        if target.startswith("action:"):
            interaction_target = "action"
            action_id = target.split(":", 1)[1]
        elif target.startswith("component:"):
            interaction_target = "component"
            component_id = target.split(":", 1)[1]
        else:
            interaction_target = "capsule"

        # Create interaction event
        event = InteractionEvent(
            event_id=str(uuid.uuid4()),
            timestamp=start_time.isoformat(),
            event_type=interaction_type,
            severity="info" if success else "error",
            user_id=user_id,
            session_id=session_id or self._get_or_create_session(user_id),
            device_id=device_id,
            device_type=device_type,
            capsule_id=capsule.get("capsule_id", ""),
            capsule_type=capsule.get("capsule_type", "status"),
            capsule_category=capsule.get("category", ""),
            interaction_target=interaction_target,
            action_id=action_id,
            component_id=component_id,
            duration_ms=duration_ms,
            time_since_last_interaction_ms=time_since_last,
            interaction_data=data,
            success=success,
            error_message=error_message,
            context=self._extract_context(capsule, user_id, session_id)
        )

        # Validate event
        is_valid, validation_error = event.validate()
        if not is_valid:
            logger.error(f"Event validation failed: {validation_error}")
            event.severity = "error"
            event.error_message = f"Validation error: {validation_error}"

        # Store event
        self._store_event(event)

        # Stream to Kafka if enabled
        if self.kafka_enabled and is_valid:
            self._stream_to_kafka(event)

        # Update session analytics
        self._update_session_analytics(user_id, session_id, event)

        logger.info(
            f"Tracked interaction: user={user_id}, type={interaction_type}, "
            f"capsule={capsule.get('capsule_id', '')}, duration={duration_ms}ms, "
            f"success={success}"
        )

        # Add tracking metadata to response
        response["_tracking"] = {
            "event_id": event.event_id,
            "tracked": True,
            "duration_ms": duration_ms
        }

        return response

    def _store_event(self, event: InteractionEvent):
        """Store event in memory (and potentially persistent storage)."""
        self.events.append(event)

        # Trim old events if limit exceeded
        if len(self.events) > self.max_events_in_memory:
            self.events = self.events[-self.max_events_in_memory:]

    def _stream_to_kafka(self, event: InteractionEvent):
        """Stream event to Kafka topic."""
        if not self.kafka_producer:
            return

        try:
            future = self.kafka_producer.send(
                self.kafka_topic,
                value=event.to_dict()
            )

            # Optional: Wait for confirmation
            # record_metadata = future.get(timeout=10)

            logger.debug(f"Event streamed to Kafka: {event.event_id}")
        except Exception as e:
            logger.error(f"Failed to stream event to Kafka: {e}")

    def _get_or_create_session(self, user_id: str) -> str:
        """Get or create user session."""
        if user_id not in self.user_sessions:
            session_id = str(uuid.uuid4())
            self.user_sessions[user_id] = {
                "session_id": session_id,
                "started_at": datetime.utcnow().isoformat(),
                "event_count": 0,
                "capsules_interacted": set(),
                "interaction_types": {}
            }
            return session_id

        return self.user_sessions[user_id]["session_id"]

    def _extract_context(
        self,
        capsule: Dict[str, Any],
        user_id: str,
        session_id: str
    ) -> Dict[str, Any]:
        """Extract behavioral context from interaction."""
        context = {
            "capsule_state": capsule.get("state", "active"),
            "capsule_priority": capsule.get("priority", "normal"),
            "user_session_event_count": self.user_sessions.get(user_id, {}).get("event_count", 0),
            "timestamp": datetime.utcnow().isoformat()
        }

        # Add capsule-specific context
        if capsule.get("capsule_type") == "task":
            context["task_status"] = capsule.get("task_info", {}).get("status", "")
            context["task_progress"] = capsule.get("task_info", {}).get("completion", 0)

        elif capsule.get("capsule_type") == "workflow":
            context["workflow_step"] = capsule.get("workflow_info", {}).get("current_step", 0)
            context["workflow_progress"] = capsule.get("content", {}).get("progress", 0)

        elif capsule.get("capsule_type") == "alert":
            context["alert_severity"] = capsule.get("alert_info", {}).get("severity", "info")
            context["alert_acknowledged"] = capsule.get("alert_info", {}).get("acknowledged", False)

        return context

    def _update_session_analytics(self, user_id: str, session_id: str, event: InteractionEvent):
        """Update session analytics with new event."""
        if user_id not in self.user_sessions:
            self._get_or_create_session(user_id)

        session = self.user_sessions[user_id]
        session["event_count"] += 1
        session["capsules_interacted"].add(event.capsule_id)

        # Track interaction type frequency
        if event.event_type not in session["interaction_types"]:
            session["interaction_types"][event.event_type] = 0
        session["interaction_types"][event.event_type] += 1

        session["last_interaction_at"] = event.timestamp

    def get_user_events(
        self,
        user_id: str,
        limit: int = 100,
        event_type: Optional[str] = None,
        capsule_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[InteractionEvent]:
        """
        Get interaction events for a user.

        Args:
            user_id: User identifier
            limit: Maximum number of events to return
            event_type: Filter by event type
            capsule_type: Filter by capsule type
            start_time: Filter events after this time
            end_time: Filter events before this time

        Returns:
            List of interaction events
        """
        filtered_events = []

        for event in reversed(self.events):  # Most recent first
            # Apply filters
            if event.user_id != user_id:
                continue

            if event_type and event.event_type != event_type:
                continue

            if capsule_type and event.capsule_type != capsule_type:
                continue

            if start_time:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time < start_time:
                    continue

            if end_time:
                event_time = datetime.fromisoformat(event.timestamp)
                if event_time > end_time:
                    continue

            filtered_events.append(event)

            if len(filtered_events) >= limit:
                break

        return filtered_events

    def get_session_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Get summary of user's current session.

        Args:
            user_id: User identifier

        Returns:
            Session summary dictionary
        """
        if user_id not in self.user_sessions:
            return {"error": "No active session found"}

        session = self.user_sessions[user_id]

        return {
            "session_id": session["session_id"],
            "started_at": session["started_at"],
            "event_count": session["event_count"],
            "unique_capsules": len(session["capsules_interacted"]),
            "interaction_types": dict(session["interaction_types"]),
            "last_interaction_at": session.get("last_interaction_at")
        }

    def calculate_engagement_score(self, user_id: str, time_window_minutes: int = 30) -> float:
        """
        Calculate user engagement score based on recent interactions.

        Args:
            user_id: User identifier
            time_window_minutes: Time window for engagement calculation

        Returns:
            Engagement score (0.0 to 1.0)
        """
        # Get recent events
        start_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)
        recent_events = self.get_user_events(
            user_id,
            limit=1000,
            start_time=start_time
        )

        if not recent_events:
            return 0.0

        # Calculate engagement metrics
        event_count = len(recent_events)
        unique_capsules = len(set(e.capsule_id for e in recent_events))
        avg_duration_ms = sum(e.duration_ms or 0 for e in recent_events) / event_count

        # Calculate time between interactions
        interaction_times = [datetime.fromisoformat(e.timestamp) for e in recent_events]
        interaction_times.sort()

        gaps = []
        for i in range(1, len(interaction_times)):
            gap = (interaction_times[i] - interaction_times[i-1]).total_seconds()
            gaps.append(gap)

        avg_gap_seconds = sum(gaps) / len(gaps) if gaps else 0

        # Normalize metrics to 0-1 scale
        event_score = min(event_count / 50, 1.0)  # 50+ events = max score
        capsule_diversity_score = min(unique_capsules / 10, 1.0)  # 10+ capsules = max score
        duration_score = min(avg_duration_ms / 5000, 1.0)  # 5s+ avg duration = max score
        frequency_score = max(0, 1.0 - (avg_gap_seconds / 60))  # < 1 min gaps = max score

        # Weighted engagement score
        engagement_score = (
            event_score * 0.3 +
            capsule_diversity_score * 0.2 +
            duration_score * 0.2 +
            frequency_score * 0.3
        )

        return round(engagement_score, 3)

    def close(self):
        """Close Kafka connections and cleanup."""
        if self.kafka_producer:
            try:
                self.kafka_producer.flush()
                self.kafka_producer.close()
                logger.info("Kafka producer closed")
            except Exception as e:
                logger.error(f"Error closing Kafka producer: {e}")


# Singleton instance
_behavioral_tracker_instance = None


def get_behavioral_tracker(
    interaction_handler=None,
    kafka_enabled: bool = False
) -> BehavioralTracker:
    """
    Get or create the singleton BehavioralTracker instance.

    Args:
        interaction_handler: Reference to CapsuleInteractionHandler
        kafka_enabled: Whether to enable Kafka streaming

    Returns:
        BehavioralTracker instance
    """
    global _behavioral_tracker_instance

    if _behavioral_tracker_instance is None:
        _behavioral_tracker_instance = BehavioralTracker(
            interaction_handler=interaction_handler,
            kafka_enabled=kafka_enabled
        )

    return _behavioral_tracker_instance
