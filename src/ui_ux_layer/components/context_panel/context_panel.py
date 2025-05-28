"""
Context Panel Component for the Industriverse UI/UX Layer.

This module provides a contextual information panel that displays relevant
information based on the current user context, industrial environment,
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

class ContextPanelMode(Enum):
    """Enumeration of context panel modes."""
    COMPACT = "compact"
    STANDARD = "standard"
    EXPANDED = "expanded"
    DETAILED = "detailed"
    CUSTOM = "custom"

class ContextPanelSection(Enum):
    """Enumeration of context panel sections."""
    OVERVIEW = "overview"
    METRICS = "metrics"
    ALERTS = "alerts"
    ACTIONS = "actions"
    HISTORY = "history"
    RELATED = "related"
    DOCUMENTATION = "documentation"
    CUSTOM = "custom"

class ContextPanelEventType(Enum):
    """Enumeration of context panel event types."""
    SECTION_ADDED = "section_added"
    SECTION_REMOVED = "section_removed"
    SECTION_UPDATED = "section_updated"
    MODE_CHANGED = "mode_changed"
    VISIBILITY_CHANGED = "visibility_changed"
    CONTEXT_CHANGED = "context_changed"
    INTERACTION = "interaction"
    CUSTOM = "custom"

@dataclass
class ContextPanelStyle:
    """Data class representing context panel styling options."""
    background_color: str = "#FFFFFF"
    text_color: str = "#333333"
    accent_color: str = "#4285F4"
    border_color: str = "#E0E0E0"
    border_radius: int = 8
    shadow: str = "0 2px 10px rgba(0, 0, 0, 0.1)"
    font_family: str = "Roboto, sans-serif"
    header_font_size: int = 18
    body_font_size: int = 14
    padding: int = 16
    margin: int = 8
    animation_duration: int = 300
    custom_css: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ContextPanelEvent:
    """Data class representing a context panel event."""
    event_type: ContextPanelEventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class ContextPanelSection:
    """Data class representing a context panel section."""
    section_id: str
    title: str
    content: Any
    type: ContextPanelSection
    visible: bool = True
    expanded: bool = True
    order: int = 0
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the section to a dictionary."""
        return {
            "id": self.section_id,
            "title": self.title,
            "content": self.content,
            "type": self.type.value,
            "visible": self.visible,
            "expanded": self.expanded,
            "order": self.order,
            "style": self.style,
            "metadata": self.metadata
        }

