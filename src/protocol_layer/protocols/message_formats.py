"""
Standardized Message Format Definitions for Industriverse Protocol Layer

This module defines the standardized message formats used throughout the
Industriverse Protocol Layer. It provides classes and utilities for creating,
validating, and processing protocol messages with consistent formats.

The standardized message formats ensure:
1. Consistent communication patterns across all protocol components
2. Proper message validation and error handling
3. Interoperability between different protocol implementations
4. Support for advanced features like reflex timers and context preservation
"""

import uuid
import json
import datetime
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union, TypeVar, Generic

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MessagePriority(Enum):
    """Enumeration of message priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityLevel(Enum):
    """Enumeration of security levels."""
    STANDARD = "standard"
    ELEVATED = "elevated"
    HIGH = "high"


class MessageType(Enum):
    """Enumeration of common message types."""
    # Core message types
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    COMMAND = "command"
    QUERY = "query"
    
    # Protocol-specific message types
    DISCOVERY = "discovery"
    REGISTRATION = "registration"
    HEARTBEAT = "heartbeat"
    STATUS = "status"
    ERROR = "error"
    
    # Task-related message types
    TASK_ASSIGNMENT = "task_assignment"
    TASK_STATUS = "task_status"
    TASK_RESULT = "task_result"
    
    # Workflow-related message types
    WORKFLOW_START = "workflow_start"
    WORKFLOW_STATUS = "workflow_status"
    WORKFLOW_RESULT = "workflow_result"
    
    # Security-related message types
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    ATTESTATION = "attestation"
    
    # Protocol management message types
    PROTOCOL_VERSION = "protocol_version"
    PROTOCOL_EXTENSION = "protocol_extension"
    PROTOCOL_REROUTE = "protocol_reroute"
    
    # AlphaEvolve-related message types
    ALGORITHM_TASK = "algorithm_task"
    ALGORITHM_RESULT = "algorithm_result"
    ALGORITHM_EVOLUTION = "algorithm_evolution"


class MessageStatus(Enum):
    """Enumeration of message status values."""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    PROCESSING = "processing"
    TIMEOUT = "timeout"
    REJECTED = "rejected"


class BaseMessage:
    """
    Base class for all protocol messages.
    
    This class provides common functionality for all message types,
    including serialization, validation, and metadata handling.
    """
    
    def __init__(
        self,
        message_id: str = None,
        correlation_id: str = None,
        timestamp: str = None,
        sender_id: str = None,
        receiver_id: str = None,
        message_type: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.NORMAL,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a base message.
        
        Args:
            message_id: Unique identifier for this message. If None, a UUID is generated.
            correlation_id: ID linking related messages in a conversation.
            timestamp: Message creation timestamp. If None, current time is used.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            message_type: Type of message.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
        """
        self.message_id = message_id or str(uuid.uuid4())
        self.correlation_id = correlation_id
        self.timestamp = timestamp or datetime.datetime.utcnow().isoformat()
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.message_type = message_type
        
        # Handle priority as either string or enum
        if isinstance(priority, str):
            try:
                self.priority = MessagePriority(priority)
            except ValueError:
                self.priority = MessagePriority.NORMAL
        else:
            self.priority = priority
        
        # Handle security level as either string or enum
        if isinstance(security_level, str):
            try:
                self.security_level = SecurityLevel(security_level)
            except ValueError:
                self.security_level = SecurityLevel.STANDARD
        else:
            self.security_level = security_level
        
        self.reflex_timer_ms = reflex_timer_ms
        self.metadata = metadata or {}
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
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add a metadata item to this message.
        
        Args:
            key: Metadata key.
            value: Metadata value.
        """
        self.metadata[key] = value
    
    def validate(self) -> bool:
        """
        Validate this message.
        
        Returns:
            True if the message is valid, False otherwise.
        """
        # Basic validation
        if not self.message_id:
            logger.error("Message validation failed: missing message_id")
            return False
        
        if not self.timestamp:
            logger.error("Message validation failed: missing timestamp")
            return False
        
        if not self.message_type:
            logger.error("Message validation failed: missing message_type")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this message to a dictionary representation.
        
        Returns:
            A dictionary representing this message.
        """
        return {
            "message_id": self.message_id,
            "correlation_id": self.correlation_id,
            "timestamp": self.timestamp,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "message_type": self.message_type,
            "priority": self.priority.value if isinstance(self.priority, MessagePriority) else self.priority,
            "security_level": self.security_level.value if isinstance(self.security_level, SecurityLevel) else self.security_level,
            "reflex_timer_ms": self.reflex_timer_ms,
            "metadata": self.metadata,
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
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseMessage':
        """
        Create a message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new BaseMessage instance.
        """
        return cls(
            message_id=data.get("message_id"),
            correlation_id=data.get("correlation_id"),
            timestamp=data.get("timestamp"),
            sender_id=data.get("sender_id"),
            receiver_id=data.get("receiver_id"),
            message_type=data.get("message_type"),
            priority=data.get("priority", MessagePriority.NORMAL.value),
            security_level=data.get("security_level", SecurityLevel.STANDARD.value),
            reflex_timer_ms=data.get("reflex_timer_ms"),
            metadata=data.get("metadata", {})
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'BaseMessage':
        """
        Create a message from a JSON string.
        
        Args:
            json_str: The JSON string containing message data.
            
        Returns:
            A new BaseMessage instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


T = TypeVar('T')

class RequestMessage(BaseMessage, Generic[T]):
    """
    Request message for protocol operations.
    
    This class represents a request for an operation to be performed,
    with a payload containing the request parameters.
    """
    
    def __init__(
        self,
        operation: str,
        payload: T = None,
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
        """
        Initialize a request message.
        
        Args:
            operation: The operation being requested.
            payload: The request payload.
            message_id: Unique identifier for this message. If None, a UUID is generated.
            correlation_id: ID linking related messages in a conversation.
            timestamp: Message creation timestamp. If None, current time is used.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
        """
        super().__init__(
            message_id=message_id,
            correlation_id=correlation_id,
            timestamp=timestamp,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.REQUEST.value,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
        self.operation = operation
        self.payload = payload
    
    def validate(self) -> bool:
        """
        Validate this request message.
        
        Returns:
            True if the message is valid, False otherwise.
        """
        if not super().validate():
            return False
        
        if not self.operation:
            logger.error("Request validation failed: missing operation")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this request message to a dictionary representation.
        
        Returns:
            A dictionary representing this request message.
        """
        base_dict = super().to_dict()
        request_dict = {
            "operation": self.operation,
            "payload": self.payload
        }
        return {**base_dict, **request_dict}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RequestMessage':
        """
        Create a request message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new RequestMessage instance.
        """
        msg = super(RequestMessage, cls).from_dict(data)
        msg.operation = data.get("operation")
        msg.payload = data.get("payload")
        return msg


class ResponseMessage(BaseMessage, Generic[T]):
    """
    Response message for protocol operations.
    
    This class represents a response to a request, with a payload
    containing the response data and a status indicating success or failure.
    """
    
    def __init__(
        self,
        request_id: str,
        status: Union[str, MessageStatus],
        payload: T = None,
        error: str = None,
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
        """
        Initialize a response message.
        
        Args:
            request_id: The ID of the request being responded to.
            status: The status of the response.
            payload: The response payload.
            error: Error message, if any.
            message_id: Unique identifier for this message. If None, a UUID is generated.
            correlation_id: ID linking related messages in a conversation.
            timestamp: Message creation timestamp. If None, current time is used.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
        """
        super().__init__(
            message_id=message_id,
            correlation_id=correlation_id or request_id,
            timestamp=timestamp,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.RESPONSE.value,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
        self.request_id = request_id
        
        # Handle status as either string or enum
        if isinstance(status, str):
            try:
                self.status = MessageStatus(status)
            except ValueError:
                self.status = MessageStatus.FAILURE
        else:
            self.status = status
        
        self.payload = payload
        self.error = error
    
    def validate(self) -> bool:
        """
        Validate this response message.
        
        Returns:
            True if the message is valid, False otherwise.
        """
        if not super().validate():
            return False
        
        if not self.request_id:
            logger.error("Response validation failed: missing request_id")
            return False
        
        if not self.status:
            logger.error("Response validation failed: missing status")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this response message to a dictionary representation.
        
        Returns:
            A dictionary representing this response message.
        """
        base_dict = super().to_dict()
        response_dict = {
            "request_id": self.request_id,
            "status": self.status.value if isinstance(self.status, MessageStatus) else self.status,
            "payload": self.payload,
            "error": self.error
        }
        return {**base_dict, **response_dict}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseMessage':
        """
        Create a response message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new ResponseMessage instance.
        """
        msg = super(ResponseMessage, cls).from_dict(data)
        msg.request_id = data.get("request_id")
        msg.status = data.get("status")
        msg.payload = data.get("payload")
        msg.error = data.get("error")
        return msg


class EventMessage(BaseMessage, Generic[T]):
    """
    Event message for protocol notifications.
    
    This class represents an event notification, with a payload
    containing the event data and an event type.
    """
    
    def __init__(
        self,
        event_type: str,
        payload: T = None,
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
        """
        Initialize an event message.
        
        Args:
            event_type: The type of event.
            payload: The event payload.
            message_id: Unique identifier for this message. If None, a UUID is generated.
            correlation_id: ID linking related messages in a conversation.
            timestamp: Message creation timestamp. If None, current time is used.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
        """
        super().__init__(
            message_id=message_id,
            correlation_id=correlation_id,
            timestamp=timestamp,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.EVENT.value,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
        self.event_type = event_type
        self.payload = payload
    
    def validate(self) -> bool:
        """
        Validate this event message.
        
        Returns:
            True if the message is valid, False otherwise.
        """
        if not super().validate():
            return False
        
        if not self.event_type:
            logger.error("Event validation failed: missing event_type")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this event message to a dictionary representation.
        
        Returns:
            A dictionary representing this event message.
        """
        base_dict = super().to_dict()
        event_dict = {
            "event_type": self.event_type,
            "payload": self.payload
        }
        return {**base_dict, **event_dict}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventMessage':
        """
        Create an event message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new EventMessage instance.
        """
        msg = super(EventMessage, cls).from_dict(data)
        msg.event_type = data.get("event_type")
        msg.payload = data.get("payload")
        return msg


class CommandMessage(BaseMessage, Generic[T]):
    """
    Command message for protocol operations.
    
    This class represents a command to be executed, with a payload
    containing the command parameters.
    """
    
    def __init__(
        self,
        command: str,
        payload: T = None,
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
        """
        Initialize a command message.
        
        Args:
            command: The command to execute.
            payload: The command payload.
            message_id: Unique identifier for this message. If None, a UUID is generated.
            correlation_id: ID linking related messages in a conversation.
            timestamp: Message creation timestamp. If None, current time is used.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
        """
        super().__init__(
            message_id=message_id,
            correlation_id=correlation_id,
            timestamp=timestamp,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.COMMAND.value,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
        self.command = command
        self.payload = payload
    
    def validate(self) -> bool:
        """
        Validate this command message.
        
        Returns:
            True if the message is valid, False otherwise.
        """
        if not super().validate():
            return False
        
        if not self.command:
            logger.error("Command validation failed: missing command")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this command message to a dictionary representation.
        
        Returns:
            A dictionary representing this command message.
        """
        base_dict = super().to_dict()
        command_dict = {
            "command": self.command,
            "payload": self.payload
        }
        return {**base_dict, **command_dict}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CommandMessage':
        """
        Create a command message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new CommandMessage instance.
        """
        msg = super(CommandMessage, cls).from_dict(data)
        msg.command = data.get("command")
        msg.payload = data.get("payload")
        return msg


class QueryMessage(BaseMessage, Generic[T]):
    """
    Query message for protocol operations.
    
    This class represents a query for information, with a payload
    containing the query parameters.
    """
    
    def __init__(
        self,
        query: str,
        payload: T = None,
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
        """
        Initialize a query message.
        
        Args:
            query: The query to execute.
            payload: The query payload.
            message_id: Unique identifier for this message. If None, a UUID is generated.
            correlation_id: ID linking related messages in a conversation.
            timestamp: Message creation timestamp. If None, current time is used.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
        """
        super().__init__(
            message_id=message_id,
            correlation_id=correlation_id,
            timestamp=timestamp,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.QUERY.value,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
        self.query = query
        self.payload = payload
    
    def validate(self) -> bool:
        """
        Validate this query message.
        
        Returns:
            True if the message is valid, False otherwise.
        """
        if not super().validate():
            return False
        
        if not self.query:
            logger.error("Query validation failed: missing query")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this query message to a dictionary representation.
        
        Returns:
            A dictionary representing this query message.
        """
        base_dict = super().to_dict()
        query_dict = {
            "query": self.query,
            "payload": self.payload
        }
        return {**base_dict, **query_dict}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QueryMessage':
        """
        Create a query message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new QueryMessage instance.
        """
        msg = super(QueryMessage, cls).from_dict(data)
        msg.query = data.get("query")
        msg.payload = data.get("payload")
        return msg


class ErrorMessage(BaseMessage):
    """
    Error message for protocol operations.
    
    This class represents an error notification, with details about
    the error that occurred.
    """
    
    def __init__(
        self,
        error_code: str,
        error_message: str,
        related_message_id: str = None,
        details: Dict[str, Any] = None,
        message_id: str = None,
        correlation_id: str = None,
        timestamp: str = None,
        sender_id: str = None,
        receiver_id: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.HIGH,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize an error message.
        
        Args:
            error_code: The error code.
            error_message: The error message.
            related_message_id: The ID of the message that caused the error.
            details: Additional error details.
            message_id: Unique identifier for this message. If None, a UUID is generated.
            correlation_id: ID linking related messages in a conversation.
            timestamp: Message creation timestamp. If None, current time is used.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
        """
        super().__init__(
            message_id=message_id,
            correlation_id=correlation_id,
            timestamp=timestamp,
            sender_id=sender_id,
            receiver_id=receiver_id,
            message_type=MessageType.ERROR.value,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
        self.error_code = error_code
        self.error_message = error_message
        self.related_message_id = related_message_id
        self.details = details or {}
    
    def validate(self) -> bool:
        """
        Validate this error message.
        
        Returns:
            True if the message is valid, False otherwise.
        """
        if not super().validate():
            return False
        
        if not self.error_code:
            logger.error("Error validation failed: missing error_code")
            return False
        
        if not self.error_message:
            logger.error("Error validation failed: missing error_message")
            return False
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this error message to a dictionary representation.
        
        Returns:
            A dictionary representing this error message.
        """
        base_dict = super().to_dict()
        error_dict = {
            "error_code": self.error_code,
            "error_message": self.error_message,
            "related_message_id": self.related_message_id,
            "details": self.details
        }
        return {**base_dict, **error_dict}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErrorMessage':
        """
        Create an error message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new ErrorMessage instance.
        """
        msg = super(ErrorMessage, cls).from_dict(data)
        msg.error_code = data.get("error_code")
        msg.error_message = data.get("error_message")
        msg.related_message_id = data.get("related_message_id")
        msg.details = data.get("details", {})
        return msg


class MessageFactory:
    """
    Factory for creating protocol messages.
    
    This class provides methods for creating various types of protocol messages
    with consistent formats and validation.
    """
    
    @staticmethod
    def create_request(
        operation: str,
        payload: Any = None,
        sender_id: str = None,
        receiver_id: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.NORMAL,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ) -> RequestMessage:
        """
        Create a request message.
        
        Args:
            operation: The operation being requested.
            payload: The request payload.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
            
        Returns:
            A new RequestMessage instance.
        """
        return RequestMessage(
            operation=operation,
            payload=payload,
            sender_id=sender_id,
            receiver_id=receiver_id,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
    
    @staticmethod
    def create_response(
        request_id: str,
        status: Union[str, MessageStatus] = MessageStatus.SUCCESS,
        payload: Any = None,
        error: str = None,
        sender_id: str = None,
        receiver_id: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.NORMAL,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ) -> ResponseMessage:
        """
        Create a response message.
        
        Args:
            request_id: The ID of the request being responded to.
            status: The status of the response.
            payload: The response payload.
            error: Error message, if any.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
            
        Returns:
            A new ResponseMessage instance.
        """
        return ResponseMessage(
            request_id=request_id,
            status=status,
            payload=payload,
            error=error,
            sender_id=sender_id,
            receiver_id=receiver_id,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
    
    @staticmethod
    def create_event(
        event_type: str,
        payload: Any = None,
        sender_id: str = None,
        receiver_id: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.NORMAL,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ) -> EventMessage:
        """
        Create an event message.
        
        Args:
            event_type: The type of event.
            payload: The event payload.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
            
        Returns:
            A new EventMessage instance.
        """
        return EventMessage(
            event_type=event_type,
            payload=payload,
            sender_id=sender_id,
            receiver_id=receiver_id,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
    
    @staticmethod
    def create_command(
        command: str,
        payload: Any = None,
        sender_id: str = None,
        receiver_id: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.NORMAL,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ) -> CommandMessage:
        """
        Create a command message.
        
        Args:
            command: The command to execute.
            payload: The command payload.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
            
        Returns:
            A new CommandMessage instance.
        """
        return CommandMessage(
            command=command,
            payload=payload,
            sender_id=sender_id,
            receiver_id=receiver_id,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
    
    @staticmethod
    def create_query(
        query: str,
        payload: Any = None,
        sender_id: str = None,
        receiver_id: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.NORMAL,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ) -> QueryMessage:
        """
        Create a query message.
        
        Args:
            query: The query to execute.
            payload: The query payload.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
            
        Returns:
            A new QueryMessage instance.
        """
        return QueryMessage(
            query=query,
            payload=payload,
            sender_id=sender_id,
            receiver_id=receiver_id,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
    
    @staticmethod
    def create_error(
        error_code: str,
        error_message: str,
        related_message_id: str = None,
        details: Dict[str, Any] = None,
        sender_id: str = None,
        receiver_id: str = None,
        priority: Union[str, MessagePriority] = MessagePriority.HIGH,
        security_level: Union[str, SecurityLevel] = SecurityLevel.STANDARD,
        reflex_timer_ms: int = None,
        metadata: Dict[str, Any] = None
    ) -> ErrorMessage:
        """
        Create an error message.
        
        Args:
            error_code: The error code.
            error_message: The error message.
            related_message_id: The ID of the message that caused the error.
            details: Additional error details.
            sender_id: ID of the sending component.
            receiver_id: ID of the receiving component.
            priority: Message priority.
            security_level: Security level.
            reflex_timer_ms: Optional reflex timer in milliseconds.
            metadata: Additional metadata for the message.
            
        Returns:
            A new ErrorMessage instance.
        """
        return ErrorMessage(
            error_code=error_code,
            error_message=error_message,
            related_message_id=related_message_id,
            details=details,
            sender_id=sender_id,
            receiver_id=receiver_id,
            priority=priority,
            security_level=security_level,
            reflex_timer_ms=reflex_timer_ms,
            metadata=metadata
        )
    
    @staticmethod
    def create_from_dict(data: Dict[str, Any]) -> BaseMessage:
        """
        Create a message from a dictionary representation.
        
        Args:
            data: The dictionary containing message data.
            
        Returns:
            A new message instance of the appropriate type.
        """
        message_type = data.get("message_type")
        
        if message_type == MessageType.REQUEST.value:
            return RequestMessage.from_dict(data)
        elif message_type == MessageType.RESPONSE.value:
            return ResponseMessage.from_dict(data)
        elif message_type == MessageType.EVENT.value:
            return EventMessage.from_dict(data)
        elif message_type == MessageType.COMMAND.value:
            return CommandMessage.from_dict(data)
        elif message_type == MessageType.QUERY.value:
            return QueryMessage.from_dict(data)
        elif message_type == MessageType.ERROR.value:
            return ErrorMessage.from_dict(data)
        else:
            return BaseMessage.from_dict(data)
    
    @staticmethod
    def create_from_json(json_str: str) -> BaseMessage:
        """
        Create a message from a JSON string.
        
        Args:
            json_str: The JSON string containing message data.
            
        Returns:
            A new message instance of the appropriate type.
        """
        data = json.loads(json_str)
        return MessageFactory.create_from_dict(data)
