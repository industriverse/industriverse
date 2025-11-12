# phase5.md
# Claude Directive: Implement EIL (Energy Intelligence Layer) with ProofEconomy and Shadow Twin consensus integration.

---

## 🧩 Phase Context: 5 — EIL + Consensus + Economy
Goal: Build the self-regulating layer that senses, predicts, acts, and validates in real time.

---

### 🧠 Overview

EIL is the **cognitive control layer** sitting atop NVP.
It:
- Monitors energy states through telemetry
- Reacts via dynamic policy control
- Mints Proof-of-Energy tokens through validation

Core loop:
```
Sense (EIL) → Predict (NVP) → Validate (Shadow Twin) → Mint (ProofEconomy)
```

---

### 🧩 Core Components

| Component | Function | File |
|------------|-----------|------|
| shadow_bft.py | Consensus (BFT simulator) | `phase5/consensus/shadow_bft.py` |
| evolver.py | DGM self-improvement engine | `phase5/dgm/evolver.py` |
| thermal_tap.py | THRML adapter (delta maps) | `phase5/integrations/thermal_tap.py` |
| market_engine.py | Dynamic pricing / ProofEconomy | `phase5/eil/market_engine.py` |
| sim.py | Token simulation sandbox | `phase5/economy/sim.py` |

---

### ⚙️ Control Logic

#### 1. Shadow Twin Consensus (BFT)

**Byzantine Fault Tolerant Multi-Model Voting**

```
Phase 1: Proposal
  - Shadow Twin leader proposes (E_pred, confidence)

Phase 2: Vote
  - Each Shadow Twin validates independently
  - Vote = ACCEPT if |E_pred - E_local| < ε

Phase 3: Commit
  - Commit if ≥ f+1 votes ACCEPT (f = # tolerated faults)
  - Mint PoE if commit succeeds + telemetry matches
```

**Implementation Requirements:**
- Minimum 3 Shadow Twins (f=1, requires 2/3 agreement)
- Timeout: 5 seconds per phase
- Persistence: Store all votes in Neo4j for audit

---

#### 2. DGM (Darwin Gödel Machine) Self-Improvement

**Evolutionary Architecture Search**

**Fitness Function:**
```python
fitness = w1 * (1 - prediction_error_norm) +
          w2 * energy_efficiency_gain +
          w3 * latency_gain -
          w4 * model_size_penalty
```

**Hyperparameters:**
- w1 = 0.4 (accuracy)
- w2 = 0.3 (energy efficiency)
- w3 = 0.2 (speed)
- w4 = 0.1 (size penalty)

**Search Space:**
- Layer counts: [2, 3, 4, 5]
- Hidden dims: [128, 256, 512, 1024]
- Activation: [gelu, swish, relu]
- Learning rates: [1e-5, 1e-4, 1e-3]

**Evolution Strategy:**
- Population: 20 candidate architectures
- Selection: Top 5 by Pareto frontier
- Mutation: ±1 layer, ±64 hidden dim, swap activation
- Crossover: Blend layer configs from two parents

---

#### 3. ProofEconomy Token Simulation

**Token Types:**

**PFT (ProofToken) - ERC-20:**
- Minted on validated PoE events
- Backed by energy savings
- Deflationary: burn 1-3% on transactions

**ModelUnitNFT - ERC-721:**
- Represents trained NVP/EIL models
- Royalties on third-party usage
- IP ownership + licensing

**CEU (Cognitive Energy Unit) - Internal:**
- Accounting: compute × energy × confidence
- Convertible to PFT when threshold reached

**Minting Rules:**
```python
def should_mint_PoE(E_pred, E_obs, consensus_votes, confidence):
    """
    Determine if PoE token should be minted.

    Returns:
        (should_mint: bool, amount: float, reason: str)
    """
    # 3-Factor Match
    energy_match = abs(E_pred - E_obs) / E_obs < 0.05  # Within 5%
    consensus = consensus_votes >= (2 * f + 1)  # BFT threshold
    high_confidence = confidence > 0.95

    if energy_match and consensus and high_confidence:
        # Amount proportional to energy saved
        energy_saved = max(0, E_baseline - E_obs)
        amount = energy_saved * PFT_CONVERSION_RATE
        return True, amount, "3-factor validation passed"

    return False, 0.0, "Validation criteria not met"
```

