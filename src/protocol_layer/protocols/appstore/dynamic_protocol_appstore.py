"""
Dynamic Protocol AppStore for Industriverse Protocol Layer

This module implements the Dynamic Protocol AppStore, enabling discovery,
distribution, and management of protocol-native applications and components
within the Industriverse ecosystem.

Features:
1. Protocol app publishing and discovery
2. Version management and dependency resolution
3. Dynamic app loading and instantiation
4. Capability-based app search and recommendation
5. App ratings and reputation tracking
6. Security scanning and verification
"""

import uuid
import time
import asyncio
import logging
import json
import hashlib
import semver
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AppCategory(Enum):
    """Categories for protocol applications."""
    ANALYTICS = "analytics"
    COMMUNICATION = "communication"
    DATA_PROCESSING = "data_processing"
    INTEGRATION = "integration"
    MONITORING = "monitoring"
    SECURITY = "security"
    UTILITY = "utility"
    VISUALIZATION = "visualization"
    WORKFLOW = "workflow"
    OTHER = "other"


class AppStatus(Enum):
    """Status of a protocol application."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"
    REMOVED = "removed"


class VerificationStatus(Enum):
    """Verification status of a protocol application."""
    UNVERIFIED = "unverified"
    PENDING = "pending"
    VERIFIED = "verified"
    FAILED = "failed"


@dataclass
class AppDependency:
    """
    Represents a dependency of a protocol application.
    """
    app_id: str
    version_constraint: str  # Semver constraint (e.g., ">=1.0.0")
    optional: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "app_id": self.app_id,
            "version_constraint": self.version_constraint,
            "optional": self.optional
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppDependency':
        """Create from dictionary representation."""
        return cls(
            app_id=data["app_id"],
            version_constraint=data["version_constraint"],
            optional=data.get("optional", False)
        )


@dataclass
class AppVersion:
    """
    Represents a version of a protocol application.
    """
    version: str  # Semver version
    description: str
    package_url: str
    checksum: str
    dependencies: List[AppDependency] = field(default_factory=list)
    release_notes: str = ""
    release_date: float = field(default_factory=time.time)
    download_count: int = 0
    status: AppStatus = AppStatus.DRAFT
    verification: VerificationStatus = VerificationStatus.UNVERIFIED
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "version": self.version,
            "description": self.description,
            "package_url": self.package_url,
            "checksum": self.checksum,
            "dependencies": [dep.to_dict() for dep in self.dependencies],
            "release_notes": self.release_notes,
            "release_date": self.release_date,
            "download_count": self.download_count,
            "status": self.status.value,
            "verification": self.verification.value,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppVersion':
        """Create from dictionary representation."""
        version = cls(
            version=data["version"],
            description=data["description"],
            package_url=data["package_url"],
            checksum=data["checksum"],
            release_notes=data.get("release_notes", ""),
            release_date=data.get("release_date", time.time()),
            download_count=data.get("download_count", 0),
            status=AppStatus(data.get("status", "draft")),
            verification=VerificationStatus(data.get("verification", "unverified")),
            metadata=data.get("metadata", {})
        )
        for dep_data in data.get("dependencies", []):
            version.dependencies.append(AppDependency.from_dict(dep_data))
        return version


@dataclass
class AppRating:
    """
    Represents a rating for a protocol application.
    """
    user_id: str
    rating: int  # 1-5
    review: str = ""
    version: str = ""
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "user_id": self.user_id,
            "rating": self.rating,
            "review": self.review,
            "version": self.version,
            "timestamp": self.timestamp
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AppRating':
        """Create from dictionary representation."""
        return cls(
            user_id=data["user_id"],
            rating=data["rating"],
            review=data.get("review", ""),
            version=data.get("version", ""),
            timestamp=data.get("timestamp", time.time())
        )


@dataclass
class ProtocolApp:
    """
    Represents a protocol application in the AppStore.
    """
    app_id: str
    name: str
    publisher_id: str
    description: str
    categories: List[AppCategory]
    capabilities: List[str]
    versions: Dict[str, AppVersion] = field(default_factory=dict)
    ratings: List[AppRating] = field(default_factory=list)
    creation_date: float = field(default_factory=time.time)
    update_date: float = field(default_factory=time.time)
    download_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_version(self, version: AppVersion) -> None:
        """Add a version to the app."""
        self.versions[version.version] = version
        self.update_date = time.time()
    
    def add_rating(self, rating: AppRating) -> None:
        """Add a rating to the app."""
        self.ratings.append(rating)
    
    def get_latest_version(self) -> Optional[AppVersion]:
        """Get the latest version of the app."""
        if not self.versions:
            return None
        
        # Filter for published versions
        published_versions = {v: ver for v, ver in self.versions.items() 
                             if ver.status == AppStatus.PUBLISHED}
        
        if not published_versions:
            return None
        
        # Sort by semver and return latest
        latest_version = max(published_versions.keys(), key=lambda v: semver.VersionInfo.parse(v))
        return self.versions[latest_version]
    
    def get_average_rating(self) -> float:
        """Get the average rating of the app."""
        if not self.ratings:
            return 0.0
        
        return sum(r.rating for r in self.ratings) / len(self.ratings)
    
    def to_dict(self, include_versions: bool = True, include_ratings: bool = True) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "app_id": self.app_id,
            "name": self.name,
            "publisher_id": self.publisher_id,
            "description": self.description,
            "categories": [cat.value for cat in self.categories],
            "capabilities": self.capabilities,
            "creation_date": self.creation_date,
            "update_date": self.update_date,
            "download_count": self.download_count,
            "average_rating": self.get_average_rating(),
            "rating_count": len(self.ratings),
            "version_count": len(self.versions),
            "metadata": self.metadata
        }
        
        if include_versions:
            result["versions"] = {v: ver.to_dict() for v, ver in self.versions.items()}
        
        if include_ratings:
            result["ratings"] = [rating.to_dict() for rating in self.ratings]
        
        latest = self.get_latest_version()
        if latest:
            result["latest_version"] = latest.version
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProtocolApp':
        """Create from dictionary representation."""
        app = cls(
            app_id=data["app_id"],
            name=data["name"],
            publisher_id=data["publisher_id"],
            description=data["description"],
            categories=[AppCategory(cat) for cat in data["categories"]],
            capabilities=data["capabilities"],
            creation_date=data.get("creation_date", time.time()),
            update_date=data.get("update_date", time.time()),
            download_count=data.get("download_count", 0),
            metadata=data.get("metadata", {})
        )
        
        # Add versions
        for version_data in data.get("versions", {}).values():
            app.add_version(AppVersion.from_dict(version_data))
        
        # Add ratings
        for rating_data in data.get("ratings", []):
            app.add_rating(AppRating.from_dict(rating_data))
        
        return app


class AppVerifier:
    """
    Verifies protocol applications for security and compatibility.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.AppVerifier")
    
    async def verify_app(self, app: ProtocolApp, version: AppVersion) -> Dict[str, Any]:
        """Verify an app version for security and compatibility."""
        self.logger.info(f"Verifying app {app.app_id} version {version.version}")
        
        # In a real implementation, this would perform various checks:
        # - Download and scan the package for malware
        # - Validate the checksum
        # - Check for known vulnerabilities
        # - Verify compatibility with the protocol layer
        # - etc.
        
        # For this implementation, we'll simulate a verification process
        await asyncio.sleep(1)  # Simulate verification time
        
        # Generate a verification result
        result = {
            "app_id": app.app_id,
            "version": version.version,
            "timestamp": time.time(),
            "status": "verified",  # verified, failed
            "score": 95,  # 0-100
            "issues": []
        }
        
        # Simulate some verification checks
        if "malware" in version.metadata.get("test_flags", []):
            result["status"] = "failed"
            result["score"] = 0
            result["issues"].append({
                "severity": "critical",
                "type": "security",
                "description": "Malware detected in package"
            })
        
        if "vulnerability" in version.metadata.get("test_flags", []):
            result["score"] -= 20
            result["issues"].append({
                "severity": "high",
                "type": "security",
                "description": "Known vulnerability detected"
            })
        
        if "incompatible" in version.metadata.get("test_flags", []):
            result["score"] -= 30
            result["issues"].append({
                "severity": "medium",
                "type": "compatibility",
                "description": "Incompatible with current protocol version"
            })
        
        # Update verification status based on result
        if result["status"] == "verified" and result["score"] >= 70:
            version.verification = VerificationStatus.VERIFIED
        else:
            version.verification = VerificationStatus.FAILED
        
        self.logger.info(f"Verification completed for {app.app_id} v{version.version}: {result['status']} (score: {result['score']})")
        return result


