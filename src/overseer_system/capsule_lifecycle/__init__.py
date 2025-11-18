"""
Capsule Lifecycle Module

Central lifecycle management for capsules across all layers.

Part of Week 18-19: Architecture Unification
"""

from .capsule_lifecycle_coordinator import (
    CapsuleLifecycleCoordinator,
    CapsuleLifecycleStage,
    CapsuleSource,
    CapsuleLifecycleContext,
    get_capsule_lifecycle_coordinator
)

__all__ = [
    "CapsuleLifecycleCoordinator",
    "CapsuleLifecycleStage",
    "CapsuleSource",
    "CapsuleLifecycleContext",
    "get_capsule_lifecycle_coordinator"
]
