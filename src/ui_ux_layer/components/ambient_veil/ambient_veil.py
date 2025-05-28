"""
Ambient Veil Component for the Industriverse UI/UX Layer.

This module provides an ambient awareness system that creates a subtle, 
non-intrusive layer of contextual information and feedback in the user's 
peripheral awareness. It serves as the ambient intelligence manifestation
in the Universal Skin environment.

Author: Manus
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class AmbientVeilMode(Enum):
    """Enumeration of ambient veil modes."""
    MINIMAL = "minimal"
    STANDARD = "standard"
    ENHANCED = "enhanced"
    IMMERSIVE = "immersive"
    CUSTOM = "custom"

class AmbientVeilLayer(Enum):
    """Enumeration of ambient veil layers."""
    BACKGROUND = "background"
    MIDGROUND = "midground"
    FOREGROUND = "foreground"
    OVERLAY = "overlay"
    CUSTOM = "custom"

class AmbientVeilEventType(Enum):
    """Enumeration of ambient veil event types."""
    ELEMENT_ADDED = "element_added"
    ELEMENT_REMOVED = "element_removed"
    ELEMENT_UPDATED = "element_updated"
    MODE_CHANGED = "mode_changed"
    VISIBILITY_CHANGED = "visibility_changed"
    INTERACTION = "interaction"
    CUSTOM = "custom"

class AmbientVeilElementType(Enum):
    """Enumeration of ambient veil element types."""
    INDICATOR = "indicator"
    NOTIFICATION = "notification"
    AMBIENT_AUDIO = "ambient_audio"
    AMBIENT_LIGHT = "ambient_light"
    PARTICLE_SYSTEM = "particle_system"
    FLOW_FIELD = "flow_field"
    AMBIENT_TEXT = "ambient_text"
    AMBIENT_ICON = "ambient_icon"
    AMBIENT_AVATAR = "ambient_avatar"
    CUSTOM = "custom"

@dataclass
class AmbientVeilStyle:
    """Data class representing ambient veil styling options."""
    background_color: str = "rgba(0, 0, 0, 0.05)"
    foreground_color: str = "rgba(255, 255, 255, 0.8)"
    accent_color: str = "rgba(64, 156, 255, 0.8)"
    alert_color: str = "rgba(255, 64, 64, 0.8)"
    success_color: str = "rgba(64, 255, 128, 0.8)"
    warning_color: str = "rgba(255, 192, 64, 0.8)"
    info_color: str = "rgba(64, 192, 255, 0.8)"
    blur_radius: int = 10
    opacity: float = 0.8
    transition_duration: int = 500
    animation_duration: int = 2000
    custom_css: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AmbientVeilEvent:
    """Data class representing an ambient veil event."""
    event_type: AmbientVeilEventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class AmbientVeilElement:
    """Data class representing an ambient veil element."""
    element_id: str
    type: AmbientVeilElementType
    content: Any
    layer: AmbientVeilLayer = AmbientVeilLayer.MIDGROUND
    position: Dict[str, Any] = field(default_factory=lambda: {"x": 0, "y": 0, "z": 0})
    size: Dict[str, Any] = field(default_factory=lambda: {"width": 100, "height": 100})
    opacity: float = 0.8
    visible: bool = True
    interactive: bool = False
    priority: int = 0
    duration: Optional[int] = None
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the element to a dictionary."""
        result = {
            "id": self.element_id,
            "type": self.type.value,
            "content": self.content,
            "layer": self.layer.value,
            "position": self.position,
            "size": self.size,
            "opacity": self.opacity,
            "visible": self.visible,
            "interactive": self.interactive,
            "priority": self.priority,
            "duration": self.duration,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "style": self.style,
            "metadata": self.metadata
        }
        
        return result
    
    def is_expired(self) -> bool:
        """Check if the element has expired."""
        if self.duration is None:
            return False
            
        if self.end_time is None:
            self.end_time = self.start_time + self.duration / 1000
            
        return time.time() > self.end_time

