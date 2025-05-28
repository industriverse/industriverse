"""
Shell State Manager for Universal Skin Shell in the Industriverse UI/UX Layer.

This module manages the state of the Universal Skin Shell, including view state,
user preferences, device capabilities, and interaction modes.

Author: Manus
"""

import logging
import time
import json
from typing import Dict, List, Optional, Any, Callable, Set, TypeVar, Generic
from enum import Enum
import uuid

T = TypeVar('T')

class StateChangeType(Enum):
    """Enumeration of state change types."""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    RESET = "reset"

class StateScope(Enum):
    """Enumeration of state scopes."""
    GLOBAL = "global"  # Global state, shared across all views and contexts
    VIEW = "view"      # View-specific state
    USER = "user"      # User-specific state
    DEVICE = "device"  # Device-specific state
    SESSION = "session"  # Session-specific state
    TEMPORARY = "temporary"  # Temporary state that doesn't persist

class StateChangeEvent:
    """Represents a state change event in the Shell State Manager."""
    
    def __init__(self,
                 state_key: str,
                 change_type: StateChangeType,
                 old_value: Optional[Any] = None,
                 new_value: Optional[Any] = None,
                 scope: Optional[StateScope] = None,
                 source: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a state change event.
        
        Args:
            state_key: Key of the state that changed
            change_type: Type of state change
            old_value: Previous value of the state (None for CREATED)
            new_value: New value of the state (None for DELETED)
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this event
        """
        self.state_key = state_key
        self.change_type = change_type
        self.old_value = old_value
        self.new_value = new_value
        self.scope = scope
        self.source = source
        self.metadata = metadata or {}
        self.timestamp = time.time()
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert this event to a dictionary representation."""
        return {
            "state_key": self.state_key,
            "change_type": self.change_type.value,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "scope": self.scope.value if self.scope else None,
            "source": self.source,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }

class StateSubscription(Generic[T]):
    """Represents a subscription to state changes."""
    
    def __init__(self,
                 state_key: str,
                 callback: Callable[[StateChangeEvent], None],
                 subscription_id: Optional[str] = None,
                 filter_change_types: Optional[Set[StateChangeType]] = None):
        """
        Initialize a state subscription.
        
        Args:
            state_key: Key of the state to subscribe to
            callback: Callback function to call when state changes
            subscription_id: Unique identifier for this subscription
            filter_change_types: Set of change types to filter by
        """
        self.state_key = state_key
        self.callback = callback
        self.subscription_id = subscription_id or str(uuid.uuid4())
        self.filter_change_types = filter_change_types or set(StateChangeType)
        self.created_at = time.time()
        
    def matches_event(self, event: StateChangeEvent) -> bool:
        """
        Check if this subscription matches a state change event.
        
        Args:
            event: The state change event to check
            
        Returns:
            True if the subscription matches the event, False otherwise
        """
        return (
            self.state_key == event.state_key and
            event.change_type in self.filter_change_types
        )
        
    def notify(self, event: StateChangeEvent) -> None:
        """
        Notify the subscriber of a state change event.
        
        Args:
            event: The state change event to notify about
        """
        self.callback(event)

class ShellStateManager:
    """
    Manages the state of the Universal Skin Shell.
    
    This class provides:
    - State storage and retrieval
    - State change notifications
    - State persistence
    - State scoping
    - State history
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Shell State Manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.state: Dict[str, Dict[str, Any]] = {
            scope.value: {} for scope in StateScope
        }
        self.subscriptions: Dict[str, List[StateSubscription]] = {}
        self.history: Dict[str, List[StateChangeEvent]] = {}
        self.history_limit = self.config.get("history_limit", 100)
        self.logger = logging.getLogger(__name__)
        
        # Initialize default state
        self._initialize_default_state()
        
    def _initialize_default_state(self) -> None:
        """Initialize default state values."""
        # Global state defaults
        self.set_state("theme", "light", StateScope.GLOBAL)
        self.set_state("language", "en", StateScope.GLOBAL)
        self.set_state("notifications_enabled", True, StateScope.GLOBAL)
        self.set_state("sound_enabled", True, StateScope.GLOBAL)
        self.set_state("haptic_enabled", True, StateScope.GLOBAL)
        
        # Device state defaults
        self.set_state("device_type", "desktop", StateScope.DEVICE)
        self.set_state("screen_size", {"width": 1920, "height": 1080}, StateScope.DEVICE)
        self.set_state("orientation", "landscape", StateScope.DEVICE)
        self.set_state("touch_enabled", False, StateScope.DEVICE)
        self.set_state("has_keyboard", True, StateScope.DEVICE)
        self.set_state("has_mouse", True, StateScope.DEVICE)
        self.set_state("has_stylus", False, StateScope.DEVICE)
        
        # Session state defaults
        self.set_state("session_start_time", time.time(), StateScope.SESSION)
        self.set_state("active_view", "dashboard", StateScope.SESSION)
        self.set_state("sidebar_expanded", True, StateScope.SESSION)
        
    def get_state(self, 
                 key: str, 
                 scope: StateScope = StateScope.GLOBAL, 
                 default: Optional[T] = None) -> Optional[T]:
        """
        Get a state value.
        
        Args:
            key: Key of the state to get
            scope: Scope of the state
            default: Default value to return if state doesn't exist
            
        Returns:
            The state value, or default if not found
        """
        return self.state[scope.value].get(key, default)
    
    def set_state(self, 
                 key: str, 
                 value: Any, 
                 scope: StateScope = StateScope.GLOBAL,
                 source: Optional[str] = None,
                 metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Set a state value.
        
        Args:
            key: Key of the state to set
            value: Value to set
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
        """
        old_value = self.state[scope.value].get(key)
        self.state[scope.value][key] = value
        
        # Determine change type
        change_type = (
            StateChangeType.CREATED if old_value is None
            else StateChangeType.UPDATED
        )
        
        # Create and dispatch state change event
        event = StateChangeEvent(
            state_key=key,
            change_type=change_type,
            old_value=old_value,
            new_value=value,
            scope=scope,
            source=source,
            metadata=metadata
        )
        self._dispatch_state_change_event(event)
        self._add_to_history(event)
        
    def delete_state(self, 
                    key: str, 
                    scope: StateScope = StateScope.GLOBAL,
                    source: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Delete a state value.
        
        Args:
            key: Key of the state to delete
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
            
        Returns:
            True if the state was deleted, False if it didn't exist
        """
        if key not in self.state[scope.value]:
            return False
            
        old_value = self.state[scope.value].pop(key)
        
        # Create and dispatch state change event
        event = StateChangeEvent(
            state_key=key,
            change_type=StateChangeType.DELETED,
            old_value=old_value,
            new_value=None,
            scope=scope,
            source=source,
            metadata=metadata
        )
        self._dispatch_state_change_event(event)
        self._add_to_history(event)
        
        return True
    
    def has_state(self, key: str, scope: StateScope = StateScope.GLOBAL) -> bool:
        """
        Check if a state value exists.
        
        Args:
            key: Key of the state to check
            scope: Scope of the state
            
        Returns:
            True if the state exists, False otherwise
        """
        return key in self.state[scope.value]
    
    def reset_state(self, 
                   scope: StateScope = StateScope.GLOBAL,
                   source: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Reset all state in a scope.
        
        Args:
            scope: Scope of the state to reset
            source: Source of the state change
            metadata: Additional metadata for this change
        """
        old_state = self.state[scope.value].copy()
        self.state[scope.value] = {}
        
        # Create and dispatch state change event for each deleted state
        for key, old_value in old_state.items():
            event = StateChangeEvent(
                state_key=key,
                change_type=StateChangeType.RESET,
                old_value=old_value,
                new_value=None,
                scope=scope,
                source=source,
                metadata=metadata
            )
            self._dispatch_state_change_event(event)
            self._add_to_history(event)
            
    def get_all_state(self, scope: Optional[StateScope] = None) -> Dict[str, Any]:
        """
        Get all state values.
        
        Args:
            scope: Optional scope to filter by
            
        Returns:
            Dictionary of all state values
        """
        if scope is not None:
            return self.state[scope.value].copy()
            
        # Combine all scopes
        all_state = {}
        for scope_value, scope_state in self.state.items():
            all_state[scope_value] = scope_state.copy()
            
        return all_state
    
    def subscribe(self, 
                 key: str, 
                 callback: Callable[[StateChangeEvent], None],
                 filter_change_types: Optional[Set[StateChangeType]] = None) -> str:
        """
        Subscribe to state changes.
        
        Args:
            key: Key of the state to subscribe to
            callback: Callback function to call when state changes
            filter_change_types: Set of change types to filter by
            
        Returns:
            Subscription ID
        """
        subscription = StateSubscription(
            state_key=key,
            callback=callback,
            filter_change_types=filter_change_types
        )
        
        if key not in self.subscriptions:
            self.subscriptions[key] = []
            
        self.subscriptions[key].append(subscription)
        
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from state changes.
        
        Args:
            subscription_id: ID of the subscription to remove
            
        Returns:
            True if the subscription was removed, False if not found
        """
        for key, subscriptions in self.subscriptions.items():
            for i, subscription in enumerate(subscriptions):
                if subscription.subscription_id == subscription_id:
                    self.subscriptions[key].pop(i)
                    return True
                    
        return False
    
    def _dispatch_state_change_event(self, event: StateChangeEvent) -> None:
        """
        Dispatch a state change event to all subscribers.
        
        Args:
            event: The state change event to dispatch
        """
        # Notify subscribers for this specific key
        for subscription in self.subscriptions.get(event.state_key, []):
            if subscription.matches_event(event):
                try:
                    subscription.notify(event)
                except Exception as e:
                    self.logger.error(f"Error in state change listener: {e}")
                    
        # Notify subscribers for wildcard key "*"
        for subscription in self.subscriptions.get("*", []):
            if subscription.matches_event(event):
                try:
                    subscription.notify(event)
                except Exception as e:
                    self.logger.error(f"Error in wildcard state change listener: {e}")
                    
    def _add_to_history(self, event: StateChangeEvent) -> None:
        """
        Add a state change event to history.
        
        Args:
            event: The state change event to add
        """
        if event.state_key not in self.history:
            self.history[event.state_key] = []
            
        self.history[event.state_key].append(event)
        
        # Trim history if it exceeds the limit
        if len(self.history[event.state_key]) > self.history_limit:
            self.history[event.state_key] = self.history[event.state_key][-self.history_limit:]
            
    def get_history(self, 
                   key: str, 
                   limit: Optional[int] = None) -> List[StateChangeEvent]:
        """
        Get history of state changes for a key.
        
        Args:
            key: Key of the state to get history for
            limit: Maximum number of history entries to return
            
        Returns:
            List of state change events
        """
        if key not in self.history:
            return []
            
        history = self.history[key]
        
        if limit is not None:
            history = history[-limit:]
            
        return history
    
    def clear_history(self, key: Optional[str] = None) -> None:
        """
        Clear history of state changes.
        
        Args:
            key: Optional key to clear history for (all keys if None)
        """
        if key is not None:
            if key in self.history:
                self.history[key] = []
        else:
            self.history = {}
            
    def save_state(self, 
                  file_path: str, 
                  scopes: Optional[List[StateScope]] = None) -> bool:
        """
        Save state to a file.
        
        Args:
            file_path: Path to save state to
            scopes: Optional list of scopes to save (all scopes if None)
            
        Returns:
            True if state was saved successfully, False otherwise
        """
        try:
            # Determine which scopes to save
            if scopes is None:
                scopes = [scope for scope in StateScope]
            else:
                scopes = list(scopes)
                
            # Filter out TEMPORARY scope
            if StateScope.TEMPORARY in scopes:
                scopes.remove(StateScope.TEMPORARY)
                
            # Create state dictionary to save
            state_to_save = {
                scope.value: self.state[scope.value]
                for scope in scopes
            }
            
            # Save to file
            with open(file_path, 'w') as f:
                json.dump(state_to_save, f, indent=2)
                
            return True
        except Exception as e:
            self.logger.error(f"Error saving state: {e}")
            return False
            
    def load_state(self, 
                  file_path: str, 
                  scopes: Optional[List[StateScope]] = None,
                  merge: bool = False) -> bool:
        """
        Load state from a file.
        
        Args:
            file_path: Path to load state from
            scopes: Optional list of scopes to load (all scopes if None)
            merge: Whether to merge with existing state (False will replace)
            
        Returns:
            True if state was loaded successfully, False otherwise
        """
        try:
            # Load from file
            with open(file_path, 'r') as f:
                loaded_state = json.load(f)
                
            # Determine which scopes to load
            if scopes is None:
                scopes = [scope for scope in StateScope]
            else:
                scopes = list(scopes)
                
            # Filter out TEMPORARY scope
            if StateScope.TEMPORARY in scopes:
                scopes.remove(StateScope.TEMPORARY)
                
            # Update state
            for scope in scopes:
                scope_value = scope.value
                if scope_value in loaded_state:
                    if merge:
                        self.state[scope_value].update(loaded_state[scope_value])
                    else:
                        self.state[scope_value] = loaded_state[scope_value]
                        
            return True
        except Exception as e:
            self.logger.error(f"Error loading state: {e}")
            return False
            
    def get_state_diff(self, 
                      other_state: Dict[str, Dict[str, Any]],
                      scopes: Optional[List[StateScope]] = None) -> Dict[str, Dict[str, Any]]:
        """
        Get difference between current state and another state.
        
        Args:
            other_state: Other state to compare with
            scopes: Optional list of scopes to compare (all scopes if None)
            
        Returns:
            Dictionary of differences
        """
        diff = {}
        
        # Determine which scopes to compare
        if scopes is None:
            scopes = [scope for scope in StateScope]
            
        # Compare each scope
        for scope in scopes:
            scope_value = scope.value
            scope_diff = {}
            
            # Check for keys in current state but not in other state
            for key, value in self.state[scope_value].items():
                if scope_value not in other_state or key not in other_state[scope_value]:
                    scope_diff[key] = {"current": value, "other": None}
                elif value != other_state[scope_value][key]:
                    scope_diff[key] = {"current": value, "other": other_state[scope_value][key]}
                    
            # Check for keys in other state but not in current state
            if scope_value in other_state:
                for key, value in other_state[scope_value].items():
                    if key not in self.state[scope_value]:
                        scope_diff[key] = {"current": None, "other": value}
                        
            if scope_diff:
                diff[scope_value] = scope_diff
                
        return diff
    
    def merge_state(self, 
                   other_state: Dict[str, Dict[str, Any]],
                   scopes: Optional[List[StateScope]] = None,
                   source: Optional[str] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Merge another state into current state.
        
        Args:
            other_state: Other state to merge
            scopes: Optional list of scopes to merge (all scopes if None)
            source: Source of the state change
            metadata: Additional metadata for this change
        """
        # Determine which scopes to merge
        if scopes is None:
            scopes = [scope for scope in StateScope]
            
        # Merge each scope
        for scope in scopes:
            scope_value = scope.value
            if scope_value in other_state:
                for key, value in other_state[scope_value].items():
                    self.set_state(key, value, scope, source, metadata)
                    
    def watch_state(self, 
                   key: str, 
                   callback: Callable[[Any], None],
                   immediate: bool = False) -> str:
        """
        Watch a state value for changes.
        
        Args:
            key: Key of the state to watch
            callback: Callback function to call with new value
            immediate: Whether to call callback immediately with current value
            
        Returns:
            Subscription ID
        """
        def state_change_handler(event: StateChangeEvent) -> None:
            if event.change_type != StateChangeType.DELETED:
                callback(event.new_value)
                
        subscription_id = self.subscribe(
            key,
            state_change_handler,
            {StateChangeType.CREATED, StateChangeType.UPDATED}
        )
        
        # Call callback immediately if requested
        if immediate:
            for scope in StateScope:
                value = self.get_state(key, scope)
                if value is not None:
                    callback(value)
                    break
                    
        return subscription_id
    
    def batch_update(self, 
                    updates: Dict[str, Any], 
                    scope: StateScope = StateScope.GLOBAL,
                    source: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Update multiple state values at once.
        
        Args:
            updates: Dictionary of key-value pairs to update
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
        """
        for key, value in updates.items():
            self.set_state(key, value, scope, source, metadata)
            
    def toggle_state(self, 
                    key: str, 
                    scope: StateScope = StateScope.GLOBAL,
                    source: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Toggle a boolean state value.
        
        Args:
            key: Key of the state to toggle
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
            
        Returns:
            New state value
        """
        current_value = self.get_state(key, scope, False)
        new_value = not bool(current_value)
        self.set_state(key, new_value, scope, source, metadata)
        return new_value
    
    def increment_state(self, 
                       key: str, 
                       amount: float = 1.0,
                       scope: StateScope = StateScope.GLOBAL,
                       source: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        Increment a numeric state value.
        
        Args:
            key: Key of the state to increment
            amount: Amount to increment by
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
            
        Returns:
            New state value
        """
        current_value = self.get_state(key, scope, 0)
        try:
            new_value = float(current_value) + amount
            self.set_state(key, new_value, scope, source, metadata)
            return new_value
        except (TypeError, ValueError):
            self.logger.warning(f"Cannot increment non-numeric state: {key}")
            return current_value
            
    def decrement_state(self, 
                       key: str, 
                       amount: float = 1.0,
                       scope: StateScope = StateScope.GLOBAL,
                       source: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> float:
        """
        Decrement a numeric state value.
        
        Args:
            key: Key of the state to decrement
            amount: Amount to decrement by
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
            
        Returns:
            New state value
        """
        return self.increment_state(key, -amount, scope, source, metadata)
    
    def append_to_state(self, 
                       key: str, 
                       value: Any,
                       scope: StateScope = StateScope.GLOBAL,
                       source: Optional[str] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Append a value to a list state.
        
        Args:
            key: Key of the state to append to
            value: Value to append
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
            
        Returns:
            New state value
        """
        current_value = self.get_state(key, scope, [])
        if not isinstance(current_value, list):
            current_value = [current_value]
            
        new_value = current_value + [value]
        self.set_state(key, new_value, scope, source, metadata)
        return new_value
    
    def remove_from_state(self, 
                         key: str, 
                         value: Any,
                         scope: StateScope = StateScope.GLOBAL,
                         source: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> List[Any]:
        """
        Remove a value from a list state.
        
        Args:
            key: Key of the state to remove from
            value: Value to remove
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
            
        Returns:
            New state value
        """
        current_value = self.get_state(key, scope, [])
        if not isinstance(current_value, list):
            return current_value
            
        new_value = [v for v in current_value if v != value]
        self.set_state(key, new_value, scope, source, metadata)
        return new_value
    
    def update_nested_state(self, 
                           key: str, 
                           path: List[str],
                           value: Any,
                           scope: StateScope = StateScope.GLOBAL,
                           source: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Update a nested state value.
        
        Args:
            key: Key of the state to update
            path: Path to the nested value
            value: New value
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
            
        Returns:
            New state value
        """
        current_value = self.get_state(key, scope, {})
        if not isinstance(current_value, dict):
            current_value = {}
            
        # Make a deep copy of the current value
        new_value = json.loads(json.dumps(current_value))
        
        # Navigate to the nested value
        target = new_value
        for i, p in enumerate(path[:-1]):
            if p not in target or not isinstance(target[p], dict):
                target[p] = {}
            target = target[p]
            
        # Update the value
        if path:
            target[path[-1]] = value
        else:
            new_value = value
            
        self.set_state(key, new_value, scope, source, metadata)
        return new_value
    
    def get_nested_state(self, 
                        key: str, 
                        path: List[str],
                        default: Optional[T] = None,
                        scope: StateScope = StateScope.GLOBAL) -> Optional[T]:
        """
        Get a nested state value.
        
        Args:
            key: Key of the state to get
            path: Path to the nested value
            default: Default value to return if not found
            scope: Scope of the state
            
        Returns:
            The nested state value, or default if not found
        """
        current_value = self.get_state(key, scope, {})
        if not isinstance(current_value, dict):
            return default
            
        # Navigate to the nested value
        target = current_value
        for p in path:
            if p not in target or not isinstance(target[p], dict):
                return default
            target = target[p]
            
        return target
    
    def delete_nested_state(self, 
                           key: str, 
                           path: List[str],
                           scope: StateScope = StateScope.GLOBAL,
                           source: Optional[str] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> Any:
        """
        Delete a nested state value.
        
        Args:
            key: Key of the state to update
            path: Path to the nested value
            scope: Scope of the state
            source: Source of the state change
            metadata: Additional metadata for this change
            
        Returns:
            New state value
        """
        current_value = self.get_state(key, scope, {})
        if not isinstance(current_value, dict):
            return current_value
            
        # Make a deep copy of the current value
        new_value = json.loads(json.dumps(current_value))
        
        # Navigate to the parent of the nested value
        target = new_value
        for i, p in enumerate(path[:-1]):
            if p not in target or not isinstance(target[p], dict):
                return new_value
            target = target[p]
            
        # Delete the value
        if path and path[-1] in target:
            del target[path[-1]]
            
        self.set_state(key, new_value, scope, source, metadata)
        return new_value
