# Week 16: Complete DAC Factory Architecture

**Mission:** Build production-ready end-to-end system connecting factory sensors to capsule visualization and interaction.

**Date:** November 18, 2025  
**Status:** In Progress

---

## 🎯 **System Overview**

The **DAC (Data-as-a-Capsule) Factory** is a complete industrial intelligence system that:

1. **Ingests** sensor data from factory equipment
2. **Transforms** raw data into actionable capsules
3. **Distributes** capsules to multiple client applications
4. **Enables** real-time interaction (acknowledge, mitigate, dismiss)
5. **Visualizes** data as living art (AR/VR, generative graphics)
6. **Learns** from worker actions (Ambient Intelligence)

---

## 🏗️ **Architecture Layers**

```
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 1: SENSOR INGESTION                                       │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│ │ MQTT Broker  │  │ OPC-UA       │  │ HTTP Polling │           │
│ │ (IoT devices)│  │ (PLCs)       │  │ (REST APIs)  │           │
│ └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 2: CAPSULE CREATION ENGINE                                │
│ - Rule-based capsule generation                                 │
│ - Threshold detection (temperature, pressure, vibration)        │
│ - Anomaly detection (ML models)                                 │
│ - Time-series analysis                                           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 3: CAPSULE GATEWAY SERVICE                                │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│ │ WebSocket    │  │ REST API     │  │ Database     │           │
│ │ Server       │  │ (Actions)    │  │ (PostgreSQL) │           │
│ └──────────────┘  └──────────────┘  └──────────────┘           │
└────────────────────────┬────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 4: CLIENT APPLICATIONS                                    │
│ ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│ │ PWA (Web)    │  │ Android      │  │ Desktop      │           │
│ │ + AR/VR      │  │ Native       │  │ Electron     │           │
│ └──────────────┘  └──────────────┘  └──────────────┘           │
└─────────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│ LAYER 5: AMBIENT INTELLIGENCE                                   │
│ - Pattern learning from worker actions                           │
│ - Proactive predictions                                          │
│ - Cross-deployment intelligence sharing                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 **Component Details**

### **1. Sensor Ingestion Pipeline**

**Purpose:** Connect to factory sensors and normalize data

**Protocols Supported:**
- **MQTT** - IoT devices (temperature, humidity, vibration sensors)
- **OPC-UA** - Industrial PLCs (Siemens, Allen-Bradley, Schneider)
- **Modbus TCP** - Legacy equipment
- **HTTP REST** - Cloud APIs (weather, supply chain)

**Data Flow:**
```
Sensor → Protocol Adapter → Data Normalizer → Capsule Creation Engine
```

**Implementation:**
- `server/services/SensorIngestion.ts` - Main ingestion service
- `server/adapters/MQTTAdapter.ts` - MQTT protocol handler
- `server/adapters/OPCUAAdapter.ts` - OPC-UA protocol handler
- `server/adapters/HTTPAdapter.ts` - HTTP polling handler

**Configuration:**
```typescript
interface SensorConfig {
  id: string;
  name: string;
  protocol: 'mqtt' | 'opcua' | 'modbus' | 'http';
  endpoint: string;
  credentials?: {
    username: string;
    password: string;
  };
  pollInterval?: number; // For HTTP
  dataMapping: {
    temperature?: string;
    pressure?: string;
    vibration?: string;
    [key: string]: string;
  };
}
```

---

### **2. Capsule Creation Engine**

**Purpose:** Transform sensor data into actionable capsules

**Rules Engine:**
```typescript
interface CapsuleRule {
  id: string;
  name: string;
  condition: {
    sensor: string;
    operator: '>' | '<' | '==' | '!=' | 'anomaly';
    threshold?: number;
    timeWindow?: number; // seconds
  };
  capsule: {
    title: string;
    description: string;
    status: 'active' | 'warning' | 'critical';
    priority: 'low' | 'medium' | 'high' | 'critical';
    category: string; // From 27 capsule taxonomy
    metadata: Record<string, any>;
  };
}
```

**Example Rules:**
```typescript
// Temperature threshold
{
  id: 'temp_critical',
  name: 'Motor Overheating',
  condition: {
    sensor: 'motor_001_temp',
    operator: '>',
    threshold: 80
  },
  capsule: {
    title: 'Motor 001 Overheating',
    description: 'Temperature exceeded 80°C',
    status: 'critical',
    priority: 'critical',
    category: 'equipment_health',
    metadata: {
      equipmentId: 'motor_001',
      location: 'Assembly Line 3'
    }
  }
}

