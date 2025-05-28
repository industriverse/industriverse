"""
A2A Integration Module

This module serves as the entry point for the A2A Integration package.
It imports and exposes the main components of the A2A protocol integration.
"""

from .a2a_integration_manager import A2AIntegrationManager
from .a2a_agent_schema import A2AAgentSchema
from .a2a_protocol_bridge import A2AProtocolBridge

__all__ = [
    'A2AIntegrationManager',
    'A2AAgentSchema',
    'A2AProtocolBridge'
]
