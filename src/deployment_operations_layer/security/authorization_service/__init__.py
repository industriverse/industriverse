"""
Authorization Service Module

This module provides components for authorizing users and managing access control
for the Deployment Operations Layer. It serves as a critical security component that ensures
only authorized users and systems can access resources and perform actions they are authorized for.
"""

from .authorization_service import AuthorizationService
from .authorization_service_api import app as authorization_service_api

__all__ = [
    'AuthorizationService',
    'authorization_service_api'
]
