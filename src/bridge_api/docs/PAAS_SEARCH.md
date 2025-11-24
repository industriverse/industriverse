# Proof/UTID Search API (PAAS Spec Alignment)

Supported filters on `/v1/proofs`:
- `utid`: exact UTID match
- `domain`: domain string
- `status`: proof status (queued, verified, validated, etc.)
- `proof_hash`: hash string
- `anchor_chain`: anchor chain id
- `anchor_tx`: anchor transaction id
- `min_energy`, `max_energy`: numeric range
- `evidence_contains`: substring search over evidence JSON
- `limit`, `offset`: pagination

Status lifecycle (suggested):
- `queued` -> `processing` -> `verified` -> `validated`

UTID listing (`/v1/utid/list`):
- `context_digest`: exact digest match
- `context_contains`: substring search over context JSON
- `limit`, `offset`: pagination

Notes:
- For Postgres backend set `PROOF_BACKEND=postgres` and `PROOF_DB_DSN`.
- Anchors should be stored as a list of `{chain, tx, time}` objects in metadata.
