"""
REST API for Overseer Capsule Orchestration.

This module exposes HTTP endpoints for launchpad generation, capsule management,
and spawn rule configuration. Week 12 deliverable.

Endpoints:
- GET /api/v1/overseer/launchpad/{user_id} - Get personalized launchpad
- POST /api/v1/overseer/capsules - Create/spawn capsule
- GET /api/v1/overseer/capsules/{capsule_id} - Get capsule details
- PATCH /api/v1/overseer/capsules/{capsule_id}/state - Update capsule state
- POST /api/v1/overseer/capsules/{capsule_id}/pin - Pin capsule
- POST /api/v1/overseer/capsules/{capsule_id}/hide - Hide capsule
- POST /api/v1/overseer/spawn-rules - Add spawn rule
- GET /api/v1/overseer/spawn-rules - List spawn rules
- POST /api/v1/overseer/evaluate-spawn - Evaluate spawn rules
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel, Field

# Import orchestrator
from .capsule_orchestrator import capsule_orchestrator, Capsule, UserLaunchpad, SpawnRule

# Import from previous weeks
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from behavioral_tracking.bv_storage import BVStorage
from adaptive_ux.adaptive_ux_engine import adaptive_ux_engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Overseer API",
    description="REST API for personalized capsule orchestration",
    version="1.0.0"
)


# Pydantic models
class LaunchpadRequest(BaseModel):
    """Request for personalized launchpad."""
    user_id: str
    user_role: str
    context: Optional[Dict[str, Any]] = {}


class LaunchpadResponse(BaseModel):
    """Response with personalized launchpad."""
    user_id: str
    user_role: str
    visible_capsules: List[Dict[str, Any]]
    pinned_capsules: List[str]
    hidden_capsules: List[str]
    layout_config: Dict[str, Any]
    generated_at: str
    expires_at: str


class CapsuleCreateRequest(BaseModel):
    """Request to create/spawn a capsule."""
    capsule_type: str
    title: str
    description: str
    priority: int = Field(default=5, ge=1, le=10)
    visibility_rule: str = "always_visible"
    visible_to_roles: List[str] = ["admin", "manager", "operator"]
    visible_to_users: Optional[List[str]] = None
    context_tags: List[str] = []
    metadata: Dict[str, Any] = {}


class CapsuleStateUpdateRequest(BaseModel):
    """Request to update capsule state."""
    new_state: str
    user_id: Optional[str] = None


class SpawnRuleRequest(BaseModel):
    """Request to add a spawn rule."""
    rule_name: str
    description: str
    trigger_type: str
    trigger_conditions: Dict[str, Any]
    capsule_template: Dict[str, Any]
    enabled: bool = True


class SpawnEvaluationRequest(BaseModel):
    """Request to evaluate spawn rules."""
    user_id: str
    event_type: str
    event_data: Dict[str, Any]


# Global storage instance
bv_storage: Optional[BVStorage] = None


async def get_bv_storage():
    """Get BV storage instance."""
    global bv_storage
    if not bv_storage:
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
        "service": "overseer-api",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/v1/overseer/launchpad", response_model=LaunchpadResponse)
async def get_launchpad(
    request: LaunchpadRequest,
    storage: BVStorage = None  # Would use Depends in production
):
    """
    Get personalized launchpad for a user.
    
    This is the main endpoint that generates a user's personalized
    dashboard with relevant capsules.
    """
    try:
        # Get user's behavioral vector (from Week 9)
        # bv = await storage.get_behavioral_vector(request.user_id)
        # Simulate BV for now
        bv = {
            "expertise_level": "intermediate",
            "engagement_patterns": {
                "preferred_capsule_types": ["task", "alert"]
            },
            "interaction_history": {
                "ignored_capsule_types": ["tutorial"]
            }
        }
        
        # Get UX configuration (from Week 10)
        ux_config = {
            "layout_type": "grid",
            "grid_columns": 3,
            "data_density": 3
        }
        
        # Generate launchpad
        launchpad = await capsule_orchestrator.generate_launchpad(
            user_id=request.user_id,
            user_role=request.user_role,
            behavioral_vector=bv,
            context=request.context,
            layout_config=ux_config
        )
        
        # Get full capsule details
        visible_capsules_details = [
            {
                "capsule_id": cid,
                **asdict(capsule_orchestrator.get_capsule(cid))
            }
            for cid in launchpad.visible_capsules
            if capsule_orchestrator.get_capsule(cid)
        ]
        
        return LaunchpadResponse(
            user_id=launchpad.user_id,
            user_role=launchpad.user_role,
            visible_capsules=visible_capsules_details,
            pinned_capsules=launchpad.pinned_capsules,
            hidden_capsules=launchpad.hidden_capsules,
            layout_config=launchpad.layout_config,
            generated_at=launchpad.generated_at,
            expires_at=launchpad.expires_at
        )
    
    except Exception as e:
        logger.error(f"Error generating launchpad: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/overseer/capsules")
async def create_capsule(request: CapsuleCreateRequest):
    """Create/spawn a new capsule."""
    try:
        capsule_template = {
            "capsule_type": request.capsule_type,
            "title": request.title,
            "description": request.description,
            "priority": request.priority,
            "visibility_rule": request.visibility_rule,
            "visible_to_roles": request.visible_to_roles,
            "context_tags": request.context_tags,
            "metadata": request.metadata
        }
        
        capsule = await capsule_orchestrator.spawn_capsule(
            capsule_template=capsule_template,
            user_id=request.visible_to_users[0] if request.visible_to_users else None
        )
        
        return {
            "success": True,
            "capsule_id": capsule.capsule_id,
            "capsule": asdict(capsule)
        }
    
    except Exception as e:
        logger.error(f"Error creating capsule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/overseer/capsules/{capsule_id}")
async def get_capsule(capsule_id: str):
    """Get details of a specific capsule."""
    try:
        capsule = capsule_orchestrator.get_capsule(capsule_id)
        
        if not capsule:
            raise HTTPException(status_code=404, detail="Capsule not found")
        
        return {
            "capsule_id": capsule.capsule_id,
            **asdict(capsule)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting capsule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.patch("/api/v1/overseer/capsules/{capsule_id}/state")
async def update_capsule_state(
    capsule_id: str,
    request: CapsuleStateUpdateRequest
):
    """Update capsule lifecycle state."""
    try:
        await capsule_orchestrator.update_capsule_state(
            capsule_id=capsule_id,
            new_state=request.new_state,
            user_id=request.user_id
        )
        
        capsule = capsule_orchestrator.get_capsule(capsule_id)
        
        return {
            "success": True,
            "capsule_id": capsule_id,
            "new_state": capsule.state if capsule else None
        }
    
    except Exception as e:
        logger.error(f"Error updating capsule state: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/overseer/capsules/{capsule_id}/pin")
async def pin_capsule(capsule_id: str, user_id: str = Body(..., embed=True)):
    """Pin a capsule to user's launchpad."""
    try:
        # Would update database in production
        logger.info(f"Pinned capsule {capsule_id} for user {user_id}")
        
        return {
            "success": True,
            "message": "Capsule pinned"
        }
    
    except Exception as e:
        logger.error(f"Error pinning capsule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/overseer/capsules/{capsule_id}/hide")
