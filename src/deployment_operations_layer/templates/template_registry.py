"""
Template Registry for the Deployment Operations Layer.

This module provides template registry capabilities for deployment operations
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TemplateRegistry:
    """
    Registry for deployment templates.
    
    This class provides methods for managing template registrations,
    including registration, retrieval, and lifecycle management.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Template Registry.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.registry_id = config.get("registry_id", f"registry-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9013")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize registry storage
        self.storage_type = config.get("storage_type", "memory")
        self.storage_path = config.get("storage_path", "/tmp/template_registry")
        self.templates = {}
        
        # Initialize registry configuration
        self.template_categories = config.get("template_categories", [
            "infrastructure", "application", "network", "security", "monitoring", "custom"
        ])
        self.template_states = config.get("template_states", [
            "draft", "published", "deprecated", "archived"
        ])
        self.default_state = config.get("default_state", "draft")
        
        # Initialize blockchain integration for immutable records
        from ..blockchain.blockchain_integration import BlockchainIntegration
        self.blockchain = BlockchainIntegration(config.get("blockchain", {}))
        
        # Initialize analytics manager for registry tracking
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        # Load existing templates if using file storage
        if self.storage_type == "file":
            self._load_templates()
        
        logger.info(f"Template Registry {self.registry_id} initialized")
    
    def register_template(self, template_data: Dict) -> Dict:
        """
        Register a new template.
        
        Args:
            template_data: Template data
            
        Returns:
            Dict: Registration results
        """
        try:
            # Generate template ID if not provided
            template_id = template_data.get("template_id")
            if not template_id:
                template_id = f"template-{uuid.uuid4().hex}"
                template_data["template_id"] = template_id
            
            # Check if template already exists
            if template_id in self.templates:
                return {
                    "status": "error",
                    "message": f"Template already exists: {template_id}"
                }
            
            # Validate template data
            validation_result = self._validate_template_data(template_data)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Add registration metadata
            template_data["registry_id"] = self.registry_id
            template_data["registration_timestamp"] = datetime.now().isoformat()
            template_data["last_updated_timestamp"] = datetime.now().isoformat()
            template_data["state"] = template_data.get("state", self.default_state)
            
            # Add version information
            template_data["version"] = template_data.get("version", "1.0.0")
            template_data["version_history"] = template_data.get("version_history", [])
            
            # Store template
            self.templates[template_id] = template_data
            
            # Save to storage if using file storage
            if self.storage_type == "file":
                self._save_templates()
            
            # Record on blockchain
            blockchain_result = self._record_on_blockchain("register", template_data)
            
            # Track registration
            self._track_template_event("register", template_data)
            
            return {
                "status": "success",
                "message": "Template registered successfully",
                "template_id": template_id,
                "registration_timestamp": template_data["registration_timestamp"],
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error registering template: {e}")
            return {"status": "error", "message": str(e)}
    
    def update_template(self, template_id: str, update_data: Dict) -> Dict:
        """
        Update an existing template.
        
        Args:
            template_id: Template ID
            update_data: Update data
            
        Returns:
            Dict: Update results
        """
        try:
            # Check if template exists
            if template_id not in self.templates:
                return {
                    "status": "error",
                    "message": f"Template not found: {template_id}"
                }
            
            # Get current template data
            template_data = self.templates[template_id]
            
            # Check if update includes state change
            if "state" in update_data and update_data["state"] != template_data["state"]:
                state_change_result = self._validate_state_change(
                    template_data["state"], update_data["state"], template_data
                )
                if state_change_result.get("status") != "success":
                    return state_change_result
            
            # Check if update includes version change
            if "version" in update_data and update_data["version"] != template_data["version"]:
                # Add current version to version history
                if "version_history" not in template_data:
                    template_data["version_history"] = []
                
                template_data["version_history"].append({
                    "version": template_data["version"],
                    "timestamp": template_data["last_updated_timestamp"]
                })
            
            # Update template data
            for key, value in update_data.items():
                if key not in ["template_id", "registry_id", "registration_timestamp"]:
                    template_data[key] = value
            
            # Update last updated timestamp
            template_data["last_updated_timestamp"] = datetime.now().isoformat()
            
            # Save to storage if using file storage
            if self.storage_type == "file":
                self._save_templates()
            
            # Record on blockchain
            blockchain_result = self._record_on_blockchain("update", template_data)
            
            # Track update
            self._track_template_event("update", template_data)
            
            return {
                "status": "success",
                "message": "Template updated successfully",
                "template_id": template_id,
                "last_updated_timestamp": template_data["last_updated_timestamp"],
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """
        Get a template by ID.
        
        Args:
            template_id: Template ID
            
        Returns:
            Optional[Dict]: Template data or None if not found
        """
        return self.templates.get(template_id)
    
    def list_templates(self, filters: Dict = None) -> List[Dict]:
        """
        List templates with optional filtering.
        
        Args:
            filters: Filter criteria
            
        Returns:
            List[Dict]: List of templates
        """
        if not filters:
            return list(self.templates.values())
        
        filtered_templates = []
        for template in self.templates.values():
            match = True
            for key, value in filters.items():
                if key not in template or template[key] != value:
                    match = False
                    break
            
            if match:
                filtered_templates.append(template)
        
        return filtered_templates
    
    def delete_template(self, template_id: str) -> Dict:
        """
        Delete a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Dict: Deletion results
        """
        try:
            # Check if template exists
            if template_id not in self.templates:
                return {
                    "status": "error",
                    "message": f"Template not found: {template_id}"
                }
            
            # Get template data for tracking
            template_data = self.templates[template_id]
            
            # Delete template
            del self.templates[template_id]
            
            # Save to storage if using file storage
            if self.storage_type == "file":
                self._save_templates()
            
            # Record on blockchain
            blockchain_result = self._record_on_blockchain("delete", template_data)
            
            # Track deletion
            self._track_template_event("delete", template_data)
            
            return {
                "status": "success",
                "message": "Template deleted successfully",
                "template_id": template_id,
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_template_history(self, template_id: str) -> Dict:
        """
        Get the history of a template.
        
        Args:
            template_id: Template ID
            
        Returns:
            Dict: History results
        """
        try:
            # Check if template exists
            if template_id not in self.templates:
                return {
                    "status": "error",
                    "message": f"Template not found: {template_id}"
                }
            
            # Get template data
            template_data = self.templates[template_id]
            
            # Get blockchain history
            blockchain_history = self.blockchain.get_entity_history(template_id)
            
            return {
                "status": "success",
                "message": "Template history retrieved successfully",
                "template_id": template_id,
                "registration_timestamp": template_data.get("registration_timestamp"),
                "last_updated_timestamp": template_data.get("last_updated_timestamp"),
                "version": template_data.get("version"),
                "version_history": template_data.get("version_history", []),
                "blockchain_history": blockchain_history
            }
        except Exception as e:
            logger.error(f"Error getting template history: {e}")
            return {"status": "error", "message": str(e)}
    
    def search_templates(self, query: str) -> Dict:
        """
        Search templates.
        
        Args:
            query: Search query
            
        Returns:
            Dict: Search results
        """
        try:
            # Perform search
            results = []
            query = query.lower()
            
            for template in self.templates.values():
                # Search in name
                if query in template.get("name", "").lower():
                    results.append(template)
                    continue
                
                # Search in description
                if query in template.get("description", "").lower():
                    results.append(template)
                    continue
                
                # Search in tags
                tags = template.get("tags", [])
                for tag in tags:
                    if query in tag.lower():
                        results.append(template)
                        break
            
            return {
                "status": "success",
                "message": "Templates searched successfully",
                "query": query,
                "count": len(results),
                "results": results
            }
        except Exception as e:
            logger.error(f"Error searching templates: {e}")
            return {"status": "error", "message": str(e)}
    
    def _validate_template_data(self, template_data: Dict) -> Dict:
        """
        Validate template data.
        
        Args:
            template_data: Template data
            
        Returns:
            Dict: Validation results
        """
        # Check required fields
        required_fields = ["name", "type"]
        for field in required_fields:
            if field not in template_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        # Validate template category if provided
        if "category" in template_data and template_data["category"] not in self.template_categories:
            return {
                "status": "error",
                "message": f"Invalid template category: {template_data['category']}"
            }
        
        # Validate state if provided
        if "state" in template_data and template_data["state"] not in self.template_states:
            return {
                "status": "error",
                "message": f"Invalid template state: {template_data['state']}"
            }
        
        return {"status": "success"}
    
    def _validate_state_change(self, current_state: str, new_state: str, template_data: Dict) -> Dict:
        """
        Validate a state change.
        
        Args:
            current_state: Current state
            new_state: New state
            template_data: Template data
            
        Returns:
            Dict: Validation results
        """
        # Define valid state transitions
        valid_transitions = {
            "draft": ["published", "archived"],
            "published": ["deprecated", "archived"],
            "deprecated": ["archived"],
            "archived": []
        }
        
        # Check if transition is valid
        if new_state not in valid_transitions.get(current_state, []):
            return {
                "status": "error",
                "message": f"Invalid state transition: {current_state} -> {new_state}"
            }
        
        return {"status": "success"}
    
    def _record_on_blockchain(self, action: str, template_data: Dict) -> Dict:
        """
        Record a template action on the blockchain.
        
        Args:
            action: Action type
            template_data: Template data
            
        Returns:
            Dict: Blockchain recording results
        """
        try:
            # Prepare record data
            record_data = {
                "action": action,
                "template_id": template_data["template_id"],
                "timestamp": datetime.now().isoformat(),
                "registry_id": self.registry_id
            }
            
            # Add action-specific data
            if action == "register":
                record_data.update({
                    "name": template_data["name"],
                    "type": template_data["type"],
                    "version": template_data["version"],
                    "state": template_data["state"]
                })
            elif action == "update":
                record_data.update({
                    "version": template_data["version"],
                    "state": template_data["state"]
                })
            
            # Record on blockchain
            return self.blockchain.record_transaction(record_data)
        except Exception as e:
            logger.error(f"Error recording on blockchain: {e}")
            return {"status": "error", "message": str(e)}
    
    def _track_template_event(self, event_type: str, template_data: Dict) -> None:
        """
        Track a template event in analytics.
        
        Args:
            event_type: Event type
            template_data: Template data
        """
        try:
            # Prepare metrics
            metrics = {
                "type": f"template_{event_type}",
                "timestamp": datetime.now().isoformat(),
                "template_id": template_data["template_id"],
                "template_type": template_data["type"],
                "template_state": template_data.get("state", self.default_state),
                "registry_id": self.registry_id
            }
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking template event: {e}")
    
    def _load_templates(self) -> None:
        """
        Load templates from file storage.
        """
        try:
            # Create storage directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Check if storage file exists
            if os.path.exists(self.storage_path):
                with open(self.storage_path, "r") as f:
                    self.templates = json.load(f)
                
                logger.info(f"Loaded {len(self.templates)} templates from storage")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def _save_templates(self) -> None:
        """
        Save templates to file storage.
        """
        try:
            # Create storage directory if it doesn't exist
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            # Save templates to file
            with open(self.storage_path, "w") as f:
                json.dump(self.templates, f)
            
            logger.info(f"Saved {len(self.templates)} templates to storage")
        except Exception as e:
            logger.error(f"Error saving templates: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Template Registry.
        
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
            
            if "template_categories" in config:
                self.template_categories = config["template_categories"]
            
            if "template_states" in config:
                self.template_states = config["template_states"]
            
            if "default_state" in config:
                self.default_state = config["default_state"]
            
            # Configure blockchain integration
            blockchain_result = None
            if "blockchain" in config:
                blockchain_result = self.blockchain.configure(config["blockchain"])
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            # Reload templates if storage type or path changed
            if "storage_type" in config or "storage_path" in config:
                if self.storage_type == "file":
                    self._load_templates()
            
            return {
                "status": "success",
                "message": "Template Registry configured successfully",
                "registry_id": self.registry_id,
                "blockchain_result": blockchain_result,
                "analytics_result": analytics_result
            }
        except Exception as e:
            logger.error(f"Error configuring Template Registry: {e}")
            return {"status": "error", "message": str(e)}
