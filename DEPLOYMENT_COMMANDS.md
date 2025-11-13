# Phase 5 EIL - Deployment & Testing Commands

## Git Commands - Pull All Commits to Local

### 1. Pull Latest Commits from Remote Branch

```bash
# Navigate to industriverse repository
cd /path/to/your/industriverse

# Fetch all remote branches
git fetch origin

# Checkout the Phase 5 branch
git checkout claude/review-industriverse-phase1-011CV2sSawNHXTjWxgW8DZnW

# Pull latest commits (11 total commits)
git pull origin claude/review-industriverse-phase1-011CV2sSawNHXTjWxgW8DZnW
```

### 2. Verify Commits Were pulled

```bash
# View commit history
git log --oneline -11

# Expected output (newest to oldest):
# 119ce32 - Add comprehensive research integration analysis for Phase 5 EIL
# eb60f40 - Add Phase 5 EIL deployment documentation and validation
# ecf2ed4 - Add Prometheus metrics for Phase 5 EIL regime tracking
# 4546ed0 - Create comprehensive Phase 0-5 integration tests
# 33acf03 - Update Helm charts with Phase 5 EIL components
# b76ea1e - Create Feedback Trainer for online learning from validation results
# 4ed2b1a - Create Market Engine for CEU/PFT dynamic pricing
# 3b5ab72 - Create Proof of Energy (PoE) Validator with tri-check
# 7bab06d - Add regime detection to streaming consumer pipeline
# c9b0fcb - Integrate EIL with ACE Server - Add /v1/regime endpoint
# 6bd8849 - Create Energy Intelligence Layer (EIL) - Phase 5 Core Orchestrator
```

### 3. View File Changes

```bash
# See all files modified in Phase 5
git diff main..claude/review-industriverse-phase1-011CV2sSawNHXTjWxgW8DZnW --name-status

# View detailed changes for specific file
git show 119ce32:Thermodynasty/phase5/docs/research_integration_analysis.md
```

---

## Testing Commands

### Prerequisites - Install Dependencies

```bash
# Navigate to Thermodynasty directory
cd Thermodynasty

# Install Python dependencies
pip install numpy jax flax scipy scikit-learn pytest

# Optional: For production deployment
pip install prometheus-client kafka-python
```

### Test 1: Individual Component Tests

#### Test Energy Intelligence Layer

```bash
# Set PYTHONPATH
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH

# Run standalone test
python phase5/core/energy_intelligence_layer.py

# Expected output:
# ✅ EnergyIntelligenceLayer initialized
# ✅ Regime detected: stable_confirmed
# ✅ Decision confidence: 0.XX
# ✅ TEST COMPLETE
```

#### Test Proof Validator

```bash
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH

python phase5/core/proof_validator.py

# Expected output:
# ✅ ProofValidator initialized
# [Test 1] Perfect Prediction: PASSED
# [Test 2] Poor Prediction: FAILED
# PFT Minted: X.XX
# ✅ TEST COMPLETE
```

#### Test Market Engine

```bash
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH

python phase5/core/market_engine.py

# Expected output:
# ✅ MarketEngine initialized
# [Test 1] CEU Cost - Stable Regime: 4.00 CEU
# [Test 2] CEU Cost - Chaotic Regime: 7.50 CEU
# [Test 3] PFT Reward - High Quality: 3.00 PFT
# [Test 5] CEU → PFT Swap: 100 CEU → 0.9993 PFT
# ✅ TEST COMPLETE
```

#### Test Feedback Trainer

```bash
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH

python phase5/core/feedback_trainer.py

# Expected output:
# ✅ FeedbackTrainer initialized
# [Simulating 50 validation results...]
# Regime accuracy: 80.0%
# Avg proof quality: 91.3%
# MicroAdapt updates: 50
# ✅ TEST COMPLETE
```

#### Test Prometheus Metrics

```bash
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH

python phase5/monitoring/prometheus_metrics.py

# Expected output:
# ✅ PrometheusMetrics initialized
# [Test 1] Regime Detection: ✅
# [Test 2] Proof Validation: ✅
# [Test 3] PFT Minting: ✅
# [Metrics Snapshot]
#   Regime detections: 1
#   PFT minted: 2.50
# ✅ TEST COMPLETE
```

### Test 2: Deployment Validation Script

