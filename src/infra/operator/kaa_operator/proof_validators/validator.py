def validate_proof_bundle(bundle: dict) -> bool:
    """
    Validates a cryptographic proof bundle.
    Requires utid and proof_hash fields present and non-empty.
    """
    if not bundle:
        return False
    utid = bundle.get("utid")
    proof_hash = bundle.get("proof_hash")
    return bool(utid and proof_hash)
