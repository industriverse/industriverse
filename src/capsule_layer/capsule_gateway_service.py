from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging
import json
import asyncio
from .database import db_manager
from .redis_manager import redis_manager
from .apns_service import apns_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Capsule Gateway Service", version="1.0.0")

# --- Models ---
class ActivityCreate(BaseModel):
    capsule_id: str
    activity_type: str
    payload: Dict[str, Any]
    device_token: Optional[str] = None

class ActivityUpdate(BaseModel):
    activity_id: int
    status: str
    payload: Optional[Dict[str, Any]] = None

class ActionRequest(BaseModel):
    capsule_id: str
    action_id: str
    payload: Optional[Dict[str, Any]] = None

# --- Lifecycle ---
@app.on_event("startup")
async def startup_event():
    await db_manager.connect()
    await redis_manager.connect()
    await apns_service.connect()
    logger.info("Capsule Gateway Service started.")

@app.on_event("shutdown")
async def shutdown_event():
    await db_manager.disconnect()
    await redis_manager.disconnect()
    logger.info("Capsule Gateway Service stopped.")

# --- REST Endpoints ---
@app.post("/create-activity")
async def create_activity(activity: ActivityCreate):
    """Create a new Live Activity or persistent notification."""
    try:
        # Persist to DB
        query = """
            INSERT INTO activities (capsule_id, activity_type, status, payload)
            VALUES ($1, $2, 'active', $3)
            RETURNING id
        """
        row = await db_manager.fetchrow(query, activity.capsule_id, activity.activity_type, json.dumps(activity.payload))
        activity_id = row['id']

        # Publish to Redis for real-time updates
        await redis_manager.publish(f"capsule:{activity.capsule_id}", {
            "type": "activity_created",
            "activity_id": activity_id,
            "payload": activity.payload
        })

        # Send Push Notification if device token provided
        if activity.device_token:
            await apns_service.send_notification(
                device_token=activity.device_token,
                title=f"New Activity: {activity.capsule_id}",
                body=f"Type: {activity.activity_type}"
            )

        return {"status": "success", "activity_id": activity_id}
    except Exception as e:
        logger.error(f"Error creating activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/update")
async def update_activity(update: ActivityUpdate):
    """Update an existing activity."""
    try:
        # Update DB
        query = """
            UPDATE activities 
            SET status = $1, payload = $2, updated_at = NOW()
            WHERE id = $3
            RETURNING capsule_id
        """
        row = await db_manager.fetchrow(query, update.status, json.dumps(update.payload) if update.payload else None, update.activity_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Activity not found")
            
        capsule_id = row['capsule_id']

        # Publish update
        await redis_manager.publish(f"capsule:{capsule_id}", {
            "type": "activity_updated",
            "activity_id": update.activity_id,
            "status": update.status,
            "payload": update.payload
        })

        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/action")
async def execute_action(action: ActionRequest):
    """Execute an action on a capsule."""
    logger.info(f"Executing action {action.action_id} on {action.capsule_id}")
    
    # In a real system, this would forward the action to the specific capsule's agent
    # For now, we'll just acknowledge it and publish an event
    
    await redis_manager.publish(f"capsule:{action.capsule_id}", {
        "type": "action_triggered",
        "action_id": action.action_id,
        "payload": action.payload
    })
    
    return {"status": "success", "message": "Action queued"}

# --- WebSocket ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    logger.info(f"WebSocket connected: {client_id}")
    
    # Subscribe to Redis channels relevant to this client
    # For simplicity, we'll subscribe to a global 'broadcast' channel and specific client channel
    # In production, this would be more granular based on user permissions
    
    async def redis_handler(message):
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending WS message: {e}")

    # Start Redis subscription in background
    # Note: This is a simplified pattern. Robust handling requires managing the task lifecycle.
    task = asyncio.create_task(redis_manager.subscribe(f"user:{client_id}", redis_handler))

    try:
        while True:
            data = await websocket.receive_json()
            logger.info(f"Received WS message from {client_id}: {data}")
            
            # Handle client messages (e.g., subscriptions to specific capsules)
            if data.get("type") == "subscribe":
                capsule_id = data.get("capsule_id")
                if capsule_id:
                    # Dynamically subscribe to capsule channel
                    # This would require a more complex RedisManager to handle dynamic subs
                    pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {client_id}")
        task.cancel()
