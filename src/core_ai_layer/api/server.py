"""
API Server for Industriverse Core AI Layer

This module implements the API server for the Core AI Layer,
providing HTTP and gRPC endpoints for interacting with the layer.
"""

import os
import logging
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import grpc
import grpc.aio

# Configure logging
logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

class APIServer:
    """
    API Server for Core AI Layer.
    """
    
    def __init__(self, agent_core, protocol_translator, mesh_boot_lifecycle, 
                observability_agent, model_feedback_loop, mesh_workload_router):
        """
        Initialize the API server.
        
        Args:
            agent_core: Agent core instance
            protocol_translator: Protocol translator instance
            mesh_boot_lifecycle: Mesh boot lifecycle instance
            observability_agent: Observability agent instance
            model_feedback_loop: Model feedback loop instance
            mesh_workload_router: Mesh workload router instance
        """
        self.agent_core = agent_core
        self.protocol_translator = protocol_translator
        self.mesh_boot_lifecycle = mesh_boot_lifecycle
        self.observability_agent = observability_agent
        self.model_feedback_loop = model_feedback_loop
        self.mesh_workload_router = mesh_workload_router
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Industriverse Core AI Layer API",
            description="API for interacting with the Industriverse Core AI Layer",
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
        
        # Initialize gRPC server
        self.grpc_server = grpc.aio.server()
        
        # Register routes
        self._register_routes()
        
        # Initialize state
        self.running = False
    
    def _register_routes(self):
        """
        Register API routes.
        """
        # Health check routes
        @self.app.get("/health/live")
        async def liveness():
            return {"status": "alive"}
        
        @self.app.get("/health/ready")
        async def readiness():
            # Check if all components are ready
            if not self.agent_core or not self.protocol_translator:
                return Response(status_code=503)
            return {"status": "ready"}
        
        @self.app.get("/health/startup")
        async def startup():
            # Check if startup is complete
            if not self.mesh_boot_lifecycle or not self.mesh_boot_lifecycle.is_started():
                return Response(status_code=503)
            return {"status": "started"}
        
        @self.app.get("/health")
        async def health():
            try:
                # Get health status from all components
                agent_core_health = await self.agent_core.health_check()
                protocol_translator_health = await self.protocol_translator.health_check()
                mesh_boot_lifecycle_health = await self.mesh_boot_lifecycle.health_check()
                observability_health = await self.observability_agent.health_check()
                
                # Determine overall health
                all_healthy = (
                    agent_core_health.get("status") == "healthy" and
                    protocol_translator_health.get("status") == "healthy" and
                    mesh_boot_lifecycle_health.get("status") == "healthy" and
                    observability_health.get("status") == "healthy"
                )
                
                status = "healthy" if all_healthy else "unhealthy"
                
                return {
                    "status": status,
                    "components": {
                        "agent_core": agent_core_health,
                        "protocol_translator": protocol_translator_health,
                        "mesh_boot_lifecycle": mesh_boot_lifecycle_health,
                        "observability": observability_health
                    }
                }
            except Exception as e:
                logger.error(f"Error checking health: {e}")
                return Response(status_code=500)
        
        # Protocol routes
        @self.app.post("/protocol/translate")
        async def translate_protocol(request: Dict[str, Any]):
            try:
                source_protocol = request.get("source_protocol")
                target_protocol = request.get("target_protocol")
                message = request.get("message")
                
                if not source_protocol or not target_protocol or not message:
                    raise HTTPException(status_code=400, detail="Missing required parameters")
                
                result = await self.protocol_translator.translate(
                    source_protocol=source_protocol,
                    target_protocol=target_protocol,
                    message=message
                )
                
                return result
            except Exception as e:
                logger.error(f"Error translating protocol: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/protocol/supported")
        async def supported_protocols():
            try:
                protocols = await self.protocol_translator.get_supported_protocols()
                return {"protocols": protocols}
            except Exception as e:
                logger.error(f"Error getting supported protocols: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Agent routes
        @self.app.post("/agent/register")
        async def register_agent(request: Dict[str, Any]):
            try:
                agent_id = request.get("agent_id")
                agent_type = request.get("agent_type")
                capabilities = request.get("capabilities")
                
                if not agent_id or not agent_type:
                    raise HTTPException(status_code=400, detail="Missing required parameters")
                
                result = await self.agent_core.register_agent(
                    agent_id=agent_id,
                    agent_type=agent_type,
                    capabilities=capabilities
                )
                
                return result
            except Exception as e:
                logger.error(f"Error registering agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agent/{agent_id}")
        async def get_agent(agent_id: str):
            try:
                agent = await self.agent_core.get_agent(agent_id)
                
                if not agent:
                    raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
                
                return agent
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents")
        async def list_agents():
            try:
                agents = await self.agent_core.list_agents()
                return {"agents": agents}
            except Exception as e:
                logger.error(f"Error listing agents: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Mesh routes
        @self.app.get("/mesh/status")
        async def mesh_status():
            try:
                status = await self.mesh_boot_lifecycle.get_status()
                return status
            except Exception as e:
                logger.error(f"Error getting mesh status: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/mesh/join")
        async def join_mesh(request: Dict[str, Any]):
            try:
                mesh_id = request.get("mesh_id")
                agent_id = request.get("agent_id")
                
                if not mesh_id or not agent_id:
                    raise HTTPException(status_code=400, detail="Missing required parameters")
                
                result = await self.mesh_boot_lifecycle.join_mesh(
                    mesh_id=mesh_id,
                    agent_id=agent_id
                )
                
                return result
            except Exception as e:
                logger.error(f"Error joining mesh: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/mesh/leave")
        async def leave_mesh(request: Dict[str, Any]):
            try:
                mesh_id = request.get("mesh_id")
                agent_id = request.get("agent_id")
                
                if not mesh_id or not agent_id:
                    raise HTTPException(status_code=400, detail="Missing required parameters")
                
                result = await self.mesh_boot_lifecycle.leave_mesh(
                    mesh_id=mesh_id,
                    agent_id=agent_id
                )
                
                return result
            except Exception as e:
                logger.error(f"Error leaving mesh: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Workload routes
        @self.app.post("/workload/route")
        async def route_workload(request: Dict[str, Any]):
            try:
                workload_id = request.get("workload_id")
                workload_type = request.get("workload_type")
                requirements = request.get("requirements")
                
                if not workload_id or not workload_type:
                    raise HTTPException(status_code=400, detail="Missing required parameters")
                
                result = await self.mesh_workload_router.route_workload(
                    workload_id=workload_id,
                    workload_type=workload_type,
                    requirements=requirements
                )
                
                return result
            except Exception as e:
                logger.error(f"Error routing workload: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/workload/{workload_id}")
        async def get_workload(workload_id: str):
            try:
                workload = await self.mesh_workload_router.get_workload(workload_id)
                
                if not workload:
                    raise HTTPException(status_code=404, detail=f"Workload {workload_id} not found")
                
                return workload
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting workload: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Observability routes
        @self.app.get("/metrics")
        async def get_metrics():
            try:
                metrics = await self.observability_agent.get_metrics()
                return metrics
            except Exception as e:
                logger.error(f"Error getting metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/feedback")
        async def submit_feedback(request: Dict[str, Any]):
            try:
                model_id = request.get("model_id")
                feedback_type = request.get("feedback_type")
                feedback_data = request.get("feedback_data")
                
                if not model_id or not feedback_type or not feedback_data:
                    raise HTTPException(status_code=400, detail="Missing required parameters")
                
                result = await self.model_feedback_loop.submit_feedback(
                    model_id=model_id,
                    feedback_type=feedback_type,
                    feedback_data=feedback_data
                )
                
                return result
            except Exception as e:
                logger.error(f"Error submitting feedback: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def start(self) -> bool:
        """
        Start the API server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.running:
                logger.warning("API server is already running")
                return True
            
            # Start FastAPI server
            import uvicorn
            
            config = uvicorn.Config(
                app=self.app,
                host="0.0.0.0",
                port=8080,
                log_level="info"
            )
            
            server = uvicorn.Server(config)
            
            # Start in a separate task
            self.server_task = asyncio.create_task(server.serve())
            
            # Start gRPC server
            await self.grpc_server.start()
            
            self.running = True
            logger.info("API server started successfully")
            return True
        except Exception as e:
            logger.error(f"Error starting API server: {e}")
            return False
    
    async def stop(self) -> bool:
        """
        Stop the API server.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.running:
                logger.warning("API server is not running")
                return True
            
            # Stop gRPC server
            await self.grpc_server.stop(0)
            
            # Cancel FastAPI server task
            if hasattr(self, "server_task"):
                self.server_task.cancel()
                try:
                    await self.server_task
                except asyncio.CancelledError:
                    pass
            
            self.running = False
            logger.info("API server stopped successfully")
            return True
        except Exception as e:
            logger.error(f"Error stopping API server: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check.
        
        Returns:
            Health check results
        """
        return {
            "status": "healthy" if self.running else "unhealthy",
            "running": self.running
        }
