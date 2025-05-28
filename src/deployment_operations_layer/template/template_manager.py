"""
Template Manager - Main interface for template management

This module provides the main interface for template management, coordinating
the various template-related components.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

from .template_versioning_manager import TemplateVersioningManager
from .template_registry import TemplateRegistry
from .template_renderer import TemplateRenderer
from .template_validator import TemplateValidator
from .template_import_export_manager import TemplateImportExportManager

logger = logging.getLogger(__name__)

class TemplateManager:
    """
    Main interface for template management.
    
    This component is responsible for coordinating the various template-related
    components, providing a unified interface for template management.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Template Manager.
        
        Args:
            config: Configuration dictionary for the manager
        """
        self.config = config or {}
        
        # Initialize subcomponents
        self.versioning_manager = TemplateVersioningManager(self.config.get("versioning", {}))
        self.registry = TemplateRegistry(self.config.get("registry", {}))
        self.renderer = TemplateRenderer(self.config.get("renderer", {}))
        self.validator = TemplateValidator(self.config.get("validator", {}))
        self.import_export_manager = TemplateImportExportManager(self.config.get("import_export", {}))
        
        logger.info("Initializing Template Manager")
    
    def initialize(self):
        """Initialize the manager and its subcomponents."""
        logger.info("Initializing Template Manager")
        
        # Initialize subcomponents
        self.versioning_manager.initialize()
        self.registry.initialize()
        self.renderer.initialize()
        self.validator.initialize()
        self.import_export_manager.initialize()
        
        logger.info("Template Manager initialization complete")
        return True
    
    def register_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a template.
        
        Args:
            template: Template definition
            
        Returns:
            Dictionary with registration result
        """
        logger.info(f"Registering template {template.get('id', 'unknown')}")
        
        # Validate template
        validation_result = self.validator.validate_template(template)
        
        if not validation_result["valid"]:
            logger.error(f"Template validation failed: {validation_result.get('errors', [])}")
            return {"success": False, "error": f"Template validation failed: {validation_result.get('errors', [])}"}
        
        # Register template in registry
        registry_result = self.registry.register_template(template)
        
        if not registry_result["success"]:
            logger.error(f"Failed to register template in registry: {registry_result.get('error', '')}")
            return registry_result
        
        # Register template for versioning
        template_id = registry_result["template_id"]
        metadata = {
            "name": template.get("name", "Unknown"),
            "description": template.get("description", ""),
            "template_type": template.get("template_type", "unknown")
        }
        
        versioning_result = self.versioning_manager.register_template(template_id, template, metadata)
        
        if not versioning_result["success"]:
            # Rollback registry registration
            self.registry.unregister_template(template_id)
            
            logger.error(f"Failed to register template for versioning: {versioning_result.get('error', '')}")
            return versioning_result
        
        logger.info(f"Successfully registered template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "version": versioning_result["version"]
        }
    
    def unregister_template(self, template_id: str) -> Dict[str, Any]:
        """
        Unregister a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with unregistration result
        """
        logger.info(f"Unregistering template {template_id}")
        
        # Unregister template from registry
        registry_result = self.registry.unregister_template(template_id)
        
        if not registry_result["success"]:
            logger.error(f"Failed to unregister template from registry: {registry_result.get('error', '')}")
            return registry_result
        
        # Unregister template from versioning
        versioning_result = self.versioning_manager.unregister_template(template_id)
        
        if not versioning_result["success"]:
            logger.error(f"Failed to unregister template from versioning: {versioning_result.get('error', '')}")
            # Continue anyway, as the template is already unregistered from the registry
        
        logger.info(f"Successfully unregistered template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id
        }
    
    def get_template(self, template_id: str, version_id: str = None) -> Dict[str, Any]:
        """
        Get a template.
        
        Args:
            template_id: ID of the template
            version_id: ID of the version (if None, returns latest version)
            
        Returns:
            Dictionary with template retrieval result
        """
        logger.info(f"Getting template {template_id}")
        
        # Get template from versioning
        versioning_result = self.versioning_manager.get_version(template_id, version_id)
        
        if not versioning_result["success"]:
            logger.error(f"Failed to get template from versioning: {versioning_result.get('error', '')}")
            return versioning_result
        
        logger.info(f"Successfully retrieved template {template_id}")
        
        return {
            "success": True,
            "template": versioning_result["template"],
            "template_id": template_id,
            "version": versioning_result["version"]
        }
    
    def update_template(self, template_id: str, template: Dict[str, Any], 
                       comment: str = "") -> Dict[str, Any]:
        """
        Update a template.
        
        Args:
            template_id: ID of the template
            template: Updated template definition
            comment: Comment for the update
            
        Returns:
            Dictionary with update result
        """
        logger.info(f"Updating template {template_id}")
        
        # Validate template
        validation_result = self.validator.validate_template(template)
        
        if not validation_result["valid"]:
            logger.error(f"Template validation failed: {validation_result.get('errors', [])}")
            return {"success": False, "error": f"Template validation failed: {validation_result.get('errors', [])}"}
        
        # Update template in registry
        registry_result = self.registry.update_template(template_id, template)
        
        if not registry_result["success"]:
            logger.error(f"Failed to update template in registry: {registry_result.get('error', '')}")
            return registry_result
        
        # Create new version
        versioning_result = self.versioning_manager.create_version(template_id, template, comment)
        
        if not versioning_result["success"]:
            logger.error(f"Failed to create new version: {versioning_result.get('error', '')}")
            return versioning_result
        
        logger.info(f"Successfully updated template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "version": versioning_result["version"]
        }
    
    def search_templates(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for templates.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        logger.info("Searching templates")
        
        # Search templates in registry
        search_result = self.registry.search_templates(query)
        
        if not search_result["success"]:
            logger.error(f"Failed to search templates: {search_result.get('error', '')}")
            return search_result
        
        logger.info(f"Found {search_result['total']} templates")
        
        return search_result
    
    def render_template(self, template_id: str, variables: Dict[str, Any], 
                       version_id: str = None) -> Dict[str, Any]:
        """
        Render a template.
        
        Args:
            template_id: ID of the template
            variables: Variables for substitution
            version_id: ID of the version (if None, uses latest version)
            
        Returns:
            Dictionary with rendering result
        """
        logger.info(f"Rendering template {template_id}")
        
        # Get template
        template_result = self.get_template(template_id, version_id)
        
        if not template_result["success"]:
            logger.error(f"Failed to get template: {template_result.get('error', '')}")
            return template_result
        
        # Render template
        render_result = self.renderer.render_template(template_result["template"], variables)
        
        if not render_result["success"]:
            logger.error(f"Failed to render template: {render_result.get('error', '')}")
            return render_result
        
        logger.info(f"Successfully rendered template {template_id}")
        
        return render_result
    
    def render_template_to_files(self, template_id: str, variables: Dict[str, Any], 
                               output_dir: str, version_id: str = None) -> Dict[str, Any]:
        """
        Render a template to files.
        
        Args:
            template_id: ID of the template
            variables: Variables for substitution
            output_dir: Directory to write output files to
            version_id: ID of the version (if None, uses latest version)
            
        Returns:
            Dictionary with rendering result
        """
        logger.info(f"Rendering template {template_id} to files")
        
        # Get template
        template_result = self.get_template(template_id, version_id)
        
        if not template_result["success"]:
            logger.error(f"Failed to get template: {template_result.get('error', '')}")
            return template_result
        
        # Render template to files
        render_result = self.renderer.render_template_to_files(
            template_result["template"], variables, output_dir)
        
        if not render_result["success"]:
            logger.error(f"Failed to render template to files: {render_result.get('error', '')}")
            return render_result
        
        logger.info(f"Successfully rendered template {template_id} to files")
        
        return render_result
    
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
        logger.info(f"Comparing versions {version_id1} and {version_id2} of template {template_id}")
        
        # Compare versions
        comparison_result = self.versioning_manager.compare_versions(
            template_id, version_id1, version_id2)
        
        if not comparison_result["success"]:
            logger.error(f"Failed to compare versions: {comparison_result.get('error', '')}")
            return comparison_result
        
        logger.info(f"Successfully compared versions of template {template_id}")
        
        return comparison_result
    
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
        
        # Get template version
        version_result = self.versioning_manager.get_version(template_id, version_id)
        
        if not version_result["success"]:
            logger.error(f"Failed to get version: {version_result.get('error', '')}")
            return version_result
        
        # Update template in registry
        registry_result = self.registry.update_template(template_id, version_result["template"])
        
        if not registry_result["success"]:
            logger.error(f"Failed to update template in registry: {registry_result.get('error', '')}")
            return registry_result
        
        # Revert to version
        revert_result = self.versioning_manager.revert_to_version(template_id, version_id)
        
        if not revert_result["success"]:
            logger.error(f"Failed to revert to version: {revert_result.get('error', '')}")
            return revert_result
        
        logger.info(f"Successfully reverted template {template_id} to version {version_id}")
        
        return revert_result
    
    def export_template(self, template_id: str, format: str, output_path: str, 
                       version_id: str = None) -> Dict[str, Any]:
        """
        Export a template to a file.
        
        Args:
            template_id: ID of the template
            format: Export format (json, yaml, zip)
            output_path: Path to write the exported template to
            version_id: ID of the version (if None, uses latest version)
            
        Returns:
            Dictionary with export result
        """
        logger.info(f"Exporting template {template_id} to {format} format")
        
        # Get template
        template_result = self.get_template(template_id, version_id)
        
        if not template_result["success"]:
            logger.error(f"Failed to get template: {template_result.get('error', '')}")
            return template_result
        
        # Export template
        export_result = self.import_export_manager.export_template(
            template_result["template"], format, output_path)
        
        if not export_result["success"]:
            logger.error(f"Failed to export template: {export_result.get('error', '')}")
            return export_result
        
        logger.info(f"Successfully exported template {template_id} to {output_path}")
        
        return export_result
    
    def import_template(self, input_path: str, format: str = None) -> Dict[str, Any]:
        """
        Import a template from a file.
        
        Args:
            input_path: Path to the file to import
            format: Import format (json, yaml, zip, auto)
            
        Returns:
            Dictionary with import result
        """
        logger.info(f"Importing template from {input_path}")
        
        # Import template
        import_result = self.import_export_manager.import_template(input_path, format)
        
        if not import_result["success"]:
            logger.error(f"Failed to import template: {import_result.get('error', '')}")
            return import_result
        
        # Register imported template
        template = import_result["template"]
        register_result = self.register_template(template)
        
        if not register_result["success"]:
            logger.error(f"Failed to register imported template: {register_result.get('error', '')}")
            return register_result
        
        logger.info(f"Successfully imported and registered template {register_result['template_id']}")
        
        return {
            "success": True,
            "template_id": register_result["template_id"],
            "version": register_result["version"],
            "format": import_result["format"]
        }
    
    def get_template_categories(self) -> Dict[str, Any]:
        """
        Get all template categories.
        
        Returns:
            Dictionary with categories
        """
        logger.info("Getting template categories")
        
        # Get categories from registry
        categories_result = self.registry.get_categories()
        
        if not categories_result["success"]:
            logger.error(f"Failed to get categories: {categories_result.get('error', '')}")
            return categories_result
        
        logger.info(f"Retrieved {len(categories_result['categories'])} categories")
        
        return categories_result
    
    def get_template_tags(self) -> Dict[str, Any]:
        """
        Get all template tags.
        
        Returns:
            Dictionary with tags
        """
        logger.info("Getting template tags")
        
        # Get tags from registry
        tags_result = self.registry.get_tags()
        
        if not tags_result["success"]:
            logger.error(f"Failed to get tags: {tags_result.get('error', '')}")
            return tags_result
        
        logger.info(f"Retrieved {len(tags_result['tags'])} tags")
        
        return tags_result
    
    def get_template_versions(self, template_id: str) -> Dict[str, Any]:
        """
        Get all versions of a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with versions
        """
        logger.info(f"Getting versions of template {template_id}")
        
        # Get versions from versioning manager
        versions_result = self.versioning_manager.get_versions(template_id)
        
        if not versions_result["success"]:
            logger.error(f"Failed to get versions: {versions_result.get('error', '')}")
            return versions_result
        
        logger.info(f"Retrieved {len(versions_result['versions'])} versions")
        
        return versions_result
    
    def get_template_metadata(self, template_id: str) -> Dict[str, Any]:
        """
        Get metadata for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with metadata
        """
        logger.info(f"Getting metadata for template {template_id}")
        
        # Get metadata from versioning manager
        metadata_result = self.versioning_manager.get_template_metadata(template_id)
        
        if not metadata_result["success"]:
            logger.error(f"Failed to get metadata: {metadata_result.get('error', '')}")
            return metadata_result
        
        logger.info(f"Retrieved metadata for template {template_id}")
        
        return metadata_result
    
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
        
        # Update metadata in versioning manager
        metadata_result = self.versioning_manager.update_template_metadata(template_id, metadata)
        
        if not metadata_result["success"]:
            logger.error(f"Failed to update metadata: {metadata_result.get('error', '')}")
            return metadata_result
        
        logger.info(f"Updated metadata for template {template_id}")
        
        return metadata_result
    
    def get_template_count(self) -> int:
        """
        Get the number of templates in the registry.
        
        Returns:
            Number of templates
        """
        return self.registry.get_template_count()
    
    def get_all_templates(self) -> Dict[str, Any]:
        """
        Get all templates in the registry.
        
        Returns:
            Dictionary with all templates
        """
        return self.registry.get_all_templates()
    
    def register_schema(self, schema_id: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a schema.
        
        Args:
            schema_id: ID of the schema
            schema: Schema definition
            
        Returns:
            Dictionary with registration result
        """
        logger.info(f"Registering schema {schema_id}")
        
        # Register schema in validator
        schema_result = self.validator.register_schema(schema_id, schema)
        
        if not schema_result["success"]:
            logger.error(f"Failed to register schema: {schema_result.get('error', '')}")
            return schema_result
        
        logger.info(f"Registered schema {schema_id}")
        
        return schema_result
    
    def get_schema(self, schema_id: str) -> Dict[str, Any]:
        """
        Get a schema.
        
        Args:
            schema_id: ID of the schema
            
        Returns:
            Dictionary with schema retrieval result
        """
        logger.info(f"Getting schema {schema_id}")
        
        # Get schema from validator
        schema_result = self.validator.get_schema(schema_id)
        
        if not schema_result["success"]:
            logger.error(f"Failed to get schema: {schema_result.get('error', '')}")
            return schema_result
        
        logger.info(f"Retrieved schema {schema_id}")
        
        return schema_result
    
    def get_all_schemas(self) -> Dict[str, Any]:
        """
        Get all schemas.
        
        Returns:
            Dictionary with all schemas
        """
        logger.info("Getting all schemas")
        
        # Get all schemas from validator
        schemas_result = self.validator.get_all_schemas()
        
        if not schemas_result["success"]:
            logger.error(f"Failed to get schemas: {schemas_result.get('error', '')}")
            return schemas_result
        
        logger.info(f"Retrieved {len(schemas_result['schemas'])} schemas")
        
        return schemas_result
