"""
Phase 5 API Gateway

REST and gRPC endpoints for Energy Intelligence Layer.
"""

from .eil_gateway import app, create_app
from .schemas import (
    PredictRequest,
    PredictResponse,
    DiffuseRequest,
    DiffuseResponse,
    ProofRequest,
    ProofResponse,
    MarketPricingResponse,
    HealthResponse
)

__all__ = [
    'app',
    'create_app',
    'PredictRequest',
    'PredictResponse',
    'DiffuseRequest',
    'DiffuseResponse',
    'ProofRequest',
    'ProofResponse',
    'MarketPricingResponse',
    'HealthResponse',
]
