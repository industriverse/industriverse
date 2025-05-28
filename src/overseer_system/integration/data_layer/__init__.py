"""
Data Layer Integration Package initialization.

This module initializes the Data Layer integration package for the Overseer System,
which provides integration with the Data Layer components of the Industriverse.

Author: Manus AI
Date: May 25, 2025
"""

# Version information
__version__ = "0.1.0"
__author__ = "Manus AI"
__email__ = "info@industriverse.ai"
__status__ = "Development"

# Package metadata
PACKAGE_METADATA = {
    "name": "data_layer",
    "version": __version__,
    "description": "Data Layer integration package for the Overseer System",
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

# Export public API
__all__ = [
    "PACKAGE_METADATA",
    "data_ingestion_adapter",
    "data_processing_adapter",
    "data_storage_adapter",
    "data_schema_adapter"
]
