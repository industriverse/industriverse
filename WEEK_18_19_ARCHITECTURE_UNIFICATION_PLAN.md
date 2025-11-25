# Week 18-19: Architecture Unification Plan

## Executive Summary

**Objective:** Unify the architecture by:
1. Consolidating AR/VR module integration in UI/UX Layer
2. Unifying DAC Factory implementations (Deployment Ops + Application Layer)
3. Connecting Overseer System to all framework layers
4. Creating bidirectional integration between all components

**Timeline:** 10 days
**Complexity:** High - involves cross-layer integration and protocol bridges

---

## Current Architecture State (Post-Week 17)

### ✅ Completed Foundation (Week 17)
- **Database:** Unified PostgreSQL schema with 5 schemas (behavioral, capsules, overseer, security, analytics)
- **Behavioral Tracking:** API bridge connecting backend to potential frontends via FastAPI
- **A2A Protocol:** Complete task execution engine with priority queue
- **DTSL:** Schema validation for twin/swarm definitions
- **Error Handling:** All 40 bare except clauses fixed with specific exception types

### 🔄 Components Requiring Unification

#### 1. AR/VR Modules
**Current Location:** `src/ui_ux_layer/edge/ar_vr_integration/`
**Status:** Properly positioned in UI/UX Layer, but isolated
**Files:**
- `ar_vr_integration.py` (ARVRIntegrationManager)
- `mobile_voice_ar_panels.py` (AR panel management)

**Integration Gaps:**
- ❌ Not connected to Overseer System for capsule orchestration
- ❌ No data layer integration for AR/VR state persistence
- ❌ Missing protocol layer bridges (MCP/A2A for AR/VR commands)
- ❌ No connection to capsule framework for AR capsule rendering

#### 2. DAC Factory (Dual Implementation)
**Current State:** Split across two layers with different purposes

**Implementation A - Deployment Operations Layer:**
- **Location:** `src/deployment_operations_layer/agent/capsule_instantiator/capsule_factory.py`
- **Purpose:** Infrastructure-level capsule instantiation
- **Features:**
  - Creates from blueprints + manifests + deployment context
  - Handles resources, networking, security, protocols
  - Full deployment configuration (scaling, trust zones, crypto zones)
- **LOC:** 472 lines

**Implementation B - Application Layer:**
- **Location:** `src/application_layer/agent_capsule_factory.py`
- **Purpose:** Business logic-level capsule creation
- **Features:**
  - Template-based capsule creation (Dashboard, Digital Twin, Workflow, Analytics)
  - Registry management and searching
  - Simpler interface for application developers
- **LOC:** 526 lines

**Integration Gaps:**
- ❌ No coordination between the two factories
- ❌ Different capsule creation flows lead to inconsistencies
- ❌ No shared capsule registry
- ❌ Missing unified capsule lifecycle management

#### 3. Overseer System
**Current Location:** `src/overseer_system/` (22 subdirectories, 110 Python files)
**Status:** Comprehensive but isolated - acts as standalone control plane

**Capabilities:**
- **Integration Managers:** For all 8 framework layers
- **Capsule Evolution & Governance:** 17 files for capsule lifecycle
- **Intelligence Market:** Multi-agent coordination (7 files)
- **Digital Twin Diplomacy:** Twin negotiation (6 files)
- **Protocol Bridges:** MCP and A2A integration managers
- **Event Bus:** Kafka-based event-driven communication
- **Trust Management:** 7 files for trust and reputation
- **Strategic Simulation:** Advanced scenario orchestration
- **API Gateway:** Service routing and management
- **UI Components:** React-based dashboard and visualization

**Integration Gaps:**
- ❌ Integration managers exist but not actively used by other layers
- ❌ No bidirectional communication with AR/VR modules
- ❌ DAC Factory implementations don't consult Overseer for governance
- ❌ Event bus not connected to behavioral tracking or task execution
- ❌ Capsule evolution not integrated with existing capsule frameworks

---

## Week 18-19 Unification Strategy

### Phase 1: DAC Factory Unification (Days 1-4)

#### Goal
Create a **Unified Capsule Lifecycle Architecture** where:
- Application Layer factory handles high-level business logic (templates, user-facing)
- Deployment Operations Layer factory handles low-level infrastructure (blueprints, deployment)
- Overseer System orchestrates the entire lifecycle (evolution, governance, coordination)

