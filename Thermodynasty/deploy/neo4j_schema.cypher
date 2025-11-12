// neo4j_schema.cypher
// Neo4j Database Schema for Industriverse Phase 4-5
// Energy Atlas, NVP, Shadow Twin Consensus, and ProofEconomy

// ============================================
// CONSTRAINTS (Ensure Data Integrity)
// ============================================

// Energy Domain Constraints
CREATE CONSTRAINT energy_domain_id_unique IF NOT EXISTS
FOR (d:EnergyDomain) REQUIRE d.domain_id IS UNIQUE;

CREATE CONSTRAINT energy_domain_name_unique IF NOT EXISTS
FOR (d:EnergyDomain) REQUIRE d.name IS UNIQUE;

// Energy Map Constraints
CREATE CONSTRAINT energy_map_id_unique IF NOT EXISTS
FOR (m:EnergyMap) REQUIRE m.map_id IS UNIQUE;

// Energy Snapshot Constraints
CREATE CONSTRAINT energy_snapshot_id_unique IF NOT EXISTS
FOR (s:EnergySnapshot) REQUIRE s.snapshot_id IS UNIQUE;

// Energy Vector Constraints
CREATE CONSTRAINT energy_vector_id_unique IF NOT EXISTS
FOR (v:EnergyVector) REQUIRE v.vector_id IS UNIQUE;

// Regime Transition Constraints
CREATE CONSTRAINT regime_id_unique IF NOT EXISTS
FOR (r:RegimeTransition) REQUIRE r.regime_id IS UNIQUE;

// Model Unit Constraints
CREATE CONSTRAINT model_unit_id_unique IF NOT EXISTS
FOR (m:ModelUnit) REQUIRE m.model_id IS UNIQUE;

// Hypothesis Constraints
CREATE CONSTRAINT hypothesis_hash_unique IF NOT EXISTS
FOR (h:Hypothesis) REQUIRE h.rnd1_hash IS UNIQUE;

// Service Constraints
CREATE CONSTRAINT service_id_unique IF NOT EXISTS
FOR (s:Service) REQUIRE s.service_id IS UNIQUE;

// Proof Constraints
CREATE CONSTRAINT proof_hash_unique IF NOT EXISTS
FOR (p:Proof) REQUIRE p.proof_hash IS UNIQUE;

// Shadow Twin Constraints
CREATE CONSTRAINT shadow_twin_id_unique IF NOT EXISTS
FOR (t:ShadowTwin) REQUIRE t.twin_id IS UNIQUE;

// Consensus Proposal Constraints
CREATE CONSTRAINT proposal_id_unique IF NOT EXISTS
FOR (p:ConsensusProposal) REQUIRE p.proposal_id IS UNIQUE;

// ============================================
// INDICES (Optimize Query Performance)
// ============================================

// Energy Domain Indices
CREATE INDEX energy_domain_name_idx IF NOT EXISTS FOR (d:EnergyDomain) ON (d.name);

// Energy Map Indices
CREATE INDEX energy_map_domain_idx IF NOT EXISTS FOR (m:EnergyMap) ON (m.domain_id);
CREATE INDEX energy_map_timestamp_idx IF NOT EXISTS FOR (m:EnergyMap) ON (m.created_at);

// Energy Snapshot Indices
CREATE INDEX energy_snapshot_map_idx IF NOT EXISTS FOR (s:EnergySnapshot) ON (s.map_id);
CREATE INDEX energy_snapshot_timestamp_idx IF NOT EXISTS FOR (s:EnergySnapshot) ON (s.timestamp);

// Energy Vector Indices
CREATE INDEX energy_vector_map_idx IF NOT EXISTS FOR (v:EnergyVector) ON (v.map_id);
CREATE INDEX energy_vector_coords_idx IF NOT EXISTS FOR (v:EnergyVector) ON (v.coords);

