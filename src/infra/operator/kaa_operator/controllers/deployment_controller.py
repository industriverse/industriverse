import kopf
import kubernetes
import yaml
from src.infra.operator.kaa_operator.proof_validators.validator import validate_proof_bundle

@kopf.on.create('infra.industriverse.ai', 'v1', 'proofeddeployments')
def create_fn(spec, name, namespace, logger, **kwargs):
    logger.info(f"Creating ProofedDeployment: {name}")
    
    # 1. Validate Proof Policy
    proof_policy = spec.get('proofPolicy', {})
    if proof_policy.get('required', True):
        bundle = {
            "utid": proof_policy.get('utid'),
            "proof_hash": proof_policy.get('proofHash')
        }
        if not validate_proof_bundle(bundle):
             raise kopf.PermanentError("Proof validation failed: UTID or proof_hash missing")
        logger.info("✅ Proof bundle validated")

    # 2. Handle Pre-warming
    if spec.get('prewarm', False):
        logger.info("🔥 Pre-warming GPU pool for instant deployment...")
        # Logic to spin up a pre-warmed pod would go here

    # 3. Create Child Deployment
    # We create a standard K8s Deployment based on the template
    template = spec.get('template', {})
    deployment_body = {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {
            "name": f"{name}-deploy",
            "namespace": namespace,
            "ownerReferences": [
                {
                    "apiVersion": "infra.industriverse.ai/v1",
                    "kind": "ProofedDeployment",
                    "name": name,
                    "uid": kwargs.get('uid'),
                    "controller": True,
                    "blockOwnerDeletion": True
                }
            ]
        },
        "spec": {
            "replicas": spec.get('autoscale', {}).get('minReplicas', 1),
            "selector": {"matchLabels": {"app": name}},
            "template": template
        }
    }
    
    # Ensure labels and annotations match
    if 'metadata' not in deployment_body['spec']['template']:
        deployment_body['spec']['template']['metadata'] = {}
    if 'labels' not in deployment_body['spec']['template']['metadata']:
        deployment_body['spec']['template']['metadata']['labels'] = {}
    if 'annotations' not in deployment_body['spec']['template']['metadata']:
        deployment_body['spec']['template']['metadata']['annotations'] = {}
    deployment_body['spec']['template']['metadata']['labels']['app'] = name
    # Propagate UTID and proof hash annotations for proof-assisted scheduling
    if proof_policy.get('utid'):
        deployment_body['spec']['template']['metadata']['annotations']['utid'] = proof_policy.get('utid')
    if proof_policy.get('proofHash'):
        deployment_body['spec']['template']['metadata']['annotations']['proofHash'] = proof_policy.get('proofHash')
    if proof_policy.get('proofScore'):
        deployment_body['spec']['template']['metadata']['annotations']['proofScore'] = str(proof_policy.get('proofScore'))

    api = kubernetes.client.AppsV1Api()
    try:
        obj = api.create_namespaced_deployment(namespace=namespace, body=deployment_body)
        logger.info(f"🚀 Child Deployment created: {obj.metadata.name}")
    except kubernetes.client.rest.ApiException as e:
        raise kopf.PermanentError(f"Failed to create child deployment: {e}")

    return {'status': 'deployed', 'proof_verified': True}

@kopf.on.update('infra.industriverse.ai', 'v1', 'proofeddeployments')
def update_fn(spec, name, namespace, logger, **kwargs):
    logger.info(f"Updating ProofedDeployment: {name}")
    # Update logic for child deployment would go here
