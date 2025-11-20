# EIL Platform - Deployment Guide

Production deployment documentation for the Energy Intelligence Layer platform.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Helm Deployment](#helm-deployment)
- [Docker Compose (Development)](#docker-compose-development)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Security](#security)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Tools

- **Kubernetes**: v1.24+ cluster
- **Helm**: v3.10+
- **kubectl**: v1.24+
- **Docker**: v24.0+ (for local development)

### Cluster Requirements

**Minimum Resources:**
- 3 nodes (for high availability)
- 8 CPU cores per node
- 16GB RAM per node
- 100GB storage

**Recommended for Production:**
- 5+ nodes across 2+ availability zones
- 16 CPU cores per node
- 32GB RAM per node
- 500GB storage (SSD)

### Dependencies

External services required:
- **S3-compatible storage** (AWS S3, MinIO, etc.)
- **InfluxDB** (optional, can be deployed via Helm)
- **Neo4j** (optional, can be deployed via Helm)
- **MQTT broker** (optional, Mosquitto, EMQX, etc.)
- **Prometheus** (optional, can be deployed via Helm)
- **Grafana** (optional, can be deployed via Helm)

---

## Quick Start

### 1. Docker Compose (Fastest for Development)

```bash
# Navigate to deployment directory
cd Thermodynasty/phase5/deploy

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f eil-api

# Access API
curl http://localhost:8000/health/live

# Access Prometheus
open http://localhost:9090

# Access Grafana
open http://localhost:3000  # admin/admin

# Stop services
docker-compose down
```

### 2. Helm (Recommended for Production)

```bash
# Add Helm repositories
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add influxdata https://helm.influxdata.com/
helm repo update

# Install EIL Platform
cd Thermodynasty/phase5/deploy/helm

helm install eil-platform ./eil-platform \
  --namespace eil-platform \
  --create-namespace \
  --set image.tag=v0.5.0 \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=api.yourdomain.com

# Check status
kubectl get pods -n eil-platform
helm status eil-platform -n eil-platform
```

---

## Kubernetes Deployment

### Manual Deployment with kubectl

```bash
cd Thermodynasty/phase5/deploy/k8s

# Create namespace
kubectl apply -f namespace.yaml

# Create ConfigMap and Secrets
kubectl apply -f configmap.yaml

# Create secrets (use your own values!)
kubectl create secret generic eil-secrets \
  --from-literal=jwt-secret-key=$(openssl rand -base64 32) \
  --from-literal=database-url=postgresql://user:pass@host:5432/eil \
  --from-literal=s3-access-key-id=YOUR_ACCESS_KEY \
  --from-literal=s3-secret-access-key=YOUR_SECRET_KEY \
  --from-literal=influxdb-token=YOUR_INFLUXDB_TOKEN \
  --from-literal=neo4j-password=YOUR_NEO4J_PASSWORD \
  --from-literal=mqtt-password=YOUR_MQTT_PASSWORD \
  --namespace eil-platform

# Deploy RBAC
kubectl apply -f rbac.yaml

# Deploy application
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Deploy ingress (optional)
kubectl apply -f ingress.yaml

# Deploy autoscaling
kubectl apply -f hpa.yaml

# Check deployment
kubectl get all -n eil-platform
kubectl logs -f deployment/eil-api -n eil-platform
```

### Verify Deployment

```bash
# Check pod status
kubectl get pods -n eil-platform

# Check services
kubectl get svc -n eil-platform

# Check HPA
kubectl get hpa -n eil-platform

# Test health endpoint
kubectl port-forward svc/eil-api 8000:80 -n eil-platform &
curl http://localhost:8000/health/live

# View metrics
curl http://localhost:8000/metrics
```

---

## Helm Deployment

### Installation

```bash
cd Thermodynasty/phase5/deploy/helm

# Install with default values
helm install eil-platform ./eil-platform \
  --namespace eil-platform \
  --create-namespace

# Install with custom values
helm install eil-platform ./eil-platform \
  --namespace eil-platform \
  --create-namespace \
  --values custom-values.yaml

# Install specific version
helm install eil-platform ./eil-platform \
  --namespace eil-platform \
  --create-namespace \
  --set image.tag=v0.5.0
```

### Custom Values Example

Create `production-values.yaml`:

```yaml
replicaCount: 5

image:
  tag: "v0.5.0"

resources:
  requests:
    cpu: 2000m
    memory: 4Gi
  limits:
    cpu: 4000m
    memory: 8Gi

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 50

ingress:
  enabled: true
  hosts:
    - host: api.eil-production.io
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: eil-prod-tls
      hosts:
        - api.eil-production.io

secrets:
  externalSecrets:
    enabled: true
    backend: vault
    vaultPath: "secret/eil-platform/prod"

prometheus:
  enabled: true
  server:
    retention: "90d"

influxdb:
  enabled: true
  persistence:
    size: 500Gi

neo4j:
  enabled: true
  persistence:
    size: 200Gi
```

Install with production values:

```bash
helm install eil-platform ./eil-platform \
  --namespace eil-platform \
  --create-namespace \
  --values production-values.yaml
```

### Upgrade

```bash
# Upgrade to new version
helm upgrade eil-platform ./eil-platform \
  --namespace eil-platform \
  --set image.tag=v0.6.0

# Upgrade with new values
helm upgrade eil-platform ./eil-platform \
  --namespace eil-platform \
  --values production-values.yaml
```

### Rollback

```bash
# View release history
helm history eil-platform -n eil-platform

# Rollback to previous version
helm rollback eil-platform -n eil-platform

# Rollback to specific revision
helm rollback eil-platform 3 -n eil-platform
```

### Uninstall

```bash
helm uninstall eil-platform -n eil-platform

# Delete namespace
kubectl delete namespace eil-platform
```

---

## Docker Compose (Development)

### Start Services

```bash
cd Thermodynasty/phase5/deploy

# Start in foreground
docker-compose up

# Start in background
docker-compose up -d

# Start specific services
docker-compose up eil-api prometheus grafana
```

### Configuration

Edit `docker-compose.yml` or create `.env` file:

```env
ENVIRONMENT=development
LOG_LEVEL=DEBUG
DIFFUSION_TIMESTEPS=1000
WORKERS=2
```

### Useful Commands

```bash
# View logs
docker-compose logs -f eil-api

# Execute command in container
docker-compose exec eil-api bash

# Rebuild images
docker-compose build

# Stop services
docker-compose stop

# Remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

---

## Configuration

### Environment Variables

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment (dev/staging/prod) | `production` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `WORKERS` | Gunicorn workers | `4` |
| `DIFFUSION_TIMESTEPS` | Diffusion timesteps | `1000` |
| `JWT_SECRET_KEY` | JWT signing key | *required* |
| `S3_BUCKET_NAME` | S3 bucket for storage | *required* |
| `INFLUXDB_URL` | InfluxDB URL | `http://localhost:8086` |
| `NEO4J_URI` | Neo4j connection URI | `bolt://localhost:7687` |
| `MQTT_BROKER_HOST` | MQTT broker host | `localhost` |

### ConfigMap

Update `k8s/configmap.yaml` or Helm values to modify configuration.

### Secrets Management

**Production**: Use external secret management:

- **HashiCorp Vault**
- **AWS Secrets Manager**
- **Azure Key Vault**
- **Google Secret Manager**
- **Kubernetes Sealed Secrets**

**Example with Vault**:

```bash
# Enable Vault secrets
helm install eil-platform ./eil-platform \
  --set secrets.externalSecrets.enabled=true \
  --set secrets.externalSecrets.backend=vault \
  --set secrets.externalSecrets.vaultPath=secret/eil-platform
```

---

## Monitoring

### Prometheus Metrics

Access Prometheus:

```bash
# Port forward
kubectl port-forward svc/prometheus-server 9090:80 -n eil-platform

# Open browser
open http://localhost:9090
```

Key metrics:
- `http_requests_total` - Total HTTP requests
- `http_request_duration_seconds` - Request latency
- `energy_fidelity` - Energy conservation fidelity
- `diffusion_steps_total` - Total diffusion steps

### Grafana Dashboards

Access Grafana:

```bash
# Port forward
kubectl port-forward svc/grafana 3000:80 -n eil-platform

# Open browser
open http://localhost:3000  # admin/admin
```

Import dashboards from `deploy/grafana/dashboards/`

### Alerts

Prometheus alerts configured in Helm values:

- High error rate (>5%)
- High response time (p95 > 1s)
- Low energy fidelity (<95%)
- High memory usage (>80%)

---

## Security

### Best Practices

1. **Never commit secrets to git**
2. **Use external secret management**
3. **Enable TLS/SSL everywhere**
4. **Use network policies**
5. **Enable pod security policies**
6. **Rotate secrets regularly**
7. **Use least privilege RBAC**
8. **Enable audit logging**

### Network Policies

```bash
# Apply network policies
kubectl apply -f k8s/network-policy.yaml
```

### TLS Certificates

Use cert-manager for automatic TLS:

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer
kubectl apply -f k8s/cert-issuer.yaml
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl get pods -n eil-platform

# View pod events
kubectl describe pod <pod-name> -n eil-platform

# Check logs
kubectl logs <pod-name> -n eil-platform

# Check previous container logs
kubectl logs <pod-name> -n eil-platform --previous
```

### High Memory Usage

```bash
# Check resource usage
kubectl top pods -n eil-platform

# Increase memory limits
helm upgrade eil-platform ./eil-platform \
  --set resources.limits.memory=8Gi
```

### Connection Issues

```bash
# Test connectivity to dependencies
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- sh

# Inside debug pod
curl http://eil-api.eil-platform.svc.cluster.local/health/live
```

### View All Resources

```bash
kubectl get all,configmap,secret,ingress,hpa,pdb -n eil-platform
```

---

## Production Checklist

Before deploying to production:

- [ ] External secret management configured
- [ ] TLS certificates configured
- [ ] Monitoring and alerting enabled
- [ ] Resource limits set appropriately
- [ ] Autoscaling configured
- [ ] Pod disruption budgets configured
- [ ] Network policies applied
- [ ] Backup strategy in place
- [ ] Disaster recovery plan documented
- [ ] Load testing completed
- [ ] Security audit passed

---

## Support

- **Documentation**: https://docs.eil-platform.io
- **GitHub**: https://github.com/industriverse/eil-platform
- **Issues**: https://github.com/industriverse/eil-platform/issues
- **Email**: support@eil-platform.io
