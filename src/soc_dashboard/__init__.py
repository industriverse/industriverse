"""
Security Operations Center (SOC) Dashboard

Real-time threat monitoring and visualization platform:
- REST API for threat data
- WebSocket streaming for real-time updates
- AR/VR threat visualization
- Thermodynamic heatmaps and attack timelines
"""

from .soc_api import (
    SOCDashboardAPI,
    get_soc_dashboard_api
)

from .arvr_threat_visualizer import (
    ARVRThreatVisualizer,
    get_arvr_threat_visualizer
)

__all__ = [
    "SOCDashboardAPI",
    "get_soc_dashboard_api",
    "ARVRThreatVisualizer",
    "get_arvr_threat_visualizer"
]
