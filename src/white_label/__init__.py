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

__version__ = "2.0.0"

__all__ = [
    # SDK
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
