from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import time

from src.proof_core.integrity_layer.integrity_manager import IntegrityManager
from src.proof_core.proof_mesh.mesh_validator import ProofMeshValidator
from src.proof_core.proof_mesh.mesh_gossip import MeshGossip
from src.proof_core.proof_economy.proofscore import compute_proof_score
from src.proof_core.proof_hub.sqlite_repository import SQLiteProofRepository

router = APIRouter(prefix="/v1/proofs", tags=["proofs"])
manager = IntegrityManager()
repository = manager.repository
mesh_validator = ProofMeshValidator()
mesh_gossip = MeshGossip(node_id="bridge_api_node")

class ProofRequest(BaseModel):
    title: str
    requester: Dict[str, str]
    artifacts: List[Dict[str, str]]
    proof_types: List[str]
    anchor: Optional[Dict[str, Any]] = None
    anchors: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    proof_hash: Optional[str] = None
    parent_proof_id: Optional[str] = None

class ProofResponse(BaseModel):
    proof_id: str
    status: str
    estimated_time_s: int
    verify_endpoint: str
    utid: Optional[str] = None
    proof_hash: Optional[str] = None

class ProofVerifyRequest(BaseModel):
    proof_hash: str
    verifier: str


class ProofStatusUpdateRequest(BaseModel):
    status: str
    anchors: Optional[List[Dict[str, Any]]] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    proof_score: Optional[float] = None

@router.post("/generate", response_model=ProofResponse)
async def generate_proof(request: ProofRequest):
    proof_id = f"proof_{uuid.uuid4().hex[:8]}"
    utid = (request.anchor or {}).get("utid") if request.anchor else None
    proof_hash = request.proof_hash or uuid.uuid4().hex
    anchors = request.anchors or []
    parent_proof_id = request.parent_proof_id or (request.anchor or {}).get("parent_proof_id")
    # Persist normalized proof skeleton
    repository.store(
        {
            "proof_id": proof_id,
            "utid": utid or "UTID:REAL:unknown",
            "domain": (request.anchor or {}).get("domain", "general"),
            "inputs": {"artifacts": request.artifacts, "metadata": request.metadata},
            "outputs": {"proof_types": request.proof_types},
            "metadata": {"requester": request.requester, "proof_hash": proof_hash, "status": "queued", "anchors": anchors, "parent_proof_id": parent_proof_id, **(request.metadata or {})},
            "parent_proof_id": parent_proof_id,
        }
    )
    return {
        "proof_id": proof_id,
        "status": "queued",
        "estimated_time_s": 5,
        "verify_endpoint": f"/v1/proofs/{proof_id}/verify",
        "utid": utid,
        "proof_hash": proof_hash,
    }

@router.get("/{proof_id}")
async def get_proof(proof_id: str):
    stored = repository.get(proof_id)
    if not stored:
        raise HTTPException(status_code=404, detail="Proof not found")
    return {
        "proof_id": stored.proof_id,
        "status": stored.metadata.get("status", "unknown"),
        "hash": stored.metadata.get("proof_hash"),
        "anchors": stored.metadata.get("anchors", []),
        "evidence": stored.metadata.get("evidence", []),
        "signed_by": stored.metadata.get("signed_by", "unknown"),
        "signature": stored.metadata.get("signature", "ecdsa:mock_signature"),
        "utid": stored.utid,
        "domain": stored.domain,
    }

@router.post("/verify")
async def verify_proof(request: ProofVerifyRequest):
    items = repository.list(proof_hash=request.proof_hash, limit=1)
    if not items:
        raise HTTPException(status_code=404, detail="Proof not found")
    proof_id = items[0].proof_id
    # Mesh validation for proof_score + hash
    mesh_result = await mesh_validator.validate(items[0].__dict__ if hasattr(items[0], "__dict__") else {})
    proof_score = mesh_result.get("proof_score")
    validation_hash = mesh_result.get("proof_hash")
    anchors = mesh_result.get("anchors") or [{"chain": "local", "tx": validation_hash, "time": time.time()}]
    # Disseminate to mesh (stub)
    await mesh_gossip.disseminate(items[0].__dict__ if hasattr(items[0], "__dict__") else {})
    if hasattr(repository, "update_status"):
        repository.update_status(proof_id, status="verified", anchors=anchors, extra={"proof_score": proof_score, "proof_hash": validation_hash})
    return {
        "status": "verified",
        "valid": True,
        "verifier": request.verifier,
        "proof_id": proof_id,
        "anchors": anchors,
        "proof_score": proof_score,
        "proof_hash": validation_hash,
    }


@router.post("/{proof_id}/status")
async def update_proof_status(proof_id: str, request: ProofStatusUpdateRequest):
    if not hasattr(repository, "update_status"):
        raise HTTPException(status_code=400, detail="Repository does not support status updates")
    extra = {}
    if request.evidence:
        extra["evidence"] = request.evidence
    if request.proof_score is not None:
        extra["proof_score"] = request.proof_score
    updated = repository.update_status(proof_id, status=request.status, anchors=request.anchors, extra=extra)
    if not updated:
        raise HTTPException(status_code=404, detail="Proof not found")
    return {"proof_id": proof_id, "status": request.status, "anchors": request.anchors or [], "proof_score": request.proof_score}

@router.get("/explain")
async def explain_proof():
    return {"detail": "Not implemented yet"}


@router.get("/")
async def list_proofs(
    utid: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    min_energy: Optional[float] = Query(None),
    max_energy: Optional[float] = Query(None),
    proof_hash: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    anchor_chain: Optional[str] = Query(None),
    anchor_tx: Optional[str] = Query(None),
    evidence_contains: Optional[str] = Query(None),
    min_score: Optional[float] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
):
    items = repository.list(
        utid=utid,
        domain=domain,
        min_energy=min_energy,
        max_energy=max_energy,
        proof_hash=proof_hash,
        status=status,
        anchor_chain=anchor_chain,
        anchor_tx=anchor_tx,
        evidence_contains=evidence_contains,
        parent_proof_id=None,
        limit=limit,
        offset=offset,
    )
    return [
        {
            "proof_id": item.proof_id,
            "utid": item.utid,
            "domain": item.domain,
            "inputs": item.inputs,
            "outputs": item.outputs,
            "metadata": item.metadata,
        }
        for item in items
    ]
