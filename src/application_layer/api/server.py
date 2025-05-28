"""
API Server for the Industriverse Application Layer.

This module provides the API server for the Application Layer,
exposing protocol-native interfaces for external access.
"""

import logging
import json
import time
import uuid
import os
from typing import Dict, Any, List, Optional, Union, Callable

from fastapi import FastAPI, Request, Response, HTTPException, Depends, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class APIServer:
    """
    API Server for the Industriverse Application Layer.
    """
    
    def __init__(self, agent_core, config: Dict[str, Any] = None):
        """
        Initialize the API Server.
        
        Args:
            agent_core: Reference to the agent core
            config: Server configuration
        """
        self.agent_core = agent_core
        self.config = config or {}
        self.app = FastAPI(
            title="Industriverse Application Layer API",
            description="API for the Industriverse Application Layer with protocol-native interfaces",
            version="1.0.0"
        )
        self.server = None
        self.running = False
        
        # Configure CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.get("cors_origins", ["*"]),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Register with agent core
        self.agent_core.register_component("api_server", self)
        
        # Initialize routes
        self._initialize_routes()
        
        logger.info("API Server initialized")
    
    def _initialize_routes(self):
        """
        Initialize API routes.
        """
        # Health check endpoint
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": time.time()}
        
        # Well-known endpoint for discovery
        @self.app.get("/.well-known/ai-plugin.json")
        async def well_known():
            well_known_endpoint = self.agent_core.get_component("well_known_endpoint")
            if well_known_endpoint:
                return well_known_endpoint.get_plugin_manifest()
            else:
                return HTTPException(status_code=503, detail="Well-known endpoint not available")
        
        # MCP protocol endpoints
        @self.app.post("/mcp/event")
        async def mcp_event(request: Request):
            try:
                event_data = await request.json()
                mcp_handler = self.agent_core.get_component("mcp_handler")
                if mcp_handler:
                    result = mcp_handler.handle_event(event_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="MCP handler not available")
            except Exception as e:
                logger.error(f"Error handling MCP event: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/mcp/status")
        async def mcp_status():
            mcp_handler = self.agent_core.get_component("mcp_handler")
            if mcp_handler:
                return mcp_handler.get_status()
            else:
                return HTTPException(status_code=503, detail="MCP handler not available")
        
        # A2A protocol endpoints
        @self.app.post("/a2a/invoke")
        async def a2a_invoke(request: Request):
            try:
                invoke_data = await request.json()
                a2a_handler = self.agent_core.get_component("a2a_handler")
                if a2a_handler:
                    result = a2a_handler.handle_invoke(invoke_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="A2A handler not available")
            except Exception as e:
                logger.error(f"Error handling A2A invoke: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/a2a/agent-card")
        async def a2a_agent_card():
            a2a_handler = self.agent_core.get_component("a2a_handler")
            if a2a_handler:
                return a2a_handler.get_agent_card()
            else:
                return HTTPException(status_code=503, detail="A2A handler not available")
        
        @self.app.get("/a2a/capabilities")
        async def a2a_capabilities():
            a2a_handler = self.agent_core.get_component("a2a_handler")
            if a2a_handler:
                return a2a_handler.get_capabilities()
            else:
                return HTTPException(status_code=503, detail="A2A handler not available")
        
        # Application Avatar Interface endpoints
        @self.app.get("/avatar/{avatar_id}")
        async def get_avatar(avatar_id: str):
            avatar_interface = self.agent_core.get_component("application_avatar_interface")
            if avatar_interface:
                avatar = avatar_interface.get_avatar(avatar_id)
                if avatar:
                    return avatar
                else:
                    return HTTPException(status_code=404, detail=f"Avatar not found: {avatar_id}")
            else:
                return HTTPException(status_code=503, detail="Avatar interface not available")
        
        @self.app.post("/avatar")
        async def create_avatar(request: Request):
            try:
                avatar_data = await request.json()
                avatar_interface = self.agent_core.get_component("application_avatar_interface")
                if avatar_interface:
                    result = avatar_interface.create_avatar(avatar_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Avatar interface not available")
            except Exception as e:
                logger.error(f"Error creating avatar: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/avatar/{avatar_id}")
        async def update_avatar(avatar_id: str, request: Request):
            try:
                avatar_data = await request.json()
                avatar_interface = self.agent_core.get_component("application_avatar_interface")
                if avatar_interface:
                    result = avatar_interface.update_avatar(avatar_id, avatar_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Avatar interface not available")
            except Exception as e:
                logger.error(f"Error updating avatar: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        # Universal Skin / Dynamic Agent Capsules endpoints
        @self.app.get("/capsule/{capsule_id}")
        async def get_capsule(capsule_id: str):
            capsule_factory = self.agent_core.get_component("agent_capsule_factory")
            if capsule_factory:
                capsule = capsule_factory.get_capsule(capsule_id)
                if capsule:
                    return capsule
                else:
                    return HTTPException(status_code=404, detail=f"Capsule not found: {capsule_id}")
            else:
                return HTTPException(status_code=503, detail="Capsule factory not available")
        
        @self.app.post("/capsule")
        async def create_capsule(request: Request):
            try:
                capsule_data = await request.json()
                capsule_factory = self.agent_core.get_component("agent_capsule_factory")
                if capsule_factory:
                    result = capsule_factory.create_capsule(capsule_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Capsule factory not available")
            except Exception as e:
                logger.error(f"Error creating capsule: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/capsule/{capsule_id}/action/{action_id}")
        async def capsule_action(capsule_id: str, action_id: str, request: Request):
            try:
                action_data = await request.json()
                interaction_handler = self.agent_core.get_component("capsule_interaction_handler")
                if interaction_handler:
                    result = interaction_handler.handle_action(capsule_id, action_id, action_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Interaction handler not available")
            except Exception as e:
                logger.error(f"Error handling capsule action: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        # Digital Twin endpoints
        @self.app.get("/digital-twin/{twin_id}")
        async def get_digital_twin(twin_id: str):
            digital_twin = self.agent_core.get_component("digital_twin_components")
            if digital_twin:
                twin = digital_twin.get_digital_twin(twin_id)
                if twin:
                    return twin
                else:
                    return HTTPException(status_code=404, detail=f"Digital twin not found: {twin_id}")
            else:
                return HTTPException(status_code=503, detail="Digital twin components not available")
        
        @self.app.post("/digital-twin")
        async def create_digital_twin(request: Request):
            try:
                twin_data = await request.json()
                digital_twin = self.agent_core.get_component("digital_twin_components")
                if digital_twin:
                    result = digital_twin.create_digital_twin(twin_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Digital twin components not available")
            except Exception as e:
                logger.error(f"Error creating digital twin: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/digital-twin/{twin_id}/telemetry")
        async def update_twin_telemetry(twin_id: str, request: Request):
            try:
                telemetry_data = await request.json()
                digital_twin = self.agent_core.get_component("digital_twin_components")
                if digital_twin:
                    result = digital_twin.update_telemetry(twin_id, telemetry_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Digital twin components not available")
            except Exception as e:
                logger.error(f"Error updating twin telemetry: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        # Workflow endpoints
        @self.app.get("/workflow/template/{template_id}")
        async def get_workflow_template(template_id: str):
            workflow = self.agent_core.get_component("workflow_orchestration")
            if workflow:
                templates = workflow.get_workflow_templates()
                for template in templates:
                    if template.get("template_id") == template_id:
                        return template
                return HTTPException(status_code=404, detail=f"Workflow template not found: {template_id}")
            else:
                return HTTPException(status_code=503, detail="Workflow orchestration not available")
        
        @self.app.post("/workflow/template")
        async def register_workflow_template(request: Request):
            try:
                template_data = await request.json()
                workflow = self.agent_core.get_component("workflow_orchestration")
                if workflow:
                    result = workflow.register_workflow_template(template_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Workflow orchestration not available")
            except Exception as e:
                logger.error(f"Error registering workflow template: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/workflow/instance")
        async def create_workflow_instance(request: Request):
            try:
                instance_data = await request.json()
                workflow = self.agent_core.get_component("workflow_orchestration")
                if workflow:
                    result = workflow.create_workflow_instance(
                        instance_data.get("template_id", ""),
                        instance_data.get("instance_config", {})
                    )
                    return result
                else:
                    return HTTPException(status_code=503, detail="Workflow orchestration not available")
            except Exception as e:
                logger.error(f"Error creating workflow instance: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/workflow/execute")
        async def execute_workflow(request: Request):
            try:
                execution_data = await request.json()
                workflow = self.agent_core.get_component("workflow_orchestration")
                if workflow:
                    result = workflow.execute_workflow(
                        execution_data.get("instance_id", ""),
                        execution_data.get("execution_config", {})
                    )
                    return result
                else:
                    return HTTPException(status_code=503, detail="Workflow orchestration not available")
            except Exception as e:
                logger.error(f"Error executing workflow: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        # Industry-specific module endpoints
        @self.app.get("/industry-module/{module_id}")
        async def get_industry_module(module_id: str):
            industry_modules = self.agent_core.get_component("industry_specific_modules")
            if industry_modules:
                module = industry_modules.get_module(module_id)
                if module:
                    return module
                else:
                    return HTTPException(status_code=404, detail=f"Industry module not found: {module_id}")
            else:
                return HTTPException(status_code=503, detail="Industry modules not available")
        
        @self.app.post("/industry-module/{module_id}/action/{action_id}")
        async def industry_module_action(module_id: str, action_id: str, request: Request):
            try:
                action_data = await request.json()
                industry_modules = self.agent_core.get_component("industry_specific_modules")
                if industry_modules:
                    result = industry_modules.handle_action(module_id, action_id, action_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Industry modules not available")
            except Exception as e:
                logger.error(f"Error handling industry module action: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        # Omniverse integration endpoints
        @self.app.post("/omniverse/connect")
        async def connect_to_omniverse(request: Request):
            try:
                connection_data = await request.json()
                omniverse = self.agent_core.get_component("omniverse_integration_services")
                if omniverse:
                    result = omniverse.connect_to_omniverse(connection_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="Omniverse integration not available")
            except Exception as e:
                logger.error(f"Error connecting to Omniverse: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/omniverse/scene")
        async def create_omniverse_scene(request: Request):
            try:
                scene_data = await request.json()
                omniverse = self.agent_core.get_component("omniverse_integration_services")
                if omniverse:
                    result = omniverse.create_omniverse_scene(
                        scene_data.get("connection_id", ""),
                        scene_data.get("scene_config", {})
                    )
                    return result
                else:
                    return HTTPException(status_code=503, detail="Omniverse integration not available")
            except Exception as e:
                logger.error(f"Error creating Omniverse scene: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        # UI component system endpoints
        @self.app.get("/ui/component/{component_id}")
        async def get_ui_component(component_id: str):
            ui_system = self.agent_core.get_component("application_ui_component_system")
            if ui_system:
                component = ui_system.get_ui_component(component_id)
                if component:
                    return component
                else:
                    return HTTPException(status_code=404, detail=f"UI component not found: {component_id}")
            else:
                return HTTPException(status_code=503, detail="UI component system not available")
        
        @self.app.post("/ui/component")
        async def register_ui_component(request: Request):
            try:
                component_data = await request.json()
                ui_system = self.agent_core.get_component("application_ui_component_system")
                if ui_system:
                    result = ui_system.register_ui_component(component_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="UI component system not available")
            except Exception as e:
                logger.error(f"Error registering UI component: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/ui/event")
        async def handle_ui_event(request: Request):
            try:
                event_data = await request.json()
                ui_system = self.agent_core.get_component("application_ui_component_system")
                if ui_system:
                    result = ui_system.handle_ui_event(event_data)
                    return result
                else:
                    return HTTPException(status_code=503, detail="UI component system not available")
            except Exception as e:
                logger.error(f"Error handling UI event: {e}")
                return HTTPException(status_code=500, detail=str(e))
        
        # Component status endpoints
        @self.app.get("/component/{component_id}/status")
        async def get_component_status(component_id: str):
            component = self.agent_core.get_component(component_id)
            if component:
                if hasattr(component, "get_status") and callable(component.get_status):
                    return component.get_status()
                else:
                    return {"status": "unknown", "error": "Component does not support status"}
            else:
                return HTTPException(status_code=404, detail=f"Component not found: {component_id}")
        
        # Component action endpoints
        @self.app.post("/component/{component_id}/action/{action_id}")
        async def handle_component_action(component_id: str, action_id: str, request: Request):
            try:
                action_data = await request.json()
                component = self.agent_core.get_component(component_id)
                if component:
                    if hasattr(component, "handle_action") and callable(component.handle_action):
                        result = component.handle_action(action_id, action_data)
                        return result
                    else:
                        return HTTPException(status_code=400, detail=f"Component does not support actions: {component_id}")
                else:
                    return HTTPException(status_code=404, detail=f"Component not found: {component_id}")
            except Exception as e:
                logger.error(f"Error handling component action: {e}")
                return HTTPException(status_code=500, detail=str(e))
    
    def start(self):
        """
        Start the API server.
        """
        if self.running:
            logger.warning("API Server already running")
            return
        
        # Get server configuration
        host = self.config.get("host", "0.0.0.0")
        port = self.config.get("port", 8000)
        
        # Start server in a separate thread
        import threading
        self.server_thread = threading.Thread(
            target=uvicorn.run,
            args=(self.app,),
            kwargs={
                "host": host,
                "port": port,
                "log_level": "info"
            },
            daemon=True
        )
        self.server_thread.start()
        
        self.running = True
        logger.info(f"API Server started on {host}:{port}")
    
    def stop(self):
        """
        Stop the API server.
        """
        if not self.running:
            logger.warning("API Server not running")
            return
        
        # In a real implementation, we would stop the uvicorn server
        # For now, we'll just mark it as stopped
        self.running = False
        logger.info("API Server stopped")
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get component information.
        
        Returns:
            Component information
        """
        return {
            "id": "api_server",
            "type": "APIServer",
            "name": "API Server",
            "status": "running" if self.running else "stopped",
            "host": self.config.get("host", "0.0.0.0"),
            "port": self.config.get("port", 8000)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get component status.
        
        Returns:
            Component status
        """
        return {
            "status": "operational" if self.running else "stopped",
            "uptime": time.time() - self.agent_core.start_time if self.running else 0,
            "host": self.config.get("host", "0.0.0.0"),
            "port": self.config.get("port", 8000)
        }
