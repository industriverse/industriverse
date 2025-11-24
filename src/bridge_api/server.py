from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

# Import Security Components
from src.bridge_api.middlewares.utid_middleware import UTIDMiddleware
from src.bridge_api.middlewares.proof_middleware import ProofMiddleware
from src.bridge_api.middlewares.ai_shield_middleware import AIShieldMiddleware
from src.bridge_api.controllers import proof_controller
from src.bridge_api.controllers import utid_controller
from src.bridge_api.controllers import shield_controller
from src.bridge_api.controllers import proof_lineage_controller
from src.bridge_api.controllers import proof_graph_controller

app = FastAPI(
    title="Industriverse Bridge API",
    description="Unified gateway for all Industriverse services (Trifecta, Expansion Packs, AI Shield)",
    version="1.0.0"
)

# 1. Security Middlewares (Order matters!)
app.add_middleware(AIShieldMiddleware) # Outer layer: Safety check
app.add_middleware(ProofMiddleware)    # Inject proof context
app.add_middleware(UTIDMiddleware)     # Verify identity

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Register Routers
app.include_router(proof_controller.router)
app.include_router(utid_controller.router)
app.include_router(shield_controller.router)
app.include_router(proof_lineage_controller.router)
app.include_router(proof_graph_controller.router)

# 4. Register Thermodynamic Router (Grand Unification)
# Some optional dependencies (e.g., flax) may not be present in minimal test envs.
try:
    from src.bridge_api.thermodynamic_router import create_bridge_api
    bridge_api = create_bridge_api()
    app.include_router(bridge_api.router)
except ImportError as e:
    # Degrade gracefully when optional thermodynamic deps are absent
    import logging

    logging.warning(f"Thermodynamic router not loaded: {e}")

# 5. Register White-Label Partner Router
try:
    from src.white_label.partner_portal.configuration_api import router as partner_router

    app.include_router(partner_router, prefix="/v1/white-label", tags=["White Label"])
except ImportError as e:
    import logging

    logging.warning(f"White-label partner routes not loaded: {e}")

# 6. Register "The Pulse" Router (Grand Unification)
from src.bridge_api.routers import pulse
app.include_router(pulse.router)

@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Industriverse Bridge API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Placeholder for Protocol Adapters
@app.get("/adapters/mcp/status")
async def mcp_adapter_status():
    return {"adapter": "MCP", "status": "connected (simulated)"}

@app.get("/adapters/a2a/status")
async def a2a_adapter_status():
    return {"adapter": "A2A", "status": "connected (simulated)"}

# 5. AI Shield WebSocket
from fastapi import WebSocket, WebSocketDisconnect
from src.bridge_api.event_bus import GlobalEventBus

@app.websocket("/ws/shield")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    async def send_event(event: dict):
        try:
            await websocket.send_json(event)
        except:
            pass
            
    GlobalEventBus.subscribe(send_event)
    
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        GlobalEventBus.unsubscribe(send_event)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
