"""
AI Shield v2 - Universal Pattern Detectors (UPD) Module
========================================================

Seven specialized physics-domain detectors with extended detection capabilities.

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

from .universal_pattern_detectors import (
    # Core classes
    UniversalPatternDetectorsSuite,
    BaseDetector,

    # Individual detectors
    SwarmDetector,
    PropagationDetector,
    FlowInstabilityDetector,
    ResonanceDetector,
    StabilityDetector,
    PlanetaryDetector,
    RadiativeDetector,

    # Enums
    ThreatLevel,
    ExtendedDomain,

    # Data classes
    DetectionPattern,
    DetectionResult,
    UPDSuiteResult
)

__all__ = [
    "UniversalPatternDetectorsSuite",
    "BaseDetector",
    "SwarmDetector",
    "PropagationDetector",
    "FlowInstabilityDetector",
    "ResonanceDetector",
    "StabilityDetector",
    "PlanetaryDetector",
    "RadiativeDetector",
    "ThreatLevel",
    "ExtendedDomain",
    "DetectionPattern",
    "DetectionResult",
    "UPDSuiteResult"
]
