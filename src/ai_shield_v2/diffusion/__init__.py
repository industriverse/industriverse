"""
AI Shield v2 - Diffusion Module
================================

Diffusion Engine integration for predictive threat simulation,
adversarial detection, and shadow twin pre-simulation.

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

from .diffusion_engine import (
    # Main engine
    DiffusionEngine,
    NoiseScheduler,

    # Enums
    DiffusionMode,
    ThreatClass,
    EnergyFluxLevel,

    # Data classes
    ThreatVector,
    AttackSurface,
    DiffusionState,
    DiffusionResult
)

from .adversarial_detector import (
    # Main detector
    AdversarialDetector,

    # Enums
    PerturbationType,

    # Data classes
    EnergyMonitor,
    ModeCollapseMetrics,
    RegimeShiftMetrics,
    AdversarialDetectionResult
)

from .shadow_twin import (
    # Main simulator
    ShadowTwinSimulator,

    # Enums
    SimulationDecision,
    ActionType,

    # Data classes
    ProposedAction,
    ShadowEnvironment,
    OutcomePrediction,
    RiskAssessment,
    ShadowTwinResult
)

__all__ = [
    # Diffusion Engine
    "DiffusionEngine",
    "NoiseScheduler",
    "DiffusionMode",
    "ThreatClass",
    "EnergyFluxLevel",
    "ThreatVector",
    "AttackSurface",
    "DiffusionState",
    "DiffusionResult",

    # Adversarial Detector
    "AdversarialDetector",
    "PerturbationType",
    "EnergyMonitor",
    "ModeCollapseMetrics",
    "RegimeShiftMetrics",
    "AdversarialDetectionResult",

    # Shadow Twin
    "ShadowTwinSimulator",
    "SimulationDecision",
    "ActionType",
    "ProposedAction",
    "ShadowEnvironment",
    "OutcomePrediction",
    "RiskAssessment",
    "ShadowTwinResult"
]
