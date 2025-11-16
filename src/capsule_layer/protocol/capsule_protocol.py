"""
Capsule Protocol Specification

Platform-agnostic protocol for Deploy Anywhere Capsules (DACs).
Defines the core data structures, state machine, and actions that
enable capsules to run on any screen, any platform, any device.

This is the single source of truth for capsule behavior across:
- iOS (ActivityKit Live Activities)
- Android (Notifications, Widgets)
- Web (PWA, Push Notifications)
- Desktop (Electron, System Notifications)
- CLI (Terminal UI)
- Future platforms (watchOS, tvOS, VisionOS, etc.)
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
import json

# ============================================================================
# CAPSULE TYPES
# ============================================================================

class CapsuleType(str, Enum):
    """Capsule types with associated icons and colors"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    COST = "cost"
    COMPLIANCE = "compliance"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    ALERT = "alert"
    TASK = "task"
    NOTIFICATION = "notification"
    CUSTOM = "custom"

# ============================================================================
# CAPSULE STATES
# ============================================================================

class CapsuleStatus(str, Enum):
    """Capsule lifecycle states"""
    PENDING = "pending"          # Created but not yet active
    ACTIVE = "active"            # Currently active and visible
    IN_PROGRESS = "in_progress"  # Action being performed
    RESOLVED = "resolved"        # Issue resolved
    DISMISSED = "dismissed"      # User dismissed
    EXPIRED = "expired"          # Timed out
    FAILED = "failed"            # Action failed
    ARCHIVED = "archived"        # Moved to history

# ============================================================================
# CAPSULE ACTIONS
# ============================================================================

class CapsuleAction(str, Enum):
    """Available actions users can perform on capsules"""
    MITIGATE = "mitigate"        # Fix the issue
    INSPECT = "inspect"          # View details
    DISMISS = "dismiss"          # Ignore for now
    APPROVE = "approve"          # Approve request
    REJECT = "reject"            # Reject request
    ESCALATE = "escalate"        # Escalate to human
    RETRY = "retry"              # Retry failed action
    CANCEL = "cancel"            # Cancel ongoing action
    ACKNOWLEDGE = "acknowledge"  # Acknowledge notification
    CUSTOM = "custom"            # Custom action

# ============================================================================
# CAPSULE PRIORITY
# ============================================================================

class CapsulePriority(int, Enum):
    """Priority levels (1-5)"""
    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1

# ============================================================================
# CAPSULE PRESENTATION MODES
# ============================================================================

class PresentationMode(str, Enum):
    """How capsule should be presented on different platforms"""
    COMPACT = "compact"          # Minimal (iOS Dynamic Island compact)
    MINIMAL = "minimal"          # Icon only (iOS Dynamic Island minimal)
    EXPANDED = "expanded"        # Full details (iOS Dynamic Island expanded)
    FULL = "full"                # Full screen (Web, Desktop)
    BANNER = "banner"            # Banner notification (Android, Web)
    WIDGET = "widget"            # Home screen widget (Android, iOS)
    LOCK_SCREEN = "lock_screen"  # Lock screen (iOS, Android)
    STANDBY = "standby"          # StandBy mode (iOS 17+)

# ============================================================================
# CAPSULE ATTRIBUTES (Static)
# ============================================================================

class CapsuleAttributes(BaseModel):
    """
    Static attributes that don't change during capsule lifecycle.
    These define the capsule's identity and appearance.
    """
    
    # Identity
    capsule_id: str = Field(..., description="Unique identifier (UTID)")
    capsule_type: CapsuleType = Field(..., description="Type of capsule")
    
    # Presentation
    title: str = Field(..., max_length=100, description="Capsule title")
    icon_name: str = Field(..., description="Icon identifier (SF Symbol, Material Icon, etc.)")
    primary_color: str = Field(..., description="Primary color (hex, named, or theme token)")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User or system that created capsule")
    source_service: Optional[str] = Field(None, description="Originating service (OBMI, DGM, etc.)")
    
    # Configuration
    max_duration_seconds: int = Field(28800, description="Max lifetime (8 hours default)")
    auto_dismiss: bool = Field(True, description="Auto-dismiss after resolution")
    requires_acknowledgment: bool = Field(False, description="Requires explicit user acknowledgment")
    
    # Platform-specific hints
    platform_hints: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific rendering hints")
    
    @validator('primary_color')
    def validate_color(cls, v):
        """Validate color format"""
        if v.startswith('#'):
            # Hex color
            if len(v) not in [4, 7, 9]:  # #RGB, #RRGGBB, #RRGGBBAA
                raise ValueError("Invalid hex color format")
        elif v.startswith('rgb'):
            # RGB/RGBA color
            pass
        # Otherwise assume named color or theme token
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "capsule_id": "UTID:obmi:security:a1b2c3d4",
                "capsule_type": "security",
                "title": "Security Alert Detected",
                "icon_name": "shield.fill",
                "primary_color": "#FF3B30",
                "created_at": "2025-11-16T08:00:00Z",
                "created_by": "obmi-enterprise",
                "source_service": "obmi",
                "max_duration_seconds": 28800,
                "auto_dismiss": True,
                "requires_acknowledgment": False,
                "platform_hints": {
                    "ios": {"interruption_level": "time-sensitive"},
                    "android": {"channel_id": "security_alerts"}
                }
            }
        }

# ============================================================================
# CAPSULE CONTENT STATE (Dynamic)
# ============================================================================

