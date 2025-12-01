-- Evolution Engine Schema

CREATE TABLE experiments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    layer INTEGER NOT NULL, -- 1: Product, 2: AI, 3: Thermo, 4: Narrative
    hypothesis TEXT,
    status VARCHAR(50) DEFAULT 'PLANNED', -- PLANNED, RUNNING, COMPLETED
    winner VARCHAR(10),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE variants (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    name VARCHAR(50), -- 'A', 'B'
    config JSONB,
    description TEXT
);

CREATE TABLE results (
    id SERIAL PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments(id),
    variant_id INTEGER REFERENCES variants(id),
    roi FLOAT,
    latency_ms FLOAT,
    stability_score FLOAT,
    truth_score FLOAT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);
