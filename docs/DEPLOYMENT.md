# DAC Factory Deployment Guide
**Week 16: Production-Ready Deployment**

Complete guide for deploying the Capsule Pins DAC (Data-as-a-Capsule) Factory in production environments.

---

## 📋 **Table of Contents**

1. [Prerequisites](#prerequisites)
2. [Docker Compose Deployment](#docker-compose-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Configuration](#configuration)
5. [Monitoring & Logging](#monitoring--logging)
6. [Security Hardening](#security-hardening)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 **Prerequisites**

### **System Requirements**

**Minimum:**
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB SSD
- OS: Ubuntu 22.04 LTS / RHEL 8+ / Debian 11+

**Recommended:**
- CPU: 8+ cores
- RAM: 16+ GB
- Storage: 100+ GB NVMe SSD
- OS: Ubuntu 22.04 LTS

### **Software Dependencies**

**For Docker Compose:**
- Docker 24.0+
- Docker Compose 2.20+

**For Kubernetes:**
- Kubernetes 1.28+
- kubectl 1.28+
- Helm 3.12+ (optional)

---

## 🐳 **Docker Compose Deployment**

### **Step 1: Clone Repository**

```bash
git clone https://github.com/your-org/capsule-pins-pwa.git
cd capsule-pins-pwa
```

### **Step 2: Configure Environment**

Create `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DB_PASSWORD=your_secure_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here

# JWT
JWT_SECRET=your_jwt_secret_here

# Application
VITE_APP_TITLE=Capsule Pins - DAC Factory
VITE_APP_LOGO=/logo.svg

# Shadow Twin Consensus
SHADOW_TWIN_INTEGRATION_URL=http://shadow-twin-integration-service.shadow-twin-integration.svc.cluster.local:80/api/v1/predict
SHADOW_TWIN_CONTROLLER_URL=http://shadow-twin-controller-service.capsule-dna-registry.svc.cluster.local:8300/health

# Feature Flags
ENABLE_CONSENSUS_VALIDATION=true
ENABLE_AR_VR_MODE=true

# OPC-UA (if using industrial PLCs)
OPCUA_ENDPOINT=opc.tcp://your-plc-server:4840
OPCUA_USERNAME=admin
OPCUA_PASSWORD=your_opcua_password

# Monitoring
GRAFANA_PASSWORD=your_grafana_password
```

### **Step 3: Build and Start Services**

```bash
# Build images
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f app
```

### **Step 4: Initialize Database**

```bash
# Run database migrations
docker-compose exec app pnpm db:push

# (Optional) Seed with demo data
docker-compose exec app node scripts/seed-demo-data.js
```

### **Step 5: Verify Deployment**

```bash
# Check service health
docker-compose ps

# Test application
curl http://localhost:3000/health

# Access Grafana dashboard
open http://localhost:3001
```

---

## ☸️ **Kubernetes Deployment**

### **Step 1: Create Namespace**

```bash
kubectl apply -f k8s/namespace.yaml
```

### **Step 2: Create Secrets**

```bash
# Create secrets from .env file
kubectl create secret generic dac-factory-secrets \
  --from-literal=db-username=capsule_admin \
  --from-literal=db-password=your_secure_password \
  --from-literal=redis-password=your_redis_password \
  --from-literal=jwt-secret=your_jwt_secret \
  --from-literal=database-url=postgresql://capsule_admin:your_secure_password@postgres:5432/capsule_pins \
  --from-literal=redis-url=redis://:your_redis_password@redis:6379 \
  -n dac-factory
```

### **Step 3: Deploy Infrastructure**

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres.yaml

# Deploy MQTT Broker
kubectl apply -f k8s/mqtt.yaml

# Deploy Redis
kubectl apply -f k8s/redis.yaml

# Wait for infrastructure to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n dac-factory --timeout=300s
```

### **Step 4: Deploy Application**

```bash
# Build and push Docker image
docker build -t your-registry/capsule-pins-pwa:latest .
docker push your-registry/capsule-pins-pwa:latest

# Deploy application
kubectl apply -f k8s/deployment.yaml

# Wait for deployment
kubectl rollout status deployment/capsule-pins-app -n dac-factory
```

### **Step 5: Configure Ingress**

```bash
# Install nginx-ingress controller (if not already installed)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install nginx-ingress ingress-nginx/ingress-nginx -n ingress-nginx --create-namespace

# Update ingress host in k8s/deployment.yaml
# Then apply:
kubectl apply -f k8s/deployment.yaml
```

### **Step 6: Verify Deployment**

```bash
# Check pods
kubectl get pods -n dac-factory

# Check services
kubectl get svc -n dac-factory

# View logs
kubectl logs -f deployment/capsule-pins-app -n dac-factory

# Test application
kubectl port-forward svc/capsule-pins-app 3000:3000 -n dac-factory
curl http://localhost:3000/health
```

---

## ⚙️ **Configuration**

### **Environment Variables**

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `NODE_ENV` | Environment mode | `production` | Yes |
| `DATABASE_URL` | PostgreSQL connection string | - | Yes |
| `REDIS_URL` | Redis connection string | - | Yes |
| `MQTT_BROKER_URL` | MQTT broker URL | `mqtt://mqtt-broker:1883` | Yes |
| `JWT_SECRET` | JWT signing secret | - | Yes |
| `ENABLE_CONSENSUS_VALIDATION` | Enable Shadow Twin consensus | `true` | No |
| `ENABLE_AR_VR_MODE` | Enable AR/VR features | `true` | No |
| `SHADOW_TWIN_INTEGRATION_URL` | Integration bridge URL | - | No |
| `SHADOW_TWIN_CONTROLLER_URL` | Controller URL | - | No |

### **Capsule Creation Rules**

Edit `server/services/CapsuleCreationEngine.ts` to customize rules:

```typescript
this.addRule({
  id: 'custom_rule',
  name: 'Custom Alert',
  enabled: true,
  condition: {
    sensorId: 'sensor_001',
    metric: 'temperature',
    operator: '>',
    threshold: 75,
  },
  capsule: {
    title: 'Custom Alert Triggered',
    description: 'Temperature exceeded threshold',
    status: 'warning',
    priority: 'high',
    category: 'custom',
    actions: ['acknowledge', 'inspect'],
  },
});
```

---

## 📊 **Monitoring & Logging**

### **Grafana Dashboards**

Access Grafana at `http://localhost:3001` (Docker Compose) or via Ingress (Kubernetes).

**Default credentials:**
- Username: `admin`
- Password: Set in `.env` (`GRAFANA_PASSWORD`)

**Pre-configured dashboards:**
1. **DAC Factory Overview** - System health, capsule metrics
2. **Sensor Ingestion** - MQTT/OPC-UA throughput
3. **Shadow Twin Consensus** - PCT scores, predictor latency
4. **Application Performance** - Response times, error rates

### **Prometheus Metrics**

Access Prometheus at `http://localhost:9090`.

**Key metrics:**
- `capsule_created_total` - Total capsules created
- `capsule_consensus_pct` - Consensus PCT scores
- `sensor_reading_total` - Total sensor readings
- `mqtt_messages_received` - MQTT message count
- `http_request_duration_seconds` - API response times

### **Loki Logs**

Query logs in Grafana using LogQL:

```logql
# View capsule creation logs
{app="capsule-pins-app"} |= "CapsuleEngine"

# View consensus validation logs
{app="capsule-pins-app"} |= "Consensus"

# View errors
{app="capsule-pins-app"} |= "error" or "ERROR"
```

---

## 🔒 **Security Hardening**

### **1. Change Default Passwords**

```bash
# Generate secure passwords
openssl rand -base64 32

# Update .env and secrets
```

### **2. Enable HTTPS**

**Docker Compose:**
```bash
# Generate SSL certificates
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/server.key \
  -out nginx/ssl/server.crt

# Update nginx.conf with SSL configuration
```

**Kubernetes:**
```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f k8s/cert-manager-issuer.yaml
```

### **3. Enable MQTT Authentication**

```bash
# Create password file
docker-compose exec mqtt-broker mosquitto_passwd -c /mosquitto/config/passwd admin

# Update mosquitto.conf
allow_anonymous false
password_file /mosquitto/config/passwd
```

### **4. Network Policies (Kubernetes)**

```bash
# Apply network policies
kubectl apply -f k8s/network-policies.yaml
```

### **5. RBAC Configuration**

```bash
# Create service accounts with minimal permissions
kubectl apply -f k8s/rbac.yaml
```

---

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Failed**

**Symptoms:**
```
Error: connect ECONNREFUSED 127.0.0.1:5432
```

**Solution:**
```bash
# Check PostgreSQL is running
docker-compose ps postgres
kubectl get pods -l app=postgres -n dac-factory

# Verify DATABASE_URL is correct
docker-compose exec app env | grep DATABASE_URL

# Check PostgreSQL logs
docker-compose logs postgres
kubectl logs -l app=postgres -n dac-factory
```

#### **2. MQTT Broker Not Reachable**

**Symptoms:**
```
[MQTTAdapter] Connection failed: ECONNREFUSED
```

**Solution:**
```bash
# Check MQTT broker is running
docker-compose ps mqtt-broker
kubectl get pods -l app=mqtt-broker -n dac-factory

# Test MQTT connection
mosquitto_sub -h localhost -p 1883 -t test

# Check firewall rules
sudo ufw status
```

#### **3. High Memory Usage**

**Symptoms:**
- Application crashes with OOM errors
- Slow response times

**Solution:**
```bash
# Increase memory limits in docker-compose.yml
services:
  app:
    deploy:
      resources:
        limits:
          memory: 4G

# Or in Kubernetes deployment.yaml
resources:
  limits:
    memory: "4Gi"

# Restart services
docker-compose restart app
kubectl rollout restart deployment/capsule-pins-app -n dac-factory
```

#### **4. Consensus Validation Failing**

**Symptoms:**
```
[CapsuleEngine] Consensus validation failed
```

**Solution:**
```bash
# Check Shadow Twin predictor URLs
echo $SHADOW_TWIN_INTEGRATION_URL
echo $SHADOW_TWIN_CONTROLLER_URL

# Test predictor endpoints
curl -X POST $SHADOW_TWIN_INTEGRATION_URL \
  -H "Content-Type: application/json" \
  -d '{"hypothesis": "test"}'

# Disable consensus temporarily
export ENABLE_CONSENSUS_VALIDATION=false
docker-compose restart app
```

---

## 📞 **Support**

For issues and questions:
- **GitHub Issues:** https://github.com/your-org/capsule-pins-pwa/issues
- **Documentation:** https://docs.capsule-pins.io
- **Email:** support@capsule-pins.io

---

## 📝 **License**

Copyright © 2024 Industriverse. All rights reserved.
