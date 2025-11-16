"""
Capsule Gateway Service
Production-ready backend service for Capsule Pins

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .database import CapsuleDatabase
from .apns_service import APNsService
from .redis_manager import RedisManager
from .websocket_server import WebSocketServer


class CapsuleState(str, Enum):
    """Capsule state enumeration"""
    ACTIVE = "active"
    PENDING = "pending"
    RESOLVED = "resolved"
    EXPIRED = "expired"


class CapsulePriority(str, Enum):
    """Capsule priority enumeration"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ActionType(str, Enum):
    """Action type enumeration"""
    MITIGATE = "mitigate"
    INSPECT = "inspect"
    DISMISS = "dismiss"
    APPROVE = "approve"
    REJECT = "reject"


# Pydantic models for API requests/responses
class CreateActivityRequest(BaseModel):
    """Request model for creating a capsule activity"""
    capsule_id: str = Field(..., description="Unique capsule identifier")
    title: str = Field(..., description="Capsule title")
    message: str = Field(..., description="Capsule message")
    priority: CapsulePriority = Field(default=CapsulePriority.MEDIUM, description="Capsule priority")
    utid: Optional[str] = Field(None, description="UTID for proof lineage")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    device_tokens: Optional[List[str]] = Field(default_factory=list, description="Target device tokens")


class UpdateActivityRequest(BaseModel):
    """Request model for updating a capsule activity"""
    capsule_id: str = Field(..., description="Capsule identifier")
    title: Optional[str] = Field(None, description="Updated title")
    message: Optional[str] = Field(None, description="Updated message")
    state: Optional[CapsuleState] = Field(None, description="Updated state")
    priority: Optional[CapsulePriority] = Field(None, description="Updated priority")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Updated metadata")


class ActionRequest(BaseModel):
    """Request model for capsule actions"""
    capsule_id: str = Field(..., description="Capsule identifier")
    action_type: ActionType = Field(..., description="Action type")
    user_id: Optional[str] = Field(None, description="User performing action")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Action metadata")


class ActivityResponse(BaseModel):
    """Response model for activity operations"""
    success: bool
    capsule_id: str
    activity_id: str
    message: str
    timestamp: float


class ActionResponse(BaseModel):
    """Response model for action operations"""
    success: bool
    capsule_id: str
    action_type: str
    result: Dict[str, Any]
    timestamp: float


