"""
View Transition Manager for Universal Skin Shell in the Industriverse UI/UX Layer.

This module manages transitions between different views and contexts in the Universal Skin Shell,
providing smooth, animated, and contextually appropriate transitions that maintain user orientation
and enhance the ambient intelligence experience.

Author: Manus
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple, Union
from enum import Enum
import uuid

class TransitionType(Enum):
    """Enumeration of view transition types."""
    FADE = "fade"
    SLIDE = "slide"
    ZOOM = "zoom"
    FLIP = "flip"
    MORPH = "morph"
    DISSOLVE = "dissolve"
    REVEAL = "reveal"
    RITUAL = "ritual"  # Enhanced transition with emotional resonance
    SWARM = "swarm"    # Transition using swarm-like particle effects
    AVATAR = "avatar"  # Transition featuring agent avatar animation
    CUSTOM = "custom"

class TransitionDirection(Enum):
    """Enumeration of transition directions."""
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    IN = "in"
    OUT = "out"
    CLOCKWISE = "clockwise"
    COUNTERCLOCKWISE = "counterclockwise"
    CUSTOM = "custom"

class TransitionTiming(Enum):
    """Enumeration of transition timing functions."""
    LINEAR = "linear"
    EASE = "ease"
    EASE_IN = "ease-in"
    EASE_OUT = "ease-out"
    EASE_IN_OUT = "ease-in-out"
    BOUNCE = "bounce"
    ELASTIC = "elastic"
    CUSTOM = "custom"

class TransitionEvent:
    """Represents a transition event in the View Transition Manager."""
    
    def __init__(self,
                 event_type: str,
                 from_view: Optional[str] = None,
                 to_view: Optional[str] = None,
                 transition_id: Optional[str] = None,
                 progress: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a transition event.
        
        Args:
            event_type: Type of event (e.g., "start", "progress", "complete", "cancel")
            from_view: ID of the view transitioning from
            to_view: ID of the view transitioning to
            transition_id: ID of the transition
            progress: Progress of the transition (0.0 to 1.0)
            metadata: Additional metadata for this event
        """
        self.event_type = event_type
        self.from_view = from_view
        self.to_view = to_view
        self.transition_id = transition_id
        self.progress = progress
        self.metadata = metadata or {}
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this event to a dictionary representation."""
        return {
            "event_type": self.event_type,
            "from_view": self.from_view,
            "to_view": self.to_view,
            "transition_id": self.transition_id,
            "progress": self.progress,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

class TransitionDefinition:
    """Defines a transition between views."""
    
    def __init__(self,
                 transition_type: TransitionType,
                 duration: float = 0.3,
                 direction: Optional[TransitionDirection] = None,
                 timing: TransitionTiming = TransitionTiming.EASE,
                 delay: float = 0.0,
                 stagger: float = 0.0,
                 custom_params: Optional[Dict[str, Any]] = None):
        """
        Initialize a transition definition.
        
        Args:
            transition_type: Type of transition
            duration: Duration of the transition in seconds
            direction: Direction of the transition
            timing: Timing function for the transition
            delay: Delay before starting the transition in seconds
            stagger: Stagger time between elements in seconds
            custom_params: Additional parameters for custom transitions
        """
        self.transition_type = transition_type
        self.duration = duration
        self.direction = direction
        self.timing = timing
        self.delay = delay
        self.stagger = stagger
        self.custom_params = custom_params or {}
        
        # Set default direction based on transition type
        if self.direction is None:
            if transition_type == TransitionType.SLIDE:
                self.direction = TransitionDirection.RIGHT
            elif transition_type == TransitionType.ZOOM:
                self.direction = TransitionDirection.IN
            elif transition_type == TransitionType.FLIP:
                self.direction = TransitionDirection.RIGHT
            else:
                self.direction = None
                
    def to_dict(self) -> Dict[str, Any]:
        """Convert this definition to a dictionary representation."""
        return {
            "transition_type": self.transition_type.value,
            "duration": self.duration,
            "direction": self.direction.value if self.direction else None,
            "timing": self.timing.value,
            "delay": self.delay,
            "stagger": self.stagger,
            "custom_params": self.custom_params
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TransitionDefinition':
        """Create a transition definition from a dictionary representation."""
        return cls(
            transition_type=TransitionType(data["transition_type"]),
            duration=data.get("duration", 0.3),
            direction=TransitionDirection(data["direction"]) if data.get("direction") else None,
            timing=TransitionTiming(data["timing"]) if data.get("timing") else TransitionTiming.EASE,
            delay=data.get("delay", 0.0),
            stagger=data.get("stagger", 0.0),
            custom_params=data.get("custom_params", {})
        )
        
    @classmethod
    def create_ritual_transition(cls, 
                               emotion: str = "neutral", 
                               intensity: float = 0.5,
                               duration: float = 0.8) -> 'TransitionDefinition':
        """
        Create a ritual transition with emotional resonance.
        
        Args:
            emotion: Emotional tone of the transition (e.g., "calm", "urgent", "celebratory")
            intensity: Intensity of the emotional effect (0.0 to 1.0)
            duration: Duration of the transition in seconds
            
        Returns:
            A ritual transition definition
        """
        # Customize parameters based on emotion and intensity
        custom_params = {
            "emotion": emotion,
            "intensity": intensity,
            "particle_count": int(100 + 200 * intensity),
            "color_palette": _get_emotion_color_palette(emotion),
            "sound_effect": f"ritual_{emotion.lower()}",
            "haptic_pattern": f"ritual_{emotion.lower()}"
        }
        
        return cls(
            transition_type=TransitionType.RITUAL,
            duration=duration,
            timing=TransitionTiming.EASE_IN_OUT,
            custom_params=custom_params
        )
        
    @classmethod
    def create_swarm_transition(cls,
                              swarm_size: int = 100,
                              swarm_speed: float = 0.5,
                              swarm_coherence: float = 0.7,
                              duration: float = 1.0) -> 'TransitionDefinition':
        """
        Create a swarm-based transition using particle effects.
        
        Args:
            swarm_size: Number of particles in the swarm
            swarm_speed: Speed of the swarm movement (0.0 to 1.0)
            swarm_coherence: Coherence of the swarm (0.0 to 1.0)
            duration: Duration of the transition in seconds
            
        Returns:
            A swarm transition definition
        """
        custom_params = {
            "swarm_size": swarm_size,
            "swarm_speed": swarm_speed,
            "swarm_coherence": swarm_coherence,
            "swarm_color": "#2196F3",  # Default blue
            "swarm_trail": True,
            "swarm_3d": True,
            "sound_effect": "swarm_movement",
            "haptic_pattern": "swarm_pulse"
        }
        
        return cls(
            transition_type=TransitionType.SWARM,
            duration=duration,
            timing=TransitionTiming.EASE_OUT,
            custom_params=custom_params
        )
        
    @classmethod
    def create_avatar_transition(cls,
                               avatar_id: str,
                               animation: str = "transition",
                               duration: float = 1.2) -> 'TransitionDefinition':
        """
        Create an avatar-based transition featuring agent animation.
        
        Args:
            avatar_id: ID of the avatar to animate
            animation: Type of animation to perform
            duration: Duration of the transition in seconds
            
        Returns:
            An avatar transition definition
        """
        custom_params = {
            "avatar_id": avatar_id,
            "animation": animation,
            "scale_factor": 1.5,
            "opacity_start": 0.8,
            "opacity_end": 0.0,
            "sound_effect": f"avatar_{animation}",
            "haptic_pattern": f"avatar_{animation}"
        }
        
        return cls(
            transition_type=TransitionType.AVATAR,
            duration=duration,
            timing=TransitionTiming.EASE_IN_OUT,
            custom_params=custom_params
        )

class ActiveTransition:
    """Represents an active transition between views."""
    
    def __init__(self,
                 transition_id: str,
                 from_view: str,
                 to_view: str,
                 definition: TransitionDefinition,
                 on_complete: Optional[Callable[[], None]] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize an active transition.
        
        Args:
            transition_id: Unique identifier for this transition
            from_view: ID of the view transitioning from
            to_view: ID of the view transitioning to
            definition: Definition of the transition
            on_complete: Callback to call when the transition completes
            metadata: Additional metadata for this transition
        """
        self.transition_id = transition_id
        self.from_view = from_view
        self.to_view = to_view
        self.definition = definition
        self.on_complete = on_complete
        self.metadata = metadata or {}
        self.start_time = time.time()
        self.end_time = self.start_time + definition.duration + definition.delay
        self.progress = 0.0
        self.is_complete = False
        self.is_cancelled = False
        
    def update(self, current_time: Optional[float] = None) -> float:
        """
        Update the transition progress.
        
        Args:
            current_time: Current time (defaults to time.time())
            
        Returns:
            Current progress (0.0 to 1.0)
        """
        if self.is_complete or self.is_cancelled:
            return self.progress
            
        if current_time is None:
            current_time = time.time()
            
        # Calculate raw progress
        elapsed = current_time - self.start_time - self.definition.delay
        if elapsed < 0:
            # Still in delay phase
            self.progress = 0.0
        else:
            # In active transition phase
            self.progress = min(1.0, elapsed / self.definition.duration)
            
        # Check if complete
        if current_time >= self.end_time:
            self.progress = 1.0
            self.is_complete = True
            if self.on_complete:
                self.on_complete()
                
        return self.progress
        
    def cancel(self) -> None:
        """Cancel the transition."""
        self.is_cancelled = True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this transition to a dictionary representation."""
        return {
            "transition_id": self.transition_id,
            "from_view": self.from_view,
            "to_view": self.to_view,
            "definition": self.definition.to_dict(),
            "metadata": self.metadata,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "progress": self.progress,
            "is_complete": self.is_complete,
            "is_cancelled": self.is_cancelled
        }

class ViewTransitionManager:
    """
    Manages transitions between views in the Universal Skin Shell.
    
    This class provides:
    - Transition definition and customization
    - Transition execution and control
    - Transition event handling
    - Context-aware transition selection
    - Transition presets for different scenarios
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the View Transition Manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.transition_presets: Dict[str, TransitionDefinition] = {}
        self.view_transition_rules: Dict[Tuple[str, str], str] = {}  # (from_view, to_view) -> preset_name
        self.active_transitions: Dict[str, ActiveTransition] = {}
        self.transition_listeners: List[Callable[[TransitionEvent], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize default transition presets
        self._initialize_default_presets()
        
    def _initialize_default_presets(self) -> None:
        """Initialize default transition presets."""
        # Basic transitions
        self.register_transition_preset("default", TransitionDefinition(
            transition_type=TransitionType.FADE,
            duration=0.3
        ))
        
        self.register_transition_preset("slide_left", TransitionDefinition(
            transition_type=TransitionType.SLIDE,
            duration=0.3,
            direction=TransitionDirection.LEFT
        ))
        
        self.register_transition_preset("slide_right", TransitionDefinition(
            transition_type=TransitionType.SLIDE,
            duration=0.3,
            direction=TransitionDirection.RIGHT
        ))
        
        self.register_transition_preset("zoom_in", TransitionDefinition(
            transition_type=TransitionType.ZOOM,
            duration=0.4,
            direction=TransitionDirection.IN
        ))
        
        self.register_transition_preset("zoom_out", TransitionDefinition(
            transition_type=TransitionType.ZOOM,
            duration=0.4,
            direction=TransitionDirection.OUT
        ))
        
        # Enhanced transitions
        self.register_transition_preset("ritual_calm", TransitionDefinition.create_ritual_transition(
            emotion="calm",
            intensity=0.6,
            duration=0.8
        ))
        
        self.register_transition_preset("ritual_urgent", TransitionDefinition.create_ritual_transition(
            emotion="urgent",
            intensity=0.8,
            duration=0.6
        ))
        
        self.register_transition_preset("ritual_celebratory", TransitionDefinition.create_ritual_transition(
            emotion="celebratory",
            intensity=0.9,
            duration=1.2
        ))
        
        self.register_transition_preset("swarm_gentle", TransitionDefinition.create_swarm_transition(
            swarm_size=80,
            swarm_speed=0.4,
            swarm_coherence=0.8,
            duration=1.0
        ))
        
        self.register_transition_preset("swarm_energetic", TransitionDefinition.create_swarm_transition(
            swarm_size=150,
            swarm_speed=0.7,
            swarm_coherence=0.6,
            duration=0.8
        ))
        
        # Set up some default transition rules
        self.set_transition_rule("dashboard", "detail", "zoom_in")
        self.set_transition_rule("detail", "dashboard", "zoom_out")
        self.set_transition_rule("*", "alert", "ritual_urgent")
        self.set_transition_rule("*", "celebration", "ritual_celebratory")
        self.set_transition_rule("*", "agent_view", "swarm_gentle")
        
    def register_transition_preset(self, 
                                 name: str, 
                                 definition: TransitionDefinition) -> None:
        """
        Register a transition preset.
        
        Args:
            name: Name of the preset
            definition: Transition definition
        """
        self.transition_presets[name] = definition
        
    def get_transition_preset(self, name: str) -> Optional[TransitionDefinition]:
        """
        Get a transition preset by name.
        
        Args:
            name: Name of the preset
            
        Returns:
            The transition definition, or None if not found
        """
        return self.transition_presets.get(name)
    
    def set_transition_rule(self, 
                          from_view: str, 
                          to_view: str, 
                          preset_name: str) -> None:
        """
        Set a rule for which transition to use between views.
        
        Args:
            from_view: ID of the source view, or "*" for any view
            to_view: ID of the destination view
            preset_name: Name of the transition preset to use
        """
        if preset_name not in self.transition_presets:
            self.logger.warning(f"Transition preset '{preset_name}' not found, rule not set")
            return
            
        self.view_transition_rules[(from_view, to_view)] = preset_name
        
    def get_transition_for_views(self, 
                               from_view: str, 
                               to_view: str) -> TransitionDefinition:
        """
        Get the appropriate transition definition for a view transition.
        
        Args:
            from_view: ID of the source view
            to_view: ID of the destination view
            
        Returns:
            The transition definition to use
        """
        # Check for exact match
        if (from_view, to_view) in self.view_transition_rules:
            preset_name = self.view_transition_rules[(from_view, to_view)]
            return self.transition_presets[preset_name]
            
        # Check for wildcard source
        if ("*", to_view) in self.view_transition_rules:
            preset_name = self.view_transition_rules[("*", to_view)]
            return self.transition_presets[preset_name]
            
        # Check for wildcard destination
        if (from_view, "*") in self.view_transition_rules:
            preset_name = self.view_transition_rules[(from_view, "*")]
            return self.transition_presets[preset_name]
            
        # Check for double wildcard
        if ("*", "*") in self.view_transition_rules:
            preset_name = self.view_transition_rules[("*", "*")]
            return self.transition_presets[preset_name]
            
        # Fall back to default
        return self.transition_presets["default"]
    
    def start_transition(self,
                        from_view: str,
                        to_view: str,
                        transition_def: Optional[Union[str, TransitionDefinition]] = None,
                        on_complete: Optional[Callable[[], None]] = None,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Start a transition between views.
        
        Args:
            from_view: ID of the source view
            to_view: ID of the destination view
            transition_def: Transition definition or preset name (auto-selected if None)
            on_complete: Callback to call when the transition completes
            metadata: Additional metadata for this transition
            
        Returns:
            ID of the created transition
        """
        # Determine transition definition
        if transition_def is None:
            definition = self.get_transition_for_views(from_view, to_view)
        elif isinstance(transition_def, str):
            if transition_def in self.transition_presets:
                definition = self.transition_presets[transition_def]
            else:
                self.logger.warning(f"Transition preset '{transition_def}' not found, using default")
                definition = self.transition_presets["default"]
        else:
            definition = transition_def
            
        # Create transition ID
        transition_id = str(uuid.uuid4())
        
        # Create active transition
        transition = ActiveTransition(
            transition_id=transition_id,
            from_view=from_view,
            to_view=to_view,
            definition=definition,
            on_complete=on_complete,
            metadata=metadata or {}
        )
        
        # Store active transition
        self.active_transitions[transition_id] = transition
        
        # Create and dispatch transition event
        event = TransitionEvent(
            event_type="start",
            from_view=from_view,
            to_view=to_view,
            transition_id=transition_id,
            progress=0.0,
            metadata=metadata
        )
        self._dispatch_transition_event(event)
        
        return transition_id
    
    def update_transitions(self, current_time: Optional[float] = None) -> None:
        """
        Update all active transitions.
        
        Args:
            current_time: Current time (defaults to time.time())
        """
        if current_time is None:
            current_time = time.time()
            
        # Update each active transition
        completed_transitions = []
        
        for transition_id, transition in list(self.active_transitions.items()):
            old_progress = transition.progress
            new_progress = transition.update(current_time)
            
            # If progress changed significantly, dispatch progress event
            if abs(new_progress - old_progress) >= 0.05:
                event = TransitionEvent(
                    event_type="progress",
                    from_view=transition.from_view,
                    to_view=transition.to_view,
                    transition_id=transition_id,
                    progress=new_progress,
                    metadata=transition.metadata
                )
                self._dispatch_transition_event(event)
                
            # If transition completed, add to completed list
            if transition.is_complete:
                completed_transitions.append(transition_id)
                
        # Remove completed transitions and dispatch complete events
        for transition_id in completed_transitions:
            transition = self.active_transitions.pop(transition_id)
            
            event = TransitionEvent(
                event_type="complete",
                from_view=transition.from_view,
                to_view=transition.to_view,
                transition_id=transition_id,
                progress=1.0,
                metadata=transition.metadata
            )
            self._dispatch_transition_event(event)
            
    def cancel_transition(self, transition_id: str) -> bool:
        """
        Cancel an active transition.
        
        Args:
            transition_id: ID of the transition to cancel
            
        Returns:
            True if the transition was cancelled, False if not found
        """
        if transition_id not in self.active_transitions:
            return False
            
        transition = self.active_transitions.pop(transition_id)
        transition.cancel()
        
        # Create and dispatch transition event
        event = TransitionEvent(
            event_type="cancel",
            from_view=transition.from_view,
            to_view=transition.to_view,
            transition_id=transition_id,
            progress=transition.progress,
            metadata=transition.metadata
        )
        self._dispatch_transition_event(event)
        
        return True
    
    def get_active_transition(self, transition_id: str) -> Optional[ActiveTransition]:
        """
        Get an active transition by ID.
        
        Args:
            transition_id: ID of the transition to get
            
        Returns:
            The active transition, or None if not found
        """
        return self.active_transitions.get(transition_id)
    
    def get_all_active_transitions(self) -> List[ActiveTransition]:
        """
        Get all active transitions.
        
        Returns:
            List of all active transitions
        """
        return list(self.active_transitions.values())
    
    def add_transition_listener(self, listener: Callable[[TransitionEvent], None]) -> None:
        """
        Add a listener for transition events.
        
        Args:
            listener: Callback function that will be called with transition events
        """
        self.transition_listeners.append(listener)
        
    def remove_transition_listener(self, listener: Callable[[TransitionEvent], None]) -> None:
        """
        Remove a listener for transition events.
        
        Args:
            listener: The listener to remove
        """
        if listener in self.transition_listeners:
            self.transition_listeners.remove(listener)
            
    def _dispatch_transition_event(self, event: TransitionEvent) -> None:
        """
        Dispatch a transition event to all listeners.
        
        Args:
            event: The transition event to dispatch
        """
        for listener in self.transition_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error in transition listener: {e}")
                
    def create_ritual_transition(self,
                               from_view: str,
                               to_view: str,
                               emotion: str = "neutral",
                               intensity: float = 0.5,
                               duration: float = 0.8,
                               on_complete: Optional[Callable[[], None]] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create and start a ritual transition with emotional resonance.
        
        Args:
            from_view: ID of the source view
            to_view: ID of the destination view
            emotion: Emotional tone of the transition
            intensity: Intensity of the emotional effect
            duration: Duration of the transition in seconds
            on_complete: Callback to call when the transition completes
            metadata: Additional metadata for this transition
            
        Returns:
            ID of the created transition
        """
        definition = TransitionDefinition.create_ritual_transition(
            emotion=emotion,
            intensity=intensity,
            duration=duration
        )
        
        return self.start_transition(
            from_view=from_view,
            to_view=to_view,
            transition_def=definition,
            on_complete=on_complete,
            metadata=metadata
        )
        
    def create_swarm_transition(self,
                              from_view: str,
                              to_view: str,
                              swarm_size: int = 100,
                              swarm_speed: float = 0.5,
                              swarm_coherence: float = 0.7,
                              duration: float = 1.0,
                              on_complete: Optional[Callable[[], None]] = None,
                              metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create and start a swarm-based transition using particle effects.
        
        Args:
            from_view: ID of the source view
            to_view: ID of the destination view
            swarm_size: Number of particles in the swarm
            swarm_speed: Speed of the swarm movement
            swarm_coherence: Coherence of the swarm
            duration: Duration of the transition in seconds
            on_complete: Callback to call when the transition completes
            metadata: Additional metadata for this transition
            
        Returns:
            ID of the created transition
        """
        definition = TransitionDefinition.create_swarm_transition(
            swarm_size=swarm_size,
            swarm_speed=swarm_speed,
            swarm_coherence=swarm_coherence,
            duration=duration
        )
        
        return self.start_transition(
            from_view=from_view,
            to_view=to_view,
            transition_def=definition,
            on_complete=on_complete,
            metadata=metadata
        )
        
    def create_avatar_transition(self,
                               from_view: str,
                               to_view: str,
                               avatar_id: str,
                               animation: str = "transition",
                               duration: float = 1.2,
                               on_complete: Optional[Callable[[], None]] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create and start an avatar-based transition featuring agent animation.
        
        Args:
            from_view: ID of the source view
            to_view: ID of the destination view
            avatar_id: ID of the avatar to animate
            animation: Type of animation to perform
            duration: Duration of the transition in seconds
            on_complete: Callback to call when the transition completes
            metadata: Additional metadata for this transition
            
        Returns:
            ID of the created transition
        """
        definition = TransitionDefinition.create_avatar_transition(
            avatar_id=avatar_id,
            animation=animation,
            duration=duration
        )
        
        return self.start_transition(
            from_view=from_view,
            to_view=to_view,
            transition_def=definition,
            on_complete=on_complete,
            metadata=metadata
        )
        
    def get_transition_css(self, transition_id: str) -> Optional[str]:
        """
        Get CSS representation of a transition for web rendering.
        
        Args:
            transition_id: ID of the transition
            
        Returns:
            CSS string for the transition, or None if not found
        """
        transition = self.get_active_transition(transition_id)
        if not transition:
            return None
            
        definition = transition.definition
        
        # Base transition properties
        css_parts = []
        
        # Transition property
        if definition.transition_type == TransitionType.FADE:
            css_parts.append("opacity")
        elif definition.transition_type == TransitionType.SLIDE:
            css_parts.append("transform")
        elif definition.transition_type == TransitionType.ZOOM:
            css_parts.append("transform")
        elif definition.transition_type == TransitionType.FLIP:
            css_parts.append("transform")
        else:
            css_parts.append("all")
            
        # Duration
        css_parts.append(f"{definition.duration}s")
        
        # Timing function
        if definition.timing == TransitionTiming.LINEAR:
            css_parts.append("linear")
        elif definition.timing == TransitionTiming.EASE:
            css_parts.append("ease")
        elif definition.timing == TransitionTiming.EASE_IN:
            css_parts.append("ease-in")
        elif definition.timing == TransitionTiming.EASE_OUT:
            css_parts.append("ease-out")
        elif definition.timing == TransitionTiming.EASE_IN_OUT:
            css_parts.append("ease-in-out")
        elif definition.timing == TransitionTiming.BOUNCE:
            css_parts.append("cubic-bezier(0.68, -0.55, 0.27, 1.55)")
        elif definition.timing == TransitionTiming.ELASTIC:
            css_parts.append("cubic-bezier(0.68, -0.55, 0.27, 1.55)")
        else:
            css_parts.append("ease")
            
        # Delay
        css_parts.append(f"{definition.delay}s")
        
        return f"transition: {' '.join(css_parts)};"
        
    def get_transition_keyframes(self, transition_id: str) -> Optional[str]:
        """
        Get CSS keyframes for a transition for web rendering.
        
        Args:
            transition_id: ID of the transition
            
        Returns:
            CSS keyframes string for the transition, or None if not found
        """
        transition = self.get_active_transition(transition_id)
        if not transition:
            return None
            
        definition = transition.definition
        
        # Generate keyframes based on transition type
        keyframes = []
        
        if definition.transition_type == TransitionType.FADE:
            keyframes.append("@keyframes fade {")
            keyframes.append("  0% { opacity: 0; }")
            keyframes.append("  100% { opacity: 1; }")
            keyframes.append("}")
            
        elif definition.transition_type == TransitionType.SLIDE:
            direction = definition.direction or TransitionDirection.RIGHT
            
            keyframes.append("@keyframes slide {")
            if direction == TransitionDirection.LEFT:
                keyframes.append("  0% { transform: translateX(100%); }")
                keyframes.append("  100% { transform: translateX(0); }")
            elif direction == TransitionDirection.RIGHT:
                keyframes.append("  0% { transform: translateX(-100%); }")
                keyframes.append("  100% { transform: translateX(0); }")
            elif direction == TransitionDirection.UP:
                keyframes.append("  0% { transform: translateY(100%); }")
                keyframes.append("  100% { transform: translateY(0); }")
            elif direction == TransitionDirection.DOWN:
                keyframes.append("  0% { transform: translateY(-100%); }")
                keyframes.append("  100% { transform: translateY(0); }")
            keyframes.append("}")
            
        elif definition.transition_type == TransitionType.ZOOM:
            direction = definition.direction or TransitionDirection.IN
            
            keyframes.append("@keyframes zoom {")
            if direction == TransitionDirection.IN:
                keyframes.append("  0% { transform: scale(0.5); opacity: 0; }")
                keyframes.append("  100% { transform: scale(1); opacity: 1; }")
            elif direction == TransitionDirection.OUT:
                keyframes.append("  0% { transform: scale(1.5); opacity: 0; }")
                keyframes.append("  100% { transform: scale(1); opacity: 1; }")
            keyframes.append("}")
            
        elif definition.transition_type == TransitionType.FLIP:
            direction = definition.direction or TransitionDirection.RIGHT
            
            keyframes.append("@keyframes flip {")
            if direction == TransitionDirection.LEFT:
                keyframes.append("  0% { transform: rotateY(90deg); opacity: 0; }")
                keyframes.append("  100% { transform: rotateY(0); opacity: 1; }")
            elif direction == TransitionDirection.RIGHT:
                keyframes.append("  0% { transform: rotateY(-90deg); opacity: 0; }")
                keyframes.append("  100% { transform: rotateY(0); opacity: 1; }")
            elif direction == TransitionDirection.UP:
                keyframes.append("  0% { transform: rotateX(-90deg); opacity: 0; }")
                keyframes.append("  100% { transform: rotateX(0); opacity: 1; }")
            elif direction == TransitionDirection.DOWN:
                keyframes.append("  0% { transform: rotateX(90deg); opacity: 0; }")
                keyframes.append("  100% { transform: rotateX(0); opacity: 1; }")
            keyframes.append("}")
            
        elif definition.transition_type == TransitionType.RITUAL:
            emotion = definition.custom_params.get("emotion", "neutral")
            intensity = definition.custom_params.get("intensity", 0.5)
            
            keyframes.append("@keyframes ritual {")
            keyframes.append("  0% { opacity: 0; filter: blur(10px); }")
            keyframes.append("  30% { opacity: 0.7; filter: blur(5px); }")
            keyframes.append("  70% { opacity: 0.9; filter: blur(3px); }")
            keyframes.append("  100% { opacity: 1; filter: blur(0); }")
            keyframes.append("}")
            
        elif definition.transition_type == TransitionType.SWARM:
            keyframes.append("@keyframes swarm {")
            keyframes.append("  0% { opacity: 0; transform: scale(0.8); }")
            keyframes.append("  50% { opacity: 0.7; transform: scale(1.05); }")
            keyframes.append("  100% { opacity: 1; transform: scale(1); }")
            keyframes.append("}")
            
        elif definition.transition_type == TransitionType.AVATAR:
            keyframes.append("@keyframes avatar {")
            keyframes.append("  0% { opacity: 0; transform: scale(1.2) translateY(20px); }")
            keyframes.append("  40% { opacity: 0.8; transform: scale(1.1) translateY(10px); }")
            keyframes.append("  70% { opacity: 0.9; transform: scale(1.05) translateY(5px); }")
            keyframes.append("  100% { opacity: 1; transform: scale(1) translateY(0); }")
            keyframes.append("}")
            
        return "\n".join(keyframes)

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
"""
