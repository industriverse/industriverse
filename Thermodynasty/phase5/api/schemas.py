"""
API Request/Response Schemas

Pydantic models for FastAPI endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime
import numpy as np


# ============================================================================
# Request Schemas
# ============================================================================

class PredictRequest(BaseModel):
    """Request for NVP prediction"""

    energy_map: List[List[float]] = Field(
        ...,
        description="Energy distribution as 2D array",
        example=[[0.1, 0.2], [0.3, 0.4]]
    )

    domain: str = Field(
        ...,
        description="Energy domain identifier",
        example="plasma"
    )

    cluster: str = Field(
        ...,
        description="Cluster name",
        example="production-cluster"
    )

    node: str = Field(
        ...,
        description="Node identifier",
        example="node-001"
    )

    num_steps: Optional[int] = Field(
        1,
        description="Number of prediction steps",
        ge=1,
        le=100
    )

    @field_validator('energy_map')
    @classmethod
    def validate_energy_map(cls, v):
        """Validate energy map is 2D"""
        if not all(isinstance(row, list) for row in v):
            raise ValueError("Energy map must be 2D list")
        if len(set(len(row) for row in v)) > 1:
            raise ValueError("Energy map rows must have same length")
        return v


class DiffuseRequest(BaseModel):
    """Request for diffusion sampling"""

    shape: List[int] = Field(
        ...,
        description="Output shape [height, width]",
        example=[256, 256]
    )

    num_inference_steps: Optional[int] = Field(
        50,
        description="Number of denoising steps",
        ge=1,
        le=1000
    )

    energy_guidance_scale: Optional[float] = Field(
        1.0,
        description="Energy guidance strength",
        ge=0.0,
        le=10.0
    )

    temperature: Optional[float] = Field(
        1.0,
        description="Boltzmann temperature",
        gt=0.0
    )

    initial_state: Optional[List[List[float]]] = Field(
        None,
        description="Optional initial energy map"
    )

    return_trajectory: bool = Field(
        False,
        description="Return full sampling trajectory"
    )


class ProofRequest(BaseModel):
    """Request for proof validation"""

    predicted_energy_map: List[List[float]] = Field(
        ...,
        description="Predicted energy distribution"
    )

    observed_energy_map: List[List[float]] = Field(
        ...,
        description="Observed energy distribution"
    )

    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional validation metadata"
    )


class MarketQueryRequest(BaseModel):
    """Request for market pricing"""

    ceu_amount: Optional[float] = Field(
        None,
        description="CEU amount for price query",
        gt=0
    )

    pft_amount: Optional[float] = Field(
        None,
        description="PFT amount for price query",
        gt=0
    )


# ============================================================================
# Response Schemas
# ============================================================================

class PredictResponse(BaseModel):
    """Response from NVP prediction"""

    prediction: List[List[float]] = Field(
        ...,
        description="Predicted next energy state"
    )

    regime: str = Field(
        ...,
        description="Detected regime",
        example="stable_converging"
    )

    confidence: float = Field(
        ...,
        description="Prediction confidence",
        ge=0.0,
        le=1.0
    )

    approved: bool = Field(
        ...,
        description="Whether decision is approved"
    )

    validity_score: float = Field(
        ...,
        description="Validity score",
        ge=0.0,
        le=1.0
    )

    energy_state: float = Field(
        ...,
        description="Total energy state"
    )

    entropy_rate: float = Field(
        ...,
        description="Entropy change rate"
    )

    forecast_mean: float = Field(
        ...,
        description="Forecast mean value"
    )

    recommended_action: str = Field(
        ...,
        description="Recommended action",
        example="approve"
    )

    risk_level: str = Field(
        ...,
        description="Risk level",
        example="low"
    )

    processing_time_ms: float = Field(
        ...,
        description="Processing time in milliseconds"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class DiffuseResponse(BaseModel):
    """Response from diffusion sampling"""

    generated_sample: List[List[float]] = Field(
        ...,
        description="Generated energy map"
    )

    trajectory: Optional[List[List[List[float]]]] = Field(
        None,
        description="Full sampling trajectory (if requested)"
    )

    energy_fidelity: float = Field(
        ...,
        description="Energy conservation fidelity",
        ge=0.0,
        le=1.0
    )

    entropy_coherence: float = Field(
        ...,
        description="Entropy monotonicity score",
        ge=0.0,
        le=1.0
    )

    total_energy: float = Field(
        ...,
        description="Total energy of sample"
    )

    final_entropy: float = Field(
        ...,
        description="Final entropy value"
    )

    num_steps: int = Field(
        ...,
        description="Number of steps taken"
    )

    processing_time_ms: float = Field(
        ...,
        description="Processing time in milliseconds"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class ProofResponse(BaseModel):
    """Response from proof validation"""

    valid: bool = Field(
        ...,
        description="Whether proof is valid"
    )

    energy_conserved: bool = Field(
        ...,
        description="Energy conservation check passed"
    )

    entropy_monotonic: bool = Field(
        ...,
        description="Entropy monotonicity check passed"
    )

    spectral_valid: bool = Field(
        ...,
        description="Spectral validation passed"
    )

    energy_drift: float = Field(
        ...,
        description="Energy drift (ΔE)"
    )

    entropy_change: float = Field(
        ...,
        description="Entropy change (ΔS)"
    )

    proof_quality: float = Field(
        ...,
        description="Overall proof quality score",
        ge=0.0,
        le=1.0
    )

    pft_minted: Optional[float] = Field(
        None,
        description="PFT tokens minted (if valid)"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class MarketPricingResponse(BaseModel):
    """Response for market pricing"""

    ceu_price: float = Field(
        ...,
        description="Current CEU price in USD"
    )

    pft_price: float = Field(
        ...,
        description="Current PFT price in USD"
    )

    ceu_pft_rate: float = Field(
        ...,
        description="CEU/PFT exchange rate"
    )

    pool_liquidity_ceu: float = Field(
        ...,
        description="CEU liquidity in pool"
    )

    pool_liquidity_pft: float = Field(
        ...,
        description="PFT liquidity in pool"
    )

    last_updated: Optional[str] = Field(
        None,
        description="Last update timestamp"
    )

    quote: Optional[Dict[str, float]] = Field(
        None,
        description="Quote for requested swap"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = Field(
        ...,
        description="Service status",
        example="healthy"
    )

    version: str = Field(
        ...,
        description="API version",
        example="0.5.0-alpha"
    )

    uptime_seconds: float = Field(
        ...,
        description="Uptime in seconds"
    )

    eil_initialized: bool = Field(
        ...,
        description="EIL is initialized"
    )

    diffusion_available: bool = Field(
        ...,
        description="Diffusion engine available"
    )

    gpu_available: bool = Field(
        ...,
        description="GPU acceleration available"
    )

    energy_fidelity: Optional[float] = Field(
        None,
        description="Current energy fidelity metric"
    )

    checks: Optional[Dict[str, bool]] = Field(
        None,
        description="Health check results"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp"
    )


class ErrorResponse(BaseModel):
    """Error response"""

    error: str = Field(
        ...,
        description="Error message"
    )

    error_code: str = Field(
        ...,
        description="Error code",
        example="ENERGY_CONSERVATION_VIOLATION"
    )

    details: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional error details"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )


class MetricsResponse(BaseModel):
    """Metrics response"""

    metrics: Dict[str, float] = Field(
        ...,
        description="Metric name to value mapping"
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Metrics timestamp"
    )
