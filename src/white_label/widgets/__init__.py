"""
White-Label Widget SDK

Embeddable components for partner integration:
- AI Shield Dashboard Widget
- Compliance Score Widget
- Threat Heatmap Widget
- Security Orb Widget
- Energy Flow Graph Widget
- Predictive Maintenance Widget
- Shadow Twin 3D Widget
- Research Explorer Widget
"""

from .widget_sdk import (
    WidgetBase,
    WidgetConfig,
    WidgetTheme,
    WidgetRegistry,
    get_widget_registry
)

from .ai_shield_dashboard import AIShieldDashboardWidget
from .compliance_score import ComplianceScoreWidget
from .threat_heatmap import ThreatHeatmapWidget
from .security_orb import SecurityOrbWidget
from .energy_flow_graph import EnergyFlowGraphWidget
from .predictive_maintenance import PredictiveMaintenanceWidget
from .shadow_twin_3d import ShadowTwin3DWidget
from .research_explorer import ResearchExplorerWidget

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
