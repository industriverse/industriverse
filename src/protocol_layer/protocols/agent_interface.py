"""
Agent Interface Definitions for Industriverse Protocol Layer

This module defines the interfaces that all protocol-aware agents must implement
to participate in the Industriverse Protocol Layer. It provides abstract classes
and concrete implementations for agent discovery, communication, and orchestration.

The agent interfaces ensure that:
1. Agents can be discovered and addressed through standard protocols
2. Agents can communicate using standardized message formats
3. Agents can be orchestrated and composed into complex workflows
4. Agents can participate in the protocol mesh with well-defined behaviors
"""

import abc
import uuid
import json
import logging
import datetime
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable

from protocols.protocol_base import ProtocolComponent, ProtocolAgent, ProtocolMessage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentInterface(abc.ABC):
    """
    Abstract interface that all protocol-aware agents must implement.
    
    This interface defines the core capabilities required for an agent to
    participate in the Industriverse Protocol Layer.
    """
    
    @abc.abstractmethod
    def get_agent_id(self) -> str:
        """
        Get the unique identifier for this agent.
        
        Returns:
            The agent's unique identifier.
        """
        pass
    
    @abc.abstractmethod
    def get_agent_type(self) -> str:
        """
        Get the type identifier for this agent.
        
        Returns:
            The agent's type identifier.
        """
        pass
    
    @abc.abstractmethod
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the capabilities of this agent.
        
        Returns:
            A list of capability descriptors.
        """
        pass
    
    @abc.abstractmethod
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
        """
        pass
    
    @abc.abstractmethod
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the agent manifest.
        
        Returns:
            A dictionary containing the agent manifest.
        """
        pass


class AsyncAgentInterface(abc.ABC):
    """
    Abstract interface for asynchronous protocol-aware agents.
    
    This interface extends the basic AgentInterface with asynchronous
    processing capabilities for high-performance protocol handling.
    """
    
    @abc.abstractmethod
    def get_agent_id(self) -> str:
        """
        Get the unique identifier for this agent.
        
        Returns:
            The agent's unique identifier.
        """
        pass
    
    @abc.abstractmethod
    def get_agent_type(self) -> str:
        """
        Get the type identifier for this agent.
        
        Returns:
            The agent's type identifier.
        """
        pass
    
    @abc.abstractmethod
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the capabilities of this agent.
        
        Returns:
            A list of capability descriptors.
        """
        pass
    
    @abc.abstractmethod
    async def process_message_async(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message asynchronously.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
        """
        pass
    
    @abc.abstractmethod
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the agent manifest.
        
        Returns:
            A dictionary containing the agent manifest.
        """
        pass


class AgentCard:
    """
    Agent Card for agent discovery and description.
    
    An Agent Card provides a standardized way to describe an agent's
    capabilities, interfaces, and metadata for discovery and orchestration.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_type: str,
        name: str,
        description: str,
        version: str,
        capabilities: List[Dict[str, Any]] = None,
        interfaces: List[str] = None,
        endpoints: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
        industry_tags: List[str] = None,
        priority: int = 0
    ):
        """
        Initialize an Agent Card.
        
        Args:
            agent_id: Unique identifier for the agent.
            agent_type: Type identifier for the agent.
            name: Human-readable name for the agent.
            description: Human-readable description of the agent.
            version: Version string for the agent.
            capabilities: List of capability descriptors.
            interfaces: List of supported interface types.
            endpoints: Dictionary of endpoint descriptors.
            metadata: Additional metadata about the agent.
            industry_tags: Industry-specific tags for the agent.
            priority: Priority level for the agent (0-100).
        """
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.version = version
        self.capabilities = capabilities or []
        self.interfaces = interfaces or []
        self.endpoints = endpoints or {}
        self.metadata = metadata or {}
        self.industry_tags = industry_tags or []
        self.priority = priority
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.updated_at = self.created_at
    
    def add_capability(self, capability_id: str, description: str = None, parameters: Dict[str, Any] = None) -> None:
        """
        Add a capability to this agent card.
        
        Args:
            capability_id: Identifier for the capability.
            description: Human-readable description of the capability.
            parameters: Parameters for the capability.
        """
        capability = {
            "id": capability_id,
            "description": description or capability_id
        }
        
        if parameters:
            capability["parameters"] = parameters
        
        self.capabilities.append(capability)
        self.updated_at = datetime.datetime.utcnow().isoformat()
    
    def add_interface(self, interface_type: str) -> None:
        """
        Add a supported interface type to this agent card.
        
        Args:
            interface_type: The interface type identifier.
        """
        if interface_type not in self.interfaces:
            self.interfaces.append(interface_type)
            self.updated_at = datetime.datetime.utcnow().isoformat()
    
    def add_endpoint(self, endpoint_name: str, url: str, description: str = None, methods: List[str] = None) -> None:
        """
        Add an endpoint to this agent card.
        
        Args:
            endpoint_name: Name of the endpoint.
            url: URL of the endpoint.
            description: Human-readable description of the endpoint.
            methods: Supported HTTP methods for the endpoint.
        """
        self.endpoints[endpoint_name] = {
            "url": url,
            "description": description or endpoint_name,
            "methods": methods or ["POST"]
        }
        self.updated_at = datetime.datetime.utcnow().isoformat()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add a metadata item to this agent card.
        
        Args:
            key: Metadata key.
            value: Metadata value.
        """
        self.metadata[key] = value
        self.updated_at = datetime.datetime.utcnow().isoformat()
    
    def add_industry_tag(self, tag: str) -> None:
        """
        Add an industry-specific tag to this agent card.
        
        Args:
            tag: The industry tag to add.
        """
        if tag not in self.industry_tags:
            self.industry_tags.append(tag)
            self.updated_at = datetime.datetime.utcnow().isoformat()
    
    def set_priority(self, priority: int) -> None:
        """
        Set the priority level for this agent.
        
        Args:
            priority: Priority level (0-100).
        """
        self.priority = max(0, min(100, priority))
        self.updated_at = datetime.datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this agent card to a dictionary representation.
        
        Returns:
            A dictionary representing this agent card.
        """
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "capabilities": self.capabilities,
            "interfaces": self.interfaces,
            "endpoints": self.endpoints,
            "metadata": self.metadata,
            "industry_tags": self.industry_tags,
            "priority": self.priority,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    def to_json(self) -> str:
        """
        Convert this agent card to a JSON string.
        
        Returns:
            A JSON string representing this agent card.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentCard':
        """
        Create an agent card from a dictionary representation.
        
        Args:
            data: The dictionary containing agent card data.
            
        Returns:
            A new AgentCard instance.
        """
        card = cls(
            agent_id=data["agent_id"],
            agent_type=data["agent_type"],
            name=data["name"],
            description=data["description"],
            version=data["version"],
            capabilities=data.get("capabilities", []),
            interfaces=data.get("interfaces", []),
            endpoints=data.get("endpoints", {}),
            metadata=data.get("metadata", {}),
            industry_tags=data.get("industry_tags", []),
            priority=data.get("priority", 0)
        )
        
        card.created_at = data.get("created_at", card.created_at)
        card.updated_at = data.get("updated_at", card.updated_at)
        
        return card
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentCard':
        """
        Create an agent card from a JSON string.
        
        Args:
            json_str: The JSON string containing agent card data.
            
        Returns:
            A new AgentCard instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class AgentTask:
    """
    Task definition for agent execution.
    
    An AgentTask defines a unit of work that can be assigned to an agent
    for execution, with inputs, outputs, and execution parameters.
    """
    
    def __init__(
        self,
        task_id: str = None,
        task_type: str = None,
        description: str = None,
        inputs: Dict[str, Any] = None,
        required_capabilities: List[str] = None,
        timeout_seconds: int = 60,
        priority: int = 0,
        workflow_id: str = None
    ):
        """
        Initialize an agent task.
        
        Args:
            task_id: Unique identifier for the task. If None, a UUID is generated.
            task_type: Type identifier for the task.
            description: Human-readable description of the task.
            inputs: Input parameters for the task.
            required_capabilities: Capabilities required to execute this task.
            timeout_seconds: Maximum execution time in seconds.
            priority: Priority level for the task (0-100).
            workflow_id: ID of the workflow this task belongs to, if any.
        """
        self.task_id = task_id or str(uuid.uuid4())
        self.task_type = task_type or "generic"
        self.description = description or f"Task {self.task_id}"
        self.inputs = inputs or {}
        self.required_capabilities = required_capabilities or []
        self.timeout_seconds = timeout_seconds
        self.priority = priority
        self.workflow_id = workflow_id
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.assigned_to = None
        self.started_at = None
        self.completed_at = None
        self.status = "created"
        self.result = None
        self.error = None
    
    def assign(self, agent_id: str) -> None:
        """
        Assign this task to an agent.
        
        Args:
            agent_id: The ID of the agent to assign the task to.
        """
        self.assigned_to = agent_id
        self.status = "assigned"
    
    def start(self) -> None:
        """Mark this task as started."""
        self.started_at = datetime.datetime.utcnow().isoformat()
        self.status = "running"
    
    def complete(self, result: Any = None) -> None:
        """
        Mark this task as completed.
        
        Args:
            result: The result of the task execution.
        """
        self.completed_at = datetime.datetime.utcnow().isoformat()
        self.result = result
        self.status = "completed"
    
    def fail(self, error: str) -> None:
        """
        Mark this task as failed.
        
        Args:
            error: The error message.
        """
        self.completed_at = datetime.datetime.utcnow().isoformat()
        self.error = error
        self.status = "failed"
    
    def cancel(self) -> None:
        """Mark this task as cancelled."""
        self.completed_at = datetime.datetime.utcnow().isoformat()
        self.status = "cancelled"
    
    def is_timed_out(self) -> bool:
        """
        Check if this task has timed out.
        
        Returns:
            True if the task has timed out, False otherwise.
        """
        if self.status != "running" or not self.started_at:
            return False
        
        start_time = datetime.datetime.fromisoformat(self.started_at)
        now = datetime.datetime.utcnow()
        elapsed_seconds = (now - start_time).total_seconds()
        
        return elapsed_seconds > self.timeout_seconds
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this task to a dictionary representation.
        
        Returns:
            A dictionary representing this task.
        """
        return {
            "task_id": self.task_id,
            "task_type": self.task_type,
            "description": self.description,
            "inputs": self.inputs,
            "required_capabilities": self.required_capabilities,
            "timeout_seconds": self.timeout_seconds,
            "priority": self.priority,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at,
            "assigned_to": self.assigned_to,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "result": self.result,
            "error": self.error
        }
    
    def to_json(self) -> str:
        """
        Convert this task to a JSON string.
        
        Returns:
            A JSON string representing this task.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentTask':
        """
        Create a task from a dictionary representation.
        
        Args:
            data: The dictionary containing task data.
            
        Returns:
            A new AgentTask instance.
        """
        task = cls(
            task_id=data.get("task_id"),
            task_type=data.get("task_type"),
            description=data.get("description"),
            inputs=data.get("inputs"),
            required_capabilities=data.get("required_capabilities"),
            timeout_seconds=data.get("timeout_seconds", 60),
            priority=data.get("priority", 0),
            workflow_id=data.get("workflow_id")
        )
        
        task.created_at = data.get("created_at", task.created_at)
        task.assigned_to = data.get("assigned_to")
        task.started_at = data.get("started_at")
        task.completed_at = data.get("completed_at")
        task.status = data.get("status", "created")
        task.result = data.get("result")
        task.error = data.get("error")
        
        return task
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentTask':
        """
        Create a task from a JSON string.
        
        Args:
            json_str: The JSON string containing task data.
            
        Returns:
            A new AgentTask instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class AgentWorkflow:
    """
    Workflow definition for orchestrating multiple agent tasks.
    
    An AgentWorkflow defines a sequence or graph of tasks that can be
    executed by multiple agents to achieve a complex goal.
    """
    
    def __init__(
        self,
        workflow_id: str = None,
        name: str = None,
        description: str = None,
        tasks: List[AgentTask] = None,
        dependencies: Dict[str, List[str]] = None,
        metadata: Dict[str, Any] = None,
        industry_tags: List[str] = None,
        priority: int = 0
    ):
        """
        Initialize an agent workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow. If None, a UUID is generated.
            name: Human-readable name for the workflow.
            description: Human-readable description of the workflow.
            tasks: List of tasks in the workflow.
            dependencies: Dictionary mapping task IDs to lists of prerequisite task IDs.
            metadata: Additional metadata about the workflow.
            industry_tags: Industry-specific tags for the workflow.
            priority: Priority level for the workflow (0-100).
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.name = name or f"Workflow {self.workflow_id}"
        self.description = description or self.name
        self.tasks = tasks or []
        self.dependencies = dependencies or {}
        self.metadata = metadata or {}
        self.industry_tags = industry_tags or []
        self.priority = priority
        self.created_at = datetime.datetime.utcnow().isoformat()
        self.started_at = None
        self.completed_at = None
        self.status = "created"
        self.error = None
    
    def add_task(self, task: AgentTask, dependencies: List[str] = None) -> None:
        """
        Add a task to this workflow.
        
        Args:
            task: The task to add.
            dependencies: List of prerequisite task IDs.
        """
        # Set the workflow ID on the task
        task.workflow_id = self.workflow_id
        
        # Add the task to the workflow
        self.tasks.append(task)
        
        # Add dependencies if provided
        if dependencies:
            self.dependencies[task.task_id] = dependencies
    
    def get_ready_tasks(self) -> List[AgentTask]:
        """
        Get tasks that are ready to be executed.
        
        A task is ready if all its dependencies have been completed.
        
        Returns:
            A list of ready tasks.
        """
        ready_tasks = []
        
        for task in self.tasks:
            if task.status != "created":
                continue
            
            # Check if this task has dependencies
            if task.task_id in self.dependencies:
                # Check if all dependencies are completed
                deps_completed = True
                for dep_id in self.dependencies[task.task_id]:
                    dep_task = next((t for t in self.tasks if t.task_id == dep_id), None)
                    if not dep_task or dep_task.status != "completed":
                        deps_completed = False
                        break
                
                if deps_completed:
                    ready_tasks.append(task)
            else:
                # No dependencies, so the task is ready
                ready_tasks.append(task)
        
        return ready_tasks
    
    def start(self) -> None:
        """Mark this workflow as started."""
        self.started_at = datetime.datetime.utcnow().isoformat()
        self.status = "running"
    
    def update_status(self) -> None:
        """Update the workflow status based on task statuses."""
        if self.status == "created":
            return
        
        if self.status in ["completed", "failed", "cancelled"]:
            return
        
        # Check if all tasks are completed
        all_completed = all(task.status == "completed" for task in self.tasks)
        if all_completed:
            self.completed_at = datetime.datetime.utcnow().isoformat()
            self.status = "completed"
            return
        
        # Check if any task has failed
        any_failed = any(task.status == "failed" for task in self.tasks)
        if any_failed:
            self.completed_at = datetime.datetime.utcnow().isoformat()
            self.status = "failed"
            failed_tasks = [task for task in self.tasks if task.status == "failed"]
            self.error = f"Tasks failed: {', '.join(task.task_id for task in failed_tasks)}"
            return
        
        # Check if all tasks are cancelled
        all_cancelled = all(task.status in ["cancelled", "completed"] for task in self.tasks)
        if all_cancelled and any(task.status == "cancelled" for task in self.tasks):
            self.completed_at = datetime.datetime.utcnow().isoformat()
            self.status = "cancelled"
            return
    
    def cancel(self) -> None:
        """Cancel this workflow and all its tasks."""
        for task in self.tasks:
            if task.status in ["created", "assigned", "running"]:
                task.cancel()
        
        self.completed_at = datetime.datetime.utcnow().isoformat()
        self.status = "cancelled"
    
    def add_industry_tag(self, tag: str) -> None:
        """
        Add an industry-specific tag to this workflow.
        
        Args:
            tag: The industry tag to add.
        """
        if tag not in self.industry_tags:
            self.industry_tags.append(tag)
    
    def set_priority(self, priority: int) -> None:
        """
        Set the priority level for this workflow.
        
        Args:
            priority: Priority level (0-100).
        """
        self.priority = max(0, min(100, priority))
        
        # Update priority of all tasks
        for task in self.tasks:
            task.priority = self.priority
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert this workflow to a dictionary representation.
        
        Returns:
            A dictionary representing this workflow.
        """
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "description": self.description,
            "tasks": [task.to_dict() for task in self.tasks],
            "dependencies": self.dependencies,
            "metadata": self.metadata,
            "industry_tags": self.industry_tags,
            "priority": self.priority,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "status": self.status,
            "error": self.error
        }
    
    def to_json(self) -> str:
        """
        Convert this workflow to a JSON string.
        
        Returns:
            A JSON string representing this workflow.
        """
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AgentWorkflow':
        """
        Create a workflow from a dictionary representation.
        
        Args:
            data: The dictionary containing workflow data.
            
        Returns:
            A new AgentWorkflow instance.
        """
        # Create tasks first
        tasks = []
        if "tasks" in data:
            for task_data in data["tasks"]:
                tasks.append(AgentTask.from_dict(task_data))
        
        workflow = cls(
            workflow_id=data.get("workflow_id"),
            name=data.get("name"),
            description=data.get("description"),
            tasks=tasks,
            dependencies=data.get("dependencies", {}),
            metadata=data.get("metadata", {}),
            industry_tags=data.get("industry_tags", []),
            priority=data.get("priority", 0)
        )
        
        workflow.created_at = data.get("created_at", workflow.created_at)
        workflow.started_at = data.get("started_at")
        workflow.completed_at = data.get("completed_at")
        workflow.status = data.get("status", "created")
        workflow.error = data.get("error")
        
        return workflow
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentWorkflow':
        """
        Create a workflow from a JSON string.
        
        Args:
            json_str: The JSON string containing workflow data.
            
        Returns:
            A new AgentWorkflow instance.
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


class BaseProtocolAgent(ProtocolAgent, AgentInterface):
    """
    Base implementation of a protocol-aware agent.
    
    This class provides a concrete implementation of the AgentInterface
    that can be extended by specific agent types.
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = None):
        """
        Initialize a base protocol agent.
        
        Args:
            agent_id: Unique identifier for this agent. If None, a UUID is generated.
            agent_type: Type identifier for this agent.
        """
        super().__init__(agent_id, agent_type)
        self.message_handlers = {}
        self.card = AgentCard(
            agent_id=self.component_id,
            agent_type=self.component_type,
            name=self.component_type,
            description=f"{self.component_type} Agent",
            version="1.0.0"
        )
    
    def get_agent_id(self) -> str:
        """
        Get the unique identifier for this agent.
        
        Returns:
            The agent's unique identifier.
        """
        return self.component_id
    
    def get_agent_type(self) -> str:
        """
        Get the type identifier for this agent.
        
        Returns:
            The agent's type identifier.
        """
        return self.component_type
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the capabilities of this agent.
        
        Returns:
            A list of capability descriptors.
        """
        return self.capabilities
    
    def register_message_handler(self, message_type: str, handler: Callable[[Dict[str, Any]], Dict[str, Any]]) -> None:
        """
        Register a handler for a specific message type.
        
        Args:
            message_type: The type of message to handle.
            handler: The function that handles messages of this type.
        """
        self.message_handlers[message_type] = handler
        self.logger.debug(f"Registered handler for message type: {message_type}")
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
            
        Raises:
            ValueError: If the message type is not supported.
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")
        
        if "message_type" not in message:
            raise ValueError("Message must have a 'message_type' field")
        
        message_type = message["message_type"]
        
        if message_type in self.message_handlers:
            self.logger.debug(f"Processing message of type: {message_type}")
            return self.message_handlers[message_type](message)
        else:
            raise ValueError(f"Unsupported message type: {message_type}")
    
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the agent manifest.
        
        Returns:
            A dictionary containing the agent manifest.
        """
        manifest = self.to_dict()
        manifest["card"] = self.card.to_dict()
        return manifest
    
    def update_card(self, card: AgentCard) -> None:
        """
        Update this agent's card.
        
        Args:
            card: The new agent card.
        """
        self.card = card


