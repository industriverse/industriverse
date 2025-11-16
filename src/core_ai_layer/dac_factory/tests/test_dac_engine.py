"""
Unit tests for DAC Runtime Engine

Tests cover:
1. Engine initialization and configuration
2. Kubernetes client management
3. DAC manifest validation
4. Capsule deployment orchestration
5. Capsule lifecycle operations (scale, stop)
6. Multi-cloud deployment
7. Status tracking and monitoring
8. Error handling

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio
from datetime import datetime

from ..dac_engine import (
    DACEngine,
    DACEngineConfig,
    DACManifest,
    DeploymentInfo,
    CloudProvider,
    DeploymentStatus,
    KubernetesClient
)


class TestDACManifest:
    """Test suite for DAC manifest."""
    
    def test_manifest_creation(self):
        """Test manifest creation with required fields."""
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test capsule",
            image="test:1.0.0"
        )
        
        assert manifest.name == "test-capsule"
        assert manifest.version == "1.0.0"
        assert manifest.description == "Test capsule"
        assert manifest.image == "test:1.0.0"
        assert manifest.replicas == 1
    
    def test_manifest_with_resources(self):
        """Test manifest with resource specifications."""
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test capsule",
            image="test:1.0.0",
            resources={
                "requests": {"cpu": "100m", "memory": "128Mi"},
                "limits": {"cpu": "500m", "memory": "512Mi"}
            }
        )
        
        assert "requests" in manifest.resources
        assert "limits" in manifest.resources
    
    def test_manifest_to_dict(self):
        """Test manifest serialization to dictionary."""
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test capsule",
            image="test:1.0.0",
            replicas=3
        )
        
        manifest_dict = manifest.to_dict()
        
        assert isinstance(manifest_dict, dict)
        assert manifest_dict["name"] == "test-capsule"
        assert manifest_dict["version"] == "1.0.0"
        assert manifest_dict["replicas"] == 3
    
    def test_manifest_from_dict(self):
        """Test manifest deserialization from dictionary."""
        data = {
            "name": "test-capsule",
            "version": "1.0.0",
            "description": "Test capsule",
            "image": "test:1.0.0",
            "replicas": 2
        }
        
        manifest = DACManifest.from_dict(data)
        
        assert manifest.name == "test-capsule"
        assert manifest.version == "1.0.0"
        assert manifest.replicas == 2


class TestKubernetesClient:
    """Test suite for Kubernetes client."""
    
    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test Kubernetes client initialization."""
        client = KubernetesClient(context="test-context")
        
        assert client.context == "test-context"
        assert not client.connected
    
    @pytest.mark.asyncio
    async def test_client_connection(self):
        """Test Kubernetes client connection."""
        client = KubernetesClient(context="test-context")
        
        success = await client.connect()
        
        assert success
        assert client.connected
    
    @pytest.mark.asyncio
    async def test_create_deployment(self):
        """Test deployment creation."""
        client = KubernetesClient(context="test-context")
        await client.connect()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        deployment = await client.create_deployment(
            name="test-capsule",
            namespace="default",
            manifest=manifest
        )
        
        assert deployment["name"] == "test-capsule"
        assert deployment["namespace"] == "default"
        assert "created_at" in deployment
    
    @pytest.mark.asyncio
    async def test_get_deployment_status(self):
        """Test getting deployment status."""
        client = KubernetesClient(context="test-context")
        await client.connect()
        
        status = await client.get_deployment_status(
            name="test-capsule",
            namespace="default"
        )
        
        assert status["name"] == "test-capsule"
        assert "status" in status
    
    @pytest.mark.asyncio
    async def test_scale_deployment(self):
        """Test deployment scaling."""
        client = KubernetesClient(context="test-context")
        await client.connect()
        
        success = await client.scale_deployment(
            name="test-capsule",
            namespace="default",
            replicas=3
        )
        
        assert success
    
    @pytest.mark.asyncio
    async def test_delete_deployment(self):
        """Test deployment deletion."""
        client = KubernetesClient(context="test-context")
        await client.connect()
        
        success = await client.delete_deployment(
            name="test-capsule",
            namespace="default"
        )
        
        assert success
    
    @pytest.mark.asyncio
    async def test_create_service(self):
        """Test service creation."""
        client = KubernetesClient(context="test-context")
        await client.connect()
        
        service = await client.create_service(
            name="test-service",
            namespace="default",
            ports=[8080, 9090]
        )
        
        assert service["name"] == "test-service"
        assert len(service["ports"]) == 2
        assert len(service["endpoints"]) == 2
    
    @pytest.mark.asyncio
    async def test_operations_without_connection(self):
        """Test that operations fail without connection."""
        client = KubernetesClient(context="test-context")
        
        manifest = DACManifest(
            name="test",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        with pytest.raises(RuntimeError):
            await client.create_deployment("test", "default", manifest)


class TestDACEngine:
    """Test suite for DAC Runtime Engine."""
    
    def test_engine_initialization(self):
        """Test engine initialization with default config."""
        engine = DACEngine()
        
        assert engine.config is not None
        assert len(engine.clients) == 3
        assert CloudProvider.AZURE in engine.clients
        assert CloudProvider.AWS in engine.clients
        assert CloudProvider.GCP in engine.clients
    
    def test_engine_initialization_custom_config(self):
        """Test engine initialization with custom config."""
        config = DACEngineConfig(
            default_namespace="custom-namespace",
            deployment_timeout=600
        )
        
        engine = DACEngine(config=config)
        
        assert engine.config.default_namespace == "custom-namespace"
        assert engine.config.deployment_timeout == 600
    
    @pytest.mark.asyncio
    async def test_connect_all_clouds(self):
        """Test connecting to all cloud providers."""
        engine = DACEngine()
        
        results = await engine.connect_all()
        
        assert len(results) == 3
        assert all(results.values())
    
    def test_validate_manifest_valid(self):
        """Test manifest validation with valid manifest."""
        engine = DACEngine()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test",
            image="test:1.0.0",
            replicas=2
        )
        
        is_valid, error = engine.validate_manifest(manifest)
        
        assert is_valid
        assert error is None
    
    def test_validate_manifest_missing_name(self):
        """Test manifest validation with missing name."""
        engine = DACEngine()
        
        manifest = DACManifest(
            name="",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        is_valid, error = engine.validate_manifest(manifest)
        
        assert not is_valid
        assert "name" in error.lower()
    
    def test_validate_manifest_missing_version(self):
        """Test manifest validation with missing version."""
        engine = DACEngine()
        
        manifest = DACManifest(
            name="test",
            version="",
            description="Test",
            image="test:1.0.0"
        )
        
        is_valid, error = engine.validate_manifest(manifest)
        
        assert not is_valid
        assert "version" in error.lower()
    
    def test_validate_manifest_missing_image(self):
        """Test manifest validation with missing image."""
        engine = DACEngine()
        
        manifest = DACManifest(
            name="test",
            version="1.0.0",
            description="Test",
            image=""
        )
        
        is_valid, error = engine.validate_manifest(manifest)
        
        assert not is_valid
        assert "image" in error.lower()
    
    def test_validate_manifest_invalid_replicas(self):
        """Test manifest validation with invalid replicas."""
        engine = DACEngine()
        
        manifest = DACManifest(
            name="test",
            version="1.0.0",
            description="Test",
            image="test:1.0.0",
            replicas=0
        )
        
        is_valid, error = engine.validate_manifest(manifest)
        
        assert not is_valid
        assert "replicas" in error.lower()
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_azure(self):
        """Test capsule deployment to Azure."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test capsule",
            image="test:1.0.0",
            replicas=2,
            ports=[8080]
        )
        
        deployment = await engine.deploy_capsule(
            manifest=manifest,
            cloud_provider=CloudProvider.AZURE
        )
        
        assert deployment.capsule_id is not None
        assert deployment.cloud_provider == CloudProvider.AZURE
        assert deployment.status == DeploymentStatus.RUNNING
        assert len(deployment.endpoints) > 0
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_aws(self):
        """Test capsule deployment to AWS."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test capsule",
            image="test:1.0.0"
        )
        
        deployment = await engine.deploy_capsule(
            manifest=manifest,
            cloud_provider=CloudProvider.AWS
        )
        
        assert deployment.cloud_provider == CloudProvider.AWS
        assert deployment.status == DeploymentStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_gcp(self):
        """Test capsule deployment to GCP."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test capsule",
            image="test:1.0.0"
        )
        
        deployment = await engine.deploy_capsule(
            manifest=manifest,
            cloud_provider=CloudProvider.GCP
        )
        
        assert deployment.cloud_provider == CloudProvider.GCP
        assert deployment.status == DeploymentStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_custom_namespace(self):
        """Test capsule deployment with custom namespace."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        deployment = await engine.deploy_capsule(
            manifest=manifest,
            cloud_provider=CloudProvider.AZURE,
            namespace="custom-namespace"
        )
        
        assert deployment.namespace == "custom-namespace"
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_invalid_manifest(self):
        """Test capsule deployment with invalid manifest."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        with pytest.raises(ValueError):
            await engine.deploy_capsule(
                manifest=manifest,
                cloud_provider=CloudProvider.AZURE
            )
    
    @pytest.mark.asyncio
    async def test_get_capsule_status(self):
        """Test getting capsule status."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        deployment = await engine.deploy_capsule(
            manifest=manifest,
            cloud_provider=CloudProvider.AZURE
        )
        
        status = await engine.get_capsule_status(deployment.capsule_id)
        
        assert status is not None
        assert status.capsule_id == deployment.capsule_id
        assert status.status == DeploymentStatus.RUNNING
    
    @pytest.mark.asyncio
    async def test_get_capsule_status_not_found(self):
        """Test getting status for non-existent capsule."""
        engine = DACEngine()
        
        status = await engine.get_capsule_status("non-existent-id")
        
        assert status is None
    
    @pytest.mark.asyncio
    async def test_scale_capsule(self):
        """Test scaling capsule replicas."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test",
            image="test:1.0.0",
            replicas=1
        )
        
        deployment = await engine.deploy_capsule(
            manifest=manifest,
            cloud_provider=CloudProvider.AZURE
        )
        
        success = await engine.scale_capsule(deployment.capsule_id, 3)
        
        assert success
        assert deployment.manifest.replicas == 3
    
    @pytest.mark.asyncio
    async def test_scale_capsule_not_found(self):
        """Test scaling non-existent capsule."""
        engine = DACEngine()
        
        with pytest.raises(ValueError):
            await engine.scale_capsule("non-existent-id", 3)
    
    @pytest.mark.asyncio
    async def test_stop_capsule(self):
        """Test stopping a capsule."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        deployment = await engine.deploy_capsule(
            manifest=manifest,
            cloud_provider=CloudProvider.AZURE
        )
        
        success = await engine.stop_capsule(deployment.capsule_id)
        
        assert success
        assert deployment.status == DeploymentStatus.STOPPED
    
    @pytest.mark.asyncio
    async def test_stop_capsule_not_found(self):
        """Test stopping non-existent capsule."""
        engine = DACEngine()
        
        with pytest.raises(ValueError):
            await engine.stop_capsule("non-existent-id")
    
    @pytest.mark.asyncio
    async def test_list_capsules_all(self):
        """Test listing all capsules."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest1 = DACManifest(
            name="capsule-1",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        manifest2 = DACManifest(
            name="capsule-2",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        await engine.deploy_capsule(manifest1, CloudProvider.AZURE)
        await engine.deploy_capsule(manifest2, CloudProvider.AWS)
        
        capsules = engine.list_capsules()
        
        assert len(capsules) == 2
    
    @pytest.mark.asyncio
    async def test_list_capsules_by_cloud(self):
        """Test listing capsules filtered by cloud provider."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest1 = DACManifest(
            name="capsule-1",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        manifest2 = DACManifest(
            name="capsule-2",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        await engine.deploy_capsule(manifest1, CloudProvider.AZURE)
        await engine.deploy_capsule(manifest2, CloudProvider.AWS)
        
        azure_capsules = engine.list_capsules(CloudProvider.AZURE)
        
        assert len(azure_capsules) == 1
        assert azure_capsules[0].cloud_provider == CloudProvider.AZURE
    
    @pytest.mark.asyncio
    async def test_get_deployment_summary(self):
        """Test getting deployment summary statistics."""
        engine = DACEngine()
        await engine.connect_all()
        
        manifest = DACManifest(
            name="test-capsule",
            version="1.0.0",
            description="Test",
            image="test:1.0.0"
        )
        
        await engine.deploy_capsule(manifest, CloudProvider.AZURE)
        await engine.deploy_capsule(manifest, CloudProvider.AWS)
        
        summary = engine.get_deployment_summary()
        
        assert summary["total_capsules"] == 2
        assert "by_cloud" in summary
        assert "by_status" in summary


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
