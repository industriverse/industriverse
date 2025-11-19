"""
White-Label Platform - Industriverse

Complete white-label solution enabling partners to rebrand and embed
Industriverse capabilities into their own products.

Architecture:
- Design token system for theme customization
- 8 embeddable widget components
- DAC (Deploy Anywhere Capsule) packaging
- Partner configuration portal
- I³ intelligence layer integration
- Credit protocol economy

Revenue Model:
- Tier 1: Security Essentials ($5K-$15K/mo)
- Tier 2: Domain Intelligence ($25K-$50K/mo)
- Tier 3: Full Discovery Platform ($100K-$500K/mo)
- Partner revenue share: 30-40%
"""

from .widgets import (
    # SDK
    WidgetBase,
    WidgetConfig,
    WidgetTheme,
    WidgetRegistry,
    get_widget_registry,

    # Widgets
    AIShieldDashboardWidget,
    ComplianceScoreWidget,
    ThreatHeatmapWidget,
    SecurityOrbWidget,
    EnergyFlowGraphWidget,
    PredictiveMaintenanceWidget,
    ShadowTwin3DWidget,
    ResearchExplorerWidget,
)

from .dac import (
    DACManifest,
    DACTier,
    DACRegistry,
    DACDeployer,
    get_dac_registry,
)

from .partner_portal import (
    Partner,
    PartnerManager,
    AnalyticsTracker,
    get_partner_manager,
    get_analytics_tracker,
    config_api_app,
)

from .i3 import (
    RDREngine,
    ShadowTwinBackend,
    MSEPIntegration,
    OBMIOrchestrator,
    get_rdr_engine,
    get_shadow_twin,
    get_msep_integration,
    get_obmi_orchestrator,
    initialize_i3_platform,
)

__version__ = "2.0.0"

__all__ = [
    # Widget SDK
    "WidgetBase",
    "WidgetConfig",
    "WidgetTheme",
    "WidgetRegistry",
    "get_widget_registry",

    # Widgets
    "AIShieldDashboardWidget",
    "ComplianceScoreWidget",
    "ThreatHeatmapWidget",
    "SecurityOrbWidget",
    "EnergyFlowGraphWidget",
    "PredictiveMaintenanceWidget",
    "ShadowTwin3DWidget",
    "ResearchExplorerWidget",

    # DAC
    "DACManifest",
    "DACTier",
    "DACRegistry",
    "DACDeployer",
    "get_dac_registry",

    # Partner Portal
    "Partner",
    "PartnerManager",
    "AnalyticsTracker",
    "get_partner_manager",
    "get_analytics_tracker",
    "config_api_app",

    # I³ Intelligence Layer
    "RDREngine",
    "ShadowTwinBackend",
    "MSEPIntegration",
    "OBMIOrchestrator",
    "get_rdr_engine",
    "get_shadow_twin",
    "get_msep_integration",
    "get_obmi_orchestrator",
    "initialize_i3_platform",
]


def initialize_widget_registry():
    """Initialize and register all widgets"""
    registry = get_widget_registry()

    registry.register("ai-shield-dashboard", AIShieldDashboardWidget)
    registry.register("compliance-score", ComplianceScoreWidget)
    registry.register("threat-heatmap", ThreatHeatmapWidget)
    registry.register("security-orb", SecurityOrbWidget)
    registry.register("energy-flow-graph", EnergyFlowGraphWidget)
    registry.register("predictive-maintenance", PredictiveMaintenanceWidget)
    registry.register("shadow-twin-3d", ShadowTwin3DWidget)
    registry.register("research-explorer", ResearchExplorerWidget)

    return registry


# Auto-initialize on import
initialize_widget_registry()
