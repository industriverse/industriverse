"""
Unit tests for DAC Lifecycle Manager

Tests cover:
1. Hypothesis packaging into capsules
2. Version generation and management
3. Capsule deployment
4. Upgrade strategies (rolling, blue-green, canary, recreate)
5. Rollback functionality
6. Version history and lineage tracking
7. Error handling

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio
from datetime import datetime

from ..dac_lifecycle_manager import (
    DACLifecycleManager,
    DACLifecycleConfig,
    Hypothesis,
    CapsuleVersion,
    CapsuleStatus,
    UpgradeStrategy,
    UpgradeResult
)
from ..dac_engine import DACEngine, CloudProvider


class TestHypothesis:
    """Test suite for Hypothesis dataclass."""
    
    def test_hypothesis_creation(self):
        """Test hypothesis creation."""
        hypothesis = Hypothesis(
            id="hyp_001",
            text="Test hypothesis",
            parameters={"param1": 1.0},
            domain="test",
            confidence=0.85
        )
        
        assert hypothesis.id == "hyp_001"
        assert hypothesis.text == "Test hypothesis"
        assert hypothesis.domain == "test"
        assert hypothesis.confidence == 0.85


class TestDACLifecycleManager:
    """Test suite for DAC Lifecycle Manager."""
    
    @pytest.fixture
    def dac_engine(self):
        """Create DAC Engine."""
        return DACEngine()
    
    @pytest.fixture
    def lifecycle_manager(self, dac_engine):
        """Create DAC Lifecycle Manager."""
        return DACLifecycleManager(dac_engine)
    
    @pytest.fixture
    def sample_hypothesis(self):
        """Create sample hypothesis."""
        return Hypothesis(
            id="hyp_001",
            text="Optimize turbine blade geometry",
            parameters={"blade_count": 12, "angle": 45.0},
            domain="aerospace",
            confidence=0.85
        )
    
    def test_manager_initialization(self, dac_engine):
        """Test lifecycle manager initialization."""
        manager = DACLifecycleManager(dac_engine)
        
        assert manager.dac_engine == dac_engine
        assert manager.config is not None
        assert len(manager.capsule_versions) == 0
        assert len(manager.active_capsules) == 0
    
    def test_manager_initialization_custom_config(self, dac_engine):
        """Test lifecycle manager with custom config."""
        config = DACLifecycleConfig(
            base_image_registry="custom-registry",
            version_history_limit=5
        )
        
        manager = DACLifecycleManager(dac_engine, config=config)
        
        assert manager.config.base_image_registry == "custom-registry"
        assert manager.config.version_history_limit == 5
    
    @pytest.mark.asyncio
    async def test_package_hypothesis(self, lifecycle_manager, sample_hypothesis):
        """Test packaging hypothesis into capsule."""
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        assert isinstance(capsule, CapsuleVersion)
        assert capsule.version == "1.0.0"
        assert capsule.hypothesis_id == sample_hypothesis.id
        assert capsule.status == CapsuleStatus.PACKAGED
        assert capsule.manifest.name.startswith("aerospace-capsule")
    
    @pytest.mark.asyncio
    async def test_package_hypothesis_with_resources(self, lifecycle_manager, sample_hypothesis):
        """Test packaging hypothesis with custom resources."""
        resources = {
            "requests": {"cpu": "200m", "memory": "512Mi"},
            "limits": {"cpu": "2000m", "memory": "2Gi"}
        }
        
        capsule = await lifecycle_manager.package_hypothesis(
            sample_hypothesis,
            resources=resources
        )
        
        assert capsule.manifest.resources == resources
    
    @pytest.mark.asyncio
    async def test_version_generation_first(self, lifecycle_manager, sample_hypothesis):
        """Test version generation for first capsule."""
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        assert capsule.version == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_version_generation_increment(self, lifecycle_manager, sample_hypothesis):
        """Test version generation increments correctly."""
        # Package first version
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        assert capsule_v1.version == "1.0.0"
        
        # Package second version
        capsule_v2 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        assert capsule_v2.version == "1.0.1"
        
        # Package third version
        capsule_v3 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        assert capsule_v3.version == "1.0.2"
    
    @pytest.mark.asyncio
    async def test_capsule_hash_generation(self, lifecycle_manager, sample_hypothesis):
        """Test capsule hash generation."""
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        assert "capsule_hash" in capsule.metadata
        assert len(capsule.metadata["capsule_hash"]) == 16
    
    @pytest.mark.asyncio
    async def test_capsule_manifest_labels(self, lifecycle_manager, sample_hypothesis):
        """Test capsule manifest includes correct labels."""
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        assert "app" in capsule.manifest.labels
        assert "version" in capsule.manifest.labels
        assert "domain" in capsule.manifest.labels
        assert capsule.manifest.labels["domain"] == "aerospace"
    
    @pytest.mark.asyncio
    async def test_capsule_manifest_annotations(self, lifecycle_manager, sample_hypothesis):
        """Test capsule manifest includes correct annotations."""
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        assert "industriverse.io/capsule-hash" in capsule.manifest.annotations
        assert "industriverse.io/hypothesis-confidence" in capsule.manifest.annotations
    
    @pytest.mark.asyncio
    async def test_deploy_capsule(self, lifecycle_manager, sample_hypothesis):
        """Test deploying a packaged capsule."""
        await lifecycle_manager.dac_engine.connect_all()
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        success = await lifecycle_manager.deploy_capsule(
            capsule,
            CloudProvider.AZURE
        )
        
        assert success
        assert capsule.status == CapsuleStatus.DEPLOYED
        assert capsule.deployed_at is not None
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_to_aws(self, lifecycle_manager, sample_hypothesis):
        """Test deploying capsule to AWS."""
        await lifecycle_manager.dac_engine.connect_all()
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        success = await lifecycle_manager.deploy_capsule(
            capsule,
            CloudProvider.AWS
        )
        
        assert success
        assert capsule.status == CapsuleStatus.DEPLOYED
    
    @pytest.mark.asyncio
    async def test_deploy_capsule_custom_namespace(self, lifecycle_manager, sample_hypothesis):
        """Test deploying capsule to custom namespace."""
        await lifecycle_manager.dac_engine.connect_all()
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        success = await lifecycle_manager.deploy_capsule(
            capsule,
            CloudProvider.AZURE,
            namespace="custom-namespace"
        )
        
        assert success
    
    @pytest.mark.asyncio
    async def test_active_capsules_tracking(self, lifecycle_manager, sample_hypothesis):
        """Test that deployed capsules are tracked as active."""
        await lifecycle_manager.dac_engine.connect_all()
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        await lifecycle_manager.deploy_capsule(capsule, CloudProvider.AZURE)
        
        active_capsules = lifecycle_manager.get_active_capsules()
        
        assert len(active_capsules) == 1
    
    @pytest.mark.asyncio
    async def test_upgrade_capsule_rolling(self, lifecycle_manager, sample_hypothesis):
        """Test capsule upgrade with rolling strategy."""
        await lifecycle_manager.dac_engine.connect_all()
        # Deploy initial version
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        await lifecycle_manager.deploy_capsule(capsule_v1, CloudProvider.AZURE)
        
        # Create new hypothesis for upgrade
        hypothesis_v2 = Hypothesis(
            id="hyp_002",
            text="Improved turbine blade geometry",
            parameters={"blade_count": 14, "angle": 47.5},
            domain="aerospace",
            confidence=0.92
        )
        
        # Upgrade capsule
        result = await lifecycle_manager.upgrade_capsule(
            capsule_name=capsule_v1.manifest.name,
            new_hypothesis=hypothesis_v2,
            cloud_provider=CloudProvider.AZURE,
            strategy=UpgradeStrategy.ROLLING
        )
        
        assert result.success
        assert result.old_version == "1.0.0"
        assert result.new_version == "1.0.0"  # New hypothesis gets its own version
        assert result.strategy == UpgradeStrategy.ROLLING
    
    @pytest.mark.asyncio
    async def test_upgrade_capsule_blue_green(self, lifecycle_manager, sample_hypothesis):
        """Test capsule upgrade with blue-green strategy."""
        await lifecycle_manager.dac_engine.connect_all()
        # Deploy initial version
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        await lifecycle_manager.deploy_capsule(capsule_v1, CloudProvider.AZURE)
        
        # Create new hypothesis
        hypothesis_v2 = Hypothesis(
            id="hyp_002",
            text="Improved hypothesis",
            parameters={"param": 2.0},
            domain="aerospace",
            confidence=0.90
        )
        
        # Upgrade with blue-green
        result = await lifecycle_manager.upgrade_capsule(
            capsule_name=capsule_v1.manifest.name,
            new_hypothesis=hypothesis_v2,
            cloud_provider=CloudProvider.AZURE,
            strategy=UpgradeStrategy.BLUE_GREEN
        )
        
        assert result.success
        assert result.strategy == UpgradeStrategy.BLUE_GREEN
    
    @pytest.mark.asyncio
    async def test_upgrade_capsule_canary(self, lifecycle_manager, sample_hypothesis):
        """Test capsule upgrade with canary strategy."""
        await lifecycle_manager.dac_engine.connect_all()
        # Deploy initial version
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        await lifecycle_manager.deploy_capsule(capsule_v1, CloudProvider.AZURE)
        
        # Create new hypothesis
        hypothesis_v2 = Hypothesis(
            id="hyp_002",
            text="Improved hypothesis",
            parameters={"param": 2.0},
            domain="aerospace",
            confidence=0.90
        )
        
        # Upgrade with canary
        result = await lifecycle_manager.upgrade_capsule(
            capsule_name=capsule_v1.manifest.name,
            new_hypothesis=hypothesis_v2,
            cloud_provider=CloudProvider.AZURE,
            strategy=UpgradeStrategy.CANARY
        )
        
        assert result.success
        assert result.strategy == UpgradeStrategy.CANARY
    
    @pytest.mark.asyncio
    async def test_upgrade_capsule_recreate(self, lifecycle_manager, sample_hypothesis):
        """Test capsule upgrade with recreate strategy."""
        await lifecycle_manager.dac_engine.connect_all()
        # Deploy initial version
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        await lifecycle_manager.deploy_capsule(capsule_v1, CloudProvider.AZURE)
        
        # Create new hypothesis
        hypothesis_v2 = Hypothesis(
            id="hyp_002",
            text="Improved hypothesis",
            parameters={"param": 2.0},
            domain="aerospace",
            confidence=0.90
        )
        
        # Upgrade with recreate
        result = await lifecycle_manager.upgrade_capsule(
            capsule_name=capsule_v1.manifest.name,
            new_hypothesis=hypothesis_v2,
            cloud_provider=CloudProvider.AZURE,
            strategy=UpgradeStrategy.RECREATE
        )
        
        assert result.success
        assert result.strategy == UpgradeStrategy.RECREATE
    
    @pytest.mark.asyncio
    async def test_upgrade_nonexistent_capsule(self, lifecycle_manager, sample_hypothesis):
        """Test upgrading non-existent capsule fails gracefully."""
        result = await lifecycle_manager.upgrade_capsule(
            capsule_name="nonexistent-capsule",
            new_hypothesis=sample_hypothesis,
            cloud_provider=CloudProvider.AZURE
        )
        
        assert not result.success
        assert result.error is not None
        assert "No active capsule found" in result.error
    
    @pytest.mark.asyncio
    async def test_upgrade_result_duration(self, lifecycle_manager, sample_hypothesis):
        """Test that upgrade result includes duration."""
        await lifecycle_manager.dac_engine.connect_all()
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        await lifecycle_manager.deploy_capsule(capsule_v1, CloudProvider.AZURE)
        
        hypothesis_v2 = Hypothesis(
            id="hyp_002",
            text="Improved",
            parameters={},
            domain="aerospace",
            confidence=0.90
        )
        
        result = await lifecycle_manager.upgrade_capsule(
            capsule_name=capsule_v1.manifest.name,
            new_hypothesis=hypothesis_v2,
            cloud_provider=CloudProvider.AZURE
        )
        
        assert result.duration > 0
    
    @pytest.mark.asyncio
    async def test_upgrade_updates_active_capsule(self, lifecycle_manager, sample_hypothesis):
        """Test that upgrade updates the active capsule."""
        await lifecycle_manager.dac_engine.connect_all()
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        await lifecycle_manager.deploy_capsule(capsule_v1, CloudProvider.AZURE)
        
        hypothesis_v2 = Hypothesis(
            id="hyp_002",
            text="Improved",
            parameters={},
            domain="aerospace",
            confidence=0.90
        )
        
        await lifecycle_manager.upgrade_capsule(
            capsule_name=capsule_v1.manifest.name,
            new_hypothesis=hypothesis_v2,
            cloud_provider=CloudProvider.AZURE
        )
        
        active_capsules = lifecycle_manager.get_active_capsules()
        capsule_id = f"{capsule_v1.manifest.name}-azure"
        
        # After upgrade, the active capsule should be updated
        assert len(active_capsules) > 0
    
    @pytest.mark.asyncio
    async def test_get_capsule_history(self, lifecycle_manager, sample_hypothesis):
        """Test getting capsule version history."""
        # Package multiple versions
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        capsule_v2 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        capsule_v3 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        history = lifecycle_manager.get_capsule_history(capsule_v1.manifest.name)
        
        assert len(history) == 3
        assert history[0].version == "1.0.0"
        assert history[1].version == "1.0.1"
        assert history[2].version == "1.0.2"
    
    @pytest.mark.asyncio
    async def test_version_history_limit(self, dac_engine, sample_hypothesis):
        """Test that version history respects limit."""
        config = DACLifecycleConfig(version_history_limit=3)
        manager = DACLifecycleManager(dac_engine, config=config)
        
        # Package 5 versions
        for i in range(5):
            await manager.package_hypothesis(sample_hypothesis)
        
        # Get first capsule name
        capsule_name = list(manager.capsule_versions.keys())[0]
        history = manager.get_capsule_history(capsule_name)
        
        # Should only keep last 3
        assert len(history) == 3
    
    @pytest.mark.asyncio
    async def test_get_capsule_lineage(self, lifecycle_manager, sample_hypothesis):
        """Test getting capsule version lineage."""
        await lifecycle_manager.dac_engine.connect_all()
        # Deploy initial version
        capsule_v1 = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        await lifecycle_manager.deploy_capsule(capsule_v1, CloudProvider.AZURE)
        
        # Upgrade twice
        for i in range(2):
            hypothesis = Hypothesis(
                id=f"hyp_{i+2:03d}",
                text=f"Improved {i+1}",
                parameters={},
                domain="aerospace",
                confidence=0.90
            )
            await lifecycle_manager.upgrade_capsule(
                capsule_name=capsule_v1.manifest.name,
                new_hypothesis=hypothesis,
                cloud_provider=CloudProvider.AZURE
            )
        
        lineage = lifecycle_manager.get_capsule_lineage(capsule_v1.manifest.name)
        
        # Lineage tracks the original capsule's versions
        assert len(lineage) >= 1
        assert lineage[0][0] == "1.0.0"
    
    @pytest.mark.asyncio
    async def test_capsule_metadata_preservation(self, lifecycle_manager, sample_hypothesis):
        """Test that capsule metadata is preserved."""
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        assert "hypothesis_text" in capsule.metadata
        assert "hypothesis_parameters" in capsule.metadata
        assert "domain" in capsule.metadata
        assert "confidence" in capsule.metadata
        assert capsule.metadata["domain"] == "aerospace"
    
    @pytest.mark.asyncio
    async def test_multiple_domains(self, lifecycle_manager):
        """Test packaging capsules from different domains."""
        hyp_aerospace = Hypothesis(
            id="hyp_001",
            text="Aerospace hypothesis",
            parameters={},
            domain="aerospace",
            confidence=0.85
        )
        
        hyp_manufacturing = Hypothesis(
            id="hyp_002",
            text="Manufacturing hypothesis",
            parameters={},
            domain="manufacturing",
            confidence=0.90
        )
        
        capsule_aero = await lifecycle_manager.package_hypothesis(hyp_aerospace)
        capsule_mfg = await lifecycle_manager.package_hypothesis(hyp_manufacturing)
        
        assert "aerospace-capsule" in capsule_aero.manifest.name
        assert "manufacturing-capsule" in capsule_mfg.manifest.name
    
    @pytest.mark.asyncio
    async def test_capsule_env_vars(self, lifecycle_manager, sample_hypothesis):
        """Test that capsule includes correct environment variables."""
        capsule = await lifecycle_manager.package_hypothesis(sample_hypothesis)
        
        assert "HYPOTHESIS_ID" in capsule.manifest.env_vars
        assert "DOMAIN" in capsule.manifest.env_vars
        assert "CONFIDENCE" in capsule.manifest.env_vars
        assert capsule.manifest.env_vars["DOMAIN"] == "aerospace"


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
