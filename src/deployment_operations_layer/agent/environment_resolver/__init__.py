"""
Environment Resolver Module

This module serves as the entry point for the Environment Resolver Agent package.
It imports and exposes the main components of the agent.
"""

from .environment_resolver_agent import EnvironmentResolverAgent
from .environment_detector import EnvironmentDetector
from .capability_analyzer import CapabilityAnalyzer
from .environment_adapter import EnvironmentAdapter
from .resource_calculator import ResourceCalculator

__all__ = [
    'EnvironmentResolverAgent',
    'EnvironmentDetector',
    'CapabilityAnalyzer',
    'EnvironmentAdapter',
    'ResourceCalculator'
]
