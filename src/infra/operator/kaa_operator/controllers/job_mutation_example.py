import kopf


@kopf.on.mutate("jobs")
def mutate_job(body, patch, **kwargs):
    """
    Example mutation for Jobs: ensure utid/proofHash annotations propagate to pod template.
    """
    metadata = body.get("spec", {}).get("template", {}).get("metadata", {})
    annotations = metadata.get("annotations", {})
    labels = metadata.get("labels", {})

    changed = False
    if "utid" in labels and "utid" not in annotations:
        annotations["utid"] = labels["utid"]
        changed = True
    if "proofHash" in labels and "proofHash" not in annotations:
        annotations["proofHash"] = labels["proofHash"]
        changed = True
    if changed:
        patch.spec.template.metadata.annotations = annotations
    return patch
