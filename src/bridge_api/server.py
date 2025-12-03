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
    version="0.1.0"
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
# --- MCP Integration (Lightweight Adapter) ---
class MCPAdapter:
    def __init__(self, app: FastAPI):
        self.app = app
        self.tools = []

    def tool(self):
        def decorator(func):
            self.tools.append({
                "name": func.__name__,
                "description": func.__doc__,
                "parameters": func.__annotations__
            })
            return func
        return decorator

    def expose_tools(self):
        @self.app.get("/mcp/tools")
        async def list_tools():
            return {"tools": self.tools}

mcp = MCPAdapter(app)

# --- A2A Integration ---
from src.capsule_layer.services.a2a_agent_integration import registry, host_agent, WorkflowRequest

@app.get("/agents")
async def list_agents():
    """List all registered agents."""
    return registry.list_agents()

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get details of a specific agent."""
    agent = registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@app.post("/orchestrate")
async def orchestrate_workflow(request: WorkflowRequest):
    """Orchestrate a workflow using A2A agents."""
    return await host_agent.orchestrate_workflow(request)

# Expose thermodynamic endpoints as MCP tools
@mcp.tool()
async def get_thermodynamic_state(capsule_id: str):
    """Get the thermodynamic state of a capsule."""
    # Mock implementation
    return {"entropy": 0.5, "energy": 100}

mcp.expose_tools()

# --- Existing Routes ---
app.include_router(capsule_router.router, prefix="/capsules", tags=["Capsules"])
app.include_router(orchestrator_router.router, prefix="/api/v1")
app.include_router(utid_controller.router)
app.include_router(shield_controller.router)
app.include_router(proof_lineage_controller.router)
app.include_router(proof_graph_controller.router)

from src.bridge_api.routers import capsule_router
app.include_router(capsule_router.router)

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

# 7. SCF Control Endpoint (Daemon Orchestration)
from pydantic import BaseModel
import json
import os

class SCFControlCommand(BaseModel):
    command: str
    payload: Dict[str, Any] = {}

@app.post("/scf/control")
async def scf_control(cmd: SCFControlCommand):
    """
    Sends a control command to the SCF Sovereign Daemon.
    """
    control_file = "data/scf/control.json"
    os.makedirs(os.path.dirname(control_file), exist_ok=True)
    
    try:
        with open(control_file, 'w') as f:
            json.dump(cmd.dict(), f)
        return {"status": "sent", "command": cmd.command}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to write control file: {str(e)}")

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

# 6. Shadow Twin WebSocket (Phase 4)
from src.twin_sync.ws_server import handle_websocket
from src.twin_sync.bus_emitter import twin_emitter

@app.on_event("startup")
async def startup_event():
    twin_emitter.start()

@app.websocket("/ws/pulse")
async def pulse_websocket(websocket: WebSocket):
    await handle_websocket(websocket)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
