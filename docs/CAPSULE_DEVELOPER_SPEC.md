# Sovereign Capsule Developer Specification

## Overview
This specification defines the standard for building, deploying, and extending **Sovereign Capsules** within the Industriverse Thermodynamic Discovery Loop V16.

## 1. Capsule Anatomy
Each capsule MUST adhere to the `CapsuleBlueprint` schema defined in `src/capsule_layer/capsule_blueprint.py`.

### Core Components
| Component | Description | Requirement |
|-----------|-------------|-------------|
| **Physics Topology** | Defines the thermodynamic domain (e.g., MHD, Fluid Dynamics). | MUST map to a valid `EnergyAtlas` prior. |
| **Domain Equations** | List of governing physical laws (e.g., Navier-Stokes). | MUST be registered in `DomainEquationPack`. |
| **PRIN Config** | Weights for Physics, Coherence, and Novelty. | MUST satisfy `PRIN > 0.75` for approval. |
| **Safety Budget** | Energy (Joules) and Entropy limits. | MUST be enforced by `ThermodynamicRuntimeMonitor`. |
| **UTID Pattern** | Unique Traceable ID format. | MUST follow `UTID:REAL:<host>:<capsule>:<ts>:<nonce>`. |

## 2. Development Workflow

### Step 1: Define Blueprint
Create a new entry in `src/capsule_layer/capsule_definitions.py`:
```python
CapsuleBlueprint(
    capsule_id="capsule:new_domain:v1",
    name="New Domain Capsule",
    category=CapsuleCategory.CATEGORY_A,
    physics_topology="...",
    ...
)
```

### Step 2: Implement Logic
Extend `ACEReasoningTemplate` if custom reasoning is needed.
Ensure `DomainEquationPack` contains necessary formulas.

### Step 3: Verify
Run `tests/verify_capsule_logic.py` to validate:
- Safety Budget enforcement
- PRIN validation
- UTID generation

## 3. Deployment (Phase 4)
Capsules are deployed as Kubernetes `Deployment` resources managed by the `SovereignCapsule` CRD.

### CRD Spec
```yaml
apiVersion: industriverse.ai/v1
kind: SovereignCapsule
metadata:
  name: capsule-name
spec:
  capsule_id: "capsule:id:v1"
  image: "industriverse/capsule-image:latest"
  replicas: 3
  energy_budget: "1000J"
```

## 4. Integration
- **BridgeAPI**: Exposed via `/v1/capsules/{id}`.
- **Mesh**: Connects via NATS for inter-capsule communication.
- **Proofs**: All outputs MUST be signed and registered in the `ProofRegistry`.
