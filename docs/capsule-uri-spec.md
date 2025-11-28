# Capsule Internet RFC v0.1
*Industriverse Specification Series — Draft v0.1 — October 2025*

## 1. Abstract
The Capsule Internet defines the capsule:// protocol for executing self-contained intelligence units (Capsules) across the Industriverse Mesh. Unlike HTTP, which fetches documents, capsule:// resolves, verifies, and executes Capsules with cryptographic provenance (UTID), deterministic sandboxing, and Proof-of-Insight credit accounting.

## 2. Motivation and Scope
- Own the substrate beneath the document web: operation-centric, proof-first execution.
- Enable sovereign edge execution with federated trust (hash-chain UTID + Merkle credit ledger).
- Scope: URI grammar, resolution architecture, execution semantics, namespace governance, credit integration, error codes. Model architectures and UI behaviors are out of scope.

## 3. Terminology
- **Capsule**: Executable unit (hypothesis, code, LoRA, proofs, metadata).
- **UTID**: Universal Trust ID; hash-chain identifier anchored to credit ledger roots.
- **Mesh Node**: Registered participant capable of resolving/executing Capsules.
- **Shadow Twin**: Dynamic visualization of capsule graph and credit flows.
- **Credit Protocol**: Off-chain Proof-of-Insight ledger with periodic Merkle reconciliation.
- **Dynamic Island**: Ambient UI element streaming capsule state.

## 4. Capsule URI Syntax (ABNF)
```
capsule-URI = "capsule://" authority "/" domain *( "/" subdomain ) "/" operation [ "/" version ] [ "?" param-list ]
param-list  = param *( "&" param )
param       = key "=" value
```
Examples:
- `capsule://fusion/mhd64/v4.1`
- `capsule://materials/stress-analysis/v2?material=titanium&temp=1500K`
- `capsule://org-x/plasma-control/internal-v5`

Segments:
- **authority**: Mesh namespace owner/org.
- **domain/subdomain**: Knowledge hierarchy.
- **operation**: Executable function/hypothesis.
- **version**: Semantic snapshot.
- **params**: Runtime args.

## 5. Resolution Architecture
1) Parse/validate URI (capsule_uri library).  
2) Local Registry lookup; if miss, broadcast via Mesh DNS (IM-DNS).  
3) UTID verification via Merkle proof against local credit root.  
4) Fetch payload from authoritative node; check signature/integrity.  
5) Sandbox execution (deterministic, sealed I/O).  
6) Emit results + telemetry (proof hash, entropy, credits).  
7) Append Proof-of-Execution and credit events to local ledger; schedule reconciliation.

## 6. Execution Semantics
- Stages: Fetch → Verify → Sandbox → Run → Emit → Reconcile.
- Deterministic runtimes (Python/WASM/CUDA containers) with no ambient network.
- Target: <300 ms resolution; <1 s execution for ≤50 MB Capsules at edge.

## 7. Namespace Governance
- Public namespaces (e.g., `capsule://fusion/*`) governed by Industriverse Root Authority.
- Private/org namespaces require key ownership and UTID prefix registration.
- Versioning: minor (v4.1→v4.2) backward-compatible; major (v4→v5) new UTID lineage. Deprecated versions remain addressable.

## 8. Scaling and Federation
- DHT index by UTID hash across nodes; adaptive replication near demand.
- Local caches store recent Capsules and embeddings with integrity hashes.
- Federated accounting: Merkle root exchanges every N minutes to root mesh; quorum accepts consistent roots.
- Mesh optimizer routes by latency/compute/credit balance.

## 9. Credit Protocol Integration
Metadata (embedded in Capsule manifest):
```json
{
  "credit": {
    "execution_cost": 10,
    "split": { "author": 0.7, "executor": 0.2, "mesh": 0.1 },
    "proof_hash": "b4e2...9a",
    "settlement_epoch": "2025-10-26T00:00Z"
  }
}
```
- Credits denominated in Proof-of-Insight units.  
- Local ledger records spend/earn; Merkle reconciliation enforces global consistency.  
- UTID lineage ties execution to credit events.

## 10. Security and Provenance
- UTID = `SHA3-512(capsule_hash || parent_UTID || credit_root)`.  
- Execution envelope: deterministic sandbox, sealed inputs/outputs, signature checks.  
- Merkle ledger per node; roots shared with root mesh; nodes failing validation are quarantined.

## 11. Error Handling / Status Codes
- 200 EXECUTED
- 201 FORKED
- 400 BAD_URI
- 401 UNAUTHORIZED
- 402 INSUFFICIENT_CREDITS
- 404 NOT_FOUND
- 409 SIGNATURE_MISMATCH
- 500 EXECUTION_ERROR

## 12. HTTP Interoperability
- Standard web content may link to capsules: `<a href="capsule://fusion/mhd64/v4.1">Run</a>`.
- Industriverse SDK intercepts capsule:// and routes to local resolver/runtime.

## 13. Developer Implementation Notes
- Registry schema: per-namespace JSON index of Capsule versions and hashes.
- Local Execution API: `POST /execute` with `{uri, params}`; streams telemetry via WebSocket `capsule/stream/<UTID>`.
- Sandbox targets: Python 3.11, WASM, CUDA containers; no outbound network during execution.
- Observability: OpenTelemetry spans from resolve → execute → reconcile.

## 14. Future Work (Road to v1.0)
- v0.2: Capsule chaining syntax (`|`) and parameter templates.  
- v0.3: Streaming subscriptions (`stream=true`) and persistent channels.  
- v0.4: Cross-protocol bridge (capsule:// → http://) and signing proxy.  
- v1.0: Mesh governance DAO, credit mainnet launch, 10⁶-node mesh support.

## 15. Security Considerations
- Post-quantum secure channels for mesh sync (e.g., Kyber512 + Dilithium2).  
- Reproducibility checks before trust propagation.  
- Quarantine protocol for nodes failing UTID or Merkle validation.

## 16. Appendices
### A. Example Capsule Manifest
```json
{
  "name": "fusion-mhd64-v4.1",
  "author": "industriverse-core",
  "version": "4.1",
  "description": "Magnetohydrodynamic plasma simulation",
  "runtime": "python3.11",
  "entrypoint": "main.py",
  "dependencies": ["numpy", "torch"],
  "inputs": ["density_field.npy", "magnetic_field.npy"],
  "outputs": ["stability_plot.png", "summary.json"],
  "utid": "sha3:b31ef9...",
  "credit": { "execution_cost": 10, "split": { "author": 0.7, "executor": 0.2, "mesh": 0.1 } }
}
```
### B. Example Resolution Log
```
[12:03:11] Parsed URI capsule://fusion/mhd64/v4.1
[12:03:12] Local registry miss, broadcasting IM-DNS
[12:03:12] Found replica @Node-Helion-23
[12:03:12] Verified UTID sha3:b31ef9... OK
[12:03:13] Executing sandbox...
[12:03:13] Status 200 EXECUTED, 3.1s total latency
```
