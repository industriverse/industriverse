"""
Cloud Provider Integration Manager

This module provides a unified interface for managing cloud provider integrations
in the Deployment Operations Layer. It handles provider registration, selection,
and cross-provider operations.

Classes:
    CloudProviderIntegrationManager: Manages cloud provider integrations
"""

import logging
from typing import Dict, List, Any, Optional

from ..agent.agent_utils import AgentResponse
from .aws_provider import AWSProviderAdapter
from .gcp_provider import GCPProviderAdapter
from .azure_provider import AzureProviderAdapter
from ..protocol.mcp_integration.mcp_context_schema import MCPContext

logger = logging.getLogger(__name__)

class CloudProviderIntegrationManager:
    """
    Manages cloud provider integrations for the Deployment Operations Layer.
    
    This class provides a unified interface for interacting with multiple cloud providers,
    handling provider registration, selection, and cross-provider operations.
    """
    
    def __init__(self):
        """
        Initialize the Cloud Provider Integration Manager.
        """
        self.providers = {}
        self.default_provider = None
    
    def register_aws_provider(self, provider_id: str, region: str, 
                             profile: Optional[str] = None, 
                             is_default: bool = False) -> bool:
        """
        Register an AWS provider.
        
        Args:
            provider_id: Unique identifier for the provider
            region: AWS region
            profile: AWS profile name (optional)
            is_default: Whether this provider should be the default
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            provider = AWSProviderAdapter(region=region, profile=profile)
            
            # Validate credentials
            if not provider.validate_credentials():
                logger.error(f"Failed to validate AWS credentials for provider {provider_id}")
                return False
            
            self.providers[provider_id] = provider
            
            if is_default or not self.default_provider:
                self.default_provider = provider_id
                
            return True
        
        except Exception as e:
            logger.error(f"Failed to register AWS provider {provider_id}: {str(e)}")
            return False
    
    def register_gcp_provider(self, provider_id: str, project_id: str, 
                             credentials_path: Optional[str] = None,
                             is_default: bool = False) -> bool:
        """
        Register a GCP provider.
        
        Args:
            provider_id: Unique identifier for the provider
            project_id: GCP project ID
            credentials_path: Path to service account credentials JSON file (optional)
            is_default: Whether this provider should be the default
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            provider = GCPProviderAdapter(project_id=project_id, credentials_path=credentials_path)
            
            # Validate credentials
            if not provider.validate_credentials():
                logger.error(f"Failed to validate GCP credentials for provider {provider_id}")
                return False
            
            self.providers[provider_id] = provider
            
            if is_default or not self.default_provider:
                self.default_provider = provider_id
                
            return True
        
        except Exception as e:
            logger.error(f"Failed to register GCP provider {provider_id}: {str(e)}")
            return False
    
    def register_azure_provider(self, provider_id: str, subscription_id: str, 
                               tenant_id: Optional[str] = None, 
                               client_id: Optional[str] = None, 
                               client_secret: Optional[str] = None,
                               is_default: bool = False) -> bool:
        """
        Register an Azure provider.
        
        Args:
            provider_id: Unique identifier for the provider
            subscription_id: Azure subscription ID
            tenant_id: Azure tenant ID (optional for DefaultAzureCredential)
            client_id: Azure client ID (optional for DefaultAzureCredential)
            client_secret: Azure client secret (optional for DefaultAzureCredential)
            is_default: Whether this provider should be the default
            
        Returns:
            bool: True if registration was successful, False otherwise
        """
        try:
            provider = AzureProviderAdapter(
                subscription_id=subscription_id,
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            
            # Validate credentials
            if not provider.validate_credentials():
                logger.error(f"Failed to validate Azure credentials for provider {provider_id}")
                return False
            
            self.providers[provider_id] = provider
            
            if is_default or not self.default_provider:
                self.default_provider = provider_id
                
            return True
        
        except Exception as e:
            logger.error(f"Failed to register Azure provider {provider_id}: {str(e)}")
            return False
    
    def get_provider(self, provider_id: Optional[str] = None):
        """
        Get a registered provider.
        
        Args:
            provider_id: Provider identifier (optional, uses default if not specified)
            
        Returns:
            Provider adapter or None if not found
        """
        if not provider_id:
            if not self.default_provider:
                logger.error("No default provider set")
                return None
            provider_id = self.default_provider
            
        if provider_id not in self.providers:
            logger.error(f"Provider {provider_id} not found")
            return None
            
        return self.providers[provider_id]
    
    def list_providers(self) -> List[Dict[str, Any]]:
        """
        List all registered providers.
        
        Returns:
            List[Dict[str, Any]]: List of provider details
        """
        return [
            {
                "id": provider_id,
                "type": self._get_provider_type(provider),
                "is_default": provider_id == self.default_provider
            }
            for provider_id, provider in self.providers.items()
        ]
    
    def _get_provider_type(self, provider) -> str:
        """
        Get the type of a provider.
        
        Args:
            provider: Provider adapter
            
        Returns:
            str: Provider type ("aws", "gcp", "azure")
        """
        if isinstance(provider, AWSProviderAdapter):
            return "aws"
        elif isinstance(provider, GCPProviderAdapter):
            return "gcp"
        elif isinstance(provider, AzureProviderAdapter):
            return "azure"
        else:
            return "unknown"
    
    def set_default_provider(self, provider_id: str) -> bool:
        """
        Set the default provider.
        
        Args:
            provider_id: Provider identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        if provider_id not in self.providers:
            logger.error(f"Provider {provider_id} not found")
            return False
            
        self.default_provider = provider_id
        return True
    
    def unregister_provider(self, provider_id: str) -> bool:
        """
        Unregister a provider.
        
        Args:
            provider_id: Provider identifier
            
        Returns:
            bool: True if successful, False otherwise
        """
        if provider_id not in self.providers:
            logger.error(f"Provider {provider_id} not found")
            return False
            
        del self.providers[provider_id]
        
        if self.default_provider == provider_id:
            self.default_provider = next(iter(self.providers)) if self.providers else None
            
        return True
    
    def provision_resources(self, provider_id: Optional[str], resource_specs: Dict[str, Any]) -> AgentResponse:
        """
        Provision resources using a provider.
        
        Args:
            provider_id: Provider identifier (optional, uses default if not specified)
            resource_specs: Resource specifications
            
        Returns:
            AgentResponse: Provisioning response
        """
        provider = self.get_provider(provider_id)
        
        if not provider:
            return AgentResponse(
                success=False,
                message=f"Provider not found",
                data={}
            )
            
        try:
            resources = provider.resource_manager.provision_resources(resource_specs)
            
            if "error" in resources:
                return AgentResponse(
                    success=False,
                    message=f"Failed to provision resources: {resources['error']}",
                    data=resources
                )
                
            return AgentResponse(
                success=True,
                message=f"Successfully provisioned resources",
                data=resources
            )
        
        except Exception as e:
            logger.error(f"Failed to provision resources: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to provision resources: {str(e)}",
                data={}
            )
    
    def cleanup_resources(self, provider_id: Optional[str], resources: Dict[str, Any]) -> AgentResponse:
        """
        Clean up resources using a provider.
        
        Args:
            provider_id: Provider identifier (optional, uses default if not specified)
            resources: Resource details to clean up
            
        Returns:
            AgentResponse: Cleanup response
        """
        provider = self.get_provider(provider_id)
        
        if not provider:
            return AgentResponse(
                success=False,
                message=f"Provider not found",
                data={}
            )
            
        try:
            results = provider.resource_manager.cleanup_resources(resources)
            
            return AgentResponse(
                success=True,
                message=f"Resource cleanup completed",
                data=results
            )
        
        except Exception as e:
            logger.error(f"Failed to clean up resources: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to clean up resources: {str(e)}",
                data={}
            )
    
    def deploy_application(self, provider_id: Optional[str], deployment_spec: Dict[str, Any]) -> AgentResponse:
        """
        Deploy an application using a provider.
        
        Args:
            provider_id: Provider identifier (optional, uses default if not specified)
            deployment_spec: Deployment specifications
            
        Returns:
            AgentResponse: Deployment response
        """
        provider = self.get_provider(provider_id)
        
        if not provider:
            return AgentResponse(
                success=False,
                message=f"Provider not found",
                data={}
            )
            
        try:
            return provider.deployment_handler.deploy_application(deployment_spec)
        
        except Exception as e:
            logger.error(f"Failed to deploy application: {str(e)}")
            return AgentResponse(
                success=False,
                message=f"Failed to deploy application: {str(e)}",
                data={}
            )
    
    def create_deployment_context(self, provider_id: Optional[str], mission_id: str) -> Dict[str, Any]:
        """
        Create a deployment context for a mission.
        
        Args:
            provider_id: Provider identifier (optional, uses default if not specified)
            mission_id: Unique identifier for the mission
            
        Returns:
            Dict[str, Any]: Deployment context
        """
        provider = self.get_provider(provider_id)
        
        if not provider:
            logger.error(f"Provider not found")
            return {}
            
        return provider.create_deployment_context(mission_id)
    
    def to_mcp_context(self, provider_id: Optional[str] = None) -> MCPContext:
        """
        Convert provider information to MCP context.
        
        Args:
            provider_id: Provider identifier (optional, uses default if not specified)
            
        Returns:
            MCPContext: MCP context with provider information
        """
        provider = self.get_provider(provider_id)
        
        if not provider:
            logger.error(f"Provider not found")
            return MCPContext(
                context_type="cloud_provider",
                provider="unknown"
            )
            
        return provider.to_mcp_context()
    
    def multi_cloud_deployment(self, deployment_specs: Dict[str, Dict[str, Any]]) -> Dict[str, AgentResponse]:
        """
        Perform a multi-cloud deployment.
        
        Args:
            deployment_specs: Dictionary mapping provider IDs to deployment specifications
            
        Returns:
            Dict[str, AgentResponse]: Dictionary mapping provider IDs to deployment responses
        """
        results = {}
        
        for provider_id, deployment_spec in deployment_specs.items():
            results[provider_id] = self.deploy_application(provider_id, deployment_spec)
            
        return results
    
    def multi_cloud_resource_provision(self, resource_specs: Dict[str, Dict[str, Any]]) -> Dict[str, AgentResponse]:
        """
        Perform multi-cloud resource provisioning.
        
        Args:
            resource_specs: Dictionary mapping provider IDs to resource specifications
            
        Returns:
            Dict[str, AgentResponse]: Dictionary mapping provider IDs to provisioning responses
        """
        results = {}
        
        for provider_id, spec in resource_specs.items():
            results[provider_id] = self.provision_resources(provider_id, spec)
            
        return results
    
    def multi_cloud_resource_cleanup(self, resources: Dict[str, Dict[str, Any]]) -> Dict[str, AgentResponse]:
        """
        Perform multi-cloud resource cleanup.
        
        Args:
            resources: Dictionary mapping provider IDs to resource details
            
        Returns:
            Dict[str, AgentResponse]: Dictionary mapping provider IDs to cleanup responses
        """
        results = {}
        
        for provider_id, resource_details in resources.items():
            results[provider_id] = self.cleanup_resources(provider_id, resource_details)
            
        return results
