"""
DAC (Deploy Anywhere Capsule) Manifest Schema

Defines the structure and validation rules for DAC deployment packages.
Enables partners to package and deploy Industriverse capabilities across
any infrastructure (cloud, edge, on-premise).
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pathlib import Path


class DACTier(Enum):
    """DAC deployment tiers"""
    SECURITY_ESSENTIALS = "security-essentials"  # $5K-$15K/mo
    DOMAIN_INTELLIGENCE = "domain-intelligence"  # $25K-$50K/mo
    FULL_DISCOVERY = "full-discovery"  # $100K-$500K/mo


class TargetEnvironment(Enum):
    """Supported deployment environments"""
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    KUBERNETES = "kubernetes"
    DOCKER = "docker"
    EDGE = "edge"
    ON_PREMISE = "on-premise"


class WidgetType(Enum):
    """Available widget types"""
    AI_SHIELD_DASHBOARD = "ai-shield-dashboard"
    COMPLIANCE_SCORE = "compliance-score"
    THREAT_HEATMAP = "threat-heatmap"
    SECURITY_ORB = "security-orb"
    ENERGY_FLOW_GRAPH = "energy-flow-graph"
    PREDICTIVE_MAINTENANCE = "predictive-maintenance"
    SHADOW_TWIN_3D = "shadow-twin-3d"
    RESEARCH_EXPLORER = "research-explorer"


@dataclass
class ResourceRequirements:
    """Compute resource requirements"""
    cpu_cores: float = 2.0
    memory_gb: float = 4.0
    storage_gb: float = 50.0
    gpu_required: bool = False
    gpu_memory_gb: Optional[float] = None


@dataclass
class NetworkConfig:
    """Network configuration"""
    requires_internet: bool = True
    ingress_ports: List[int] = field(default_factory=lambda: [80, 443])
    egress_allowed: bool = True
    api_endpoint: str = "https://api.industriverse.ai"


@dataclass
class SecurityConfig:
    """Security configuration"""
    requires_tls: bool = True
    api_key_required: bool = True
    client_cert_required: bool = False
    allowed_origins: List[str] = field(default_factory=list)
    rate_limit_per_minute: int = 1000


@dataclass
class ThemeCustomization:
    """Partner theme customization"""
    theme_base: str = "cosmic"
    custom_colors: Optional[Dict[str, str]] = None
    logo_url: Optional[str] = None
    brand_name: Optional[str] = None
    custom_domain: Optional[str] = None


@dataclass
class WidgetConfig:
    """Individual widget configuration"""
    widget_type: str
    enabled: bool = True
    refresh_interval_ms: int = 5000
    enable_animations: bool = True
    enable_websocket: bool = True
    custom_features: Dict[str, bool] = field(default_factory=dict)


@dataclass
class DACManifest:
    """
    Complete DAC Manifest specification

    Defines everything needed to deploy an Industriverse capsule:
    - Metadata and versioning
    - Target environments
    - Resource requirements
    - Widget configuration
    - Security settings
    - Partner customization
    """

    # Metadata
    name: str
    version: str
    description: str
    partner_id: str
    tier: str  # DACTier enum value

    # Deployment
    target_environments: List[str]  # TargetEnvironment enum values
    resources: ResourceRequirements = field(default_factory=ResourceRequirements)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # Widgets
    widgets: List[WidgetConfig] = field(default_factory=list)
    theme: ThemeCustomization = field(default_factory=ThemeCustomization)

    # Features
    features: Dict[str, bool] = field(default_factory=dict)

    # Integration
    integration_points: Dict[str, Any] = field(default_factory=dict)

    # Metadata
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    deployed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'partner_id': self.partner_id,
            'tier': self.tier,
            'target_environments': self.target_environments,
            'resources': {
                'cpu_cores': self.resources.cpu_cores,
                'memory_gb': self.resources.memory_gb,
                'storage_gb': self.resources.storage_gb,
                'gpu_required': self.resources.gpu_required,
                'gpu_memory_gb': self.resources.gpu_memory_gb,
            },
            'network': {
                'requires_internet': self.network.requires_internet,
                'ingress_ports': self.network.ingress_ports,
                'egress_allowed': self.network.egress_allowed,
                'api_endpoint': self.network.api_endpoint,
            },
            'security': {
                'requires_tls': self.security.requires_tls,
                'api_key_required': self.security.api_key_required,
                'client_cert_required': self.security.client_cert_required,
                'allowed_origins': self.security.allowed_origins,
                'rate_limit_per_minute': self.security.rate_limit_per_minute,
            },
            'widgets': [
                {
                    'widget_type': w.widget_type,
                    'enabled': w.enabled,
                    'refresh_interval_ms': w.refresh_interval_ms,
                    'enable_animations': w.enable_animations,
                    'enable_websocket': w.enable_websocket,
                    'custom_features': w.custom_features,
                }
                for w in self.widgets
            ],
            'theme': {
                'theme_base': self.theme.theme_base,
                'custom_colors': self.theme.custom_colors,
                'logo_url': self.theme.logo_url,
                'brand_name': self.theme.brand_name,
                'custom_domain': self.theme.custom_domain,
            },
            'features': self.features,
            'integration_points': self.integration_points,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deployed_at': self.deployed_at,
        }

    def to_yaml(self) -> str:
        """Export manifest as YAML"""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DACManifest':
        """Create manifest from dictionary"""
        resources = ResourceRequirements(**data.get('resources', {}))
        network = NetworkConfig(**data.get('network', {}))
        security = SecurityConfig(**data.get('security', {}))
        theme = ThemeCustomization(**data.get('theme', {}))

        widgets = [
            WidgetConfig(**w) for w in data.get('widgets', [])
        ]

        return cls(
            name=data['name'],
            version=data['version'],
            description=data['description'],
            partner_id=data['partner_id'],
            tier=data['tier'],
            target_environments=data.get('target_environments', []),
            resources=resources,
            network=network,
            security=security,
            widgets=widgets,
            theme=theme,
            features=data.get('features', {}),
            integration_points=data.get('integration_points', {}),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            deployed_at=data.get('deployed_at'),
        )

    @classmethod
    def from_yaml(cls, yaml_content: str) -> 'DACManifest':
        """Create manifest from YAML string"""
        data = yaml.safe_load(yaml_content)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls, file_path: Path) -> 'DACManifest':
        """Load manifest from YAML file"""
        with open(file_path, 'r') as f:
            return cls.from_yaml(f.read())

    def save(self, file_path: Path):
        """Save manifest to YAML file"""
        with open(file_path, 'w') as f:
            f.write(self.to_yaml())


class ManifestValidator:
    """Validates DAC manifests"""

    @staticmethod
    def validate(manifest: DACManifest) -> tuple[bool, List[str]]:
        """
        Validate manifest completeness and correctness

        Returns:
            (is_valid, list_of_errors)
        """
        errors = []

        # Validate required fields
        if not manifest.name:
            errors.append("Manifest name is required")

        if not manifest.version:
            errors.append("Manifest version is required")

        if not manifest.partner_id:
            errors.append("Partner ID is required")

        # Validate tier
        try:
            DACTier(manifest.tier)
        except ValueError:
            errors.append(f"Invalid tier: {manifest.tier}. Must be one of: {[t.value for t in DACTier]}")

        # Validate environments
        for env in manifest.target_environments:
            try:
                TargetEnvironment(env)
            except ValueError:
                errors.append(f"Invalid target environment: {env}")

        # Validate resource requirements
        if manifest.resources.cpu_cores <= 0:
            errors.append("CPU cores must be positive")

        if manifest.resources.memory_gb <= 0:
            errors.append("Memory must be positive")

        if manifest.resources.storage_gb <= 0:
            errors.append("Storage must be positive")

        if manifest.resources.gpu_required and not manifest.resources.gpu_memory_gb:
            errors.append("GPU memory must be specified when GPU is required")

        # Validate widgets
        if not manifest.widgets:
            errors.append("At least one widget must be configured")

        for widget in manifest.widgets:
            try:
                WidgetType(widget.widget_type)
            except ValueError:
                errors.append(f"Invalid widget type: {widget.widget_type}")

            if widget.refresh_interval_ms < 100:
                errors.append(f"Widget refresh interval too low: {widget.refresh_interval_ms}ms (minimum 100ms)")

        # Validate network config
        if not manifest.network.ingress_ports:
            errors.append("At least one ingress port must be specified")

        for port in manifest.network.ingress_ports:
            if port < 1 or port > 65535:
                errors.append(f"Invalid port number: {port}")

        # Validate security config
        if manifest.security.rate_limit_per_minute < 1:
            errors.append("Rate limit must be at least 1 request per minute")

        # Validate tier-specific requirements
        tier = DACTier(manifest.tier)
        if tier == DACTier.FULL_DISCOVERY:
            # Full discovery requires Shadow Twin and Research Explorer
            widget_types = [w.widget_type for w in manifest.widgets]
            if 'shadow-twin-3d' not in widget_types:
                errors.append("Full Discovery tier requires Shadow Twin 3D widget")
            if 'research-explorer' not in widget_types:
                errors.append("Full Discovery tier requires Research Explorer widget")

        return (len(errors) == 0, errors)

    @staticmethod
    def validate_file(file_path: Path) -> tuple[bool, List[str]]:
        """Validate manifest file"""
        try:
            manifest = DACManifest.from_file(file_path)
            return ManifestValidator.validate(manifest)
        except Exception as e:
            return (False, [f"Failed to load manifest: {str(e)}"])


def create_example_manifest(partner_id: str, tier: DACTier) -> DACManifest:
    """Create an example manifest for a given tier"""

    base_widgets = [
        WidgetConfig(widget_type="ai-shield-dashboard"),
        WidgetConfig(widget_type="compliance-score"),
        WidgetConfig(widget_type="security-orb"),
    ]

    domain_widgets = base_widgets + [
        WidgetConfig(widget_type="threat-heatmap"),
        WidgetConfig(widget_type="energy-flow-graph"),
        WidgetConfig(widget_type="predictive-maintenance"),
    ]

    full_widgets = domain_widgets + [
        WidgetConfig(widget_type="shadow-twin-3d"),
        WidgetConfig(widget_type="research-explorer"),
    ]

    widgets_map = {
        DACTier.SECURITY_ESSENTIALS: base_widgets,
        DACTier.DOMAIN_INTELLIGENCE: domain_widgets,
        DACTier.FULL_DISCOVERY: full_widgets,
    }

    resources_map = {
        DACTier.SECURITY_ESSENTIALS: ResourceRequirements(
            cpu_cores=2.0,
            memory_gb=4.0,
            storage_gb=50.0
        ),
        DACTier.DOMAIN_INTELLIGENCE: ResourceRequirements(
            cpu_cores=4.0,
            memory_gb=8.0,
            storage_gb=100.0
        ),
        DACTier.FULL_DISCOVERY: ResourceRequirements(
            cpu_cores=8.0,
            memory_gb=16.0,
            storage_gb=200.0,
            gpu_required=True,
            gpu_memory_gb=8.0
        ),
    }

    return DACManifest(
        name=f"{partner_id}-{tier.value}",
        version="1.0.0",
        description=f"Industriverse {tier.value} deployment capsule",
        partner_id=partner_id,
        tier=tier.value,
        target_environments=["kubernetes", "docker", "aws"],
        resources=resources_map[tier],
        widgets=widgets_map[tier],
        features={
            "quantum_monitoring": tier == DACTier.FULL_DISCOVERY,
            "grid_validation": tier in [DACTier.DOMAIN_INTELLIGENCE, DACTier.FULL_DISCOVERY],
            "swarm_monitoring": tier in [DACTier.DOMAIN_INTELLIGENCE, DACTier.FULL_DISCOVERY],
            "i3_integration": tier == DACTier.FULL_DISCOVERY,
        }
    )
