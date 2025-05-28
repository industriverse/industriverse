# Industriverse UI/UX Layer: Deployment Guide

## Introduction

This deployment guide provides comprehensive instructions for deploying the Industriverse UI/UX Layer to a Kubernetes cluster. The UI/UX Layer serves as the "living membrane" between humans and AI in the Industriverse ecosystem, providing an Ambient Intelligence experience through the Universal Skin concept and Dynamic Agent Capsules.

## Prerequisites

Before deploying the UI/UX Layer, ensure you have the following prerequisites:

1. **Kubernetes Cluster**: A running Kubernetes cluster (v1.20+)
2. **Helm**: Helm 3.0+ installed
3. **kubectl**: Configured to communicate with your Kubernetes cluster
4. **Docker Registry**: Access to a Docker registry for storing container images
5. **Storage**: Persistent volume provisioner in your Kubernetes cluster
6. **Existing Layers**: The following layers should already be deployed:
   - Data Layer
   - Core AI Layer
   - Generative Layer
   - Application Layer
   - Protocol Layer
   - Workflow Automation Layer

## Architecture Overview

The UI/UX Layer consists of the following main components:

1. **Universal Skin Shell**: The core container for the UI/UX experience
2. **Agent Ecosystem**: Manages Layer Avatars and agent representations
3. **Capsule Framework**: Handles Dynamic Agent Capsules lifecycle
4. **Context Engine**: Manages contextual awareness and state
5. **Interaction Orchestrator**: Coordinates user-agent interactions
6. **Protocol Bridge**: Connects to MCP/A2A protocols
7. **Real-Time Context Bus**: Enables cross-layer integration
8. **Rendering Engine**: Handles adaptive rendering across devices
9. **Specialized UI Components**: Provides rich UI experiences
10. **Edge Support**: Enables edge and mobile experiences

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/industriverse/ui-ux-layer.git
cd ui-ux-layer
```

### 2. Configure Environment Variables

Create a `.env` file with the following variables:

```
# Core Configuration
UI_UX_LAYER_VERSION=1.0.0
NAMESPACE=industriverse
STORAGE_CLASS=standard

# Cross-Layer Integration
DATA_LAYER_ENDPOINT=http://data-layer-service.industriverse.svc.cluster.local
CORE_AI_LAYER_ENDPOINT=http://core-ai-layer-service.industriverse.svc.cluster.local
GENERATIVE_LAYER_ENDPOINT=http://generative-layer-service.industriverse.svc.cluster.local
APPLICATION_LAYER_ENDPOINT=http://application-layer-service.industriverse.svc.cluster.local
PROTOCOL_LAYER_ENDPOINT=http://protocol-layer-service.industriverse.svc.cluster.local
WORKFLOW_AUTOMATION_LAYER_ENDPOINT=http://workflow-automation-layer-service.industriverse.svc.cluster.local

# Security Configuration
ENABLE_TLS=true
TLS_SECRET_NAME=ui-ux-layer-tls
ENABLE_AUTHENTICATION=true
AUTH_SECRET_NAME=ui-ux-layer-auth

# Performance Configuration
REPLICAS=3
RESOURCE_CPU_REQUEST=500m
RESOURCE_CPU_LIMIT=1000m
RESOURCE_MEMORY_REQUEST=1Gi
RESOURCE_MEMORY_LIMIT=2Gi

# Feature Flags
ENABLE_EDGE_SUPPORT=true
ENABLE_AR_VR_SUPPORT=true
ENABLE_BITNET_UI_PACKS=true
```

### 3. Update Helm Values

Modify the `kubernetes/helm/values.yaml` file to match your environment:

```yaml
# Global settings
global:
  environment: production
  namespace: industriverse
  labels:
    app: ui-ux-layer
    layer: ui-ux

# Image settings
image:
  repository: industriverse/ui-ux-layer
  tag: 1.0.0
  pullPolicy: IfNotPresent

# Deployment settings
deployment:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0

# Resource settings
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 1000m
    memory: 2Gi

# Service settings
service:
  type: ClusterIP
  port: 80
  targetPort: 8080

# Ingress settings
ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: ui-ux.industriverse.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: ui-ux-layer-tls
      hosts:
        - ui-ux.industriverse.com

# Persistence settings
persistence:
  enabled: true
  storageClass: standard
  size: 10Gi

# Cross-layer integration settings
crossLayerIntegration:
  dataLayer:
    endpoint: http://data-layer-service.industriverse.svc.cluster.local
  coreAiLayer:
    endpoint: http://core-ai-layer-service.industriverse.svc.cluster.local
  generativeLayer:
    endpoint: http://generative-layer-service.industriverse.svc.cluster.local
  applicationLayer:
    endpoint: http://application-layer-service.industriverse.svc.cluster.local
  protocolLayer:
    endpoint: http://protocol-layer-service.industriverse.svc.cluster.local
  workflowAutomationLayer:
    endpoint: http://workflow-automation-layer-service.industriverse.svc.cluster.local

# Feature flags
featureFlags:
  edgeSupport: true
  arVrSupport: true
  bitnetUiPacks: true

# Security settings
security:
  authentication:
    enabled: true
    secretName: ui-ux-layer-auth
  rbac:
    enabled: true
  networkPolicy:
    enabled: true
```

### 4. Build and Push Docker Images

```bash
# Build the Docker image
docker build -t industriverse/ui-ux-layer:1.0.0 .

