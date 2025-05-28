"""
Base Agent Framework Module for Industriverse Workflow Automation Layer

This module defines the base agent framework for the Workflow Automation Layer,
providing the foundation for all workflow agents. It implements the core agent
capabilities, communication protocols, and lifecycle management.

The BaseAgent class is the abstract base class that all workflow agents must inherit from.
"""

import logging
import uuid
import json
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Enum representing the possible statuses of an agent."""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    TERMINATED = "terminated"


class AgentCapability(str, Enum):
    """Enum representing the possible capabilities of an agent."""
    WORKFLOW_TRIGGER = "workflow_trigger"
    CONTRACT_PARSING = "contract_parsing"
    HUMAN_INTERVENTION = "human_intervention"
    WORKFLOW_CONTROL = "workflow_control"
    N8N_INTEGRATION = "n8n_integration"
    WORKFLOW_OPTIMIZATION = "workflow_optimization"
    FEEDBACK_PROCESSING = "feedback_processing"
    CONTRACT_VERSIONING = "contract_versioning"
    WORKFLOW_SPLITTING = "workflow_splitting"
    WORKFLOW_ROUTING = "workflow_routing"
    FALLBACK_HANDLING = "fallback_handling"
    FEEDBACK_LOOP = "feedback_loop"
    CHAOS_TESTING = "chaos_testing"
    WORKFLOW_VISUALIZATION = "workflow_visualization"
    NEGOTIATION = "negotiation"
    FORENSICS = "forensics"
    MEMORY_MANAGEMENT = "memory_management"
    WORKFLOW_EVOLUTION = "workflow_evolution"


class AgentMessage(BaseModel):
    """Model representing a message sent between agents."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender_id: str
    recipient_id: str
    message_type: str
    content: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: Optional[int] = None  # Time to live in seconds
    priority: int = 0  # Higher number = higher priority


class AgentMetadata(BaseModel):
    """Model representing metadata for an agent."""
    id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    capabilities: List[AgentCapability] = Field(default_factory=list)
    trust_score: float = 0.8
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    industry: Optional[str] = None
    location: Optional[str] = None  # e.g., "edge", "cloud", "region-us-east"


class AgentConfig(BaseModel):
    """Model representing configuration for an agent."""
    id: str
    enabled: bool = True
    priority: int = 0
    timeout_seconds: int = 60
    retry_count: int = 3
    retry_delay_seconds: int = 5
    max_concurrent_tasks: int = 10
    custom_settings: Dict[str, Any] = Field(default_factory=dict)


class AgentContext(BaseModel):
    """Model representing the execution context for an agent."""
    workflow_id: Optional[str] = None
    execution_id: Optional[str] = None
    task_id: Optional[str] = None
    parent_agent_id: Optional[str] = None
    correlation_id: Optional[str] = None
    start_time: datetime = Field(default_factory=datetime.now)
    timeout_seconds: int = 60
    variables: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentResult(BaseModel):
    """Model representing the result of an agent execution."""
    success: bool
    message: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    execution_time_ms: float = 0
    next_agent_id: Optional[str] = None
    trust_impact: float = 0.0  # Positive or negative impact on trust score


