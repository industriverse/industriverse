# Implementation Threads and Codebase Touchpoints

Purpose: map the execution plan into concrete code areas, data contracts, and immediate tasks so teams can move in parallel while keeping chains connected.

## Services and Modules
- **capsule_uri library** (`src/protocol/capsule_uri.py` or similar): parse/validate capsule://; shared by resolver, SDK, mesh router.
- **capsule_resolver service** (`services/capsule_resolver/`): resolve → verify UTID/Merkle → sandbox execute → credit log; exposes `/resolve` and `/execute`. (Scaffold in `src/protocol_layer/protocols/capsule_resolver.py` with in-memory registry/mesh/sandbox.)
- **mesh router extension** (`services/mesh_router/`): accept URI jobs, route by latency/compute/credit balance; integrates IM-DNS. (Mock in `src/protocol_layer/protocols/mesh_client.py`.)
- **credit ledger daemon** (`services/credit_ledger/`): local Proof-of-Insight ledger, Merkle reconciliation to root mesh; emits credit events to UI. (Stub in `src/protocol_layer/protocols/credit_ledger.py`.)
- **RDR ingestion workers** (`services/rdr_ingest/`): crawlers, perspective extraction, embedding + clustering; writes to Postgres + vector DB.
- **Discovery Loop / LoRA forge** (`services/discovery_loop/`): hypothesis queue → T2L/LoRA → validation → DAC packaging.
- **Shadow Twin sync** (`services/twin_sync/`): websocket event fanout; merges RDR graph + resolver telemetry.
- **DAC Factory** (`services/dac_factory/`): package validated LoRAs/capsules into deployable DACs with manifests and credit metadata.

## Data Stores
- **Postgres**: RDR metadata, perspective JSON, ledger events.
- **Vector DB (Weaviate/Qdrant)**: embeddings for RDR graph and similarity routing.
- **Graph DB (Neo4j)**: Shadow Twin capsule graph, URI edges (invokes, validates, depends).
- **Object store/IPFS**: Capsule payloads, DAC images, manifests.
- **Cache (Redis/Dragonfly)**: registry cache, resolution hot paths, telemetry buffers.

## UI/Data Contracts
- **Telemetry topics** (resolver → UI): `capsule.status`, `capsule.proof_hash`, `capsule.entropy`, `capsule.credit_flow`, `capsule.latency`.
- **Shadow Twin feed**: nodes (URI, UTID, credit, entropy), edges (invokes, validates, depends), trend overlays from RDR.
- **Dynamic Islands/HUD**: ReactorGauge (entropy/stability), TruthSigil (proof events), Constellation (DAG nodes), EnergyField (execution pulses).
- **Client uploads**: PDF/dataset drop → RDR ingest endpoint → private twin namespace.

## Testing Harness
- **Resolver tests**: URI parsing, bad URI handling, UTID/Merkle validation, sandbox determinism, status code coverage.
- **Credit ledger tests**: reconciliation against synthetic Merkle roots; double-spend protection.
- **RDR pipeline tests**: ingestion → perspective extraction → embeddings → clustering outputs.
- **Capsule verification**: `tests/verify_capsule_<id>.py` + grand harness validating proofs/entropy budgets per capsule.
- **End-to-end**: capsule:// pipeline (ingest → forge → DAC → resolver → UI telemetry) under load.

## Immediate Tasks
1) Swap scaffold to real registry/mesh/sandbox/ledger services; retain status codes/telemetry contract.  
2) Wire resolver to twin_sync emitter with websocket/bus sink (per `resolver-telemetry-wiring.md`).  
3) Stand up RDR ingestion service (ingest → perspective JSON → embedding store) and connect to twin_sync.  
4) Define registry/ledger schemas in Postgres; set up vector DB + graph DB configs.  
5) Harden tests for resolver, ledger, and telemetry; add deterministic fixtures.  
6) Align capsule manifests to include credit metadata and UTID lineage for DAC Factory.

## Suggested Role Mapping
- Protocol/Resolver: systems engineer + infra.  
- Ledger/Credits: backend + security/crypto.  
- RDR/Embedding: ML engineer + data engineer.  
- Shadow Twin/UX: frontend/graphics + realtime backend.  
- Capsules/DACs: applied physics + backend + QA.  
