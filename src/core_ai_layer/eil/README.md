# Phase 5: Energy Intelligence Layer (EIL)

## Overview

Phase 5 is the **convergence layer** that unifies all previous Industriverse Thermodynasty phases (0-4) into a production-ready Energy Intelligence Layer.

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   PHASE 5: ENERGY INTELLIGENCE LAYER            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────┐              ┌──────────────────┐        │
│  │  Statistical     │              │  Physics         │        │
│  │  Branch          │              │  Branch          │        │
│  │  (MicroAdapt)    │              │  (RegimeDetector)│        │
│  └────────┬─────────┘              └────────┬─────────┘        │
│           │                                 │                  │
│           └────────────┬────────────────────┘                  │
│                        │                                       │
│                  ┌─────▼─────┐                                 │
│                  │  Decision  │                                │
│                  │  Fusion    │                                │
│                  └─────┬─────┘                                 │
│                        │                                       │
│           ┌────────────┼────────────┐                          │
│           │            │            │                          │
│    ┌──────▼─────┐ ┌───▼────┐ ┌────▼──────┐                   │
│    │   Proof    │ │ Market │ │ Feedback  │                   │
│    │ Validator  │ │ Engine │ │ Trainer   │                   │
│    └────────────┘ └────────┘ └───────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │                    │                     │
    ┌────▼─────┐        ┌─────▼──────┐       ┌─────▼──────┐
    │ Phase 0  │        │  Phase 2   │       │  Phase 4   │
    │ Shadow   │        │ Proof      │       │ ACE/NVP    │
    │ Consensus│        │ Economy    │       │ Thermo     │
    └──────────┘        └────────────┘       └────────────┘
```

### Key Components

#### 1. Energy Intelligence Layer (EIL)
**File**: `core/energy_intelligence_layer.py`

Parallel ensemble architecture that fuses statistical (MicroAdapt) and physics-based (RegimeDetector) approaches for regime detection.

- **Statistical Branch**: MicroAdapt with multi-scale hierarchical windows
- **Physics Branch**: RegimeDetector with thermodynamic metrics
- **Decision Fusion**: Weighted combination (40% statistical, 60% physics)
- **Processing Time**: <1 second per request

#### 2. Proof Validator
**File**: `core/proof_validator.py`

Tri-check validation for Proof of Energy (PoE):

1. **Energy Conservation**: `|E_predicted - E_observed| / E_observed < 1%`
2. **Entropy Coherence**: Monotonic entropy increase ≥ 90%
3. **Spectral Similarity**: Power spectrum correlation ≥ 85%

All three checks must pass for PFT minting.

#### 3. Market Engine
**File**: `core/market_engine.py`

Dynamic CEU/PFT pricing with regime awareness:

- **CEU Costs**: 0.8x (stable) to 1.5x (chaotic/unapproved)
- **PFT Rewards**: 0.5x (poor) to 3.0x (excellent stable)
- **AMM Bonding Curve**: `x * y = k` for price discovery

#### 4. Feedback Trainer
**File**: `core/feedback_trainer.py`

Online learning system that adapts from validation results:

- MicroAdapt fitness boosting/penalizing
- RegimeDetector threshold calibration
- Fusion weight optimization
- No retraining required

#### 5. MicroAdapt Library
**Directory**: `core/microadapt/`

Self-evolutionary dynamic modeling framework (ported from Phase 1):

- Multi-scale hierarchical window decomposition
- Model unit adaptation with Levenberg-Marquardt
- Regime search with fitness-based selection
- Differential dynamical system forecasting

#### 6. Prometheus Metrics
**Directory**: `monitoring/`

Comprehensive observability with 45 metrics:

- Regime detection (detections, confidence, transitions)
- Proof validation (tri-check results, quality scores)
- Market engine (CEU costs, PFT minting, AMM reserves)
- Feedback trainer (learning events, accuracy, fusion weights)
- Performance (latency, throughput, errors)

---

## Quick Start

### Prerequisites

```bash
# Python 3.11+
python --version

# Required packages
pip install numpy jax flax scipy scikit-learn pytest

# Optional (for production)
pip install prometheus-client kafka-python
```

### Local Testing

```bash
# Run Phase 5 EIL integration tests
cd phase5/tests
./run_tests.sh phase5

# Run full stack Phase 0-5 tests
./run_tests.sh full_stack

