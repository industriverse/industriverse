#!/usr/bin/env python3
"""
ACE Inference API Server - Phase 5 Enterprise Integration Layer
FastAPI server for real-time thermodynamic inference with Shadow Ensemble consensus

Integrates:
- ACE cognitive architecture from Phase 4
- THRML-inspired energy-based computation patterns
- Shadow Ensemble Byzantine Fault Tolerance
- Thermal Tap delta patching
- Proof Economy hooks
"""

import os
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import time
import hashlib
import json

import numpy as np
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator
import jax
import jax.numpy as jnp

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from phase5.consensus.shadow_ensemble import ShadowEnsemble
from phase5.adapters.thermal_tap import ThermalTap
from phase5.validation.metrics import compute_energy_fidelity, compute_entropy_coherence
from phase5.data.loaders import load_checkpoint
from phase4.ace import ACEAgent, ACEConfig

# ============================================================================
# Configuration
# ============================================================================

class ServerConfig:
    """Server configuration from environment"""
    MODEL_DIR = os.getenv("ACE_MODEL_DIR", "/models")
    PYRAMID_DIR = os.getenv("THERMAL_PYRAMID_DIR", "/data/pyramids")
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")
    ENABLE_PROOF_ECONOMY = os.getenv("ENABLE_PROOF_ECONOMY", "false").lower() == "true"

    # THRML-inspired temperature parameter for exploration/exploitation
    BETA_TEMPERATURE = float(os.getenv("BETA_TEMPERATURE", "1.0"))

    # Consensus thresholds
    CONSENSUS_PIXEL_TOL = float(os.getenv("CONSENSUS_PIXEL_TOL", "1e-3"))
    CONSENSUS_ENERGY_TOL = float(os.getenv("CONSENSUS_ENERGY_TOL", "0.01"))
    CONSENSUS_MIN_VOTES = int(os.getenv("CONSENSUS_MIN_VOTES", "2"))

    # Performance
    MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "16"))
    INFERENCE_TIMEOUT = int(os.getenv("INFERENCE_TIMEOUT", "30"))

config = ServerConfig()

# ============================================================================
# API Models
# ============================================================================

class PredictRequest(BaseModel):
    """Prediction request schema"""
    domain: str = Field(..., description="Physical domain (plasma_physics, fluid_dynamics, etc.)")
    energy_map: List[List[float]] = Field(..., description="2D energy map (normalized float32)")
    num_steps: int = Field(10, ge=1, le=100, description="Number of timesteps to predict")
    agent_mode: str = Field("ensemble", description="Agent mode: single|socratic|ensemble")
    beta: Optional[float] = Field(None, description="Temperature parameter (THRML-inspired)")
    return_confidence_map: bool = Field(True, description="Include per-pixel confidence")
    enable_proof: bool = Field(True, description="Generate Proof Economy record")

    @validator('energy_map')
    def validate_energy_map(cls, v):
        """Validate energy map dimensions and values"""
        if not v or not v[0]:
            raise ValueError("energy_map cannot be empty")
        height = len(v)
        width = len(v[0])
        if not all(len(row) == width for row in v):
            raise ValueError("energy_map must be rectangular")
        if width not in [64, 128, 256] or height not in [64, 128, 256]:
            raise ValueError("energy_map dimensions must be power of 2 (64, 128, or 256)")
        # Check for physical validity
        flat = [val for row in v for val in row]
        if any(val < 0 for val in flat):
            raise ValueError("Energy values cannot be negative")
        if all(val == 0 for val in flat):
            raise ValueError("Energy map cannot be all zeros")
        return v

    @validator('agent_mode')
    def validate_mode(cls, v):
        if v not in ['single', 'socratic', 'ensemble']:
            raise ValueError("agent_mode must be one of: single, socratic, ensemble")
        return v

