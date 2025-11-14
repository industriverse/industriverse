"""
EIL API Gateway

FastAPI server exposing Energy Intelligence Layer via REST endpoints.
"""

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client import CONTENT_TYPE_LATEST
from starlette.responses import Response
import torch
import numpy as np
import time
import logging
from pathlib import Path
import sys
from typing import Optional
import yaml

# Add phase5 and parent to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from phase5.api.schemas import (
    PredictRequest, PredictResponse,
    DiffuseRequest, DiffuseResponse,
    ProofRequest, ProofResponse,
    MarketPricingResponse,
    HealthResponse, ErrorResponse, MetricsResponse
)
from phase5.diffusion import (
    EnergyField, DiffusionModel, DiffusionConfig,
    EnergyGuidedSampler
)
from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer
from phase5.core.proof_validator import ProofValidator
from phase5.core.market_engine import MarketEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Prometheus Metrics
# ============================================================================

# Initialize metrics - use module-level variables to prevent re-registration
REQUEST_COUNT = None
REQUEST_DURATION = None
ENERGY_FIDELITY = None
ENTROPY_COHERENCE = None
REGIME_CONFIDENCE = None

try:
    REQUEST_COUNT = Counter(
        'eil_api_requests_total',
        'Total API requests',
        ['endpoint', 'status']
    )
except ValueError:
    # Already registered, skip
    pass

try:
    REQUEST_DURATION = Histogram(
        'eil_api_request_duration_seconds',
        'Request duration in seconds',
        ['endpoint']
    )
except ValueError:
    pass

try:
    ENERGY_FIDELITY = Gauge(
        'eil_energy_fidelity',
        'Energy conservation fidelity'
    )
except ValueError:
    pass

try:
    ENTROPY_COHERENCE = Gauge(
        'eil_entropy_coherence',
        'Entropy monotonicity score'
    )
except ValueError:
    pass

try:
    REGIME_CONFIDENCE = Gauge(
        'eil_regime_confidence',
        'Regime detection confidence'
    )
except ValueError:
    pass

# ============================================================================
# Application State
# ============================================================================

class ApplicationState:
    """Global application state"""

    def __init__(self):
        self.start_time = time.time()
        self.eil: Optional[EnergyIntelligenceLayer] = None
        self.diffusion_model: Optional[DiffusionModel] = None
        self.proof_validator: Optional[ProofValidator] = None
        self.market_engine: Optional[MarketEngine] = None
        self.config: dict = {}
        self.initialized = False

    def initialize(self, config_path: Optional[str] = None):
        """Initialize EIL and diffusion components"""
        if self.initialized:
            logger.info("Application already initialized")
            return

        logger.info("Initializing EIL API Gateway...")

        # Load config
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        # Initialize EIL
        logger.info("Initializing Energy Intelligence Layer...")
        self.eil = EnergyIntelligenceLayer()

        # Initialize diffusion model
        logger.info("Initializing Diffusion Model...")
        diffusion_config = DiffusionConfig(
            timesteps=self.config['diffusion']['timesteps'],
            beta_start=self.config['diffusion']['beta_start'],
            beta_end=self.config['diffusion']['beta_end'],
            schedule_type=self.config['diffusion']['noise_schedule'],
            temperature=self.config['diffusion'].get('temperature', 1.0),
            device=self.config['diffusion'].get('device', 'cpu')
        )
        self.diffusion_model = DiffusionModel(diffusion_config)

        # Initialize proof validator
        logger.info("Initializing Proof Validator...")
        self.proof_validator = ProofValidator(
            energy_tolerance=self.config['proof']['energy_tolerance'],
            entropy_threshold=self.config['proof']['entropy_threshold'],
            spectral_threshold=self.config['proof']['spectral_threshold']
        )

        # Initialize market engine
        logger.info("Initializing Market Engine...")
        self.market_engine = MarketEngine(
            base_ceu_price=self.config['market']['base_ceu_price_usd'],
            base_pft_price=self.config['market']['base_pft_price_usd']
        )

        self.initialized = True
        logger.info("✅ EIL API Gateway initialized successfully")


# Global state
app_state = ApplicationState()