// Regime Transition Indices
CREATE INDEX regime_timestamp_idx IF NOT EXISTS FOR (r:RegimeTransition) ON (r.start_time);
CREATE INDEX regime_domain_idx IF NOT EXISTS FOR (r:RegimeTransition) ON (r.domain);

// Hypothesis Indices
CREATE INDEX hypothesis_domain_idx IF NOT EXISTS FOR (h:Hypothesis) ON (h.energy_map_utid);
CREATE INDEX hypothesis_timestamp_idx IF NOT EXISTS FOR (h:Hypothesis) ON (h.created_at);

// Proof Indices
CREATE INDEX proof_hypothesis_idx IF NOT EXISTS FOR (p:Proof) ON (p.hypothesis_rnd1_hash);
CREATE INDEX proof_timestamp_idx IF NOT EXISTS FOR (p:Proof) ON (p.minted_at);

// Consensus Proposal Indices
CREATE INDEX proposal_timestamp_idx IF NOT EXISTS FOR (p:ConsensusProposal) ON (p.created_at);
CREATE INDEX proposal_status_idx IF NOT EXISTS FOR (p:ConsensusProposal) ON (p.status);

// ============================================
// NODE SCHEMAS (Property Definitions)
// ============================================

// Energy Domain Node
// Represents a physics domain (plasma_physics, fluid_dynamics, etc.)
// Properties:
//   - domain_id: Unique identifier (UUID)
//   - name: Domain name (e.g., 'plasma_physics')
//   - description: Domain description
//   - resolution: Default map resolution (e.g., [256, 256])
//   - created_at: Timestamp

// Energy Map Node
// Represents a single energy map (2D array)
// Properties:
//   - map_id: Unique identifier (UUID)
//   - domain_id: Reference to parent domain
//   - scale: Resolution (64, 128, or 256)
//   - energy_mean: Mean energy value
//   - energy_var: Energy variance
//   - entropy: Shannon entropy of map
//   - created_at: Timestamp
//   - s3_key: S3 storage location

// Energy Snapshot Node
// Represents a temporal snapshot of an energy map
// Properties:
//   - snapshot_id: Unique identifier (UUID)
//   - map_id: Reference to parent map
//   - timestamp: Snapshot time
//   - energy_mean: Mean energy at snapshot
//   - energy_var: Variance at snapshot
//   - entropy: Entropy at snapshot
//   - regime: Current regime label
//   - confidence: Regime detection confidence

// Energy Vector Node
// Represents a single cell in an energy map with rich features
// Properties:
//   - vector_id: Unique identifier (format: map_id:x:y)
//   - map_id: Parent map reference
//   - coords: [x, y] coordinates
//   - E: Energy value
//   - grad_x: Energy gradient in x direction
//   - grad_y: Energy gradient in y direction
//   - laplacian: Laplacian (curvature)
//   - local_entropy: Local neighborhood entropy
//   - temporal_trend: Change over time
//   - regime_score: Regime probability distribution

// Regime Transition Node
// Represents a detected regime change
// Properties:
//   - regime_id: Unique identifier (UUID)
//   - domain: Domain name
//   - regime_from: Previous regime label
//   - regime_to: New regime label
//   - start_time: Transition start
//   - end_time: Transition end (if completed)
//   - stability_score: Stability metric
//   - energy_delta: Energy change during transition

// Model Unit Node
// Represents a trained NVP model
// Properties:
//   - model_id: Unique identifier (UUID)
//   - architecture: Model architecture description (JSON)
//   - fitness: Thermodynamic fitness score
//   - accuracy: Prediction accuracy
//   - energy_efficiency: Energy per prediction (joules)
//   - generation: DGM generation number
//   - parent_ids: List of parent model IDs (for lineage)
//   - created_at: Training completion timestamp
//   - s3_weights: S3 location of model weights

