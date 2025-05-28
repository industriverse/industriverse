"""
Capsule Dock Component for the Industriverse UI/UX Layer.

This module provides a comprehensive capsule management interface that allows users to
interact with Agent Capsules in the Universal Skin environment. It serves as the primary
container and interaction point for Agent Capsules, providing docking, undocking, arrangement,
and management capabilities.

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

class CapsuleDockPosition(Enum):
    """Enumeration of capsule dock positions."""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    FLOATING = "floating"
    CUSTOM = "custom"

class CapsuleDockLayout(Enum):
    """Enumeration of capsule dock layouts."""
    LINEAR = "linear"
    GRID = "grid"
    RADIAL = "radial"
    STACK = "stack"
    FREEFORM = "freeform"
    CUSTOM = "custom"

class CapsuleDockMode(Enum):
    """Enumeration of capsule dock modes."""
    NORMAL = "normal"
    COMPACT = "compact"
    EXPANDED = "expanded"
    AMBIENT = "ambient"
    FOCUS = "focus"
    CUSTOM = "custom"

class CapsuleDockEventType(Enum):
    """Enumeration of capsule dock event types."""
    CAPSULE_ADDED = "capsule_added"
    CAPSULE_REMOVED = "capsule_removed"
    CAPSULE_SELECTED = "capsule_selected"
    CAPSULE_DESELECTED = "capsule_deselected"
    CAPSULE_MOVED = "capsule_moved"
    CAPSULE_RESIZED = "capsule_resized"
    CAPSULE_STATE_CHANGED = "capsule_state_changed"
    DOCK_POSITION_CHANGED = "dock_position_changed"
    DOCK_LAYOUT_CHANGED = "dock_layout_changed"
    DOCK_MODE_CHANGED = "dock_mode_changed"
    CUSTOM = "custom"

@dataclass
class CapsuleDockStyle:
    """Data class representing capsule dock styling options."""
    background_color: str = "rgba(20, 20, 20, 0.8)"
    border_color: str = "rgba(60, 60, 60, 0.8)"
    border_width: int = 1
    border_radius: int = 8
    padding: int = 8
    spacing: int = 4
    shadow: str = "0 4px 8px rgba(0, 0, 0, 0.2)"
    backdrop_filter: str = "blur(10px)"
    transition: str = "all 0.3s ease"
    custom_css: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CapsuleDockEvent:
    """Data class representing a capsule dock event."""
    event_type: CapsuleDockEventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class CapsuleDockComponent:
    """
    Provides a comprehensive capsule management interface for the Industriverse UI/UX Layer.
    
    This class provides:
    - Capsule docking and undocking
    - Capsule arrangement and organization
    - Capsule state management
    - Capsule interaction handling
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Capsule Dock Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.position = CapsuleDockPosition.BOTTOM
        self.layout = CapsuleDockLayout.LINEAR
        self.mode = CapsuleDockMode.NORMAL
        self.style = CapsuleDockStyle()
        self.capsules: Dict[str, Dict[str, Any]] = {}
        self.selected_capsules: Set[str] = set()
        self.event_listeners: Dict[CapsuleDockEventType, List[Callable[[CapsuleDockEvent], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize from config if provided
        if config:
            if "position" in config:
                try:
                    self.position = CapsuleDockPosition(config["position"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid position: {config['position']}, using default.")
                    
            if "layout" in config:
                try:
                    self.layout = CapsuleDockLayout(config["layout"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid layout: {config['layout']}, using default.")
                    
            if "mode" in config:
                try:
                    self.mode = CapsuleDockMode(config["mode"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid mode: {config['mode']}, using default.")
                    
            if "style" in config:
                for key, value in config["style"].items():
                    if hasattr(self.style, key):
                        setattr(self.style, key, value)
                    else:
                        self.style.custom_css[key] = value
        
    def start(self) -> bool:
        """
        Start the Capsule Dock Component.
        
        Returns:
            True if the component was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.CUSTOM, {
            "action": "component_started"
        })
        
        self.logger.info("Capsule Dock Component started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Capsule Dock Component.
        
        Returns:
            True if the component was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.CUSTOM, {
            "action": "component_stopped"
        })
        
        self.logger.info("Capsule Dock Component stopped.")
        return True
    
    def add_capsule(self, 
                  capsule_id: str, 
                  title: str, 
                  content: Optional[str] = None,
                  icon: Optional[str] = None,
                  avatar: Optional[str] = None,
                  state: Optional[Dict[str, Any]] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  style: Optional[Dict[str, Any]] = None,
                  position: Optional[Dict[str, int]] = None) -> bool:
        """
        Add a capsule to the dock.
        
        Args:
            capsule_id: Unique identifier for the capsule
            title: Title of the capsule
            content: Optional content/description of the capsule
            icon: Optional icon URL or data URI
            avatar: Optional avatar URL or data URI
            state: Optional state information
            metadata: Optional metadata
            style: Optional style configuration
            position: Optional position information (x, y coordinates)
            
        Returns:
            True if the capsule was added, False if already exists
        """
        if capsule_id in self.capsules:
            self.logger.warning(f"Capsule {capsule_id} already exists.")
            return False
            
        # Create capsule
        capsule = {
            "id": capsule_id,
            "title": title,
            "content": content,
            "icon": icon,
            "avatar": avatar,
            "state": state or {},
            "metadata": metadata or {},
            "style": style or {},
            "position": position or {"x": 0, "y": 0},
            "added_at": time.time()
        }
        
        # Add to capsules
        self.capsules[capsule_id] = capsule
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.CAPSULE_ADDED, {
            "capsule_id": capsule_id,
            "capsule": capsule
        })
        
        self.logger.debug(f"Added capsule: {capsule_id} ({title})")
        return True
    
    def remove_capsule(self, capsule_id: str) -> bool:
        """
        Remove a capsule from the dock.
        
        Args:
            capsule_id: ID of the capsule to remove
            
        Returns:
            True if the capsule was removed, False if not found
        """
        if capsule_id not in self.capsules:
            self.logger.warning(f"Capsule {capsule_id} not found.")
            return False
            
        capsule = self.capsules[capsule_id]
        
        # Remove from capsules
        del self.capsules[capsule_id]
        
        # Remove from selected capsules
        if capsule_id in self.selected_capsules:
            self.selected_capsules.remove(capsule_id)
            
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.CAPSULE_REMOVED, {
            "capsule_id": capsule_id,
            "capsule": capsule
        })
        
        self.logger.debug(f"Removed capsule: {capsule_id} ({capsule['title']})")
        return True
    
    def update_capsule(self,
                     capsule_id: str,
                     title: Optional[str] = None,
                     content: Optional[str] = None,
                     icon: Optional[str] = None,
                     avatar: Optional[str] = None,
                     state: Optional[Dict[str, Any]] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     style: Optional[Dict[str, Any]] = None,
                     position: Optional[Dict[str, int]] = None) -> bool:
        """
        Update a capsule in the dock.
        
        Args:
            capsule_id: ID of the capsule to update
            title: Optional new title
            content: Optional new content
            icon: Optional new icon
            avatar: Optional new avatar
            state: Optional new state
            metadata: Optional new metadata
            style: Optional new style
            position: Optional new position
            
        Returns:
            True if the capsule was updated, False if not found
        """
        if capsule_id not in self.capsules:
            self.logger.warning(f"Capsule {capsule_id} not found.")
            return False
            
        capsule = self.capsules[capsule_id]
        
        # Update properties
        if title is not None:
            capsule["title"] = title
            
        if content is not None:
            capsule["content"] = content
            
        if icon is not None:
            capsule["icon"] = icon
            
        if avatar is not None:
            capsule["avatar"] = avatar
            
        if state is not None:
            old_state = capsule["state"].copy()
            capsule["state"].update(state)
            
            # Dispatch state changed event
            self._dispatch_event(CapsuleDockEventType.CAPSULE_STATE_CHANGED, {
                "capsule_id": capsule_id,
                "old_state": old_state,
                "new_state": capsule["state"]
            })
            
        if metadata is not None:
            capsule["metadata"].update(metadata)
            
        if style is not None:
            capsule["style"].update(style)
            
        if position is not None:
            old_position = capsule["position"].copy()
            capsule["position"].update(position)
            
            # Dispatch moved event
            self._dispatch_event(CapsuleDockEventType.CAPSULE_MOVED, {
                "capsule_id": capsule_id,
                "old_position": old_position,
                "new_position": capsule["position"]
            })
            
        self.logger.debug(f"Updated capsule: {capsule_id} ({capsule['title']})")
        return True
    
    def get_capsule(self, capsule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a capsule from the dock.
        
        Args:
            capsule_id: ID of the capsule to get
            
        Returns:
            The capsule, or None if not found
        """
        return self.capsules.get(capsule_id)
    
    def get_capsules(self) -> List[Dict[str, Any]]:
        """
        Get all capsules in the dock.
        
        Returns:
            List of capsules
        """
        return list(self.capsules.values())
    
    def select_capsule(self, capsule_id: str) -> bool:
        """
        Select a capsule.
        
        Args:
            capsule_id: ID of the capsule to select
            
        Returns:
            True if the capsule was selected, False if not found
        """
        if capsule_id not in self.capsules:
            self.logger.warning(f"Capsule {capsule_id} not found.")
            return False
            
        # Add to selected capsules
        self.selected_capsules.add(capsule_id)
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.CAPSULE_SELECTED, {
            "capsule_id": capsule_id,
            "selected_capsules": list(self.selected_capsules)
        })
        
        self.logger.debug(f"Selected capsule: {capsule_id}")
        return True
    
    def deselect_capsule(self, capsule_id: str) -> bool:
        """
        Deselect a capsule.
        
        Args:
            capsule_id: ID of the capsule to deselect
            
        Returns:
            True if the capsule was deselected, False if not found or not selected
        """
        if capsule_id not in self.capsules:
            self.logger.warning(f"Capsule {capsule_id} not found.")
            return False
            
        if capsule_id not in self.selected_capsules:
            return False
            
        # Remove from selected capsules
        self.selected_capsules.remove(capsule_id)
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.CAPSULE_DESELECTED, {
            "capsule_id": capsule_id,
            "selected_capsules": list(self.selected_capsules)
        })
        
        self.logger.debug(f"Deselected capsule: {capsule_id}")
        return True
    
    def clear_selection(self) -> None:
        """Clear all selected capsules."""
        if not self.selected_capsules:
            return
            
        deselected = list(self.selected_capsules)
        self.selected_capsules.clear()
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.CUSTOM, {
            "action": "selection_cleared",
            "capsule_ids": deselected,
            "selected_capsules": []
        })
        
        self.logger.debug("Cleared selection")
    
    def get_selected_capsules(self) -> List[Dict[str, Any]]:
        """
        Get selected capsules.
        
        Returns:
            List of selected capsules
        """
        return [self.capsules[capsule_id] for capsule_id in self.selected_capsules if capsule_id in self.capsules]
    
    def is_capsule_selected(self, capsule_id: str) -> bool:
        """
        Check if a capsule is selected.
        
        Args:
            capsule_id: ID of the capsule to check
            
        Returns:
            True if the capsule is selected, False otherwise
        """
        return capsule_id in self.selected_capsules
    
    def set_position(self, position: Union[CapsuleDockPosition, str]) -> bool:
        """
        Set the dock position.
        
        Args:
            position: New position
            
        Returns:
            True if the position was set, False if invalid
        """
        # Convert position to CapsuleDockPosition if needed
        if not isinstance(position, CapsuleDockPosition):
            try:
                position = CapsuleDockPosition(position)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid position: {position}.")
                return False
                
        old_position = self.position
        self.position = position
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.DOCK_POSITION_CHANGED, {
            "old_position": old_position.value,
            "new_position": position.value
        })
        
        self.logger.debug(f"Set position: {position.value}")
        return True
    
    def set_layout(self, layout: Union[CapsuleDockLayout, str]) -> bool:
        """
        Set the dock layout.
        
        Args:
            layout: New layout
            
        Returns:
            True if the layout was set, False if invalid
        """
        # Convert layout to CapsuleDockLayout if needed
        if not isinstance(layout, CapsuleDockLayout):
            try:
                layout = CapsuleDockLayout(layout)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid layout: {layout}.")
                return False
                
        old_layout = self.layout
        self.layout = layout
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.DOCK_LAYOUT_CHANGED, {
            "old_layout": old_layout.value,
            "new_layout": layout.value
        })
        
        self.logger.debug(f"Set layout: {layout.value}")
        return True
    
    def set_mode(self, mode: Union[CapsuleDockMode, str]) -> bool:
        """
        Set the dock mode.
        
        Args:
            mode: New mode
            
        Returns:
            True if the mode was set, False if invalid
        """
        # Convert mode to CapsuleDockMode if needed
        if not isinstance(mode, CapsuleDockMode):
            try:
                mode = CapsuleDockMode(mode)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid mode: {mode}.")
                return False
                
        old_mode = self.mode
        self.mode = mode
        
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.DOCK_MODE_CHANGED, {
            "old_mode": old_mode.value,
            "new_mode": mode.value
        })
        
        self.logger.debug(f"Set mode: {mode.value}")
        return True
    
    def set_style(self, style: Dict[str, Any]) -> None:
        """
        Set the dock style.
        
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
        self._dispatch_event(CapsuleDockEventType.CUSTOM, {
            "action": "style_updated",
            "style": {
                "background_color": self.style.background_color,
                "border_color": self.style.border_color,
                "border_width": self.style.border_width,
                "border_radius": self.style.border_radius,
                "padding": self.style.padding,
                "spacing": self.style.spacing,
                "shadow": self.style.shadow,
                "backdrop_filter": self.style.backdrop_filter,
                "transition": self.style.transition,
                "custom_css": self.style.custom_css
            }
        })
        
        self.logger.debug("Updated dock style")
    
    def get_style(self) -> CapsuleDockStyle:
        """
        Get the dock style.
        
        Returns:
            The dock style
        """
        return self.style
    
    def add_event_listener(self, event_type: Union[CapsuleDockEventType, str], listener: Callable[[CapsuleDockEvent], None]) -> bool:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
            
        Returns:
            True if the listener was added, False if invalid event type
        """
        # Convert event_type to CapsuleDockEventType if needed
        if not isinstance(event_type, CapsuleDockEventType):
            try:
                event_type = CapsuleDockEventType(event_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid event type: {event_type}.")
                return False
                
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        return True
    
    def remove_event_listener(self, event_type: Union[CapsuleDockEventType, str], listener: Callable[[CapsuleDockEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        # Convert event_type to CapsuleDockEventType if needed
        if not isinstance(event_type, CapsuleDockEventType):
            try:
                event_type = CapsuleDockEventType(event_type)
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
    
    def arrange_capsules(self, layout: Optional[Union[CapsuleDockLayout, str]] = None) -> bool:
        """
        Arrange capsules according to the specified layout.
        
        Args:
            layout: Optional layout to use, defaults to current layout
            
        Returns:
            True if the capsules were arranged, False if invalid layout
        """
        # Use current layout if not specified
        if layout is None:
            layout = self.layout
        else:
            # Convert layout to CapsuleDockLayout if needed
            if not isinstance(layout, CapsuleDockLayout):
                try:
                    layout = CapsuleDockLayout(layout)
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid layout: {layout}.")
                    return False
        
        # Arrange capsules based on layout
        if layout == CapsuleDockLayout.LINEAR:
            self._arrange_linear()
        elif layout == CapsuleDockLayout.GRID:
            self._arrange_grid()
        elif layout == CapsuleDockLayout.RADIAL:
            self._arrange_radial()
        elif layout == CapsuleDockLayout.STACK:
            self._arrange_stack()
        elif layout == CapsuleDockLayout.FREEFORM:
            # Freeform layout doesn't rearrange capsules
            pass
        elif layout == CapsuleDockLayout.CUSTOM:
            # Custom layout would be implemented here
            pass
            
        # Dispatch event
        self._dispatch_event(CapsuleDockEventType.CUSTOM, {
            "action": "capsules_arranged",
            "layout": layout.value
        })
        
        self.logger.debug(f"Arranged capsules using {layout.value} layout")
        return True
    
    def _arrange_linear(self) -> None:
        """Arrange capsules in a linear layout."""
        capsules = list(self.capsules.values())
        
        # Sort capsules by added_at time
        capsules.sort(key=lambda c: c["added_at"])
        
        # Calculate positions
        spacing = self.style.spacing
        
        for i, capsule in enumerate(capsules):
            if self.position in [CapsuleDockPosition.TOP, CapsuleDockPosition.BOTTOM]:
                # Horizontal arrangement
                capsule["position"] = {"x": i * (100 + spacing), "y": 0}
            else:
                # Vertical arrangement
                capsule["position"] = {"x": 0, "y": i * (100 + spacing)}
    
    def _arrange_grid(self) -> None:
        """Arrange capsules in a grid layout."""
        capsules = list(self.capsules.values())
        
        # Sort capsules by added_at time
        capsules.sort(key=lambda c: c["added_at"])
        
        # Calculate positions
        spacing = self.style.spacing
        cols = 3  # Number of columns in the grid
        
        for i, capsule in enumerate(capsules):
            row = i // cols
            col = i % cols
            
            capsule["position"] = {
                "x": col * (100 + spacing),
                "y": row * (100 + spacing)
            }
    
    def _arrange_radial(self) -> None:
        """Arrange capsules in a radial layout."""
        import math
        
        capsules = list(self.capsules.values())
        
        # Sort capsules by added_at time
        capsules.sort(key=lambda c: c["added_at"])
        
        # Calculate positions
        num_capsules = len(capsules)
        
        if num_capsules == 0:
            return
            
        radius = 150  # Radius of the circle
        center_x = 0
        center_y = 0
        
        for i, capsule in enumerate(capsules):
            angle = 2 * math.pi * i / num_capsules
            
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            capsule["position"] = {"x": int(x), "y": int(y)}
    
    def _arrange_stack(self) -> None:
        """Arrange capsules in a stack layout."""
        capsules = list(self.capsules.values())
        
        # Sort capsules by added_at time
        capsules.sort(key=lambda c: c["added_at"])
        
        # Calculate positions
        offset = 5  # Offset between stacked capsules
        
        for i, capsule in enumerate(capsules):
            capsule["position"] = {"x": i * offset, "y": i * offset}
    
    def render(self) -> Dict[str, Any]:
        """
        Render the capsule dock for display.
        
        Returns:
            Rendered dock data
        """
        # Convert capsules to list
        capsules_data = list(self.capsules.values())
        
        # Build the dock data
        dock_data = {
            "position": self.position.value,
            "layout": self.layout.value,
            "mode": self.mode.value,
            "style": {
                "background_color": self.style.background_color,
                "border_color": self.style.border_color,
                "border_width": self.style.border_width,
                "border_radius": self.style.border_radius,
                "padding": self.style.padding,
                "spacing": self.style.spacing,
                "shadow": self.style.shadow,
                "backdrop_filter": self.style.backdrop_filter,
                "transition": self.style.transition,
                "custom_css": self.style.custom_css
            },
            "capsules": capsules_data,
            "selected_capsules": list(self.selected_capsules)
        }
        
        return dock_data
    
    def _dispatch_event(self, event_type: CapsuleDockEventType, data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Create event
        event = CapsuleDockEvent(
            event_type=event_type,
            source="CapsuleDockComponent",
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
    
    def _event_to_dict(self, event: CapsuleDockEvent) -> Dict[str, Any]:
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
    
    # Create capsule dock component
    dock = CapsuleDockComponent({
        "position": "bottom",
        "layout": "linear",
        "mode": "normal"
    })
    
    # Start the component
    dock.start()
    
    # Add an event listener
    def on_capsule_added(event):
        print(f"Capsule added: {event.data['capsule_id']}")
        
    dock.add_event_listener(CapsuleDockEventType.CAPSULE_ADDED, on_capsule_added)
    
    # Add some capsules
    dock.add_capsule(
        capsule_id="agent1",
        title="Manufacturing Agent",
        content="Monitors and optimizes manufacturing processes",
        icon="manufacturing_icon.png",
        avatar="manufacturing_avatar.png",
        state={"status": "active", "task_count": 3},
        metadata={"type": "manufacturing", "priority": "high"}
    )
    
    dock.add_capsule(
        capsule_id="agent2",
        title="Logistics Agent",
        content="Manages supply chain and logistics operations",
        icon="logistics_icon.png",
        avatar="logistics_avatar.png",
        state={"status": "idle", "task_count": 0},
        metadata={"type": "logistics", "priority": "medium"}
    )
    
    dock.add_capsule(
        capsule_id="agent3",
        title="Quality Control Agent",
        content="Monitors product quality and compliance",
        icon="quality_icon.png",
        avatar="quality_avatar.png",
        state={"status": "active", "task_count": 2},
        metadata={"type": "quality", "priority": "high"}
    )
    
    # Arrange capsules
    dock.arrange_capsules(CapsuleDockLayout.GRID)
    
    # Select a capsule
    dock.select_capsule("agent1")
    
    # Render the dock
    rendered = dock.render()
    print(f"Dock has {len(rendered['capsules'])} capsules")
    
    # Stop the component
    dock.stop()
"""
