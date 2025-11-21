# BRIDGE API ARCHITECTURE: MCP + A2A + UTID + Proof + AI Shield

**Date**: November 21, 2025
**Purpose**: Unified API gateway for Industriverse platform with identity, proof, and safety layers
**Status**: Design Document - Ready for Implementation

---

## 🎯 EXECUTIVE SUMMARY

The **Bridge API** is the primary entry point for all external interactions with the Industriverse platform. It provides:

1. **Unified REST API** - FastAPI-based HTTP/2 endpoints
2. **MCP + A2A Integration** - Reuses existing overseer system protocol bridges
3. **UTID Middleware** - Universal Trusted Identity verification for all requests
4. **Proof Economy Hooks** - Cryptographic attestation and ZK-proofs for trust
5. **AI Shield v2 Integration** - 5-layer safety validation for all AI operations
6. **Multi-Backend Routing** - Routes to EIL, Trifecta, Expansion Packs, etc.

---

## 📐 ARCHITECTURE OVERVIEW

```
┌────────────────────────────────────────────────────────────────────────┐
│                          CLIENT APPLICATIONS                           │
│  (Web, Mobile, IoT, CLI, External Agents)                             │
└────────────────────────────┬───────────────────────────────────────────┘
                             │ HTTPS/HTTP2 + WebSocket
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         BRIDGE API GATEWAY                             │
│                                                                        │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │                    MIDDLEWARE STACK                          │    │
│  │                                                              │    │
│  │  1. UTID Verification    ← Hardware-bound identity          │    │
│  │  2. Proof Validation     ← ZK-proof + SPA/PCCA             │    │
│  │  3. AI Shield Gateway    ← 5-layer safety pre-check        │    │
│  │  4. Rate Limiting        ← DDoS protection                  │    │
│  │  5. Request Logging      ← Audit trail                      │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                             │                                          │
│  ┌──────────────────────────┴────────────────────────────────┐        │
│  │                  ROUTE CONTROLLERS                         │        │
│  │                                                            │        │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │        │
│  │  │   /eil/     │  │ /trifecta/  │  │  /packs/    │      │        │
│  │  │  (Phase 5)  │  │ (3 Agents)  │  │(20 Pillars) │      │        │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │        │
│  │                                                            │        │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐      │        │
│  │  │   /proof/   │  │   /utid/    │  │   /kaas/    │      │        │
│  │  │ (Economy)   │  │ (Identity)  │  │(Kubernetes) │      │        │
│  │  └─────────────┘  └─────────────┘  └─────────────┘      │        │
│  └────────────────────────────────────────────────────────────┘      │
│                             │                                          │
│  ┌──────────────────────────┴────────────────────────────────┐        │
│  │              PROTOCOL ADAPTERS (EXISTING)                  │        │
│  │                                                            │        │
│  │  ┌────────────────────┐      ┌────────────────────┐      │        │
│  │  │   MCP Bridge       │      │    A2A Bridge      │      │        │
│  │  │  (Model Context)   │◄────►│  (Agent-to-Agent) │      │        │
│  │  │  ✅ Overseer Sys   │      │  ✅ Overseer Sys   │      │        │
│  │  └────────────────────┘      └────────────────────┘      │        │
│  └────────────────────────────────────────────────────────────┘      │
└────────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       BACKEND SERVICES                                 │
│                                                                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐               │
│  │ EIL (Phase5) │  │   Trifecta   │  │  Expansion   │               │
│  │ • MicroAdapt │  │ • UserLM     │  │    Packs     │               │
│  │ • Shadow Ens │  │ • RND1       │  │ • TSC        │               │
│  │ • Market Eng │  │ • ACE        │  │ • UPV        │               │
│  └──────────────┘  └──────────────┘  │ • TIL        │               │
│                                       │ • TSE        │               │
│  ┌──────────────┐  ┌──────────────┐  │ • TSO        │               │
│  │ Proof Economy│  │  AI Shield   │  │ • 100 Cases  │               │
│  │ • Registry   │  │ • 5 Layers   │  └──────────────┘               │
│  │ • SPA/PCCA   │  │ • Heartbeat  │                                  │
│  │ • ZK Proofs  │  │ • Validator  │  ┌──────────────┐               │
│  └──────────────┘  └──────────────┘  │ KaaS Operator│               │
│                                       │ • CRDs       │               │
│  ┌──────────────┐  ┌──────────────┐  │ • Webhooks   │               │
│  │    UTID      │  │     IDF      │  │ • Controllers│               │
│  │ • Generator  │  │ • Diffusion  │  └──────────────┘               │
│  │ • Validator  │  │ • Boltzmann  │                                  │
│  └──────────────┘  └──────────────┘                                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 MIDDLEWARE STACK (Request Processing Pipeline)

### 1. UTID Verification Middleware

**Purpose**: Verify Universal Trusted Identity for all requests

**File**: `src/bridge_api/middlewares/utid_middleware.py`

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.utid.core.utid_generator import UTIDValidator
from src.proof_economy.core.proof_registry import ProofRegistry

class UTIDMiddleware(BaseHTTPMiddleware):
    """
    UTID Verification Middleware

    Validates Universal Trusted Identity on every request.

    UTID Components:
    1. Hardware Entropy (eSIM, RF fingerprint)
    2. Physics-Domain Signature (thermodynamic hash)
    3. Cryptographic ZK-Signature
    4. Verifiable Computation Hash
    """

    def __init__(self, app, utid_validator: UTIDValidator):
        super().__init__(app)
        self.validator = utid_validator

    async def dispatch(self, request: Request, call_next):
        # Extract UTID from request header
        utid_token = request.headers.get("X-UTID-Token")

        if not utid_token:
            raise HTTPException(
                status_code=401,
                detail="Missing UTID token. All requests must include X-UTID-Token header."
            )

        # Validate UTID
        try:
            utid_claims = await self.validator.validate_token(utid_token)

            # Check hardware binding
            if not utid_claims.hardware_bound:
                raise HTTPException(
                    status_code=403,
                    detail="UTID not hardware-bound. Device attestation required."
                )

            # Check physics signature
            if not utid_claims.physics_signature_valid:
                raise HTTPException(
                    status_code=403,
                    detail="Physics signature invalid. Thermodynamic hash mismatch."
                )

            # Check ZK proof
            if not utid_claims.zk_proof_valid:
                raise HTTPException(
                    status_code=403,
                    detail="Zero-knowledge proof invalid."
                )

            # Attach UTID claims to request state
            request.state.utid_claims = utid_claims
            request.state.user_id = utid_claims.user_id
            request.state.device_id = utid_claims.device_id

        except Exception as e:
            raise HTTPException(
                status_code=401,
                detail=f"UTID validation failed: {str(e)}"
            )

        # Continue to next middleware
        response = await call_next(request)

        # Add UTID verification proof to response header
        response.headers["X-UTID-Verified"] = "true"
        response.headers["X-UTID-User-ID"] = request.state.user_id

        return response
```

