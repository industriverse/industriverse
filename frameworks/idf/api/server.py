from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import numpy as np
import sys
import os
import shutil
import tempfile
import asyncio
import json
import random
import time

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from frameworks.idf.layers.eil_optimizer import EILOptimizer
from src.data_layer.universal_ingestion.engine import UniversalIngestionEngine
from src.ui_ux_layer.multimodal_bridge.speech_processor import SpeechProcessor
from src.core.orchestration.trifecta_orchestrator import TrifectaOrchestrator

app = FastAPI(title="Industriverse Diffusion Framework (IDF)", version="2.0.0")

# Global instances
optimizer = None
ingestion_engine = UniversalIngestionEngine()
speech_processor = SpeechProcessor()
trifecta_orchestrator = TrifectaOrchestrator()

# WebSocket Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                # Handle disconnected clients gracefully
                pass

manager = ConnectionManager()

# --- Data Models ---
class OptimizationRequest(BaseModel):
    map_name: str = "default_map"
    steps: int = 100
    initial_state: Optional[List[float]] = None

class OptimizationResponse(BaseModel):
    final_energy: float
    energy_delta: float
    entropy: float
    converged: bool
    final_state_sample: List[float]

class IngestionRequest(BaseModel):
    source_type: str
    connection_string: str
    query: Optional[str] = None
    mapping: Optional[Dict[str, str]] = None

class TrifectaRequest(BaseModel):
    goal: str
    persona: str = "Operator"

# --- Background Simulation (The Pulse) ---
async def simulate_system_pulse():
    """
    Simulates the thermodynamic heartbeat of the Industriverse.
    Broadcasts metrics every second.
    """
    while True:
        # Simulate fluctuating metrics
        metrics = {
            "total_power_watts": 45000 + random.uniform(-500, 500),
            "avg_temperature_c": 42.0 + random.uniform(-0.5, 0.5),
            "system_entropy": 0.15 + random.uniform(-0.01, 0.01)
        }
        
        pulse_data = {
            "type": "system_heartbeat",
            "timestamp": time.time(),
            "metrics": metrics
        }
        
        await manager.broadcast(pulse_data)
        await asyncio.sleep(1)

@app.on_event("startup")
async def startup_event():
    global optimizer
    optimizer = EILOptimizer()
    # Start the pulse
    asyncio.create_task(simulate_system_pulse())

# --- WebSocket Endpoint ---
@app.websocket("/ws/pulse")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive, maybe handle incoming control messages later
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- REST Endpoints ---

@app.get("/api/capsules/{capsule_id}")
async def get_capsule_data(capsule_id: str):
    """
    Returns real-time data for a specific capsule to power the Portals.
    """
    # In a real system, this would query the DB or the running Agent.
    # For now, we simulate "live" data based on the ID.
    
    base_response = {
        "id": capsule_id,
        "status": "active",
        "timestamp": time.time()
    }

    if "fusion" in capsule_id or "physics" in capsule_id:
        return {
            **base_response,
            "type": "physics",
            "data": {
                "plasma_temp": 150000000 + random.uniform(-1000000, 1000000),
                "magnetic_field": 12.5 + random.uniform(-0.1, 0.1),
                "stability_index": 0.98 + random.uniform(-0.02, 0.01),
                "energy_output_mw": 500 + random.uniform(-10, 10)
            }
        }
    
    if "bio" in capsule_id or "protein" in capsule_id:
        return {
            **base_response,
            "type": "bio",
            "data": {
                "folding_progress": 99.9,
                "rmsd_accuracy": 0.15 + random.uniform(-0.01, 0.01),
                "active_ligands": 142,
                "reaction_rate": 1.5e6
            }
        }

    if "space" in capsule_id or "orbit" in capsule_id:
        return {
            **base_response,
            "type": "space",
            "data": {
                "altitude_km": 450 + random.uniform(-0.1, 0.1),
                "velocity_kms": 7.8 + random.uniform(-0.01, 0.01),
                "fuel_level": 84.2,
                "threat_level": "LOW"
            }
        }
        
    if "econ" in capsule_id or "token" in capsule_id:
        return {
            **base_response,
            "type": "economy",
            "data": {
                "token_price": 124.50 + random.uniform(-0.5, 0.5),
                "market_cap": 42000000,
                "volume_24h": 1500000,
                "staking_apy": 5.4
            }
        }

    # Default/Generic
    return {
        **base_response,
        "type": "generic",
        "data": {
            "cpu_usage": 45.2,
            "memory_usage": 12.4
        }
    }

@app.post("/diffuse/optimize", response_model=OptimizationResponse)
async def optimize(req: OptimizationRequest):
    global optimizer
    if optimizer.field.map_name != req.map_name:
        optimizer = EILOptimizer(req.map_name)
        
    init_config = None
    if req.initial_state:
        state = np.array(req.initial_state)
        if state.size >= 2:
            init_config = state[:2]
        else:
            init_config = np.random.rand(2) 
        
    result = optimizer.optimize_configuration(initial_config=init_config, steps=req.steps)
    final_flat = np.array(result["final_config"]).flatten().tolist()[:10]
    
    return OptimizationResponse(
        final_energy=result["final_energy"],
        energy_delta=result["energy_delta"],
        entropy=result["trajectory_entropy"],
        converged=result["converged"],
        final_state_sample=final_flat
    )

@app.post("/ingest/universal")
async def ingest_universal(req: IngestionRequest):
    try:
        df = ingestion_engine.ingest_data(req.source_type, req.connection_string, req.query)
        mapping = req.mapping or {}
        energy_map = ingestion_engine.normalize_to_energy_map(df, mapping)
        return {"status": "success", "rows_ingested": len(df), "energy_map_summary": energy_map["node_count"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interact/voice")
async def interact_voice(file: UploadFile = File(...)):
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            shutil.copyfileobj(file.file, temp_audio)
            temp_path = temp_audio.name
            
        text = speech_processor.transcribe_audio_file(temp_path)
        intent = speech_processor.parse_intent(text)
        os.unlink(temp_path)
        return {"transcript": text, "intent": intent}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/trifecta/loop")
async def run_trifecta_loop(req: TrifectaRequest):
    try:
        result = await trifecta_orchestrator.run_conscious_loop(req.goal, req.persona)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "active", "layer": "IDF Phase 5", "modules": ["Diffusion", "Ingestion", "Voice", "Pulse"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
