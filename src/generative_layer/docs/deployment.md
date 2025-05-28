# Generative Layer Deployment Guide

## Overview

This document provides comprehensive instructions for deploying the Industriverse Generative Layer to a Kubernetes cluster. The Generative Layer is designed with protocol-native architecture and full MCP/A2A integration, enabling seamless interaction with the Data Layer and Core AI Layer.

## Prerequisites

- Kubernetes cluster (v1.20+)
- kubectl configured to communicate with your cluster
- Docker or container registry access
- Persistent storage provisioner in your cluster

## Directory Structure

```
industriverse_generative_layer/
├── manifests/                  # Agent manifests
├── protocols/                  # Protocol-native architecture components
├── distributed_intelligence/   # Advanced agent capabilities
├── offer_templates/            # Templates for low-ticket offers
├── kubernetes/                 # Kubernetes deployment manifests
├── tests/                      # Test suite
├── docs/                       # Documentation
├── main.py                     # Main application entry point
├── template_system.py          # Template system implementation
├── ui_component_system.py      # UI component system implementation
├── variability_management.py   # Variability management implementation
├── performance_optimization.py # Performance optimization implementation
├── documentation_generation.py # Documentation generation implementation
├── security_accessibility.py   # Security & accessibility implementation
├── testing_framework.py        # Testing framework implementation
├── Dockerfile                  # Container image definition
├── entrypoint.sh               # Container entrypoint script
└── requirements.txt            # Python dependencies
```

## Deployment Steps

### 1. Build the Container Image

```bash
# Navigate to the Generative Layer directory
cd industriverse_generative_layer

# Build the Docker image
docker build -t your-registry/industriverse-generative-layer:latest .

# Push the image to your registry
docker push your-registry/industriverse-generative-layer:latest
```

### 2. Configure Kubernetes Manifests

Update the Kubernetes manifests in the `kubernetes/` directory:

1. Edit `deployment.yaml` to use your container registry and image version
2. Adjust resource requests/limits based on your environment
3. Configure environment variables as needed
4. Update the bootstrap nodes to match your environment

### 3. Create Kubernetes Resources

```bash
# Create namespace if it doesn't exist
kubectl create namespace industriverse

# Apply ConfigMap
kubectl apply -f kubernetes/configmap.yaml

# Apply Storage
kubectl apply -f kubernetes/storage.yaml

# Apply Deployment
kubectl apply -f kubernetes/deployment.yaml

# Apply Service
kubectl apply -f kubernetes/service.yaml
```

### 4. Verify Deployment

```bash
# Check if pods are running
kubectl get pods -n industriverse -l app=industriverse-generative-layer

# Check logs
kubectl logs -n industriverse -l app=industriverse-generative-layer

# Check service
kubectl get svc -n industriverse generative-layer-service
```

### 5. Test the Deployment

The Generative Layer exposes HTTP and gRPC endpoints:

- HTTP: `http://generative-layer-service.industriverse:8082`
- gRPC: `generative-layer-service.industriverse:8083`

You can test the deployment using:

```bash
# Port forward to access the service locally
kubectl port-forward -n industriverse svc/generative-layer-service 8082:8082

# Test the health endpoint
curl http://localhost:8082/health
```

## Integration with Other Layers

The Generative Layer integrates with other Industriverse layers through protocol-native architecture:

1. **Data Layer**: Provides data for templates and UI components
2. **Core AI Layer**: Provides AI capabilities for prompt mutation and artifact generation

Ensure the Data Layer and Core AI Layer are deployed and accessible before deploying the Generative Layer.

## Configuration Options

The Generative Layer can be configured through the ConfigMap:

- **Agent Core**: Configure agent identity and protocol support
- **Mesh**: Configure mesh network and discovery
- **API**: Configure HTTP and gRPC endpoints
- **Storage**: Configure persistence and backup
- **Logging**: Configure logging level and rotation
- **Security**: Configure authentication and authorization
- **Performance**: Configure caching and parallel processing
- **Edge Behavior**: Configure behavior on edge devices
- **UI Capsule Support**: Configure Universal Skin integration
- **Agent Lineage**: Configure inheritance behavior

## Troubleshooting

Common issues and solutions:

1. **Pods not starting**: Check pod events and logs
   ```bash
   kubectl describe pod -n industriverse -l app=industriverse-generative-layer
   kubectl logs -n industriverse -l app=industriverse-generative-layer
   ```

2. **Service not accessible**: Check service and endpoints
   ```bash
   kubectl get endpoints -n industriverse generative-layer-service
   ```

3. **Protocol errors**: Check protocol translator logs
   ```bash
   kubectl logs -n industriverse -l app=industriverse-generative-layer | grep "protocol_translator"
   ```

4. **Template generation failures**: Check template system logs
   ```bash
   kubectl logs -n industriverse -l app=industriverse-generative-layer | grep "template_system"
   ```

## Advanced Features

### Agent Capsule Integration

The Generative Layer supports the Universal Skin / Dynamic Agent Capsules UX concept, allowing agents to be represented as floating, adaptive UI nodes. To enable this feature:

1. Set `ENABLE_CAPSULE_INTEGRATION=true` in the deployment
2. Configure `ui_capsule_support` in the ConfigMap

### Zero-Knowledge Artifact Traceability

All generated artifacts include ZK proof hashes for traceability. To verify artifact integrity:

1. Retrieve the artifact and its ZK proof hash
2. Use the verification endpoint to validate the artifact

### Live Prompt Tuning

The Prompt Mutator Agent enables adaptive prompt engineering for human-AI co-creation. To use this feature:

1. Send prompts to the `generative_layer/prompt/mutate` endpoint
2. Provide feedback to improve prompt quality over time

## Conclusion

The Industriverse Generative Layer is now deployed and ready for use. It provides a protocol-native foundation for generating templates, UI components, and documentation with full MCP/A2A integration.
