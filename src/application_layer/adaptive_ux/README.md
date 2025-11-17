# Adaptive UX System

## Overview

The Adaptive UX System is a comprehensive framework for dynamically personalizing capsule interfaces based on user behavior, expertise, and context. This system enables real-time UX adaptation, A/B testing, and continuous optimization.

**Week 10 Deliverable** - Part of Phase 3: Adaptive UX & ASAL Integration

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  User Interactions                           │
│         (Behavioral Vector from Week 9)                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Adaptive UX Engine                              │
│  - Generate personalized UX configuration                    │
│  - Context-aware optimization                                │
│  - Confidence scoring                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
┌──────────────────┐   ┌──────────────────┐
│ Dynamic Layout   │   │ Data Density     │
│ Adjuster         │   │ Tuner            │
│ - 6 rules        │   │ - 5 tiers        │
│ - Real-time      │   │ - Progressive    │
└──────────────────┘   └──────────────────┘
          │                     │
          └──────────┬──────────┘
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              A/B Testing Framework                           │
│  - Multi-variant experiments                                 │
│  - Statistical significance                                  │
│  - Metrics tracking                                          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  REST API                                    │
│  - UX configuration endpoints                                │
│  - Adjustment tracking                                       │
│  - Experiment management                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Adaptive UX Engine (`adaptive_ux_engine.py`)

**Purpose:** Core personalization engine that generates UX configurations.

**Key Features:**
- Expertise-based configuration (novice → power user)
- Context-aware optimization (device, network, battery)
- Action priority reweighting
- Capsule-type-specific configs
- Confidence scoring

**Usage:**
```python
from adaptive_ux import adaptive_ux_engine

# Generate UX config
ux_config = await adaptive_ux_engine.generate_ux_config(
    user_id="user_123",
    behavioral_vector=bv,
    context={"device_type": "mobile"}
)

# Optimize for context
optimized = await adaptive_ux_engine.optimize_for_context(
    config=ux_config,
    context={"battery_level": 15}  # Low battery
)
```

### 2. Dynamic Layout Adjuster (`dynamic_layout_adjuster.py`)

**Purpose:** Real-time layout adaptation based on behavior and context.

**Key Features:**
- 6 default rules (mobile, tablet, power user, high error, frequent expand, engagement drop)
- Priority-based evaluation (1-10 scale)
- 4 adjustment strategies (immediate, animated, next_session, gradual)
- User override system
- Effectiveness tracking

**Default Rules:**

| Rule | Priority | Trigger | Action |
|------|----------|---------|--------|
| Mobile Optimization | 10 | device=mobile, width<768 | List layout, 1 column, large cards |
| Tablet Optimization | 10 | device=tablet, 768-1024px | Grid layout, 3 columns, medium cards |
| Power User Compact | 9 | expertise=power_user, fast, low errors | Compact, 5 columns, small cards |
| High Error Simplify | 9 | error_rate>15%, 5+ errors/10min | Reduce density, add confirmations |
| Frequent Expanders | 8 | expand_rate>60% | Spacious layout, large cards |
| Engagement Drop | 6 | 20% engagement drop | More visual, animations, haptic |

**Usage:**
```python
from adaptive_ux import dynamic_layout_adjuster

# Evaluate triggers
adjustments = await dynamic_layout_adjuster.evaluate_triggers(
    user_id="user_123",
    behavioral_vector=bv,
    current_layout=current_layout,
    context={"device_type": "mobile"}
)

# Apply adjustment
if adjustments:
    await dynamic_layout_adjuster.apply_adjustment(adjustments[0])
```

### 3. Data Density Tuner (`data_density_tuner.py`)

**Purpose:** Progressive information disclosure based on expertise and cognitive load.

**Key Features:**
- 5-tier density system (minimal → maximum)
- 15 information elements with priority classification
- Error-rate feedback loop
- Progressive disclosure (time-based)
- Context-aware adjustments

**Density Levels:**

| Level | User Type | What's Shown | Elements |
|-------|-----------|--------------|----------|
| **MINIMAL** | Novice | Title + Primary Action | 2 elements |
| **LOW** | Intermediate | + Status + Timestamp + Category | 5 elements |
| **MEDIUM** | Proficient | + Metadata + Secondary Actions + Description | 9 elements |
| **HIGH** | Advanced | + Tags + Related + History + Shortcuts | 13 elements |
| **MAXIMUM** | Power User | Everything + Debug + API Details | 15 elements |

**Information Priority:**
- **CRITICAL:** Always show (title, primary action)
- **HIGH:** Show at LOW+ (status, timestamp, category)
- **MEDIUM:** Show at MEDIUM+ (metadata, secondary actions, description)
- **LOW:** Show at HIGH+ (tags, related, history, shortcuts)
- **OPTIONAL:** Show at MAXIMUM only (debug, API details)