#### Deliverables

**Day 1: Create Capsule Lifecycle Coordinator in Overseer System**

**File:** `src/overseer_system/capsule_lifecycle/capsule_lifecycle_coordinator.py`

```python
"""
Capsule Lifecycle Coordinator

Orchestrates capsule creation across Application Layer (templates) and
Deployment Operations Layer (infrastructure), ensuring governance and evolution.
"""

class CapsuleLifecycleCoordinator:
    """
    Coordinates capsule lifecycle across all layers.

    Flow:
    1. Application Layer creates high-level capsule request (template-based)
    2. Coordinator validates against governance policies
    3. Coordinator enriches with evolution metadata
    4. Deployment Operations Layer instantiates infrastructure
    5. Coordinator registers in unified capsule registry
    6. Coordinator initiates monitoring and evolution tracking
    """

    def __init__(self):
        self.app_factory = None  # Application Layer factory
        self.deploy_factory = None  # Deployment Ops factory
        self.governance_service = None  # Capsule governance
        self.evolution_service = None  # Capsule evolution
        self.registry = {}  # Unified capsule registry

    async def create_capsule_full_lifecycle(
        self,
        template_id: str,
        instance_config: Dict[str, Any],
        deployment_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Complete capsule creation with governance and evolution.

        Steps:
        1. Create application-level instance (AgentCapsuleFactory)
        2. Apply governance policies (CapsuleGovernanceService)
        3. Generate blueprint from template
        4. Create deployment instance (CapsuleFactory)
        5. Register in unified registry
        6. Initialize evolution tracking
        7. Publish lifecycle events to event bus
        """
        pass
```

**Day 2: Integrate Application Layer Factory with Coordinator**

**Modify:** `src/application_layer/agent_capsule_factory.py`

Add coordinator integration:
```python
class AgentCapsuleFactory:
    def __init__(self, agent_core, lifecycle_coordinator=None):
        self.agent_core = agent_core
        self.lifecycle_coordinator = lifecycle_coordinator  # NEW

        # Register with coordinator if available
        if self.lifecycle_coordinator:
            self.lifecycle_coordinator.register_app_factory(self)

    async def create_capsule_instance(
        self,
        template_id: str,
        instance_config: Dict[str, Any],
        use_coordinator: bool = True  # NEW
    ) -> Dict[str, Any]:
        """
        Create capsule instance, optionally using lifecycle coordinator.
        """
        if use_coordinator and self.lifecycle_coordinator:
            # Use full lifecycle management
            return await self.lifecycle_coordinator.create_capsule_full_lifecycle(
                template_id=template_id,
                instance_config=instance_config,
                deployment_context=instance_config.get("deployment", {})
            )
        else:
            # Direct creation (backward compatibility)
            return self._create_instance_direct(template_id, instance_config)
```

**Day 3: Integrate Deployment Operations Factory with Coordinator**

**Modify:** `src/deployment_operations_layer/agent/capsule_instantiator/capsule_factory.py`

Add coordinator integration and registry:
```python
class CapsuleFactory:
    def __init__(self, lifecycle_coordinator=None):
        self.lifecycle_coordinator = lifecycle_coordinator  # NEW

        # Register with coordinator if available
        if self.lifecycle_coordinator:
            self.lifecycle_coordinator.register_deploy_factory(self)

    def create_capsule(
        self,
        blueprint: Dict[str, Any],
        manifest: Dict[str, Any],
        context: Dict[str, Any],
        governance_metadata: Dict[str, Any] = None  # NEW
    ) -> Dict[str, Any]:
        """
        Create capsule with optional governance metadata from coordinator.
        """
        # Existing creation logic...

        # NEW: Apply governance metadata if provided
        if governance_metadata:
            capsule["governance"] = governance_metadata

        # NEW: Register with coordinator
        if self.lifecycle_coordinator:
            self.lifecycle_coordinator.register_capsule_instance(capsule)

        return capsule
```

**Day 4: Create Unified Capsule Registry**

**File:** `src/overseer_system/capsule_lifecycle/unified_capsule_registry.py`

