"""
Global Navigation for Universal Skin Shell in the Industriverse UI/UX Layer.

This module implements global navigation and context switching capabilities for the Universal Skin Shell,
enabling seamless movement between different views, contexts, and layers of the Industrial Foundry Framework.

Author: Manus
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from enum import Enum

class NavigationLevel(Enum):
    """Enumeration of navigation levels in the Universal Skin Shell."""
    MASTER = "master"
    DOMAIN = "domain"
    PROCESS = "process"
    AGENT = "agent"
    CAPSULE = "capsule"
    DETAIL = "detail"

class NavigationContext:
    """Represents a navigation context in the Universal Skin Shell."""
    
    def __init__(self, 
                 level: NavigationLevel, 
                 id: str, 
                 title: str, 
                 parent_id: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a navigation context.
        
        Args:
            level: The navigation level of this context
            id: Unique identifier for this context
            title: Human-readable title for this context
            parent_id: Optional ID of the parent context
            metadata: Optional additional metadata for this context
        """
        self.level = level
        self.id = id
        self.title = title
        self.parent_id = parent_id
        self.metadata = metadata or {}
        self.children: List[NavigationContext] = []
        
    def add_child(self, child: 'NavigationContext') -> None:
        """Add a child context to this context."""
        self.children.append(child)
        child.parent_id = self.id
        
    def remove_child(self, child_id: str) -> Optional['NavigationContext']:
        """Remove a child context from this context."""
        for i, child in enumerate(self.children):
            if child.id == child_id:
                return self.children.pop(i)
        return None
    
    def find_child(self, child_id: str) -> Optional['NavigationContext']:
        """Find a child context by ID."""
        for child in self.children:
            if child.id == child_id:
                return child
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert this context to a dictionary representation."""
        return {
            "level": self.level.value,
            "id": self.id,
            "title": self.title,
            "parent_id": self.parent_id,
            "metadata": self.metadata,
            "children": [child.to_dict() for child in self.children]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NavigationContext':
        """Create a navigation context from a dictionary representation."""
        context = cls(
            level=NavigationLevel(data["level"]),
            id=data["id"],
            title=data["title"],
            parent_id=data.get("parent_id"),
            metadata=data.get("metadata", {})
        )
        
        for child_data in data.get("children", []):
            child = cls.from_dict(child_data)
            context.add_child(child)
            
        return context

class NavigationHistory:
    """Manages navigation history for the Universal Skin Shell."""
    
    def __init__(self, max_history: int = 100):
        """
        Initialize navigation history.
        
        Args:
            max_history: Maximum number of history entries to keep
        """
        self.history: List[str] = []
        self.current_index: int = -1
        self.max_history = max_history
        
    def add(self, context_id: str) -> None:
        """Add a context to the history."""
        # If we're not at the end of the history, truncate it
        if self.current_index < len(self.history) - 1:
            self.history = self.history[:self.current_index + 1]
            
        # Add the new context
        self.history.append(context_id)
        self.current_index = len(self.history) - 1
        
        # Trim history if it exceeds max_history
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
            self.current_index = len(self.history) - 1
            
    def back(self) -> Optional[str]:
        """Go back in history and return the previous context ID."""
        if self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
        return None
    
    def forward(self) -> Optional[str]:
        """Go forward in history and return the next context ID."""
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        return None
    
    def current(self) -> Optional[str]:
        """Get the current context ID."""
        if self.current_index >= 0 and self.current_index < len(self.history):
            return self.history[self.current_index]
        return None
    
    def clear(self) -> None:
        """Clear the navigation history."""
        self.history = []
        self.current_index = -1
        
    def can_go_back(self) -> bool:
        """Check if we can go back in history."""
        return self.current_index > 0
    
    def can_go_forward(self) -> bool:
        """Check if we can go forward in history."""
        return self.current_index < len(self.history) - 1

class NavigationEvent:
    """Represents a navigation event in the Universal Skin Shell."""
    
    def __init__(self, 
                 event_type: str, 
                 context_id: str, 
                 source: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a navigation event.
        
        Args:
            event_type: Type of navigation event (e.g., "navigate", "back", "forward")
            context_id: ID of the context being navigated to
            source: Optional source of the navigation event
            metadata: Optional additional metadata for this event
        """
        self.event_type = event_type
        self.context_id = context_id
        self.source = source
        self.metadata = metadata or {}
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this event to a dictionary representation."""
        return {
            "event_type": self.event_type,
            "context_id": self.context_id,
            "source": self.source,
            "metadata": self.metadata
        }

class GlobalNavigation:
    """
    Implements global navigation and context switching for the Universal Skin Shell.
    
    This class provides:
    - Navigation context management
    - Context switching
    - Navigation history
    - Breadcrumb generation
    - Navigation event handling
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Global Navigation.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.contexts: Dict[str, NavigationContext] = {}
        self.history = NavigationHistory(
            max_history=self.config.get("max_history", 100)
        )
        self.current_context_id: Optional[str] = None
        self.navigation_listeners: List[Callable[[NavigationEvent], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize root contexts for each navigation level
        self._initialize_root_contexts()
        
    def _initialize_root_contexts(self) -> None:
        """Initialize root contexts for each navigation level."""
        # Master view (top level)
        master_context = NavigationContext(
            level=NavigationLevel.MASTER,
            id="master",
            title="Master View"
        )
        self.contexts[master_context.id] = master_context
        
        # Domain view
        domain_context = NavigationContext(
            level=NavigationLevel.DOMAIN,
            id="domain",
            title="Domain View",
            parent_id="master"
        )
        self.contexts[domain_context.id] = domain_context
        master_context.add_child(domain_context)
        
        # Process view
        process_context = NavigationContext(
            level=NavigationLevel.PROCESS,
            id="process",
            title="Process View",
            parent_id="domain"
        )
        self.contexts[process_context.id] = process_context
        domain_context.add_child(process_context)
        
        # Agent view
        agent_context = NavigationContext(
            level=NavigationLevel.AGENT,
            id="agent",
            title="Agent View",
            parent_id="process"
        )
        self.contexts[agent_context.id] = agent_context
        process_context.add_child(agent_context)
        
    def register_context(self, context: NavigationContext) -> None:
        """
        Register a new navigation context.
        
        Args:
            context: The navigation context to register
        """
        if context.id in self.contexts:
            self.logger.warning(f"Context with ID {context.id} already exists, overwriting")
            
        self.contexts[context.id] = context
        
        # If this context has a parent, add it as a child of the parent
        if context.parent_id and context.parent_id in self.contexts:
            parent = self.contexts[context.parent_id]
            parent.add_child(context)
            
    def unregister_context(self, context_id: str) -> Optional[NavigationContext]:
        """
        Unregister a navigation context.
        
        Args:
            context_id: ID of the context to unregister
            
        Returns:
            The unregistered context, or None if not found
        """
        if context_id not in self.contexts:
            self.logger.warning(f"Context with ID {context_id} not found")
            return None
            
        context = self.contexts.pop(context_id)
        
        # If this context has a parent, remove it from the parent's children
        if context.parent_id and context.parent_id in self.contexts:
            parent = self.contexts[context.parent_id]
            parent.remove_child(context_id)
            
        return context
    
    def get_context(self, context_id: str) -> Optional[NavigationContext]:
        """
        Get a navigation context by ID.
        
        Args:
            context_id: ID of the context to get
            
        Returns:
            The navigation context, or None if not found
        """
        return self.contexts.get(context_id)
    
    def navigate_to(self, context_id: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Navigate to a specific context.
        
        Args:
            context_id: ID of the context to navigate to
            metadata: Optional metadata for the navigation event
            
        Returns:
            True if navigation was successful, False otherwise
        """
        if context_id not in self.contexts:
            self.logger.warning(f"Cannot navigate to unknown context: {context_id}")
            return False
            
        # Update current context
        self.current_context_id = context_id
        
        # Add to history
        self.history.add(context_id)
        
        # Create and dispatch navigation event
        event = NavigationEvent(
            event_type="navigate",
            context_id=context_id,
            source="user",
            metadata=metadata
        )
        self._dispatch_navigation_event(event)
        
        return True
    
    def navigate_back(self) -> bool:
        """
        Navigate back in history.
        
        Returns:
            True if navigation was successful, False otherwise
        """
        previous_context_id = self.history.back()
        if previous_context_id is None:
            self.logger.info("Cannot navigate back: at start of history")
            return False
            
        # Update current context
        self.current_context_id = previous_context_id
        
        # Create and dispatch navigation event
        event = NavigationEvent(
            event_type="back",
            context_id=previous_context_id,
            source="user"
        )
        self._dispatch_navigation_event(event)
        
        return True
    
    def navigate_forward(self) -> bool:
        """
        Navigate forward in history.
        
        Returns:
            True if navigation was successful, False otherwise
        """
        next_context_id = self.history.forward()
        if next_context_id is None:
            self.logger.info("Cannot navigate forward: at end of history")
            return False
            
        # Update current context
        self.current_context_id = next_context_id
        
        # Create and dispatch navigation event
        event = NavigationEvent(
            event_type="forward",
            context_id=next_context_id,
            source="user"
        )
        self._dispatch_navigation_event(event)
        
        return True
    
    def get_current_context(self) -> Optional[NavigationContext]:
        """
        Get the current navigation context.
        
        Returns:
            The current navigation context, or None if not set
        """
        if self.current_context_id is None:
            return None
        return self.contexts.get(self.current_context_id)
    
    def get_breadcrumbs(self) -> List[NavigationContext]:
        """
        Get breadcrumbs for the current navigation context.
        
        Returns:
            List of navigation contexts representing the breadcrumb trail
        """
        breadcrumbs = []
        current = self.get_current_context()
        
        while current is not None:
            breadcrumbs.insert(0, current)
            if current.parent_id is None:
                break
            current = self.contexts.get(current.parent_id)
            
        return breadcrumbs
    
    def add_navigation_listener(self, listener: Callable[[NavigationEvent], None]) -> None:
        """
        Add a listener for navigation events.
        
        Args:
            listener: Callback function that will be called with navigation events
        """
        self.navigation_listeners.append(listener)
        
    def remove_navigation_listener(self, listener: Callable[[NavigationEvent], None]) -> None:
        """
        Remove a listener for navigation events.
        
        Args:
            listener: The listener to remove
        """
        if listener in self.navigation_listeners:
            self.navigation_listeners.remove(listener)
            
    def _dispatch_navigation_event(self, event: NavigationEvent) -> None:
        """
        Dispatch a navigation event to all listeners.
        
        Args:
            event: The navigation event to dispatch
        """
        for listener in self.navigation_listeners:
            try:
                listener(event)
            except Exception as e:
                self.logger.error(f"Error in navigation listener: {e}")
                
    def get_navigation_tree(self) -> Dict[str, Any]:
        """
        Get the complete navigation tree.
        
        Returns:
            Dictionary representation of the navigation tree
        """
        # Start with the master context
        master_context = self.contexts.get("master")
        if master_context is None:
            return {}
            
        return master_context.to_dict()
    
    def clear_history(self) -> None:
        """Clear the navigation history."""
        self.history.clear()
        
    def can_go_back(self) -> bool:
        """Check if we can navigate back in history."""
        return self.history.can_go_back()
    
    def can_go_forward(self) -> bool:
        """Check if we can navigate forward in history."""
        return self.history.can_go_forward()
    
    def get_context_by_level(self, level: NavigationLevel) -> List[NavigationContext]:
        """
        Get all contexts at a specific navigation level.
        
        Args:
            level: The navigation level to filter by
            
        Returns:
            List of navigation contexts at the specified level
        """
        return [
            context for context in self.contexts.values()
            if context.level == level
        ]
    
    def navigate_to_parent(self) -> bool:
        """
        Navigate to the parent of the current context.
        
        Returns:
            True if navigation was successful, False otherwise
        """
        current = self.get_current_context()
        if current is None or current.parent_id is None:
            self.logger.info("Cannot navigate to parent: no current context or no parent")
            return False
            
        return self.navigate_to(current.parent_id)
    
    def navigate_to_child(self, child_id: str) -> bool:
        """
        Navigate to a child of the current context.
        
        Args:
            child_id: ID of the child context to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        current = self.get_current_context()
        if current is None:
            self.logger.info("Cannot navigate to child: no current context")
            return False
            
        child = current.find_child(child_id)
        if child is None:
            self.logger.warning(f"Child context {child_id} not found in current context")
            return False
            
        return self.navigate_to(child.id)
    
    def navigate_to_level(self, level: NavigationLevel) -> bool:
        """
        Navigate to the first context at a specific level.
        
        Args:
            level: The navigation level to navigate to
            
        Returns:
            True if navigation was successful, False otherwise
        """
        contexts = self.get_context_by_level(level)
        if not contexts:
            self.logger.warning(f"No contexts found at level {level.value}")
            return False
            
        return self.navigate_to(contexts[0].id)
    
    def get_navigation_state(self) -> Dict[str, Any]:
        """
        Get the current navigation state.
        
        Returns:
            Dictionary representation of the current navigation state
        """
        return {
            "current_context_id": self.current_context_id,
            "can_go_back": self.can_go_back(),
            "can_go_forward": self.can_go_forward(),
            "breadcrumbs": [context.to_dict() for context in self.get_breadcrumbs()]
        }
