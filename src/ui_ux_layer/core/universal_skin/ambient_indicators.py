"""
Ambient Indicators for Universal Skin Shell in the Industriverse UI/UX Layer.

This module implements system-wide ambient awareness indicators for the Universal Skin Shell,
providing subtle, non-intrusive signals that communicate system state, agent activity,
trust levels, and other important information.

Author: Manus
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from enum import Enum
import uuid

class IndicatorType(Enum):
    """Enumeration of ambient indicator types."""
    SYSTEM_STATUS = "system_status"
    AGENT_ACTIVITY = "agent_activity"
    TRUST_LEVEL = "trust_level"
    DECISION_CONFIDENCE = "decision_confidence"
    WORKFLOW_PROGRESS = "workflow_progress"
    ALERT = "alert"
    NOTIFICATION = "notification"
    CONTEXT_CHANGE = "context_change"
    RESOURCE_USAGE = "resource_usage"
    CONNECTIVITY = "connectivity"
    SECURITY = "security"
    CUSTOM = "custom"

class IndicatorPriority(Enum):
    """Enumeration of ambient indicator priorities."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

class IndicatorVisibility(Enum):
    """Enumeration of ambient indicator visibility levels."""
    SUBTLE = "subtle"  # Barely noticeable, ambient
    NORMAL = "normal"  # Standard visibility
    PROMINENT = "prominent"  # More noticeable
    URGENT = "urgent"  # Demands attention

class IndicatorAnimation(Enum):
    """Enumeration of ambient indicator animation types."""
    NONE = "none"
    PULSE = "pulse"
    FADE = "fade"
    GLOW = "glow"
    RIPPLE = "ripple"
    BREATHE = "breathe"
    BOUNCE = "bounce"
    ROTATE = "rotate"
    CUSTOM = "custom"

class IndicatorPosition(Enum):
    """Enumeration of ambient indicator positions."""
    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    MIDDLE_LEFT = "middle_left"
    MIDDLE_CENTER = "middle_center"
    MIDDLE_RIGHT = "middle_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"
    FLOATING = "floating"
    CUSTOM = "custom"

