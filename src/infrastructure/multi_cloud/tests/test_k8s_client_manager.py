"""
Unit tests for Kubernetes Multi-Cloud Client Manager

Tests cover:
1. Manager initialization and configuration
2. Cluster configuration and registration
3. Connection management (connect, disconnect)
4. Health checking and monitoring
5. Client retrieval and listing
6. Statistics and capacity tracking
7. Error handling

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio

from ..k8s_client_manager import (
    K8sClientManager,
    K8sClientManagerConfig,
    ClusterConfig,
    ClusterHealth,
    CloudProvider,
    ClusterStatus
)


class TestK8sClientManager:
    """Test suite for K8s Client Manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization with default config."""
        manager = K8sClientManager()
        
        assert manager.config is not None
        assert len(manager.clusters) == 3  # Azure, AWS, GCP
        assert len(manager.clients) == 0
    
    def test_manager_initialization_custom_config(self):
        """Test manager initialization with custom config."""
        config = K8sClientManagerConfig(
            default_namespace="custom",
            connection_timeout=60
        )
        
        manager = K8sClientManager(config=config)
        
        assert manager.config.default_namespace == "custom"
        assert manager.config.connection_timeout == 60
    
    def test_default_clusters_initialized(self):
        """Test that default clusters are initialized."""
        manager = K8sClientManager()
        
        assert "industriverse-azure-v2" in manager.clusters
        assert "molecular-industrial-cluster" in manager.clusters
        assert "industriverse-cluster" in manager.clusters
    
    def test_azure_cluster_config(self):
        """Test Azure cluster configuration."""
        manager = K8sClientManager()
        
        azure_cluster = manager.get_cluster("industriverse-azure-v2")
        
        assert azure_cluster is not None
        assert azure_cluster.provider == CloudProvider.AZURE
        assert azure_cluster.region == "eastus2"
        assert azure_cluster.namespace == "industriverse"
    
    def test_aws_cluster_config(self):
        """Test AWS cluster configuration."""
        manager = K8sClientManager()
        
        aws_cluster = manager.get_cluster("molecular-industrial-cluster")
        
        assert aws_cluster is not None
        assert aws_cluster.provider == CloudProvider.AWS
        assert aws_cluster.region == "us-east-1"
        assert aws_cluster.namespace == "molecular"
    
    def test_gcp_cluster_config(self):
        """Test GCP cluster configuration."""
        manager = K8sClientManager()
        
        gcp_cluster = manager.get_cluster("industriverse-cluster")
        
        assert gcp_cluster is not None
        assert gcp_cluster.provider == CloudProvider.GCP
        assert gcp_cluster.region == "us-central1"
        assert gcp_cluster.namespace == "industriverse"
    
    @pytest.mark.asyncio
    async def test_connect_cluster(self):
        """Test connecting to a cluster."""
        manager = K8sClientManager()
        
        success = await manager.connect_cluster("industriverse-azure-v2")
        
        assert success
        assert "industriverse-azure-v2" in manager.clients
        assert "industriverse-azure-v2" in manager.health_status
    
    @pytest.mark.asyncio
    async def test_connect_cluster_not_found(self):
        """Test connecting to non-existent cluster."""
        manager = K8sClientManager()
        
        with pytest.raises(ValueError):
            await manager.connect_cluster("nonexistent")
    
    @pytest.mark.asyncio
    async def test_disconnect_cluster(self):
        """Test disconnecting from a cluster."""
        manager = K8sClientManager()
        
        await manager.connect_cluster("industriverse-azure-v2")
        await manager.disconnect_cluster("industriverse-azure-v2")
        
        assert "industriverse-azure-v2" not in manager.clients
        assert manager.health_status["industriverse-azure-v2"].status == ClusterStatus.DISCONNECTED
    
    @pytest.mark.asyncio
    async def test_connect_all_clusters(self):
        """Test connecting to all clusters."""
        manager = K8sClientManager()
        
        results = await manager.connect_all_clusters()
        
        assert len(results) == 3
        assert all(results.values())  # All should succeed
        assert len(manager.clients) == 3
    
    @pytest.mark.asyncio
    async def test_check_cluster_health(self):
        """Test checking cluster health."""
        manager = K8sClientManager()
        
        await manager.connect_cluster("industriverse-azure-v2")
        health = await manager.check_cluster_health("industriverse-azure-v2")
        
        assert isinstance(health, ClusterHealth)
        assert health.cluster_name == "industriverse-azure-v2"
        assert health.status == ClusterStatus.CONNECTED
        assert health.node_count > 0
    
    @pytest.mark.asyncio
    async def test_check_cluster_health_not_connected(self):
        """Test checking health of disconnected cluster."""
        manager = K8sClientManager()
        
        health = await manager.check_cluster_health("industriverse-azure-v2")
        
        assert health.status == ClusterStatus.DISCONNECTED
        assert health.error_message is not None
    
    @pytest.mark.asyncio
    async def test_check_cluster_health_not_found(self):
        """Test checking health of non-existent cluster."""
        manager = K8sClientManager()
        
        with pytest.raises(ValueError):
            await manager.check_cluster_health("nonexistent")
    
    @pytest.mark.asyncio
    async def test_check_all_clusters_health(self):
        """Test checking health of all clusters."""
        manager = K8sClientManager()
        
        await manager.connect_all_clusters()
        health_results = await manager.check_all_clusters_health()
        
        assert len(health_results) == 3
        assert all(isinstance(h, ClusterHealth) for h in health_results.values())
    
    def test_get_cluster(self):
        """Test getting cluster configuration."""
        manager = K8sClientManager()
        
        cluster = manager.get_cluster("industriverse-azure-v2")
        
        assert cluster is not None
        assert cluster.name == "industriverse-azure-v2"
    
    def test_get_cluster_not_found(self):
        """Test getting non-existent cluster."""
        manager = K8sClientManager()
        
        cluster = manager.get_cluster("nonexistent")
        
        assert cluster is None
    
    @pytest.mark.asyncio
    async def test_get_client(self):
        """Test getting Kubernetes client."""
        manager = K8sClientManager()
        
        await manager.connect_cluster("industriverse-azure-v2")
        client = manager.get_client("industriverse-azure-v2")
        
        assert client is not None
        assert client["connected"]
    
    @pytest.mark.asyncio
    async def test_get_client_not_connected(self):
        """Test getting client for disconnected cluster."""
        manager = K8sClientManager()
        
        client = manager.get_client("industriverse-azure-v2")
        
        assert client is None
    
    def test_list_clusters_all(self):
        """Test listing all clusters."""
        manager = K8sClientManager()
        
        clusters = manager.list_clusters()
        
        assert len(clusters) == 3
        assert all(isinstance(c, ClusterConfig) for c in clusters)
    
    def test_list_clusters_by_provider_azure(self):
        """Test listing Azure clusters."""
        manager = K8sClientManager()
        
        clusters = manager.list_clusters(CloudProvider.AZURE)
        
        assert len(clusters) == 1
        assert clusters[0].provider == CloudProvider.AZURE
    
    def test_list_clusters_by_provider_aws(self):
        """Test listing AWS clusters."""
        manager = K8sClientManager()
        
        clusters = manager.list_clusters(CloudProvider.AWS)
        
        assert len(clusters) == 1
        assert clusters[0].provider == CloudProvider.AWS
    
    def test_list_clusters_by_provider_gcp(self):
        """Test listing GCP clusters."""
        manager = K8sClientManager()
        
        clusters = manager.list_clusters(CloudProvider.GCP)
        
        assert len(clusters) == 1
        assert clusters[0].provider == CloudProvider.GCP
    
    @pytest.mark.asyncio
    async def test_get_connected_clusters(self):
        """Test getting list of connected clusters."""
        manager = K8sClientManager()
        
        await manager.connect_cluster("industriverse-azure-v2")
        await manager.connect_cluster("industriverse-cluster")
        
        connected = manager.get_connected_clusters()
        
        assert len(connected) == 2
        assert "industriverse-azure-v2" in connected
        assert "industriverse-cluster" in connected
    
    @pytest.mark.asyncio
    async def test_get_statistics(self):
        """Test getting manager statistics."""
        manager = K8sClientManager()
        
        await manager.connect_all_clusters()
        await manager.check_all_clusters_health()
        
        stats = manager.get_statistics()
        
        assert stats["total_clusters"] == 3
        assert stats["connected_clusters"] == 3
        assert stats["by_provider"]["azure"] == 1
        assert stats["by_provider"]["aws"] == 1
        assert stats["by_provider"]["gcp"] == 1
        assert stats["total_cpu_capacity"] > 0
        assert stats["total_memory_capacity"] > 0
        assert stats["total_nodes"] > 0


class TestClusterHealthDataclass:
    """Test suite for ClusterHealth dataclass."""
    
    def test_cluster_health_to_dict(self):
        """Test cluster health serialization."""
        health = ClusterHealth(
            cluster_name="test-cluster",
            status=ClusterStatus.CONNECTED,
            version="v1.28.0",
            node_count=3,
            healthy_nodes=3,
            cpu_capacity=24.0,
            memory_capacity=96.0
        )
        
        health_dict = health.to_dict()
        
        assert isinstance(health_dict, dict)
        assert health_dict["cluster_name"] == "test-cluster"
        assert health_dict["status"] == "connected"
        assert health_dict["node_count"] == 3


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
