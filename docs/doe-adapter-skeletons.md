# DOE Adapter Skeletons (Phase 6)

## Fusion Control Capsule v1
- Namespace: `capsule://fusion/control/v1`
- Components: MHD priors, coil optimizer, instability predictor, safety budgets, proof schema, UTID patterns.
- Adapter: exposes control loop endpoints for reactor simulators/HPC jobs.

## Grid Immunity Capsule v1
- Namespace: `capsule://grid/immunity/v1`
- Components: grid topology models, thermodynamic anomaly detection, microgrid simulation, AI Shield hooks.
- Adapter: listens for grid telemetry; outputs mitigation actions; emits proofs.

## DOE HPC Adapter
- Namespace: `capsule://hpc/adapter/v1`
- Function: routes discovery jobs to DOE schedulers; maps capsule URIs to job templates; returns proof hashes.

## Defense Materials Capsule v1
- Namespace: `capsule://materials/defense/v1`
- Components: shock/supernova priors, radiation hardening models, safety budgets.

## Quantum State Capsule v1
- Namespace: `capsule://quantum/state/v1`
- Components: QPU telemetry modeling, noise prediction, decoherence mapping, safety budgets.

Implementation notes:
- Each adapter should publish manifests with credit metadata, UTID lineage, and registry entries for resolver/mesh.
- Provide sample payloads and job specs for HPC adapter integration.
