"""
Template System for Industriverse Generative Layer

This module implements the template system for managing and rendering various templates
with protocol-native architecture and MCP/A2A integration.
"""

import json
import logging
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemplateSystem:
    """
    Implements the template system for the Generative Layer.
    Manages and renders various templates with protocol-native architecture.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the template system.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.templates = {}
        self.template_categories = {}
        self.renderers = {}
        self.render_history = {}
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "template_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        # Register default renderers
        self._register_default_renderers()
        
        logger.info("Template System initialized")
    
    def _register_default_renderers(self):
        """Register default template renderers."""
        self.register_renderer("text", self._render_text_template)
        self.register_renderer("html", self._render_html_template)
        self.register_renderer("markdown", self._render_markdown_template)
        self.register_renderer("code", self._render_code_template)
        self.register_renderer("json", self._render_json_template)
    
    def register_template(self, 
                         template_id: str, 
                         name: str,
                         description: str,
                         template_type: str,
                         content: str,
                         variables: List[Dict[str, Any]],
                         category: Optional[str] = None,
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new template.
        
        Args:
            template_id: Unique identifier for the template
            name: Name of the template
            description: Description of the template
            template_type: Type of template (text, html, markdown, code, json)
            content: Template content
            variables: List of variables used in the template
            category: Category of the template (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        if template_id in self.templates:
            logger.warning(f"Template {template_id} already registered")
            return False
        
        if template_type not in self.renderers:
            logger.warning(f"Unknown template type: {template_type}")
            return False
        
        timestamp = time.time()
        
        # Create template record
        template = {
            "id": template_id,
            "name": name,
            "description": description,
            "type": template_type,
            "content": content,
            "variables": variables,
            "category": category,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "version": 1
        }
        
        # Store template
        self.templates[template_id] = template
        
        # Add to category
        if category:
            if category not in self.template_categories:
                self.template_categories[category] = []
            
            self.template_categories[category].append(template_id)
        
        # Store template file
        template_path = os.path.join(self.storage_path, f"{template_id}_template.json")
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info(f"Registered template {template_id}: {name}")
        
        # Emit MCP event for template registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/template/registered",
                {
                    "template_id": template_id,
                    "name": name,
                    "type": template_type
                }
            )
        
        return True
    
    def update_template(self, 
                       template_id: str, 
                       content: Optional[str] = None,
                       variables: Optional[List[Dict[str, Any]]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing template.
        
        Args:
            template_id: ID of the template to update
            content: New template content (optional)
            variables: New list of variables (optional)
            metadata: New metadata (optional)
            
        Returns:
            True if update was successful, False otherwise
        """
        if template_id not in self.templates:
            logger.warning(f"Template {template_id} not found")
            return False
        
        template = self.templates[template_id]
        timestamp = time.time()
        
        # Update template
        if content is not None:
            template["content"] = content
        
        if variables is not None:
            template["variables"] = variables
        
        if metadata is not None:
            template["metadata"].update(metadata)
        
        template["timestamp"] = timestamp
        template["version"] += 1
        
        # Store updated template
        self.templates[template_id] = template
        
        # Store template file
        template_path = os.path.join(self.storage_path, f"{template_id}_template.json")
        with open(template_path, 'w') as f:
            json.dump(template, f, indent=2)
        
        logger.info(f"Updated template {template_id} to version {template['version']}")
        
        # Emit MCP event for template update
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/template/updated",
                {
                    "template_id": template_id,
                    "name": template["name"],
                    "version": template["version"]
                }
            )
        
        return True
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by ID.
        
        Args:
            template_id: ID of the template to retrieve
            
        Returns:
            Template data if found, None otherwise
        """
        if template_id not in self.templates:
            logger.warning(f"Template {template_id} not found")
            return None
        
        return self.templates[template_id]
    
    def get_templates_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        Get all templates in a category.
        
        Args:
            category: Category to retrieve templates for
            
        Returns:
            List of templates in the category
        """
        if category not in self.template_categories:
            logger.warning(f"Category {category} not found")
            return []
        
        template_ids = self.template_categories[category]
        templates = [self.templates[tid] for tid in template_ids if tid in self.templates]
        
        return templates
    
    def register_renderer(self, template_type: str, renderer: Callable) -> bool:
        """
        Register a template renderer.
        
        Args:
            template_type: Type of template to register renderer for
            renderer: Renderer function
            
        Returns:
            True if registration was successful, False otherwise
        """
        if template_type in self.renderers:
            logger.warning(f"Renderer for {template_type} already registered")
            return False
        
        self.renderers[template_type] = renderer
        logger.info(f"Registered renderer for {template_type}")
        
        return True
    
    def render_template(self, 
                       template_id: str, 
                       variables: Dict[str, Any],
                       render_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Render a template with the provided variables.
        
        Args:
            template_id: ID of the template to render
            variables: Variables to use in rendering
            render_id: Optional ID for the render (generated if not provided)
            
        Returns:
            Render result if successful, None otherwise
        """
        if template_id not in self.templates:
            logger.warning(f"Template {template_id} not found")
            return None
        
        template = self.templates[template_id]
        template_type = template["type"]
        
        if template_type not in self.renderers:
            logger.warning(f"No renderer found for template type: {template_type}")
            return None
        
        # Generate render ID if not provided
        if render_id is None:
            render_id = f"render_{uuid.uuid4().hex[:8]}"
        
        timestamp = time.time()
        
        # Validate variables
        required_vars = {var["name"] for var in template["variables"] if var.get("required", False)}
        provided_vars = set(variables.keys())
        
        missing_vars = required_vars - provided_vars
        if missing_vars:
            logger.warning(f"Missing required variables: {missing_vars}")
            
            # Create failure result
            result = {
                "id": render_id,
                "template_id": template_id,
                "timestamp": timestamp,
                "status": "failed",
                "reason": f"Missing required variables: {missing_vars}",
                "variables": variables
            }
            
            self.render_history[render_id] = result
            return result
        
        # Render template
        try:
            renderer = self.renderers[template_type]
            rendered_content = renderer(template["content"], variables)
            
            # Create success result
            result = {
                "id": render_id,
                "template_id": template_id,
                "timestamp": timestamp,
                "status": "success",
                "content": rendered_content,
                "variables": variables,
                "template_name": template["name"],
                "template_type": template_type
            }
            
            self.render_history[render_id] = result
            
            # Store render result
            result_path = os.path.join(self.storage_path, f"{render_id}_result.json")
            with open(result_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Store rendered content
            content_path = os.path.join(self.storage_path, f"{render_id}_content.{self._get_extension(template_type)}")
            with open(content_path, 'w') as f:
                f.write(rendered_content)
            
            logger.info(f"Rendered template {template_id} as {render_id}")
            
            # Emit MCP event for template rendering
            if self.agent_core:
                self.agent_core.send_mcp_event(
                    "generative_layer/template/rendered",
                    {
                        "render_id": render_id,
                        "template_id": template_id,
                        "template_name": template["name"]
                    }
                )
            
            return result
        
        except Exception as e:
            logger.error(f"Error rendering template {template_id}: {str(e)}")
            
            # Create failure result
            result = {
                "id": render_id,
                "template_id": template_id,
                "timestamp": timestamp,
                "status": "failed",
                "reason": f"Rendering error: {str(e)}",
                "variables": variables
            }
            
            self.render_history[render_id] = result
            return result
    
    def get_render_result(self, render_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a render result by ID.
        
        Args:
            render_id: ID of the render result to retrieve
            
        Returns:
            Render result if found, None otherwise
        """
        if render_id not in self.render_history:
            logger.warning(f"Render result {render_id} not found")
            return None
        
        return self.render_history[render_id]
    
    def _render_text_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Render a text template.
        
        Args:
            template_content: Template content
            variables: Variables to use in rendering
            
        Returns:
            Rendered content
        """
        # Simple variable substitution
        result = template_content
        
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            result = result.replace(placeholder, str(var_value))
        
        return result
    
    def _render_html_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Render an HTML template.
        
        Args:
            template_content: Template content
            variables: Variables to use in rendering
            
        Returns:
            Rendered content
        """
        # For now, use the same implementation as text
        return self._render_text_template(template_content, variables)
    
    def _render_markdown_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Render a Markdown template.
        
        Args:
            template_content: Template content
            variables: Variables to use in rendering
            
        Returns:
            Rendered content
        """
        # For now, use the same implementation as text
        return self._render_text_template(template_content, variables)
    
    def _render_code_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Render a code template.
        
        Args:
            template_content: Template content
            variables: Variables to use in rendering
            
        Returns:
            Rendered content
        """
        # For now, use the same implementation as text
        return self._render_text_template(template_content, variables)
    
    def _render_json_template(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Render a JSON template.
        
        Args:
            template_content: Template content
            variables: Variables to use in rendering
            
        Returns:
            Rendered content
        """
        try:
            # Parse template as JSON
            template_json = json.loads(template_content)
            
            # Replace variables in the JSON structure
            def replace_vars(obj):
                if isinstance(obj, dict):
                    return {k: replace_vars(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [replace_vars(item) for item in obj]
                elif isinstance(obj, str):
                    # Check if this is a variable reference
                    if obj.startswith("{{") and obj.endswith("}}"):
                        var_name = obj[2:-2].strip()
                        if var_name in variables:
                            return variables[var_name]
                    return self._render_text_template(obj, variables)
                else:
                    return obj
            
            result_json = replace_vars(template_json)
            
            # Convert back to JSON string
            return json.dumps(result_json, indent=2)
        
        except json.JSONDecodeError:
            # If not valid JSON, treat as text
            return self._render_text_template(template_content, variables)
    
    def _get_extension(self, template_type: str) -> str:
        """
        Get the file extension for a template type.
        
        Args:
            template_type: Template type
            
        Returns:
            File extension
        """
        extensions = {
            "text": "txt",
            "html": "html",
            "markdown": "md",
            "code": "txt",
            "json": "json"
        }
        
        return extensions.get(template_type, "txt")
    
    def create_template_for_offer(self, 
                                offer_type: str,
                                offer_name: str,
                                offer_description: str) -> Optional[str]:
        """
        Create a template for a specific low-ticket offer.
        
        Args:
            offer_type: Type of offer
            offer_name: Name of the offer
            offer_description: Description of the offer
            
        Returns:
            Template ID if successful, None otherwise
        """
        # Generate a unique template ID
        template_id = f"offer_{offer_type}_{uuid.uuid4().hex[:8]}"
        
        # Determine template type and content based on offer type
        template_type = "markdown"
        variables = []
        content = ""
        
        if offer_type == "document_generation":
            template_type = "markdown"
            content = """# {{title}}

## Overview
{{overview}}

## Details
{{details}}

## Specifications
- **Client**: {{client_name}}
- **Industry**: {{industry}}
- **Date**: {{date}}

## Requirements
{{requirements}}

## Deliverables
{{deliverables}}

## Timeline
{{timeline}}

## Contact Information
{{contact_info}}
"""
            variables = [
                {"name": "title", "type": "string", "description": "Document title", "required": True},
                {"name": "overview", "type": "string", "description": "Brief overview", "required": True},
                {"name": "details", "type": "string", "description": "Detailed information", "required": True},
                {"name": "client_name", "type": "string", "description": "Client name", "required": True},
                {"name": "industry", "type": "string", "description": "Industry", "required": True},
                {"name": "date", "type": "string", "description": "Date", "required": True},
                {"name": "requirements", "type": "string", "description": "Requirements", "required": True},
                {"name": "deliverables", "type": "string", "description": "Deliverables", "required": True},
                {"name": "timeline", "type": "string", "description": "Timeline", "required": True},
                {"name": "contact_info", "type": "string", "description": "Contact information", "required": False}
            ]
        
        elif offer_type == "code_generation":
            template_type = "code"
            content = """/**
 * {{file_name}}
 * {{description}}
 * 
 * @author {{author}}
 * @date {{date}}
 */

{{imports}}

/**
 * {{class_description}}
 */
class {{class_name}} {
    /**
     * Constructor
     */
    constructor({{constructor_params}}) {
        {{constructor_body}}
    }
    
    /**
     * {{method_description}}
     */
    {{method_name}}({{method_params}}) {
        {{method_body}}
    }
}

{{exports}}
"""
            variables = [
                {"name": "file_name", "type": "string", "description": "File name", "required": True},
                {"name": "description", "type": "string", "description": "File description", "required": True},
                {"name": "author", "type": "string", "description": "Author name", "required": True},
                {"name": "date", "type": "string", "description": "Date", "required": True},
                {"name": "imports", "type": "string", "description": "Import statements", "required": False},
                {"name": "class_description", "type": "string", "description": "Class description", "required": True},
                {"name": "class_name", "type": "string", "description": "Class name", "required": True},
                {"name": "constructor_params", "type": "string", "description": "Constructor parameters", "required": False},
                {"name": "constructor_body", "type": "string", "description": "Constructor body", "required": False},
                {"name": "method_description", "type": "string", "description": "Method description", "required": True},
                {"name": "method_name", "type": "string", "description": "Method name", "required": True},
                {"name": "method_params", "type": "string", "description": "Method parameters", "required": False},
                {"name": "method_body", "type": "string", "description": "Method body", "required": True},
                {"name": "exports", "type": "string", "description": "Export statements", "required": False}
            ]
        
        elif offer_type == "data_analysis":
            template_type = "markdown"
            content = """# {{title}} - Data Analysis Report

## Executive Summary
{{executive_summary}}

## Data Overview
{{data_overview}}

## Methodology
{{methodology}}

## Key Findings
{{key_findings}}

## Detailed Analysis
{{detailed_analysis}}

## Visualizations
{{visualizations}}

## Conclusions
{{conclusions}}

## Recommendations
{{recommendations}}

## Appendix
{{appendix}}
"""
            variables = [
                {"name": "title", "type": "string", "description": "Report title", "required": True},
                {"name": "executive_summary", "type": "string", "description": "Executive summary", "required": True},
                {"name": "data_overview", "type": "string", "description": "Data overview", "required": True},
                {"name": "methodology", "type": "string", "description": "Methodology", "required": True},
                {"name": "key_findings", "type": "string", "description": "Key findings", "required": True},
                {"name": "detailed_analysis", "type": "string", "description": "Detailed analysis", "required": True},
                {"name": "visualizations", "type": "string", "description": "Visualizations", "required": False},
                {"name": "conclusions", "type": "string", "description": "Conclusions", "required": True},
                {"name": "recommendations", "type": "string", "description": "Recommendations", "required": True},
                {"name": "appendix", "type": "string", "description": "Appendix", "required": False}
            ]
        
        else:
            # Generic template
            template_type = "markdown"
            content = """# {{title}}

## Overview
{{overview}}

## Details
{{details}}

## Additional Information
{{additional_info}}
"""
            variables = [
                {"name": "title", "type": "string", "description": "Title", "required": True},
                {"name": "overview", "type": "string", "description": "Overview", "required": True},
                {"name": "details", "type": "string", "description": "Details", "required": True},
                {"name": "additional_info", "type": "string", "description": "Additional information", "required": False}
            ]
        
        # Register template
        success = self.register_template(
            template_id=template_id,
            name=offer_name,
            description=offer_description,
            template_type=template_type,
            content=content,
            variables=variables,
            category=offer_type,
            metadata={
                "offer_type": offer_type,
                "generated": True,
                "timestamp": time.time()
            }
        )
        
        if success:
            return template_id
        else:
            return None
    
    def export_template_data(self) -> Dict[str, Any]:
        """
        Export template data for persistence.
        
        Returns:
            Template data
        """
        return {
            "templates": self.templates,
            "template_categories": self.template_categories
        }
    
    def import_template_data(self, template_data: Dict[str, Any]) -> None:
        """
        Import template data from persistence.
        
        Args:
            template_data: Template data to import
        """
        if "templates" in template_data:
            self.templates = template_data["templates"]
        
        if "template_categories" in template_data:
            self.template_categories = template_data["template_categories"]
        
        logger.info("Imported template data")
