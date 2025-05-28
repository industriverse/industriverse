"""
Deployment Operations Layer Orchestration API

This module provides a RESTful API for orchestrating deployment operations
across the Industriverse ecosystem.
"""

import os
import sys
import json
import logging
import uuid
import datetime
import time
from typing import Dict, List, Optional, Any, Union

from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('deployment_ops_api')

# Import execution engine components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from execution.execution_engine import (
    ExecutionEngine, Mission, MissionStatus, MissionType,
    create_execution_engine
)

# Import other required components
from agent.mission_planner import MissionPlanner
from agent.mission_executor import MissionExecutor
from agent.error_handler import ErrorHandler
from agent.recovery_manager import RecoveryManager
from simulation.simulation_engine import SimulationEngine
from integration.layer_integration_manager import LayerIntegrationManager
from integration.cross_layer_integration_manager import CrossLayerIntegrationManager

# Pydantic models for API requests and responses
class MissionRequest(BaseModel):
    """Request model for creating a new mission"""
    mission_type: str = Field(..., description="Type of mission (deploy, update, rollback, etc.)")
    priority: int = Field(5, ge=1, le=10, description="Priority of the mission (1-10, 1 being highest)")
    target_layers: List[str] = Field(..., description="List of target layers for the mission")
    configuration: Dict[str, Any] = Field(..., description="Mission configuration")
    simulation_required: bool = Field(True, description="Whether simulation is required before execution")
    rollback_on_failure: bool = Field(True, description="Whether to automatically rollback on failure")
    timeout_seconds: Optional[int] = Field(None, description="Timeout in seconds (None for no timeout)")
    description: Optional[str] = Field(None, description="Description of the mission")
    
    @validator('mission_type')
    def validate_mission_type(cls, v):
        valid_types = [
            MissionType.DEPLOY, MissionType.UPDATE, MissionType.ROLLBACK,
            MissionType.SCALE, MissionType.MIGRATE, MissionType.BACKUP,
            MissionType.RESTORE, MissionType.HEALTH_CHECK, MissionType.SECURITY_SCAN,
            MissionType.COMPLIANCE_CHECK
        ]
        if v not in valid_types:
            raise ValueError(f"Invalid mission type. Must be one of: {', '.join(valid_types)}")
        return v
    
    @validator('target_layers')
    def validate_target_layers(cls, v):
        valid_layers = [
            "data-layer", "core-ai-layer", "generative-layer", "application-layer",
            "protocol-layer", "workflow-layer", "ui-ux-layer", "security-compliance-layer",
            "deployment-ops-layer", "native-app-layer"
        ]
        for layer in v:
            if layer not in valid_layers:
                raise ValueError(f"Invalid layer: {layer}. Must be one of: {', '.join(valid_layers)}")
        return v

class MissionResponse(BaseModel):
    """Response model for mission operations"""
    mission_id: str
    status: str
    message: str

class MissionDetailResponse(BaseModel):
    """Response model for detailed mission information"""
    mission_id: str
    type: str
    status: str
    priority: int
    timestamp: str
    engine_id: Optional[str]
    target_layers: List[str]
    configuration: Dict[str, Any]
    simulation_required: bool
    rollback_on_failure: bool
    timeout_seconds: Optional[int]
    description: Optional[str]
    planning_started_at: Optional[str]
    planning_completed_at: Optional[str]
    simulation_started_at: Optional[str]
    simulation_completed_at: Optional[str]
    execution_started_at: Optional[str]
    execution_completed_at: Optional[str]
    succeeded_at: Optional[str]
    failed_at: Optional[str]
    canceled_at: Optional[str]
    paused_at: Optional[str]
    resumed_at: Optional[str]
    rollback_started_at: Optional[str]
    rollback_completed_at: Optional[str]
    error: Optional[str]
    plan_summary: Optional[str]
    simulation_summary: Optional[str]
    execution_summary: Optional[str]
    timeline: List[Dict[str, Any]]
    resources: Dict[str, List[Dict[str, Any]]]
    capsules: List[Dict[str, Any]]
    layers: List[Dict[str, Any]]
    validation_results: Dict[str, List[Dict[str, Any]]]