**Key Features**:
- ✅ Hardware-bound verification (eSIM, RF fingerprint)
- ✅ Physics-domain signature validation (thermodynamic hash)
- ✅ Zero-knowledge proof verification
- ✅ Attach verified identity to request context
- ✅ Response headers include verification proof

---

### 2. Proof Validation Middleware

**Purpose**: Validate cryptographic proofs for high-trust operations

**File**: `src/bridge_api/middlewares/proof_middleware.py`

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.proof_economy.core.proof_registry import ProofRegistry
from src.proof_economy.generators.spa_generator import SPAGenerator
from src.proof_economy.generators.pcca_generator import PCCAGenerator

class ProofMiddleware(BaseHTTPMiddleware):
    """
    Proof Validation Middleware

    Validates cryptographic proofs (SPA, PCCA, ZK) for high-trust operations.

    Proof Types:
    - SPA: Statistical Proof of Attestation
    - PCCA: Physics-Constrained Cryptographic Attestation
    - ZK: Zero-Knowledge Proof
    """

    def __init__(
        self,
        app,
        proof_registry: ProofRegistry,
        spa_generator: SPAGenerator,
        pcca_generator: PCCAGenerator
    ):
        super().__init__(app)
        self.registry = proof_registry
        self.spa_generator = spa_generator
        self.pcca_generator = pcca_generator

    async def dispatch(self, request: Request, call_next):
        # Check if this endpoint requires proof
        requires_proof = self._endpoint_requires_proof(request.url.path)

        if requires_proof:
            # Extract proof from request header
            proof_token = request.headers.get("X-Proof-Token")
            proof_type = request.headers.get("X-Proof-Type", "SPA")  # Default to SPA

            if not proof_token:
                raise HTTPException(
                    status_code=403,
                    detail="Proof required for this operation. Include X-Proof-Token header."
                )

            # Validate proof based on type
            try:
                if proof_type == "SPA":
                    proof_valid = await self.spa_generator.verify_proof(proof_token)
                elif proof_type == "PCCA":
                    proof_valid = await self.pcca_generator.verify_proof(proof_token)
                elif proof_type == "ZK":
                    proof_valid = await self.registry.verify_zk_proof(proof_token)
                else:
                    raise ValueError(f"Unknown proof type: {proof_type}")

                if not proof_valid:
                    raise HTTPException(
                        status_code=403,
                        detail=f"{proof_type} proof validation failed."
                    )

                # Attach proof metadata to request
                request.state.proof_type = proof_type
                request.state.proof_verified = True

            except Exception as e:
                raise HTTPException(
                    status_code=403,
                    detail=f"Proof validation error: {str(e)}"
                )
        else:
            request.state.proof_verified = False

        # Continue to next middleware
        response = await call_next(request)

        # Add proof verification to response header
        if requires_proof:
            response.headers["X-Proof-Verified"] = "true"
            response.headers["X-Proof-Type"] = proof_type

        return response

    def _endpoint_requires_proof(self, path: str) -> bool:
        """Determine if endpoint requires cryptographic proof"""
        high_trust_patterns = [
            "/eil/market/trade",        # Market trades
            "/trifecta/red-team",       # Red-team operations
            "/kaas/clusters/create",    # Cluster creation
            "/proof/anchor",            # Proof anchoring
        ]
        return any(pattern in path for pattern in high_trust_patterns)