class AsyncProtocolAgent(ProtocolAgent, AsyncAgentInterface):
    """
    Asynchronous implementation of a protocol-aware agent.
    
    This class provides a concrete implementation of the AsyncAgentInterface
    for high-performance protocol handling.
    """
    
    def __init__(self, agent_id: str = None, agent_type: str = None):
        """
        Initialize an asynchronous protocol agent.
        
        Args:
            agent_id: Unique identifier for this agent. If None, a UUID is generated.
            agent_type: Type identifier for this agent.
        """
        super().__init__(agent_id, agent_type)
        self.async_message_handlers = {}
        self.card = AgentCard(
            agent_id=self.component_id,
            agent_type=self.component_type,
            name=self.component_type,
            description=f"{self.component_type} Agent",
            version="1.0.0"
        )
    
    def get_agent_id(self) -> str:
        """
        Get the unique identifier for this agent.
        
        Returns:
            The agent's unique identifier.
        """
        return self.component_id
    
    def get_agent_type(self) -> str:
        """
        Get the type identifier for this agent.
        
        Returns:
            The agent's type identifier.
        """
        return self.component_type
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the capabilities of this agent.
        
        Returns:
            A list of capability descriptors.
        """
        return self.capabilities
    
    def register_async_message_handler(
        self,
        message_type: str,
        handler: Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]
    ) -> None:
        """
        Register an asynchronous handler for a specific message type.
        
        Args:
            message_type: The type of message to handle.
            handler: The async function that handles messages of this type.
        """
        self.async_message_handlers[message_type] = handler
        self.logger.debug(f"Registered async handler for message type: {message_type}")
    
    async def process_message_async(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message asynchronously.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
            
        Raises:
            ValueError: If the message type is not supported.
        """
        if not isinstance(message, dict):
            raise ValueError("Message must be a dictionary")
        
        if "message_type" not in message:
            raise ValueError("Message must have a 'message_type' field")
        
        message_type = message["message_type"]
        
        if message_type in self.async_message_handlers:
            self.logger.debug(f"Processing message of type: {message_type}")
            return await self.async_message_handlers[message_type](message)
        else:
            raise ValueError(f"Unsupported message type: {message_type}")
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming message synchronously.
        
        This method creates an event loop and runs the asynchronous handler.
        
        Args:
            message: The incoming message to process.
            
        Returns:
            The response message.
            
        Raises:
            ValueError: If the message type is not supported.
        """
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()
    
    def get_manifest(self) -> Dict[str, Any]:
        """
        Get the agent manifest.
        
        Returns:
            A dictionary containing the agent manifest.
        """
        manifest = self.to_dict()
        manifest["card"] = self.card.to_dict()
        return manifest
    
    def update_card(self, card: AgentCard) -> None:
        """
        Update this agent's card.
        
        Args:
            card: The new agent card.
        """
        self.card = card
