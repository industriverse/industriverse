"""
Capsule Workflow Controller Agent Module for Industriverse Workflow Automation Layer

This module implements the Capsule Workflow Controller Agent, which is responsible for
managing workflow execution within Dynamic Agent Capsules. It handles the lifecycle
of workflow instances, coordinates with the UI layer, and manages capsule state.

The CapsuleWorkflowControllerAgent class extends the BaseAgent to provide specialized
functionality for capsule-based workflow control.
"""

import logging
import asyncio
import json
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta

from pydantic import BaseModel, Field, validator

from .base_agent import BaseAgent, AgentMetadata, AgentConfig, AgentContext, AgentResult, AgentCapability

# Configure logging
logger = logging.getLogger(__name__)


class CapsuleState(str, Enum):
    """Enum representing the possible states of a workflow capsule."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    SUSPENDED = "suspended"
    MIGRATING = "migrating"
    FORKED = "forked"


class CapsuleVisibility(str, Enum):
    """Enum representing the possible visibility modes of a workflow capsule."""
    VISIBLE = "visible"
    MINIMIZED = "minimized"
    BACKGROUND = "background"
    PINNED = "pinned"
    EXPANDED = "expanded"
    FOCUSED = "focused"


class CapsuleUIMode(str, Enum):
    """Enum representing the possible UI modes of a workflow capsule."""
    STANDARD = "standard"
    COMPACT = "compact"
    DETAILED = "detailed"
    DEBUG = "debug"
    PRESENTATION = "presentation"


class CapsuleMemorySnapshot(BaseModel):
    """Model representing a snapshot of a capsule's memory state."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    context_variables: Dict[str, Any] = Field(default_factory=dict)
    workflow_state: Dict[str, Any] = Field(default_factory=dict)
    task_states: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CapsuleDebugTrace(BaseModel):
    """Model representing a debug trace entry for a workflow capsule."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    level: str = "INFO"
    component: str
    message: str
    data: Optional[Dict[str, Any]] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = None
    execution_mode: Optional[str] = None
    pattern_signature: Optional[str] = None  # For pattern recognition


class WorkflowCapsule(BaseModel):
    """Model representing a workflow capsule."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    execution_id: str
    name: str
    description: Optional[str] = None
    state: CapsuleState = CapsuleState.INITIALIZING
    visibility: CapsuleVisibility = CapsuleVisibility.VISIBLE
    ui_mode: CapsuleUIMode = CapsuleUIMode.STANDARD
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    owner_id: Optional[str] = None
    current_task_id: Optional[str] = None
    progress: float = 0.0
    estimated_completion_time: Optional[datetime] = None
    trust_score: float = 0.8
    execution_mode: str = "reactive"  # Current execution mode
    location: str = "cloud"  # cloud, edge, hybrid
    context_variables: Dict[str, Any] = Field(default_factory=dict)
    ui_state: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def update_progress(self, progress: float):
        """Update the progress of the capsule."""
        self.progress = max(0.0, min(1.0, progress))
        self.updated_at = datetime.now()
    
    def update_state(self, state: CapsuleState):
        """Update the state of the capsule."""
        self.state = state
        self.updated_at = datetime.now()
    
    def update_visibility(self, visibility: CapsuleVisibility):
        """Update the visibility of the capsule."""
        self.visibility = visibility
        self.updated_at = datetime.now()
    
    def update_ui_mode(self, ui_mode: CapsuleUIMode):
        """Update the UI mode of the capsule."""
        self.ui_mode = ui_mode
        self.updated_at = datetime.now()
    
    def update_execution_mode(self, mode: str):
        """Update the execution mode of the capsule."""
        self.execution_mode = mode
        self.updated_at = datetime.now()
        
    def to_ui_representation(self) -> Dict[str, Any]:
        """Convert the capsule to a UI-friendly representation."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "state": self.state,
            "visibility": self.visibility,
            "ui_mode": self.ui_mode,
            "progress": self.progress,
            "current_task": self.current_task_id,
            "execution_mode": self.execution_mode,
            "trust_score": self.trust_score,
            "updated_at": self.updated_at.isoformat(),
            "estimated_completion_time": self.estimated_completion_time.isoformat() if self.estimated_completion_time else None,
            "ui_state": self.ui_state
        }


class CapsuleAction(BaseModel):
    """Model representing an action that can be performed on a capsule."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    capsule_id: str
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)
    requester_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CapsuleWorkflowControllerAgent(BaseAgent):
    """
    Agent responsible for managing workflow execution within Dynamic Agent Capsules.
    
    This agent handles the lifecycle of workflow instances, coordinates with the UI layer,
    and manages capsule state, providing a unified interface for workflow visualization
    and control.
    """
    
    def __init__(self, metadata: Optional[AgentMetadata] = None, config: Optional[AgentConfig] = None):
        """
        Initialize the CapsuleWorkflowControllerAgent.
        
        Args:
            metadata: Optional metadata for the agent
            config: Optional configuration for the agent
        """
        if metadata is None:
            metadata = AgentMetadata(
                id="capsule_workflow_controller_agent",
                name="Capsule Workflow Controller Agent",
                description="Manages workflow execution within Dynamic Agent Capsules",
                capabilities=[AgentCapability.WORKFLOW_CONTROL]
            )
        
        super().__init__(metadata, config)
        
        # Store active capsules
        self.capsules: Dict[str, WorkflowCapsule] = {}
        
        # Store capsule memory snapshots
        self.memory_snapshots: Dict[str, List[CapsuleMemorySnapshot]] = {}
        
        # Store capsule debug traces
        self.debug_traces: Dict[str, List[CapsuleDebugTrace]] = {}
        
        # Store pending capsule actions
        self.pending_actions: Dict[str, List[CapsuleAction]] = {}
        
        # Callbacks
        self.on_capsule_created: Optional[Callable[[WorkflowCapsule], None]] = None
        self.on_capsule_updated: Optional[Callable[[WorkflowCapsule], None]] = None
        self.on_capsule_state_changed: Optional[Callable[[WorkflowCapsule, CapsuleState], None]] = None
        self.on_capsule_action_received: Optional[Callable[[CapsuleAction], None]] = None
        self.on_debug_trace_added: Optional[Callable[[CapsuleDebugTrace], None]] = None
        
        # Background tasks
        self.background_tasks = []
        
        logger.info(f"CapsuleWorkflowControllerAgent initialized")
    
    async def _initialize_impl(self) -> bool:
        """
        Implementation of agent initialization.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        # Start background tasks for processing actions
        self._start_action_processor()
        
        return True
    
    def _start_action_processor(self):
        """Start the background task for processing capsule actions."""
        task = asyncio.create_task(self._process_capsule_actions())
        self.background_tasks.append(task)
    
    async def _process_capsule_actions(self):
        """Process pending capsule actions."""
        while True:
            try:
                # Process actions for each capsule
                for capsule_id, actions in list(self.pending_actions.items()):
                    if not actions:
                        continue
                    
                    # Get the capsule
                    capsule = self.capsules.get(capsule_id)
                    if not capsule:
                        # Capsule no longer exists, discard actions
                        del self.pending_actions[capsule_id]
                        continue
                    
                    # Process the oldest action
                    action = actions[0]
                    
                    try:
                        # Process the action
                        await self._process_action(action, capsule)
                        
                        # Remove the processed action
                        actions.pop(0)
                        
                        # If no more actions, clean up
                        if not actions:
                            del self.pending_actions[capsule_id]
                    
                    except Exception as e:
                        logger.error(f"Error processing action {action.action_type} for capsule {capsule_id}: {e}")
                        
                        # Add debug trace
                        await self.add_debug_trace(
                            capsule_id=capsule_id,
                            level="ERROR",
                            component="action_processor",
                            message=f"Failed to process action {action.action_type}: {e}",
                            data={"action": action.dict()}
                        )
                        
                        # Skip this action to avoid infinite loop
                        actions.pop(0)
                
                # Sleep for a short time before checking again
                await asyncio.sleep(0.1)
            
            except Exception as e:
                logger.error(f"Error in capsule action processor: {e}")
                await asyncio.sleep(1)  # Sleep longer on error
    
    async def _process_action(self, action: CapsuleAction, capsule: WorkflowCapsule):
        """
        Process a capsule action.
        
        Args:
            action: The action to process
            capsule: The capsule to apply the action to
        """
        action_type = action.action_type
        
        if action_type == "pause":
            # Pause the workflow
            if capsule.state == CapsuleState.RUNNING:
                capsule.update_state(CapsuleState.PAUSED)
                
                # Add debug trace
                await self.add_debug_trace(
                    capsule_id=capsule.id,
                    component="workflow_controller",
                    message=f"Workflow paused by {action.requester_id or 'system'}"
                )
                
                # Notify callback
                if self.on_capsule_state_changed:
                    self.on_capsule_state_changed(capsule, CapsuleState.PAUSED)
        
        elif action_type == "resume":
            # Resume the workflow
            if capsule.state == CapsuleState.PAUSED:
                capsule.update_state(CapsuleState.RUNNING)
                
                # Add debug trace
                await self.add_debug_trace(
                    capsule_id=capsule.id,
                    component="workflow_controller",
                    message=f"Workflow resumed by {action.requester_id or 'system'}"
                )
                
                # Notify callback
                if self.on_capsule_state_changed:
                    self.on_capsule_state_changed(capsule, CapsuleState.RUNNING)
        
        elif action_type == "terminate":
            # Terminate the workflow
            if capsule.state not in [CapsuleState.COMPLETED, CapsuleState.FAILED]:
                capsule.update_state(CapsuleState.FAILED)
                capsule.metadata["termination_reason"] = action.parameters.get("reason", "User requested termination")
                
                # Add debug trace
                await self.add_debug_trace(
                    capsule_id=capsule.id,
                    component="workflow_controller",
                    message=f"Workflow terminated by {action.requester_id or 'system'}: {capsule.metadata['termination_reason']}"
                )
                
                # Notify callback
                if self.on_capsule_state_changed:
                    self.on_capsule_state_changed(capsule, CapsuleState.FAILED)
        
        elif action_type == "suspend":
            # Suspend the workflow
            if capsule.state in [CapsuleState.RUNNING, CapsuleState.PAUSED]:
                capsule.update_state(CapsuleState.SUSPENDED)
                
                # Take a memory snapshot
                await self.take_memory_snapshot(capsule.id)
                
                # Add debug trace
                await self.add_debug_trace(
                    capsule_id=capsule.id,
                    component="workflow_controller",
                    message=f"Workflow suspended by {action.requester_id or 'system'}"
                )
                
                # Notify callback
                if self.on_capsule_state_changed:
                    self.on_capsule_state_changed(capsule, CapsuleState.SUSPENDED)
        
        elif action_type == "migrate":
            # Migrate the workflow to another location
            target_location = action.parameters.get("target_location")
            if not target_location:
                raise ValueError("target_location is required for migrate action")
            
            # Update state to migrating
            capsule.update_state(CapsuleState.MIGRATING)
            
            # Take a memory snapshot
            snapshot_id = await self.take_memory_snapshot(capsule.id)
            
            # Update location
            old_location = capsule.location
            capsule.location = target_location
            
            # Add debug trace
            await self.add_debug_trace(
                capsule_id=capsule.id,
                component="workflow_controller",
                message=f"Workflow migrating from {old_location} to {target_location}",
                data={"snapshot_id": snapshot_id}
            )
            
            # Notify callback
            if self.on_capsule_state_changed:
                self.on_capsule_state_changed(capsule, CapsuleState.MIGRATING)
            
            # In a real implementation, we would initiate the actual migration here
            # For now, we'll just simulate it by updating the state after a delay
            await asyncio.sleep(1)
            
            # Update state back to running
            capsule.update_state(CapsuleState.RUNNING)
            
            # Add debug trace
            await self.add_debug_trace(
                capsule_id=capsule.id,
                component="workflow_controller",
                message=f"Workflow migration to {target_location} completed"
            )
            
            # Notify callback
            if self.on_capsule_state_changed:
                self.on_capsule_state_changed(capsule, CapsuleState.RUNNING)
        
        elif action_type == "fork":
            # Fork the workflow
            fork_name = action.parameters.get("name", f"Fork of {capsule.name}")
            
            # Take a memory snapshot
            snapshot_id = await self.take_memory_snapshot(capsule.id)
            
            # Create a new capsule as a fork
            fork_capsule = WorkflowCapsule(
                workflow_id=capsule.workflow_id,
                execution_id=f"{capsule.execution_id}_fork_{uuid.uuid4().hex[:8]}",
                name=fork_name,
                description=f"Forked from {capsule.name}",
                owner_id=action.requester_id or capsule.owner_id,
                context_variables=capsule.context_variables.copy(),
                metadata={
                    **capsule.metadata,
                    "forked_from": capsule.id,
                    "fork_time": datetime.now().isoformat(),
                    "snapshot_id": snapshot_id
                }
            )
            
            # Store the fork
            self.capsules[fork_capsule.id] = fork_capsule
            
            # Add debug trace to original capsule
            await self.add_debug_trace(
                capsule_id=capsule.id,
                component="workflow_controller",
                message=f"Workflow forked by {action.requester_id or 'system'}: {fork_capsule.id}"
            )
            
            # Add debug trace to fork
            await self.add_debug_trace(
                capsule_id=fork_capsule.id,
                component="workflow_controller",
                message=f"Workflow forked from {capsule.id}"
            )
            
            # Update original capsule state
            capsule.update_state(CapsuleState.FORKED)
            
            # Notify callbacks
            if self.on_capsule_created:
                self.on_capsule_created(fork_capsule)
            
            if self.on_capsule_state_changed:
                self.on_capsule_state_changed(capsule, CapsuleState.FORKED)
        
        elif action_type == "update_visibility":
            # Update visibility
            visibility_str = action.parameters.get("visibility")
            if not visibility_str:
                raise ValueError("visibility is required for update_visibility action")
            
            try:
                visibility = CapsuleVisibility(visibility_str)
            except ValueError:
                raise ValueError(f"Invalid visibility: {visibility_str}")
            
            # Update visibility
            capsule.update_visibility(visibility)
            
            # Add debug trace
            await self.add_debug_trace(
                capsule_id=capsule.id,
                component="ui_controller",
                message=f"Visibility updated to {visibility}"
            )
            
            # Notify callback
            if self.on_capsule_updated:
                self.on_capsule_updated(capsule)
        
        elif action_type == "update_ui_mode":
            # Update UI mode
            ui_mode_str = action.parameters.get("ui_mode")
            if not ui_mode_str:
                raise ValueError("ui_mode is required for update_ui_mode action")
            
            try:
                ui_mode = CapsuleUIMode(ui_mode_str)
            except ValueError:
                raise ValueError(f"Invalid UI mode: {ui_mode_str}")
            
            # Update UI mode
            capsule.update_ui_mode(ui_mode)
            
            # Add debug trace
            await self.add_debug_trace(
                capsule_id=capsule.id,
                component="ui_controller",
                message=f"UI mode updated to {ui_mode}"
            )
            
            # Notify callback
            if self.on_capsule_updated:
                self.on_capsule_updated(capsule)
        
        elif action_type == "update_execution_mode":
            # Update execution mode
            execution_mode = action.parameters.get("execution_mode")
            if not execution_mode:
                raise ValueError("execution_mode is required for update_execution_mode action")
            
            # Update execution mode
            capsule.update_execution_mode(execution_mode)
            
            # Add debug trace
            await self.add_debug_trace(
                capsule_id=capsule.id,
                component="workflow_controller",
                message=f"Execution mode updated to {execution_mode}",
                execution_mode=execution_mode
            )
            
            # Notify callback
            if self.on_capsule_updated:
                self.on_capsule_updated(capsule)
        
        elif action_type == "update_ui_state":
            # Update UI state
            ui_state = action.parameters.get("ui_state")
            if not ui_state:
                raise ValueError("ui_state is required for update_ui_state action")
            
            # Update UI state
            capsule.ui_state.update(ui_state)
            capsule.updated_at = datetime.now()
            
            # Notify callback
            if self.on_capsule_updated:
                self.on_capsule_updated(capsule)
        
        else:
            # Unknown action type
            raise ValueError(f"Unknown action type: {action_type}")
    
    async def create_capsule(self, workflow_id: str, execution_id: str, name: str, **kwargs) -> str:
        """
        Create a new workflow capsule.
        
        Args:
            workflow_id: The ID of the workflow
            execution_id: The ID of the workflow execution
            name: The name of the capsule
            **kwargs: Additional capsule parameters
            
        Returns:
            The ID of the created capsule
        """
        # Create the capsule
        capsule = WorkflowCapsule(
            workflow_id=workflow_id,
            execution_id=execution_id,
            name=name,
            **kwargs
        )
        
        # Store the capsule
        self.capsules[capsule.id] = capsule
        
        # Initialize memory snapshots and debug traces
        self.memory_snapshots[capsule.id] = []
        self.debug_traces[capsule.id] = []
        
        # Add initial debug trace
        await self.add_debug_trace(
            capsule_id=capsule.id,
            component="workflow_controller",
            message=f"Capsule created for workflow {workflow_id}, execution {execution_id}"
        )
        
        # Notify callback
        if self.on_capsule_created:
            self.on_capsule_created(capsule)
        
        logger.info(f"Created capsule {capsule.id} for workflow {workflow_id}")
        return capsule.id
    
    async def get_capsule(self, capsule_id: str) -> Optional[WorkflowCapsule]:
        """
        Get a capsule by ID.
        
        Args:
            capsule_id: The ID of the capsule
            
        Returns:
            The capsule if found, None otherwise
        """
        return self.capsules.get(capsule_id)
    
    async def list_capsules(self, 
                          workflow_id: Optional[str] = None, 
                          state: Optional[CapsuleState] = None,
                          owner_id: Optional[str] = None) -> List[WorkflowCapsule]:
        """
        List capsules, optionally filtered.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            state: Optional state to filter by
            owner_id: Optional owner ID to filter by
            
        Returns:
            A list of matching capsules
        """
        result = []
        
        for capsule in self.capsules.values():
            if (workflow_id is None or capsule.workflow_id == workflow_id) and \
               (state is None or capsule.state == state) and \
               (owner_id is None or capsule.owner_id == owner_id):
                result.append(capsule)
        
        return result
    
    async def update_capsule_progress(self, capsule_id: str, progress: float) -> bool:
        """
        Update the progress of a capsule.
        
        Args:
            capsule_id: The ID of the capsule
            progress: The new progress value (0.0 to 1.0)
            
        Returns:
            True if the capsule was updated, False if it wasn't found
        """
        if capsule_id not in self.capsules:
            logger.warning(f"Attempted to update progress of unknown capsule {capsule_id}")
            return False
        
        capsule = self.capsules[capsule_id]
        capsule.update_progress(progress)
        
        # Notify callback
        if self.on_capsule_updated:
            self.on_capsule_updated(capsule)
        
        return True
    
    async def update_capsule_state(self, capsule_id: str, state: CapsuleState) -> bool:
        """
        Update the state of a capsule.
        
        Args:
            capsule_id: The ID of the capsule
            state: The new state
            
        Returns:
            True if the capsule was updated, False if it wasn't found
        """
        if capsule_id not in self.capsules:
            logger.warning(f"Attempted to update state of unknown capsule {capsule_id}")
            return False
        
        capsule = self.capsules[capsule_id]
        old_state = capsule.state
        
        if old_state == state:
            # No change
            return True
        
        capsule.update_state(state)
        
        # Add debug trace
        await self.add_debug_trace(
            capsule_id=capsule_id,
            component="workflow_controller",
            message=f"State changed from {old_state} to {state}"
        )
        
        # Notify callback
        if self.on_capsule_state_changed:
            self.on_capsule_state_changed(capsule, state)
        
        return True
    
    async def update_capsule_task(self, capsule_id: str, task_id: str) -> bool:
        """
        Update the current task of a capsule.
        
        Args:
            capsule_id: The ID of the capsule
            task_id: The ID of the current task
            
        Returns:
            True if the capsule was updated, False if it wasn't found
        """
        if capsule_id not in self.capsules:
            logger.warning(f"Attempted to update task of unknown capsule {capsule_id}")
            return False
        
        capsule = self.capsules[capsule_id]
        old_task_id = capsule.current_task_id
        
        if old_task_id == task_id:
            # No change
            return True
        
        capsule.current_task_id = task_id
        capsule.updated_at = datetime.now()
        
        # Add debug trace
        await self.add_debug_trace(
            capsule_id=capsule_id,
            component="workflow_controller",
            message=f"Current task changed from {old_task_id or 'None'} to {task_id}",
            task_id=task_id
        )
        
        # Notify callback
        if self.on_capsule_updated:
            self.on_capsule_updated(capsule)
        
        return True
    
    async def update_capsule_context(self, capsule_id: str, context_variables: Dict[str, Any]) -> bool:
        """
        Update the context variables of a capsule.
        
        Args:
            capsule_id: The ID of the capsule
            context_variables: The context variables to update
            
        Returns:
            True if the capsule was updated, False if it wasn't found
        """
        if capsule_id not in self.capsules:
            logger.warning(f"Attempted to update context of unknown capsule {capsule_id}")
            return False
        
        capsule = self.capsules[capsule_id]
        capsule.context_variables.update(context_variables)
        capsule.updated_at = datetime.now()
        
        # Notify callback
        if self.on_capsule_updated:
            self.on_capsule_updated(capsule)
        
        return True
    
    async def take_memory_snapshot(self, capsule_id: str) -> Optional[str]:
        """
        Take a snapshot of a capsule's memory state.
        
        Args:
            capsule_id: The ID of the capsule
            
        Returns:
            The ID of the created snapshot, or None if the capsule wasn't found
        """
        if capsule_id not in self.capsules:
            logger.warning(f"Attempted to take memory snapshot of unknown capsule {capsule_id}")
            return None
        
        capsule = self.capsules[capsule_id]
        
        # Create snapshot
        snapshot = CapsuleMemorySnapshot(
            capsule_id=capsule_id,
            context_variables=capsule.context_variables.copy(),
            workflow_state={
                "state": capsule.state,
                "progress": capsule.progress,
                "current_task_id": capsule.current_task_id,
                "execution_mode": capsule.execution_mode
            },
            task_states={},  # In a real implementation, we would capture task states
            metadata={
                "capsule_name": capsule.name,
                "workflow_id": capsule.workflow_id,
                "execution_id": capsule.execution_id
            }
        )
        
        # Store snapshot
        if capsule_id not in self.memory_snapshots:
            self.memory_snapshots[capsule_id] = []
        
        self.memory_snapshots[capsule_id].append(snapshot)
        
        # Add debug trace
        await self.add_debug_trace(
            capsule_id=capsule_id,
            component="memory_manager",
            message=f"Memory snapshot taken: {snapshot.id}"
        )
        
        logger.info(f"Took memory snapshot {snapshot.id} for capsule {capsule_id}")
        return snapshot.id
    
    async def get_memory_snapshot(self, snapshot_id: str) -> Optional[CapsuleMemorySnapshot]:
        """
        Get a memory snapshot by ID.
        
        Args:
            snapshot_id: The ID of the snapshot
            
        Returns:
            The memory snapshot if found, None otherwise
        """
        # Search for the snapshot in all capsules
        for snapshots in self.memory_snapshots.values():
            for snapshot in snapshots:
                if snapshot.id == snapshot_id:
                    return snapshot
        
        return None
    
    async def list_memory_snapshots(self, capsule_id: str) -> List[CapsuleMemorySnapshot]:
        """
        List memory snapshots for a capsule.
        
        Args:
            capsule_id: The ID of the capsule
            
        Returns:
            A list of memory snapshots
        """
        return self.memory_snapshots.get(capsule_id, [])
    
    async def restore_memory_snapshot(self, snapshot_id: str) -> bool:
        """
        Restore a capsule's state from a memory snapshot.
        
        Args:
            snapshot_id: The ID of the snapshot
            
        Returns:
            True if the snapshot was restored, False if it wasn't found
        """
        # Find the snapshot
        snapshot = await self.get_memory_snapshot(snapshot_id)
        if not snapshot:
            logger.warning(f"Attempted to restore unknown memory snapshot {snapshot_id}")
            return False
        
        capsule_id = snapshot.capsule_id
        
        # Check if the capsule exists
        if capsule_id not in self.capsules:
            logger.warning(f"Attempted to restore snapshot for unknown capsule {capsule_id}")
            return False
        
        capsule = self.capsules[capsule_id]
        
        # Restore context variables
        capsule.context_variables = snapshot.context_variables.copy()
        
        # Restore workflow state
        workflow_state = snapshot.workflow_state
        capsule.state = CapsuleState(workflow_state.get("state", CapsuleState.RUNNING))
        capsule.progress = workflow_state.get("progress", 0.0)
        capsule.current_task_id = workflow_state.get("current_task_id")
        capsule.execution_mode = workflow_state.get("execution_mode", "reactive")
        
        # Update timestamp
        capsule.updated_at = datetime.now()
        
        # Add debug trace
        await self.add_debug_trace(
            capsule_id=capsule_id,
            component="memory_manager",
            message=f"Memory snapshot restored: {snapshot_id}"
        )
        
        # Notify callback
        if self.on_capsule_updated:
            self.on_capsule_updated(capsule)
        
        logger.info(f"Restored memory snapshot {snapshot_id} for capsule {capsule_id}")
        return True
    
    async def add_debug_trace(self, 
                            capsule_id: str, 
                            component: str, 
                            message: str,
                            level: str = "INFO",
                            data: Optional[Dict[str, Any]] = None,
                            task_id: Optional[str] = None,
                            agent_id: Optional[str] = None,
                            execution_mode: Optional[str] = None) -> str:
        """
        Add a debug trace entry for a capsule.
        
        Args:
            capsule_id: The ID of the capsule
            component: The component that generated the trace
            message: The trace message
            level: The trace level
            data: Optional data associated with the trace
            task_id: Optional ID of the task related to the trace
            agent_id: Optional ID of the agent related to the trace
            execution_mode: Optional execution mode at the time of the trace
            
        Returns:
            The ID of the created trace entry
        """
        # Create trace entry
        trace = CapsuleDebugTrace(
            capsule_id=capsule_id,
            level=level,
            component=component,
            message=message,
            data=data,
            task_id=task_id,
            agent_id=agent_id,
            execution_mode=execution_mode
        )
        
        # Generate pattern signature if possible
        if task_id and component:
            trace.pattern_signature = f"{component}:{task_id}:{level}"
        
        # Store trace
        if capsule_id not in self.debug_traces:
            self.debug_traces[capsule_id] = []
        
        self.debug_traces[capsule_id].append(trace)
        
        # Notify callback
        if self.on_debug_trace_added:
            self.on_debug_trace_added(trace)
        
        return trace.id
    
    async def get_debug_traces(self, 
                             capsule_id: str, 
                             limit: int = 100,
                             level: Optional[str] = None,
                             component: Optional[str] = None,
                             task_id: Optional[str] = None,
                             agent_id: Optional[str] = None) -> List[CapsuleDebugTrace]:
        """
        Get debug traces for a capsule, optionally filtered.
        
        Args:
            capsule_id: The ID of the capsule
            limit: Maximum number of traces to return
            level: Optional level to filter by
            component: Optional component to filter by
            task_id: Optional task ID to filter by
            agent_id: Optional agent ID to filter by
            
        Returns:
            A list of debug traces
        """
        if capsule_id not in self.debug_traces:
            return []
        
        traces = self.debug_traces[capsule_id]
        
        # Apply filters
        if level:
            traces = [t for t in traces if t.level == level]
        
        if component:
            traces = [t for t in traces if t.component == component]
        
        if task_id:
            traces = [t for t in traces if t.task_id == task_id]
        
        if agent_id:
            traces = [t for t in traces if t.agent_id == agent_id]
        
        # Sort by timestamp (newest first) and limit
        return sorted(traces, key=lambda t: t.timestamp, reverse=True)[:limit]
    
    async def submit_capsule_action(self, action: Dict[str, Any]) -> bool:
        """
        Submit an action to be performed on a capsule.
        
        Args:
            action: The action parameters
            
        Returns:
            True if the action was submitted successfully, False otherwise
            
        Raises:
            ValueError: If the action is invalid
        """
        try:
            # Create action
            capsule_action = CapsuleAction(**action)
            
            # Check if the capsule exists
            capsule_id = capsule_action.capsule_id
            if capsule_id not in self.capsules:
                logger.warning(f"Attempted to submit action for unknown capsule {capsule_id}")
                return False
            
            # Initialize action queue if needed
            if capsule_id not in self.pending_actions:
                self.pending_actions[capsule_id] = []
            
            # Add the action to the queue
            self.pending_actions[capsule_id].append(capsule_action)
            
            # Notify callback
            if self.on_capsule_action_received:
                self.on_capsule_action_received(capsule_action)
            
            logger.info(f"Submitted {capsule_action.action_type} action for capsule {capsule_id}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to submit capsule action: {e}")
            raise ValueError(f"Invalid capsule action: {e}")
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Args:
            context: The execution context for the agent
            
        Returns:
            The result of the agent execution
        """
        # Extract parameters from context
        action = context.variables.get("action", "create_capsule")
        
        if action == "create_capsule":
            # Create a new capsule
            workflow_id = context.variables.get("workflow_id")
            execution_id = context.variables.get("execution_id")
            name = context.variables.get("name")
            
            if not workflow_id or not execution_id or not name:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="workflow_id, execution_id, and name are required for create_capsule action"
                )
            
            # Extract optional parameters
            kwargs = {}
            for key in ["description", "owner_id", "execution_mode", "location"]:
                if key in context.variables:
                    kwargs[key] = context.variables[key]
            
            try:
                capsule_id = await self.create_capsule(workflow_id, execution_id, name, **kwargs)
                
                return AgentResult(
                    success=True,
                    message=f"Created capsule {capsule_id}",
                    data={"capsule_id": capsule_id}
                )
            except Exception as e:
                return AgentResult(
                    success=False,
                    message=f"Failed to create capsule",
                    error=str(e)
                )
        
        elif action == "get_capsule":
            # Get a capsule
            capsule_id = context.variables.get("capsule_id")
            if not capsule_id:
                return AgentResult(
                    success=False,
                    message="Missing capsule ID",
                    error="capsule_id is required for get_capsule action"
                )
            
            capsule = await self.get_capsule(capsule_id)
            
            if capsule:
                return AgentResult(
                    success=True,
                    message=f"Retrieved capsule {capsule_id}",
                    data={"capsule": capsule.dict()}
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to get capsule {capsule_id}",
                    error=f"Capsule {capsule_id} not found"
                )
        
        elif action == "list_capsules":
            # List capsules
            workflow_id = context.variables.get("workflow_id")
            state_str = context.variables.get("state")
            owner_id = context.variables.get("owner_id")
            
            state = None
            if state_str:
                try:
                    state = CapsuleState(state_str)
                except ValueError:
                    return AgentResult(
                        success=False,
                        message=f"Invalid capsule state: {state_str}",
                        error=f"State must be one of: {', '.join(e.value for e in CapsuleState)}"
                    )
            
            capsules = await self.list_capsules(workflow_id, state, owner_id)
            
            return AgentResult(
                success=True,
                message=f"Listed {len(capsules)} capsules",
                data={"capsules": [c.dict() for c in capsules]}
            )
        
        elif action == "update_capsule_progress":
            # Update capsule progress
            capsule_id = context.variables.get("capsule_id")
            progress = context.variables.get("progress")
            
            if not capsule_id or progress is None:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="capsule_id and progress are required for update_capsule_progress action"
                )
            
            try:
                progress = float(progress)
            except ValueError:
                return AgentResult(
                    success=False,
                    message=f"Invalid progress value: {progress}",
                    error="Progress must be a number between 0 and 1"
                )
            
            success = await self.update_capsule_progress(capsule_id, progress)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Updated progress of capsule {capsule_id} to {progress}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to update progress of capsule {capsule_id}",
                    error=f"Capsule {capsule_id} not found"
                )
        
        elif action == "update_capsule_state":
            # Update capsule state
            capsule_id = context.variables.get("capsule_id")
            state_str = context.variables.get("state")
            
            if not capsule_id or not state_str:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="capsule_id and state are required for update_capsule_state action"
                )
            
            try:
                state = CapsuleState(state_str)
            except ValueError:
                return AgentResult(
                    success=False,
                    message=f"Invalid capsule state: {state_str}",
                    error=f"State must be one of: {', '.join(e.value for e in CapsuleState)}"
                )
            
            success = await self.update_capsule_state(capsule_id, state)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Updated state of capsule {capsule_id} to {state}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to update state of capsule {capsule_id}",
                    error=f"Capsule {capsule_id} not found"
                )
        
        elif action == "update_capsule_task":
            # Update capsule task
            capsule_id = context.variables.get("capsule_id")
            task_id = context.variables.get("task_id")
            
            if not capsule_id or not task_id:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="capsule_id and task_id are required for update_capsule_task action"
                )
            
            success = await self.update_capsule_task(capsule_id, task_id)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Updated task of capsule {capsule_id} to {task_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to update task of capsule {capsule_id}",
                    error=f"Capsule {capsule_id} not found"
                )
        
        elif action == "update_capsule_context":
            # Update capsule context
            capsule_id = context.variables.get("capsule_id")
            context_variables = context.variables.get("context_variables")
            
            if not capsule_id or not context_variables:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="capsule_id and context_variables are required for update_capsule_context action"
                )
            
            success = await self.update_capsule_context(capsule_id, context_variables)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Updated context of capsule {capsule_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to update context of capsule {capsule_id}",
                    error=f"Capsule {capsule_id} not found"
                )
        
        elif action == "take_memory_snapshot":
            # Take memory snapshot
            capsule_id = context.variables.get("capsule_id")
            
            if not capsule_id:
                return AgentResult(
                    success=False,
                    message="Missing capsule ID",
                    error="capsule_id is required for take_memory_snapshot action"
                )
            
            snapshot_id = await self.take_memory_snapshot(capsule_id)
            
            if snapshot_id:
                return AgentResult(
                    success=True,
                    message=f"Took memory snapshot {snapshot_id} for capsule {capsule_id}",
                    data={"snapshot_id": snapshot_id}
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to take memory snapshot for capsule {capsule_id}",
                    error=f"Capsule {capsule_id} not found"
                )
        
        elif action == "get_memory_snapshot":
            # Get memory snapshot
            snapshot_id = context.variables.get("snapshot_id")
            
            if not snapshot_id:
                return AgentResult(
                    success=False,
                    message="Missing snapshot ID",
                    error="snapshot_id is required for get_memory_snapshot action"
                )
            
            snapshot = await self.get_memory_snapshot(snapshot_id)
            
            if snapshot:
                return AgentResult(
                    success=True,
                    message=f"Retrieved memory snapshot {snapshot_id}",
                    data={"snapshot": snapshot.dict()}
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to get memory snapshot {snapshot_id}",
                    error=f"Snapshot {snapshot_id} not found"
                )
        
        elif action == "list_memory_snapshots":
            # List memory snapshots
            capsule_id = context.variables.get("capsule_id")
            
            if not capsule_id:
                return AgentResult(
                    success=False,
                    message="Missing capsule ID",
                    error="capsule_id is required for list_memory_snapshots action"
                )
            
            snapshots = await self.list_memory_snapshots(capsule_id)
            
            return AgentResult(
                success=True,
                message=f"Listed {len(snapshots)} memory snapshots for capsule {capsule_id}",
                data={"snapshots": [s.dict() for s in snapshots]}
            )
        
        elif action == "restore_memory_snapshot":
            # Restore memory snapshot
            snapshot_id = context.variables.get("snapshot_id")
            
            if not snapshot_id:
                return AgentResult(
                    success=False,
                    message="Missing snapshot ID",
                    error="snapshot_id is required for restore_memory_snapshot action"
                )
            
            success = await self.restore_memory_snapshot(snapshot_id)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Restored memory snapshot {snapshot_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to restore memory snapshot {snapshot_id}",
                    error=f"Snapshot {snapshot_id} not found or capsule not found"
                )
        
        elif action == "add_debug_trace":
            # Add debug trace
            capsule_id = context.variables.get("capsule_id")
            component = context.variables.get("component")
            message = context.variables.get("message")
            
            if not capsule_id or not component or not message:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="capsule_id, component, and message are required for add_debug_trace action"
                )
            
            # Extract optional parameters
            kwargs = {}
            for key in ["level", "data", "task_id", "agent_id", "execution_mode"]:
                if key in context.variables:
                    kwargs[key] = context.variables[key]
            
            trace_id = await self.add_debug_trace(capsule_id, component, message, **kwargs)
            
            return AgentResult(
                success=True,
                message=f"Added debug trace {trace_id} for capsule {capsule_id}",
                data={"trace_id": trace_id}
            )
        
        elif action == "get_debug_traces":
            # Get debug traces
            capsule_id = context.variables.get("capsule_id")
            
            if not capsule_id:
                return AgentResult(
                    success=False,
                    message="Missing capsule ID",
                    error="capsule_id is required for get_debug_traces action"
                )
            
            # Extract optional parameters
            kwargs = {}
            for key in ["limit", "level", "component", "task_id", "agent_id"]:
                if key in context.variables:
                    kwargs[key] = context.variables[key]
            
            traces = await self.get_debug_traces(capsule_id, **kwargs)
            
            return AgentResult(
                success=True,
                message=f"Retrieved {len(traces)} debug traces for capsule {capsule_id}",
                data={"traces": [t.dict() for t in traces]}
            )
        
        elif action == "submit_capsule_action":
            # Submit capsule action
            action_data = context.variables.get("action")
            
            if not action_data:
                return AgentResult(
                    success=False,
                    message="Missing action data",
                    error="action is required for submit_capsule_action action"
                )
            
            try:
                success = await self.submit_capsule_action(action_data)
                
                if success:
                    return AgentResult(
                        success=True,
                        message=f"Submitted {action_data.get('action_type')} action for capsule {action_data.get('capsule_id')}"
                    )
                else:
                    return AgentResult(
                        success=False,
                        message=f"Failed to submit action for capsule {action_data.get('capsule_id')}",
                        error=f"Capsule {action_data.get('capsule_id')} not found"
                    )
            except ValueError as e:
                return AgentResult(
                    success=False,
                    message=f"Failed to submit capsule action",
                    error=str(e)
                )
        
        else:
            # Unknown action
            return AgentResult(
                success=False,
                message=f"Unknown action: {action}",
                error=f"Action {action} is not supported"
            )