class AmbientIndicator:
    """Represents an ambient indicator in the Universal Skin Shell."""
    
    def __init__(self,
                 indicator_type: IndicatorType,
                 id: Optional[str] = None,
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 value: Any = None,
                 min_value: Optional[float] = None,
                 max_value: Optional[float] = None,
                 priority: IndicatorPriority = IndicatorPriority.MEDIUM,
                 visibility: IndicatorVisibility = IndicatorVisibility.NORMAL,
                 animation: IndicatorAnimation = IndicatorAnimation.NONE,
                 position: IndicatorPosition = IndicatorPosition.TOP_RIGHT,
                 color: Optional[str] = None,
                 icon: Optional[str] = None,
                 sound: Optional[str] = None,
                 haptic: Optional[str] = None,
                 duration: Optional[float] = None,
                 auto_dismiss: bool = False,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an ambient indicator.
        
        Args:
            indicator_type: Type of indicator
            id: Unique identifier for this indicator (generated if not provided)
            title: Human-readable title for this indicator
            description: Detailed description of this indicator
            value: Current value of the indicator
            min_value: Minimum possible value (for numeric indicators)
            max_value: Maximum possible value (for numeric indicators)
            priority: Priority level of this indicator
            visibility: Visibility level of this indicator
            animation: Animation type for this indicator
            position: Position of this indicator in the UI
            color: Color of this indicator (CSS color string)
            icon: Icon for this indicator (icon name or URL)
            sound: Sound to play when this indicator is shown (sound name or URL)
            haptic: Haptic feedback pattern to use when this indicator is shown
            duration: Duration in seconds for this indicator to be shown (None for persistent)
            auto_dismiss: Whether this indicator should be automatically dismissed after duration
            metadata: Additional metadata for this indicator
        """
        self.indicator_type = indicator_type
        self.id = id or str(uuid.uuid4())
        self.title = title
        self.description = description
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.priority = priority
        self.visibility = visibility
        self.animation = animation
        self.position = position
        self.color = color
        self.icon = icon
        self.sound = sound
        self.haptic = haptic
        self.duration = duration
        self.auto_dismiss = auto_dismiss
        self.metadata = metadata or {}
        self.created_at = time.time()
        self.updated_at = self.created_at
        self.dismissed = False
        self.dismissed_at = None
        self.custom_animation_params = {}
        self.custom_position_params = {}
        
    def update(self, 
               value: Optional[Any] = None, 
               priority: Optional[IndicatorPriority] = None,
               visibility: Optional[IndicatorVisibility] = None,
               animation: Optional[IndicatorAnimation] = None,
               position: Optional[IndicatorPosition] = None,
               color: Optional[str] = None,
               icon: Optional[str] = None,
               sound: Optional[str] = None,
               haptic: Optional[str] = None,
               duration: Optional[float] = None,
               auto_dismiss: Optional[bool] = None,
               metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update this indicator with new values.
        
        Args:
            value: New value for the indicator
            priority: New priority level
            visibility: New visibility level
            animation: New animation type
            position: New position
            color: New color
            icon: New icon
            sound: New sound
            haptic: New haptic feedback pattern
            duration: New duration
            auto_dismiss: New auto-dismiss setting
            metadata: New or updated metadata
        """
        if value is not None:
            self.value = value
        if priority is not None:
            self.priority = priority
        if visibility is not None:
            self.visibility = visibility
        if animation is not None:
            self.animation = animation
        if position is not None:
            self.position = position
        if color is not None:
            self.color = color
        if icon is not None:
            self.icon = icon
        if sound is not None:
            self.sound = sound
        if haptic is not None:
            self.haptic = haptic
        if duration is not None:
            self.duration = duration
        if auto_dismiss is not None:
            self.auto_dismiss = auto_dismiss
        if metadata is not None:
            self.metadata.update(metadata)
            
        self.updated_at = time.time()
        
    def dismiss(self) -> None:
        """Dismiss this indicator."""
        self.dismissed = True
        self.dismissed_at = time.time()
        
    def is_expired(self) -> bool:
        """Check if this indicator has expired based on its duration."""
        if self.duration is None:
            return False
        return (time.time() - self.updated_at) > self.duration
    
    def get_normalized_value(self) -> Optional[float]:
        """
        Get the normalized value of this indicator (0.0 to 1.0).
        
        Returns:
            Normalized value between 0.0 and 1.0, or None if not applicable
        """
        if self.value is None or self.min_value is None or self.max_value is None:
            return None
            
        try:
            value_range = self.max_value - self.min_value
            if value_range <= 0:
                return 0.0
                
            normalized = (float(self.value) - self.min_value) / value_range
            return max(0.0, min(1.0, normalized))
        except (TypeError, ValueError):
            return None
            
    def set_custom_animation(self, animation_type: str, params: Dict[str, Any]) -> None:
        """
        Set custom animation parameters.
        
        Args:
            animation_type: Type of custom animation
            params: Parameters for the custom animation
        """
        self.animation = IndicatorAnimation.CUSTOM
        self.metadata["custom_animation_type"] = animation_type
        self.custom_animation_params = params
        
    def set_custom_position(self, position_type: str, params: Dict[str, Any]) -> None:
        """
        Set custom position parameters.
        
        Args:
            position_type: Type of custom position
            params: Parameters for the custom position
        """
        self.position = IndicatorPosition.CUSTOM
        self.metadata["custom_position_type"] = position_type
        self.custom_position_params = params
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this indicator to a dictionary representation."""
        return {
            "id": self.id,
            "indicator_type": self.indicator_type.value,
            "title": self.title,
            "description": self.description,
            "value": self.value,
            "min_value": self.min_value,
            "max_value": self.max_value,
            "priority": self.priority.value,
            "visibility": self.visibility.value,
            "animation": self.animation.value,
            "position": self.position.value,
            "color": self.color,
            "icon": self.icon,
            "sound": self.sound,
            "haptic": self.haptic,
            "duration": self.duration,
            "auto_dismiss": self.auto_dismiss,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "dismissed": self.dismissed,
            "dismissed_at": self.dismissed_at,
            "custom_animation_params": self.custom_animation_params,
            "custom_position_params": self.custom_position_params
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AmbientIndicator':
        """Create an ambient indicator from a dictionary representation."""
        indicator = cls(
            indicator_type=IndicatorType(data["indicator_type"]),
            id=data.get("id"),
            title=data.get("title"),
            description=data.get("description"),
            value=data.get("value"),
            min_value=data.get("min_value"),
            max_value=data.get("max_value"),
            priority=IndicatorPriority(data["priority"]) if "priority" in data else IndicatorPriority.MEDIUM,
            visibility=IndicatorVisibility(data["visibility"]) if "visibility" in data else IndicatorVisibility.NORMAL,
            animation=IndicatorAnimation(data["animation"]) if "animation" in data else IndicatorAnimation.NONE,
            position=IndicatorPosition(data["position"]) if "position" in data else IndicatorPosition.TOP_RIGHT,
            color=data.get("color"),
            icon=data.get("icon"),
            sound=data.get("sound"),
            haptic=data.get("haptic"),
            duration=data.get("duration"),
            auto_dismiss=data.get("auto_dismiss", False),
            metadata=data.get("metadata", {})
        )
        
        indicator.created_at = data.get("created_at", time.time())
        indicator.updated_at = data.get("updated_at", indicator.created_at)
        indicator.dismissed = data.get("dismissed", False)
        indicator.dismissed_at = data.get("dismissed_at")
        indicator.custom_animation_params = data.get("custom_animation_params", {})
        indicator.custom_position_params = data.get("custom_position_params", {})
        
        return indicator

class IndicatorGroup:
    """Represents a group of related ambient indicators."""
    
    def __init__(self, 
                 id: str, 
                 title: Optional[str] = None,
                 description: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an indicator group.
        
        Args:
            id: Unique identifier for this group
            title: Human-readable title for this group
            description: Detailed description of this group
            metadata: Additional metadata for this group
        """
        self.id = id
        self.title = title
        self.description = description
        self.metadata = metadata or {}
        self.indicators: Dict[str, AmbientIndicator] = {}
        
    def add_indicator(self, indicator: AmbientIndicator) -> None:
        """Add an indicator to this group."""
        self.indicators[indicator.id] = indicator
        
    def remove_indicator(self, indicator_id: str) -> Optional[AmbientIndicator]:
        """Remove an indicator from this group."""
        return self.indicators.pop(indicator_id, None)
        
    def get_indicator(self, indicator_id: str) -> Optional[AmbientIndicator]:
        """Get an indicator by ID."""
        return self.indicators.get(indicator_id)
        
    def get_all_indicators(self) -> List[AmbientIndicator]:
        """Get all indicators in this group."""
        return list(self.indicators.values())
        
    def get_highest_priority(self) -> Optional[IndicatorPriority]:
        """Get the highest priority of any indicator in this group."""
        if not self.indicators:
            return None
            
        return max(
            (indicator.priority for indicator in self.indicators.values()),
            default=None
        )
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this group to a dictionary representation."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "metadata": self.metadata,
            "indicators": {
                indicator_id: indicator.to_dict()
                for indicator_id, indicator in self.indicators.items()
            }
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IndicatorGroup':
        """Create an indicator group from a dictionary representation."""
        group = cls(
            id=data["id"],
            title=data.get("title"),
            description=data.get("description"),
            metadata=data.get("metadata", {})
        )
        
        for indicator_id, indicator_data in data.get("indicators", {}).items():
            indicator = AmbientIndicator.from_dict(indicator_data)
            group.add_indicator(indicator)
            
        return group

class IndicatorEvent:
    """Represents an event related to ambient indicators."""
    
    def __init__(self, 
                 event_type: str, 
                 indicator_id: str,
                 group_id: Optional[str] = None,
                 source: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an indicator event.
        
        Args:
            event_type: Type of event (e.g., "created", "updated", "dismissed")
            indicator_id: ID of the indicator this event relates to
            group_id: Optional ID of the group this indicator belongs to
            source: Optional source of the event
            metadata: Optional additional metadata for this event
        """
        self.event_type = event_type
        self.indicator_id = indicator_id
        self.group_id = group_id
        self.source = source
        self.metadata = metadata or {}
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this event to a dictionary representation."""
        return {
            "event_type": self.event_type,
            "indicator_id": self.indicator_id,
            "group_id": self.group_id,
            "source": self.source,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

class AmbientIndicators:
    """
    Manages system-wide ambient awareness indicators for the Universal Skin Shell.
    
    This class provides:
    - Indicator registration and management
    - Indicator grouping
    - Indicator event handling
    - Indicator rendering coordination
    - Indicator state persistence
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Ambient Indicators manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.indicators: Dict[str, AmbientIndicator] = {}
        self.groups: Dict[str, IndicatorGroup] = {}
        self.indicator_listeners: List[Callable[[IndicatorEvent], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize default indicator groups
        self._initialize_default_groups()
        
    def _initialize_default_groups(self) -> None:
        """Initialize default indicator groups."""
        default_groups = [
            ("system", "System Status", "Indicators related to system status"),
            ("agents", "Agent Activity", "Indicators related to agent activity"),
            ("trust", "Trust Levels", "Indicators related to trust and confidence"),
            ("workflows", "Workflow Progress", "Indicators related to workflow progress"),
            ("alerts", "Alerts", "System alerts and notifications"),
            ("resources", "Resource Usage", "Indicators related to resource usage"),
            ("security", "Security", "Indicators related to security status")
        ]
        
        for group_id, title, description in default_groups:
            self.register_group(IndicatorGroup(
                id=group_id,
                title=title,
                description=description
            ))
            
    def register_indicator(self, 
                          indicator: AmbientIndicator, 
                          group_id: Optional[str] = None) -> None:
        """
        Register a new ambient indicator.
        
        Args:
            indicator: The ambient indicator to register
            group_id: Optional group to add this indicator to
        """
        if indicator.id in self.indicators:
            self.logger.warning(f"Indicator with ID {indicator.id} already exists, overwriting")
            
        self.indicators[indicator.id] = indicator
        
        # Add to group if specified
        if group_id is not None:
            if group_id not in self.groups:
                self.logger.warning(f"Group with ID {group_id} not found, creating it")
                self.register_group(IndicatorGroup(id=group_id))
                
            self.groups[group_id].add_indicator(indicator)
            
        # Create and dispatch indicator event
        event = IndicatorEvent(
            event_type="created",
            indicator_id=indicator.id,
            group_id=group_id,
            source="system"
        )
        self._dispatch_indicator_event(event)
        
    def unregister_indicator(self, indicator_id: str) -> Optional[AmbientIndicator]:
        """
        Unregister an ambient indicator.
        
        Args:
            indicator_id: ID of the indicator to unregister
            
        Returns:
            The unregistered indicator, or None if not found
        """
        if indicator_id not in self.indicators:
            self.logger.warning(f"Indicator with ID {indicator_id} not found")
            return None
            
        indicator = self.indicators.pop(indicator_id)
        
        # Remove from any groups
        for group in self.groups.values():
            group.remove_indicator(indicator_id)
            
        # Create and dispatch indicator event
        event = IndicatorEvent(
            event_type="removed",
            indicator_id=indicator_id,
            source="system"
        )
        self._dispatch_indicator_event(event)
        
        return indicator
    
    def update_indicator(self, 
                        indicator_id: str, 
                        **update_kwargs) -> bool:
        """
        Update an existing ambient indicator.
        
        Args:
            indicator_id: ID of the indicator to update
            **update_kwargs: Keyword arguments to pass to the indicator's update method
            
        Returns:
            True if the update was successful, False otherwise
        """
        if indicator_id not in self.indicators:
            self.logger.warning(f"Cannot update unknown indicator: {indicator_id}")
            return False
            
        indicator = self.indicators[indicator_id]
        indicator.update(**update_kwargs)
        
        # Create and dispatch indicator event
        event = IndicatorEvent(
            event_type="updated",
            indicator_id=indicator_id,
            source="system",
            metadata=update_kwargs
        )
        self._dispatch_indicator_event(event)
        
        return True
    
    def get_indicator(self, indicator_id: str) -> Optional[AmbientIndicator]:
        """
        Get an ambient indicator by ID.
        
        Args:
            indicator_id: ID of the indicator to get
            
        Returns:
            The ambient indicator, or None if not found
        """
        return self.indicators.get(indicator_id)
    
    def get_all_indicators(self) -> List[AmbientIndicator]:
        """
        Get all registered ambient indicators.
        
        Returns:
            List of all ambient indicators
        """
        return list(self.indicators.values())
    
    def get_indicators_by_type(self, indicator_type: IndicatorType) -> List[AmbientIndicator]:
        """
        Get all indicators of a specific type.
        
        Args:
            indicator_type: The indicator type to filter by
            
        Returns:
            List of indicators of the specified type
        """
        return [
            indicator for indicator in self.indicators.values()
            if indicator.indicator_type == indicator_type
        ]
    
    def get_indicators_by_priority(self, priority: IndicatorPriority) -> List[AmbientIndicator]:
        """
        Get all indicators with a specific priority.
        
        Args:
            priority: The priority level to filter by
            
        Returns:
            List of indicators with the specified priority
        """
        return [
            indicator for indicator in self.indicators.values()
            if indicator.priority == priority
        ]
    
    def dismiss_indicator(self, indicator_id: str) -> bool:
        """
        Dismiss an ambient indicator.
        
        Args:
            indicator_id: ID of the indicator to dismiss
            
        Returns:
            True if the indicator was dismissed, False otherwise
        """
        if indicator_id not in self.indicators:
            self.logger.warning(f"Cannot dismiss unknown indicator: {indicator_id}")
            return False
            
        indicator = self.indicators[indicator_id]
        indicator.dismiss()
        
        # Create and dispatch indicator event
        event = IndicatorEvent(
            event_type="dismissed",
            indicator_id=indicator_id,
            source="user"
        )
        self._dispatch_indicator_event(event)
        
        return True
    
    def register_group(self, group: IndicatorGroup) -> None:
        """
        Register a new indicator group.
        
        Args:
            group: The indicator group to register
        """
        if group.id in self.groups:
            self.logger.warning(f"Group with ID {group.id} already exists, overwriting")
            
        self.groups[group.id] = group
        
    def unregister_group(self, group_id: str) -> Optional[IndicatorGroup]:
        """
        Unregister an indicator group.
        
        Args:
            group_id: ID of the group to unregister
            
        Returns:
            The unregistered group, or None if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group with ID {group_id} not found")
            return None
            
        return self.groups.pop(group_id)
    
    def get_group(self, group_id: str) -> Optional[IndicatorGroup]:
        """
        Get an indicator group by ID.
        
        Args:
            group_id: ID of the group to get
            
        Returns:
            The indicator group, or None if not found
        """
        return self.groups.get(group_id)
    
    def get_all_groups(self) -> List[IndicatorGroup]:
        """
        Get all registered indicator groups.
        
        Returns:
            List of all indicator groups
        """
        return list(self.groups.values())
    
    def add_indicator_to_group(self, indicator_id: str, group_id: str) -> bool:
        """
        Add an indicator to a group.
        
        Args:
            indicator_id: ID of the indicator to add
            group_id: ID of the group to add the indicator to
            
        Returns:
            True if the indicator was added to the group, False otherwise
        """
        if indicator_id not in self.indicators:
            self.logger.warning(f"Indicator with ID {indicator_id} not found")
            return False
            
        if group_id not in self.groups:
            self.logger.warning(f"Group with ID {group_id} not found")
            return False
            
        indicator = self.indicators[indicator_id]
        self.groups[group_id].add_indicator(indicator)
        
        # Create and dispatch indicator event
        event = IndicatorEvent(
            event_type="added_to_group",
            indicator_id=indicator_id,
            group_id=group_id,
            source="system"
        )
        self._dispatch_indicator_event(event)
        
        return True
    
    def remove_indicator_from_group(self, indicator_id: str, group_id: str) -> bool:
        """
        Remove an indicator from a group.
        
        Args:
            indicator_id: ID of the indicator to remove
            group_id: ID of the group to remove the indicator from
            
        Returns:
            True if the indicator was removed from the group, False otherwise
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group with ID {group_id} not found")
            return False
            
        removed = self.groups[group_id].remove_indicator(indicator_id)
        if removed is None:
            self.logger.warning(f"Indicator with ID {indicator_id} not found in group {group_id}")
            return False
            
        # Create and dispatch indicator event
        event = IndicatorEvent(
            event_type="removed_from_group",
            indicator_id=indicator_id,
            group_id=group_id,
            source="system"
        )
        self._dispatch_indicator_event(event)
        
        return True
    
    def get_indicators_in_group(self, group_id: str) -> List[AmbientIndicator]:
        """
        Get all indicators in a specific group.
        
        Args:
            group_id: ID of the group to get indicators from
            
        Returns:
            List of indicators in the specified group
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group with ID {group_id} not found")
            return []
            
        return self.groups[group_id].get_all_indicators()
    
    def add_indicator_listener(self, listener: Callable[[IndicatorEvent], None]) -> None:
        """
        Add a listener for indicator events.
        
        Args:
            listener: Callback function that will be called with indicator events
        """
        self.indicator_listeners.append(listener)
        
    def remove_indicator_listener(self, listener: Callable[[IndicatorEvent], None]) -> None:
        """
        Remove a listener for indicator events.
        
        Args:
            listener: The listener to remove
        """
        if listener in self.indicator_listeners:
            self.indicator_listeners.remove(listener)
            
    def _dispatch_indicator_event(self, event: IndicatorEvent) -> None:
        """
        Dispatch an indicator event to all listeners.
        
        Args:
            event: The indicator event to dispatch
        """
        for listener in self.indicator_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error in indicator listener: {e}")
                
    def cleanup_expired_indicators(self) -> List[str]:
        """
        Clean up expired indicators.
        
        Returns:
            List of IDs of indicators that were removed
        """
        expired_ids = []
        
        for indicator_id, indicator in list(self.indicators.items()):
            if indicator.is_expired() and indicator.auto_dismiss:
                self.unregister_indicator(indicator_id)
                expired_ids.append(indicator_id)
                
        return expired_ids
    
    def get_highest_priority_indicators(self, limit: int = 5) -> List[AmbientIndicator]:
        """
        Get the highest priority indicators.
        
        Args:
            limit: Maximum number of indicators to return
            
        Returns:
            List of highest priority indicators
        """
        sorted_indicators = sorted(
            self.indicators.values(),
            key=lambda i: (i.priority.value, i.updated_at),
            reverse=True
        )
        
        return sorted_indicators[:limit]
    
    def create_system_status_indicator(self, 
                                      status: str, 
                                      value: float,
                                      title: Optional[str] = None,
                                      description: Optional[str] = None) -> AmbientIndicator:
        """
        Create and register a system status indicator.
        
        Args:
            status: Status string (e.g., "healthy", "warning", "error")
            value: Status value between 0.0 and 1.0
            title: Optional title for the indicator
            description: Optional description for the indicator
            
        Returns:
            The created indicator
        """
        # Determine properties based on status
        if status.lower() == "healthy":
            priority = IndicatorPriority.LOW
            visibility = IndicatorVisibility.SUBTLE
            animation = IndicatorAnimation.NONE
            color = "#4CAF50"  # Green
        elif status.lower() == "warning":
            priority = IndicatorPriority.MEDIUM
            visibility = IndicatorVisibility.NORMAL
            animation = IndicatorAnimation.PULSE
            color = "#FF9800"  # Orange
        elif status.lower() == "error":
            priority = IndicatorPriority.HIGH
            visibility = IndicatorVisibility.PROMINENT
            animation = IndicatorAnimation.PULSE
            color = "#F44336"  # Red
        elif status.lower() == "critical":
            priority = IndicatorPriority.CRITICAL
            visibility = IndicatorVisibility.URGENT
            animation = IndicatorAnimation.PULSE
            color = "#9C27B0"  # Purple
        else:
            priority = IndicatorPriority.MEDIUM
            visibility = IndicatorVisibility.NORMAL
            animation = IndicatorAnimation.NONE
            color = "#2196F3"  # Blue
            
        # Create indicator
        indicator = AmbientIndicator(
            indicator_type=IndicatorType.SYSTEM_STATUS,
            title=title or f"System Status: {status.capitalize()}",
            description=description or f"The system is currently in {status} state",
            value=value,
            min_value=0.0,
            max_value=1.0,
            priority=priority,
            visibility=visibility,
            animation=animation,
            color=color,
            icon="system_status",
            metadata={"status": status}
        )
        
        # Register indicator
        self.register_indicator(indicator, "system")
        
        return indicator
    
    def create_agent_activity_indicator(self,
                                       agent_id: str,
                                       agent_name: str,
                                       activity_type: str,
                                       confidence: float,
                                       title: Optional[str] = None,
                                       description: Optional[str] = None) -> AmbientIndicator:
        """
        Create and register an agent activity indicator.
        
        Args:
            agent_id: ID of the agent
            agent_name: Name of the agent
            activity_type: Type of activity (e.g., "thinking", "deciding", "executing")
            confidence: Confidence level between 0.0 and 1.0
            title: Optional title for the indicator
            description: Optional description for the indicator
            
        Returns:
            The created indicator
        """
        # Determine properties based on activity type and confidence
        if activity_type.lower() == "thinking":
            animation = IndicatorAnimation.BREATHE
            color = "#2196F3"  # Blue
        elif activity_type.lower() == "deciding":
            animation = IndicatorAnimation.PULSE
            color = "#9C27B0"  # Purple
        elif activity_type.lower() == "executing":
            animation = IndicatorAnimation.GLOW
            color = "#4CAF50"  # Green
        elif activity_type.lower() == "waiting":
            animation = IndicatorAnimation.FADE
            color = "#FF9800"  # Orange
        elif activity_type.lower() == "error":
            animation = IndicatorAnimation.PULSE
            color = "#F44336"  # Red
        else:
            animation = IndicatorAnimation.NONE
            color = "#2196F3"  # Blue
            
        # Determine priority based on confidence
        if confidence < 0.3:
            priority = IndicatorPriority.HIGH
        elif confidence < 0.7:
            priority = IndicatorPriority.MEDIUM
        else:
            priority = IndicatorPriority.LOW
            
        # Create indicator
        indicator = AmbientIndicator(
            indicator_type=IndicatorType.AGENT_ACTIVITY,
            title=title or f"Agent {agent_name}: {activity_type.capitalize()}",
            description=description or f"Agent {agent_name} is {activity_type}",
            value=confidence,
            min_value=0.0,
            max_value=1.0,
            priority=priority,
            visibility=IndicatorVisibility.NORMAL,
            animation=animation,
            color=color,
            icon="agent_activity",
            metadata={
                "agent_id": agent_id,
                "agent_name": agent_name,
                "activity_type": activity_type
            }
        )
        
        # Register indicator
        self.register_indicator(indicator, "agents")
        
        return indicator
    
    def create_trust_level_indicator(self,
                                    entity_id: str,
                                    entity_name: str,
                                    trust_score: float,
                                    title: Optional[str] = None,
                                    description: Optional[str] = None) -> AmbientIndicator:
        """
        Create and register a trust level indicator.
        
        Args:
            entity_id: ID of the entity (agent, workflow, etc.)
            entity_name: Name of the entity
            trust_score: Trust score between 0.0 and 1.0
            title: Optional title for the indicator
            description: Optional description for the indicator
            
        Returns:
            The created indicator
        """
        # Determine properties based on trust score
        if trust_score < 0.3:
            priority = IndicatorPriority.HIGH
            visibility = IndicatorVisibility.PROMINENT
            animation = IndicatorAnimation.PULSE
            color = "#F44336"  # Red
        elif trust_score < 0.7:
            priority = IndicatorPriority.MEDIUM
            visibility = IndicatorVisibility.NORMAL
            animation = IndicatorAnimation.NONE
            color = "#FF9800"  # Orange
        else:
            priority = IndicatorPriority.LOW
            visibility = IndicatorVisibility.SUBTLE
            animation = IndicatorAnimation.NONE
            color = "#4CAF50"  # Green
            
        # Create indicator
        indicator = AmbientIndicator(
            indicator_type=IndicatorType.TRUST_LEVEL,
            title=title or f"Trust Level: {entity_name}",
            description=description or f"Trust score for {entity_name}: {trust_score:.2f}",
            value=trust_score,
            min_value=0.0,
            max_value=1.0,
            priority=priority,
            visibility=visibility,
            animation=animation,
            color=color,
            icon="trust_level",
            metadata={
                "entity_id": entity_id,
                "entity_name": entity_name
            }
        )
        
        # Register indicator
        self.register_indicator(indicator, "trust")
        
        return indicator
    
    def create_workflow_progress_indicator(self,
                                         workflow_id: str,
                                         workflow_name: str,
                                         progress: float,
                                         status: str,
                                         title: Optional[str] = None,
                                         description: Optional[str] = None) -> AmbientIndicator:
        """
        Create and register a workflow progress indicator.
        
        Args:
            workflow_id: ID of the workflow
            workflow_name: Name of the workflow
            progress: Progress value between 0.0 and 1.0
            status: Status string (e.g., "running", "paused", "completed", "failed")
            title: Optional title for the indicator
            description: Optional description for the indicator
            
        Returns:
            The created indicator
        """
        # Determine properties based on status
        if status.lower() == "running":
            priority = IndicatorPriority.MEDIUM
            visibility = IndicatorVisibility.NORMAL
            animation = IndicatorAnimation.BREATHE
            color = "#2196F3"  # Blue
        elif status.lower() == "paused":
            priority = IndicatorPriority.MEDIUM
            visibility = IndicatorVisibility.NORMAL
            animation = IndicatorAnimation.NONE
            color = "#FF9800"  # Orange
        elif status.lower() == "completed":
            priority = IndicatorPriority.LOW
            visibility = IndicatorVisibility.SUBTLE
            animation = IndicatorAnimation.NONE
            color = "#4CAF50"  # Green
        elif status.lower() == "failed":
            priority = IndicatorPriority.HIGH
            visibility = IndicatorVisibility.PROMINENT
            animation = IndicatorAnimation.PULSE
            color = "#F44336"  # Red
        else:
            priority = IndicatorPriority.MEDIUM
            visibility = IndicatorVisibility.NORMAL
            animation = IndicatorAnimation.NONE
            color = "#2196F3"  # Blue
            
        # Create indicator
        indicator = AmbientIndicator(
            indicator_type=IndicatorType.WORKFLOW_PROGRESS,
            title=title or f"Workflow: {workflow_name}",
            description=description or f"Workflow {workflow_name} is {status} ({progress:.0%} complete)",
            value=progress,
            min_value=0.0,
            max_value=1.0,
            priority=priority,
            visibility=visibility,
            animation=animation,
            color=color,
            icon="workflow_progress",
            metadata={
                "workflow_id": workflow_id,
                "workflow_name": workflow_name,
                "status": status
            }
        )
        
        # Register indicator
        self.register_indicator(indicator, "workflows")
        
        return indicator
    
    def create_alert_indicator(self,
                              alert_type: str,
                              message: str,
                              severity: str,
                              title: Optional[str] = None,
                              description: Optional[str] = None,
                              auto_dismiss: bool = True,
                              duration: float = 10.0) -> AmbientIndicator:
        """
        Create and register an alert indicator.
        
        Args:
            alert_type: Type of alert
            message: Alert message
            severity: Severity level (e.g., "info", "warning", "error", "critical")
            title: Optional title for the indicator
            description: Optional description for the indicator
            auto_dismiss: Whether the alert should auto-dismiss
            duration: Duration in seconds before auto-dismissal
            
        Returns:
            The created indicator
        """
        # Determine properties based on severity
        if severity.lower() == "info":
            priority = IndicatorPriority.LOW
            visibility = IndicatorVisibility.NORMAL
            animation = IndicatorAnimation.FADE
            color = "#2196F3"  # Blue
            sound = "info_alert"
        elif severity.lower() == "warning":
            priority = IndicatorPriority.MEDIUM
            visibility = IndicatorVisibility.PROMINENT
            animation = IndicatorAnimation.PULSE
            color = "#FF9800"  # Orange
            sound = "warning_alert"
        elif severity.lower() == "error":
            priority = IndicatorPriority.HIGH
            visibility = IndicatorVisibility.URGENT
            animation = IndicatorAnimation.PULSE
            color = "#F44336"  # Red
            sound = "error_alert"
        elif severity.lower() == "critical":
            priority = IndicatorPriority.CRITICAL
            visibility = IndicatorVisibility.URGENT
            animation = IndicatorAnimation.PULSE
            color = "#9C27B0"  # Purple
            sound = "critical_alert"
            haptic = "critical_alert"
        else:
            priority = IndicatorPriority.MEDIUM
            visibility = IndicatorVisibility.NORMAL
            animation = IndicatorAnimation.NONE
            color = "#2196F3"  # Blue
            sound = None
            haptic = None
            
        # Create indicator
        indicator = AmbientIndicator(
            indicator_type=IndicatorType.ALERT,
            title=title or f"{severity.capitalize()} Alert",
            description=description or message,
            value=None,
            priority=priority,
            visibility=visibility,
            animation=animation,
            color=color,
            icon=f"{severity.lower()}_alert",
            sound=sound,
            haptic=haptic,
            duration=duration,
            auto_dismiss=auto_dismiss,
            metadata={
                "alert_type": alert_type,
                "severity": severity,
                "message": message
            }
        )
        
        # Register indicator
        self.register_indicator(indicator, "alerts")
        
        return indicator
    
    def get_indicator_state(self) -> Dict[str, Any]:
        """
        Get the current state of all indicators.
        
        Returns:
            Dictionary representation of the current indicator state
        """
        return {
            "indicators": {
                indicator_id: indicator.to_dict()
                for indicator_id, indicator in self.indicators.items()
            },
            "groups": {
                group_id: group.to_dict()
                for group_id, group in self.groups.items()
            }
        }
    
    def load_indicator_state(self, state: Dict[str, Any]) -> None:
        """
        Load indicator state from a dictionary.
        
        Args:
            state: Dictionary representation of indicator state
        """
        # Clear existing state
        self.indicators = {}
        self.groups = {}
        
        # Load groups first
        for group_id, group_data in state.get("groups", {}).items():
            group = IndicatorGroup.from_dict(group_data)
            self.groups[group_id] = group
            
        # Load indicators
        for indicator_id, indicator_data in state.get("indicators", {}).items():
            indicator = AmbientIndicator.from_dict(indicator_data)
            self.indicators[indicator_id] = indicator
