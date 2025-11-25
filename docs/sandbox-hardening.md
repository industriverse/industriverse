# Sandbox Hardening (Phase 1/2 security)

Goals:
- Deterministic execution
- Isolation from host network/filesystem
- Resource limits (CPU/memory/GPU/time)
- Reproducibility and auditability

Recommended approach:
- Use containerized sandbox (gVisor/Firecracker) with read-only root, whitelisted mounts for inputs/outputs.
- Disable outbound network; only allow resolver-controlled channels.
- Enforce cgroups for CPU/memory; set GPU quotas if applicable.
- Record hashes of inputs/outputs; include in telemetry.
- Run as non-root; drop capabilities.
- Provide attestation of sandbox image hash.

Implementation steps:
- Wrap `DeterministicSandbox.run` with container runner.
- Inject sandbox policy: allowed syscalls, env vars, resource ceilings.
- Add timeouts and kill on overrun.
- Emit telemetry fields: `sandbox_hash`, `cpu_ms`, `mem_bytes`, `network_bytes=0`.