class PredictResponse(BaseModel):
    """Prediction response schema"""
    predictions: List[List[List[float]]] = Field(..., description="Predicted energy maps (steps, height, width)")
    confidence_map: Optional[List[List[float]]] = Field(None, description="Per-pixel confidence")
    energy_fidelity: float = Field(..., description="Energy conservation metric [0-1]")
    entropy_coherence: float = Field(..., description="Entropy consistency metric [0-1]")
    aspiration_rate: float = Field(..., description="ACE goal achievement rate [0-1]")
    consensus_votes: Optional[Dict[str, bool]] = Field(None, description="Per-model consensus votes")
    proof_id: Optional[str] = Field(None, description="Proof Economy proof identifier")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status: healthy|degraded|unhealthy")
    models_loaded: int = Field(..., description="Number of models loaded")
    inference_ready: bool = Field(..., description="Ready to accept inference requests")
    uptime_seconds: float = Field(..., description="Service uptime")
    version: str = Field("1.0.0-phase5", description="Service version")

class ModelInfo(BaseModel):
    """Model information"""
    model_id: str
    checkpoint_path: str
    domain: str
    metrics: Dict[str, float]
    loaded: bool

class ValidationRequest(BaseModel):
    """HDF5 validation request"""
    hdf5_uri: str = Field(..., description="HDF5 file path or S3 URI")
    domain: str = Field(..., description="Physical domain")
    num_sequences: int = Field(5, ge=1, le=100, description="Number of sequences to validate")

# ============================================================================
# FastAPI Application
# ============================================================================

