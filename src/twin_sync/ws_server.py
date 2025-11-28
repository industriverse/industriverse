"""
WebSocket server for Shadow Twin streaming.
Broadcasts telemetry events to connected clients.
"""

import asyncio
import json
import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return
            
        # Serialize once
        text = json.dumps(message)
        
        # Broadcast to all
        to_remove = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(text)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                to_remove.add(connection)
        
        for conn in to_remove:
            self.disconnect(conn)

manager = ConnectionManager()

async def handle_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and handle incoming messages (e.g. subscriptions)
            # For now, just echo or ignore
            data = await websocket.receive_text()
            # Optional: handle heartbeat or subscription requests
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
