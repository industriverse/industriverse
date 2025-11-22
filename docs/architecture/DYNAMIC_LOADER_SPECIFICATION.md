# Dynamic Loader Specification: The Runtime Nervous System

**Status:** Draft
**Version:** 1.0
**Objective:** Enable seamless, atomic hot-swapping of massive AI models, LoRAs, and capsules without downtime, ensuring sovereign and adaptive industrial intelligence.

## 1. Core Concept
The Dynamic Loader is not just a model loader; it is an **adaptive runtime conductor**. It manages the lifecycle of AI models as "living" entities that can be streamed, swapped, and suspended without interrupting operations.

### Key Capabilities
*   **Hot-Swap:** Atomic swap of 30-70B parameter models or LoRA stacks in <45s.
*   **Elasticity:** Auto-negotiate resources (CPU/GPU/TPU/FPGA).
*   **Context-Awareness:** Load specific weights based on ACE/UserLM context.
*   **Proof-Attached Runtime:** Emit micro-proofs (UTID + hash) for every load event.
*   **Self-Healing:** Auto-rollback on validation failure.

## 2. Architecture

### 2.1. Components
1.  **Loader Core (The Conductor):**
    *   Manages memory pools and device allocation.
    *   Handles `mmap` streaming of SafeTensors shards.
    *   Orchestrates atomic symlink swaps for model artifacts.
2.  **Registry & Cache:**
    *   Local high-speed cache for frequently used LoRAs and base model shards.
    *   Connects to the global Capsule Registry for updates.
3.  **Proof Emitter:**
    *   Generates a signed event (UTID, Timestamp, ModelHash, Context) for every lifecycle event.
    *   Publishes to NATS and logs to ACE.
4.  **Scheduler (Token-Level):**
    *   (Future) Slices generation into micro-batches to allow preemption and multi-model hosting.

### 2.2. Integration Points
*   **UserLM:** Requests specific personas/skills -> Loader swaps in relevant LoRA.
*   **RND1:** Submits new hypotheses (models) -> Loader deploys to sandbox/canary.
*   **ACE:** Provides context headers -> Loader optimizes weight selection.
*   **AI Shield:** Validates model integrity before traffic shifting.

## 3. Implementation Strategy

### Phase 1: Foundation (Sprint 1)
*   **Event Telemetry:** Emit signed NATS events for every load/unload.
*   **Basic Hot-Swap:** Implement atomic model reloading using `safeTensors` and Python memory management.
*   **Dashboard:** Visualize currently loaded models and swap history.

### Phase 2: Optimization (Sprint 2)
*   **LoRA Adapters:** Implement "Base Model + Adapter" architecture to reduce swap size.
*   **Rollback:** Implement automatic revert on health check failure.
*   **Memory Mapping:** Use `mmap` for instant model presence.

### Phase 3: Scale (Sprint 3+)
*   **Kubernetes Operator:** CRDs for `ModelDeployment` and `Capsule`.
*   **Token Scheduling:** Implement time-sliced inference for high concurrency.
*   **Edge Proxy:** Lightweight loader for EDCoC devices.

## 4. Frontend Vision (Nanochat & Real3D)
*   **Streaming UX:** Frontend receives token streams via SSE/WebSockets.
*   **Progress Indicators:** "Loading Specialist Module..." displayed during hot-swaps.
*   **Shadow Twin:** Real-time 3D visualization of the model's focus (e.g., highlighting a turbine blade when the "Fatigue" LoRA is active).

## 5. Security & Governance
*   **Provenance:** No model runs without a valid UTID and signature.
*   **Audit Trail:** Full history of *what* model made *which* decision.
*   **Sovereignty:** All weights and logs remain local/on-prem unless explicitly federated.
