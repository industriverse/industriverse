"""
Overseer Module for Capsule Orchestration and Personalized Launchpads.

Week 12 deliverable - Complete overseer system with:
- Capsule Orchestrator (personalized launchpad generation)
- Spawn Rules (automatic capsule creation)
- Lifecycle Management (create → complete → archive)
- REST API (launchpad and capsule management)
"""

from .capsule_orchestrator import (
    CapsuleOrchestrator,
    Capsule,
    UserLaunchpad,
    SpawnRule,
    CapsuleState,
    VisibilityRule,
    capsule_orchestrator
)

__all__ = [
    "CapsuleOrchestrator",
    "Capsule",
    "UserLaunchpad",
    "SpawnRule",
    "CapsuleState",
    "VisibilityRule",
    "capsule_orchestrator"
]
