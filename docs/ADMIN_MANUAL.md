# Capsule Pins - Administrator Manual
**Week 16: DAC Factory System Administration**

Complete reference for IT administrators, DevOps engineers, and system integrators deploying and managing the Capsule Pins DAC Factory.

---

## 📋 **Table of Contents**

1. [System Architecture](#system-architecture)
2. [Installation & Configuration](#installation--configuration)
3. [User Management](#user-management)
4. [Sensor Integration](#sensor-integration)
5. [Capsule Rules Engine](#capsule-rules-engine)
6. [Shadow Twin Consensus](#shadow-twin-consensus)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Security & Compliance](#security--compliance)
9. [Backup & Recovery](#backup--recovery)
10. [Troubleshooting](#troubleshooting)

---

## 🏗️ **System Architecture**

### **High-Level Overview**

```
┌─────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                        │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Web PWA     │  Android     │  Desktop     │  AR/VR Interface  │
│  (React 19)  │  Native      │  Electron    │  (MediaPipe)      │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Capsule     │  Sensor      │  WebSocket   │  Shadow Twin      │
│  Gateway     │  Ingestion   │  Server      │  Consensus Client │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                               │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  PostgreSQL  │  Redis       │  MQTT Broker │  S3 Storage       │
│  (Capsules)  │  (Cache)     │  (Sensors)   │  (Files)          │
└──────────────┴──────────────┴──────────────┴───────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│                     INFRASTRUCTURE LAYER                         │
├──────────────┬──────────────┬──────────────┬───────────────────┤
│  Docker      │  Kubernetes  │  Prometheus  │  Grafana/Loki     │
│  Compose     │  Cluster     │  (Metrics)   │  (Logs)           │
└──────────────┴──────────────┴──────────────┴───────────────────┘
```

### **Component Responsibilities**

| Component | Purpose | Technology | Scalability |
|-----------|---------|------------|-------------|
| **Capsule Gateway** | WebSocket server, capsule broadcasting | Node.js + ws | Horizontal (3-10 pods) |
| **Sensor Ingestion** | MQTT/OPC-UA data collection | Node.js + mqtt/opcua | Horizontal (2-5 pods) |
| **Capsule Engine** | Rules evaluation, consensus validation | TypeScript | Stateful (1-3 instances) |
| **PostgreSQL** | Capsule persistence, user data | PostgreSQL 16 | Vertical + Read replicas |
| **MQTT Broker** | Sensor message bus | Mosquitto 2.0 | Vertical (single instance) |
| **Redis** | Session cache, rate limiting | Redis 7 | Vertical + Sentinel |

---

## 🔧 **Installation & Configuration**

### **Prerequisites Checklist**

```bash
# System requirements
- [ ] CPU: 8+ cores
- [ ] RAM: 16+ GB
- [ ] Storage: 100+ GB SSD
- [ ] OS: Ubuntu 22.04 LTS / RHEL 8+

# Software dependencies
- [ ] Docker 24.0+
- [ ] Docker Compose 2.20+
- [ ] kubectl 1.28+ (for K8s)
- [ ] PostgreSQL client tools
- [ ] OpenSSL (for certificates)

# Network requirements
- [ ] Outbound HTTPS (443) - For external APIs
- [ ] Inbound HTTPS (443) - For web access
- [ ] Inbound MQTT (1883) - For sensors
- [ ] Inbound WebSocket (9001) - For real-time updates
```

### **Quick Start (Docker Compose)**

```bash
# 1. Clone repository
git clone https://github.com/your-org/capsule-pins-pwa.git
cd capsule-pins-pwa

# 2. Configure environment
cp .env.example .env
nano .env  # Edit configuration

# 3. Generate secrets
./scripts/generate-secrets.sh

# 4. Start services
docker-compose up -d

# 5. Initialize database
docker-compose exec app pnpm db:push

# 6. Create admin user
docker-compose exec app node scripts/create-admin.js \
  --email admin@your-factory.com \
  --password "SecurePassword123!"

# 7. Verify deployment
curl http://localhost:3000/health
```

### **Production Deployment (Kubernetes)**

```bash
# 1. Create namespace
kubectl create namespace dac-factory

# 2. Configure secrets
kubectl create secret generic dac-factory-secrets \
  --from-env-file=.env.production \
  -n dac-factory

# 3. Deploy infrastructure
kubectl apply -f k8s/postgres.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/mqtt.yaml

# 4. Wait for infrastructure
kubectl wait --for=condition=ready pod \
  -l app=postgres -n dac-factory --timeout=300s

# 5. Deploy application
kubectl apply -f k8s/deployment.yaml

# 6. Configure ingress
kubectl apply -f k8s/ingress.yaml

# 7. Verify deployment
kubectl get pods -n dac-factory
kubectl logs -f deployment/capsule-pins-app -n dac-factory
```

### **Environment Configuration**

**Critical Variables:**

```env
# Database (REQUIRED)
DATABASE_URL=postgresql://user:pass@host:5432/capsule_pins

# Redis (REQUIRED)
REDIS_URL=redis://:password@host:6379

# MQTT (REQUIRED)
MQTT_BROKER_URL=mqtt://mqtt-broker:1883

# JWT (REQUIRED - Generate with: openssl rand -base64 64)
JWT_SECRET=your_64_character_secret_here

# Shadow Twin Consensus (OPTIONAL)
SHADOW_TWIN_INTEGRATION_URL=http://integration-bridge/api/v1/predict
SHADOW_TWIN_CONTROLLER_URL=http://controller/health
ENABLE_CONSENSUS_VALIDATION=true

# Feature Flags
ENABLE_AR_VR_MODE=true
ENABLE_VOICE_COMMANDS=false
ENABLE_POSE_DETECTION=true

# Performance Tuning
MAX_WEBSOCKET_CONNECTIONS=10000
CAPSULE_RETENTION_DAYS=90
SENSOR_BUFFER_SIZE=1000
```

---

## 👥 **User Management**

### **User Roles**

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Full system access, user management | IT administrators |
| **Supervisor** | View all capsules, escalate, reports | Shift supervisors |
| **Operator** | View/acknowledge capsules, basic actions | Factory workers |
| **Viewer** | Read-only access | Executives, auditors |
| **API** | Programmatic access only | Integration systems |

### **Creating Users**

**Via CLI:**
```bash
# Create operator
docker-compose exec app node scripts/create-user.js \
  --email worker@factory.com \
  --password "TempPass123!" \
  --role operator \
  --name "John Doe"

# Create admin
kubectl exec -it deployment/capsule-pins-app -n dac-factory -- \
  node scripts/create-user.js \
  --email admin@factory.com \
  --password "AdminPass123!" \
  --role admin \
  --name "Admin User"
```

**Via API:**
```bash
curl -X POST https://your-factory-url.com/api/users \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@factory.com",
    "password": "SecurePass123!",
    "role": "operator",
    "name": "New User"
  }'
```

### **Bulk User Import**

```bash
# Prepare CSV file (users.csv)
email,password,role,name
worker1@factory.com,Pass123!,operator,Worker One
worker2@factory.com,Pass123!,operator,Worker Two
supervisor@factory.com,Pass123!,supervisor,Supervisor

# Import users
docker-compose exec app node scripts/import-users.js \
  --file /path/to/users.csv \
  --send-welcome-email
```

### **Password Policies**

Configure in `.env`:
```env
# Password requirements
PASSWORD_MIN_LENGTH=12
PASSWORD_REQUIRE_UPPERCASE=true
PASSWORD_REQUIRE_LOWERCASE=true
PASSWORD_REQUIRE_NUMBERS=true
PASSWORD_REQUIRE_SPECIAL=true
PASSWORD_EXPIRY_DAYS=90

# Account lockout
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=30
```

---

## 📡 **Sensor Integration**

### **Supported Protocols**

1. **MQTT** (Recommended for IoT sensors)
2. **OPC-UA** (Industrial PLCs)
3. **HTTP REST** (Custom sensors)
4. **WebSocket** (Real-time streams)

### **MQTT Sensor Configuration**

**Topic Structure:**
```
factory/{site_id}/{line_id}/{equipment_id}/{metric}

Example:
factory/austin/line3/motor001/temperature
factory/austin/line3/motor001/vibration
factory/austin/line3/motor001/power
```

**Message Format (JSON):**
```json
{
  "sensor_id": "motor001_temp",
  "equipment_id": "motor001",
  "metric": "temperature",
  "value": 78.5,
  "unit": "celsius",
  "timestamp": "2024-01-15T10:30:00Z",
  "quality": "good"
}
```

**Registering MQTT Sensor:**
```bash
curl -X POST https://your-factory-url.com/api/sensors \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "motor001_temp",
    "name": "Motor 001 Temperature",
    "type": "mqtt",
    "config": {
      "topic": "factory/austin/line3/motor001/temperature",
      "qos": 1
    },
    "equipment_id": "motor001",
    "metric": "temperature",
    "unit": "celsius",
    "min_value": 0,
    "max_value": 150,
    "normal_range": [20, 80]
  }'
```

### **OPC-UA Sensor Configuration**

**Registering OPC-UA Sensor:**
```bash
curl -X POST https://your-factory-url.com/api/sensors \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "plc001_pressure",
    "name": "PLC 001 Pressure",
    "type": "opcua",
    "config": {
      "endpoint": "opc.tcp://192.168.1.100:4840",
      "node_id": "ns=2;s=Pressure",
      "sampling_interval": 1000
    },
    "equipment_id": "plc001",
    "metric": "pressure",
    "unit": "psi"
  }'
```

### **Testing Sensor Connection**

```bash
# Test MQTT sensor
mosquitto_pub -h localhost -p 1883 \
  -t "factory/austin/line3/motor001/temperature" \
  -m '{"sensor_id":"motor001_temp","value":85.5,"timestamp":"2024-01-15T10:30:00Z"}'

# Verify in logs
docker-compose logs -f sensor-ingestion | grep motor001

# Check in dashboard
curl https://your-factory-url.com/api/sensors/motor001_temp/latest
```

---

## ⚙️ **Capsule Rules Engine**

### **Rule Structure**

```typescript
{
  id: string;              // Unique rule ID
  name: string;            // Human-readable name
  enabled: boolean;        // Enable/disable rule
  condition: {
    sensorId: string;      // Which sensor to monitor
    metric: string;        // Which metric (temperature, pressure, etc.)
    operator: '>' | '<' | '==' | '!=';
    threshold: number;     // Threshold value
    duration?: number;     // Optional: Must persist for X seconds
  };
  capsule: {
    title: string;         // Capsule title
    description: string;   // Capsule description
    status: 'critical' | 'warning' | 'active';
    priority: 'P1' | 'P2' | 'P3' | 'P4' | 'P5';
    category: string;      // Category (thermal, mechanical, etc.)
    actions: string[];     // Available actions
  };
}
```

### **Creating Rules**

**Via API:**
```bash
curl -X POST https://your-factory-url.com/api/capsule-rules \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "motor_overheat",
    "name": "Motor Overheating Alert",
    "enabled": true,
    "condition": {
      "sensorId": "motor001_temp",
      "metric": "temperature",
      "operator": ">",
      "threshold": 85,
      "duration": 30
    },
    "capsule": {
      "title": "Motor {{equipment_id}} Overheating",
      "description": "Temperature exceeded {{threshold}}°C for {{duration}} seconds",
      "status": "critical",
      "priority": "P1",
      "category": "thermal",
      "actions": ["acknowledge", "inspect", "emergency_stop"]
    }
  }'
```

**Via Configuration File:**
```yaml
# config/capsule-rules.yaml
rules:
  - id: motor_overheat
    name: Motor Overheating Alert
    enabled: true
    condition:
      sensorId: motor001_temp
      metric: temperature
      operator: ">"
      threshold: 85
      duration: 30
    capsule:
      title: "Motor {{equipment_id}} Overheating"
      description: "Temperature exceeded {{threshold}}°C"
      status: critical
      priority: P1
      category: thermal
      actions:
        - acknowledge
        - inspect
        - emergency_stop
```

Load rules:
```bash
docker-compose exec app node scripts/load-rules.js \
  --file /app/config/capsule-rules.yaml
```

### **Rule Templates**

**Temperature Monitoring:**
```javascript
{
  id: 'temp_high',
  condition: { metric: 'temperature', operator: '>', threshold: 85 },
  capsule: { status: 'critical', priority: 'P1' }
}
```

**Vibration Monitoring:**
```javascript
{
  id: 'vibration_high',
  condition: { metric: 'vibration', operator: '>', threshold: 50 },
  capsule: { status: 'warning', priority: 'P2' }
}
```

**Pressure Monitoring:**
```javascript
{
  id: 'pressure_high',
  condition: { metric: 'pressure', operator: '>', threshold: 90 },
  capsule: { status: 'critical', priority: 'P1' }
}
```

---

## 🤖 **Shadow Twin Consensus**

### **Architecture**

```
┌─────────────────────────────────────────────────────────┐
│                  Capsule Creation Request                │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Shadow Twin Consensus Client                │
│  (Validates capsule with distributed predictors)         │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
┌──────────────────┐              ┌──────────────────┐
│  Primary         │              │  Secondary       │
│  Predictor       │              │  Predictors      │
│  (Integration    │              │  (Controller,    │
│   Bridge)        │              │   Engine)        │
└──────────────────┘              └──────────────────┘
        ↓                                   ↓
        └─────────────────┬─────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│              Calculate PCT (Consensus Score)             │
│  PCT = 1.0 - (stdev / mean)                             │
│  Threshold: ≥ 90%                                       │
└─────────────────────────────────────────────────────────┘
                          ↓
        ┌─────────────────┴─────────────────┐
        ↓                                   ↓
   PCT ≥ 90%                            PCT < 90%
   Approved ✅                          Rejected ❌
   Create Capsule                       Log & Discard
```

### **Configuring Predictors**

**Edit `server/services/CapsuleCreationEngine.ts`:**
```typescript
const predictors = {
  primary: {
    name: 'integration-bridge',
    url: 'http://shadow-twin-integration-service/api/v1/predict',
    weight: 1.5,
    enabled: true,
  },
  controller: {
    name: 'shadow-twin-controller',
    url: 'http://shadow-twin-controller-service/health',
    weight: 0.8,
    enabled: true,
  },
  // Add custom predictor
  custom: {
    name: 'custom-predictor',
    url: 'http://your-predictor-service/predict',
    weight: 1.0,
    enabled: true,
  },
};
```

### **Consensus Metrics**

**View consensus statistics:**
```bash
curl https://your-factory-url.com/api/consensus/stats \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Response:**
```json
{
  "total_validations": 1523,
  "approved": 1489,
  "rejected": 34,
  "approval_rate": 0.978,
  "avg_pct": 0.953,
  "avg_latency_ms": 87,
  "predictors": {
    "integration-bridge": {
      "requests": 1523,
      "success": 1520,
      "avg_latency_ms": 46
    },
    "controller": {
      "requests": 1523,
      "success": 1518,
      "avg_latency_ms": 44
    }
  }
}
```

### **Tuning Consensus**

**Adjust PCT threshold:**
```env
# .env
CONSENSUS_PCT_THRESHOLD=0.90  # 90% (default)
# Lower = more lenient (more capsules approved)
# Higher = more strict (fewer capsules approved)
```

**Adjust predictor weights:**
```typescript
// Higher weight = more influence on consensus
primary: { weight: 1.5 },  // 50% more influence
secondary: { weight: 0.8 }, // 20% less influence
```

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**

**Application Health:**
```bash
curl https://your-factory-url.com/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 86400,
  "services": {
    "database": "healthy",
    "redis": "healthy",
    "mqtt": "healthy",
    "websocket": "healthy"
  },
  "metrics": {
    "active_capsules": 12,
    "connected_clients": 45,
    "sensor_readings_per_sec": 120
  }
}
```

### **Key Metrics to Monitor**

| Metric | Threshold | Action |
|--------|-----------|--------|
| **CPU Usage** | >80% | Scale horizontally |
| **Memory Usage** | >85% | Increase limits |
| **Database Connections** | >80% of max | Increase pool size |
| **WebSocket Connections** | >8000 | Add more pods |
| **MQTT Message Queue** | >1000 | Increase buffer |
| **Capsule Creation Rate** | >100/sec | Review rules |
| **Consensus Latency** | >200ms | Check predictors |

### **Grafana Dashboards**

Access: `https://your-factory-url.com:3001`

**Pre-configured dashboards:**
1. **System Overview** - CPU, memory, disk, network
2. **Application Metrics** - Capsule rates, WebSocket connections
3. **Sensor Ingestion** - MQTT throughput, OPC-UA connections
4. **Shadow Twin Consensus** - PCT scores, predictor latency
5. **User Activity** - Active users, action rates

### **Log Analysis**

**View application logs:**
```bash
# Docker Compose
docker-compose logs -f app

# Kubernetes
kubectl logs -f deployment/capsule-pins-app -n dac-factory

# Loki query (in Grafana)
{app="capsule-pins-app"} |= "error" or "ERROR"
```

**Common log patterns:**
```
[CapsuleEngine] Capsule created: motor001_overheat
[SensorIngestion] MQTT message received: motor001_temp
[Consensus] PCT: 0.95, Approved: true
[WebSocket] Client connected: user_123
[WebSocket] Broadcasted capsule: capsule_456
```

### **Database Maintenance**

**Vacuum and analyze:**
```bash
docker-compose exec postgres psql -U capsule_admin -d capsule_pins -c "VACUUM ANALYZE;"
```

**Check database size:**
```bash
docker-compose exec postgres psql -U capsule_admin -d capsule_pins -c "
  SELECT pg_size_pretty(pg_database_size('capsule_pins'));"
```

**Archive old capsules:**
```bash
# Archive capsules older than 90 days
docker-compose exec app node scripts/archive-capsules.js --days 90
```

---

## 🔒 **Security & Compliance**

### **Security Checklist**

```bash
- [ ] Change all default passwords
- [ ] Enable HTTPS/TLS
- [ ] Configure firewall rules
- [ ] Enable MQTT authentication
- [ ] Rotate JWT secrets (every 90 days)
- [ ] Enable audit logging
- [ ] Configure rate limiting
- [ ] Set up intrusion detection
- [ ] Regular security updates
- [ ] Penetration testing (annually)
```

### **SSL/TLS Configuration**

**Generate certificates:**
```bash
# Self-signed (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout server.key -out server.crt

# Let's Encrypt (production)
certbot certonly --standalone -d your-factory-url.com
```

**Configure Nginx:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-factory-url.com;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://app:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### **Audit Logging**

**Enable audit logs:**
```env
ENABLE_AUDIT_LOGGING=true
AUDIT_LOG_PATH=/app/logs/audit.log
AUDIT_LOG_RETENTION_DAYS=365
```

**Audit events logged:**
- User login/logout
- Capsule acknowledgment
- Rule changes
- User creation/deletion
- Configuration changes

**Query audit logs:**
```bash
# View recent logins
docker-compose exec app node scripts/audit-query.js \
  --event login --since "2024-01-01"

# View capsule acknowledgments by user
docker-compose exec app node scripts/audit-query.js \
  --event capsule_acknowledge --user user@factory.com
```

---

## 💾 **Backup & Recovery**

### **Backup Strategy**

**Daily backups:**
```bash
# Database backup
docker-compose exec postgres pg_dump -U capsule_admin capsule_pins \
  > backups/capsule_pins_$(date +%Y%m%d).sql

# Configuration backup
tar -czf backups/config_$(date +%Y%m%d).tar.gz \
  .env docker-compose.yml config/

# Uploads backup
tar -czf backups/uploads_$(date +%Y%m%d).tar.gz uploads/
```

**Automated backup script:**
```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database
docker-compose exec -T postgres pg_dump -U capsule_admin capsule_pins \
  | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Configuration
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" .env config/

# Uploads
tar -czf "$BACKUP_DIR/uploads_$DATE.tar.gz" uploads/

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
```

**Schedule with cron:**
```bash
# Run daily at 2 AM
0 2 * * * /path/to/scripts/backup.sh >> /var/log/capsule-backup.log 2>&1
```

### **Restore Procedure**

**Restore database:**
```bash
# Stop application
docker-compose stop app

# Restore database
gunzip < backups/db_20240115.sql.gz | \
  docker-compose exec -T postgres psql -U capsule_admin capsule_pins

# Restart application
docker-compose start app
```

**Restore configuration:**
```bash
tar -xzf backups/config_20240115.tar.gz
docker-compose restart
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

**1. High CPU Usage**
```bash
# Check processes
docker-compose exec app top

# Check slow queries
docker-compose exec postgres psql -U capsule_admin -d capsule_pins -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY mean_time DESC
  LIMIT 10;"

# Solution: Add database indexes, optimize queries
```

**2. Memory Leaks**
```bash
# Check memory usage
docker stats

# Restart affected service
docker-compose restart app

# Solution: Investigate with heap profiler
docker-compose exec app node --inspect server-dist/index.js
```

**3. WebSocket Disconnections**
```bash
# Check WebSocket errors
docker-compose logs app | grep WebSocket

# Check network connectivity
ping your-factory-url.com

# Solution: Increase timeout, check firewall
```

**4. Sensor Data Not Appearing**
```bash
# Test MQTT connection
mosquitto_sub -h localhost -p 1883 -t "factory/#" -v

# Check sensor ingestion logs
docker-compose logs sensor-ingestion

# Verify sensor registration
curl https://your-factory-url.com/api/sensors
```

---

## 📞 **Support & Escalation**

### **Support Tiers**

**Tier 1: Self-Service**
- Documentation: https://docs.capsule-pins.io
- FAQ: https://docs.capsule-pins.io/faq
- Community Forum: https://community.capsule-pins.io

**Tier 2: Email Support**
- Email: support@capsule-pins.io
- Response time: 24 hours

**Tier 3: Priority Support**
- Phone: +1-XXX-XXX-XXXX
- Email: priority@capsule-pins.io
- Response time: 4 hours

**Tier 4: Emergency**
- Phone: +1-XXX-XXX-XXXX (24/7)
- Response time: 1 hour

---

## 📝 **Appendix**

### **API Reference**

Full API documentation: https://docs.capsule-pins.io/api

### **Configuration Reference**

All environment variables: https://docs.capsule-pins.io/config

### **Changelog**

- **v1.0.0** (Week 16) - Initial release
  - Complete DAC Factory system
  - Shadow Twin Consensus integration
  - AR/VR support
  - Docker + Kubernetes deployment

---

**For technical support, contact: support@capsule-pins.io**
