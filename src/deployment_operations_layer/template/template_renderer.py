"""
Template Renderer - Renders templates with variable substitution

This module renders templates with variable substitution, transforming
template definitions into concrete deployment artifacts.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import uuid
import os
import jinja2

logger = logging.getLogger(__name__)

class TemplateRenderer:
    """
    Renders templates with variable substitution.
    
    This component is responsible for rendering templates with variable substitution,
    transforming template definitions into concrete deployment artifacts.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Template Renderer.
        
        Args:
            config: Configuration dictionary for the renderer
        """
        self.config = config or {}
        self.render_history = {}  # Template ID -> List of render events
        self.max_history_length = self.config.get("max_history_length", 100)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=False,
            undefined=jinja2.StrictUndefined
        )
        
        logger.info("Initializing Template Renderer")
    
    def initialize(self):
        """Initialize the renderer."""
        logger.info("Initializing Template Renderer")
        
        # Add custom filters
        self._add_custom_filters()
        
        logger.info("Template Renderer initialization complete")
        return True
    
    def render_template(self, template: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a template with variable substitution.
        
        Args:
            template: Template definition
            variables: Variables for substitution
            
        Returns:
            Dictionary with rendering result
        """
        logger.info(f"Rendering template {template.get('id', 'unknown')}")
        
        try:
            # Validate template
            if not self._validate_template(template):
                logger.error("Invalid template")
                return {"success": False, "error": "Invalid template"}
            
            # Validate variables
            if not self._validate_variables(template, variables):
                logger.error("Invalid variables")
                return {"success": False, "error": "Invalid variables"}
            
            # Create a copy of the template
            template_copy = json.loads(json.dumps(template))
            
            # Get template ID
            template_id = template_copy.get("id", "unknown")
            
            # Get template content
            template_content = template_copy.get("content", {})
            
            # Render template content
            rendered_content = self._render_content(template_content, variables)
            
            # Create result
            result = {
                "id": str(uuid.uuid4()),
                "template_id": template_id,
                "timestamp": datetime.now().isoformat(),
                "content": rendered_content
            }
            
            # Record render event
            self._record_render_event(template_id, result["id"], variables)
            
            logger.info(f"Successfully rendered template {template_id}")
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to render template: {str(e)}")
            return {"success": False, "error": f"Failed to render template: {str(e)}"}
    
    def render_template_to_files(self, template: Dict[str, Any], variables: Dict[str, Any], 
                               output_dir: str) -> Dict[str, Any]:
        """
        Render a template to files.
        
        Args:
            template: Template definition
            variables: Variables for substitution
            output_dir: Directory to write output files to
            
        Returns:
            Dictionary with rendering result
        """
        logger.info(f"Rendering template {template.get('id', 'unknown')} to files")
        
        try:
            # Render template
            render_result = self.render_template(template, variables)
            
            if not render_result["success"]:
                return render_result
            
            # Get rendered content
            rendered_content = render_result["result"]["content"]
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Write files
            files_written = []
            
            for file_path, file_content in rendered_content.items():
                # Create full path
                full_path = os.path.join(output_dir, file_path)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                
                # Write file
                with open(full_path, "w") as f:
                    if isinstance(file_content, str):
                        f.write(file_content)
                    else:
                        f.write(json.dumps(file_content, indent=2))
                
                files_written.append(full_path)
            
            logger.info(f"Successfully rendered template to {len(files_written)} files")
            
            return {
                "success": True,
                "files_written": files_written,
                "output_dir": output_dir,
                "template_id": template.get("id", "unknown"),
                "result_id": render_result["result"]["id"]
            }
        except Exception as e:
            logger.error(f"Failed to render template to files: {str(e)}")
            return {"success": False, "error": f"Failed to render template to files: {str(e)}"}
    
    def get_render_history(self, template_id: str) -> Dict[str, Any]:
        """
        Get render history for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with history retrieval result
        """
        if template_id not in self.render_history:
            return {
                "success": True,
                "template_id": template_id,
                "history": []
            }
        
        history = self.render_history[template_id]
        
        logger.info(f"Retrieved render history for template {template_id}")
        
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
        required_fields = ["id", "content"]
        for field in required_fields:
            if field not in template:
                logger.error(f"Missing required field in template: {field}")
                return False
        
        # Check content
        content = template.get("content")
        if not isinstance(content, dict):
            logger.error("Template content must be a dictionary")
            return False
        
        return True
    
    def _validate_variables(self, template: Dict[str, Any], variables: Dict[str, Any]) -> bool:
        """
        Validate variables for a template.
        
        Args:
            template: Template definition
            variables: Variables to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check if template has variable requirements
        if "variables" not in template:
            return True
        
        # Get required variables
        required_variables = template["variables"].get("required", [])
        
        # Check required variables
        for var_name in required_variables:
            if var_name not in variables:
                logger.error(f"Missing required variable: {var_name}")
                return False
        
        # Check variable types
        if "types" in template["variables"]:
            var_types = template["variables"]["types"]
            
            for var_name, var_type in var_types.items():
                if var_name in variables:
                    # Check type
                    if var_type == "string" and not isinstance(variables[var_name], str):
                        logger.error(f"Variable {var_name} must be a string")
                        return False
                    elif var_type == "number" and not isinstance(variables[var_name], (int, float)):
                        logger.error(f"Variable {var_name} must be a number")
                        return False
                    elif var_type == "boolean" and not isinstance(variables[var_name], bool):
                        logger.error(f"Variable {var_name} must be a boolean")
                        return False
                    elif var_type == "array" and not isinstance(variables[var_name], list):
                        logger.error(f"Variable {var_name} must be an array")
                        return False
                    elif var_type == "object" and not isinstance(variables[var_name], dict):
                        logger.error(f"Variable {var_name} must be an object")
                        return False
        
        return True
    
    def _render_content(self, content: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render template content with variable substitution.
        
        Args:
            content: Template content
            variables: Variables for substitution
            
        Returns:
            Rendered content
        """
        # Create a copy of the content
        rendered_content = {}
        
        # Process each file in the content
        for file_path, file_content in content.items():
            # Render file path
            rendered_path = self._render_string(file_path, variables)
            
            # Render file content
            if isinstance(file_content, str):
                rendered_file = self._render_string(file_content, variables)
            elif isinstance(file_content, dict):
                rendered_file = self._render_object(file_content, variables)
            elif isinstance(file_content, list):
                rendered_file = self._render_array(file_content, variables)
            else:
                rendered_file = file_content
            
            # Add to rendered content
            rendered_content[rendered_path] = rendered_file
        
        return rendered_content
    
    def _render_string(self, text: str, variables: Dict[str, Any]) -> str:
        """
        Render a string with variable substitution.
        
        Args:
            text: String to render
            variables: Variables for substitution
            
        Returns:
            Rendered string
        """
        # Use Jinja2 for rendering
        template = self.jinja_env.from_string(text)
        rendered = template.render(**variables)
        
        return rendered
    
    def _render_object(self, obj: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render an object with variable substitution.
        
        Args:
            obj: Object to render
            variables: Variables for substitution
            
        Returns:
            Rendered object
        """
        # Create a copy of the object
        rendered_obj = {}
        
        # Process each field in the object
        for key, value in obj.items():
            # Render key
            rendered_key = self._render_string(key, variables)
            
            # Render value
            if isinstance(value, str):
                rendered_value = self._render_string(value, variables)
            elif isinstance(value, dict):
                rendered_value = self._render_object(value, variables)
            elif isinstance(value, list):
                rendered_value = self._render_array(value, variables)
            else:
                rendered_value = value
            
            # Add to rendered object
            rendered_obj[rendered_key] = rendered_value
        
        return rendered_obj
    
    def _render_array(self, arr: List[Any], variables: Dict[str, Any]) -> List[Any]:
        """
        Render an array with variable substitution.
        
        Args:
            arr: Array to render
            variables: Variables for substitution
            
        Returns:
            Rendered array
        """
        # Create a copy of the array
        rendered_arr = []
        
        # Process each item in the array
        for item in arr:
            # Render item
            if isinstance(item, str):
                rendered_item = self._render_string(item, variables)
            elif isinstance(item, dict):
                rendered_item = self._render_object(item, variables)
            elif isinstance(item, list):
                rendered_item = self._render_array(item, variables)
            else:
                rendered_item = item
            
            # Add to rendered array
            rendered_arr.append(rendered_item)
        
        return rendered_arr
    
    def _record_render_event(self, template_id: str, result_id: str, variables: Dict[str, Any]):
        """
        Record a render event.
        
        Args:
            template_id: ID of the template
            result_id: ID of the render result
            variables: Variables used for rendering
        """
        # Create event
        event = {
            "template_id": template_id,
            "result_id": result_id,
            "timestamp": datetime.now().isoformat(),
            "variables": variables
        }
        
        # Initialize history for this template if it doesn't exist
        if template_id not in self.render_history:
            self.render_history[template_id] = []
        
        # Add event to history
        self.render_history[template_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.render_history[template_id]) > self.max_history_length:
            self.render_history[template_id] = self.render_history[template_id][-self.max_history_length:]
        
        logger.info(f"Recorded render event for template {template_id}")
    
    def _add_custom_filters(self):
        """Add custom filters to the Jinja environment."""
        # Add custom filters
        self.jinja_env.filters["to_json"] = lambda obj: json.dumps(obj)
        self.jinja_env.filters["from_json"] = lambda s: json.loads(s)
        self.jinja_env.filters["base64_encode"] = lambda s: base64.b64encode(s.encode()).decode()
        self.jinja_env.filters["base64_decode"] = lambda s: base64.b64decode(s.encode()).decode()
        self.jinja_env.filters["uuid"] = lambda: str(uuid.uuid4())
        self.jinja_env.filters["timestamp"] = lambda: datetime.now().isoformat()
        
        logger.info("Added custom filters to Jinja environment")
