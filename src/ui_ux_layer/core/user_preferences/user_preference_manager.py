"""
User Preference Manager for the Industriverse UI/UX Layer.

This module provides comprehensive user preference management capabilities for the Universal Skin
and Agent Capsules, enabling personalized experiences across devices and industrial contexts.

Author: Manus
"""

import logging
import time
import threading
import uuid
import json
import os
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field, asdict

class PreferenceScope(Enum):
    """Enumeration of preference scopes."""
    GLOBAL = "global"  # Global preferences (apply to all contexts)
    CONTEXT = "context"  # Context-specific preferences
    ROLE = "role"  # Role-specific preferences
    DEVICE = "device"  # Device-specific preferences
    USER = "user"  # User-specific preferences

class PreferenceCategory(Enum):
    """Enumeration of preference categories."""
    APPEARANCE = "appearance"  # Visual appearance preferences
    INTERACTION = "interaction"  # Interaction mode preferences
    NOTIFICATION = "notification"  # Notification preferences
    LAYOUT = "layout"  # Layout preferences
    ACCESSIBILITY = "accessibility"  # Accessibility preferences
    PRIVACY = "privacy"  # Privacy preferences
    PERFORMANCE = "performance"  # Performance preferences
    CUSTOM = "custom"  # Custom preferences