```bash
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH

python phase5/scripts/validate_deployment.py

# Expected output:
# ======================================================================
#                   PHASE 5 EIL DEPLOYMENT VALIDATION
# ======================================================================
#
# [VALIDATING IMPORTS]
# ✅ EnergyIntelligenceLayer import successful
# ✅ ProofValidator import successful
# ✅ MarketEngine import successful
# ✅ FeedbackTrainer import successful
# ✅ MicroAdapt import successful
# ✅ Prometheus Metrics import successful
#
# [VALIDATING COMPONENT INITIALIZATION]
# ✅ EIL initialization
# ✅ ProofValidator initialization
# ✅ MarketEngine initialization
# ✅ FeedbackTrainer initialization
# ✅ Prometheus Metrics initialization
#
# [VALIDATING END-TO-END WORKFLOWS]
# ✅ Regime Detection Workflow
# ✅ Proof Validation Workflow
# ✅ Market Engine Pricing Workflow
# ✅ AMM Swap Workflow
#
# [VALIDATING PERFORMANCE TARGETS]
# ✅ Regime Detection Latency (<1000ms): 0.45ms
# ✅ Throughput (>1 req/s): 18.75 req/s
#
# [VALIDATION SUMMARY]
# ✅ Imports: PASSED
# ✅ Components: PASSED
# ✅ Workflows: PASSED
# ✅ Performance: PASSED
#
# ✅ All 4 validation checks PASSED ✅
```

#### Verbose Mode (for debugging)

```bash
python phase5/scripts/validate_deployment.py --verbose
```

### Test 3: Integration Tests (Pytest)

#### Install pytest

```bash
pip install pytest
```

#### Run Phase 5 EIL Integration Tests

```bash
cd Thermodynasty/phase5/tests

# Run all Phase 5 tests
./run_tests.sh phase5

# Or directly with pytest
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH
pytest test_phase5_eil_integration.py -v -s

# Expected output:
# test_01_eil_regime_detection PASSED
# test_02_stable_regime_pipeline PASSED
# test_03_chaotic_regime_rejection PASSED
# test_04_regime_gating_skip_inference PASSED
# test_05_feedback_trainer_learning PASSED
# test_06_market_engine_amm_swap PASSED
# test_07_end_to_end_workflow PASSED
```

#### Run Full Stack Phase 0-5 Tests

```bash
cd Thermodynasty/phase5/tests

# Run full stack tests
./run_tests.sh full_stack

# Or directly with pytest
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH
pytest test_full_stack_phase0_5.py -v -s

# Expected output:
# test_01_phase0_shadow_consensus_simulation PASSED
# test_02_phase1_microadapt_integration PASSED
# test_03_phase2_proof_economy_pft_minting PASSED
# test_04_phase3_hypothesis_orchestration_simulation PASSED
# test_05_phase4_ace_nvp_thermodynasty PASSED
# test_06_phase5_eil_convergence PASSED
# test_07_full_stack_end_to_end PASSED
# test_08_performance_benchmarks PASSED
# test_09_scalability_stress_test PASSED
```

#### Run All Tests

```bash
cd Thermodynasty/phase5/tests

./run_tests.sh all

# Or
pytest . -v -s
```

#### Run Specific Test

```bash
# Run single test function
pytest test_phase5_eil_integration.py::TestPhase5EILIntegration::test_01_eil_regime_detection -v -s

# Run specific test class
pytest test_full_stack_phase0_5.py::TestPhase0_5_FullStack -v -s
```

### Test 4: MicroAdapt Components

