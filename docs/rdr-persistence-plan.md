# RDR Persistence and Services (Phase 3 hardening)

Components:
- **Postgres**: `rdr_ingest_queue`, `rdr_perspectives`, `rdr_trends`, `rdr_hypotheses`.
- **Vector DB (Qdrant/Weaviate)**: store embeddings keyed by paper_id, with tags.
- **Graph DB (Neo4j)**: Shadow Twin nodes/edges (capsule URIs, RDR nodes, similarity edges).
- **Object store**: PDFs/datasets, processed JSON, manifests.

Service endpoints:
- `POST /rdr/ingest` (source, uri, tags, priority)
- `GET /rdr/status/<id>`
- `POST /rdr/upload` (client upload → object store → ingest queue)
- Message bus topics: `rdr.hypothesis.ready`, `rdr.node`, `rdr.edge`, `rdr.trend`.

Operational:
- Ingestion scheduler every 12h + on-demand.
- Perspective extractor workers pull from queue, write to Postgres + vector DB.
- Trend job aggregates clusters weekly into `rdr_trends`.
- Hypothesis dispatcher pushes high-novelty items to Discovery Loop (forge).

Security:
- Auth on ingest/upload endpoints.
- Signed object URLs for client uploads.
- PII scrubbers on uploads when enabled.
