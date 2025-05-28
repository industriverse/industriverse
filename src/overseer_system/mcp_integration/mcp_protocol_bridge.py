"""
MCP Protocol Bridge for the Overseer System.

This module provides a bridge for MCP protocol communication between Overseer System components
and other layers of the Industriverse ecosystem.
"""

import json
import uuid
import datetime
import logging
from typing import Dict, Any, List, Optional, Callable, Union
from pydantic import BaseModel, Field

from .mcp_context_schema import MCPContextType

class MCPContext(BaseModel):
    """Model Context Protocol context object."""
    context_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    source: str
    target: Optional[str] = None
    context_type: str
    payload: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    parent_context_id: Optional[str] = None
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    version: str = "1.0"

class MCPProtocolBridge:
    """Bridge for handling MCP protocol communication."""
    
    def __init__(self, service_name: str, event_bus_client=None):
        """
        Initialize the MCP Protocol Bridge.
        
        Args:
            service_name: Name of the service using this bridge
            event_bus_client: Client for the event bus (Kafka)
        """
        self.service_name = service_name
        self.event_bus_client = event_bus_client
        self.context_handlers = {}
        self.logger = logging.getLogger("mcp_protocol_bridge")
        
    async def initialize(self):
        """Initialize the MCP Protocol Bridge."""
        if not self.event_bus_client:
            self.logger.warning("No event bus client provided, MCP bridge will operate in local-only mode")
            return
            
        # Subscribe to MCP topics
        await self._subscribe_to_topics()
        
    async def _subscribe_to_topics(self):
        """Subscribe to relevant MCP topics."""
        if not self.event_bus_client:
            return
            
        # Subscribe to topics for this service
        service_topic = f"mcp.service.{self.service_name}"
        await self.event_bus_client.subscribe(service_topic, self._handle_mcp_message)
        
        # Subscribe to broadcast topics
        broadcast_topic = "mcp.broadcast"
        await self.event_bus_client.subscribe(broadcast_topic, self._handle_mcp_message)
        
        # Subscribe to topics for registered context types
        for context_type in self.context_handlers.keys():
            topic = f"mcp.{context_type}"
            await self.event_bus_client.subscribe(topic, self._handle_mcp_message)
        
    async def _handle_mcp_message(self, topic: str, value: Any, key: Optional[str]):
        """
        Handle an incoming MCP message.
        
        Args:
            topic: Kafka topic
            value: Message value
            key: Message key
        """
        try:
            # Parse context
            context = MCPContext.parse_obj(value)
            
            # Check if this context is targeted for this service
            if context.target and context.target != self.service_name:
                return
                
            # Find and call the appropriate handler
            await self.handle_context(context)
                
        except Exception as e:
            self.logger.error(f"Error handling MCP message: {e}")
        
    def register_context_handler(self, context_type: str, handler_func):
        """
        Register a handler function for a specific context type.
        
        Args:
            context_type: Type of context to handle
            handler_func: Function to call when context is received
        """
        self.context_handlers[context_type] = handler_func
        
        # Subscribe to topic if event bus client is available
        if self.event_bus_client:
            topic = f"mcp.{context_type}"
            asyncio.create_task(self.event_bus_client.subscribe(topic, self._handle_mcp_message))
        
    def create_context(
        self, 
        context_type: str, 
        payload: Dict[str, Any], 
        target: Optional[str] = None,
        parent_context_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> MCPContext:
        """
        Create a new MCP context.
        
        Args:
            context_type: Type of context
            payload: Context payload
            target: Target service (if any)
            parent_context_id: ID of parent context (if any)
            metadata: Additional metadata
            
        Returns:
            New MCP context object
        """
        return MCPContext(
            source=self.service_name,
            target=target,
            context_type=context_type,
            payload=payload,
            parent_context_id=parent_context_id,
            metadata=metadata or {}
        )
        
    async def send_context(self, context: MCPContext) -> bool:
        """
        Send an MCP context via the event bus.
        
        Args:
            context: MCP context to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.event_bus_client:
            self.logger.warning(f"No event bus client configured, context {context.context_id} not sent")
            return False
            
        try:
            # Determine topic based on context type and target
            if context.target:
                topic = f"mcp.service.{context.target}"
            else:
                topic = f"mcp.{context.context_type}"
                
            # Send context
            return await self.event_bus_client.send(
                topic=topic,
                value=context.dict(),
                key=context.context_id
            )
        except Exception as e:
            self.logger.error(f"Error sending context: {e}")
            return False
            
    async def handle_context(self, context: MCPContext) -> bool:
        """
        Handle an incoming MCP context.
        
        Args:
            context: MCP context to handle
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            # Find and call the appropriate handler
            handler = self.context_handlers.get(context.context_type)
            if handler:
                await handler(context)
                return True
            else:
                self.logger.warning(f"No handler registered for context type: {context.context_type}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error handling context: {e}")
            return False
            
    def create_response_context(
        self, 
        original_context: MCPContext, 
        payload: Dict[str, Any],
        context_type: Optional[str] = None
    ) -> MCPContext:
        """
        Create a response context for an original context.
        
        Args:
            original_context: Original context to respond to
            payload: Response payload
            context_type: Type of response context (defaults to original type + ".response")
            
        Returns:
            New response context
        """
        response_type = context_type or f"{original_context.context_type}.response"
        return MCPContext(
            source=self.service_name,
            target=original_context.source,
            context_type=response_type,
            payload=payload,
            parent_context_id=original_context.context_id,
            trace_id=original_context.trace_id,
            metadata={
                "is_response": True,
                **original_context.metadata
            }
        )
        
    async def broadcast_context(
        self, 
        context_type: str, 
        payload: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Broadcast an MCP context to all services.
        
        Args:
            context_type: Type of context
            payload: Context payload
            metadata: Additional metadata
            
        Returns:
            True if broadcast successfully, False otherwise
        """
        context = self.create_context(
            context_type=context_type,
            payload=payload,
            metadata=metadata
        )
        
        if not self.event_bus_client:
            self.logger.warning(f"No event bus client configured, context {context.context_id} not broadcast")
            return False
            
        try:
            # Send to broadcast topic
            return await self.event_bus_client.send(
                topic="mcp.broadcast",
                value=context.dict(),
                key=context.context_id
            )
        except Exception as e:
            self.logger.error(f"Error broadcasting context: {e}")
            return False
