"""
MCP Integration Framework for the Overseer System.

This module provides integration with the Model Context Protocol (MCP),
enabling context-aware communication between Overseer System components
and other layers of the Industriverse ecosystem.
"""

import json
import uuid
import datetime
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field

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
        
    def register_context_handler(self, context_type: str, handler_func):
        """
        Register a handler function for a specific context type.
        
        Args:
            context_type: Type of context to handle
            handler_func: Function to call when context is received
        """
        self.context_handlers[context_type] = handler_func
        
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
            print(f"Warning: No event bus client configured, context {context.context_id} not sent")
            return False
            
        try:
            # In production, this would use the actual Kafka client
            topic = f"mcp.{context.context_type}"
            await self.event_bus_client.send(
                topic=topic,
                value=context.json(),
                key=context.context_id
            )
            return True
        except Exception as e:
            print(f"Error sending context: {e}")
            return False
            
    async def handle_context(self, context_json: str) -> bool:
        """
        Handle an incoming MCP context.
        
        Args:
            context_json: JSON string of the context
            
        Returns:
            True if handled successfully, False otherwise
        """
        try:
            context = MCPContext.parse_raw(context_json)
            
            # Check if this context is targeted for this service
            if context.target and context.target != self.service_name:
                return False
                
            # Find and call the appropriate handler
            handler = self.context_handlers.get(context.context_type)
            if handler:
                await handler(context)
                return True
            else:
                print(f"No handler registered for context type: {context.context_type}")
                return False
                
        except Exception as e:
            print(f"Error handling context: {e}")
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

class MCPContextSchema:
    """Schema definitions for common MCP context types."""
    
    # System contexts
    SYSTEM_HEARTBEAT = "system.heartbeat"
    SYSTEM_CONFIG_UPDATE = "system.config.update"
    SYSTEM_STATUS = "system.status"
    
    # Agent contexts
    AGENT_REGISTRATION = "agent.registration"
    AGENT_STATUS_UPDATE = "agent.status.update"
    AGENT_CAPABILITY_UPDATE = "agent.capability.update"
    
    # Capsule contexts
    CAPSULE_INSTANTIATION = "capsule.instantiation"
    CAPSULE_LIFECYCLE_UPDATE = "capsule.lifecycle.update"
    CAPSULE_TRUST_UPDATE = "capsule.trust.update"
    CAPSULE_EVOLUTION = "capsule.evolution"
    
    # Process contexts
    PROCESS_DEFINITION = "process.definition"
    PROCESS_EXECUTION = "process.execution"
    PROCESS_STATUS_UPDATE = "process.status.update"
    
    # Monitoring contexts
    MONITORING_METRIC = "monitoring.metric"
    MONITORING_ALERT = "monitoring.alert"
    MONITORING_ANOMALY = "monitoring.anomaly"
    
    # Analytics contexts
    ANALYTICS_REPORT = "analytics.report"
    ANALYTICS_INSIGHT = "analytics.insight"
    
    # Optimization contexts
    OPTIMIZATION_RECOMMENDATION = "optimization.recommendation"
    OPTIMIZATION_EXECUTION = "optimization.execution"
    
    # Compliance contexts
    COMPLIANCE_CHECK = "compliance.check"
    COMPLIANCE_VIOLATION = "compliance.violation"
    COMPLIANCE_REPORT = "compliance.report"
    
    # Simulation contexts
    SIMULATION_SCENARIO = "simulation.scenario"
    SIMULATION_EXECUTION = "simulation.execution"
    SIMULATION_RESULT = "simulation.result"
    
    # Ethics contexts
    ETHICS_CHECK = "ethics.check"
    ETHICS_VIOLATION = "ethics.violation"
    ETHICS_ESCALATION = "ethics.escalation"
    
    # Digital twin contexts
    TWIN_NEGOTIATION = "twin.negotiation"
    TWIN_AGREEMENT = "twin.agreement"
    TWIN_CONFLICT = "twin.conflict"
    
    # Market contexts
    MARKET_BID = "market.bid"
    MARKET_AWARD = "market.award"
    MARKET_STABILIZATION = "market.stabilization"

class MCPIntegrationManager:
    """Manager for MCP integration across the Overseer System."""
    
    def __init__(self, service_name: str, event_bus_client=None):
        """
        Initialize the MCP Integration Manager.
        
        Args:
            service_name: Name of the service using this manager
            event_bus_client: Client for the event bus (Kafka)
        """
        self.service_name = service_name
        self.protocol_bridge = MCPProtocolBridge(service_name, event_bus_client)
        self.schema = MCPContextSchema
        
    async def initialize(self):
        """Initialize the MCP integration."""
        # Register for relevant topics
        if self.event_bus_client:
            # In production, this would subscribe to Kafka topics
            pass
            
        # Send registration context
        registration_context = self.protocol_bridge.create_context(
            context_type=self.schema.SYSTEM_HEARTBEAT,
            payload={
                "service_name": self.service_name,
                "status": "online",
                "capabilities": self._get_capabilities()
            }
        )
        await self.protocol_bridge.send_context(registration_context)
        
    def _get_capabilities(self) -> List[str]:
        """Get the capabilities of this service for registration."""
        # This would be overridden by specific services
        return ["mcp.base"]
        
    async def send_heartbeat(self):
        """Send a heartbeat context."""
        heartbeat_context = self.protocol_bridge.create_context(
            context_type=self.schema.SYSTEM_HEARTBEAT,
            payload={
                "service_name": self.service_name,
                "status": "online",
                "timestamp": datetime.datetime.now().isoformat()
            }
        )
        await self.protocol_bridge.send_context(heartbeat_context)
        
    def register_context_handler(self, context_type: str, handler_func):
        """
        Register a handler function for a specific context type.
        
        Args:
            context_type: Type of context to handle
            handler_func: Function to call when context is received
        """
        self.protocol_bridge.register_context_handler(context_type, handler_func)
        
    async def send_context(self, context_type: str, payload: Dict[str, Any], **kwargs) -> bool:
        """
        Send an MCP context.
        
        Args:
            context_type: Type of context
            payload: Context payload
            **kwargs: Additional context parameters
            
        Returns:
            True if sent successfully, False otherwise
        """
        context = self.protocol_bridge.create_context(
            context_type=context_type,
            payload=payload,
            **kwargs
        )
        return await self.protocol_bridge.send_context(context)
