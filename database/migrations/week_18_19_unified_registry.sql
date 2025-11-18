--
-- Week 18-19 Day 4: Unified Capsule Registry Schema
--
-- Central registry for all capsules created across Application Layer and
-- Deployment Operations Layer with full lineage tracking and governance metadata
--

-- Ensure UUID extension is available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create capsules schema if not exists (should already exist from Week 17)
CREATE SCHEMA IF NOT EXISTS capsules;

-- Unified Capsule Registry Table
CREATE TABLE IF NOT EXISTS capsules.unified_registry (
    -- Primary identification
    capsule_id UUID PRIMARY KEY,

    -- Source tracking
    source VARCHAR(50) NOT NULL,  -- 'application_layer' or 'deployment_ops_layer'

    -- Template/Blueprint tracking
    template_id VARCHAR(255),     -- Template ID if created from template
    blueprint_id VARCHAR(255),    -- Blueprint ID

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Lifecycle tracking
    status VARCHAR(50) DEFAULT 'active',  -- 'requested', 'active', 'evolving', 'deprecated', etc.
    governance_status VARCHAR(50) DEFAULT 'pending',  -- 'pending', 'validated', 'rejected'

    -- Evolution tracking
    evolution_generation INTEGER DEFAULT 1,
    parent_capsule_id UUID REFERENCES capsules.unified_registry(capsule_id),

    -- Complete capsule data (JSONB for flexible schema)
    capsule_data JSONB NOT NULL,

    -- Additional metadata (JSONB for extensibility)
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Constraints
    CONSTRAINT valid_source CHECK (source IN ('application_layer', 'deployment_ops_layer')),
    CONSTRAINT valid_status CHECK (status IN (
        'requested', 'governance_review', 'governance_approved', 'governance_rejected',
        'infrastructure_provisioning', 'infrastructure_ready', 'active',
        'evolving', 'deprecated', 'decommissioned'
    )),
    CONSTRAINT valid_governance_status CHECK (governance_status IN ('pending', 'validated', 'rejected'))
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_unified_registry_source
    ON capsules.unified_registry(source);

CREATE INDEX IF NOT EXISTS idx_unified_registry_template
    ON capsules.unified_registry(template_id);

CREATE INDEX IF NOT EXISTS idx_unified_registry_blueprint
    ON capsules.unified_registry(blueprint_id);

CREATE INDEX IF NOT EXISTS idx_unified_registry_status
    ON capsules.unified_registry(status);

CREATE INDEX IF NOT EXISTS idx_unified_registry_governance_status
    ON capsules.unified_registry(governance_status);

CREATE INDEX IF NOT EXISTS idx_unified_registry_generation
    ON capsules.unified_registry(evolution_generation);

CREATE INDEX IF NOT EXISTS idx_unified_registry_parent
    ON capsules.unified_registry(parent_capsule_id);

CREATE INDEX IF NOT EXISTS idx_unified_registry_created_at
    ON capsules.unified_registry(created_at DESC);

-- GIN index for JSONB search (fast queries on capsule_data)
CREATE INDEX IF NOT EXISTS idx_unified_registry_data
    ON capsules.unified_registry USING gin(capsule_data);

CREATE INDEX IF NOT EXISTS idx_unified_registry_metadata
    ON capsules.unified_registry USING gin(metadata);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_unified_registry_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_unified_registry_updated_at
    BEFORE UPDATE ON capsules.unified_registry
    FOR EACH ROW
    EXECUTE FUNCTION update_unified_registry_updated_at();

-- Comments
COMMENT ON TABLE capsules.unified_registry IS
    'Unified registry for all capsules created across Application Layer and Deployment Operations Layer';

COMMENT ON COLUMN capsules.unified_registry.capsule_id IS
    'Unique capsule identifier (UUID)';

COMMENT ON COLUMN capsules.unified_registry.source IS
    'Source of capsule creation: application_layer (template-based) or deployment_ops_layer (infrastructure)';

COMMENT ON COLUMN capsules.unified_registry.template_id IS
    'Template ID if capsule was created from a template in Application Layer';

COMMENT ON COLUMN capsules.unified_registry.blueprint_id IS
    'Blueprint ID used for infrastructure provisioning';

COMMENT ON COLUMN capsules.unified_registry.governance_status IS
    'Governance validation status: pending (not yet validated), validated (approved), rejected (denied)';

COMMENT ON COLUMN capsules.unified_registry.evolution_generation IS
    'Generation number for evolution tracking (increments with each descendant)';

COMMENT ON COLUMN capsules.unified_registry.parent_capsule_id IS
    'Parent capsule ID for evolution lineage tracking (NULL if first generation)';

COMMENT ON COLUMN capsules.unified_registry.capsule_data IS
    'Complete capsule data including lifecycle context, governance metadata, application instance, and infrastructure instance (JSONB)';

-- Example queries for documentation
--
-- Get all active capsules from Application Layer:
--   SELECT * FROM capsules.unified_registry
--   WHERE source = 'application_layer' AND status = 'active';
--
-- Get all validated capsules:
--   SELECT * FROM capsules.unified_registry
--   WHERE governance_status = 'validated';
--
-- Get capsule lineage (children of a parent):
--   SELECT * FROM capsules.unified_registry
--   WHERE parent_capsule_id = '<parent-capsule-id>';
--
-- Search capsule_data JSONB:
--   SELECT * FROM capsules.unified_registry
--   WHERE capsule_data @> '{"governance": {"validated_at": 1234567890}}'::jsonb;
--
-- Get evolution tree (recursive query for all ancestors):
--   WITH RECURSIVE ancestors AS (
--     SELECT capsule_id, parent_capsule_id, evolution_generation, 1 as depth
--     FROM capsules.unified_registry
--     WHERE capsule_id = '<capsule-id>'
--     UNION ALL
--     SELECT r.capsule_id, r.parent_capsule_id, r.evolution_generation, a.depth + 1
--     FROM capsules.unified_registry r
--     INNER JOIN ancestors a ON r.capsule_id = a.parent_capsule_id
--     WHERE a.depth < 10
--   )
--   SELECT * FROM ancestors;
