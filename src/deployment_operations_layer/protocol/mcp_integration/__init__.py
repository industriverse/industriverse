"""
MCP Integration Module

This module serves as the entry point for the MCP Integration package.
It imports and exposes the main components of the MCP protocol integration.
"""

from .mcp_integration_manager import MCPIntegrationManager
from .mcp_context_schema import MCPContextSchema
from .mcp_protocol_bridge import MCPProtocolBridge

__all__ = [
    'MCPIntegrationManager',
    'MCPContextSchema',
    'MCPProtocolBridge'
]
