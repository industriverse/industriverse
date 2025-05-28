"""
A2A (Agent-to-Agent) Protocol Handler for Industriverse Protocol Layer

This module implements the A2A protocol handler for the Industriverse Protocol Layer,
building upon Google's A2A protocol specification with Industriverse-specific enhancements.
It provides services for agent discovery, task management, and collaboration.

The A2A handler ensures:
1. Compatibility with the standard A2A protocol
2. Enhanced agent discovery with industry-specific metadata
3. Task prioritization and workflow template support
4. Secure and efficient multi-tenant agent communication
5. Integration with the Industriverse Protocol Kernel Intelligence
"""

import uuid
import json
import asyncio
import logging
import datetime
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable

from protocols.protocol_base import ProtocolComponent, ProtocolService, ProtocolAgent
from protocols.agent_interface import AgentCard, AgentTask, AgentWorkflow, BaseProtocolAgent, AsyncProtocolAgent
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus, MessageType
)
from protocols.discovery_service import DiscoveryService, AsyncDiscoveryService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format=\'%(asctime)s - %(name)s - %(levelname)s - %(message)s\'
)
logger = logging.getLogger(__name__)


# --- A2A Protocol Specific Data Structures ---

class A2APart:
    """
    Represents a part in an A2A message, enhanced for Industriverse.
    """
    def __init__(self, part_id: str, content_type: str, content: Any, metadata: Dict[str, Any] = None):
        self.part_id = part_id
        self.content_type = content_type
        self.content = content
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "part_id": self.part_id,
            "content_type": self.content_type,
            "content": self.content, # Content might need specific serialization
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> \'A2APart\':
        return cls(
            part_id=data["part_id"],
            content_type=data["content_type"],
            content=data["content"], # Content might need specific deserialization
            metadata=data.get("metadata", {})
        )

