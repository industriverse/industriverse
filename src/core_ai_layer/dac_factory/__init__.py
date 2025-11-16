"""
DAC Factory Package

This package provides the complete DAC (Deploy Anywhere Capsule) Factory
infrastructure for transforming hypotheses into deployable intelligent capsules.

Key Components:
- DACEngine: Multi-cloud Kubernetes orchestration
- DACLifecycleManager: Capsule packaging and version management
- UTIDGenerator: Universal Traceable Identifier generation
- ProofGenerator: zk-SNARK proof generation
- EnergySignature: Thermodynamic energy signature calculation

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

from .dac_engine import (
    DACEngine,
    DACEngineConfig,
    DACManifest,
    DeploymentInfo,
    CloudProvider,
    DeploymentStatus,
    KubernetesClient
)

__all__ = [
    "DACEngine",
    "DACEngineConfig",
    "DACManifest",
    "DeploymentInfo",
    "CloudProvider",
    "DeploymentStatus",
    "KubernetesClient"
]

__version__ = "1.0.0"

from .dac_lifecycle_manager import (
    DACLifecycleManager,
    DACLifecycleConfig,
    Hypothesis,
    CapsuleVersion,
    CapsuleStatus,
    UpgradeStrategy,
    UpgradeResult
)

__all__.extend([
    "DACLifecycleManager",
    "DACLifecycleConfig",
    "Hypothesis",
    "CapsuleVersion",
    "CapsuleStatus",
    "UpgradeStrategy",
    "UpgradeResult"
])

from .utid_generator import (
    UTIDGenerator,
    UTIDGeneratorConfig,
    UTID,
    UTIDType,
    BlockchainNetwork,
    BlockchainConnector,
    BlockchainAnchor
)

__all__.extend([
    "UTIDGenerator",
    "UTIDGeneratorConfig",
    "UTID",
    "UTIDType",
    "BlockchainNetwork",
    "BlockchainConnector",
    "BlockchainAnchor"
])
