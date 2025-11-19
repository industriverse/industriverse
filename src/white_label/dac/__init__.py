"""
DAC (Deploy Anywhere Capsule) System

Packaging and distribution system for Industriverse white-label deployments.
Enables partners to deploy AI Shield, widgets, and I³ capabilities across
any infrastructure.

Components:
- Manifest schema and validation
- DAC registry and versioning
- Deployment automation
- Multi-cloud orchestration
"""

from .manifest_schema import (
    DACManifest,
    DACTier,
    TargetEnvironment,
    WidgetType,
    ResourceRequirements,
    NetworkConfig,
    SecurityConfig,
    ThemeCustomization,
    WidgetConfig,
    ManifestValidator,
    create_example_manifest,
)

from .registry import (
    DACRegistry,
    DACPackage,
    DACVersion,
    get_dac_registry,
)

from .deployer import (
    DACDeployer,
    DeployerBase,
    KubernetesDeployer,
    DockerDeployer,
    DeploymentStatus,
    DeploymentResult,
)

__all__ = [
    # Manifest
    "DACManifest",
    "DACTier",
    "TargetEnvironment",
    "WidgetType",
    "ResourceRequirements",
    "NetworkConfig",
    "SecurityConfig",
    "ThemeCustomization",
    "WidgetConfig",
    "ManifestValidator",
    "create_example_manifest",

    # Registry
    "DACRegistry",
    "DACPackage",
    "DACVersion",
    "get_dac_registry",

    # Deployment
    "DACDeployer",
    "DeployerBase",
    "KubernetesDeployer",
    "DockerDeployer",
    "DeploymentStatus",
    "DeploymentResult",
]
