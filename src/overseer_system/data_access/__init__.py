"""
Data Access Service package initialization.

This package provides a database abstraction layer for the Overseer System,
handling CRUD operations, data validation, and ensuring data integrity.
"""

from .data_access_service import app

__all__ = [
    'app'
]
