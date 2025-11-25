# KaaS Operator Design

## 1. Goal
Run proof-backed, self-healing Kubernetes-as-a-Service that understands UTID, DAC capsules, and ASAL proofs.

## 2. High-Level Features
*   **Proof-binding deployment**: Every pod/capsule has a proof hash & UTID identity pinned to it.
*   **Proof-first autoscaling**: Scale decisions weigh proof cost, trust weight, and SLO.
*   **Pre-warmed GPU pools**: Warm flag + pool management for instant demos.
*   **Hot-migration <500ms**: Pre-warm + ghost-copy + live cutover.
*   **Policy gates**: AI Shield policies enforced at admission.
*   **Billing + Metering**: Per-proof, per-GPU-minute, per-DAC fee metrics.
*   **Edge-aware scheduling**: Supports EDCoC tags and on-chip capsules.
*   **Attack surface minimized**: mTLS, SPIFFE identities, HSM signing for proofs.

## 3. Components
1.  **CRD**: `KaaSCluster`, `ProofedDeployment`, `DACCapsule`
2.  **Controller**: Watches CRDs, handles lifecycle (build→sign→deploy→verify)
3.  **Admission Webhook**: Enforces AI Shield policies and UTID attestation
4.  **Autoscaler**: Proof-aware HPA (hooks into Prometheus + proof_cost_estimator)
5.  **Migration Controller**: Prewarm, ghost copy, migrate, verify SPA
6.  **Billing Exporter**: Emits metrics for billing system (Kong/Apigee plugin)
7.  **Proof Verifier**: Caches verified proofs for fast admissions
8.  **UTID Manager**: Binds hardware token / identity if edge-hosted

## 4. Example CRD: ProofedDeployment

```yaml
apiVersion: infra.industriverse.ai/v1
kind: ProofedDeployment
metadata:
  name: metal-optimize
spec:
  template:
    metadata:
      labels:
        capsule: m2n2-metal
    spec:
      containers:
      - name: engine
        image: registry.industriverse/m2n2:tag
        resources:
          limits: { nvidia.com/gpu: 1 }
  proofPolicy:
    required: true
    proofTypes: ["mathematical_proof","sim_alignment"]
  utidBinding:
    type: "hardware-bound"   # or "soft"
  prewarm: true
  autoscale:
    minReplicas: 1
    maxReplicas: 5
    proofCostTarget: 0.05   # $/run budget
```

## 5. Controller Logic (Pseudocode)

```python
def on_proofeddeployment_create(pd):
    build_capsule_image(pd)
    sign_image_with_hsm()
    upload_proof_materials_to_proof_registry(pd)
    if pd.spec.prewarm:
        create_prewarm_pod(pd)  # warm GPU pool
    create_k8s_deployment(pd)
    attach_admission_webhook(pd)  # enforce AI Shield
```

## 6. Admission Webhook Checks
*   Verify container image signature
*   Verify proof bundle exists for manifest (sha256)
*   Validate UTID binding (if hardware-bound, challenge attestation)
*   Evaluate risk via AI Shield policy model (SwiReasoning + ACE playbook)

## 7. Metrics
*   `kaas.proofs.attested_total`
*   `kaas.hot_migrations.latency_ms{prewarm=true}`
*   `kaas.billing.gpu_minutes`
*   `kaas.utid.failed_attestations`
