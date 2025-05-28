"""
Shell Event Handler for Universal Skin Shell in the Industriverse UI/UX Layer.

This module handles events within the Universal Skin Shell, including user interactions,
system events, and cross-component communication. It implements the Capsule Ritual Engine
to provide emotionally resonant transitions and interactions.

Author: Manus
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Set, Union
from enum import Enum
import uuid
import json

class EventCategory(Enum):
    """Enumeration of event categories."""
    USER_INTERACTION = "user_interaction"
    SYSTEM = "system"
    NAVIGATION = "navigation"
    STATE_CHANGE = "state_change"
    NOTIFICATION = "notification"
    CAPSULE = "capsule"
    RITUAL = "ritual"  # For emotionally resonant interactions
    SWARM = "swarm"    # For swarm-related events
    AVATAR = "avatar"  # For avatar-related events
    CUSTOM = "custom"

class EventPriority(Enum):
    """Enumeration of event priorities."""
    LOW = 0
    MEDIUM = 1
    HIGH = 2
    CRITICAL = 3

class EventSource(Enum):
    """Enumeration of event sources."""
    USER = "user"
    SYSTEM = "system"
    CAPSULE = "capsule"
    AGENT = "agent"
    AVATAR = "avatar"
    SWARM = "swarm"
    EXTERNAL = "external"
    CUSTOM = "custom"

class ShellEvent:
    """Represents an event in the Universal Skin Shell."""
    
    def __init__(self,
                 event_type: str,
                 category: EventCategory,
                 source: EventSource,
                 event_id: Optional[str] = None,
                 priority: EventPriority = EventPriority.MEDIUM,
                 data: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 bubbles: bool = True,
                 cancelable: bool = True):
        """
        Initialize a shell event.
        
        Args:
            event_type: Type of event (e.g., "click", "hover", "capsule_created")
            category: Category of the event
            source: Source of the event
            event_id: Unique identifier for this event (generated if not provided)
            priority: Priority level of this event
            data: Event-specific data
            metadata: Additional metadata for this event
            bubbles: Whether this event bubbles up through the component hierarchy
            cancelable: Whether this event can be cancelled
        """
        self.event_type = event_type
        self.category = category
        self.source = source
        self.event_id = event_id or str(uuid.uuid4())
        self.priority = priority
        self.data = data or {}
        self.metadata = metadata or {}
        self.bubbles = bubbles
        self.cancelable = cancelable
        self.timestamp = time.time()
        self.is_cancelled = False
        self.propagation_stopped = False
        self.current_target = None
        self.original_target = self.data.get("target")
        self.processed_by = set()
        
    def cancel(self) -> bool:
        """
        Cancel this event.
        
        Returns:
            True if the event was cancelled, False if not cancelable
        """
        if not self.cancelable:
            return False
            
        self.is_cancelled = True
        return True
        
    def stop_propagation(self) -> None:
        """Stop propagation of this event."""
        self.propagation_stopped = True
        
    def mark_processed_by(self, handler_id: str) -> None:
        """
        Mark this event as processed by a handler.
        
        Args:
            handler_id: ID of the handler that processed this event
        """
        self.processed_by.add(handler_id)
        
    def was_processed_by(self, handler_id: str) -> bool:
        """
        Check if this event was processed by a handler.
        
        Args:
            handler_id: ID of the handler to check
            
        Returns:
            True if the event was processed by the handler, False otherwise
        """
        return handler_id in self.processed_by
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this event to a dictionary representation."""
        return {
            "event_type": self.event_type,
            "category": self.category.value,
            "source": self.source.value,
            "event_id": self.event_id,
            "priority": self.priority.value,
            "data": self.data,
            "metadata": self.metadata,
            "bubbles": self.bubbles,
            "cancelable": self.cancelable,
            "timestamp": self.timestamp,
            "is_cancelled": self.is_cancelled,
            "propagation_stopped": self.propagation_stopped,
            "current_target": self.current_target,
            "original_target": self.original_target,
            "processed_by": list(self.processed_by)
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShellEvent':
        """Create a shell event from a dictionary representation."""
        event = cls(
            event_type=data["event_type"],
            category=EventCategory(data["category"]),
            source=EventSource(data["source"]),
            event_id=data.get("event_id"),
            priority=EventPriority(data["priority"]) if "priority" in data else EventPriority.MEDIUM,
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            bubbles=data.get("bubbles", True),
            cancelable=data.get("cancelable", True)
        )
        
        event.timestamp = data.get("timestamp", time.time())
        event.is_cancelled = data.get("is_cancelled", False)
        event.propagation_stopped = data.get("propagation_stopped", False)
        event.current_target = data.get("current_target")
        event.original_target = data.get("original_target")
        event.processed_by = set(data.get("processed_by", []))
        
        return event
        
    @classmethod
    def create_ritual_event(cls,
                          ritual_type: str,
                          emotion: str,
                          intensity: float,
                          source_id: str,
                          target_id: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> 'ShellEvent':
        """
        Create a ritual event with emotional resonance.
        
        Args:
            ritual_type: Type of ritual (e.g., "override", "approval", "completion")
            emotion: Emotional tone of the ritual (e.g., "calm", "urgent", "celebratory")
            intensity: Intensity of the emotional effect (0.0 to 1.0)
            source_id: ID of the source component/entity
            target_id: Optional ID of the target component/entity
            metadata: Additional metadata for this event
            
        Returns:
            A ritual event
        """
        # Determine color palette based on emotion
        color_palette = _get_emotion_color_palette(emotion)
        
        # Determine sound and haptic effects based on ritual type and emotion
        sound_effect = f"ritual_{emotion.lower()}_{ritual_type.lower()}"
        haptic_pattern = f"ritual_{emotion.lower()}_{ritual_type.lower()}"
        
        # Create event data
        data = {
            "ritual_type": ritual_type,
            "emotion": emotion,
            "intensity": intensity,
            "source_id": source_id,
            "target_id": target_id,
            "color_palette": color_palette,
            "sound_effect": sound_effect,
            "haptic_pattern": haptic_pattern,
            "particle_count": int(100 + 200 * intensity),
            "duration": 0.8 + (intensity * 0.4)  # 0.8 to 1.2 seconds based on intensity
        }
        
        return cls(
            event_type=f"ritual_{ritual_type}",
            category=EventCategory.RITUAL,
            source=EventSource.CAPSULE,
            priority=EventPriority.MEDIUM,
            data=data,
            metadata=metadata
        )
        
    @classmethod
    def create_swarm_event(cls,
                         swarm_event_type: str,
                         swarm_id: str,
                         agent_ids: List[str],
                         swarm_state: str,
                         metadata: Optional[Dict[str, Any]] = None) -> 'ShellEvent':
        """
        Create a swarm-related event.
        
        Args:
            swarm_event_type: Type of swarm event (e.g., "formation", "dispersion", "reconfiguration")
            swarm_id: ID of the swarm
            agent_ids: List of agent IDs in the swarm
            swarm_state: State of the swarm (e.g., "forming", "active", "dispersing")
            metadata: Additional metadata for this event
            
        Returns:
            A swarm event
        """
        # Create event data
        data = {
            "swarm_id": swarm_id,
            "agent_ids": agent_ids,
            "swarm_state": swarm_state,
            "agent_count": len(agent_ids)
        }
        
        return cls(
            event_type=f"swarm_{swarm_event_type}",
            category=EventCategory.SWARM,
            source=EventSource.SWARM,
            priority=EventPriority.MEDIUM,
            data=data,
            metadata=metadata
        )
        
    @classmethod
    def create_avatar_event(cls,
                          avatar_event_type: str,
                          avatar_id: str,
                          avatar_state: str,
                          expression: Optional[str] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> 'ShellEvent':
        """
        Create an avatar-related event.
        
        Args:
            avatar_event_type: Type of avatar event (e.g., "appearance", "expression_change", "interaction")
            avatar_id: ID of the avatar
            avatar_state: State of the avatar (e.g., "idle", "speaking", "thinking")
            expression: Optional expression of the avatar (e.g., "happy", "concerned", "neutral")
            metadata: Additional metadata for this event
            
        Returns:
            An avatar event
        """
        # Create event data
        data = {
            "avatar_id": avatar_id,
            "avatar_state": avatar_state,
            "expression": expression
        }
        
        return cls(
            event_type=f"avatar_{avatar_event_type}",
            category=EventCategory.AVATAR,
            source=EventSource.AVATAR,
            priority=EventPriority.MEDIUM,
            data=data,
            metadata=metadata
        )

class EventHandler:
    """Represents an event handler in the Shell Event Handler."""
    
    def __init__(self,
                 handler_id: str,
                 event_types: Union[str, List[str]],
                 callback: Callable[[ShellEvent], None],
                 priority: int = 0,
                 filter_func: Optional[Callable[[ShellEvent], bool]] = None):
        """
        Initialize an event handler.
        
        Args:
            handler_id: Unique identifier for this handler
            event_types: Event type(s) to handle
            callback: Callback function to call when an event is handled
            priority: Priority of this handler (higher values are called first)
            filter_func: Optional function to filter events
        """
        self.handler_id = handler_id
        self.event_types = [event_types] if isinstance(event_types, str) else event_types
        self.callback = callback
        self.priority = priority
        self.filter_func = filter_func
        
    def matches_event(self, event: ShellEvent) -> bool:
        """
        Check if this handler matches an event.
        
        Args:
            event: The event to check
            
        Returns:
            True if the handler matches the event, False otherwise
        """
        # Check event type
        if "*" not in self.event_types and event.event_type not in self.event_types:
            return False
            
        # Apply filter function if provided
        if self.filter_func is not None:
            return self.filter_func(event)
            
        return True
        
    def handle_event(self, event: ShellEvent) -> None:
        """
        Handle an event.
        
        Args:
            event: The event to handle
        """
        self.callback(event)
        event.mark_processed_by(self.handler_id)

class CapsuleRitualEngine:
    """
    Implements the Capsule Ritual Engine for emotionally resonant transitions and interactions.
    
    This class provides:
    - Ritual event creation and handling
    - Emotional resonance mapping
    - Visual and audio effects for rituals
    - Ritual templates for common interactions
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Capsule Ritual Engine.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.ritual_templates: Dict[str, Dict[str, Any]] = {}
        self.active_rituals: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger(__name__)
        
        # Initialize default ritual templates
        self._initialize_default_templates()
        
    def _initialize_default_templates(self) -> None:
        """Initialize default ritual templates."""
        # Override ritual (when human overrides an agent decision)
        self.ritual_templates["override"] = {
            "emotion": "focused",
            "intensity": 0.7,
            "duration": 1.0,
            "particle_count": 150,
            "color_palette": ["#B388FF", "#7C4DFF", "#651FFF", "#6200EA", "#4527A0"],
            "sound_effect": "ritual_override",
            "haptic_pattern": "ritual_override",
            "animation": "pulse_wave"
        }
        
        # Approval ritual (when human approves an agent decision)
        self.ritual_templates["approval"] = {
            "emotion": "celebratory",
            "intensity": 0.6,
            "duration": 0.8,
            "particle_count": 120,
            "color_palette": ["#FFFF8D", "#FFFF00", "#FFEA00", "#FFD600", "#FFC107"],
            "sound_effect": "ritual_approval",
            "haptic_pattern": "ritual_approval",
            "animation": "sparkle"
        }
        
        # Completion ritual (when a task or workflow completes)
        self.ritual_templates["completion"] = {
            "emotion": "productive",
            "intensity": 0.8,
            "duration": 1.2,
            "particle_count": 200,
            "color_palette": ["#A5D6A7", "#66BB6A", "#4CAF50", "#43A047", "#2E7D32"],
            "sound_effect": "ritual_completion",
            "haptic_pattern": "ritual_completion",
            "animation": "confetti"
        }
        
        # Alert ritual (for important notifications)
        self.ritual_templates["alert"] = {
            "emotion": "urgent",
            "intensity": 0.9,
            "duration": 0.7,
            "particle_count": 100,
            "color_palette": ["#FF8A80", "#FF5252", "#FF1744", "#D50000", "#B71C1C"],
            "sound_effect": "ritual_alert",
            "haptic_pattern": "ritual_alert",
            "animation": "pulse"
        }
        
        # Connection ritual (when connecting capsules or agents)
        self.ritual_templates["connection"] = {
            "emotion": "calm",
            "intensity": 0.5,
            "duration": 1.0,
            "particle_count": 80,
            "color_palette": ["#4FC3F7", "#29B6F6", "#03A9F4", "#039BE5", "#0288D1"],
            "sound_effect": "ritual_connection",
            "haptic_pattern": "ritual_connection",
            "animation": "flow"
        }
        
    def register_ritual_template(self, 
                               name: str, 
                               template: Dict[str, Any]) -> None:
        """
        Register a ritual template.
        
        Args:
            name: Name of the template
            template: Template definition
        """
        self.ritual_templates[name] = template
        
    def get_ritual_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a ritual template by name.
        
        Args:
            name: Name of the template
            
        Returns:
            The ritual template, or None if not found
        """
        return self.ritual_templates.get(name)
    
    def create_ritual(self,
                    ritual_type: str,
                    source_id: str,
                    target_id: Optional[str] = None,
                    emotion: Optional[str] = None,
                    intensity: Optional[float] = None,
                    custom_params: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a ritual.
        
        Args:
            ritual_type: Type of ritual (e.g., "override", "approval", "completion")
            source_id: ID of the source component/entity
            target_id: Optional ID of the target component/entity
            emotion: Optional emotional tone to override template
            intensity: Optional intensity to override template
            custom_params: Additional parameters for the ritual
            
        Returns:
            ID of the created ritual
        """
        # Get template for this ritual type
        template = self.get_ritual_template(ritual_type)
        if template is None:
            self.logger.warning(f"Ritual template '{ritual_type}' not found, using default")
            template = {
                "emotion": "neutral",
                "intensity": 0.5,
                "duration": 0.8,
                "particle_count": 100,
                "color_palette": ["#90CAF9", "#64B5F6", "#42A5F5", "#2196F3", "#1E88E5"],
                "sound_effect": "ritual_default",
                "haptic_pattern": "ritual_default",
                "animation": "fade"
            }
            
        # Create ritual parameters
        ritual_params = template.copy()
        
        # Override with provided parameters
        if emotion is not None:
            ritual_params["emotion"] = emotion
            ritual_params["color_palette"] = _get_emotion_color_palette(emotion)
            
        if intensity is not None:
            ritual_params["intensity"] = intensity
            ritual_params["particle_count"] = int(100 + 200 * intensity)
            
        if custom_params is not None:
            ritual_params.update(custom_params)
            
        # Create ritual ID
        ritual_id = str(uuid.uuid4())
        
        # Store active ritual
        self.active_rituals[ritual_id] = {
            "ritual_id": ritual_id,
            "ritual_type": ritual_type,
            "source_id": source_id,
            "target_id": target_id,
            "params": ritual_params,
            "start_time": time.time(),
            "end_time": time.time() + ritual_params["duration"],
            "is_complete": False
        }
        
        return ritual_id
    
    def update_rituals(self, current_time: Optional[float] = None) -> List[str]:
        """
        Update all active rituals.
        
        Args:
            current_time: Current time (defaults to time.time())
            
        Returns:
            List of IDs of completed rituals
        """
        if current_time is None:
            current_time = time.time()
            
        completed_rituals = []
        
        for ritual_id, ritual in list(self.active_rituals.items()):
            if current_time >= ritual["end_time"]:
                ritual["is_complete"] = True
                completed_rituals.append(ritual_id)
                
        # Remove completed rituals
        for ritual_id in completed_rituals:
            self.active_rituals.pop(ritual_id)
            
        return completed_rituals
    
    def get_ritual(self, ritual_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an active ritual by ID.
        
        Args:
            ritual_id: ID of the ritual to get
            
        Returns:
            The ritual, or None if not found
        """
        return self.active_rituals.get(ritual_id)
    
    def get_all_active_rituals(self) -> List[Dict[str, Any]]:
        """
        Get all active rituals.
        
        Returns:
            List of all active rituals
        """
        return list(self.active_rituals.values())
    
    def get_ritual_css(self, ritual_id: str) -> Optional[str]:
        """
        Get CSS representation of a ritual for web rendering.
        
        Args:
            ritual_id: ID of the ritual
            
        Returns:
            CSS string for the ritual, or None if not found
        """
        ritual = self.get_ritual(ritual_id)
        if not ritual:
            return None
            
        params = ritual["params"]
        animation = params.get("animation", "fade")
        duration = params.get("duration", 0.8)
        
        css = []
        css.append(f"animation: {animation} {duration}s ease-in-out;")
        
        if animation == "pulse":
            css.append("@keyframes pulse {")
            css.append("  0% { transform: scale(1); opacity: 0.7; }")
            css.append("  50% { transform: scale(1.05); opacity: 1; }")
            css.append("  100% { transform: scale(1); opacity: 0.7; }")
            css.append("}")
        elif animation == "sparkle":
            css.append("@keyframes sparkle {")
            css.append("  0% { filter: brightness(1) contrast(1); }")
            css.append("  50% { filter: brightness(1.2) contrast(1.1); }")
            css.append("  100% { filter: brightness(1) contrast(1); }")
            css.append("}")
        elif animation == "confetti":
            css.append("@keyframes confetti {")
            css.append("  0% { background-position: 0% 0%; }")
            css.append("  100% { background-position: 100% 100%; }")
            css.append("}")
        elif animation == "flow":
            css.append("@keyframes flow {")
            css.append("  0% { background-position: 0% 50%; }")
            css.append("  50% { background-position: 100% 50%; }")
            css.append("  100% { background-position: 0% 50%; }")
            css.append("}")
        elif animation == "pulse_wave":
            css.append("@keyframes pulse_wave {")
            css.append("  0% { box-shadow: 0 0 0 0 rgba(100, 100, 255, 0.7); }")
            css.append("  70% { box-shadow: 0 0 0 10px rgba(100, 100, 255, 0); }")
            css.append("  100% { box-shadow: 0 0 0 0 rgba(100, 100, 255, 0); }")
            css.append("}")
            
        return "\n".join(css)
    
    def get_ritual_animation_data(self, ritual_id: str) -> Optional[Dict[str, Any]]:
        """
        Get animation data for a ritual.
        
        Args:
            ritual_id: ID of the ritual
            
        Returns:
            Animation data for the ritual, or None if not found
        """
        ritual = self.get_ritual(ritual_id)
        if not ritual:
            return None
            
        params = ritual["params"]
        
        return {
            "animation": params.get("animation", "fade"),
            "duration": params.get("duration", 0.8),
            "particle_count": params.get("particle_count", 100),
            "color_palette": params.get("color_palette", ["#2196F3"]),
            "intensity": params.get("intensity", 0.5),
            "emotion": params.get("emotion", "neutral")
        }

class ShellEventHandler:
    """
    Handles events within the Universal Skin Shell.
    
    This class provides:
    - Event registration and dispatching
    - Event bubbling and propagation
    - Event filtering and prioritization
    - Component-specific event handling
    - Integration with the Capsule Ritual Engine
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Shell Event Handler.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.handlers: Dict[str, EventHandler] = {}
        self.component_hierarchy: Dict[str, str] = {}  # component_id -> parent_id
        self.event_history: List[ShellEvent] = []
        self.history_limit = self.config.get("history_limit", 100)
        self.logger = logging.getLogger(__name__)
        self.ritual_engine = CapsuleRitualEngine(self.config.get("ritual_engine"))
        
    def register_handler(self,
                        handler_id: str,
                        event_types: Union[str, List[str]],
                        callback: Callable[[ShellEvent], None],
                        priority: int = 0,
                        filter_func: Optional[Callable[[ShellEvent], bool]] = None) -> None:
        """
        Register an event handler.
        
        Args:
            handler_id: Unique identifier for this handler
            event_types: Event type(s) to handle
            callback: Callback function to call when an event is handled
            priority: Priority of this handler (higher values are called first)
            filter_func: Optional function to filter events
        """
        if handler_id in self.handlers:
            self.logger.warning(f"Handler with ID {handler_id} already exists, overwriting")
            
        self.handlers[handler_id] = EventHandler(
            handler_id=handler_id,
            event_types=event_types,
            callback=callback,
            priority=priority,
            filter_func=filter_func
        )
        
    def unregister_handler(self, handler_id: str) -> bool:
        """
        Unregister an event handler.
        
        Args:
            handler_id: ID of the handler to unregister
            
        Returns:
            True if the handler was unregistered, False if not found
        """
        if handler_id not in self.handlers:
            return False
            
        del self.handlers[handler_id]
        return True
    
    def register_component(self, 
                         component_id: str, 
                         parent_id: Optional[str] = None) -> None:
        """
        Register a component in the hierarchy.
        
        Args:
            component_id: ID of the component
            parent_id: Optional ID of the parent component
        """
        self.component_hierarchy[component_id] = parent_id
        
    def unregister_component(self, component_id: str) -> bool:
        """
        Unregister a component from the hierarchy.
        
        Args:
            component_id: ID of the component to unregister
            
        Returns:
            True if the component was unregistered, False if not found
        """
        if component_id not in self.component_hierarchy:
            return False
            
        del self.component_hierarchy[component_id]
        return True
    
    def dispatch_event(self, event: ShellEvent) -> bool:
        """
        Dispatch an event to all matching handlers.
        
        Args:
            event: The event to dispatch
            
        Returns:
            True if the event was handled by at least one handler, False otherwise
        """
        # Add to history
        self._add_to_history(event)
        
        # Get all handlers that match this event, sorted by priority
        matching_handlers = [
            handler for handler in self.handlers.values()
            if handler.matches_event(event)
        ]
        matching_handlers.sort(key=lambda h: h.priority, reverse=True)
        
        # Handle the event
        handled = False
        
        for handler in matching_handlers:
            if event.is_cancelled:
                break
                
            try:
                handler.handle_event(event)
                handled = True
            except Exception as e:
                self.logger.error(f"Error in event handler {handler.handler_id}: {e}")
                
        # If the event bubbles and has a target, bubble up through the component hierarchy
        if (event.bubbles and 
            not event.propagation_stopped and 
            event.data.get("target") in self.component_hierarchy):
            
            target_id = event.data["target"]
            parent_id = self.component_hierarchy.get(target_id)
            
            if parent_id is not None:
                # Create a new event for the parent
                parent_event = ShellEvent(
                    event_type=event.event_type,
                    category=event.category,
                    source=event.source,
                    event_id=event.event_id,
                    priority=event.priority,
                    data={**event.data, "target": parent_id},
                    metadata=event.metadata,
                    bubbles=event.bubbles,
                    cancelable=event.cancelable
                )
                
                # Copy processed_by set
                parent_event.processed_by = event.processed_by.copy()
                
                # Dispatch to parent
                parent_handled = self.dispatch_event(parent_event)
                handled = handled or parent_handled
                
        return handled
    
    def create_event(self,
                    event_type: str,
                    category: EventCategory,
                    source: EventSource,
                    data: Optional[Dict[str, Any]] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    priority: EventPriority = EventPriority.MEDIUM,
                    bubbles: bool = True,
                    cancelable: bool = True) -> ShellEvent:
        """
        Create a new event.
        
        Args:
            event_type: Type of event
            category: Category of the event
            source: Source of the event
            data: Event-specific data
            metadata: Additional metadata for this event
            priority: Priority level of this event
            bubbles: Whether this event bubbles up through the component hierarchy
            cancelable: Whether this event can be cancelled
            
        Returns:
            The created event
        """
        return ShellEvent(
            event_type=event_type,
            category=category,
            source=source,
            priority=priority,
            data=data,
            metadata=metadata,
            bubbles=bubbles,
            cancelable=cancelable
        )
    
    def dispatch_user_interaction(self,
                                interaction_type: str,
                                target_id: str,
                                data: Optional[Dict[str, Any]] = None,
                                metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Dispatch a user interaction event.
        
        Args:
            interaction_type: Type of interaction (e.g., "click", "hover", "drag")
            target_id: ID of the target component
            data: Interaction-specific data
            metadata: Additional metadata for this event
            
        Returns:
            True if the event was handled, False otherwise
        """
        event_data = data or {}
        event_data["target"] = target_id
        
        event = self.create_event(
            event_type=interaction_type,
            category=EventCategory.USER_INTERACTION,
            source=EventSource.USER,
            data=event_data,
            metadata=metadata
        )
        
        return self.dispatch_event(event)
    
    def dispatch_system_event(self,
                            event_type: str,
                            data: Optional[Dict[str, Any]] = None,
                            metadata: Optional[Dict[str, Any]] = None,
                            priority: EventPriority = EventPriority.MEDIUM) -> bool:
        """
        Dispatch a system event.
        
        Args:
            event_type: Type of system event
            data: Event-specific data
            metadata: Additional metadata for this event
            priority: Priority level of this event
            
        Returns:
            True if the event was handled, False otherwise
        """
        event = self.create_event(
            event_type=event_type,
            category=EventCategory.SYSTEM,
            source=EventSource.SYSTEM,
            data=data,
            metadata=metadata,
            priority=priority,
            bubbles=False
        )
        
        return self.dispatch_event(event)
    
    def dispatch_capsule_event(self,
                             event_type: str,
                             capsule_id: str,
                             data: Optional[Dict[str, Any]] = None,
                             metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Dispatch a capsule-related event.
        
        Args:
            event_type: Type of capsule event
            capsule_id: ID of the capsule
            data: Event-specific data
            metadata: Additional metadata for this event
            
        Returns:
            True if the event was handled, False otherwise
        """
        event_data = data or {}
        event_data["capsule_id"] = capsule_id
        event_data["target"] = capsule_id
        
        event = self.create_event(
            event_type=event_type,
            category=EventCategory.CAPSULE,
            source=EventSource.CAPSULE,
            data=event_data,
            metadata=metadata
        )
        
        return self.dispatch_event(event)
    
    def dispatch_ritual_event(self,
                            ritual_type: str,
                            source_id: str,
                            target_id: Optional[str] = None,
                            emotion: Optional[str] = None,
                            intensity: Optional[float] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create and dispatch a ritual event.
        
        Args:
            ritual_type: Type of ritual
            source_id: ID of the source component/entity
            target_id: Optional ID of the target component/entity
            emotion: Optional emotional tone to override template
            intensity: Optional intensity to override template
            metadata: Additional metadata for this event
            
        Returns:
            ID of the created ritual
        """
        # Create ritual using the Ritual Engine
        ritual_id = self.ritual_engine.create_ritual(
            ritual_type=ritual_type,
            source_id=source_id,
            target_id=target_id,
            emotion=emotion,
            intensity=intensity
        )
        
        # Get ritual parameters
        ritual = self.ritual_engine.get_ritual(ritual_id)
        
        # Create event data
        event_data = {
            "ritual_id": ritual_id,
            "ritual_type": ritual_type,
            "source_id": source_id,
            "target_id": target_id,
            "target": source_id,  # For event bubbling
            "params": ritual["params"]
        }
        
        # Create and dispatch event
        event = self.create_event(
            event_type=f"ritual_{ritual_type}",
            category=EventCategory.RITUAL,
            source=EventSource.CAPSULE,
            data=event_data,
            metadata=metadata
        )
        
        self.dispatch_event(event)
        
        return ritual_id
    
    def dispatch_swarm_event(self,
                           swarm_event_type: str,
                           swarm_id: str,
                           agent_ids: List[str],
                           swarm_state: str,
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Dispatch a swarm-related event.
        
        Args:
            swarm_event_type: Type of swarm event
            swarm_id: ID of the swarm
            agent_ids: List of agent IDs in the swarm
            swarm_state: State of the swarm
            metadata: Additional metadata for this event
            
        Returns:
            True if the event was handled, False otherwise
        """
        event = ShellEvent.create_swarm_event(
            swarm_event_type=swarm_event_type,
            swarm_id=swarm_id,
            agent_ids=agent_ids,
            swarm_state=swarm_state,
            metadata=metadata
        )
        
        return self.dispatch_event(event)
    
    def dispatch_avatar_event(self,
                            avatar_event_type: str,
                            avatar_id: str,
                            avatar_state: str,
                            expression: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Dispatch an avatar-related event.
        
        Args:
            avatar_event_type: Type of avatar event
            avatar_id: ID of the avatar
            avatar_state: State of the avatar
            expression: Optional expression of the avatar
            metadata: Additional metadata for this event
            
        Returns:
            True if the event was handled, False otherwise
        """
        event = ShellEvent.create_avatar_event(
            avatar_event_type=avatar_event_type,
            avatar_id=avatar_id,
            avatar_state=avatar_state,
            expression=expression,
            metadata=metadata
        )
        
        return self.dispatch_event(event)
    
    def _add_to_history(self, event: ShellEvent) -> None:
        """
        Add an event to history.
        
        Args:
            event: The event to add
        """
        self.event_history.append(event)
        
        # Trim history if it exceeds the limit
        if len(self.event_history) > self.history_limit:
            self.event_history = self.event_history[-self.history_limit:]
            
    def get_history(self, 
                   limit: Optional[int] = None, 
                   event_type: Optional[str] = None,
                   category: Optional[EventCategory] = None) -> List[ShellEvent]:
        """
        Get history of events.
        
        Args:
            limit: Maximum number of events to return
            event_type: Optional event type to filter by
            category: Optional event category to filter by
            
        Returns:
            List of events
        """
        # Filter history
        filtered_history = self.event_history
        
        if event_type is not None:
            filtered_history = [
                event for event in filtered_history
                if event.event_type == event_type
            ]
            
        if category is not None:
            filtered_history = [
                event for event in filtered_history
                if event.category == category
            ]
            
        # Apply limit
        if limit is not None:
            filtered_history = filtered_history[-limit:]
            
        return filtered_history
    
    def clear_history(self) -> None:
        """Clear event history."""
        self.event_history = []
        
    def update(self) -> None:
        """Update the event handler and its components."""
        # Update ritual engine
        self.ritual_engine.update_rituals()
        
    def get_ritual_engine(self) -> CapsuleRitualEngine:
        """
        Get the Capsule Ritual Engine.
        
        Returns:
            The Capsule Ritual Engine
        """
        return self.ritual_engine
    
    def create_override_ritual(self,
                             capsule_id: str,
                             agent_id: Optional[str] = None,
                             intensity: float = 0.7,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create an override ritual (when human overrides an agent decision).
        
        Args:
            capsule_id: ID of the capsule being overridden
            agent_id: Optional ID of the agent being overridden
            intensity: Intensity of the ritual (0.0 to 1.0)
            metadata: Additional metadata for this event
            
        Returns:
            ID of the created ritual
        """
        return self.dispatch_ritual_event(
            ritual_type="override",
            source_id=capsule_id,
            target_id=agent_id,
            emotion="focused",
            intensity=intensity,
            metadata=metadata
        )
        
    def create_approval_ritual(self,
                             capsule_id: str,
                             agent_id: Optional[str] = None,
                             intensity: float = 0.6,
                             metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create an approval ritual (when human approves an agent decision).
        
        Args:
            capsule_id: ID of the capsule being approved
            agent_id: Optional ID of the agent being approved
            intensity: Intensity of the ritual (0.0 to 1.0)
            metadata: Additional metadata for this event
            
        Returns:
            ID of the created ritual
        """
        return self.dispatch_ritual_event(
            ritual_type="approval",
            source_id=capsule_id,
            target_id=agent_id,
            emotion="celebratory",
            intensity=intensity,
            metadata=metadata
        )
        
    def create_completion_ritual(self,
                               capsule_id: str,
                               intensity: float = 0.8,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a completion ritual (when a task or workflow completes).
        
        Args:
            capsule_id: ID of the capsule that completed
            intensity: Intensity of the ritual (0.0 to 1.0)
            metadata: Additional metadata for this event
            
        Returns:
            ID of the created ritual
        """
        return self.dispatch_ritual_event(
            ritual_type="completion",
            source_id=capsule_id,
            emotion="productive",
            intensity=intensity,
            metadata=metadata
        )
        
    def create_connection_ritual(self,
                               source_id: str,
                               target_id: str,
                               intensity: float = 0.5,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a connection ritual (when connecting capsules or agents).
        
        Args:
            source_id: ID of the source component/entity
            target_id: ID of the target component/entity
            intensity: Intensity of the ritual (0.0 to 1.0)
            metadata: Additional metadata for this event
            
        Returns:
            ID of the created ritual
        """
        return self.dispatch_ritual_event(
            ritual_type="connection",
            source_id=source_id,
            target_id=target_id,
            emotion="calm",
            intensity=intensity,
            metadata=metadata
        )

# Helper functions

def _get_emotion_color_palette(emotion: str) -> List[str]:
    """
    Get a color palette for an emotion.
    
    Args:
        emotion: Emotional tone
        
    Returns:
        List of color hex codes
    """
    if emotion.lower() == "calm":
        return ["#4FC3F7", "#29B6F6", "#03A9F4", "#039BE5", "#0288D1"]
    elif emotion.lower() == "urgent":
        return ["#FF8A80", "#FF5252", "#FF1744", "#D50000", "#B71C1C"]
    elif emotion.lower() == "celebratory":
        return ["#FFFF8D", "#FFFF00", "#FFEA00", "#FFD600", "#FFC107"]
    elif emotion.lower() == "focused":
        return ["#B388FF", "#7C4DFF", "#651FFF", "#6200EA", "#4527A0"]
    elif emotion.lower() == "productive":
        return ["#A5D6A7", "#66BB6A", "#4CAF50", "#43A047", "#2E7D32"]
    else:  # neutral
        return ["#90CAF9", "#64B5F6", "#42A5F5", "#2196F3", "#1E88E5"]
