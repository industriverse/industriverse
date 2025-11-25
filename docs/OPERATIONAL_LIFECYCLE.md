# Operational Lifecycle: The Great Migration & Rehydration

## Overview
This document outlines the complete lifecycle for Industriverse services, moving from active running clusters to cold storage (Backblaze B2) and finally to on-demand client deployment ("Rehydration").

**Goal**: Reduce operational costs by ~$200k/year while preserving 100% of capabilities for on-demand deployment.

---

## Phase 1: Export & Store (The Purge)
*Status: COMPLETED*

1.  **Export**: All 6 clusters (AWS, Azure, GCP) exported.
    *   700+ services
    *   276 namespaces
    *   All ConfigMaps, Secrets, RBAC, PVCs.
2.  **Packaging**: Organized into 9 modular "Value Packages".
    *   `01-core-platform`
    *   `02-ai-services`
    *   `03-manufacturing`
    *   ...and others.
3.  **Compression**: High-ratio compression (90%+) using tarballs.
4.  **Storage**: Uploaded to Backblaze B2 (`industriverse-backup`).
    *   Cost: ~$0.35/month (vs $27k/month previously).

---

## Phase 2: Client Deployment (Rehydration)
*Status: READY TO EXECUTE*

When a client requests a service (e.g., "AI Services"), the following "Rehydration" process is triggered:

### 1. Retrieval
Fetch the specific package from Cold Storage.
```bash
# Example: Retrieve AI Services Package
rclone copy industriverse-backup:packages/02-ai-services.tar.gz ./deploy/
tar -xzf ./deploy/02-ai-services.tar.gz
```

### 2. Image Restoration
Ensure container images are available to the target cluster.
*   **Option A (Online)**: Pull from original registry (Docker Hub/GCR).
*   **Option B (Offline/Air-gapped)**: Load from saved `.tar` archives.
    ```bash
    docker load -i ./images/ai-ripple.tar
    ```
*   **Option C (Enterprise)**: Push to client's private registry.

### 3. Deployment
Apply the manifests to the client's infrastructure.
```bash
# 1. Create Namespaces
kubectl create namespace ai-ripple

# 2. Apply Secrets (Client-Specific)
kubectl create secret generic api-keys --from-literal=key=$CLIENT_KEY

# 3. Hydrate Manifests
kubectl apply -f ./02-ai-services/manifests/
```

### 4. Configuration
*   **Ingress**: Configure `client-domain.com` to point to the LoadBalancer.
*   **Resources**: Tune HPA and resource limits for client scale.

---

## Deployment Architectures

| Architecture | Description | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Client Cloud** | Deploy to client's AWS/GCP/Azure. | Client pays infra; Scalable. | varied environments. |
| **Managed SaaS** | Deploy to our dedicated cluster. | High margins; Control. | We pay infra; Multi-tenant complexity. |
| **On-Premise** | Air-gapped deployment on client hardware. | High security; Premium pricing. | Logistics; No remote access. |

---

## The Role of the Control Interface (This Repo)
The `industriverse` repository serves as the **Control Plane** for this lifecycle.

*   **Dashboard**: Can visualize which packages are active for which tenant.
*   **Deployment Wizard**: (Future) A UI to trigger the "Rehydration" scripts.
*   **License Management**: Issue UTIDs/Proofs for deployed instances.

## Verification
*   **Data Integrity**: 100% preserved (Manifests + Images).
*   **Capabilities**: 100% preserved (Same code running in new env).
*   **Cost**: Optimized (Pay only for active client usage).