```

**Key Features**:
- ✅ Supports SPA, PCCA, and ZK proof types
- ✅ Configurable proof requirements per endpoint
- ✅ Proof verification using Proof Economy services
- ✅ Metadata attached to request context

---

### 3. AI Shield Gateway Middleware

**Purpose**: Pre-validation of all AI operations using 5-layer safety

**File**: `src/bridge_api/middlewares/ai_shield_middleware.py`

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from src.ai_shield_v2.core.shield_orchestrator import AIShieldOrchestrator
from src.ai_shield_v2.layers.substrate_safety import SubstrateSafetyLayer
from src.ai_shield_v2.layers.structural_safety import StructuralSafetyLayer
from src.ai_shield_v2.layers.semantic_safety import SemanticSafetyLayer
from src.ai_shield_v2.layers.behavioral_safety import BehavioralSafetyLayer
from src.ai_shield_v2.layers.policy_safety import PolicySafetyLayer

class AIShieldMiddleware(BaseHTTPMiddleware):
    """
    AI Shield Gateway Middleware

    Validates all AI operations through 5 safety layers:
    1. Substrate Safety: Physics-based consistency
    2. Structural Safety: DAG validation, digital twin alignment
    3. Semantic Safety: Context-bound reasoning
    4. Behavioral Safety: Runtime anomaly detection
    5. Policy Safety: Regulatory + enterprise compliance
    """

    def __init__(self, app, shield: AIShieldOrchestrator):
        super().__init__(app)
        self.shield = shield

    async def dispatch(self, request: Request, call_next):
        # Check if this is an AI operation
        is_ai_operation = self._is_ai_operation(request.url.path)

        if is_ai_operation:
            # Extract request payload for validation
            try:
                body = await request.body()
                payload = json.loads(body) if body else {}
            except:
                payload = {}

            # Run AI Shield validation
            validation_result = await self.shield.validate_request(
                endpoint=request.url.path,
                method=request.method,
                payload=payload,
                utid_claims=getattr(request.state, 'utid_claims', None)
            )

            if not validation_result.approved:
                # Return which layers failed
                failed_layers = [
                    layer for layer, passed in validation_result.layer_results.items()
                    if not passed
                ]

                raise HTTPException(
                    status_code=403,
                    detail=f"AI Shield blocked request. Failed layers: {failed_layers}",
                    headers={
                        "X-Shield-Status": "blocked",
                        "X-Shield-Reason": validation_result.reason
                    }
                )

            # Attach shield validation to request
            request.state.shield_validated = True
            request.state.shield_layers = validation_result.layer_results
            request.state.shield_score = validation_result.safety_score

        # Continue to next middleware
        response = await call_next(request)

        # Add shield validation to response
        if is_ai_operation:
            response.headers["X-Shield-Validated"] = "true"
            response.headers["X-Shield-Score"] = str(request.state.shield_score)

        return response

    def _is_ai_operation(self, path: str) -> bool:
        """Determine if this is an AI operation requiring shield validation"""
        ai_patterns = [
            "/eil/",            # EIL operations
            "/trifecta/",       # Trifecta agents
            "/packs/",          # Expansion packs
            "/idf/",            # IDF diffusion
        ]
        return any(pattern in path for pattern in ai_patterns)
```

**Key Features**:
- ✅ 5-layer safety validation (Substrate, Structural, Semantic, Behavioral, Policy)
- ✅ Request blocking if safety check fails
- ✅ Detailed failure reasons in response
- ✅ Safety score computed for each request

---

### 4. Rate Limiting Middleware

**Purpose**: DDoS protection and fair usage enforcement

**File**: `src/bridge_api/middlewares/rate_limit_middleware.py`

```python
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate Limiting Middleware

    Implements token bucket algorithm for rate limiting.

    Tiers:
    - Free: 100 req/min
    - Pro: 1000 req/min
    - Enterprise: 10000 req/min
    """

    def __init__(self, app):
        super().__init__(app)
        # user_id -> (tokens, last_refill_time, tier)
        self.buckets: Dict[str, Tuple[int, float, str]] = defaultdict(
            lambda: (100, time.time(), "free")
        )

    async def dispatch(self, request: Request, call_next):
        # Get user ID from UTID claims
        user_id = getattr(request.state, 'user_id', 'anonymous')

        # Get or initialize bucket
        tokens, last_refill, tier = self.buckets[user_id]

        # Determine rate limit based on tier
        rate_limit = self._get_rate_limit(tier)

        # Refill tokens based on time elapsed
        now = time.time()
        elapsed = now - last_refill
        tokens_to_add = int(elapsed * rate_limit / 60)  # tokens per second
        tokens = min(tokens + tokens_to_add, rate_limit)
        last_refill = now

        # Check if request can be served
        if tokens < 1:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Tier: {tier}, Limit: {rate_limit} req/min",
                headers={
                    "X-RateLimit-Limit": str(rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60"
                }
            )

        # Consume one token
        tokens -= 1
        self.buckets[user_id] = (tokens, last_refill, tier)

        # Continue to next middleware
        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(tokens)

        return response

    def _get_rate_limit(self, tier: str) -> int:
        """Get rate limit for user tier"""
        limits = {
            "free": 100,
            "pro": 1000,
            "enterprise": 10000
        }
        return limits.get(tier, 100)
```

**Key Features**:
- ✅ Token bucket algorithm
- ✅ Tiered rate limits (Free, Pro, Enterprise)
- ✅ Per-user tracking via UTID
- ✅ Standard HTTP 429 responses

---

### 5. Request Logging Middleware

**Purpose**: Audit trail for all API requests

**File**: `src/bridge_api/middlewares/logging_middleware.py`

```python
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import time
import logging
import json

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Request Logging Middleware

    Logs all API requests for audit and debugging.

    Logged Data:
    - Request method, path, headers
    - UTID user_id, device_id
    - Proof verification status
    - AI Shield validation results
    - Response status code, latency
    """

    def __init__(self, app):
        super().__init__(app)
        self.logger = logging.getLogger("bridge_api.requests")

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # Log request
        request_log = {
            "timestamp": start_time,
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host,
            "user_id": getattr(request.state, 'user_id', None),
            "device_id": getattr(request.state, 'device_id', None),
            "proof_verified": getattr(request.state, 'proof_verified', False),
            "shield_validated": getattr(request.state, 'shield_validated', False),
        }

        # Process request
        response = await call_next(request)

        # Log response
        end_time = time.time()
        latency = (end_time - start_time) * 1000  # milliseconds

        response_log = {
            **request_log,
            "status_code": response.status_code,
            "latency_ms": latency,
        }

        # Log to structured logger
        self.logger.info(json.dumps(response_log))

        # Add latency header
        response.headers["X-Response-Time-Ms"] = str(int(latency))

        return response
```

**Key Features**:
- ✅ Structured JSON logging
- ✅ Request/response correlation
- ✅ Latency tracking
- ✅ User/device identification
- ✅ Security event logging (UTID, Proof, Shield)

---

## 🛣️ ROUTE CONTROLLERS (API Endpoints)

### 1. EIL Routes (`/eil/*`)

**Purpose**: Access Energy Intelligence Layer (Phase 5) capabilities

