# REPOSITORY_MAP.md
# Module Dependency Graph and Import Structure for Industriverse Phase 4-5

---

## 📊 Directory Structure

```
/home/user/industriverse_phase4_5/
├── docs/                           # Documentation and manifests
│   ├── PROJECT_OVERVIEW.md         # Root context document
│   ├── phase4.md                   # NVP implementation directives
│   ├── phase5.md                   # EIL implementation directives
│   └── REPOSITORY_MAP.md           # This file
│
├── phase4/                         # Next Vector Prediction (NVP)
│   ├── core/                       # Core data handling
│   │   └── atlas_loader.py         # Energy Atlas data loader
│   ├── data/                       # Data processing
│   │   └── synthetic_generator.py  # Synthetic data generation
│   ├── nvp/                        # NVP model implementation
│   │   ├── nvp_model.py            # JAX/Flax NVP architecture
│   │   └── trainer.py              # Training loop with thermo loss
│   ├── agents/                     # ACE agent lifecycle
│   │   └── ace_base.py             # Base ACE agent implementation
│   └── tests/                      # Phase 4 unit tests
│       └── test_nvp.py
│
├── phase5/                         # Energy Intelligence Layer (EIL)
│   ├── consensus/                  # Shadow Twin consensus
│   │   └── shadow_bft.py           # BFT consensus implementation
│   ├── dgm/                        # Darwin Gödel Machine
│   │   └── evolver.py              # Evolutionary architecture search
│   ├── integrations/               # External integrations
│   │   ├── thermal_tap.py          # THRML adapter
│   │   └── jasmine_client.py       # Jasmine world models (future)
│   ├── eil/                        # EIL core
│   │   └── market_engine.py        # ProofEconomy market logic
│   ├── economy/                    # Token economics
│   │   └── sim.py                  # Economic simulation sandbox
│   └── tests/                      # Phase 5 unit tests
│       └── test_consensus.py
│
├── data/                           # Shared data storage
│   ├── energy_maps/                # Energy map storage
│   │   └── pyramids/               # Multi-scale pyramid cache
│   ├── telemetry/                  # Real-time telemetry data
│   └── catalogs/                   # Data catalogs and metadata
│
└── deploy/                         # Deployment artifacts
    ├── bootstrap.sh                # Environment setup script
    ├── requirements_phase4.txt     # Phase 4 dependencies
    ├── requirements_phase5.txt     # Phase 5 dependencies
    └── neo4j_schema.cypher         # Neo4j database schema
```

---

## 🔗 Import Dependency Graph

### Phase 4 Dependencies

```
phase4/core/atlas_loader.py
├── numpy
├── h5py
├── scipy.ndimage (zoom, gaussian_filter)
└── py2neo (Neo4j client)

phase4/data/synthetic_generator.py
├── numpy
├── scipy.ndimage (rotate, gaussian_filter)
└── phase4.core.atlas_loader

phase4/nvp/nvp_model.py
├── jax
├── jax.numpy
├── flax.linen
└── optax

phase4/nvp/trainer.py
├── jax
├── optax
├── wandb (optional, for logging)
├── phase4.nvp.nvp_model
└── phase4.core.atlas_loader

phase4/agents/ace_base.py
├── typing
├── dataclasses
├── py2neo
├── phase4.core.atlas_loader
└── phase4.nvp.nvp_model (interface only)
```

### Phase 5 Dependencies

```
phase5/consensus/shadow_bft.py
├── typing
├── dataclasses
├── datetime
├── py2neo
└── phase4.nvp.nvp_model (interface only - NVPModel class)

phase5/dgm/evolver.py
├── numpy
├── jax
├── optax
├── py2neo
├── phase4.nvp.nvp_model (interface only)
└── phase5.consensus.shadow_bft

phase5/integrations/thermal_tap.py
├── numpy
├── scipy.ndimage (gaussian_filter)
├── datetime
└── phase4.core.atlas_loader (interface only - EnergyAtlasLoader)

phase5/eil/market_engine.py
├── typing
├── dataclasses
├── hashlib
├── py2neo
└── phase5.consensus.shadow_bft

phase5/economy/sim.py
├── numpy
├── matplotlib.pyplot
├── pandas
└── phase5.eil.market_engine
```

