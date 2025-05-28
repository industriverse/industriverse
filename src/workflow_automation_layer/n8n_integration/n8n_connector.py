"""
n8n Connector Module for Industriverse Workflow Automation Layer

This module implements the core connector for integrating with n8n workflow automation platform.
It provides functionality for bidirectional communication, workflow synchronization, and
webhook management between Industriverse and n8n.
"""

import logging
import asyncio
import json
import uuid
import os
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta

import httpx
from pydantic import BaseModel, Field, validator

# Configure logging
logger = logging.getLogger(__name__)


class N8nConnectionConfig(BaseModel):
    """Model representing configuration for connecting to an n8n instance."""
    base_url: str
    api_key: str
    webhook_base_url: Optional[str] = None  # Base URL for Industriverse webhooks
    timeout_seconds: int = 10
    verify_ssl: bool = True


class N8nWorkflow(BaseModel):
    """Model representing an n8n workflow."""
    id: str
    name: str
    active: bool
    nodes: List[Dict[str, Any]]
    connections: Dict[str, Any]
    settings: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class N8nWebhook(BaseModel):
    """Model representing an n8n webhook."""
    id: str
    workflow_id: str
    node_id: str
    url: str
    method: str = "POST"
    path_suffix: Optional[str] = None
    industriverse_endpoint: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class N8nNodeTemplate(BaseModel):
    """Model representing a template for an n8n node."""
    type: str
    name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    position: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class N8nConnector:
    """
    Core connector for integrating with n8n workflow automation platform.
    
    This class provides functionality for bidirectional communication, workflow
    synchronization, and webhook management between Industriverse and n8n.
    """
    
    def __init__(self, config: N8nConnectionConfig):
        """
        Initialize the N8nConnector.
        
        Args:
            config: Configuration for connecting to the n8n instance
        """
        self.config = config
        
        # HTTP client for n8n communication
        self.http_client = httpx.AsyncClient(
            base_url=self.config.base_url,
            headers={
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.config.timeout_seconds,
            verify=self.config.verify_ssl
        )
        
        # Store registered webhooks
        self.webhooks: Dict[str, N8nWebhook] = {}
        
        # Callbacks
        self.on_webhook_received: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
        logger.info(f"N8nConnector initialized for n8n instance at {config.base_url}")
    
    async def test_connection(self) -> bool:
        """Test the connection to the configured n8n instance."""
        try:
            # Use a simple endpoint like listing workflows
            response = await self.http_client.get("/api/v1/workflows")
            response.raise_for_status()
            logger.info(f"Successfully connected to n8n instance at {self.config.base_url}")
            return True
        except httpx.RequestError as e:
            logger.error(f"Failed to connect to n8n instance at {self.config.base_url}: {e}")
            return False
        except httpx.HTTPStatusError as e:
            logger.error(f"n8n API returned error: {e.response.status_code} - {e.response.text}")
            return False
    
    async def get_workflows(self) -> List[N8nWorkflow]:
        """
        Get all workflows from the n8n instance.
        
        Returns:
            A list of n8n workflows
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
        """
        response = await self.http_client.get("/api/v1/workflows")
        response.raise_for_status()
        
        workflows_data = response.json()
        workflows = []
        
        for workflow_data in workflows_data.get("data", []):
            try:
                workflow = N8nWorkflow(
                    id=workflow_data.get("id"),
                    name=workflow_data.get("name"),
                    active=workflow_data.get("active", False),
                    nodes=workflow_data.get("nodes", []),
                    connections=workflow_data.get("connections", {}),
                    settings=workflow_data.get("settings"),
                    tags=workflow_data.get("tags", []),
                    created_at=workflow_data.get("createdAt"),
                    updated_at=workflow_data.get("updatedAt")
                )
                workflows.append(workflow)
            except Exception as e:
                logger.warning(f"Failed to parse workflow data: {e}")
        
        logger.info(f"Retrieved {len(workflows)} workflows from n8n")
        return workflows
    
    async def get_workflow(self, workflow_id: str) -> Optional[N8nWorkflow]:
        """
        Get a specific workflow from the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            The workflow if found, None otherwise
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
        """
        try:
            response = await self.http_client.get(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()
            
            workflow_data = response.json()
            
            workflow = N8nWorkflow(
                id=workflow_data.get("id"),
                name=workflow_data.get("name"),
                active=workflow_data.get("active", False),
                nodes=workflow_data.get("nodes", []),
                connections=workflow_data.get("connections", {}),
                settings=workflow_data.get("settings"),
                tags=workflow_data.get("tags", []),
                created_at=workflow_data.get("createdAt"),
                updated_at=workflow_data.get("updatedAt")
            )
            
            logger.info(f"Retrieved workflow {workflow_id} from n8n")
            return workflow
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Workflow {workflow_id} not found in n8n")
                return None
            raise
    
    async def create_workflow(self, workflow: Dict[str, Any]) -> str:
        """
        Create a new workflow in the n8n instance.
        
        Args:
            workflow: The workflow data
            
        Returns:
            The ID of the created workflow
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
        """
        response = await self.http_client.post("/api/v1/workflows", json=workflow)
        response.raise_for_status()
        
        workflow_data = response.json()
        workflow_id = workflow_data.get("id")
        
        logger.info(f"Created workflow {workflow_id} in n8n")
        return workflow_id
    
    async def update_workflow(self, workflow_id: str, workflow: Dict[str, Any]) -> bool:
        """
        Update an existing workflow in the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            workflow: The updated workflow data
            
        Returns:
            True if the workflow was updated successfully, False otherwise
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
        """
        try:
            response = await self.http_client.put(f"/api/v1/workflows/{workflow_id}", json=workflow)
            response.raise_for_status()
            
            logger.info(f"Updated workflow {workflow_id} in n8n")
            return True
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Workflow {workflow_id} not found in n8n")
                return False
            raise
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow from the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            True if the workflow was deleted successfully, False otherwise
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
        """
        try:
            response = await self.http_client.delete(f"/api/v1/workflows/{workflow_id}")
            response.raise_for_status()
            
            logger.info(f"Deleted workflow {workflow_id} from n8n")
            return True
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Workflow {workflow_id} not found in n8n")
                return False
            raise
    
    async def activate_workflow(self, workflow_id: str) -> bool:
        """
        Activate a workflow in the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            True if the workflow was activated successfully, False otherwise
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
        """
        try:
            response = await self.http_client.post(f"/api/v1/workflows/{workflow_id}/activate")
            response.raise_for_status()
            
            logger.info(f"Activated workflow {workflow_id} in n8n")
            return True
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Workflow {workflow_id} not found in n8n")
                return False
            raise
    
    async def deactivate_workflow(self, workflow_id: str) -> bool:
        """
        Deactivate a workflow in the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            True if the workflow was deactivated successfully, False otherwise
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
        """
        try:
            response = await self.http_client.post(f"/api/v1/workflows/{workflow_id}/deactivate")
            response.raise_for_status()
            
            logger.info(f"Deactivated workflow {workflow_id} in n8n")
            return True
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Workflow {workflow_id} not found in n8n")
                return False
            raise
    
    async def execute_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow in the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            data: Optional data to pass to the workflow
            
        Returns:
            The execution result
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
        """
        try:
            response = await self.http_client.post(
                f"/api/v1/workflows/{workflow_id}/execute",
                json=data or {}
            )
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Executed workflow {workflow_id} in n8n")
            return result
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Workflow {workflow_id} not found in n8n")
                return {"error": "Workflow not found"}
            raise
    
    async def register_webhook(self, webhook: Dict[str, Any]) -> str:
        """
        Register a webhook for an n8n workflow.
        
        Args:
            webhook: The webhook data
            
        Returns:
            The ID of the registered webhook
            
        Raises:
            ValueError: If the webhook data is invalid
        """
        try:
            # Create webhook object
            webhook_obj = N8nWebhook(**webhook)
            
            # Generate an ID if not provided
            if not webhook_obj.id:
                webhook_obj.id = str(uuid.uuid4())
            
            # Generate Industriverse endpoint if not provided
            if not webhook_obj.industriverse_endpoint and self.config.webhook_base_url:
                path_suffix = webhook_obj.path_suffix or f"n8n-webhook/{webhook_obj.id}"
                webhook_obj.industriverse_endpoint = f"{self.config.webhook_base_url.rstrip('/')}/{path_suffix}"
            
            # Store the webhook
            self.webhooks[webhook_obj.id] = webhook_obj
            
            logger.info(f"Registered webhook {webhook_obj.id} for workflow {webhook_obj.workflow_id}")
            return webhook_obj.id
        
        except Exception as e:
            logger.error(f"Failed to register webhook: {e}")
            raise ValueError(f"Invalid webhook data: {e}")
    
    async def get_webhook(self, webhook_id: str) -> Optional[N8nWebhook]:
        """
        Get a registered webhook by ID.
        
        Args:
            webhook_id: The ID of the webhook
            
        Returns:
            The webhook if found, None otherwise
        """
        return self.webhooks.get(webhook_id)
    
    async def list_webhooks(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all registered webhooks, optionally filtered by workflow ID.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            A list of webhooks with their IDs
        """
        result = []
        
        for webhook_id, webhook in self.webhooks.items():
            if workflow_id is None or webhook.workflow_id == workflow_id:
                result.append({"id": webhook_id, "webhook": webhook.dict()})
        
        return result
    
    async def delete_webhook(self, webhook_id: str) -> bool:
        """
        Delete a registered webhook.
        
        Args:
            webhook_id: The ID of the webhook
            
        Returns:
            True if the webhook was deleted, False if it wasn't found
        """
        if webhook_id in self.webhooks:
            del self.webhooks[webhook_id]
            logger.info(f"Deleted webhook {webhook_id}")
            return True
        
        logger.warning(f"Attempted to delete unknown webhook {webhook_id}")
        return False
    
    async def handle_webhook(self, webhook_id: str, data: Dict[str, Any]) -> bool:
        """
        Handle an incoming webhook from n8n.
        
        Args:
            webhook_id: The ID of the webhook
            data: The webhook payload
            
        Returns:
            True if the webhook was handled successfully, False otherwise
        """
        webhook = await self.get_webhook(webhook_id)
        if not webhook:
            logger.warning(f"Received webhook for unknown webhook ID {webhook_id}")
            return False
        
        # Process the webhook
        logger.info(f"Received webhook {webhook_id} for workflow {webhook.workflow_id}")
        
        # Call the webhook callback if registered
        if self.on_webhook_received:
            try:
                self.on_webhook_received(webhook_id, data)
                return True
            except Exception as e:
                logger.error(f"Error in webhook callback: {e}")
                return False
        
        return True
    
    async def create_workflow_from_template(self, template: Dict[str, Any]) -> str:
        """
        Create a new workflow in n8n from a template.
        
        Args:
            template: The workflow template
            
        Returns:
            The ID of the created workflow
            
        Raises:
            httpx.RequestError: If the request fails
            httpx.HTTPStatusError: If the n8n API returns an error
            ValueError: If the template is invalid
        """
        # Validate required fields
        if "name" not in template:
            raise ValueError("Workflow template must include a name")
        
        if "nodes" not in template or not isinstance(template["nodes"], list):
            raise ValueError("Workflow template must include a list of nodes")
        
        # Create the workflow
        workflow_id = await self.create_workflow(template)
        
        logger.info(f"Created workflow {workflow_id} from template")
        return workflow_id
    
    async def create_node_from_template(self, node_template: N8nNodeTemplate) -> Dict[str, Any]:
        """
        Create an n8n node from a template.
        
        Args:
            node_template: The node template
            
        Returns:
            The created node data
        """
        # Generate a node ID if not provided
        node_id = node_template.metadata.get("id", f"node_{uuid.uuid4().hex[:8]}")
        
        # Create the node
        node = {
            "id": node_id,
            "name": node_template.name,
            "type": node_template.type,
            "parameters": node_template.parameters,
            "typeVersion": 1,
            "position": node_template.position or {"x": 0, "y": 0}
        }
        
        return node
    
    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