class CapsuleGatewayService:
    """
    Production Capsule Gateway Service
    
    Backend service for Capsule Pins with:
    - PostgreSQL database for persistent storage
    - APNs integration for iOS push notifications
    - Redis for WebSocket session management
    - REST API endpoints (/create-activity, /update, /action)
    - WebSocket real-time updates
    """
    
    def __init__(self, port: int = 8210):
        """
        Initialize Capsule Gateway Service
        
        Args:
            port: Service port (default: 8210)
        """
        self.port = port
        self.app = FastAPI(
            title="Capsule Gateway Service",
            description="Production backend service for Capsule Pins",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Initialize production services
        self.db = CapsuleDatabase()
        self.apns = APNsService()
        self.redis = RedisManager()
        self.ws_server: Optional[WebSocketServer] = None
        
        # Setup routes
        self._setup_routes()
        
        print(f"✅ Capsule Gateway Service initialized on port {self.port}")
    
    async def startup(self):
        """Startup event handler"""
        await self.db.connect()
        await self.apns.connect()
        await self.redis.connect()
        
        # Initialize WebSocket server
        self.ws_server = WebSocketServer(self.redis)
        
        print("✅ All services connected")
    
    async def shutdown(self):
        """Shutdown event handler"""
        await self.db.disconnect()
        await self.apns.disconnect()
        await self.redis.disconnect()
        print("✅ All services disconnected")
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.on_event("startup")
        async def startup_event():
            await self.startup()
        
        @self.app.on_event("shutdown")
        async def shutdown_event():
            await self.shutdown()
        
        @self.app.get("/")
        async def root():
            """Health check endpoint"""
            return {
                "service": "Capsule Gateway Service",
                "status": "operational",
                "version": "1.0.0",
                "timestamp": time.time()
            }
        
        @self.app.get("/health")
        async def health():
            """Health check endpoint"""
            stats = await self.db.get_statistics()
            connection_count = await self.redis.get_connection_count()
            
            return {
                "status": "healthy",
                "database": "connected",
                "redis": "connected",
                "apns": "connected" if self.apns.client else "disconnected",
                "active_activities": stats["active_activities"],
                "active_connections": connection_count,
                "timestamp": time.time()
            }
        
        @self.app.post("/create-activity", response_model=ActivityResponse)
        async def create_activity(request: CreateActivityRequest):
            """Create a new capsule activity"""
            try:
                # Generate activity ID
                activity_id = f"activity_{uuid.uuid4().hex[:16]}"
                
                # Create activity in database
                activity = await self.db.create_activity(
                    activity_id=activity_id,
                    capsule_id=request.capsule_id,
                    title=request.title,
                    message=request.message,
                    priority=request.priority.value,
                    utid=request.utid,
                    metadata=request.metadata or {},
                    device_tokens=request.device_tokens or []
                )
                
                # Cache activity in Redis
                await self.redis.cache_activity(request.capsule_id, activity)
                
                # Broadcast to connected clients via Redis pub/sub
                await self.redis.publish_update("capsule_updates", {
                    "type": "activity_created",
                    "activity_id": activity_id,
                    "capsule_id": request.capsule_id,
                    "data": activity
                })
                
                # Broadcast to WebSocket connections
                await self._broadcast_update({
                    "type": "activity_created",
                    "activity_id": activity_id,
                    "capsule_id": request.capsule_id,
                    "data": activity
                })
                
                # Send push notifications
                if request.device_tokens:
                    await self.apns.send_batch_notifications(
                        device_tokens=request.device_tokens,
                        title=request.title,
                        message=request.message,
                        priority=request.priority.value,
                        custom_data={
                            "capsule_id": request.capsule_id,
                            "activity_id": activity_id,
                            "utid": request.utid
                        }
                    )
                
                print(f"✅ Created activity: {activity_id} for capsule {request.capsule_id}")
                
                return ActivityResponse(
                    success=True,
                    capsule_id=request.capsule_id,
                    activity_id=activity_id,
                    message="Activity created successfully",
                    timestamp=time.time()
                )
            
            except Exception as e:
                print(f"❌ Error creating activity: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.put("/update", response_model=ActivityResponse)
        async def update_activity(request: UpdateActivityRequest):
            """Update an existing capsule activity"""
            try:
                # Update activity in database
                activity = await self.db.update_activity(
                    capsule_id=request.capsule_id,
                    title=request.title,
                    message=request.message,
                    state=request.state.value if request.state else None,
                    priority=request.priority.value if request.priority else None,
                    metadata=request.metadata
                )
                
                if not activity:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Activity not found for capsule {request.capsule_id}"
                    )
                
                # Invalidate cache
                await self.redis.invalidate_activity_cache(request.capsule_id)
                
                # Cache updated activity
                await self.redis.cache_activity(request.capsule_id, activity)
                
                # Broadcast update
                await self.redis.publish_update("capsule_updates", {
                    "type": "activity_updated",
                    "capsule_id": request.capsule_id,
                    "data": activity
                })
                
                await self._broadcast_update({
                    "type": "activity_updated",
                    "capsule_id": request.capsule_id,
                    "data": activity
                })
                
                # Send push notification for important updates
                if request.state in [CapsuleState.RESOLVED, CapsuleState.EXPIRED]:
                    device_tokens = activity.get("device_tokens", [])
                    if device_tokens:
                        await self.apns.send_batch_notifications(
                            device_tokens=device_tokens,
                            title=activity["title"],
                            message=f"Status updated: {request.state.value}",
                            priority=activity["priority"]
                        )
                
                print(f"✅ Updated activity for capsule {request.capsule_id}")
                
                return ActivityResponse(
                    success=True,
                    capsule_id=request.capsule_id,
                    activity_id=activity["activity_id"],
                    message="Activity updated successfully",
                    timestamp=time.time()
                )
            
            except HTTPException:
                raise
            except Exception as e:
                print(f"❌ Error updating activity: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/action", response_model=ActionResponse)
        async def handle_action(request: ActionRequest):
            """Handle capsule action"""
            try:
                # Get activity from database
                activity = await self.db.get_activity_by_capsule_id(request.capsule_id)
                
                if not activity:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Activity not found for capsule {request.capsule_id}"
                    )
                
                # Generate action ID
                action_id = f"action_{uuid.uuid4().hex[:16]}"
                
                # Process action
                result = await self._process_action(
                    activity,
                    request.action_type,
                    request.user_id,
                    request.metadata
                )
                
                # Create action record in database
                await self.db.create_action(
                    action_id=action_id,
                    capsule_id=request.capsule_id,
                    action_type=request.action_type.value,
                    user_id=request.user_id,
                    metadata=request.metadata or {},
                    result=result
                )
                
                # Broadcast action
                await self.redis.publish_update("capsule_updates", {
                    "type": "action_performed",
                    "action_id": action_id,
                    "capsule_id": request.capsule_id,
                    "action_type": request.action_type.value,
                    "result": result
                })
                
                await self._broadcast_update({
                    "type": "action_performed",
                    "action_id": action_id,
                    "capsule_id": request.capsule_id,
                    "action_type": request.action_type.value,
                    "result": result
                })
                
                print(f"✅ Processed action: {request.action_type.value} for capsule {request.capsule_id}")
                
                return ActionResponse(
                    success=True,
                    capsule_id=request.capsule_id,
                    action_type=request.action_type.value,
                    result=result,
                    timestamp=time.time()
                )
            
            except HTTPException:
                raise
            except Exception as e:
                print(f"❌ Error handling action: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/activities")
        async def list_activities(
            state: Optional[str] = None,
            priority: Optional[str] = None,
            limit: int = 100
        ):
            """List capsule activities"""
            activities = await self.db.list_activities(
                state=state,
                priority=priority,
                limit=limit
            )
            
            return {
                "activities": activities,
                "count": len(activities),
                "timestamp": time.time()
            }
        
        @self.app.get("/activity/{capsule_id}")
        async def get_activity(capsule_id: str):
            """Get activity by capsule ID"""
            # Try cache first
            activity = await self.redis.get_cached_activity(capsule_id)
            
            if not activity:
                # Fetch from database
                activity = await self.db.get_activity_by_capsule_id(capsule_id)
                
                if activity:
                    # Cache for future requests
                    await self.redis.cache_activity(capsule_id, activity)
            
            if not activity:
                raise HTTPException(
                    status_code=404,
                    detail=f"Activity not found for capsule {capsule_id}"
                )
            
            return {
                "activity": activity,
                "timestamp": time.time()
            }
        
        @self.app.delete("/activity/{capsule_id}")
        async def delete_activity(capsule_id: str):
            """Delete activity"""
            success = await self.db.delete_activity(capsule_id)
            
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Activity not found for capsule {capsule_id}"
                )
            
            # Invalidate cache
            await self.redis.invalidate_activity_cache(capsule_id)
            
            # Broadcast deletion
            await self.redis.publish_update("capsule_updates", {
                "type": "activity_deleted",
                "capsule_id": capsule_id,
                "timestamp": time.time()
            })
            
            await self._broadcast_update({
                "type": "activity_deleted",
                "capsule_id": capsule_id,
                "timestamp": time.time()
            })
            
            return {
                "success": True,
                "message": f"Activity deleted for capsule {capsule_id}",
                "timestamp": time.time()
            }
        
        @self.app.get("/statistics")
        async def get_statistics():
            """Get service statistics"""
            db_stats = await self.db.get_statistics()
            redis_stats = await self.redis.get_statistics()
            
            return {
                **db_stats,
                "redis": redis_stats,
                "timestamp": time.time()
            }
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates"""
            connection_id = f"ws_{uuid.uuid4().hex[:16]}"
            await self.ws_server.handle_connection(websocket, connection_id)
        
        @self.app.post("/ws/token")
        async def generate_ws_token(user_id: str, device_token: Optional[str] = None):
            """Generate JWT token for WebSocket authentication"""
            token = self.ws_server.generate_jwt_token(user_id, device_token)
            return {
                'token': token,
                'expires_in': 86400,
                'timestamp': time.time()
            }
    

    
    async def _broadcast_update(self, message: Dict):
        """Broadcast update to all WebSocket connections"""
        if self.ws_server:
            await self.ws_server.broadcast_to_all(message)
    
    async def _process_action(
        self,
        activity: Dict,
        action_type: ActionType,
        user_id: Optional[str],
        metadata: Dict
    ) -> Dict[str, Any]:
        """Process capsule action"""
        result = {
            "status": "success",
            "action_type": action_type.value,
            "timestamp": time.time()
        }
        
        if action_type == ActionType.MITIGATE:
            await self.db.update_activity(
                capsule_id=activity["capsule_id"],
                state="resolved"
            )
            result["message"] = "Threat mitigated successfully"
            
        elif action_type == ActionType.INSPECT:
            result["details"] = {
                "utid": activity.get("utid"),
                "metadata": activity.get("metadata"),
                "created_at": str(activity.get("created_at")),
                "updated_at": str(activity.get("updated_at"))
            }
            result["message"] = "Activity inspected"
            
        elif action_type == ActionType.DISMISS:
            await self.db.update_activity(
                capsule_id=activity["capsule_id"],
                state="expired"
            )
            result["message"] = "Activity dismissed"
            
        elif action_type == ActionType.APPROVE:
            await self.db.update_activity(
                capsule_id=activity["capsule_id"],
                metadata={
                    "approved": True,
                    "approved_by": user_id,
                    "approved_at": time.time()
                }
            )
            result["message"] = "Activity approved"
            
        elif action_type == ActionType.REJECT:
            await self.db.update_activity(
                capsule_id=activity["capsule_id"],
                state="expired",
                metadata={
                    "rejected": True,
                    "rejected_by": user_id,
                    "rejected_at": time.time()
                }
            )
            result["message"] = "Activity rejected"
        
        return result
    
    def run(self):
        """Run the service"""
        print(f"🚀 Starting Capsule Gateway Service on port {self.port}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)


# Main entry point
if __name__ == "__main__":
    service = CapsuleGatewayService(port=8210)
    service.run()
