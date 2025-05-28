"""
API Gateway package initialization.

This package provides a unified entry point for all Overseer System components,
handling routing, authentication, rate limiting, and request/response transformation.
"""

from .api_gateway_service import app

__all__ = [
    'app'
]
