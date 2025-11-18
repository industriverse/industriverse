--
-- Week 18-19 Day 6: AR/VR State Schema
--
-- Persistence layer for AR/VR spatial data, capsule states, environments, and interactions
--

-- Ensure UUID extension is available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create AR/VR state schema
CREATE SCHEMA IF NOT EXISTS ar_vr_state;

-- ============================================================================
-- Spatial Anchors Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS ar_vr_state.spatial_anchors (
    -- Primary identification
    anchor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Environment reference
    environment_id VARCHAR(255) NOT NULL,

    -- 3D Position (meters)
    position_x FLOAT NOT NULL,
    position_y FLOAT NOT NULL,
    position_z FLOAT NOT NULL,

    -- Quaternion Rotation
    rotation_x FLOAT NOT NULL,
    rotation_y FLOAT NOT NULL,
    rotation_z FLOAT NOT NULL,
    rotation_w FLOAT NOT NULL,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Additional metadata (JSONB for extensibility)
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for spatial_anchors
CREATE INDEX IF NOT EXISTS idx_spatial_anchors_environment
    ON ar_vr_state.spatial_anchors(environment_id);

CREATE INDEX IF NOT EXISTS idx_spatial_anchors_created_at
    ON ar_vr_state.spatial_anchors(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_spatial_anchors_metadata
    ON ar_vr_state.spatial_anchors USING gin(metadata);

COMMENT ON TABLE ar_vr_state.spatial_anchors IS
    'Spatial anchors for AR/VR objects with 3D position and quaternion rotation';

COMMENT ON COLUMN ar_vr_state.spatial_anchors.position_x IS
    'X coordinate in 3D space (meters)';

COMMENT ON COLUMN ar_vr_state.spatial_anchors.rotation_w IS
    'W component of quaternion rotation (scalar part)';

-- ============================================================================
-- AR Capsule States Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS ar_vr_state.capsule_states (
    -- Primary identification (references unified registry)
    capsule_id UUID PRIMARY KEY REFERENCES capsules.unified_registry(capsule_id),

    -- Spatial anchor reference
    anchor_id UUID REFERENCES ar_vr_state.spatial_anchors(anchor_id),

    -- Scale
    scale_x FLOAT DEFAULT 1.0,
    scale_y FLOAT DEFAULT 1.0,
    scale_z FLOAT DEFAULT 1.0,

    -- Visibility
    visible BOOLEAN DEFAULT TRUE,

    -- Interaction state
    interaction_state VARCHAR(50) DEFAULT 'idle',  -- idle, focused, selected, interacting
    last_interaction_at TIMESTAMP WITH TIME ZONE,

    -- AR-specific metadata (JSONB)
    ar_metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for capsule_states
CREATE INDEX IF NOT EXISTS idx_capsule_states_anchor
    ON ar_vr_state.capsule_states(anchor_id);

CREATE INDEX IF NOT EXISTS idx_capsule_states_visible
    ON ar_vr_state.capsule_states(visible);

CREATE INDEX IF NOT EXISTS idx_capsule_states_interaction
    ON ar_vr_state.capsule_states(interaction_state);

CREATE INDEX IF NOT EXISTS idx_capsule_states_ar_metadata
    ON ar_vr_state.capsule_states USING gin(ar_metadata);

COMMENT ON TABLE ar_vr_state.capsule_states IS
    'AR/VR rendering states for capsules including scale, visibility, and interaction state';

COMMENT ON COLUMN ar_vr_state.capsule_states.interaction_state IS
    'Current interaction state: idle (no interaction), focused (gaze), selected (tap), interacting (active)';

-- ============================================================================
-- AR/VR Environments Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS ar_vr_state.environments (
    -- Primary identification
    environment_id VARCHAR(255) PRIMARY KEY,

    -- Environment type
    environment_type VARCHAR(50) NOT NULL,  -- mobile_ar, headset_ar, headset_vr, webxr_ar, webxr_vr

    -- User and session
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255) NOT NULL,

    -- Capabilities (JSONB array)
    capabilities JSONB DEFAULT '[]'::jsonb,

    -- Configuration (JSONB)
    configuration JSONB DEFAULT '{}'::jsonb,

    -- Timestamps
    registered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Active status
    active BOOLEAN DEFAULT TRUE,

    -- Constraints
    CONSTRAINT valid_environment_type CHECK (environment_type IN (
        'mobile_ar', 'headset_ar', 'headset_vr', 'webxr_ar', 'webxr_vr'
    ))
);

-- Indexes for environments
CREATE INDEX IF NOT EXISTS idx_environments_user
    ON ar_vr_state.environments(user_id);

CREATE INDEX IF NOT EXISTS idx_environments_session
    ON ar_vr_state.environments(session_id);

CREATE INDEX IF NOT EXISTS idx_environments_active
    ON ar_vr_state.environments(active);

CREATE INDEX IF NOT EXISTS idx_environments_last_active
    ON ar_vr_state.environments(last_active_at DESC);

CREATE INDEX IF NOT EXISTS idx_environments_type
    ON ar_vr_state.environments(environment_type);

COMMENT ON TABLE ar_vr_state.environments IS
    'AR/VR environment configurations and session tracking';

COMMENT ON COLUMN ar_vr_state.environments.capabilities IS
    'Array of environment capabilities: hand_tracking, gaze_input, voice_command, etc.';

-- ============================================================================
-- Interaction History Table
-- ============================================================================

CREATE TABLE IF NOT EXISTS ar_vr_state.interaction_history (
    -- Primary identification
    interaction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Environment reference
    environment_id VARCHAR(255) NOT NULL,

    -- User
    user_id VARCHAR(255) NOT NULL,

    -- Capsule (optional)
    capsule_id UUID REFERENCES capsules.unified_registry(capsule_id),

    -- Interaction type
    interaction_type VARCHAR(50) NOT NULL,  -- hand_tracking, controller_input, gaze_input, voice_command, gesture_recognition

    -- Interaction data (JSONB)
    interaction_data JSONB NOT NULL,

    -- Timestamp
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for interaction_history
CREATE INDEX IF NOT EXISTS idx_interaction_history_environment
    ON ar_vr_state.interaction_history(environment_id);

CREATE INDEX IF NOT EXISTS idx_interaction_history_user
    ON ar_vr_state.interaction_history(user_id);

CREATE INDEX IF NOT EXISTS idx_interaction_history_capsule
    ON ar_vr_state.interaction_history(capsule_id);

CREATE INDEX IF NOT EXISTS idx_interaction_history_type
    ON ar_vr_state.interaction_history(interaction_type);

CREATE INDEX IF NOT EXISTS idx_interaction_history_timestamp
    ON ar_vr_state.interaction_history(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_interaction_history_data
    ON ar_vr_state.interaction_history USING gin(interaction_data);

COMMENT ON TABLE ar_vr_state.interaction_history IS
    'Historical log of all AR/VR interactions for analytics and behavioral tracking';

COMMENT ON COLUMN ar_vr_state.interaction_history.interaction_type IS
    'Type of spatial interaction: hand_tracking, controller_input, gaze_input, voice_command, gesture_recognition';

-- ============================================================================
-- Triggers
-- ============================================================================

-- Auto-update updated_at for spatial_anchors
CREATE OR REPLACE FUNCTION update_spatial_anchors_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_spatial_anchors_updated_at
    BEFORE UPDATE ON ar_vr_state.spatial_anchors
    FOR EACH ROW
    EXECUTE FUNCTION update_spatial_anchors_updated_at();

-- ============================================================================
-- Permissions (optional - adjust as needed)
-- ============================================================================

-- REVOKE ALL ON SCHEMA ar_vr_state FROM PUBLIC;
-- GRANT USAGE ON SCHEMA ar_vr_state TO industriverse_app;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA ar_vr_state TO industriverse_app;

-- ============================================================================
-- Example Queries
-- ============================================================================

-- Get all spatial anchors for an environment:
--   SELECT * FROM ar_vr_state.spatial_anchors
--   WHERE environment_id = '<environment-id>';
--
-- Get AR capsule state with spatial anchor:
--   SELECT
--     cs.*,
--     sa.position_x, sa.position_y, sa.position_z,
--     sa.rotation_x, sa.rotation_y, sa.rotation_z, sa.rotation_w
--   FROM ar_vr_state.capsule_states cs
--   LEFT JOIN ar_vr_state.spatial_anchors sa ON cs.anchor_id = sa.anchor_id
--   WHERE cs.capsule_id = '<capsule-id>';
--
-- Get active environments for a user:
--   SELECT * FROM ar_vr_state.environments
--   WHERE user_id = '<user-id>' AND active = TRUE;
--
-- Get interaction history for a capsule:
--   SELECT * FROM ar_vr_state.interaction_history
--   WHERE capsule_id = '<capsule-id>'
--   ORDER BY timestamp DESC
--   LIMIT 100;
--
-- Search interaction data (JSONB):
--   SELECT * FROM ar_vr_state.interaction_history
--   WHERE interaction_data @> '{"gesture": "pinch"}'::jsonb;