# Run all tests
./run_tests.sh all
```

### Standalone Component Tests

```bash
# Set PYTHONPATH
export PYTHONPATH=/home/user/industriverse/Thermodynasty:$PYTHONPATH

# Test EIL
python phase5/core/energy_intelligence_layer.py

# Test Proof Validator
python phase5/core/proof_validator.py

# Test Market Engine
python phase5/core/market_engine.py

# Test Feedback Trainer
python phase5/core/feedback_trainer.py

# Test Prometheus Metrics
python phase5/monitoring/prometheus_metrics.py
```

---

## Kubernetes Deployment

### Prerequisites

- Kubernetes 1.24+
- Helm 3.8+
- GPU nodes with NVIDIA drivers
- Kafka cluster
- Prometheus/Grafana (optional)

### Deploy Phase 5 EIL

```bash
cd deploy/helm/phase5

# Install
helm install thermodynasty-ace . \
  --namespace thermodynasty \
  --create-namespace \
  --values values.yaml

# Verify deployment
kubectl get pods -n thermodynasty
kubectl logs -n thermodynasty -l app=thermodynasty-ace

# Check metrics endpoint
kubectl port-forward -n thermodynasty svc/thermodynasty-ace 8000:8000
curl http://localhost:8000/v1/metrics
```

### Configuration

Edit `deploy/helm/phase5/values.yaml`:

```yaml
# EIL Configuration
config:
  eil:
    enabled: "true"
    regimeDetector:
      entropyRateMin: "0.001"
      temperatureStableMax: "1.5"
    microadapt:
      maxModelUnits: "100"
      topK: "5"
    fusion:
      statisticalWeight: "0.40"
      physicsWeight: "0.60"

  # Proof Validator
  proofValidator:
    energyTolerance: "0.01"    # 1% tolerance
    entropyThreshold: "0.90"   # 90% coherence
    spectralThreshold: "0.85"  # 85% similarity

  # Market Engine
  marketEngine:
    initialCeuReserve: "1000000.0"
    initialPftReserve: "100000.0"
```

---

## API Usage

### Regime Detection Endpoint

```bash
POST /v1/regime
Content-Type: application/json
Authorization: Bearer <token>

{
  "energy_map": [[...]],  # 2D array
  "domain": "fluid_dynamics",
  "cluster": "cluster-1",
  "node": "node-1"
}

Response:
{
  "regime": "stable_confirmed",
  "confidence": 0.92,
  "approved": true,
  "forecast_mean": 1.05,
  "entropy_rate": 0.005,
  "temperature": 1.2,
  "recommended_action": "proceed",
  "risk_level": "low",
  "timestamp": 1699999999.123
}
```

### ACE Inference Endpoint

```bash
POST /v1/predict
Content-Type: application/json
Authorization: Bearer <token>

{
  "energy_map": [[...]],
  "domain": "molecular_dynamics",
  "steps": 10,
  "beta": 1.0
}

Response:
{
  "prediction": [[...]],
  "energy": 123.45,
  "confidence": 0.95,
  "processing_time": 0.234
}
```

---

## Metrics & Monitoring

### Prometheus Metrics

Access metrics at: `http://<pod-ip>:8000/v1/metrics`

Key metrics:

```prometheus
# Regime Detection
thermodynasty_regime_detections_total{regime="stable_confirmed",approved="true"}
thermodynasty_regime_confidence{regime="stable_confirmed"}

# Proof Validation
thermodynasty_poe_validations_total{passed="true",action="mint"}
thermodynasty_poe_proof_quality

# Market Engine
thermodynasty_market_ceu_cost{regime="stable_confirmed"}
thermodynasty_market_pft_minted_total{quality_tier="high"}
thermodynasty_market_amm_ceu_reserve

# Performance
thermodynasty_eil_process_latency_seconds
thermodynasty_eil_requests_total
```

### Grafana Dashboards

Import dashboards from `deploy/grafana/`:

- **EIL Overview**: Regime detection trends, approval rates
- **Proof Economy**: PFT minting, validation pass rates
- **Market Dynamics**: CEU/PFT pricing, AMM reserves
- **Performance**: Latency, throughput, errors

---

## Integration with Previous Phases

### Phase 0: Shadow Twin Consensus
- EIL validates consensus through tri-check validation
- BFT consensus ensures 98.3% pixel agreement

