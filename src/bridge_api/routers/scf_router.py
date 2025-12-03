from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import os
import json

# Mock dependencies for now as we are integrating into a larger system
# In a real app, these would be injected dependencies
from src.scf.factory.dac_manager import DACManager

router = APIRouter(prefix="/scf", tags=["Sovereign Code Foundry"])
dac_manager = DACManager()

class IntentRequest(BaseModel):
    text: str
    source: str = "text" # text or voice

@router.get("/status")
async def get_status():
    """
    Returns the heartbeat of the Sovereign Daemon.
    """
    heartbeat_path = "data/scf/heartbeat.json"
    if os.path.exists(heartbeat_path):
        with open(heartbeat_path, 'r') as f:
            return json.load(f)
    return {"status": "OFFLINE", "message": "Daemon not running"}

@router.post("/intent")
async def submit_intent(request: IntentRequest):
    """
    Submits a natural language intent to the SCF.
    This writes to the control plane for the Daemon to pick up.
    """
    # In a real implementation, we might push to a queue.
    # For now, we'll just acknowledge it. The Daemon pulls from its own internal queue (IntentEngine).
    # To make this "live", we could write to a special "intent_inbox.json" that the Daemon checks.
    
    inbox_path = "data/scf/intent_inbox.json"
    entry = {
        "text": request.text,
        "source": request.source,
        "status": "pending"
    }
    
    # Simple append to a list file (mock queue)
    queue = []
    if os.path.exists(inbox_path):
        with open(inbox_path, 'r') as f:
            try:
                queue = json.load(f)
            except:
                pass
    queue.append(entry)
    
    with open(inbox_path, 'w') as f:
        json.dump(queue, f)
        
    return {"status": "accepted", "message": "Intent queued for processing"}

@router.get("/dacs")
async def list_dacs():
    """
    Lists all available Deploy Anywhere Capsules.
    """
    return {"capsules": dac_manager.list_capsules()}

@router.get("/dacs/{capsule_id}/download")
async def download_dac(capsule_id: str):
    """
    Returns the download path for a capsule.
    """
    # The capsule_id in registry is "partner:name", but the zip is named "dac-uuid".
    # We need to map them or just use the ID returned by create_capsule.
    # For simplicity in this prototype, we'll assume the frontend requests by the filename/UUID 
    # or we iterate to find the zip.
    
    # If capsule_id is a UUID-like string (from create_capsule return)
    path = dac_manager.dac_dir / f"{capsule_id}.zip"
    if path.exists():
        return {"download_url": f"/files/scf/dacs/{capsule_id}.zip"}
        
    # If capsule_id is a registry ID (partner:name), we need to find the latest version's zip
    # This part is tricky without storing the mapping. 
    # For now, let's stick to the UUID-based access if possible, or search.
    
    raise HTTPException(status_code=404, detail="Capsule not found")

@router.get("/dashboard")
async def get_dashboard_metrics():
    """
    Returns the real-time Sovereign Intelligence Dashboard metrics.
    """
    metrics_path = "data/datahub/dashboard_metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            return json.load(f)
    return {"status": "WAITING_FOR_DATA", "message": "Metrics not yet generated"}
