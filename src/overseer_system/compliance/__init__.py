"""
Compliance package initialization.

This package provides compliance monitoring, validation, and reporting capabilities for the Overseer System.
"""

from .compliance_service import app as compliance_app

__all__ = ['compliance_app']
