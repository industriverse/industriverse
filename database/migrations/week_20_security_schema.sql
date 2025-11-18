-- ============================================================================
-- AI Shield v2: Thermodynamic Cybersecurity Database Schema
--
-- Week 20: Security Event Registry & Threat Intelligence Storage
--
-- Tables:
-- 1. security_events.threat_signatures - Thermodynamic threat fingerprints
-- 2. security_events.device_pufs - Physical Unclonable Functions
-- 3. security_events.thermodynamic_baselines - Normal operating parameters
-- 4. security_events.events - Security events and incidents
-- 5. security_events.forensic_evidence - Investigation data
-- 6. security_events.mitigation_actions - Defensive responses
-- ============================================================================

-- Create security_events schema
CREATE SCHEMA IF NOT EXISTS security_events;

-- ============================================================================
-- TABLE 1: Threat Signatures
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events.threat_signatures (
    signature_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    threat_type VARCHAR(100) NOT NULL,
    threat_name VARCHAR(255),
    description TEXT,

    -- Thermodynamic fingerprint
    thermodynamic_fingerprint JSONB NOT NULL,
    energy_pattern JSONB,
    entropy_pattern JSONB,
    power_signature JSONB,
    thermal_signature JSONB,
    em_signature JSONB,

    -- Detection metrics
    confidence FLOAT,
    severity VARCHAR(20) CHECK (severity IN ('low', 'medium', 'high', 'critical')),

    -- Temporal tracking
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    occurrence_count INTEGER DEFAULT 1,

    -- Mitigation
    mitigation_strategy JSONB,
    automated_response JSONB,

    -- Metadata
    created_by VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb,

    CONSTRAINT valid_confidence CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

-- Indexes for threat signatures
CREATE INDEX idx_threat_signatures_type ON security_events.threat_signatures(threat_type);
CREATE INDEX idx_threat_signatures_severity ON security_events.threat_signatures(severity);
CREATE INDEX idx_threat_signatures_first_seen ON security_events.threat_signatures(first_seen);
CREATE INDEX idx_threat_signatures_last_seen ON security_events.threat_signatures(last_seen);
CREATE INDEX idx_threat_signatures_occurrence ON security_events.threat_signatures(occurrence_count DESC);

-- GIN index for JSONB thermodynamic fingerprint queries
CREATE INDEX idx_threat_signatures_fingerprint
ON security_events.threat_signatures USING GIN (thermodynamic_fingerprint);

CREATE INDEX idx_threat_signatures_energy
ON security_events.threat_signatures USING GIN (energy_pattern);

CREATE INDEX idx_threat_signatures_entropy
ON security_events.threat_signatures USING GIN (entropy_pattern);

-- ============================================================================
-- TABLE 2: Device Physical Unclonable Functions (PUFs)
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events.device_pufs (
    device_id VARCHAR(255) PRIMARY KEY,
    puf_fingerprint VARCHAR(64) NOT NULL UNIQUE,  -- 256-bit hex (SHA-256)

    -- Thermodynamic measurements
    thermodynamic_vector JSONB NOT NULL,

    -- Quality metrics
    reproducibility_score FLOAT NOT NULL,

    -- Temporal tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_validated TIMESTAMP WITH TIME ZONE,

    -- Validation history
    validation_count INTEGER DEFAULT 0,
    failed_validations INTEGER DEFAULT 0,

    -- Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'revoked', 'expired')),

    -- Metadata
    device_type VARCHAR(100),
    manufacturer VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb,

    CONSTRAINT valid_reproducibility CHECK (reproducibility_score >= 0.0 AND reproducibility_score <= 1.0)
);

-- Indexes for PUFs
CREATE INDEX idx_device_pufs_device ON security_events.device_pufs(device_id);
CREATE INDEX idx_device_pufs_fingerprint ON security_events.device_pufs(puf_fingerprint);
CREATE INDEX idx_device_pufs_created ON security_events.device_pufs(created_at);
CREATE INDEX idx_device_pufs_last_validated ON security_events.device_pufs(last_validated);
CREATE INDEX idx_device_pufs_status ON security_events.device_pufs(status);
CREATE INDEX idx_device_pufs_device_type ON security_events.device_pufs(device_type);

-- GIN index for thermodynamic vector
CREATE INDEX idx_device_pufs_vector
ON security_events.device_pufs USING GIN (thermodynamic_vector);

