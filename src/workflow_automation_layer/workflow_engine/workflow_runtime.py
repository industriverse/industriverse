"""
Workflow Runtime Module for Industriverse Workflow Automation Layer

This module serves as the core execution engine for workflow automation, handling:
- Workflow lifecycle management (creation, execution, monitoring, termination)
- Execution mode management based on trust scores and confidence
- Integration with MCP/A2A protocols for agent communication
- State management and persistence
- Error handling and recovery

The WorkflowRuntime class is the central component that orchestrates workflow execution
across the Industriverse ecosystem.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any, Callable, Union, Tuple

import yaml
from pydantic import BaseModel, Field

# Local imports
from .workflow_manifest_parser import WorkflowManifest, TaskDefinition
from .task_contract_manager import TaskContract
from .workflow_registry import WorkflowRegistry
from .workflow_telemetry import WorkflowTelemetry
from .execution_mode_manager import ExecutionModeManager, ExecutionMode
from .mesh_topology_manager import MeshTopologyManager, RoutingStrategy
from .capsule_debug_trace_manager import CapsuleDebugTraceManager, AgentTrace

# Configure logging
logger = logging.getLogger(__name__)


class WorkflowStatus(str, Enum):
    """Enum representing the possible states of a workflow."""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    ESCALATED = "escalated"


class WorkflowExecutionContext(BaseModel):
    """Model representing the execution context of a workflow."""
    workflow_id: str
    execution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: WorkflowStatus = WorkflowStatus.PENDING
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    current_task_id: Optional[str] = None
    variables: Dict[str, Any] = Field(default_factory=dict)
    trust_score: float = 0.8
    agent_confidence: float = 0.8
    execution_mode: ExecutionMode = ExecutionMode.REACTIVE
    routing_strategy: RoutingStrategy = RoutingStrategy.TRUST_WEIGHTED
    agent_trace: List[AgentTrace] = Field(default_factory=list)
    parent_execution_id: Optional[str] = None
    human_intervention_required: bool = False
    error_message: Optional[str] = None


class WorkflowRuntime:
    """
    Core runtime engine for workflow execution in the Industriverse ecosystem.
    
    This class manages the lifecycle of workflows, coordinates agent interactions,
    handles state transitions, and provides monitoring and telemetry.
    """
    
    def __init__(self, registry: WorkflowRegistry, telemetry: WorkflowTelemetry):
        """
        Initialize the WorkflowRuntime.
        
        Args:
            registry: The workflow registry for workflow lookup and registration
            telemetry: The telemetry service for monitoring and metrics
        """
        self.registry = registry
        self.telemetry = telemetry
        self.execution_mode_manager = ExecutionModeManager()
        self.mesh_topology_manager = MeshTopologyManager()
        self.debug_trace_manager = CapsuleDebugTraceManager()
        self.active_workflows: Dict[str, WorkflowExecutionContext] = {}
        self.task_handlers: Dict[str, Callable] = {}
        self.event_listeners: Dict[str, List[Callable]] = {}
        
        # Register default task handlers
        self._register_default_task_handlers()
        
        logger.info("WorkflowRuntime initialized")
    
    def _register_default_task_handlers(self):
        """Register default task handlers for common task types."""
        # These will be expanded as more task types are implemented
        self.register_task_handler("http_request", self._handle_http_request)
        self.register_task_handler("agent_task", self._handle_agent_task)
        self.register_task_handler("human_approval", self._handle_human_approval)
        self.register_task_handler("condition", self._handle_condition)
        self.register_task_handler("delay", self._handle_delay)
        self.register_task_handler("parallel", self._handle_parallel)
        self.register_task_handler("n8n_workflow", self._handle_n8n_workflow)
    
    def register_task_handler(self, task_type: str, handler: Callable):
        """
        Register a handler for a specific task type.
        
        Args:
            task_type: The type of task this handler can process
            handler: The function that will handle tasks of this type
        """
        self.task_handlers[task_type] = handler
        logger.debug(f"Registered task handler for {task_type}")
    
    def register_event_listener(self, event_type: str, listener: Callable):
        """
        Register a listener for workflow events.
        
        Args:
            event_type: The type of event to listen for
            listener: The function to call when the event occurs
        """
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
        self.event_listeners[event_type].append(listener)
        logger.debug(f"Registered event listener for {event_type}")
    
    def _emit_event(self, event_type: str, data: Any):
        """
        Emit an event to all registered listeners.
        
        Args:
            event_type: The type of event being emitted
            data: The data associated with the event
        """
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                try:
                    listener(data)
                except Exception as e:
                    logger.error(f"Error in event listener for {event_type}: {e}")
    
    async def create_workflow(self, manifest: Union[str, Dict, WorkflowManifest]) -> str:
        """
        Create a new workflow from a manifest.
        
        Args:
            manifest: The workflow manifest as a YAML string, dict, or WorkflowManifest object
            
        Returns:
            The ID of the created workflow
        """
        # Parse the manifest if it's not already a WorkflowManifest
        if isinstance(manifest, str):
            try:
                manifest_dict = yaml.safe_load(manifest)
                manifest = WorkflowManifest(**manifest_dict)
            except Exception as e:
                logger.error(f"Failed to parse workflow manifest: {e}")
                raise ValueError(f"Invalid workflow manifest: {e}")
        elif isinstance(manifest, dict):
            try:
                manifest = WorkflowManifest(**manifest)
            except Exception as e:
                logger.error(f"Failed to parse workflow manifest: {e}")
                raise ValueError(f"Invalid workflow manifest: {e}")
        
        # Register the workflow
        workflow_id = self.registry.register_workflow(manifest)
        
        # Log the creation
        logger.info(f"Created workflow {workflow_id}: {manifest.name}")
        self._emit_event("workflow_created", {"workflow_id": workflow_id, "manifest": manifest})
        
        return workflow_id
    
    async def start_workflow(
        self, 
        workflow_id: str, 
        initial_variables: Optional[Dict[str, Any]] = None,
        parent_execution_id: Optional[str] = None
    ) -> str:
        """
        Start a workflow execution.
        
        Args:
            workflow_id: The ID of the workflow to start
            initial_variables: Initial variables for the workflow context
            parent_execution_id: ID of a parent workflow execution if this is a sub-workflow
            
        Returns:
            The execution ID of the started workflow
        """
        # Get the workflow manifest
        manifest = self.registry.get_workflow(workflow_id)
        if not manifest:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        # Create execution context
        context = WorkflowExecutionContext(
            workflow_id=workflow_id,
            status=WorkflowStatus.PENDING,
            variables=initial_variables or {},
            parent_execution_id=parent_execution_id
        )
        
        # Determine execution mode based on trust score and agent confidence
        context.execution_mode = self.execution_mode_manager.determine_execution_mode(
            context.trust_score, 
            context.agent_confidence,
            manifest.execution_modes if hasattr(manifest, 'execution_modes') else None
        )
        
        # Determine routing strategy from manifest
        if hasattr(manifest, 'agent_mesh_topology') and manifest.agent_mesh_topology:
            context.routing_strategy = RoutingStrategy(manifest.agent_mesh_topology.routing_strategy)
        
        # Store the context
        self.active_workflows[context.execution_id] = context
        
        # Log the start
        logger.info(f"Starting workflow {workflow_id} with execution ID {context.execution_id}")
        self._emit_event("workflow_started", {"execution_id": context.execution_id, "context": context})
        
        # Start the workflow execution
        asyncio.create_task(self._execute_workflow(context.execution_id))
        
        return context.execution_id
    
    async def _execute_workflow(self, execution_id: str):
        """
        Execute a workflow.
        
        Args:
            execution_id: The execution ID of the workflow to execute
        """
        context = self.active_workflows.get(execution_id)
        if not context:
            logger.error(f"Workflow execution {execution_id} not found")
            return
        
        # Update context
        context.status = WorkflowStatus.RUNNING
        context.start_time = datetime.now()
        
        # Get the workflow manifest
        manifest = self.registry.get_workflow(context.workflow_id)
        if not manifest:
            logger.error(f"Workflow {context.workflow_id} not found")
            context.status = WorkflowStatus.FAILED
            context.error_message = f"Workflow {context.workflow_id} not found"
            return
        
        try:
            # Execute tasks in sequence (this will be enhanced for parallel execution)
            for task in manifest.tasks:
                context.current_task_id = task.id
                
                # Log task start
                logger.info(f"Executing task {task.id} in workflow {context.execution_id}")
                self._emit_event("task_started", {
                    "execution_id": context.execution_id, 
                    "task_id": task.id
                })
                
                # Record in debug trace
                trace_entry = AgentTrace(
                    agent_id=task.agent_id if hasattr(task, 'agent_id') else "workflow_runtime",
                    input_received=True,
                    time=datetime.now().isoformat()
                )
                context.agent_trace.append(trace_entry)
                
                # Execute the task
                try:
                    # Get the appropriate handler for this task type
                    handler = self.task_handlers.get(task.type)
                    if not handler:
                        raise ValueError(f"No handler registered for task type {task.type}")
                    
                    # Execute the task
                    result = await handler(task, context)
                    
                    # Update the context with the result
                    if result and isinstance(result, dict):
                        context.variables.update(result)
                    
                    # Update trace with success
                    trace_entry.decision = "completed"
                    trace_entry.reason = "Task executed successfully"
                    
                    # Log task completion
                    logger.info(f"Task {task.id} completed in workflow {context.execution_id}")
                    self._emit_event("task_completed", {
                        "execution_id": context.execution_id, 
                        "task_id": task.id,
                        "result": result
                    })
                    
                except Exception as e:
                    # Update trace with failure
                    trace_entry.decision = "failed"
                    trace_entry.reason = str(e)
                    
                    # Log task failure
                    logger.error(f"Task {task.id} failed in workflow {context.execution_id}: {e}")
                    self._emit_event("task_failed", {
                        "execution_id": context.execution_id, 
                        "task_id": task.id,
                        "error": str(e)
                    })
                    
                    # Handle task failure based on task configuration
                    if hasattr(task, 'on_failure') and task.on_failure:
                        if task.on_failure == "continue":
                            logger.info(f"Continuing workflow {context.execution_id} despite task failure")
                            continue
                        elif task.on_failure == "retry":
                            # Implement retry logic
                            pass
                        elif task.on_failure == "escalate":
                            context.status = WorkflowStatus.ESCALATED
                            context.human_intervention_required = True
                            self._emit_event("workflow_escalated", {
                                "execution_id": context.execution_id,
                                "task_id": task.id,
                                "error": str(e)
                            })
                            return
                    
                    # Default behavior is to fail the workflow
                    context.status = WorkflowStatus.FAILED
                    context.error_message = f"Task {task.id} failed: {e}"
                    context.end_time = datetime.now()
                    
                    self._emit_event("workflow_failed", {
                        "execution_id": context.execution_id,
                        "error": str(e)
                    })
                    return
                
                # Check if human intervention is required
                if context.human_intervention_required:
                    logger.info(f"Workflow {context.execution_id} paused for human intervention")
                    context.status = WorkflowStatus.PAUSED
                    self._emit_event("workflow_paused", {
                        "execution_id": context.execution_id,
                        "reason": "Human intervention required"
                    })
                    return
            
            # All tasks completed successfully
            context.status = WorkflowStatus.COMPLETED
            context.end_time = datetime.now()
            context.current_task_id = None
            
            logger.info(f"Workflow {context.execution_id} completed successfully")
            self._emit_event("workflow_completed", {"execution_id": context.execution_id})
            
            # Save debug trace
            self.debug_trace_manager.save_trace(
                context.workflow_id,
                context.execution_id,
                context.agent_trace
            )
            
        except Exception as e:
            # Handle workflow-level exceptions
            context.status = WorkflowStatus.FAILED
            context.error_message = str(e)
            context.end_time = datetime.now()
            
            logger.error(f"Workflow {context.execution_id} failed: {e}")
            self._emit_event("workflow_failed", {
                "execution_id": context.execution_id,
                "error": str(e)
            })
    
    async def pause_workflow(self, execution_id: str, reason: Optional[str] = None) -> bool:
        """
        Pause a running workflow.
        
        Args:
            execution_id: The execution ID of the workflow to pause
            reason: The reason for pausing
            
        Returns:
            True if the workflow was paused, False otherwise
        """
        context = self.active_workflows.get(execution_id)
        if not context or context.status != WorkflowStatus.RUNNING:
            return False
        
        context.status = WorkflowStatus.PAUSED
        
        logger.info(f"Workflow {execution_id} paused: {reason or 'No reason provided'}")
        self._emit_event("workflow_paused", {
            "execution_id": execution_id,
            "reason": reason
        })
        
        return True
    
    async def resume_workflow(self, execution_id: str) -> bool:
        """
        Resume a paused workflow.
        
        Args:
            execution_id: The execution ID of the workflow to resume
            
        Returns:
            True if the workflow was resumed, False otherwise
        """
        context = self.active_workflows.get(execution_id)
        if not context or context.status != WorkflowStatus.PAUSED:
            return False
        
        context.status = WorkflowStatus.RUNNING
        context.human_intervention_required = False
        
        logger.info(f"Resuming workflow {execution_id}")
        self._emit_event("workflow_resumed", {"execution_id": execution_id})
        
        # Resume execution
        asyncio.create_task(self._execute_workflow(execution_id))
        
        return True
    
    async def cancel_workflow(self, execution_id: str, reason: Optional[str] = None) -> bool:
        """
        Cancel a workflow execution.
        
        Args:
            execution_id: The execution ID of the workflow to cancel
            reason: The reason for cancellation
            
        Returns:
            True if the workflow was cancelled, False otherwise
        """
        context = self.active_workflows.get(execution_id)
        if not context or context.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
            return False
        
        context.status = WorkflowStatus.CANCELLED
        context.end_time = datetime.now()
        
        logger.info(f"Workflow {execution_id} cancelled: {reason or 'No reason provided'}")
        self._emit_event("workflow_cancelled", {
            "execution_id": execution_id,
            "reason": reason
        })
        
        return True
    
    async def get_workflow_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the current status of a workflow execution.
        
        Args:
            execution_id: The execution ID of the workflow
            
        Returns:
            A dictionary with the workflow status information, or None if not found
        """
        context = self.active_workflows.get(execution_id)
        if not context:
            return None
        
        return {
            "execution_id": context.execution_id,
            "workflow_id": context.workflow_id,
            "status": context.status,
            "start_time": context.start_time,
            "end_time": context.end_time,
            "current_task_id": context.current_task_id,
            "execution_mode": context.execution_mode,
            "routing_strategy": context.routing_strategy,
            "human_intervention_required": context.human_intervention_required,
            "error_message": context.error_message
        }
    
    async def list_active_workflows(self) -> List[Dict[str, Any]]:
        """
        List all active workflow executions.
        
        Returns:
            A list of dictionaries with basic workflow information
        """
        return [
            {
                "execution_id": context.execution_id,
                "workflow_id": context.workflow_id,
                "status": context.status,
                "start_time": context.start_time
            }
            for context in self.active_workflows.values()
            if context.status in [WorkflowStatus.RUNNING, WorkflowStatus.PAUSED, WorkflowStatus.PENDING]
        ]
    
    # Task handler implementations
    
    async def _handle_http_request(self, task: TaskDefinition, context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle an HTTP request task."""
        # This is a placeholder implementation
        logger.info(f"Executing HTTP request task {task.id}")
        return {"http_response": "Placeholder response"}
    
    async def _handle_agent_task(self, task: TaskDefinition, context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle a task that involves an agent."""
        # This is a placeholder implementation
        logger.info(f"Executing agent task {task.id} with agent {task.agent_id}")
        return {"agent_response": "Placeholder response"}
    
    async def _handle_human_approval(self, task: TaskDefinition, context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle a human approval task."""
        # Mark that human intervention is required
        context.human_intervention_required = True
        logger.info(f"Human approval required for task {task.id} in workflow {context.execution_id}")
        return {}
    
    async def _handle_condition(self, task: TaskDefinition, context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle a conditional task."""
        # This is a placeholder implementation
        logger.info(f"Evaluating condition for task {task.id}")
        return {"condition_result": True}
    
    async def _handle_delay(self, task: TaskDefinition, context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle a delay task."""
        delay_seconds = task.config.get("delay_seconds", 1)
        logger.info(f"Delaying workflow {context.execution_id} for {delay_seconds} seconds")
        await asyncio.sleep(delay_seconds)
        return {}
    
    async def _handle_parallel(self, task: TaskDefinition, context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle parallel task execution."""
        # This is a placeholder implementation
        logger.info(f"Executing parallel tasks for {task.id}")
        return {"parallel_results": []}
    
    async def _handle_n8n_workflow(self, task: TaskDefinition, context: WorkflowExecutionContext) -> Dict[str, Any]:
        """Handle execution of an n8n workflow."""
        # This is a placeholder implementation
        logger.info(f"Executing n8n workflow for task {task.id}")
        return {"n8n_result": "Placeholder response"}
