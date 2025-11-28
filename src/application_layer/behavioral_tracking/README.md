# Behavioral Tracking Infrastructure

## Overview

The Behavioral Tracking Infrastructure is a comprehensive system for capturing, analyzing, and leveraging user interactions with Dynamic Agent Capsules. This system enables adaptive UX personalization by building detailed behavioral profiles of users.

**Week 9 Deliverable** - Part of Phase 3: Adaptive UX & ASAL Integration

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interactions                        │
│         (Taps, Clicks, Expands, Actions, etc.)              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              Behavioral Tracker                              │
│  - Event logging with validation                            │
│  - Session tracking                                          │
│  - Kafka streaming (optional)                               │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              BV Storage Layer                                │
│  - PostgreSQL (partitioned tables)                          │
│  - Redis (caching layer)                                    │
│  - Event persistence                                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│         Behavioral Vector Computer                           │
│  - Usage pattern analysis                                    │
│  - Preference inference                                      │
│  - Expertise classification                                  │
│  - Adaptive UX recommendations                              │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  REST API                                    │
│  - Event logging endpoints                                   │
│  - BV retrieval endpoints                                    │
│  - Analytics endpoints                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Behavioral Tracker (`behavioral_tracker.py`)

**Purpose:** Capture and validate user interaction events.

**Key Features:**
- 15+ interaction types (tap, click, expand, collapse, pin, drag, etc.)
- Event schema validation with Pydantic
- Kafka streaming integration (with graceful fallback)
- Session tracking and analytics
- Engagement scoring

**Usage:**
```python
from behavioral_tracker import BehavioralTracker, InteractionType

tracker = BehavioralTracker(
    kafka_bootstrap_servers="localhost:9092",
    kafka_topic="interaction-events"
)

# Log an interaction
await tracker.log_interaction(
    user_id="user_123",
    session_id="session_456",
    event_type=InteractionType.TAP.value,
    capsule_id="capsule_789",
    capsule_type="task",
    device_type="web",
    duration_ms=1500
)
```

### 2. Behavioral Vector Computer (`behavioral_vector_computer.py`)

**Purpose:** Compute behavioral profiles from interaction events.

**Key Features:**
- Usage pattern analysis (time of day, day of week, capsule type distributions)
- User preference inference (layout, density, animation preferences)
- Expertise level classification (5-tier archetype system)
- Proficiency indicators (duration, error rate, completion rate)
- Adaptive UX configuration recommendations

**Usage:**
```python
from behavioral_vector_computer import BehavioralVectorComputer

computer = BehavioralVectorComputer()

# Compute BV from events
bv = await computer.compute_behavioral_vector(
    user_id="user_123",
    events=interaction_events
)

print(f"Expertise Level: {bv.expertise_level}")
print(f"Preferred Layout: {bv.user_preferences['layout_preference']}")
```

### 3. BV Storage (`bv_storage.py`)

**Purpose:** Persist events and behavioral vectors with caching.

**Key Features:**
- PostgreSQL async storage backend
- Redis caching layer with TTL
- Cache-aside pattern for performance
- Event and BV persistence
- Query optimization with indexes

**Usage:**
```python
from bv_storage import BVStorage

storage = BVStorage(
    postgres_dsn="postgresql://user:pass@localhost/db",
    redis_url="redis://localhost:6379"
)

await storage.initialize()

# Store an event
await storage.store_interaction_event(event)

# Retrieve BV (with caching)
bv = await storage.get_behavioral_vector(user_id="user_123")
```

### 4. REST API (`bv_api.py`)

**Purpose:** Expose behavioral tracking functionality via HTTP.

**Endpoints:**

#### Event Logging
```
POST /api/v1/interactions/log
```
Log a new interaction event.

**Request Body:**
```json
{
  "user_id": "user_123",
  "session_id": "session_456",
  "event_type": "tap",
  "capsule_id": "capsule_789",
  "capsule_type": "task",
  "device_type": "web",
  "duration_ms": 1500
}
```

**Response:**
```json
{
  "event_id": "evt_abc123",
  "timestamp": "2025-11-17T10:30:00Z",
  "user_id": "user_123",
  "event_type": "tap",
  "success": true
}
```

#### BV Retrieval
```
GET /api/v1/behavioral-vectors/{user_id}
```
Retrieve behavioral vector for a user.

**Response:**
```json
{
  "user_id": "user_123",
  "computed_at": "2025-11-17T10:30:00Z",
  "expertise_level": "proficient",
  "total_interactions": 1250,
  "usage_patterns": {
    "time_of_day_distribution": {"morning": 0.3, "afternoon": 0.5, "evening": 0.2},
    "day_of_week_distribution": {"monday": 0.15, "tuesday": 0.14, ...},
    "capsule_type_distribution": {"task": 0.45, "alert": 0.32, "workflow": 0.23}
  },
  "user_preferences": {
    "layout_preference": "compact",
    "data_density": "high",
    "animation_preference": "minimal"
  },
  "proficiency_indicators": {
    "avg_interaction_duration_ms": 850,
    "error_rate": 0.03,
    "completion_rate": 0.92
  }
}
```