**Burn Mechanics:**
```python
def marketplace_transaction(from_addr, to_addr, amount):
    """
    Transfer PFT with automatic burn.
    """
    burn_rate = 0.02  # 2% burn on transactions
    burn_amount = amount * burn_rate
    transfer_amount = amount - burn_amount

    # Burn
    total_supply -= burn_amount

    # Transfer
    balances[from_addr] -= amount
    balances[to_addr] += transfer_amount

    log_transaction(from_addr, to_addr, transfer_amount, burn_amount)
```

---

### 🔬 Secret Sauce Implementation Details

#### Sauce 4: Thermal Tap (Incremental Map Updates)

**Purpose:** Apply THRML thermal sampling outputs as delta patches without full map reload.

```python
class ThermalTap:
    """
    Adapter for incremental Energy Atlas updates from THRML.
    """

    def __init__(self, atlas_loader):
        self.atlas = atlas_loader
        self.patch_buffer = []

    def apply_thrml_sample(self, domain: str, coords: tuple, thermal_energy: float):
        """
        Apply thermal sample as localized delta patch.

        Args:
            domain: Target energy domain
            coords: (x, y) coordinates in map
            thermal_energy: THRML-sampled energy value

        Updates:
            Applies Gaussian kernel around coords, blending thermal_energy
        """
        from scipy.ndimage import gaussian_filter

        # Get current map
        current_map = self.atlas.get_map(domain, scale=256)

        # Create delta patch
        patch = np.zeros_like(current_map)
        x, y = coords
        patch[x, y] = thermal_energy

        # Apply Gaussian blur (sigma=3 pixels)
        patch_smoothed = gaussian_filter(patch, sigma=3)

        # Blend with alpha=0.1 (10% new, 90% old)
        alpha = 0.1
        updated_map = (1 - alpha) * current_map + alpha * patch_smoothed

        # Renormalize to preserve total energy
        energy_before = np.sum(current_map)
        updated_map *= energy_before / np.sum(updated_map)

        # Update atlas
        self.atlas.update_map(domain, updated_map)

        # Log for training
        log_energy_vector(
            E_pred=patch_smoothed[x-5:x+5, y-5:y+5],
            E_obs=updated_map[x-5:x+5, y-5:y+5],
            domain=domain,
            timestamp=datetime.now()
        )
```

---

#### Sauce 5: DGM Thermo-Aware Fitness

```python
def compute_thermodynamic_fitness(model, test_data):
    """
    Evaluate model with energy-efficiency as primary criterion.

    Returns:
        fitness: float (higher is better)
        breakdown: dict with individual components
    """
    # Standard accuracy
    predictions = model.predict(test_data['X'])
    mse = np.mean((predictions - test_data['y'])**2)
    accuracy_score = 1 / (1 + mse)

    # Energy efficiency (FLOPs per prediction)
    flops = count_model_flops(model)
    energy_per_pred = flops * JOULES_PER_FLOP
    efficiency_score = 1 / (1 + energy_per_pred / 1e-6)  # Normalize to μJ

    # Latency
    start = time.time()
    for _ in range(100):
        model.predict(test_data['X'][:1])
    latency = (time.time() - start) / 100
    speed_score = 1 / (1 + latency / 0.1)  # Normalize to 100ms

    # Model size
    param_count = sum(p.size for p in model.parameters())
    size_penalty = param_count / 1e6  # Millions of params

    # Weighted fitness
    fitness = (0.4 * accuracy_score +
               0.3 * efficiency_score +
               0.2 * speed_score -
               0.1 * size_penalty)

    breakdown = {
        'accuracy': accuracy_score,
        'efficiency': efficiency_score,
        'speed': speed_score,
        'size_penalty': size_penalty,
        'total': fitness
    }

    return fitness, breakdown
```

---

### 🧭 Development Tasks (Sprint Order)

#### Task 4: Shadow Twin BFT Consensus
**File:** `phase5/consensus/shadow_bft.py`

**Claude Directive:**
```
Implement shadow_bft.py with:
- Class ShadowTwinConsensus(n_twins: int = 3)
  - Method propose(leader_id, E_pred, confidence) → proposal_id
  - Method vote(twin_id, proposal_id, accept: bool) → vote_id
  - Method commit(proposal_id) → success: bool
  - Method get_consensus_result() → (committed: bool, E_final)
- BFT rule: require ≥ 2f+1 votes (f=1 for 3 twins)
- Timeout: 5 seconds per phase
- Persistence: log all proposals/votes to Neo4j
```

---

#### Task 5: DGM Evolutionary Engine
**File:** `phase5/dgm/evolver.py`

