import kopf


@kopf.on.mutate("statefulsets")
def mutate_statefulset(body, patch, **kwargs):
    """
    Example mutation for StatefulSets: ensure utid/proofHash annotations propagate to pod template.
    """
    template = body.get("spec", {}).get("template", {})
    metadata = template.get("metadata", {})
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
