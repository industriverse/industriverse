from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import numpy as np
import sys
import os
import shutil
import tempfile

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from frameworks.idf.layers.eil_optimizer import EILOptimizer
from src.data_layer.universal_ingestion.engine import UniversalIngestionEngine
from src.ui_ux_layer.multimodal_bridge.speech_processor import SpeechProcessor

app = FastAPI(title="Industriverse Diffusion Framework (IDF)", version="1.1.0")

from src.core.orchestration.trifecta_orchestrator import TrifectaOrchestrator

# Global instances
optimizer = None
ingestion_engine = UniversalIngestionEngine()
speech_processor = SpeechProcessor()
trifecta_orchestrator = TrifectaOrchestrator()

class OptimizationRequest(BaseModel):
    map_name: str = "default_map"
    steps: int = 100
    initial_state: Optional[List[float]] = None # Flattened

class OptimizationResponse(BaseModel):
    final_energy: float
    energy_delta: float
    entropy: float
    converged: bool
    final_state_sample: List[float] # Sample of the config

class IngestionRequest(BaseModel):
    source_type: str # 'file' or 'sql'
    connection_string: str
    query: Optional[str] = None
    mapping: Optional[Dict[str, str]] = None

class TrifectaRequest(BaseModel):
    goal: str
    persona: str = "Operator"

@app.on_event("startup")
async def startup_event():
    global optimizer
    optimizer = EILOptimizer()

@app.post("/diffuse/optimize", response_model=OptimizationResponse)
async def optimize(req: OptimizationRequest):
    """
    Run energy-guided diffusion to optimize a configuration.
    """
    global optimizer
    if optimizer.field.map_name != req.map_name:
        optimizer = EILOptimizer(req.map_name)
        
    init_config = None
    if req.initial_state:
        # Take first 2 dimensions for 2D optimization
        # If input is smaller than 2, pad with random
        state = np.array(req.initial_state)
        if state.size >= 2:
            init_config = state[:2]
        else:
            init_config = np.random.rand(2) 
        
    result = optimizer.optimize_configuration(initial_config=init_config, steps=req.steps)
    
    # Flatten final config for response (just a sample to avoid huge payload)
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
    """
    Ingest data from enterprise sources.
    """
    try:
        df = ingestion_engine.ingest_data(req.source_type, req.connection_string, req.query)
        mapping = req.mapping or {}
        energy_map = ingestion_engine.normalize_to_energy_map(df, mapping)
        return {"status": "success", "rows_ingested": len(df), "energy_map_summary": energy_map["node_count"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/interact/voice")
async def interact_voice(file: UploadFile = File(...)):
    """
    Process voice command and return intent/action.
    """
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
    """
    Execute the Trifecta Conscious Loop.
    """
    try:
        result = await trifecta_orchestrator.run_conscious_loop(req.goal, req.persona)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "active", "layer": "IDF Phase 5", "modules": ["Diffusion", "Ingestion", "Voice"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