// Vibration anomaly
{
  id: 'vibration_anomaly',
  name: 'Abnormal Vibration Detected',
  condition: {
    sensor: 'motor_001_vibration',
    operator: 'anomaly',
    timeWindow: 300 // 5 minutes
  },
  capsule: {
    title: 'Abnormal Vibration - Motor 001',
    description: 'Vibration pattern deviates from normal',
    status: 'warning',
    priority: 'high',
    category: 'predictive_maintenance',
    metadata: {
      equipmentId: 'motor_001',
      anomalyScore: 0.85
    }
  }
}
```

**Implementation:**
- `server/services/CapsuleCreationEngine.ts` - Main engine
- `server/rules/` - Rule definitions (JSON files)
- `server/ml/AnomalyDetector.ts` - ML-based anomaly detection

---

### **3. Capsule Gateway Service**

**Purpose:** Real-time capsule distribution and action handling

**WebSocket Server:**
```typescript
// Connection
wss://capsule-gateway.industriverse.io/ws?token=JWT_TOKEN

// Incoming messages (from clients)
{
  type: 'subscribe',
  capsuleIds: string[] | 'all'
}

{
  type: 'action',
  capsuleId: string,
  action: 'acknowledge' | 'mitigate' | 'inspect' | 'dismiss' | 'escalate',
  metadata?: Record<string, any>
}

{
  type: 'heartbeat',
  timestamp: string
}

// Outgoing messages (to clients)
{
  type: 'capsule_new',
  data: CapsuleData
}

{
  type: 'capsule_update',
  data: {
    capsuleId: string,
    updates: Partial<CapsuleData>
  }
}

{
  type: 'capsule_removed',
  data: { capsuleId: string }
}

{
  type: 'heartbeat',
  data: { timestamp: string }
}
```

**REST API:**
```
GET    /api/v1/capsules              - List all capsules
GET    /api/v1/capsules/:id          - Get capsule by ID
POST   /api/v1/capsules              - Create capsule (manual)
PUT    /api/v1/capsules/:id          - Update capsule
DELETE /api/v1/capsules/:id          - Delete capsule
POST   /api/v1/capsules/:id/action   - Execute action
GET    /api/v1/capsules/statistics   - Get statistics
GET    /api/v1/sensors               - List sensors
POST   /api/v1/sensors               - Add sensor
GET    /api/v1/rules                 - List rules
POST   /api/v1/rules                 - Add rule
```

**Implementation:**
- `server/websocket/CapsuleGateway.ts` - WebSocket server
- `server/routes/capsules.ts` - REST API routes
- `server/routes/sensors.ts` - Sensor management routes
- `server/routes/rules.ts` - Rule management routes

---

### **4. Database Schema**

**Capsules Table:**
```sql
CREATE TABLE capsules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  description TEXT,
  status VARCHAR(50) NOT NULL, -- active, warning, critical, resolved, dismissed
  priority VARCHAR(50) NOT NULL, -- low, medium, high, critical
  category VARCHAR(100) NOT NULL,
  source_sensor_id UUID REFERENCES sensors(id),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  resolved_at TIMESTAMP,
  resolved_by UUID REFERENCES users(id),
  metadata JSONB,
  metrics JSONB -- { temperature: 85, pressure: 60, vibration: 70 }
);

CREATE INDEX idx_capsules_status ON capsules(status);
CREATE INDEX idx_capsules_priority ON capsules(priority);
CREATE INDEX idx_capsules_created_at ON capsules(created_at DESC);
```

**Sensors Table:**
```sql
CREATE TABLE sensors (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  protocol VARCHAR(50) NOT NULL, -- mqtt, opcua, modbus, http
  endpoint TEXT NOT NULL,
  credentials JSONB,
  poll_interval INTEGER, -- seconds
  data_mapping JSONB NOT NULL,
  status VARCHAR(50) DEFAULT 'active', -- active, inactive, error
  last_reading_at TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Rules Table:**
```sql
CREATE TABLE capsule_rules (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  sensor_id UUID REFERENCES sensors(id),
  condition JSONB NOT NULL,
  capsule_template JSONB NOT NULL,
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

**Actions Table:**
```sql
CREATE TABLE capsule_actions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  capsule_id UUID REFERENCES capsules(id),
  action VARCHAR(50) NOT NULL, -- acknowledge, mitigate, inspect, dismiss, escalate
  performed_by UUID REFERENCES users(id),
  performed_at TIMESTAMP DEFAULT NOW(),
  metadata JSONB,
  result VARCHAR(50), -- success, failure, pending
  result_message TEXT
);

CREATE INDEX idx_actions_capsule_id ON capsule_actions(capsule_id);
CREATE INDEX idx_actions_performed_at ON capsule_actions(performed_at DESC);
```

---

### **5. AR/VR Integration**

**Purpose:** Bring Week 15 AR/VR work into PWA

**Components to Port:**
1. **MediaPipe Hands Controller** - Gesture-free capsule selection
2. **MediaPipe Pose Controller** - Body language commands
3. **TouchDesigner Visualizer** - Generative capsule art
4. **3DGS Shadow Twin Viewer** - Photorealistic factory twins

**Integration Points:**
```typescript
// Add AR/VR mode toggle in PWA
interface AppMode {
  mode: '2d' | '3d' | 'ar' | 'vr';
  features: {
    handTracking: boolean;
    poseTracking: boolean;
    generativeArt: boolean;
    shadowTwin: boolean;
  };
}

