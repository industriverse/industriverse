LIFECYCLE_STATES = ["queued", "processing", "verified", "validated"]


def advance_state(current: str) -> str:
    if current not in LIFECYCLE_STATES:
        return "queued"
    idx = LIFECYCLE_STATES.index(current)
    if idx < len(LIFECYCLE_STATES) - 1:
        return LIFECYCLE_STATES[idx + 1]
    return current