class AmbientVeilComponent:
    """
    Provides an ambient awareness system for the Industriverse UI/UX Layer.
    
    This class provides:
    - Ambient information display
    - Peripheral awareness indicators
    - Contextual background effects
    - Subtle notifications and feedback
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Ambient Veil Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.is_visible = True
        self.mode = AmbientVeilMode.STANDARD
        self.style = AmbientVeilStyle()
        self.elements: Dict[str, AmbientVeilElement] = {}
        self.event_listeners: Dict[AmbientVeilEventType, List[Callable[[AmbientVeilEvent], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize from config if provided
        if config:
            if "mode" in config:
                try:
                    self.mode = AmbientVeilMode(config["mode"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid mode: {config['mode']}, using default.")
                    
            if "visible" in config:
                self.is_visible = bool(config["visible"])
                
            if "style" in config:
                for key, value in config["style"].items():
                    if hasattr(self.style, key):
                        setattr(self.style, key, value)
                    else:
                        self.style.custom_css[key] = value
        
    def start(self) -> bool:
        """
        Start the Ambient Veil Component.
        
        Returns:
            True if the component was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start cleanup timer for expired elements
        self._start_cleanup_timer()
        
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.CUSTOM, {
            "action": "component_started"
        })
        
        self.logger.info("Ambient Veil Component started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Ambient Veil Component.
        
        Returns:
            True if the component was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Stop cleanup timer
        self._stop_cleanup_timer()
        
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.CUSTOM, {
            "action": "component_stopped"
        })
        
        self.logger.info("Ambient Veil Component stopped.")
        return True
    
    def _start_cleanup_timer(self) -> None:
        """Start the cleanup timer for expired elements."""
        # In a real implementation, this would start a timer
        # For this example, we'll just log that it would happen
        self.logger.debug("Cleanup timer started.")
    
    def _stop_cleanup_timer(self) -> None:
        """Stop the cleanup timer."""
        # In a real implementation, this would stop the timer
        # For this example, we'll just log that it would happen
        self.logger.debug("Cleanup timer stopped.")
    
    def _cleanup_expired_elements(self) -> None:
        """Remove expired elements."""
        expired_ids = []
        
        for element_id, element in self.elements.items():
            if element.is_expired():
                expired_ids.append(element_id)
                
        for element_id in expired_ids:
            self.remove_element(element_id)
            
        if expired_ids:
            self.logger.debug(f"Removed {len(expired_ids)} expired elements.")
    
    def add_element(self,
                  type: Union[AmbientVeilElementType, str],
                  content: Any,
                  layer: Union[AmbientVeilLayer, str] = AmbientVeilLayer.MIDGROUND,
                  position: Optional[Dict[str, Any]] = None,
                  size: Optional[Dict[str, Any]] = None,
                  opacity: float = 0.8,
                  visible: bool = True,
                  interactive: bool = False,
                  priority: int = 0,
                  duration: Optional[int] = None,
                  style: Optional[Dict[str, Any]] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  element_id: Optional[str] = None) -> str:
        """
        Add an element to the ambient veil.
        
        Args:
            type: Type of element
            content: Content of the element
            layer: Layer to place the element on
            position: Optional position information
            size: Optional size information
            opacity: Opacity of the element
            visible: Whether the element is visible
            interactive: Whether the element is interactive
            priority: Priority of the element
            duration: Optional duration in milliseconds
            style: Optional style configuration
            metadata: Optional metadata
            element_id: Optional element ID, generated if not provided
            
        Returns:
            The element ID
        """
        # Generate element ID if not provided
        if element_id is None:
            element_id = str(uuid.uuid4())
            
        # Convert type to AmbientVeilElementType if needed
        if not isinstance(type, AmbientVeilElementType):
            try:
                type = AmbientVeilElementType(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid element type: {type}, using CUSTOM.")
                type = AmbientVeilElementType.CUSTOM
                
        # Convert layer to AmbientVeilLayer if needed
        if not isinstance(layer, AmbientVeilLayer):
            try:
                layer = AmbientVeilLayer(layer)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid layer: {layer}, using MIDGROUND.")
                layer = AmbientVeilLayer.MIDGROUND
                
        # Create element
        element = AmbientVeilElement(
            element_id=element_id,
            type=type,
            content=content,
            layer=layer,
            position=position or {"x": 0, "y": 0, "z": 0},
            size=size or {"width": 100, "height": 100},
            opacity=opacity,
            visible=visible,
            interactive=interactive,
            priority=priority,
            duration=duration,
            style=style or {},
            metadata=metadata or {}
        )
        
        # Calculate end time if duration is provided
        if duration is not None:
            element.end_time = element.start_time + duration / 1000
            
        # Add to elements
        self.elements[element_id] = element
        
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.ELEMENT_ADDED, {
            "element_id": element_id,
            "element": element.to_dict()
        })
        
        self.logger.debug(f"Added element: {element_id} ({type.value})")
        return element_id
    
    def remove_element(self, element_id: str) -> bool:
        """
        Remove an element from the ambient veil.
        
        Args:
            element_id: ID of the element to remove
            
        Returns:
            True if the element was removed, False if not found
        """
        if element_id not in self.elements:
            self.logger.warning(f"Element {element_id} not found.")
            return False
            
        element = self.elements[element_id]
        
        # Remove from elements
        del self.elements[element_id]
        
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.ELEMENT_REMOVED, {
            "element_id": element_id,
            "element": element.to_dict()
        })
        
        self.logger.debug(f"Removed element: {element_id} ({element.type.value})")
        return True
    
    def update_element(self,
                     element_id: str,
                     content: Any = None,
                     layer: Union[AmbientVeilLayer, str, None] = None,
                     position: Optional[Dict[str, Any]] = None,
                     size: Optional[Dict[str, Any]] = None,
                     opacity: Optional[float] = None,
                     visible: Optional[bool] = None,
                     interactive: Optional[bool] = None,
                     priority: Optional[int] = None,
                     duration: Optional[int] = None,
                     style: Optional[Dict[str, Any]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an element in the ambient veil.
        
        Args:
            element_id: ID of the element to update
            content: Optional new content
            layer: Optional new layer
            position: Optional new position
            size: Optional new size
            opacity: Optional new opacity
            visible: Optional new visibility
            interactive: Optional new interactivity
            priority: Optional new priority
            duration: Optional new duration
            style: Optional new style
            metadata: Optional new metadata
            
        Returns:
            True if the element was updated, False if not found
        """
        if element_id not in self.elements:
            self.logger.warning(f"Element {element_id} not found.")
            return False
            
        element = self.elements[element_id]
        
        # Update properties
        if content is not None:
            element.content = content
            
        if layer is not None:
            # Convert layer to AmbientVeilLayer if needed
            if not isinstance(layer, AmbientVeilLayer):
                try:
                    layer = AmbientVeilLayer(layer)
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid layer: {layer}, ignoring.")
                else:
                    element.layer = layer
            else:
                element.layer = layer
                
        if position is not None:
            element.position.update(position)
            
        if size is not None:
            element.size.update(size)
            
        if opacity is not None:
            element.opacity = opacity
            
        if visible is not None:
            element.visible = visible
            
        if interactive is not None:
            element.interactive = interactive
            
        if priority is not None:
            element.priority = priority
            
        if duration is not None:
            element.duration = duration
            element.end_time = time.time() + duration / 1000
            
        if style is not None:
            element.style.update(style)
            
        if metadata is not None:
            element.metadata.update(metadata)
            
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.ELEMENT_UPDATED, {
            "element_id": element_id,
            "element": element.to_dict()
        })
        
        self.logger.debug(f"Updated element: {element_id} ({element.type.value})")
        return True
    
    def get_element(self, element_id: str) -> Optional[AmbientVeilElement]:
        """
        Get an element from the ambient veil.
        
        Args:
            element_id: ID of the element to get
            
        Returns:
            The element, or None if not found
        """
        return self.elements.get(element_id)
    
    def get_elements(self, filter_func: Optional[Callable[[AmbientVeilElement], bool]] = None) -> List[AmbientVeilElement]:
        """
        Get elements from the ambient veil, optionally filtered.
        
        Args:
            filter_func: Optional filter function
            
        Returns:
            List of elements
        """
        if filter_func is None:
            return list(self.elements.values())
            
        return [element for element in self.elements.values() if filter_func(element)]
    
    def get_elements_by_type(self, type: Union[AmbientVeilElementType, str]) -> List[AmbientVeilElement]:
        """
        Get elements of a specific type.
        
        Args:
            type: Type of elements to get
            
        Returns:
            List of elements of the specified type
        """
        # Convert type to AmbientVeilElementType if needed
        if not isinstance(type, AmbientVeilElementType):
            try:
                type = AmbientVeilElementType(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid element type: {type}, using CUSTOM.")
                type = AmbientVeilElementType.CUSTOM
                
        return [element for element in self.elements.values() if element.type == type]
    
    def get_elements_by_layer(self, layer: Union[AmbientVeilLayer, str]) -> List[AmbientVeilElement]:
        """
        Get elements on a specific layer.
        
        Args:
            layer: Layer to get elements from
            
        Returns:
            List of elements on the specified layer
        """
        # Convert layer to AmbientVeilLayer if needed
        if not isinstance(layer, AmbientVeilLayer):
            try:
                layer = AmbientVeilLayer(layer)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid layer: {layer}, using MIDGROUND.")
                layer = AmbientVeilLayer.MIDGROUND
                
        return [element for element in self.elements.values() if element.layer == layer]
    
    def set_mode(self, mode: Union[AmbientVeilMode, str]) -> bool:
        """
        Set the ambient veil mode.
        
        Args:
            mode: New mode
            
        Returns:
            True if the mode was set, False if invalid
        """
        # Convert mode to AmbientVeilMode if needed
        if not isinstance(mode, AmbientVeilMode):
            try:
                mode = AmbientVeilMode(mode)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid mode: {mode}.")
                return False
                
        old_mode = self.mode
        self.mode = mode
        
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.MODE_CHANGED, {
            "old_mode": old_mode.value,
            "new_mode": mode.value
        })
        
        self.logger.debug(f"Set mode: {mode.value}")
        return True
    
    def show(self) -> bool:
        """
        Show the ambient veil.
        
        Returns:
            True if the visibility was changed, False if already visible
        """
        if self.is_visible:
            return False
            
        self.is_visible = True
        
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.VISIBILITY_CHANGED, {
            "visible": True
        })
        
        self.logger.debug("Ambient veil shown")
        return True
    
    def hide(self) -> bool:
        """
        Hide the ambient veil.
        
        Returns:
            True if the visibility was changed, False if already hidden
        """
        if not self.is_visible:
            return False
            
        self.is_visible = False
        
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.VISIBILITY_CHANGED, {
            "visible": False
        })
        
        self.logger.debug("Ambient veil hidden")
        return True
    
    def set_style(self, style: Dict[str, Any]) -> None:
        """
        Set the ambient veil style.
        
        Args:
            style: Style configuration
        """
        # Update style properties
        for key, value in style.items():
            if hasattr(self.style, key):
                setattr(self.style, key, value)
            else:
                self.style.custom_css[key] = value
                
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.CUSTOM, {
            "action": "style_updated",
            "style": {
                "background_color": self.style.background_color,
                "foreground_color": self.style.foreground_color,
                "accent_color": self.style.accent_color,
                "alert_color": self.style.alert_color,
                "success_color": self.style.success_color,
                "warning_color": self.style.warning_color,
                "info_color": self.style.info_color,
                "blur_radius": self.style.blur_radius,
                "opacity": self.style.opacity,
                "transition_duration": self.style.transition_duration,
                "animation_duration": self.style.animation_duration,
                "custom_css": self.style.custom_css
            }
        })
        
        self.logger.debug("Updated ambient veil style")
    
    def get_style(self) -> AmbientVeilStyle:
        """
        Get the ambient veil style.
        
        Returns:
            The ambient veil style
        """
        return self.style
    
    def add_event_listener(self, event_type: Union[AmbientVeilEventType, str], listener: Callable[[AmbientVeilEvent], None]) -> bool:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
            
        Returns:
            True if the listener was added, False if invalid event type
        """
        # Convert event_type to AmbientVeilEventType if needed
        if not isinstance(event_type, AmbientVeilEventType):
            try:
                event_type = AmbientVeilEventType(event_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid event type: {event_type}.")
                return False
                
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        return True
    
    def remove_event_listener(self, event_type: Union[AmbientVeilEventType, str], listener: Callable[[AmbientVeilEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        # Convert event_type to AmbientVeilEventType if needed
        if not isinstance(event_type, AmbientVeilEventType):
            try:
                event_type = AmbientVeilEventType(event_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid event type: {event_type}.")
                return False
                
        if event_type not in self.event_listeners:
            return False
            
        if listener in self.event_listeners[event_type]:
            self.event_listeners[event_type].remove(listener)
            return True
            
        return False
    
    def add_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.global_listeners.append(listener)
        
    def remove_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove a global listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.global_listeners:
            self.global_listeners.remove(listener)
            return True
            
        return False
    
    def handle_interaction(self, element_id: str, interaction_type: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle an interaction with an element.
        
        Args:
            element_id: ID of the element that was interacted with
            interaction_type: Type of interaction
            data: Optional interaction data
            
        Returns:
            True if the interaction was handled, False if element not found or not interactive
        """
        if element_id not in self.elements:
            self.logger.warning(f"Element {element_id} not found.")
            return False
            
        element = self.elements[element_id]
        
        if not element.interactive:
            self.logger.warning(f"Element {element_id} is not interactive.")
            return False
            
        # Dispatch event
        self._dispatch_event(AmbientVeilEventType.INTERACTION, {
            "element_id": element_id,
            "interaction_type": interaction_type,
            "data": data or {}
        })
        
        self.logger.debug(f"Handled interaction: {interaction_type} on element {element_id}")
        return True
    
    def add_indicator(self,
                    content: str,
                    color: Optional[str] = None,
                    position: Optional[Dict[str, Any]] = None,
                    size: Optional[Dict[str, Any]] = None,
                    duration: Optional[int] = None,
                    priority: int = 0,
                    metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an indicator to the ambient veil.
        
        Args:
            content: Content of the indicator
            color: Optional color
            position: Optional position
            size: Optional size
            duration: Optional duration in milliseconds
            priority: Priority of the indicator
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        style = {}
        if color is not None:
            style["color"] = color
            
        return self.add_element(
            type=AmbientVeilElementType.INDICATOR,
            content=content,
            layer=AmbientVeilLayer.FOREGROUND,
            position=position,
            size=size,
            opacity=0.9,
            visible=True,
            interactive=False,
            priority=priority,
            duration=duration,
            style=style,
            metadata=metadata
        )
    
    def add_notification(self,
                       title: str,
                       message: str,
                       type: str = "info",
                       position: Optional[Dict[str, Any]] = None,
                       duration: int = 5000,
                       priority: int = 1,
                       interactive: bool = True,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a notification to the ambient veil.
        
        Args:
            title: Title of the notification
            message: Message of the notification
            type: Type of notification (info, success, warning, error)
            position: Optional position
            duration: Duration in milliseconds
            priority: Priority of the notification
            interactive: Whether the notification is interactive
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        content = {
            "title": title,
            "message": message,
            "type": type
        }
        
        style = {}
        if type == "info":
            style["color"] = self.style.info_color
        elif type == "success":
            style["color"] = self.style.success_color
        elif type == "warning":
            style["color"] = self.style.warning_color
        elif type == "error":
            style["color"] = self.style.alert_color
            
        return self.add_element(
            type=AmbientVeilElementType.NOTIFICATION,
            content=content,
            layer=AmbientVeilLayer.OVERLAY,
            position=position,
            size={"width": 300, "height": 100},
            opacity=0.95,
            visible=True,
            interactive=interactive,
            priority=priority,
            duration=duration,
            style=style,
            metadata=metadata
        )
    
    def add_ambient_audio(self,
                        audio_url: str,
                        volume: float = 0.5,
                        loop: bool = True,
                        duration: Optional[int] = None,
                        priority: int = 0,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add ambient audio to the ambient veil.
        
        Args:
            audio_url: URL of the audio file
            volume: Volume of the audio
            loop: Whether to loop the audio
            duration: Optional duration in milliseconds
            priority: Priority of the audio
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        content = {
            "audio_url": audio_url,
            "volume": volume,
            "loop": loop
        }
        
        return self.add_element(
            type=AmbientVeilElementType.AMBIENT_AUDIO,
            content=content,
            layer=AmbientVeilLayer.BACKGROUND,
            opacity=volume,
            visible=True,
            interactive=False,
            priority=priority,
            duration=duration,
            metadata=metadata
        )
    
    def add_ambient_light(self,
                        color: str,
                        intensity: float = 0.5,
                        position: Optional[Dict[str, Any]] = None,
                        size: Optional[Dict[str, Any]] = None,
                        duration: Optional[int] = None,
                        priority: int = 0,
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add ambient light to the ambient veil.
        
        Args:
            color: Color of the light
            intensity: Intensity of the light
            position: Optional position
            size: Optional size
            duration: Optional duration in milliseconds
            priority: Priority of the light
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        content = {
            "color": color,
            "intensity": intensity
        }
        
        return self.add_element(
            type=AmbientVeilElementType.AMBIENT_LIGHT,
            content=content,
            layer=AmbientVeilLayer.BACKGROUND,
            position=position,
            size=size,
            opacity=intensity,
            visible=True,
            interactive=False,
            priority=priority,
            duration=duration,
            metadata=metadata
        )
    
    def add_particle_system(self,
                          particle_type: str,
                          count: int = 100,
                          color: Optional[str] = None,
                          speed: float = 1.0,
                          position: Optional[Dict[str, Any]] = None,
                          size: Optional[Dict[str, Any]] = None,
                          duration: Optional[int] = None,
                          priority: int = 0,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a particle system to the ambient veil.
        
        Args:
            particle_type: Type of particles
            count: Number of particles
            color: Optional color
            speed: Speed of particles
            position: Optional position
            size: Optional size
            duration: Optional duration in milliseconds
            priority: Priority of the particle system
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        content = {
            "particle_type": particle_type,
            "count": count,
            "color": color,
            "speed": speed
        }
        
        return self.add_element(
            type=AmbientVeilElementType.PARTICLE_SYSTEM,
            content=content,
            layer=AmbientVeilLayer.BACKGROUND,
            position=position,
            size=size,
            opacity=0.7,
            visible=True,
            interactive=False,
            priority=priority,
            duration=duration,
            metadata=metadata
        )
    
    def add_flow_field(self,
                     field_type: str,
                     intensity: float = 0.5,
                     color: Optional[str] = None,
                     position: Optional[Dict[str, Any]] = None,
                     size: Optional[Dict[str, Any]] = None,
                     duration: Optional[int] = None,
                     priority: int = 0,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a flow field to the ambient veil.
        
        Args:
            field_type: Type of flow field
            intensity: Intensity of the flow field
            color: Optional color
            position: Optional position
            size: Optional size
            duration: Optional duration in milliseconds
            priority: Priority of the flow field
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        content = {
            "field_type": field_type,
            "intensity": intensity,
            "color": color
        }
        
        return self.add_element(
            type=AmbientVeilElementType.FLOW_FIELD,
            content=content,
            layer=AmbientVeilLayer.BACKGROUND,
            position=position,
            size=size,
            opacity=intensity,
            visible=True,
            interactive=False,
            priority=priority,
            duration=duration,
            metadata=metadata
        )
    
    def add_ambient_text(self,
                       text: str,
                       color: Optional[str] = None,
                       font_size: int = 16,
                       position: Optional[Dict[str, Any]] = None,
                       duration: Optional[int] = None,
                       priority: int = 0,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add ambient text to the ambient veil.
        
        Args:
            text: Text content
            color: Optional color
            font_size: Font size
            position: Optional position
            duration: Optional duration in milliseconds
            priority: Priority of the text
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        style = {
            "font_size": f"{font_size}px"
        }
        
        if color is not None:
            style["color"] = color
            
        return self.add_element(
            type=AmbientVeilElementType.AMBIENT_TEXT,
            content=text,
            layer=AmbientVeilLayer.MIDGROUND,
            position=position,
            size={"width": len(text) * font_size * 0.6, "height": font_size * 1.2},
            opacity=0.8,
            visible=True,
            interactive=False,
            priority=priority,
            duration=duration,
            style=style,
            metadata=metadata
        )
    
    def add_ambient_icon(self,
                       icon_url: str,
                       position: Optional[Dict[str, Any]] = None,
                       size: Optional[Dict[str, Any]] = None,
                       opacity: float = 0.8,
                       duration: Optional[int] = None,
                       priority: int = 0,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an ambient icon to the ambient veil.
        
        Args:
            icon_url: URL of the icon
            position: Optional position
            size: Optional size
            opacity: Opacity of the icon
            duration: Optional duration in milliseconds
            priority: Priority of the icon
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        return self.add_element(
            type=AmbientVeilElementType.AMBIENT_ICON,
            content=icon_url,
            layer=AmbientVeilLayer.MIDGROUND,
            position=position,
            size=size or {"width": 32, "height": 32},
            opacity=opacity,
            visible=True,
            interactive=False,
            priority=priority,
            duration=duration,
            metadata=metadata
        )
    
    def add_ambient_avatar(self,
                         avatar_url: str,
                         name: str,
                         position: Optional[Dict[str, Any]] = None,
                         size: Optional[Dict[str, Any]] = None,
                         opacity: float = 0.8,
                         duration: Optional[int] = None,
                         priority: int = 0,
                         metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Add an ambient avatar to the ambient veil.
        
        Args:
            avatar_url: URL of the avatar
            name: Name of the avatar
            position: Optional position
            size: Optional size
            opacity: Opacity of the avatar
            duration: Optional duration in milliseconds
            priority: Priority of the avatar
            metadata: Optional metadata
            
        Returns:
            The element ID
        """
        content = {
            "avatar_url": avatar_url,
            "name": name
        }
        
        return self.add_element(
            type=AmbientVeilElementType.AMBIENT_AVATAR,
            content=content,
            layer=AmbientVeilLayer.FOREGROUND,
            position=position,
            size=size or {"width": 48, "height": 48},
            opacity=opacity,
            visible=True,
            interactive=True,
            priority=priority,
            duration=duration,
            metadata=metadata
        )
    
    def render(self) -> Dict[str, Any]:
        """
        Render the ambient veil for display.
        
        Returns:
            Rendered ambient veil data
        """
        # Clean up expired elements
        self._cleanup_expired_elements()
        
        # Get visible elements
        visible_elements = [element for element in self.elements.values() if element.visible]
        
        # Sort elements by layer and priority
        layer_order = {
            AmbientVeilLayer.BACKGROUND: 0,
            AmbientVeilLayer.MIDGROUND: 1,
            AmbientVeilLayer.FOREGROUND: 2,
            AmbientVeilLayer.OVERLAY: 3,
            AmbientVeilLayer.CUSTOM: 4
        }
        
        visible_elements.sort(key=lambda e: (layer_order[e.layer], -e.priority))
        
        # Convert elements to dictionaries
        elements_data = [element.to_dict() for element in visible_elements]
        
        # Build the ambient veil data
        veil_data = {
            "mode": self.mode.value,
            "visible": self.is_visible,
            "style": {
                "background_color": self.style.background_color,
                "foreground_color": self.style.foreground_color,
                "accent_color": self.style.accent_color,
                "alert_color": self.style.alert_color,
                "success_color": self.style.success_color,
                "warning_color": self.style.warning_color,
                "info_color": self.style.info_color,
                "blur_radius": self.style.blur_radius,
                "opacity": self.style.opacity,
                "transition_duration": self.style.transition_duration,
                "animation_duration": self.style.animation_duration,
                "custom_css": self.style.custom_css
            },
            "elements": elements_data
        }
        
        return veil_data
    
    def _dispatch_event(self, event_type: AmbientVeilEventType, data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Create event
        event = AmbientVeilEvent(
            event_type=event_type,
            source="AmbientVeilComponent",
            data=data
        )
        
        # Dispatch to event type listeners
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                try:
                    listener(event)
                except Exception as e:
                    self.logger.error(f"Error in event listener for {event_type.value}: {e}")
                    
        # Dispatch to global listeners
        for listener in self.global_listeners:
            try:
                listener(self._event_to_dict(event))
            except Exception as e:
                self.logger.error(f"Error in global listener: {e}")
    
    def _event_to_dict(self, event: AmbientVeilEvent) -> Dict[str, Any]:
        """
        Convert event to dictionary.
        
        Args:
            event: The event to convert
            
        Returns:
            Dictionary representation of the event
        """
        return {
            "event_type": event.event_type.value,
            "source": event.source,
            "data": event.data,
            "timestamp": event.timestamp
        }

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create ambient veil component
    veil = AmbientVeilComponent({
        "mode": "standard",
        "visible": True
    })
    
    # Start the component
    veil.start()
    
    # Add an event listener
    def on_element_added(event):
        print(f"Element added: {event.data['element_id']}")
        
    veil.add_event_listener(AmbientVeilEventType.ELEMENT_ADDED, on_element_added)
    
    # Add some elements
    veil.add_indicator(
        content="System Status: Normal",
        color="#4CAF50",
        position={"x": 20, "y": 20},
        priority=1
    )
    
    veil.add_notification(
        title="Process Complete",
        message="Manufacturing process has completed successfully.",
        type="success",
        duration=10000
    )
    
    veil.add_ambient_audio(
        audio_url="ambient_factory.mp3",
        volume=0.3,
        loop=True
    )
    
    veil.add_particle_system(
        particle_type="dust",
        count=50,
        color="#CCCCCC",
        speed=0.5
    )
    
    veil.add_ambient_text(
        text="Production efficiency: 94%",
        color="#2196F3",
        font_size=18,
        position={"x": 100, "y": 150}
    )
    
    # Render the ambient veil
    rendered = veil.render()
    print(f"Ambient veil has {len(rendered['elements'])} visible elements")
    
    # Stop the component
    veil.stop()
"""
