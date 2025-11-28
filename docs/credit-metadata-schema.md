# Credit Metadata Schema (Phase 2)

Embed this metadata in capsule manifests/DACs to align with Proof-of-Insight ledger and UI telemetry.

```json
{
  "credit": {
    "execution_cost": 10,
    "split": {
      "author": 0.7,
      "executor": 0.2,
      "mesh": 0.1
    },
    "proof_hash": "b4e2...9a",
    "credit_root": "sha3:...",
    "settlement_epoch": "2025-10-26T00:00:00Z"
  }
}
```

Fields:
- `execution_cost`: numeric PoI units per execution.
- `split`: royalty shares.
- `proof_hash`: proof-of-execution hash for this capsule.
- `credit_root`: ledger root at packaging time (for UTID derivation).
- `settlement_epoch`: reconciliation window.

Consumption:
- Resolver/sandbox emits `execution_cost` and splits in telemetry (`capsule.credit_flow`).
- Ledger uses `credit_root` for UTID verification and reconciliation.
```