@dataclass
class UserPreference:
    """Data class representing a user preference."""
    preference_id: str
    key: str
    value: Any
    scope: PreferenceScope
    category: PreferenceCategory
    user_id: Optional[str] = None
    context_id: Optional[str] = None
    role_id: Optional[str] = None
    device_id: Optional[str] = None
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class UserPreferenceManager:
    """
    Provides comprehensive user preference management for the Industriverse UI/UX Layer.
    
    This class provides:
    - User preference storage and retrieval
    - Scope-based preference management (global, context, role, device, user)
    - Category-based preference organization
    - Preference inheritance and override
    - Preference synchronization across devices
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the User Preference Manager.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.preferences: Dict[str, UserPreference] = {}
        self.preference_listeners: Dict[str, List[Callable[[UserPreference], None]]] = {}
        self.category_listeners: Dict[PreferenceCategory, List[Callable[[UserPreference], None]]] = {}
        self.scope_listeners: Dict[PreferenceScope, List[Callable[[UserPreference], None]]] = {}
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        self.storage_path = self.config.get("storage_path", "preferences")
        
        # Initialize preference categories
        for category in PreferenceCategory:
            self.category_listeners[category] = []
            
        # Initialize preference scopes
        for scope in PreferenceScope:
            self.scope_listeners[scope] = []
            
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
        
    def start(self) -> bool:
        """
        Start the User Preference Manager.
        
        Returns:
            True if the manager was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Load preferences from storage
        self._load_preferences()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "preference_manager_started"
        })
        
        self.logger.info("User Preference Manager started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the User Preference Manager.
        
        Returns:
            True if the manager was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Save preferences to storage
        self._save_preferences()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "preference_manager_stopped"
        })
        
        self.logger.info("User Preference Manager stopped.")
        return True
    
    def set_preference(self,
                     key: str,
                     value: Any,
                     category: PreferenceCategory,
                     scope: PreferenceScope,
                     user_id: Optional[str] = None,
                     context_id: Optional[str] = None,
                     role_id: Optional[str] = None,
                     device_id: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Set a user preference.
        
        Args:
            key: Preference key
            value: Preference value
            category: Preference category
            scope: Preference scope
            user_id: Optional user ID for user-specific preferences
            context_id: Optional context ID for context-specific preferences
            role_id: Optional role ID for role-specific preferences
            device_id: Optional device ID for device-specific preferences
            metadata: Additional metadata for this preference
            
        Returns:
            The preference ID
        """
        # Validate scope-specific parameters
        if scope == PreferenceScope.USER and user_id is None:
            raise ValueError("User ID is required for user-specific preferences")
        if scope == PreferenceScope.CONTEXT and context_id is None:
            raise ValueError("Context ID is required for context-specific preferences")
        if scope == PreferenceScope.ROLE and role_id is None:
            raise ValueError("Role ID is required for role-specific preferences")
        if scope == PreferenceScope.DEVICE and device_id is None:
            raise ValueError("Device ID is required for device-specific preferences")
            
        # Generate preference ID
        preference_id = str(uuid.uuid4())
        
        # Create preference
        preference = UserPreference(
            preference_id=preference_id,
            key=key,
            value=value,
            scope=scope,
            category=category,
            user_id=user_id,
            context_id=context_id,
            role_id=role_id,
            device_id=device_id,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        # Store preference
        self.preferences[preference_id] = preference
        
        # Save preferences to storage
        self._save_preferences()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "preference_set",
            "preference_id": preference_id,
            "key": key,
            "category": category.value,
            "scope": scope.value
        })
        
        # Notify preference listeners
        if preference_id in self.preference_listeners:
            for listener in self.preference_listeners[preference_id]:
                try:
                    listener(preference)
                except Exception as e:
                    self.logger.error(f"Error in preference listener for {preference_id}: {e}")
                    
        # Notify category listeners
        for listener in self.category_listeners[category]:
            try:
                listener(preference)
            except Exception as e:
                self.logger.error(f"Error in category listener for {category.value}: {e}")
                
        # Notify scope listeners
        for listener in self.scope_listeners[scope]:
            try:
                listener(preference)
            except Exception as e:
                self.logger.error(f"Error in scope listener for {scope.value}: {e}")
                
        self.logger.debug(f"Set preference: {preference_id} ({key})")
        return preference_id
    
    def get_preference(self,
                     key: str,
                     category: PreferenceCategory,
                     user_id: Optional[str] = None,
                     context_id: Optional[str] = None,
                     role_id: Optional[str] = None,
                     device_id: Optional[str] = None,
                     default_value: Any = None) -> Any:
        """
        Get a user preference with scope inheritance.
        
        This method implements preference inheritance in the following order:
        1. User-specific preference
        2. Device-specific preference
        3. Role-specific preference
        4. Context-specific preference
        5. Global preference
        6. Default value
        
        Args:
            key: Preference key
            category: Preference category
            user_id: Optional user ID for user-specific preferences
            context_id: Optional context ID for context-specific preferences
            role_id: Optional role ID for role-specific preferences
            device_id: Optional device ID for device-specific preferences
            default_value: Default value to return if preference not found
            
        Returns:
            The preference value, or default_value if not found
        """
        # Check user-specific preference
        if user_id is not None:
            for preference in self.preferences.values():
                if (preference.key == key and
                    preference.category == category and
                    preference.scope == PreferenceScope.USER and
                    preference.user_id == user_id):
                    return preference.value
                    
        # Check device-specific preference
        if device_id is not None:
            for preference in self.preferences.values():
                if (preference.key == key and
                    preference.category == category and
                    preference.scope == PreferenceScope.DEVICE and
                    preference.device_id == device_id):
                    return preference.value
                    
        # Check role-specific preference
        if role_id is not None:
            for preference in self.preferences.values():
                if (preference.key == key and
                    preference.category == category and
                    preference.scope == PreferenceScope.ROLE and
                    preference.role_id == role_id):
                    return preference.value
                    
        # Check context-specific preference
        if context_id is not None:
            for preference in self.preferences.values():
                if (preference.key == key and
                    preference.category == category and
                    preference.scope == PreferenceScope.CONTEXT and
                    preference.context_id == context_id):
                    return preference.value
                    
        # Check global preference
        for preference in self.preferences.values():
            if (preference.key == key and
                preference.category == category and
                preference.scope == PreferenceScope.GLOBAL):
                return preference.value
                
        # Return default value
        return default_value
    
    def get_preference_by_id(self, preference_id: str) -> Optional[UserPreference]:
        """
        Get a preference by ID.
        
        Args:
            preference_id: ID of the preference to get
            
        Returns:
            The preference, or None if not found
        """
        return self.preferences.get(preference_id)
    
    def delete_preference(self, preference_id: str) -> bool:
        """
        Delete a preference.
        
        Args:
            preference_id: ID of the preference to delete
            
        Returns:
            True if the preference was deleted, False if not found
        """
        if preference_id not in self.preferences:
            self.logger.warning(f"Preference {preference_id} not found.")
            return False
            
        preference = self.preferences[preference_id]
        
        # Remove preference
        del self.preferences[preference_id]
        
        # Save preferences to storage
        self._save_preferences()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "preference_deleted",
            "preference_id": preference_id,
            "key": preference.key,
            "category": preference.category.value,
            "scope": preference.scope.value
        })
        
        self.logger.debug(f"Deleted preference: {preference_id} ({preference.key})")
        return True
    
    def get_preferences_by_category(self,
                                  category: PreferenceCategory,
                                  user_id: Optional[str] = None,
                                  context_id: Optional[str] = None,
                                  role_id: Optional[str] = None,
                                  device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all preferences in a category with scope inheritance.
        
        Args:
            category: Preference category
            user_id: Optional user ID for user-specific preferences
            context_id: Optional context ID for context-specific preferences
            role_id: Optional role ID for role-specific preferences
            device_id: Optional device ID for device-specific preferences
            
        Returns:
            Dictionary of preference keys to values
        """
        result = {}
        
        # Get global preferences
        for preference in self.preferences.values():
            if (preference.category == category and
                preference.scope == PreferenceScope.GLOBAL):
                result[preference.key] = preference.value
                
        # Override with context-specific preferences
        if context_id is not None:
            for preference in self.preferences.values():
                if (preference.category == category and
                    preference.scope == PreferenceScope.CONTEXT and
                    preference.context_id == context_id):
                    result[preference.key] = preference.value
                    
        # Override with role-specific preferences
        if role_id is not None:
            for preference in self.preferences.values():
                if (preference.category == category and
                    preference.scope == PreferenceScope.ROLE and
                    preference.role_id == role_id):
                    result[preference.key] = preference.value
                    
        # Override with device-specific preferences
        if device_id is not None:
            for preference in self.preferences.values():
                if (preference.category == category and
                    preference.scope == PreferenceScope.DEVICE and
                    preference.device_id == device_id):
                    result[preference.key] = preference.value
                    
        # Override with user-specific preferences
        if user_id is not None:
            for preference in self.preferences.values():
                if (preference.category == category and
                    preference.scope == PreferenceScope.USER and
                    preference.user_id == user_id):
                    result[preference.key] = preference.value
                    
        return result
    
    def reset_preferences(self,
                        category: Optional[PreferenceCategory] = None,
                        scope: Optional[PreferenceScope] = None,
                        user_id: Optional[str] = None,
                        context_id: Optional[str] = None,
                        role_id: Optional[str] = None,
                        device_id: Optional[str] = None) -> int:
        """
        Reset preferences to defaults.
        
        Args:
            category: Optional category to reset
            scope: Optional scope to reset
            user_id: Optional user ID for user-specific preferences
            context_id: Optional context ID for context-specific preferences
            role_id: Optional role ID for role-specific preferences
            device_id: Optional device ID for device-specific preferences
            
        Returns:
            Number of preferences reset
        """
        preferences_to_delete = []
        
        for preference_id, preference in self.preferences.items():
            # Apply filters
            if category is not None and preference.category != category:
                continue
                
            if scope is not None and preference.scope != scope:
                continue
                
            if user_id is not None and preference.user_id != user_id:
                continue
                
            if context_id is not None and preference.context_id != context_id:
                continue
                
            if role_id is not None and preference.role_id != role_id:
                continue
                
            if device_id is not None and preference.device_id != device_id:
                continue
                
            preferences_to_delete.append(preference_id)
            
        # Delete preferences
        for preference_id in preferences_to_delete:
            self.delete_preference(preference_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "preferences_reset",
            "count": len(preferences_to_delete),
            "category": category.value if category else None,
            "scope": scope.value if scope else None,
            "user_id": user_id,
            "context_id": context_id,
            "role_id": role_id,
            "device_id": device_id
        })
        
        self.logger.debug(f"Reset {len(preferences_to_delete)} preferences")
        return len(preferences_to_delete)
    
    def import_preferences(self, preferences_data: Dict[str, Any]) -> int:
        """
        Import preferences from a dictionary.
        
        Args:
            preferences_data: Dictionary of preference data
            
        Returns:
            Number of preferences imported
        """
        count = 0
        
        for preference_data in preferences_data.get("preferences", []):
            try:
                # Create preference
                preference = UserPreference(
                    preference_id=preference_data.get("preference_id", str(uuid.uuid4())),
                    key=preference_data["key"],
                    value=preference_data["value"],
                    scope=PreferenceScope(preference_data["scope"]),
                    category=PreferenceCategory(preference_data["category"]),
                    user_id=preference_data.get("user_id"),
                    context_id=preference_data.get("context_id"),
                    role_id=preference_data.get("role_id"),
                    device_id=preference_data.get("device_id"),
                    timestamp=preference_data.get("timestamp", time.time()),
                    metadata=preference_data.get("metadata", {})
                )
                
                # Store preference
                self.preferences[preference.preference_id] = preference
                count += 1
                
            except (KeyError, ValueError) as e:
                self.logger.warning(f"Error importing preference: {e}")
                
        # Save preferences to storage
        self._save_preferences()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "preferences_imported",
            "count": count
        })
        
        self.logger.debug(f"Imported {count} preferences")
        return count
    
    def export_preferences(self,
                         category: Optional[PreferenceCategory] = None,
                         scope: Optional[PreferenceScope] = None,
                         user_id: Optional[str] = None,
                         context_id: Optional[str] = None,
                         role_id: Optional[str] = None,
                         device_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Export preferences to a dictionary.
        
        Args:
            category: Optional category to export
            scope: Optional scope to export
            user_id: Optional user ID for user-specific preferences
            context_id: Optional context ID for context-specific preferences
            role_id: Optional role ID for role-specific preferences
            device_id: Optional device ID for device-specific preferences
            
        Returns:
            Dictionary of preference data
        """
        preferences_to_export = []
        
        for preference in self.preferences.values():
            # Apply filters
            if category is not None and preference.category != category:
                continue
                
            if scope is not None and preference.scope != scope:
                continue
                
            if user_id is not None and preference.user_id != user_id:
                continue
                
            if context_id is not None and preference.context_id != context_id:
                continue
                
            if role_id is not None and preference.role_id != role_id:
                continue
                
            if device_id is not None and preference.device_id != device_id:
                continue
                
            # Convert preference to dictionary
            preference_dict = asdict(preference)
            
            # Convert enum values to strings
            preference_dict["scope"] = preference.scope.value
            preference_dict["category"] = preference.category.value
            
            preferences_to_export.append(preference_dict)
            
        # Create export data
        export_data = {
            "version": "1.0",
            "timestamp": time.time(),
            "preferences": preferences_to_export
        }
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "preferences_exported",
            "count": len(preferences_to_export)
        })
        
        self.logger.debug(f"Exported {len(preferences_to_export)} preferences")
        return export_data
    
    def add_preference_listener(self, preference_id: str, listener: Callable[[UserPreference], None]) -> bool:
        """
        Add a listener for a specific preference.
        
        Args:
            preference_id: ID of the preference
            listener: Callback function that will be called when the preference is updated
            
        Returns:
            True if the listener was added, False if preference not found
        """
        if preference_id not in self.preferences:
            self.logger.warning(f"Preference {preference_id} not found.")
            return False
            
        if preference_id not in self.preference_listeners:
            self.preference_listeners[preference_id] = []
            
        self.preference_listeners[preference_id].append(listener)
        return True
    
    def add_category_listener(self, category: PreferenceCategory, listener: Callable[[UserPreference], None]) -> bool:
        """
        Add a listener for a specific preference category.
        
        Args:
            category: The preference category
            listener: Callback function that will be called when a preference in this category is updated
            
        Returns:
            True if the listener was added
        """
        self.category_listeners[category].append(listener)
        return True
    
    def add_scope_listener(self, scope: PreferenceScope, listener: Callable[[UserPreference], None]) -> bool:
        """
        Add a listener for a specific preference scope.
        
        Args:
            scope: The preference scope
            listener: Callback function that will be called when a preference in this scope is updated
            
        Returns:
            True if the listener was added
        """
        self.scope_listeners[scope].append(listener)
        return True
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all preference manager events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            return True
            
        return False
    
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_data: The event data to dispatch
        """
        # Add source if not present
        if "source" not in event_data:
            event_data["source"] = "UserPreferenceManager"
            
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = time.time()
            
        # Dispatch to global event listeners
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in preference event listener: {e}")
                
    def _load_preferences(self) -> None:
        """Load preferences from storage."""
        try:
            storage_file = os.path.join(self.storage_path, "preferences.json")
            
            if os.path.exists(storage_file):
                with open(storage_file, "r") as f:
                    preferences_data = json.load(f)
                    
                self.import_preferences(preferences_data)
                self.logger.info(f"Loaded preferences from {storage_file}")
                
        except Exception as e:
            self.logger.error(f"Error loading preferences: {e}")
            
    def _save_preferences(self) -> None:
        """Save preferences to storage."""
        try:
            storage_file = os.path.join(self.storage_path, "preferences.json")
            
            # Export all preferences
            preferences_data = self.export_preferences()
            
            # Save to file
            with open(storage_file, "w") as f:
                json.dump(preferences_data, f, indent=2)
                
            self.logger.debug(f"Saved preferences to {storage_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving preferences: {e}")

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create user preference manager
    preference_manager = UserPreferenceManager(config={"storage_path": "/tmp/preferences"})
    
    # Start the manager
    preference_manager.start()
    
    # Add an event listener
    def on_event(event):
        print(f"Event: {event['event_type']}")
        
    preference_manager.add_event_listener(on_event)
    
    # Set global preferences
    preference_manager.set_preference(
        key="theme",
        value="dark",
        category=PreferenceCategory.APPEARANCE,
        scope=PreferenceScope.GLOBAL
    )
    
    preference_manager.set_preference(
        key="font_size",
        value=14,
        category=PreferenceCategory.APPEARANCE,
        scope=PreferenceScope.GLOBAL
    )
    
    # Set context-specific preferences
    preference_manager.set_preference(
        key="theme",
        value="industrial",
        category=PreferenceCategory.APPEARANCE,
        scope=PreferenceScope.CONTEXT,
        context_id="manufacturing"
    )
    
    # Set user-specific preferences
    preference_manager.set_preference(
        key="font_size",
        value=16,
        category=PreferenceCategory.APPEARANCE,
        scope=PreferenceScope.USER,
        user_id="user123"
    )
    
    # Get preferences with inheritance
    theme = preference_manager.get_preference(
        key="theme",
        category=PreferenceCategory.APPEARANCE,
        user_id="user123",
        context_id="manufacturing"
    )
    
    font_size = preference_manager.get_preference(
        key="font_size",
        category=PreferenceCategory.APPEARANCE,
        user_id="user123",
        context_id="manufacturing"
    )
    
    print(f"Theme: {theme}")  # Should be "industrial" (from context)
    print(f"Font Size: {font_size}")  # Should be 16 (from user)
    
    # Get all appearance preferences
    appearance_prefs = preference_manager.get_preferences_by_category(
        category=PreferenceCategory.APPEARANCE,
        user_id="user123",
        context_id="manufacturing"
    )
    
    print(f"All Appearance Preferences: {appearance_prefs}")
    
    # Export preferences
    export_data = preference_manager.export_preferences()
    print(f"Exported {len(export_data['preferences'])} preferences")
    
    # Reset user preferences
    preference_manager.reset_preferences(
        scope=PreferenceScope.USER,
        user_id="user123"
    )
    
    # Get font size again (should fall back to global)
    font_size = preference_manager.get_preference(
        key="font_size",
        category=PreferenceCategory.APPEARANCE,
        user_id="user123",
        context_id="manufacturing"
    )
    
    print(f"Font Size after reset: {font_size}")  # Should be 14 (from global)
    
    # Stop the manager
    preference_manager.stop()
"""
