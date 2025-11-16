"""
ASAL (Autonomous Scoring and Learning) Service Package

This package provides consciousness scoring and hypothesis evaluation capabilities
based on the Orch OR (Orchestrated Objective Reduction) framework.

Key Components:
- ASALService: Main service for consciousness scoring
- ConsciousnessScore: Multi-dimensional consciousness score
- HypothesisEvaluation: Complete hypothesis evaluation
- ConsciousnessDimension: Consciousness dimensions enum
- ASALConfig: Configuration for ASAL service

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

from .asal_service import (
    ASALService,
    ASALConfig,
    ConsciousnessScore,
    ConsciousnessDimension,
    HypothesisEvaluation
)

__all__ = [
    "ASALService",
    "ASALConfig",
    "ConsciousnessScore",
    "ConsciousnessDimension",
    "HypothesisEvaluation"
]

__version__ = "1.0.0"
