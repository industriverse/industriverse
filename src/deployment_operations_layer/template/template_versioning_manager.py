"""
Template Versioning Manager - Manages versioning of deployment templates

This module manages versioning of deployment templates, tracking changes and
ensuring compatibility across different versions.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import copy
import difflib
import uuid

logger = logging.getLogger(__name__)

class TemplateVersioningManager:
    """
    Manages versioning of deployment templates.
    
    This component is responsible for managing versioning of deployment templates,
    tracking changes and ensuring compatibility across different versions.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Template Versioning Manager.
        
        Args:
            config: Configuration dictionary for the manager
        """
        self.config = config or {}
        self.template_versions = {}  # Template ID -> List of versions
        self.template_metadata = {}  # Template ID -> Metadata
        self.version_history = {}  # Template ID -> Version history
        self.max_history_length = self.config.get("max_history_length", 100)
        
        logger.info("Initializing Template Versioning Manager")
    
    def initialize(self):
        """Initialize the manager and load template data."""
        logger.info("Initializing Template Versioning Manager")
        
        # Load template versions
        self._load_template_versions()
        
        # Load template metadata
        self._load_template_metadata()
        
        # Load version history
        self._load_version_history()
        
        logger.info(f"Loaded {len(self.template_versions)} template version sets")
        return True
    
    def register_template(self, template_id: str, template: Dict[str, Any], 
                         metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a new template.
        
        Args:
            template_id: ID of the template
            template: Template definition
            metadata: Template metadata
            
        Returns:
            Dictionary with registration result
        """
        logger.info(f"Registering template {template_id}")
        
        # Check if template already exists
        if template_id in self.template_versions:
            logger.warning(f"Template {template_id} already exists")
            return {"success": False, "error": "Template already exists"}
        
        # Validate template
        if not self._validate_template(template):
            logger.error(f"Invalid template for {template_id}")
            return {"success": False, "error": "Invalid template"}
        
        # Initialize version list
        self.template_versions[template_id] = []
        
        # Initialize metadata
        self.template_metadata[template_id] = metadata or {}
        
        # Initialize version history
        self.version_history[template_id] = []
        
        # Create initial version
        version_result = self.create_version(template_id, template, "Initial version")
        
        if not version_result["success"]:
            # Clean up if version creation failed
            del self.template_versions[template_id]
            del self.template_metadata[template_id]
            del self.version_history[template_id]
            
            logger.error(f"Failed to create initial version for template {template_id}")
            return version_result
        
        # Save template data
        self._save_template_versions()
        self._save_template_metadata()
        self._save_version_history()
        
        logger.info(f"Registered template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "version": version_result["version"]
        }
    
    def unregister_template(self, template_id: str) -> Dict[str, Any]:
        """
        Unregister a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with unregistration result
        """
        if template_id not in self.template_versions:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Remove template data
        del self.template_versions[template_id]
        del self.template_metadata[template_id]
        del self.version_history[template_id]
        
        # Save template data
        self._save_template_versions()
        self._save_template_metadata()
        self._save_version_history()
        
        logger.info(f"Unregistered template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id
        }
    
    def create_version(self, template_id: str, template: Dict[str, Any], 
                      comment: str = "") -> Dict[str, Any]:
        """
        Create a new version of a template.
        
        Args:
            template_id: ID of the template
            template: Template definition
            comment: Comment for the version
            
        Returns:
            Dictionary with version creation result
        """
        logger.info(f"Creating new version for template {template_id}")
        
        # Check if template exists
        if template_id not in self.template_versions:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Validate template
        if not self._validate_template(template):
            logger.error(f"Invalid template for {template_id}")
            return {"success": False, "error": "Invalid template"}
        
        # Generate version ID
        version_id = str(uuid.uuid4())
        
        # Create version
        version = {
            "id": version_id,
            "template": copy.deepcopy(template),
            "created": datetime.now().isoformat(),
            "comment": comment
        }
        
        # Add version to list
        self.template_versions[template_id].append(version)
        
        # Record version creation in history
        self._record_version_event(template_id, version_id, "create", comment)
        
        # Save template versions
        self._save_template_versions()
        
        logger.info(f"Created version {version_id} for template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "version": version_id
        }
    
    def get_version(self, template_id: str, version_id: str = None) -> Dict[str, Any]:
        """
        Get a specific version of a template.
        
        Args:
            template_id: ID of the template
            version_id: ID of the version (if None, returns latest version)
            
        Returns:
            Dictionary with version retrieval result
        """
        # Check if template exists
        if template_id not in self.template_versions:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Get versions
        versions = self.template_versions[template_id]
        
        if not versions:
            logger.error(f"No versions found for template {template_id}")
            return {"success": False, "error": "No versions found"}
        
        # Get specific version or latest
        if version_id:
            # Find version by ID
            version = next((v for v in versions if v["id"] == version_id), None)
            
            if not version:
                logger.error(f"Version {version_id} not found for template {template_id}")
                return {"success": False, "error": "Version not found"}
        else:
            # Get latest version
            version = versions[-1]
        
        logger.info(f"Retrieved version {version['id']} for template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "version": version["id"],
            "template": version["template"],
            "created": version["created"],
            "comment": version["comment"]
        }
    
    def get_versions(self, template_id: str) -> Dict[str, Any]:
        """
        Get all versions of a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with versions retrieval result
        """
        # Check if template exists
        if template_id not in self.template_versions:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Get versions
        versions = self.template_versions[template_id]
        
        if not versions:
            logger.error(f"No versions found for template {template_id}")
            return {"success": False, "error": "No versions found"}
        
        # Create version list
        version_list = []
        for version in versions:
            version_list.append({
                "id": version["id"],
                "created": version["created"],
                "comment": version["comment"]
            })
        
        logger.info(f"Retrieved {len(version_list)} versions for template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "versions": version_list
        }
    
    def compare_versions(self, template_id: str, version_id1: str, 
                        version_id2: str) -> Dict[str, Any]:
        """
        Compare two versions of a template.
        
        Args:
            template_id: ID of the template
            version_id1: ID of the first version
            version_id2: ID of the second version
            
        Returns:
            Dictionary with comparison result
        """
        logger.info(f"Comparing versions {version_id1} and {version_id2} for template {template_id}")
        
        # Get first version
        version1_result = self.get_version(template_id, version_id1)
        
        if not version1_result["success"]:
            logger.error(f"Failed to get version {version_id1}: {version1_result['error']}")
            return version1_result
        
        # Get second version
        version2_result = self.get_version(template_id, version_id2)
        
        if not version2_result["success"]:
            logger.error(f"Failed to get version {version_id2}: {version2_result['error']}")
            return version2_result
        
        # Get templates
        template1 = version1_result["template"]
        template2 = version2_result["template"]
        
        # Compare templates
        differences = self._compare_templates(template1, template2)
        
        logger.info(f"Found {len(differences)} differences between versions {version_id1} and {version_id2}")
        
        return {
            "success": True,
            "template_id": template_id,
            "version1": version_id1,
            "version2": version_id2,
            "differences": differences
        }
    
    def revert_to_version(self, template_id: str, version_id: str) -> Dict[str, Any]:
        """
        Revert to a specific version of a template.
        
        Args:
            template_id: ID of the template
            version_id: ID of the version to revert to
            
        Returns:
            Dictionary with reversion result
        """
        logger.info(f"Reverting template {template_id} to version {version_id}")
        
        # Get version
        version_result = self.get_version(template_id, version_id)
        
        if not version_result["success"]:
            logger.error(f"Failed to get version {version_id}: {version_result['error']}")
            return version_result
        
        # Create new version with reverted template
        comment = f"Reverted to version {version_id}"
        version_result = self.create_version(template_id, version_result["template"], comment)
        
        if not version_result["success"]:
            logger.error(f"Failed to create reverted version: {version_result['error']}")
            return version_result
        
        # Record reversion in history
        self._record_version_event(template_id, version_result["version"], "revert", 
                                 f"Reverted to version {version_id}")
        
        logger.info(f"Reverted template {template_id} to version {version_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "original_version": version_id,
            "new_version": version_result["version"]
        }
    
    def get_template_metadata(self, template_id: str) -> Dict[str, Any]:
        """
        Get metadata for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with metadata retrieval result
        """
        # Check if template exists
        if template_id not in self.template_metadata:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Get metadata
        metadata = self.template_metadata[template_id]
        
        logger.info(f"Retrieved metadata for template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "metadata": metadata
        }
    
    def update_template_metadata(self, template_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update metadata for a template.
        
        Args:
            template_id: ID of the template
            metadata: New metadata
            
        Returns:
            Dictionary with metadata update result
        """
        logger.info(f"Updating metadata for template {template_id}")
        
        # Check if template exists
        if template_id not in self.template_metadata:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Update metadata
        self.template_metadata[template_id] = metadata
        
        # Save template metadata
        self._save_template_metadata()
        
        logger.info(f"Updated metadata for template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id
        }
    
    def get_version_history(self, template_id: str) -> Dict[str, Any]:
        """
        Get version history for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with history retrieval result
        """
        # Check if template exists
        if template_id not in self.version_history:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Get history
        history = self.version_history[template_id]
        
        logger.info(f"Retrieved version history for template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "history": history
        }
    
    def _validate_template(self, template: Dict[str, Any]) -> bool:
        """
        Validate a template.
        
        Args:
            template: Template to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "description", "schema_version"]
        for field in required_fields:
            if field not in template:
                logger.error(f"Missing required field in template: {field}")
                return False
        
        # Check schema version
        schema_version = template.get("schema_version")
        if not isinstance(schema_version, str):
            logger.error("Schema version must be a string")
            return False
        
        # Additional validation could be added here
        
        return True
    
    def _compare_templates(self, template1: Dict[str, Any], template2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compare two templates and identify differences.
        
        Args:
            template1: First template
            template2: Second template
            
        Returns:
            List of differences
        """
        differences = []
        
        # Compare top-level fields
        for key in set(list(template1.keys()) + list(template2.keys())):
            # Check if field exists in both templates
            if key in template1 and key in template2:
                # Check if values are different
                if template1[key] != template2[key]:
                    # For complex objects, generate a detailed diff
                    if isinstance(template1[key], dict) and isinstance(template2[key], dict):
                        diff = self._compare_objects(template1[key], template2[key], key)
                        differences.extend(diff)
                    elif isinstance(template1[key], list) and isinstance(template2[key], list):
                        diff = self._compare_lists(template1[key], template2[key], key)
                        differences.extend(diff)
                    else:
                        differences.append({
                            "path": key,
                            "type": "modified",
                            "old_value": template1[key],
                            "new_value": template2[key]
                        })
            # Field exists only in first template
            elif key in template1:
                differences.append({
                    "path": key,
                    "type": "removed",
                    "old_value": template1[key]
                })
            # Field exists only in second template
            else:
                differences.append({
                    "path": key,
                    "type": "added",
                    "new_value": template2[key]
                })
        
        return differences
    
    def _compare_objects(self, obj1: Dict[str, Any], obj2: Dict[str, Any], 
                        path: str) -> List[Dict[str, Any]]:
        """
        Compare two objects and identify differences.
        
        Args:
            obj1: First object
            obj2: Second object
            path: Path to the objects
            
        Returns:
            List of differences
        """
        differences = []
        
        # Compare fields
        for key in set(list(obj1.keys()) + list(obj2.keys())):
            # Build path
            field_path = f"{path}.{key}"
            
            # Check if field exists in both objects
            if key in obj1 and key in obj2:
                # Check if values are different
                if obj1[key] != obj2[key]:
                    # For complex objects, generate a detailed diff
                    if isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                        diff = self._compare_objects(obj1[key], obj2[key], field_path)
                        differences.extend(diff)
                    elif isinstance(obj1[key], list) and isinstance(obj2[key], list):
                        diff = self._compare_lists(obj1[key], obj2[key], field_path)
                        differences.extend(diff)
                    else:
                        differences.append({
                            "path": field_path,
                            "type": "modified",
                            "old_value": obj1[key],
                            "new_value": obj2[key]
                        })
            # Field exists only in first object
            elif key in obj1:
                differences.append({
                    "path": field_path,
                    "type": "removed",
                    "old_value": obj1[key]
                })
            # Field exists only in second object
            else:
                differences.append({
                    "path": field_path,
                    "type": "added",
                    "new_value": obj2[key]
                })
        
        return differences
    
    def _compare_lists(self, list1: List[Any], list2: List[Any], path: str) -> List[Dict[str, Any]]:
        """
        Compare two lists and identify differences.
        
        Args:
            list1: First list
            list2: Second list
            path: Path to the lists
            
        Returns:
            List of differences
        """
        differences = []
        
        # For simplicity, we'll just check if the lists are different
        # In a real implementation, this would use a more sophisticated algorithm
        # to identify specific changes within the lists
        
        if list1 != list2:
            differences.append({
                "path": path,
                "type": "modified",
                "old_value": list1,
                "new_value": list2
            })
        
        return differences
    
    def _record_version_event(self, template_id: str, version_id: str, event_type: str, 
                            comment: str = ""):
        """
        Record a version event in history.
        
        Args:
            template_id: ID of the template
            version_id: ID of the version
            event_type: Type of event
            comment: Comment for the event
        """
        # Create event
        event = {
            "template_id": template_id,
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "comment": comment
        }
        
        # Add event to history
        self.version_history[template_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.version_history[template_id]) > self.max_history_length:
            self.version_history[template_id] = self.version_history[template_id][-self.max_history_length:]
        
        # Save version history
        self._save_version_history()
        
        logger.info(f"Recorded {event_type} event for template {template_id}, version {version_id}")
    
    def _load_template_versions(self):
        """Load template versions from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.template_versions = {}
            logger.info("Loaded template versions")
        except Exception as e:
            logger.error(f"Failed to load template versions: {str(e)}")
    
    def _save_template_versions(self):
        """Save template versions to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.template_versions)} template version sets")
        except Exception as e:
            logger.error(f"Failed to save template versions: {str(e)}")
    
    def _load_template_metadata(self):
        """Load template metadata from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.template_metadata = {}
            logger.info("Loaded template metadata")
        except Exception as e:
            logger.error(f"Failed to load template metadata: {str(e)}")
    
    def _save_template_metadata(self):
        """Save template metadata to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.template_metadata)} template metadata entries")
        except Exception as e:
            logger.error(f"Failed to save template metadata: {str(e)}")
    
    def _load_version_history(self):
        """Load version history from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.version_history = {}
            logger.info("Loaded version history")
        except Exception as e:
            logger.error(f"Failed to load version history: {str(e)}")
    
    def _save_version_history(self):
        """Save version history to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved version history")
        except Exception as e:
            logger.error(f"Failed to save version history: {str(e)}")
