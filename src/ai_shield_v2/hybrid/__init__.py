"""
AI Shield v2 - Hybrid Superstructure Module
============================================

Phase 6: Full Hybrid Superstructure

Unified orchestration layer that coordinates all AI Shield v2 subsystems
through a three-role architecture.

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

from .hybrid_superstructure import (
    # Main superstructure
    HybridSuperstructure,

    # Enums
    SystemRole,
    OperationMode,
    SuperstructureStatus,

    # Data classes
    RoleMetrics,
    SuperstructureMetrics,
    ThreatResponse
)

__all__ = [
    # Main superstructure
    "HybridSuperstructure",

    # Enums
    "SystemRole",
    "OperationMode",
    "SuperstructureStatus",

    # Data classes
    "RoleMetrics",
    "SuperstructureMetrics",
    "ThreatResponse"
]