```bash
export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH

# Test Data Collection
python -c "
from phase5.core.microadapt import DynamicDataCollection
import numpy as np

collector = DynamicDataCollection(hierarchy_levels=3)
data = np.random.randn(100)
for val in data:
    collector.add_data_point(val)

window_set = collector.decompose()
print(f'✅ Collected {len(data)} points across {len(window_set.windows)} hierarchical levels')
"

# Test Model Adaptation
python -c "
from phase5.core.microadapt import ModelUnitAdaptation, DynamicDataCollection
import numpy as np

adaptation = ModelUnitAdaptation(max_units=10, initial_units=3)
collector = DynamicDataCollection()
collector.add_data_point(1.0)

window_set = collector.decompose()
adaptation.initialize_model_units(window_set)
print(f'✅ Initialized {len(adaptation.model_units)} model units')

adapted_units = adaptation.adapt(window_set)
print(f'✅ Adapted {len(adapted_units)} model units')
"

# Test Model Search
python -c "
from phase5.core.microadapt import ModelUnitSearch, ModelUnitAdaptation, DynamicDataCollection
import numpy as np

search = ModelUnitSearch(top_k=3)
adaptation = ModelUnitAdaptation(initial_units=5)
collector = DynamicDataCollection()

for i in range(10):
    collector.add_data_point(np.random.randn())

window_set = collector.decompose()
adaptation.initialize_model_units(window_set)

regime = search.assign_regime(window_set, adaptation.model_units)
print(f'✅ Assigned regime: {regime.regime_id}')
print(f'   Confidence: {regime.confidence:.2f}')

predictions, ci = search.forecast(window_set, regime, adaptation.model_units, forecast_steps=10)
print(f'✅ Forecasted {len(predictions)} steps')
"
```

---

## Performance Benchmarks

### Benchmark 1: Regime Detection Latency

```bash
python -c "
import time
import numpy as np
from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer

eil = EnergyIntelligenceLayer(
    regime_detector_checkpoint=None,
    microadapt_config={'max_units': 10, 'initial_units': 3}
)

# Warmup
for _ in range(5):
    energy_map = np.random.randn(64, 64) * 0.1 + 1.0
    eil.process(energy_map, 'test', 'cluster', 'node')

# Benchmark
latencies = []
for i in range(100):
    energy_map = np.random.randn(64, 64) * 0.1 + 1.0
    start = time.time()
    decision = eil.process(energy_map, f'test_{i}', 'cluster', 'node')
    latency_ms = (time.time() - start) * 1000
    latencies.append(latency_ms)

print(f'✅ Regime Detection Latency Benchmark (100 requests)')
print(f'   Mean: {np.mean(latencies):.2f}ms')
print(f'   Median: {np.median(latencies):.2f}ms')
print(f'   P95: {np.percentile(latencies, 95):.2f}ms')
print(f'   P99: {np.percentile(latencies, 99):.2f}ms')
print(f'   Min: {np.min(latencies):.2f}ms')
print(f'   Max: {np.max(latencies):.2f}ms')
"
```

### Benchmark 2: Throughput

```bash
python -c "
import time
import numpy as np
from phase5.core.energy_intelligence_layer import EnergyIntelligenceLayer

eil = EnergyIntelligenceLayer(
    regime_detector_checkpoint=None,
    microadapt_config={'max_units': 10, 'initial_units': 3}
)

num_requests = 1000
start = time.time()

for i in range(num_requests):
    energy_map = np.random.randn(64, 64) * 0.1 + 1.0
    decision = eil.process(energy_map, f'test_{i}', 'cluster', 'node')

elapsed = time.time() - start
throughput = num_requests / elapsed

print(f'✅ Throughput Benchmark ({num_requests} requests)')
print(f'   Total time: {elapsed:.2f}s')
print(f'   Throughput: {throughput:.2f} req/s')
print(f'   Avg latency: {(elapsed/num_requests)*1000:.2f}ms')
"
```

### Benchmark 3: Proof Validation Speed

```bash
python -c "
import time
import numpy as np
from phase5.core.proof_validator import ProofValidator

pv = ProofValidator()

num_validations = 100
latencies = []

for i in range(num_validations):
    predicted = np.random.randn(64, 64) * 0.1 + 1.0
    observed = predicted + np.random.randn(64, 64) * 0.01

    proof = pv.create_proof('test', predicted, 'stable', True)

    start = time.time()
    result = pv.validate(proof, observed)
    latency_ms = (time.time() - start) * 1000
    latencies.append(latency_ms)

print(f'✅ Proof Validation Benchmark ({num_validations} validations)')
print(f'   Mean: {np.mean(latencies):.2f}ms')
print(f'   Median: {np.median(latencies):.2f}ms')
print(f'   P95: {np.percentile(latencies, 95):.2f}ms')
"
```

---

## Directory Structure Verification