**Usage:**
```python
from adaptive_ux import data_density_tuner

# Determine optimal density
density = await data_density_tuner.determine_optimal_density(
    user_id="user_123",
    behavioral_vector=bv,
    capsule_type="task"
)

# Progressive disclosure
new_density = await data_density_tuner.progressive_disclosure(
    user_id="user_123",
    capsule_id="capsule_456",
    current_density=2,  # LOW
    engagement_duration_seconds=25  # User engaged for 25s
)
# Returns 3 (MEDIUM) after 20s threshold
```

### 4. A/B Testing Framework (`ab_testing_framework.py`)

**Purpose:** Run controlled experiments on UX variations.

**Key Features:**
- Multi-variant support (A/B/C/...)
- Deterministic user assignment (consistent hashing)
- Traffic allocation control
- User targeting (expertise, device type)
- Statistical significance calculation (two-proportion z-test)
- Experiment lifecycle management

**Usage:**
```python
from adaptive_ux import ab_testing_framework

# Create experiment
experiment = await ab_testing_framework.create_experiment(
    experiment_name="Compact Layout Test",
    description="Test if compact layout improves efficiency for advanced users",
    hypothesis="Advanced users will complete tasks 15% faster with compact layout",
    variants=[
        {
            "variant_name": "control",
            "variant_type": "control",
            "traffic_allocation": 0.5,
            "ux_config_overrides": {}
        },
        {
            "variant_name": "compact",
            "variant_type": "treatment",
            "traffic_allocation": 0.5,
            "ux_config_overrides": {
                "layout_type": "compact",
                "grid_columns": 5,
                "card_size": "small"
            }
        }
    ],
    target_expertise_levels=["advanced", "power_user"],
    min_sample_size=100
)

# Start experiment
await ab_testing_framework.start_experiment(experiment.experiment_id)

# Assign user
assignment = await ab_testing_framework.assign_user_to_experiment(
    experiment_id=experiment.experiment_id,
    user_id="user_123",
    user_context={"expertise_level": "advanced"}
)

# Track conversion
await ab_testing_framework.track_conversion(
    experiment_id=experiment.experiment_id,
    user_id="user_123"
)

# Analyze results
results = await ab_testing_framework.analyze_experiment(experiment.experiment_id)
print(f"Winner: {results['winner']}")
print(f"Significance: {results['statistical_significance']:.3f}")
```

### 5. REST API (`adaptive_ux_api.py`)

**Purpose:** HTTP endpoints for frontend integration.

**Endpoints:**

#### GET /health
Health check endpoint.

#### POST /api/v1/ux/config
Get personalized UX configuration.

**Request:**
```json
{
  "user_id": "user_123",
  "device_type": "mobile",
  "screen_width": 375,
  "screen_height": 812,
  "network_speed": "slow",
  "battery_level": 20
}
```

**Response:**
```json
{
  "user_id": "user_123",
  "config": {
    "layout_type": "list",
    "grid_columns": 1,
    "card_size": "large",
    "data_density": 2,
    "visible_elements": ["title", "primary_action", "status_indicator"],
    "animation_speed": "none",
    "primary_actions": ["complete", "snooze"],
    "secondary_actions": ["edit", "delete"]
  },
  "confidence_score": 0.85,
  "generated_at": "2025-11-17T10:30:00Z"
}
```

#### POST /api/v1/ux/adjustment
Apply a UX adjustment.

#### POST /api/v1/ux/override
Record user override.

#### GET /api/v1/ux/experiments
List active experiments.

#### POST /api/v1/ux/experiments/{id}/assign
Assign user to experiment.

#### POST /api/v1/ux/track
Track UX metric.

#### GET /api/v1/ux/effectiveness/{user_id}
Get effectiveness metrics.

---

## Integration with Week 9 (Behavioral Tracking)

The Adaptive UX System builds directly on Week 9's behavioral tracking:

```python
# Week 9: Capture behavior
await behavioral_tracker.log_interaction(
    user_id="user_123",
    event_type="tap",
    capsule_id="capsule_456"
)

# Week 9: Compute behavioral vector
bv = await bv_computer.compute_behavioral_vector(
    user_id="user_123",
    events=events
)

# Week 10: Generate UX config from BV
ux_config = await adaptive_ux_engine.generate_ux_config(
    user_id="user_123",
    behavioral_vector=bv  # ← Week 9 output
)
```

**Data Flow:**
```
User Interactions → BehavioralTracker → BV Storage
                                          ↓
                                    BV Computer
                                          ↓
                                  Behavioral Vector
                                          ↓
                                Adaptive UX Engine ← Week 10
                                          ↓
                                  UX Configuration
```

---

## Configuration

### Environment Variables

