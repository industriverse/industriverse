"""
Capsule Protocol Package

Platform-agnostic capsule protocol specification.
"""

from .capsule_protocol import (
    Capsule,
    CapsuleAttributes,
    CapsuleContentState,
    CapsuleType,
    CapsuleStatus,
    CapsulePriority,
    CapsuleAction,
    CapsuleActionResult,
    CapsuleEvent,
    PresentationMode
)

from .capsule_state_machine import (
    CapsuleStateMachine
)

__all__ = [
    "Capsule",
    "CapsuleAttributes",
    "CapsuleContentState",
    "CapsuleType",
    "CapsuleStatus",
    "CapsulePriority",
    "CapsuleAction",
    "CapsuleActionResult",
    "CapsuleEvent",
    "PresentationMode",

    "CapsuleStateMachine"
]