class A2AMessage(BaseMessage):
    """
    Represents an A2A protocol message, incorporating Industriverse enhancements.
    """
    def __init__(
        self,
        a2a_type: str, # e.g., "request_capabilities", "assign_task"
        parts: List[A2APart] = None,
        message_id: str = None,
        correlation_id: str = None,
        timestamp: str = None,
        sender_id: str = None,
        receiver_id: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.NORMAL,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ):
        super().__init__(
            message_id=message_id,
            correlation_id=correlation_id,
            timestamp=timestamp,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type="a2a", # Specific message type for A2A
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
        self.a2a_type = a2a_type
        self.parts = parts or []

    def add_part(self, part: A2APart) -> None:
        self.parts.append(part)

    def get_part(self, part_id: str) -> Optional[A2APart]:
        return next((p for p in self.parts if p.part_id == part_id), None)

    def validate(self) -> bool:
        if not super().validate():
            return False
        if not self.a2a_type:
            logger.error("A2A validation failed: missing a2a_type")
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        base_dict = super().to_dict()
        a2a_dict = {
            "a2a_type": self.a2a_type,
            "parts": [part.to_dict() for part in self.parts]
        }
        return {**base_dict, **a2a_dict}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> \'A2AMessage\':
        msg = super(A2AMessage, cls).from_dict(data)
        msg.a2a_type = data.get("a2a_type")
        msg.parts = [A2APart.from_dict(p_data) for p_data in data.get("parts", [])]
        return msg

# --- A2A Handler Implementation ---

class A2AHandler(ProtocolService):
    """
    Handler for the Agent-to-Agent (A2A) protocol with Industriverse enhancements.
    
    Provides services for agent discovery, task management, and collaboration based
    on the A2A protocol specification.
    """
    
    def __init__(
        self,
        service_id: str = None,
        discovery_service: DiscoveryService = None,
        mcp_handler: \'MCPHandler\' = None, # Reference to MCP handler for mesh communication
        config: Dict[str, Any] = None
    ):
        """
        Initialize an A2A handler.
        
        Args:
            service_id: Unique identifier for this service. If None, a UUID is generated.
            discovery_service: Discovery service for agent lookup.
            mcp_handler: MCP handler for sending messages across the mesh.
            config: Configuration parameters for the handler.
        """
        super().__init__(service_id or str(uuid.uuid4()), "a2a_handler")
        self.discovery_service = discovery_service
        self.mcp_handler = mcp_handler
        self.config = config or {}
        self.a2a_message_handlers = {}
        self.local_agent: Optional[Union[BaseProtocolAgent, AsyncProtocolAgent]] = None
        self.logger = logging.getLogger(f"{__name__}.A2AHandler.{self.component_id[:8]}")
        self.logger.info(f"A2A Handler initialized with ID {self.component_id}")

        # Register default A2A message handlers
        self.register_a2a_message_handler("request_capabilities", self._handle_request_capabilities)
        self.register_a2a_message_handler("capabilities_response", self._handle_capabilities_response)
        self.register_a2a_message_handler("assign_task", self._handle_assign_task)
        self.register_a2a_message_handler("task_status", self._handle_task_status)
        self.register_a2a_message_handler("task_result", self._handle_task_result)
        self.register_a2a_message_handler("error", self._handle_a2a_error)
        # Add more handlers as needed based on A2A spec and Industriverse extensions

        # Add capabilities
        self.add_capability("a2a_communication", "Agent-to-Agent communication based on A2A protocol")
        self.add_capability("agent_discovery", "Discovering agents and their capabilities")
        self.add_capability("task_management", "Assigning and managing tasks between agents")
        self.add_capability("industriverse_a2a_extensions", "Support for Industriverse-specific A2A enhancements")

    def set_local_agent(self, agent: Union[BaseProtocolAgent, AsyncProtocolAgent]) -> None:
        """Set the local agent associated with this handler."""
        self.local_agent = agent
        self.logger.info(f"Associated local agent {agent.get_agent_type()} with ID {agent.get_agent_id()}")

    def register_a2a_message_handler(
        self,
        a2a_type: str,
        handler: Callable[[A2AMessage], Optional[BaseMessage]]
    ) -> None:
        """
        Register a handler for a specific A2A message type.
        
        Args:
            a2a_type: The type of A2A message to handle.
            handler: The function that handles messages of this type.
        """
        self.a2a_message_handlers[a2a_type] = handler
        self.logger.debug(f"Registered handler for A2A message type: {a2a_type}")

    def send_a2a_message(self, message: A2AMessage) -> Optional[BaseMessage]:
        """
        Send an A2A message using the underlying MCP handler.
        
        Args:
            message: The A2A message to send.
            
        Returns:
            The response message, if any.
        """
        if not self.mcp_handler:
            self.logger.error("MCP Handler not configured, cannot send A2A message")
            return MessageFactory.create_error(
                "configuration_error",
                "MCP Handler not configured",
                related_message_id=message.message_id
            )
        
        if not message.validate():
            self.logger.error("Invalid A2A message")
            return MessageFactory.create_error(
                "invalid_message",
                "The A2A message is invalid",
                related_message_id=message.message_id
            )

        # Ensure sender ID is set (usually the local agent)
        if not message.sender_id and self.local_agent:
            message.sender_id = self.local_agent.get_agent_id()
        elif not message.sender_id:
             self.logger.warning("Sending A2A message without sender_id")

        self.logger.debug(f"Sending A2A message type {message.a2a_type} from {message.sender_id} to {message.receiver_id}")
        return self.mcp_handler.send_message(message)

    # --- Default A2A Message Handlers ---

    def _handle_request_capabilities(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle a request for agent capabilities."""
        self.logger.info(f"Received request_capabilities from {message.sender_id}")
        if not self.local_agent:
            self.logger.error("No local agent configured to respond to capabilities request")
            return self._create_a2a_error_response(message, "no_local_agent", "Handler has no local agent")

        # Get the agent card (manifest)
        agent_card = self.local_agent.card
        if not agent_card:
             self.logger.error("Local agent has no AgentCard")
             return self._create_a2a_error_response(message, "internal_error", "Local agent has no card")

        # Create capabilities response message
        response_parts = [
            A2APart(
                part_id="agent_card",
                content_type="application/json",
                content=agent_card.to_dict()
            )
        ]
        
        response_message = A2AMessage(
            a2a_type="capabilities_response",
            parts=response_parts,
            correlation_id=message.message_id,
            sender_id=self.local_agent.get_agent_id(),
            receiver_id=message.sender_id,
            priority=message.priority, # Respond with same priority
            security_level=message.security_level
        )
        
        self.logger.info(f"Sending capabilities_response to {message.sender_id}")
        return response_message

    def _handle_capabilities_response(self, message: A2AMessage) -> None:
        """Handle a capabilities response message."""
        self.logger.info(f"Received capabilities_response from {message.sender_id}")
        card_part = message.get_part("agent_card")
        if card_part and card_part.content_type == "application/json":
            try:
                agent_card = AgentCard.from_dict(card_part.content)
                self.logger.info(f"Received Agent Card for {agent_card.name} (ID: {agent_card.agent_id})")
                # Optionally, update the discovery service
                if self.discovery_service:
                    # Assuming discovery service has a method to update/register cards
                    if hasattr(self.discovery_service, "register_agent_card"): 
                         self.discovery_service.register_agent_card(agent_card)
                    else:
                         self.logger.warning("Discovery service does not support register_agent_card")
            except Exception as e:
                self.logger.error(f"Failed to parse AgentCard from capabilities_response: {e}")
        else:
            self.logger.warning("Capabilities response did not contain a valid agent_card part")
        # Typically, no response is sent back for a response message
        return None

    def _handle_assign_task(self, message: A2AMessage) -> Optional[A2AMessage]:
        """Handle a task assignment message."""
        self.logger.info(f"Received assign_task from {message.sender_id}")
        if not self.local_agent:
            self.logger.error("No local agent configured to handle task assignment")
            return self._create_a2a_error_response(message, "no_local_agent", "Handler has no local agent")

        task_part = message.get_part("task_definition")
        if task_part and task_part.content_type == "application/json":
            try:
                task_data = task_part.content
                agent_task = AgentTask.from_dict(task_data)
                agent_task.assign(self.local_agent.get_agent_id())
                self.logger.info(f"Assigned task {agent_task.task_id} ({agent_task.task_type}) to local agent")

                # TODO: Integrate with local agent's task execution logic
                # This might involve queuing the task, starting execution, etc.
                # For now, just acknowledge receipt and send a pending status

                status_part = A2APart(
                    part_id="task_status_update",
                    content_type="application/json",
                    content={
                        "task_id": agent_task.task_id,
                        "status": "assigned", # Or "pending" / "queued"
                        "timestamp": datetime.datetime.utcnow().isoformat()
                    }
                )
                
                response_message = A2AMessage(
                    a2a_type="task_status",
                    parts=[status_part],
                    correlation_id=message.message_id,
                    sender_id=self.local_agent.get_agent_id(),
                    receiver_id=message.sender_id,
                    priority=message.priority,
                    security_level=message.security_level
                )
                return response_message

            except Exception as e:
                self.logger.error(f"Failed to parse or assign task: {e}")
                return self._create_a2a_error_response(message, "task_error", f"Failed to process task: {e}")
        else:
            self.logger.warning("Assign task message did not contain a valid task_definition part")
            return self._create_a2a_error_response(message, "invalid_message", "Missing task_definition part")

    def _handle_task_status(self, message: A2AMessage) -> None:
        """Handle a task status update message."""
        self.logger.info(f"Received task_status update from {message.sender_id}")
        status_part = message.get_part("task_status_update")
        if status_part and status_part.content_type == "application/json":
            try:
                status_data = status_part.content
                task_id = status_data.get("task_id")
                status = status_data.get("status")
                timestamp = status_data.get("timestamp")
                self.logger.info(f"Task {task_id} status updated to {status} at {timestamp}")
                # TODO: Update local task tracking system
            except Exception as e:
                self.logger.error(f"Failed to parse task status update: {e}")
        else:
            self.logger.warning("Task status message did not contain a valid task_status_update part")
        return None # No response needed

    def _handle_task_result(self, message: A2AMessage) -> None:
        """Handle a task result message."""
        self.logger.info(f"Received task_result from {message.sender_id}")
        result_part = message.get_part("task_result_data")
        if result_part:
            try:
                result_data = result_part.content
                task_id = message.metadata.get("task_id") # Assuming task_id is in metadata or another part
                self.logger.info(f"Received result for task {task_id}: {result_data}")
                # TODO: Process task result, update workflow, etc.
            except Exception as e:
                self.logger.error(f"Failed to parse task result: {e}")
        else:
            self.logger.warning("Task result message did not contain a valid task_result_data part")
        return None # No response needed

    def _handle_a2a_error(self, message: A2AMessage) -> None:
        """Handle an A2A error message."""
        self.logger.info(f"Received A2A error from {message.sender_id}")
        error_part = message.get_part("error_details")
        if error_part and error_part.content_type == "application/json":
            try:
                error_data = error_part.content
                error_code = error_data.get("error_code")
                error_message = error_data.get("error_message")
                related_message_id = error_data.get("related_message_id")
                self.logger.error(f"A2A Error {error_code}: {error_message} (Related to: {related_message_id})")
                # TODO: Handle error appropriately (e.g., retry, notify user)
            except Exception as e:
                self.logger.error(f"Failed to parse A2A error details: {e}")
        else:
            self.logger.warning("A2A error message did not contain valid error_details part")
        return None # No response needed

    def _create_a2a_error_response(self, original_message: A2AMessage, error_code: str, error_message: str) -> A2AMessage:
        """Helper to create an A2A error message."""
        error_part = A2APart(
            part_id="error_details",
            content_type="application/json",
            content={
                "error_code": error_code,
                "error_message": error_message,
                "related_message_id": original_message.message_id,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        )
        
        error_response = A2AMessage(
            a2a_type="error",
            parts=[error_part],
            correlation_id=original_message.message_id,
            sender_id=self.local_agent.get_agent_id() if self.local_agent else self.component_id,
            receiver_id=original_message.sender_id,
            priority=MessagePriority.HIGH, # Errors usually have high priority
            security_level=original_message.security_level
        )
        return error_response

    # --- ProtocolService Methods ---

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process an incoming message, expecting A2A format.
        
        Args:
            message: The incoming message dictionary.
            
        Returns:
            The response message dictionary, if any.
        """
        if not isinstance(message, dict):
            self.logger.error("A2A Handler received non-dict message")
            return MessageFactory.create_error("invalid_message", "Message must be a dictionary").to_dict()

        # Check if it's an A2A message
        if message.get("message_type") != "a2a" or "a2a_type" not in message:
            self.logger.warning(f"A2A Handler received non-A2A message type: {message.get(\'message_type\')}")
            # Optionally, pass to MCP handler or return error
            # For now, return an error indicating wrong handler
            return MessageFactory.create_error(
                "protocol_mismatch",
                "Message is not in A2A format",
                related_message_id=message.get("message_id")
            ).to_dict()

        try:
            a2a_message = A2AMessage.from_dict(message)
            a2a_type = a2a_message.a2a_type

            if a2a_type in self.a2a_message_handlers:
                handler = self.a2a_message_handlers[a2a_type]
                response = handler(a2a_message)
                if response:
                    # If handler returns a message, send it back via MCP
                    # Note: The handler itself might call send_a2a_message, 
                    # so this direct return might be redundant depending on handler logic.
                    # Let's assume handlers return the message to be sent.
                    return self.send_a2a_message(response).to_dict() if response else None
                else:
                    # Handler processed the message but generated no direct response
                    return None 
            else:
                self.logger.error(f"Unsupported A2A message type: {a2a_type}")
                error_response = self._create_a2a_error_response(a2a_message, "unsupported_type", f"Unsupported A2A message type: {a2a_type}")
                return self.send_a2a_message(error_response).to_dict()

        except Exception as e:
            self.logger.exception(f"Error processing A2A message: {e}")
            # Attempt to create an error response if possible
            try:
                error_response = self._create_a2a_error_response(A2AMessage.from_dict(message), "processing_error", f"Internal error processing message: {e}")
                return self.send_a2a_message(error_response).to_dict()
            except Exception:
                 # Fallback if creating error response fails
                 return MessageFactory.create_error("processing_error", f"Internal error processing message: {e}").to_dict()

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check.
        
        Returns:
            A dictionary containing health check results.
        """
        return {
            "status": "healthy",
            "local_agent_id": self.local_agent.get_agent_id() if self.local_agent else None,
            "discovery_service_status": "configured" if self.discovery_service else "not_configured",
            "mcp_handler_status": "configured" if self.mcp_handler else "not_configured",
            "registered_handlers": list(self.a2a_message_handlers.keys())
        }

    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the component manifest.
        
        Returns:
            A dictionary containing the component manifest.
        """
        manifest = super().get_manifest()
        manifest.update({
            "local_agent_id": self.local_agent.get_agent_id() if self.local_agent else None,
            "registered_handlers_count": len(self.a2a_message_handlers)
        })
        return manifest

# --- Async A2A Handler (Similar structure, using async methods) ---

class AsyncA2AHandler(ProtocolService):
    """
    Asynchronous handler for the Agent-to-Agent (A2A) protocol.
    """
    
    def __init__(
        self,
        service_id: str = None,
        discovery_service: AsyncDiscoveryService = None,
        mcp_handler: \'AsyncMCPHandler\' = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "async_a2a_handler")
        self.discovery_service = discovery_service
        self.mcp_handler = mcp_handler
        self.config = config or {}
        self.a2a_message_handlers = {}
        self.local_agent: Optional[AsyncProtocolAgent] = None # Expects async agent
        self.lock = asyncio.Lock()
        self.logger = logging.getLogger(f"{__name__}.AsyncA2AHandler.{self.component_id[:8]}")
        self.logger.info(f"Async A2A Handler initialized with ID {self.component_id}")

        # Register default async A2A message handlers
        self.register_a2a_message_handler("request_capabilities", self._handle_request_capabilities)
        self.register_a2a_message_handler("capabilities_response", self._handle_capabilities_response)
        self.register_a2a_message_handler("assign_task", self._handle_assign_task)
        self.register_a2a_message_handler("task_status", self._handle_task_status)
        self.register_a2a_message_handler("task_result", self._handle_task_result)
        self.register_a2a_message_handler("error", self._handle_a2a_error)

        # Add capabilities (same as sync version)
        self.add_capability("a2a_communication", "Agent-to-Agent communication based on A2A protocol")
        self.add_capability("agent_discovery", "Discovering agents and their capabilities")
        self.add_capability("task_management", "Assigning and managing tasks between agents")
        self.add_capability("industriverse_a2a_extensions", "Support for Industriverse-specific A2A enhancements")

    async def set_local_agent(self, agent: AsyncProtocolAgent) -> None:
        """Set the local agent associated with this handler."""
        async with self.lock:
            self.local_agent = agent
        self.logger.info(f"Associated local agent {agent.get_agent_type()} with ID {agent.get_agent_id()}")

    def register_a2a_message_handler(
        self,
        a2a_type: str,
        handler: Callable[[A2AMessage], Awaitable[Optional[BaseMessage]]]
    ) -> None:
        """
        Register an async handler for a specific A2A message type.
        
        Args:
            a2a_type: The type of A2A message to handle.
            handler: The async function that handles messages of this type.
        """
        self.a2a_message_handlers[a2a_type] = handler
        self.logger.debug(f"Registered async handler for A2A message type: {a2a_type}")

    async def send_a2a_message(self, message: A2AMessage) -> Optional[BaseMessage]:
        """
        Send an A2A message using the underlying async MCP handler.
        
        Args:
            message: The A2A message to send.
            
        Returns:
            The response message, if any.
        """
        if not self.mcp_handler:
            self.logger.error("Async MCP Handler not configured, cannot send A2A message")
            return MessageFactory.create_error("configuration_error", "Async MCP Handler not configured")
        
        if not message.validate():
            self.logger.error("Invalid A2A message")
            return MessageFactory.create_error("invalid_message", "The A2A message is invalid")

        async with self.lock:
             if not message.sender_id and self.local_agent:
                 message.sender_id = self.local_agent.get_agent_id()
             elif not message.sender_id:
                 self.logger.warning("Sending A2A message without sender_id")

        self.logger.debug(f"Sending A2A message type {message.a2a_type} from {message.sender_id} to {message.receiver_id}")
        return await self.mcp_handler.send_message(message)

    # --- Async Default A2A Message Handlers ---
    # (Implement async versions of _handle_* methods, similar to sync ones but using await)

    async def _handle_request_capabilities(self, message: A2AMessage) -> Optional[A2AMessage]:
        self.logger.info(f"Received request_capabilities from {message.sender_id}")
        async with self.lock:
            if not self.local_agent:
                self.logger.error("No local agent configured")
                return await self._create_a2a_error_response(message, "no_local_agent", "Handler has no local agent")
            agent_card = self.local_agent.card
            if not agent_card:
                 self.logger.error("Local agent has no AgentCard")
                 return await self._create_a2a_error_response(message, "internal_error", "Local agent has no card")
            sender_id = self.local_agent.get_agent_id()

        response_parts = [A2APart("agent_card", "application/json", agent_card.to_dict())]
        response_message = A2AMessage(
            a2a_type="capabilities_response", parts=response_parts,
            correlation_id=message.message_id, sender_id=sender_id,
            receiver_id=message.sender_id, priority=message.priority,
            security_level=message.security_level
        )
        self.logger.info(f"Sending capabilities_response to {message.sender_id}")
        return response_message

    async def _handle_capabilities_response(self, message: A2AMessage) -> None:
        self.logger.info(f"Received capabilities_response from {message.sender_id}")
        card_part = message.get_part("agent_card")
        if card_part and card_part.content_type == "application/json":
            try:
                agent_card = AgentCard.from_dict(card_part.content)
                self.logger.info(f"Received Agent Card for {agent_card.name} (ID: {agent_card.agent_id})")
                if self.discovery_service:
                    if hasattr(self.discovery_service, "register_agent_card"): 
                         await self.discovery_service.register_agent_card(agent_card)
                    else:
                         self.logger.warning("Async Discovery service does not support register_agent_card")
            except Exception as e:
                self.logger.error(f"Failed to parse AgentCard from capabilities_response: {e}")
        else:
            self.logger.warning("Capabilities response did not contain a valid agent_card part")
        return None

    async def _handle_assign_task(self, message: A2AMessage) -> Optional[A2AMessage]:
        self.logger.info(f"Received assign_task from {message.sender_id}")
        async with self.lock:
            if not self.local_agent:
                self.logger.error("No local agent configured")
                return await self._create_a2a_error_response(message, "no_local_agent", "Handler has no local agent")
            sender_id = self.local_agent.get_agent_id()

        task_part = message.get_part("task_definition")
        if task_part and task_part.content_type == "application/json":
            try:
                task_data = task_part.content
                agent_task = AgentTask.from_dict(task_data)
                agent_task.assign(sender_id)
                self.logger.info(f"Assigned task {agent_task.task_id} ({agent_task.task_type}) to local agent")

                # TODO: Integrate with local agent's async task execution logic
                # Example: await self.local_agent.queue_task(agent_task)

                status_part = A2APart("task_status_update", "application/json",
                                      {"task_id": agent_task.task_id, "status": "assigned",
                                       "timestamp": datetime.datetime.utcnow().isoformat()})
                response_message = A2AMessage(
                    a2a_type="task_status", parts=[status_part],
                    correlation_id=message.message_id, sender_id=sender_id,
                    receiver_id=message.sender_id, priority=message.priority,
                    security_level=message.security_level
                )
                return response_message
            except Exception as e:
                self.logger.error(f"Failed to parse or assign task: {e}")
                return await self._create_a2a_error_response(message, "task_error", f"Failed to process task: {e}")
        else:
            self.logger.warning("Assign task message missing task_definition part")
            return await self._create_a2a_error_response(message, "invalid_message", "Missing task_definition part")

    async def _handle_task_status(self, message: A2AMessage) -> None:
        self.logger.info(f"Received task_status update from {message.sender_id}")
        status_part = message.get_part("task_status_update")
        if status_part and status_part.content_type == "application/json":
            try:
                status_data = status_part.content
                task_id = status_data.get("task_id")
                status = status_data.get("status")
                timestamp = status_data.get("timestamp")
                self.logger.info(f"Task {task_id} status updated to {status} at {timestamp}")
                # TODO: Update local task tracking system (async)
            except Exception as e:
                self.logger.error(f"Failed to parse task status update: {e}")
        else:
            self.logger.warning("Task status message missing task_status_update part")
        return None

    async def _handle_task_result(self, message: A2AMessage) -> None:
        self.logger.info(f"Received task_result from {message.sender_id}")
        result_part = message.get_part("task_result_data")
        if result_part:
            try:
                result_data = result_part.content
                task_id = message.metadata.get("task_id")
                self.logger.info(f"Received result for task {task_id}: {result_data}")
                # TODO: Process task result (async)
            except Exception as e:
                self.logger.error(f"Failed to parse task result: {e}")
        else:
            self.logger.warning("Task result message missing task_result_data part")
        return None

    async def _handle_a2a_error(self, message: A2AMessage) -> None:
        self.logger.info(f"Received A2A error from {message.sender_id}")
        error_part = message.get_part("error_details")
        if error_part and error_part.content_type == "application/json":
            try:
                error_data = error_part.content
                error_code = error_data.get("error_code")
                error_message = error_data.get("error_message")
                related_message_id = error_data.get("related_message_id")
                self.logger.error(f"A2A Error {error_code}: {error_message} (Related to: {related_message_id})")
                # TODO: Handle error appropriately (async)
            except Exception as e:
                self.logger.error(f"Failed to parse A2A error details: {e}")
        else:
            self.logger.warning("A2A error message missing error_details part")
        return None

    async def _create_a2a_error_response(self, original_message: A2AMessage, error_code: str, error_message: str) -> A2AMessage:
        async with self.lock:
             sender_id = self.local_agent.get_agent_id() if self.local_agent else self.component_id
        error_part = A2APart("error_details", "application/json",
                             {"error_code": error_code, "error_message": error_message,
                              "related_message_id": original_message.message_id,
                              "timestamp": datetime.datetime.utcnow().isoformat()})
        error_response = A2AMessage(
            a2a_type="error", parts=[error_part],
            correlation_id=original_message.message_id, sender_id=sender_id,
            receiver_id=original_message.sender_id, priority=MessagePriority.HIGH,
            security_level=original_message.security_level
        )
        return error_response

    # --- Async ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(message, dict):
            self.logger.error("Async A2A Handler received non-dict message")
            return MessageFactory.create_error("invalid_message", "Message must be a dictionary").to_dict()

        if message.get("message_type") != "a2a" or "a2a_type" not in message:
            self.logger.warning(f"Async A2A Handler received non-A2A message type: {message.get(\'message_type\')}")
            return MessageFactory.create_error("protocol_mismatch", "Message is not in A2A format").to_dict()

        try:
            a2a_message = A2AMessage.from_dict(message)
            a2a_type = a2a_message.a2a_type

            if a2a_type in self.a2a_message_handlers:
                handler = self.a2a_message_handlers[a2a_type]
                response = await handler(a2a_message)
                if response:
                    # Send the response back via MCP
                    sent_response = await self.send_a2a_message(response)
                    return sent_response.to_dict() if sent_response else None
                else:
                    return None
            else:
                self.logger.error(f"Unsupported A2A message type: {a2a_type}")
                error_response = await self._create_a2a_error_response(a2a_message, "unsupported_type", f"Unsupported A2A message type: {a2a_type}")
                sent_response = await self.send_a2a_message(error_response)
                return sent_response.to_dict() if sent_response else None

        except Exception as e:
            self.logger.exception(f"Error processing async A2A message: {e}")
            try:
                error_response = await self._create_a2a_error_response(A2AMessage.from_dict(message), "processing_error", f"Internal error processing message: {e}")
                sent_response = await self.send_a2a_message(error_response)
                return sent_response.to_dict() if sent_response else None
            except Exception:
                 return MessageFactory.create_error("processing_error", f"Internal error processing message: {e}").to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        async with self.lock:
            local_agent_id = self.local_agent.get_agent_id() if self.local_agent else None
        return {
            "status": "healthy",
            "local_agent_id": local_agent_id,
            "discovery_service_status": "configured" if self.discovery_service else "not_configured",
            "mcp_handler_status": "configured" if self.mcp_handler else "not_configured",
            "registered_handlers": list(self.a2a_message_handlers.keys())
        }

    async def get_manifest(self) -> Dict[str, Any]:
        manifest = await super().get_manifest()
        async with self.lock:
            local_agent_id = self.local_agent.get_agent_id() if self.local_agent else None
        manifest.update({
            "local_agent_id": local_agent_id,
            "registered_handlers_count": len(self.a2a_message_handlers)
        })
        return manifest
"""
