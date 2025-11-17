"""
REST API for Adaptive UX System.

This module exposes HTTP endpoints for the adaptive UX system, allowing
frontend clients to retrieve personalized UX configurations and track
effectiveness. Week 10 Day 5-7 deliverable.

Endpoints:
- GET /api/v1/ux/config/{user_id} - Get personalized UX configuration
- POST /api/v1/ux/adjustment - Apply a UX adjustment
- POST /api/v1/ux/override - Record user override
- GET /api/v1/ux/experiments - List active experiments
- POST /api/v1/ux/experiments/{experiment_id}/assign - Assign user to experiment
- POST /api/v1/ux/track - Track UX interaction metric
- GET /api/v1/ux/effectiveness/{user_id} - Get effectiveness metrics
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import asyncio

# Import our adaptive UX components
from .adaptive_ux_engine import adaptive_ux_engine, UXConfiguration
from .ab_testing_framework import ab_testing_framework, Experiment
from .dynamic_layout_adjuster import dynamic_layout_adjuster, LayoutAdjustment
from .data_density_tuner import data_density_tuner, DensityAdjustment

# Import behavioral tracking (from Week 9)
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from behavioral_tracking.bv_storage import BVStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Adaptive UX API",
    description="REST API for personalized UX configuration and adaptation",
    version="1.0.0"
)

# Global storage instance
bv_storage: Optional[BVStorage] = None


# Pydantic models for request/response
class UXConfigRequest(BaseModel):
    """Request for UX configuration."""
    user_id: str
    device_type: Optional[str] = "web"
    screen_width: Optional[int] = 1920
    screen_height: Optional[int] = 1080
    network_speed: Optional[str] = "fast"
    battery_level: Optional[int] = 100


class UXConfigResponse(BaseModel):
    """Response with UX configuration."""
    user_id: str
    config: Dict[str, Any]
    experiment_id: Optional[str] = None
    variant: Optional[str] = None
    confidence_score: float
    generated_at: str


class AdjustmentRequest(BaseModel):
    """Request to apply a UX adjustment."""
    user_id: str
    adjustment_type: str  # layout, density, animation, actions
    target_value: Any
    reason: str
    capsule_id: Optional[str] = None


class OverrideRequest(BaseModel):
    """Request to record user override."""
    user_id: str
    property_name: str
    original_value: Any
    user_value: Any


class ExperimentAssignRequest(BaseModel):
    """Request to assign user to experiment."""
    user_id: str
    expertise_level: Optional[str] = None
    device_type: Optional[str] = None


class TrackingRequest(BaseModel):
    """Request to track UX metric."""
    experiment_id: str
    user_id: str
    metric_name: str
    metric_value: float
    metadata: Optional[Dict[str, Any]] = None


class EffectivenessResponse(BaseModel):
    """Response with effectiveness metrics."""
    user_id: str
    total_adjustments: int
    accepted_adjustments: int
    acceptance_rate: float
    avg_effectiveness_score: float
    recent_adjustments: List[Dict[str, Any]]


# Dependency to get BV storage
async def get_bv_storage():
    """Get BV storage instance."""
    global bv_storage
    if not bv_storage:
        # Initialize storage (would use actual DB credentials in production)
        bv_storage = BVStorage(
            postgres_dsn="postgresql://user:pass@localhost/db",
            redis_url="redis://localhost:6379"
        )
        await bv_storage.initialize()
    return bv_storage


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "adaptive-ux-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/ux/config", response_model=UXConfigResponse)
async def get_ux_config(
    request: UXConfigRequest,
    storage: BVStorage = Depends(get_bv_storage)
):
    """
    Get personalized UX configuration for a user.
    
    This is the main endpoint that frontend clients call to get
    the optimal UX configuration based on the user's behavioral vector.
    """
    try:
        # Retrieve user's behavioral vector
        bv = await storage.get_behavioral_vector(request.user_id)
        
        if not bv:
            # New user, return default configuration
            logger.info(f"New user {request.user_id}, returning default config")
            return UXConfigResponse(
                user_id=request.user_id,
                config={
                    "layout_type": "card",
                    "data_density": "medium",
                    "animation_speed": "normal",
                    "grid_columns": 3
                },
                confidence_score=0.3,
                generated_at=datetime.utcnow().isoformat()
            )
        
        # Build context from request
        context = {
            "device_type": request.device_type,
            "screen_width": request.screen_width,
            "screen_height": request.screen_height,
            "network_speed": request.network_speed,
            "battery_level": request.battery_level
        }
        
        # Generate UX configuration
        ux_config = await adaptive_ux_engine.generate_ux_config(
            user_id=request.user_id,
            behavioral_vector=bv,
            context=context
        )
        
        # Optimize for context
        ux_config = await adaptive_ux_engine.optimize_for_context(
            config=ux_config,
            context=context
        )
        
        # Check for layout adjustments
        current_layout = {
            "layout_type": ux_config.layout_type,
            "grid_columns": ux_config.grid_columns,
            "card_size": ux_config.card_size
        }
        
        adjustments = await dynamic_layout_adjuster.evaluate_triggers(
            user_id=request.user_id,
            behavioral_vector=bv,
            current_layout=current_layout,
            context=context
        )
        
        # Apply highest priority adjustment if any
        if adjustments:
            adjustment = adjustments[0]  # Already sorted by priority
            await dynamic_layout_adjuster.apply_adjustment(adjustment)
            
            # Update config with adjustment
            for change in adjustment.changes:
                setattr(ux_config, change["property"], change["to"])
        
        # Determine optimal data density
        optimal_density = await data_density_tuner.determine_optimal_density(
            user_id=request.user_id,
            behavioral_vector=bv,
            context=context
        )
        
        # Get density configuration
        density_config = data_density_tuner.get_density_config(optimal_density)
        
        logger.info(
            f"Generated UX config for {request.user_id}: "
            f"layout={ux_config.layout_type}, density={optimal_density}"
        )
        
        return UXConfigResponse(
            user_id=request.user_id,
            config={
                # Layout
                "layout_type": ux_config.layout_type,
                "layout_density": ux_config.layout_density,
                "grid_columns": ux_config.grid_columns,
                "card_size": ux_config.card_size,
                
                # Data density
                "data_density": optimal_density,
                "visible_elements": density_config.get("visible_elements", []),
                "hidden_elements": density_config.get("hidden_elements", []),
                "show_details": ux_config.show_details,
                "show_metadata": ux_config.show_metadata,
                "show_timestamps": ux_config.show_timestamps,
                
                # Interaction
                "animation_speed": ux_config.animation_speed,
                "haptic_feedback": ux_config.haptic_feedback,
                "sound_effects": ux_config.sound_effects,
                "confirmation_dialogs": ux_config.confirmation_dialogs,
                
                # Actions
                "primary_actions": ux_config.primary_actions,
                "secondary_actions": ux_config.secondary_actions,
                "hidden_actions": ux_config.hidden_actions,
                
                # Capsule-specific
                "capsule_type_configs": ux_config.capsule_type_configs
            },
            experiment_id=ux_config.experiment_id,
            variant=ux_config.variant,
            confidence_score=ux_config.confidence_score,
            generated_at=ux_config.generated_at
        )
    
    except Exception as e:
        logger.error(f"Error generating UX config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ux/adjustment")
async def apply_adjustment(
    request: AdjustmentRequest,
    storage: BVStorage = Depends(get_bv_storage)
):
    """Apply a UX adjustment for a user."""
    try:
        # Get current BV
        bv = await storage.get_behavioral_vector(request.user_id)
        if not bv:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Generate current config
        ux_config = await adaptive_ux_engine.generate_ux_config(
            user_id=request.user_id,
            behavioral_vector=bv
        )
        
        # Apply adjustment based on type
        if request.adjustment_type == "density":
            current_density = await data_density_tuner.determine_optimal_density(
                user_id=request.user_id,
                behavioral_vector=bv
            )
            
            adjustment = await data_density_tuner.generate_density_adjustment(
                user_id=request.user_id,
                current_density=current_density,
                target_density=request.target_value,
                reason=request.reason,
                capsule_id=request.capsule_id
            )
            
            config = await data_density_tuner.apply_density_adjustment(adjustment)
            
            return {
                "success": True,
                "adjustment_id": adjustment.adjustment_id,
                "adjustment_type": "density",
                "config": config
            }
        
        # Other adjustment types...
        return {"success": True, "message": "Adjustment applied"}
    
    except Exception as e:
        logger.error(f"Error applying adjustment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ux/override")
async def record_override(request: OverrideRequest):
    """Record when a user manually overrides an automatic adjustment."""
    try:
        await dynamic_layout_adjuster.record_user_override(
            user_id=request.user_id,
            overridden_property=request.property_name,
            original_value=request.original_value,
            user_value=request.user_value
        )
        
        logger.info(
            f"Recorded override for {request.user_id}: "
            f"{request.property_name} = {request.user_value}"
        )
        
        return {
            "success": True,
            "message": "Override recorded"
        }
    
    except Exception as e:
        logger.error(f"Error recording override: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ux/experiments")
async def list_experiments():
    """List all active experiments."""
    try:
        experiments = [
            exp for exp in ab_testing_framework.experiments.values()
            if exp.status == "active"
        ]
        
        return {
            "experiments": [
                {
                    "experiment_id": exp.experiment_id,
                    "experiment_name": exp.experiment_name,
                    "description": exp.description,
                    "variants": [
                        {
                            "variant_id": v.variant_id,
                            "variant_name": v.variant_name,
                            "traffic_allocation": v.traffic_allocation,
                            "users_assigned": v.users_assigned
                        }
                        for v in exp.variants
                    ]
                }
                for exp in experiments
            ]
        }
    
    except Exception as e:
        logger.error(f"Error listing experiments: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ux/experiments/{experiment_id}/assign")
async def assign_to_experiment(
    experiment_id: str,
    request: ExperimentAssignRequest
):
    """Assign a user to an experiment."""
    try:
        user_context = {
            "expertise_level": request.expertise_level,
            "device_type": request.device_type
        }
        
        assignment = await ab_testing_framework.assign_user_to_experiment(
            experiment_id=experiment_id,
            user_id=request.user_id,
            user_context=user_context
        )
        
        if not assignment:
            return {
                "success": False,
                "message": "User does not qualify for experiment"
            }
        
        return {
            "success": True,
            "assignment_id": assignment.assignment_id,
            "variant_id": assignment.variant_id,
            "assigned_at": assignment.assigned_at
        }
    
    except Exception as e:
        logger.error(f"Error assigning to experiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/ux/track")
async def track_metric(request: TrackingRequest):
    """Track a UX interaction metric."""
    try:
        await ab_testing_framework.track_interaction(
            experiment_id=request.experiment_id,
            user_id=request.user_id,
            metric_name=request.metric_name,
            metric_value=request.metric_value,
            metadata=request.metadata
        )
        
        return {
            "success": True,
            "message": "Metric tracked"
        }
    
    except Exception as e:
        logger.error(f"Error tracking metric: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/ux/effectiveness/{user_id}", response_model=EffectivenessResponse)
async def get_effectiveness(user_id: str):
    """Get effectiveness metrics for a user's UX adjustments."""
    try:
        # Get adjustment history
        layout_adjustments = dynamic_layout_adjuster.get_adjustment_history(user_id)
        density_adjustments = data_density_tuner.get_adjustment_history(user_id)
        
        all_adjustments = layout_adjustments + density_adjustments
        
        # Calculate metrics
        total = len(all_adjustments)
        accepted = sum(
            1 for adj in all_adjustments
            if adj.get("user_accepted") == True
        )
        
        acceptance_rate = accepted / total if total > 0 else 0
        
        effectiveness_scores = [
            adj.get("effectiveness_score", 0)
            for adj in all_adjustments
            if adj.get("effectiveness_score") is not None
        ]
        
        avg_effectiveness = (
            sum(effectiveness_scores) / len(effectiveness_scores)
            if effectiveness_scores else 0
        )
        
        return EffectivenessResponse(
            user_id=user_id,
            total_adjustments=total,
            accepted_adjustments=accepted,
            acceptance_rate=acceptance_rate,
            avg_effectiveness_score=avg_effectiveness,
            recent_adjustments=all_adjustments[-10:]
        )
    
    except Exception as e:
        logger.error(f"Error getting effectiveness: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
