# Behavioral Tracking API Bridge

**Week 17 Day 2: Unified Behavioral Tracking Integration**

This module provides the API bridge connecting Week 16 TypeScript/JavaScript frontends to the Week 9 Python behavioral tracking backend.

## 📋 Overview

The API Bridge consists of three main components:

1. **behavioral_tracking_client.py** - Python client for database operations
2. **behavioral_tracking_api.py** - FastAPI REST endpoints
3. **BehavioralTrackingClient.ts** - TypeScript/JavaScript client

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  WEEK 16: TypeScript Frontend (capsule-pins-pwa)               │
│  ├─ React Components                                            │
│  ├─ State Management                                            │
│  └─ BehavioralTrackingClient.ts ─────────┐                     │
└──────────────────────────────────────────│─────────────────────┘
                                            │ HTTP/REST
                                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  WEEK 17: API Bridge (FastAPI)                                  │
│  ├─ POST /api/v1/behavioral/interactions                        │
│  ├─ GET  /api/v1/behavioral/vectors/{user_id}                   │
│  ├─ POST /api/v1/behavioral/vectors/{user_id}/compute           │
│  └─ behavioral_tracking_api.py ──────────┐                      │
└──────────────────────────────────────────│─────────────────────┘
                                            │ Python Async
                                            ↓
┌─────────────────────────────────────────────────────────────────┐
│  WEEK 9: Python Backend (behavioral_tracking)                   │
│  ├─ behavioral_tracking_client.py                               │
│  ├─ behavioral_vector_computer.py                               │
│  └─ PostgreSQL + Redis + Kafka ──────────┐                     │
└──────────────────────────────────────────│─────────────────────┘
                                            │
                                            ↓
                                    Unified Database
                                  (behavioral schema)
```

## 🚀 Quick Start

### 1. Start the API Server

```bash
# Navigate to the API bridge directory
cd src/application_layer/behavioral_tracking/api_bridge

# Install dependencies
pip install fastapi uvicorn asyncpg aioredis kafka-python

# Start the server
python behavioral_tracking_api.py

# Server will start on http://localhost:8001
```

### 2. Use from TypeScript/JavaScript

```typescript
import BehavioralTrackingClient from './BehavioralTrackingClient';

// Initialize client
const client = new BehavioralTrackingClient('http://localhost:8001');

// Track interaction
await client.trackInteraction({
  event_type: 'click',
  user_id: 'user123',
  session_id: 'sess456',
  capsule_id: 'cap789',
  capsule_type: 'alert',
  device_type: 'web',
});

// Get behavioral vector
const bv = await client.getBehavioralVector('user123');
console.log(bv.adaptive_ux_config);

// Get engagement score
const score = await client.getEngagementScore('user123');
console.log(`Engagement: ${score.engagement_score}`);
```

### 3. Use from React

```typescript
import { useBehavioralTracking } from './BehavioralTrackingClient';

function MyComponent() {
  const { behavioralVector, trackInteraction } = useBehavioralTracking(
    'user123',
    'sess456'
  );

  const handleCapsuleClick = async (capsuleId: string) => {
    await trackInteraction({
      event_type: 'click',
      capsule_id: capsuleId,
      capsule_type: 'alert',
    });
  };

  // Adaptive UX based on behavioral vector
  const showTooltips = behavioralVector?.adaptive_ux_config?.tooltips ?? true;

  return (
    <div>
      {showTooltips && <Tooltip>...</Tooltip>}
      <button onClick={() => handleCapsuleClick('cap123')}>
        Click Me
      </button>
    </div>
  );
}
```

## 📚 API Endpoints

### Health Check

```bash
GET /api/v1/behavioral/health
```

Response:
```json
{
  "status": "healthy",
  "service": "behavioral-tracking-api",
  "version": "1.0.0"
}
```

### Track Interaction

```bash
POST /api/v1/behavioral/interactions
Content-Type: application/json

{
  "event_type": "click",
  "user_id": "user123",
  "session_id": "sess456",
  "capsule_id": "cap789",
  "capsule_type": "alert"
}
```

Response:
```json
{
  "event_id": "uuid-here",
  "status": "tracked",
  "timestamp": "2025-11-18T12:00:00Z"
}
```

### Get Behavioral Vector

```bash
GET /api/v1/behavioral/vectors/{user_id}
```

Response:
```json
{
  "user_id": "user123",
  "computed_at": "2025-11-18T12:00:00Z",
  "version": 5,
  "usage_patterns": {
    "avg_session_duration": 600,
    "interaction_frequency": "high"
  },
  "expertise_level": {
    "level": "intermediate",
    "score": 0.7
  },
  "engagement_metrics": {
    "score": 0.85,
    "confidence": 0.9
  },
  "adaptive_ux_config": {
    "tooltips": false,
    "shortcuts": true,
    "complexity": "moderate"
  }
}
```

### Compute Behavioral Vector

```bash
POST /api/v1/behavioral/vectors/{user_id}/compute
```

Analyzes user's interaction history and generates fresh behavioral profile.

### Get Engagement Score

```bash
GET /api/v1/behavioral/vectors/{user_id}/engagement
```

Response:
```json
{
  "user_id": "user123",
  "engagement_score": 0.85,
  "confidence": 0.9,
  "last_computed": "2025-11-18T12:00:00Z",
  "factors": {
    "session_frequency": 0.9,
    "interaction_diversity": 0.8,
    "task_completion_rate": 0.85
  }
}
```

### Get Session Details

```bash
GET /api/v1/behavioral/sessions/{session_id}
```

### Get User Interactions

```bash
GET /api/v1/behavioral/interactions/{user_id}?limit=50&offset=0&start_date=2025-11-01T00:00:00Z
```

### Clear Cache

```bash
DELETE /api/v1/behavioral/vectors/{user_id}/cache
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql://industriverse:changeme@localhost:5432/industriverse

