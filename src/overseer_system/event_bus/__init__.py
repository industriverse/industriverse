"""
Event Bus package initialization.

This package provides event bus integration for the Overseer System,
enabling asynchronous communication between components.
"""

from .kafka_client import KafkaClientWrapper

__all__ = [
    'KafkaClientWrapper'
]
