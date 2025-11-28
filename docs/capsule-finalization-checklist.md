# 27 Capsule Finalization Checklist (Phase 5)

For each capsule, ensure the following artifacts and tests are present.

- Topology spec: `/topology/<capsule_id>.yaml` (state vars, boundary conditions, coupling, energy constraints).
- Domain equations: `/capsule/<id>/models/equations.py` (PDE/ODE + constraints; differentiable where possible).
- Energy priors: `/capsule/<id>/priors/energy_prior.json` (potential wells, thresholds, stability basins).
- PRIN profile: `/capsule/<id>/prin.yaml` (Physics, Regularity, Intelligence, Narrative).
- Agent behavior: `/capsule/<id>/agent/behavior.py` (observation, policy, thermodynamic mode hooks).
- Safety budgets: `/capsule/<id>/runtime/safety.json` (entropy/stability/thermal/compute budgets, horizon limits).
- Proof schema: `/capsule/<id>/proof/schema.json` (constraint checks, work definition, hash rules).
- UTID patterns: `/capsule/<id>/identity/utid_patterns.yaml` (credentials, lineage signatures, permissions).
- Mesh routing: `/capsule/<id>/mesh/routing.json` (upstream/downstream, triggers, coupling factors).
- DAC affordances: `/capsule/<id>/dac/` (schema, gesture mappings, visualization hints, operator affordances).
- Tests: `tests/verify_capsule_<id>.py` + inclusion in `tests/verify_all_capsules.py` (UTID check, entropy stability, proof hash returned).
- UI wiring: ensure reactor/truth/constellation signals emitted via telemetry contract.

Done criteria for Phase 5:
- All 27 capsules have the above files committed.
- Grand harness passes across capsules (proof hash present, entropy within budgets, UTID lineage valid).
- DAC Factory packages per-capsule assets with credit metadata and manifests.
