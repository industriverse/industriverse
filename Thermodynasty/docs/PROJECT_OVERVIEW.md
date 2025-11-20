# PROJECT_OVERVIEW.md
# Claude Directive: Establish full architectural context for Industriverse Phase 4–5 development.

---

## 🧩 Phase Context: GLOBAL OVERVIEW
This document gives Claude Code the **holistic understanding** of the Industriverse architecture, purpose, and engineering ethos before entering Phase 4 or Phase 5 manifests.

### 🧠 Project Summary
**Industriverse** is a physics-native AI framework that models, predicts, and optimizes energy transformations across physical, cognitive, and economic domains.
It unifies *thermodynamics, computation, reasoning,* and *markets* under one universal mathematical substrate.

**Core Principle:**
```
Energy = Information = Computation = Intelligence
```

The project transitions from symbolic reasoning → physical representation → energetic prediction via:

```
Next Token Prediction (LLMs) → Next Vector Prediction (Energy Models)
```

---

## ⚙️ System Hierarchy (Claude Context Map)

```
/industriverse/
├── phase0_3/              # Completed foundational work
├── phase4/                # NVP (Next Vector Prediction) – active
├── phase5/                # EIL (Energy Intelligence Layer) – next
├── core/                  # Shared libraries (energy_atlas, asi_core, neo4j_client)
├── data/                  # Energy maps, telemetry, training datasets
├── deploy/                # K8s, Helm, infrastructure
├── docs/                  # All markdown manifests (this file + others)
└── tests/                 # Validation scripts
```

---

## 🌌 Architectural Flow

```
Hypothesis Input
    ↓
Energy Atlas (11-domain vector maps)
    ↓
Energy Vector Space (E, ∇E, entropy, temporal embeddings)
    ↓
ASI Core (Boltzmann scheduler, P(x) ∝ exp(-E(x)/T))
    ↓
NVP Engine (predicts E_{t+1} via diffusion)
    ↓
EIL (sense, predict, act)
    ↓
ProofEconomy (mint PoE, distribute credits)
```

💡 **Thermodynamic Principle:**
Every prediction (vector update) represents an *entropy descent* — a transition toward lower informational disorder.

---

## 🧠 Core Modules

| Module | Function | Language | Storage | Framework |
|--------|-----------|-----------|-----------|------------|
| Energy Atlas | Vectorized energy maps across domains | Python | Neo4j, NumPy | JAX |
| ASI Core | Boltzmann scheduler, energy sampling | Python | - | JAX |
| NVP Engine | Next Vector Prediction via diffusion | Python | NumPy/HDF5 | Flax/JAX |
| EIL | Energy sensing & control | Python | Parquet/Influx | PyTorch/JAX |
| ProofEconomy | Token minting, consensus | Solidity/Python | Polygon | Web3.py |

---

## 🪐 Strategic Intent

Industriverse Phase 4–5 will:
1. **Create a predictive substrate (NVP)** – models next energetic state across systems.
2. **Build self-regulating intelligence (EIL)** – closes the sensing → prediction → actuation loop.
3. **Establish ProofEconomy** – value system tying thermodynamic accuracy to tokenized proof.

---

## 🧬 ACE (Autonomous Cognitive Entity) Lifecycle

```
1. spawn       → Hypothesis created
2. compose     → SocratesAgent + UserLM expand goal
                 PlatoSynthesizer consolidates
3. plan        → AtlasIndexer queries Energy Atlas + Neo4j
                 Builds placement DAG
4. schedule    → ASI Core: Boltzmann thermodynamic placement
5. execute     → TTF agents run containers
6. monitor     → Energy telemetry collection
7. report      → Persist results, trigger NVP/EIL feedback
8. retire      → Archive hypothesis, mint PoE if validated
```

**Critical Distinction:**
- **Services (1,090)** = computational microservices in registry
- **ACE agents** = cognitive actors (hypothesis → execution orchestration)

---

## 🔒 Shadow Twin Consensus (BFT Hybrid)

**Phase 1 (Current):** Byzantine Fault Tolerant multi-model voting
- 3-phase: Proposal → Vote → Commit
- Requires ≥f+1 agreement (f = tolerated faults)

**Consensus Data:**
- EnergySnapshot (map changes)
- High-value placement decisions
- Proof documents (execution trace + energy consumption)

**Multi-Dimensional Proof Requirements:**
1. Predicted energy (NVP)
2. Observed energy delta (actual)
3. Model consensus (Shadow Twin agreement)

When all three align within thresholds → **mint PoE token**

---

## 📊 Energy Atlas Current State

**Target Implementation:**
- **256×256** resolution (128×384 for rectangular domains)
- **Multiscale Pyramids:** Store at [64, 128, 256] resolutions
- **Precomputed ∇E** (gradients) for each scale
- **EnergySnapshot versioning** for time-series training
- Neo4j schema: `EnergyDomain`, `EnergyMap`, `EnergySnapshot` nodes

**Data Catalog Components:**
- map_id, domain, resolution, min/max energy, entropy
- Timestamp, provenance, version

---

## 🧪 The Eight Secret Sauces

1. **Atlas Pyramids + ∇E Precompute** - Multi-scale learning, 10x training speedup
2. **Thermodynamic Priors in Loss** - Physics constraints prevent unphysical predictions
3. **Shadow Agent Ensembles** - 3 independent ACE instances, 80% hallucination reduction
4. **Thermal Tap** - Incremental THRML map updates (online learning)
5. **DGM Thermo-Aware Fitness** - Evolve energy-efficient architectures
6. **3-Factor PoE Minting** - High-confidence validation only
7. **O(1) Edge Sketches** - K-means++ micro clusters, scales to 1,000+ streams
8. **Synthetic Data Generator** - Physics-based augmentation when data sparse

---

## 🧩 Claude Guidance

### Task:
- Use this document as the **root context** for interpreting all subphase manifests.
- All reasoning in `phase4.md` and `phase5.md` must remain consistent with:
  - Thermodynamic logic (Boltzmann, diffusion, entropy)
  - Energy-minimization ethics (low-energy, high-coherence computation)
  - Phase-isolated development (no code bleeding between phase4 and phase5)

### Execution Principles:
1. **Context is environment state** - Load manifests at session start
2. **Energy principles are constraints** - Every function has thermodynamic budget
3. **Phase isolation is architectural law** - Phase 4 ↔ Phase 5 only via defined APIs
4. **Chain-of-build preserves lineage** - Stage scaffold → stubs → implementation

### Thermodynamic Constraints (Non-Negotiable):
- Energy conservation must hold: `∑E_in = ∑E_out + ∑E_stored`
- Entropy cannot decrease without justification: `ΔS ≥ 0`
- Temperature gradients must be smooth: `|∇T| < threshold`

---

<!-- thermodynamic principle: Claude should treat reasoning paths as "energy trajectories" — lower-entropy chains are preferred. -->

<<< PROJECT_OVERVIEW_END >>>
