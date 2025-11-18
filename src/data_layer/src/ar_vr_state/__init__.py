"""
AR/VR State Persistence Module

Handles persistence of AR/VR spatial data, capsule states, and interaction history.

Part of Week 18-19: Architecture Unification - Day 6
"""

from .ar_vr_state_manager import (
    ARVRStateManager,
    get_ar_vr_state_manager
)

__all__ = [
    "ARVRStateManager",
    "get_ar_vr_state_manager"
]
