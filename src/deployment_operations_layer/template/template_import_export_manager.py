"""
Template Import/Export Manager - Manages import and export of templates

This module manages the import and export of templates to and from various formats,
facilitating template sharing and migration.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import zipfile
import yaml
import uuid

logger = logging.getLogger(__name__)

class TemplateImportExportManager:
    """
    Manages import and export of templates.
    
    This component is responsible for managing the import and export of templates
    to and from various formats, facilitating template sharing and migration.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Template Import/Export Manager.
        
        Args:
            config: Configuration dictionary for the manager
        """
        self.config = config or {}
        self.import_history = []  # List of import events
        self.export_history = []  # List of export events
        self.max_history_length = self.config.get("max_history_length", 100)
        
        logger.info("Initializing Template Import/Export Manager")
    
    def initialize(self):
        """Initialize the manager."""
        logger.info("Initializing Template Import/Export Manager")
        return True
    
    def export_template(self, template: Dict[str, Any], format: str, 
                       output_path: str) -> Dict[str, Any]:
        """
        Export a template to a file.
        
        Args:
            template: Template to export
            format: Export format (json, yaml, zip)
            output_path: Path to write the exported template to
            
        Returns:
            Dictionary with export result
        """
        logger.info(f"Exporting template {template.get('id', 'unknown')} to {format} format")
        
        try:
            # Validate template
            if not self._validate_template(template):
                logger.error("Invalid template")
                return {"success": False, "error": "Invalid template"}
            
            # Validate format
            if format not in ["json", "yaml", "zip"]:
                logger.error(f"Unsupported format: {format}")
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            # Export based on format
            if format == "json":
                result = self._export_to_json(template, output_path)
            elif format == "yaml":
                result = self._export_to_yaml(template, output_path)
            elif format == "zip":
                result = self._export_to_zip(template, output_path)
            
            if not result["success"]:
                return result
            
            # Record export event
            self._record_export_event(template, format, output_path)
            
            logger.info(f"Successfully exported template {template.get('id', 'unknown')} to {output_path}")
            
            return {
                "success": True,
                "template_id": template.get("id", "unknown"),
                "format": format,
                "output_path": output_path
            }
        except Exception as e:
            logger.error(f"Failed to export template: {str(e)}")
            return {"success": False, "error": f"Failed to export template: {str(e)}"}
    
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
        
        try:
            # Determine format if not provided
            if not format or format == "auto":
                format = self._determine_format(input_path)
            
            # Validate format
            if format not in ["json", "yaml", "zip"]:
                logger.error(f"Unsupported format: {format}")
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            # Import based on format
            if format == "json":
                result = self._import_from_json(input_path)
            elif format == "yaml":
                result = self._import_from_yaml(input_path)
            elif format == "zip":
                result = self._import_from_zip(input_path)
            
            if not result["success"]:
                return result
            
            # Validate imported template
            template = result["template"]
            if not self._validate_template(template):
                logger.error("Invalid imported template")
                return {"success": False, "error": "Invalid imported template"}
            
            # Record import event
            self._record_import_event(template, format, input_path)
            
            logger.info(f"Successfully imported template {template.get('id', 'unknown')} from {input_path}")
            
            return {
                "success": True,
                "template": template,
                "format": format
            }
        except Exception as e:
            logger.error(f"Failed to import template: {str(e)}")
            return {"success": False, "error": f"Failed to import template: {str(e)}"}
    
    def export_templates(self, templates: List[Dict[str, Any]], format: str, 
                        output_path: str) -> Dict[str, Any]:
        """
        Export multiple templates to a file.
        
        Args:
            templates: Templates to export
            format: Export format (json, yaml, zip)
            output_path: Path to write the exported templates to
            
        Returns:
            Dictionary with export result
        """
        logger.info(f"Exporting {len(templates)} templates to {format} format")
        
        try:
            # Validate templates
            for template in templates:
                if not self._validate_template(template):
                    logger.error(f"Invalid template: {template.get('id', 'unknown')}")
                    return {"success": False, "error": f"Invalid template: {template.get('id', 'unknown')}"}
            
            # Validate format
            if format not in ["json", "yaml", "zip"]:
                logger.error(f"Unsupported format: {format}")
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            # Export based on format
            if format == "json":
                result = self._export_multiple_to_json(templates, output_path)
            elif format == "yaml":
                result = self._export_multiple_to_yaml(templates, output_path)
            elif format == "zip":
                result = self._export_multiple_to_zip(templates, output_path)
            
            if not result["success"]:
                return result
            
            # Record export events
            for template in templates:
                self._record_export_event(template, format, output_path)
            
            logger.info(f"Successfully exported {len(templates)} templates to {output_path}")
            
            return {
                "success": True,
                "template_count": len(templates),
                "format": format,
                "output_path": output_path
            }
        except Exception as e:
            logger.error(f"Failed to export templates: {str(e)}")
            return {"success": False, "error": f"Failed to export templates: {str(e)}"}
    
    def import_templates(self, input_path: str, format: str = None) -> Dict[str, Any]:
        """
        Import multiple templates from a file.
        
        Args:
            input_path: Path to the file to import
            format: Import format (json, yaml, zip, auto)
            
        Returns:
            Dictionary with import result
        """
        logger.info(f"Importing templates from {input_path}")
        
        try:
            # Determine format if not provided
            if not format or format == "auto":
                format = self._determine_format(input_path)
            
            # Validate format
            if format not in ["json", "yaml", "zip"]:
                logger.error(f"Unsupported format: {format}")
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            # Import based on format
            if format == "json":
                result = self._import_multiple_from_json(input_path)
            elif format == "yaml":
                result = self._import_multiple_from_yaml(input_path)
            elif format == "zip":
                result = self._import_multiple_from_zip(input_path)
            
            if not result["success"]:
                return result
            
            # Validate imported templates
            templates = result["templates"]
            for template in templates:
                if not self._validate_template(template):
                    logger.error(f"Invalid imported template: {template.get('id', 'unknown')}")
                    return {"success": False, "error": f"Invalid imported template: {template.get('id', 'unknown')}"}
            
            # Record import events
            for template in templates:
                self._record_import_event(template, format, input_path)
            
            logger.info(f"Successfully imported {len(templates)} templates from {input_path}")
            
            return {
                "success": True,
                "templates": templates,
                "template_count": len(templates),
                "format": format
            }
        except Exception as e:
            logger.error(f"Failed to import templates: {str(e)}")
            return {"success": False, "error": f"Failed to import templates: {str(e)}"}
    
    def get_import_history(self) -> Dict[str, Any]:
        """
        Get import history.
        
        Returns:
            Dictionary with import history
        """
        return {
            "success": True,
            "history": self.import_history
        }
    
    def get_export_history(self) -> Dict[str, Any]:
        """
        Get export history.
        
        Returns:
            Dictionary with export history
        """
        return {
            "success": True,
            "history": self.export_history
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
        required_fields = ["id", "name", "description", "schema_version", "template_type"]
        for field in required_fields:
            if field not in template:
                logger.error(f"Missing required field in template: {field}")
                return False
        
        # Check template type
        template_type = template.get("template_type")
        valid_types = ["deployment", "environment", "capsule", "workflow"]
        if template_type not in valid_types:
            logger.error(f"Invalid template type: {template_type}")
            return False
        
        return True
    
    def _determine_format(self, input_path: str) -> str:
        """
        Determine the format of a file.
        
        Args:
            input_path: Path to the file
            
        Returns:
            Format of the file
        """
        # Check file extension
        _, ext = os.path.splitext(input_path)
        
        if ext.lower() == ".json":
            return "json"
        elif ext.lower() in [".yaml", ".yml"]:
            return "yaml"
        elif ext.lower() == ".zip":
            return "zip"
        else:
            # Try to determine format by content
            try:
                with open(input_path, "r") as f:
                    content = f.read(100)  # Read first 100 characters
                    
                    if content.strip().startswith("{"):
                        return "json"
                    elif content.strip().startswith("---") or ":" in content:
                        return "yaml"
            except (UnicodeDecodeError, AttributeError):
                # UnicodeDecodeError: file is not UTF-8
                # AttributeError: file_obj doesn't have read()
                pass
            
            # Default to zip if can't determine
            return "zip"
    
    def _export_to_json(self, template: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        Export a template to JSON format.
        
        Args:
            template: Template to export
            output_path: Path to write the exported template to
            
        Returns:
            Dictionary with export result
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write template to file
            with open(output_path, "w") as f:
                json.dump(template, f, indent=2)
            
            return {
                "success": True,
                "output_path": output_path
            }
        except Exception as e:
            logger.error(f"Failed to export template to JSON: {str(e)}")
            return {"success": False, "error": f"Failed to export template to JSON: {str(e)}"}
    
    def _export_to_yaml(self, template: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        Export a template to YAML format.
        
        Args:
            template: Template to export
            output_path: Path to write the exported template to
            
        Returns:
            Dictionary with export result
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write template to file
            with open(output_path, "w") as f:
                yaml.dump(template, f, default_flow_style=False)
            
            return {
                "success": True,
                "output_path": output_path
            }
        except Exception as e:
            logger.error(f"Failed to export template to YAML: {str(e)}")
            return {"success": False, "error": f"Failed to export template to YAML: {str(e)}"}
    
    def _export_to_zip(self, template: Dict[str, Any], output_path: str) -> Dict[str, Any]:
        """
        Export a template to ZIP format.
        
        Args:
            template: Template to export
            output_path: Path to write the exported template to
            
        Returns:
            Dictionary with export result
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create temporary directory
            temp_dir = os.path.join(os.path.dirname(output_path), f"temp_{uuid.uuid4()}")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Write template metadata to file
                metadata = template.copy()
                if "content" in metadata:
                    del metadata["content"]
                
                with open(os.path.join(temp_dir, "metadata.json"), "w") as f:
                    json.dump(metadata, f, indent=2)
                
                # Write template content to files
                if "content" in template:
                    content_dir = os.path.join(temp_dir, "content")
                    os.makedirs(content_dir, exist_ok=True)
                    
                    for file_path, file_content in template["content"].items():
                        # Create full path
                        full_path = os.path.join(content_dir, file_path)
                        
                        # Ensure directory exists
                        os.makedirs(os.path.dirname(full_path), exist_ok=True)
                        
                        # Write file
                        with open(full_path, "w") as f:
                            if isinstance(file_content, str):
                                f.write(file_content)
                            else:
                                if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                                    yaml.dump(file_content, f, default_flow_style=False)
                                else:
                                    json.dump(file_content, f, indent=2)
                
                # Create ZIP file
                with zipfile.ZipFile(output_path, "w") as zip_file:
                    # Add files to ZIP
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zip_file.write(file_path, arcname)
                
                return {
                    "success": True,
                    "output_path": output_path
                }
            finally:
                # Clean up temporary directory
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Failed to export template to ZIP: {str(e)}")
            return {"success": False, "error": f"Failed to export template to ZIP: {str(e)}"}
    
    def _import_from_json(self, input_path: str) -> Dict[str, Any]:
        """
        Import a template from JSON format.
        
        Args:
            input_path: Path to the file to import
            
        Returns:
            Dictionary with import result
        """
        try:
            # Read template from file
            with open(input_path, "r") as f:
                template = json.load(f)
            
            return {
                "success": True,
                "template": template
            }
        except Exception as e:
            logger.error(f"Failed to import template from JSON: {str(e)}")
            return {"success": False, "error": f"Failed to import template from JSON: {str(e)}"}
    
    def _import_from_yaml(self, input_path: str) -> Dict[str, Any]:
        """
        Import a template from YAML format.
        
        Args:
            input_path: Path to the file to import
            
        Returns:
            Dictionary with import result
        """
        try:
            # Read template from file
            with open(input_path, "r") as f:
                template = yaml.safe_load(f)
            
            return {
                "success": True,
                "template": template
            }
        except Exception as e:
            logger.error(f"Failed to import template from YAML: {str(e)}")
            return {"success": False, "error": f"Failed to import template from YAML: {str(e)}"}
    
    def _import_from_zip(self, input_path: str) -> Dict[str, Any]:
        """
        Import a template from ZIP format.
        
        Args:
            input_path: Path to the file to import
            
        Returns:
            Dictionary with import result
        """
        try:
            # Create temporary directory
            temp_dir = os.path.join(os.path.dirname(input_path), f"temp_{uuid.uuid4()}")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Extract ZIP file
                with zipfile.ZipFile(input_path, "r") as zip_file:
                    zip_file.extractall(temp_dir)
                
                # Read template metadata
                with open(os.path.join(temp_dir, "metadata.json"), "r") as f:
                    template = json.load(f)
                
                # Read template content
                content_dir = os.path.join(temp_dir, "content")
                if os.path.exists(content_dir):
                    content = {}
                    
                    for root, _, files in os.walk(content_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, content_dir)
                            
                            with open(file_path, "r") as f:
                                if file.endswith(".yaml") or file.endswith(".yml"):
                                    file_content = yaml.safe_load(f)
                                elif file.endswith(".json"):
                                    file_content = json.load(f)
                                else:
                                    file_content = f.read()
                            
                            content[rel_path] = file_content
                    
                    template["content"] = content
                
                return {
                    "success": True,
                    "template": template
                }
            finally:
                # Clean up temporary directory
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Failed to import template from ZIP: {str(e)}")
            return {"success": False, "error": f"Failed to import template from ZIP: {str(e)}"}
    
    def _export_multiple_to_json(self, templates: List[Dict[str, Any]], 
                               output_path: str) -> Dict[str, Any]:
        """
        Export multiple templates to JSON format.
        
        Args:
            templates: Templates to export
            output_path: Path to write the exported templates to
            
        Returns:
            Dictionary with export result
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write templates to file
            with open(output_path, "w") as f:
                json.dump(templates, f, indent=2)
            
            return {
                "success": True,
                "output_path": output_path
            }
        except Exception as e:
            logger.error(f"Failed to export templates to JSON: {str(e)}")
            return {"success": False, "error": f"Failed to export templates to JSON: {str(e)}"}
    
    def _export_multiple_to_yaml(self, templates: List[Dict[str, Any]], 
                               output_path: str) -> Dict[str, Any]:
        """
        Export multiple templates to YAML format.
        
        Args:
            templates: Templates to export
            output_path: Path to write the exported templates to
            
        Returns:
            Dictionary with export result
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write templates to file
            with open(output_path, "w") as f:
                yaml.dump(templates, f, default_flow_style=False)
            
            return {
                "success": True,
                "output_path": output_path
            }
        except Exception as e:
            logger.error(f"Failed to export templates to YAML: {str(e)}")
            return {"success": False, "error": f"Failed to export templates to YAML: {str(e)}"}
    
    def _export_multiple_to_zip(self, templates: List[Dict[str, Any]], 
                              output_path: str) -> Dict[str, Any]:
        """
        Export multiple templates to ZIP format.
        
        Args:
            templates: Templates to export
            output_path: Path to write the exported templates to
            
        Returns:
            Dictionary with export result
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Create temporary directory
            temp_dir = os.path.join(os.path.dirname(output_path), f"temp_{uuid.uuid4()}")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Write templates index
                index = []
                for template in templates:
                    index.append({
                        "id": template.get("id", "unknown"),
                        "name": template.get("name", "Unknown"),
                        "description": template.get("description", ""),
                        "template_type": template.get("template_type", "unknown")
                    })
                
                with open(os.path.join(temp_dir, "index.json"), "w") as f:
                    json.dump(index, f, indent=2)
                
                # Write templates
                for template in templates:
                    template_id = template.get("id", "unknown")
                    template_dir = os.path.join(temp_dir, "templates", template_id)
                    os.makedirs(template_dir, exist_ok=True)
                    
                    # Write template metadata
                    metadata = template.copy()
                    if "content" in metadata:
                        del metadata["content"]
                    
                    with open(os.path.join(template_dir, "metadata.json"), "w") as f:
                        json.dump(metadata, f, indent=2)
                    
                    # Write template content
                    if "content" in template:
                        content_dir = os.path.join(template_dir, "content")
                        os.makedirs(content_dir, exist_ok=True)
                        
                        for file_path, file_content in template["content"].items():
                            # Create full path
                            full_path = os.path.join(content_dir, file_path)
                            
                            # Ensure directory exists
                            os.makedirs(os.path.dirname(full_path), exist_ok=True)
                            
                            # Write file
                            with open(full_path, "w") as f:
                                if isinstance(file_content, str):
                                    f.write(file_content)
                                else:
                                    if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                                        yaml.dump(file_content, f, default_flow_style=False)
                                    else:
                                        json.dump(file_content, f, indent=2)
                
                # Create ZIP file
                with zipfile.ZipFile(output_path, "w") as zip_file:
                    # Add files to ZIP
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zip_file.write(file_path, arcname)
                
                return {
                    "success": True,
                    "output_path": output_path
                }
            finally:
                # Clean up temporary directory
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Failed to export templates to ZIP: {str(e)}")
            return {"success": False, "error": f"Failed to export templates to ZIP: {str(e)}"}
    
    def _import_multiple_from_json(self, input_path: str) -> Dict[str, Any]:
        """
        Import multiple templates from JSON format.
        
        Args:
            input_path: Path to the file to import
            
        Returns:
            Dictionary with import result
        """
        try:
            # Read templates from file
            with open(input_path, "r") as f:
                templates = json.load(f)
            
            # Ensure templates is a list
            if not isinstance(templates, list):
                logger.error("Imported data is not a list of templates")
                return {"success": False, "error": "Imported data is not a list of templates"}
            
            return {
                "success": True,
                "templates": templates
            }
        except Exception as e:
            logger.error(f"Failed to import templates from JSON: {str(e)}")
            return {"success": False, "error": f"Failed to import templates from JSON: {str(e)}"}
    
    def _import_multiple_from_yaml(self, input_path: str) -> Dict[str, Any]:
        """
        Import multiple templates from YAML format.
        
        Args:
            input_path: Path to the file to import
            
        Returns:
            Dictionary with import result
        """
        try:
            # Read templates from file
            with open(input_path, "r") as f:
                templates = yaml.safe_load(f)
            
            # Ensure templates is a list
            if not isinstance(templates, list):
                logger.error("Imported data is not a list of templates")
                return {"success": False, "error": "Imported data is not a list of templates"}
            
            return {
                "success": True,
                "templates": templates
            }
        except Exception as e:
            logger.error(f"Failed to import templates from YAML: {str(e)}")
            return {"success": False, "error": f"Failed to import templates from YAML: {str(e)}"}
    
    def _import_multiple_from_zip(self, input_path: str) -> Dict[str, Any]:
        """
        Import multiple templates from ZIP format.
        
        Args:
            input_path: Path to the file to import
            
        Returns:
            Dictionary with import result
        """
        try:
            # Create temporary directory
            temp_dir = os.path.join(os.path.dirname(input_path), f"temp_{uuid.uuid4()}")
            os.makedirs(temp_dir, exist_ok=True)
            
            try:
                # Extract ZIP file
                with zipfile.ZipFile(input_path, "r") as zip_file:
                    zip_file.extractall(temp_dir)
                
                # Read templates index
                with open(os.path.join(temp_dir, "index.json"), "r") as f:
                    index = json.load(f)
                
                # Read templates
                templates = []
                templates_dir = os.path.join(temp_dir, "templates")
                
                if os.path.exists(templates_dir):
                    for template_id in os.listdir(templates_dir):
                        template_dir = os.path.join(templates_dir, template_id)
                        
                        if os.path.isdir(template_dir):
                            # Read template metadata
                            with open(os.path.join(template_dir, "metadata.json"), "r") as f:
                                template = json.load(f)
                            
                            # Read template content
                            content_dir = os.path.join(template_dir, "content")
                            if os.path.exists(content_dir):
                                content = {}
                                
                                for root, _, files in os.walk(content_dir):
                                    for file in files:
                                        file_path = os.path.join(root, file)
                                        rel_path = os.path.relpath(file_path, content_dir)
                                        
                                        with open(file_path, "r") as f:
                                            if file.endswith(".yaml") or file.endswith(".yml"):
                                                file_content = yaml.safe_load(f)
                                            elif file.endswith(".json"):
                                                file_content = json.load(f)
                                            else:
                                                file_content = f.read()
                                        
                                        content[rel_path] = file_content
                                
                                template["content"] = content
                            
                            templates.append(template)
                
                return {
                    "success": True,
                    "templates": templates
                }
            finally:
                # Clean up temporary directory
                import shutil
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception as e:
            logger.error(f"Failed to import templates from ZIP: {str(e)}")
            return {"success": False, "error": f"Failed to import templates from ZIP: {str(e)}"}
    
    def _record_import_event(self, template: Dict[str, Any], format: str, input_path: str):
        """
        Record an import event.
        
        Args:
            template: Imported template
            format: Import format
            input_path: Path to the imported file
        """
        # Create event
        event = {
            "template_id": template.get("id", "unknown"),
            "template_name": template.get("name", "Unknown"),
            "template_type": template.get("template_type", "unknown"),
            "format": format,
            "input_path": input_path,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add event to history
        self.import_history.append(event)
        
        # Trim history if it exceeds max length
        if len(self.import_history) > self.max_history_length:
            self.import_history = self.import_history[-self.max_history_length:]
        
        logger.info(f"Recorded import event for template {template.get('id', 'unknown')}")
    
    def _record_export_event(self, template: Dict[str, Any], format: str, output_path: str):
        """
        Record an export event.
        
        Args:
            template: Exported template
            format: Export format
            output_path: Path to the exported file
        """
        # Create event
        event = {
            "template_id": template.get("id", "unknown"),
            "template_name": template.get("name", "Unknown"),
            "template_type": template.get("template_type", "unknown"),
            "format": format,
            "output_path": output_path,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add event to history
        self.export_history.append(event)
        
        # Trim history if it exceeds max length
        if len(self.export_history) > self.max_history_length:
            self.export_history = self.export_history[-self.max_history_length:]
        
        logger.info(f"Recorded export event for template {template.get('id', 'unknown')}")
