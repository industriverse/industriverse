# Capsule Population Plan (Phase 5)

Steps to move from checklist to populated capsules:
1. Assign owners per capsule; create PR templates enforcing topology/priors/PRIN/agent/safety/proof/UTID/routing/DAC files.
2. Define canonical directories (`capsules/<id>/...`) and manifests linking to capsule:// URIs and credit metadata.
3. Add lint/check script to verify presence of required files and JSON/YAML validity.
4. Implement grand harness `tests/verify_all_capsules.py` to iterate capsules and run schema/entropy/proof checks.
5. Publish capsule registry index consumed by resolver/mesh to keep URIs discoverable.
6. Incrementally fill DOE-priority capsules first (Fusion, Grid, HPC adapter, Defense Materials, Quantum State).
