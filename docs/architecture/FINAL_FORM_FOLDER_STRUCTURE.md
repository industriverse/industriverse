# Final Form Folder Structure & Trifecta Integration Map

## 1. Overview
This document defines the canonical folder structure for the Industriverse "Final Form" architecture and maps each component to the Trifecta (UserLM, RND1, ACE) agents.

## 2. Canonical Directory Structure

```
src/
├── diffusion_framework/        # Physics substrate (energy diffusion, kernels)
│   ├── core/
│   │   └── energy_diffusion.py
│   ├── operators/              # Quantum/attosecond operators, proofs hooks
│   └── kernels/                # Domain-specific physics kernels
│
├── bridge_api/                 # External API surface (server.py, auth, proof endpoints)
│   ├── server.py
│   ├── middlewares/
│   ├── controllers/
│   └── api_specs/
│
├── expansion_packs/            # 20 Pillars — modular DAC capsules
│   ├── tsc/
│   │   ├── ingestion/
│   │   ├── annotation/
│   │   └── filter/
│   ├── upv/
│   ├── use_cases/
│   └── ...                     # Each pack contains: ingest, model, policy, proof hooks
│
├── core_ai_layer/
│   ├── obmi/                   # Planning / operator generation
│   ├── m2n2/                   # Material evolution engines
│   ├── dgm/                    # Darwin Gödel Machine (formal proof helpers)
│   └── asal/                   # ASAL statistical / proof engine
│
├── overseer/                   # Orchestrator agents, agent factories
│   ├── userlm_adapters/        # Adapters for UserLM-style sim fleet
│   ├── rnd1_adapters/          # RND1 control & meta-optimization
│   ├── ace/                    # Agentic Context Engineering modules & playbooks
│   └── task_router/            # NATS / JetStream connectors
│
├── proof_registry/             # Proof mesh + ledger writers + verifier
│   ├── ledger/
│   ├── anchoring/
│   └── verifier/
│
├── utid/                       # UTID generation, hardware-bind hooks
│   └── attestation/
│
├── edcoc/                      # Edge Data Center on a Chip runtime bindings
│
└── infra/                      # K8s manifests, operators, argo workflows, scripts
```

## 3. Trifecta Integration Map

### UserLM (The Human Interface)
*   **Role**: Human-behavior simulations, outreach, persona generation.
*   **Integration**:
    *   Calls `bridge_api` endpoints.
    *   Uses `expansion_packs/use_cases/` to frame domain constraints.
    *   Consults `diffusion_framework` for physics-grounded narratives when required.

### RND1 (The Optimizer)
*   **Role**: Scheduler + optimizer.
*   **Integration**:
    *   Calls `core_ai_layer/m2n2` for evolution.
    *   Calls `diffusion_framework/kernels` for physics-cost models.
    *   Calls `infra/operator` for KaaS decisions.

### ACE (The Context Engineer)
*   **Role**: Online playbook updater.
*   **Integration**:
    *   Maintains append-only playbooks inside `overseer/ace/`.
    *   Uses `proof_registry` to store unit tests & execution signals.