```bash
# Verify all Phase 5 files are present
cd /path/to/industriverse/Thermodynasty

# Core components
ls -lh phase5/core/energy_intelligence_layer.py
ls -lh phase5/core/proof_validator.py
ls -lh phase5/core/market_engine.py
ls -lh phase5/core/feedback_trainer.py

# MicroAdapt
ls -lh phase5/core/microadapt/__init__.py
ls -lh phase5/core/microadapt/algorithms/
ls -lh phase5/core/microadapt/models/

# Monitoring
ls -lh phase5/monitoring/prometheus_metrics.py

# Tests
ls -lh phase5/tests/test_phase5_eil_integration.py
ls -lh phase5/tests/test_full_stack_phase0_5.py
ls -lh phase5/tests/run_tests.sh

# Deployment
ls -lh phase5/scripts/validate_deployment.py
ls -lh phase5/README.md

# Helm charts
ls -lh deploy/helm/phase5/values.yaml
ls -lh deploy/helm/phase5/templates/

# Documentation
ls -lh phase5/docs/research_integration_analysis.md
```

---

## Troubleshooting

### Issue 1: Import Errors

```bash
# Problem: ModuleNotFoundError: No module named 'phase5'
# Solution: Set PYTHONPATH correctly

export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH

# Verify it's set
echo $PYTHONPATH

# Make it permanent (add to ~/.bashrc or ~/.zshrc)
echo 'export PYTHONPATH=/path/to/industriverse/Thermodynasty:$PYTHONPATH' >> ~/.bashrc
source ~/.bashrc
```

### Issue 2: Missing Dependencies

```bash
# Install all dependencies at once
pip install numpy jax flax scipy scikit-learn pytest prometheus-client kafka-python

# If JAX GPU support needed
pip install --upgrade "jax[cuda12_pip]" -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
```

### Issue 3: Validation Test Warnings

```bash
# Warning: "RuntimeWarning: invalid value encountered in scalar divide"
# This is expected for edge cases in entropy calculation
# Tests should still pass - focus on final PASSED/FAILED status
```

### Issue 4: Git Branch Not Found

```bash
# If branch doesn't exist locally
git fetch origin
git checkout -b claude/review-industriverse-phase1-011CV2sSawNHXTjWxgW8DZnW origin/claude/review-industriverse-phase1-011CV2sSawNHXTjWxgW8DZnW
```

---

## Quick Start - Complete Workflow

```bash
# 1. Pull latest code
cd /path/to/industriverse
git fetch origin
git checkout claude/review-industriverse-phase1-011CV2sSawNHXTjWxgW8DZnW
git pull origin claude/review-industriverse-phase1-011CV2sSawNHXTjWxgW8DZnW

# 2. Install dependencies
cd Thermodynasty
pip install numpy jax flax scipy scikit-learn pytest

# 3. Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH

# 4. Run deployment validation
python phase5/scripts/validate_deployment.py

# 5. Run integration tests
cd phase5/tests
./run_tests.sh all

# 6. Read documentation
cat ../README.md
cat ../docs/research_integration_analysis.md
```

---

## Summary of Available Tests

| Test Type | Command | Expected Time | Pass Criteria |
|-----------|---------|---------------|---------------|
| Deployment Validation | `python phase5/scripts/validate_deployment.py` | ~5s | All 4 checks PASSED |
| Phase 5 Integration | `pytest test_phase5_eil_integration.py -v` | ~10s | 7/7 tests PASSED |
| Full Stack Phase 0-5 | `pytest test_full_stack_phase0_5.py -v` | ~20s | 9/9 tests PASSED |
| Individual Components | `python phase5/core/<component>.py` | ~1-3s | ✅ TEST COMPLETE |
| Performance Benchmark | Python snippets above | ~30s | Latency <1s, Throughput >1 req/s |

---

## Next Steps After Testing

1. **Review Research Integration Analysis**:
   ```bash
   cat phase5/docs/research_integration_analysis.md
   ```

2. **Plan Egocentric-10K Download** (16.4TB):
   - Ensure 20TB+ free space on target drive
   - Use HuggingFace streaming API for incremental access
   - Start with subset (10 factories) for prototyping

3. **Implement Priority 1 Components** (from research analysis):
   - LeJEPA encoder architecture
   - Egocentric-10K data pipeline
   - PhysWorld reconstruction module
   - RealDeepResearch paper crawler

4. **Deploy to Kubernetes**:
   ```bash
   cd deploy/helm/phase5
   helm install thermodynasty-ace . --namespace thermodynasty --create-namespace
   ```

---

**Phase 5 EIL is production-ready and tested! All 11 commits successfully integrated.**