```python
"""
Unified Capsule Registry

Central registry for all capsules created across Application Layer and
Deployment Operations Layer, providing unified search, tracking, and lifecycle management.
"""

class UnifiedCapsuleRegistry:
    """
    Registry tracking all capsules regardless of creation source.

    Features:
    - Unified search across all capsules
    - Lifecycle state tracking
    - Parent-child capsule relationships
    - Evolution lineage tracking
    - Governance status monitoring
    """

    def __init__(self, database_pool):
        self.db_pool = database_pool  # PostgreSQL connection
        self.cache = {}  # In-memory cache

    async def register_capsule(
        self,
        capsule_id: str,
        capsule_data: Dict[str, Any],
        source: str  # "application_layer" or "deployment_ops_layer"
    ):
        """
        Register capsule in unified registry.

        Stores in database schema: capsules.unified_registry
        """
        pass

    async def search_capsules(
        self,
        filters: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Search capsules across all sources.
        """
        pass

    async def get_capsule_lineage(
        self,
        capsule_id: str
    ) -> Dict[str, Any]:
        """
        Get complete evolution lineage for a capsule.
        """
        pass
```

**Database Migration:**
```sql
-- Add to database/schema/unified_schema.sql

CREATE TABLE IF NOT EXISTS capsules.unified_registry (
    capsule_id UUID PRIMARY KEY,
    source VARCHAR(50) NOT NULL, -- 'application_layer' or 'deployment_ops_layer'
    template_id VARCHAR(255),
    blueprint_id VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) DEFAULT 'active',
    governance_status VARCHAR(50) DEFAULT 'pending',
    evolution_generation INTEGER DEFAULT 1,
    parent_capsule_id UUID REFERENCES capsules.unified_registry(capsule_id),
    capsule_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE INDEX idx_unified_registry_source ON capsules.unified_registry(source);
CREATE INDEX idx_unified_registry_template ON capsules.unified_registry(template_id);
CREATE INDEX idx_unified_registry_blueprint ON capsules.unified_registry(blueprint_id);
CREATE INDEX idx_unified_registry_status ON capsules.unified_registry(status);
CREATE INDEX idx_unified_registry_data ON capsules.unified_registry USING gin(capsule_data);
```

---

### Phase 2: AR/VR Integration (Days 5-7)

#### Goal
Connect AR/VR modules to the unified architecture:
- Overseer System for capsule orchestration in AR/VR
- Data Layer for AR/VR state persistence
- Protocol Layer for AR/VR command processing
- Capsule Framework for AR capsule rendering

#### Deliverables

**Day 5: Create AR/VR Integration Adapter in Overseer System**

**File:** `src/overseer_system/integration/ar_vr_integration_adapter.py`

```python
"""
AR/VR Integration Adapter

Connects Overseer System to UI/UX Layer AR/VR modules for:
- Capsule orchestration in AR/VR environments
- Spatial data synchronization
- AR/VR command processing
- User interaction tracking
"""

class ARVRIntegrationAdapter:
    """
    Bidirectional bridge between Overseer and AR/VR modules.
    """

    def __init__(self, overseer_event_bus, ar_vr_manager):
        self.event_bus = overseer_event_bus
        self.ar_vr_manager = ar_vr_manager
        self.capsule_coordinator = None

    async def orchestrate_ar_capsule_spawn(
        self,
        capsule_id: str,
        ar_environment: Dict[str, Any],
        spatial_anchor: Dict[str, Any]
    ):
        """
        Orchestrate capsule spawning in AR environment.

        Flow:
        1. Request capsule from unified registry
        2. Adapt capsule data for AR rendering
        3. Determine spatial placement using spatial_awareness_engine
        4. Send spawn command to ar_vr_manager
        5. Track spawn event in behavioral tracking
        """
        pass

    async def handle_ar_interaction_event(
        self,
        event: Dict[str, Any]
    ):
        """
        Handle AR interaction events (gaze, hand tracking, voice).

        Flow:
        1. Receive AR interaction from ar_vr_manager
        2. Translate to capsule command
        3. Send to task execution engine (A2A)
        4. Track in behavioral system
        5. Update AR visualization
        """
        pass
```

**Day 6: Add AR/VR State Persistence to Data Layer**

