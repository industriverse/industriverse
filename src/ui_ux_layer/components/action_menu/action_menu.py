"""
Action Menu Component for the Industriverse UI/UX Layer.

This module provides a contextual action menu that displays relevant
actions based on the current user context, industrial environment,
and system state.

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

class ActionMenuMode(Enum):
    """Enumeration of action menu modes."""
    COMPACT = "compact"
    STANDARD = "standard"
    EXPANDED = "expanded"
    RADIAL = "radial"
    CONTEXTUAL = "contextual"
    CUSTOM = "custom"

class ActionMenuPosition(Enum):
    """Enumeration of action menu positions."""
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_RIGHT = "bottom_right"
    CENTER = "center"
    FLOATING = "floating"
    CUSTOM = "custom"

class ActionMenuEventType(Enum):
    """Enumeration of action menu event types."""
    ACTION_ADDED = "action_added"
    ACTION_REMOVED = "action_removed"
    ACTION_UPDATED = "action_updated"
    ACTION_EXECUTED = "action_executed"
    MODE_CHANGED = "mode_changed"
    POSITION_CHANGED = "position_changed"
    VISIBILITY_CHANGED = "visibility_changed"
    CONTEXT_CHANGED = "context_changed"
    CUSTOM = "custom"

@dataclass
class ActionMenuStyle:
    """Data class representing action menu styling options."""
    background_color: str = "#FFFFFF"
    text_color: str = "#333333"
    accent_color: str = "#4285F4"
    border_color: str = "#E0E0E0"
    border_radius: int = 8
    shadow: str = "0 2px 10px rgba(0, 0, 0, 0.1)"
    font_family: str = "Roboto, sans-serif"
    icon_size: int = 24
    button_size: int = 40
    padding: int = 8
    margin: int = 4
    animation_duration: int = 200
    custom_css: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ActionMenuEvent:
    """Data class representing an action menu event."""
    event_type: ActionMenuEventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class ActionMenuItem:
    """Data class representing an action menu item."""
    action_id: str
    label: str
    icon: str
    handler: Callable[[Dict[str, Any]], Any]
    enabled: bool = True
    visible: bool = True
    order: int = 0
    group: Optional[str] = None
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the action item to a dictionary."""
        return {
            "id": self.action_id,
            "label": self.label,
            "icon": self.icon,
            "enabled": self.enabled,
            "visible": self.visible,
            "order": self.order,
            "group": self.group,
            "style": self.style,
            "metadata": self.metadata
        }