**File**: `src/bridge_api/routes/eil_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from src.core_ai_layer.eil.core.energy_intelligence_layer import EnergyIntelligenceLayer, EILContext

router = APIRouter(prefix="/eil", tags=["Energy Intelligence Layer"])

class EILDecisionRequest(BaseModel):
    """Request for EIL decision"""
    energy_map: List[List[float]]  # 2D energy map
    domain: str
    cluster: str
    context: Optional[Dict[str, Any]] = None

class EILDecisionResponse(BaseModel):
    """Response from EIL decision"""
    decision: str
    confidence: float
    energy_fidelity: float
    entropy_coherence: float
    statistical_regime: str
    physics_regime: str
    consensus_achieved: bool
    proof_validated: bool
    metadata: Dict[str, Any]

@router.post("/decide", response_model=EILDecisionResponse)
async def eil_decide(
    request_data: EILDecisionRequest,
    request: Request
):
    """
    Make an EIL decision with dual-branch fusion

    Process:
    1. Statistical branch (40%): MicroAdapt v2 regime detection
    2. Physics branch (60%): Physics-informed decision
    3. Shadow Ensemble: BFT consensus
    4. Proof Validator: Tri-check validation
    5. Market Engine: CEU/PFT token allocation
    """
    # Get EIL service (from dependency injection)
    eil = request.app.state.eil_service

    # Create EIL context
    context = EILContext(
        energy_map=np.array(request_data.energy_map),
        domain=request_data.domain,
        cluster=request_data.cluster
    )

    # Run decision pipeline
    result = await eil.decide(context)

    return EILDecisionResponse(
        decision=result.decision,
        confidence=result.confidence,
        energy_fidelity=result.energy_fidelity,
        entropy_coherence=result.entropy_coherence,
        statistical_regime=result.statistical_regime_id,
        physics_regime=result.physics_regime_label,
        consensus_achieved=result.consensus,
        proof_validated=result.approved,
        metadata=result.metadata
    )

@router.get("/regimes/statistical")
async def get_statistical_regimes(request: Request):
    """Get all statistical regimes (MicroAdapt v2)"""
    eil = request.app.state.eil_service
    regimes = await eil.microadapt.get_all_regimes()
    return {"regimes": regimes}

@router.get("/regimes/physics")
async def get_physics_regimes(request: Request):
    """Get all physics regimes"""
    eil = request.app.state.eil_service
    regimes = await eil.physics_branch.get_all_regimes()
    return {"regimes": regimes}

@router.post("/market/trade")
async def execute_market_trade(
    request: Request,
    trade_data: Dict[str, Any]
):
    """
    Execute CEU/PFT market trade

    Requires: Proof validation (PCCA)
    """
    # Check proof requirement (handled by middleware)
    if not request.state.proof_verified:
        raise HTTPException(403, "Market trades require PCCA proof")

    eil = request.app.state.eil_service
    result = await eil.market_engine.execute_trade(
        user_id=request.state.user_id,
        **trade_data
    )

    return result

@router.get("/metrics")
async def get_eil_metrics(request: Request):
    """Get EIL system metrics"""
    eil = request.app.state.eil_service

    return {
        "total_decisions": eil.metrics.total_decisions,
        "avg_confidence": eil.metrics.avg_confidence,
        "consensus_rate": eil.metrics.consensus_rate,
        "proof_validation_rate": eil.metrics.proof_validation_rate,
        "avg_latency_ms": eil.metrics.avg_latency_ms
    }
```

**Endpoints**:
- `POST /eil/decide` - Make EIL decision with dual-branch fusion
- `GET /eil/regimes/statistical` - Get statistical regimes (MicroAdapt v2)
- `GET /eil/regimes/physics` - Get physics regimes
- `POST /eil/market/trade` - Execute CEU/PFT trade (requires PCCA proof)
- `GET /eil/metrics` - Get EIL system metrics

---

### 2. Trifecta Routes (`/trifecta/*`)

**Purpose**: Access Trifecta multi-agent system (UserLM + RND1 + ACE)

**File**: `src/bridge_api/routes/trifecta_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from src.trifecta.cortex.trifecta_cortex import TrifectaCortex

router = APIRouter(prefix="/trifecta", tags=["Trifecta Multi-Agent"])

class TrifectaPredictionRequest(BaseModel):
    """Request for Trifecta prediction"""
    mode: str  # "defense", "optimization", "threat_prediction"
    context: Dict[str, Any]
    agents: List[str] = ["userlm", "rnd1", "ace"]  # Which agents to use

class TrifectaPredictionResponse(BaseModel):
    """Response from Trifecta prediction"""
    prediction: Dict[str, Any]
    confidence: float
    agent_contributions: Dict[str, Any]
    playbook_executed: Optional[str] = None
    metadata: Dict[str, Any]

@router.post("/predict", response_model=TrifectaPredictionResponse)
async def trifecta_predict(
    request_data: TrifectaPredictionRequest,
    request: Request
):
    """
    Multi-agent Trifecta prediction

    Modes:
    - defense: Red-team defense testing (UserLM → RND1 → ACE)
    - optimization: Resource optimization (ACE → RND1 → UserLM)
    - threat_prediction: Attack prediction (RND1 → UserLM → ACE)
    """
    cortex = request.app.state.trifecta_cortex

    if request_data.mode == "defense":
        result = await cortex.execute_playbook("red_team_defense_test", request_data.context)
    elif request_data.mode == "optimization":
        result = await cortex.execute_playbook("resource_optimization", request_data.context)
    elif request_data.mode == "threat_prediction":
        result = await cortex.predict_and_respond_to_threat(request_data.context)
    else:
        raise HTTPException(400, f"Unknown mode: {request_data.mode}")

    return TrifectaPredictionResponse(**result)

@router.post("/userlm/persona")
async def generate_persona(
    request: Request,
    persona_type: str = "benign",
    attack_vector: Optional[str] = None
):
    """Generate synthetic user persona"""
    cortex = request.app.state.trifecta_cortex

    if persona_type == "adversarial":
        persona = await cortex.userlm.generate_adversarial_persona(attack_vector)
    else:
        persona = await cortex.userlm.generate_persona(persona_type)

    return {"persona": persona.dict()}

@router.post("/rnd1/optimize")
async def optimize_resources(
    request: Request,
    allocation_data: Dict[str, Any]
):
    """Optimize resource allocation using RND1"""
    cortex = request.app.state.trifecta_cortex

    optimized = await cortex.rnd1.optimize_allocation(**allocation_data)

    return {"optimized_allocation": optimized.dict()}

@router.post("/ace/validate")
async def validate_with_ace(
    request: Request,
    validation_data: Dict[str, Any]
):
    """Validate using ACE agent"""
    cortex = request.app.state.trifecta_cortex

    result = await cortex.ace.predict(**validation_data)

    return {"validation_result": result.dict()}
```

