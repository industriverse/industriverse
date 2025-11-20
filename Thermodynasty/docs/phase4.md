# phase4.md
# Claude Directive: Implement NVP (Next Vector Prediction) using JAX diffusion models and thermodynamic priors.

---

## 🧩 Phase Context: 4 — NVP Engine Development
Goal: Build the **core predictive engine** that models the evolution of energy states over time.

---

### 🧠 Conceptual Overview

NVP represents a **generalized diffusion model** that predicts next-step energy vector fields across any domain:

```
E_t → E_{t+1} = f(E_t, ∇E_t, T, external_inputs)
```

It replaces Next-Token Prediction (LLMs) with **Next-Vector Prediction** (physics).

💡 *Interpretation:*
Claude Code should treat each predicted vector as a point in a high-dimensional energy landscape where gradient descent = thermodynamic optimization.

---

### 🧩 Core Components

| Component | Function | File |
|------------|-----------|------|
| atlas_loader.py | Load + vectorize maps | `phase4/core/atlas_loader.py` |
| synthetic_generator.py | Generate synthetic time-series | `phase4/data/synthetic_generator.py` |
| nvp_model.py | Main JAX diffusion model | `phase4/nvp/nvp_model.py` |
| trainer.py | Training loop + thermo loss | `phase4/nvp/trainer.py` |
| ace_base.py | ACE agent lifecycle | `phase4/agents/ace_base.py` |

---

### ⚙️ Model Design Directives

#### 1. Architecture
- Encoder–decoder diffusion pipeline with latent `z_t` embedding
- Predict next-state energy map: `ΔE = f(E_t, ∇E_t, context)`
- Hierarchical resolutions [64, 128, 256] using pyramid precomputation
- Optional noise conditioning for stochastic regimes

#### 2. Loss Function

```python
L_total = L_MSE + λ₁ * L_energy_conservation + λ₂ * L_entropy_smooth
```

Components:
- `L_MSE`: Mean squared error on predicted vs actual E_{t+1}
- `L_energy_conservation`: Penalize predicted E violating first law
  ```python
  L_conservation = |sum(E_pred) - sum(E_actual)| / sum(E_actual)
  ```
- `L_entropy_smooth`: Encourage monotonic entropy change (no unphysical spikes)
  ```python
  L_entropy = max(0, entropy(E_t) - entropy(E_{t+1}) - threshold)
  ```

**Hyperparameters:**
- λ₁ = 0.1 (energy conservation weight)
- λ₂ = 0.05 (entropy smoothness weight)

#### 3. Data Handling
- **Energy maps:** `.npy`, `.hdf5` formats
- **Metadata:** Neo4j nodes (`EnergySnapshot`, `Domain`)
- **Temporal linking:** `E_t` → `E_{t+1}` pairs with timestamps
- **Synthetic generation:** If insufficient real data (<1000 samples)

**Data Pipeline:**
```python
def load_energy_batch(domain: str, scale: int, window: int):
    """
    Load temporal window of energy maps.

    Args:
        domain: Physics domain ('plasma_physics', 'fluid_dynamics', etc.)
        scale: Resolution (64, 128, or 256)
        window: Number of time steps (default 10)

    Returns:
        batch: (N, H, W, T) array of energy maps
        metadata: Dict with entropy, timestamps, regime labels
    """
    pass
```

#### 4. Evaluation Metrics

**Primary Metric: Energy Fidelity**
```python
fidelity = 1 - |ΔE_pred - ΔE_actual| / |ΔE_actual|
```

**Secondary Metrics:**
- RMSE on raw energy values
- Entropy coherence: `|S(E_pred) - S(E_actual)| / S(E_actual)`
- Gradient alignment: `cos_similarity(∇E_pred, ∇E_actual)`

**Target Performance:**
- Energy fidelity > 0.90
- Entropy violations < 1% of predictions
- Gradient alignment > 0.85

---

### 🔬 Secret Sauce Implementation Details

