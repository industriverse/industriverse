"""
n8n Bridge Service Module for Industriverse Workflow Automation Layer

This module implements the bridge service that connects Industriverse with n8n,
providing a REST API for webhook handling, workflow synchronization, and
bidirectional communication between the two systems.
"""

import logging
import asyncio
import json
import uuid
import os
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Request, Response, Depends, Header, BackgroundTasks
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator

from .n8n_connector import N8nConnector, N8nConnectionConfig, N8nWebhook

# Configure logging
logger = logging.getLogger(__name__)


class WebhookPayload(BaseModel):
    """Model representing a webhook payload."""
    workflow_id: str
    execution_id: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowSyncRequest(BaseModel):
    """Model representing a workflow synchronization request."""
    industriverse_workflow_id: str
    n8n_workflow_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    sync_direction: str = "bidirectional"  # "to_n8n", "from_n8n", "bidirectional"
    nodes: Optional[List[Dict[str, Any]]] = None
    connections: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class N8nBridgeService:
    """
    Bridge service that connects Industriverse with n8n.
    
    This service provides a REST API for webhook handling, workflow synchronization,
    and bidirectional communication between Industriverse and n8n.
    """
    
    def __init__(self, connector: N8nConnector, api_prefix: str = "/api/n8n"):
        """
        Initialize the N8nBridgeService.
        
        Args:
            connector: The n8n connector
            api_prefix: The API prefix for the service endpoints
        """
        self.connector = connector
        self.api_prefix = api_prefix
        
        # Create FastAPI app
        self.app = FastAPI(
            title="Industriverse n8n Bridge Service",
            description="Bridge service for connecting Industriverse with n8n",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()
        
        # Callbacks
        self.on_webhook_received: Optional[Callable[[str, Dict[str, Any]], None]] = None
        
        # Set connector webhook callback
        self.connector.on_webhook_received = self._handle_webhook_callback
        
        logger.info(f"N8nBridgeService initialized with API prefix {api_prefix}")
    
    def _register_routes(self):
        """Register API routes."""
        # Health check
        self.app.get(f"{self.api_prefix}/health", response_model=Dict[str, Any])(self.health_check)
        
        # Webhook endpoints
        self.app.post(f"{self.api_prefix}/webhooks/{{webhook_id}}", response_model=Dict[str, Any])(self.handle_webhook)
        self.app.post(f"{self.api_prefix}/webhooks", response_model=Dict[str, str])(self.register_webhook)
        self.app.get(f"{self.api_prefix}/webhooks", response_model=List[Dict[str, Any]])(self.list_webhooks)
        self.app.get(f"{self.api_prefix}/webhooks/{{webhook_id}}", response_model=Dict[str, Any])(self.get_webhook)
        self.app.delete(f"{self.api_prefix}/webhooks/{{webhook_id}}", response_model=Dict[str, bool])(self.delete_webhook)
        
        # Workflow endpoints
        self.app.get(f"{self.api_prefix}/workflows", response_model=List[Dict[str, Any]])(self.list_workflows)
        self.app.get(f"{self.api_prefix}/workflows/{{workflow_id}}", response_model=Dict[str, Any])(self.get_workflow)
        self.app.post(f"{self.api_prefix}/workflows", response_model=Dict[str, str])(self.create_workflow)
        self.app.put(f"{self.api_prefix}/workflows/{{workflow_id}}", response_model=Dict[str, bool])(self.update_workflow)
        self.app.delete(f"{self.api_prefix}/workflows/{{workflow_id}}", response_model=Dict[str, bool])(self.delete_workflow)
        self.app.post(f"{self.api_prefix}/workflows/{{workflow_id}}/activate", response_model=Dict[str, bool])(self.activate_workflow)
        self.app.post(f"{self.api_prefix}/workflows/{{workflow_id}}/deactivate", response_model=Dict[str, bool])(self.deactivate_workflow)
        self.app.post(f"{self.api_prefix}/workflows/{{workflow_id}}/execute", response_model=Dict[str, Any])(self.execute_workflow)
        
        # Sync endpoints
        self.app.post(f"{self.api_prefix}/sync", response_model=Dict[str, Any])(self.sync_workflow)
    
    async def health_check(self):
        """Health check endpoint."""
        try:
            n8n_connected = await self.connector.test_connection()
            return {
                "status": "healthy",
                "n8n_connected": n8n_connected,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def handle_webhook(self, webhook_id: str, payload: Request):
        """
        Handle an incoming webhook from n8n.
        
        Args:
            webhook_id: The ID of the webhook
            payload: The webhook payload
            
        Returns:
            A response indicating success or failure
        """
        try:
            # Parse the payload
            data = await payload.json()
            
            # Handle the webhook
            success = await self.connector.handle_webhook(webhook_id, data)
            
            if success:
                return {"success": True, "message": f"Webhook {webhook_id} processed successfully"}
            else:
                return {"success": False, "message": f"Failed to process webhook {webhook_id}"}
        
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON payload for webhook {webhook_id}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        except Exception as e:
            logger.error(f"Error handling webhook {webhook_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error handling webhook: {str(e)}")
    
    async def register_webhook(self, webhook: Dict[str, Any]):
        """
        Register a new webhook.
        
        Args:
            webhook: The webhook data
            
        Returns:
            The ID of the registered webhook
        """
        try:
            webhook_id = await self.connector.register_webhook(webhook)
            return {"webhook_id": webhook_id}
        
        except ValueError as e:
            logger.error(f"Invalid webhook data: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        except Exception as e:
            logger.error(f"Error registering webhook: {e}")
            raise HTTPException(status_code=500, detail=f"Error registering webhook: {str(e)}")
    
    async def list_webhooks(self, workflow_id: Optional[str] = None):
        """
        List all registered webhooks, optionally filtered by workflow ID.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            A list of webhooks
        """
        try:
            webhooks = await self.connector.list_webhooks(workflow_id)
            return webhooks
        
        except Exception as e:
            logger.error(f"Error listing webhooks: {e}")
            raise HTTPException(status_code=500, detail=f"Error listing webhooks: {str(e)}")
    
    async def get_webhook(self, webhook_id: str):
        """
        Get a webhook by ID.
        
        Args:
            webhook_id: The ID of the webhook
            
        Returns:
            The webhook data
        """
        try:
            webhook = await self.connector.get_webhook(webhook_id)
            
            if webhook:
                return {"id": webhook_id, "webhook": webhook.dict()}
            else:
                raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"Error getting webhook {webhook_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting webhook: {str(e)}")
    
    async def delete_webhook(self, webhook_id: str):
        """
        Delete a webhook.
        
        Args:
            webhook_id: The ID of the webhook
            
        Returns:
            A response indicating success or failure
        """
        try:
            success = await self.connector.delete_webhook(webhook_id)
            
            if success:
                return {"success": True, "message": f"Webhook {webhook_id} deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail=f"Webhook {webhook_id} not found")
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"Error deleting webhook {webhook_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting webhook: {str(e)}")
    
    async def list_workflows(self):
        """
        List all workflows in the n8n instance.
        
        Returns:
            A list of workflows
        """
        try:
            workflows = await self.connector.get_workflows()
            return [workflow.dict() for workflow in workflows]
        
        except Exception as e:
            logger.error(f"Error listing workflows: {e}")
            raise HTTPException(status_code=500, detail=f"Error listing workflows: {str(e)}")
    
    async def get_workflow(self, workflow_id: str):
        """
        Get a workflow by ID.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            The workflow data
        """
        try:
            workflow = await self.connector.get_workflow(workflow_id)
            
            if workflow:
                return workflow.dict()
            else:
                raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"Error getting workflow {workflow_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error getting workflow: {str(e)}")
    
    async def create_workflow(self, workflow: Dict[str, Any]):
        """
        Create a new workflow in the n8n instance.
        
        Args:
            workflow: The workflow data
            
        Returns:
            The ID of the created workflow
        """
        try:
            workflow_id = await self.connector.create_workflow(workflow)
            return {"workflow_id": workflow_id}
        
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise HTTPException(status_code=500, detail=f"Error creating workflow: {str(e)}")
    
    async def update_workflow(self, workflow_id: str, workflow: Dict[str, Any]):
        """
        Update a workflow in the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            workflow: The updated workflow data
            
        Returns:
            A response indicating success or failure
        """
        try:
            success = await self.connector.update_workflow(workflow_id, workflow)
            
            if success:
                return {"success": True, "message": f"Workflow {workflow_id} updated successfully"}
            else:
                raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"Error updating workflow {workflow_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error updating workflow: {str(e)}")
    
    async def delete_workflow(self, workflow_id: str):
        """
        Delete a workflow from the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            A response indicating success or failure
        """
        try:
            success = await self.connector.delete_workflow(workflow_id)
            
            if success:
                return {"success": True, "message": f"Workflow {workflow_id} deleted successfully"}
            else:
                raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"Error deleting workflow {workflow_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error deleting workflow: {str(e)}")
    
    async def activate_workflow(self, workflow_id: str):
        """
        Activate a workflow in the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            A response indicating success or failure
        """
        try:
            success = await self.connector.activate_workflow(workflow_id)
            
            if success:
                return {"success": True, "message": f"Workflow {workflow_id} activated successfully"}
            else:
                raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"Error activating workflow {workflow_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error activating workflow: {str(e)}")
    
    async def deactivate_workflow(self, workflow_id: str):
        """
        Deactivate a workflow in the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            
        Returns:
            A response indicating success or failure
        """
        try:
            success = await self.connector.deactivate_workflow(workflow_id)
            
            if success:
                return {"success": True, "message": f"Workflow {workflow_id} deactivated successfully"}
            else:
                raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")
        
        except HTTPException:
            raise
        
        except Exception as e:
            logger.error(f"Error deactivating workflow {workflow_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error deactivating workflow: {str(e)}")
    
    async def execute_workflow(self, workflow_id: str, data: Optional[Dict[str, Any]] = None):
        """
        Execute a workflow in the n8n instance.
        
        Args:
            workflow_id: The ID of the workflow
            data: Optional data to pass to the workflow
            
        Returns:
            The execution result
        """
        try:
            result = await self.connector.execute_workflow(workflow_id, data)
            return result
        
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Error executing workflow: {str(e)}")
    
    async def sync_workflow(self, sync_request: WorkflowSyncRequest):
        """
        Synchronize a workflow between Industriverse and n8n.
        
        Args:
            sync_request: The synchronization request
            
        Returns:
            The synchronization result
        """
        try:
            # Check sync direction
            if sync_request.sync_direction not in ["to_n8n", "from_n8n", "bidirectional"]:
                raise ValueError(f"Invalid sync direction: {sync_request.sync_direction}")
            
            # Sync to n8n
            if sync_request.sync_direction in ["to_n8n", "bidirectional"]:
                # Check if we have nodes and connections
                if not sync_request.nodes or not sync_request.connections:
                    raise ValueError("Nodes and connections are required for syncing to n8n")
                
                # Prepare workflow data
                workflow_data = {
                    "name": sync_request.name,
                    "nodes": sync_request.nodes,
                    "connections": sync_request.connections,
                    "active": False,  # Start inactive by default
                    "settings": {
                        "saveManualExecutions": True,
                        "callerPolicy": "workflowsFromSameOwner",
                        "executionTimeout": 3600,
                        "timezone": "UTC"
                    },
                    "tags": ["industriverse", f"industriverse-{sync_request.industriverse_workflow_id}"]
                }
                
                # Create or update workflow in n8n
                if sync_request.n8n_workflow_id:
                    # Update existing workflow
                    success = await self.connector.update_workflow(sync_request.n8n_workflow_id, workflow_data)
                    
                    if not success:
                        # Workflow not found, create a new one
                        sync_request.n8n_workflow_id = await self.connector.create_workflow(workflow_data)
                        logger.info(f"Created new workflow in n8n: {sync_request.n8n_workflow_id}")
                    else:
                        logger.info(f"Updated workflow in n8n: {sync_request.n8n_workflow_id}")
                else:
                    # Create new workflow
                    sync_request.n8n_workflow_id = await self.connector.create_workflow(workflow_data)
                    logger.info(f"Created new workflow in n8n: {sync_request.n8n_workflow_id}")
            
            # Sync from n8n
            if sync_request.sync_direction in ["from_n8n", "bidirectional"] and sync_request.n8n_workflow_id:
                # Get workflow from n8n
                workflow = await self.connector.get_workflow(sync_request.n8n_workflow_id)
                
                if workflow:
                    # Update sync request with workflow data
                    sync_request.name = workflow.name
                    sync_request.nodes = workflow.nodes
                    sync_request.connections = workflow.connections
                    
                    logger.info(f"Synced workflow from n8n: {sync_request.n8n_workflow_id}")
                else:
                    logger.warning(f"Workflow not found in n8n: {sync_request.n8n_workflow_id}")
            
            # Return the sync result
            return {
                "success": True,
                "industriverse_workflow_id": sync_request.industriverse_workflow_id,
                "n8n_workflow_id": sync_request.n8n_workflow_id,
                "name": sync_request.name,
                "sync_direction": sync_request.sync_direction,
                "timestamp": datetime.now().isoformat()
            }
        
        except ValueError as e:
            logger.error(f"Invalid sync request: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        except Exception as e:
            logger.error(f"Error syncing workflow: {e}")
            raise HTTPException(status_code=500, detail=f"Error syncing workflow: {str(e)}")
    
    def _handle_webhook_callback(self, webhook_id: str, data: Dict[str, Any]):
        """
        Handle a webhook callback from the n8n connector.
        
        Args:
            webhook_id: The ID of the webhook
            data: The webhook payload
        """
        # Call the webhook callback if registered
        if self.on_webhook_received:
            try:
                self.on_webhook_received(webhook_id, data)
            except Exception as e:
                logger.error(f"Error in webhook callback: {e}")
    
    def get_app(self) -> FastAPI:
        """
        Get the FastAPI application.
        
        Returns:
            The FastAPI application
        """
        return self.app
"""
