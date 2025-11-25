from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging
import random

from src.capsule_layer.capsule_definitions import CAPSULE_REGISTRY
from src.capsule_layer.ace_reasoning import ACEReasoningTemplate
from src.proof_layer.utid import UTIDGenerator
from src.proof_layer.proof_registry import ProofRegistry
from src.proof_layer.proof_schema import CapsuleProof
from src.bridge_api.event_bus import GlobalEventBus

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
    
    # 5. Publish Event to Pulse
    await GlobalEventBus.publish({
        "type": "capsule_update",
        "capsule_id": capsule.capsule_id,
        "status": "active",
        "utid": utid,
        "energy_usage": 100 # Placeholder for real energy delta
    })

    # 6. Emit Proof Generation Event (Mock)
    # In reality, this comes from the Proof Layer after ZK generation
    proof_id = f"proof-{utid[-6:]}"
    await GlobalEventBus.publish({
        "type": "proof_generated",
        "proof": {
            "proof_id": proof_id,
            "utid": utid,
            "domain": capsule.category.value,
            "metadata": {
                "energy_joules": 100 + random.randint(0, 50),
                "status": "verified",
                "proof_score": 0.95 + (random.random() * 0.05),
                "anchors": [{"chain": "ETH", "tx": f"0x{random.randbytes(4).hex()}"}]
            }
        }
    })

    return CapsuleResponse(
        utid=utid,
        status="queued",
        result=result
    )

    return {
        "physics_topology": capsule.physics_topology,
        "domain_equations": capsule.domain_equations,
        "energy_prior": capsule.energy_prior_file
    }

# --- Resolver Integration ---

from src.protocol_layer.protocols.capsule_resolver import CapsuleResolver, ResolutionResult
from src.protocol_layer.protocols.capsule_uri import CapsuleURI, parse_capsule_uri

class BridgeCapsuleRegistry:
    """Adapter to expose CAPSULE_REGISTRY to the CapsuleResolver."""
    def get_capsule(self, uri: CapsuleURI) -> Optional[Dict[str, Any]]:
        # Simple mapping: check if any capsule name matches the operation
        # In a real system, we'd have a proper index by URI
        for capsule in CAPSULE_REGISTRY.values():
            # Match domain/category and operation/name
            # This is a heuristic for the prototype
            if capsule.category.value == uri.domain and capsule.name == uri.operation:
                 return {
                     "utid": utid_gen.generate(capsule.capsule_id), # Generate/Retrieve UTID
                     "location": "local",
                     "local": True,
                     "credit_root": "mock_root", # Mock credit root
                     "metadata": {
                         "description": capsule.description,
                         "version": capsule.version
                     }
                 }
        return None

# Instantiate Resolver with the adapter
# We use a mock mesh client and ledger for now as they are not fully wired in BridgeAPI yet
resolver = CapsuleResolver(
    registry=BridgeCapsuleRegistry(),
    mesh_client=None, 
    ledger=None, 
    sandbox=None, # We will wire the sandbox later
    emitter=GlobalEventBus # GlobalEventBus has a publish method, but resolver expects emit(event). We need an adapter.
)

class EventBusEmitter:
    def emit(self, event: Dict[str, Any]):
        # Fire and forget async publish is tricky here without await
        # For now, we might skip or use a background task if possible, 
        # but CapsuleResolver.resolve is synchronous. 
        # We will skip emitting from inside resolver for this synchronous pass 
        # or rely on the router to emit.
        pass

resolver.emitter = EventBusEmitter()

class ResolveRequest(BaseModel):
    uri: str

@router.post("/resolve")
async def resolve_capsule(request: ResolveRequest):
    """
    Resolve a capsule:// URI to its metadata and execution status.
    """
    result = resolver.resolve(request.uri)
    
    return {
        "status": "success",
        "message": "Capsule Resolved",
        "resolution": result
    }

@router.post("/capsules/{capsule_id}/dac")
async def generate_dac(capsule_id: str, version: str = "v1"):
    """
    Phase 6: Generate a DAC for a Sovereign Capsule.
    """
    # Construct local path (assuming running from project root)
    sovereign_dir = f"src/capsules/sovereign/{capsule_id}_{version}"
    
    if not os.path.isdir(sovereign_dir):
        raise HTTPException(status_code=404, detail=f"Sovereign Capsule {capsule_id} not found")

    try:
        from src.capsules.core.sovereign_capsule import SovereignCapsule
        from src.capsules.factory.dac_factory import dac_factory
        
        capsule = SovereignCapsule(sovereign_dir)
        dac_package = dac_factory.generate_dac(capsule)
        
        return {
            "status": "success",
            "message": "DAC Generated",
            "dac": dac_package
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```