**Endpoints**:
- `POST /trifecta/predict` - Multi-agent prediction (defense, optimization, threat)
- `POST /trifecta/userlm/persona` - Generate synthetic persona
- `POST /trifecta/rnd1/optimize` - Optimize resource allocation
- `POST /trifecta/ace/validate` - Validate using ACE agent

---

### 3. Expansion Packs Routes (`/packs/*`)

**Purpose**: Access 20 Pillars across 6 Expansion Packs

**File**: `src/bridge_api/routes/packs_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/packs", tags=["Expansion Packs"])

# Pack 1: TSC (Thermodynamic Signal Compiler)
@router.post("/tsc/ingest")
async def tsc_ingest_signal(request: Request, signal_data: Dict[str, Any]):
    """Ingest signal into TSC"""
    tsc = request.app.state.tsc_service
    return await tsc.ingest(signal_data)

@router.post("/tsc/annotate")
async def tsc_annotate_signal(request: Request, signal_id: str, annotations: Dict):
    """Annotate signal with thermodynamic metadata"""
    tsc = request.app.state.tsc_service
    return await tsc.annotate(signal_id, annotations)

# Pack 2: UPV (Universal Physics Vectorizer)
@router.post("/upv/vectorize")
async def upv_vectorize(request: Request, domain: str, data: Dict[str, Any]):
    """Vectorize domain data into physics representation"""
    upv = request.app.state.upv_service
    return await upv.vectorize(domain, data)

# Pack 4: TIL (Thermodynamic Intelligence Layer v2)
@router.post("/til/coordinate")
async def til_coordinate(request: Request, agents: List[Dict]):
    """Coordinate multiple agents using TIL hierarchy"""
    til = request.app.state.til_service
    return await til.coordinate(agents)

# Pack 5: TSE (Thermodynamic Simulation Engine)
@router.post("/tse/simulate")
async def tse_simulate(request: Request, simulation_config: Dict):
    """Run thermodynamic simulation"""
    tse = request.app.state.tse_service
    return await tse.simulate(simulation_config)

# Pack 6: TSO (Thermodynamic Signal Ontology)
@router.get("/tso/schema")
async def tso_get_schema(request: Request):
    """Get TSO schema"""
    tso = request.app.state.tso_service
    return await tso.get_schema()

# Pack 3: 100 Use Cases
@router.get("/use-cases")
async def list_use_cases(request: Request):
    """List all 100 use case templates"""
    return {"use_cases": request.app.state.use_cases_library.list_all()}

@router.get("/use-cases/{use_case_id}")
async def get_use_case(request: Request, use_case_id: str):
    """Get specific use case template"""
    return request.app.state.use_cases_library.get(use_case_id)
```

**Endpoints**: (20 Pillars total, examples shown)
- `POST /packs/tsc/ingest` - Ingest signal (Pack 1, Pillar 1)
- `POST /packs/tsc/annotate` - Annotate signal (Pack 1, Pillar 2)
- `POST /packs/upv/vectorize` - Vectorize to physics (Pack 2, Pillar 5)
- `POST /packs/til/coordinate` - Coordinate agents (Pack 4, Pillar 13)
- `POST /packs/tse/simulate` - Run simulation (Pack 5, Pillar 17)
- `GET /packs/tso/schema` - Get ontology schema (Pack 6, Pillar 21)
- `GET /packs/use-cases` - List 100 use cases (Pack 3)

---

### 4. Proof Economy Routes (`/proof/*`)

**Purpose**: Access Proof Economy services (SPA, PCCA, ZK proofs)

**File**: `src/bridge_api/routes/proof_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from src.proof_economy.core.proof_registry import ProofRegistry
from src.proof_economy.generators.spa_generator import SPAGenerator
from src.proof_economy.generators.pcca_generator import PCCAGenerator

router = APIRouter(prefix="/proof", tags=["Proof Economy"])

@router.post("/generate/spa")
async def generate_spa_proof(request: Request, data: Dict[str, Any]):
    """Generate Statistical Proof of Attestation"""
    spa_gen = request.app.state.spa_generator
    proof = await spa_gen.generate(data)
    return {"proof": proof, "type": "SPA"}

@router.post("/generate/pcca")
async def generate_pcca_proof(request: Request, data: Dict[str, Any]):
    """Generate Physics-Constrained Cryptographic Attestation"""
    pcca_gen = request.app.state.pcca_generator
    proof = await pcca_gen.generate(data)
    return {"proof": proof, "type": "PCCA"}

@router.post("/verify")
async def verify_proof(request: Request, proof_token: str, proof_type: str):
    """Verify cryptographic proof"""
    registry = request.app.state.proof_registry
    valid = await registry.verify(proof_token, proof_type)
    return {"valid": valid}

@router.post("/anchor")
async def anchor_proof(request: Request, proof_data: Dict):
    """Anchor proof to L2 + Arweave (requires PCCA proof)"""
    if not request.state.proof_verified:
        raise HTTPException(403, "Proof anchoring requires PCCA proof")

    registry = request.app.state.proof_registry
    anchor_id = await registry.anchor(proof_data)
    return {"anchor_id": anchor_id}
```