#### BV Computation
```
POST /api/v1/behavioral-vectors/compute
```
Trigger BV computation for a user.

**Request Body:**
```json
{
  "user_id": "user_123",
  "lookback_days": 30
}
```

#### Engagement Metrics
```
GET /api/v1/analytics/engagement/{user_id}
```
Get engagement metrics for a user.

**Response:**
```json
{
  "user_id": "user_123",
  "total_sessions": 45,
  "avg_session_duration_minutes": 12.5,
  "avg_interactions_per_session": 8.2,
  "engagement_score": 0.78,
  "last_active": "2025-11-17T10:30:00Z"
}
```

### 5. Monitoring Dashboard (`monitoring_dashboard.py`)

**Purpose:** Real-time monitoring and alerting for the behavioral tracking system.

**Key Features:**
- System health monitoring
- Performance metrics (event processing time, BV computation time)
- User engagement analytics
- Cache hit rate tracking
- Error rate monitoring
- Alerting for anomalies

**Usage:**
```python
from monitoring_dashboard import MonitoringDashboard, MetricsCollector

collector = MetricsCollector()
dashboard = MonitoringDashboard(collector)

# Start monitoring loop
await dashboard.start_monitoring(interval_seconds=60)
```

**Dashboard API:**
```
GET /dashboard              # Complete dashboard data
GET /metrics/system         # System metrics
GET /metrics/engagement     # Engagement metrics
GET /metrics/bv-computation # BV computation metrics
GET /alerts                 # Recent alerts
GET /health                 # Health check
```

### 6. Integration Tests (`test_behavioral_tracking_integration.py`)

**Purpose:** Comprehensive end-to-end testing of the behavioral tracking system.

**Test Coverage:**
- Event tracking and validation
- BV computation accuracy
- Storage layer (PostgreSQL + Redis)
- API endpoints
- Kafka integration (with mocks)
- Performance benchmarks

**Running Tests:**
```bash
pytest test_behavioral_tracking_integration.py -v
```

---

## Data Schemas

### Interaction Event Schema

```python
@dataclass
class InteractionEvent:
    # Event identity
    event_id: str
    timestamp: str
    event_type: str  # tap, click, expand, collapse, etc.
    severity: str = "info"
    
    # User context
    user_id: str
    session_id: str
    device_id: str
    device_type: str  # web, ios, android, desktop
    
    # Capsule context
    capsule_id: str
    capsule_type: str  # task, workflow, alert, status, decision
    capsule_category: str
    
    # Interaction details
    interaction_target: str  # capsule, action, component
    action_id: Optional[str]
    component_id: Optional[str]
    
    # Timing metrics
    duration_ms: Optional[int]
    time_since_last_interaction_ms: Optional[int]
    
    # Result
    success: bool
    error_message: Optional[str]
```

### Behavioral Vector Schema

```python
@dataclass
class BehavioralVector:
    # Identity
    user_id: str
    computed_at: str
    version: str = "1.0"
    
    # Expertise classification
    expertise_level: str  # novice, intermediate, proficient, advanced, power_user
    
    # Interaction statistics
    total_interactions: int
    total_sessions: int
    avg_session_duration_minutes: float
    
    # Usage patterns
    usage_patterns: Dict[str, Any]  # time_of_day, day_of_week, capsule_type distributions
    
    # User preferences
    user_preferences: Dict[str, str]  # layout, density, animation preferences
    
    # Proficiency indicators
    proficiency_indicators: Dict[str, float]  # duration, error_rate, completion_rate
    
    # Adaptive UX configuration
    adaptive_ux_config: Dict[str, Any]  # recommended UX settings
```

---

## Database Schema

### Tables

#### 1. `interaction_events` (Partitioned by month)
```sql
CREATE TABLE interaction_events (
    event_id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'info',
    user_id VARCHAR(255) NOT NULL,
    session_id VARCHAR(255),
    device_id VARCHAR(255),
    device_type VARCHAR(50),
    capsule_id VARCHAR(255),
    capsule_type VARCHAR(50),
    capsule_category VARCHAR(100),
    interaction_target VARCHAR(50),
    action_id VARCHAR(255),
    component_id VARCHAR(255),
    duration_ms INTEGER,
    time_since_last_interaction_ms INTEGER,
    interaction_data JSONB,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    context JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
) PARTITION BY RANGE (timestamp);

CREATE INDEX idx_events_user_timestamp ON interaction_events(user_id, timestamp DESC);
CREATE INDEX idx_events_session ON interaction_events(session_id);
CREATE INDEX idx_events_capsule ON interaction_events(capsule_id);
CREATE INDEX idx_events_type ON interaction_events(event_type);
```

