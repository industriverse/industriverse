# Proof-as-a-Service (PaaS) API Specification

## 1. Purpose
Unify mathematical proof generation/verifying, proof ledger, UTID anchoring and make proofs first-class objects used by KaaS, DACs, and clients.

## 2. Authentication & Common
*   **Auth**: JWT for services / mTLS for K8s controllers. HSM-backed signing for server tokens.
*   **Rate limits**: Tiered per-account (pilot: 1k proofs/day; standard: 1M/day).
*   **Content-Type**: `application/json` or `multipart/form-data`.

## 3. Endpoints
1.  `POST /v1/proofs/generate` — Request proof generation
2.  `GET /v1/proofs/{proof_id}` — Fetch proof bundle & metadata
3.  `POST /v1/proofs/verify` — Submit proof + artifacts for verification
4.  `GET /v1/ledger/{proof_id}` — View anchoring & blockchain txs
5.  `POST /v1/anchor` — Anchor proof hash to configured chains (L2 + archival)
6.  `POST /v1/utid/generate` — Produce hardware-bound UTID (service-only)
7.  `POST /v1/webhook/register` — Register a callback for proof state changes
8.  `GET /v1/proofs?filter=...` — Search by capsule, UTID, domain

## 4. Data Models

### ProofRequest
```json
{
  "title":"Consciousness proof - shear_flow run #42",
  "requester": {"org":"ACME","user":"ops@acme"},
  "artifacts": [ {"type":"simulation_output","uri":"s3://.../run42.tar.gz","hash":"sha256:..."} ],
  "proof_types":["statistical_rigor","mathematical_certainty"],
  "anchor": {"chains":["eth:goerli","arweave"], "batch":true},
  "metadata":{"dataset":"shear_flow","params":{"integration_window":15}}
}
```

### ProofResponse
```json
{
  "proof_id":"proof_6ecd434a",
  "status":"queued",
  "estimated_time_s": 12,
  "verify_endpoint":"/v1/proofs/proof_6ecd434a/verify"
}
```

### ProofBundle
```json
{
  "proof_id":"proof_6ecd434a",
  "status":"verified",
  "hash":"sha256:abcd...",
  "anchors":[ {"chain":"eth","tx":"0x33d0...","time":"..."} ],
  "evidence":[
    {"type":"latex","uri":"s3://.../paper.tex"},
    {"type":"proof-pickle","uri":"s3://.../proof.pk"},
    {"type":"stat-table","json":{"cohen_d":2.94}}
  ],
  "signed_by":"hsm-key-001",
  "signature":"ecdsa:...",
  "utid":"UTID:REAL:eb31f6..."
}
```

## 5. Proof Generation Flow
1.  Client `POST /v1/proofs/generate` with artifacts.
2.  Proof engine (ASAL + DGM) runs:
    *   Statistical tests, bootstrap, cross-validation
    *   Formal math proof generator if requested (DGM)
    *   Assemble PoE (proof of evidence) bundle
3.  Bundle hashed → `sha256:Z` stored in registry & DB.
4.  Anchoring job: batch anchor to chains specified → returns tx IDs.
5.  Verifier service runs independent checks and sets status `verified`.
6.  Notifier webhooks invoked for registered listeners.

## 6. Verification & Trust Model
*   **Signed bundles**: HSM signs bundle hash and metadata.
*   **Dual-anchor**: Cheap L2 (quick) + archival chain (permanent).
*   **Proof ledger**: Append-only DB + IPFS/Arweave URI for artifact storage.
*   **On-chain pointer**: tx → points to IPFS hash of proof bundle (not full data).
