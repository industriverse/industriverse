"""
Unit tests for Deploy Anywhere Integration

Tests cover:
1. Integration initialization and configuration
2. Service initialization and registration
3. Service selection logic
4. Capsule deployment to each cloud
5. Deployment health checking
6. Deployment rollback
7. Deployment listing and filtering
8. Statistics and monitoring

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio

from ..deploy_anywhere_integration import (
    DeployAnywhereIntegration,
    DeployAnywhereIntegrationConfig,
    DeployAnywhereService,
    DACDeployment,
    DeploymentStatus,
    ServiceType
)
from ..k8s_client_manager import K8sClientManager, CloudProvider


class TestDeployAnywhereIntegration:
    """Test suite for Deploy Anywhere Integration."""
    
    def test_integration_initialization(self):
        """Test integration initialization with default config."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        assert integration.config is not None
        assert len(integration.services) == 7  # 4 Azure + 1 AWS + 2 GCP
        assert len(integration.deployments) == 0
    
    def test_integration_initialization_custom_config(self):
        """Test integration initialization with custom config."""
        k8s_manager = K8sClientManager()
        config = DeployAnywhereIntegrationConfig(
            deployment_timeout=1200,
            retry_attempts=5
        )
        
        integration = DeployAnywhereIntegration(k8s_manager, config=config)
        
        assert integration.config.deployment_timeout == 1200
        assert integration.config.retry_attempts == 5
    
    def test_azure_services_initialized(self):
        """Test that Azure services are initialized."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        assert "a2a-deploy-anywhere" in integration.services
        assert "azure-deploy-anywhere" in integration.services
        assert "obmi-enterprise" in integration.services
        assert "enterprise-client-portal" in integration.services
    
    def test_aws_services_initialized(self):
        """Test that AWS services are initialized."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        assert "ai-ripple-deploy-anywhere" in integration.services
    
    def test_gcp_services_initialized(self):
        """Test that GCP services are initialized."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        assert "bitnet-protocol" in integration.services
        assert "edge-device-registry" in integration.services
    
    def test_azure_service_config(self):
        """Test Azure service configuration."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        service = integration.get_service("obmi-enterprise")
        
        assert service is not None
        assert service.provider == CloudProvider.AZURE
        assert service.service_type == ServiceType.OBMI
        assert service.namespace == "industriverse"
    
    def test_aws_service_config(self):
        """Test AWS service configuration."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        service = integration.get_service("ai-ripple-deploy-anywhere")
        
        assert service is not None
        assert service.provider == CloudProvider.AWS
        assert service.service_type == ServiceType.RIPPLE
        assert service.namespace == "molecular"
    
    def test_gcp_service_config(self):
        """Test GCP service configuration."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        service = integration.get_service("bitnet-protocol")
        
        assert service is not None
        assert service.provider == CloudProvider.GCP
        assert service.service_type == ServiceType.BITNET
        assert service.namespace == "industriverse"
    
    def test_select_service_azure(self):
        """Test service selection for Azure."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        service = integration._select_service(CloudProvider.AZURE)
        
        assert service is not None
        # Should prefer OBMI Enterprise
        assert service.service_type == ServiceType.OBMI
        assert service.name == "obmi-enterprise"
    
    def test_select_service_aws(self):
        """Test service selection for AWS."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        service = integration._select_service(CloudProvider.AWS)
        
        assert service is not None
        assert service.service_type == ServiceType.RIPPLE
        assert service.name == "ai-ripple-deploy-anywhere"
    
    def test_select_service_gcp(self):
        """Test service selection for GCP."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        service = integration._select_service(CloudProvider.GCP)
        
        assert service is not None
        # Should prefer BitNet Protocol
        assert service.service_type == ServiceType.BITNET
        assert service.name == "bitnet-protocol"
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_to_azure(self):
        """Test deploying capsule to Azure."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {
            "name": "test-capsule",
            "image": "industriverse/test:latest",
            "replicas": 3
        }
        
        deployment = await integration.deploy_capsule(
            "test-capsule",
            CloudProvider.AZURE,
            manifest
        )
        
        assert isinstance(deployment, DACDeployment)
        assert deployment.capsule_name == "test-capsule"
        assert deployment.provider == CloudProvider.AZURE
        assert deployment.status == DeploymentStatus.DEPLOYED
        assert deployment.target_service == "obmi-enterprise"
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_to_aws(self):
        """Test deploying capsule to AWS."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {
            "name": "test-capsule",
            "image": "industriverse/test:latest",
            "replicas": 3
        }
        
        deployment = await integration.deploy_capsule(
            "test-capsule",
            CloudProvider.AWS,
            manifest
        )
        
        assert deployment.provider == CloudProvider.AWS
        assert deployment.status == DeploymentStatus.DEPLOYED
        assert deployment.target_service == "ai-ripple-deploy-anywhere"
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_to_gcp(self):
        """Test deploying capsule to GCP."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {
            "name": "test-capsule",
            "image": "industriverse/test:latest",
            "replicas": 3
        }
        
        deployment = await integration.deploy_capsule(
            "test-capsule",
            CloudProvider.GCP,
            manifest
        )
        
        assert deployment.provider == CloudProvider.GCP
        assert deployment.status == DeploymentStatus.DEPLOYED
        assert deployment.target_service == "bitnet-protocol"
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_with_metadata(self):
        """Test deploying capsule with metadata."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        metadata = {"version": "1.0.0", "environment": "production"}
        
        deployment = await integration.deploy_capsule(
            "test-capsule",
            CloudProvider.AZURE,
            manifest,
            metadata=metadata
        )
        
        assert deployment.metadata["version"] == "1.0.0"
        assert deployment.metadata["environment"] == "production"
    
    @pytest.mark.asyncio
    async def test_deployment_storage(self):
        """Test that deployments are stored."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        
        deployment = await integration.deploy_capsule(
            "test-capsule",
            CloudProvider.AZURE,
            manifest
        )
        
        assert deployment.deployment_id in integration.deployments
    
    @pytest.mark.asyncio
    async def test_check_deployment_health(self):
        """Test checking deployment health."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        
        deployment = await integration.deploy_capsule(
            "test-capsule",
            CloudProvider.AZURE,
            manifest
        )
        
        health = await integration.check_deployment_health(deployment.deployment_id)
        
        assert health == "healthy"
        assert deployment.health_status == "healthy"
    
    @pytest.mark.asyncio
    async def test_check_deployment_health_not_found(self):
        """Test checking health of non-existent deployment."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        with pytest.raises(ValueError):
            await integration.check_deployment_health("nonexistent")
    
    @pytest.mark.asyncio
    async def test_rollback_deployment(self):
        """Test rolling back a deployment."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        
        deployment = await integration.deploy_capsule(
            "test-capsule",
            CloudProvider.AZURE,
            manifest
        )
        
        success = await integration.rollback_deployment(deployment.deployment_id)
        
        assert success
        assert deployment.status == DeploymentStatus.ROLLED_BACK
    
    @pytest.mark.asyncio
    async def test_rollback_deployment_not_found(self):
        """Test rolling back non-existent deployment."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        with pytest.raises(ValueError):
            await integration.rollback_deployment("nonexistent")
    
    @pytest.mark.asyncio
    async def test_get_deployment(self):
        """Test getting deployment by ID."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        
        deployment = await integration.deploy_capsule(
            "test-capsule",
            CloudProvider.AZURE,
            manifest
        )
        
        retrieved = integration.get_deployment(deployment.deployment_id)
        
        assert retrieved is not None
        assert retrieved.deployment_id == deployment.deployment_id
    
    @pytest.mark.asyncio
    async def test_get_deployment_not_found(self):
        """Test getting non-existent deployment."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        retrieved = integration.get_deployment("nonexistent")
        
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_list_deployments_all(self):
        """Test listing all deployments."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        
        await integration.deploy_capsule("capsule1", CloudProvider.AZURE, manifest)
        await integration.deploy_capsule("capsule2", CloudProvider.AWS, manifest)
        await integration.deploy_capsule("capsule3", CloudProvider.GCP, manifest)
        
        deployments = integration.list_deployments()
        
        assert len(deployments) == 3
    
    @pytest.mark.asyncio
    async def test_list_deployments_by_provider(self):
        """Test listing deployments filtered by provider."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        
        await integration.deploy_capsule("capsule1", CloudProvider.AZURE, manifest)
        await integration.deploy_capsule("capsule2", CloudProvider.AZURE, manifest)
        await integration.deploy_capsule("capsule3", CloudProvider.AWS, manifest)
        
        azure_deployments = integration.list_deployments(provider=CloudProvider.AZURE)
        
        assert len(azure_deployments) == 2
        assert all(d.provider == CloudProvider.AZURE for d in azure_deployments)
    
    @pytest.mark.asyncio
    async def test_list_deployments_by_status(self):
        """Test listing deployments filtered by status."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        
        deployment1 = await integration.deploy_capsule("capsule1", CloudProvider.AZURE, manifest)
        deployment2 = await integration.deploy_capsule("capsule2", CloudProvider.AWS, manifest)
        
        # Rollback one deployment
        await integration.rollback_deployment(deployment1.deployment_id)
        
        deployed = integration.list_deployments(status=DeploymentStatus.DEPLOYED)
        rolled_back = integration.list_deployments(status=DeploymentStatus.ROLLED_BACK)
        
        assert len(deployed) == 1
        assert len(rolled_back) == 1
    
    def test_get_service(self):
        """Test getting service by name."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        service = integration.get_service("obmi-enterprise")
        
        assert service is not None
        assert service.name == "obmi-enterprise"
    
    def test_get_service_not_found(self):
        """Test getting non-existent service."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        service = integration.get_service("nonexistent")
        
        assert service is None
    
    def test_list_services_all(self):
        """Test listing all services."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        services = integration.list_services()
        
        assert len(services) == 7
    
    def test_list_services_by_provider_azure(self):
        """Test listing Azure services."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        services = integration.list_services(provider=CloudProvider.AZURE)
        
        assert len(services) == 4
        assert all(s.provider == CloudProvider.AZURE for s in services)
    
    def test_list_services_by_provider_aws(self):
        """Test listing AWS services."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        services = integration.list_services(provider=CloudProvider.AWS)
        
        assert len(services) == 1
        assert all(s.provider == CloudProvider.AWS for s in services)
    
    def test_list_services_by_provider_gcp(self):
        """Test listing GCP services."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        services = integration.list_services(provider=CloudProvider.GCP)
        
        assert len(services) == 2
        assert all(s.provider == CloudProvider.GCP for s in services)
    
    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """Test getting integration statistics."""
        k8s_manager = K8sClientManager()
        integration = DeployAnywhereIntegration(k8s_manager)
        
        manifest = {"name": "test-capsule"}
        
        await integration.deploy_capsule("capsule1", CloudProvider.AZURE, manifest)
        await integration.deploy_capsule("capsule2", CloudProvider.AWS, manifest)
        await integration.deploy_capsule("capsule3", CloudProvider.GCP, manifest)
        
        stats = integration.get_statistics()
        
        assert stats["total_services"] == 7
        assert stats["total_deployments"] == 3
        assert stats["by_provider"]["azure"] == 4
        assert stats["by_provider"]["aws"] == 1
        assert stats["by_provider"]["gcp"] == 2
        assert stats["success_rate"] == 100.0


class TestDACDeploymentDataclass:
    """Test suite for DACDeployment dataclass."""
    
    def test_deployment_to_dict(self):
        """Test deployment serialization."""
        deployment = DACDeployment(
            deployment_id="test-id",
            capsule_name="test-capsule",
            target_service="obmi-enterprise",
            provider=CloudProvider.AZURE,
            status=DeploymentStatus.DEPLOYED,
            manifest={"name": "test"},
            health_status="healthy"
        )
        
        deployment_dict = deployment.to_dict()
        
        assert isinstance(deployment_dict, dict)
        assert deployment_dict["deployment_id"] == "test-id"
        assert deployment_dict["provider"] == "azure"
        assert deployment_dict["status"] == "deployed"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
