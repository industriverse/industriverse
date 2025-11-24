from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any, List

from src.bridge_api.security.real_utid_service import RealUTIDService


router = APIRouter(prefix="/v1/utid", tags=["utid"])
service = RealUTIDService()


class UTIDGenerateRequest(BaseModel):
    context: Optional[Dict[str, str]] = None


class UTIDGenerateResponse(BaseModel):
    utid: str
    issued_at_ms: int


class UTIDVerifyRequest(BaseModel):
    utid: str


class UTIDVerifyResponse(BaseModel):
    valid: bool


class UTIDRecordResponse(BaseModel):
    utid: str
    issued_at_ms: int
    context_digest: str
    context: Optional[Dict[str, Any]] = None


@router.post("/generate", response_model=UTIDGenerateResponse)
async def generate_utid(req: UTIDGenerateRequest):
    utid = service.issue(context=req.context)
    issued_at = int(utid.split(":")[3])
    return {"utid": utid, "issued_at_ms": issued_at}


@router.post("/verify", response_model=UTIDVerifyResponse)
async def verify_utid(req: UTIDVerifyRequest):
    valid = service.verify(req.utid)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid UTID")
    return {"valid": True}


@router.get("/list", response_model=List[UTIDRecordResponse])
async def list_utids(limit: int = 50, offset: int = 0, context_digest: Optional[str] = None, context_contains: Optional[str] = None):
    items = service.registry.list(limit=limit, offset=offset, context_digest=context_digest, context_contains=context_contains)
    return [
        {
            "utid": item.utid,
            "issued_at_ms": item.issued_at_ms,
            "context_digest": item.context_digest,
            "context": item.context,
        }
        for item in items
    ]