// Hypothesis Node
// Represents a scientific hypothesis submitted by user/ACE
// Properties:
//   - rnd1_hash: Unique hypothesis hash (SHA256)
//   - content: Hypothesis text
//   - dataset_id: Associated dataset
//   - energy_map_utid: Target energy map
//   - created_by: User or agent ID
//   - created_at: Submission timestamp
//   - s3_key: S3 storage location
//   - energy_prediction_mean: Predicted energy consumption
//   - energy_prediction_std: Prediction uncertainty
//   - regime: Assigned regime
//   - confidence: Assignment confidence

// Service Node
// Represents a computational service in the registry
// Properties:
//   - service_id: Unique identifier
//   - name: Service name
//   - type: Service type (compute, storage, etc.)
//   - endpoint: Service URL/endpoint
//   - cloud_provider: AWS, Azure, GCP
//   - region: Cloud region
//   - energy_cost: Estimated energy cost per invocation
//   - reliability: Historical reliability score
//   - capabilities: List of capabilities (JSON)

// Proof Node
// Represents a validated proof eligible for PoE token
// Properties:
//   - proof_hash: Unique proof identifier (SHA256)
//   - hypothesis_rnd1_hash: Source hypothesis
//   - validation_status: Status (pending, validated, rejected)
//   - energy_predicted: NVP predicted energy
//   - energy_observed: Actual observed energy
//   - energy_fidelity: Prediction accuracy
//   - consensus_votes: Number of Shadow Twin votes
//   - confidence: Validation confidence
//   - pft_amount: ProofToken amount minted
//   - minted_at: Token mint timestamp

// Shadow Twin Node
// Represents a Shadow Twin validator instance
// Properties:
//   - twin_id: Unique identifier (UUID)
//   - model_version: NVP model version
//   - status: Status (active, inactive, faulty)
//   - vote_count: Total votes cast
//   - agreement_rate: % of votes matching consensus
//   - last_active: Last activity timestamp

// Consensus Proposal Node
// Represents a BFT consensus proposal
// Properties:
//   - proposal_id: Unique identifier (UUID)
//   - leader_twin_id: Proposing Shadow Twin
//   - energy_predicted: Proposed energy value
//   - confidence: Proposal confidence
//   - status: Status (proposed, committed, rejected, timeout)
//   - votes_accept: Count of ACCEPT votes
//   - votes_reject: Count of REJECT votes
//   - created_at: Proposal timestamp
//   - committed_at: Commit timestamp (if committed)

// ============================================
// RELATIONSHIP SCHEMAS
// ============================================

// Energy Atlas Relationships
// (EnergyDomain)-[:HAS_MAP]->(EnergyMap)
// (EnergyMap)-[:HAS_SNAPSHOT]->(EnergySnapshot)
// (EnergySnapshot)-[:HAS_VECTOR]->(EnergyVector)
// (EnergyVector)-[:LOCATED_IN]->(EnergyMap)

// Regime Relationships
// (EnergySnapshot)-[:DETECTED_REGIME]->(RegimeTransition)
// (RegimeTransition)-[:IN_DOMAIN]->(EnergyDomain)

// Model Lineage Relationships
// (ModelUnit)-[:PARENT_OF]->(ModelUnit)  // DGM evolution lineage
// (ModelUnit)-[:TRAINED_ON]->(EnergySnapshot)
// (ModelUnit)-[:PREDICTS]->(EnergyDomain)

// Hypothesis Relationships
// (Hypothesis)-[:TARGETS_DOMAIN]->(EnergyDomain)
// (Hypothesis)-[:USES_SERVICE]->(Service)
// (Hypothesis)-[:DEPENDS_ON]->(Hypothesis)  // DAG dependencies

// Proof Relationships
// (Proof)-[:VALIDATES]->(Hypothesis)
// (Proof)-[:CONSENSUS_BY]->(ShadowTwin)

// Consensus Relationships
// (ConsensusProposal)-[:PROPOSED_BY]->(ShadowTwin)
// (ShadowTwin)-[:VOTED_ON]->(ConsensusProposal)
//   Properties: vote (ACCEPT/REJECT), timestamp
// (ConsensusProposal)-[:RESULTED_IN]->(Proof)

