from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from src.capsule_layer.capsule_definitions import CAPSULE_REGISTRY
from src.capsule_layer.ace_reasoning import ACEReasoningTemplate
from src.proof_layer.utid import UTIDGenerator
from src.proof_layer.proof_registry import ProofRegistry
from src.proof_layer.proof_schema import CapsuleProof

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1/capsules", tags=["Capsules"])

# Shared instances (in a real app, use dependency injection)
utid_gen = UTIDGenerator()
proof_registry = ProofRegistry()

class CapsuleRequest(BaseModel):
    capsule_id: str
    payload: Dict[str, Any]
    priority: str = "normal"

class CapsuleResponse(BaseModel):
    utid: str
    status: str
    proof_id: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

@router.get("/")
async def list_capsules():
    """List all available Sovereign Capsules."""
    return [
        {
            "id": c.capsule_id,
            "name": c.name,
            "category": c.category.value,
            "description": c.description
        }
        for c in CAPSULE_REGISTRY.values()
    ]

@router.post("/execute", response_model=CapsuleResponse)
async def execute_capsule(request: CapsuleRequest, background_tasks: BackgroundTasks):
    """
    Trigger execution of a specific capsule.
    """
    if request.capsule_id not in CAPSULE_REGISTRY:
        raise HTTPException(status_code=404, detail="Capsule not found")
    
    capsule = CAPSULE_REGISTRY[request.capsule_id]
    
    # 1. Generate UTID
    utid = utid_gen.generate(capsule.capsule_id)
    
    # 2. Initialize ACE Context
    ace = ACEReasoningTemplate(capsule)
    
    # 3. Check Safety Budget (Mock estimation)
    estimated_cost = 10.0 # Placeholder
    if not ace.check_safety_budget(estimated_cost):
        raise HTTPException(status_code=400, detail="Safety budget exceeded")
    
    # 4. Execute Logic (Mock for now - would be async task)
    # In production, this pushes to NATS
    logger.info(f"Executing {capsule.name} [UTID={utid}]")
    
    # Simulate result
    result = {"status": "success", "data": "processed"}
    
    # 5. Generate Proof (Mock)
    # In production, this happens after execution
    # We'll just return the UTID for now
    
    return CapsuleResponse(
        utid=utid,
        status="queued",
        result=result
    )

@router.get("/{capsule_id}/topology")
async def get_topology(capsule_id: str):
    """Get the thermodynamic topology signature of a capsule."""
    if capsule_id not in CAPSULE_REGISTRY:
        raise HTTPException(status_code=404, detail="Capsule not found")
        
    capsule = CAPSULE_REGISTRY[capsule_id]
    return {
        "physics_topology": capsule.physics_topology,
        "domain_equations": capsule.domain_equations,
        "energy_prior": capsule.energy_prior_file
    }
