"""
Adaptive UX Module for Dynamic Capsule Personalization.

Week 10 deliverable - Adaptive UX Engine with A/B testing framework.
"""

from .adaptive_ux_engine import (
    AdaptiveUXEngine,
    UXConfiguration,
    UXAdjustment,
    LayoutType,
    DataDensity,
    AnimationSpeed,
    adaptive_ux_engine
)

from .ab_testing_framework import (
    ABTestingFramework,
    Experiment,
    ExperimentVariant,
    ExperimentAssignment,
    ExperimentStatus,
    VariantType,
    ab_testing_framework
)

__all__ = [
    "AdaptiveUXEngine",
    "UXConfiguration",
    "UXAdjustment",
    "LayoutType",
    "DataDensity",
    "AnimationSpeed",
    "adaptive_ux_engine",
    "ABTestingFramework",
    "Experiment",
    "ExperimentVariant",
    "ExperimentAssignment",
    "ExperimentStatus",
    "VariantType",
    "ab_testing_framework"
]
