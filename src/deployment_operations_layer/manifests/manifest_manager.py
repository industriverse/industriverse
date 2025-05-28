"""
Manifest Manager for the Deployment Operations Layer.

This module provides manifest management capabilities for deployment operations
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
import yaml
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ManifestManager:
    """
    Manager for deployment manifests.
    
    This class provides methods for managing deployment manifests,
    including creation, validation, and application.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Manifest Manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.manager_id = config.get("manager_id", f"manifest-manager-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9014")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize manifest storage
        self.storage_type = config.get("storage_type", "file")
        self.storage_path = config.get("storage_path", "/tmp/manifests")
        self.manifests = {}
        
        # Initialize manifest configuration
        self.manifest_types = config.get("manifest_types", [
            "kubernetes", "docker", "terraform", "ansible", "helm", "custom"
        ])
        self.manifest_formats = config.get("manifest_formats", [
            "yaml", "json", "tf", "j2", "sh", "py"
        ])
        
        # Initialize template manager for manifest generation
        from ..templates.template_manager import TemplateManager
        self.template_manager = TemplateManager(config.get("template_manager", {}))
        
        # Initialize kubernetes integration for manifest application
        from ..kubernetes.kubernetes_integration import KubernetesIntegration
        self.kubernetes = KubernetesIntegration(config.get("kubernetes", {}))
        
        # Initialize analytics manager for manifest tracking
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        # Load existing manifests
        self._load_manifests()
        
        logger.info(f"Manifest Manager {self.manager_id} initialized")
    
    def create_manifest(self, manifest_data: Dict) -> Dict:
        """
        Create a new manifest.
        
        Args:
            manifest_data: Manifest data
            
        Returns:
            Dict: Creation results
        """
        try:
            # Generate manifest ID if not provided
            manifest_id = manifest_data.get("manifest_id")
            if not manifest_id:
                manifest_id = f"manifest-{uuid.uuid4().hex}"
                manifest_data["manifest_id"] = manifest_id
            
            # Check if manifest already exists
            if manifest_id in self.manifests:
                return {
                    "status": "error",
                    "message": f"Manifest already exists: {manifest_id}"
                }
            
            # Validate manifest data
            validation_result = self._validate_manifest_data(manifest_data)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Add creation metadata
            manifest_data["creation_timestamp"] = datetime.now().isoformat()
            manifest_data["last_updated_timestamp"] = datetime.now().isoformat()
            
            # Add version information
            manifest_data["version"] = manifest_data.get("version", "1.0.0")
            manifest_data["version_history"] = manifest_data.get("version_history", [])
            
            # Store manifest
            self.manifests[manifest_id] = manifest_data
            
            # Save manifest to storage
            self._save_manifest(manifest_id, manifest_data)
            
            # Track manifest creation
            self._track_manifest_event("create", manifest_data)
            
            return {
                "status": "success",
                "message": "Manifest created successfully",
                "manifest_id": manifest_id,
                "creation_timestamp": manifest_data["creation_timestamp"]
            }
        except Exception as e:
            logger.error(f"Error creating manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def update_manifest(self, manifest_id: str, update_data: Dict) -> Dict:
        """
        Update an existing manifest.
        
        Args:
            manifest_id: Manifest ID
            update_data: Update data
            
        Returns:
            Dict: Update results
        """
        try:
            # Check if manifest exists
            if manifest_id not in self.manifests:
                return {
                    "status": "error",
                    "message": f"Manifest not found: {manifest_id}"
                }
            
            # Get current manifest data
            manifest_data = self.manifests[manifest_id]
            
            # Check if update includes version change
            if "version" in update_data and update_data["version"] != manifest_data["version"]:
                # Add current version to version history
                if "version_history" not in manifest_data:
                    manifest_data["version_history"] = []
                
                manifest_data["version_history"].append({
                    "version": manifest_data["version"],
                    "timestamp": manifest_data["last_updated_timestamp"]
                })
            
            # Update manifest data
            for key, value in update_data.items():
                if key not in ["manifest_id", "creation_timestamp"]:
                    manifest_data[key] = value
            
            # Update last updated timestamp
            manifest_data["last_updated_timestamp"] = datetime.now().isoformat()
            
            # Save manifest to storage
            self._save_manifest(manifest_id, manifest_data)
            
            # Track manifest update
            self._track_manifest_event("update", manifest_data)
            
            return {
                "status": "success",
                "message": "Manifest updated successfully",
                "manifest_id": manifest_id,
                "last_updated_timestamp": manifest_data["last_updated_timestamp"]
            }
        except Exception as e:
            logger.error(f"Error updating manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_manifest(self, manifest_id: str) -> Optional[Dict]:
        """
        Get a manifest by ID.
        
        Args:
            manifest_id: Manifest ID
            
        Returns:
            Optional[Dict]: Manifest data or None if not found
        """
        return self.manifests.get(manifest_id)
    
    def list_manifests(self, filters: Dict = None) -> List[Dict]:
        """
        List manifests with optional filtering.
        
        Args:
            filters: Filter criteria
            
        Returns:
            List[Dict]: List of manifests
        """
        if not filters:
            return list(self.manifests.values())
        
        filtered_manifests = []
        for manifest in self.manifests.values():
            match = True
            for key, value in filters.items():
                if key not in manifest or manifest[key] != value:
                    match = False
                    break
            
            if match:
                filtered_manifests.append(manifest)
        
        return filtered_manifests
    
    def delete_manifest(self, manifest_id: str) -> Dict:
        """
        Delete a manifest.
        
        Args:
            manifest_id: Manifest ID
            
        Returns:
            Dict: Deletion results
        """
        try:
            # Check if manifest exists
            if manifest_id not in self.manifests:
                return {
                    "status": "error",
                    "message": f"Manifest not found: {manifest_id}"
                }
            
            # Get manifest data for tracking
            manifest_data = self.manifests[manifest_id]
            
            # Delete manifest
            del self.manifests[manifest_id]
            
            # Delete manifest from storage
            self._delete_manifest(manifest_id)
            
            # Track manifest deletion
            self._track_manifest_event("delete", manifest_data)
            
            return {
                "status": "success",
                "message": "Manifest deleted successfully",
                "manifest_id": manifest_id
            }
        except Exception as e:
            logger.error(f"Error deleting manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def validate_manifest(self, manifest_id: str) -> Dict:
        """
        Validate a manifest.
        
        Args:
            manifest_id: Manifest ID
            
        Returns:
            Dict: Validation results
        """
        try:
            # Check if manifest exists
            if manifest_id not in self.manifests:
                return {
                    "status": "error",
                    "message": f"Manifest not found: {manifest_id}"
                }
            
            # Get manifest data
            manifest_data = self.manifests[manifest_id]
            
            # Get manifest content
            manifest_content = manifest_data.get("content")
            if not manifest_content:
                return {
                    "status": "error",
                    "message": f"Manifest has no content: {manifest_id}"
                }
            
            # Get manifest type
            manifest_type = manifest_data.get("type")
            
            # Validate based on manifest type
            if manifest_type == "kubernetes":
                # Validate Kubernetes manifest
                validation_result = self.kubernetes.validate_manifest(manifest_content)
            else:
                # Generic validation
                validation_result = self._validate_generic_manifest(manifest_content, manifest_type)
            
            # Track manifest validation
            self._track_manifest_event("validate", manifest_data)
            
            return validation_result
        except Exception as e:
            logger.error(f"Error validating manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def apply_manifest(self, manifest_id: str, context: Dict = None) -> Dict:
        """
        Apply a manifest.
        
        Args:
            manifest_id: Manifest ID
            context: Application context
            
        Returns:
            Dict: Application results
        """
        try:
            # Check if manifest exists
            if manifest_id not in self.manifests:
                return {
                    "status": "error",
                    "message": f"Manifest not found: {manifest_id}"
                }
            
            # Get manifest data
            manifest_data = self.manifests[manifest_id]
            
            # Get manifest content
            manifest_content = manifest_data.get("content")
            if not manifest_content:
                return {
                    "status": "error",
                    "message": f"Manifest has no content: {manifest_id}"
                }
            
            # Get manifest type
            manifest_type = manifest_data.get("type")
            
            # Apply based on manifest type
            if manifest_type == "kubernetes":
                # Apply Kubernetes manifest
                application_result = self.kubernetes.apply_manifest(manifest_content, context)
            else:
                # Generic application
                application_result = self._apply_generic_manifest(manifest_content, manifest_type, context)
            
            # Track manifest application
            self._track_manifest_event("apply", manifest_data)
            
            return application_result
        except Exception as e:
            logger.error(f"Error applying manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def generate_manifest(self, template_id: str, context: Dict) -> Dict:
        """
        Generate a manifest from a template.
        
        Args:
            template_id: Template ID
            context: Generation context
            
        Returns:
            Dict: Generation results
        """
        try:
            # Render template
            render_result = self.template_manager.render_template(template_id, context)
            
            if render_result.get("status") != "success":
                return render_result
            
            # Get rendered content
            rendered_content = render_result.get("rendered_content")
            
            # Get template data
            template_data = self.template_manager.get_template(template_id)
            
            # Create manifest data
            manifest_data = {
                "name": f"{template_data.get('name')}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": template_data.get("type"),
                "format": template_data.get("format"),
                "content": rendered_content,
                "template_id": template_id,
                "context": context,
                "description": f"Generated from template {template_data.get('name')} ({template_id})"
            }
            
            # Create manifest
            create_result = self.create_manifest(manifest_data)
            
            return create_result
        except Exception as e:
            logger.error(f"Error generating manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_manifest_data(self, manifest_data: Dict) -> Dict:
        """
        Validate manifest data.
        
        Args:
            manifest_data: Manifest data
            
        Returns:
            Dict: Validation results
        """
        # Check required fields
        required_fields = ["name", "type", "content"]
        for field in required_fields:
            if field not in manifest_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        # Validate manifest type
        if manifest_data["type"] not in self.manifest_types:
            return {
                "status": "error",
                "message": f"Invalid manifest type: {manifest_data['type']}"
            }
        
        # Validate manifest format if provided
        if "format" in manifest_data and manifest_data["format"] not in self.manifest_formats:
            return {
                "status": "error",
                "message": f"Invalid manifest format: {manifest_data['format']}"
            }
        
        return {"status": "success"}
    
    def _validate_generic_manifest(self, manifest_content: str, manifest_type: str) -> Dict:
        """
        Validate a generic manifest.
        
        Args:
            manifest_content: Manifest content
            manifest_type: Manifest type
            
        Returns:
            Dict: Validation results
        """
        try:
            # Basic validation based on manifest type
            if manifest_type == "docker":
                # Validate Docker manifest (e.g., Dockerfile)
                # In a real implementation, this would use a proper validator
                if "FROM" not in manifest_content:
                    return {
                        "status": "error",
                        "message": "Invalid Docker manifest: missing FROM directive"
                    }
            elif manifest_type == "terraform":
                # Validate Terraform manifest
                # In a real implementation, this would use a proper validator
                if "resource" not in manifest_content and "provider" not in manifest_content:
                    return {
                        "status": "error",
                        "message": "Invalid Terraform manifest: missing resource or provider"
                    }
            elif manifest_type == "ansible":
                # Validate Ansible manifest
                # In a real implementation, this would use a proper validator
                if "tasks" not in manifest_content and "roles" not in manifest_content:
                    return {
                        "status": "error",
                        "message": "Invalid Ansible manifest: missing tasks or roles"
                    }
            elif manifest_type == "helm":
                # Validate Helm manifest
                # In a real implementation, this would use a proper validator
                if "apiVersion" not in manifest_content or "kind" not in manifest_content:
                    return {
                        "status": "error",
                        "message": "Invalid Helm manifest: missing apiVersion or kind"
                    }
            
            return {
                "status": "success",
                "message": f"{manifest_type} manifest validated successfully"
            }
        except Exception as e:
            logger.error(f"Error validating generic manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def _apply_generic_manifest(self, manifest_content: str, manifest_type: str, context: Dict = None) -> Dict:
        """
        Apply a generic manifest.
        
        Args:
            manifest_content: Manifest content
            manifest_type: Manifest type
            context: Application context
            
        Returns:
            Dict: Application results
        """
        try:
            # Basic application based on manifest type
            if manifest_type == "docker":
                # Apply Docker manifest (e.g., build Docker image)
                return {
                    "status": "success",
                    "message": "Docker manifest applied successfully",
                    "details": "Docker image would be built in a real implementation"
                }
            elif manifest_type == "terraform":
                # Apply Terraform manifest
                return {
                    "status": "success",
                    "message": "Terraform manifest applied successfully",
                    "details": "Terraform resources would be created in a real implementation"
                }
            elif manifest_type == "ansible":
                # Apply Ansible manifest
                return {
                    "status": "success",
                    "message": "Ansible manifest applied successfully",
                    "details": "Ansible playbook would be executed in a real implementation"
                }
            elif manifest_type == "helm":
                # Apply Helm manifest
                return {
                    "status": "success",
                    "message": "Helm manifest applied successfully",
                    "details": "Helm chart would be installed in a real implementation"
                }
            else:
                return {
                    "status": "success",
                    "message": f"{manifest_type} manifest applied successfully",
                    "details": "Generic application simulated"
                }
        except Exception as e:
            logger.error(f"Error applying generic manifest: {e}")
            return {"status": "error", "message": str(e)}
    
    def _load_manifests(self) -> None:
        """
        Load manifests from storage.
        """
        try:
            if self.storage_type == "file":
                # Create storage directory if it doesn't exist
                os.makedirs(self.storage_path, exist_ok=True)
                
                # Get manifest files
                manifest_files = []
                for root, _, files in os.walk(self.storage_path):
                    for file in files:
                        if file.endswith(".json"):
                            manifest_files.append(os.path.join(root, file))
                
                # Load manifests
                for manifest_file in manifest_files:
                    try:
                        with open(manifest_file, "r") as f:
                            manifest_data = json.load(f)
                            
                            # Add manifest to manifests
                            manifest_id = manifest_data.get("manifest_id")
                            if manifest_id:
                                self.manifests[manifest_id] = manifest_data
                    except Exception as e:
                        logger.error(f"Error loading manifest file {manifest_file}: {e}")
                
                logger.info(f"Loaded {len(self.manifests)} manifests from storage")
        except Exception as e:
            logger.error(f"Error loading manifests: {e}")
    
    def _save_manifest(self, manifest_id: str, manifest_data: Dict) -> None:
        """
        Save a manifest to storage.
        
        Args:
            manifest_id: Manifest ID
            manifest_data: Manifest data
        """
        try:
            if self.storage_type == "file":
                # Create storage directory if it doesn't exist
                os.makedirs(self.storage_path, exist_ok=True)
                
                # Save manifest to file
                manifest_file = os.path.join(self.storage_path, f"{manifest_id}.json")
                with open(manifest_file, "w") as f:
                    json.dump(manifest_data, f, indent=2)
                
                logger.info(f"Saved manifest {manifest_id} to storage")
        except Exception as e:
            logger.error(f"Error saving manifest {manifest_id}: {e}")
    
    def _delete_manifest(self, manifest_id: str) -> None:
        """
        Delete a manifest from storage.
        
        Args:
            manifest_id: Manifest ID
        """
        try:
            if self.storage_type == "file":
                # Delete manifest file
                manifest_file = os.path.join(self.storage_path, f"{manifest_id}.json")
                if os.path.exists(manifest_file):
                    os.remove(manifest_file)
                
                logger.info(f"Deleted manifest {manifest_id} from storage")
        except Exception as e:
            logger.error(f"Error deleting manifest {manifest_id}: {e}")
    
    def _track_manifest_event(self, event_type: str, manifest_data: Dict) -> None:
        """
        Track a manifest event in analytics.
        
        Args:
            event_type: Event type
            manifest_data: Manifest data
        """
        try:
            # Prepare metrics
            metrics = {
                "type": f"manifest_{event_type}",
                "timestamp": datetime.now().isoformat(),
                "manifest_id": manifest_data.get("manifest_id"),
                "manifest_type": manifest_data.get("type"),
                "manager_id": self.manager_id
            }
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking manifest event: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Manifest Manager.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "storage_type" in config:
                self.storage_type = config["storage_type"]
            
            if "storage_path" in config:
                self.storage_path = config["storage_path"]
            
            if "manifest_types" in config:
                self.manifest_types = config["manifest_types"]
            
            if "manifest_formats" in config:
                self.manifest_formats = config["manifest_formats"]
            
            # Configure template manager
            template_manager_result = None
            if "template_manager" in config:
                template_manager_result = self.template_manager.configure(config["template_manager"])
            
            # Configure kubernetes integration
            kubernetes_result = None
            if "kubernetes" in config:
                kubernetes_result = self.kubernetes.configure(config["kubernetes"])
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            # Reload manifests if storage type or path changed
            if "storage_type" in config or "storage_path" in config:
                self._load_manifests()
            
            return {
                "status": "success",
                "message": "Manifest Manager configured successfully",
                "manager_id": self.manager_id,
                "template_manager_result": template_manager_result,
                "kubernetes_result": kubernetes_result,
                "analytics_result": analytics_result
            }
        except Exception as e:
            logger.error(f"Error configuring Manifest Manager: {e}")
            return {"status": "error", "message": str(e)}
