"""
n8n Synchronization Bridge Agent Module for Industriverse Workflow Automation Layer

This module implements the n8n Sync Bridge Agent, which is responsible for
synchronizing workflow state and human tasks between the Industriverse Workflow
Automation Layer and an external n8n instance.

The N8nSyncBridgeAgent class extends the BaseAgent to provide specialized
functionality for n8n integration.
"""

import logging
import asyncio
import json
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta

import httpx
from pydantic import BaseModel, Field, validator

from .base_agent import BaseAgent, AgentMetadata, AgentConfig, AgentContext, AgentResult, AgentCapability
from .human_intervention_agent import InterventionRequest, InterventionResponse, InterventionStatus

# Configure logging
logger = logging.getLogger(__name__)


class N8nConnectionConfig(BaseModel):
    """Model representing configuration for connecting to an n8n instance."""
    base_url: str
    api_key: str
    webhook_url: Optional[str] = None  # URL for n8n to send updates back
    timeout_seconds: int = 10


class N8nWorkflowMapping(BaseModel):
    """Model representing the mapping between an Industriverse workflow and an n8n workflow."""
    industriverse_workflow_id: str
    n8n_workflow_id: str
    sync_direction: str = "bidirectional"  # "to_n8n", "from_n8n", "bidirectional"
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class N8nTaskMapping(BaseModel):
    """Model representing the mapping between an Industriverse task and an n8n node."""
    industriverse_task_id: str
    n8n_node_id: str
    workflow_mapping_id: str
    sync_direction: str = "bidirectional"
    enabled: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)


