"""
Manifest Renderer - Renders manifests with variable substitution

This module renders manifests with variable substitution, transforming
manifest definitions into concrete deployment artifacts.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import re
import os
import jinja2
import yaml

logger = logging.getLogger(__name__)

class ManifestRenderer:
    """
    Renders manifests with variable substitution.
    
    This component is responsible for rendering manifests with variable substitution,
    transforming manifest definitions into concrete deployment artifacts.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Manifest Renderer.
        
        Args:
            config: Configuration dictionary for the renderer
        """
        self.config = config or {}
        self.render_history = {}  # Manifest ID -> List of render events
        self.max_history_length = self.config.get("max_history_length", 100)
        self.jinja_env = jinja2.Environment(
            loader=jinja2.BaseLoader(),
            autoescape=False,
            undefined=jinja2.StrictUndefined
        )
        
        logger.info("Initializing Manifest Renderer")
    
    def initialize(self):
        """Initialize the renderer."""
        logger.info("Initializing Manifest Renderer")
        
        # Add custom filters
        self._add_custom_filters()
        
        logger.info("Manifest Renderer initialization complete")
        return True
    
    def render_manifest(self, manifest: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a manifest with variable substitution.
        
        Args:
            manifest: Manifest definition
            variables: Variables for substitution
            
        Returns:
            Dictionary with rendering result
        """
        logger.info(f"Rendering manifest {manifest.get('id', 'unknown')}")
        
        try:
            # Validate manifest
            if not self._validate_manifest(manifest):
                logger.error("Invalid manifest")
                return {"success": False, "error": "Invalid manifest"}
            
            # Create a copy of the manifest
            manifest_copy = json.loads(json.dumps(manifest))
            
            # Get manifest ID
            manifest_id = manifest_copy.get("id", "unknown")
            
            # Get manifest content
            content = manifest_copy.get("content", {})
            
            # Render content
            rendered_content = self._render_content(content, variables)
            
            # Create result
            result = {
                "id": manifest_id,
                "timestamp": datetime.now().isoformat(),
                "content": rendered_content
            }
            
            # Record render event
            self._record_render_event(manifest_id, variables)
            
            logger.info(f"Successfully rendered manifest {manifest_id}")
            
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            logger.error(f"Failed to render manifest: {str(e)}")
            return {"success": False, "error": f"Failed to render manifest: {str(e)}"}
    
    def render_manifest_to_files(self, manifest: Dict[str, Any], variables: Dict[str, Any], 
                               output_dir: str) -> Dict[str, Any]:
        """
        Render a manifest to files.
        
        Args:
            manifest: Manifest definition
            variables: Variables for substitution
            output_dir: Directory to write output files to
            
        Returns:
            Dictionary with rendering result
        """
        logger.info(f"Rendering manifest {manifest.get('id', 'unknown')} to files")
        
        try:
            # Render manifest
            render_result = self.render_manifest(manifest, variables)
            
            if not render_result["success"]:
                return render_result
            
            # Get rendered content
            rendered_content = render_result["result"]["content"]
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            # Write files
            files_written = []
            
            # For Kubernetes manifests, write to a single file or multiple files based on config
            manifest_type = manifest.get("manifest_type", "")
            if manifest_type in ["deployment", "service", "configmap", "secret", "ingress", "volume"]:
                # Get file name
                file_name = manifest.get("name", "manifest").lower().replace(" ", "-")
                file_path = os.path.join(output_dir, f"{file_name}.yaml")
                
                # Write to file
                with open(file_path, "w") as f:
                    yaml.dump(rendered_content, f, default_flow_style=False)
                
                files_written.append(file_path)
            else:
                # For other manifests, write each content item to a separate file
                for key, value in rendered_content.items():
                    # Create file path
                    file_path = os.path.join(output_dir, key)
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Write file
                    with open(file_path, "w") as f:
                        if isinstance(value, str):
                            f.write(value)
                        elif isinstance(value, dict) or isinstance(value, list):
                            if file_path.endswith(".yaml") or file_path.endswith(".yml"):
                                yaml.dump(value, f, default_flow_style=False)
                            else:
                                json.dump(value, f, indent=2)
                        else:
                            f.write(str(value))
                    
                    files_written.append(file_path)
            
            logger.info(f"Successfully rendered manifest to {len(files_written)} files")
            
            return {
                "success": True,
                "files_written": files_written,
                "output_dir": output_dir,
                "manifest_id": manifest.get("id", "unknown")
            }
        except Exception as e:
            logger.error(f"Failed to render manifest to files: {str(e)}")
            return {"success": False, "error": f"Failed to render manifest to files: {str(e)}"}
    
    def render_kubernetes_manifest(self, manifest_content: Dict[str, Any], 
                                 variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a Kubernetes manifest with variable substitution.
        
        Args:
            manifest_content: Kubernetes manifest content
            variables: Variables for substitution
            
        Returns:
            Dictionary with rendering result
        """
        logger.info("Rendering Kubernetes manifest")
        
        try:
            # Create a copy of the manifest content
            content_copy = json.loads(json.dumps(manifest_content))
            
            # Render content
            rendered_content = self._render_content(content_copy, variables)
            
            logger.info("Successfully rendered Kubernetes manifest")
            
            return {
                "success": True,
                "content": rendered_content
            }
        except Exception as e:
            logger.error(f"Failed to render Kubernetes manifest: {str(e)}")
            return {"success": False, "error": f"Failed to render Kubernetes manifest: {str(e)}"}
    
    def render_yaml_manifest(self, yaml_content: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render a YAML manifest with variable substitution.
        
        Args:
            yaml_content: YAML content
            variables: Variables for substitution
            
        Returns:
            Dictionary with rendering result
        """
        logger.info("Rendering YAML manifest")
        
        try:
            # Render YAML content as a template
            template = self.jinja_env.from_string(yaml_content)
            rendered_yaml = template.render(**variables)
            
            # Parse rendered YAML
            rendered_content = yaml.safe_load(rendered_yaml)
            
            logger.info("Successfully rendered YAML manifest")
            
            return {
                "success": True,
                "content": rendered_content,
                "yaml": rendered_yaml
            }
        except Exception as e:
            logger.error(f"Failed to render YAML manifest: {str(e)}")
            return {"success": False, "error": f"Failed to render YAML manifest: {str(e)}"}
    
    def get_render_history(self, manifest_id: str) -> Dict[str, Any]:
        """
        Get render history for a manifest.
        
        Args:
            manifest_id: ID of the manifest
            
        Returns:
            Dictionary with history retrieval result
        """
        if manifest_id not in self.render_history:
            return {
                "success": True,
                "manifest_id": manifest_id,
                "history": []
            }
        
        history = self.render_history[manifest_id]
        
        logger.info(f"Retrieved render history for manifest {manifest_id}")
        
        return {
            "success": True,
            "manifest_id": manifest_id,
            "history": history
        }
    
    def _validate_manifest(self, manifest: Dict[str, Any]) -> bool:
        """
        Validate a manifest.
        
        Args:
            manifest: Manifest to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["id", "content"]
        for field in required_fields:
            if field not in manifest:
                logger.error(f"Missing required field in manifest: {field}")
                return False
        
        # Check content
        content = manifest.get("content")
        if not isinstance(content, dict):
            logger.error("Manifest content must be a dictionary")
            return False
        
        return True
    
    def _render_content(self, content: Dict[str, Any], variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Render content with variable substitution.
        
        Args:
            content: Content to render
            variables: Variables for substitution
            
        Returns:
            Rendered content
        """
        # Convert content to JSON string
        content_json = json.dumps(content)
        
        # Render JSON string as a template
        template = self.jinja_env.from_string(content_json)
        rendered_json = template.render(**variables)
        
        # Parse rendered JSON
        rendered_content = json.loads(rendered_json)
        
        return rendered_content
    
    def _record_render_event(self, manifest_id: str, variables: Dict[str, Any]):
        """
        Record a render event.
        
        Args:
            manifest_id: ID of the manifest
            variables: Variables used for rendering
        """
        # Create event
        event = {
            "manifest_id": manifest_id,
            "timestamp": datetime.now().isoformat(),
            "variables": variables
        }
        
        # Initialize history for this manifest if it doesn't exist
        if manifest_id not in self.render_history:
            self.render_history[manifest_id] = []
        
        # Add event to history
        self.render_history[manifest_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.render_history[manifest_id]) > self.max_history_length:
            self.render_history[manifest_id] = self.render_history[manifest_id][-self.max_history_length:]
        
        logger.info(f"Recorded render event for manifest {manifest_id}")
    
    def _add_custom_filters(self):
        """Add custom filters to the Jinja environment."""
        # Add custom filters
        self.jinja_env.filters["to_json"] = lambda obj: json.dumps(obj)
        self.jinja_env.filters["from_json"] = lambda s: json.loads(s)
        self.jinja_env.filters["to_yaml"] = lambda obj: yaml.dump(obj, default_flow_style=False)
        self.jinja_env.filters["from_yaml"] = lambda s: yaml.safe_load(s)
        self.jinja_env.filters["base64_encode"] = lambda s: base64.b64encode(s.encode()).decode()
        self.jinja_env.filters["base64_decode"] = lambda s: base64.b64decode(s.encode()).decode()
        
        logger.info("Added custom filters to Jinja environment")
