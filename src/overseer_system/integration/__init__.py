"""
Integration package initialization module.

This module initializes the integration package for the Overseer System,
which provides integration with all Industriverse layers and external systems.

Author: Manus AI
Date: May 25, 2025
"""

from typing import Dict, List, Optional, Any, Union

# Version information
__version__ = "0.1.0"
__author__ = "Manus AI"
__email__ = "info@industriverse.ai"
__status__ = "Development"

# Package metadata
PACKAGE_METADATA = {
    "name": "integration",
    "version": __version__,
    "description": "Integration package for the Overseer System",
    "author": __author__,
    "email": __email__,
    "status": __status__,
    "dependencies": [
        "mcp_integration",
        "a2a_integration",
        "event_bus",
        "data_access",
        "config",
        "auth"
    ]
}

# Week 18-19: Export unified architecture components
from .integration_orchestrator import (
    IntegrationOrchestrator,
    get_integration_orchestrator
)

from .ar_vr_integration_adapter import (
    ARVRIntegrationAdapter,
    get_ar_vr_integration_adapter
)

# Export public API
__all__ = [
    "PACKAGE_METADATA",
    "integration_manager",
    "base_integration_adapter",
    "protocol_bridge",
    # Week 18-19 additions
    "IntegrationOrchestrator",
    "get_integration_orchestrator",
    "ARVRIntegrationAdapter",
    "get_ar_vr_integration_adapter"
]
