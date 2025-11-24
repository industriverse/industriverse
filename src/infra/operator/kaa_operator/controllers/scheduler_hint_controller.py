import kopf
import logging


@kopf.on.mutate("deployments")
def add_scheduler_hints(body, patch, **kwargs):
    """
    Add scheduler hints based on proofScore if present.
    """
    template = body.get("spec", {}).get("template", {})
    metadata = template.get("metadata", {})
    annotations = metadata.get("annotations", {})
    labels = metadata.get("labels", {})

    proof_score = annotations.get("proofScore") or labels.get("proofScore")
    if proof_score:
        try:
            score = float(proof_score)
            if score >= 0.8:
                labels["priority"] = "high-proof"
            elif score >= 0.5:
                labels["priority"] = "medium-proof"
            else:
                labels["priority"] = "low-proof"
            patch.spec.template.metadata.labels = labels
        except Exception:
            logging.warning("Invalid proofScore; skipping scheduler hint")
    return patch
