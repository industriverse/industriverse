"""
Workflow Trigger Agent Module for Industriverse Workflow Automation Layer

This module implements the Workflow Trigger Agent, which is responsible for
initiating workflows based on various triggers such as schedules, events,
data changes, and external system notifications.

The WorkflowTriggerAgent class extends the BaseAgent to provide specialized
functionality for workflow triggering and initialization.
"""

import logging
import asyncio
import json
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta

from pydantic import BaseModel, Field

from .base_agent import BaseAgent, AgentMetadata, AgentConfig, AgentContext, AgentResult, AgentCapability

# Configure logging
logger = logging.getLogger(__name__)


class TriggerType(str, Enum):
    """Enum representing the possible types of workflow triggers."""
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    DATA_CHANGE = "data_change"
    EXTERNAL_SYSTEM = "external_system"
    API_CALL = "api_call"
    MANUAL = "manual"
    DEPENDENT_WORKFLOW = "dependent_workflow"
    CONDITION_BASED = "condition_based"


class TriggerConfig(BaseModel):
    """Model representing configuration for a workflow trigger."""
    trigger_type: TriggerType
    workflow_id: str
    enabled: bool = True
    priority: int = 0
    
    # Schedule-specific fields
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # Event-based fields
    event_source: Optional[str] = None
    event_type: Optional[str] = None
    event_filter: Optional[Dict[str, Any]] = None
    
    # Data change fields
    data_source: Optional[str] = None
    data_path: Optional[str] = None
    change_type: Optional[str] = None  # "create", "update", "delete"
    
    # External system fields
    system_name: Optional[str] = None
    system_endpoint: Optional[str] = None
    
    # Dependent workflow fields
    parent_workflow_id: Optional[str] = None
    parent_workflow_status: Optional[str] = None
    
    # Condition-based fields
    condition_expression: Optional[str] = None
    
    # Common fields
    parameters: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TriggerHistory(BaseModel):
    """Model representing the history of a workflow trigger execution."""
    trigger_id: str
    workflow_id: str
    execution_id: Optional[str] = None
    trigger_time: datetime = Field(default_factory=datetime.now)
    success: bool = True
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)


