"""
DAC Registry

Versioned registry for Deploy Anywhere Capsules.
Manages DAC lifecycle, versioning, and distribution.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import json
import hashlib
from .manifest_schema import DACManifest, ManifestValidator


@dataclass
class DACVersion:
    """DAC version information"""
    version: str
    manifest: DACManifest
    checksum: str
    created_at: datetime
    deprecated: bool = False
    deprecation_reason: Optional[str] = None


@dataclass
class DACPackage:
    """Complete DAC package with versioning"""
    dac_id: str
    name: str
    partner_id: str
    tier: str
    description: str
    versions: List[DACVersion] = field(default_factory=list)
    latest_version: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    total_deployments: int = 0
    active_deployments: int = 0

    def get_version(self, version: str) -> Optional[DACVersion]:
        """Get specific version"""
        for v in self.versions:
            if v.version == version:
                return v
        return None

    def get_latest(self) -> Optional[DACVersion]:
        """Get latest non-deprecated version"""
        if not self.versions:
            return None

        # Find latest non-deprecated
        for v in sorted(self.versions, key=lambda x: x.created_at, reverse=True):
            if not v.deprecated:
                return v

        # If all deprecated, return latest
        return sorted(self.versions, key=lambda x: x.created_at, reverse=True)[0]

    def add_version(self, manifest: DACManifest) -> DACVersion:
        """Add new version"""
        # Calculate checksum
        manifest_yaml = manifest.to_yaml()
        checksum = hashlib.sha256(manifest_yaml.encode()).hexdigest()

        # Check for duplicate
        for v in self.versions:
            if v.checksum == checksum:
                raise ValueError(f"Version with identical manifest already exists: {v.version}")

        version = DACVersion(
            version=manifest.version,
            manifest=manifest,
            checksum=checksum,
            created_at=datetime.now()
        )

        self.versions.append(version)
        self.latest_version = manifest.version
        self.updated_at = datetime.now()

        return version

    def deprecate_version(self, version: str, reason: str):
        """Deprecate a version"""
        v = self.get_version(version)
        if not v:
            raise ValueError(f"Version {version} not found")

        v.deprecated = True
        v.deprecation_reason = reason
        self.updated_at = datetime.now()

        # Update latest if we deprecated it
        if self.latest_version == version:
            latest = self.get_latest()
            self.latest_version = latest.version if latest else None


class DACRegistry:
    """
    Central registry for all DAC packages

    Responsibilities:
    - Version management
    - Package distribution
    - Deployment tracking
    - Manifest validation
    - Partner access control
    """

    def __init__(self, storage_path: Optional[Path] = None):
        self.packages: Dict[str, DACPackage] = {}
        self.storage_path = storage_path or Path("./dac_registry")
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def register(self, manifest: DACManifest) -> DACPackage:
        """
        Register a new DAC or add version to existing

        Returns:
            DACPackage with new version added
        """
        # Validate manifest first
        is_valid, errors = ManifestValidator.validate(manifest)
        if not is_valid:
            raise ValueError(f"Invalid manifest: {', '.join(errors)}")

        dac_id = f"{manifest.partner_id}:{manifest.name}"

        if dac_id in self.packages:
            # Add new version to existing package
            package = self.packages[dac_id]
            package.add_version(manifest)
        else:
            # Create new package
            package = DACPackage(
                dac_id=dac_id,
                name=manifest.name,
                partner_id=manifest.partner_id,
                tier=manifest.tier,
                description=manifest.description
            )
            package.add_version(manifest)
            self.packages[dac_id] = package

        self._save_package(package)
        return package

    def get_package(self, dac_id: str) -> Optional[DACPackage]:
        """Get DAC package by ID"""
        return self.packages.get(dac_id)

    def get_by_partner(self, partner_id: str) -> List[DACPackage]:
        """Get all DACs for a partner"""
        return [p for p in self.packages.values() if p.partner_id == partner_id]

    def get_by_tier(self, tier: str) -> List[DACPackage]:
        """Get all DACs for a tier"""
        return [p for p in self.packages.values() if p.tier == tier]

    def search(self, query: str) -> List[DACPackage]:
        """Search packages by name or description"""
        results = []
        query_lower = query.lower()

        for package in self.packages.values():
            if (query_lower in package.name.lower() or
                query_lower in package.description.lower() or
                query_lower in package.partner_id.lower()):
                results.append(package)

        return results

    def list_packages(self) -> List[DACPackage]:
        """List all packages"""
        return list(self.packages.values())

    def deprecate_package(self, dac_id: str, version: str, reason: str):
        """Deprecate a specific version"""
        package = self.get_package(dac_id)
        if not package:
            raise ValueError(f"Package {dac_id} not found")

        package.deprecate_version(version, reason)
        self._save_package(package)

    def record_deployment(self, dac_id: str, version: str):
        """Record a deployment of a DAC"""
        package = self.get_package(dac_id)
        if not package:
            raise ValueError(f"Package {dac_id} not found")

        package.total_deployments += 1
        package.active_deployments += 1
        self._save_package(package)

    def record_undeployment(self, dac_id: str):
        """Record removal of a deployment"""
        package = self.get_package(dac_id)
        if not package:
            raise ValueError(f"Package {dac_id} not found")

        package.active_deployments = max(0, package.active_deployments - 1)
        self._save_package(package)

    def get_manifest(self, dac_id: str, version: Optional[str] = None) -> Optional[DACManifest]:
        """Get manifest for specific version or latest"""
        package = self.get_package(dac_id)
        if not package:
            return None

        if version:
            dac_version = package.get_version(version)
        else:
            dac_version = package.get_latest()

        return dac_version.manifest if dac_version else None

    def export_manifest(self, dac_id: str, version: Optional[str] = None, output_path: Optional[Path] = None) -> Path:
        """Export manifest to YAML file"""
        manifest = self.get_manifest(dac_id, version)
        if not manifest:
            raise ValueError(f"Manifest not found for {dac_id}:{version}")

        if not output_path:
            output_path = self.storage_path / f"{dac_id.replace(':', '_')}_{manifest.version}.yaml"

        manifest.save(output_path)
        return output_path

    def _save_package(self, package: DACPackage):
        """Persist package to storage"""
        package_dir = self.storage_path / package.dac_id.replace(':', '_')
        package_dir.mkdir(parents=True, exist_ok=True)

        # Save package metadata
        metadata = {
            'dac_id': package.dac_id,
            'name': package.name,
            'partner_id': package.partner_id,
            'tier': package.tier,
            'description': package.description,
            'latest_version': package.latest_version,
            'created_at': package.created_at.isoformat(),
            'updated_at': package.updated_at.isoformat(),
            'total_deployments': package.total_deployments,
            'active_deployments': package.active_deployments,
            'versions': [
                {
                    'version': v.version,
                    'checksum': v.checksum,
                    'created_at': v.created_at.isoformat(),
                    'deprecated': v.deprecated,
                    'deprecation_reason': v.deprecation_reason,
                }
                for v in package.versions
            ]
        }

        metadata_path = package_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Save each manifest version
        for version in package.versions:
            manifest_path = package_dir / f"{version.version}.yaml"
            version.manifest.save(manifest_path)

    def _load_package(self, dac_id: str) -> Optional[DACPackage]:
        """Load package from storage"""
        package_dir = self.storage_path / dac_id.replace(':', '_')
        metadata_path = package_dir / 'metadata.json'

        if not metadata_path.exists():
            return None

        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        package = DACPackage(
            dac_id=metadata['dac_id'],
            name=metadata['name'],
            partner_id=metadata['partner_id'],
            tier=metadata['tier'],
            description=metadata['description'],
            latest_version=metadata['latest_version'],
            created_at=datetime.fromisoformat(metadata['created_at']),
            updated_at=datetime.fromisoformat(metadata['updated_at']),
            total_deployments=metadata['total_deployments'],
            active_deployments=metadata['active_deployments']
        )

        # Load versions
        for v_meta in metadata['versions']:
            manifest_path = package_dir / f"{v_meta['version']}.yaml"
            manifest = DACManifest.from_file(manifest_path)

            version = DACVersion(
                version=v_meta['version'],
                manifest=manifest,
                checksum=v_meta['checksum'],
                created_at=datetime.fromisoformat(v_meta['created_at']),
                deprecated=v_meta['deprecated'],
                deprecation_reason=v_meta.get('deprecation_reason')
            )
            package.versions.append(version)

        return package

    def load_registry(self):
        """Load all packages from storage"""
        if not self.storage_path.exists():
            return

        for package_dir in self.storage_path.iterdir():
            if package_dir.is_dir():
                metadata_path = package_dir / 'metadata.json'
                if metadata_path.exists():
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                        dac_id = metadata['dac_id']
                        package = self._load_package(dac_id)
                        if package:
                            self.packages[dac_id] = package

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        total_packages = len(self.packages)
        total_versions = sum(len(p.versions) for p in self.packages.values())
        total_deployments = sum(p.total_deployments for p in self.packages.values())
        active_deployments = sum(p.active_deployments for p in self.packages.values())

        tier_distribution = {}
        for package in self.packages.values():
            tier_distribution[package.tier] = tier_distribution.get(package.tier, 0) + 1

        partner_count = len(set(p.partner_id for p in self.packages.values()))

        return {
            'total_packages': total_packages,
            'total_versions': total_versions,
            'total_deployments': total_deployments,
            'active_deployments': active_deployments,
            'tier_distribution': tier_distribution,
            'unique_partners': partner_count
        }


# Global registry instance
_registry: Optional[DACRegistry] = None


def get_dac_registry(storage_path: Optional[Path] = None) -> DACRegistry:
    """Get or create global DAC registry"""
    global _registry
    if _registry is None:
        _registry = DACRegistry(storage_path)
        _registry.load_registry()
    return _registry
