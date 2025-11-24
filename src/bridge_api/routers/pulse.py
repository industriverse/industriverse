from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from src.bridge_api.event_bus import GlobalEventBus
import asyncio
import json
import random
from datetime import datetime

router = APIRouter(tags=["pulse"])

@router.websocket("/ws/pulse")
async def pulse_websocket(websocket: WebSocket):
    """
    "The Pulse": A unified stream of System Heartbeats.
    Aggregates:
    - Hardware Telemetry (Energy Atlas)
    - AI Agent Actions (ACE/DGM)
    - Security Events (Shield)
    """
    await websocket.accept()
    
    async def send_event(event: dict):
        try:
            await websocket.send_json(event)
        except:
            pass
            
    # Subscribe to the Global Event Bus (Shield & Agent events)
    GlobalEventBus.subscribe(send_event)
    
    try:
        while True:
            # Also emit periodic "Heartbeat" events from the Energy Atlas
            # In a real system, this would be pushed by the Atlas
            # Here we simulate a 1Hz heartbeat
            heartbeat = {
                "type": "system_heartbeat",
                "timestamp": datetime.now().isoformat(),
                "metrics": {
                    "total_power_watts": 450.0 + random.gauss(0, 10),
                    "avg_temperature_c": 65.0 + random.gauss(0, 2),
                    "system_entropy": 0.4 + random.random() * 0.1
                }
            }
            try:
                from src.bridge_api.telemetry.thermo import thermo_metrics
                metrics = thermo_metrics.current_metrics()
                heartbeat["metrics"].update(metrics)
            except Exception:
                pass
            await websocket.send_json(heartbeat)
            # Send current shield state snapshot
            from src.bridge_api.ai_shield.state import shield_state
            await websocket.send_json({"type": "shield_state", **shield_state.get()})
            await asyncio.sleep(1.0)
            
    except WebSocketDisconnect:
        GlobalEventBus.unsubscribe(send_event)
