"""
Context Awareness Engine for Context Engine

This module provides context awareness capabilities for the Industriverse UI/UX Layer.
It collects, processes, and provides contextual information about the user, environment,
device, and system state to enable adaptive and intelligent user experiences.

The Context Awareness Engine:
1. Collects contextual data from various sources
2. Processes and interprets contextual information
3. Provides an API for accessing context data
4. Notifies other components of context changes
5. Adapts to changing environments and user behaviors

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import time
import os
import threading

# Configure logging
logger = logging.getLogger(__name__)

class ContextType(Enum):
    """Enumeration of context types."""
    USER = "user"               # User-related context (identity, preferences, etc.)
    DEVICE = "device"           # Device-related context (capabilities, state, etc.)
    ENVIRONMENT = "environment" # Environment-related context (location, time, etc.)
    TASK = "task"               # Task-related context (current workflow, goals, etc.)
    SYSTEM = "system"           # System-related context (performance, resources, etc.)
    SOCIAL = "social"           # Social context (collaboration, sharing, etc.)
    SECURITY = "security"       # Security-related context (trust levels, permissions, etc.)

class ContextPriority(Enum):
    """Enumeration of context priority levels."""
    CRITICAL = "critical"       # Highest priority, requires immediate attention
    HIGH = "high"               # High priority, important for current operation
    MEDIUM = "medium"           # Medium priority, relevant but not urgent
    LOW = "low"                 # Low priority, background information
    INFO = "info"               # Informational only, lowest priority

class ContextAwarenessEngine:
    """
    Provides context awareness capabilities for the Industriverse UI/UX Layer.
    
    This class is responsible for collecting, processing, and providing contextual
    information about the user, environment, device, and system state to enable
    adaptive and intelligent user experiences.
    """
    
    def __init__(self, storage_path: str = None):
        """
        Initialize the Context Awareness Engine.
        
        Args:
            storage_path: Optional path for context data storage
        """
        # Set storage path
        self.storage_path = storage_path or os.path.join(os.path.dirname(__file__), "../../data/context")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Current context data
        self.context_data = {
            ContextType.USER.value: {},
            ContextType.DEVICE.value: {},
            ContextType.ENVIRONMENT.value: {},
            ContextType.TASK.value: {},
            ContextType.SYSTEM.value: {},
            ContextType.SOCIAL.value: {},
            ContextType.SECURITY.value: {}
        }
        
        # Context history
        self.context_history = {
            ContextType.USER.value: [],
            ContextType.DEVICE.value: [],
            ContextType.ENVIRONMENT.value: [],
            ContextType.TASK.value: [],
            ContextType.SYSTEM.value: [],
            ContextType.SOCIAL.value: [],
            ContextType.SECURITY.value: []
        }
        
        # Context change listeners
        self.context_listeners = []
        
        # Context update frequency (in seconds)
        self.update_frequency = {
            ContextType.USER.value: 60,        # Update user context every minute
            ContextType.DEVICE.value: 30,      # Update device context every 30 seconds
            ContextType.ENVIRONMENT.value: 300, # Update environment context every 5 minutes
            ContextType.TASK.value: 10,        # Update task context every 10 seconds
            ContextType.SYSTEM.value: 15,      # Update system context every 15 seconds
            ContextType.SOCIAL.value: 120,     # Update social context every 2 minutes
            ContextType.SECURITY.value: 60     # Update security context every minute
        }
        
        # Last update timestamps
        self.last_update = {
            ContextType.USER.value: 0,
            ContextType.DEVICE.value: 0,
            ContextType.ENVIRONMENT.value: 0,
            ContextType.TASK.value: 0,
            ContextType.SYSTEM.value: 0,
            ContextType.SOCIAL.value: 0,
            ContextType.SECURITY.value: 0
        }
        
        # Context data sources
        self.data_sources = {}
        
        # Context inference rules
        self.inference_rules = {}
        
        # Initialize context data
        self._initialize_context_data()
        
        # Start context update thread
        self.update_thread_running = True
        self.update_thread = threading.Thread(target=self._context_update_thread)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        logger.info("Context Awareness Engine initialized")
    
    def _initialize_context_data(self) -> None:
        """Initialize context data with default values."""
        # Initialize user context
        self.context_data[ContextType.USER.value] = {
            "user_id": None,
            "username": None,
            "role": None,
            "preferences": {},
            "session_id": None,
            "login_time": None,
            "last_activity": time.time(),
            "focus_level": "normal",
            "experience_level": "intermediate"
        }
        
        # Initialize device context
        self.context_data[ContextType.DEVICE.value] = {
            "device_id": None,
            "device_type": "desktop",
            "platform": "web",
            "screen_size": {
                "width": 1920,
                "height": 1080
            },
            "orientation": "landscape",
            "input_methods": ["keyboard", "mouse"],
            "performance_tier": 2,
            "connection_quality": "high",
            "battery_level": None,
            "storage_available": True,
            "audio_enabled": True,
            "haptic_enabled": False,
            "camera_available": False,
            "location_available": False
        }
        
        # Initialize environment context
        self.context_data[ContextType.ENVIRONMENT.value] = {
            "location": None,
            "timezone": "UTC",
            "time_of_day": "day",
            "noise_level": "normal",
            "lighting_condition": "normal",
            "privacy_level": "normal",
            "connectivity": "online",
            "bandwidth": "high",
            "latency": "low"
        }
        
        # Initialize task context
        self.context_data[ContextType.TASK.value] = {
            "current_task": None,
            "task_priority": "normal",
            "task_complexity": "medium",
            "task_progress": 0,
            "task_deadline": None,
            "workflow_id": None,
            "workflow_step": None,
            "active_capsules": [],
            "focus_area": None,
            "interruption_level": "low"
        }
        
        # Initialize system context
        self.context_data[ContextType.SYSTEM.value] = {
            "system_status": "normal",
            "cpu_usage": 0,
            "memory_usage": 0,
            "network_usage": 0,
            "storage_usage": 0,
            "battery_usage": 0,
            "error_rate": 0,
            "response_time": 0,
            "active_layers": [],
            "maintenance_mode": False,
            "update_available": False
        }
        
        # Initialize social context
        self.context_data[ContextType.SOCIAL.value] = {
            "collaboration_mode": "individual",
            "team_members": [],
            "shared_resources": [],
            "communication_channels": [],
            "activity_feed": [],
            "notifications": [],
            "presence_status": "active"
        }
        
        # Initialize security context
        self.context_data[ContextType.SECURITY.value] = {
            "authentication_level": "standard",
            "authorization_level": "standard",
            "trust_level": "medium",
            "data_sensitivity": "medium",
            "compliance_requirements": [],
            "security_alerts": [],
            "audit_mode": False,
            "encryption_level": "standard"
        }
    
    def _context_update_thread(self) -> None:
        """Background thread for periodic context updates."""
        while self.update_thread_running:
            current_time = time.time()
            
            # Check each context type for updates
            for context_type in ContextType:
                type_value = context_type.value
                last_update = self.last_update[type_value]
                update_interval = self.update_frequency[type_value]
                
                # If it's time to update this context type
                if current_time - last_update > update_interval:
                    self._update_context(type_value)
                    self.last_update[type_value] = current_time
            
            # Sleep for a short interval
            time.sleep(1)
    
    def _update_context(self, context_type: str) -> None:
        """
        Update context data for a specific context type.
        
        Args:
            context_type: The type of context to update
        """
        # Get data sources for this context type
        sources = self.data_sources.get(context_type, [])
        
        # Collect data from each source
        updated_data = {}
        for source in sources:
            try:
                source_data = source.get_data()
                updated_data.update(source_data)
            except Exception as e:
                logger.error(f"Error collecting data from source for {context_type}: {str(e)}")
        
        # If no data sources or no data collected, use inference
        if not updated_data:
            updated_data = self._infer_context(context_type)
        
        # If we have updated data, apply it
        if updated_data:
            self._apply_context_update(context_type, updated_data)
    
    def _infer_context(self, context_type: str) -> Dict:
        """
        Infer context data based on existing context and rules.
        
        Args:
            context_type: The type of context to infer
            
        Returns:
            Dictionary of inferred context data
        """
        # Get inference rules for this context type
        rules = self.inference_rules.get(context_type, [])
        
        # Apply each rule
        inferred_data = {}
        for rule in rules:
            try:
                rule_result = rule.apply(self.context_data)
                inferred_data.update(rule_result)
            except Exception as e:
                logger.error(f"Error applying inference rule for {context_type}: {str(e)}")
        
        return inferred_data
    
    def _apply_context_update(self, context_type: str, updated_data: Dict) -> None:
        """
        Apply context update and notify listeners if significant changes.
        
        Args:
            context_type: The type of context being updated
            updated_data: The updated context data
        """
        # Check if there are significant changes
        significant_change = False
        current_data = self.context_data[context_type]
        
        for key, value in updated_data.items():
            # If key doesn't exist or value has changed
            if key not in current_data or current_data[key] != value:
                significant_change = True
                break
        
        # If significant changes, update context and notify listeners
        if significant_change:
            # Add to history before updating
            history_entry = {
                "timestamp": time.time(),
                "data": current_data.copy()
            }
            self.context_history[context_type].append(history_entry)
            
            # Limit history length
            if len(self.context_history[context_type]) > 100:
                self.context_history[context_type].pop(0)
            
            # Update current context
            self.context_data[context_type].update(updated_data)
            
            # Notify listeners
            self._notify_context_change(context_type, updated_data)
    
    def _notify_context_change(self, context_type: str, updated_data: Dict) -> None:
        """
        Notify listeners of context change.
        
        Args:
            context_type: The type of context that changed
            updated_data: The updated context data
        """
        # Create context change event
        event = {
            "type": context_type,
            "timestamp": time.time(),
            "data": updated_data
        }
        
        # Determine priority
        priority = ContextPriority.MEDIUM.value
        
        # Check for critical changes
        if context_type == ContextType.SECURITY.value and "security_alerts" in updated_data:
            priority = ContextPriority.CRITICAL.value
        elif context_type == ContextType.SYSTEM.value and updated_data.get("system_status") == "error":
            priority = ContextPriority.CRITICAL.value
        elif context_type == ContextType.TASK.value and updated_data.get("task_priority") == "high":
            priority = ContextPriority.HIGH.value
        
        event["priority"] = priority
        
        # Notify each listener
        for listener in self.context_listeners:
            try:
                listener(event)
            except Exception as e:
                logger.error(f"Error notifying context listener: {str(e)}")
    
    def register_context_listener(self, listener_function) -> bool:
        """
        Register a function to be called when context changes.
        
        Args:
            listener_function: Function to call with context change event
            
        Returns:
            Boolean indicating success
        """
        if listener_function not in self.context_listeners:
            self.context_listeners.append(listener_function)
            logger.info(f"Registered context listener: {listener_function.__name__}")
            return True
        return False
    
    def unregister_context_listener(self, listener_function) -> bool:
        """
        Unregister a context change listener.
        
        Args:
            listener_function: Function to unregister
            
        Returns:
            Boolean indicating success
        """
        if listener_function in self.context_listeners:
            self.context_listeners.remove(listener_function)
            logger.info(f"Unregistered context listener: {listener_function.__name__}")
            return True
        return False
    
    def register_data_source(self, context_type: str, data_source) -> bool:
        """
        Register a data source for a specific context type.
        
        Args:
            context_type: The type of context the source provides
            data_source: Object with get_data() method
            
        Returns:
            Boolean indicating success
        """
        if context_type not in self.data_sources:
            self.data_sources[context_type] = []
        
        if data_source not in self.data_sources[context_type]:
            self.data_sources[context_type].append(data_source)
            logger.info(f"Registered data source for {context_type}: {data_source.__class__.__name__}")
            return True
        return False
    
    def unregister_data_source(self, context_type: str, data_source) -> bool:
        """
        Unregister a data source.
        
        Args:
            context_type: The type of context the source provides
            data_source: Object to unregister
            
        Returns:
            Boolean indicating success
        """
        if context_type in self.data_sources and data_source in self.data_sources[context_type]:
            self.data_sources[context_type].remove(data_source)
            logger.info(f"Unregistered data source for {context_type}: {data_source.__class__.__name__}")
            return True
        return False
    
    def register_inference_rule(self, context_type: str, inference_rule) -> bool:
        """
        Register an inference rule for a specific context type.
        
        Args:
            context_type: The type of context the rule infers
            inference_rule: Object with apply() method
            
        Returns:
            Boolean indicating success
        """
        if context_type not in self.inference_rules:
            self.inference_rules[context_type] = []
        
        if inference_rule not in self.inference_rules[context_type]:
            self.inference_rules[context_type].append(inference_rule)
            logger.info(f"Registered inference rule for {context_type}: {inference_rule.__class__.__name__}")
            return True
        return False
    
    def unregister_inference_rule(self, context_type: str, inference_rule) -> bool:
        """
        Unregister an inference rule.
        
        Args:
            context_type: The type of context the rule infers
            inference_rule: Object to unregister
            
        Returns:
            Boolean indicating success
        """
        if context_type in self.inference_rules and inference_rule in self.inference_rules[context_type]:
            self.inference_rules[context_type].remove(inference_rule)
            logger.info(f"Unregistered inference rule for {context_type}: {inference_rule.__class__.__name__}")
            return True
        return False
    
    def get_context(self, context_type: str = None) -> Dict:
        """
        Get current context data.
        
        Args:
            context_type: Optional specific context type to get
            
        Returns:
            Dictionary of context data
        """
        if context_type:
            return self.context_data.get(context_type, {})
        else:
            # Return all context data
            return {
                "user": self.context_data[ContextType.USER.value],
                "device": self.context_data[ContextType.DEVICE.value],
                "environment": self.context_data[ContextType.ENVIRONMENT.value],
                "task": self.context_data[ContextType.TASK.value],
                "system": self.context_data[ContextType.SYSTEM.value],
                "social": self.context_data[ContextType.SOCIAL.value],
                "security": self.context_data[ContextType.SECURITY.value]
            }
    
    def get_context_history(self, context_type: str, limit: int = 10) -> List[Dict]:
        """
        Get context history for a specific context type.
        
        Args:
            context_type: The type of context to get history for
            limit: Maximum number of history entries to return
            
        Returns:
            List of historical context entries
        """
        if context_type not in self.context_history:
            return []
        
        # Return most recent entries first
        history = self.context_history[context_type]
        return sorted(history, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
    def update_user_context(self, user_data: Dict) -> bool:
        """
        Update user context data.
        
        Args:
            user_data: Dictionary of user context data
            
        Returns:
            Boolean indicating success
        """
        return self._apply_context_update(ContextType.USER.value, user_data)
    
    def update_device_context(self, device_data: Dict) -> bool:
        """
        Update device context data.
        
        Args:
            device_data: Dictionary of device context data
            
        Returns:
            Boolean indicating success
        """
        return self._apply_context_update(ContextType.DEVICE.value, device_data)
    
    def update_task_context(self, task_data: Dict) -> bool:
        """
        Update task context data.
        
        Args:
            task_data: Dictionary of task context data
            
        Returns:
            Boolean indicating success
        """
        return self._apply_context_update(ContextType.TASK.value, task_data)
    
    def get_current_user_id(self) -> str:
        """
        Get the current user ID.
        
        Returns:
            Current user ID or None
        """
        return self.context_data[ContextType.USER.value].get("user_id")
    
    def get_current_session_id(self) -> str:
        """
        Get the current session ID.
        
        Returns:
            Current session ID or None
        """
        return self.context_data[ContextType.USER.value].get("session_id")
    
    def get_current_device_id(self) -> str:
        """
        Get the current device ID.
        
        Returns:
            Current device ID or None
        """
        return self.context_data[ContextType.DEVICE.value].get("device_id")
    
    def get_device_capabilities(self) -> Dict:
        """
        Get current device capabilities.
        
        Returns:
            Dictionary of device capabilities
        """
        return self.context_data[ContextType.DEVICE.value]
    
    def get_user_preferences(self) -> Dict:
        """
        Get current user preferences.
        
        Returns:
            Dictionary of user preferences
        """
        return self.context_data[ContextType.USER.value].get("preferences", {})
    
    def get_current_context(self) -> Dict:
        """
        Get a simplified version of the current context.
        
        Returns:
            Dictionary of current context
        """
        return {
            "user_id": self.get_current_user_id(),
            "session_id": self.get_current_session_id(),
            "device_id": self.get_current_device_id(),
            "device_type": self.context_data[ContextType.DEVICE.value].get("device_type"),
            "platform": self.context_data[ContextType.DEVICE.value].get("platform"),
            "role": self.context_data[ContextType.USER.value].get("role"),
            "focus_level": self.context_data[ContextType.USER.value].get("focus_level"),
            "task_priority": self.context_data[ContextType.TASK.value].get("task_priority"),
            "system_status": self.context_data[ContextType.SYSTEM.value].get("system_status"),
            "connectivity": self.context_data[ContextType.ENVIRONMENT.value].get("connectivity"),
            "trust_level": self.context_data[ContextType.SECURITY.value].get("trust_level"),
            "time": time.time()
        }
    
    def get_agent_state(self, agent_id: str) -> Dict:
        """
        Get state data for a specific agent.
        
        Args:
            agent_id: The ID of the agent to get state for
            
        Returns:
            Dictionary of agent state data or None if not found
        """
        # In a real implementation, this would query the agent state from a registry
        # For now, we'll return a mock state based on the agent ID
        
        # Check if we have any active capsules with this agent ID
        active_capsules = self.context_data[ContextType.TASK.value].get("active_capsules", [])
        
        for capsule in active_capsules:
            if capsule.get("agent_id") == agent_id:
                return capsule.get("agent_state", {})
        
        # If not found in active capsules, return a mock state
        return {
            "agent_id": agent_id,
            "name": f"Agent {agent_id}",
            "type": "unknown",
            "status": "unknown",
            "trust": 0.5,
            "confidence": 0.5,
            "last_update": time.time() - 3600  # 1 hour ago
        }
    
    def set_update_frequency(self, context_type: str, frequency_seconds: int) -> bool:
        """
        Set the update frequency for a specific context type.
        
        Args:
            context_type: The type of context to set frequency for
            frequency_seconds: Update frequency in seconds
            
        Returns:
            Boolean indicating success
        """
        if context_type in self.update_frequency:
            self.update_frequency[context_type] = frequency_seconds
            logger.info(f"Set update frequency for {context_type} to {frequency_seconds} seconds")
            return True
        return False
    
    def save_context_snapshot(self) -> str:
        """
        Save a snapshot of the current context to storage.
        
        Returns:
            Path to the saved snapshot file
        """
        snapshot = {
            "timestamp": time.time(),
            "context": self.get_context()
        }
        
        # Generate filename based on timestamp
        filename = f"context_snapshot_{int(time.time())}.json"
        file_path = os.path.join(self.storage_path, filename)
        
        try:
            with open(file_path, 'w') as f:
                json.dump(snapshot, f)
            
            logger.info(f"Saved context snapshot to {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save context snapshot: {str(e)}")
            return None
    
    def load_context_snapshot(self, file_path: str) -> bool:
        """
        Load a context snapshot from storage.
        
        Args:
            file_path: Path to the snapshot file
            
        Returns:
            Boolean indicating success
        """
        try:
            with open(file_path, 'r') as f:
                snapshot = json.load(f)
            
            # Extract context data
            context = snapshot.get("context", {})
            
            # Apply each context type
            for context_type, data in context.items():
                if context_type in self.context_data:
                    self._apply_context_update(context_type, data)
            
            logger.info(f"Loaded context snapshot from {file_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to load context snapshot: {str(e)}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown the Context Awareness Engine."""
        # Stop update thread
        self.update_thread_running = False
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=2)
        
        # Save final context snapshot
        self.save_context_snapshot()
        
        logger.info("Context Awareness Engine shutdown")
"""