class N8nSyncBridgeAgent(BaseAgent):
    """
    Agent responsible for synchronizing workflow state with an external n8n instance.
    
    This agent acts as a bridge, allowing Industriverse workflows to interact with
    n8n workflows and vice versa, enabling human-in-the-loop tasks and leveraging
    n8n's extensive integration capabilities.
    """
    
    def __init__(self, 
                 n8n_config: N8nConnectionConfig,
                 metadata: Optional[AgentMetadata] = None, 
                 config: Optional[AgentConfig] = None):
        """
        Initialize the N8nSyncBridgeAgent.
        
        Args:
            n8n_config: Configuration for connecting to the n8n instance
            metadata: Optional metadata for the agent
            config: Optional configuration for the agent
        """
        if metadata is None:
            metadata = AgentMetadata(
                id="n8n_sync_bridge_agent",
                name="n8n Sync Bridge Agent",
                description="Synchronizes workflow state with an external n8n instance",
                capabilities=[AgentCapability.N8N_INTEGRATION]
            )
        
        super().__init__(metadata, config)
        
        self.n8n_config = n8n_config
        
        # Store workflow and task mappings
        self.workflow_mappings: Dict[str, N8nWorkflowMapping] = {}
        self.task_mappings: Dict[str, N8nTaskMapping] = {}
        
        # HTTP client for n8n communication
        self.http_client = httpx.AsyncClient(
            base_url=self.n8n_config.base_url,
            headers={
                "Authorization": f"Bearer {self.n8n_config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.n8n_config.timeout_seconds
        )
        
        # Callbacks
        self.on_n8n_sync_completed: Optional[Callable[[str, bool, Optional[str]], None]] = None
        
        logger.info(f"N8nSyncBridgeAgent initialized for n8n instance at {n8n_config.base_url}")
    
    async def _initialize_impl(self) -> bool:
        """
        Implementation of agent initialization.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        # Test connection to n8n
        return await self.test_n8n_connection()
    
    async def test_n8n_connection(self) -> bool:
        """Test the connection to the configured n8n instance."""
        try:
            # Use a simple endpoint like listing workflows
            response = await self.http_client.get("/api/v1/workflows")
            response.raise_for_status()
            logger.info(f"Successfully connected to n8n instance at {self.n8n_config.base_url}")
            return True
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to n8n instance at {self.n8n_config.base_url}: {e}")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"n8n API returned error: {e.response.status_code} - {e.response.text}")
            return False
    
    async def register_workflow_mapping(self, mapping: Dict[str, Any]) -> str:
        """
        Register a new workflow mapping.
        
        Args:
            mapping: The workflow mapping parameters
            
        Returns:
            The ID of the registered mapping
            
        Raises:
            ValueError: If the mapping is invalid
        """
        try:
            # Create mapping object
            workflow_mapping = N8nWorkflowMapping(**mapping)
            
            # Generate an ID
            mapping_id = f"wfmap_{workflow_mapping.industriverse_workflow_id}_{workflow_mapping.n8n_workflow_id}"
            
            # Store the mapping
            self.workflow_mappings[mapping_id] = workflow_mapping
            
            logger.info(f"Registered workflow mapping {mapping_id}")
            return mapping_id
        
        except Exception as e:
            logger.error(f"Failed to register workflow mapping: {e}")
            raise ValueError(f"Invalid workflow mapping: {e}")
    
    async def get_workflow_mapping(self, mapping_id: str) -> Optional[N8nWorkflowMapping]:
        """
        Get a workflow mapping by ID.
        
        Args:
            mapping_id: The ID of the mapping
            
        Returns:
            The workflow mapping if found, None otherwise
        """
        return self.workflow_mappings.get(mapping_id)
    
    async def list_workflow_mappings(self) -> List[Dict[str, Any]]:
        """
        List all registered workflow mappings.
        
        Returns:
            A list of workflow mappings with their IDs
        """
        return [
            {"id": mapping_id, "mapping": mapping.dict()}
            for mapping_id, mapping in self.workflow_mappings.items()
        ]
    
    async def register_task_mapping(self, mapping: Dict[str, Any]) -> str:
        """
        Register a new task mapping.
        
        Args:
            mapping: The task mapping parameters
            
        Returns:
            The ID of the registered mapping
            
        Raises:
            ValueError: If the mapping is invalid
        """
        try:
            # Create mapping object
            task_mapping = N8nTaskMapping(**mapping)
            
            # Check if workflow mapping exists
            if task_mapping.workflow_mapping_id not in self.workflow_mappings:
                raise ValueError(f"Workflow mapping {task_mapping.workflow_mapping_id} not found")
            
            # Generate an ID
            mapping_id = f"taskmap_{task_mapping.industriverse_task_id}_{task_mapping.n8n_node_id}"
            
            # Store the mapping
            self.task_mappings[mapping_id] = task_mapping
            
            logger.info(f"Registered task mapping {mapping_id}")
            return mapping_id
        
        except Exception as e:
            logger.error(f"Failed to register task mapping: {e}")
            raise ValueError(f"Invalid task mapping: {e}")
    
    async def get_task_mapping(self, mapping_id: str) -> Optional[N8nTaskMapping]:
        """
        Get a task mapping by ID.
        
        Args:
            mapping_id: The ID of the mapping
            
        Returns:
            The task mapping if found, None otherwise
        """
        return self.task_mappings.get(mapping_id)
    
    async def list_task_mappings(self, workflow_mapping_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered task mappings, optionally filtered by workflow mapping ID.
        
        Args:
            workflow_mapping_id: Optional workflow mapping ID to filter by
            
        Returns:
            A list of task mappings with their IDs
        """
        result = []
        
        for mapping_id, mapping in self.task_mappings.items():
            if workflow_mapping_id is None or mapping.workflow_mapping_id == workflow_mapping_id:
                result.append({"id": mapping_id, "mapping": mapping.dict()})
        
        return result
    
    async def sync_intervention_to_n8n(self, intervention: InterventionRequest) -> bool:
        """
        Synchronize a human intervention request to n8n.
        
        Args:
            intervention: The intervention request
            
        Returns:
            True if synchronization was successful, False otherwise
        """
        # Find relevant workflow mapping
        workflow_mapping = None
        for mapping in self.workflow_mappings.values():
            if mapping.industriverse_workflow_id == intervention.workflow_id and \
               mapping.enabled and \
               mapping.sync_direction in ["to_n8n", "bidirectional"]:
                workflow_mapping = mapping
                break
        
        if not workflow_mapping:
            logger.debug(f"No active n8n workflow mapping found for workflow {intervention.workflow_id}")
            return False
        
        # Find relevant task mapping
        task_mapping = None
        for mapping in self.task_mappings.values():
            if mapping.industriverse_task_id == intervention.task_id and \
               mapping.workflow_mapping_id == workflow_mapping.id and \
               mapping.enabled and \
               mapping.sync_direction in ["to_n8n", "bidirectional"]:
                task_mapping = mapping
                break
        
        if not task_mapping:
            logger.debug(f"No active n8n task mapping found for task {intervention.task_id}")
            return False
        
        # Prepare data for n8n webhook
        n8n_payload = {
            "intervention_id": intervention.id,
            "workflow_id": intervention.workflow_id,
            "execution_id": intervention.execution_id,
            "task_id": intervention.task_id,
            "intervention_type": intervention.intervention_type,
            "priority": intervention.priority,
            "title": intervention.title,
            "description": intervention.description,
            "created_at": intervention.created_at.isoformat(),
            "expires_at": intervention.expires_at.isoformat() if intervention.expires_at else None,
            "assigned_to": intervention.assigned_to,
            "context_data": intervention.context_data,
            "options": intervention.options,
            "industriverse_webhook_url": self.n8n_config.webhook_url  # URL for n8n to send response back
        }
        
        # Send data to n8n workflow webhook
        try:
            # Construct the webhook URL for the specific n8n workflow
            # This assumes n8n webhook URLs follow a pattern like /webhook/{workflow_id}
            # Adjust this based on your actual n8n webhook setup
            webhook_path = f"/webhook/{workflow_mapping.n8n_workflow_id}"
            
            response = await self.http_client.post(webhook_path, json=n8n_payload)
            response.raise_for_status()
            
            logger.info(f"Successfully synced intervention {intervention.id} to n8n workflow {workflow_mapping.n8n_workflow_id}")
            
            # Notify callback
            if self.on_n8n_sync_completed:
                self.on_n8n_sync_completed(intervention.id, True, None)
            
            return True
        
        except httpx.RequestError as e:
            error_msg = f"Failed to send intervention {intervention.id} to n8n: {e}"
            logger.error(error_msg)
            if self.on_n8n_sync_completed:
                self.on_n8n_sync_completed(intervention.id, False, error_msg)
            return False
        except httpx.HTTPStatusError as e:
            error_msg = f"n8n webhook returned error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            if self.on_n8n_sync_completed:
                self.on_n8n_sync_completed(intervention.id, False, error_msg)
            return False
    
    async def handle_n8n_webhook(self, payload: Dict[str, Any]) -> bool:
        """
        Handle an incoming webhook from n8n.
        
        This typically contains the response to a human intervention task.
        
        Args:
            payload: The webhook payload from n8n
            
        Returns:
            True if the webhook was processed successfully, False otherwise
        """
        # Extract intervention ID and response data
        intervention_id = payload.get("intervention_id")
        response_data = payload.get("response")
        
        if not intervention_id or not response_data:
            logger.warning(f"Received invalid webhook payload from n8n: {payload}")
            return False
        
        # Find the corresponding intervention request
        # In a real implementation, this would likely involve a lookup in a database
        # or coordination with the HumanInterventionAgent
        # For now, we assume the HumanInterventionAgent is accessible
        # This requires passing the HumanInterventionAgent instance or using a shared service
        
        # Placeholder: Assume we have access to the HumanInterventionAgent instance
        # human_intervention_agent = get_human_intervention_agent_instance()
        # if not human_intervention_agent:
        #     logger.error("HumanInterventionAgent instance not available")
        #     return False
        
        # intervention = await human_intervention_agent.get_intervention(intervention_id)
        # if not intervention:
        #     logger.warning(f"Received n8n response for unknown intervention {intervention_id}")
        #     return False
        
        # # Check if intervention is still pending
        # if intervention.status != InterventionStatus.PENDING and intervention.status != InterventionStatus.IN_PROGRESS:
        #     logger.warning(f"Received n8n response for non-pending intervention {intervention_id} (status: {intervention.status})")
        #     return False
        
        # Prepare the response object
        response = {
            "intervention_id": intervention_id,
            "responder_id": payload.get("responder_id", "n8n_user"),
            "decision": response_data.get("decision"),
            "comments": response_data.get("comments"),
            "data": response_data.get("data", {}),
            "metadata": {"source": "n8n", **payload.get("metadata", {})}
        }
        
        # Submit the response
        # success = await human_intervention_agent.submit_response(response)
        
        # Placeholder: Log the received response
        logger.info(f"Received n8n response for intervention {intervention_id}: {response}")
        success = True # Assume success for now
        
        if success:
            logger.info(f"Successfully processed n8n webhook for intervention {intervention_id}")
            return True
        else:
            logger.error(f"Failed to process n8n webhook for intervention {intervention_id}")
            return False
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Args:
            context: The execution context for the agent
            
        Returns:
            The result of the agent execution
        """
        # Extract parameters from context
        action = context.variables.get("action", "sync_intervention")
        
        if action == "test_connection":
            # Test connection to n8n
            success = await self.test_n8n_connection()
            
            return AgentResult(
                success=success,
                message=f"n8n connection test {"succeeded" if success else "failed"}"
            )
        
        elif action == "register_workflow_mapping":
            # Register a workflow mapping
            mapping_data = context.variables.get("mapping")
            if not mapping_data:
                return AgentResult(
                    success=False,
                    message="Missing mapping data",
                    error="mapping is required for register_workflow_mapping action"
                )
            
            try:
                mapping_id = await self.register_workflow_mapping(mapping_data)
                return AgentResult(
                    success=True,
                    message=f"Registered workflow mapping {mapping_id}",
                    data={"mapping_id": mapping_id}
                )
            except ValueError as e:
                return AgentResult(
                    success=False,
                    message="Failed to register workflow mapping",
                    error=str(e)
                )
        
        elif action == "list_workflow_mappings":
            # List workflow mappings
            mappings = await self.list_workflow_mappings()
            return AgentResult(
                success=True,
                message=f"Listed {len(mappings)} workflow mappings",
                data={"mappings": mappings}
            )
        
        elif action == "register_task_mapping":
            # Register a task mapping
            mapping_data = context.variables.get("mapping")
            if not mapping_data:
                return AgentResult(
                    success=False,
                    message="Missing mapping data",
                    error="mapping is required for register_task_mapping action"
                )
            
            try:
                mapping_id = await self.register_task_mapping(mapping_data)
                return AgentResult(
                    success=True,
                    message=f"Registered task mapping {mapping_id}",
                    data={"mapping_id": mapping_id}
                )
            except ValueError as e:
                return AgentResult(
                    success=False,
                    message="Failed to register task mapping",
                    error=str(e)
                )
        
        elif action == "list_task_mappings":
            # List task mappings
            workflow_mapping_id = context.variables.get("workflow_mapping_id")
            mappings = await self.list_task_mappings(workflow_mapping_id)
            return AgentResult(
                success=True,
                message=f"Listed {len(mappings)} task mappings",
                data={"mappings": mappings}
            )
        
        elif action == "sync_intervention":
            # Synchronize an intervention to n8n
            intervention_data = context.variables.get("intervention")
            if not intervention_data:
                return AgentResult(
                    success=False,
                    message="Missing intervention data",
                    error="intervention is required for sync_intervention action"
                )
            
            try:
                # Assuming intervention data is a dict, create the object
                # In a real scenario, this might come from the HumanInterventionAgent
                intervention = InterventionRequest(**intervention_data)
            except Exception as e:
                return AgentResult(
                    success=False,
                    message="Invalid intervention data",
                    error=str(e)
                )
            
            success = await self.sync_intervention_to_n8n(intervention)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Successfully synced intervention {intervention.id} to n8n"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to sync intervention {intervention.id} to n8n",
                    error="Synchronization failed, check logs for details"
                )
        
        elif action == "handle_webhook":
            # Handle incoming webhook from n8n
            payload = context.variables.get("payload")
            if not payload:
                return AgentResult(
                    success=False,
                    message="Missing webhook payload",
                    error="payload is required for handle_webhook action"
                )
            
            success = await self.handle_n8n_webhook(payload)
            
            if success:
                return AgentResult(
                    success=True,
                    message="Successfully processed n8n webhook"
                )
            else:
                return AgentResult(
                    success=False,
                    message="Failed to process n8n webhook",
                    error="Webhook processing failed, check logs for details"
                )
        
        else:
            # Unknown action
            return AgentResult(
                success=False,
                message=f"Unknown action: {action}",
                error=f"Action {action} is not supported"
            )