class BaseAgent(ABC):
    """
    Abstract base class for all workflow agents.
    
    This class provides the foundation for all agents in the Workflow Automation Layer,
    including lifecycle management, communication, and core capabilities.
    """
    
    def __init__(self, metadata: AgentMetadata, config: Optional[AgentConfig] = None):
        """
        Initialize the BaseAgent.
        
        Args:
            metadata: The metadata for the agent
            config: Optional configuration for the agent
        """
        self.metadata = metadata
        self.config = config or AgentConfig(id=metadata.id)
        self.status = AgentStatus.IDLE
        self.current_context: Optional[AgentContext] = None
        
        # Message queue for asynchronous processing
        self.message_queue: List[AgentMessage] = []
        
        # Callbacks
        self.on_status_changed: Optional[Callable[[AgentStatus], None]] = None
        self.on_message_received: Optional[Callable[[AgentMessage], None]] = None
        self.on_execution_completed: Optional[Callable[[AgentResult], None]] = None
        
        logger.info(f"Agent {metadata.id} ({metadata.name}) initialized")
    
    @abstractmethod
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        This method must be implemented by all concrete agent classes.
        
        Args:
            context: The execution context for the agent
            
        Returns:
            The result of the agent execution
        """
        pass
    
    async def initialize(self) -> bool:
        """
        Initialize the agent.
        
        This method is called when the agent is first started.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        if not self.config.enabled:
            logger.warning(f"Agent {self.metadata.id} is disabled, skipping initialization")
            return False
        
        self._set_status(AgentStatus.INITIALIZING)
        
        try:
            # Perform any necessary initialization
            result = await self._initialize_impl()
            
            if result:
                self._set_status(AgentStatus.IDLE)
            else:
                self._set_status(AgentStatus.FAILED)
            
            return result
        
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.metadata.id}: {e}")
            self._set_status(AgentStatus.FAILED)
            return False
    
    async def _initialize_impl(self) -> bool:
        """
        Implementation of agent initialization.
        
        This method can be overridden by concrete agent classes to provide
        custom initialization logic.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        return True
    
    async def start(self, context: AgentContext) -> bool:
        """
        Start the agent with the given context.
        
        Args:
            context: The execution context for the agent
            
        Returns:
            True if the agent was started successfully, False otherwise
        """
        if not self.config.enabled:
            logger.warning(f"Agent {self.metadata.id} is disabled, cannot start")
            return False
        
        if self.status != AgentStatus.IDLE:
            logger.warning(f"Agent {self.metadata.id} is not idle (status: {self.status}), cannot start")
            return False
        
        self.current_context = context
        self._set_status(AgentStatus.RUNNING)
        
        logger.info(f"Agent {self.metadata.id} started with context: workflow_id={context.workflow_id}, execution_id={context.execution_id}")
        return True
    
    async def pause(self) -> bool:
        """
        Pause the agent.
        
        Returns:
            True if the agent was paused successfully, False otherwise
        """
        if self.status != AgentStatus.RUNNING:
            logger.warning(f"Agent {self.metadata.id} is not running (status: {self.status}), cannot pause")
            return False
        
        self._set_status(AgentStatus.PAUSED)
        
        logger.info(f"Agent {self.metadata.id} paused")
        return True
    
    async def resume(self) -> bool:
        """
        Resume the agent.
        
        Returns:
            True if the agent was resumed successfully, False otherwise
        """
        if self.status != AgentStatus.PAUSED:
            logger.warning(f"Agent {self.metadata.id} is not paused (status: {self.status}), cannot resume")
            return False
        
        self._set_status(AgentStatus.RUNNING)
        
        logger.info(f"Agent {self.metadata.id} resumed")
        return True
    
    async def terminate(self) -> bool:
        """
        Terminate the agent.
        
        Returns:
            True if the agent was terminated successfully, False otherwise
        """
        if self.status not in [AgentStatus.RUNNING, AgentStatus.PAUSED]:
            logger.warning(f"Agent {self.metadata.id} is not running or paused (status: {self.status}), cannot terminate")
            return False
        
        self._set_status(AgentStatus.TERMINATED)
        self.current_context = None
        
        logger.info(f"Agent {self.metadata.id} terminated")
        return True
    
    def _set_status(self, status: AgentStatus):
        """
        Set the agent's status and notify listeners.
        
        Args:
            status: The new status
        """
        old_status = self.status
        self.status = status
        
        if old_status != status and self.on_status_changed:
            self.on_status_changed(status)
    
    async def send_message(self, recipient_id: str, message_type: str, content: Dict[str, Any], **kwargs) -> str:
        """
        Send a message to another agent.
        
        Args:
            recipient_id: The ID of the recipient agent
            message_type: The type of message
            content: The content of the message
            **kwargs: Additional message parameters
            
        Returns:
            The ID of the sent message
        """
        message = AgentMessage(
            sender_id=self.metadata.id,
            recipient_id=recipient_id,
            message_type=message_type,
            content=content,
            **kwargs
        )
        
        # In a real implementation, this would send the message through a message broker
        # For now, we'll just log it
        logger.debug(f"Agent {self.metadata.id} sent message to {recipient_id}: {message_type}")
        
        # Notify listeners
        if self.on_message_received:
            self.on_message_received(message)
        
        return message.id
    
    async def receive_message(self, message: AgentMessage) -> bool:
        """
        Receive a message from another agent.
        
        Args:
            message: The message to receive
            
        Returns:
            True if the message was received successfully, False otherwise
        """
        if message.recipient_id != self.metadata.id:
            logger.warning(f"Agent {self.metadata.id} received message intended for {message.recipient_id}")
            return False
        
        # Add to message queue
        self.message_queue.append(message)
        
        # Notify listeners
        if self.on_message_received:
            self.on_message_received(message)
        
        logger.debug(f"Agent {self.metadata.id} received message from {message.sender_id}: {message.message_type}")
        return True
    
    async def process_messages(self) -> int:
        """
        Process all messages in the queue.
        
        Returns:
            The number of messages processed
        """
        if not self.message_queue:
            return 0
        
        count = 0
        for message in list(self.message_queue):
            try:
                await self._process_message(message)
                self.message_queue.remove(message)
                count += 1
            except Exception as e:
                logger.error(f"Failed to process message {message.id}: {e}")
        
        return count
    
    async def _process_message(self, message: AgentMessage):
        """
        Process a single message.
        
        This method can be overridden by concrete agent classes to provide
        custom message processing logic.
        
        Args:
            message: The message to process
        """
        # Default implementation does nothing
        pass
    
    async def run(self) -> AgentResult:
        """
        Run the agent with the current context.
        
        Returns:
            The result of the agent execution
        """
        if not self.current_context:
            error_msg = f"Agent {self.metadata.id} has no context, cannot run"
            logger.error(error_msg)
            return AgentResult(success=False, error=error_msg)
        
        if self.status != AgentStatus.RUNNING:
            error_msg = f"Agent {self.metadata.id} is not running (status: {self.status}), cannot run"
            logger.error(error_msg)
            return AgentResult(success=False, error=error_msg)
        
        start_time = time.time()
        
        try:
            # Process any pending messages
            await self.process_messages()
            
            # Execute the agent's main functionality
            result = await self.execute(self.current_context)
            
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            result.execution_time_ms = execution_time_ms
            
            # Update status based on result
            if result.success:
                self._set_status(AgentStatus.COMPLETED)
            else:
                self._set_status(AgentStatus.FAILED)
            
            # Clear context
            self.current_context = None
            
            # Notify listeners
            if self.on_execution_completed:
                self.on_execution_completed(result)
            
            logger.info(f"Agent {self.metadata.id} completed execution: success={result.success}, time={execution_time_ms:.2f}ms")
            return result
        
        except Exception as e:
            # Calculate execution time
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Create error result
            error_msg = f"Agent {self.metadata.id} failed with exception: {e}"
            logger.error(error_msg)
            result = AgentResult(
                success=False,
                error=error_msg,
                execution_time_ms=execution_time_ms,
                trust_impact=-0.1  # Negative impact on trust score due to exception
            )
            
            # Update status
            self._set_status(AgentStatus.FAILED)
            
            # Clear context
            self.current_context = None
            
            # Notify listeners
            if self.on_execution_completed:
                self.on_execution_completed(result)
            
            return result
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the agent to a dictionary.
        
        Returns:
            A dictionary representation of the agent
        """
        return {
            "metadata": self.metadata.dict(),
            "config": self.config.dict(),
            "status": self.status
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseAgent':
        """
        Create an agent from a dictionary.
        
        Args:
            data: The dictionary representation of the agent
            
        Returns:
            The created agent
            
        Raises:
            ValueError: If the agent type is not supported
        """
        metadata = AgentMetadata(**data["metadata"])
        config = AgentConfig(**data["config"])
        
        # This is a placeholder for a factory pattern
        # In a real implementation, this would create the appropriate agent type
        raise ValueError(f"Cannot create agent from dictionary: abstract base class")
    
    def __str__(self) -> str:
        """
        Get a string representation of the agent.
        
        Returns:
            A string representation of the agent
        """
        return f"{self.metadata.name} ({self.metadata.id}): {self.status}"