class DependencyResolver:
    """
    Resolves dependencies for protocol applications.
    """
    def __init__(self, app_store: 'DynamicProtocolAppStore'):
        self.app_store = app_store
        self.logger = logging.getLogger(f"{__name__}.DependencyResolver")
    
    async def resolve_dependencies(self, app_id: str, version: str) -> Dict[str, Any]:
        """Resolve dependencies for an app version."""
        self.logger.info(f"Resolving dependencies for {app_id} v{version}")
        
        # Get the app and version
        app = await self.app_store.get_app(app_id)
        if not app:
            self.logger.error(f"App {app_id} not found")
            return {"success": False, "error": "App not found"}
        
        if version not in app.versions:
            self.logger.error(f"Version {version} not found for app {app_id}")
            return {"success": False, "error": "Version not found"}
        
        app_version = app.versions[version]
        
        # Resolve dependencies
        resolved = {}
        unresolved = []
        
        for dep in app_version.dependencies:
            dep_app = await self.app_store.get_app(dep.app_id)
            if not dep_app:
                if dep.optional:
                    self.logger.warning(f"Optional dependency {dep.app_id} not found")
                    continue
                else:
                    self.logger.error(f"Required dependency {dep.app_id} not found")
                    unresolved.append({
                        "app_id": dep.app_id,
                        "constraint": dep.version_constraint,
                        "error": "App not found"
                    })
                    continue
            
            # Find a version that satisfies the constraint
            satisfied_version = None
            for ver_str, ver_obj in dep_app.versions.items():
                if ver_obj.status != AppStatus.PUBLISHED:
                    continue
                
                if self._satisfies_constraint(ver_str, dep.version_constraint):
                    if satisfied_version is None or semver.VersionInfo.parse(ver_str) > semver.VersionInfo.parse(satisfied_version):
                        satisfied_version = ver_str
            
            if satisfied_version:
                resolved[dep.app_id] = {
                    "version": satisfied_version,
                    "optional": dep.optional
                }
                
                # Recursively resolve dependencies of this dependency
                sub_result = await self.resolve_dependencies(dep.app_id, satisfied_version)
                if sub_result["success"]:
                    resolved[dep.app_id]["dependencies"] = sub_result["resolved"]
                else:
                    if dep.optional:
                        self.logger.warning(f"Failed to resolve dependencies for optional dependency {dep.app_id}")
                        del resolved[dep.app_id]
                    else:
                        self.logger.error(f"Failed to resolve dependencies for required dependency {dep.app_id}")
                        unresolved.append({
                            "app_id": dep.app_id,
                            "constraint": dep.version_constraint,
                            "error": "Dependency resolution failed",
                            "details": sub_result["unresolved"]
                        })
            else:
                if dep.optional:
                    self.logger.warning(f"No version of {dep.app_id} satisfies constraint {dep.version_constraint}")
                else:
                    self.logger.error(f"No version of {dep.app_id} satisfies constraint {dep.version_constraint}")
                    unresolved.append({
                        "app_id": dep.app_id,
                        "constraint": dep.version_constraint,
                        "error": "No satisfying version found"
                    })
        
        # Return the resolution result
        if not unresolved:
            self.logger.info(f"Successfully resolved all dependencies for {app_id} v{version}")
            return {
                "success": True,
                "resolved": resolved,
                "unresolved": []
            }
        else:
            self.logger.warning(f"Failed to resolve some dependencies for {app_id} v{version}")
            return {
                "success": False,
                "resolved": resolved,
                "unresolved": unresolved
            }
    
    def _satisfies_constraint(self, version: str, constraint: str) -> bool:
        """Check if a version satisfies a constraint."""
        try:
            return semver.match(version, constraint)
        except ValueError:
            self.logger.error(f"Invalid version or constraint: {version}, {constraint}")
            return False


