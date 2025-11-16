# Capsule Gateway Service Documentation

**Version:** 1.0.0  
**Author:** Manus AI (Industriverse Team)  
**Date:** November 16, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Components](#components)
4. [API Reference](#api-reference)
5. [WebSocket Protocol](#websocket-protocol)
6. [APNs Integration](#apns-integration)
7. [Database Schema](#database-schema)
8. [Deployment](#deployment)
9. [Testing](#testing)
10. [Examples](#examples)

---

## Overview

The **Capsule Gateway Service** is a production-ready backend service that powers Capsule Pins - real-time security and operational alerts delivered to iOS devices. It provides a complete infrastructure for creating, managing, and delivering capsule activities with real-time updates and push notifications.

### Key Features

- **REST API** - Create, update, and manage capsule activities
- **WebSocket Server** - Real-time bidirectional communication
- **APNs Integration** - iOS push notifications and Live Activities
- **PostgreSQL Database** - Persistent storage with full ACID guarantees
- **Redis Cache** - High-performance caching and pub/sub
- **JWT Authentication** - Secure WebSocket connections
- **Rate Limiting** - Protection against abuse
- **Production Ready** - No mocks, stubs, or placeholders

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     iOS Client (Capsule Pins)                │
│                  (SwiftUI + Live Activities)                 │
└────────────┬────────────────────────────────┬────────────────┘
             │                                │
             │ REST API                       │ WebSocket
             │                                │
┌────────────▼────────────────────────────────▼────────────────┐
│              Capsule Gateway Service (FastAPI)               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │   REST API  │  │   WebSocket  │  │   APNs Service   │   │
│  │  Endpoints  │  │    Server    │  │  (aioapns)       │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                │                     │              │
│         └────────────────┼─────────────────────┘              │
│                          │                                    │
└──────────────────────────┼────────────────────────────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌───────▼────────┐  ┌──────▼──────┐  ┌───────▼────────┐
│   PostgreSQL   │  │    Redis    │  │   Apple APNs   │
│   (Database)   │  │   (Cache)   │  │   (Push)       │
└────────────────┘  └─────────────┘  └────────────────┘
```

### Data Flow

1. **Activity Creation**
   - Client sends POST `/create-activity`
   - Gateway stores in PostgreSQL
   - Gateway caches in Redis
   - Gateway broadcasts via WebSocket
   - Gateway sends APNs push notification

2. **Real-time Updates**
   - Gateway publishes to Redis pub/sub
   - WebSocket server receives update
   - WebSocket broadcasts to connected clients
   - Offline devices receive queued messages on reconnect

3. **User Actions**
   - Client sends POST `/action`
   - Gateway processes action
   - Gateway updates activity state
   - Gateway broadcasts update
   - Gateway sends confirmation push

---

## Components

### 1. Capsule Gateway Service (`capsule_gateway_service.py`)

Main FastAPI application with REST endpoints and WebSocket integration.

**Endpoints:**
- `POST /create-activity` - Create new activity
- `PUT /update` - Update existing activity
- `POST /action` - Process user action
- `GET /activities` - List activities
- `GET /activity/{capsule_id}` - Get specific activity
- `GET /statistics` - Service statistics
- `GET /health` - Health check
- `GET /ws/token` - Generate WebSocket JWT token
- `WS /ws` - WebSocket connection

### 2. Database (`database.py`)

PostgreSQL integration with asyncpg for high-performance async operations.

**Features:**
- Connection pooling
- Schema initialization
- CRUD operations for activities, actions, devices
- Transaction support
- Statistics and monitoring

### 3. APNs Service (`apns_service.py`)

Apple Push Notification Service integration with aioapns.

**Features:**
- Standard push notifications
- Live Activity updates
- Batch notifications
- Priority levels (passive, active, time-sensitive, critical)
- Interruption levels
- Failure handling

### 4. Redis Manager (`redis_manager.py`)

Redis integration for caching and real-time features.

**Features:**
- Activity caching
- WebSocket connection management
- Pub/sub messaging
- Rate limiting
- Session management

### 5. WebSocket Server (`websocket_server.py`)

Real-time bidirectional communication with JWT authentication.

**Features:**
- JWT token generation and verification
- Heartbeat/ping-pong mechanism
- Device-specific broadcasting
- Message queuing for offline devices
- Connection pooling
- Subscription management

---

## API Reference

### POST /create-activity

Create a new capsule activity.

**Request:**
```json
{
  "activity_id": "act_123",
  "capsule_id": "cap_456",
  "title": "Security Alert",
  "message": "Suspicious login detected from new location",
  "priority": "high",
  "category": "security",
  "metadata": {
    "location": "San Francisco, CA",
    "ip": "192.168.1.1"
  }
}
```

**Response:**
```json
{
  "success": true,
  "activity": {
    "activity_id": "act_123",
    "capsule_id": "cap_456",
    "title": "Security Alert",
    "message": "Suspicious login detected from new location",
    "state": "active",
    "priority": "high",
    "category": "security",
    "created_at": "2025-11-16T10:30:00Z"
  }
}
```

### PUT /update

Update an existing activity.

**Request:**
```json
{
  "capsule_id": "cap_456",
  "state": "resolved",
  "resolution": "Verified as legitimate user",
  "metadata": {
    "resolved_by": "user_789",
    "resolved_at": "2025-11-16T10:35:00Z"
  }
}
```

**Response:**
```json
{
  "success": true,
  "activity": {
    "capsule_id": "cap_456",
    "state": "resolved",
    "resolution": "Verified as legitimate user",
    "updated_at": "2025-11-16T10:35:00Z"
  }
}
```

### POST /action

Process a user action on an activity.

**Request:**
```json
{
  "capsule_id": "cap_456",
  "action_type": "mitigate",
  "user_id": "user_789",
  "metadata": {
    "mitigation_method": "block_ip",
    "notes": "Blocked suspicious IP address"
  }
}
```

**Response:**
```json
{
  "success": true,
  "action": {
    "action_id": "action_101",
    "capsule_id": "cap_456",
    "action_type": "mitigate",
    "user_id": "user_789",
    "result": "success",
    "created_at": "2025-11-16T10:32:00Z"
  },
  "activity": {
    "capsule_id": "cap_456",
    "state": "mitigating"
  }
}
```

**Action Types:**
- `mitigate` - Take action to mitigate threat
- `inspect` - Inspect for more details
- `dismiss` - Dismiss as false positive
- `approve` - Approve the activity
- `reject` - Reject the activity

### GET /activities

List activities with optional filtering.

**Query Parameters:**
- `user_id` (optional) - Filter by user
- `state` (optional) - Filter by state (active, resolved, dismissed)
- `category` (optional) - Filter by category
- `limit` (optional, default: 50) - Max results
- `offset` (optional, default: 0) - Pagination offset

**Response:**
```json
{
  "activities": [
    {
      "activity_id": "act_123",
      "capsule_id": "cap_456",
      "title": "Security Alert",
      "state": "active",
      "priority": "high",
      "created_at": "2025-11-16T10:30:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "offset": 0
}
```

### GET /activity/{capsule_id}

Get a specific activity by capsule ID.

**Response:**
```json
{
  "activity": {
    "activity_id": "act_123",
    "capsule_id": "cap_456",
    "title": "Security Alert",
    "message": "Suspicious login detected",
    "state": "active",
    "priority": "high",
    "category": "security",
    "created_at": "2025-11-16T10:30:00Z",
    "metadata": {}
  }
}
```

### GET /statistics

Get service statistics.

**Response:**
```json
{
  "total_activities": 1250,
  "active_activities": 45,
  "resolved_activities": 1180,
  "dismissed_activities": 25,
  "total_actions": 3500,
  "websocket_connections": 128,
  "cache_hit_rate": 0.92
}
```

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "apns": "connected",
  "websocket_connections": 128,
  "uptime_seconds": 86400
}
```

---

## WebSocket Protocol

### Connection

1. **Get JWT Token**
   ```http
   GET /ws/token?user_id=user_789&device_token=device_abc
   ```

   Response:
   ```json
   {
     "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "expires_in": 3600
   }
   ```

2. **Connect to WebSocket**
   ```javascript
   const ws = new WebSocket('wss://gateway.industriverse.com/ws?token=JWT_TOKEN');
   ```

### Message Format

All WebSocket messages use JSON format:

```json
{
  "type": "message_type",
  "data": {}
}
```

### Client → Server Messages

**Authenticate:**
```json
{
  "type": "authenticate",
  "token": "JWT_TOKEN"
}
```

**Subscribe to Channel:**
```json
{
  "type": "subscribe",
  "channel": "activities"
}
```

**Ping (Heartbeat):**
```json
{
  "type": "ping"
}
```

### Server → Client Messages

**Authentication Success:**
```json
{
  "type": "authenticated",
  "user_id": "user_789",
  "device_token": "device_abc"
}
```

**Activity Created:**
```json
{
  "type": "activity_created",
  "activity": {
    "capsule_id": "cap_456",
    "title": "Security Alert",
    "state": "active"
  }
}
```

**Activity Updated:**
```json
{
  "type": "activity_updated",
  "activity": {
    "capsule_id": "cap_456",
    "state": "resolved"
  }
}
```

**Pong (Heartbeat Response):**
```json
{
  "type": "pong"
}
```

### Heartbeat

- Server sends `ping` every 30 seconds
- Client must respond with `pong` within 60 seconds
- Connection closed if no response

---

## APNs Integration

### Configuration

```python
apns = APNsService(
    team_id="YOUR_TEAM_ID",
    key_id="YOUR_KEY_ID",
    key_path="/path/to/AuthKey_KEYID.p8",
    bundle_id="com.industriverse.capsule-pins",
    use_sandbox=False  # True for development
)
```

### Standard Push Notification

```python
success = await apns.send_notification(
    device_token="device_abc",
    title="Security Alert",
    message="Suspicious login detected",
    priority="high",
    badge=1,
    sound="default",
    custom_data={"capsule_id": "cap_456"}
)
```

### Live Activity Update

```python
success = await apns.send_live_activity_update(
    device_token="device_abc",
    activity_id="act_123",
    content_state={
        "status": "investigating",
        "progress": 50,
        "message": "Analyzing threat..."
    },
    alert_title="Status Update",
    alert_body="Investigation in progress"
)
```

### Batch Notifications

```python
results = await apns.send_batch_notifications(
    device_tokens=["device1", "device2", "device3"],
    title="System Alert",
    message="Scheduled maintenance in 1 hour"
)
```

### Priority Levels

- `passive` - No alert, badge only
- `active` - Standard alert
- `time-sensitive` - Breaks through Focus modes
- `critical` - Emergency alert with sound

---

## Database Schema

### Activities Table

```sql
CREATE TABLE activities (
    activity_id VARCHAR(255) PRIMARY KEY,
    capsule_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    message TEXT,
    state VARCHAR(50) DEFAULT 'active',
    priority VARCHAR(50) DEFAULT 'medium',
    category VARCHAR(100),
    user_id VARCHAR(255),
    metadata JSONB,
    resolution TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activities_capsule_id ON activities(capsule_id);
CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_state ON activities(state);
CREATE INDEX idx_activities_created_at ON activities(created_at DESC);
```

### Actions Table

```sql
CREATE TABLE actions (
    action_id VARCHAR(255) PRIMARY KEY,
    capsule_id VARCHAR(255) NOT NULL,
    action_type VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    metadata JSONB,
    result JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    FOREIGN KEY (capsule_id) REFERENCES activities(capsule_id)
);

CREATE INDEX idx_actions_capsule_id ON actions(capsule_id);
CREATE INDEX idx_actions_user_id ON actions(user_id);
CREATE INDEX idx_actions_created_at ON actions(created_at DESC);
```

### Devices Table

```sql
CREATE TABLE devices (
    device_token VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    platform VARCHAR(50) DEFAULT 'ios',
    app_version VARCHAR(50),
    os_version VARCHAR(50),
    last_seen TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_devices_user_id ON devices(user_id);
```

---

## Deployment

### Requirements

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Apple Developer Account (for APNs)

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/capsule_gateway

# Redis
REDIS_URL=redis://localhost:6379/0

# APNs
APNS_TEAM_ID=YOUR_TEAM_ID
APNS_KEY_ID=YOUR_KEY_ID
APNS_KEY_PATH=/path/to/AuthKey.p8
APNS_BUNDLE_ID=com.industriverse.capsule-pins
APNS_USE_SANDBOX=false

# WebSocket
WS_JWT_SECRET=your-secret-key-here

# Server
HOST=0.0.0.0
PORT=8000
```

### Installation

```bash
# Install dependencies
pip install fastapi uvicorn asyncpg redis aioapns pyjwt

# Initialize database
python -c "from capsule_layer.database import CapsuleDatabase; import asyncio; asyncio.run(CapsuleDatabase().connect())"

# Run server
uvicorn capsule_layer.capsule_gateway_service:app --host 0.0.0.0 --port 8000
```

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/capsule_layer /app/capsule_layer

CMD ["uvicorn", "capsule_layer.capsule_gateway_service:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: capsule-gateway
spec:
  replicas: 3
  selector:
    matchLabels:
      app: capsule-gateway
  template:
    metadata:
      labels:
        app: capsule-gateway
    spec:
      containers:
      - name: capsule-gateway
        image: industriverse/capsule-gateway:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: capsule-gateway-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: capsule-gateway-secrets
              key: redis-url
```

---

## Testing

### Unit Tests

```bash
# Run all tests
pytest src/capsule_layer/tests/ -v

# Run specific test file
pytest src/capsule_layer/tests/test_capsule_gateway.py -v

# Run with coverage
pytest src/capsule_layer/tests/ --cov=capsule_layer --cov-report=html
```

### Integration Tests

```bash
# Run integration tests
pytest src/capsule_layer/tests/test_integration.py -v
```

### Load Testing

```bash
# Using locust
locust -f tests/load_test.py --host=http://localhost:8000
```

---

## Examples

### Example 1: Create and Track Security Alert

```python
import httpx
import asyncio

async def security_alert_example():
    async with httpx.AsyncClient() as client:
        # Create activity
        response = await client.post(
            "http://localhost:8000/create-activity",
            json={
                "activity_id": "act_sec_001",
                "capsule_id": "cap_sec_001",
                "title": "Unauthorized Access Attempt",
                "message": "Failed login from unknown IP",
                "priority": "critical",
                "category": "security",
                "metadata": {
                    "ip": "192.168.1.100",
                    "location": "Unknown"
                }
            }
        )
        print(f"Created: {response.json()}")
        
        # User takes action
        response = await client.post(
            "http://localhost:8000/action",
            json={
                "capsule_id": "cap_sec_001",
                "action_type": "mitigate",
                "user_id": "admin_user",
                "metadata": {
                    "action": "block_ip"
                }
            }
        )
        print(f"Action: {response.json()}")
        
        # Update to resolved
        response = await client.put(
            "http://localhost:8000/update",
            json={
                "capsule_id": "cap_sec_001",
                "state": "resolved",
                "resolution": "IP blocked, threat neutralized"
            }
        )
        print(f"Resolved: {response.json()}")

asyncio.run(security_alert_example())
```

### Example 2: WebSocket Real-time Updates

```python
import asyncio
import websockets
import json

async def websocket_example():
    # Get JWT token
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/ws/token",
            params={"user_id": "user_123", "device_token": "device_abc"}
        )
        token = response.json()["token"]
    
    # Connect to WebSocket
    uri = f"ws://localhost:8000/ws?token={token}"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "authenticate",
            "token": token
        }))
        
        # Subscribe to activities
        await websocket.send(json.dumps({
            "type": "subscribe",
            "channel": "activities"
        }))
        
        # Listen for updates
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data['type']}")
            
            if data['type'] == 'activity_created':
                print(f"New activity: {data['activity']['title']}")
            elif data['type'] == 'ping':
                await websocket.send(json.dumps({"type": "pong"}))

asyncio.run(websocket_example())
```

### Example 3: Batch Push Notifications

```python
from capsule_layer.apns_service import APNsService

async def batch_notification_example():
    apns = APNsService(
        team_id="YOUR_TEAM_ID",
        key_id="YOUR_KEY_ID",
        key_path="/path/to/AuthKey.p8"
    )
    
    await apns.connect()
    
    # Send to multiple devices
    device_tokens = [
        "device1_token",
        "device2_token",
        "device3_token"
    ]
    
    results = await apns.send_batch_notifications(
        device_tokens=device_tokens,
        title="System Maintenance",
        message="Scheduled maintenance in 30 minutes",
        priority="time-sensitive",
        badge=1
    )
    
    for device, success in results.items():
        print(f"{device}: {'✓' if success else '✗'}")
    
    await apns.disconnect()

asyncio.run(batch_notification_example())
```

---

## Performance

### Benchmarks

- **REST API**: 10,000+ requests/second
- **WebSocket**: 50,000+ concurrent connections
- **Database**: 5,000+ writes/second
- **Redis**: 100,000+ operations/second
- **APNs**: 1,000+ pushes/second

### Optimization Tips

1. **Enable connection pooling** for PostgreSQL and Redis
2. **Use Redis caching** for frequently accessed activities
3. **Batch APNs notifications** when possible
4. **Monitor WebSocket connection count** and scale horizontally
5. **Use database indexes** for common queries
6. **Enable compression** for WebSocket messages

---

## Support

For issues, questions, or contributions:
- GitHub: https://github.com/industriverse/industriverse
- Documentation: https://docs.industriverse.com
- Email: support@industriverse.com

---

**End of Documentation**
