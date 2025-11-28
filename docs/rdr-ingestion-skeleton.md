# Real Deep Research (RDR) Ingestion Skeleton

Purpose: operational outline for Phase 3 (RDR ingestion → Discovery Loop feed) with concrete components to implement next.

## Pipeline
1) **Ingress**: sources (arXiv API, industry feeds, client uploads).  
   - Worker: `rdr_ingest` fetches metadata + blobs.  
   - Store metadata in Postgres table `rdr_ingest_queue` with source tags.
2) **Perspective Extraction**: LLM prompt to emit perspectives `["Observable","Phenomenon","Mechanism","Scale","Method","Application"]`.  
   - Output JSON stored at `rdr_processed/<paper_id>.json`.
3) **Embedding + Projection**: encode summaries → vector DB (Weaviate/Qdrant); HDBSCAN/UMAP for clusters.  
   - Persist cluster IDs + scores in Postgres.
4) **Trend Delta**: time-sliced clustering; write weekly reports to `rdr_trends`.
5) **Hypothesis Queue**: high-novelty items pushed to `discovery_loop` queue for T2L/LoRA forge.
6) **Shadow Twin Sync**: stream graph updates (nodes/edges) to `twin_sync` for visualization.

## Data Contracts
- `rdr_ingest_queue`: id, source, uri, status, priority, tags, created_at.
- `rdr_perspectives`: paper_id, json_blob, embedding_id, cluster_id, novelty_score.
- `rdr_trends`: window_start, window_end, cluster_summaries.
- `rdr_hypotheses`: paper_id, hypothesis_text, priority, status.

## Interfaces
- REST/gRPC: `/rdr/ingest` for client uploads (PDF/datasets); `/rdr/status/<id>`.
- Message bus topic: `rdr.hypothesis.ready` → consumed by discovery_loop/forge.
- Twin feed: websocket events `rdr.node`, `rdr.edge`, `rdr.trend`.

## Testing Hooks
- Deterministic fixtures for ingestion and perspective extraction.
- Embedding regression tests (same text → stable vector within tolerance).
- Novelty score smoke tests over synthetic corpora.

## Performance Targets
- Ingestion cadence: every 12h scheduled; ad-hoc uploads on-demand.
- Perspective extraction p50 < 2s per doc; embedding p50 < 500ms.
- Twin updates within < 1s of new hypothesis emission.
