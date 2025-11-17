"""
Adaptive UX Module for Dynamic Capsule Personalization.

Week 10 deliverable - Complete adaptive UX system with:
- Adaptive UX Engine (core personalization)
- A/B Testing Framework (experimentation)
- Dynamic Layout Adjuster (real-time layout adaptation)
- Data Density Tuner (progressive information disclosure)
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

from .dynamic_layout_adjuster import (
    DynamicLayoutAdjuster,
    LayoutRule,
    LayoutAdjustment,
    TriggerType,
    AdjustmentStrategy,
    dynamic_layout_adjuster
)

from .data_density_tuner import (
    DataDensityTuner,
    DensityLevel,
    InformationPriority,
    InformationElement,
    DensityConfiguration,
    DensityAdjustment,
    data_density_tuner
)

__all__ = [
    # Core engine
    "AdaptiveUXEngine",
    "UXConfiguration",
    "UXAdjustment",
    "LayoutType",
    "DataDensity",
    "AnimationSpeed",
    "adaptive_ux_engine",
    
    # A/B testing
    "ABTestingFramework",
    "Experiment",
    "ExperimentVariant",
    "ExperimentAssignment",
    "ExperimentStatus",
    "VariantType",
    "ab_testing_framework",
    
    # Dynamic layout
    "DynamicLayoutAdjuster",
    "LayoutRule",
    "LayoutAdjustment",
    "TriggerType",
    "AdjustmentStrategy",
    "dynamic_layout_adjuster",
    
    # Data density
    "DataDensityTuner",
    "DensityLevel",
    "InformationPriority",
    "InformationElement",
    "DensityConfiguration",
    "DensityAdjustment",
    "data_density_tuner"
]
