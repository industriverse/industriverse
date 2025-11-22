from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

# Import Security Components
from src.bridge_api.middlewares.utid_middleware import UTIDMiddleware
from src.bridge_api.middlewares.proof_middleware import ProofMiddleware
from src.bridge_api.middlewares.ai_shield_middleware import AIShieldMiddleware
from src.bridge_api.controllers import proof_controller

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