class WorkflowTriggerAgent(BaseAgent):
    """
    Agent responsible for triggering workflows based on various conditions.
    
    This agent monitors schedules, events, data changes, and external system
    notifications to initiate workflows at the appropriate times.
    """
    
    def __init__(self, metadata: Optional[AgentMetadata] = None, config: Optional[AgentConfig] = None):
        """
        Initialize the WorkflowTriggerAgent.
        
        Args:
            metadata: Optional metadata for the agent
            config: Optional configuration for the agent
        """
        if metadata is None:
            metadata = AgentMetadata(
                id="workflow_trigger_agent",
                name="Workflow Trigger Agent",
                description="Initiates workflows based on various triggers",
                capabilities=[AgentCapability.WORKFLOW_TRIGGER]
            )
        
        super().__init__(metadata, config)
        
        # Store trigger configurations
        self.triggers: Dict[str, TriggerConfig] = {}
        
        # Store trigger history
        self.trigger_history: List[TriggerHistory] = []
        
        # Callbacks
        self.on_workflow_triggered: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
        # Background tasks
        self.background_tasks = []
        
        logger.info(f"WorkflowTriggerAgent initialized")
    
    async def _initialize_impl(self) -> bool:
        """
        Implementation of agent initialization.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        # Start background tasks for monitoring triggers
        self._start_schedule_monitor()
        
        return True
    
    def _start_schedule_monitor(self):
        """Start the background task for monitoring scheduled triggers."""
        task = asyncio.create_task(self._monitor_scheduled_triggers())
        self.background_tasks.append(task)
    
    async def _monitor_scheduled_triggers(self):
        """Monitor scheduled triggers and execute them when due."""
        while True:
            try:
                now = datetime.now()
                
                # Check each scheduled trigger
                for trigger_id, trigger in self.triggers.items():
                    if (trigger.trigger_type == TriggerType.SCHEDULED and 
                        trigger.enabled and 
                        self._is_trigger_due(trigger, now)):
                        
                        # Trigger the workflow
                        await self._trigger_workflow(trigger_id, trigger, {})
                
                # Sleep for a short time before checking again
                await asyncio.sleep(1)
            
            except Exception as e:
                logger.error(f"Error in scheduled trigger monitor: {e}")
                await asyncio.sleep(5)  # Sleep longer on error
    
    def _is_trigger_due(self, trigger: TriggerConfig, now: datetime) -> bool:
        """
        Check if a scheduled trigger is due to execute.
        
        Args:
            trigger: The trigger configuration
            now: The current time
            
        Returns:
            True if the trigger is due, False otherwise
        """
        # Check time window
        if trigger.start_time and now < trigger.start_time:
            return False
        
        if trigger.end_time and now > trigger.end_time:
            return False
        
        # Check interval
        if trigger.interval_seconds:
            # Find the most recent execution of this trigger
            recent_executions = [
                h for h in self.trigger_history
                if h.trigger_id == trigger.workflow_id and h.success
            ]
            
            if recent_executions:
                last_execution = max(recent_executions, key=lambda h: h.trigger_time)
                next_due = last_execution.trigger_time + timedelta(seconds=trigger.interval_seconds)
                return now >= next_due
            
            # No previous executions, trigger immediately
            return True
        
        # Check cron expression
        if trigger.cron_expression:
            # This is a simplified check - in a real implementation,
            # we would use a proper cron parser
            # For now, we'll just return False
            return False
        
        # Default: not due
        return False
    
    async def register_trigger(self, trigger: TriggerConfig) -> str:
        """
        Register a new workflow trigger.
        
        Args:
            trigger: The trigger configuration
            
        Returns:
            The ID of the registered trigger
        """
        trigger_id = f"{trigger.workflow_id}_{trigger.trigger_type}_{len(self.triggers)}"
        self.triggers[trigger_id] = trigger
        
        logger.info(f"Registered trigger {trigger_id} for workflow {trigger.workflow_id}")
        return trigger_id
    
    async def unregister_trigger(self, trigger_id: str) -> bool:
        """
        Unregister a workflow trigger.
        
        Args:
            trigger_id: The ID of the trigger to unregister
            
        Returns:
            True if the trigger was unregistered, False if it wasn't found
        """
        if trigger_id not in self.triggers:
            logger.warning(f"Attempted to unregister unknown trigger {trigger_id}")
            return False
        
        del self.triggers[trigger_id]
        
        logger.info(f"Unregistered trigger {trigger_id}")
        return True
    
    async def update_trigger(self, trigger_id: str, trigger: TriggerConfig) -> bool:
        """
        Update a workflow trigger.
        
        Args:
            trigger_id: The ID of the trigger to update
            trigger: The new trigger configuration
            
        Returns:
            True if the trigger was updated, False if it wasn't found
        """
        if trigger_id not in self.triggers:
            logger.warning(f"Attempted to update unknown trigger {trigger_id}")
            return False
        
        self.triggers[trigger_id] = trigger
        
        logger.info(f"Updated trigger {trigger_id}")
        return True
    
    async def get_trigger(self, trigger_id: str) -> Optional[TriggerConfig]:
        """
        Get a workflow trigger by ID.
        
        Args:
            trigger_id: The ID of the trigger to get
            
        Returns:
            The trigger configuration if found, None otherwise
        """
        return self.triggers.get(trigger_id)
    
    async def list_triggers(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered triggers, optionally filtered by workflow ID.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            A list of trigger configurations with their IDs
        """
        result = []
        
        for trigger_id, trigger in self.triggers.items():
            if workflow_id is None or trigger.workflow_id == workflow_id:
                result.append({
                    "id": trigger_id,
                    "config": trigger.dict()
                })
        
        return result
    
    async def handle_event(self, event_source: str, event_type: str, event_data: Dict[str, Any]) -> List[str]:
        """
        Handle an incoming event and trigger matching workflows.
        
        Args:
            event_source: The source of the event
            event_type: The type of event
            event_data: The event data
            
        Returns:
            A list of triggered workflow execution IDs
        """
        triggered_workflows = []
        
        # Find matching event-based triggers
        for trigger_id, trigger in self.triggers.items():
            if (trigger.trigger_type == TriggerType.EVENT_BASED and
                trigger.enabled and
                trigger.event_source == event_source and
                trigger.event_type == event_type and
                self._matches_event_filter(trigger, event_data)):
                
                # Trigger the workflow
                execution_id = await self._trigger_workflow(trigger_id, trigger, event_data)
                if execution_id:
                    triggered_workflows.append(execution_id)
        
        return triggered_workflows
    
    def _matches_event_filter(self, trigger: TriggerConfig, event_data: Dict[str, Any]) -> bool:
        """
        Check if an event matches the filter for a trigger.
        
        Args:
            trigger: The trigger configuration
            event_data: The event data
            
        Returns:
            True if the event matches the filter, False otherwise
        """
        if not trigger.event_filter:
            return True
        
        # Simple filter matching - in a real implementation, this would be more sophisticated
        for key, value in trigger.event_filter.items():
            if key not in event_data or event_data[key] != value:
                return False
        
        return True
    
    async def handle_data_change(self, data_source: str, data_path: str, change_type: str, data: Dict[str, Any]) -> List[str]:
        """
        Handle a data change and trigger matching workflows.
        
        Args:
            data_source: The source of the data
            data_path: The path to the changed data
            change_type: The type of change ("create", "update", "delete")
            data: The changed data
            
        Returns:
            A list of triggered workflow execution IDs
        """
        triggered_workflows = []
        
        # Find matching data change triggers
        for trigger_id, trigger in self.triggers.items():
            if (trigger.trigger_type == TriggerType.DATA_CHANGE and
                trigger.enabled and
                trigger.data_source == data_source and
                trigger.data_path == data_path and
                (trigger.change_type is None or trigger.change_type == change_type)):
                
                # Trigger the workflow
                execution_id = await self._trigger_workflow(trigger_id, trigger, {
                    "data_source": data_source,
                    "data_path": data_path,
                    "change_type": change_type,
                    "data": data
                })
                if execution_id:
                    triggered_workflows.append(execution_id)
        
        return triggered_workflows
    
    async def handle_external_notification(self, system_name: str, notification_data: Dict[str, Any]) -> List[str]:
        """
        Handle a notification from an external system and trigger matching workflows.
        
        Args:
            system_name: The name of the external system
            notification_data: The notification data
            
        Returns:
            A list of triggered workflow execution IDs
        """
        triggered_workflows = []
        
        # Find matching external system triggers
        for trigger_id, trigger in self.triggers.items():
            if (trigger.trigger_type == TriggerType.EXTERNAL_SYSTEM and
                trigger.enabled and
                trigger.system_name == system_name):
                
                # Trigger the workflow
                execution_id = await self._trigger_workflow(trigger_id, trigger, notification_data)
                if execution_id:
                    triggered_workflows.append(execution_id)
        
        return triggered_workflows
    
    async def handle_workflow_completion(self, workflow_id: str, status: str, result: Dict[str, Any]) -> List[str]:
        """
        Handle a workflow completion and trigger dependent workflows.
        
        Args:
            workflow_id: The ID of the completed workflow
            status: The status of the completed workflow
            result: The result of the completed workflow
            
        Returns:
            A list of triggered workflow execution IDs
        """
        triggered_workflows = []
        
        # Find matching dependent workflow triggers
        for trigger_id, trigger in self.triggers.items():
            if (trigger.trigger_type == TriggerType.DEPENDENT_WORKFLOW and
                trigger.enabled and
                trigger.parent_workflow_id == workflow_id and
                (trigger.parent_workflow_status is None or trigger.parent_workflow_status == status)):
                
                # Trigger the workflow
                execution_id = await self._trigger_workflow(trigger_id, trigger, {
                    "parent_workflow_id": workflow_id,
                    "parent_workflow_status": status,
                    "parent_workflow_result": result
                })
                if execution_id:
                    triggered_workflows.append(execution_id)
        
        return triggered_workflows
    
    async def evaluate_condition_triggers(self, context: Dict[str, Any]) -> List[str]:
        """
        Evaluate condition-based triggers and trigger matching workflows.
        
        Args:
            context: The context for condition evaluation
            
        Returns:
            A list of triggered workflow execution IDs
        """
        triggered_workflows = []
        
        # Find matching condition-based triggers
        for trigger_id, trigger in self.triggers.items():
            if (trigger.trigger_type == TriggerType.CONDITION_BASED and
                trigger.enabled and
                trigger.condition_expression and
                self._evaluate_condition(trigger.condition_expression, context)):
                
                # Trigger the workflow
                execution_id = await self._trigger_workflow(trigger_id, trigger, context)
                if execution_id:
                    triggered_workflows.append(execution_id)
        
        return triggered_workflows
    
    def _evaluate_condition(self, condition_expression: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression using the provided context.
        
        Args:
            condition_expression: The condition expression
            context: The context for evaluation
            
        Returns:
            True if the condition evaluates to true, False otherwise
        """
        try:
            # Define the context for evaluation
            eval_context = {
                **context,
                "True": True,
                "False": False
            }
            
            # Evaluate the condition expression
            # Warning: Using eval can be risky if the condition string is user-provided.
            # In a production system, use a safer evaluation method (e.g., a dedicated expression language parser).
            result = eval(condition_expression, {"__builtins__": {}}, eval_context)
            return bool(result)
        
        except Exception as e:
            logger.error(f"Failed to evaluate condition '{condition_expression}': {e}")
            return False
    
    async def manually_trigger_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> Optional[str]:
        """
        Manually trigger a workflow.
        
        Args:
            workflow_id: The ID of the workflow to trigger
            parameters: Optional parameters for the workflow
            
        Returns:
            The execution ID of the triggered workflow, or None if triggering failed
        """
        # Create a manual trigger configuration
        trigger = TriggerConfig(
            trigger_type=TriggerType.MANUAL,
            workflow_id=workflow_id,
            parameters=parameters or {}
        )
        
        # Trigger the workflow
        return await self._trigger_workflow("manual", trigger, parameters or {})
    
    async def _trigger_workflow(self, trigger_id: str, trigger: TriggerConfig, context: Dict[str, Any]) -> Optional[str]:
        """
        Trigger a workflow.
        
        Args:
            trigger_id: The ID of the trigger
            trigger: The trigger configuration
            context: The context for the workflow execution
            
        Returns:
            The execution ID of the triggered workflow, or None if triggering failed
        """
        try:
            # Generate an execution ID
            execution_id = f"{trigger.workflow_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{len(self.trigger_history)}"
            
            # Combine trigger parameters with context
            parameters = {
                **trigger.parameters,
                **context
            }
            
            # Record the trigger in history
            history_entry = TriggerHistory(
                trigger_id=trigger_id,
                workflow_id=trigger.workflow_id,
                execution_id=execution_id,
                parameters=parameters
            )
            self.trigger_history.append(history_entry)
            
            # Notify callback if registered
            if self.on_workflow_triggered:
                self.on_workflow_triggered(trigger.workflow_id, {
                    "execution_id": execution_id,
                    "trigger_id": trigger_id,
                    "parameters": parameters
                })
            
            logger.info(f"Triggered workflow {trigger.workflow_id} with execution ID {execution_id}")
            return execution_id
        
        except Exception as e:
            # Record the failure in history
            history_entry = TriggerHistory(
                trigger_id=trigger_id,
                workflow_id=trigger.workflow_id,
                success=False,
                error_message=str(e),
                parameters=context
            )
            self.trigger_history.append(history_entry)
            
            logger.error(f"Failed to trigger workflow {trigger.workflow_id}: {e}")
            return None
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Args:
            context: The execution context for the agent
            
        Returns:
            The result of the agent execution
        """
        # Extract parameters from context
        action = context.variables.get("action", "list_triggers")
        
        if action == "register_trigger":
            # Register a new trigger
            trigger_config = context.variables.get("trigger_config")
            if not trigger_config:
                return AgentResult(
                    success=False,
                    message="Missing trigger configuration",
                    error="trigger_config is required for register_trigger action"
                )
            
            trigger = TriggerConfig(**trigger_config)
            trigger_id = await self.register_trigger(trigger)
            
            return AgentResult(
                success=True,
                message=f"Registered trigger {trigger_id}",
                data={"trigger_id": trigger_id}
            )
        
        elif action == "unregister_trigger":
            # Unregister a trigger
            trigger_id = context.variables.get("trigger_id")
            if not trigger_id:
                return AgentResult(
                    success=False,
                    message="Missing trigger ID",
                    error="trigger_id is required for unregister_trigger action"
                )
            
            success = await self.unregister_trigger(trigger_id)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Unregistered trigger {trigger_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to unregister trigger {trigger_id}",
                    error=f"Trigger {trigger_id} not found"
                )
        
        elif action == "update_trigger":
            # Update a trigger
            trigger_id = context.variables.get("trigger_id")
            trigger_config = context.variables.get("trigger_config")
            
            if not trigger_id or not trigger_config:
                return AgentResult(
                    success=False,
                    message="Missing trigger ID or configuration",
                    error="trigger_id and trigger_config are required for update_trigger action"
                )
            
            trigger = TriggerConfig(**trigger_config)
            success = await self.update_trigger(trigger_id, trigger)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Updated trigger {trigger_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to update trigger {trigger_id}",
                    error=f"Trigger {trigger_id} not found"
                )
        
        elif action == "get_trigger":
            # Get a trigger
            trigger_id = context.variables.get("trigger_id")
            if not trigger_id:
                return AgentResult(
                    success=False,
                    message="Missing trigger ID",
                    error="trigger_id is required for get_trigger action"
                )
            
            trigger = await self.get_trigger(trigger_id)
            
            if trigger:
                return AgentResult(
                    success=True,
                    message=f"Retrieved trigger {trigger_id}",
                    data={"trigger": trigger.dict()}
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to get trigger {trigger_id}",
                    error=f"Trigger {trigger_id} not found"
                )
        
        elif action == "list_triggers":
            # List triggers
            workflow_id = context.variables.get("workflow_id")
            triggers = await self.list_triggers(workflow_id)
            
            return AgentResult(
                success=True,
                message=f"Listed {len(triggers)} triggers",
                data={"triggers": triggers}
            )
        
        elif action == "handle_event":
            # Handle an event
            event_source = context.variables.get("event_source")
            event_type = context.variables.get("event_type")
            event_data = context.variables.get("event_data", {})
            
            if not event_source or not event_type:
                return AgentResult(
                    success=False,
                    message="Missing event source or type",
                    error="event_source and event_type are required for handle_event action"
                )
            
            triggered_workflows = await self.handle_event(event_source, event_type, event_data)
            
            return AgentResult(
                success=True,
                message=f"Handled event {event_type} from {event_source}, triggered {len(triggered_workflows)} workflows",
                data={"triggered_workflows": triggered_workflows}
            )
        
        elif action == "handle_data_change":
            # Handle a data change
            data_source = context.variables.get("data_source")
            data_path = context.variables.get("data_path")
            change_type = context.variables.get("change_type")
            data = context.variables.get("data", {})
            
            if not data_source or not data_path or not change_type:
                return AgentResult(
                    success=False,
                    message="Missing data source, path, or change type",
                    error="data_source, data_path, and change_type are required for handle_data_change action"
                )
            
            triggered_workflows = await self.handle_data_change(data_source, data_path, change_type, data)
            
            return AgentResult(
                success=True,
                message=f"Handled {change_type} change to {data_path} in {data_source}, triggered {len(triggered_workflows)} workflows",
                data={"triggered_workflows": triggered_workflows}
            )
        
        elif action == "handle_external_notification":
            # Handle an external notification
            system_name = context.variables.get("system_name")
            notification_data = context.variables.get("notification_data", {})
            
            if not system_name:
                return AgentResult(
                    success=False,
                    message="Missing system name",
                    error="system_name is required for handle_external_notification action"
                )
            
            triggered_workflows = await self.handle_external_notification(system_name, notification_data)
            
            return AgentResult(
                success=True,
                message=f"Handled notification from {system_name}, triggered {len(triggered_workflows)} workflows",
                data={"triggered_workflows": triggered_workflows}
            )
        
        elif action == "handle_workflow_completion":
            # Handle a workflow completion
            workflow_id = context.variables.get("workflow_id")
            status = context.variables.get("status")
            result = context.variables.get("result", {})
            
            if not workflow_id or not status:
                return AgentResult(
                    success=False,
                    message="Missing workflow ID or status",
                    error="workflow_id and status are required for handle_workflow_completion action"
                )
            
            triggered_workflows = await self.handle_workflow_completion(workflow_id, status, result)
            
            return AgentResult(
                success=True,
                message=f"Handled completion of workflow {workflow_id} with status {status}, triggered {len(triggered_workflows)} workflows",
                data={"triggered_workflows": triggered_workflows}
            )
        
        elif action == "evaluate_condition_triggers":
            # Evaluate condition triggers
            context_data = context.variables.get("context", {})
            
            triggered_workflows = await self.evaluate_condition_triggers(context_data)
            
            return AgentResult(
                success=True,
                message=f"Evaluated condition triggers, triggered {len(triggered_workflows)} workflows",
                data={"triggered_workflows": triggered_workflows}
            )
        
        elif action == "manually_trigger_workflow":
            # Manually trigger a workflow
            workflow_id = context.variables.get("workflow_id")
            parameters = context.variables.get("parameters", {})
            
            if not workflow_id:
                return AgentResult(
                    success=False,
                    message="Missing workflow ID",
                    error="workflow_id is required for manually_trigger_workflow action"
                )
            
            execution_id = await self.manually_trigger_workflow(workflow_id, parameters)
            
            if execution_id:
                return AgentResult(
                    success=True,
                    message=f"Manually triggered workflow {workflow_id}",
                    data={"execution_id": execution_id}
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to manually trigger workflow {workflow_id}",
                    error="Workflow triggering failed"
                )
        
        else:
            # Unknown action
            return AgentResult(
                success=False,
                message=f"Unknown action: {action}",
                error=f"Action {action} is not supported"
            )
