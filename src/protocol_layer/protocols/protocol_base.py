"""
Protocol Base Classes for Industriverse Protocol Layer

This module provides the foundational classes for the protocol-native architecture
of the Industriverse Protocol Layer. It defines abstract base classes and interfaces
that all protocol components must implement.

The protocol-native architecture ensures that:
1. Every component is exposed as a protocol-aware agent with well-defined interfaces
2. All communication follows standardized message formats and interaction patterns
3. Components can be discovered, composed, and orchestrated through protocol mechanisms
4. The layer serves as a protocol mesh coordinator for the entire Industriverse ecosystem
"""

import abc
import uuid
import json
import logging
import datetime
from typing import Dict, List, Any, Optional, Union, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProtocolComponent(abc.ABC):
    """
    Abstract base class for all protocol components in the Industriverse Protocol Layer.
    
    Every component in the protocol layer must inherit from this class and implement
    its abstract methods to ensure protocol-native behavior.
    """
    
    def __init__(self, component_id: str = None, component_type: str = None):
        """
        Initialize a protocol component.
        
        Args:
            component_id: Unique identifier for this component. If None, a UUID is generated.
            component_type: Type identifier for this component.
        """
        self.component_id = component_id or str(uuid.uuid4())
        self.component_type = component_type or self.__class__.__name__
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.status = "initialized"
        self.capabilities = []
        self.dependencies = []
        self.metrics = {}
        self.logger = logging.getLogger(f"{__name__}.{self.component_type}.{self.component_id[:8]}")
        self.logger.info(f"Component {self.component_type} initialized with ID {self.component_id}")
    
    @abc.abstractmethod
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming protocol message.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
        """
        pass
    
    @abc.abstractmethod
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the component manifest describing its capabilities and interfaces.
        
        Returns:
            A dictionary containing the component manifest.
        """
        pass
    
    @abc.abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on this component.
        
        Returns:
            A dictionary containing health status information.
        """
        pass
    
    def update_status(self, status: str) -> None:
        """
        Update the component status.
        
        Args:
            status: The new status string.
        """
        self.status = status
        self.logger.info(f"Status updated to: {status}")
    
    def register_capability(self, capability: str, description: str = None) -> None:
        """
        Register a new capability for this component.
        
        Args:
            capability: The capability identifier.
            description: Optional description of the capability.
        """
        cap_info = {
            "id": capability,
            "description": description or capability
        }
        self.capabilities.append(cap_info)
        self.logger.debug(f"Registered capability: {capability}")
    
    def register_dependency(self, component_id: str, component_type: str, required: bool = True) -> None:
        """
        Register a dependency on another component.
        
        Args:
            component_id: The ID of the required component.
            component_type: The type of the required component.
            required: Whether this dependency is required or optional.
        """
        dep_info = {
            "component_id": component_id,
            "component_type": component_type,
            "required": required
        }
        self.dependencies.append(dep_info)
        self.logger.debug(f"Registered dependency: {component_type} ({component_id})")
    
    def update_metric(self, metric_name: str, value: Any) -> None:
        """
        Update a performance or health metric for this component.
        
        Args:
            metric_name: The name of the metric to update.
            value: The new value for the metric.
        """
        self.metrics[metric_name] = {
            "value": value,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self.logger.debug(f"Updated metric {metric_name}: {value}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this component to a dictionary representation.
        
        Returns:
            A dictionary representing this component.
        """
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "created_at": self.created_at,
            "status": self.status,
            "capabilities": self.capabilities,
            "dependencies": self.dependencies,
            "metrics": self.metrics
        }
    
    def __str__(self) -> str:
        """String representation of the component."""
        return f"{self.component_type}(id={self.component_id}, status={self.status})"


