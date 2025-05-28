"""
Context Integration Bridge for Context Engine

This module provides integration between the Context Engine and other layers/components
of the Industriverse system. It implements the bidirectional flow of context data
between the UI/UX Layer and other layers through the MCP and A2A protocols.

The Context Integration Bridge:
1. Connects the Context Engine to other system layers
2. Translates context data to/from MCP and A2A formats
3. Synchronizes context across distributed components
4. Provides an API for cross-layer context operations
5. Manages context-based interactions with external systems

Author: Manus
"""

import logging
import json
from typing import Dict, List, Optional, Any, Tuple, Callable
import time
import threading
import uuid

# Local imports
from .context_awareness_engine import ContextType, ContextPriority
from .context_rules_engine import ContextRulesEngine
from ..protocol_bridge.protocol_bridge import ProtocolBridge
from ..cross_layer_integration.real_time_context_bus import RealTimeContextBus

# Configure logging
logger = logging.getLogger(__name__)

class ContextIntegrationBridge:
    """
    Provides integration between the Context Engine and other layers/components.
    
    This class is responsible for implementing the bidirectional flow of context data
    between the UI/UX Layer and other layers through the MCP and A2A protocols.
    """
    
    def __init__(
        self,
        context_rules_engine: ContextRulesEngine,
        protocol_bridge: ProtocolBridge,
        real_time_context_bus: RealTimeContextBus
    ):
        """
        Initialize the Context Integration Bridge.
        
        Args:
            context_rules_engine: The Context Rules Engine instance
            protocol_bridge: The Protocol Bridge instance for MCP/A2A communication
            real_time_context_bus: The Real-Time Context Bus instance
        """
        self.context_rules_engine = context_rules_engine
        self.protocol_bridge = protocol_bridge
        self.real_time_context_bus = real_time_context_bus
        
        # Context subscriptions
        self.context_subscriptions = {}
        
        # Context publication topics
        self.publication_topics = {
            ContextType.USER.value: "context.user",
            ContextType.DEVICE.value: "context.device",
            ContextType.ENVIRONMENT.value: "context.environment",
            ContextType.TASK.value: "context.task",
            ContextType.SYSTEM.value: "context.system",
            ContextType.SOCIAL.value: "context.social",
            ContextType.SECURITY.value: "context.security"
        }
        
        # Context data cache
        self.context_cache = {}
        
        # Last publication timestamps
        self.last_publication = {}
        
        # Publication throttling intervals (in seconds)
        self.publication_throttle = {
            ContextType.USER.value: 5,
            ContextType.DEVICE.value: 2,
            ContextType.ENVIRONMENT.value: 10,
            ContextType.TASK.value: 1,
            ContextType.SYSTEM.value: 3,
            ContextType.SOCIAL.value: 5,
            ContextType.SECURITY.value: 5
        }
        
        # Register as context rule listener
        self.context_rules_engine.register_rule_listener(self._handle_rule_execution)
        
        # Register as context bus subscriber
        self.real_time_context_bus.subscribe("context.*", self._handle_context_message)
        
        # Start context publication thread
        self.publication_thread_running = True
        self.publication_thread = threading.Thread(target=self._context_publication_thread)
        self.publication_thread.daemon = True
        self.publication_thread.start()
        
        logger.info("Context Integration Bridge initialized")
    
    def _context_publication_thread(self) -> None:
        """Background thread for periodic context publication."""
        while self.publication_thread_running:
            current_time = time.time()
            
            # Check each context type for publication
            for context_type in ContextType:
                type_value = context_type.value
                last_pub = self.last_publication.get(type_value, 0)
                throttle_interval = self.publication_throttle[type_value]
                
                # If it's time to publish this context type
                if current_time - last_pub > throttle_interval:
                    # Check if we have cached data for this type
                    if type_value in self.context_cache:
                        self._publish_context(type_value, self.context_cache[type_value])
                        self.last_publication[type_value] = current_time
            
            # Sleep for a short interval
            time.sleep(0.5)
    
    def _handle_rule_execution(self, event: Dict) -> None:
        """
        Handle rule execution events.
        
        Args:
            event: Rule execution event
        """
        # Check if this rule execution should be shared with other layers
        rule_type = event.get("rule_type")
        
        # Share inference and adaptation results
        if rule_type in ["inference", "adaptation"]:
            # Extract context updates from action results
            context_updates = {}
            
            for action_type, action_result in event.get("action_results", {}).items():
                if action_type == "infer_context":
                    context_type = action_result.get("context_type")
                    inferred_data = action_result.get("inferred_data", {})
                    
                    if context_type:
                        if context_type not in context_updates:
                            context_updates[context_type] = {}
                        
                        context_updates[context_type].update(inferred_data)
                
                elif action_type == "set_context_value":
                    context_type = action_result.get("context_type")
                    path = action_result.get("path")
                    value = action_result.get("value")
                    
                    if context_type and path:
                        if context_type not in context_updates:
                            context_updates[context_type] = {}
                        
                        # Handle nested paths
                        parts = path.split(".")
                        if len(parts) == 1:
                            context_updates[context_type][path] = value
                        else:
                            # For nested paths, we need the full context object
                            # In a real implementation, this would be more sophisticated
                            # For now, we'll just use a simple approach
                            context_updates[context_type][parts[0]] = {parts[1]: value}
            
            # Update context cache
            for context_type, updates in context_updates.items():
                if context_type not in self.context_cache:
                    self.context_cache[context_type] = {}
                
                self.context_cache[context_type].update(updates)
            
            # Publish context updates
            for context_type, updates in context_updates.items():
                self._publish_context(context_type, updates)
                self.last_publication[context_type] = time.time()
    
    def _handle_context_message(self, topic: str, message: Dict) -> None:
        """
        Handle context messages from the Real-Time Context Bus.
        
        Args:
            topic: Message topic
            message: Message content
        """
        # Extract context type from topic
        parts = topic.split(".")
        if len(parts) >= 2:
            context_type = parts[1]
            
            # Only process if it's a valid context type
            if context_type in [ct.value for ct in ContextType]:
                # Extract context data
                context_data = message.get("data", {})
                
                # Update context cache
                if context_type not in self.context_cache:
                    self.context_cache[context_type] = {}
                
                self.context_cache[context_type].update(context_data)
                
                # Notify subscribers
                self._notify_subscribers(context_type, context_data)
    
    def _publish_context(self, context_type: str, context_data: Dict) -> None:
        """
        Publish context data to other layers.
        
        Args:
            context_type: The type of context to publish
            context_data: The context data to publish
        """
        # Get publication topic
        topic = self.publication_topics.get(context_type)
        
        if not topic:
            logger.warning(f"No publication topic defined for context type: {context_type}")
            return
        
        # Create message
        message = {
            "type": "context_update",
            "context_type": context_type,
            "timestamp": time.time(),
            "data": context_data,
            "source": "ui_ux_layer"
        }
        
        # Publish to Real-Time Context Bus
        self.real_time_context_bus.publish(topic, message)
        
        # Publish to other layers via MCP
        self._publish_via_mcp(context_type, context_data)
        
        logger.debug(f"Published context data for {context_type}")
    
    def _publish_via_mcp(self, context_type: str, context_data: Dict) -> None:
        """
        Publish context data to other layers via MCP.
        
        Args:
            context_type: The type of context to publish
            context_data: The context data to publish
        """
        # Create MCP message
        mcp_message = {
            "protocol": "mcp",
            "version": "1.0",
            "message_id": str(uuid.uuid4()),
            "message_type": "context_update",
            "source": "ui_ux_layer",
            "destination": "all",
            "timestamp": time.time(),
            "payload": {
                "context_type": context_type,
                "context_data": context_data
            }
        }
        
        # Send via Protocol Bridge
        try:
            self.protocol_bridge.send_mcp_message(mcp_message)
            logger.debug(f"Published context data via MCP for {context_type}")
        except Exception as e:
            logger.error(f"Failed to publish context data via MCP: {str(e)}")
    
    def _notify_subscribers(self, context_type: str, context_data: Dict) -> None:
        """
        Notify subscribers of context updates.
        
        Args:
            context_type: The type of context that was updated
            context_data: The updated context data
        """
        # Get subscribers for this context type
        subscribers = self.context_subscriptions.get(context_type, [])
        
        # Notify each subscriber
        for subscriber in subscribers:
            try:
                subscriber(context_type, context_data)
            except Exception as e:
                logger.error(f"Error notifying context subscriber: {str(e)}")
    
    def subscribe_to_context(self, context_type: str, callback: Callable) -> bool:
        """
        Subscribe to context updates.
        
        Args:
            context_type: The type of context to subscribe to
            callback: Function to call with context updates
            
        Returns:
            Boolean indicating success
        """
        if context_type not in self.context_subscriptions:
            self.context_subscriptions[context_type] = []
        
        if callback not in self.context_subscriptions[context_type]:
            self.context_subscriptions[context_type].append(callback)
            logger.info(f"Subscribed to context updates for {context_type}")
            return True
        
        return False
    
    def unsubscribe_from_context(self, context_type: str, callback: Callable) -> bool:
        """
        Unsubscribe from context updates.
        
        Args:
            context_type: The type of context to unsubscribe from
            callback: Function to unsubscribe
            
        Returns:
            Boolean indicating success
        """
        if context_type in self.context_subscriptions and callback in self.context_subscriptions[context_type]:
            self.context_subscriptions[context_type].remove(callback)
            logger.info(f"Unsubscribed from context updates for {context_type}")
            return True
        
        return False
    
    def get_cached_context(self, context_type: str = None) -> Dict:
        """
        Get cached context data.
        
        Args:
            context_type: Optional specific context type to get
            
        Returns:
            Dictionary of cached context data
        """
        if context_type:
            return self.context_cache.get(context_type, {})
        else:
            return self.context_cache
    
    def update_context(self, context_type: str, context_data: Dict) -> bool:
        """
        Update context data and publish to other layers.
        
        Args:
            context_type: The type of context to update
            context_data: The context data to update
            
        Returns:
            Boolean indicating success
        """
        # Update context cache
        if context_type not in self.context_cache:
            self.context_cache[context_type] = {}
        
        self.context_cache[context_type].update(context_data)
        
        # Publish context update
        self._publish_context(context_type, context_data)
        self.last_publication[context_type] = time.time()
        
        # Notify subscribers
        self._notify_subscribers(context_type, context_data)
        
        return True
    
    def set_publication_throttle(self, context_type: str, interval_seconds: int) -> bool:
        """
        Set publication throttling interval for a context type.
        
        Args:
            context_type: The type of context to set throttling for
            interval_seconds: Throttling interval in seconds
            
        Returns:
            Boolean indicating success
        """
        if context_type in self.publication_throttle:
            self.publication_throttle[context_type] = interval_seconds
            logger.info(f"Set publication throttle for {context_type} to {interval_seconds} seconds")
            return True
        
        return False
    
    def request_context_from_layer(self, layer_name: str, context_type: str) -> bool:
        """
        Request context data from another layer.
        
        Args:
            layer_name: The name of the layer to request from
            context_type: The type of context to request
            
        Returns:
            Boolean indicating success
        """
        # Create MCP message
        mcp_message = {
            "protocol": "mcp",
            "version": "1.0",
            "message_id": str(uuid.uuid4()),
            "message_type": "context_request",
            "source": "ui_ux_layer",
            "destination": layer_name,
            "timestamp": time.time(),
            "payload": {
                "context_type": context_type
            }
        }
        
        # Send via Protocol Bridge
        try:
            self.protocol_bridge.send_mcp_message(mcp_message)
            logger.info(f"Requested context data for {context_type} from {layer_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to request context data: {str(e)}")
            return False
    
    def handle_mcp_message(self, message: Dict) -> None:
        """
        Handle incoming MCP messages.
        
        Args:
            message: The MCP message to handle
        """
        message_type = message.get("message_type")
        
        # Handle context update messages
        if message_type == "context_update":
            payload = message.get("payload", {})
            context_type = payload.get("context_type")
            context_data = payload.get("context_data", {})
            
            if context_type:
                # Update context cache
                if context_type not in self.context_cache:
                    self.context_cache[context_type] = {}
                
                self.context_cache[context_type].update(context_data)
                
                # Notify subscribers
                self._notify_subscribers(context_type, context_data)
                
                logger.debug(f"Received context update via MCP for {context_type}")
        
        # Handle context request messages
        elif message_type == "context_request":
            payload = message.get("payload", {})
            context_type = payload.get("context_type")
            source = message.get("source")
            
            if context_type and source:
                # Get requested context data
                context_data = self.get_cached_context(context_type)
                
                # Send response
                response = {
                    "protocol": "mcp",
                    "version": "1.0",
                    "message_id": str(uuid.uuid4()),
                    "message_type": "context_response",
                    "source": "ui_ux_layer",
                    "destination": source,
                    "timestamp": time.time(),
                    "in_response_to": message.get("message_id"),
                    "payload": {
                        "context_type": context_type,
                        "context_data": context_data
                    }
                }
                
                # Send via Protocol Bridge
                try:
                    self.protocol_bridge.send_mcp_message(response)
                    logger.debug(f"Sent context response to {source} for {context_type}")
                except Exception as e:
                    logger.error(f"Failed to send context response: {str(e)}")
    
    def handle_a2a_message(self, message: Dict) -> None:
        """
        Handle incoming A2A messages.
        
        Args:
            message: The A2A message to handle
        """
        message_type = message.get("type")
        
        # Handle context-related A2A messages
        if message_type == "context_request":
            context_type = message.get("context_type")
            agent_id = message.get("agent_id")
            
            if context_type and agent_id:
                # Get requested context data
                context_data = self.get_cached_context(context_type)
                
                # Send response
                response = {
                    "protocol": "a2a",
                    "version": "1.0",
                    "message_id": str(uuid.uuid4()),
                    "type": "context_response",
                    "source_agent_id": "ui_ux_layer",
                    "target_agent_id": agent_id,
                    "timestamp": time.time(),
                    "in_response_to": message.get("message_id"),
                    "context_type": context_type,
                    "context_data": context_data
                }
                
                # Send via Protocol Bridge
                try:
                    self.protocol_bridge.send_a2a_message(response)
                    logger.debug(f"Sent context response to agent {agent_id} for {context_type}")
                except Exception as e:
                    logger.error(f"Failed to send A2A context response: {str(e)}")
    
    def send_context_to_agent(self, agent_id: str, context_type: str, context_data: Dict) -> bool:
        """
        Send context data to a specific agent via A2A.
        
        Args:
            agent_id: The ID of the agent to send to
            context_type: The type of context to send
            context_data: The context data to send
            
        Returns:
            Boolean indicating success
        """
        # Create A2A message
        a2a_message = {
            "protocol": "a2a",
            "version": "1.0",
            "message_id": str(uuid.uuid4()),
            "type": "context_update",
            "source_agent_id": "ui_ux_layer",
            "target_agent_id": agent_id,
            "timestamp": time.time(),
            "context_type": context_type,
            "context_data": context_data
        }
        
        # Send via Protocol Bridge
        try:
            self.protocol_bridge.send_a2a_message(a2a_message)
            logger.info(f"Sent context data to agent {agent_id} for {context_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to send context data to agent: {str(e)}")
            return False
    
    def shutdown(self) -> None:
        """Shutdown the Context Integration Bridge."""
        # Stop publication thread
        self.publication_thread_running = False
        if self.publication_thread.is_alive():
            self.publication_thread.join(timeout=2)
        
        # Unregister as context rule listener
        self.context_rules_engine.unregister_rule_listener(self._handle_rule_execution)
        
        # Unregister as context bus subscriber
        self.real_time_context_bus.unsubscribe("context.*", self._handle_context_message)
        
        logger.info("Context Integration Bridge shutdown")
"""