**Endpoints**:
- `POST /proof/generate/spa` - Generate SPA proof
- `POST /proof/generate/pcca` - Generate PCCA proof
- `POST /proof/verify` - Verify proof
- `POST /proof/anchor` - Anchor proof to L2 + Arweave

---

### 5. UTID Routes (`/utid/*`)

**Purpose**: Universal Trusted Identity management

**File**: `src/bridge_api/routes/utid_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request
from src.utid.core.utid_generator import UTIDGenerator, UTIDValidator

router = APIRouter(prefix="/utid", tags=["Universal Trusted Identity"])

@router.post("/register")
async def register_device(request: Request, device_data: Dict[str, Any]):
    """Register device and generate UTID"""
    utid_gen = request.app.state.utid_generator
    utid = await utid_gen.register_device(device_data)
    return {"utid": utid, "token": utid.token}

@router.post("/validate")
async def validate_utid(request: Request, utid_token: str):
    """Validate UTID token"""
    validator = request.app.state.utid_validator
    claims = await validator.validate_token(utid_token)
    return {"valid": True, "claims": claims.dict()}

@router.post("/refresh")
async def refresh_utid_token(request: Request):
    """Refresh UTID token (requires valid existing UTID)"""
    utid_gen = request.app.state.utid_generator
    new_token = await utid_gen.refresh_token(request.state.user_id)
    return {"token": new_token}
```

**Endpoints**:
- `POST /utid/register` - Register device and generate UTID
- `POST /utid/validate` - Validate UTID token
- `POST /utid/refresh` - Refresh UTID token

---

### 6. KaaS Routes (`/kaas/*`)

**Purpose**: Kubernetes-as-a-Service with proof-backed clusters

**File**: `src/bridge_api/routes/kaas_routes.py`

```python
from fastapi import APIRouter, Depends, HTTPException, Request

router = APIRouter(prefix="/kaas", tags=["Kubernetes-as-a-Service"])

@router.post("/clusters/create")
async def create_kaas_cluster(request: Request, cluster_config: Dict):
    """Create proof-backed Kubernetes cluster (requires PCCA proof)"""
    if not request.state.proof_verified:
        raise HTTPException(403, "Cluster creation requires PCCA proof")

    kaas_operator = request.app.state.kaas_operator
    cluster = await kaas_operator.create_cluster(cluster_config)
    return {"cluster_id": cluster.id, "status": cluster.status}

@router.get("/clusters/{cluster_id}")
async def get_cluster_status(request: Request, cluster_id: str):
    """Get cluster status"""
    kaas_operator = request.app.state.kaas_operator
    cluster = await kaas_operator.get_cluster(cluster_id)
    return cluster.dict()

@router.post("/clusters/{cluster_id}/deploy")
async def deploy_to_cluster(request: Request, cluster_id: str, deployment: Dict):
    """Deploy workload to cluster"""
    kaas_operator = request.app.state.kaas_operator
    result = await kaas_operator.deploy(cluster_id, deployment)
    return result
```

**Endpoints**:
- `POST /kaas/clusters/create` - Create proof-backed cluster
- `GET /kaas/clusters/{cluster_id}` - Get cluster status
- `POST /kaas/clusters/{cluster_id}/deploy` - Deploy workload

---

## 📡 PROTOCOL ADAPTERS (MCP + A2A Integration)

### MCP Integration

**Purpose**: Reuse existing MCP protocol bridge from overseer system

**File**: `src/bridge_api/adapters/mcp_adapter.py`

```python
from src.overseer_system.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge, MCPContext

class BridgeAPIMCPAdapter:
    """
    Adapter to integrate Bridge API with existing MCP protocol bridge

    Reuses: src/overseer_system/mcp_integration/mcp_protocol_bridge.py
    """

    def __init__(self, event_bus_client):
        # Create MCP bridge instance (from overseer system)
        self.mcp_bridge = MCPProtocolBridge(
            service_name="bridge_api",
            event_bus_client=event_bus_client
        )

    async def initialize(self):
        """Initialize MCP bridge"""
        await self.mcp_bridge.initialize()

        # Register handlers for Bridge API contexts
        self.mcp_bridge.register_context_handler("eil_decision", self._handle_eil_decision)
        self.mcp_bridge.register_context_handler("trifecta_predict", self._handle_trifecta_predict)

    async def _handle_eil_decision(self, context: MCPContext):
        """Handle EIL decision context from MCP"""
        # Forward to EIL service
        eil = get_eil_service()
        result = await eil.decide(context.payload)

        # Send response context
        response_context = MCPContext(
            source="bridge_api",
            target=context.source,
            context_type="eil_decision_response",
            payload=result,
            parent_context_id=context.context_id
        )
        await self.mcp_bridge.send_context(response_context)

    async def _handle_trifecta_predict(self, context: MCPContext):
        """Handle Trifecta prediction context from MCP"""
        # Forward to Trifecta cortex
        cortex = get_trifecta_cortex()
        result = await cortex.execute_playbook(context.payload["playbook"], context.payload["context"])

        # Send response context
        response_context = MCPContext(
            source="bridge_api",
            target=context.source,
            context_type="trifecta_predict_response",
            payload=result,
            parent_context_id=context.context_id
        )
        await self.mcp_bridge.send_context(response_context)
```

**Key Features**:
- ✅ Reuses existing MCP bridge from overseer system
- ✅ Registers Bridge API handlers for EIL, Trifecta, etc.
- ✅ Bidirectional context communication
- ✅ Event bus (Kafka) integration

---

### A2A Integration

**Purpose**: Reuse existing A2A protocol bridge from overseer system

**File**: `src/bridge_api/adapters/a2a_adapter.py`

