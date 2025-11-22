# DAC Capsule Loader & Automation Loop

## 1. Goal
Deterministic capsule packaging, sign → push → deploy → proof generation → register.

## 2. Capsule Package Layout
```
capsule_m2n2-metal-0.1.0.tar.gz
|
|-- capsule.json            # Manifest (metadata, versions, utid requirements)
|-- capsule.tarball         # OCI image or filesystem blob
|-- scripts/
|   |-- install.sh
|   |-- healthcheck.sh
|-- expansion/              # The expansion pack to run
|   |-- m2n2/
|       |-- model.pt
|       |-- runner.py
|-- proof-hooks/
|   |-- generate_proof.py   # Will call /v1/proofs/generate
|-- signature.sig           # Detached signature (HSM-signed)
|-- checksum.sha256
```

## 3. Capsule Manifest (capsule.json)
```json
{
  "name":"m2n2-metal",
  "version":"0.1.0",
  "entrypoint":"expansion/m2n2/runner.py",
  "requirements":[ "gpu:true", "utid:hardware-bound" ],
  "proof_policy":{"required": true, "types":["mathematical_proof","sim_alignment"]},
  "prewarm":true,
  "billing":{"unit":"run","price":5.00}
}
```

## 4. Loader Behavior (On Deploy)
1.  Validate signature (HSM public key), checksum.
2.  Validate manifest capabilities vs target cluster (GPU / UTID).
3.  If `prewarm==true` create a warm pod pool with image preloaded.
4.  Create `ProofedDeployment` CRD pointing to capsule image & manifest.
5.  Trigger `proof_hooks/generate_proof.py` after first run; attach `proof_id` to capsule metadata.
6.  Publish proof bundle to registry & anchor to chains per manifest policy.
7.  Update capsule registry index so clients can fetch `capsule://m2n2-metal:0.1.0?proof=true`.

## 5. Argo Workflow (Automated Loop)
```yaml
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  name: capsule-deploy-loop
spec:
  entrypoint: deploy-capsule
  templates:
  - name: deploy-capsule
    steps:
    - - name: download
        template: download-capsule
    - - name: verify
        template: verify-capsule
    - - name: publish
        template: publish-capsule
    - - name: deploy
        template: deploy-capsule-k8s
    - - name: generate-proof
        template: generate-proof
    # ... (templates omitted for brevity)
```

## 6. Trifecta Integration
*   **UserLM**: Generate persona-specific capsule configs and outreach metadata.
*   **RND1**: Continuously optimizes capsule runtime parameters (GPU fractions, batch size).
*   **ACE**: Logs runs as trajectories, extracts failure modes, appends to playbook.
*   **ASAL**: Every capsule run triggers a lightweight ASAL statistical sanity check.
