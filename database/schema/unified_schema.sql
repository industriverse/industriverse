-- =============================================================================
-- Industriverse Unified Database Schema
-- Week 17: Database Setup & Schema Migration
-- =============================================================================
--
-- This unified schema consolidates:
-- 1. Week 9 Behavioral Tracking (from application_layer/behavioral_tracking/)
-- 2. Week 16 Capsule-Pins PWA (from week-16 branch)
-- 3. Core framework requirements
--
-- Database: PostgreSQL 16+
-- Extensions: pgcrypto, uuid-ossp
-- =============================================================================

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS behavioral;
CREATE SCHEMA IF NOT EXISTS capsules;
CREATE SCHEMA IF NOT EXISTS overseer;
CREATE SCHEMA IF NOT EXISTS security;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Set default search path
SET search_path TO public, behavioral, capsules, overseer, security, analytics;

-- =============================================================================
-- SCHEMA 1: BEHAVIORAL TRACKING (Week 9)
-- =============================================================================

SET search_path TO behavioral;

-- Interaction Events Table (from Week 9)
CREATE TABLE IF NOT EXISTS interaction_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
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
CREATE INDEX IF NOT EXISTS idx_events_user_id ON interaction_events(user_id);
CREATE INDEX IF NOT EXISTS idx_events_timestamp ON interaction_events(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_user_timestamp ON interaction_events(user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_events_session_id ON interaction_events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_capsule_id ON interaction_events(capsule_id);
CREATE INDEX IF NOT EXISTS idx_events_event_type ON interaction_events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_device_type ON interaction_events(device_type);
CREATE INDEX IF NOT EXISTS idx_events_interaction_data ON interaction_events USING gin(interaction_data);
CREATE INDEX IF NOT EXISTS idx_events_context ON interaction_events USING gin(context);

-- User Sessions Table
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
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started_at ON user_sessions(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_sessions_active ON user_sessions(active);

-- Behavioral Vectors Table
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
CREATE INDEX IF NOT EXISTS idx_bv_user_id ON behavioral_vectors(user_id);
CREATE INDEX IF NOT EXISTS idx_bv_computed_at ON behavioral_vectors(computed_at DESC);
CREATE INDEX IF NOT EXISTS idx_bv_version ON behavioral_vectors(version);
CREATE INDEX IF NOT EXISTS idx_bv_usage_patterns ON behavioral_vectors USING gin(usage_patterns);
CREATE INDEX IF NOT EXISTS idx_bv_expertise_level ON behavioral_vectors USING gin(expertise_level);
CREATE INDEX IF NOT EXISTS idx_bv_engagement_metrics ON behavioral_vectors USING gin(engagement_metrics);

-- Behavioral Vector History (for temporal tracking)
CREATE TABLE IF NOT EXISTS bv_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    behavioral_vector_id INTEGER REFERENCES behavioral_vectors(id),
    archived_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    vector_data JSONB NOT NULL,
    reason VARCHAR(100)
);

CREATE INDEX IF NOT EXISTS idx_bv_history_user_id ON bv_history(user_id);
CREATE INDEX IF NOT EXISTS idx_bv_history_archived_at ON bv_history(archived_at DESC);

-- User Archetypes (behavioral personas)
CREATE TABLE IF NOT EXISTS user_archetypes (
    id SERIAL PRIMARY KEY,
    archetype_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    characteristic_patterns JSONB NOT NULL,
    suggested_ux_config JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert default archetypes
INSERT INTO user_archetypes (archetype_name, description, characteristic_patterns, suggested_ux_config)
VALUES
    ('novice', 'New user, minimal interaction history', '{"avg_session_duration": 300, "interaction_frequency": "low"}', '{"tooltips": true, "guided_tour": true, "complexity": "simple"}'),
    ('intermediate', 'Regular user with moderate experience', '{"avg_session_duration": 600, "interaction_frequency": "medium"}', '{"tooltips": false, "shortcuts": true, "complexity": "moderate"}'),
    ('power_user', 'Advanced user with high engagement', '{"avg_session_duration": 1200, "interaction_frequency": "high"}', '{"tooltips": false, "shortcuts": true, "advanced_features": true, "complexity": "advanced"}')
ON CONFLICT (archetype_name) DO NOTHING;

-- UX Experiments (for A/B testing)
CREATE TABLE IF NOT EXISTS ux_experiments (
    id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    variant_a_config JSONB NOT NULL,
    variant_b_config JSONB NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- SCHEMA 2: CAPSULES (Week 16 + Main Framework)
-- =============================================================================

SET search_path TO capsules;

-- Capsules Table (unified from Week 16 and application_layer)
CREATE TABLE IF NOT EXISTS capsules (
    capsule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Core identification
    title VARCHAR(255) NOT NULL,
    description TEXT,
    capsule_type VARCHAR(50) NOT NULL, -- task, workflow, alert, status, decision, custom
    severity VARCHAR(50) NOT NULL DEFAULT 'info', -- info, warning, critical
    category VARCHAR(100),

    -- Source information
    sensor_id VARCHAR(255),
    sensor_type VARCHAR(100),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    metric_unit VARCHAR(50),

    -- Shadow Twin Consensus
    consensus_approved BOOLEAN DEFAULT false,
    consensus_pct FLOAT DEFAULT 0.0,
    consensus_data JSONB,

    -- Capsule lifecycle
    status VARCHAR(50) DEFAULT 'active', -- active, acknowledged, completed, dismissed
    priority INTEGER DEFAULT 0,

    -- Assignment
    assigned_to VARCHAR(255),
    assigned_at TIMESTAMP WITH TIME ZONE,

    -- Completion
    completed_at TIMESTAMP WITH TIME ZONE,
    dismissed_at TIMESTAMP WITH TIME ZONE,
    acknowledged_at TIMESTAMP WITH TIME ZONE,

    -- Data
    payload JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for capsules
CREATE INDEX IF NOT EXISTS idx_capsules_type ON capsules(capsule_type);
CREATE INDEX IF NOT EXISTS idx_capsules_severity ON capsules(severity);
CREATE INDEX IF NOT EXISTS idx_capsules_status ON capsules(status);
CREATE INDEX IF NOT EXISTS idx_capsules_created_at ON capsules(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_capsules_sensor_id ON capsules(sensor_id);
CREATE INDEX IF NOT EXISTS idx_capsules_assigned_to ON capsules(assigned_to);
CREATE INDEX IF NOT EXISTS idx_capsules_consensus ON capsules(consensus_approved, consensus_pct);
CREATE INDEX IF NOT EXISTS idx_capsules_payload ON capsules USING gin(payload);
CREATE INDEX IF NOT EXISTS idx_capsules_metadata ON capsules USING gin(metadata);

-- Capsule Rules (for automated capsule creation)
CREATE TABLE IF NOT EXISTS capsule_rules (
    rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    rule_name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Trigger conditions
    sensor_type VARCHAR(100),
    metric_name VARCHAR(100) NOT NULL,
    threshold FLOAT NOT NULL,
    operator VARCHAR(10) NOT NULL, -- gt, lt, eq, gte, lte

    -- Capsule template
    capsule_type VARCHAR(50) NOT NULL,
    severity VARCHAR(50) NOT NULL,
    title_template VARCHAR(255),
    description_template TEXT,

    -- Rule configuration
    active BOOLEAN DEFAULT true,
    priority INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_capsule_rules_active ON capsule_rules(active);
CREATE INDEX IF NOT EXISTS idx_capsule_rules_metric ON capsule_rules(metric_name);

-- Sensor Readings (raw data from sensors)
CREATE TABLE IF NOT EXISTS sensor_readings (
    reading_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    sensor_id VARCHAR(255) NOT NULL,
    sensor_type VARCHAR(100) NOT NULL,

    -- Reading data
    metric_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(50),

    -- Metadata
    location VARCHAR(255),
    equipment_id VARCHAR(255),
    tags JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    reading_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    received_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Partitioning by month for performance (example for current month)
CREATE TABLE IF NOT EXISTS sensor_readings_2025_11 PARTITION OF sensor_readings
    FOR VALUES FROM ('2025-11-01') TO ('2025-12-01');

-- Indexes for sensor_readings
CREATE INDEX IF NOT EXISTS idx_sensor_readings_sensor_id ON sensor_readings(sensor_id);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_timestamp ON sensor_readings(reading_timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_sensor_readings_metric ON sensor_readings(metric_name);

-- =============================================================================
-- SCHEMA 3: OVERSEER SYSTEM
-- =============================================================================

SET search_path TO overseer;

-- Capsule Governance Policies
CREATE TABLE IF NOT EXISTS governance_policies (
    policy_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    policy_name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,

    -- Policy rules
    rules JSONB NOT NULL,
    enforcement_level VARCHAR(50) DEFAULT 'advisory', -- strict, advisory, monitoring

    -- Scope
    applies_to_capsule_types VARCHAR(100)[],
    applies_to_users VARCHAR(255)[],

    -- Status
    active BOOLEAN DEFAULT true,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Capsule Events (audit trail)
CREATE TABLE IF NOT EXISTS capsule_events (
    event_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    capsule_id UUID REFERENCES capsules.capsules(capsule_id),

    -- Event details
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}'::jsonb,

    -- Actor
    actor_type VARCHAR(50), -- user, system, agent
    actor_id VARCHAR(255),

    -- Timestamp
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_capsule_events_capsule_id ON capsule_events(capsule_id);
CREATE INDEX IF NOT EXISTS idx_capsule_events_type ON capsule_events(event_type);
CREATE INDEX IF NOT EXISTS idx_capsule_events_occurred_at ON capsule_events(occurred_at DESC);

-- System Health Metrics
CREATE TABLE IF NOT EXISTS system_health_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Metric details
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    metric_unit VARCHAR(50),

    -- Component
    component_name VARCHAR(100),
    component_layer VARCHAR(100),

    -- Metadata
    tags JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_health_metrics_name ON system_health_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_health_metrics_component ON system_health_metrics(component_name);
CREATE INDEX IF NOT EXISTS idx_health_metrics_recorded_at ON system_health_metrics(recorded_at DESC);

-- =============================================================================
-- SCHEMA 4: SECURITY & USERS
-- =============================================================================

SET search_path TO security;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,

    -- Authentication
    password_hash VARCHAR(255) NOT NULL,
    salt VARCHAR(255) NOT NULL,

    -- Profile
    full_name VARCHAR(255),
    role VARCHAR(100) DEFAULT 'operator',
    department VARCHAR(100),

    -- Status
    active BOOLEAN DEFAULT true,
    email_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

-- API Keys (for programmatic access)
CREATE TABLE IF NOT EXISTS api_keys (
    key_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(user_id),

    -- Key details
    key_name VARCHAR(255),
    key_hash VARCHAR(255) NOT NULL UNIQUE,

    -- Permissions
    scopes VARCHAR(100)[],

    -- Status
    active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    last_used_at TIMESTAMP WITH TIME ZONE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_api_keys_active ON api_keys(active);

-- Audit Logs (security audit trail)
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Action details
    action_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),

    -- Actor
    user_id UUID REFERENCES users(user_id),
    api_key_id UUID REFERENCES api_keys(key_id),
    ip_address INET,
    user_agent TEXT,

    -- Details
    action_details JSONB DEFAULT '{}'::jsonb,
    result VARCHAR(50), -- success, failure, partial
    error_message TEXT,

    -- Timestamp
    occurred_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action_type ON audit_logs(action_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_occurred_at ON audit_logs(occurred_at DESC);

-- =============================================================================
-- SCHEMA 5: ANALYTICS
-- =============================================================================

SET search_path TO analytics;

-- Capsule Analytics (aggregated statistics)
CREATE TABLE IF NOT EXISTS capsule_analytics (
    analytics_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Time bucket
    time_bucket TIMESTAMP WITH TIME ZONE NOT NULL,
    bucket_size VARCHAR(20) NOT NULL, -- hour, day, week, month

    -- Aggregations
    total_capsules_created INTEGER DEFAULT 0,
    total_capsules_acknowledged INTEGER DEFAULT 0,
    total_capsules_completed INTEGER DEFAULT 0,
    total_capsules_dismissed INTEGER DEFAULT 0,

    -- By severity
    critical_capsules INTEGER DEFAULT 0,
    warning_capsules INTEGER DEFAULT 0,
    info_capsules INTEGER DEFAULT 0,

    -- Performance metrics
    avg_resolution_time_minutes FLOAT,
    avg_consensus_pct FLOAT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_capsule_analytics_time_bucket ON capsule_analytics(time_bucket DESC);
CREATE INDEX IF NOT EXISTS idx_capsule_analytics_bucket_size ON capsule_analytics(bucket_size);

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Active Capsules View
CREATE OR REPLACE VIEW capsules.active_capsules AS
SELECT
    capsule_id,
    title,
    description,
    capsule_type,
    severity,
    sensor_id,
    consensus_approved,
    consensus_pct,
    status,
    assigned_to,
    created_at
FROM capsules.capsules
WHERE status = 'active'
  AND (expires_at IS NULL OR expires_at > NOW())
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'warning' THEN 2
        WHEN 'info' THEN 3
        ELSE 4
    END,
    created_at DESC;

-- User Engagement Summary View
CREATE OR REPLACE VIEW behavioral.user_engagement_summary AS
SELECT
    bv.user_id,
    bv.computed_at,
    bv.expertise_level->>'level' as expertise_level,
    bv.engagement_metrics->>'score' as engagement_score,
    us.event_count as total_interactions,
    us.unique_capsules_count,
    us.duration_minutes as total_session_duration
FROM behavioral.behavioral_vectors bv
LEFT JOIN behavioral.user_sessions us ON bv.user_id = us.user_id
WHERE us.active = true;

-- System Health Dashboard View
CREATE OR REPLACE VIEW overseer.system_health_dashboard AS
SELECT
    component_name,
    component_layer,
    metric_name,
    AVG(metric_value) as avg_value,
    MIN(metric_value) as min_value,
    MAX(metric_value) as max_value,
    COUNT(*) as sample_count,
    MAX(recorded_at) as last_recorded
FROM overseer.system_health_metrics
WHERE recorded_at > NOW() - INTERVAL '1 hour'
GROUP BY component_name, component_layer, metric_name;

-- =============================================================================
-- FUNCTIONS & TRIGGERS
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update_updated_at trigger to relevant tables
CREATE TRIGGER update_behavioral_vectors_updated_at
    BEFORE UPDATE ON behavioral.behavioral_vectors
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_user_sessions_updated_at
    BEFORE UPDATE ON behavioral.user_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_capsules_updated_at
    BEFORE UPDATE ON capsules.capsules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_capsule_rules_updated_at
    BEFORE UPDATE ON capsules.capsule_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_governance_policies_updated_at
    BEFORE UPDATE ON overseer.governance_policies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON security.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- GRANTS (Default permissions)
-- =============================================================================

-- Grant usage on schemas
GRANT USAGE ON SCHEMA behavioral TO PUBLIC;
GRANT USAGE ON SCHEMA capsules TO PUBLIC;
GRANT USAGE ON SCHEMA overseer TO PUBLIC;
GRANT USAGE ON SCHEMA security TO PUBLIC;
GRANT USAGE ON SCHEMA analytics TO PUBLIC;

-- Grant select on all tables (adjust as needed for production)
GRANT SELECT ON ALL TABLES IN SCHEMA behavioral TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA capsules TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA overseer TO PUBLIC;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO PUBLIC;

-- Security schema should be more restricted
GRANT SELECT ON security.users TO PUBLIC;
REVOKE ALL ON security.audit_logs FROM PUBLIC;

-- =============================================================================
-- INITIALIZATION COMPLETE
-- =============================================================================

-- Insert initial test data (optional)
-- INSERT INTO security.users (username, email, password_hash, salt, full_name, role)
-- VALUES ('admin', 'admin@industriverse.ai', 'hash', 'salt', 'System Administrator', 'admin');

-- Log schema creation
DO $$
BEGIN
    RAISE NOTICE 'Industriverse Unified Database Schema initialized successfully!';
    RAISE NOTICE 'Schemas created: behavioral, capsules, overseer, security, analytics';
    RAISE NOTICE 'Total tables: 20+';
    RAISE NOTICE 'Views: 3';
    RAISE NOTICE 'Functions: 1';
END $$;
