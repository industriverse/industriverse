"""
Capsule Instantiator Agent Module

This module serves as the entry point for the Capsule Instantiator Agent package.
It imports and exposes the main components of the agent.
"""

from .capsule_instantiator_agent import CapsuleInstantiatorAgent
from .capsule_blueprint_manager import CapsuleBlueprintManager
from .capsule_factory import CapsuleFactory
from .capsule_validator import CapsuleValidator
from .capsule_registry_client import CapsuleRegistryClient

__all__ = [
    'CapsuleInstantiatorAgent',
    'CapsuleBlueprintManager',
    'CapsuleFactory',
    'CapsuleValidator',
    'CapsuleRegistryClient'
]
