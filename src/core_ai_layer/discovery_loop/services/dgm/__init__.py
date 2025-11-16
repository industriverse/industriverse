"""
Deep Genetic Modification (DGM) Service Package

This package provides the DGM service for hypothesis evolution using genetic algorithms.
"""

from .dgm_service import (
    DGMService,
    DGMConfig,
    Hypothesis,
    example_fitness_function
)

__all__ = [
    "DGMService",
    "DGMConfig",
    "Hypothesis",
    "example_fitness_function"
]
