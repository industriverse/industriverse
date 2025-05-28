# Industriverse Protocol Layer Deployment Guide

## Overview

The Industriverse Protocol Layer serves as the "maestro" of the Industrial Foundry Framework ecosystem, providing a resilient, intelligent, and self-optimizing communication infrastructure. This guide outlines the deployment process for the Protocol Layer to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster (v1.19+)
- kubectl configured to access your cluster
- Persistent storage provider (NFS, cloud provider storage, etc.)
- Container registry access
- Namespace `industriverse` created in the cluster

## Deployment Components

The Protocol Layer consists of several key components:

1. **Protocol Kernel** - Core intelligence with intent-aware routing and semantic compression
2. **Mesh Controller** - Manages the protocol mesh and cross-mesh federation
3. **Genetic Algorithm Engine** - Provides algorithm evolution and optimization
4. **Enhanced UDEP Handler** - Enables mobile/edge device communication
5. **Dynamic Protocol AppStore** - Manages protocol-native applications

## Configuration

Before deployment, update the following configuration files:

1. **ConfigMap** (`kubernetes/configmap.yaml`):
   - Set the appropriate `mesh_id` and environment variables
   - Configure intent routing and semantic compression settings
   - Adjust genetic algorithm parameters if needed
   - Set appropriate logging and metrics settings

2. **Storage** (`kubernetes/storage.yaml`):
   - Adjust storage class and size based on your environment
   - Ensure ReadWriteMany access mode is supported by your storage provider

3. **Deployment** (`kubernetes/deployment.yaml`):
   - Update container image registry references
   - Adjust resource requests/limits based on your environment
   - Configure any environment-specific settings

## Deployment Steps

1. **Create Namespace** (if not already created):
   ```bash
   kubectl create namespace industriverse
   ```

2. **Create Service Account**:
   ```bash
   kubectl apply -f kubernetes/rbac.yaml
   ```

3. **Deploy Storage**:
   ```bash
   kubectl apply -f kubernetes/storage.yaml
   ```

4. **Deploy ConfigMap**:
   ```bash
   kubectl apply -f kubernetes/configmap.yaml
   ```

5. **Deploy Protocol Layer Components**:
   ```bash
   kubectl apply -f kubernetes/deployment.yaml
   ```

6. **Deploy Services**:
   ```bash
   kubectl apply -f kubernetes/service.yaml
   ```

7. **Verify Deployment**:
   ```bash
   kubectl get pods -n industriverse
   kubectl get services -n industriverse
   ```

## Environment Variables

The following environment variables should be set before deployment:

- `REGISTRY`: Container registry path (e.g., `gcr.io/industriverse`)
- `VERSION`: Version tag for container images (e.g., `v1.0.0`)
- `ENVIRONMENT`: Deployment environment (e.g., `production`, `staging`, `development`)
- `DOMAIN`: Base domain for the deployment (e.g., `industriverse.io`)

Example:
```bash
export REGISTRY=gcr.io/industriverse
export VERSION=v1.0.0
export ENVIRONMENT=production
export DOMAIN=industriverse.io

# Apply variable substitution to manifests
envsubst < kubernetes/deployment.yaml | kubectl apply -f -
envsubst < kubernetes/configmap.yaml | kubectl apply -f -
```

## Integration with Other Layers

The Protocol Layer integrates with other Industriverse layers through the following endpoints:

- **Data Layer**: Connect via the Protocol Kernel service (`industriverse-protocol-kernel:9090`)
- **Core AI Layer**: Connect via the Protocol Kernel service (`industriverse-protocol-kernel:9090`)
- **Generative Layer**: Connect via the Protocol Kernel service (`industriverse-protocol-kernel:9090`)
- **Application Layer**: Connect via the Protocol Kernel service (`industriverse-protocol-kernel:9090`)

External systems can connect to the Protocol Layer through the Enhanced UDEP Handler service (`industriverse-protocol-udep:8443`).

## Monitoring and Maintenance

- **Health Checks**: All components expose `/health` and `/ready` endpoints
- **Metrics**: Prometheus metrics are available at `/metrics` on each component
- **Logs**: All components output structured logs to stdout
- **Tracing**: Jaeger tracing is enabled by default

## Troubleshooting

Common issues and solutions:

1. **Pods not starting**: Check persistent volume claims and storage class
2. **Connection issues**: Verify service endpoints and network policies
3. **Performance issues**: Adjust resource requests/limits in deployment.yaml

## Security Considerations

- TLS certificates should be provided via the `industriverse-protocol-certs` secret
- Network policies should be applied to restrict communication between components
- RBAC permissions should be limited to the minimum required

## Backup and Recovery

- Persistent volumes should be backed up regularly
- ConfigMaps and Secrets should be version controlled
- Consider using Velero or similar tools for cluster-level backups

## Scaling

The Protocol Layer can be scaled horizontally by adjusting the replica count in the deployment.yaml file. Vertical scaling can be achieved by adjusting resource requests/limits.

## Upgrading

To upgrade the Protocol Layer:

1. Update the `VERSION` environment variable
2. Apply the updated manifests with the new version
3. Monitor the rollout with `kubectl rollout status deployment/industriverse-protocol-kernel -n industriverse`

## Support

For support, contact the Industriverse team at support@industriverse.io or open an issue in the repository.
