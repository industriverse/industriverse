"""
Workflow Manifest Parser Module for Industriverse Workflow Automation Layer

This module is responsible for parsing, validating, and managing workflow manifests.
It provides the data structures and validation logic for workflow definitions,
ensuring they conform to the expected schema and contain all required information.

The WorkflowManifest class is the central data model that represents a complete
workflow definition with all its tasks, execution modes, mesh topology, and other
configuration elements.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator

import yaml

# Configure logging
logger = logging.getLogger(__name__)


class ExecutionMode(str, Enum):
    """Enum representing the possible execution modes for workflows."""
    PASSIVE = "passive"
    REACTIVE = "reactive"
    PREDICTIVE = "predictive"
    STRATEGIC = "strategic"


class RoutingStrategy(str, Enum):
    """Enum representing the possible routing strategies for the agent mesh."""
    LATENCY_WEIGHTED = "latency_weighted"
    TRUST_WEIGHTED = "trust_weighted"
    FALLBACK_LINEAR = "fallback_linear"


class CongestionBehavior(str, Enum):
    """Enum representing the possible behaviors during mesh congestion."""
    QUEUE = "queue"
    REROUTE = "reroute"
    DEGRADE_GRACEFULLY = "degrade_gracefully"


class FallbackAgent(BaseModel):
    """Model representing a fallback agent in the mesh topology."""
    agent_id: str
    priority: int = 1


class AgentMeshTopology(BaseModel):
    """Model representing the mesh topology configuration for a workflow."""
    routing_strategy: RoutingStrategy = RoutingStrategy.TRUST_WEIGHTED
    allow_rerouting: bool = True
    fallback_agents: List[FallbackAgent] = Field(default_factory=list)
    congestion_behavior: CongestionBehavior = CongestionBehavior.QUEUE


class ExecutionModeConfig(BaseModel):
    """Model representing an execution mode configuration with triggers and conditions."""
    mode: ExecutionMode
    trigger: str
    threshold: Optional[str] = None
    condition: Optional[str] = None


class HumanInteraction(BaseModel):
    """Model representing human interaction configuration for a workflow."""
    provider: str = "n8n"
    n8n_flow_id: Optional[str] = None
    sync_mode: str = "async"  # "async" or "blocking"
    agent_involved: str = "human_in_loop_agent"
    escalation_protocol: str = "mcp_event/escalate"


class EscalationProtocol(BaseModel):
    """Model representing the escalation protocol configuration."""
    trigger: str
    resolve_with: str
    fallback: str
    bid_system: Optional[Dict[str, Any]] = None


class TaskInput(BaseModel):
    """Model representing an input parameter for a task."""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = True
    default: Optional[Any] = None


class TaskOutput(BaseModel):
    """Model representing an output parameter from a task."""
    name: str
    type: str
    description: Optional[str] = None


class TaskDefinition(BaseModel):
    """Model representing a task within a workflow."""
    id: str
    name: str
    type: str
    description: Optional[str] = None
    agent_id: Optional[str] = None
    inputs: List[TaskInput] = Field(default_factory=list)
    outputs: List[TaskOutput] = Field(default_factory=list)
    config: Dict[str, Any] = Field(default_factory=dict)
    on_failure: Optional[str] = None  # "continue", "retry", "escalate", or None (fail)
    retry_config: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = None
    next_tasks: List[str] = Field(default_factory=list)
    condition: Optional[str] = None


class WorkflowManifest(BaseModel):
    """
    Model representing a complete workflow manifest.
    
    This is the central data structure that defines a workflow, including its tasks,
    execution modes, mesh topology, and other configuration elements.
    """
    id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    author: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    tags: List[str] = Field(default_factory=list)
    industry: Optional[str] = None
    
    # Execution configuration
    execution_modes: List[ExecutionModeConfig] = Field(default_factory=list)
    agent_mesh_topology: Optional[AgentMeshTopology] = None
    human_interaction: Optional[HumanInteraction] = None
    escalation_protocol: Optional[EscalationProtocol] = None
    
    # Tasks
    tasks: List[TaskDefinition] = Field(default_factory=list)
    
    # Integration points
    mcp_events: List[str] = Field(default_factory=list)
    a2a_capabilities: List[str] = Field(default_factory=list)
    
    # DTSL embedding (for edge-native autonomy)
    dtsl_compatible: bool = False
    twin_id: Optional[str] = None
    
    @validator('tasks')
    def validate_tasks(cls, tasks):
        """Validate that task IDs are unique and references are valid."""
        task_ids = set()
        for task in tasks:
            if task.id in task_ids:
                raise ValueError(f"Duplicate task ID: {task.id}")
            task_ids.add(task.id)
            
            # Validate next_tasks references
            for next_task in task.next_tasks:
                if next_task not in task_ids and next_task != "end":
                    # We can't fully validate forward references, but we can warn
                    logger.warning(f"Task {task.id} references unknown next task: {next_task}")
        
        return tasks


class WorkflowManifestParser:
    """
    Parser for workflow manifests.
    
    This class provides methods to load, parse, validate, and manipulate
    workflow manifests from various sources (YAML, JSON, dict).
    """
    
    @staticmethod
    def parse_from_yaml(yaml_str: str) -> WorkflowManifest:
        """
        Parse a workflow manifest from a YAML string.
        
        Args:
            yaml_str: The YAML string containing the workflow manifest
            
        Returns:
            A WorkflowManifest object
            
        Raises:
            ValueError: If the YAML is invalid or doesn't conform to the schema
        """
        try:
            manifest_dict = yaml.safe_load(yaml_str)
            return WorkflowManifestParser.parse_from_dict(manifest_dict)
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML: {e}")
            raise ValueError(f"Invalid YAML: {e}")
    
    @staticmethod
    def parse_from_dict(manifest_dict: Dict[str, Any]) -> WorkflowManifest:
        """
        Parse a workflow manifest from a dictionary.
        
        Args:
            manifest_dict: The dictionary containing the workflow manifest
            
        Returns:
            A WorkflowManifest object
            
        Raises:
            ValueError: If the dictionary doesn't conform to the schema
        """
        try:
            return WorkflowManifest(**manifest_dict)
        except Exception as e:
            logger.error(f"Failed to parse workflow manifest: {e}")
            raise ValueError(f"Invalid workflow manifest: {e}")
    
    @staticmethod
    def to_yaml(manifest: WorkflowManifest) -> str:
        """
        Convert a WorkflowManifest to a YAML string.
        
        Args:
            manifest: The WorkflowManifest object
            
        Returns:
            A YAML string representation of the manifest
        """
        # Convert to dict first to handle datetime serialization
        manifest_dict = manifest.dict()
        
        # Convert datetime objects to ISO format strings
        manifest_dict['created_at'] = manifest_dict['created_at'].isoformat()
        manifest_dict['updated_at'] = manifest_dict['updated_at'].isoformat()
        
        return yaml.dump(manifest_dict, sort_keys=False)
    
    @staticmethod
    def validate(manifest: WorkflowManifest) -> List[str]:
        """
        Perform additional validation on a workflow manifest beyond schema validation.
        
        Args:
            manifest: The WorkflowManifest to validate
            
        Returns:
            A list of validation error messages, empty if valid
        """
        errors = []
        
        # Check for at least one task
        if not manifest.tasks:
            errors.append("Workflow must contain at least one task")
        
        # Check for circular references in task dependencies
        try:
            WorkflowManifestParser._check_circular_references(manifest)
        except ValueError as e:
            errors.append(str(e))
        
        # Check for unreachable tasks
        unreachable = WorkflowManifestParser._find_unreachable_tasks(manifest)
        if unreachable:
            errors.append(f"Unreachable tasks: {', '.join(unreachable)}")
        
        return errors
    
    @staticmethod
    def _check_circular_references(manifest: WorkflowManifest):
        """
        Check for circular references in task dependencies.
        
        Args:
            manifest: The WorkflowManifest to check
            
        Raises:
            ValueError: If circular references are found
        """
        # Build a dependency graph
        graph = {task.id: set(task.next_tasks) - {"end"} for task in manifest.tasks}
        
        # Check for cycles using DFS
        visited = set()
        path = set()
        
        def dfs(node):
            if node in path:
                cycle_path = " -> ".join(list(path) + [node])
                raise ValueError(f"Circular reference detected: {cycle_path}")
            
            if node in visited:
                return
            
            visited.add(node)
            path.add(node)
            
            for neighbor in graph.get(node, set()):
                dfs(neighbor)
            
            path.remove(node)
        
        # Start DFS from each task
        for task_id in graph:
            dfs(task_id)
    
    @staticmethod
    def _find_unreachable_tasks(manifest: WorkflowManifest) -> List[str]:
        """
        Find tasks that are not reachable from any entry point.
        
        Args:
            manifest: The WorkflowManifest to check
            
        Returns:
            A list of unreachable task IDs
        """
        # Build a dependency graph
        graph = {task.id: set(task.next_tasks) - {"end"} for task in manifest.tasks}
        
        # Find entry points (tasks not referenced by any other task)
        all_tasks = {task.id for task in manifest.tasks}
        referenced_tasks = set()
        for next_tasks in graph.values():
            referenced_tasks.update(next_tasks)
        
        entry_points = all_tasks - referenced_tasks
        
        # If no entry points, assume the first task is the entry point
        if not entry_points and manifest.tasks:
            entry_points = {manifest.tasks[0].id}
        
        # Traverse the graph from entry points
        reachable = set()
        
        def dfs(node):
            if node in reachable:
                return
            
            reachable.add(node)
            
            for neighbor in graph.get(node, set()):
                dfs(neighbor)
        
        # Start DFS from each entry point
        for entry_point in entry_points:
            dfs(entry_point)
        
        # Return unreachable tasks
        return list(all_tasks - reachable)
    
    @staticmethod
    def get_task_by_id(manifest: WorkflowManifest, task_id: str) -> Optional[TaskDefinition]:
        """
        Get a task by its ID.
        
        Args:
            manifest: The WorkflowManifest to search
            task_id: The ID of the task to find
            
        Returns:
            The TaskDefinition if found, None otherwise
        """
        for task in manifest.tasks:
            if task.id == task_id:
                return task
        return None
    
    @staticmethod
    def add_task(manifest: WorkflowManifest, task: TaskDefinition) -> WorkflowManifest:
        """
        Add a task to a workflow manifest.
        
        Args:
            manifest: The WorkflowManifest to modify
            task: The TaskDefinition to add
            
        Returns:
            The updated WorkflowManifest
            
        Raises:
            ValueError: If a task with the same ID already exists
        """
        # Check for duplicate task ID
        if WorkflowManifestParser.get_task_by_id(manifest, task.id):
            raise ValueError(f"Task with ID {task.id} already exists")
        
        # Add the task
        manifest.tasks.append(task)
        manifest.updated_at = datetime.now()
        
        return manifest
    
    @staticmethod
    def update_task(manifest: WorkflowManifest, task: TaskDefinition) -> WorkflowManifest:
        """
        Update a task in a workflow manifest.
        
        Args:
            manifest: The WorkflowManifest to modify
            task: The TaskDefinition with updated values
            
        Returns:
            The updated WorkflowManifest
            
        Raises:
            ValueError: If the task doesn't exist
        """
        # Find the task
        for i, existing_task in enumerate(manifest.tasks):
            if existing_task.id == task.id:
                # Update the task
                manifest.tasks[i] = task
                manifest.updated_at = datetime.now()
                return manifest
        
        # Task not found
        raise ValueError(f"Task with ID {task.id} not found")
    
    @staticmethod
    def remove_task(manifest: WorkflowManifest, task_id: str) -> WorkflowManifest:
        """
        Remove a task from a workflow manifest.
        
        Args:
            manifest: The WorkflowManifest to modify
            task_id: The ID of the task to remove
            
        Returns:
            The updated WorkflowManifest
            
        Raises:
            ValueError: If the task doesn't exist
        """
        # Find the task
        for i, task in enumerate(manifest.tasks):
            if task.id == task_id:
                # Remove the task
                manifest.tasks.pop(i)
                manifest.updated_at = datetime.now()
                
                # Remove references to this task
                for task in manifest.tasks:
                    if task_id in task.next_tasks:
                        task.next_tasks.remove(task_id)
                
                return manifest
        
        # Task not found
        raise ValueError(f"Task with ID {task_id} not found")