class DynamicProtocolAppStore(ProtocolService):
    """
    Service for managing the Dynamic Protocol AppStore.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "dynamic_protocol_appstore")
        self.config = config or {}
        
        # Initialize apps
        self.apps: Dict[str, ProtocolApp] = {}
        
        # Initialize verifier
        self.verifier = AppVerifier(self.config.get("verifier", {}))
        
        # Initialize dependency resolver
        self.dependency_resolver = DependencyResolver(self)
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.DynamicProtocolAppStore.{self.component_id[:8]}")
        self.logger.info(f"Dynamic Protocol AppStore initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("app_publishing", "Publish protocol applications")
        self.add_capability("app_discovery", "Discover protocol applications")
        self.add_capability("version_management", "Manage application versions")
        self.add_capability("dependency_resolution", "Resolve application dependencies")
        self.add_capability("app_verification", "Verify application security and compatibility")

    # --- App Management ---

    async def register_app(self, app_data: Dict[str, Any]) -> str:
        """Register a new protocol application."""
        app_id = app_data.get("app_id", str(uuid.uuid4()))
        
        async with self.lock:
            if app_id in self.apps:
                self.logger.warning(f"App {app_id} already registered")
                return app_id
            
            # Create app
            app = ProtocolApp(
                app_id=app_id,
                name=app_data["name"],
                publisher_id=app_data["publisher_id"],
                description=app_data["description"],
                categories=[AppCategory(cat) for cat in app_data.get("categories", ["other"])],
                capabilities=app_data.get("capabilities", []),
                metadata=app_data.get("metadata", {})
            )
            
            self.apps[app_id] = app
            self.logger.info(f"Registered app {app_id} ({app.name}) by publisher {app.publisher_id}")
        
        # Publish app registration event
        await self._publish_appstore_event("app_registered", {
            "app_id": app_id,
            "name": app.name,
            "publisher_id": app.publisher_id
        })
        
        return app_id

    async def update_app(self, app_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return False
            
            app = self.apps[app_id]
            
            # Update basic properties
            if "name" in updates:
                app.name = updates["name"]
            
            if "description" in updates:
                app.description = updates["description"]
            
            if "categories" in updates:
                app.categories = [AppCategory(cat) for cat in updates["categories"]]
            
            if "capabilities" in updates:
                app.capabilities = updates["capabilities"]
            
            if "metadata" in updates:
                app.metadata.update(updates["metadata"])
            
            app.update_date = time.time()
            self.logger.info(f"Updated app {app_id}")
        
        # Publish app update event
        await self._publish_appstore_event("app_updated", {
            "app_id": app_id,
            "name": app.name
        })
        
        return True

    async def add_app_version(self, app_id: str, version_data: Dict[str, Any]) -> Optional[str]:
        """Add a version to an existing protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return None
            
            app = self.apps[app_id]
            version_str = version_data["version"]
            
            # Check if version already exists
            if version_str in app.versions:
                self.logger.warning(f"Version {version_str} already exists for app {app_id}")
                return version_str
            
            # Create version
            version = AppVersion(
                version=version_str,
                description=version_data["description"],
                package_url=version_data["package_url"],
                checksum=version_data["checksum"],
                release_notes=version_data.get("release_notes", ""),
                status=AppStatus(version_data.get("status", "draft")),
                metadata=version_data.get("metadata", {})
            )
            
            # Add dependencies
            for dep_data in version_data.get("dependencies", []):
                version.dependencies.append(AppDependency.from_dict(dep_data))
            
            app.add_version(version)
            self.logger.info(f"Added version {version_str} to app {app_id}")
        
        # Publish version added event
        await self._publish_appstore_event("version_added", {
            "app_id": app_id,
            "version": version_str
        })
        
        # If version is submitted for verification, start verification process
        if version.status == AppStatus.SUBMITTED:
            await self.verify_app_version(app_id, version_str)
        
        return version_str

    async def update_app_version(self, app_id: str, version_str: str, updates: Dict[str, Any]) -> bool:
        """Update a version of an existing protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return False
            
            app = self.apps[app_id]
            
            if version_str not in app.versions:
                self.logger.error(f"Version {version_str} not found for app {app_id}")
                return False
            
            version = app.versions[version_str]
            
            # Only allow updates to draft versions
            if version.status != AppStatus.DRAFT and "status" not in updates:
                self.logger.warning(f"Cannot update non-draft version {version_str} of app {app_id}")
                return False
            
            # Update version properties
            if "description" in updates:
                version.description = updates["description"]
            
            if "package_url" in updates:
                version.package_url = updates["package_url"]
            
            if "checksum" in updates:
                version.checksum = updates["checksum"]
            
            if "release_notes" in updates:
                version.release_notes = updates["release_notes"]
            
            if "status" in updates:
                version.status = AppStatus(updates["status"])
            
            if "metadata" in updates:
                version.metadata.update(updates["metadata"])
            
            if "dependencies" in updates:
                version.dependencies = []
                for dep_data in updates["dependencies"]:
                    version.dependencies.append(AppDependency.from_dict(dep_data))
            
            app.update_date = time.time()
            self.logger.info(f"Updated version {version_str} of app {app_id}")
        
        # Publish version updated event
        await self._publish_appstore_event("version_updated", {
            "app_id": app_id,
            "version": version_str
        })
        
        # If version is submitted for verification, start verification process
        if version.status == AppStatus.SUBMITTED:
            await self.verify_app_version(app_id, version_str)
        
        return True

    async def publish_app_version(self, app_id: str, version_str: str) -> bool:
        """Publish a version of a protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return False
            
            app = self.apps[app_id]
            
            if version_str not in app.versions:
                self.logger.error(f"Version {version_str} not found for app {app_id}")
                return False
            
            version = app.versions[version_str]
            
            # Only allow publishing of verified versions
            if version.verification != VerificationStatus.VERIFIED:
                self.logger.warning(f"Cannot publish unverified version {version_str} of app {app_id}")
                return False
            
            # Update status
            version.status = AppStatus.PUBLISHED
            app.update_date = time.time()
            self.logger.info(f"Published version {version_str} of app {app_id}")
        
        # Publish version published event
        await self._publish_appstore_event("version_published", {
            "app_id": app_id,
            "version": version_str
        })
        
        return True

    async def deprecate_app_version(self, app_id: str, version_str: str) -> bool:
        """Deprecate a version of a protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return False
            
            app = self.apps[app_id]
            
            if version_str not in app.versions:
                self.logger.error(f"Version {version_str} not found for app {app_id}")
                return False
            
            version = app.versions[version_str]
            
            # Only allow deprecating of published versions
            if version.status != AppStatus.PUBLISHED:
                self.logger.warning(f"Cannot deprecate non-published version {version_str} of app {app_id}")
                return False
            
            # Update status
            version.status = AppStatus.DEPRECATED
            app.update_date = time.time()
            self.logger.info(f"Deprecated version {version_str} of app {app_id}")
        
        # Publish version deprecated event
        await self._publish_appstore_event("version_deprecated", {
            "app_id": app_id,
            "version": version_str
        })
        
        return True

    async def remove_app_version(self, app_id: str, version_str: str) -> bool:
        """Remove a version of a protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return False
            
            app = self.apps[app_id]
            
            if version_str not in app.versions:
                self.logger.error(f"Version {version_str} not found for app {app_id}")
                return False
            
            version = app.versions[version_str]
            
            # Update status
            version.status = AppStatus.REMOVED
            app.update_date = time.time()
            self.logger.info(f"Removed version {version_str} of app {app_id}")
        
        # Publish version removed event
        await self._publish_appstore_event("version_removed", {
            "app_id": app_id,
            "version": version_str
        })
        
        return True

    async def add_app_rating(self, app_id: str, rating_data: Dict[str, Any]) -> bool:
        """Add a rating to a protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return False
            
            app = self.apps[app_id]
            
            # Create rating
            rating = AppRating(
                user_id=rating_data["user_id"],
                rating=rating_data["rating"],
                review=rating_data.get("review", ""),
                version=rating_data.get("version", ""),
                timestamp=rating_data.get("timestamp", time.time())
            )
            
            # Validate rating
            if rating.rating < 1 or rating.rating > 5:
                self.logger.error(f"Invalid rating value: {rating.rating}")
                return False
            
            # Check if user already rated this app
            for existing_rating in app.ratings:
                if existing_rating.user_id == rating.user_id:
                    # Update existing rating
                    existing_rating.rating = rating.rating
                    existing_rating.review = rating.review
                    existing_rating.version = rating.version
                    existing_rating.timestamp = rating.timestamp
                    self.logger.info(f"Updated rating for app {app_id} by user {rating.user_id}")
                    
                    # Publish rating updated event
                    await self._publish_appstore_event("rating_updated", {
                        "app_id": app_id,
                        "user_id": rating.user_id,
                        "rating": rating.rating
                    })
                    
                    return True
            
            # Add new rating
            app.add_rating(rating)
            self.logger.info(f"Added rating for app {app_id} by user {rating.user_id}")
        
        # Publish rating added event
        await self._publish_appstore_event("rating_added", {
            "app_id": app_id,
            "user_id": rating.user_id,
            "rating": rating.rating
        })
        
        return True

    async def get_app(self, app_id: str) -> Optional[ProtocolApp]:
        """Get a protocol application by ID."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return None
            
            return self.apps[app_id]

    async def get_app_dict(self, app_id: str, include_versions: bool = True, include_ratings: bool = True) -> Optional[Dict[str, Any]]:
        """Get a protocol application by ID as a dictionary."""
        app = await self.get_app(app_id)
        if not app:
            return None
        
        return app.to_dict(include_versions=include_versions, include_ratings=include_ratings)

    async def list_apps(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List protocol applications with optional filtering."""
        filters = filters or {}
        
        async with self.lock:
            apps = list(self.apps.values())
        
        # Apply filters
        if "publisher_id" in filters:
            publisher_id = filters["publisher_id"]
            apps = [app for app in apps if app.publisher_id == publisher_id]
        
        if "category" in filters:
            category = AppCategory(filters["category"])
            apps = [app for app in apps if category in app.categories]
        
        if "capability" in filters:
            capability = filters["capability"]
            apps = [app for app in apps if capability in app.capabilities]
        
        if "min_rating" in filters:
            min_rating = float(filters["min_rating"])
            apps = [app for app in apps if app.get_average_rating() >= min_rating]
        
        # Sort by specified field
        sort_by = filters.get("sort_by", "name")
        reverse = filters.get("reverse", False)
        
        if sort_by == "name":
            apps.sort(key=lambda app: app.name, reverse=reverse)
        elif sort_by == "rating":
            apps.sort(key=lambda app: app.get_average_rating(), reverse=reverse)
        elif sort_by == "downloads":
            apps.sort(key=lambda app: app.download_count, reverse=reverse)
        elif sort_by == "update_date":
            apps.sort(key=lambda app: app.update_date, reverse=reverse)
        
        # Convert to dict representation (without versions and ratings for brevity)
        return [app.to_dict(include_versions=False, include_ratings=False) for app in apps]

    # --- App Verification ---

    async def verify_app_version(self, app_id: str, version_str: str) -> Dict[str, Any]:
        """Verify a version of a protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return {"success": False, "error": "App not found"}
            
            app = self.apps[app_id]
            
            if version_str not in app.versions:
                self.logger.error(f"Version {version_str} not found for app {app_id}")
                return {"success": False, "error": "Version not found"}
            
            version = app.versions[version_str]
            
            # Update verification status
            version.verification = VerificationStatus.PENDING
            self.logger.info(f"Started verification for app {app_id} version {version_str}")
        
        # Publish verification started event
        await self._publish_appstore_event("verification_started", {
            "app_id": app_id,
            "version": version_str
        })
        
        # Perform verification
        result = await self.verifier.verify_app(app, version)
        
        # Update verification status based on result
        async with self.lock:
            if app_id in self.apps and version_str in self.apps[app_id].versions:
                version = self.apps[app_id].versions[version_str]
                if result["status"] == "verified":
                    version.verification = VerificationStatus.VERIFIED
                    self.logger.info(f"Verification succeeded for app {app_id} version {version_str}")
                else:
                    version.verification = VerificationStatus.FAILED
                    self.logger.warning(f"Verification failed for app {app_id} version {version_str}")
        
        # Publish verification completed event
        await self._publish_appstore_event("verification_completed", {
            "app_id": app_id,
            "version": version_str,
            "status": result["status"],
            "score": result["score"]
        })
        
        return result

    # --- App Installation and Dependency Resolution ---

    async def download_app(self, app_id: str, version_str: str = None) -> Dict[str, Any]:
        """Download a protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return {"success": False, "error": "App not found"}
            
            app = self.apps[app_id]
            
            # If version not specified, use latest
            if not version_str:
                latest = app.get_latest_version()
                if not latest:
                    self.logger.error(f"No published versions found for app {app_id}")
                    return {"success": False, "error": "No published versions found"}
                version_str = latest.version
            
            if version_str not in app.versions:
                self.logger.error(f"Version {version_str} not found for app {app_id}")
                return {"success": False, "error": "Version not found"}
            
            version = app.versions[version_str]
            
            # Check if version is published
            if version.status != AppStatus.PUBLISHED:
                self.logger.error(f"Version {version_str} of app {app_id} is not published")
                return {"success": False, "error": "Version not published"}
            
            # Update download count
            version.download_count += 1
            app.download_count += 1
            self.logger.info(f"Downloaded app {app_id} version {version_str}")
        
        # Publish download event
        await self._publish_appstore_event("app_downloaded", {
            "app_id": app_id,
            "version": version_str
        })
        
        # Return download info
        return {
            "success": True,
            "app_id": app_id,
            "name": app.name,
            "version": version_str,
            "package_url": version.package_url,
            "checksum": version.checksum
        }

    async def resolve_dependencies(self, app_id: str, version_str: str = None) -> Dict[str, Any]:
        """Resolve dependencies for a protocol application."""
        async with self.lock:
            if app_id not in self.apps:
                self.logger.error(f"App {app_id} not found")
                return {"success": False, "error": "App not found"}
            
            app = self.apps[app_id]
            
            # If version not specified, use latest
            if not version_str:
                latest = app.get_latest_version()
                if not latest:
                    self.logger.error(f"No published versions found for app {app_id}")
                    return {"success": False, "error": "No published versions found"}
                version_str = latest.version
            
            if version_str not in app.versions:
                self.logger.error(f"Version {version_str} not found for app {app_id}")
                return {"success": False, "error": "Version not found"}
        
        # Resolve dependencies
        result = await self.dependency_resolver.resolve_dependencies(app_id, version_str)
        
        self.logger.info(f"Resolved dependencies for app {app_id} version {version_str}: {result['success']}")
        return result

    # --- Event Publishing ---

    async def _publish_appstore_event(self, event_type: str, data: Dict[str, Any] = None) -> None:
        """Publish an appstore-related event."""
        data = data or {}
        
        # Create event message
        event = {
            "event_type": f"appstore.{event_type}",
            "timestamp": time.time(),
            "data": data
        }
        
        # In a real implementation, this would publish to an event bus or message broker
        self.logger.debug(f"Published appstore event: {event_type}")

    # --- ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "register_app":
                app_id = await self.register_app(msg_obj.params)
                response_payload = {"app_id": app_id}
            
            elif msg_obj.command == "update_app":
                params = msg_obj.params
                if "app_id" in params and "updates" in params:
                    success = await self.update_app(params["app_id"], params["updates"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or updates"}
            
            elif msg_obj.command == "add_app_version":
                params = msg_obj.params
                if "app_id" in params and "version" in params:
                    version_str = await self.add_app_version(params["app_id"], params["version"])
                    if version_str:
                        response_payload = {"version": version_str}
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Failed to add version"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or version"}
            
            elif msg_obj.command == "update_app_version":
                params = msg_obj.params
                if "app_id" in params and "version" in params and "updates" in params:
                    success = await self.update_app_version(params["app_id"], params["version"], params["updates"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id, version, or updates"}
            
            elif msg_obj.command == "publish_app_version":
                params = msg_obj.params
                if "app_id" in params and "version" in params:
                    success = await self.publish_app_version(params["app_id"], params["version"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or version"}
            
            elif msg_obj.command == "deprecate_app_version":
                params = msg_obj.params
                if "app_id" in params and "version" in params:
                    success = await self.deprecate_app_version(params["app_id"], params["version"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or version"}
            
            elif msg_obj.command == "remove_app_version":
                params = msg_obj.params
                if "app_id" in params and "version" in params:
                    success = await self.remove_app_version(params["app_id"], params["version"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or version"}
            
            elif msg_obj.command == "add_app_rating":
                params = msg_obj.params
                if "app_id" in params and "rating" in params:
                    success = await self.add_app_rating(params["app_id"], params["rating"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or rating"}
            
            elif msg_obj.command == "verify_app_version":
                params = msg_obj.params
                if "app_id" in params and "version" in params:
                    result = await self.verify_app_version(params["app_id"], params["version"])
                    response_payload = result
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id or version"}
            
            elif msg_obj.command == "download_app":
                params = msg_obj.params
                if "app_id" in params:
                    result = await self.download_app(params["app_id"], params.get("version"))
                    if result["success"]:
                        response_payload = result
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": result["error"]}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id"}
            
            elif msg_obj.command == "resolve_dependencies":
                params = msg_obj.params
                if "app_id" in params:
                    result = await self.resolve_dependencies(params["app_id"], params.get("version"))
                    if result["success"]:
                        response_payload = result
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Dependency resolution failed", "details": result}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_app":
                params = msg_obj.params
                if "app_id" in params:
                    app = await self.get_app_dict(
                        params["app_id"],
                        include_versions=params.get("include_versions", True),
                        include_ratings=params.get("include_ratings", True)
                    )
                    if app:
                        response_payload = app
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "App not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing app_id"}
            
            elif msg_obj.query == "list_apps":
                apps = await self.list_apps(msg_obj.params.get("filters"))
                response_payload = {"apps": apps}
            
            elif msg_obj.query == "get_app_categories":
                response_payload = {
                    "categories": [cat.value for cat in AppCategory]
                }
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        else:
            # Ignore other message types
            return None

        # Create response
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message (synchronous wrapper)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        async with self.lock:
            num_apps = len(self.apps)
            num_versions = sum(len(app.versions) for app in self.apps.values())
            num_published = sum(
                sum(1 for v in app.versions.values() if v.status == AppStatus.PUBLISHED)
                for app in self.apps.values()
            )
            num_ratings = sum(len(app.ratings) for app in self.apps.values())
        
        return {
            "status": "healthy",
            "apps": {
                "total": num_apps,
                "versions": num_versions,
                "published": num_published,
                "ratings": num_ratings
            }
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