**File:** `src/data_layer/src/ar_vr_state/ar_vr_state_manager.py`

```python
"""
AR/VR State Manager

Persists AR/VR state to Data Layer:
- Spatial anchors
- AR environment configurations
- User AR interaction history
- AR capsule placement and state
"""

class ARVRStateManager:
    """
    Manages AR/VR state persistence.
    """

    def __init__(self, database_pool):
        self.db_pool = database_pool

    async def save_spatial_anchor(
        self,
        anchor_id: str,
        position: Dict[str, float],
        rotation: Dict[str, float],
        environment_id: str,
        metadata: Dict[str, Any]
    ):
        """
        Save spatial anchor to database.

        Table: ar_vr_state.spatial_anchors
        """
        pass

    async def save_ar_capsule_state(
        self,
        capsule_id: str,
        ar_state: Dict[str, Any]
    ):
        """
        Save AR capsule state (position, scale, interaction state).

        Table: ar_vr_state.capsule_states
        """
        pass
```

**Database Migration:**
```sql
-- Add AR/VR state schema

CREATE SCHEMA IF NOT EXISTS ar_vr_state;

CREATE TABLE IF NOT EXISTS ar_vr_state.spatial_anchors (
    anchor_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    environment_id VARCHAR(255) NOT NULL,
    position_x FLOAT NOT NULL,
    position_y FLOAT NOT NULL,
    position_z FLOAT NOT NULL,
    rotation_x FLOAT NOT NULL,
    rotation_y FLOAT NOT NULL,
    rotation_z FLOAT NOT NULL,
    rotation_w FLOAT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS ar_vr_state.capsule_states (
    capsule_id UUID PRIMARY KEY REFERENCES capsules.unified_registry(capsule_id),
    anchor_id UUID REFERENCES ar_vr_state.spatial_anchors(anchor_id),
    scale_x FLOAT DEFAULT 1.0,
    scale_y FLOAT DEFAULT 1.0,
    scale_z FLOAT DEFAULT 1.0,
    visible BOOLEAN DEFAULT true,
    interaction_state VARCHAR(50) DEFAULT 'idle',
    last_interaction_at TIMESTAMP WITH TIME ZONE,
    ar_metadata JSONB DEFAULT '{}'::jsonb
);
```

**Day 7: Integrate AR/VR with Capsule Framework**

**Modify:** `src/ui_ux_layer/core/capsule_framework/capsule_manager.py`

Add AR/VR rendering support:
```python
class CapsuleManager:
    def __init__(self, ar_vr_integration_adapter=None):
        # Existing init...
        self.ar_vr_adapter = ar_vr_integration_adapter  # NEW

    async def render_capsule_in_ar(
        self,
        capsule_id: str,
        ar_environment: Dict[str, Any],
        spatial_anchor: Dict[str, Any]
    ):
        """
        Render capsule in AR environment.

        Flow:
        1. Get capsule from unified registry
        2. Adapt capsule morphology for AR (using capsule_morphology_engine)
        3. Request AR spawn through ar_vr_adapter
        4. Track AR interaction state
        """
        if not self.ar_vr_adapter:
            raise RuntimeError("AR/VR adapter not configured")

        # Get capsule
        capsule = await self.get_capsule(capsule_id)

        # Adapt for AR rendering
        ar_capsule = self._adapt_capsule_for_ar(capsule, ar_environment)

        # Spawn in AR
        await self.ar_vr_adapter.orchestrate_ar_capsule_spawn(
            capsule_id=capsule_id,
            ar_environment=ar_environment,
            spatial_anchor=spatial_anchor
        )

        return {"status": "spawned", "capsule_id": capsule_id}
```

---

### Phase 3: Overseer System Integration (Days 8-10)

#### Goal
Connect Overseer System integration managers to all framework layers with bidirectional communication.

#### Deliverables

**Day 8: Activate Layer Integration Managers**

**Tasks:**
1. Review and update all 8 integration managers:
   - `application_layer_integration_manager.py`
   - `core_ai_layer_integration_manager.py`
   - `data_layer_integration_manager.py`
   - `generative_layer_integration_manager.py`
   - `protocol_layer_integration_manager.py`
   - `security_compliance_layer_integration_manager.py`
   - `ui_ux_layer_integration_manager.py`
   - `workflow_automation_layer_integration_manager.py`