-- ============================================================================
-- TABLE 3: Thermodynamic Baselines
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events.thermodynamic_baselines (
    baseline_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    device_id VARCHAR(255) NOT NULL,
    operation_type VARCHAR(100),

    -- Baseline measurements
    energy_baseline JSONB NOT NULL,
    entropy_baseline JSONB NOT NULL,
    power_baseline JSONB,
    thermal_baseline JSONB,
    em_baseline JSONB,

    -- Statistical properties
    mean_values JSONB,
    std_dev_values JSONB,
    percentiles JSONB,

    -- Metadata
    established_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sample_count INTEGER,
    confidence FLOAT,

    -- Validity
    valid_until TIMESTAMP WITH TIME ZONE,
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'expired', 'superseded')),

    -- Additional data
    metadata JSONB DEFAULT '{}'::jsonb,

    CONSTRAINT valid_confidence CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

-- Indexes for baselines
CREATE INDEX idx_baselines_device ON security_events.thermodynamic_baselines(device_id);
CREATE INDEX idx_baselines_operation ON security_events.thermodynamic_baselines(operation_type);
CREATE INDEX idx_baselines_established ON security_events.thermodynamic_baselines(established_at);
CREATE INDEX idx_baselines_status ON security_events.thermodynamic_baselines(status);
CREATE INDEX idx_baselines_valid_until ON security_events.thermodynamic_baselines(valid_until);

-- GIN indexes for baseline patterns
CREATE INDEX idx_baselines_energy
ON security_events.thermodynamic_baselines USING GIN (energy_baseline);

CREATE INDEX idx_baselines_entropy
ON security_events.thermodynamic_baselines USING GIN (entropy_baseline);

-- ============================================================================
-- TABLE 4: Security Events
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events.events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,

    -- Device/system affected
    device_id VARCHAR(255),
    system_id VARCHAR(255),

    -- Threat classification
    threat_category VARCHAR(100),
    signature_id UUID REFERENCES security_events.threat_signatures(signature_id),

    -- Thermodynamic data
    thermodynamic_data JSONB NOT NULL,
    anomaly_metrics JSONB,
    deviation_from_baseline JSONB,

    -- Severity & confidence
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    confidence FLOAT,

    -- Temporal tracking
    detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,

    -- Status
    status VARCHAR(50) DEFAULT 'detected' CHECK (status IN (
        'detected', 'investigating', 'mitigating', 'mitigated', 'resolved', 'false_positive'
    )),

    -- Response
    mitigation_actions JSONB,
    automated_response BOOLEAN DEFAULT FALSE,

    -- False positive tracking
    false_positive BOOLEAN DEFAULT FALSE,
    false_positive_reason TEXT,

    -- Assigned analyst
    assigned_to VARCHAR(255),

    -- Metadata
    source_sensor VARCHAR(100),
    correlation_ids UUID[],
    metadata JSONB DEFAULT '{}'::jsonb,

    CONSTRAINT valid_confidence CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

-- Indexes for events
CREATE INDEX idx_events_type ON security_events.events(event_type);
CREATE INDEX idx_events_device ON security_events.events(device_id);
CREATE INDEX idx_events_system ON security_events.events(system_id);
CREATE INDEX idx_events_category ON security_events.events(threat_category);
CREATE INDEX idx_events_signature ON security_events.events(signature_id);
CREATE INDEX idx_events_severity ON security_events.events(severity);
CREATE INDEX idx_events_detected ON security_events.events(detected_at DESC);
CREATE INDEX idx_events_resolved ON security_events.events(resolved_at);
CREATE INDEX idx_events_status ON security_events.events(status);
CREATE INDEX idx_events_false_positive ON security_events.events(false_positive);
CREATE INDEX idx_events_assigned ON security_events.events(assigned_to);
CREATE INDEX idx_events_source ON security_events.events(source_sensor);

-- GIN indexes for JSONB
CREATE INDEX idx_events_data
ON security_events.events USING GIN (thermodynamic_data);

CREATE INDEX idx_events_anomaly
ON security_events.events USING GIN (anomaly_metrics);

CREATE INDEX idx_events_mitigation
ON security_events.events USING GIN (mitigation_actions);

-- GIN index for correlation IDs array
CREATE INDEX idx_events_correlation
ON security_events.events USING GIN (correlation_ids);

