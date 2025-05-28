"""
MCP (Mesh Communication Protocol) Handler for Industriverse Protocol Layer

This module implements the MCP protocol handler for the Industriverse Protocol Layer.
It provides services for mesh-based communication between protocol components,
with support for advanced features like intent-aware routing and semantic compression.

The MCP handler ensures:
1. Reliable message delivery across the protocol mesh
2. Intelligent routing based on message content and intent
3. Semantic compression for efficient communication
4. Protocol-native integration with other components
"""

import uuid
import json
import asyncio
import logging
import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.agent_interface import AgentCard
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)
from protocols.discovery_service import DiscoveryService, AsyncDiscoveryService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPHandler(ProtocolService):
    """
    Handler for the Mesh Communication Protocol (MCP).
    
    The MCPHandler provides services for mesh-based communication between
    protocol components, with support for advanced features like intent-aware
    routing and semantic compression.
    """
    
    def __init__(
        self,
        service_id: str = None,
        discovery_service: DiscoveryService = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize an MCP handler.
        
        Args:
            service_id: Unique identifier for this service. If None, a UUID is generated.
            discovery_service: Discovery service for component lookup.
            config: Configuration parameters for the handler.
        """
        super().__init__(service_id or str(uuid.uuid4()), "mcp_handler")
        self.discovery_service = discovery_service
        self.config = config or {}
        self.routes = {}
        self.message_handlers = {}
        self.intent_handlers = {}
        self.semantic_compressors = {}
        self.message_queue = asyncio.Queue()
        self.processing_task = None
        self.is_running = False
        self.logger = logging.getLogger(f"{__name__}.MCPHandler.{self.component_id[:8]}")
        self.logger.info(f"MCP Handler initialized with ID {self.component_id}")
        
        # Register default message handlers
        self.register_message_handler("request", self._handle_request)
        self.register_message_handler("response", self._handle_response)
        self.register_message_handler("event", self._handle_event)
        self.register_message_handler("command", self._handle_command)
        self.register_message_handler("query", self._handle_query)
        self.register_message_handler("error", self._handle_error)
        
        # Add capabilities
        self.add_capability("mesh_communication", "Mesh-based communication between components")
        self.add_capability("intent_routing", "Intent-aware message routing")
        self.add_capability("semantic_compression", "Semantic compression for efficient communication")
        self.add_capability("protocol_translation", "Translation between different protocols")
    
    def register_message_handler(
        self,
        message_type: str,
        handler: Callable[[BaseMessage], Optional[BaseMessage]]
    ) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: The type of message to handle.
            handler: The function that handles messages of this type.
        """
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")
    
    def register_intent_handler(
        self,
        intent: str,
        handler: Callable[[BaseMessage], Optional[str]]
    ) -> None:
        """
        Register a handler for a specific intent.
        
        Args:
            intent: The intent to handle.
            handler: The function that determines the routing for messages with this intent.
        """
        self.intent_handlers[intent] = handler
        self.logger.debug(f"Registered handler for intent: {intent}")
    
    def register_semantic_compressor(
        self,
        content_type: str,
        compressor: Callable[[Any], Any],
        decompressor: Callable[[Any], Any]
    ) -> None:
        """
        Register a semantic compressor for a specific content type.
        
        Args:
            content_type: The content type to compress/decompress.
            compressor: The function that compresses content.
            decompressor: The function that decompresses content.
        """
        self.semantic_compressors[content_type] = {
            "compress": compressor,
            "decompress": decompressor
        }
        self.logger.debug(f"Registered semantic compressor for content type: {content_type}")
    
    def add_route(self, source: str, destination: str, route_info: Dict[str, Any] = None) -> None:
        """
        Add a route between two components.
        
        Args:
            source: The source component ID.
            destination: The destination component ID.
            route_info: Additional information about the route.
        """
        if source not in self.routes:
            self.routes[source] = {}
        
        self.routes[source][destination] = route_info or {}
        self.logger.debug(f"Added route from {source} to {destination}")
    
    def get_route(self, source: str, destination: str) -> Optional[Dict[str, Any]]:
        """
        Get route information between two components.
        
        Args:
            source: The source component ID.
            destination: The destination component ID.
            
        Returns:
            Route information, or None if no route exists.
        """
        if source in self.routes and destination in self.routes[source]:
            return self.routes[source][destination]
        return None
    
    def send_message(self, message: BaseMessage) -> Optional[BaseMessage]:
        """
        Send a message through the mesh.
        
        Args:
            message: The message to send.
            
        Returns:
            The response message, if any.
        """
        if not message.validate():
            self.logger.error("Invalid message")
            return MessageFactory.create_error(
                "invalid_message",
                "The message is invalid",
                related_message_id=message.message_id
            )
        
        # Add this component as a hop
        message.add_hop(self.component_id)
        
        # Check if we have a direct route
        if message.receiver_id and message.sender_id:
            route = self.get_route(message.sender_id, message.receiver_id)
            if route:
                self.logger.debug(f"Using direct route from {message.sender_id} to {message.receiver_id}")
                return self._deliver_message(message)
        
        # Check for intent-based routing
        if "intent" in message.metadata:
            intent = message.metadata["intent"]
            if intent in self.intent_handlers:
                self.logger.debug(f"Using intent-based routing for intent: {intent}")
                receiver_id = self.intent_handlers[intent](message)
                if receiver_id:
                    message.receiver_id = receiver_id
                    return self._deliver_message(message)
        
        # If we have a receiver_id but no route, try to deliver directly
        if message.receiver_id:
            self.logger.debug(f"Attempting direct delivery to {message.receiver_id}")
            return self._deliver_message(message)
        
        # If all else fails, broadcast to all components of the appropriate type
        if "target_type" in message.metadata:
            target_type = message.metadata["target_type"]
            self.logger.debug(f"Broadcasting to all components of type: {target_type}")
            return self._broadcast_message(message, target_type)
        
        self.logger.error("Unable to route message")
        return MessageFactory.create_error(
            "routing_error",
            "Unable to determine message route",
            related_message_id=message.message_id
        )
    
    def _deliver_message(self, message: BaseMessage) -> Optional[BaseMessage]:
        """
        Deliver a message to its intended recipient.
        
        Args:
            message: The message to deliver.
            
        Returns:
            The response message, if any.
        """
        if not message.receiver_id:
            self.logger.error("Message has no receiver_id")
            return MessageFactory.create_error(
                "delivery_error",
                "Message has no receiver_id",
                related_message_id=message.message_id
            )
        
        # Apply semantic compression if available
        if "content_type" in message.metadata:
            content_type = message.metadata["content_type"]
            if content_type in self.semantic_compressors:
                self.logger.debug(f"Applying semantic compression for content type: {content_type}")
                compressor = self.semantic_compressors[content_type]["compress"]
                
                if hasattr(message, "payload") and message.payload is not None:
                    message.metadata["compressed"] = True
                    message.payload = compressor(message.payload)
        
        # Find the component
        if self.discovery_service:
            component = self.discovery_service.get_component(message.receiver_id)
            if component:
                self.logger.debug(f"Delivering message to component {message.receiver_id}")
                
                # Decompress payload if necessary
                if "content_type" in message.metadata and message.metadata.get("compressed", False):
                    content_type = message.metadata["content_type"]
                    if content_type in self.semantic_compressors:
                        self.logger.debug(f"Applying semantic decompression for content type: {content_type}")
                        decompressor = self.semantic_compressors[content_type]["decompress"]
                        
                        if hasattr(message, "payload") and message.payload is not None:
                            message.payload = decompressor(message.payload)
                            message.metadata["compressed"] = False
                
                # Process the message
                try:
                    response = component.process_message(message.to_dict())
                    if response:
                        if isinstance(response, dict) and "message_id" in response:
                            return MessageFactory.create_from_dict(response)
                        else:
                            return MessageFactory.create_response(
                                message.message_id,
                                MessageStatus.SUCCESS,
                                response,
                                sender_id=message.receiver_id,
                                receiver_id=message.sender_id
                            )
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    return MessageFactory.create_error(
                        "processing_error",
                        f"Error processing message: {str(e)}",
                        related_message_id=message.message_id,
                        sender_id=message.receiver_id,
                        receiver_id=message.sender_id
                    )
            else:
                self.logger.error(f"Component not found: {message.receiver_id}")
                return MessageFactory.create_error(
                    "component_not_found",
                    f"Component not found: {message.receiver_id}",
                    related_message_id=message.message_id
                )
        else:
            self.logger.error("No discovery service available")
            return MessageFactory.create_error(
                "no_discovery_service",
                "No discovery service available",
                related_message_id=message.message_id
            )
    
    def _broadcast_message(self, message: BaseMessage, target_type: str) -> List[BaseMessage]:
        """
        Broadcast a message to all components of a specific type.
        
        Args:
            message: The message to broadcast.
            target_type: The type of components to broadcast to.
            
        Returns:
            A list of response messages.
        """
        responses = []
        
        if self.discovery_service:
            components = self.discovery_service.find_components_by_type(target_type)
            self.logger.debug(f"Broadcasting message to {len(components)} components of type {target_type}")
            
            for component in components:
                broadcast_message = MessageFactory.create_from_dict(message.to_dict())
                broadcast_message.receiver_id = component.component_id
                response = self._deliver_message(broadcast_message)
                if response:
                    responses.append(response)
        else:
            self.logger.error("No discovery service available")
            error = MessageFactory.create_error(
                "no_discovery_service",
                "No discovery service available",
                related_message_id=message.message_id
            )
            responses.append(error)
        
        return responses
    
    def _handle_request(self, message: RequestMessage) -> Optional[ResponseMessage]:
        """
        Handle a request message.
        
        Args:
            message: The request message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling request message: {message.operation}")
        
        # Check if this is a request for this component
        if message.receiver_id == self.component_id:
            if message.operation == "get_routes":
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    self.routes,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            elif message.operation == "add_route":
                if "source" in message.payload and "destination" in message.payload:
                    self.add_route(
                        message.payload["source"],
                        message.payload["destination"],
                        message.payload.get("route_info")
                    )
                    return MessageFactory.create_response(
                        message.message_id,
                        MessageStatus.SUCCESS,
                        {"status": "route_added"},
                        sender_id=self.component_id,
                        receiver_id=message.sender_id
                    )
                else:
                    return MessageFactory.create_error(
                        "invalid_payload",
                        "Payload must contain 'source' and 'destination'",
                        related_message_id=message.message_id,
                        sender_id=self.component_id,
                        receiver_id=message.sender_id
                    )
            else:
                return MessageFactory.create_error(
                    "unsupported_operation",
                    f"Unsupported operation: {message.operation}",
                    related_message_id=message.message_id,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
        
        # Otherwise, route the message
        return self.send_message(message)
    
    def _handle_response(self, message: ResponseMessage) -> Optional[BaseMessage]:
        """
        Handle a response message.
        
        Args:
            message: The response message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling response message for request {message.request_id}")
        
        # Route the message to its destination
        return self.send_message(message)
    
    def _handle_event(self, message: EventMessage) -> Optional[BaseMessage]:
        """
        Handle an event message.
        
        Args:
            message: The event message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling event message: {message.event_type}")
        
        # Route the message to its destination
        return self.send_message(message)
    
    def _handle_command(self, message: CommandMessage) -> Optional[BaseMessage]:
        """
        Handle a command message.
        
        Args:
            message: The command message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling command message: {message.command}")
        
        # Check if this is a command for this component
        if message.receiver_id == self.component_id:
            if message.command == "start":
                self.start()
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    {"status": "started"},
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            elif message.command == "stop":
                self.stop()
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    {"status": "stopped"},
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            else:
                return MessageFactory.create_error(
                    "unsupported_command",
                    f"Unsupported command: {message.command}",
                    related_message_id=message.message_id,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
        
        # Otherwise, route the message
        return self.send_message(message)
    
    def _handle_query(self, message: QueryMessage) -> Optional[BaseMessage]:
        """
        Handle a query message.
        
        Args:
            message: The query message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling query message: {message.query}")
        
        # Check if this is a query for this component
        if message.receiver_id == self.component_id:
            if message.query == "status":
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    {
                        "status": "running" if self.is_running else "stopped",
                        "queue_size": self.message_queue.qsize() if self.message_queue else 0,
                        "routes_count": sum(len(routes) for routes in self.routes.values()),
                        "handlers_count": len(self.message_handlers),
                        "intent_handlers_count": len(self.intent_handlers),
                        "semantic_compressors_count": len(self.semantic_compressors)
                    },
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            elif message.query == "routes":
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    self.routes,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            else:
                return MessageFactory.create_error(
                    "unsupported_query",
                    f"Unsupported query: {message.query}",
                    related_message_id=message.message_id,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
        
        # Otherwise, route the message
        return self.send_message(message)
    
    def _handle_error(self, message: ErrorMessage) -> Optional[BaseMessage]:
        """
        Handle an error message.
        
        Args:
            message: The error message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling error message: {message.error_code}")
        
        # Log the error
        self.logger.error(f"Error message received: {message.error_code} - {message.error_message}")
        
        # Route the message to its destination
        return self.send_message(message)
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
        """
        if not isinstance(message, dict):
            self.logger.error("Message must be a dictionary")
            return MessageFactory.create_error(
                "invalid_message",
                "Message must be a dictionary"
            ).to_dict()
        
        # Convert to appropriate message type
        if "message_type" in message:
            message_obj = MessageFactory.create_from_dict(message)
            
            # Handle the message based on its type
            if message_obj.message_type in self.message_handlers:
                handler = self.message_handlers[message_obj.message_type]
                response = handler(message_obj)
                if response:
                    return response.to_dict()
                else:
                    return MessageFactory.create_response(
                        message_obj.message_id,
                        MessageStatus.SUCCESS,
                        {"status": "processed"},
                        sender_id=self.component_id,
                        receiver_id=message_obj.sender_id
                    ).to_dict()
            else:
                self.logger.error(f"Unsupported message type: {message_obj.message_type}")
                return MessageFactory.create_error(
                    "unsupported_message_type",
                    f"Unsupported message type: {message_obj.message_type}",
                    related_message_id=message_obj.message_id,
                    sender_id=self.component_id,
                    receiver_id=message_obj.sender_id
                ).to_dict()
        else:
            self.logger.error("Message must have a 'message_type' field")
            return MessageFactory.create_error(
                "invalid_message",
                "Message must have a 'message_type' field"
            ).to_dict()
    
    async def _process_queue(self) -> None:
        """Process messages from the queue."""
        self.logger.info("Message queue processor started")
        
        while self.is_running:
            try:
                message = await self.message_queue.get()
                self.logger.debug(f"Processing message from queue: {message.message_id}")
                
                # Process the message
                response = self.process_message(message.to_dict())
                
                # Mark the task as done
                self.message_queue.task_done()
                
                self.logger.debug(f"Message processed: {message.message_id}")
            except asyncio.CancelledError:
                self.logger.info("Message queue processor cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error processing message from queue: {e}")
    
    def start(self) -> None:
        """Start the MCP handler."""
        if self.is_running:
            self.logger.warning("MCP Handler is already running")
            return
        
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_queue())
        self.logger.info("MCP Handler started")
    
    def stop(self) -> None:
        """Stop the MCP handler."""
        if not self.is_running:
            self.logger.warning("MCP Handler is not running")
            return
        
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
        self.logger.info("MCP Handler stopped")
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check.
        
        Returns:
            A dictionary containing health check results.
        """
        return {
            "status": "healthy" if self.is_running else "stopped",
            "queue_size": self.message_queue.qsize() if self.message_queue else 0,
            "routes_count": sum(len(routes) for routes in self.routes.values()),
            "handlers_count": len(self.message_handlers),
            "intent_handlers_count": len(self.intent_handlers),
            "semantic_compressors_count": len(self.semantic_compressors)
        }
    
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the component manifest.
        
        Returns:
            A dictionary containing the component manifest.
        """
        manifest = super().get_manifest()
        manifest.update({
            "routes_count": sum(len(routes) for routes in self.routes.values()),
            "handlers_count": len(self.message_handlers),
            "intent_handlers_count": len(self.intent_handlers),
            "semantic_compressors_count": len(self.semantic_compressors),
            "is_running": self.is_running
        })
        return manifest


class AsyncMCPHandler(ProtocolService):
    """
    Asynchronous handler for the Mesh Communication Protocol (MCP).
    
    This class provides the same functionality as MCPHandler but with
    asynchronous methods for high-performance protocol handling.
    """
    
    def __init__(
        self,
        service_id: str = None,
        discovery_service: AsyncDiscoveryService = None,
        config: Dict[str, Any] = None
    ):
        """
        Initialize an asynchronous MCP handler.
        
        Args:
            service_id: Unique identifier for this service. If None, a UUID is generated.
            discovery_service: Asynchronous discovery service for component lookup.
            config: Configuration parameters for the handler.
        """
        super().__init__(service_id or str(uuid.uuid4()), "async_mcp_handler")
        self.discovery_service = discovery_service
        self.config = config or {}
        self.routes = {}
        self.message_handlers = {}
        self.intent_handlers = {}
        self.semantic_compressors = {}
        self.message_queue = asyncio.Queue()
        self.processing_task = None
        self.is_running = False
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{__name__}.AsyncMCPHandler.{self.component_id[:8]}")
        self.logger.info(f"Async MCP Handler initialized with ID {self.component_id}")
        
        # Register default message handlers
        self.register_message_handler("request", self._handle_request)
        self.register_message_handler("response", self._handle_response)
        self.register_message_handler("event", self._handle_event)
        self.register_message_handler("command", self._handle_command)
        self.register_message_handler("query", self._handle_query)
        self.register_message_handler("error", self._handle_error)
        
        # Add capabilities
        self.add_capability("mesh_communication", "Mesh-based communication between components")
        self.add_capability("intent_routing", "Intent-aware message routing")
        self.add_capability("semantic_compression", "Semantic compression for efficient communication")
        self.add_capability("protocol_translation", "Translation between different protocols")
    
    def register_message_handler(
        self,
        message_type: str,
        handler: Callable[[BaseMessage], Awaitable[Optional[BaseMessage]]]
    ) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: The type of message to handle.
            handler: The async function that handles messages of this type.
        """
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")
    
    def register_intent_handler(
        self,
        intent: str,
        handler: Callable[[BaseMessage], Awaitable[Optional[str]]]
    ) -> None:
        """
        Register a handler for a specific intent.
        
        Args:
            intent: The intent to handle.
            handler: The async function that determines the routing for messages with this intent.
        """
        self.intent_handlers[intent] = handler
        self.logger.debug(f"Registered handler for intent: {intent}")
    
    def register_semantic_compressor(
        self,
        content_type: str,
        compressor: Callable[[Any], Any],
        decompressor: Callable[[Any], Any]
    ) -> None:
        """
        Register a semantic compressor for a specific content type.
        
        Args:
            content_type: The content type to compress/decompress.
            compressor: The function that compresses content.
            decompressor: The function that decompresses content.
        """
        self.semantic_compressors[content_type] = {
            "compress": compressor,
            "decompress": decompressor
        }
        self.logger.debug(f"Registered semantic compressor for content type: {content_type}")
    
    async def add_route(self, source: str, destination: str, route_info: Dict[str, Any] = None) -> None:
        """
        Add a route between two components.
        
        Args:
            source: The source component ID.
            destination: The destination component ID.
            route_info: Additional information about the route.
        """
        async with self.lock:
            if source not in self.routes:
                self.routes[source] = {}
            
            self.routes[source][destination] = route_info or {}
        
        self.logger.debug(f"Added route from {source} to {destination}")
    
    async def get_route(self, source: str, destination: str) -> Optional[Dict[str, Any]]:
        """
        Get route information between two components.
        
        Args:
            source: The source component ID.
            destination: The destination component ID.
            
        Returns:
            Route information, or None if no route exists.
        """
        async with self.lock:
            if source in self.routes and destination in self.routes[source]:
                return self.routes[source][destination]
        return None
    
    async def send_message(self, message: BaseMessage) -> Optional[BaseMessage]:
        """
        Send a message through the mesh.
        
        Args:
            message: The message to send.
            
        Returns:
            The response message, if any.
        """
        if not message.validate():
            self.logger.error("Invalid message")
            return MessageFactory.create_error(
                "invalid_message",
                "The message is invalid",
                related_message_id=message.message_id
            )
        
        # Add this component as a hop
        message.add_hop(self.component_id)
        
        # Check if we have a direct route
        if message.receiver_id and message.sender_id:
            route = await self.get_route(message.sender_id, message.receiver_id)
            if route:
                self.logger.debug(f"Using direct route from {message.sender_id} to {message.receiver_id}")
                return await self._deliver_message(message)
        
        # Check for intent-based routing
        if "intent" in message.metadata:
            intent = message.metadata["intent"]
            if intent in self.intent_handlers:
                self.logger.debug(f"Using intent-based routing for intent: {intent}")
                receiver_id = await self.intent_handlers[intent](message)
                if receiver_id:
                    message.receiver_id = receiver_id
                    return await self._deliver_message(message)
        
        # If we have a receiver_id but no route, try to deliver directly
        if message.receiver_id:
            self.logger.debug(f"Attempting direct delivery to {message.receiver_id}")
            return await self._deliver_message(message)
        
        # If all else fails, broadcast to all components of the appropriate type
        if "target_type" in message.metadata:
            target_type = message.metadata["target_type"]
            self.logger.debug(f"Broadcasting to all components of type: {target_type}")
            return await self._broadcast_message(message, target_type)
        
        self.logger.error("Unable to route message")
        return MessageFactory.create_error(
            "routing_error",
            "Unable to determine message route",
            related_message_id=message.message_id
        )
    
    async def _deliver_message(self, message: BaseMessage) -> Optional[BaseMessage]:
        """
        Deliver a message to its intended recipient.
        
        Args:
            message: The message to deliver.
            
        Returns:
            The response message, if any.
        """
        if not message.receiver_id:
            self.logger.error("Message has no receiver_id")
            return MessageFactory.create_error(
                "delivery_error",
                "Message has no receiver_id",
                related_message_id=message.message_id
            )
        
        # Apply semantic compression if available
        if "content_type" in message.metadata:
            content_type = message.metadata["content_type"]
            if content_type in self.semantic_compressors:
                self.logger.debug(f"Applying semantic compression for content type: {content_type}")
                compressor = self.semantic_compressors[content_type]["compress"]
                
                if hasattr(message, "payload") and message.payload is not None:
                    message.metadata["compressed"] = True
                    message.payload = compressor(message.payload)
        
        # Find the component
        if self.discovery_service:
            component = await self.discovery_service.get_component(message.receiver_id)
            if component:
                self.logger.debug(f"Delivering message to component {message.receiver_id}")
                
                # Decompress payload if necessary
                if "content_type" in message.metadata and message.metadata.get("compressed", False):
                    content_type = message.metadata["content_type"]
                    if content_type in self.semantic_compressors:
                        self.logger.debug(f"Applying semantic decompression for content type: {content_type}")
                        decompressor = self.semantic_compressors[content_type]["decompress"]
                        
                        if hasattr(message, "payload") and message.payload is not None:
                            message.payload = decompressor(message.payload)
                            message.metadata["compressed"] = False
                
                # Process the message
                try:
                    # Check if the component has an async process_message method
                    if hasattr(component, "process_message_async"):
                        response = await component.process_message_async(message.to_dict())
                    else:
                        # Fall back to synchronous processing
                        response = component.process_message(message.to_dict())
                    
                    if response:
                        if isinstance(response, dict) and "message_id" in response:
                            return MessageFactory.create_from_dict(response)
                        else:
                            return MessageFactory.create_response(
                                message.message_id,
                                MessageStatus.SUCCESS,
                                response,
                                sender_id=message.receiver_id,
                                receiver_id=message.sender_id
                            )
                except Exception as e:
                    self.logger.error(f"Error processing message: {e}")
                    return MessageFactory.create_error(
                        "processing_error",
                        f"Error processing message: {str(e)}",
                        related_message_id=message.message_id,
                        sender_id=message.receiver_id,
                        receiver_id=message.sender_id
                    )
            else:
                self.logger.error(f"Component not found: {message.receiver_id}")
                return MessageFactory.create_error(
                    "component_not_found",
                    f"Component not found: {message.receiver_id}",
                    related_message_id=message.message_id
                )
        else:
            self.logger.error("No discovery service available")
            return MessageFactory.create_error(
                "no_discovery_service",
                "No discovery service available",
                related_message_id=message.message_id
            )
    
    async def _broadcast_message(self, message: BaseMessage, target_type: str) -> List[BaseMessage]:
        """
        Broadcast a message to all components of a specific type.
        
        Args:
            message: The message to broadcast.
            target_type: The type of components to broadcast to.
            
        Returns:
            A list of response messages.
        """
        responses = []
        
        if self.discovery_service:
            components = await self.discovery_service.find_components_by_type(target_type)
            self.logger.debug(f"Broadcasting message to {len(components)} components of type {target_type}")
            
            for component in components:
                broadcast_message = MessageFactory.create_from_dict(message.to_dict())
                broadcast_message.receiver_id = component.component_id
                response = await self._deliver_message(broadcast_message)
                if response:
                    responses.append(response)
        else:
            self.logger.error("No discovery service available")
            error = MessageFactory.create_error(
                "no_discovery_service",
                "No discovery service available",
                related_message_id=message.message_id
            )
            responses.append(error)
        
        return responses
    
    async def _handle_request(self, message: RequestMessage) -> Optional[ResponseMessage]:
        """
        Handle a request message.
        
        Args:
            message: The request message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling request message: {message.operation}")
        
        # Check if this is a request for this component
        if message.receiver_id == self.component_id:
            if message.operation == "get_routes":
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    self.routes,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            elif message.operation == "add_route":
                if "source" in message.payload and "destination" in message.payload:
                    await self.add_route(
                        message.payload["source"],
                        message.payload["destination"],
                        message.payload.get("route_info")
                    )
                    return MessageFactory.create_response(
                        message.message_id,
                        MessageStatus.SUCCESS,
                        {"status": "route_added"},
                        sender_id=self.component_id,
                        receiver_id=message.sender_id
                    )
                else:
                    return MessageFactory.create_error(
                        "invalid_payload",
                        "Payload must contain 'source' and 'destination'",
                        related_message_id=message.message_id,
                        sender_id=self.component_id,
                        receiver_id=message.sender_id
                    )
            else:
                return MessageFactory.create_error(
                    "unsupported_operation",
                    f"Unsupported operation: {message.operation}",
                    related_message_id=message.message_id,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
        
        # Otherwise, route the message
        return await self.send_message(message)
    
    async def _handle_response(self, message: ResponseMessage) -> Optional[BaseMessage]:
        """
        Handle a response message.
        
        Args:
            message: The response message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling response message for request {message.request_id}")
        
        # Route the message to its destination
        return await self.send_message(message)
    
    async def _handle_event(self, message: EventMessage) -> Optional[BaseMessage]:
        """
        Handle an event message.
        
        Args:
            message: The event message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling event message: {message.event_type}")
        
        # Route the message to its destination
        return await self.send_message(message)
    
    async def _handle_command(self, message: CommandMessage) -> Optional[BaseMessage]:
        """
        Handle a command message.
        
        Args:
            message: The command message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling command message: {message.command}")
        
        # Check if this is a command for this component
        if message.receiver_id == self.component_id:
            if message.command == "start":
                await self.start()
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    {"status": "started"},
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            elif message.command == "stop":
                await self.stop()
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    {"status": "stopped"},
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            else:
                return MessageFactory.create_error(
                    "unsupported_command",
                    f"Unsupported command: {message.command}",
                    related_message_id=message.message_id,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
        
        # Otherwise, route the message
        return await self.send_message(message)
    
    async def _handle_query(self, message: QueryMessage) -> Optional[BaseMessage]:
        """
        Handle a query message.
        
        Args:
            message: The query message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling query message: {message.query}")
        
        # Check if this is a query for this component
        if message.receiver_id == self.component_id:
            if message.query == "status":
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    {
                        "status": "running" if self.is_running else "stopped",
                        "queue_size": self.message_queue.qsize() if self.message_queue else 0,
                        "routes_count": sum(len(routes) for routes in self.routes.values()),
                        "handlers_count": len(self.message_handlers),
                        "intent_handlers_count": len(self.intent_handlers),
                        "semantic_compressors_count": len(self.semantic_compressors)
                    },
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            elif message.query == "routes":
                return MessageFactory.create_response(
                    message.message_id,
                    MessageStatus.SUCCESS,
                    self.routes,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
            else:
                return MessageFactory.create_error(
                    "unsupported_query",
                    f"Unsupported query: {message.query}",
                    related_message_id=message.message_id,
                    sender_id=self.component_id,
                    receiver_id=message.sender_id
                )
        
        # Otherwise, route the message
        return await self.send_message(message)
    
    async def _handle_error(self, message: ErrorMessage) -> Optional[BaseMessage]:
        """
        Handle an error message.
        
        Args:
            message: The error message to handle.
            
        Returns:
            The response message, if any.
        """
        self.logger.debug(f"Handling error message: {message.error_code}")
        
        # Log the error
        self.logger.error(f"Error message received: {message.error_code} - {message.error_message}")
        
        # Route the message to its destination
        return await self.send_message(message)
    
    async def process_message_async(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message asynchronously.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
        """
        if not isinstance(message, dict):
            self.logger.error("Message must be a dictionary")
            return MessageFactory.create_error(
                "invalid_message",
                "Message must be a dictionary"
            ).to_dict()
        
        # Convert to appropriate message type
        if "message_type" in message:
            message_obj = MessageFactory.create_from_dict(message)
            
            # Handle the message based on its type
            if message_obj.message_type in self.message_handlers:
                handler = self.message_handlers[message_obj.message_type]
                response = await handler(message_obj)
                if response:
                    return response.to_dict()
                else:
                    return MessageFactory.create_response(
                        message_obj.message_id,
                        MessageStatus.SUCCESS,
                        {"status": "processed"},
                        sender_id=self.component_id,
                        receiver_id=message_obj.sender_id
                    ).to_dict()
            else:
                self.logger.error(f"Unsupported message type: {message_obj.message_type}")
                return MessageFactory.create_error(
                    "unsupported_message_type",
                    f"Unsupported message type: {message_obj.message_type}",
                    related_message_id=message_obj.message_id,
                    sender_id=self.component_id,
                    receiver_id=message_obj.sender_id
                ).to_dict()
        else:
            self.logger.error("Message must have a 'message_type' field")
            return MessageFactory.create_error(
                "invalid_message",
                "Message must have a 'message_type' field"
            ).to_dict()
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message synchronously.
        
        This method creates an event loop and runs the asynchronous handler.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()
    
    async def _process_queue(self) -> None:
        """Process messages from the queue."""
        self.logger.info("Message queue processor started")
        
        while self.is_running:
            try:
                message = await self.message_queue.get()
                self.logger.debug(f"Processing message from queue: {message.message_id}")
                
                # Process the message
                await self.process_message_async(message.to_dict())
                
                # Mark the task as done
                self.message_queue.task_done()
                
                self.logger.debug(f"Message processed: {message.message_id}")
            except asyncio.CancelledError:
                self.logger.info("Message queue processor cancelled")
                break
            except Exception as e:
                self.logger.error(f"Error processing message from queue: {e}")
    
    async def start(self) -> None:
        """Start the MCP handler."""
        if self.is_running:
            self.logger.warning("Async MCP Handler is already running")
            return
        
        self.is_running = True
        self.processing_task = asyncio.create_task(self._process_queue())
        self.logger.info("Async MCP Handler started")
    
    async def stop(self) -> None:
        """Stop the MCP handler."""
        if not self.is_running:
            self.logger.warning("Async MCP Handler is not running")
            return
        
        self.is_running = False
        if self.processing_task:
            self.processing_task.cancel()
        self.logger.info("Async MCP Handler stopped")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check.
        
        Returns:
            A dictionary containing health check results.
        """
        return {
            "status": "healthy" if self.is_running else "stopped",
            "queue_size": self.message_queue.qsize() if self.message_queue else 0,
            "routes_count": sum(len(routes) for routes in self.routes.values()),
            "handlers_count": len(self.message_handlers),
            "intent_handlers_count": len(self.intent_handlers),
            "semantic_compressors_count": len(self.semantic_compressors)
        }
    
    async def get_manifest(self) -> Dict[str, Any]:
        """
        Get the component manifest.
        
        Returns:
            A dictionary containing the component manifest.
        """
        manifest = await super().get_manifest()
        manifest.update({
            "routes_count": sum(len(routes) for routes in self.routes.values()),
            "handlers_count": len(self.message_handlers),
            "intent_handlers_count": len(self.intent_handlers),
            "semantic_compressors_count": len(self.semantic_compressors),
            "is_running": self.is_running
        })
        return manifest
"""