```python
from src.overseer_system.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge, A2AAgentCard, A2ATask

class BridgeAPIAAAdapter:
    """
    Adapter to integrate Bridge API with existing A2A protocol bridge

    Reuses: src/overseer_system/a2a_integration/a2a_protocol_bridge.py
    """

    def __init__(self, event_bus_client):
        # Create agent card for Bridge API
        agent_card = A2AAgentCard(
            name="Bridge API",
            description="Unified API gateway for Industriverse platform",
            version="1.0.0",
            provider="Industriverse",
            capabilities=["eil_decision", "trifecta_predict", "proof_generation", "utid_validation"],
            api_url="https://api.industriverse.com",
            auth_type="utid"
        )

        # Create A2A bridge instance (from overseer system)
        self.a2a_bridge = A2AProtocolBridge(
            agent_card=agent_card,
            event_bus_client=event_bus_client
        )

    async def initialize(self):
        """Initialize A2A bridge"""
        await self.a2a_bridge.initialize()

        # Register task handlers
        self.a2a_bridge.register_task_handler("eil_decision", self._handle_eil_decision_task)
        self.a2a_bridge.register_task_handler("trifecta_predict", self._handle_trifecta_predict_task)

    async def _handle_eil_decision_task(self, task: A2ATask):
        """Handle EIL decision task from A2A"""
        # Forward to EIL service
        eil = get_eil_service()
        result = await eil.decide(task.input_data)

        # Return task result
        return A2ATaskResult(
            task_id=task.task_id,
            agent_id=self.a2a_bridge.agent_card.agent_id,
            status="completed",
            output_data=result
        )

    async def _handle_trifecta_predict_task(self, task: A2ATask):
        """Handle Trifecta prediction task from A2A"""
        # Forward to Trifecta cortex
        cortex = get_trifecta_cortex()
        result = await cortex.execute_playbook(task.input_data["playbook"], task.input_data["context"])

        # Return task result
        return A2ATaskResult(
            task_id=task.task_id,
            agent_id=self.a2a_bridge.agent_card.agent_id,
            status="completed",
            output_data=result
        )
```

**Key Features**:
- ✅ Reuses existing A2A bridge from overseer system
- ✅ Registers Bridge API as A2A agent
- ✅ Task-based communication
- ✅ Bidding and capability negotiation support

---

## 📁 COMPLETE FILE STRUCTURE

```
src/
├── bridge_api/                          # NEW: Bridge API Gateway
│   ├── __init__.py
│   ├── server.py                        # FastAPI application server
│   ├── config.py                        # Configuration
│   │
│   ├── middlewares/                     # Middleware stack
│   │   ├── __init__.py
│   │   ├── utid_middleware.py           # UTID verification
│   │   ├── proof_middleware.py          # Proof validation
│   │   ├── ai_shield_middleware.py      # AI Shield gateway
│   │   ├── rate_limit_middleware.py     # Rate limiting
│   │   └── logging_middleware.py        # Request logging
│   │
│   ├── routes/                          # Route controllers
│   │   ├── __init__.py
│   │   ├── eil_routes.py                # /eil/* endpoints
│   │   ├── trifecta_routes.py           # /trifecta/* endpoints
│   │   ├── packs_routes.py              # /packs/* endpoints (20 Pillars)
│   │   ├── proof_routes.py              # /proof/* endpoints
│   │   ├── utid_routes.py               # /utid/* endpoints
│   │   ├── kaas_routes.py               # /kaas/* endpoints
│   │   └── idf_routes.py                # /idf/* endpoints
│   │
│   ├── adapters/                        # Protocol adapters
│   │   ├── __init__.py
│   │   ├── mcp_adapter.py               # MCP protocol integration
│   │   └── a2a_adapter.py               # A2A protocol integration
│   │
│   ├── models/                          # Pydantic models
│   │   ├── __init__.py
│   │   ├── requests.py                  # Request models
│   │   ├── responses.py                 # Response models
│   │   └── errors.py                    # Error models
│   │
│   ├── services/                        # Business logic services
│   │   ├── __init__.py
│   │   ├── eil_service.py               # EIL integration
│   │   ├── trifecta_service.py          # Trifecta integration
│   │   └── packs_service.py             # Expansion Packs integration
│   │
│   ├── dependencies.py                  # FastAPI dependencies
│   ├── exceptions.py                    # Custom exceptions
│   │
│   └── tests/                           # Tests
│       ├── __init__.py
│       ├── test_middlewares.py
│       ├── test_eil_routes.py
│       ├── test_trifecta_routes.py
│       ├── test_proof_routes.py
│       └── test_integration.py
│
├── utid/                                # NEW: Universal Trusted Identity
│   ├── __init__.py
│   ├── core/
│   │   ├── utid_generator.py            # Generate UTID
│   │   ├── utid_validator.py            # Validate UTID
│   │   └── hardware_binding.py          # Hardware entropy binding
│   └── tests/
│
├── proof_economy/                       # NEW: Proof Economy
│   ├── __init__.py
│   ├── core/
│   │   ├── proof_registry.py            # Proof registry
│   │   └── proof_anchoring.py           # L2 + Arweave anchoring
│   ├── generators/
│   │   ├── spa_generator.py             # Statistical Proof of Attestation
│   │   ├── pcca_generator.py            # Physics-Constrained Crypto Attestation
│   │   └── zk_generator.py              # Zero-knowledge proofs
│   └── tests/
│
├── ai_shield_v2/                        # NEW: AI Shield v2
│   ├── __init__.py
│   ├── core/
│   │   └── shield_orchestrator.py       # Shield orchestrator
│   ├── layers/
│   │   ├── substrate_safety.py          # Layer 1: Physics consistency
│   │   ├── structural_safety.py         # Layer 2: DAG validation
│   │   ├── semantic_safety.py           # Layer 3: Context reasoning
│   │   ├── behavioral_safety.py         # Layer 4: Anomaly detection
│   │   └── policy_safety.py             # Layer 5: Compliance
│   └── tests/
│
├── trifecta/                            # NEW: Trifecta (from previous design)
│   ├── userlm/
│   ├── rnd1/
│   └── cortex/
│
├── expansion_packs/                     # NEW: 20 Pillars (6 Packs)
│   ├── tsc/                             # Pack 1: TSC
│   ├── upv/                             # Pack 2: UPV
│   ├── use_cases/                       # Pack 3: 100 Use Cases
│   ├── til/                             # Pack 4: TIL v2
│   ├── tse/                             # Pack 5: TSE
│   └── tso/                             # Pack 6: TSO
│
├── kaas_operator/                       # NEW: KaaS Operator
│   ├── __init__.py
│   ├── controllers/
│   │   ├── cluster_controller.py
│   │   └── deployment_controller.py
│   ├── crds/
│   │   ├── kaas_cluster_crd.yaml
│   │   └── proofed_deployment_crd.yaml
│   └── webhooks/
│       └── admission_webhook.py
│
├── core_ai_layer/                       # EXISTING: Thermodynasty
│   ├── nvp/                             # Phase 4 (ACE)
│   ├── eil/                             # Phase 5 (EIL)
│   └── data/                            # Phase 0 (Bootstrap)
│
└── overseer_system/                     # EXISTING: MCP + A2A
    ├── mcp_integration/                 # ✅ REUSE
    │   ├── mcp_protocol_bridge.py
    │   └── mcp_context_schema.py
    └── a2a_integration/                 # ✅ REUSE
        ├── a2a_protocol_bridge.py
        └── a2a_agent_schema.py
```