// ============================================
// SAMPLE QUERIES (For Reference)
// ============================================

// Query 1: Get all energy snapshots for a domain in time range
// MATCH (d:EnergyDomain {name: 'plasma_physics'})-[:HAS_MAP]->(m:EnergyMap)-[:HAS_SNAPSHOT]->(s:EnergySnapshot)
// WHERE s.timestamp >= $start_time AND s.timestamp <= $end_time
// RETURN s
// ORDER BY s.timestamp ASC;

// Query 2: Find regime transitions with high energy delta
// MATCH (r:RegimeTransition)
// WHERE r.energy_delta > $threshold
// RETURN r.domain, r.regime_from, r.regime_to, r.energy_delta
// ORDER BY r.energy_delta DESC;

// Query 3: Get model lineage (parents and children)
// MATCH path = (parent:ModelUnit)-[:PARENT_OF*]->(child:ModelUnit)
// WHERE child.model_id = $target_model_id
// RETURN path;

// Query 4: Find hypotheses with high prediction accuracy
// MATCH (h:Hypothesis)<-[:VALIDATES]-(p:Proof)
// WHERE p.energy_fidelity > 0.9
// RETURN h.rnd1_hash, h.content, p.energy_fidelity
// ORDER BY p.energy_fidelity DESC;

// Query 5: Get Shadow Twin consensus statistics
// MATCH (t:ShadowTwin)-[v:VOTED_ON]->(p:ConsensusProposal)
// WHERE t.twin_id = $twin_id
// RETURN t.twin_id, t.agreement_rate, COUNT(v) AS total_votes;

// ============================================
// INITIALIZATION DATA (Optional Seed Data)
// ============================================

// Create default Energy Domains
CREATE (d1:EnergyDomain {
    domain_id: 'domain_plasma_physics',
    name: 'plasma_physics',
    description: 'Plasma physics and fusion energy domains',
    resolution: [256, 256],
    created_at: datetime()
});

CREATE (d2:EnergyDomain {
    domain_id: 'domain_fluid_dynamics',
    name: 'fluid_dynamics',
    description: 'Fluid dynamics and flow simulations',
    resolution: [256, 256],
    created_at: datetime()
});

CREATE (d3:EnergyDomain {
    domain_id: 'domain_astrophysics',
    name: 'astrophysics',
    description: 'Astrophysical simulations',
    resolution: [256, 256],
    created_at: datetime()
});

CREATE (d4:EnergyDomain {
    domain_id: 'domain_turbulent_radiative_layer',
    name: 'turbulent_radiative_layer',
    description: 'Turbulent radiative layer dynamics',
    resolution: [256, 256],
    created_at: datetime()
});

CREATE (d5:EnergyDomain {
    domain_id: 'domain_active_matter',
    name: 'active_matter',
    description: 'Active matter and self-organizing systems',
    resolution: [256, 256],
    created_at: datetime()
});

// Create Shadow Twins (3 initial instances for f=1 BFT)
CREATE (t1:ShadowTwin {
    twin_id: 'shadow_twin_1',
    model_version: 'nvp_v0.1',
    status: 'active',
    vote_count: 0,
    agreement_rate: 1.0,
    last_active: datetime()
});

CREATE (t2:ShadowTwin {
    twin_id: 'shadow_twin_2',
    model_version: 'nvp_v0.1',
    status: 'active',
    vote_count: 0,
    agreement_rate: 1.0,
    last_active: datetime()
});

CREATE (t3:ShadowTwin {
    twin_id: 'shadow_twin_3',
    model_version: 'nvp_v0.1',
    status: 'active',
    vote_count: 0,
    agreement_rate: 1.0,
    last_active: datetime()
});

// ============================================
// END OF SCHEMA
// ============================================
