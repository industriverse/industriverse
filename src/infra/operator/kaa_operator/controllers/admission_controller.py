import json
import kopf

def _has_required_annotations(template_metadata):
    annotations = template_metadata.get("annotations", {})
    return "utid" in annotations and "proofHash" in annotations


@kopf.on.validate("pods")
def validate_pod(body, **kwargs):
    metadata = body.get("metadata", {})
    annotations = metadata.get("annotations", {})
    if "utid" not in annotations or "proofHash" not in annotations:
        raise kopf.AdmissionError("Pod must include utid and proofHash annotations")


@kopf.on.mutate("pods")
def mutate_pod(body, patch, **kwargs):
    metadata = body.get("metadata", {})
    annotations = metadata.get("annotations", {})
    # If annotations missing, attempt to add placeholders from labels (proof-assisted scheduling)
    labels = metadata.get("labels", {})
    changed = False
    if "utid" not in annotations and "utid" in labels:
        annotations["utid"] = labels["utid"]
        changed = True
    if "proofHash" not in annotations and "proofHash" in labels:
        annotations["proofHash"] = labels["proofHash"]
        changed = True
    if changed:
        patch.metadata.annotations = annotations
    # Add proofScore label if present to influence schedulers
    if "proofScore" in annotations:
        if "proofScore" not in labels:
            labels["proofScore"] = annotations["proofScore"]
            patch.metadata.labels = labels
    return patch