async def hide_capsule(capsule_id: str, user_id: str = Body(..., embed=True)):
    """Hide a capsule from user's launchpad."""
    try:
        # Would update database in production
        logger.info(f"Hid capsule {capsule_id} for user {user_id}")
        
        return {
            "success": True,
            "message": "Capsule hidden"
        }
    
    except Exception as e:
        logger.error(f"Error hiding capsule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/overseer/spawn-rules")
async def add_spawn_rule(request: SpawnRuleRequest):
    """Add a spawn rule for automatic capsule creation."""
    try:
        rule_id = f"rule_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        rule = SpawnRule(
            rule_id=rule_id,
            rule_name=request.rule_name,
            description=request.description,
            trigger_type=request.trigger_type,
            trigger_conditions=request.trigger_conditions,
            capsule_template=request.capsule_template,
            enabled=request.enabled
        )
        
        capsule_orchestrator.add_spawn_rule(rule)
        
        return {
            "success": True,
            "rule_id": rule_id,
            "rule": asdict(rule)
        }
    
    except Exception as e:
        logger.error(f"Error adding spawn rule: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/overseer/spawn-rules")
async def list_spawn_rules():
    """List all spawn rules."""
    try:
        rules = list(capsule_orchestrator.spawn_rules.values())
        
        return {
            "total_rules": len(rules),
            "rules": [asdict(r) for r in rules]
        }
    
    except Exception as e:
        logger.error(f"Error listing spawn rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/overseer/evaluate-spawn")
async def evaluate_spawn_rules(request: SpawnEvaluationRequest):
    """Evaluate spawn rules and spawn capsules if conditions are met."""
    try:
        await capsule_orchestrator.evaluate_spawn_rules(
            user_id=request.user_id,
            event_type=request.event_type,
            event_data=request.event_data
        )
        
        return {
            "success": True,
            "message": "Spawn rules evaluated"
        }
    
    except Exception as e:
        logger.error(f"Error evaluating spawn rules: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper to import asdict
from dataclasses import asdict


# Run the API server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