---

## 🧩 Module Responsibilities

### Phase 4 Modules

| Module | Primary Responsibility | Key Exports | Dependencies |
|--------|------------------------|-------------|--------------|
| `atlas_loader.py` | Load and vectorize energy maps | `EnergyAtlasLoader`, `precompute_pyramids()` | NumPy, Neo4j |
| `synthetic_generator.py` | Generate synthetic training data | `generate_sequence()`, `apply_perturbations()` | NumPy, SciPy |
| `nvp_model.py` | NVP neural architecture | `NVPModel`, `Encoder`, `Decoder` | JAX, Flax |
| `trainer.py` | Training loop with thermo loss | `train_nvp()`, `compute_loss()` | JAX, Optax |
| `ace_base.py` | ACE agent lifecycle | `ACEAgent`, `SocratesAgent`, `AtlasIndexer` | Py2neo |

### Phase 5 Modules

| Module | Primary Responsibility | Key Exports | Dependencies |
|--------|------------------------|-------------|--------------|
| `shadow_bft.py` | Byzantine consensus | `ShadowTwinConsensus`, `propose()`, `vote()` | Py2neo |
| `evolver.py` | Architecture evolution | `DGMEvolver`, `compute_thermodynamic_fitness()` | JAX, Py2neo |
| `thermal_tap.py` | Incremental map updates | `ThermalTap`, `apply_thrml_sample()` | NumPy, SciPy |
| `market_engine.py` | Token minting logic | `ProofEconomyEngine`, `should_mint_PoE()` | Py2neo |
| `sim.py` | Economic simulation | `simulate_economy()`, `plot_token_distribution()` | NumPy, Pandas |

---

## 🚫 Phase Isolation Rules

### Allowed Cross-Phase Imports

**Phase 5 → Phase 4 (Interface Only):**
```python
# ✅ ALLOWED: Import public interfaces
from phase4.nvp.nvp_model import NVPModel
from phase4.core.atlas_loader import EnergyAtlasLoader

# ❌ FORBIDDEN: Import implementation details
from phase4.nvp.trainer import _compute_loss  # NEVER DO THIS
from phase4.core.atlas_loader import _validate_shape  # NEVER DO THIS
```

**Phase 4 → Phase 5:**
```python
# ❌ FORBIDDEN: Phase 4 should NOT import Phase 5
# Phase 4 is lower in the stack
```

### API Contract (Phase 4 Public Interface)

**Guaranteed Stable Interfaces for Phase 5:**

```python
# phase4/nvp/nvp_model.py
class NVPModel(nn.Module):
    def predict(self, E_t: jnp.ndarray, context: dict) -> tuple[jnp.ndarray, jnp.ndarray]:
        """
        Predict next energy vector.

        Args:
            E_t: Current energy map (H, W)
            context: Dict with metadata

        Returns:
            E_t1_mean: Predicted energy map (H, W)
            E_t1_var: Prediction variance (H, W)
        """
        pass

# phase4/core/atlas_loader.py
class EnergyAtlasLoader:
    def get_map(self, domain: str, scale: int) -> np.ndarray:
        """Get energy map for domain at scale."""
        pass

    def update_map(self, domain: str, updated_map: np.ndarray) -> None:
        """Update energy map (used by Thermal Tap)."""
        pass
```

---

## 🧪 Testing Strategy

### Unit Test Isolation

