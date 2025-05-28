"""
MCP Integration package initialization.

This package provides integration with the Model Context Protocol (MCP),
enabling context-aware communication between Overseer System components
and other layers of the Industriverse ecosystem.
"""

from .mcp_integration_manager import MCPIntegrationManager
from .mcp_context_schema import MCPContextType
from .mcp_protocol_bridge import MCPProtocolBridge, MCPContext

__all__ = [
    'MCPIntegrationManager',
    'MCPContextType',
    'MCPProtocolBridge',
    'MCPContext'
]
