# Phase 5: EIL → Diffusion Engine Development Plan

## Week 1–2 : Formalization
- Derive diffusion update rule from EIL energy gradients:  
  `x_{t+1} = x_t - ∇E(x_t) + σ ε`
- Implement JAX/PyTorch module `EnergyDiffusionModel`.
- Integrate EIL telemetry as conditioning input.

## Week 3–4 : Training Pipeline
- Build dataset loader for Energy Atlas embeddings.
- Train conditional diffusion model (reverse process).
- Validate with synthetic .hdf5 physics data.

## Week 5–6 : Integration & API
- Add `/diffusion/sample` and `/diffusion/optimize` endpoints in FastAPI.
- Connect to Thermodynasty ACE Bridge for energy-law gating.
- Add Kafka topic `energy.diffusion.events`.

## Week 7–8 : Acceleration
- Implement CUDA/JAX XLA kernels for reverse diffusion.
- Target latency < 10 ms for 256×256 energy maps.
- Benchmark vs baseline EIL optimizer.

## Week 9–10 : Validation & Docs
- Physics-law validation (ΔE < 0.01, ΔS ≥ 0).  
- Compare with OpenFOAM/BOUT++ ground truth.  
- Write Jupyter tutorial: “Energy-Guided Diffusion in Industriverse.”

## Integration Checklist
- [ ] NVP conditioning  
- [ ] ACE feedback loop  
- [ ] Proof-Validator hook  
- [ ] Monitoring (Grafana)  
- [ ] Deployment (Helm)

---

# Claude Code Execution Directives

## Core Modules to Implement
1. `energy_diffusion_core.py`
   - Classes: `EnergyDiffusionModel`, `EnergyScheduler`
   - Functions:
     - `forward_diffuse(x0, t, noise_schedule)`
     - `reverse_denoise(xt, context)`
     - `energy_gradient(x)` – from EIL
     - `boltzmann_weight(x)` – exp(-E/kT)

2. `energy_guided_sampler.py`
   - Implements Boltzmann-weighted sampling.
   - Interfaces with `ACEAgent` for adaptive temperature control.

3. `diffusion_api.py`
   - FastAPI routes:  
     - `POST /diffuse` → generate configuration samples  
     - `POST /optimize` → return lowest-energy sample  

4. `tests/test_diffusion_validation.py`
   - Energy conservation test  
   - Entropy monotonicity test  
   - Physical-law regression vs .hdf5 baseline  

## Configuration Directives
```yaml
EIL:
  cluster: industriverse-aws
  namespace: plan-solidify-phase5
  serviceAccount: thermodynasty-ace
  gpu: true
  maxLatencyMs: 10
Diffusion:
  learningRate: 1e-4
  noiseSchedule: cosine
  timesteps: 1000
  batchSize: 32
Validation:
  energyTolerance: 0.01
  entropyDriftMax: -0.001
```

## Expected Outputs
- `diffusion_checkpoints/*.ckpt`
- `metrics/energy_fidelity.json`
- `visuals/entropy_evolution.mp4`
- `api_docs/diffusion_openapi.yaml`
