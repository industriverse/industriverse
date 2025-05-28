"""
Authentication Service Module

This module provides components for authenticating users and managing access control
for the Deployment Operations Layer. It serves as a critical security component that ensures
only authorized users and systems can access and manage deployment operations.
"""

from .authentication_service import AuthenticationService
from .authentication_service_api import app as authentication_service_api

__all__ = [
    'AuthenticationService',
    'authentication_service_api'
]
