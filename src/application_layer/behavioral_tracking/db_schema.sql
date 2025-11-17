--
-- PostgreSQL Schema for Behavioral Tracking and Behavioral Vectors
-- Part of Week 9: Behavioral Tracking Infrastructure
--

-- Create schema
CREATE SCHEMA IF NOT EXISTS behavioral;

-- Set search path
SET search_path TO behavioral, public;

-- ==============================================================================
-- Interaction Events Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS interaction_events (
    event_id UUID PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',

    -- User context
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,
    device_id VARCHAR(255),
    device_type VARCHAR(50) DEFAULT 'web',

    -- Capsule context
    capsule_id VARCHAR(255),
    capsule_type VARCHAR(50),
    capsule_category VARCHAR(100),

    -- Interaction details
    interaction_target VARCHAR(50),
    action_id VARCHAR(255),
    component_id VARCHAR(255),

    -- Timing metrics
    duration_ms INTEGER,
    time_since_last_interaction_ms INTEGER,

    -- Interaction data (JSONB for flexibility)
    interaction_data JSONB DEFAULT '{}'::jsonb,

    -- Result
    success BOOLEAN DEFAULT true,
    error_message TEXT,

    -- Behavioral context
    context JSONB DEFAULT '{}'::jsonb,

    -- Indexing
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for interaction_events
CREATE INDEX idx_events_user_id ON interaction_events(user_id);
CREATE INDEX idx_events_timestamp ON interaction_events(timestamp DESC);
CREATE INDEX idx_events_user_timestamp ON interaction_events(user_id, timestamp DESC);
CREATE INDEX idx_events_session_id ON interaction_events(session_id);
CREATE INDEX idx_events_capsule_id ON interaction_events(capsule_id);
CREATE INDEX idx_events_event_type ON interaction_events(event_type);
CREATE INDEX idx_events_device_type ON interaction_events(device_type);
CREATE INDEX idx_events_interaction_data ON interaction_events USING gin(interaction_data);
CREATE INDEX idx_events_context ON interaction_events USING gin(context);

-- Partition by timestamp (monthly partitions)
-- This will improve query performance for time-range queries
CREATE TABLE interaction_events_y2025m01 PARTITION OF interaction_events
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE interaction_events_y2025m02 PARTITION OF interaction_events
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
-- Add more partitions as needed

-- ==============================================================================
-- User Sessions Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS user_sessions (
    session_id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    last_interaction_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    device_id VARCHAR(255),
    device_type VARCHAR(50),

    -- Session metrics
    event_count INTEGER DEFAULT 0,
    unique_capsules_count INTEGER DEFAULT 0,
    duration_minutes FLOAT,

    -- Session data
    interaction_type_distribution JSONB DEFAULT '{}'::jsonb,
    capsule_types_visited JSONB DEFAULT '[]'::jsonb,

    -- Status
    active BOOLEAN DEFAULT true,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for user_sessions
CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_sessions_started_at ON user_sessions(started_at DESC);
CREATE INDEX idx_sessions_active ON user_sessions(active);

-- ==============================================================================
-- Behavioral Vectors Table
-- ==============================================================================

CREATE TABLE IF NOT EXISTS behavioral_vectors (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL UNIQUE,
    computed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    version INTEGER DEFAULT 1,

    -- Usage patterns
    usage_patterns JSONB NOT NULL,

    -- Preferences
    preferences JSONB NOT NULL,

    -- Expertise level
    expertise_level JSONB NOT NULL,

    -- Engagement metrics
    engagement_metrics JSONB NOT NULL,

    -- Adaptive UX config
    adaptive_ux_config JSONB NOT NULL,

    -- Metadata
    metadata JSONB NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for behavioral_vectors
CREATE INDEX idx_bv_user_id ON behavioral_vectors(user_id);
CREATE INDEX idx_bv_computed_at ON behavioral_vectors(computed_at DESC);
CREATE INDEX idx_bv_version ON behavioral_vectors(version);
CREATE INDEX idx_bv_usage_patterns ON behavioral_vectors USING gin(usage_patterns);
CREATE INDEX idx_bv_expertise_level ON behavioral_vectors USING gin(expertise_level);
CREATE INDEX idx_bv_engagement_metrics ON behavioral_vectors USING gin(engagement_metrics);

-- ==============================================================================
-- BV History Table (for tracking changes over time)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS bv_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    computed_at TIMESTAMP WITH TIME ZONE NOT NULL,
    version INTEGER DEFAULT 1,

    -- Snapshot of the BV at this time
    bv_snapshot JSONB NOT NULL,

    -- What changed
    changes_summary JSONB,

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for bv_history
CREATE INDEX idx_bv_history_user_id ON bv_history(user_id);
CREATE INDEX idx_bv_history_computed_at ON bv_history(computed_at DESC);
CREATE INDEX idx_bv_history_user_computed ON bv_history(user_id, computed_at DESC);

-- ==============================================================================
-- User Archetypes Table (for cross-user pattern analysis)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS user_archetypes (
    id SERIAL PRIMARY KEY,
    archetype_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,

    -- Archetype characteristics
    characteristics JSONB NOT NULL,

    -- Typical usage patterns
    typical_patterns JSONB NOT NULL,

    -- UX recommendations
    ux_recommendations JSONB NOT NULL,

    -- Statistics
    user_count INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for user_archetypes
CREATE INDEX idx_archetypes_name ON user_archetypes(archetype_name);

-- ==============================================================================
-- UX Experiment Tracking (for A/B testing - Week 10)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS ux_experiments (
    id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,

    -- Experiment configuration
    variant_a JSONB NOT NULL,
    variant_b JSONB NOT NULL,

    -- Metrics to track
    metrics JSONB NOT NULL,

    -- Status
    status VARCHAR(50) DEFAULT 'draft', -- draft, active, completed, archived

    -- Results
    results JSONB,
    statistical_significance FLOAT,
    winner VARCHAR(10), -- 'A', 'B', or 'none'

    -- Timestamps
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ux_experiments
CREATE INDEX idx_experiments_status ON ux_experiments(status);
CREATE INDEX idx_experiments_start_date ON ux_experiments(start_date DESC);

-- ==============================================================================
-- User Experiment Assignments (which users are in which experiment variant)
-- ==============================================================================

CREATE TABLE IF NOT EXISTS user_experiment_assignments (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    experiment_id INTEGER NOT NULL REFERENCES ux_experiments(id) ON DELETE CASCADE,
    variant VARCHAR(10) NOT NULL, -- 'A' or 'B'
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Ensure each user is only assigned to an experiment once
    UNIQUE(user_id, experiment_id)
);

-- Indexes for user_experiment_assignments
CREATE INDEX idx_user_exp_user_id ON user_experiment_assignments(user_id);
CREATE INDEX idx_user_exp_experiment_id ON user_experiment_assignments(experiment_id);
CREATE INDEX idx_user_exp_variant ON user_experiment_assignments(variant);

-- ==============================================================================
-- Views for common queries
-- ==============================================================================

-- Recent user activity view
CREATE OR REPLACE VIEW recent_user_activity AS
SELECT
    user_id,
    COUNT(*) as event_count,
    MAX(timestamp) as last_interaction,
    COUNT(DISTINCT session_id) as session_count,
    COUNT(DISTINCT capsule_id) as unique_capsules,
    AVG(duration_ms) as avg_duration_ms
FROM interaction_events
WHERE timestamp > NOW() - INTERVAL '30 days'
GROUP BY user_id;

-- User engagement summary view
CREATE OR REPLACE VIEW user_engagement_summary AS
SELECT
    bv.user_id,
    bv.expertise_level->>'archetype' as archetype,
    (bv.expertise_level->>'overall_score')::float as expertise_score,
    (bv.engagement_metrics->>'engagement_score')::float as engagement_score,
    (bv.engagement_metrics->>'recency_days')::float as recency_days,
    bv.computed_at,
    rua.event_count as recent_event_count,
    rua.last_interaction
FROM behavioral_vectors bv
LEFT JOIN recent_user_activity rua ON bv.user_id = rua.user_id;

-- ==============================================================================
-- Functions
-- ==============================================================================

-- Function to update BV timestamp on modification
CREATE OR REPLACE FUNCTION update_bv_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update timestamp
CREATE TRIGGER trigger_update_bv_timestamp
    BEFORE UPDATE ON behavioral_vectors
    FOR EACH ROW
    EXECUTE FUNCTION update_bv_timestamp();

-- Function to archive old BV to history
CREATE OR REPLACE FUNCTION archive_bv_to_history()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO bv_history (user_id, computed_at, version, bv_snapshot)
    VALUES (
        OLD.user_id,
        OLD.computed_at,
        OLD.version,
        jsonb_build_object(
            'usage_patterns', OLD.usage_patterns,
            'preferences', OLD.preferences,
            'expertise_level', OLD.expertise_level,
            'engagement_metrics', OLD.engagement_metrics,
            'adaptive_ux_config', OLD.adaptive_ux_config,
            'metadata', OLD.metadata
        )
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-archive on BV update
CREATE TRIGGER trigger_archive_bv
    BEFORE UPDATE ON behavioral_vectors
    FOR EACH ROW
    EXECUTE FUNCTION archive_bv_to_history();

-- ==============================================================================
-- Initial Data / Seed Data
-- ==============================================================================

-- Insert default user archetypes
INSERT INTO user_archetypes (archetype_name, description, characteristics, typical_patterns, ux_recommendations)
VALUES
    ('novice', 'New users learning the system',
     '{"expertise_range": [0.0, 0.3], "typical_duration": "high", "error_rate": "high"}',
     '{"interactions_per_session": 5, "prefers_guided_flows": true}',
     '{"show_tooltips": true, "enable_tutorials": true, "simplified_layout": true}'),

    ('intermediate', 'Regular users with basic proficiency',
     '{"expertise_range": [0.3, 0.5], "typical_duration": "medium", "error_rate": "medium"}',
     '{"interactions_per_session": 15, "explores_features": true}',
     '{"contextual_help": true, "moderate_density": true, "shortcuts_suggested": true}'),

    ('advanced', 'Experienced users with deep knowledge',
     '{"expertise_range": [0.5, 0.7], "typical_duration": "low", "error_rate": "low"}',
     '{"interactions_per_session": 25, "uses_advanced_features": true}',
     '{"dense_information": true, "keyboard_shortcuts": true, "advanced_filters": true}'),

    ('expert', 'Highly skilled users',
     '{"expertise_range": [0.7, 0.8], "typical_duration": "very_low", "error_rate": "very_low"}',
     '{"interactions_per_session": 35, "efficient_workflows": true}',
     '{"maximum_density": true, "all_shortcuts": true, "customization": true}'),

    ('power_user', 'Expert users who push the system to its limits',
     '{"expertise_range": [0.8, 1.0], "typical_duration": "minimal", "error_rate": "minimal"}',
     '{"interactions_per_session": 50, "automation": true, "bulk_operations": true}',
     '{"api_access": true, "scripting": true, "full_customization": true, "power_tools": true}')
ON CONFLICT (archetype_name) DO NOTHING;

-- ==============================================================================
-- Permissions (adjust as needed for your environment)
-- ==============================================================================

-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA behavioral TO your_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA behavioral TO your_app_user;

-- ==============================================================================
-- Maintenance
-- ==============================================================================

-- Create monthly partitions automatically (requires pg_cron or external scheduler)
-- Example for creating next month's partition:
-- CREATE TABLE interaction_events_y2025m03 PARTITION OF interaction_events
--     FOR VALUES FROM ('2025-03-01') TO ('2025-04-01');

-- Vacuum and analyze regularly
-- VACUUM ANALYZE behavioral.interaction_events;
-- VACUUM ANALYZE behavioral.behavioral_vectors;

COMMENT ON SCHEMA behavioral IS 'Schema for behavioral tracking and adaptive UX';
COMMENT ON TABLE interaction_events IS 'Stores all capsule interaction events for behavioral analysis';
COMMENT ON TABLE behavioral_vectors IS 'Stores computed Behavioral Vectors for each user';
COMMENT ON TABLE bv_history IS 'Historical snapshots of Behavioral Vectors';
COMMENT ON TABLE user_archetypes IS 'Predefined user archetype definitions';
COMMENT ON TABLE ux_experiments IS 'A/B testing experiments for UX optimization';
