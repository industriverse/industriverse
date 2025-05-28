"""
Calico Integration Module

This module provides integration with Calico for the Deployment Operations Layer.
It handles deployment, configuration, and management of Calico resources
including network policies, BGP configuration, and IPAM capabilities.
"""

from .calico_integration_manager import CalicoIntegrationManager
from .calico_integration_manager import NetworkPolicyManager
from .calico_integration_manager import BGPConfigurationManager
from .calico_integration_manager import IPAMManager
from .calico_integration_manager import CalicoExecutor

__all__ = [
    'CalicoIntegrationManager',
    'NetworkPolicyManager',
    'BGPConfigurationManager',
    'IPAMManager',
    'CalicoExecutor'
]
