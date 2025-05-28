"""
Template Registry - Manages the registry of deployment templates

This module manages the registry of deployment templates, providing storage,
retrieval, and search capabilities for templates.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class TemplateRegistry:
    """
    Manages the registry of deployment templates.
    
    This component is responsible for managing the registry of deployment templates,
    providing storage, retrieval, and search capabilities for templates.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Template Registry.
        
        Args:
            config: Configuration dictionary for the registry
        """
        self.config = config or {}
        self.templates = {}  # Template ID -> Template
        self.template_index = {}  # Index for searching templates
        self.template_categories = {}  # Category -> List of template IDs
        self.template_tags = {}  # Tag -> List of template IDs
        
        logger.info("Initializing Template Registry")
    
    def initialize(self):
        """Initialize the registry and load templates."""
        logger.info("Initializing Template Registry")
        
        # Load templates
        self._load_templates()
        
        # Build indexes
        self._build_indexes()
        
        logger.info(f"Loaded {len(self.templates)} templates")
        return True
    
    def register_template(self, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a template in the registry.
        
        Args:
            template: Template definition
            
        Returns:
            Dictionary with registration result
        """
        logger.info("Registering template")
        
        # Validate template
        if not self._validate_template(template):
            logger.error("Invalid template")
            return {"success": False, "error": "Invalid template"}
        
        # Generate template ID if not provided
        template_id = template.get("id")
        if not template_id:
            template_id = str(uuid.uuid4())
            template["id"] = template_id
        
        # Check if template already exists
        if template_id in self.templates:
            logger.warning(f"Template {template_id} already exists")
            return {"success": False, "error": "Template already exists"}
        
        # Add timestamp if not provided
        if "created" not in template:
            template["created"] = datetime.now().isoformat()
        
        # Register template
        self.templates[template_id] = template
        
        # Update indexes
        self._update_indexes(template_id, template)
        
        # Save templates
        self._save_templates()
        
        logger.info(f"Registered template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id
        }
    
    def unregister_template(self, template_id: str) -> Dict[str, Any]:
        """
        Unregister a template from the registry.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with unregistration result
        """
        logger.info(f"Unregistering template {template_id}")
        
        # Check if template exists
        if template_id not in self.templates:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Get template
        template = self.templates[template_id]
        
        # Remove template
        del self.templates[template_id]
        
        # Update indexes
        self._remove_from_indexes(template_id, template)
        
        # Save templates
        self._save_templates()
        
        logger.info(f"Unregistered template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id
        }
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """
        Get a template from the registry.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with template retrieval result
        """
        # Check if template exists
        if template_id not in self.templates:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Get template
        template = self.templates[template_id]
        
        logger.info(f"Retrieved template {template_id}")
        
        return {
            "success": True,
            "template": template
        }
    
    def update_template(self, template_id: str, template: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a template in the registry.
        
        Args:
            template_id: ID of the template
            template: Updated template definition
            
        Returns:
            Dictionary with update result
        """
        logger.info(f"Updating template {template_id}")
        
        # Check if template exists
        if template_id not in self.templates:
            logger.warning(f"Template {template_id} does not exist")
            return {"success": False, "error": "Template does not exist"}
        
        # Validate template
        if not self._validate_template(template):
            logger.error("Invalid template")
            return {"success": False, "error": "Invalid template"}
        
        # Ensure template ID is correct
        if "id" in template and template["id"] != template_id:
            logger.error("Template ID mismatch")
            return {"success": False, "error": "Template ID mismatch"}
        
        template["id"] = template_id
        
        # Get old template
        old_template = self.templates[template_id]
        
        # Update template
        self.templates[template_id] = template
        
        # Update indexes
        self._remove_from_indexes(template_id, old_template)
        self._update_indexes(template_id, template)
        
        # Save templates
        self._save_templates()
        
        logger.info(f"Updated template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id
        }
    
    def search_templates(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for templates in the registry.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        logger.info("Searching templates")
        
        # Initialize result set with all template IDs
        result_set = set(self.templates.keys())
        
        # Apply filters
        if "category" in query:
            category = query["category"]
            if category in self.template_categories:
                category_templates = set(self.template_categories[category])
                result_set = result_set.intersection(category_templates)
            else:
                # No templates in this category
                result_set = set()
        
        if "tags" in query and query["tags"]:
            tags = query["tags"]
            for tag in tags:
                if tag in self.template_tags:
                    tag_templates = set(self.template_tags[tag])
                    result_set = result_set.intersection(tag_templates)
                else:
                    # No templates with this tag
                    result_set = set()
                    break
        
        if "text" in query and query["text"]:
            text = query["text"].lower()
            text_results = set()
            
            # Search in template index
            for template_id, indexed_text in self.template_index.items():
                if text in indexed_text:
                    text_results.add(template_id)
            
            result_set = result_set.intersection(text_results)
        
        # Get templates
        results = []
        for template_id in result_set:
            template = self.templates[template_id]
            results.append(template)
        
        # Sort results
        if "sort_by" in query:
            sort_by = query["sort_by"]
            reverse = query.get("sort_order", "asc").lower() == "desc"
            
            if sort_by in ["name", "created", "category"]:
                results.sort(key=lambda t: t.get(sort_by, ""), reverse=reverse)
        
        # Apply pagination
        page = query.get("page", 1)
        page_size = query.get("page_size", 10)
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        paginated_results = results[start_index:end_index]
        
        logger.info(f"Found {len(results)} templates, returning {len(paginated_results)} for page {page}")
        
        return {
            "success": True,
            "total": len(results),
            "page": page,
            "page_size": page_size,
            "templates": paginated_results
        }
    
    def get_categories(self) -> Dict[str, Any]:
        """
        Get all template categories.
        
        Returns:
            Dictionary with categories
        """
        categories = []
        
        for category, template_ids in self.template_categories.items():
            categories.append({
                "name": category,
                "count": len(template_ids)
            })
        
        # Sort categories by name
        categories.sort(key=lambda c: c["name"])
        
        logger.info(f"Retrieved {len(categories)} categories")
        
        return {
            "success": True,
            "categories": categories
        }
    
    def get_tags(self) -> Dict[str, Any]:
        """
        Get all template tags.
        
        Returns:
            Dictionary with tags
        """
        tags = []
        
        for tag, template_ids in self.template_tags.items():
            tags.append({
                "name": tag,
                "count": len(template_ids)
            })
        
        # Sort tags by name
        tags.sort(key=lambda t: t["name"])
        
        logger.info(f"Retrieved {len(tags)} tags")
        
        return {
            "success": True,
            "tags": tags
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
        required_fields = ["name", "description", "schema_version", "template_type"]
        for field in required_fields:
            if field not in template:
                logger.error(f"Missing required field in template: {field}")
                return False
        
        # Check schema version
        schema_version = template.get("schema_version")
        if not isinstance(schema_version, str):
            logger.error("Schema version must be a string")
            return False
        
        # Check template type
        template_type = template.get("template_type")
        valid_types = ["deployment", "environment", "capsule", "workflow"]
        if template_type not in valid_types:
            logger.error(f"Invalid template type: {template_type}")
            return False
        
        # Check category
        if "category" in template and not isinstance(template["category"], str):
            logger.error("Category must be a string")
            return False
        
        # Check tags
        if "tags" in template:
            if not isinstance(template["tags"], list):
                logger.error("Tags must be a list")
                return False
            
            for tag in template["tags"]:
                if not isinstance(tag, str):
                    logger.error("Tags must be strings")
                    return False
        
        # Additional validation could be added here
        
        return True
    
    def _update_indexes(self, template_id: str, template: Dict[str, Any]):
        """
        Update indexes for a template.
        
        Args:
            template_id: ID of the template
            template: Template definition
        """
        # Update category index
        if "category" in template and template["category"]:
            category = template["category"]
            if category not in self.template_categories:
                self.template_categories[category] = []
            
            if template_id not in self.template_categories[category]:
                self.template_categories[category].append(template_id)
        
        # Update tag index
        if "tags" in template and template["tags"]:
            for tag in template["tags"]:
                if tag not in self.template_tags:
                    self.template_tags[tag] = []
                
                if template_id not in self.template_tags[tag]:
                    self.template_tags[tag].append(template_id)
        
        # Update text index
        indexed_text = self._create_indexed_text(template)
        self.template_index[template_id] = indexed_text
    
    def _remove_from_indexes(self, template_id: str, template: Dict[str, Any]):
        """
        Remove a template from indexes.
        
        Args:
            template_id: ID of the template
            template: Template definition
        """
        # Remove from category index
        if "category" in template and template["category"]:
            category = template["category"]
            if category in self.template_categories and template_id in self.template_categories[category]:
                self.template_categories[category].remove(template_id)
                
                # Remove category if empty
                if not self.template_categories[category]:
                    del self.template_categories[category]
        
        # Remove from tag index
        if "tags" in template and template["tags"]:
            for tag in template["tags"]:
                if tag in self.template_tags and template_id in self.template_tags[tag]:
                    self.template_tags[tag].remove(template_id)
                    
                    # Remove tag if empty
                    if not self.template_tags[tag]:
                        del self.template_tags[tag]
        
        # Remove from text index
        if template_id in self.template_index:
            del self.template_index[template_id]
    
    def _create_indexed_text(self, template: Dict[str, Any]) -> str:
        """
        Create indexed text for a template.
        
        Args:
            template: Template definition
            
        Returns:
            Indexed text
        """
        # Combine searchable fields
        searchable_fields = ["name", "description", "category", "template_type"]
        text_parts = []
        
        for field in searchable_fields:
            if field in template and template[field]:
                text_parts.append(str(template[field]))
        
        # Add tags
        if "tags" in template and template["tags"]:
            text_parts.extend(template["tags"])
        
        # Combine and normalize
        indexed_text = " ".join(text_parts).lower()
        
        return indexed_text
    
    def _build_indexes(self):
        """Build indexes for all templates."""
        logger.info("Building template indexes")
        
        # Clear indexes
        self.template_index = {}
        self.template_categories = {}
        self.template_tags = {}
        
        # Build indexes
        for template_id, template in self.templates.items():
            self._update_indexes(template_id, template)
        
        logger.info(f"Built indexes with {len(self.template_categories)} categories and {len(self.template_tags)} tags")
    
    def _load_templates(self):
        """Load templates from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.templates = {}
            logger.info("Loaded templates")
        except Exception as e:
            logger.error(f"Failed to load templates: {str(e)}")
    
    def _save_templates(self):
        """Save templates to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.templates)} templates")
        except Exception as e:
            logger.error(f"Failed to save templates: {str(e)}")
    
    def get_template_count(self) -> int:
        """
        Get the number of templates in the registry.
        
        Returns:
            Number of templates
        """
        return len(self.templates)
    
    def get_all_templates(self) -> Dict[str, Any]:
        """
        Get all templates in the registry.
        
        Returns:
            Dictionary with all templates
        """
        return {
            "success": True,
            "templates": list(self.templates.values())
        }
    
    def get_templates_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get templates by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            Dictionary with templates in the category
        """
        if category not in self.template_categories:
            return {
                "success": True,
                "templates": []
            }
        
        templates = []
        for template_id in self.template_categories[category]:
            if template_id in self.templates:
                templates.append(self.templates[template_id])
        
        return {
            "success": True,
            "templates": templates
        }
    
    def get_templates_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Get templates by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            Dictionary with templates with the tag
        """
        if tag not in self.template_tags:
            return {
                "success": True,
                "templates": []
            }
        
        templates = []
        for template_id in self.template_tags[tag]:
            if template_id in self.templates:
                templates.append(self.templates[template_id])
        
        return {
            "success": True,
            "templates": templates
        }