app = FastAPI(
    title="Thermodynasty ACE Server",
    description="Enterprise Integration Layer for Thermodynamic Intelligence",
    version="1.0.0-phase5",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Global state
class ServerState:
    """Global server state"""
    def __init__(self):
        self.start_time = time.time()
        self.ensemble: Optional[ShadowEnsemble] = None
        self.thermal_tap: Optional[ThermalTap] = None
        self.models_loaded = False
        self.inference_count = 0
        self.error_count = 0

state = ServerState()

# ============================================================================
# Startup & Shutdown
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize models and services on startup"""
    print("=" * 70)
    print("THERMODYNASTY ACE SERVER - PHASE 5")
    print("=" * 70)

    try:
        # Load Shadow Ensemble
        checkpoint_dir = Path(config.MODEL_DIR)
        checkpoints = sorted(checkpoint_dir.glob("*.flax"))

        if not checkpoints:
            print(f"⚠️  No checkpoints found in {checkpoint_dir}")
            print("   Server will start in limited mode")
            state.ensemble = None
        else:
            print(f"Loading {len(checkpoints)} model checkpoints...")
            # Take up to 3 checkpoints for ensemble
            ensemble_checkpoints = [str(cp) for cp in checkpoints[:3]]
            state.ensemble = ShadowEnsemble(
                checkpoints=ensemble_checkpoints,
                pixel_tol=config.CONSENSUS_PIXEL_TOL,
                energy_tol=config.CONSENSUS_ENERGY_TOL,
                min_votes=config.CONSENSUS_MIN_VOTES
            )
            print(f"✓ Shadow Ensemble loaded with {len(ensemble_checkpoints)} models")
            state.models_loaded = True

        # Initialize Thermal Tap
        state.thermal_tap = ThermalTap(
            pyramid_dir=config.PYRAMID_DIR,
            neo4j_uri=config.NEO4J_URI if config.NEO4J_URI != "bolt://localhost:7687" else None,
            neo4j_user=config.NEO4J_USER,
            neo4j_password=config.NEO4J_PASSWORD
        )
        print(f"✓ Thermal Tap initialized: {config.PYRAMID_DIR}")

        print("\nConfiguration:")
        print(f"  Beta Temperature: {config.BETA_TEMPERATURE}")
        print(f"  Consensus Tolerances: pixel={config.CONSENSUS_PIXEL_TOL}, energy={config.CONSENSUS_ENERGY_TOL}")
        print(f"  Proof Economy: {'Enabled' if config.ENABLE_PROOF_ECONOMY else 'Disabled'}")
        print("=" * 70)
        print("✓ Server ready for inference")
        print("=" * 70)

    except Exception as e:
        print(f"❌ Startup error: {e}")
        import traceback
        traceback.print_exc()
        state.models_loaded = False

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\nShutting down Thermodynasty ACE Server...")
    if state.thermal_tap:
        state.thermal_tap.close()
    print("✓ Shutdown complete")

# ============================================================================
# Authentication & Authorization
# ============================================================================

async def verify_token(authorization: Optional[str] = Header(None)) -> Dict[str, Any]:
    """Verify JWT token (stub - integrate with ASAL)"""
    # TODO: Integrate with ASAL Consciousness authentication
    if authorization and authorization.startswith("Bearer "):
        token = authorization[7:]
        # Stub verification
        return {"user_id": "stub_user", "roles": ["inference"]}
    return {"user_id": "anonymous", "roles": ["inference"]}

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/v1/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for liveness/readiness probes"""
    uptime = time.time() - state.start_time

    # Determine health status
    if not state.models_loaded:
        status = "degraded"
    elif state.error_count > 10:
        status = "degraded"
    else:
        status = "healthy"

    return HealthResponse(
        status=status,
        models_loaded=len(state.ensemble.models) if state.ensemble else 0,
        inference_ready=state.models_loaded,
        uptime_seconds=uptime
    )

@app.get("/v1/models", response_model=List[ModelInfo])
async def list_models(user: Dict = Depends(verify_token)):
    """List available models and their status"""
    if not state.ensemble:
        return []

    models = []
    for i, model in enumerate(state.ensemble.models):
        models.append(ModelInfo(
            model_id=f"model_{i}",
            checkpoint_path=state.ensemble.checkpoint_paths[i],
            domain=getattr(model, 'domain', 'unknown'),
            metrics=getattr(model, 'metrics', {}),
            loaded=True
        ))
    return models

@app.post("/v1/predict", response_model=PredictResponse)
async def predict(
    request: PredictRequest,
    user: Dict = Depends(verify_token)
):
    """
    Perform thermodynamic inference with Shadow Ensemble consensus

    This endpoint accepts energy maps and predicts future timesteps using
    ACE cognitive architecture with Byzantine Fault Tolerance.
    """
    if not state.ensemble:
        raise HTTPException(status_code=503, detail="Models not loaded. Server in limited mode.")

    start_time = time.time()

    try:
        # Convert to numpy array
        energy_map = np.array(request.energy_map, dtype=np.float32)

        # Apply temperature scaling if provided (THRML-inspired)
        beta = request.beta if request.beta is not None else config.BETA_TEMPERATURE
        if beta != 1.0:
            # Temperature scaling for exploration/exploitation
            energy_map = energy_map ** (1.0 / beta)
            energy_map = energy_map / energy_map.sum() * energy_map.shape[0] * energy_map.shape[1]

        # Coarse-to-fine gating for performance
        resolution = energy_map.shape[0]
        use_coarse_gate = resolution > 128

        if use_coarse_gate:
            # Quick coarse check at 64x64
            coarse = jnp.array(energy_map[::4, ::4])  # Downsample
            coarse_confidence = state.ensemble.quick_confidence(coarse)

            # If coarse confidence is very high and regime stable, can skip full inference
            # For now, always run full inference (can optimize later)

        # Run Shadow Ensemble inference
        result = state.ensemble.predict(
            energy_map=energy_map,
            domain=request.domain,
            num_steps=request.num_steps,
            mode=request.agent_mode,
            return_confidence=request.return_confidence_map
        )

        # Generate proof if requested
        proof_id = None
        if request.enable_proof and config.ENABLE_PROOF_ECONOMY:
            proof_id = _generate_proof(
                predictions=result['predictions'],
                domain=request.domain,
                models=state.ensemble.checkpoint_paths,
                energy_fidelity=result['energy_fidelity'],
                entropy_coherence=result['entropy_coherence']
            )

        # Update metrics
        state.inference_count += 1
        inference_time = time.time() - start_time

        # Prepare response
        response = PredictResponse(
            predictions=result['predictions'].tolist(),
            confidence_map=result.get('confidence_map', [[0.99]]).tolist() if request.return_confidence_map else None,
            energy_fidelity=float(result['energy_fidelity']),
            entropy_coherence=float(result['entropy_coherence']),
            aspiration_rate=float(result.get('aspiration_rate', 1.0)),
            consensus_votes=result.get('consensus_votes'),
            proof_id=proof_id,
            meta={
                'inference_time_ms': inference_time * 1000,
                'resolution': f"{resolution}x{resolution}",
                'beta_temperature': beta,
                'coarse_gate_used': use_coarse_gate,
                'request_id': hashlib.sha256(f"{time.time()}{request.domain}".encode()).hexdigest()[:16]
            }
        )

        return response

    except Exception as e:
        state.error_count += 1
        print(f"❌ Inference error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

@app.post("/v1/validate_hdf5")
async def validate_hdf5(
    request: ValidationRequest,
    user: Dict = Depends(verify_token)
):
    """
    Validate model predictions against ground truth HDF5 simulation data

    This endpoint will be used when external drive with real physics datasets is connected.
    """
    if not state.ensemble:
        raise HTTPException(status_code=503, detail="Models not loaded")

    # Import validator
    from phase5.validation.hdf5_validator import HDF5Validator

    try:
        validator = HDF5Validator(model=state.ensemble)

        # Run validation
        report = validator.validate(
            hdf5_uri=request.hdf5_uri,
            domain=request.domain,
            num_sequences=request.num_sequences
        )

        return JSONResponse(content=report)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/v1/metrics")
async def get_metrics():
    """Prometheus-compatible metrics endpoint"""
    uptime = time.time() - state.start_time

    metrics = []
    metrics.append(f"# HELP ace_inference_total Total number of inferences")
    metrics.append(f"# TYPE ace_inference_total counter")
    metrics.append(f"ace_inference_total {state.inference_count}")

    metrics.append(f"# HELP ace_errors_total Total number of errors")
    metrics.append(f"# TYPE ace_errors_total counter")
    metrics.append(f"ace_errors_total {state.error_count}")

    metrics.append(f"# HELP ace_uptime_seconds Server uptime in seconds")
    metrics.append(f"# TYPE ace_uptime_seconds gauge")
    metrics.append(f"ace_uptime_seconds {uptime}")

    metrics.append(f"# HELP ace_models_loaded Number of models loaded")
    metrics.append(f"# TYPE ace_models_loaded gauge")
    metrics.append(f"ace_models_loaded {len(state.ensemble.models) if state.ensemble else 0}")

    return "\n".join(metrics)

# ============================================================================
# Helper Functions
# ============================================================================

def _generate_proof(
    predictions: np.ndarray,
    domain: str,
    models: List[str],
    energy_fidelity: float,
    entropy_coherence: float
) -> str:
    """Generate Proof Economy record"""
    proof = {
        'domain': domain,
        'timestamp': time.time(),
        'predicted_hash': hashlib.sha256(predictions.tobytes()).hexdigest(),
        'observed_hash': None,  # Filled later when telemetry arrives
        'models': [Path(m).name for m in models],
        'energy_predicted': float(predictions.sum()),
        'energy_fidelity': energy_fidelity,
        'entropy_coherence': entropy_coherence,
        'signatures': []  # To be filled by signing service
    }

    proof_id = f"proof-{hashlib.sha256(json.dumps(proof, sort_keys=True).encode()).hexdigest()[:16]}"
    proof['proof_id'] = proof_id

    # TODO: Persist to Neo4j and emit to thermodynasty.audit Kafka topic

    return proof_id

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    print(f"\nStarting ACE Server on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True
    )
