from src.proof_core.proof_hub.lifecycle import LIFECYCLE_STATES, advance_state


def next_state(current: str) -> str:
    return advance_state(current)