class MissionListResponse(BaseModel):
    """Response model for listing missions"""
    missions: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int

class EngineStatusResponse(BaseModel):
    """Response model for engine status"""
    is_running: bool
    queue_size: int
    active_mission_count: int
    worker_count: int
    active_worker_count: int
    uptime_seconds: Optional[int]
    version: str

class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str
    detail: Optional[str] = None

# Create FastAPI app
app = FastAPI(
    title="Deployment Operations API",
    description="API for orchestrating deployment operations across the Industriverse ecosystem",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
mission_planner = MissionPlanner()
simulation_engine = SimulationEngine()
mission_executor = MissionExecutor()
error_handler = ErrorHandler()
recovery_manager = RecoveryManager()
layer_integration_manager = LayerIntegrationManager()
cross_layer_integration_manager = CrossLayerIntegrationManager()

# Create execution engine
execution_engine = create_execution_engine(
    mission_planner,
    simulation_engine,
    mission_executor,
    error_handler,
    recovery_manager,
    worker_count=5
)

# Start the execution engine on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Deployment Operations API")
    execution_engine.start()

# Stop the execution engine on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Deployment Operations API")
    execution_engine.stop()

# API endpoints
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "name": "Deployment Operations API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/status", response_model=EngineStatusResponse, tags=["Engine"])
async def get_engine_status():
    """Get the status of the execution engine"""
    return execution_engine.get_status()

@app.post("/missions", response_model=MissionResponse, tags=["Missions"])
async def create_mission(mission_request: MissionRequest):
    """Create a new mission"""
    try:
        # Create mission
        mission = Mission(
            mission_id=f"mission-{str(uuid.uuid4())[:8]}",
            mission_type=mission_request.mission_type,
            priority=mission_request.priority,
            target_layers=mission_request.target_layers,
            configuration=mission_request.configuration,
            simulation_required=mission_request.simulation_required,
            rollback_on_failure=mission_request.rollback_on_failure,
            timeout_seconds=mission_request.timeout_seconds,
            description=mission_request.description
        )
        
        # Submit mission
        mission_id = execution_engine.submit_mission(mission)
        
        return {
            "mission_id": mission_id,
            "status": "submitted",
            "message": "Mission submitted successfully"
        }
    except Exception as e:
        logger.error(f"Error creating mission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating mission: {str(e)}"
        )

