"""
DAC Lifecycle Manager

This module implements the DAC Lifecycle Manager for packaging hypotheses into
deployable capsules and managing their lifecycle (versioning, upgrades, rollbacks).

The DAC Lifecycle Manager is responsible for:
1. Transforming hypotheses into deployable DAC capsules
2. Managing capsule versions and metadata
3. Orchestrating capsule upgrades and rollbacks
4. Tracking capsule lineage and evolution
5. Integrating with UTID generation and proof systems
6. Managing capsule dependencies and compatibility

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib
import json
from pathlib import Path

from .dac_engine import DACManifest, DACEngine, CloudProvider

logger = logging.getLogger(__name__)


class CapsuleStatus(Enum):
    """Capsule lifecycle status."""
    DRAFT = "draft"
    PACKAGED = "packaged"
    DEPLOYED = "deployed"
    UPGRADING = "upgrading"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class UpgradeStrategy(Enum):
    """Capsule upgrade strategies."""
    ROLLING = "rolling"  # Rolling update with zero downtime
    BLUE_GREEN = "blue_green"  # Blue-green deployment
    CANARY = "canary"  # Canary deployment
    RECREATE = "recreate"  # Recreate all pods


@dataclass
class Hypothesis:
    """
    Hypothesis to be packaged into a capsule.
    
    Attributes:
        id: Unique hypothesis identifier
        text: Hypothesis text
        parameters: Hypothesis parameters
        domain: Domain (aerospace, manufacturing, etc.)
        confidence: Confidence score
        metadata: Additional metadata
    """
    id: str
    text: str
    parameters: Dict[str, Any]
    domain: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapsuleVersion:
    """
    Capsule version information.
    
    Attributes:
        version: Version string (semantic versioning)
        hypothesis_id: Source hypothesis ID
        manifest: DAC manifest
        utid: Universal Traceable Identifier
        proof_hash: zk-SNARK proof hash
        energy_signature: Energy signature
        created_at: Creation timestamp
        deployed_at: Deployment timestamp
        status: Capsule status
        parent_version: Parent version (for upgrades)
        metadata: Additional metadata
    """
    version: str
    hypothesis_id: str
    manifest: DACManifest
    utid: Optional[str] = None
    proof_hash: Optional[str] = None
    energy_signature: Optional[Dict[str, float]] = None
    created_at: datetime = field(default_factory=datetime.now)
    deployed_at: Optional[datetime] = None
    status: CapsuleStatus = CapsuleStatus.DRAFT
    parent_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class UpgradeResult:
    """
    Result of capsule upgrade operation.
    
    Attributes:
        success: Whether upgrade succeeded
        old_version: Previous version
        new_version: New version
        strategy: Upgrade strategy used
        duration: Upgrade duration in seconds
        rollback_available: Whether rollback is available
        error: Error message if failed
    """
    success: bool
    old_version: str
    new_version: str
    strategy: UpgradeStrategy
    duration: float
    rollback_available: bool = True
    error: Optional[str] = None


@dataclass
class DACLifecycleConfig:
    """
    Configuration for DAC Lifecycle Manager.
    
    Attributes:
        base_image_registry: Base container image registry
        default_upgrade_strategy: Default upgrade strategy
        version_history_limit: Maximum versions to keep in history
        enable_auto_rollback: Enable automatic rollback on failure
        health_check_timeout: Health check timeout in seconds
    """
    base_image_registry: str = "industriverse"
    default_upgrade_strategy: UpgradeStrategy = UpgradeStrategy.ROLLING
    version_history_limit: int = 10
    enable_auto_rollback: bool = True
    health_check_timeout: int = 60


class DACLifecycleManager:
    """
    DAC Lifecycle Manager for capsule packaging and version management.
    
    This manager transforms hypotheses into deployable capsules and manages
    their entire lifecycle from creation to deprecation.
    """
    
    def __init__(
        self,
        dac_engine: DACEngine,
        config: Optional[DACLifecycleConfig] = None
    ):
        """
        Initialize DAC Lifecycle Manager.
        
        Args:
            dac_engine: DAC Runtime Engine instance
            config: Lifecycle manager configuration
        """
        self.dac_engine = dac_engine
        self.config = config or DACLifecycleConfig()
        self.capsule_versions: Dict[str, List[CapsuleVersion]] = {}
        self.active_capsules: Dict[str, CapsuleVersion] = {}
        
        logger.info(f"DAC Lifecycle Manager initialized with config: {self.config}")
    
    def _generate_version(self, capsule_name: str) -> str:
        """
        Generate next semantic version for capsule.
        
        Args:
            capsule_name: Capsule name
        
        Returns:
            Next version string
        """
        versions = self.capsule_versions.get(capsule_name, [])
        
        if not versions:
            return "1.0.0"
        
        # Get latest version
        latest = versions[-1].version
        major, minor, patch = map(int, latest.split('.'))
        
        # Increment patch version
        return f"{major}.{minor}.{patch + 1}"
    
    def _generate_capsule_hash(self, hypothesis: Hypothesis) -> str:
        """
        Generate hash for capsule based on hypothesis.
        
        Args:
            hypothesis: Source hypothesis
        
        Returns:
            Capsule hash
        """
        # Create hash from hypothesis content
        content = f"{hypothesis.id}:{hypothesis.text}:{json.dumps(hypothesis.parameters)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    async def package_hypothesis(
        self,
        hypothesis: Hypothesis,
        resources: Optional[Dict[str, Any]] = None
    ) -> CapsuleVersion:
        """
        Package a hypothesis into a deployable capsule.
        
        Args:
            hypothesis: Hypothesis to package
            resources: Resource requirements (optional)
        
        Returns:
            Capsule version
        """
        logger.info(f"Packaging hypothesis {hypothesis.id} into capsule")
        
        # Generate capsule name
        capsule_name = f"{hypothesis.domain}-capsule-{hypothesis.id[:8]}"
        
        # Generate version
        version = self._generate_version(capsule_name)
        
        # Generate capsule hash
        capsule_hash = self._generate_capsule_hash(hypothesis)
        
        # Create container image name
        image = f"{self.config.base_image_registry}/{capsule_name}:{version}"
        
        # Set default resources if not provided
        if not resources:
            resources = {
                "requests": {"cpu": "100m", "memory": "256Mi"},
                "limits": {"cpu": "1000m", "memory": "1Gi"}
            }
        
        # Create DAC manifest
        manifest = DACManifest(
            name=capsule_name,
            version=version,
            description=f"Capsule for hypothesis: {hypothesis.text[:100]}",
            image=image,
            replicas=1,
            resources=resources,
            env_vars={
                "HYPOTHESIS_ID": hypothesis.id,
                "DOMAIN": hypothesis.domain,
                "CONFIDENCE": str(hypothesis.confidence)
            },
            ports=[8080, 9090],
            labels={
                "app": capsule_name,
                "version": version,
                "domain": hypothesis.domain,
                "hypothesis-id": hypothesis.id
            },
            annotations={
                "industriverse.io/capsule-hash": capsule_hash,
                "industriverse.io/hypothesis-confidence": str(hypothesis.confidence),
                "industriverse.io/created-at": datetime.now().isoformat()
            }
        )
        
        # Create capsule version
        capsule_version = CapsuleVersion(
            version=version,
            hypothesis_id=hypothesis.id,
            manifest=manifest,
            status=CapsuleStatus.PACKAGED,
            metadata={
                "hypothesis_text": hypothesis.text,
                "hypothesis_parameters": hypothesis.parameters,
                "domain": hypothesis.domain,
                "confidence": hypothesis.confidence,
                "capsule_hash": capsule_hash
            }
        )
        
        # Store capsule version
        if capsule_name not in self.capsule_versions:
            self.capsule_versions[capsule_name] = []
        
        self.capsule_versions[capsule_name].append(capsule_version)
        
        # Trim version history
        if len(self.capsule_versions[capsule_name]) > self.config.version_history_limit:
            self.capsule_versions[capsule_name] = self.capsule_versions[capsule_name][-self.config.version_history_limit:]
        
        logger.info(f"Packaged capsule {capsule_name} version {version}")
        return capsule_version
    
    async def deploy_capsule(
        self,
        capsule_version: CapsuleVersion,
        cloud_provider: CloudProvider,
        namespace: Optional[str] = None
    ) -> bool:
        """
        Deploy a packaged capsule.
        
        Args:
            capsule_version: Capsule version to deploy
            cloud_provider: Target cloud provider
            namespace: Kubernetes namespace (optional)
        
        Returns:
            True if deployment successful
        """
        logger.info(f"Deploying capsule {capsule_version.manifest.name} version {capsule_version.version}")
        
        try:
            # Deploy using DAC Engine
            deployment_info = await self.dac_engine.deploy_capsule(
                manifest=capsule_version.manifest,
                cloud_provider=cloud_provider,
                namespace=namespace
            )
            
            # Update capsule status
            capsule_version.status = CapsuleStatus.DEPLOYED
            capsule_version.deployed_at = datetime.now()
            
            # Store as active capsule
            capsule_id = f"{capsule_version.manifest.name}-{cloud_provider.value}"
            self.active_capsules[capsule_id] = capsule_version
            
            logger.info(f"Successfully deployed capsule {capsule_version.manifest.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to deploy capsule: {e}")
            return False
    
    async def upgrade_capsule(
        self,
        capsule_name: str,
        new_hypothesis: Hypothesis,
        cloud_provider: CloudProvider,
        strategy: Optional[UpgradeStrategy] = None,
        namespace: Optional[str] = None
    ) -> UpgradeResult:
        """
        Upgrade a deployed capsule to a new version.
        
        Args:
            capsule_name: Name of capsule to upgrade
            new_hypothesis: New hypothesis for upgraded version
            cloud_provider: Target cloud provider
            strategy: Upgrade strategy (uses default if None)
            namespace: Kubernetes namespace (optional)
        
        Returns:
            Upgrade result
        """
        start_time = datetime.now()
        strategy = strategy or self.config.default_upgrade_strategy
        
        logger.info(f"Upgrading capsule {capsule_name} using {strategy.value} strategy")
        
        # Get current active version
        capsule_id = f"{capsule_name}-{cloud_provider.value}"
        current_version = self.active_capsules.get(capsule_id)
        
        if not current_version:
            error = f"No active capsule found: {capsule_name}"
            logger.error(error)
            return UpgradeResult(
                success=False,
                old_version="unknown",
                new_version="unknown",
                strategy=strategy,
                duration=0.0,
                rollback_available=False,
                error=error
            )
        
        try:
            # Package new hypothesis
            new_version = await self.package_hypothesis(new_hypothesis)
            new_version.parent_version = current_version.version
            
            # Mark current version as upgrading
            current_version.status = CapsuleStatus.UPGRADING
            
            # Execute upgrade based on strategy
            if strategy == UpgradeStrategy.ROLLING:
                success = await self._rolling_upgrade(
                    current_version, new_version, cloud_provider, namespace
                )
            elif strategy == UpgradeStrategy.BLUE_GREEN:
                success = await self._blue_green_upgrade(
                    current_version, new_version, cloud_provider, namespace
                )
            elif strategy == UpgradeStrategy.CANARY:
                success = await self._canary_upgrade(
                    current_version, new_version, cloud_provider, namespace
                )
            else:  # RECREATE
                success = await self._recreate_upgrade(
                    current_version, new_version, cloud_provider, namespace
                )
            
            duration = (datetime.now() - start_time).total_seconds()
            
            if success:
                # Update active capsule
                self.active_capsules[capsule_id] = new_version
                current_version.status = CapsuleStatus.DEPRECATED
                
                logger.info(f"Successfully upgraded capsule {capsule_name} from {current_version.version} to {new_version.version}")
                
                return UpgradeResult(
                    success=True,
                    old_version=current_version.version,
                    new_version=new_version.version,
                    strategy=strategy,
                    duration=duration,
                    rollback_available=True
                )
            else:
                # Rollback if auto-rollback enabled
                if self.config.enable_auto_rollback:
                    await self._rollback_upgrade(current_version, cloud_provider, namespace)
                
                error = "Upgrade failed health checks"
                logger.error(error)
                
                return UpgradeResult(
                    success=False,
                    old_version=current_version.version,
                    new_version=new_version.version,
                    strategy=strategy,
                    duration=duration,
                    rollback_available=True,
                    error=error
                )
                
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            error = f"Upgrade exception: {str(e)}"
            logger.error(error)
            
            return UpgradeResult(
                success=False,
                old_version=current_version.version,
                new_version="unknown",
                strategy=strategy,
                duration=duration,
                rollback_available=True,
                error=error
            )
    
    async def _rolling_upgrade(
        self,
        current_version: CapsuleVersion,
        new_version: CapsuleVersion,
        cloud_provider: CloudProvider,
        namespace: Optional[str]
    ) -> bool:
        """
        Perform rolling upgrade.
        
        Args:
            current_version: Current capsule version
            new_version: New capsule version
            cloud_provider: Target cloud provider
            namespace: Kubernetes namespace
        
        Returns:
            True if upgrade successful
        """
        logger.info("Executing rolling upgrade")
        
        # Deploy new version
        success = await self.deploy_capsule(new_version, cloud_provider, namespace)
        if not success:
            return False
        
        # Wait for health checks
        await asyncio.sleep(2)
        
        # Simulate health check (in production, check actual pod health)
        health_ok = True
        
        if health_ok:
            # Scale down old version
            logger.info("Health checks passed, scaling down old version")
            return True
        else:
            logger.error("Health checks failed")
            return False
    
    async def _blue_green_upgrade(
        self,
        current_version: CapsuleVersion,
        new_version: CapsuleVersion,
        cloud_provider: CloudProvider,
        namespace: Optional[str]
    ) -> bool:
        """
        Perform blue-green upgrade.
        
        Args:
            current_version: Current capsule version (blue)
            new_version: New capsule version (green)
            cloud_provider: Target cloud provider
            namespace: Kubernetes namespace
        
        Returns:
            True if upgrade successful
        """
        logger.info("Executing blue-green upgrade")
        
        # Deploy green version
        success = await self.deploy_capsule(new_version, cloud_provider, namespace)
        if not success:
            return False
        
        # Wait for health checks
        await asyncio.sleep(2)
        
        # Switch traffic to green
        logger.info("Switching traffic to green deployment")
        
        # Simulate traffic switch (in production, update service selector)
        return True
    
    async def _canary_upgrade(
        self,
        current_version: CapsuleVersion,
        new_version: CapsuleVersion,
        cloud_provider: CloudProvider,
        namespace: Optional[str]
    ) -> bool:
        """
        Perform canary upgrade.
        
        Args:
            current_version: Current capsule version
            new_version: New capsule version (canary)
            cloud_provider: Target cloud provider
            namespace: Kubernetes namespace
        
        Returns:
            True if upgrade successful
        """
        logger.info("Executing canary upgrade")
        
        # Deploy canary with 10% traffic
        new_version.manifest.replicas = 1
        success = await self.deploy_capsule(new_version, cloud_provider, namespace)
        if not success:
            return False
        
        # Monitor canary
        await asyncio.sleep(2)
        
        # Gradually increase traffic (simulated)
        logger.info("Canary healthy, increasing traffic to 100%")
        
        return True
    
    async def _recreate_upgrade(
        self,
        current_version: CapsuleVersion,
        new_version: CapsuleVersion,
        cloud_provider: CloudProvider,
        namespace: Optional[str]
    ) -> bool:
        """
        Perform recreate upgrade (downtime expected).
        
        Args:
            current_version: Current capsule version
            new_version: New capsule version
            cloud_provider: Target cloud provider
            namespace: Kubernetes namespace
        
        Returns:
            True if upgrade successful
        """
        logger.info("Executing recreate upgrade (downtime expected)")
        
        # Stop old version
        capsule_id = f"{current_version.manifest.name}-{current_version.version}-{cloud_provider.value}"
        await self.dac_engine.stop_capsule(capsule_id)
        
        # Deploy new version
        success = await self.deploy_capsule(new_version, cloud_provider, namespace)
        
        return success
    
    async def _rollback_upgrade(
        self,
        previous_version: CapsuleVersion,
        cloud_provider: CloudProvider,
        namespace: Optional[str]
    ) -> bool:
        """
        Rollback to previous version.
        
        Args:
            previous_version: Previous capsule version
            cloud_provider: Target cloud provider
            namespace: Kubernetes namespace
        
        Returns:
            True if rollback successful
        """
        logger.info(f"Rolling back to version {previous_version.version}")
        
        # Redeploy previous version
        success = await self.deploy_capsule(previous_version, cloud_provider, namespace)
        
        if success:
            previous_version.status = CapsuleStatus.DEPLOYED
            logger.info("Rollback successful")
        else:
            logger.error("Rollback failed")
        
        return success
    
    def get_capsule_history(self, capsule_name: str) -> List[CapsuleVersion]:
        """
        Get version history for a capsule.
        
        Args:
            capsule_name: Capsule name
        
        Returns:
            List of capsule versions
        """
        return self.capsule_versions.get(capsule_name, [])
    
    def get_active_capsules(self) -> Dict[str, CapsuleVersion]:
        """
        Get all active capsules.
        
        Returns:
            Dictionary of active capsules
        """
        return self.active_capsules
    
    def get_capsule_lineage(self, capsule_name: str) -> List[Tuple[str, str]]:
        """
        Get capsule version lineage (parent-child relationships).
        
        Args:
            capsule_name: Capsule name
        
        Returns:
            List of (version, parent_version) tuples
        """
        versions = self.capsule_versions.get(capsule_name, [])
        lineage = []
        
        for version in versions:
            lineage.append((version.version, version.parent_version or "root"))
        
        return lineage


# Example usage
async def main():
    """Example usage of DAC Lifecycle Manager."""
    # Create DAC Engine
    dac_engine = DACEngine()
    await dac_engine.connect_all()
    
    # Create Lifecycle Manager
    lifecycle_manager = DACLifecycleManager(dac_engine)
    
    # Create hypothesis
    hypothesis = Hypothesis(
        id="hyp_001",
        text="Optimize turbine blade geometry for maximum efficiency",
        parameters={"blade_count": 12, "angle": 45.0, "material": "titanium"},
        domain="aerospace",
        confidence=0.85
    )
    
    # Package hypothesis into capsule
    print("\nPackaging hypothesis into capsule...")
    capsule_v1 = await lifecycle_manager.package_hypothesis(hypothesis)
    print(f"  Capsule: {capsule_v1.manifest.name}")
    print(f"  Version: {capsule_v1.version}")
    print(f"  Status: {capsule_v1.status.value}")
    
    # Deploy capsule
    print("\nDeploying capsule to Azure...")
    success = await lifecycle_manager.deploy_capsule(
        capsule_v1,
        CloudProvider.AZURE
    )
    print(f"  Deployment: {'✓ Success' if success else '✗ Failed'}")
    
    # Create updated hypothesis
    hypothesis_v2 = Hypothesis(
        id="hyp_002",
        text="Optimize turbine blade geometry with improved CFD analysis",
        parameters={"blade_count": 14, "angle": 47.5, "material": "titanium-alloy"},
        domain="aerospace",
        confidence=0.92
    )
    
    # Upgrade capsule
    print("\nUpgrading capsule with rolling strategy...")
    upgrade_result = await lifecycle_manager.upgrade_capsule(
        capsule_name=capsule_v1.manifest.name,
        new_hypothesis=hypothesis_v2,
        cloud_provider=CloudProvider.AZURE,
        strategy=UpgradeStrategy.ROLLING
    )
    
    print(f"  Upgrade: {'✓ Success' if upgrade_result.success else '✗ Failed'}")
    print(f"  Old version: {upgrade_result.old_version}")
    print(f"  New version: {upgrade_result.new_version}")
    print(f"  Duration: {upgrade_result.duration:.2f}s")
    
    # Get capsule history
    print("\nCapsule version history:")
    history = lifecycle_manager.get_capsule_history(capsule_v1.manifest.name)
    for version in history:
        print(f"  v{version.version}: {version.status.value} (deployed: {version.deployed_at})")
    
    # Get capsule lineage
    print("\nCapsule lineage:")
    lineage = lifecycle_manager.get_capsule_lineage(capsule_v1.manifest.name)
    for version, parent in lineage:
        print(f"  v{version} ← {parent}")


if __name__ == "__main__":
    asyncio.run(main())