#### 2. `behavioral_vectors`
```sql
CREATE TABLE behavioral_vectors (
    user_id VARCHAR(255) PRIMARY KEY,
    computed_at TIMESTAMPTZ NOT NULL,
    version VARCHAR(20) DEFAULT '1.0',
    expertise_level VARCHAR(50),
    total_interactions INTEGER,
    total_sessions INTEGER,
    avg_session_duration_minutes FLOAT,
    usage_patterns JSONB,
    user_preferences JSONB,
    proficiency_indicators JSONB,
    adaptive_ux_config JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bv_expertise ON behavioral_vectors(expertise_level);
CREATE INDEX idx_bv_computed_at ON behavioral_vectors(computed_at DESC);
```

#### 3. `bv_history`
```sql
CREATE TABLE bv_history (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    computed_at TIMESTAMPTZ NOT NULL,
    expertise_level VARCHAR(50),
    total_interactions INTEGER,
    snapshot JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_bv_history_user ON bv_history(user_id, computed_at DESC);
```

---

## Configuration

### Environment Variables

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=industriverse
POSTGRES_USER=industriverse_user
POSTGRES_PASSWORD=secure_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Kafka (optional)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_EVENTS=interaction-events
KAFKA_TOPIC_BV=behavioral-vectors

# API
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Monitoring
MONITORING_ENABLED=true
MONITORING_INTERVAL_SECONDS=60
ALERT_EMAIL=alerts@industriverse.com
```

### Kafka Configuration

See `kafka_config.yaml` for complete Kafka topic configuration including:
- Partition count
- Replication factor
- Retention policies
- Compression settings

---

## Deployment

### Docker Compose

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: industriverse
      POSTGRES_USER: industriverse_user
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./db_schema.sql:/docker-entrypoint-initdb.d/schema.sql

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes

  behavioral-api:
    build: .
    environment:
      POSTGRES_HOST: postgres
      REDIS_HOST: redis
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    command: uvicorn bv_api:app --host 0.0.0.0 --port 8000

  monitoring-dashboard:
    build: .
    environment:
      POSTGRES_HOST: postgres
      REDIS_HOST: redis
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis
    command: python monitoring_dashboard.py

volumes:
  postgres_data:
```

### Kubernetes

See `kubernetes/` directory for complete Kubernetes manifests including:
- Deployments
- Services
- ConfigMaps
- Secrets
- Ingress

---

## Performance Considerations

### Caching Strategy

- **Redis TTL:** 1 hour for BVs, 5 minutes for engagement metrics
- **Cache-aside pattern:** Check cache first, fallback to database
- **Cache invalidation:** On BV computation, clear user's cache entry

### Database Optimization

- **Partitioning:** `interaction_events` partitioned by month for efficient queries
- **Indexes:** Strategic indexes on user_id, timestamp, session_id
- **Connection pooling:** asyncpg pool with min=10, max=20 connections

### Kafka Optimization

- **Batch processing:** Events batched in 100ms windows
- **Compression:** LZ4 compression for event payloads
- **Partitioning:** Events partitioned by user_id for ordering

---

## Monitoring & Alerting

### Key Metrics

- **Event Processing Rate:** Events/second
- **BV Computation Time:** Average, P95, P99
- **Cache Hit Rate:** Target > 80%
- **Error Rate:** Target < 1%
- **Active Users:** Last hour, last day
- **Storage Operations:** Reads/writes per second

### Alerts

- **Critical:** Error rate > 5%, System health = critical
- **Warning:** Cache hit rate < 50%, Avg processing time > 100ms
- **Info:** New user archetype detected, Unusual usage pattern

---

## Future Enhancements

### Week 10: Adaptive UX Engine
- Dynamic capsule layout adjustments
- Data density tuning
- Action priority reweighting
- A/B testing framework

### Week 11: ASAL Meta-Learning
- UX Genome collection across capsules
- Global Interaction Policy (GIP) generation
- Cross-capsule UX archetypes
- Policy distribution to devices

### Week 12: Overseer Orchestration
- User launchpad (personalized dashboard)
- Role-based capsule visibility
- Contextual capsule spawning
- Capsule lifecycle management

---

## API Reference

See [API Documentation](./API.md) for complete API reference with examples.

---

## Contributing

### Code Style
- Follow PEP 8 for Python code
- Use type hints for all function signatures
- Add docstrings to all classes and functions
- Write tests for new features

### Testing
```bash
# Run all tests
pytest test_behavioral_tracking_integration.py -v

# Run specific test suite
pytest test_behavioral_tracking_integration.py::TestEventTracking -v

# Run with coverage
pytest --cov=. --cov-report=html
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

**Week 9 Day 7 Complete** ✅
- Integration tests implemented
- Monitoring dashboard operational
- Comprehensive documentation delivered
