from fastapi import APIRouter, Query
from typing import List, Optional

from src.proof_core.integrity_layer.integrity_manager import IntegrityManager

router = APIRouter(prefix="/v1/proofs", tags=["proof-graph"])
manager = IntegrityManager()
repository = manager.repository


@router.get("/graph")
async def get_graph(limit: int = Query(100, le=500), offset: int = Query(0, ge=0)):
    items = repository.list(limit=limit, offset=offset)
    nodes = [
        {
            "id": item.proof_id,
            "utid": item.utid,
            "status": item.metadata.get("status"),
            "proof_score": item.metadata.get("proof_score"),
            "anchors": item.metadata.get("anchors", []),
        }
        for item in items
    ]
    edges = []
    for item in items:
        parent = item.metadata.get("parent_proof_id")
        if parent:
            edges.append(
                {
                    "from": parent,
                    "to": item.proof_id,
                    "utid": item.utid,
                    "status": item.metadata.get("status"),
                    "proof_score": item.metadata.get("proof_score"),
                }
            )
    return {"nodes": nodes, "edges": edges}