---

## 🚀 IMPLEMENTATION ROADMAP

### Week 1: Core Server + Middleware
- [ ] Implement `server.py` (FastAPI application)
- [ ] Implement middleware stack:
  - [ ] UTID middleware
  - [ ] Proof middleware
  - [ ] AI Shield middleware
  - [ ] Rate limiting
  - [ ] Logging
- [ ] Unit tests for middleware (50+ tests)

### Week 2: EIL + Trifecta Routes
- [ ] Implement EIL routes (`/eil/*`)
- [ ] Implement Trifecta routes (`/trifecta/*`)
- [ ] Integration with existing EIL service
- [ ] Integration with Trifecta cortex
- [ ] API tests (30+ tests)

### Week 3: Proof + UTID Routes
- [ ] Implement Proof routes (`/proof/*`)
- [ ] Implement UTID routes (`/utid/*`)
- [ ] Implement proof generators (SPA, PCCA, ZK)
- [ ] Implement UTID generator + validator
- [ ] Integration tests (25+ tests)

### Week 4: Protocol Adapters + Deployment
- [ ] Implement MCP adapter
- [ ] Implement A2A adapter
- [ ] Integration with overseer system
- [ ] OpenAPI documentation
- [ ] Docker + Kubernetes deployment configs
- [ ] End-to-end tests (20+ tests)

---

## 📊 SUCCESS METRICS

### Functional Metrics
- ✅ All middleware validates correctly (UTID, Proof, AI Shield)
- ✅ All routes return correct responses (100+ endpoint tests)
- ✅ MCP/A2A integration works with overseer system
- ✅ 200+ unit tests, 50+ integration tests, all passing

### Performance Metrics
- ✅ Latency: <50ms (p95) for simple endpoints, <200ms for AI operations
- ✅ Throughput: >5000 req/s (load balanced)
- ✅ Middleware overhead: <10ms per middleware
- ✅ Memory: <2GB per server instance

### Security Metrics
- ✅ 100% UTID verification coverage
- ✅ Proof validation for high-trust operations
- ✅ AI Shield blocks 100% of invalid AI operations
- ✅ Rate limiting prevents DDoS (tested)
- ✅ Audit logs for all requests

---

## 🔒 SECURITY CONSIDERATIONS

### 1. UTID Security
- Hardware-bound identity (eSIM, RF fingerprint)
- Physics-domain signatures (thermodynamic hash)
- Zero-knowledge proofs
- Token expiration (1 hour default)
- Refresh token rotation

### 2. Proof Validation
- SPA: Statistical attestation with confidence threshold
- PCCA: Physics-constrained with energy conservation checks
- ZK: Zero-knowledge proofs for privacy
- Proof anchoring to L2 + Arweave for immutability

### 3. AI Shield Protection
- 5-layer validation for all AI operations
- Request blocking if any layer fails
- Detailed failure reasons (no information leakage)
- Safety scores tracked per user

### 4. Rate Limiting
- Per-user token bucket algorithm
- Tiered limits (Free, Pro, Enterprise)
- DDoS protection
- Automatic blacklisting for abuse

### 5. Audit Logging
- All requests logged (structured JSON)
- Security events highlighted
- Immutable audit trail
- Compliance with SOC2, GDPR, HIPAA

---

## 📖 REFERENCES

### Existing Code References
- MCP Bridge: `src/overseer_system/mcp_integration/mcp_protocol_bridge.py:30-100`
- A2A Bridge: `src/overseer_system/a2a_integration/a2a_protocol_bridge.py:70-100`
- EIL Core: `src/core_ai_layer/eil/core/energy_intelligence_layer.py`
- ACE Agent: `src/core_ai_layer/nvp/ace/ace_agent.py:407-530`

### Related Documents
- `COMPREHENSIVE_INTEGRATION_ANALYSIS.md` - Master integration plan
- `TRIFECTA_ARCHITECTURE.md` - Trifecta design
- `FINAL_FORM_ARCHITECTURE.md` - Complete system architecture

### External References
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://pydantic-docs.helpmanual.io/
- OpenAPI 3.0: https://swagger.io/specification/
- JWT: https://jwt.io/

---

**Status**: Ready for Implementation ✅
**Priority**: Critical - Entry point for entire platform
**Dependencies**: EIL (Phase 5), Overseer System (MCP/A2A)
**Estimated Effort**: 4 weeks (2 engineers)

**Date**: November 21, 2025
**Created By**: Industriverse Core Team (Claude Code)