```bash
# API
ADAPTIVE_UX_API_HOST=0.0.0.0
ADAPTIVE_UX_API_PORT=8002
ADAPTIVE_UX_API_WORKERS=4

# Storage (from Week 9)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=industriverse
REDIS_HOST=localhost
REDIS_PORT=6379

# Experiments
AB_TESTING_ENABLED=true
MIN_SAMPLE_SIZE=100
CONFIDENCE_LEVEL=0.95

# Adjustments
LAYOUT_ADJUSTMENT_ENABLED=true
DENSITY_ADJUSTMENT_ENABLED=true
USER_OVERRIDE_ENABLED=true
```

---

## Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  adaptive-ux-api:
    build: .
    environment:
      POSTGRES_HOST: postgres
      REDIS_HOST: redis
    ports:
      - "8002:8002"
    depends_on:
      - postgres
      - redis
    command: uvicorn adaptive_ux_api:app --host 0.0.0.0 --port 8002
```

---

## Frontend Integration

### 1. Get UX Configuration on Load

```typescript
// Frontend: Get UX config when user logs in
async function loadUXConfig(userId: string) {
  const response = await fetch('/api/v1/ux/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      device_type: getDeviceType(),
      screen_width: window.innerWidth,
      screen_height: window.innerHeight,
      network_speed: getNetworkSpeed(),
      battery_level: await getBatteryLevel()
    })
  });
  
  const config = await response.json();
  
  // Apply configuration
  applyLayoutConfig(config.config);
}
```

### 2. Track User Overrides

```typescript
// Frontend: User manually changes layout
function onUserChangeLayout(newLayout: string) {
  // Apply change
  setLayout(newLayout);
  
  // Record override
  fetch('/api/v1/ux/override', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_id: currentUser.id,
      property_name: 'layout_type',
      original_value: currentLayout,
      user_value: newLayout
    })
  });
}
```

### 3. Progressive Disclosure

```typescript
// Frontend: User engages with capsule
let engagementStart = Date.now();

capsule.addEventListener('focus', () => {
  engagementStart = Date.now();
});

setInterval(() => {
  const duration = (Date.now() - engagementStart) / 1000;
  
  if (duration >= 20 && currentDensity < 3) {
    // Request density increase
    increaseDensity();
  }
}, 5000);
```

---

## Performance Metrics

### Target Performance:
- **UX Config Generation:** < 50ms (p95)
- **Layout Adjustment:** < 10ms
- **Density Adjustment:** < 5ms
- **API Response Time:** < 100ms (p95)

### Caching:
- **BV Cache:** 1 hour TTL (Redis)
- **UX Config Cache:** 5 minutes TTL
- **Experiment Assignment:** Permanent (deterministic)

---

## Testing

### Unit Tests

```bash
pytest test_adaptive_ux_engine.py -v
pytest test_dynamic_layout_adjuster.py -v
pytest test_data_density_tuner.py -v
pytest test_ab_testing_framework.py -v
```

### Integration Tests

```bash
pytest test_adaptive_ux_integration.py -v
```

### Load Tests

```bash
# Test API under load
locust -f locustfile.py --host http://localhost:8002
```

---

## Roadmap

### Week 11: ASAL Meta-Learning Integration
- Collect UX Genomes across all users
- Generate Global Interaction Policies (GIPs)
- Learn optimal rules from aggregate data
- Cross-capsule UX archetypes

### Week 12: Overseer Orchestration
- User launchpad (personalized dashboard)
- Role-based capsule visibility
- Contextual capsule spawning
- Lifecycle management

---

## Contributing

### Adding New Layout Rules

```python
# Add to dynamic_layout_adjuster.py
adjuster.add_rule(LayoutRule(
    rule_id="my_custom_rule",
    rule_name="My Custom Rule",
    description="Description of when this rule triggers",
    trigger_type=TriggerType.BEHAVIOR_PATTERN.value,
    trigger_conditions={
        "expertise_level": "advanced",
        "min_interactions": 50
    },
    layout_changes={
        "layout_type": "custom",
        "grid_columns": 4
    },
    strategy=AdjustmentStrategy.ANIMATED.value,
    priority=7
))
```

### Adding New Information Elements

```python
# Add to data_density_tuner.py
tuner.add_element(InformationElement(
    element_id="my_element",
    element_name="My Element",
    element_type="text",
    priority=InformationPriority.MEDIUM.value,
    min_density_level=DensityLevel.MEDIUM.value
))
```

---

## License

Copyright © 2025 Industriverse. All rights reserved.

---

## Support

For questions or issues:
- GitHub Issues: https://github.com/industriverse/industriverse/issues
- Email: support@industriverse.com
- Documentation: https://docs.industriverse.com

---

**Week 10 Complete** ✅
- Adaptive UX Engine
- Dynamic Layout Adjuster
- Data Density Tuner
- A/B Testing Framework
- REST API
- Complete Documentation

**Total: ~4,200 lines across 6 files**

**Next: Week 11 - ASAL Meta-Learning Integration**
