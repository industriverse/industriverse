# Multi-Cloud DAC Deployment Guide

This guide documents the complete process for deploying DAC (Decentralized Autonomous Capsule) packages across Azure, AWS, and GCP using the Industriverse DAC Factory.

**Author:** Manus AI (Industriverse Team)  
**Date:** November 16, 2025  
**Version:** 1.0.0

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [Deployment Process](#deployment-process)
5. [Deploy Anywhere Services](#deploy-anywhere-services)
6. [Health Monitoring](#health-monitoring)
7. [Rollback Procedures](#rollback-procedures)
8. [Upgrade Strategies](#upgrade-strategies)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

---

## Overview

The Industriverse DAC Factory enables seamless deployment of DAC capsules across multiple cloud providers. The system automatically selects the appropriate Deploy Anywhere service for each cloud and manages the complete deployment lifecycle.

### Key Features

- **Multi-Cloud Support:** Deploy to Azure, AWS, and GCP from a single interface
- **Automatic Service Selection:** Intelligent routing to the best Deploy Anywhere service
- **Health Monitoring:** Real-time health checks across all deployments
- **Rollback Support:** Automatic rollback on deployment failures
- **Upgrade Strategies:** Multiple upgrade strategies (rolling, blue-green, canary, recreate)

---

## Architecture

### Components

The multi-cloud deployment system consists of three main components:

1. **K8s Client Manager**
   - Manages connections to Kubernetes clusters across all clouds
   - Handles authentication and context switching
   - Monitors cluster health and capacity

2. **Deploy Anywhere Integration**
   - Routes deployments to appropriate services
   - Manages deployment lifecycle
   - Tracks deployment status and health

3. **DAC Factory**
   - Packages hypotheses into deployable capsules
   - Generates UTIDs and zk-SNARK proofs
   - Calculates energy signatures

### Supported Clusters

| Cloud | Cluster Name | Context | Region | Namespace |
|-------|--------------|---------|--------|-----------|
| Azure | industriverse-azure-v2 | industriverse-azure-v2 | eastus2 | industriverse |
| AWS | molecular-industrial-cluster | molecular-industrial-cluster | us-east-1 | molecular |
| GCP | industriverse-cluster | industriverse-cluster | us-central1 | industriverse |

---

## Prerequisites

### Required Software

- Python 3.11+
- kubectl configured with access to all clusters
- Valid kubeconfig file at `~/.kube/config`

### Required Credentials

- Azure: Service principal with AKS access
- AWS: IAM credentials with EKS access
- GCP: Service account with GKE access

### Python Dependencies

```bash
pip install kubernetes-asyncio
pip install pytest pytest-asyncio
```

---

## Deployment Process

### Step 1: Initialize K8s Client Manager

```python
from src.infrastructure.multi_cloud import K8sClientManager

# Create manager
manager = K8sClientManager()

# Connect to all clusters
await manager.connect_all_clusters()

# Verify connections
stats = manager.get_statistics()
print(f"Connected to {stats['connected_clusters']}/{stats['total_clusters']} clusters")
```

### Step 2: Initialize Deploy Anywhere Integration

```python
from src.infrastructure.multi_cloud import DeployAnywhereIntegration

# Create integration
integration = DeployAnywhereIntegration(manager)

# List available services
services = integration.list_services()
for service in services:
    print(f"{service.name} ({service.provider.value})")
```

### Step 3: Prepare Capsule Manifest

```python
manifest = {
    "name": "my-capsule",
    "version": "1.0.0",
    "description": "My DAC capsule",
    "image": "industriverse/my-capsule:latest",
    "replicas": 3,
    "resources": {
        "cpu": "500m",
        "memory": "512Mi"
    },
    "env": {
        "ENVIRONMENT": "production"
    },
    "ports": [
        {
            "name": "http",
            "port": 8080,
            "protocol": "TCP"
        }
    ]
}
```

### Step 4: Deploy to Cloud

```python
from src.infrastructure.multi_cloud import CloudProvider

# Deploy to Azure
deployment = await integration.deploy_capsule(
    "my-capsule",
    CloudProvider.AZURE,
    manifest,
    metadata={"team": "ai-research", "environment": "production"}
)

print(f"Deployment ID: {deployment.deployment_id}")
print(f"Status: {deployment.status.value}")
print(f"Service: {deployment.target_service}")
```

### Step 5: Monitor Deployment Health

```python
# Check health
health = await integration.check_deployment_health(deployment.deployment_id)
print(f"Health: {health}")

# Get deployment details
deployment = integration.get_deployment(deployment.deployment_id)
print(f"Replicas: {deployment.manifest['replicas']}")
print(f"Health Status: {deployment.health_status}")
```

---

## Deploy Anywhere Services

The system integrates with 7 Deploy Anywhere services across 3 clouds:

### Azure Services (4)

#### 1. OBMI Enterprise (Preferred)
- **Service Type:** OBMI
- **Endpoint:** `http://obmi-enterprise.industriverse.svc.cluster.local:8080`
- **Features:** Quantum-enabled, OBMI integration
- **Use Case:** Production deployments requiring quantum capabilities

#### 2. A2A Deploy Anywhere
- **Service Type:** A2A
- **Endpoint:** `http://a2a-deploy-anywhere.industriverse.svc.cluster.local:8080`
- **Features:** Azure-to-Anywhere deployment
- **Use Case:** General-purpose Azure deployments

#### 3. Azure Deploy Anywhere
- **Service Type:** A2A
- **Endpoint:** `http://azure-deploy-anywhere.industriverse.svc.cluster.local:8080`
- **Features:** Legacy Azure deployment service
- **Use Case:** Backward compatibility

#### 4. Enterprise Client Portal
- **Service Type:** Portal
- **Endpoint:** `http://enterprise-client-portal.industriverse.svc.cluster.local:8080`
- **Features:** UI-enabled deployment portal
- **Use Case:** Interactive deployments

### AWS Services (1)

#### 1. AI Ripple Deploy Anywhere
- **Service Type:** Ripple
- **Endpoint:** `http://ai-ripple-deploy-anywhere.molecular.svc.cluster.local:8080`
- **Features:** AI-enabled deployment with ripple effects
- **Use Case:** All AWS deployments

### GCP Services (2)

#### 1. BitNet Protocol (Preferred)
- **Service Type:** BitNet
- **Endpoint:** `http://bitnet-protocol.industriverse.svc.cluster.local:8080`
- **Features:** Protocol-based deployment
- **Use Case:** Production GCP deployments

#### 2. Edge Device Registry
- **Service Type:** Edge
- **Endpoint:** `http://edge-device-registry.industriverse.svc.cluster.local:8080`
- **Features:** Edge device management
- **Use Case:** Edge deployments

### Service Selection Logic

The system automatically selects the best service for each cloud:

- **Azure:** Prefers OBMI Enterprise → Falls back to A2A
- **AWS:** Uses AI Ripple Deploy Anywhere
- **GCP:** Prefers BitNet Protocol → Falls back to Edge

---

## Health Monitoring

### Automatic Health Checks

The system performs automatic health checks on all deployments:

```python
# Check single deployment
health = await integration.check_deployment_health(deployment_id)

# Health status values:
# - "healthy": Deployment is running normally
# - "unhealthy": Deployment has issues
# - "unknown": Health status cannot be determined
```

### Manual Health Verification

```python
# Get deployment
deployment = integration.get_deployment(deployment_id)

# Check status
if deployment.status == DeploymentStatus.DEPLOYED:
    print("Deployment is active")
    print(f"Health: {deployment.health_status}")
    print(f"Last updated: {deployment.updated_at}")
```

### Cluster Health

```python
# Check cluster health
health = await manager.check_cluster_health("industriverse-azure-v2")

print(f"Status: {health.status.value}")
print(f"Nodes: {health.healthy_nodes}/{health.node_count}")
print(f"CPU Capacity: {health.cpu_capacity} cores")
print(f"Memory Capacity: {health.memory_capacity} GB")
```

---

## Rollback Procedures

### Automatic Rollback

Deployments automatically rollback on failure. To manually rollback:

```python
# Rollback deployment
success = await integration.rollback_deployment(deployment_id)

if success:
    print("Rollback successful")
    deployment = integration.get_deployment(deployment_id)
    print(f"Status: {deployment.status.value}")  # "rolled_back"
```

### Rollback All Clouds

```python
# Deploy to all clouds
azure_deployment = await integration.deploy_capsule("my-capsule", CloudProvider.AZURE, manifest)
aws_deployment = await integration.deploy_capsule("my-capsule", CloudProvider.AWS, manifest)
gcp_deployment = await integration.deploy_capsule("my-capsule", CloudProvider.GCP, manifest)

# Rollback all
await integration.rollback_deployment(azure_deployment.deployment_id)
await integration.rollback_deployment(aws_deployment.deployment_id)
await integration.rollback_deployment(gcp_deployment.deployment_id)
```

---

## Upgrade Strategies

### Rolling Upgrade

Deploy new version while gradually replacing old instances:

```python
# Deploy v1
v1_manifest = {
    "name": "my-capsule",
    "version": "1.0.0",
    "image": "industriverse/my-capsule:v1.0.0",
    "replicas": 3
}

v1_deployment = await integration.deploy_capsule(
    "my-capsule",
    CloudProvider.AZURE,
    v1_manifest
)

# Upgrade to v2
v2_manifest = {
    "name": "my-capsule",
    "version": "2.0.0",
    "image": "industriverse/my-capsule:v2.0.0",
    "replicas": 3
}

v2_deployment = await integration.deploy_capsule(
    "my-capsule",
    CloudProvider.AZURE,
    v2_manifest
)
```

### Blue-Green Deployment

Deploy new version alongside old, then switch traffic:

```python
# Blue deployment (current)
blue_manifest = {
    "name": "my-capsule-blue",
    "version": "1.0.0",
    "image": "industriverse/my-capsule:v1.0.0"
}

# Green deployment (new)
green_manifest = {
    "name": "my-capsule-green",
    "version": "2.0.0",
    "image": "industriverse/my-capsule:v2.0.0"
}

blue_deployment = await integration.deploy_capsule("my-capsule-blue", CloudProvider.AZURE, blue_manifest)
green_deployment = await integration.deploy_capsule("my-capsule-green", CloudProvider.AZURE, green_manifest)

# Verify green is healthy
health = await integration.check_deployment_health(green_deployment.deployment_id)

if health == "healthy":
    # Switch traffic to green
    # Rollback blue
    await integration.rollback_deployment(blue_deployment.deployment_id)
```

### Canary Deployment

Gradually shift traffic from old to new version:

```python
# Deploy stable version (90% traffic)
stable_manifest = {
    "name": "my-capsule-stable",
    "version": "1.0.0",
    "replicas": 9  # 90% of traffic
}

# Deploy canary version (10% traffic)
canary_manifest = {
    "name": "my-capsule-canary",
    "version": "2.0.0",
    "replicas": 1  # 10% of traffic
}

stable = await integration.deploy_capsule("my-capsule-stable", CloudProvider.AZURE, stable_manifest)
canary = await integration.deploy_capsule("my-capsule-canary", CloudProvider.AZURE, canary_manifest)

# Monitor canary health
# If healthy, gradually increase canary replicas and decrease stable replicas
```

---

## Troubleshooting

### Common Issues

#### 1. Connection Failures

**Problem:** Cannot connect to cluster

**Solution:**
```python
# Check cluster health
health = await manager.check_cluster_health("industriverse-azure-v2")
print(f"Status: {health.status.value}")
print(f"Error: {health.error_message}")

# Reconnect
await manager.connect_cluster("industriverse-azure-v2")
```

#### 2. Deployment Failures

**Problem:** Deployment fails

**Solution:**
```python
# Get deployment details
deployment = integration.get_deployment(deployment_id)
print(f"Status: {deployment.status.value}")
print(f"Error: {deployment.error_message}")

# Rollback
await integration.rollback_deployment(deployment_id)
```

#### 3. Service Unavailable

**Problem:** Deploy Anywhere service not available

**Solution:**
```python
# List available services
services = integration.list_services(provider=CloudProvider.AZURE)
for service in services:
    print(f"{service.name}: enabled={service.enabled}")

# Check if service is enabled
service = integration.get_service("obmi-enterprise")
if not service.enabled:
    service.enabled = True
```

---

## Examples

### Example 1: Deploy Hello World to All Clouds

```python
from src.infrastructure.multi_cloud import K8sClientManager, DeployAnywhereIntegration, CloudProvider

# Initialize
manager = K8sClientManager()
await manager.connect_all_clusters()
integration = DeployAnywhereIntegration(manager)

# Create manifest
manifest = {
    "name": "hello-world",
    "version": "1.0.0",
    "image": "industriverse/hello-world:latest",
    "replicas": 2,
    "resources": {
        "cpu": "100m",
        "memory": "128Mi"
    }
}

# Deploy to all clouds
azure = await integration.deploy_capsule("hello-world", CloudProvider.AZURE, manifest)
aws = await integration.deploy_capsule("hello-world", CloudProvider.AWS, manifest)
gcp = await integration.deploy_capsule("hello-world", CloudProvider.GCP, manifest)

# Check health
print(f"Azure: {await integration.check_deployment_health(azure.deployment_id)}")
print(f"AWS: {await integration.check_deployment_health(aws.deployment_id)}")
print(f"GCP: {await integration.check_deployment_health(gcp.deployment_id)}")

# Get statistics
stats = integration.get_statistics()
print(f"Total deployments: {stats['total_deployments']}")
print(f"Success rate: {stats['success_rate']:.1f}%")
```

### Example 2: Deploy with Monitoring

```python
# Deploy
deployment = await integration.deploy_capsule("my-capsule", CloudProvider.AZURE, manifest)

# Monitor health every 30 seconds
import asyncio

while True:
    health = await integration.check_deployment_health(deployment.deployment_id)
    print(f"Health: {health}")
    
    if health == "healthy":
        break
    
    await asyncio.sleep(30)

print("Deployment is healthy!")
```

### Example 3: Deploy with Automatic Rollback

```python
# Deploy
deployment = await integration.deploy_capsule("my-capsule", CloudProvider.AZURE, manifest)

# Check health
health = await integration.check_deployment_health(deployment.deployment_id)

if health != "healthy":
    print("Deployment unhealthy, rolling back...")
    success = await integration.rollback_deployment(deployment.deployment_id)
    print(f"Rollback: {'successful' if success else 'failed'}")
```

---

## Summary

The Industriverse DAC Factory provides a complete multi-cloud deployment solution with:

- ✅ Seamless deployment to Azure, AWS, and GCP
- ✅ Automatic service selection and routing
- ✅ Real-time health monitoring
- ✅ Automatic rollback on failure
- ✅ Multiple upgrade strategies
- ✅ Comprehensive error handling

For additional support, refer to the test suite in `tests/e2e/test_multi_cloud_deployment.py`.

---

**End of Documentation**
