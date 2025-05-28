# Deployment Guide for Industriverse Application Layer

This document provides comprehensive instructions for deploying the Industriverse Application Layer to a Kubernetes cluster. The Application Layer serves as the user-facing interface for the Industrial Foundry Framework, providing Dynamic Agent Capsules, AI Avatars, and protocol-native integration with all other layers.

## Prerequisites

Before deploying the Application Layer, ensure you have the following:

1. Kubernetes cluster (v1.20+) with sufficient resources
2. kubectl CLI tool configured to access your cluster
3. Docker registry access for storing container images
4. Industriverse Data Layer deployed and running
5. Industriverse Core AI Layer deployed and running
6. Industriverse Generative Layer deployed and running

## Architecture Overview

The Application Layer follows a protocol-native architecture with the following components:

- **Protocol Handlers**: MCP and A2A protocol integration
- **Universal Skin / Dynamic Agent Capsules**: Advanced UX components
- **Application Avatar Interface**: AI-driven user interactions
- **Digital Twin Components**: Industrial asset representation
- **Industry-Specific Modules**: Domain-specific functionality
- **Workflow Orchestration**: Process automation and management
- **Omniverse Integration**: 3D visualization and simulation

## Deployment Steps

### 1. Configure Environment Variables

Create a ConfigMap with the necessary environment variables:

```bash
kubectl apply -f kubernetes/configmap.yaml
```

### 2. Set Up Persistent Storage

Apply the storage configuration:

```bash
kubectl apply -f kubernetes/storage.yaml
```

### 3. Build and Push Docker Image

Build the Application Layer Docker image and push it to your registry:

```bash
# Set your registry information
REGISTRY=your-registry.com
TAG=latest

# Build the image
docker build -t ${REGISTRY}/industriverse-application-layer:${TAG} .

# Push the image
docker push ${REGISTRY}/industriverse-application-layer:${TAG}
```

### 4. Update Deployment Configuration

Edit the `kubernetes/deployment.yaml` file to use your Docker image:

```yaml
containers:
- name: application-layer
  image: your-registry.com/industriverse-application-layer:latest
```

### 5. Deploy the Application Layer

Apply the deployment configuration:

```bash
kubectl apply -f kubernetes/deployment.yaml
```

### 6. Expose the Service

Apply the service configuration:

```bash
kubectl apply -f kubernetes/service.yaml
```

### 7. Verify Deployment

Check that all pods are running:

```bash
kubectl get pods -l app=industriverse-application-layer
```

Verify the service is exposed:

```bash
kubectl get svc industriverse-application-layer
```

## Cross-Layer Integration

The Application Layer integrates with other layers through protocol-native interfaces:

### Data Layer Integration

The Application Layer connects to the Data Layer for data access and persistence:

```yaml
env:
- name: DATA_LAYER_SERVICE
  value: "industriverse-data-layer.default.svc.cluster.local"
- name: DATA_LAYER_PORT
  value: "8000"
```

### Core AI Layer Integration

The Application Layer connects to the Core AI Layer for AI model access:

```yaml
env:
- name: CORE_AI_LAYER_SERVICE
  value: "industriverse-core-ai-layer.default.svc.cluster.local"
- name: CORE_AI_LAYER_PORT
  value: "8000"
```

### Generative Layer Integration

The Application Layer connects to the Generative Layer for artifact generation:

```yaml
env:
- name: GENERATIVE_LAYER_SERVICE
  value: "industriverse-generative-layer.default.svc.cluster.local"
- name: GENERATIVE_LAYER_PORT
  value: "8000"
```

## Security Considerations

The Application Layer implements several security measures:

1. **Protocol Security**: All protocol communications are authenticated and encrypted
2. **API Security**: API endpoints require authentication and authorization
3. **Data Protection**: Sensitive data is encrypted at rest and in transit
4. **Network Policies**: Kubernetes network policies restrict pod-to-pod communication

## Monitoring and Logging

The Application Layer exposes metrics and logs for monitoring:

### Prometheus Metrics

Metrics are exposed on the `/metrics` endpoint for Prometheus scraping.

### Logging

Logs are output in JSON format to stdout/stderr for collection by Kubernetes logging solutions.

## Troubleshooting

Common issues and their solutions:

### Pod Startup Failures

If pods fail to start, check the logs:

```bash
kubectl logs -l app=industriverse-application-layer
```

### Connection Issues

If the Application Layer cannot connect to other layers, verify network policies and service DNS:

```bash
kubectl exec -it <pod-name> -- nslookup industriverse-data-layer.default.svc.cluster.local
kubectl exec -it <pod-name> -- curl -v http://industriverse-data-layer.default.svc.cluster.local:8000/health
```

### Protocol Errors

If protocol errors occur, check the protocol handler logs:

```bash
kubectl logs -l app=industriverse-application-layer -c application-layer | grep "protocol"
```

## Scaling

The Application Layer can be scaled horizontally by increasing the number of replicas:

```bash
kubectl scale deployment industriverse-application-layer --replicas=3
```

## Upgrading

To upgrade the Application Layer:

1. Build and push a new Docker image with the updated version
2. Update the deployment to use the new image:

```bash
kubectl set image deployment/industriverse-application-layer application-layer=your-registry.com/industriverse-application-layer:new-version
```

## Conclusion

The Industriverse Application Layer is now deployed and integrated with the other layers of the Industrial Foundry Framework. It provides a protocol-native interface for users to interact with the system through Dynamic Agent Capsules and AI Avatars.