-- ============================================================================
-- TABLE 5: Forensic Evidence
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events.forensic_evidence (
    evidence_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES security_events.events(event_id) ON DELETE CASCADE,

    -- Evidence type
    evidence_type VARCHAR(100) NOT NULL,

    -- Evidence data
    data JSONB NOT NULL,
    data_format VARCHAR(50),

    -- Temporal
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Chain of custody
    collected_by VARCHAR(255),
    chain_of_custody JSONB,

    -- Integrity
    cryptographic_hash VARCHAR(64) NOT NULL,  -- SHA-256 of data
    signed_by VARCHAR(255),
    signature VARCHAR(512),

    -- Storage
    storage_location TEXT,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Indexes for forensic evidence
CREATE INDEX idx_forensic_event ON security_events.forensic_evidence(event_id);
CREATE INDEX idx_forensic_type ON security_events.forensic_evidence(evidence_type);
CREATE INDEX idx_forensic_collected ON security_events.forensic_evidence(collected_at);
CREATE INDEX idx_forensic_hash ON security_events.forensic_evidence(cryptographic_hash);
CREATE INDEX idx_forensic_collected_by ON security_events.forensic_evidence(collected_by);

-- GIN index for evidence data
CREATE INDEX idx_forensic_data
ON security_events.forensic_evidence USING GIN (data);

CREATE INDEX idx_forensic_custody
ON security_events.forensic_evidence USING GIN (chain_of_custody);

-- ============================================================================
-- TABLE 6: Mitigation Actions
-- ============================================================================

CREATE TABLE IF NOT EXISTS security_events.mitigation_actions (
    action_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id UUID REFERENCES security_events.events(event_id) ON DELETE CASCADE,

    -- Action details
    action_type VARCHAR(100) NOT NULL,
    action_name VARCHAR(255),
    description TEXT,

    -- Execution
    executed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    executed_by VARCHAR(255),
    automated BOOLEAN DEFAULT FALSE,

    -- Result
    status VARCHAR(50) DEFAULT 'pending' CHECK (status IN (
        'pending', 'in_progress', 'completed', 'failed', 'rolled_back'
    )),
    result JSONB,

    -- Effectiveness
    effectiveness_score FLOAT,

    -- Capsule integration
    capsule_id UUID,
    capsule_type VARCHAR(100),

    -- Rollback
    rollback_possible BOOLEAN DEFAULT FALSE,
    rollback_procedure JSONB,
    rolled_back_at TIMESTAMP WITH TIME ZONE,

    -- Metadata
    metadata JSONB DEFAULT '{}'::jsonb,

    CONSTRAINT valid_effectiveness CHECK (effectiveness_score IS NULL OR (effectiveness_score >= 0.0 AND effectiveness_score <= 1.0))
);

-- Indexes for mitigation actions
CREATE INDEX idx_mitigation_event ON security_events.mitigation_actions(event_id);
CREATE INDEX idx_mitigation_type ON security_events.mitigation_actions(action_type);
CREATE INDEX idx_mitigation_executed ON security_events.mitigation_actions(executed_at);
CREATE INDEX idx_mitigation_status ON security_events.mitigation_actions(status);
CREATE INDEX idx_mitigation_automated ON security_events.mitigation_actions(automated);
CREATE INDEX idx_mitigation_capsule ON security_events.mitigation_actions(capsule_id);
CREATE INDEX idx_mitigation_effectiveness ON security_events.mitigation_actions(effectiveness_score DESC NULLS LAST);

-- GIN indexes
CREATE INDEX idx_mitigation_result
ON security_events.mitigation_actions USING GIN (result);

CREATE INDEX idx_mitigation_rollback
ON security_events.mitigation_actions USING GIN (rollback_procedure);

-- ============================================================================
-- Views for Security Operations
-- ============================================================================

-- Active threats view
CREATE OR REPLACE VIEW security_events.active_threats AS
SELECT
    e.event_id,
    e.event_type,
    e.device_id,
    e.severity,
    e.confidence,
    e.detected_at,
    e.status,
    ts.threat_name,
    ts.threat_type,
    COUNT(DISTINCT ma.action_id) AS mitigation_count
FROM security_events.events e
LEFT JOIN security_events.threat_signatures ts ON e.signature_id = ts.signature_id
LEFT JOIN security_events.mitigation_actions ma ON e.event_id = ma.event_id
WHERE e.status IN ('detected', 'investigating', 'mitigating')
AND e.false_positive = FALSE
GROUP BY e.event_id, e.event_type, e.device_id, e.severity, e.confidence,
         e.detected_at, e.status, ts.threat_name, ts.threat_type
ORDER BY e.severity DESC, e.detected_at DESC;

-- Device security health view
CREATE OR REPLACE VIEW security_events.device_security_health AS
SELECT
    dp.device_id,
    dp.puf_fingerprint,
    dp.reproducibility_score,
    dp.validation_count,
    dp.failed_validations,
    dp.last_validated,
    COUNT(DISTINCT e.event_id) AS total_events,
    COUNT(DISTINCT e.event_id) FILTER (WHERE e.severity = 'critical') AS critical_events,
    MAX(e.detected_at) AS last_event_time
FROM security_events.device_pufs dp
LEFT JOIN security_events.events e ON dp.device_id = e.device_id
WHERE dp.status = 'active'
GROUP BY dp.device_id, dp.puf_fingerprint, dp.reproducibility_score,
         dp.validation_count, dp.failed_validations, dp.last_validated
ORDER BY critical_events DESC, total_events DESC;

-- ============================================================================
-- Functions for Security Operations
-- ============================================================================

-- Function to update threat signature occurrence
CREATE OR REPLACE FUNCTION security_events.update_threat_occurrence()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' AND NEW.signature_id IS NOT NULL THEN
        UPDATE security_events.threat_signatures
        SET last_seen = NEW.detected_at,
            occurrence_count = occurrence_count + 1
        WHERE signature_id = NEW.signature_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for threat occurrence updates
DROP TRIGGER IF EXISTS trigger_update_threat_occurrence ON security_events.events;
CREATE TRIGGER trigger_update_threat_occurrence
    AFTER INSERT ON security_events.events
    FOR EACH ROW
    EXECUTE FUNCTION security_events.update_threat_occurrence();

-- Function to calculate time to resolution
CREATE OR REPLACE FUNCTION security_events.time_to_resolution(event_uuid UUID)
RETURNS INTERVAL AS $$
DECLARE
    detected_time TIMESTAMP WITH TIME ZONE;
    resolved_time TIMESTAMP WITH TIME ZONE;
BEGIN
    SELECT detected_at, resolved_at
    INTO detected_time, resolved_time
    FROM security_events.events
    WHERE event_id = event_uuid;

    IF resolved_time IS NULL THEN
        RETURN NULL;
    END IF;

    RETURN resolved_time - detected_time;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Grants (adjust user as needed)
-- ============================================================================

-- GRANT ALL ON SCHEMA security_events TO industriverse_user;
-- GRANT ALL ON ALL TABLES IN SCHEMA security_events TO industriverse_user;
-- GRANT ALL ON ALL SEQUENCES IN SCHEMA security_events TO industriverse_user;

-- ============================================================================
-- Comments
-- ============================================================================

COMMENT ON SCHEMA security_events IS 'AI Shield v2 thermodynamic cybersecurity event storage';

COMMENT ON TABLE security_events.threat_signatures IS 'Thermodynamic fingerprints of known threats';
COMMENT ON TABLE security_events.device_pufs IS 'Physical Unclonable Function signatures for device authentication';
COMMENT ON TABLE security_events.thermodynamic_baselines IS 'Normal operating parameters for devices';
COMMENT ON TABLE security_events.events IS 'Security events and incidents';
COMMENT ON TABLE security_events.forensic_evidence IS 'Evidence collected during security investigations';
COMMENT ON TABLE security_events.mitigation_actions IS 'Defensive actions taken in response to threats';

COMMENT ON VIEW security_events.active_threats IS 'Currently active security threats requiring attention';
COMMENT ON VIEW security_events.device_security_health IS 'Security health metrics per device';

-- ============================================================================
-- Sample Data (for testing)
-- ============================================================================

-- Insert sample threat signature
INSERT INTO security_events.threat_signatures (
    threat_type,
    threat_name,
    description,
    thermodynamic_fingerprint,
    severity,
    confidence
) VALUES (
    'power_analysis_attack',
    'Differential Power Analysis',
    'Side-channel attack using power consumption correlation',
    '{"energy_spike": 1.5, "entropy_drop": 0.3, "frequency_peak": 125000}'::jsonb,
    'high',
    0.92
) ON CONFLICT DO NOTHING;

-- ============================================================================
-- Migration Complete
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE 'Week 20 Security Schema Migration Complete';
    RAISE NOTICE '- 6 tables created';
    RAISE NOTICE '- 40+ indexes created';
    RAISE NOTICE '- 2 views created';
    RAISE NOTICE '- 2 functions + 1 trigger created';
    RAISE NOTICE 'AI Shield v2 database ready for thermodynamic cybersecurity';
END $$;