# Push the image to your registry
docker push industriverse/ui-ux-layer:1.0.0
```

### 5. Create Kubernetes Namespace

```bash
kubectl create namespace industriverse
```

### 6. Deploy with Helm

```bash
# Add the Industriverse Helm repository
helm repo add industriverse https://charts.industriverse.com
helm repo update

# Install the UI/UX Layer
helm install ui-ux-layer industriverse/ui-ux-layer \
  --namespace industriverse \
  --values kubernetes/helm/values.yaml
```

Alternatively, deploy from the local chart:

```bash
helm install ui-ux-layer ./kubernetes/helm \
  --namespace industriverse \
  --values kubernetes/helm/values.yaml
```

### 7. Verify Deployment

```bash
# Check if pods are running
kubectl get pods -n industriverse -l app=ui-ux-layer

# Check services
kubectl get services -n industriverse -l app=ui-ux-layer

# Check ingress
kubectl get ingress -n industriverse -l app=ui-ux-layer
```

### 8. Configure Cross-Layer Integration

Ensure the Real-Time Context Bus is properly connected to all other layers:

```bash
# Apply the cross-layer integration ConfigMap
kubectl apply -f kubernetes/base/cross-layer-integration-configmap.yaml -n industriverse
```

### 9. Test the Deployment

Access the UI/UX Layer through the configured ingress URL:

```
https://ui-ux.industriverse.com
```

Verify that the welcome page loads correctly and that you can see the Layer Avatars and Dynamic Agent Capsules.

## Advanced Configuration

### Scaling

To scale the UI/UX Layer horizontally:

```bash
kubectl scale deployment ui-ux-layer --replicas=5 -n industriverse
```

Or update the Helm values and upgrade:

```bash
helm upgrade ui-ux-layer industriverse/ui-ux-layer \
  --namespace industriverse \
  --values kubernetes/helm/values.yaml \
  --set deployment.replicas=5
```

### High Availability

For high availability, ensure:

1. Multiple replicas are configured (at least 3)
2. Pod anti-affinity is enabled to distribute pods across nodes
3. PodDisruptionBudget is configured to maintain minimum availability during updates

Update your values.yaml:

```yaml
deployment:
  replicas: 5
  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchExpressions:
              - key: app
                operator: In
                values:
                  - ui-ux-layer
          topologyKey: "kubernetes.io/hostname"

podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

### Edge Deployment

To enable edge deployment capabilities:

1. Ensure the BitNet UI Pack feature flag is enabled
2. Configure edge device registration endpoints
3. Deploy the Edge Protocol Compression service

```bash
# Deploy Edge Protocol Compression service
kubectl apply -f kubernetes/base/edge-protocol-compression.yaml -n industriverse
```

### AR/VR Integration

To enable AR/VR integration:

1. Ensure the AR/VR Support feature flag is enabled
2. Deploy the AR/VR Integration service

```bash
# Deploy AR/VR Integration service
kubectl apply -f kubernetes/base/ar-vr-integration.yaml -n industriverse
```

## Monitoring and Logging

### Prometheus Metrics

The UI/UX Layer exposes Prometheus metrics at `/metrics`. Configure your Prometheus instance to scrape these metrics.

Example Prometheus scrape configuration:

```yaml
scrape_configs:
  - job_name: 'ui-ux-layer'
    kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
            - industriverse
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_label_app]
        regex: ui-ux-layer
        action: keep
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        regex: metrics
        action: keep
```

### Logging

The UI/UX Layer sends logs to stdout/stderr, which can be collected by your Kubernetes logging solution (e.g., Elasticsearch, Fluentd, Kibana).

Example log queries:

- Universal Skin Shell logs: `kubernetes.labels.app=ui-ux-layer AND message=*universal-skin*`
- Capsule Framework logs: `kubernetes.labels.app=ui-ux-layer AND message=*capsule*`
- Cross-Layer Integration logs: `kubernetes.labels.app=ui-ux-layer AND message=*cross-layer*`

## Troubleshooting

### Common Issues

1. **Pods not starting**:
   - Check pod events: `kubectl describe pod <pod-name> -n industriverse`
   - Check logs: `kubectl logs <pod-name> -n industriverse`

2. **Cross-Layer Integration issues**:
   - Verify endpoints in ConfigMap: `kubectl get configmap cross-layer-integration -n industriverse -o yaml`
   - Check Real-Time Context Bus logs: `kubectl logs -l component=real-time-context-bus -n industriverse`

3. **Performance issues**:
   - Check resource usage: `kubectl top pods -n industriverse`
   - Consider scaling up: `kubectl scale deployment ui-ux-layer --replicas=5 -n industriverse`

4. **UI not loading**:
   - Check browser console for errors
   - Verify ingress configuration: `kubectl get ingress -n industriverse`
   - Check rendering engine logs: `kubectl logs -l component=rendering-engine -n industriverse`

### Support

For additional support, contact:
- Email: support@industriverse.com
- Documentation: https://docs.industriverse.com/ui-ux-layer

## Conclusion

You have successfully deployed the Industriverse UI/UX Layer to your Kubernetes cluster. This layer provides the Ambient Intelligence experience through the Universal Skin concept and Dynamic Agent Capsules, serving as the "living membrane" between humans and AI in the Industriverse ecosystem.

For more information on using and extending the UI/UX Layer, refer to the User Guide and Developer Documentation.
