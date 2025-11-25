# DOE Genesis Alignment Deliverables (Phase 6)

## Target Capsules/Adapters
- **Fusion Control Capsule v1**: MHD priors, plasma instability prediction, coil optimizer, UTID/PRIN, safety budgets; capsule://fusion/* namespace.
- **Grid Immunity Capsule v1**: grid topology + thermodynamic anomaly detection, microgrid simulation, AI Shield hooks; capsule://grid/*.
- **DOE HPC Adapter**: ties Trifecta/Discovery Loop to DOE exascale schedulers; capsule://hpc/adapter/v1 (routes jobs to HPC backends).
- **Defense Materials Capsule v1**: shock/supernova priors, radiation hardening models; capsule://materials/defense/*.
- **Quantum State Capsule v1**: QPU telemetry modeling, noise prediction, decoherence mapping; capsule://quantum/state/*.

## Proof & Compliance
- Proof Economy whitepaper: UTID lineage, PRIN validation, ProofScore/ProofMesh policies for labs.
- Credit splits for partner nodes encoded in capsule manifests.
- Safety: entropic gating + runtime budgets per capsule; audit logs accessible via resolver telemetry and ledger replay.

## Integration Steps
1) Register namespaces with Root Authority; publish URI manifests.  
2) Package DACs with manifests and credit metadata; push to registry.  
3) Expose HPC adapter endpoints for DOE schedulers; map capsule:// URIs to job templates.  
4) Provide Genesis deck + whitepaper to partners; include Shadow Twin views for each capsule.  
5) Run acceptance tests: execute capsules via resolver, validate proofs/credits, render UI telemetry.  