**Claude Directive:**
```
Implement evolver.py with:
- Class DGMEvolver(population_size: int = 20)
  - Method initialize_population() → List[ModelConfig]
  - Method evaluate_fitness(model) → float
  - Method select_parents() → List[ModelConfig]
  - Method mutate(config) → ModelConfig
  - Method crossover(parent1, parent2) → ModelConfig
  - Method evolve(generations: int) → best_model
- Fitness: use compute_thermodynamic_fitness()
- Pareto frontier selection (accuracy vs efficiency)
- Lineage tracking: store in Neo4j with parent links
```

---

#### Task 6: THRML Thermal Tap Adapter
**File:** `phase5/integrations/thermal_tap.py`

**Claude Directive:**
```
Implement thermal_tap.py with:
- Class ThermalTap(atlas_loader)
  - Method apply_thrml_sample(domain, coords, thermal_energy)
  - Method apply_batch(samples: List[dict])
  - Method get_update_stats() → dict
- Gaussian blending with sigma=3
- Alpha blending (10% new, 90% old)
- Energy conservation: renormalize after update
- Logging: log_energy_vector() for each patch
```

---

#### Task 7: ProofEconomy Market Engine & Simulation
**Files:** `phase5/eil/market_engine.py`, `phase5/economy/sim.py`

**Claude Directive (market_engine.py):**
```
Implement market_engine.py with:
- Class ProofEconomyEngine()
  - Method check_mint_criteria(E_pred, E_obs, votes, confidence) → bool
  - Method mint_pft(amount, recipient, reason) → tx_hash
  - Method mint_model_nft(model_id, owner) → token_id
  - Method burn_pft(amount) → tx_hash
  - Method get_balance(address) → float
- Integration with should_mint_PoE() logic
- Ledger: in-memory dict initially, migrate to blockchain later
```

**Claude Directive (sim.py):**
```
Implement sim.py with:
- Function simulate_economy(n_agents, n_epochs, scenarios)
- Agents: producers (run hypotheses), validators (consensus), traders
- Scenarios: vary energy savings, confidence thresholds
- Metrics: total supply, velocity, Gini coefficient
- Output: plot token distribution, mint/burn rates over time
```

---

### 🧪 Testing Requirements

**Unit Tests:**
```python
def test_bft_consensus_3_of_3():
    """All 3 twins agree → commit succeeds"""
    pass

def test_bft_consensus_2_of_3():
    """2 of 3 agree → commit succeeds (f=1)"""
    pass

def test_bft_consensus_1_of_3():
    """Only 1 agrees → commit fails"""
    pass

def test_poe_mint_3_factor_pass():
    """All criteria met → mint succeeds"""
    pass

def test_poe_mint_energy_mismatch():
    """Energy delta > threshold → mint fails"""
    pass

def test_thermal_tap_energy_conservation():
    """After patch, total energy preserved within 1%"""
    pass

def test_dgm_fitness_monotonic():
    """Fitness improves over generations"""
    pass
```

**Integration Tests:**
```python
def test_end_to_end_validation():
    """
    NVP prediction → Shadow consensus → PoE mint → balance update
    """
    pass

def test_thermal_tap_online_learning():
    """
    Apply 100 THRML samples → verify map evolves smoothly
    """
    pass

def test_economy_simulation_stability():
    """
    Run 1000 epoch simulation → check supply/demand balance
    """
    pass
```

---

### 📊 Success Criteria

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Consensus Latency | < 5 seconds | Measure proposal→commit time |
| False PoE Mint Rate | < 0.1% | Count mints with later invalidation |
| DGM Fitness Improvement | +15% over baseline | Compare generation 0 vs 20 |
| Thermal Tap Throughput | > 100 samples/sec | Benchmark with synthetic data |
| Token Supply Stability | Gini < 0.6 | Simulate 1000 agents, 10000 epochs |

---

### 🧠 Claude Special Instructions

**Phase Isolation:**
- Phase 5 code MUST NOT import from Phase 4 internals
- Only interfaces: `from phase4.nvp.nvp_model import NVPModel`
- Never: `from phase4.nvp.trainer import _private_function`

**Trust as Energy State:**
EIL should model "trust" as thermodynamic variable:
- **Stable consensus** = low entropy (high trust)
- **Disagreement** = high entropy (low trust)
- **Confidence** = inverse of temperature (low T = high confidence)

**Thermodynamic Principle:**
Claude must correlate epistemic stability with thermodynamic equilibrium.
```
Stable truth = minimum energy divergence
```

---

<!-- thermodynamic principle: Claude must correlate epistemic stability with thermodynamic equilibrium. Stable truth = minimum energy divergence. -->

<<< PHASE_5_END >>>