@app.get("/missions", response_model=MissionListResponse, tags=["Missions"])
async def list_missions(
    status: Optional[str] = Query(None, description="Filter by mission status"),
    limit: int = Query(10, ge=1, le=100, description="Number of missions to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """List missions"""
    try:
        missions, total = execution_engine.get_missions(status, limit, offset)
        
        return {
            "missions": missions,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Error listing missions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing missions: {str(e)}"
        )

@app.get("/missions/{mission_id}", response_model=MissionDetailResponse, tags=["Missions"])
async def get_mission(mission_id: str = Path(..., description="ID of the mission")):
    """Get mission details"""
    try:
        mission = execution_engine.get_mission(mission_id)
        
        if not mission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Mission {mission_id} not found"
            )
        
        return mission
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting mission {mission_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting mission {mission_id}: {str(e)}"
        )

@app.post("/missions/{mission_id}/cancel", response_model=MissionResponse, tags=["Missions"])
async def cancel_mission(mission_id: str = Path(..., description="ID of the mission")):
    """Cancel a mission"""
    try:
        result = execution_engine.cancel_mission(mission_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to cancel mission {mission_id}"
            )
        
        return {
            "mission_id": mission_id,
            "status": "canceled",
            "message": "Mission canceled successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error canceling mission {mission_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error canceling mission {mission_id}: {str(e)}"
        )

@app.post("/missions/{mission_id}/pause", response_model=MissionResponse, tags=["Missions"])
async def pause_mission(mission_id: str = Path(..., description="ID of the mission")):
    """Pause a mission"""
    try:
        result = execution_engine.pause_mission(mission_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to pause mission {mission_id}"
            )
        
        return {
            "mission_id": mission_id,
            "status": "paused",
            "message": "Mission paused successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing mission {mission_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pausing mission {mission_id}: {str(e)}"
        )

@app.post("/missions/{mission_id}/resume", response_model=MissionResponse, tags=["Missions"])
async def resume_mission(mission_id: str = Path(..., description="ID of the mission")):
    """Resume a paused mission"""
    try:
        result = execution_engine.resume_mission(mission_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to resume mission {mission_id}"
            )
        
        return {
            "mission_id": mission_id,
            "status": "resumed",
            "message": "Mission resumed successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming mission {mission_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resuming mission {mission_id}: {str(e)}"
        )

@app.post("/missions/{mission_id}/rollback", response_model=MissionResponse, tags=["Missions"])
async def rollback_mission(mission_id: str = Path(..., description="ID of the mission")):
    """Rollback a mission"""
    try:
        result = execution_engine.rollback_mission(mission_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to rollback mission {mission_id}"
            )
        
        return {
            "mission_id": mission_id,
            "status": "rollback_initiated",
            "message": "Mission rollback initiated successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back mission {mission_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error rolling back mission {mission_id}: {str(e)}"
        )

@app.get("/layers", tags=["Layers"])
async def list_layers():
    """List available layers"""
    try:
        layers = layer_integration_manager.get_layers()
        return {"layers": layers}
    except Exception as e:
        logger.error(f"Error listing layers: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing layers: {str(e)}"
        )

@app.get("/layers/{layer_id}", tags=["Layers"])
async def get_layer(layer_id: str = Path(..., description="ID of the layer")):
    """Get layer details"""
    try:
        layer = layer_integration_manager.get_layer(layer_id)
        
        if not layer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Layer {layer_id} not found"
            )
        
        return layer
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting layer {layer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting layer {layer_id}: {str(e)}"
        )

@app.get("/layers/{layer_id}/capsules", tags=["Layers"])
async def list_layer_capsules(layer_id: str = Path(..., description="ID of the layer")):
    """List capsules for a layer"""
    try:
        capsules = layer_integration_manager.get_layer_capsules(layer_id)
        
        if capsules is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Layer {layer_id} not found"
            )
        
        return {"capsules": capsules}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing capsules for layer {layer_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing capsules for layer {layer_id}: {str(e)}"
        )

@app.get("/capsules", tags=["Capsules"])
async def list_capsules(
    layer_id: Optional[str] = Query(None, description="Filter by layer ID"),
    status: Optional[str] = Query(None, description="Filter by capsule status")
):
    """List capsules"""
    try:
        capsules = cross_layer_integration_manager.get_capsules(layer_id, status)
        return {"capsules": capsules}
    except Exception as e:
        logger.error(f"Error listing capsules: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing capsules: {str(e)}"
        )

@app.get("/capsules/{capsule_id}", tags=["Capsules"])
async def get_capsule(capsule_id: str = Path(..., description="ID of the capsule")):
    """Get capsule details"""
    try:
        capsule = cross_layer_integration_manager.get_capsule(capsule_id)
        
        if not capsule:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Capsule {capsule_id} not found"
            )
        
        return capsule
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting capsule {capsule_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting capsule {capsule_id}: {str(e)}"
        )

@app.get("/templates", tags=["Templates"])
async def list_templates():
    """List available templates"""
    try:
        from templates.template_registry import TemplateRegistry
        template_registry = TemplateRegistry()
        templates = template_registry.list_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Error listing templates: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing templates: {str(e)}"
        )

@app.get("/templates/{template_id}", tags=["Templates"])
async def get_template(template_id: str = Path(..., description="ID of the template")):
    """Get template details"""
    try:
        from templates.template_registry import TemplateRegistry
        template_registry = TemplateRegistry()
        template = template_registry.get_template(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template {template_id} not found"
            )
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting template {template_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting template {template_id}: {str(e)}"
        )

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail}
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