2. Ensure each manager:
   - Subscribes to Overseer event bus
   - Publishes layer events to event bus
   - Implements bidirectional communication
   - Handles protocol translation (MCP/A2A)

**Example Enhancement:** `src/overseer_system/integration/application_layer_integration_manager.py`

```python
class ApplicationLayerIntegrationManager:
    def __init__(self, event_bus, capsule_coordinator):
        self.event_bus = event_bus
        self.capsule_coordinator = capsule_coordinator

        # Subscribe to application layer events
        self.event_bus.subscribe("application.capsule.created", self.handle_capsule_created)
        self.event_bus.subscribe("application.agent.request", self.handle_agent_request)

    async def handle_capsule_created(self, event: Dict[str, Any]):
        """
        Handle capsule creation events from Application Layer.

        Actions:
        1. Validate against governance policies
        2. Initiate evolution tracking
        3. Publish to intelligence market if applicable
        4. Notify other layers (UI/UX for rendering, Data for persistence)
        """
        capsule_id = event["capsule_id"]

        # Validate governance
        is_compliant = await self.capsule_coordinator.validate_governance(capsule_id)

        if is_compliant:
            # Publish to other layers
            await self.event_bus.publish("overseer.capsule.validated", {
                "capsule_id": capsule_id,
                "timestamp": time.time()
            })
        else:
            # Quarantine non-compliant capsule
            await self.event_bus.publish("overseer.capsule.quarantined", {
                "capsule_id": capsule_id,
                "reason": "governance_violation"
            })
```

**Day 9: Connect Event Bus to Week 17 Components**

**Task:** Integrate Overseer event bus with:
- Behavioral Tracking API (Week 17 Day 2)
- A2A Task Execution Engine (Week 17 Day 3)
- DTSL Schema Validator (Week 17 Day 4)

**File:** `src/overseer_system/event_bus/component_connectors.py`

```python
"""
Component Connectors

Connects Week 17 components to Overseer event bus.
"""

class BehavioralTrackingConnector:
    """
    Connects behavioral tracking to event bus.
    """

    def __init__(self, event_bus, behavioral_client):
        self.event_bus = event_bus
        self.behavioral_client = behavioral_client

        # Subscribe to behavioral events
        self.event_bus.subscribe("behavioral.interaction", self.handle_interaction)

    async def handle_interaction(self, event: Dict[str, Any]):
        """
        Handle interaction events from event bus and track in behavioral system.
        """
        await self.behavioral_client.track_interaction(event)


class A2ATaskExecutionConnector:
    """
    Connects A2A task execution to event bus.
    """

    def __init__(self, event_bus, task_engine):
        self.event_bus = event_bus
        self.task_engine = task_engine

        # Subscribe to task events
        self.event_bus.subscribe("task.submit", self.handle_task_submission)

    async def handle_task_submission(self, event: Dict[str, Any]):
        """
        Handle task submission from event bus.
        """
        task_context = self._create_task_context(event)
        await self.task_engine.submit_task(task_context)


class DTSLValidationConnector:
    """
    Connects DTSL validation to event bus.
    """

    def __init__(self, event_bus, schema_validator):
        self.event_bus = event_bus
        self.schema_validator = schema_validator

        # Subscribe to validation events
        self.event_bus.subscribe("dtsl.validate", self.handle_validation_request)

    async def handle_validation_request(self, event: Dict[str, Any]):
        """
        Handle DTSL validation requests from event bus.
        """
        definition = event["definition"]
        definition_type = event["type"]  # "twin" or "swarm"

        if definition_type == "twin":
            is_valid, errors = self.schema_validator.validate_twin_definition(definition)
        else:
            is_valid, errors = self.schema_validator.validate_swarm_definition(definition)

        # Publish result
        await self.event_bus.publish("dtsl.validation_result", {
            "is_valid": is_valid,
            "errors": errors,
            "definition_id": event.get("definition_id")
        })
```

**Day 10: Create Integration Tests and Documentation**

**Tests:** `tests/week18_19/test_architecture_unification.py`

