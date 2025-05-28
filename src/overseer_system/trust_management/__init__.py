"""
Trust Management package initialization.

This package provides trust management capabilities for the Overseer System,
including trust verification, reputation management, trust policy enforcement,
and trust relationship tracking.

Author: Manus AI
Date: May 25, 2025
"""

from .trust_management_service import app as trust_management_app

__all__ = ['trust_management_app']
