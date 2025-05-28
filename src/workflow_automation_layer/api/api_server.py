"""
API Server Module for the Workflow Automation Layer.

This module provides the REST API endpoints for interacting with the
Workflow Automation Layer, including workflow management, task execution,
and integration with other layers.
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Depends, Header, Request, Response, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIServer:
    """API Server for the Workflow Automation Layer."""

    def __init__(self, components: Dict[str, Any], config: Dict[str, Any]):
        """Initialize the API server.

        Args:
            components: Dictionary of workflow automation components.
            config: Configuration dictionary.
        """
        self.components = components
        self.config = config
        self.app = FastAPI(
            title="Workflow Automation Layer API",
            description="API for the Industriverse Workflow Automation Layer",
            version="1.0.0"
        )
        self.server = None
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # In production, restrict to specific origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register API routes."""
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "service": "workflow-automation-layer"}
        
        # Workflow management endpoints
        @self.app.post("/api/workflows")
        async def create_workflow(request: Request):
            workflow_data = await request.json()
            workflow_registry = self.components["workflow_registry"]
            result = workflow_registry.register_workflow(workflow_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        @self.app.get("/api/workflows")
        async def list_workflows():
            workflow_registry = self.components["workflow_registry"]
            return {"workflows": workflow_registry.list_workflows()}
        
        @self.app.get("/api/workflows/{workflow_id}")
        async def get_workflow(workflow_id: str):
            workflow_registry = self.components["workflow_registry"]
            workflow = workflow_registry.get_workflow(workflow_id)
            if workflow:
                return workflow
            else:
                raise HTTPException(status_code=404, detail="Workflow not found")
        
        @self.app.put("/api/workflows/{workflow_id}")
        async def update_workflow(workflow_id: str, request: Request):
            workflow_data = await request.json()
            workflow_registry = self.components["workflow_registry"]
            result = workflow_registry.update_workflow(workflow_id, workflow_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        @self.app.delete("/api/workflows/{workflow_id}")
        async def delete_workflow(workflow_id: str):
            workflow_registry = self.components["workflow_registry"]
            result = workflow_registry.delete_workflow(workflow_id)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=404, detail=result["error"])
        
        # Workflow execution endpoints
        @self.app.post("/api/workflows/{workflow_id}/start")
        async def start_workflow(workflow_id: str, request: Request):
            input_data = await request.json()
            workflow_runtime = self.components["workflow_runtime"]
            result = await workflow_runtime.start_workflow(workflow_id, input_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        @self.app.post("/api/workflows/{workflow_id}/stop")
        async def stop_workflow(workflow_id: str):
            workflow_runtime = self.components["workflow_runtime"]
            result = await workflow_runtime.stop_workflow(workflow_id)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        @self.app.get("/api/workflows/{workflow_id}/status")
        async def get_workflow_status(workflow_id: str):
            workflow_runtime = self.components["workflow_runtime"]
            status = workflow_runtime.get_workflow_status(workflow_id)
            if status:
                return status
            else:
                raise HTTPException(status_code=404, detail="Workflow not found or not running")
        
        # Task management endpoints
        @self.app.post("/api/workflows/{workflow_id}/tasks/{task_id}/complete")
        async def complete_task(workflow_id: str, task_id: str, request: Request):
            result_data = await request.json()
            workflow_runtime = self.components["workflow_runtime"]
            result = await workflow_runtime.complete_task(workflow_id, task_id, result_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        @self.app.post("/api/workflows/{workflow_id}/tasks/{task_id}/fail")
        async def fail_task(workflow_id: str, task_id: str, request: Request):
            error_data = await request.json()
            workflow_runtime = self.components["workflow_runtime"]
            result = await workflow_runtime.fail_task(workflow_id, task_id, error_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        # Human intervention endpoints
        @self.app.post("/api/interventions")
        async def request_intervention(request: Request):
            intervention_data = await request.json()
            human_agent = self.components["human_agent"]
            result = await human_agent.request_intervention(intervention_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        @self.app.get("/api/interventions")
        async def list_interventions():
            human_agent = self.components["human_agent"]
            return {"interventions": human_agent.list_interventions()}
        
        @self.app.get("/api/interventions/{intervention_id}")
        async def get_intervention(intervention_id: str):
            human_agent = self.components["human_agent"]
            intervention = human_agent.get_intervention(intervention_id)
            if intervention:
                return intervention
            else:
                raise HTTPException(status_code=404, detail="Intervention not found")
        
        @self.app.post("/api/interventions/{intervention_id}/respond")
        async def respond_to_intervention(intervention_id: str, request: Request):
            response_data = await request.json()
            human_agent = self.components["human_agent"]
            result = await human_agent.process_intervention_response({
                "intervention_id": intervention_id,
                **response_data
            })
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        # n8n integration endpoints
        @self.app.post("/api/n8n/webhook")
        async def n8n_webhook(request: Request):
            webhook_data = await request.json()
            n8n_bridge_service = self.components["n8n_bridge_service"]
            result = await n8n_bridge_service.handle_n8n_webhook(webhook_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        @self.app.post("/api/n8n/sync/{workflow_id}")
        async def sync_workflow_to_n8n(workflow_id: str):
            n8n_bridge_service = self.components["n8n_bridge_service"]
            result = await n8n_bridge_service.sync_workflow_to_n8n(workflow_id)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        # Visualization endpoints
        @self.app.get("/api/visualizations/workflows/{workflow_id}/graph")
        async def get_workflow_graph(workflow_id: str):
            workflow_visualization = self.components["workflow_visualization"]
            graph = workflow_visualization.generate_workflow_graph(workflow_id)
            if graph:
                return graph
            else:
                raise HTTPException(status_code=404, detail="Workflow not found")
        
        @self.app.get("/api/visualizations/workflows/{workflow_id}/timeline")
        async def get_workflow_timeline(workflow_id: str):
            workflow_visualization = self.components["workflow_visualization"]
            timeline = workflow_visualization.generate_workflow_timeline(workflow_id)
            if timeline:
                return timeline
            else:
                raise HTTPException(status_code=404, detail="Workflow not found or no execution history")
        
        # Dynamic Agent Capsule endpoints
        @self.app.get("/api/capsules")
        async def list_capsules():
            capsule_controller = self.components["capsule_controller"]
            return {"capsules": capsule_controller.list_capsules()}
        
        @self.app.get("/api/capsules/{capsule_id}")
        async def get_capsule(capsule_id: str):
            capsule_controller = self.components["capsule_controller"]
            capsule = capsule_controller.get_capsule(capsule_id)
            if capsule:
                return capsule.render()
            else:
                raise HTTPException(status_code=404, detail="Capsule not found")
        
        @self.app.post("/api/capsules/{capsule_id}/actions/{action_id}")
        async def execute_capsule_action(capsule_id: str, action_id: str, request: Request):
            action_data = await request.json()
            capsule_controller = self.components["capsule_controller"]
            result = await capsule_controller.execute_action(capsule_id, action_id, action_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        # Protocol Layer integration endpoints
        @self.app.post("/api/protocol/messages")
        async def handle_protocol_message(request: Request):
            message_data = await request.json()
            integration_manager = self.components["integration_manager"]
            result = await integration_manager.protocol_layer.receive_message(message_data)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])
        
        @self.app.get("/api/system/health")
        async def check_system_health():
            integration_manager = self.components["integration_manager"]
            health_result = await integration_manager.check_system_health()
            return health_result
        
        # Template management endpoints
        @self.app.get("/api/templates")
        async def list_templates():
            workflow_registry = self.components["workflow_registry"]
            return {"templates": workflow_registry.list_templates()}
        
        @self.app.get("/api/templates/{template_id}")
        async def get_template(template_id: str):
            workflow_registry = self.components["workflow_registry"]
            template = workflow_registry.get_template(template_id)
            if template:
                return template
            else:
                raise HTTPException(status_code=404, detail="Template not found")
        
        @self.app.post("/api/templates/{template_id}/instantiate")
        async def instantiate_template(template_id: str, request: Request):
            params = await request.json()
            workflow_registry = self.components["workflow_registry"]
            result = workflow_registry.instantiate_template(template_id, params)
            if result["success"]:
                return result
            else:
                raise HTTPException(status_code=400, detail=result["error"])

    async def start(self, host: str = "0.0.0.0", port: int = 8080):
        """Start the API server.

        Args:
            host: Host to bind to.
            port: Port to bind to.
        """
        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level=self.config.get("log_level", "info").lower()
        )
        self.server = uvicorn.Server(config)
        
        # Start the server in a background task
        self.server_task = asyncio.create_task(self.server.serve())
        logger.info(f"API server started on {host}:{port}")

    async def stop(self):
        """Stop the API server."""
        if self.server:
            self.server.should_exit = True
            await self.server_task
            logger.info("API server stopped")


async def create_api_server(components: Dict[str, Any], config: Dict[str, Any]) -> APIServer:
    """Create and initialize the API server.

    Args:
        components: Dictionary of workflow automation components.
        config: Configuration dictionary.

    Returns:
        Initialized API server instance.
    """
    api_server = APIServer(components, config)
    return api_server