```python
"""
Week 18-19 Architecture Unification Tests
"""

import pytest

class TestDACFactoryUnification:
    """Test unified capsule lifecycle."""

    @pytest.mark.asyncio
    async def test_full_capsule_lifecycle(self):
        """
        Test complete capsule lifecycle through coordinator.

        Steps:
        1. Create capsule via Application Layer factory
        2. Coordinator validates governance
        3. Deployment Ops factory creates infrastructure
        4. Capsule registered in unified registry
        5. Evolution tracking initiated
        """
        pass

class TestARVRIntegration:
    """Test AR/VR integration with Overseer."""

    @pytest.mark.asyncio
    async def test_ar_capsule_spawn(self):
        """
        Test AR capsule spawning through Overseer.
        """
        pass

class TestOverseerEventBus:
    """Test Overseer event bus connections."""

    @pytest.mark.asyncio
    async def test_behavioral_tracking_integration(self):
        """
        Test behavioral tracking through event bus.
        """
        pass
```

**Documentation:** `WEEK_18_19_SUMMARY.md`

---

## Success Criteria

### DAC Factory Unification ✅
- [ ] CapsuleLifecycleCoordinator operational in Overseer System
- [ ] Application Layer factory integrated with coordinator
- [ ] Deployment Ops factory integrated with coordinator
- [ ] Unified capsule registry stores all capsules
- [ ] Database schema extended with capsules.unified_registry table
- [ ] Governance policies applied to all capsule creation
- [ ] Evolution tracking initiated for all capsules

### AR/VR Integration ✅
- [ ] AR/VR Integration Adapter operational in Overseer
- [ ] AR/VR state persistence in Data Layer
- [ ] AR capsule spawning through unified architecture
- [ ] AR interactions tracked in behavioral system
- [ ] Spatial anchors persisted and synchronized
- [ ] Capsule framework supports AR rendering

### Overseer System Integration ✅
- [ ] All 8 layer integration managers activated
- [ ] Event bus connected to Week 17 components (behavioral, A2A, DTSL)
- [ ] Bidirectional communication established
- [ ] Protocol translation (MCP/A2A) operational
- [ ] Integration tests passing
- [ ] Documentation complete

### Overall Architecture ✅
- [ ] Single source of truth for capsule registry
- [ ] Event-driven communication across all layers
- [ ] Governance and evolution applied uniformly
- [ ] AR/VR fully integrated with capsule lifecycle
- [ ] Reduced code duplication
- [ ] Clear separation of concerns (business logic vs. infrastructure vs. orchestration)

---

## Architecture Diagram (Post-Week 18-19)

```
┌─────────────────────────────────────────────────────────────────┐
│                     OVERSEER SYSTEM (Control Plane)              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         Capsule Lifecycle Coordinator                   │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │    │
│  │  │ Governance   │  │ Evolution    │  │ Unified      │ │    │
│  │  │ Service      │  │ Service      │  │ Registry     │ │    │
│  │  └──────────────┘  └──────────────┘  └──────────────┘ │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         Layer Integration Managers (8 Managers)         │    │
│  │  App │ Core AI │ Data │ Gen │ Protocol │ Sec │ UI │ WF  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │         Event Bus (Kafka) + Protocol Bridges            │    │
│  │              MCP Bridge  │  A2A Bridge                  │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │    Intelligence Market │ Digital Twin Diplomacy │       │    │
│  │    Strategic Simulation │ Trust Management       │       │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                                 │
            ┌────────────────────┼────────────────────┐
            │                    │                    │
            ▼                    ▼                    ▼
┌───────────────────┐  ┌───────────────────┐  ┌──────────────────┐
│  APPLICATION      │  │  DEPLOYMENT OPS   │  │  UI/UX LAYER     │
│  LAYER            │  │  LAYER            │  │                  │
├───────────────────┤  ├───────────────────┤  ├──────────────────┤
│                   │  │                   │  │                  │
│ AgentCapsule      │  │ CapsuleFactory    │  │ AR/VR            │
│ Factory           │  │ (Infrastructure)  │  │ Integration      │
│ (Templates)       │  │                   │  │                  │
│      │            │  │      │            │  │      │           │
│      │            │  │      │            │  │      │           │
│      └────────────┼──┼──────┴────────────┼──┼──────┘           │
│                   │  │                   │  │                  │
│ Behavioral        │  │ Capsule           │  │ Capsule          │
│ Tracking API      │◄─┤ Instantiator      │  │ Framework        │
│      │            │  │                   │  │      │           │
│      │            │  │                   │  │      │           │
└──────┼────────────┘  └───────────────────┘  └──────┼───────────┘
       │                                              │
       │              ┌───────────────────┐           │
       └──────────────►  DATA LAYER       ◄───────────┘
                      ├───────────────────┤
                      │                   │
                      │ PostgreSQL 16     │
                      │ ┌───────────────┐ │
                      │ │ behavioral    │ │
                      │ │ capsules      │ │
                      │ │ overseer      │ │
                      │ │ ar_vr_state   │ │
                      │ └───────────────┘ │
                      │                   │
                      │ Redis (Cache)     │
                      │ Kafka (Events)    │
                      └───────────────────┘
                                │
                                ▼
                      ┌───────────────────┐
                      │ PROTOCOL LAYER    │
                      ├───────────────────┤
                      │                   │
                      │ A2A Task Engine   │
                      │ DTSL Validator    │
                      │ MCP Handler       │
                      │                   │
                      └───────────────────┘
```

