"""
A2A Integration package initialization.

This package provides integration with the Agent-to-Agent (A2A) Protocol,
enabling agent-based communication between Overseer System components
and external agent ecosystems.
"""

from .a2a_integration_manager import A2AIntegrationManager
from .a2a_agent_schema import A2ATaskType, A2ACapabilityType, A2AIndustryTag
from .a2a_protocol_bridge import A2AProtocolBridge, A2AAgentCard, A2ATask, A2ATaskResult, A2ABid

__all__ = [
    'A2AIntegrationManager',
    'A2ATaskType',
    'A2ACapabilityType',
    'A2AIndustryTag',
    'A2AProtocolBridge',
    'A2AAgentCard',
    'A2ATask',
    'A2ATaskResult',
    'A2ABid'
]