#### Sauce 1: Atlas Pyramids + ∇E Precompute
```python
def precompute_pyramids(energy_map: np.ndarray):
    """
    Generate multi-scale pyramid and precompute gradients.

    Returns:
        pyramids: {64: E_64, 128: E_128, 256: E_256}
        gradients: {64: ∇E_64, 128: ∇E_128, 256: ∇E_256}
    """
    from scipy.ndimage import zoom, gaussian_gradient_magnitude

    pyramids = {}
    gradients = {}

    for scale in [64, 128, 256]:
        # Downsample to target scale
        factor = scale / energy_map.shape[0]
        pyramids[scale] = zoom(energy_map, factor, order=3)

        # Compute gradients (∇E)
        grad_x = np.gradient(pyramids[scale], axis=0)
        grad_y = np.gradient(pyramids[scale], axis=1)
        gradients[scale] = np.stack([grad_x, grad_y], axis=-1)

    return pyramids, gradients
```

#### Sauce 2: Thermodynamic Priors Decorator
```python
def thermo_compile(energy_budget: float = 1.0, entropy_max: float = 10.0):
    """
    Decorator that enforces thermodynamic constraints at runtime.

    Usage:
        @thermo_compile(energy_budget=0.5, entropy_max=8.0)
        def predict_next_vector(E_t, context):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # Check energy conservation
            E_in = np.sum(args[0])  # Assuming first arg is E_t
            E_out = np.sum(result)
            if abs(E_out - E_in) / E_in > energy_budget:
                raise ThermodynamicViolation(
                    f"Energy conservation violated: ΔE/E = {abs(E_out-E_in)/E_in:.3f}"
                )

            # Check entropy bound
            entropy = -np.sum(result * np.log(result + 1e-10))
            if entropy > entropy_max:
                raise ThermodynamicViolation(
                    f"Entropy exceeded: S = {entropy:.2f} > {entropy_max}"
                )

            return result
        return wrapper
    return decorator


class ThermodynamicViolation(Exception):
    """Raised when physical constraints are violated."""
    pass
```

#### Sauce 3: Cognitive Vector Logging
```python
def log_energy_vector(E_pred, E_obs, domain, timestamp):
    """
    Log prediction for DGM meta-learning.

    Stores: predicted energy, observed energy, delta, entropy, regime
    """
    ΔE = E_obs - E_pred
    entropy_pred = -np.sum(E_pred * np.log(E_pred + 1e-10))
    entropy_obs = -np.sum(E_obs * np.log(E_obs + 1e-10))

    log_entry = {
        'timestamp': timestamp,
        'domain': domain,
        'E_pred_mean': float(np.mean(E_pred)),
        'E_obs_mean': float(np.mean(E_obs)),
        'ΔE_rmse': float(np.sqrt(np.mean(ΔE**2))),
        'entropy_pred': float(entropy_pred),
        'entropy_obs': float(entropy_obs),
        'fidelity': 1 - abs(np.sum(ΔE)) / abs(np.sum(E_obs))
    }

    # Append to training log for DGM
    with open('data/nvp_training_log.jsonl', 'a') as f:
        f.write(json.dumps(log_entry) + '\n')
```

---

### 🧭 Development Tasks (Sprint Order)

#### Task 1: Data Layer Implementation
**File:** `phase4/core/atlas_loader.py`

**Requirements:**
- Load .npy/.hdf5 energy maps
- Validate shapes (must be square or 2:3 aspect ratio)
- Precompute ∇E using `np.gradient`
- Generate pyramid scales [64, 128, 256]
- Store metadata in Neo4j (`EnergySnapshot` nodes)

**Claude Directive:**
```
Implement atlas_loader.py with:
- Class EnergyAtlasLoader(domain: str, scale: int)
- Method load_batch(window: int) → (maps, metadata)
- Method precompute_pyramids() → dict
- Schema validation: assert map.shape in [(64,64), (128,128), (256,256), (128,384)]
- Neo4j integration via py2neo
```

---

#### Task 2: Synthetic Data Generator
**File:** `phase4/data/synthetic_generator.py`

**Requirements:**
- Generate realistic energy map sequences when real data < 1000 samples
- Physics-based perturbations: rotation, noise, thermal diffusion
- Maintain thermodynamic validity: energy conservation, entropy monotonicity
- Export in same format as real data

