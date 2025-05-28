"""
Capsule Blueprint Manager

This module manages capsule blueprints for different use cases. It provides functionality
for retrieving, storing, and versioning blueprints that are used to create capsules.

Blueprints define the structure, behavior, and requirements of capsules, serving as
templates that the Capsule Instantiator Agent uses to create actual capsule instances.
"""

import logging
import json
import os
from typing import Dict, List, Optional, Any, Tuple

logger = logging.getLogger(__name__)

class CapsuleBlueprintManager:
    """
    Manager for capsule blueprints.
    """
    
    def __init__(self, blueprint_repository_path: Optional[str] = None):
        """
        Initialize the Capsule Blueprint Manager.
        
        Args:
            blueprint_repository_path: Path to the blueprint repository
        """
        self.blueprint_repository_path = blueprint_repository_path or os.environ.get(
            "BLUEPRINT_REPOSITORY_PATH", "/var/lib/industriverse/blueprints"
        )
        self.blueprints_cache = {}
        self.blueprint_metadata = {}
        logger.info(f"Capsule Blueprint Manager initialized with repository path: {self.blueprint_repository_path}")
    
    def get_blueprint(self, blueprint_type: str, version: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a blueprint by type and version.
        
        Args:
            blueprint_type: Type of blueprint to retrieve
            version: Version of blueprint to retrieve (latest if None)
            
        Returns:
            Blueprint as a dictionary
        """
        logger.info(f"Getting blueprint of type {blueprint_type}, version {version or 'latest'}")
        
        # Check cache first
        cache_key = f"{blueprint_type}:{version or 'latest'}"
        if cache_key in self.blueprints_cache:
            logger.debug(f"Blueprint {cache_key} found in cache")
            return self.blueprints_cache[cache_key]
        
        # If version is None, get the latest version
        if version is None:
            version = self._get_latest_version(blueprint_type)
            logger.debug(f"Using latest version {version} for blueprint type {blueprint_type}")
        
        # Load blueprint from repository
        blueprint = self._load_blueprint(blueprint_type, version)
        
        # Cache the blueprint
        self.blueprints_cache[cache_key] = blueprint
        
        return blueprint
    
    def list_blueprints(self, filter_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List available blueprints, optionally filtered by criteria.
        
        Args:
            filter_criteria: Criteria to filter blueprints by
            
        Returns:
            List of blueprint metadata
        """
        logger.info(f"Listing blueprints with filter: {filter_criteria}")
        
        # Load metadata if not already loaded
        if not self.blueprint_metadata:
            self._load_blueprint_metadata()
        
        # Apply filters if provided
        if filter_criteria:
            return [
                metadata for metadata in self.blueprint_metadata.values()
                if self._matches_criteria(metadata, filter_criteria)
            ]
        
        return list(self.blueprint_metadata.values())
    
    def store_blueprint(self, blueprint: Dict[str, Any], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store a blueprint in the repository.
        
        Args:
            blueprint: Blueprint to store
            metadata: Metadata for the blueprint
            
        Returns:
            Result of the storage operation
        """
        blueprint_type = metadata.get("type")
        version = metadata.get("version")
        
        if not blueprint_type or not version:
            raise ValueError("Blueprint metadata must include type and version")
        
        logger.info(f"Storing blueprint of type {blueprint_type}, version {version}")
        
        # Ensure blueprint directory exists
        blueprint_dir = os.path.join(self.blueprint_repository_path, blueprint_type)
        os.makedirs(blueprint_dir, exist_ok=True)
        
        # Write blueprint file
        blueprint_path = os.path.join(blueprint_dir, f"{version}.json")
        with open(blueprint_path, 'w') as f:
            json.dump(blueprint, f, indent=2)
        
        # Update metadata
        metadata_path = os.path.join(blueprint_dir, "metadata.json")
        existing_metadata = []
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                existing_metadata = json.load(f)
        
        # Add or update metadata
        updated = False
        for i, item in enumerate(existing_metadata):
            if item.get("version") == version:
                existing_metadata[i] = metadata
                updated = True
                break
        
        if not updated:
            existing_metadata.append(metadata)
        
        # Write updated metadata
        with open(metadata_path, 'w') as f:
            json.dump(existing_metadata, f, indent=2)
        
        # Update cache
        cache_key = f"{blueprint_type}:{version}"
        self.blueprints_cache[cache_key] = blueprint
        self.blueprint_metadata[cache_key] = metadata
        
        return {
            "success": True,
            "blueprint_type": blueprint_type,
            "version": version,
            "path": blueprint_path
        }
    
    def validate_blueprint(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a blueprint against schema and best practices.
        
        Args:
            blueprint: Blueprint to validate
            
        Returns:
            Validation result
        """
        logger.info("Validating blueprint")
        
        # Basic validation
        required_fields = ["name", "version", "components", "requirements"]
        missing_fields = [field for field in required_fields if field not in blueprint]
        
        if missing_fields:
            return {
                "valid": False,
                "errors": [f"Missing required fields: {', '.join(missing_fields)}"]
            }
        
        # Additional validation logic would go here
        
        return {
            "valid": True
        }
    
    def _load_blueprint(self, blueprint_type: str, version: str) -> Dict[str, Any]:
        """
        Load a blueprint from the repository.
        
        Args:
            blueprint_type: Type of blueprint to load
            version: Version of blueprint to load
            
        Returns:
            Blueprint as a dictionary
        """
        blueprint_path = os.path.join(self.blueprint_repository_path, blueprint_type, f"{version}.json")
        
        if not os.path.exists(blueprint_path):
            raise FileNotFoundError(f"Blueprint not found: {blueprint_path}")
        
        with open(blueprint_path, 'r') as f:
            blueprint = json.load(f)
        
        return blueprint
    
    def _get_latest_version(self, blueprint_type: str) -> str:
        """
        Get the latest version of a blueprint type.
        
        Args:
            blueprint_type: Type of blueprint
            
        Returns:
            Latest version string
        """
        blueprint_dir = os.path.join(self.blueprint_repository_path, blueprint_type)
        
        if not os.path.exists(blueprint_dir):
            raise FileNotFoundError(f"Blueprint type not found: {blueprint_type}")
        
        # Load metadata to find latest version
        metadata_path = os.path.join(blueprint_dir, "metadata.json")
        
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Find latest version based on metadata
            if metadata:
                versions = [item.get("version") for item in metadata]
                return self._get_latest_semantic_version(versions)
        
        # Fallback to file listing
        files = [f for f in os.listdir(blueprint_dir) if f.endswith('.json') and f != "metadata.json"]
        
        if not files:
            raise FileNotFoundError(f"No blueprint versions found for type: {blueprint_type}")
        
        versions = [os.path.splitext(f)[0] for f in files]
        return self._get_latest_semantic_version(versions)
    
    def _get_latest_semantic_version(self, versions: List[str]) -> str:
        """
        Get the latest semantic version from a list of version strings.
        
        Args:
            versions: List of version strings
            
        Returns:
            Latest version string
        """
        def parse_version(version: str) -> Tuple[int, int, int]:
            try:
                parts = version.split('.')
                if len(parts) >= 3:
                    return (int(parts[0]), int(parts[1]), int(parts[2]))
                elif len(parts) == 2:
                    return (int(parts[0]), int(parts[1]), 0)
                else:
                    return (int(parts[0]), 0, 0)
            except (ValueError, IndexError):
                return (0, 0, 0)
        
        return max(versions, key=parse_version)
    
    def _load_blueprint_metadata(self):
        """
        Load metadata for all blueprints in the repository.
        """
        logger.info("Loading blueprint metadata")
        
        if not os.path.exists(self.blueprint_repository_path):
            logger.warning(f"Blueprint repository path does not exist: {self.blueprint_repository_path}")
            return
        
        # Iterate through blueprint types
        for blueprint_type in os.listdir(self.blueprint_repository_path):
            blueprint_dir = os.path.join(self.blueprint_repository_path, blueprint_type)
            
            if not os.path.isdir(blueprint_dir):
                continue
            
            # Load metadata file
            metadata_path = os.path.join(blueprint_dir, "metadata.json")
            
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata_list = json.load(f)
                
                # Add metadata to cache
                for metadata in metadata_list:
                    version = metadata.get("version")
                    if version:
                        cache_key = f"{blueprint_type}:{version}"
                        self.blueprint_metadata[cache_key] = metadata
    
    def _matches_criteria(self, metadata: Dict[str, Any], criteria: Dict[str, Any]) -> bool:
        """
        Check if metadata matches the given criteria.
        
        Args:
            metadata: Blueprint metadata
            criteria: Filter criteria
            
        Returns:
            True if metadata matches criteria, False otherwise
        """
        for key, value in criteria.items():
            if key not in metadata or metadata[key] != value:
                return False
        
        return True