class ActionMenuComponent:
    """
    Provides a contextual action menu for the Industriverse UI/UX Layer.
    
    This class provides:
    - Context-aware action display
    - Multiple menu modes (compact, standard, expanded, radial, contextual)
    - Multiple position options
    - Action grouping and ordering
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Action Menu Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_visible = True
        self.mode = ActionMenuMode.STANDARD
        self.position = ActionMenuPosition.BOTTOM
        self.style = ActionMenuStyle()
        self.actions: Dict[str, ActionMenuItem] = {}
        self.groups: Dict[str, Dict[str, Any]] = {}
        self.current_context: Dict[str, Any] = {}
        self.event_listeners: Dict[ActionMenuEventType, List[Callable[[ActionMenuEvent], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize from config if provided
        if config:
            if "mode" in config:
                try:
                    self.mode = ActionMenuMode(config["mode"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid mode: {config['mode']}, using default.")
                    
            if "position" in config:
                try:
                    self.position = ActionMenuPosition(config["position"])
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid position: {config['position']}, using default.")
                    
            if "visible" in config:
                self.is_visible = bool(config["visible"])
                
            if "style" in config:
                for key, value in config["style"].items():
                    if hasattr(self.style, key):
                        setattr(self.style, key, value)
                    else:
                        self.style.custom_css[key] = value
                        
            if "groups" in config:
                for group_id, group_config in config["groups"].items():
                    self.add_group(
                        group_id=group_id,
                        title=group_config.get("title", group_id),
                        order=group_config.get("order", 0),
                        expanded=group_config.get("expanded", True),
                        style=group_config.get("style", {})
                    )
                    
            if "actions" in config:
                for action_config in config["actions"]:
                    if "id" not in action_config or "label" not in action_config or "icon" not in action_config:
                        self.logger.warning(f"Invalid action configuration: {action_config}")
                        continue
                        
                    # Create a dummy handler if not provided
                    handler = action_config.get("handler", lambda data: None)
                    
                    self.add_action(
                        label=action_config["label"],
                        icon=action_config["icon"],
                        handler=handler,
                        enabled=action_config.get("enabled", True),
                        visible=action_config.get("visible", True),
                        order=action_config.get("order", 0),
                        group=action_config.get("group"),
                        style=action_config.get("style", {}),
                        metadata=action_config.get("metadata", {}),
                        action_id=action_config["id"]
                    )
                    
            if "context" in config:
                self.set_context(config["context"])
        
    def add_action(self,
                 label: str,
                 icon: str,
                 handler: Callable[[Dict[str, Any]], Any],
                 enabled: bool = True,
                 visible: bool = True,
                 order: int = 0,
                 group: Optional[str] = None,
                 style: Optional[Dict[str, Any]] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 action_id: Optional[str] = None) -> str:
        """
        Add an action to the menu.
        
        Args:
            label: Label of the action
            icon: Icon of the action
            handler: Function to call when the action is executed
            enabled: Whether the action is enabled
            visible: Whether the action is visible
            order: Order of the action
            group: Optional group ID
            style: Optional style configuration
            metadata: Optional metadata
            action_id: Optional action ID, generated if not provided
            
        Returns:
            The action ID
        """
        # Generate action ID if not provided
        if action_id is None:
            action_id = str(uuid.uuid4())
            
        # Create action
        action = ActionMenuItem(
            action_id=action_id,
            label=label,
            icon=icon,
            handler=handler,
            enabled=enabled,
            visible=visible,
            order=order,
            group=group,
            style=style or {},
            metadata=metadata or {}
        )
        
        # Add to actions
        self.actions[action_id] = action
        
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.ACTION_ADDED, {
            "action_id": action_id,
            "action": action.to_dict()
        })
        
        self.logger.debug(f"Added action: {action_id} ({label})")
        return action_id
    
    def remove_action(self, action_id: str) -> bool:
        """
        Remove an action from the menu.
        
        Args:
            action_id: ID of the action to remove
            
        Returns:
            True if the action was removed, False if not found
        """
        if action_id not in self.actions:
            self.logger.warning(f"Action {action_id} not found.")
            return False
            
        action = self.actions[action_id]
        
        # Remove from actions
        del self.actions[action_id]
        
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.ACTION_REMOVED, {
            "action_id": action_id,
            "action": action.to_dict()
        })
        
        self.logger.debug(f"Removed action: {action_id} ({action.label})")
        return True
    
    def update_action(self,
                    action_id: str,
                    label: Optional[str] = None,
                    icon: Optional[str] = None,
                    handler: Optional[Callable[[Dict[str, Any]], Any]] = None,
                    enabled: Optional[bool] = None,
                    visible: Optional[bool] = None,
                    order: Optional[int] = None,
                    group: Optional[str] = None,
                    style: Optional[Dict[str, Any]] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an action in the menu.
        
        Args:
            action_id: ID of the action to update
            label: Optional new label
            icon: Optional new icon
            handler: Optional new handler
            enabled: Optional new enabled state
            visible: Optional new visibility
            order: Optional new order
            group: Optional new group
            style: Optional new style
            metadata: Optional new metadata
            
        Returns:
            True if the action was updated, False if not found
        """
        if action_id not in self.actions:
            self.logger.warning(f"Action {action_id} not found.")
            return False
            
        action = self.actions[action_id]
        
        # Update properties
        if label is not None:
            action.label = label
            
        if icon is not None:
            action.icon = icon
            
        if handler is not None:
            action.handler = handler
            
        if enabled is not None:
            action.enabled = enabled
            
        if visible is not None:
            action.visible = visible
            
        if order is not None:
            action.order = order
            
        if group is not None:
            action.group = group
            
        if style is not None:
            action.style.update(style)
            
        if metadata is not None:
            action.metadata.update(metadata)
            
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.ACTION_UPDATED, {
            "action_id": action_id,
            "action": action.to_dict()
        })
        
        self.logger.debug(f"Updated action: {action_id} ({action.label})")
        return True
    
    def get_action(self, action_id: str) -> Optional[ActionMenuItem]:
        """
        Get an action from the menu.
        
        Args:
            action_id: ID of the action to get
            
        Returns:
            The action, or None if not found
        """
        return self.actions.get(action_id)
    
    def get_actions(self, filter_func: Optional[Callable[[ActionMenuItem], bool]] = None) -> List[ActionMenuItem]:
        """
        Get actions from the menu, optionally filtered.
        
        Args:
            filter_func: Optional filter function
            
        Returns:
            List of actions
        """
        if filter_func is None:
            return list(self.actions.values())
            
        return [action for action in self.actions.values() if filter_func(action)]
    
    def get_actions_by_group(self, group: Optional[str]) -> List[ActionMenuItem]:
        """
        Get actions in a specific group.
        
        Args:
            group: Group ID, or None for ungrouped actions
            
        Returns:
            List of actions in the group
        """
        return [action for action in self.actions.values() if action.group == group]
    
    def execute_action(self, action_id: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute an action.
        
        Args:
            action_id: ID of the action to execute
            data: Optional data to pass to the action handler
            
        Returns:
            Result of the action handler
        
        Raises:
            ValueError: If the action is not found or disabled
        """
        if action_id not in self.actions:
            raise ValueError(f"Action {action_id} not found.")
            
        action = self.actions[action_id]
        
        if not action.enabled:
            raise ValueError(f"Action {action_id} is disabled.")
            
        # Prepare data
        execution_data = {
            "action_id": action_id,
            "context": self.current_context,
            "timestamp": time.time()
        }
        
        if data:
            execution_data.update(data)
            
        # Execute handler
        try:
            result = action.handler(execution_data)
            
            # Dispatch event
            self._dispatch_event(ActionMenuEventType.ACTION_EXECUTED, {
                "action_id": action_id,
                "data": execution_data,
                "result": result
            })
            
            self.logger.debug(f"Executed action: {action_id} ({action.label})")
            return result
        except Exception as e:
            self.logger.error(f"Error executing action {action_id}: {e}")
            raise
    
    def add_group(self,
                group_id: str,
                title: str,
                order: int = 0,
                expanded: bool = True,
                style: Optional[Dict[str, Any]] = None) -> str:
        """
        Add a group to the menu.
        
        Args:
            group_id: ID of the group
            title: Title of the group
            order: Order of the group
            expanded: Whether the group is expanded
            style: Optional style configuration
            
        Returns:
            The group ID
        """
        self.groups[group_id] = {
            "id": group_id,
            "title": title,
            "order": order,
            "expanded": expanded,
            "style": style or {}
        }
        
        self.logger.debug(f"Added group: {group_id} ({title})")
        return group_id
    
    def remove_group(self, group_id: str) -> bool:
        """
        Remove a group from the menu.
        
        Args:
            group_id: ID of the group to remove
            
        Returns:
            True if the group was removed, False if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        # Remove group
        del self.groups[group_id]
        
        # Update actions in the group
        for action in self.actions.values():
            if action.group == group_id:
                action.group = None
                
        self.logger.debug(f"Removed group: {group_id}")
        return True
    
    def update_group(self,
                   group_id: str,
                   title: Optional[str] = None,
                   order: Optional[int] = None,
                   expanded: Optional[bool] = None,
                   style: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a group in the menu.
        
        Args:
            group_id: ID of the group to update
            title: Optional new title
            order: Optional new order
            expanded: Optional new expanded state
            style: Optional new style
            
        Returns:
            True if the group was updated, False if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Update properties
        if title is not None:
            group["title"] = title
            
        if order is not None:
            group["order"] = order
            
        if expanded is not None:
            group["expanded"] = expanded
            
        if style is not None:
            group["style"].update(style)
            
        self.logger.debug(f"Updated group: {group_id}")
        return True
    
    def get_group(self, group_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a group from the menu.
        
        Args:
            group_id: ID of the group to get
            
        Returns:
            The group, or None if not found
        """
        return self.groups.get(group_id)
    
    def get_groups(self) -> List[Dict[str, Any]]:
        """
        Get all groups from the menu.
        
        Returns:
            List of groups
        """
        return list(self.groups.values())
    
    def set_mode(self, mode: Union[ActionMenuMode, str]) -> bool:
        """
        Set the menu mode.
        
        Args:
            mode: New mode
            
        Returns:
            True if the mode was set, False if invalid
        """
        # Convert mode to ActionMenuMode if needed
        if not isinstance(mode, ActionMenuMode):
            try:
                mode = ActionMenuMode(mode)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid mode: {mode}.")
                return False
                
        old_mode = self.mode
        self.mode = mode
        
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.MODE_CHANGED, {
            "old_mode": old_mode.value,
            "new_mode": mode.value
        })
        
        self.logger.debug(f"Set mode: {mode.value}")
        return True
    
    def set_position(self, position: Union[ActionMenuPosition, str]) -> bool:
        """
        Set the menu position.
        
        Args:
            position: New position
            
        Returns:
            True if the position was set, False if invalid
        """
        # Convert position to ActionMenuPosition if needed
        if not isinstance(position, ActionMenuPosition):
            try:
                position = ActionMenuPosition(position)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid position: {position}.")
                return False
                
        old_position = self.position
        self.position = position
        
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.POSITION_CHANGED, {
            "old_position": old_position.value,
            "new_position": position.value
        })
        
        self.logger.debug(f"Set position: {position.value}")
        return True
    
    def show(self) -> bool:
        """
        Show the menu.
        
        Returns:
            True if the visibility was changed, False if already visible
        """
        if self.is_visible:
            return False
            
        self.is_visible = True
        
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.VISIBILITY_CHANGED, {
            "visible": True
        })
        
        self.logger.debug("Menu shown")
        return True
    
    def hide(self) -> bool:
        """
        Hide the menu.
        
        Returns:
            True if the visibility was changed, False if already hidden
        """
        if not self.is_visible:
            return False
            
        self.is_visible = False
        
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.VISIBILITY_CHANGED, {
            "visible": False
        })
        
        self.logger.debug("Menu hidden")
        return True
    
    def set_style(self, style: Dict[str, Any]) -> None:
        """
        Set the menu style.
        
        Args:
            style: Style configuration
        """
        # Update style properties
        for key, value in style.items():
            if hasattr(self.style, key):
                setattr(self.style, key, value)
            else:
                self.style.custom_css[key] = value
                
        self.logger.debug("Updated menu style")
    
    def get_style(self) -> ActionMenuStyle:
        """
        Get the menu style.
        
        Returns:
            The menu style
        """
        return self.style
    
    def set_context(self, context: Dict[str, Any]) -> None:
        """
        Set the current context.
        
        Args:
            context: Context data
        """
        old_context = self.current_context.copy()
        self.current_context = context
        
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.CONTEXT_CHANGED, {
            "old_context": old_context,
            "new_context": context
        })
        
        self.logger.debug("Updated context")
    
    def get_context(self) -> Dict[str, Any]:
        """
        Get the current context.
        
        Returns:
            The current context
        """
        return self.current_context
    
    def update_context(self, context_updates: Dict[str, Any]) -> None:
        """
        Update the current context.
        
        Args:
            context_updates: Context updates
        """
        old_context = self.current_context.copy()
        self.current_context.update(context_updates)
        
        # Dispatch event
        self._dispatch_event(ActionMenuEventType.CONTEXT_CHANGED, {
            "old_context": old_context,
            "new_context": self.current_context,
            "updates": context_updates
        })
        
        self.logger.debug("Updated context")
    
    def add_event_listener(self, event_type: Union[ActionMenuEventType, str], listener: Callable[[ActionMenuEvent], None]) -> bool:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
            
        Returns:
            True if the listener was added, False if invalid event type
        """
        # Convert event_type to ActionMenuEventType if needed
        if not isinstance(event_type, ActionMenuEventType):
            try:
                event_type = ActionMenuEventType(event_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid event type: {event_type}.")
                return False
                
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        return True
    
    def remove_event_listener(self, event_type: Union[ActionMenuEventType, str], listener: Callable[[ActionMenuEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        # Convert event_type to ActionMenuEventType if needed
        if not isinstance(event_type, ActionMenuEventType):
            try:
                event_type = ActionMenuEventType(event_type)
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
    
    def render(self) -> Dict[str, Any]:
        """
        Render the menu for display.
        
        Returns:
            Rendered menu data
        """
        # Get visible actions
        visible_actions = [action for action in self.actions.values() if action.visible]
        
        # Group actions
        grouped_actions = {}
        ungrouped_actions = []
        
        for action in visible_actions:
            if action.group is not None and action.group in self.groups:
                if action.group not in grouped_actions:
                    grouped_actions[action.group] = []
                    
                grouped_actions[action.group].append(action)
            else:
                ungrouped_actions.append(action)
                
        # Sort groups
        sorted_groups = sorted(self.groups.values(), key=lambda g: g["order"])
        
        # Sort actions within groups
        for group_id in grouped_actions:
            grouped_actions[group_id].sort(key=lambda a: a.order)
            
        # Sort ungrouped actions
        ungrouped_actions.sort(key=lambda a: a.order)
        
        # Convert actions to dictionaries
        action_data = []
        
        for group in sorted_groups:
            group_id = group["id"]
            
            if group_id in grouped_actions:
                group_data = {
                    "type": "group",
                    "id": group_id,
                    "title": group["title"],
                    "expanded": group["expanded"],
                    "style": group["style"],
                    "actions": [action.to_dict() for action in grouped_actions[group_id]]
                }
                
                action_data.append(group_data)
                
        for action in ungrouped_actions:
            action_data.append({
                "type": "action",
                **action.to_dict()
            })
            
        # Build the menu data
        menu_data = {
            "mode": self.mode.value,
            "position": self.position.value,
            "visible": self.is_visible,
            "style": {
                "background_color": self.style.background_color,
                "text_color": self.style.text_color,
                "accent_color": self.style.accent_color,
                "border_color": self.style.border_color,
                "border_radius": self.style.border_radius,
                "shadow": self.style.shadow,
                "font_family": self.style.font_family,
                "icon_size": self.style.icon_size,
                "button_size": self.style.button_size,
                "padding": self.style.padding,
                "margin": self.style.margin,
                "animation_duration": self.style.animation_duration,
                "custom_css": self.style.custom_css
            },
            "context": self.current_context,
            "items": action_data
        }
        
        return menu_data
    
    def _dispatch_event(self, event_type: ActionMenuEventType, data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Create event
        event = ActionMenuEvent(
            event_type=event_type,
            source="ActionMenuComponent",
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
    
    def _event_to_dict(self, event: ActionMenuEvent) -> Dict[str, Any]:
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
    
    # Create action menu component
    menu = ActionMenuComponent({
        "mode": "standard",
        "position": "bottom",
        "visible": True
    })
    
    # Set context
    menu.set_context({
        "user": {
            "id": "user123",
            "name": "John Doe",
            "role": "Process Engineer"
        },
        "environment": {
            "location": "Factory Floor",
            "area": "Assembly Line 3",
            "shift": "Morning"
        },
        "system": {
            "status": "operational",
            "uptime": "3d 7h 22m",
            "version": "1.2.3"
        }
    })
    
    # Add groups
    menu.add_group(
        group_id="production",
        title="Production",
        order=0
    )
    
    menu.add_group(
        group_id="maintenance",
        title="Maintenance",
        order=1
    )
    
    menu.add_group(
        group_id="analytics",
        title="Analytics",
        order=2
    )
    
    # Add actions
    def handle_action(data):
        print(f"Action executed: {data['action_id']}")
        return {"success": True}
    
    menu.add_action(
        label="Start Production",
        icon="play_arrow",
        handler=handle_action,
        group="production",
        order=0
    )
    
    menu.add_action(
        label="Pause Production",
        icon="pause",
        handler=handle_action,
        group="production",
        order=1
    )
    
    menu.add_action(
        label="Stop Production",
        icon="stop",
        handler=handle_action,
        group="production",
        order=2
    )
    
    menu.add_action(
        label="Request Maintenance",
        icon="build",
        handler=handle_action,
        group="maintenance",
        order=0
    )
    
    menu.add_action(
        label="View Maintenance History",
        icon="history",
        handler=handle_action,
        group="maintenance",
        order=1
    )
    
    menu.add_action(
        label="View Analytics",
        icon="analytics",
        handler=handle_action,
        group="analytics",
        order=0
    )
    
    menu.add_action(
        label="Export Data",
        icon="download",
        handler=handle_action,
        group="analytics",
        order=1
    )
    
    menu.add_action(
        label="Settings",
        icon="settings",
        handler=handle_action,
        order=0
    )
    
    menu.add_action(
        label="Help",
        icon="help",
        handler=handle_action,
        order=1
    )
    
    # Render the menu
    rendered = menu.render()
    print(f"Action menu has {len(rendered['items'])} items")
    
    # Execute an action
    try:
        result = menu.execute_action(list(menu.actions.keys())[0])
        print(f"Action result: {result}")
    except Exception as e:
        print(f"Error executing action: {e}")
"""
