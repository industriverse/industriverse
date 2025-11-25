# Industriverse Integrated Execution Plan

Purpose: unify the 27 Capsules final-form directives, Capsule Internet substrate (capsule://), Shadow Twin, Real Deep Research (RDR) ingestion, Credit/UTID mesh, and DOE-aligned deliverables into one phased roadmap with clear interconnections.

## System Chain (end-to-end)
- Ingest (RDR + client uploads) → Perspective extraction → Embeddings/graph → Trend deltas → Hypotheses.
- Discovery Loop → T2L/LoRA forge → Guardrails (PRIN/OBMI) → Validation → DAC packaging.
- Capsule Internet (capsule://) → Resolver (parse → verify UTID/Merkle → sandbox execute) → Credit log → Proof Mesh.
- Shadow Twin (3D/AR) + Dynamic Islands → live state from resolver telemetry, proofs, credits, and RDR graph.
- 27 Capsules → topology/priors/agents/safety/proofs/UTID patterns → DACs → Mesh routing → UI/Constellation.
- Credit Protocol (Proof-of-Insight) → off-chain ledger + periodic Merkle reconciliation → fuels execution and royalties.

## Phase Plan (with dependencies)

### Phase 0 — Baseline & Repos
- Confirm submodule `industriverse` is on `feature/final-form-integration`; keep gitlink aligned when committing.
- Catalog current WIP deltas (frontend, bridge_api, tests) and avoid overwriting during doc/spec work.

### Phase 1 — Capsule Internet Substrate
- Deliverables: `docs/capsule-uri-spec.md`, `capsule_uri` parser/validator lib, `capsule_resolver` service stub.
- Flow: `capsule://` URI → Local Registry → Mesh DNS → UTID/Merkle verify → sandbox execute → credit log.
- Error/status codes: 200 EXECUTED, 201 FORKED, 400 BAD_URI, 401 UNAUTHORIZED, 402 INSUFFICIENT_CREDITS, 404 NOT_FOUND, 409 SIGNATURE_MISMATCH, 500 EXECUTION_ERROR.
- Interfaces: mesh router accepts URI jobs; SDK/CLI (`iv exec`, `iv pipe`) wraps resolver.

### Phase 2 — Credit + UTID Mesh
- Deliverables: hash-chain UTID format, local credit ledger + Merkle reconciliation daemon, credit metadata schema per capsule.
- Flow: execution emits Proof-of-Insight credits; local ledger updates → periodic reconciliation to root mesh; UTID lineage anchors provenance.
- Interfaces: resolver writes credit events; UI surfaces credit spend/royalties; mesh consensus verifies Merkle roots.

### Phase 3 — RDR Ingestion & Discovery Loop
- Deliverables: ingestion workers (arXiv/APIs/uploads), perspective extractor, embedding + clustering service, trend reports.
- Flow: raw papers/data → perspective JSON → embeddings/vector DB + graph → trend deltas → hypothesis queue → T2L/LoRA → validation → DAC packaging.
- Interfaces: hypotheses sent to forge; outputs registered as capsules with UTID/credits; feeds Shadow Twin graph.

### Phase 4 — Shadow Twin & Dynamic Islands
- Deliverables: live 3D/AR visualization (three.js/Babylon/WebGPU), websocket twin_sync service, client-private twin views.
- Flow: consume RDR graph + resolver telemetry (entropy, proofs, credits) → render Constellation/energy fields → drive ReactorGauge, TruthSigil, Dyson HUD.
- Interfaces: UI contract for telemetry topics (capsule status, proof hash, credit flow, entropy/stability).

### Phase 5 — 27 Capsules Finalization & Tests
- Deliverables: per-capsule specs (topology, equations, priors, PRIN, agent behavior, safety budgets, proof schema, UTID patterns, mesh routing), DAC affordances, verify scripts (`tests/verify_capsule_<id>.py`, grand harness).
- Flow: capsules act as thermodynamic solvers + mesh nodes → emitted proofs feed Proof Mesh → UI updates via resolver streams.
- Interfaces: DAC Factory consumes capsule manifests; mesh routing tables use declared dependencies; Shadow Twin graph uses capsule URIs.

### Phase 6 — DOE Genesis Alignment Packages
- Deliverables: Fusion Control Capsule v1, Grid Immunity Capsule v1, DOE HPC adapter, Defense Materials Capsule v1, Quantum State Capsule v1; “Proof Economy for Scientific Integrity” whitepaper; Genesis-aligned deck.
- Flow: each capsule exposes capsule:// URIs, UTID lineage, safety budgets, and DACs; HPC adapter routes to DOE compute; credit splits align with partner nodes.

## Cross-Cutting Concerns
- Security: deterministic sandbox, post-quantum channels for mesh sync, UTID/Merkle validation before execution.
- Observability: OpenTelemetry traces on resolver/RDR/forge; execution logs feed Shadow Twin and audit.
- Performance targets: <300 ms URI resolution avg; <1 s edge execution for ≤50 MB capsules; ingestion cadence 12h.
- Governance: namespace ownership per keypair; deprecation policy via versioned URIs; quarantine nodes failing UTID checks.

## Immediate Next Actions
1) Add `docs/capsule-uri-spec.md` (Phase 1 spec) and `capsule_uri` parser stub.
2) Define telemetry contract for UI (entropy/proof/credit topics) to wire resolver → HUD.
3) Stand up RDR ingestion skeleton (ingest → perspective JSON → embeddings store) feeding Shadow Twin.