---

## Risk Mitigation

### Risk 1: Breaking Existing Functionality
**Mitigation:**
- Maintain backward compatibility in all factory modifications
- Use feature flags for coordinator integration
- Comprehensive integration tests before merging

### Risk 2: Performance Degradation
**Mitigation:**
- Use async/await throughout
- Implement caching in unified registry
- Event bus message batching
- Performance benchmarks before/after

### Risk 3: Complex Debugging
**Mitigation:**
- Structured logging at every integration point
- Request tracing across layers
- Health check endpoints for all integrations
- Comprehensive error messages

---

## Next Steps (Week 20-21)

After Week 18-19 unification:
1. **LLM Inference Service** - Connect Core AI Layer to unified architecture
2. **Avatar Interface Completion** - Full avatar system with unified capsule registry
3. **Authentication & Authorization** - Security layer integration
4. **Comprehensive End-to-End Testing** - Target 15% test coverage
5. **Performance Optimization** - Based on Week 18-19 integration

---

## Appendix: File Checklist

### New Files Created (Week 18-19)
- [ ] `src/overseer_system/capsule_lifecycle/capsule_lifecycle_coordinator.py`
- [ ] `src/overseer_system/capsule_lifecycle/unified_capsule_registry.py`
- [ ] `src/overseer_system/integration/ar_vr_integration_adapter.py`
- [ ] `src/data_layer/src/ar_vr_state/ar_vr_state_manager.py`
- [ ] `src/overseer_system/event_bus/component_connectors.py`
- [ ] `database/migrations/week_18_19_ar_vr_schema.sql`
- [ ] `database/migrations/week_18_19_unified_registry.sql`
- [ ] `tests/week18_19/test_architecture_unification.py`
- [ ] `tests/week18_19/test_dac_factory_unification.py`
- [ ] `tests/week18_19/test_ar_vr_integration.py`
- [ ] `tests/week18_19/test_overseer_event_bus.py`
- [ ] `WEEK_18_19_SUMMARY.md`

### Modified Files (Week 18-19)
- [ ] `src/application_layer/agent_capsule_factory.py` (coordinator integration)
- [ ] `src/deployment_operations_layer/agent/capsule_instantiator/capsule_factory.py` (coordinator integration)
- [ ] `src/ui_ux_layer/core/capsule_framework/capsule_manager.py` (AR rendering)
- [ ] `src/ui_ux_layer/edge/ar_vr_integration/ar_vr_integration.py` (adapter integration)
- [ ] `src/overseer_system/integration/application_layer_integration_manager.py` (activated)
- [ ] `src/overseer_system/integration/ui_ux_layer_integration_manager.py` (activated)
- [ ] `database/schema/unified_schema.sql` (AR/VR and unified registry schemas)

---

**Total Estimated LOC:** 5,000+ new lines
**Total Estimated Modifications:** 2,000+ lines
**Total New Tests:** 50+ tests
**Timeline:** 10 days (Days 1-10 of Week 18-19)
