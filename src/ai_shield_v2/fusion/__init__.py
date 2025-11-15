"""
AI Shield v2 - Physics Fusion Engine Module
============================================

Multi-detector consensus engine with ICI scoring and automated response.

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

from .physics_fusion_engine import (
    # Main engine
    PhysicsFusionEngine,

    # Enums
    ResponseAction,
    ConsensusType,

    # Data classes
    ConsensusMetrics,
    ICIScore,
    ThreatIntelligence,
    FusionResult
)

__all__ = [
    "PhysicsFusionEngine",
    "ResponseAction",
    "ConsensusType",
    "ConsensusMetrics",
    "ICIScore",
    "ThreatIntelligence",
    "FusionResult"
]
