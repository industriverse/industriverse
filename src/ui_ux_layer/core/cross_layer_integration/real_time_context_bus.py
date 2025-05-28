"""
Real-Time Context Bus for the Industriverse UI/UX Layer.

This module provides a real-time context bus for cross-layer communication,
enabling seamless data flow between the UI/UX Layer and other layers of the
Industriverse ecosystem.

Author: Manus
"""

import logging
import json
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Callable, Union, Set
from enum import Enum
from dataclasses import dataclass, field

from ..cross_layer_integration.cross_layer_integration import CrossLayerIntegration, CrossLayerMessage, LayerType, MessageType, MessagePriority

class ContextScope(Enum):
    """Enumeration of context scopes."""
    GLOBAL = "global"
    USER = "user"
    DEVICE = "device"
    SESSION = "session"
    WORKSPACE = "workspace"
    INDUSTRY = "industry"
    PROCESS = "process"
    TASK = "task"

class ContextPriority(Enum):
    """Enumeration of context priorities."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class ContextData:
    """Data class representing context data."""
    id: str
    scope: ContextScope
    type: str
    data: Dict[str, Any]
    source_layer: LayerType
    priority: ContextPriority
    timestamp: float = field(default_factory=time.time)
    ttl: Optional[int] = None  # Time to live in seconds
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the context data to a dictionary."""
        return {
            "id": self.id,
            "scope": self.scope.value,
            "type": self.type,
            "data": self.data,
            "source_layer": self.source_layer.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextData':
        """Create context data from a dictionary."""
        return cls(
            id=data["id"],
            scope=ContextScope(data["scope"]),
            type=data["type"],
            data=data["data"],
            source_layer=LayerType(data["source_layer"]),
            priority=ContextPriority(data["priority"]),
            timestamp=data.get("timestamp", time.time()),
            ttl=data.get("ttl"),
            metadata=data.get("metadata", {})
        )

class RealTimeContextBus:
    """
    Provides a real-time context bus for cross-layer communication.
    
    This class provides:
    - Real-time data streaming between layers
    - Context-aware message routing
    - Event-based communication
    - Context caching and retrieval
    - Context subscription and publication
    """
    
    def __init__(self, cross_layer_integration: CrossLayerIntegration, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Real-Time Context Bus.
        
        Args:
            cross_layer_integration: Cross-Layer Integration module
            config: Optional configuration dictionary
        """
        self.cross_layer_integration = cross_layer_integration
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.context_handlers: Dict[str, List[Callable[[ContextData], None]]] = {}
        self.context_cache: Dict[str, Dict[str, ContextData]] = {}
        self.running = False
        self.worker_thread = None
        self.context_queue = queue.Queue()
        
        # Initialize from config if provided
        if config:
            pass
            
        # Initialize context cache
        for scope in ContextScope:
            self.context_cache[scope.value] = {}
            
        # Subscribe to context events from other layers
        self.cross_layer_integration.subscribe(
            topic="*.event.context_updated",
            callback=self._handle_context_event
        )
        
        self.logger.info("Real-Time Context Bus initialized")
        
    def start(self) -> bool:
        """
        Start the Real-Time Context Bus.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.logger.warning("Real-Time Context Bus already running")
            return False
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._context_worker, daemon=True)
        self.worker_thread.start()
        
        self.logger.info("Real-Time Context Bus started")
        return True
        
    def stop(self) -> bool:
        """
        Stop the Real-Time Context Bus.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.running:
            self.logger.warning("Real-Time Context Bus not running")
            return False
            
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            
        self.logger.info("Real-Time Context Bus stopped")
        return True
        
    def _context_worker(self) -> None:
        """
        Worker thread for processing context updates.
        """
        self.logger.info("Context worker thread started")
        
        while self.running:
            try:
                context_data = self.context_queue.get(timeout=1.0)
                self._process_context(context_data)
                self.context_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing context: {e}")
                
        self.logger.info("Context worker thread stopped")
        
    def _process_context(self, context_data: ContextData) -> None:
        """
        Process context data.
        
        Args:
            context_data: Context data to process
        """
        # Check TTL
        if context_data.ttl is not None and context_data.ttl <= 0:
            self.logger.warning(f"Context {context_data.id} expired (TTL <= 0)")
            return
            
        # Update context cache
        scope = context_data.scope.value
        context_type = context_data.type
        
        cache_key = f"{context_type}:{context_data.id}"
        self.context_cache[scope][cache_key] = context_data
        
        # Notify context handlers
        handler_key = f"{scope}.{context_type}"
        if handler_key in self.context_handlers:
            for handler in self.context_handlers[handler_key]:
                try:
                    handler(context_data)
                except Exception as e:
                    self.logger.error(f"Error in context handler for {handler_key}: {e}")
                    
        # Notify wildcard handlers
        wildcard_keys = [
            f"*.{context_type}",
            f"{scope}.*",
            "*.*"
        ]
        
        for key in wildcard_keys:
            if key in self.context_handlers:
                for handler in self.context_handlers[key]:
                    try:
                        handler(context_data)
                    except Exception as e:
                        self.logger.error(f"Error in wildcard context handler for {key}: {e}")
                        
    def _handle_context_event(self, message: CrossLayerMessage) -> None:
        """
        Handle a context event message from another layer.
        
        Args:
            message: Message to handle
        """
        if message.message_type != MessageType.EVENT:
            return
            
        payload = message.payload
        if "context_type" not in payload or "context_data" not in payload:
            return
            
        context_type = payload["context_type"]
        context_data = payload["context_data"]
        scope = payload.get("context_scope", ContextScope.GLOBAL.value)
        
        # Create context data object
        context = ContextData(
            id=f"ext_{int(time.time() * 1000)}_{message.source_layer.value}_{context_type}",
            scope=ContextScope(scope),
            type=context_type,
            data=context_data,
            source_layer=message.source_layer,
            priority=ContextPriority.NORMAL,
            timestamp=payload.get("timestamp", time.time()),
            ttl=payload.get("ttl"),
            metadata=payload.get("metadata", {})
        )
        
        # Queue for processing
        self.context_queue.put(context)
        
    def publish_context(self, scope: ContextScope, context_type: str, context_data: Dict[str, Any],
                      priority: ContextPriority = ContextPriority.NORMAL,
                      ttl: Optional[int] = None,
                      metadata: Optional[Dict[str, Any]] = None,
                      target_layers: Optional[List[LayerType]] = None) -> str:
        """
        Publish context data to the bus.
        
        Args:
            scope: Context scope
            context_type: Type of context data
            context_data: Context data
            priority: Context priority
            ttl: Time to live in seconds, or None for no expiration
            metadata: Optional metadata
            target_layers: Target layers, or None for all layers
            
        Returns:
            Context ID
        """
        context_id = f"ctx_{int(time.time() * 1000)}_{scope.value}_{context_type}"
        
        # Create context data object
        context = ContextData(
            id=context_id,
            scope=scope,
            type=context_type,
            data=context_data,
            source_layer=LayerType.UI_UX,
            priority=priority,
            timestamp=time.time(),
            ttl=ttl,
            metadata=metadata or {}
        )
        
        # Queue for local processing
        self.context_queue.put(context)
        
        # Publish to other layers
        if target_layers is not None:
            # Create context payload
            payload = {
                "context_type": context_type,
                "context_scope": scope.value,
                "context_data": context_data,
                "timestamp": context.timestamp,
                "ttl": ttl,
                "metadata": metadata or {}
            }
            
            # Map context priority to message priority
            message_priority = MessagePriority.NORMAL
            if priority == ContextPriority.LOW:
                message_priority = MessagePriority.LOW
            elif priority == ContextPriority.HIGH:
                message_priority = MessagePriority.HIGH
            elif priority == ContextPriority.CRITICAL:
                message_priority = MessagePriority.CRITICAL
                
            # Publish as event
            self.cross_layer_integration.publish_event(
                event_type="context_updated",
                payload=payload,
                priority=message_priority,
                target_layers=target_layers
            )
            
        return context_id
        
    def get_context(self, scope: ContextScope, context_type: str, context_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get context data from the cache.
        
        Args:
            scope: Context scope
            context_type: Type of context data
            context_id: Optional context ID to retrieve specific context
            
        Returns:
            Context data, or None if not found
        """
        scope_value = scope.value
        if scope_value not in self.context_cache:
            return None
            
        if context_id is not None:
            # Get specific context
            cache_key = f"{context_type}:{context_id}"
            context = self.context_cache[scope_value].get(cache_key)
            if context is not None:
                return context.data.copy()
                
            return None
            
        # Get all context of the specified type
        result = {}
        for key, context in self.context_cache[scope_value].items():
            if key.startswith(f"{context_type}:"):
                result.update(context.data)
                
        return result if result else None
        
    def get_all_context(self, scope: ContextScope) -> Dict[str, Dict[str, Any]]:
        """
        Get all context data for a scope.
        
        Args:
            scope: Context scope
            
        Returns:
            Dictionary of context type to context data
        """
        scope_value = scope.value
        if scope_value not in self.context_cache:
            return {}
            
        result = {}
        for key, context in self.context_cache[scope_value].items():
            context_type = context.type
            if context_type not in result:
                result[context_type] = {}
                
            result[context_type].update(context.data)
            
        return result
        
    def clear_context(self, scope: ContextScope, context_type: Optional[str] = None, context_id: Optional[str] = None) -> bool:
        """
        Clear context data from the cache.
        
        Args:
            scope: Context scope
            context_type: Optional type of context data to clear
            context_id: Optional context ID to clear specific context
            
        Returns:
            True if context was cleared, False otherwise
        """
        scope_value = scope.value
        if scope_value not in self.context_cache:
            return False
            
        if context_id is not None and context_type is not None:
            # Clear specific context
            cache_key = f"{context_type}:{context_id}"
            if cache_key in self.context_cache[scope_value]:
                del self.context_cache[scope_value][cache_key]
                return True
                
            return False
            
        if context_type is not None:
            # Clear all context of the specified type
            keys_to_remove = []
            for key in self.context_cache[scope_value]:
                if key.startswith(f"{context_type}:"):
                    keys_to_remove.append(key)
                    
            for key in keys_to_remove:
                del self.context_cache[scope_value][key]
                
            return len(keys_to_remove) > 0
            
        # Clear all context for the scope
        self.context_cache[scope_value] = {}
        return True
        
    def register_context_handler(self, scope: Union[ContextScope, str], context_type: str, 
                               handler: Callable[[ContextData], None]) -> bool:
        """
        Register a handler for a specific context type.
        
        Args:
            scope: Context scope, or "*" for all scopes
            context_type: Context type to handle, or "*" for all types
            handler: Handler function
            
        Returns:
            True if the handler was registered, False otherwise
        """
        scope_value = scope.value if isinstance(scope, ContextScope) else scope
        handler_key = f"{scope_value}.{context_type}"
        
        if handler_key not in self.context_handlers:
            self.context_handlers[handler_key] = []
            
        self.context_handlers[handler_key].append(handler)
        self.logger.debug(f"Registered context handler for {handler_key}")
        
        return True
        
    def unregister_context_handler(self, scope: Union[ContextScope, str], context_type: str,
                                 handler: Callable[[ContextData], None]) -> bool:
        """
        Unregister a context handler.
        
        Args:
            scope: Context scope, or "*" for all scopes
            context_type: Context type the handler was registered for, or "*" for all types
            handler: Handler function to unregister
            
        Returns:
            True if the handler was unregistered, False otherwise
        """
        scope_value = scope.value if isinstance(scope, ContextScope) else scope
        handler_key = f"{scope_value}.{context_type}"
        
        if handler_key not in self.context_handlers:
            return False
            
        if handler in self.context_handlers[handler_key]:
            self.context_handlers[handler_key].remove(handler)
            self.logger.debug(f"Unregistered context handler for {handler_key}")
            
            # Clean up empty handler lists
            if not self.context_handlers[handler_key]:
                del self.context_handlers[handler_key]
                
            return True
            
        return False
        
    def cleanup_expired_context(self) -> int:
        """
        Clean up expired context data.
        
        Returns:
            Number of expired context items removed
        """
        current_time = time.time()
        expired_count = 0
        
        for scope in self.context_cache:
            keys_to_remove = []
            
            for key, context in self.context_cache[scope].items():
                if context.ttl is not None:
                    elapsed = current_time - context.timestamp
                    if elapsed > context.ttl:
                        keys_to_remove.append(key)
                        
            for key in keys_to_remove:
                del self.context_cache[scope][key]
                expired_count += 1
                
        if expired_count > 0:
            self.logger.debug(f"Cleaned up {expired_count} expired context items")
            
        return expired_count

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create Cross-Layer Integration module
    from ..cross_layer_integration.cross_layer_integration import CrossLayerIntegration
    cross_layer_integration = CrossLayerIntegration()
    cross_layer_integration.start()
    
    # Create Real-Time Context Bus
    context_bus = RealTimeContextBus(cross_layer_integration)
    context_bus.start()
    
    # Register context handler
    def handle_user_context(context_data):
        print(f"Received user context: {context_data.data}")
        
    context_bus.register_context_handler(ContextScope.USER, "preferences", handle_user_context)
    
    # Publish context
    context_bus.publish_context(
        scope=ContextScope.USER,
        context_type="preferences",
        context_data={
            "theme": "dark",
            "notifications": True,
            "language": "en"
        }
    )
    
    # Get context
    user_prefs = context_bus.get_context(ContextScope.USER, "preferences")
    print(f"User preferences: {user_prefs}")
    
    # Clean up
    context_bus.stop()
    cross_layer_integration.stop()