### Phase 1: MicroAdapt + TTF Agent
- MicroAdapt integrated as statistical branch in EIL
- Multi-scale temporal patterns for regime detection

### Phase 2: ProofEconomy Smart Contracts
- Proof Validator enables PFT minting via tri-check
- Market Engine implements CEU/PFT tokenomics

### Phase 3: Hypothesis Orchestration
- EIL decision fusion combines 1,090 microservice hypotheses
- Ensemble intelligence across statistical + physics branches

### Phase 4: ACE/NVP Thermodynasty
- RegimeDetector provides physics-based validation
- 99.99% energy fidelity targets for proof validation

---

## Performance Targets

| Metric | Target | Current |
|--------|--------|---------|
| Regime Detection Latency | <1s | ~200ms |
| Proof Validation Time | <100ms | ~50ms |
| CEU Cost Calculation | <10ms | ~5ms |
| Throughput | >100 req/s | ~200 req/s |
| Regime Accuracy | >90% | ~85% (improving) |
| Proof Pass Rate | >80% | ~75% (stable regimes) |

---

## Testing

### Unit Tests

```bash
# Test individual components
pytest phase5/tests/test_phase5_eil_integration.py::TestPhase5EILIntegration::test_01_eil_regime_detection -v
```

### Integration Tests

```bash
# Full Phase 0-5 stack
pytest phase5/tests/test_full_stack_phase0_5.py::TestPhase0_5_FullStack::test_07_full_stack_end_to_end -v
```

### Performance Benchmarks

```bash
# Latency + throughput
pytest phase5/tests/test_full_stack_phase0_5.py::TestPhase0_5_FullStack::test_08_performance_benchmarks -v

# Stress test
pytest phase5/tests/test_full_stack_phase0_5.py::TestPhase0_5_FullStack::test_09_scalability_stress_test -v
```

---

## Troubleshooting

### Common Issues

**1. EIL not initialized**
```
Error: Energy Intelligence Layer not initialized
Fix: Check REGIME_DETECTOR_CHECKPOINT path in deployment.yaml
```

**2. Regime always unapproved**
```
Issue: All regimes showing approved=false
Fix: Lower confidence thresholds in values.yaml (REGIME_MIN_CONFIDENCE)
```

**3. Proof validation always failing**
```
Issue: All proofs failing tri-check
Fix: Increase tolerance thresholds in values.yaml (PROOF_ENERGY_TOLERANCE)
```

**4. High CEU costs**
```
Issue: CEU costs >50 per inference
Fix: Check regime approval rates, adjust regime multipliers
```

---

## Development

### Adding New Regimes

Edit `core/energy_intelligence_layer.py`:

```python
# Add new regime classification
if entropy_rate < 0.005 and temperature < 1.0:
    regime = "ultra_stable_confirmed"
    approved = True
```

### Adjusting Fusion Weights

Use Feedback Trainer or manual config:

```python
eil = EnergyIntelligenceLayer(
    fusion_weights={'statistical': 0.35, 'physics': 0.65}
)
```

### Custom Proof Validators

Subclass `ProofValidator`:

```python
class CustomProofValidator(ProofValidator):
    def validate(self, proof, observed):
        # Add custom validation logic
        result = super().validate(proof, observed)
        # Additional checks...
        return result
```

---

## Production Checklist

- [ ] RegimeDetector model trained and validated
- [ ] Kafka topics created (regimes, proofs, predictions)
- [ ] Neo4j Energy Atlas populated (optional)
- [ ] Prometheus/Grafana dashboards configured
- [ ] Helm values reviewed for production settings
- [ ] GPU nodes provisioned and labeled
- [ ] PVCs created for model storage
- [ ] Network policies configured
- [ ] Backup/restore procedures tested
- [ ] Alerting rules configured
- [ ] Load testing completed

---

## Contributing

Phase 5 development follows the established Industriverse patterns:

1. All components include standalone tests
2. Dataclasses for structured data
3. Comprehensive error handling
4. Prometheus metrics integration
5. Kubernetes-ready design

---

## Version History

**v1.0.0-phase5** (Current)
- Initial Phase 5 EIL release
- MicroAdapt integration from Phase 1
- Proof Validator tri-check implementation
- Market Engine CEU/PFT pricing
- Feedback Trainer online learning
- Comprehensive Prometheus metrics
- Helm charts for Kubernetes deployment
- Full stack Phase 0-5 integration tests

---

## License

Proprietary - Industriverse
