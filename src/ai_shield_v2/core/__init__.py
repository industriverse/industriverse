"""
AI Shield v2 - Core Module
===========================

Core functionality for PDE-hash validation and canonical state identity.

Copyright © 2025 Industriverse Corporation. All Rights Reserved.
"""

from .pde_hash_validator import (
    # Main validator
    PDEHashValidator,
    PDEHashGenerator,
    PDEHashRegistry,

    # Enums
    ValidationStatus,
    TransitionType,

    # Data classes
    PDEHashRecord,
    ValidationResult,
    TransitionValidation
)

__all__ = [
    "PDEHashValidator",
    "PDEHashGenerator",
    "PDEHashRegistry",
    "ValidationStatus",
    "TransitionType",
    "PDEHashRecord",
    "ValidationResult",
    "TransitionValidation"
]
