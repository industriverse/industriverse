# Shadow Twin Telemetry Contract

Purpose: align resolver, twin_sync, and UI/HUD (ReactorGauge, TruthSigil, Constellation, EnergyField) for Phase 4.

## Event Topics
- `capsule.status`  
  - Fields: `uri`, `utid`, `status` (enum: resolving|executing|executed|error), `latency_ms`, `resolution_source` (local|mesh).
- `capsule.proof`  
  - Fields: `uri`, `utid`, `proof_hash`, `entropy_delta`, `timestamp`.
- `capsule.credit_flow`  
  - Fields: `uri`, `utid`, `execution_cost`, `author_split`, `executor_split`, `mesh_split`, `balance_after`.
- `capsule.entropy`  
  - Fields: `uri`, `utid`, `entropy`, `stability`, `safety_budget_used`.
- `rdr.node`  
  - Fields: `id`, `label`, `uri?`, `embedding_id`, `cluster_id`, `novelty_score`.
- `rdr.edge`  
  - Fields: `source`, `target`, `type` (invokes|validates|depends|similar), `weight`.
- `rdr.trend`  
  - Fields: `window_start`, `window_end`, `cluster_id`, `delta`, `summary`.

## Transport
- WebSocket (twin_sync) for UI; protobuf/JSON payloads.
- Message bus topics mirrored for backend consumers.

## UI Mappings
- ReactorGauge: `capsule.entropy` (entropy/stability).  
- TruthSigil: `capsule.proof` (proof_hash, entropy_delta).  
- Constellation DAG: `capsule.status` + edges from `rdr.edge` and execution dependencies.  
- EnergyField: pulse intensity from `capsule.status.latency_ms` and `capsule.entropy.entropy`.

## Reliability
- At-least-once delivery with event ids for de-duplication.  
- Heartbeat topic `twin.heartbeat` every 5s from twin_sync.  
- Backfill: UI can request recent window via `/twin/replay?since=<ts>`.