**Claude Directive:**
```
Implement synthetic_generator.py with:
- Function generate_sequence(base_map, n_steps, perturbation_strength)
- Perturbations: Gaussian noise, rotation (0-360°), thermal blur
- Validation: check energy conservation within 5%
- Export as .npy with timestamp metadata
```

---

#### Task 3: NVP Model Architecture
**File:** `phase4/nvp/nvp_model.py`

**Requirements:**
- JAX/Flax implementation
- Encoder-decoder with residual connections
- Multi-scale input (pyramid levels)
- Bayesian uncertainty estimation

**Claude Directive:**
```
Implement nvp_model.py using JAX/Flax:
- Class NVPModel(nn.Module)
  - Encoder: 3 conv layers + residual blocks
  - Latent: z_t embedding (dim=512)
  - Decoder: 3 transposed conv layers
  - Uncertainty head: outputs mean + log_var
- Forward pass: (E_t, ∇E_t, context) → (E_{t+1}_mean, E_{t+1}_var)
- JIT compilation for speed
```

---

#### Task 4: Training Loop with Thermo Loss
**File:** `phase4/nvp/trainer.py`

**Requirements:**
- Implement L_total = L_MSE + λ₁*L_conservation + λ₂*L_entropy
- Use Optax optimizer (Adam, lr=1e-4)
- 5% data for entropy validation (held-out)
- Log fidelity, RMSE, entropy coherence per epoch
- Checkpoint every 10 epochs

**Claude Directive:**
```
Implement trainer.py with:
- Function train_nvp(model, train_data, val_data, epochs=100)
- Loss: MSE + 0.1*conservation + 0.05*entropy_smooth
- Optimizer: optax.adam(1e-4)
- Metrics: log to wandb or tensorboard
- Checkpoints: save to phase4/checkpoints/
```

---

#### Task 5: ACE Agent Lifecycle
**File:** `phase4/agents/ace_base.py`

**Requirements:**
- Implement 8-stage lifecycle (spawn → retire)
- Socratic Loop: SocratesAgent, PlatoSynthesizer, AtlasIndexer
- Shadow ensemble: 3 independent instances, consensus voting
- Energy budget enforcement

**Claude Directive:**
```
Implement ace_base.py with:
- Class ACEAgent(hypothesis: str, energy_budget: float)
  - Method spawn() → initialize
  - Method compose() → SocratesAgent expands hypothesis
  - Method plan() → AtlasIndexer queries Energy Atlas
  - Method schedule() → ASI Core placement
  - Method execute() → TTF agents run
  - Method report() → log to Neo4j
  - Method retire() → archive + PoE trigger
- Shadow consensus: require 2/3 agreement
```

---

### 🧪 Testing Requirements

**Unit Tests:**
```python
def test_energy_conservation():
    """Verify sum(E_pred) ≈ sum(E_actual) within 5%"""
    pass

def test_entropy_monotonicity():
    """Verify S(E_{t+1}) >= S(E_t) - threshold"""
    pass

def test_gradient_smoothness():
    """Verify |∇²E| < threshold (no discontinuities)"""
    pass

def test_pyramid_consistency():
    """Verify downsampling preserves total energy"""
    pass
```

**Integration Tests:**
```python
def test_end_to_end_prediction():
    """Load map → predict → validate fidelity > 0.9"""
    pass

def test_ace_lifecycle():
    """Spawn ACE → execute → retire with PoE mint"""
    pass
```

---

### 📊 Success Criteria

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Energy Fidelity | > 0.90 | Test on held-out domain |
| Entropy Violations | < 1% | Count predictions with ΔS < 0 |
| Training Time | < 24 hours | 100 epochs on 256×256 maps |
| Inference Speed | < 100ms | Single prediction latency |
| Gradient Alignment | > 0.85 | Cosine similarity |

---

<!-- thermodynamic principle: Claude should ensure energy loss functions obey physical constraints—no perpetual motion predictions. -->

<<< PHASE_4_END >>>