// Enable AR/VR in Home.tsx
<ARVRContainer mode={appMode}>
  <CapsuleList capsules={capsules} />
  <HandTrackingOverlay />
  <GenerativeVisualizer />
  <ShadowTwinViewer />
</ARVRContainer>
```

**Files to Create:**
- `client/src/components/ar-vr/MediaPipeHandsController.tsx`
- `client/src/components/ar-vr/MediaPipePoseController.tsx`
- `client/src/components/ar-vr/TouchDesignerVisualizer.tsx`
- `client/src/components/ar-vr/ShadowTwinViewer.tsx`
- `client/src/components/ar-vr/ARVRContainer.tsx`

---

### **6. Deployment Architecture**

**Docker Compose Stack:**
```yaml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: dac_factory
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
  
  # Capsule Gateway Service
  capsule-gateway:
    build: ./server
    environment:
      DATABASE_URL: postgresql://admin:${DB_PASSWORD}@postgres:5432/dac_factory
      JWT_SECRET: ${JWT_SECRET}
      MQTT_BROKER: ${MQTT_BROKER}
      OPCUA_ENDPOINT: ${OPCUA_ENDPOINT}
    ports:
      - "3001:3001" # REST API
      - "3002:3002" # WebSocket
    depends_on:
      - postgres
  
  # PWA Frontend
  pwa:
    build: ./client
    environment:
      VITE_CAPSULE_GATEWAY_API: http://capsule-gateway:3001
      VITE_CAPSULE_GATEWAY_WS: ws://capsule-gateway:3002
    ports:
      - "3000:3000"
    depends_on:
      - capsule-gateway
  
  # MQTT Broker (for IoT sensors)
  mosquitto:
    image: eclipse-mosquitto:2
    volumes:
      - ./mosquitto/config:/mosquitto/config
      - mosquitto_data:/mosquitto/data
    ports:
      - "1883:1883" # MQTT
      - "9001:9001" # WebSocket

volumes:
  postgres_data:
  mosquitto_data:
```

**Kubernetes Manifests:**
- `k8s/postgres-deployment.yaml`
- `k8s/capsule-gateway-deployment.yaml`
- `k8s/pwa-deployment.yaml`
- `k8s/mosquitto-deployment.yaml`
- `k8s/ingress.yaml`

---

## 🔐 **Security**

### **Authentication**
- JWT tokens for all API/WebSocket connections
- Token expiration: 24 hours
- Refresh tokens: 30 days
- Role-based access control (RBAC)

### **Authorization**
- **Admin:** Full access (sensors, rules, capsules, users)
- **Operator:** View capsules, execute actions
- **Viewer:** Read-only access

### **Data Protection**
- TLS 1.3 for all connections
- Database encryption at rest
- Sensitive data (credentials) encrypted with AES-256
- GDPR compliance (data retention policies)

---

## 📊 **Monitoring & Observability**

### **Metrics**
- Capsule creation rate (capsules/minute)
- WebSocket connections (active clients)
- Action execution time (ms)
- Sensor ingestion latency (ms)
- Database query performance (ms)

### **Logging**
- Structured JSON logs
- Log levels: DEBUG, INFO, WARN, ERROR
- Centralized logging (ELK stack or Loki)

### **Alerting**
- Sensor disconnection alerts
- High capsule creation rate (> 100/min)
- WebSocket connection failures
- Database connection pool exhaustion

---

## 🚀 **Performance Targets**

| Metric | Target | Critical |
|--------|--------|----------|
| **Sensor Ingestion Latency** | < 100ms | < 500ms |
| **Capsule Creation Time** | < 50ms | < 200ms |
| **WebSocket Message Latency** | < 30ms | < 100ms |
| **REST API Response Time** | < 100ms | < 500ms |
| **Database Query Time** | < 50ms | < 200ms |
| **Concurrent WebSocket Clients** | 1,000+ | 500+ |
| **Capsules/Minute** | 1,000+ | 500+ |

---

## 📚 **Documentation Deliverables**

1. **Factory Operator Guide** - How to use capsule system
2. **Admin Deployment Manual** - How to deploy DAC Factory
3. **Sensor Integration Guide** - How to connect sensors
4. **Rule Configuration Guide** - How to create capsule rules
5. **API Reference** - Complete REST API documentation
6. **WebSocket Protocol Spec** - Message format reference
7. **Troubleshooting Guide** - Common issues and solutions

---

## ✅ **Week 16 Completion Criteria**

- [ ] Sensor ingestion working with MQTT and OPC-UA
- [ ] Capsule creation engine generating capsules from rules
- [ ] Capsule Gateway WebSocket server broadcasting real-time
- [ ] REST API endpoints functional
- [ ] Database schema deployed and tested
- [ ] AR/VR components integrated into PWA
- [ ] Docker Compose stack running complete system
- [ ] Kubernetes manifests ready for production
- [ ] All documentation complete
- [ ] End-to-end testing passed (97%+ pass rate)

---

**Status:** Architecture defined. Ready for implementation! 🚀
