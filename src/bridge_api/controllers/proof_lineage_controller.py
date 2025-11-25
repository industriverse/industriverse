from fastapi import APIRouter, Query
from typing import List, Optional

from src.proof_core.integrity_layer.integrity_manager import IntegrityManager

router = APIRouter(prefix="/v1/proofs", tags=["proof-lineage"])
manager = IntegrityManager()
repository = manager.repository


@router.get("/lineage")
async def get_lineage(parent_proof_id: Optional[str] = Query(None), limit: int = Query(50, le=200), offset: int = Query(0, ge=0)):
    items = repository.list(parent_proof_id=parent_proof_id, limit=limit, offset=offset)
    edges = []
    for item in items:
        parent = item.metadata.get("parent_proof_id")
        if parent:
            edges.append({"from": parent, "to": item.proof_id, "utid": item.utid, "status": item.metadata.get("status")})
    return edges