class ProtocolAgent(ProtocolComponent):
    """
    Base class for protocol agents that can actively participate in the protocol mesh.
    
    Protocol agents extend protocol components with additional capabilities for
    autonomous operation, discovery, and collaboration.
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = None):
        """
        Initialize a protocol agent.
        
        Args:
            agent_id: Unique identifier for this agent. If None, a UUID is generated.
            agent_type: Type identifier for this agent.
        """
        super().__init__(agent_id, agent_type)
        self.trust_score = 0.5  # Default neutral trust score
        self.roles = []
        self.permissions = []
        self.connections = []
        self.last_active = datetime.datetime.utcnow().isoformat()
        self.intent_tokens = {}
    
    def register_role(self, role: str, description: str = None) -> None:
        """
        Register a role for this agent.
        
        Args:
            role: The role identifier.
            description: Optional description of the role.
        """
        role_info = {
            "id": role,
            "description": description or role,
            "assigned_at": datetime.datetime.utcnow().isoformat()
        }
        self.roles.append(role_info)
        self.logger.debug(f"Registered role: {role}")
    
    def grant_permission(self, permission: str, scope: str = "default", expiry: str = None) -> None:
        """
        Grant a permission to this agent.
        
        Args:
            permission: The permission identifier.
            scope: The scope of the permission.
            expiry: Optional expiry time for the permission.
        """
        perm_info = {
            "id": permission,
            "scope": scope,
            "granted_at": datetime.datetime.utcnow().isoformat(),
            "expiry": expiry
        }
        self.permissions.append(perm_info)
        self.logger.debug(f"Granted permission: {permission} (scope: {scope})")
    
    def register_connection(self, target_id: str, connection_type: str, metadata: Dict[str, Any] = None) -> None:
        """
        Register a connection to another agent or component.
        
        Args:
            target_id: The ID of the target component.
            connection_type: The type of connection.
            metadata: Optional metadata about the connection.
        """
        conn_info = {
            "target_id": target_id,
            "connection_type": connection_type,
            "established_at": datetime.datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        self.connections.append(conn_info)
        self.logger.debug(f"Registered connection to {target_id} of type {connection_type}")
    
    def issue_intent_token(self, intent: str, scope: str, expiry_seconds: int = 3600) -> str:
        """
        Issue an intent token for a specific purpose.
        
        Args:
            intent: The intent identifier.
            scope: The scope of the intent.
            expiry_seconds: Validity period in seconds.
            
        Returns:
            The token identifier.
        """
        token_id = str(uuid.uuid4())
        expiry = datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry_seconds)
        
        token_info = {
            "intent": intent,
            "scope": scope,
            "issued_at": datetime.datetime.utcnow().isoformat(),
            "expiry": expiry.isoformat(),
            "issuer_id": self.component_id
        }
        
        self.intent_tokens[token_id] = token_info
        self.logger.debug(f"Issued intent token {token_id} for {intent}")
        return token_id
    
    def verify_intent_token(self, token_id: str, intent: str = None) -> bool:
        """
        Verify an intent token.
        
        Args:
            token_id: The token identifier.
            intent: Optional specific intent to verify.
            
        Returns:
            True if the token is valid, False otherwise.
        """
        if token_id not in self.intent_tokens:
            return False
        
        token = self.intent_tokens[token_id]
        now = datetime.datetime.utcnow()
        expiry = datetime.datetime.fromisoformat(token["expiry"])
        
        if now > expiry:
            self.logger.debug(f"Token {token_id} has expired")
            return False
        
        if intent and token["intent"] != intent:
            self.logger.debug(f"Token {token_id} intent mismatch: expected {intent}, got {token['intent']}")
            return False
        
        return True
    
    def update_activity(self) -> None:
        """Update the last active timestamp for this agent."""
        self.last_active = datetime.datetime.utcnow().isoformat()
    
    def update_trust_score(self, delta: float) -> None:
        """
        Update the trust score for this agent.
        
        Args:
            delta: The change in trust score (-1.0 to 1.0).
        """
        self.trust_score = max(0.0, min(1.0, self.trust_score + delta))
        self.logger.debug(f"Updated trust score to {self.trust_score}")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this agent to a dictionary representation.
        
        Returns:
            A dictionary representing this agent.
        """
        base_dict = super().to_dict()
        agent_dict = {
            "trust_score": self.trust_score,
            "roles": self.roles,
            "permissions": self.permissions,
            "connections": self.connections,
            "last_active": self.last_active
        }
        return {**base_dict, **agent_dict}


