# Consensus and Merkle Root Signing Service (Blueprint)

Purpose: finalize ledger roots across validators with signatures and publish finalized proofs.

## Flow
1) Each validator computes Merkle root over local ledger entries.
2) Validator signs root (Ed25519/ECDSA or BLS for aggregation).
3) Signatures published to `ledger.reconciliations` topic (Kafka/JetStream).
4) Consensus worker collects signatures, verifies quorum, marks root finalized.
5) Finalization proof recorded in ProofRegistry and emitted to `proofs.finalized`.

## Payloads
- Reconciliation publish:
```json
{
  "node_id": "validator-1",
  "merkle_root": "hex",
  "signature": "hex",
  "public_key": "hex",
  "utid_count": 123,
  "ts": "2025-01-01T00:00:00Z"
}
```
- Finalization:
```json
{
  "merkle_root": "hex",
  "signatures": [{"node_id":"validator-1","signature":"hex"}],
  "finalized": true,
  "aggregated_signature": "hex"
}
```

## Implementation notes
- Use Ed25519 for simplicity or BLS for aggregated signatures.
- Store trusted validator pubkeys in config/secret.
- Quorum rule: N >= 3f+1; require f+1 signatures to finalize (tune for environment).
- Anchor finalized roots to blockchain (optional) and store anchor_tx in ProofRegistry.

## Tests
- Verify signature validation for good/bad signatures.
- Verify quorum logic and state transition to finalized.
- Verify proof event emitted on finalize.