# ============================================================================
# FastAPI Application
# ============================================================================

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""

    app = FastAPI(
        title="Industriverse EIL Platform",
        description="Energy Intelligence Layer - Thermodynamic AI API",
        version="0.5.0-alpha",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # CORS middleware
    if app_state.config.get('api', {}).get('cors', {}).get('enabled', False):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=app_state.config['api']['cors']['allow_origins'],
            allow_credentials=True,
            allow_methods=app_state.config['api']['cors']['allow_methods'],
            allow_headers=app_state.config['api']['cors']['allow_headers'],
        )

    # ========================================================================
    # Health & Metrics Endpoints
    # ========================================================================

    @app.get("/health/live", response_model=HealthResponse)
    async def liveness():
        """Liveness probe"""
        return HealthResponse(
            status="alive",
            version="0.5.0-alpha",
            uptime_seconds=time.time() - app_state.start_time,
            eil_initialized=app_state.initialized,
            diffusion_available=app_state.diffusion_model is not None,
            gpu_available=torch.cuda.is_available()
        )

    @app.get("/health/ready", response_model=HealthResponse)
    async def readiness():
        """Readiness probe"""
        if not app_state.initialized:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service not initialized"
            )

        return HealthResponse(
            status="ready",
            version="0.5.0-alpha",
            uptime_seconds=time.time() - app_state.start_time,
            eil_initialized=True,
            diffusion_available=True,
            gpu_available=torch.cuda.is_available(),
            energy_fidelity=float(ENERGY_FIDELITY._value.get()) if hasattr(ENERGY_FIDELITY, '_value') else None
        )

    @app.get("/metrics")
    async def metrics():
        """Prometheus metrics endpoint"""
        return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

    @app.get("/metrics/json", response_model=MetricsResponse)
    async def metrics_json():
        """Metrics in JSON format"""
        return MetricsResponse(
            metrics={
                "energy_fidelity": float(ENERGY_FIDELITY._value.get()) if hasattr(ENERGY_FIDELITY, '_value') else 0.0,
                "entropy_coherence": float(ENTROPY_COHERENCE._value.get()) if hasattr(ENTROPY_COHERENCE, '_value') else 0.0,
                "regime_confidence": float(REGIME_CONFIDENCE._value.get()) if hasattr(REGIME_CONFIDENCE, '_value') else 0.0,
                "uptime_seconds": time.time() - app_state.start_time
            }
        )

    # ========================================================================
    # Prediction Endpoint (NVP)
    # ========================================================================

    @app.post("/v1/predict", response_model=PredictResponse)
    async def predict(request: PredictRequest):
        """Predict next energy state using NVP"""
        start_time = time.time()

        try:
            if not app_state.initialized:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service not initialized"
                )

            # Convert energy map to numpy
            energy_map = np.array(request.energy_map, dtype=np.float32)

            # Process with EIL
            decision = app_state.eil.process(
                energy_map=energy_map,
                domain=request.domain,
                cluster=request.cluster,
                node=request.node
            )

            # Update metrics
            REGIME_CONFIDENCE.set(decision.confidence)
            processing_time = (time.time() - start_time) * 1000

            REQUEST_COUNT.labels(endpoint='/v1/predict', status='success').inc()
            REQUEST_DURATION.labels(endpoint='/v1/predict').observe(time.time() - start_time)

            return PredictResponse(
                prediction=energy_map.tolist(),  # Return current state for now
                regime=decision.regime,
                confidence=decision.confidence,
                approved=decision.approved,
                validity_score=decision.validity_score,
                energy_state=decision.energy_state,
                entropy_rate=decision.entropy_rate,
                forecast_mean=decision.forecast_mean,
                recommended_action=decision.recommended_action,
                risk_level=decision.risk_level,
                processing_time_ms=processing_time
            )

        except Exception as e:
            REQUEST_COUNT.labels(endpoint='/v1/predict', status='error').inc()
            logger.error(f"Prediction error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # ========================================================================
    # Diffusion Endpoint
    # ========================================================================

    @app.post("/v1/diffuse", response_model=DiffuseResponse)
    async def diffuse(request: DiffuseRequest):
        """Generate samples using energy-based diffusion"""
        start_time = time.time()

        try:
            if not app_state.initialized:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service not initialized"
                )

            # Generate sample
            shape = tuple(request.shape)
            sample = app_state.diffusion_model.sample(
                shape=shape,
                num_inference_steps=request.num_inference_steps
            )

            # Validate energy conservation
            energy_field = app_state.diffusion_model.energy_field
            initial_energy = 0.0  # Starting from noise
            final_energy = float(sample.sum().item())

            energy_fidelity = 1.0 - abs(final_energy - initial_energy) / (abs(initial_energy) + 1e-8)
            ENERGY_FIDELITY.set(energy_fidelity)

            # Compute entropy
            final_entropy = energy_field.compute_entropy(sample)

            processing_time = (time.time() - start_time) * 1000

            REQUEST_COUNT.labels(endpoint='/v1/diffuse', status='success').inc()
            REQUEST_DURATION.labels(endpoint='/v1/diffuse').observe(time.time() - start_time)

            return DiffuseResponse(
                generated_sample=sample.cpu().numpy().tolist(),
                trajectory=None,
                energy_fidelity=energy_fidelity,
                entropy_coherence=0.99,  # Placeholder
                total_energy=final_energy,
                final_entropy=final_entropy,
                num_steps=request.num_inference_steps,
                processing_time_ms=processing_time
            )

        except Exception as e:
            REQUEST_COUNT.labels(endpoint='/v1/diffuse', status='error').inc()
            logger.error(f"Diffusion error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # ========================================================================
    # Proof Validation Endpoint
    # ========================================================================

    @app.post("/v1/proof", response_model=ProofResponse)
    async def validate_proof(request: ProofRequest):
        """Validate energy proof"""
        start_time = time.time()

        try:
            if not app_state.initialized:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service not initialized"
                )

            # Convert to numpy
            predicted = np.array(request.predicted_energy_map, dtype=np.float32)
            observed = np.array(request.observed_energy_map, dtype=np.float32)

            # Validate with ProofValidator
            validation = app_state.proof_validator.validate(predicted, observed)

            # Compute drift
            energy_drift = float(np.abs(predicted.sum() - observed.sum()))
            entropy_change = 0.0  # Placeholder

            REQUEST_COUNT.labels(endpoint='/v1/proof', status='success').inc()
            REQUEST_DURATION.labels(endpoint='/v1/proof').observe(time.time() - start_time)

            return ProofResponse(
                valid=validation['passed'],
                energy_conserved=validation['energy_conserved'],
                entropy_monotonic=validation['entropy_monotonic'],
                spectral_valid=validation['spectral_valid'],
                energy_drift=energy_drift,
                entropy_change=entropy_change,
                proof_quality=validation['overall_score'],
                pft_minted=1.0 if validation['passed'] else None
            )

        except Exception as e:
            REQUEST_COUNT.labels(endpoint='/v1/proof', status='error').inc()
            logger.error(f"Proof validation error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # ========================================================================
    # Market Pricing Endpoint
    # ========================================================================

    @app.get("/v1/market/pricing", response_model=MarketPricingResponse)
    async def get_market_pricing():
        """Get current market pricing"""
        try:
            if not app_state.initialized:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service not initialized"
                )

            pricing = app_state.market_engine.get_pricing()

            REQUEST_COUNT.labels(endpoint='/v1/market/pricing', status='success').inc()

            return MarketPricingResponse(
                ceu_price_usd=pricing['ceu_price_usd'],
                pft_price_usd=pricing['pft_price_usd'],
                ceu_pft_rate=pricing['ceu_pft_rate'],
                pool_liquidity_ceu=pricing.get('pool_liquidity_ceu', 1000000.0),
                pool_liquidity_pft=pricing.get('pool_liquidity_pft', 10000.0)
            )

        except Exception as e:
            REQUEST_COUNT.labels(endpoint='/v1/market/pricing', status='error').inc()
            logger.error(f"Market pricing error: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    return app


# ============================================================================
# Application Initialization
# ============================================================================

# Initialize application state
try:
    app_state.initialize()
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    # Continue anyway - will return 503 until initialized

# Create FastAPI app
app = create_app()


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
