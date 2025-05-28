"""
Config Service package initialization.

This package provides centralized configuration management for the Overseer System,
handling environment-specific settings, dynamic configuration updates, and configuration versioning.
"""

from .config_service import app

__all__ = [
    'app'
]