class ProtocolService(ProtocolComponent):
    """
    Base class for protocol services that provide functionality to other components.
    
    Protocol services extend protocol components with additional capabilities for
    service registration, discovery, and management.
    """
    
    def __init__(self, service_id: str = None, service_type: str = None):
        """
        Initialize a protocol service.
        
        Args:
            service_id: Unique identifier for this service. If None, a UUID is generated.
            service_type: Type identifier for this service.
        """
        super().__init__(service_id, service_type)
        self.endpoints = {}
        self.service_level = "standard"
        self.version = "1.0.0"
        self.uptime_start = datetime.datetime.utcnow().isoformat()
    
    def register_endpoint(self, endpoint_name: str, handler: Callable, description: str = None) -> None:
        """
        Register a service endpoint.
        
        Args:
            endpoint_name: The name of the endpoint.
            handler: The function that handles requests to this endpoint.
            description: Optional description of the endpoint.
        """
        endpoint_info = {
            "name": endpoint_name,
            "description": description or endpoint_name,
            "handler": handler
        }
        self.endpoints[endpoint_name] = endpoint_info
        self.logger.debug(f"Registered endpoint: {endpoint_name}")
    
    def handle_request(self, endpoint_name: str, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a request to a specific endpoint.
        
        Args:
            endpoint_name: The name of the endpoint to call.
            request: The request data.
            
        Returns:
            The response data.
            
        Raises:
            ValueError: If the endpoint does not exist.
        """
        if endpoint_name not in self.endpoints:
            raise ValueError(f"Endpoint {endpoint_name} not found")
        
        self.logger.debug(f"Handling request to endpoint {endpoint_name}")
        handler = self.endpoints[endpoint_name]["handler"]
        return handler(request)
    
    def get_uptime(self) -> float:
        """
        Get the service uptime in seconds.
        
        Returns:
            The uptime in seconds.
        """
        start_time = datetime.datetime.fromisoformat(self.uptime_start)
        now = datetime.datetime.utcnow()
        return (now - start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this service to a dictionary representation.
        
        Returns:
            A dictionary representing this service.
        """
        base_dict = super().to_dict()
        
        # Create a version of endpoints dict without the handler functions
        endpoints_dict = {}
        for name, info in self.endpoints.items():
            endpoints_dict[name] = {
                "name": info["name"],
                "description": info["description"]
            }
        
        service_dict = {
            "endpoints": endpoints_dict,
            "service_level": self.service_level,
            "version": self.version,
            "uptime_start": self.uptime_start,
            "uptime_seconds": self.get_uptime()
        }
        return {**base_dict, **service_dict}


class ProtocolMessage:
    """
    Base class for protocol messages in the Industriverse Protocol Layer.
    
    This class provides a standardized format for all messages exchanged between
    protocol components, ensuring consistent handling and traceability.
    """
    
    def __init__(
        self,
        message_type: str,
        sender_id: str,
        receiver_id: str = None,
        payload: Dict[str, Any] = None,
        message_id: str = None,
        correlation_id: str = None,
        priority: str = "normal",
        security_level: str = "standard",
        reflex_timer_ms: int = None
    ):
        """
        Initialize a protocol message.
        
        Args:
            message_type: The type of message.
            sender_id: The ID of the sending component.
            receiver_id: The ID of the receiving component, if known.
            payload: The message payload.
            message_id: Unique identifier for this message. If None, a UUID is generated.
            correlation_id: ID linking related messages in a conversation.
            priority: Message priority (low, normal, high, critical).
            security_level: Security level (standard, elevated, high).
            reflex_timer_ms: Optional reflex timer in milliseconds.
        """
        self.message_type = message_type
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.payload = payload or {}
        self.message_id = message_id or str(uuid.uuid4())
        self.correlation_id = correlation_id
        self.timestamp = datetime.datetime.utcnow().isoformat()
        self.priority = priority
        self.security_level = security_level
        self.reflex_timer_ms = reflex_timer_ms
        self.hops = []
    
    def add_hop(self, component_id: str, timestamp: str = None) -> None:
        """
        Record a hop in the message's journey.
        
        Args:
            component_id: The ID of the component that processed the message.
            timestamp: The timestamp of the hop. If None, current time is used.
        """
        hop_info = {
            "component_id": component_id,
            "timestamp": timestamp or datetime.datetime.utcnow().isoformat()
        }
        self.hops.append(hop_info)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this message to a dictionary representation.
        
        Returns:
            A dictionary representing this message.
        """
        return {
            "message_id": self.message_id,
            "message_type": self.message_type,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "priority": self.priority,
            "security_level": self.security_level,
            "reflex_timer_ms": self.reflex_timer_ms,
            "payload": self.payload,
            "hops": self.hops
        }
    
    def to_json(self) -> str:
        """
        Convert this message to a JSON string.
        
        Returns:
            A JSON string representing this message.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtocolMessage':
        """
        Create a message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new ProtocolMessage instance.
        """
        msg = cls(
            message_type=data["message_type"],
            sender_id=data["sender_id"],
            receiver_id=data.get("receiver_id"),
            payload=data.get("payload", {}),
            message_id=data.get("message_id"),
            correlation_id=data.get("correlation_id"),
            priority=data.get("priority", "normal"),
            security_level=data.get("security_level", "standard"),
            reflex_timer_ms=data.get("reflex_timer_ms")
        )
        
        msg.timestamp = data.get("timestamp", msg.timestamp)
        msg.hops = data.get("hops", [])
        
        return msg
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ProtocolMessage':
        """
        Create a message from a JSON string.
        
        Args:
            json_str: The JSON string containing message data.
            
        Returns:
            A new ProtocolMessage instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class UnifiedMessageEnvelope:
    """
    Unified Message Envelope (UME) for cross-protocol communication.
    
    The UME acts as a "carrier envelope" across cross-protocol transitions,
    preserving context and enabling observability.
    """
    
    def __init__(
        self,
        origin_protocol: str,
        target_protocol: str,
        payload: Dict[str, Any],
        context: Dict[str, Any] = None,
        trace_id: str = None,
        security_level: str = "standard",
        reflex_timer_ms: int = None
    ):
        """
        Initialize a unified message envelope.
        
        Args:
            origin_protocol: The originating protocol (e.g., "MCP", "A2A").
            target_protocol: The target protocol.
            payload: The message payload.
            context: Additional context information.
            trace_id: Unique trace identifier. If None, a UUID is generated.
            security_level: Security level (standard, elevated, high).
            reflex_timer_ms: Optional reflex timer in milliseconds.
        """
        self.origin_protocol = origin_protocol
        self.target_protocol = target_protocol
        self.payload = payload
        self.context = context or {}
        self.trace_id = trace_id or str(uuid.uuid4())
        self.security_level = security_level
        self.reflex_timer_ms = reflex_timer_ms
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.transitions = []
    
    def add_transition(self, from_protocol: str, to_protocol: str, component_id: str) -> None:
        """
        Record a protocol transition.
        
        Args:
            from_protocol: The source protocol.
            to_protocol: The destination protocol.
            component_id: The ID of the component that performed the transition.
        """
        transition_info = {
            "from_protocol": from_protocol,
            "to_protocol": to_protocol,
            "component_id": component_id,
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
        self.transitions.append(transition_info)
    
    def update_context(self, key: str, value: Any) -> None:
        """
        Update a context value.
        
        Args:
            key: The context key to update.
            value: The new value.
        """
        self.context[key] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this envelope to a dictionary representation.
        
        Returns:
            A dictionary representing this envelope.
        """
        return {
            "origin_protocol": self.origin_protocol,
            "target_protocol": self.target_protocol,
            "payload": self.payload,
            "context": self.context,
            "trace_id": self.trace_id,
            "security_level": self.security_level,
            "reflex_timer_ms": self.reflex_timer_ms,
            "created_at": self.created_at,
            "transitions": self.transitions
        }
    
    def to_json(self) -> str:
        """
        Convert this envelope to a JSON string.
        
        Returns:
            A JSON string representing this envelope.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UnifiedMessageEnvelope':
        """
        Create an envelope from a dictionary representation.
        
        Args:
            data: The dictionary containing envelope data.
            
        Returns:
            A new UnifiedMessageEnvelope instance.
        """
        envelope = cls(
            origin_protocol=data["origin_protocol"],
            target_protocol=data["target_protocol"],
            payload=data["payload"],
            context=data.get("context", {}),
            trace_id=data.get("trace_id"),
            security_level=data.get("security_level", "standard"),
            reflex_timer_ms=data.get("reflex_timer_ms")
        )
        
        envelope.created_at = data.get("created_at", envelope.created_at)
        envelope.transitions = data.get("transitions", [])
        
        return envelope
    
    @classmethod
    def from_json(cls, json_str: str) -> 'UnifiedMessageEnvelope':
        """
        Create an envelope from a JSON string.
        
        Args:
            json_str: The JSON string containing envelope data.
            
        Returns:
            A new UnifiedMessageEnvelope instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class ProtocolRegistry:
    """
    Registry for protocol components, agents, and services.
    
    The registry provides discovery and lookup capabilities for the protocol mesh.
    """
    
    def __init__(self):
        """Initialize a protocol registry."""
        self.components = {}
        self.agents = {}
        self.services = {}
        self.logger = logging.getLogger(f"{__name__}.ProtocolRegistry")
    
    def register_component(self, component: ProtocolComponent) -> None:
        """
        Register a protocol component.
        
        Args:
            component: The component to register.
        """
        self.components[component.component_id] = component
        self.logger.info(f"Registered component {component.component_type} with ID {component.component_id}")
        
        if isinstance(component, ProtocolAgent):
            self.agents[component.component_id] = component
            self.logger.info(f"Registered agent {component.component_type} with ID {component.component_id}")
        
        if isinstance(component, ProtocolService):
            self.services[component.component_id] = component
            self.logger.info(f"Registered service {component.component_type} with ID {component.component_id}")
    
    def unregister_component(self, component_id: str) -> None:
        """
        Unregister a protocol component.
        
        Args:
            component_id: The ID of the component to unregister.
        """
        if component_id in self.components:
            component = self.components[component_id]
            self.logger.info(f"Unregistered component {component.component_type} with ID {component_id}")
            del self.components[component_id]
            
            if component_id in self.agents:
                del self.agents[component_id]
            
            if component_id in self.services:
                del self.services[component_id]
    
    def get_component(self, component_id: str) -> Optional[ProtocolComponent]:
        """
        Get a component by ID.
        
        Args:
            component_id: The ID of the component to retrieve.
            
        Returns:
            The component, or None if not found.
        """
        return self.components.get(component_id)
    
    def get_agent(self, agent_id: str) -> Optional[ProtocolAgent]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: The ID of the agent to retrieve.
            
        Returns:
            The agent, or None if not found.
        """
        return self.agents.get(agent_id)
    
    def get_service(self, service_id: str) -> Optional[ProtocolService]:
        """
        Get a service by ID.
        
        Args:
            service_id: The ID of the service to retrieve.
            
        Returns:
            The service, or None if not found.
        """
        return self.services.get(service_id)
    
    def find_components_by_type(self, component_type: str) -> List[ProtocolComponent]:
        """
        Find components by type.
        
        Args:
            component_type: The type of components to find.
            
        Returns:
            A list of matching components.
        """
        return [c for c in self.components.values() if c.component_type == component_type]
    
    def find_agents_by_role(self, role: str) -> List[ProtocolAgent]:
        """
        Find agents by role.
        
        Args:
            role: The role to search for.
            
        Returns:
            A list of matching agents.
        """
        return [a for a in self.agents.values() if any(r["id"] == role for r in a.roles)]
    
    def find_services_by_capability(self, capability: str) -> List[ProtocolService]:
        """
        Find services by capability.
        
        Args:
            capability: The capability to search for.
            
        Returns:
            A list of matching services.
        """
        return [s for s in self.services.values() if any(c["id"] == capability for c in s.capabilities)]
    
    def get_all_components(self) -> List[ProtocolComponent]:
        """
        Get all registered components.
        
        Returns:
            A list of all components.
        """
        return list(self.components.values())
    
    def get_all_agents(self) -> List[ProtocolAgent]:
        """
        Get all registered agents.
        
        Returns:
            A list of all agents.
        """
        return list(self.agents.values())
    
    def get_all_services(self) -> List[ProtocolService]:
        """
        Get all registered services.
        
        Returns:
            A list of all services.
        """
        return list(self.services.values())
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this registry to a dictionary representation.
        
        Returns:
            A dictionary representing this registry.
        """
        return {
            "components_count": len(self.components),
            "agents_count": len(self.agents),
            "services_count": len(self.services),
            "components": {cid: c.to_dict() for cid, c in self.components.items()}
        }