class CapsuleContentState(BaseModel):
    """
    Dynamic state that changes during capsule lifecycle.
    This is what gets updated in real-time via WebSocket or push notifications.
    """
    
    # Status
    status: CapsuleStatus = Field(..., description="Current lifecycle status")
    status_message: str = Field(..., max_length=200, description="Human-readable status message")
    
    # Progress
    progress: float = Field(0.0, ge=0.0, le=1.0, description="Progress (0.0 to 1.0)")
    progress_label: Optional[str] = Field(None, description="Progress label (e.g., '3 of 5 steps')")
    
    # Metrics
    metric_value: str = Field(..., description="Primary metric value")
    metric_label: str = Field(..., description="Metric label")
    secondary_metrics: List[Dict[str, str]] = Field(default_factory=list, description="Additional metrics")
    
    # Timing
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    
    # Actions
    available_actions: List[CapsuleAction] = Field(default_factory=list, description="Actions user can perform")
    action_count: int = Field(0, description="Number of available actions")
    
    # Priority & Urgency
    priority: CapsulePriority = Field(CapsulePriority.MEDIUM, description="Current priority")
    is_urgent: bool = Field(False, description="Requires immediate attention")
    is_stale: bool = Field(False, description="Data is stale (needs refresh)")
    
    # Alerts
    alert_title: Optional[str] = Field(None, description="Alert title for critical updates")
    alert_message: Optional[str] = Field(None, description="Alert message for critical updates")
    alert_sound: bool = Field(False, description="Play sound with alert")
    
    # Rich content
    details_url: Optional[str] = Field(None, description="URL for full details")
    thumbnail_url: Optional[str] = Field(None, description="Thumbnail image URL")
    
    # Platform-specific data
    platform_data: Dict[str, Any] = Field(default_factory=dict, description="Platform-specific state data")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "active",
                "status_message": "Suspicious activity detected in production cluster",
                "progress": 0.65,
                "progress_label": "3 of 5 threats mitigated",
                "metric_value": "23 events",
                "metric_label": "Total Events",
                "secondary_metrics": [
                    {"label": "Severity", "value": "High"},
                    {"label": "Affected Services", "value": "3"}
                ],
                "last_updated": "2025-11-16T08:15:00Z",
                "estimated_completion": "2025-11-16T08:30:00Z",
                "available_actions": ["mitigate", "inspect", "escalate"],
                "action_count": 3,
                "priority": 5,
                "is_urgent": True,
                "is_stale": False,
                "alert_title": None,
                "alert_message": None,
                "alert_sound": False,
                "details_url": "https://portal.industriverse.com/security/alert-123",
                "thumbnail_url": None,
                "platform_data": {}
            }
        }

# ============================================================================
# COMPLETE CAPSULE
# ============================================================================

class Capsule(BaseModel):
    """
    Complete capsule with both static attributes and dynamic state.
    This is the full representation sent to clients.
    """
    
    attributes: CapsuleAttributes
    content_state: CapsuleContentState
    
    # Computed properties
    @property
    def is_expired(self) -> bool:
        """Check if capsule has expired"""
        age_seconds = (datetime.utcnow() - self.attributes.created_at).total_seconds()
        return age_seconds > self.attributes.max_duration_seconds
    
    @property
    def age_seconds(self) -> float:
        """Get capsule age in seconds"""
        return (datetime.utcnow() - self.attributes.created_at).total_seconds()
    
    @property
    def time_remaining_seconds(self) -> float:
        """Get remaining time before expiration"""
        return max(0, self.attributes.max_duration_seconds - self.age_seconds)
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return self.model_dump_json()
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Capsule':
        """Deserialize from JSON"""
        return cls.model_validate_json(json_str)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Capsule':
        """Create from dictionary"""
        return cls.model_validate(data)

# ============================================================================
# CAPSULE ACTION RESULT
# ============================================================================

class CapsuleActionResult(BaseModel):
    """Result of performing an action on a capsule"""
    
    capsule_id: str
    action: CapsuleAction
    success: bool
    message: str
    new_state: Optional[CapsuleContentState] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    error_code: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "capsule_id": "UTID:obmi:security:a1b2c3d4",
                "action": "mitigate",
                "success": True,
                "message": "Mitigation successful",
                "new_state": {
                    "status": "resolved",
                    "status_message": "Threat mitigated successfully",
                    "progress": 1.0
                },
                "timestamp": "2025-11-16T08:20:00Z",
                "error_code": None
            }
        }

# ============================================================================
# CAPSULE EVENT
# ============================================================================

class CapsuleEventType(str, Enum):
    """Types of capsule events"""
    CREATED = "created"
    UPDATED = "updated"
    ACTION_PERFORMED = "action_performed"
    STATUS_CHANGED = "status_changed"
    EXPIRED = "expired"
    DISMISSED = "dismissed"
    DELETED = "deleted"

class CapsuleEvent(BaseModel):
    """Event emitted when capsule changes"""
    
    event_type: CapsuleEventType
    capsule_id: str
    capsule: Optional[Capsule] = None
    action_result: Optional[CapsuleActionResult] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

# ============================================================================
# PROTOCOL VERSION
# ============================================================================

CAPSULE_PROTOCOL_VERSION = "1.0.0"

def get_protocol_version() -> str:
    """Get current protocol version"""
    return CAPSULE_PROTOCOL_VERSION
