"""
Template Manager for the Deployment Operations Layer.

This module provides template management capabilities for deployment operations
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
from jinja2 import Template, Environment, FileSystemLoader, select_autoescape

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TemplateManager:
    """
    Manager for deployment templates.
    
    This class provides methods for managing deployment templates,
    including creation, retrieval, and rendering.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Template Manager.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.manager_id = config.get("manager_id", f"template-manager-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9012")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize template storage
        self.storage_type = config.get("storage_type", "file")
        self.storage_path = config.get("storage_path", "/tmp/templates")
        self.templates = {}
        
        # Initialize template configuration
        self.template_types = config.get("template_types", [
            "kubernetes", "docker", "terraform", "ansible", "helm", "custom"
        ])
        self.template_formats = config.get("template_formats", [
            "yaml", "json", "tf", "j2", "sh", "py"
        ])
        
        # Initialize Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(self.storage_path),
            autoescape=select_autoescape(['html', 'xml']),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Add custom Jinja2 filters
        self.jinja_env.filters['to_json'] = lambda obj: json.dumps(obj)
        self.jinja_env.filters['to_yaml'] = lambda obj: yaml.dump(obj)
        
        # Initialize template registry
        from .template_registry import TemplateRegistry
        self.registry = TemplateRegistry(config.get("registry", {}))
        
        # Initialize analytics manager for template tracking
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        # Load existing templates
        self._load_templates()
        
        logger.info(f"Template Manager {self.manager_id} initialized")
    
    def create_template(self, template_data: Dict) -> Dict:
        """
        Create a new template.
        
        Args:
            template_data: Template data
            
        Returns:
            Dict: Creation results
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
            
            # Add creation metadata
            template_data["creation_timestamp"] = datetime.now().isoformat()
            template_data["last_updated_timestamp"] = datetime.now().isoformat()
            
            # Add version information
            template_data["version"] = template_data.get("version", "1.0.0")
            template_data["version_history"] = template_data.get("version_history", [])
            
            # Store template
            self.templates[template_id] = template_data
            
            # Save template to storage
            self._save_template(template_id, template_data)
            
            # Register template
            registry_result = self.registry.register_template(template_data)
            
            # Track template creation
            self._track_template_event("create", template_data)
            
            return {
                "status": "success",
                "message": "Template created successfully",
                "template_id": template_id,
                "creation_timestamp": template_data["creation_timestamp"],
                "registry_result": registry_result
            }
        except Exception as e:
            logger.error(f"Error creating template: {e}")
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
                if key not in ["template_id", "creation_timestamp"]:
                    template_data[key] = value
            
            # Update last updated timestamp
            template_data["last_updated_timestamp"] = datetime.now().isoformat()
            
            # Save template to storage
            self._save_template(template_id, template_data)
            
            # Update template in registry
            registry_result = self.registry.update_template(template_id, template_data)
            
            # Track template update
            self._track_template_event("update", template_data)
            
            return {
                "status": "success",
                "message": "Template updated successfully",
                "template_id": template_id,
                "last_updated_timestamp": template_data["last_updated_timestamp"],
                "registry_result": registry_result
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
            
            # Delete template from storage
            self._delete_template(template_id)
            
            # Delete template from registry
            registry_result = self.registry.delete_template(template_id)
            
            # Track template deletion
            self._track_template_event("delete", template_data)
            
            return {
                "status": "success",
                "message": "Template deleted successfully",
                "template_id": template_id,
                "registry_result": registry_result
            }
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            return {"status": "error", "message": str(e)}
    
    def render_template(self, template_id: str, context: Dict) -> Dict:
        """
        Render a template with context.
        
        Args:
            template_id: Template ID
            context: Rendering context
            
        Returns:
            Dict: Rendering results
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
            
            # Get template content
            template_content = template_data.get("content")
            if not template_content:
                return {
                    "status": "error",
                    "message": f"Template has no content: {template_id}"
                }
            
            # Create Jinja2 template
            jinja_template = Template(template_content)
            
            # Render template
            rendered_content = jinja_template.render(**context)
            
            # Track template rendering
            self._track_template_event("render", template_data)
            
            return {
                "status": "success",
                "message": "Template rendered successfully",
                "template_id": template_id,
                "rendered_content": rendered_content,
                "context": context
            }
        except Exception as e:
            logger.error(f"Error rendering template: {e}")
            return {"status": "error", "message": str(e)}
    
    def render_template_file(self, template_path: str, context: Dict, output_path: str = None) -> Dict:
        """
        Render a template file with context.
        
        Args:
            template_path: Template file path
            context: Rendering context
            output_path: Output file path
            
        Returns:
            Dict: Rendering results
        """
        try:
            # Check if template file exists
            if not os.path.exists(template_path):
                return {
                    "status": "error",
                    "message": f"Template file not found: {template_path}"
                }
            
            # Get template name
            template_name = os.path.basename(template_path)
            
            # Create Jinja2 environment with template directory
            template_dir = os.path.dirname(template_path)
            env = Environment(
                loader=FileSystemLoader(template_dir),
                autoescape=select_autoescape(['html', 'xml']),
                trim_blocks=True,
                lstrip_blocks=True
            )
            
            # Add custom filters
            env.filters['to_json'] = lambda obj: json.dumps(obj)
            env.filters['to_yaml'] = lambda obj: yaml.dump(obj)
            
            # Get template
            template = env.get_template(template_name)
            
            # Render template
            rendered_content = template.render(**context)
            
            # Save rendered content if output path provided
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                with open(output_path, "w") as f:
                    f.write(rendered_content)
            
            # Track template file rendering
            self._track_template_event("render_file", {
                "template_path": template_path,
                "output_path": output_path
            })
            
            return {
                "status": "success",
                "message": "Template file rendered successfully",
                "template_path": template_path,
                "rendered_content": rendered_content,
                "output_path": output_path,
                "context": context
            }
        except Exception as e:
            logger.error(f"Error rendering template file: {e}")
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
        required_fields = ["name", "type", "content"]
        for field in required_fields:
            if field not in template_data:
                return {
                    "status": "error",
                    "message": f"Missing required field: {field}"
                }
        
        # Validate template type
        if template_data["type"] not in self.template_types:
            return {
                "status": "error",
                "message": f"Invalid template type: {template_data['type']}"
            }
        
        # Validate template format if provided
        if "format" in template_data and template_data["format"] not in self.template_formats:
            return {
                "status": "error",
                "message": f"Invalid template format: {template_data['format']}"
            }
        
        # Validate template content
        try:
            Template(template_data["content"])
        except Exception as e:
            return {
                "status": "error",
                "message": f"Invalid template content: {str(e)}"
            }
        
        return {"status": "success"}
    
    def _load_templates(self) -> None:
        """
        Load templates from storage.
        """
        try:
            if self.storage_type == "file":
                # Create storage directory if it doesn't exist
                os.makedirs(self.storage_path, exist_ok=True)
                
                # Get template files
                template_files = []
                for root, _, files in os.walk(self.storage_path):
                    for file in files:
                        if file.endswith(".json"):
                            template_files.append(os.path.join(root, file))
                
                # Load templates
                for template_file in template_files:
                    try:
                        with open(template_file, "r") as f:
                            template_data = json.load(f)
                            
                            # Add template to templates
                            template_id = template_data.get("template_id")
                            if template_id:
                                self.templates[template_id] = template_data
                    except Exception as e:
                        logger.error(f"Error loading template file {template_file}: {e}")
                
                logger.info(f"Loaded {len(self.templates)} templates from storage")
        except Exception as e:
            logger.error(f"Error loading templates: {e}")
    
    def _save_template(self, template_id: str, template_data: Dict) -> None:
        """
        Save a template to storage.
        
        Args:
            template_id: Template ID
            template_data: Template data
        """
        try:
            if self.storage_type == "file":
                # Create storage directory if it doesn't exist
                os.makedirs(self.storage_path, exist_ok=True)
                
                # Save template to file
                template_file = os.path.join(self.storage_path, f"{template_id}.json")
                with open(template_file, "w") as f:
                    json.dump(template_data, f, indent=2)
                
                logger.info(f"Saved template {template_id} to storage")
        except Exception as e:
            logger.error(f"Error saving template {template_id}: {e}")
    
    def _delete_template(self, template_id: str) -> None:
        """
        Delete a template from storage.
        
        Args:
            template_id: Template ID
        """
        try:
            if self.storage_type == "file":
                # Delete template file
                template_file = os.path.join(self.storage_path, f"{template_id}.json")
                if os.path.exists(template_file):
                    os.remove(template_file)
                
                logger.info(f"Deleted template {template_id} from storage")
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {e}")
    
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
                "template_id": template_data.get("template_id"),
                "template_type": template_data.get("type"),
                "manager_id": self.manager_id
            }
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking template event: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Template Manager.
        
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
                
                # Update Jinja2 environment
                self.jinja_env = Environment(
                    loader=FileSystemLoader(self.storage_path),
                    autoescape=select_autoescape(['html', 'xml']),
                    trim_blocks=True,
                    lstrip_blocks=True
                )
                
                # Add custom Jinja2 filters
                self.jinja_env.filters['to_json'] = lambda obj: json.dumps(obj)
                self.jinja_env.filters['to_yaml'] = lambda obj: yaml.dump(obj)
            
            if "template_types" in config:
                self.template_types = config["template_types"]
            
            if "template_formats" in config:
                self.template_formats = config["template_formats"]
            
            # Configure template registry
            registry_result = None
            if "registry" in config:
                registry_result = self.registry.configure(config["registry"])
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            # Reload templates if storage type or path changed
            if "storage_type" in config or "storage_path" in config:
                self._load_templates()
            
            return {
                "status": "success",
                "message": "Template Manager configured successfully",
                "manager_id": self.manager_id,
                "registry_result": registry_result,
                "analytics_result": analytics_result
            }
        except Exception as e:
            logger.error(f"Error configuring Template Manager: {e}")
            return {"status": "error", "message": str(e)}
