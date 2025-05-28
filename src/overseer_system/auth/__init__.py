"""
Auth Service package initialization.

This package provides authentication and authorization services for the Overseer System,
handling user authentication, role-based access control, and token management.
"""

from .auth_service import app

__all__ = [
    'app'
]
