from fastapi import APIRouter
from src.bridge_api.ai_shield.state import shield_state

router = APIRouter(prefix="/v1/shield", tags=["shield"])


@router.get("/state")
async def get_shield_state():
    return shield_state.get()
