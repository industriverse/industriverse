from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
import numpy as np
import sys
import os

# Add root to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../../.."))

from frameworks.idf.layers.eil_optimizer import EILOptimizer

app = FastAPI(title="Industriverse Diffusion Framework (IDF)", version="1.0.0")

# Global optimizer instance (lazy load)
optimizer = None

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
        # Reshape based on map shape (assuming 2D square for simplicity or use field shape)
        # For now, just use random if shape doesn't match, or assume 100x100
        pass 
        
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

@app.get("/health")
async def health():
    return {"status": "active", "layer": "IDF Phase 5"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