```python
# phase4/tests/test_nvp.py
def test_nvp_energy_conservation():
    """Test NVP respects energy conservation."""
    from phase4.nvp.nvp_model import NVPModel
    # Test only Phase 4 modules
    pass

# phase5/tests/test_consensus.py
def test_bft_consensus():
    """Test BFT consensus logic."""
    from phase5.consensus.shadow_bft import ShadowTwinConsensus
    from unittest.mock import Mock
    # Mock Phase 4 dependencies
    mock_nvp = Mock(spec=NVPModel)
    pass
```

### Integration Test Cross-Phase

```python
# tests/integration/test_end_to_end.py
def test_nvp_to_consensus_to_poe():
    """
    Full pipeline: NVP → Consensus → PoE mint
    """
    from phase4.nvp.nvp_model import NVPModel
    from phase5.consensus.shadow_bft import ShadowTwinConsensus
    from phase5.eil.market_engine import ProofEconomyEngine
    # Test integrated flow
    pass
```

---

## 📦 Dependency Installation Order

```bash
# 1. System dependencies
apt-get update && apt-get install -y python3.11 python3-pip

# 2. Phase 4 dependencies
pip install -r deploy/requirements_phase4.txt
# Contents: jax[cuda], flax, optax, numpy, scipy, h5py, py2neo, pytest

# 3. Phase 5 dependencies
pip install -r deploy/requirements_phase5.txt
# Contents: pandas, matplotlib, networkx, torch-geometric (for GNN)

# 4. Neo4j database
# Start via Docker or native installation
```

---

## 🔧 Code Owner Responsibilities

| Module Area | Owner Role | Key Responsibilities |
|-------------|-----------|----------------------|
| **Phase 4 Core** | ML Engineer Lead | NVP architecture, training stability |
| **Phase 4 Data** | Data Engineer | Data pipeline, synthetic generation |
| **Phase 5 Consensus** | Systems Engineer | BFT correctness, Neo4j integration |
| **Phase 5 DGM** | Research Scientist | Evolutionary algorithms, fitness functions |
| **Phase 5 Economy** | Product/BD Lead | Token economics, market simulation |

---

## 🚀 Quick Start Commands

```bash
# Navigate to workspace
cd /home/user/industriverse_phase4_5

# Set up environment
bash deploy/bootstrap.sh

# Run Phase 4 tests
pytest phase4/tests/ -v

# Run Phase 5 tests
pytest phase5/tests/ -v

# Train NVP model
python phase4/nvp/trainer.py --config configs/nvp_default.yaml

# Run economic simulation
python phase5/economy/sim.py --agents 100 --epochs 1000
```

---

## 📝 Import Convention Rules

1. **Absolute imports only** (never relative beyond package)
   ```python
   # ✅ GOOD
   from phase4.nvp.nvp_model import NVPModel

   # ❌ BAD
   from ..nvp.nvp_model import NVPModel
   ```

2. **Group imports by source**
   ```python
   # Standard library
   import os
   from typing import List, Dict

   # Third-party
   import numpy as np
   import jax.numpy as jnp

   # Phase 4
   from phase4.core.atlas_loader import EnergyAtlasLoader

   # Phase 5
   from phase5.consensus.shadow_bft import ShadowTwinConsensus
   ```

3. **Type hints mandatory for public APIs**
   ```python
   def predict(self, E_t: jnp.ndarray, context: dict) -> tuple[jnp.ndarray, jnp.ndarray]:
       pass
   ```

---

## 🧠 Claude Code Usage Notes

When generating code, Claude Code should:

1. **Load context first:**
   ```
   Read PROJECT_OVERVIEW.md + phase4.md OR phase5.md
   ```

2. **Check REPOSITORY_MAP.md for:**
   - Correct import paths
   - Dependency availability
   - Phase isolation rules

3. **Generate imports following conventions:**
   - Absolute paths
   - Grouped by source
   - Type hints included

4. **Test phase isolation:**
   - Run `pytest --collect-only` to verify no forbidden imports
   - Use mock objects for cross-phase dependencies in unit tests

---

<<< REPOSITORY_MAP_END >>>