class ContextPanelComponent:
    """
    Provides a contextual information panel for the Industriverse UI/UX Layer.
    
    This class provides:
    - Context-aware information display
    - Multiple panel sections for different types of information
    - Multiple display modes (compact, standard, expanded, detailed)
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Context Panel Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_visible = True
        self.mode = ContextPanelMode.STANDARD
        self.style = ContextPanelStyle()
        self.sections: Dict[str, ContextPanelSection] = {}
        self.current_context: Dict[str, Any] = {}
        self.event_listeners: Dict[ContextPanelEventType, List[Callable[[ContextPanelEvent], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize from config if provided
        if config:
            if "mode" in config:
                try:
                    self.mode = ContextPanelMode(config["mode"])
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
                        
            if "sections" in config:
                for section_config in config["sections"]:
                    if "id" not in section_config or "title" not in section_config or "content" not in section_config or "type" not in section_config:
                        self.logger.warning(f"Invalid section configuration: {section_config}")
                        continue
                        
                    self.add_section(
                        title=section_config["title"],
                        content=section_config["content"],
                        type=section_config["type"],
                        visible=section_config.get("visible", True),
                        expanded=section_config.get("expanded", True),
                        order=section_config.get("order", 0),
                        style=section_config.get("style", {}),
                        metadata=section_config.get("metadata", {}),
                        section_id=section_config["id"]
                    )
                    
            if "context" in config:
                self.set_context(config["context"])
        
    def add_section(self,
                  title: str,
                  content: Any,
                  type: Union[ContextPanelSection, str],
                  visible: bool = True,
                  expanded: bool = True,
                  order: int = 0,
                  style: Optional[Dict[str, Any]] = None,
                  metadata: Optional[Dict[str, Any]] = None,
                  section_id: Optional[str] = None) -> str:
        """
        Add a section to the context panel.
        
        Args:
            title: Title of the section
            content: Content of the section
            type: Type of section
            visible: Whether the section is visible
            expanded: Whether the section is expanded
            order: Order of the section
            style: Optional style configuration
            metadata: Optional metadata
            section_id: Optional section ID, generated if not provided
            
        Returns:
            The section ID
        """
        # Generate section ID if not provided
        if section_id is None:
            section_id = str(uuid.uuid4())
            
        # Convert type to ContextPanelSection if needed
        if not isinstance(type, ContextPanelSection):
            try:
                type = ContextPanelSection(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid section type: {type}, using CUSTOM.")
                type = ContextPanelSection.CUSTOM
                
        # Create section
        section = ContextPanelSection(
            section_id=section_id,
            title=title,
            content=content,
            type=type,
            visible=visible,
            expanded=expanded,
            order=order,
            style=style or {},
            metadata=metadata or {}
        )
        
        # Add to sections
        self.sections[section_id] = section
        
        # Dispatch event
        self._dispatch_event(ContextPanelEventType.SECTION_ADDED, {
            "section_id": section_id,
            "section": section.to_dict()
        })
        
        self.logger.debug(f"Added section: {section_id} ({title})")
        return section_id
    
    def remove_section(self, section_id: str) -> bool:
        """
        Remove a section from the context panel.
        
        Args:
            section_id: ID of the section to remove
            
        Returns:
            True if the section was removed, False if not found
        """
        if section_id not in self.sections:
            self.logger.warning(f"Section {section_id} not found.")
            return False
            
        section = self.sections[section_id]
        
        # Remove from sections
        del self.sections[section_id]
        
        # Dispatch event
        self._dispatch_event(ContextPanelEventType.SECTION_REMOVED, {
            "section_id": section_id,
            "section": section.to_dict()
        })
        
        self.logger.debug(f"Removed section: {section_id} ({section.title})")
        return True
    
    def update_section(self,
                     section_id: str,
                     title: Optional[str] = None,
                     content: Any = None,
                     visible: Optional[bool] = None,
                     expanded: Optional[bool] = None,
                     order: Optional[int] = None,
                     style: Optional[Dict[str, Any]] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a section in the context panel.
        
        Args:
            section_id: ID of the section to update
            title: Optional new title
            content: Optional new content
            visible: Optional new visibility
            expanded: Optional new expanded state
            order: Optional new order
            style: Optional new style
            metadata: Optional new metadata
            
        Returns:
            True if the section was updated, False if not found
        """
        if section_id not in self.sections:
            self.logger.warning(f"Section {section_id} not found.")
            return False
            
        section = self.sections[section_id]
        
        # Update properties
        if title is not None:
            section.title = title
            
        if content is not None:
            section.content = content
            
        if visible is not None:
            section.visible = visible
            
        if expanded is not None:
            section.expanded = expanded
            
        if order is not None:
            section.order = order
            
        if style is not None:
            section.style.update(style)
            
        if metadata is not None:
            section.metadata.update(metadata)
            
        # Dispatch event
        self._dispatch_event(ContextPanelEventType.SECTION_UPDATED, {
            "section_id": section_id,
            "section": section.to_dict()
        })
        
        self.logger.debug(f"Updated section: {section_id} ({section.title})")
        return True
    
    def get_section(self, section_id: str) -> Optional[ContextPanelSection]:
        """
        Get a section from the context panel.
        
        Args:
            section_id: ID of the section to get
            
        Returns:
            The section, or None if not found
        """
        return self.sections.get(section_id)
    
    def get_sections(self, filter_func: Optional[Callable[[ContextPanelSection], bool]] = None) -> List[ContextPanelSection]:
        """
        Get sections from the context panel, optionally filtered.
        
        Args:
            filter_func: Optional filter function
            
        Returns:
            List of sections
        """
        if filter_func is None:
            return list(self.sections.values())
            
        return [section for section in self.sections.values() if filter_func(section)]
    
    def get_sections_by_type(self, type: Union[ContextPanelSection, str]) -> List[ContextPanelSection]:
        """
        Get sections of a specific type.
        
        Args:
            type: Type of sections to get
            
        Returns:
            List of sections of the specified type
        """
        # Convert type to ContextPanelSection if needed
        if not isinstance(type, ContextPanelSection):
            try:
                type = ContextPanelSection(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid section type: {type}, using CUSTOM.")
                type = ContextPanelSection.CUSTOM
                
        return [section for section in self.sections.values() if section.type == type]
    
    def set_mode(self, mode: Union[ContextPanelMode, str]) -> bool:
        """
        Set the context panel mode.
        
        Args:
            mode: New mode
            
        Returns:
            True if the mode was set, False if invalid
        """
        # Convert mode to ContextPanelMode if needed
        if not isinstance(mode, ContextPanelMode):
            try:
                mode = ContextPanelMode(mode)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid mode: {mode}.")
                return False
                
        old_mode = self.mode
        self.mode = mode
        
        # Dispatch event
        self._dispatch_event(ContextPanelEventType.MODE_CHANGED, {
            "old_mode": old_mode.value,
            "new_mode": mode.value
        })
        
        self.logger.debug(f"Set mode: {mode.value}")
        return True
    
    def show(self) -> bool:
        """
        Show the context panel.
        
        Returns:
            True if the visibility was changed, False if already visible
        """
        if self.is_visible:
            return False
            
        self.is_visible = True
        
        # Dispatch event
        self._dispatch_event(ContextPanelEventType.VISIBILITY_CHANGED, {
            "visible": True
        })
        
        self.logger.debug("Context panel shown")
        return True
    
    def hide(self) -> bool:
        """
        Hide the context panel.
        
        Returns:
            True if the visibility was changed, False if already hidden
        """
        if not self.is_visible:
            return False
            
        self.is_visible = False
        
        # Dispatch event
        self._dispatch_event(ContextPanelEventType.VISIBILITY_CHANGED, {
            "visible": False
        })
        
        self.logger.debug("Context panel hidden")
        return True
    
    def set_style(self, style: Dict[str, Any]) -> None:
        """
        Set the context panel style.
        
        Args:
            style: Style configuration
        """
        # Update style properties
        for key, value in style.items():
            if hasattr(self.style, key):
                setattr(self.style, key, value)
            else:
                self.style.custom_css[key] = value
                
        self.logger.debug("Updated context panel style")
    
    def get_style(self) -> ContextPanelStyle:
        """
        Get the context panel style.
        
        Returns:
            The context panel style
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
        self._dispatch_event(ContextPanelEventType.CONTEXT_CHANGED, {
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
        self._dispatch_event(ContextPanelEventType.CONTEXT_CHANGED, {
            "old_context": old_context,
            "new_context": self.current_context,
            "updates": context_updates
        })
        
        self.logger.debug("Updated context")
    
    def add_event_listener(self, event_type: Union[ContextPanelEventType, str], listener: Callable[[ContextPanelEvent], None]) -> bool:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
            
        Returns:
            True if the listener was added, False if invalid event type
        """
        # Convert event_type to ContextPanelEventType if needed
        if not isinstance(event_type, ContextPanelEventType):
            try:
                event_type = ContextPanelEventType(event_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid event type: {event_type}.")
                return False
                
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        return True
    
    def remove_event_listener(self, event_type: Union[ContextPanelEventType, str], listener: Callable[[ContextPanelEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        # Convert event_type to ContextPanelEventType if needed
        if not isinstance(event_type, ContextPanelEventType):
            try:
                event_type = ContextPanelEventType(event_type)
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
    
    def handle_interaction(self, section_id: str, interaction_type: str, data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Handle an interaction with a section.
        
        Args:
            section_id: ID of the section that was interacted with
            interaction_type: Type of interaction
            data: Optional interaction data
            
        Returns:
            True if the interaction was handled, False if section not found
        """
        if section_id not in self.sections:
            self.logger.warning(f"Section {section_id} not found.")
            return False
            
        # Dispatch event
        self._dispatch_event(ContextPanelEventType.INTERACTION, {
            "section_id": section_id,
            "interaction_type": interaction_type,
            "data": data or {}
        })
        
        self.logger.debug(f"Handled interaction: {interaction_type} on section {section_id}")
        return True
    
    def add_overview_section(self,
                           title: str = "Overview",
                           content: Dict[str, Any] = None,
                           order: int = 0) -> str:
        """
        Add an overview section to the context panel.
        
        Args:
            title: Title of the section
            content: Content of the section
            order: Order of the section
            
        Returns:
            The section ID
        """
        content = content or {}
        
        return self.add_section(
            title=title,
            content=content,
            type=ContextPanelSection.OVERVIEW,
            order=order
        )
    
    def add_metrics_section(self,
                          title: str = "Metrics",
                          metrics: List[Dict[str, Any]] = None,
                          order: int = 1) -> str:
        """
        Add a metrics section to the context panel.
        
        Args:
            title: Title of the section
            metrics: List of metrics
            order: Order of the section
            
        Returns:
            The section ID
        """
        metrics = metrics or []
        
        return self.add_section(
            title=title,
            content={"metrics": metrics},
            type=ContextPanelSection.METRICS,
            order=order
        )
    
    def add_alerts_section(self,
                         title: str = "Alerts",
                         alerts: List[Dict[str, Any]] = None,
                         order: int = 2) -> str:
        """
        Add an alerts section to the context panel.
        
        Args:
            title: Title of the section
            alerts: List of alerts
            order: Order of the section
            
        Returns:
            The section ID
        """
        alerts = alerts or []
        
        return self.add_section(
            title=title,
            content={"alerts": alerts},
            type=ContextPanelSection.ALERTS,
            order=order
        )
    
    def add_actions_section(self,
                          title: str = "Actions",
                          actions: List[Dict[str, Any]] = None,
                          order: int = 3) -> str:
        """
        Add an actions section to the context panel.
        
        Args:
            title: Title of the section
            actions: List of actions
            order: Order of the section
            
        Returns:
            The section ID
        """
        actions = actions or []
        
        return self.add_section(
            title=title,
            content={"actions": actions},
            type=ContextPanelSection.ACTIONS,
            order=order
        )
    
    def add_history_section(self,
                          title: str = "History",
                          history_items: List[Dict[str, Any]] = None,
                          order: int = 4) -> str:
        """
        Add a history section to the context panel.
        
        Args:
            title: Title of the section
            history_items: List of history items
            order: Order of the section
            
        Returns:
            The section ID
        """
        history_items = history_items or []
        
        return self.add_section(
            title=title,
            content={"history_items": history_items},
            type=ContextPanelSection.HISTORY,
            order=order
        )
    
    def add_related_section(self,
                          title: str = "Related",
                          related_items: List[Dict[str, Any]] = None,
                          order: int = 5) -> str:
        """
        Add a related items section to the context panel.
        
        Args:
            title: Title of the section
            related_items: List of related items
            order: Order of the section
            
        Returns:
            The section ID
        """
        related_items = related_items or []
        
        return self.add_section(
            title=title,
            content={"related_items": related_items},
            type=ContextPanelSection.RELATED,
            order=order
        )
    
    def add_documentation_section(self,
                                title: str = "Documentation",
                                documentation: Dict[str, Any] = None,
                                order: int = 6) -> str:
        """
        Add a documentation section to the context panel.
        
        Args:
            title: Title of the section
            documentation: Documentation content
            order: Order of the section
            
        Returns:
            The section ID
        """
        documentation = documentation or {}
        
        return self.add_section(
            title=title,
            content=documentation,
            type=ContextPanelSection.DOCUMENTATION,
            order=order
        )
    
    def render(self) -> Dict[str, Any]:
        """
        Render the context panel for display.
        
        Returns:
            Rendered context panel data
        """
        # Get visible sections
        visible_sections = [section for section in self.sections.values() if section.visible]
        
        # Sort sections by order
        visible_sections.sort(key=lambda s: s.order)
        
        # Convert sections to dictionaries
        sections_data = [section.to_dict() for section in visible_sections]
        
        # Build the context panel data
        panel_data = {
            "mode": self.mode.value,
            "visible": self.is_visible,
            "style": {
                "background_color": self.style.background_color,
                "text_color": self.style.text_color,
                "accent_color": self.style.accent_color,
                "border_color": self.style.border_color,
                "border_radius": self.style.border_radius,
                "shadow": self.style.shadow,
                "font_family": self.style.font_family,
                "header_font_size": self.style.header_font_size,
                "body_font_size": self.style.body_font_size,
                "padding": self.style.padding,
                "margin": self.style.margin,
                "animation_duration": self.style.animation_duration,
                "custom_css": self.style.custom_css
            },
            "context": self.current_context,
            "sections": sections_data
        }
        
        return panel_data
    
    def _dispatch_event(self, event_type: ContextPanelEventType, data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Create event
        event = ContextPanelEvent(
            event_type=event_type,
            source="ContextPanelComponent",
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
    
    def _event_to_dict(self, event: ContextPanelEvent) -> Dict[str, Any]:
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
    
    # Create context panel component
    panel = ContextPanelComponent({
        "mode": "standard",
        "visible": True
    })
    
    # Set context
    panel.set_context({
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
    
    # Add sections
    panel.add_overview_section(
        content={
            "title": "Assembly Line 3",
            "description": "Main assembly line for product X",
            "status": "Operational",
            "efficiency": "94%",
            "current_task": "Component Assembly Phase 2"
        }
    )
    
    panel.add_metrics_section(
        metrics=[
            {
                "name": "Production Rate",
                "value": 127,
                "unit": "units/hour",
                "trend": "up",
                "change": "+3%"
            },
            {
                "name": "Quality Score",
                "value": 98.5,
                "unit": "%",
                "trend": "stable",
                "change": "0%"
            },
            {
                "name": "Energy Usage",
                "value": 42.3,
                "unit": "kWh",
                "trend": "down",
                "change": "-5%"
            }
        ]
    )
    
    panel.add_alerts_section(
        alerts=[
            {
                "id": "alert1",
                "type": "warning",
                "message": "Component supply running low",
                "timestamp": time.time() - 300,
                "source": "Inventory System"
            },
            {
                "id": "alert2",
                "type": "info",
                "message": "Maintenance scheduled in 2 hours",
                "timestamp": time.time() - 600,
                "source": "Maintenance System"
            }
        ]
    )
    
    panel.add_actions_section(
        actions=[
            {
                "id": "action1",
                "label": "Adjust Production Rate",
                "icon": "speed",
                "enabled": True
            },
            {
                "id": "action2",
                "label": "Request Maintenance",
                "icon": "build",
                "enabled": True
            },
            {
                "id": "action3",
                "label": "View Detailed Analytics",
                "icon": "analytics",
                "enabled": True
            }
        ]
    )
    
    # Render the context panel
    rendered = panel.render()
    print(f"Context panel has {len(rendered['sections'])} visible sections")
    
    # Handle an interaction
    panel.handle_interaction("action1", "click", {"value": 135})
"""
