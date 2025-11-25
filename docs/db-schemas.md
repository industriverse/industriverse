# Database Schemas (Phase 2/3 hardening)

## Ledger (Postgres)
```
CREATE TABLE ledger_entries (
  utid TEXT PRIMARY KEY,
  uri TEXT NOT NULL,
  delta_credits NUMERIC NOT NULL,
  proof_hash TEXT,
  credit_root TEXT,
  ts TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX ON ledger_entries (credit_root);
CREATE INDEX ON ledger_entries (ts);
```

## RDR
```
CREATE TABLE rdr_ingest_queue (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source TEXT,
  uri TEXT,
  tags TEXT[],
  priority INT DEFAULT 0,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE rdr_perspectives (
  paper_id TEXT PRIMARY KEY,
  perspectives JSONB,
  embedding_id TEXT,
  cluster_id TEXT,
  novelty_score NUMERIC,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE rdr_trends (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  window_start TIMESTAMPTZ,
  window_end TIMESTAMPTZ,
  cluster_id TEXT,
  delta NUMERIC,
  summary TEXT
);

CREATE TABLE rdr_hypotheses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  paper_id TEXT,
  hypothesis_text TEXT,
  priority INT DEFAULT 0,
  status TEXT DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT now()
);
```

## DAC Registry (suggested)
```
CREATE TABLE dac_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  uri TEXT,
  utid TEXT,
  manifest JSONB,
  location TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
```
