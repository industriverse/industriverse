"""
Capsule Manifest Validator Module

This module provides components for validating capsule manifests to ensure they meet all requirements
for deployment. It serves as a critical safeguard against deployment failures by verifying
that capsule manifests are complete, consistent, and compliant with organizational policies.
"""

from .capsule_manifest_validator import CapsuleManifestValidator
from .capsule_manifest_validator_agent import CapsuleManifestValidatorAgent

__all__ = [
    'CapsuleManifestValidator',
    'CapsuleManifestValidatorAgent'
]