# Redis
REDIS_URL=redis://localhost:6379/0

# Kafka (optional)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092

# API Settings
API_HOST=0.0.0.0
API_PORT=8001
API_CORS_ORIGINS=*

# Logging
LOG_LEVEL=INFO
```

### TypeScript Configuration

```typescript
// Configure base URL for different environments
const client = new BehavioralTrackingClient(
  process.env.NODE_ENV === 'production'
    ? 'https://api.industriverse.ai'
    : 'http://localhost:8001'
);
```

## 🧪 Testing

### Test API Server

```bash
# Health check
curl http://localhost:8001/api/v1/behavioral/health

# Track interaction
curl -X POST http://localhost:8001/api/v1/behavioral/interactions \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "click",
    "user_id": "test_user",
    "session_id": "test_session"
  }'

# Get behavioral vector
curl http://localhost:8001/api/v1/behavioral/vectors/test_user
```

### Test TypeScript Client

```typescript
import BehavioralTrackingClient from './BehavioralTrackingClient';

async function testClient() {
  const client = new BehavioralTrackingClient();

  // Test health check
  const health = await client.healthCheck();
  console.log('Health:', health);

  // Test track interaction
  const result = await client.trackInteraction({
    event_type: 'click',
    user_id: 'test_user',
    session_id: 'test_session',
  });
  console.log('Tracked:', result);

  // Test get behavioral vector
  try {
    const bv = await client.getBehavioralVector('test_user');
    console.log('Behavioral Vector:', bv);
  } catch (err) {
    console.log('No behavioral vector yet (expected for new user)');
  }
}

testClient();
```

## 📊 Monitoring

The API includes built-in monitoring endpoints:

### Prometheus Metrics (Future)

```bash
GET /metrics
```

### API Documentation

```bash
# Swagger UI
http://localhost:8001/api/v1/behavioral/docs

# ReDoc
http://localhost:8001/api/v1/behavioral/redoc
```

## 🔐 Security

### Authentication (Future Enhancement)

```python
# Add authentication to API
from fastapi.security import HTTPBearer

security = HTTPBearer()

@app.post("/api/v1/behavioral/interactions")
async def track_interaction(
    event: InteractionEventCreate,
    token: str = Depends(security),
    client: BehavioralTrackingClient = Depends(get_behavioral_client)
):
    # Validate token
    user = validate_token(token)
    # ...
```

### Rate Limiting (Future Enhancement)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/behavioral/interactions")
@limiter.limit("100/minute")
async def track_interaction(...):
    # ...
```

## 🚨 Troubleshooting

### API Server Won't Start

```bash
# Check if port is already in use
lsof -i :8001

# Check database connection
psql postgresql://industriverse:changeme@localhost:5432/industriverse

# Check Redis connection
redis-cli -h localhost -p 6379 PING
```

### TypeScript Client Errors

```typescript
// Enable debug logging
axios.interceptors.request.use(request => {
  console.log('Request:', request);
  return request;
});

// Check CORS issues
// Ensure API server has correct CORS configuration
```

### Database Connection Issues

```bash
# Verify database is running
pg_isready -h localhost -p 5432

# Check database exists
psql -U postgres -l | grep industriverse

# Check schema exists
psql postgresql://industriverse:changeme@localhost:5432/industriverse \
  -c "SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'behavioral';"
```

## 📈 Performance

### Caching Strategy

- Behavioral vectors are cached in Redis for 30 minutes
- Cache is invalidated when vector is recomputed
- Manual cache clear available via API

### Connection Pooling

```python
# Configure in behavioral_tracking_api.py
db_pool = await create_pool(
    host='localhost',
    port=5432,
    database='industriverse',
    user='industriverse',
    password='changeme',
    min_size=5,      # Minimum connections
    max_size=20,     # Maximum connections
)
```

### Async Operations

All operations are async for maximum throughput:

```python
# Concurrent operations
results = await asyncio.gather(
    client.track_interaction(event1),
    client.track_interaction(event2),
    client.track_interaction(event3),
)
```

## 📝 Changelog

### Week 17 Day 2 (2025-11-18)
- ✅ Created Python behavioral tracking client
- ✅ Created FastAPI REST API endpoints
- ✅ Created TypeScript client with React hook
- ✅ Added comprehensive documentation
- ✅ Integrated with unified database schema
- ✅ Added caching with Redis
- ✅ Added Kafka integration for real-time events

## 🤝 Contributing

When extending the API bridge:

1. Add new endpoints to `behavioral_tracking_api.py`
2. Add corresponding methods to `behavioral_tracking_client.py`
3. Update TypeScript client with new methods
4. Update this README with examples
5. Add tests for new functionality

## 📧 Support

For issues with the API bridge:
- Check [COMPREHENSIVE_ENHANCEMENT_ANALYSIS.md](../../../../COMPREHENSIVE_ENHANCEMENT_ANALYSIS.md)
- Review [Week 17 Development Log](../../../../docs/week17_development_log.md)
- Check database setup: [database/README.md](../../../../database/README.md)
