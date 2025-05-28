"""
Hardware Deployment Manifest Generator - Generates deployment manifests for hardware triggers

This module generates deployment manifests for hardware-triggered capsule instantiation,
translating hardware trigger context into deployment manifests.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

logger = logging.getLogger(__name__)

class HardwareDeploymentManifestGenerator:
    """
    Generates deployment manifests for hardware triggers.
    
    This component is responsible for generating deployment manifests for
    hardware-triggered capsule instantiation, translating hardware trigger
    context into deployment manifests.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Hardware Deployment Manifest Generator.
        
        Args:
            config: Configuration dictionary for the generator
        """
        self.config = config or {}
        self.manifest_templates = {}  # Template ID -> Template
        self.manifest_history = {}  # Trigger ID -> List of manifests
        self.max_history_length = self.config.get("max_history_length", 100)
        
        logger.info("Initializing Hardware Deployment Manifest Generator")
    
    def initialize(self):
        """Initialize the generator and load manifest templates."""
        logger.info("Initializing Hardware Deployment Manifest Generator")
        
        # Load manifest templates
        self._load_manifest_templates()
        
        logger.info(f"Loaded {len(self.manifest_templates)} manifest templates")
        return True
    
    def generate_manifest(self, trigger_id: str, trigger_config: Dict[str, Any], 
                         processing_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a deployment manifest for a hardware trigger.
        
        Args:
            trigger_id: ID of the trigger
            trigger_config: Configuration for the trigger
            processing_result: Result of signal processing
            
        Returns:
            Dictionary with generation result
        """
        logger.info(f"Generating deployment manifest for trigger {trigger_id}")
        
        # Check if processing was successful
        if not processing_result.get("success", False):
            logger.error(f"Cannot generate manifest: Processing failed for trigger {trigger_id}")
            return {"success": False, "error": "Processing failed"}
        
        # Extract action and context
        action = processing_result.get("action")
        context = processing_result.get("context", {})
        
        if not action:
            logger.error("No action in processing result")
            return {"success": False, "error": "No action in processing result"}
        
        # Get template ID from action
        template_id = action.get("template_id")
        
        if not template_id:
            logger.error("No template ID in action")
            return {"success": False, "error": "No template ID in action"}
        
        # Check if template exists
        if template_id not in self.manifest_templates:
            logger.error(f"Template {template_id} not found")
            return {"success": False, "error": f"Template {template_id} not found"}
        
        # Get template
        template = self.manifest_templates[template_id]
        
        # Generate manifest
        try:
            manifest = self._generate_manifest_from_template(template, context, action)
            
            # Record manifest
            self._record_manifest(trigger_id, manifest)
            
            logger.info(f"Generated manifest for trigger {trigger_id}")
            
            return {
                "success": True,
                "manifest": manifest
            }
        except Exception as e:
            logger.error(f"Failed to generate manifest: {str(e)}")
            return {"success": False, "error": f"Failed to generate manifest: {str(e)}"}
    
    def register_manifest_template(self, template_id: str, template: Dict[str, Any]) -> bool:
        """
        Register a manifest template.
        
        Args:
            template_id: ID of the template
            template: Template definition
            
        Returns:
            True if successful, False otherwise
        """
        if template_id in self.manifest_templates:
            logger.warning(f"Template {template_id} is already registered")
            return False
        
        # Validate template
        if not self._validate_template(template):
            logger.error(f"Invalid template for {template_id}")
            return False
        
        # Register template
        self.manifest_templates[template_id] = template
        
        # Save manifest templates
        self._save_manifest_templates()
        
        logger.info(f"Registered manifest template {template_id}")
        return True
    
    def unregister_manifest_template(self, template_id: str) -> bool:
        """
        Unregister a manifest template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            True if successful, False otherwise
        """
        if template_id not in self.manifest_templates:
            logger.warning(f"Template {template_id} is not registered")
            return False
        
        # Unregister template
        del self.manifest_templates[template_id]
        
        # Save manifest templates
        self._save_manifest_templates()
        
        logger.info(f"Unregistered manifest template {template_id}")
        return True
    
    def get_manifest_history(self, trigger_id: str) -> List[Dict[str, Any]]:
        """
        Get the manifest history for a trigger.
        
        Args:
            trigger_id: ID of the trigger
            
        Returns:
            List of manifest dictionaries
        """
        return self.manifest_history.get(trigger_id, [])
    
    def _generate_manifest_from_template(self, template: Dict[str, Any], 
                                       context: Dict[str, Any], 
                                       action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a manifest from a template.
        
        Args:
            template: Template definition
            context: Context data
            action: Action data
            
        Returns:
            Generated manifest
        """
        # Create a copy of the template
        manifest = json.loads(json.dumps(template.get("manifest_template", {})))
        
        # Generate manifest ID
        manifest_id = f"hw-{uuid.uuid4()}"
        
        # Set basic manifest fields
        manifest["id"] = manifest_id
        manifest["name"] = self._replace_variables(template.get("name", "Hardware Triggered Deployment"), context, action)
        manifest["description"] = self._replace_variables(template.get("description", ""), context, action)
        manifest["timestamp"] = datetime.now().isoformat()
        manifest["trigger"] = {
            "type": "hardware",
            "id": context.get("trigger_id"),
            "context": context
        }
        
        # Set capsule configuration
        if "capsule_config" in template:
            capsule_config = json.loads(json.dumps(template["capsule_config"]))
            
            # Replace variables in capsule configuration
            for key, value in capsule_config.items():
                if isinstance(value, str):
                    capsule_config[key] = self._replace_variables(value, context, action)
            
            manifest["capsule_config"] = capsule_config
        
        # Set environment configuration
        if "environment_config" in template:
            environment_config = json.loads(json.dumps(template["environment_config"]))
            
            # Replace variables in environment configuration
            for key, value in environment_config.items():
                if isinstance(value, str):
                    environment_config[key] = self._replace_variables(value, context, action)
            
            manifest["environment_config"] = environment_config
        
        # Set parameters
        if "parameters" in template:
            parameters = json.loads(json.dumps(template["parameters"]))
            
            # Replace variables in parameters
            for key, value in parameters.items():
                if isinstance(value, str):
                    parameters[key] = self._replace_variables(value, context, action)
            
            manifest["parameters"] = parameters
        
        # Add MCP context
        manifest["mcp_context"] = self._generate_mcp_context(context, action)
        
        # Add A2A metadata
        manifest["a2a_metadata"] = self._generate_a2a_metadata(context, action)
        
        return manifest
    
    def _replace_variables(self, text: str, context: Dict[str, Any], action: Dict[str, Any]) -> str:
        """
        Replace variables in text with values from context and action.
        
        Args:
            text: Text with variables
            context: Context data
            action: Action data
            
        Returns:
            Text with variables replaced
        """
        if not isinstance(text, str):
            return text
        
        # Replace context variables
        for key, value in context.items():
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                text = text.replace(f"{{context.{key}}}", str(value))
        
        # Replace action variables
        for key, value in action.items():
            if isinstance(value, str) or isinstance(value, int) or isinstance(value, float):
                text = text.replace(f"{{action.{key}}}", str(value))
        
        # Replace system variables
        text = text.replace("{timestamp}", datetime.now().isoformat())
        text = text.replace("{uuid}", str(uuid.uuid4()))
        
        return text
    
    def _validate_template(self, template: Dict[str, Any]) -> bool:
        """
        Validate a manifest template.
        
        Args:
            template: Template to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "description", "manifest_template"]
        for field in required_fields:
            if field not in template:
                logger.error(f"Missing required field in template: {field}")
                return False
        
        # Check manifest template
        manifest_template = template.get("manifest_template", {})
        if not isinstance(manifest_template, dict):
            logger.error("Manifest template must be a dictionary")
            return False
        
        # Check capsule configuration
        if "capsule_config" in template and not isinstance(template["capsule_config"], dict):
            logger.error("Capsule configuration must be a dictionary")
            return False
        
        # Check environment configuration
        if "environment_config" in template and not isinstance(template["environment_config"], dict):
            logger.error("Environment configuration must be a dictionary")
            return False
        
        # Check parameters
        if "parameters" in template and not isinstance(template["parameters"], dict):
            logger.error("Parameters must be a dictionary")
            return False
        
        return True
    
    def _record_manifest(self, trigger_id: str, manifest: Dict[str, Any]):
        """
        Record a generated manifest.
        
        Args:
            trigger_id: ID of the trigger
            manifest: Generated manifest
        """
        # Initialize history for this trigger if it doesn't exist
        if trigger_id not in self.manifest_history:
            self.manifest_history[trigger_id] = []
        
        # Add manifest to history
        self.manifest_history[trigger_id].append(manifest)
        
        # Trim history if it exceeds max length
        if len(self.manifest_history[trigger_id]) > self.max_history_length:
            self.manifest_history[trigger_id] = self.manifest_history[trigger_id][-self.max_history_length:]
        
        logger.info(f"Recorded manifest for trigger {trigger_id}")
    
    def _load_manifest_templates(self):
        """Load manifest templates from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.manifest_templates = {}
            logger.info("Loaded manifest templates")
        except Exception as e:
            logger.error(f"Failed to load manifest templates: {str(e)}")
    
    def _save_manifest_templates(self):
        """Save manifest templates to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.manifest_templates)} manifest templates")
        except Exception as e:
            logger.error(f"Failed to save manifest templates: {str(e)}")
    
    def _generate_mcp_context(self, context: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate MCP context for the manifest.
        
        Args:
            context: Context data
            action: Action data
            
        Returns:
            Dictionary with MCP context
        """
        # This is a placeholder for MCP integration
        # In a real implementation, this would generate a proper MCP context
        return {
            "contextType": "hardware_trigger",
            "triggerType": context.get("proximity_type", "unknown") if "proximity_type" in context else context.get("signal_type", "unknown"),
            "triggerId": context.get("trigger_id", "unknown"),
            "actionType": action.get("type", "unknown"),
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_a2a_metadata(self, context: Dict[str, Any], action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate A2A metadata for the manifest.
        
        Args:
            context: Context data
            action: Action data
            
        Returns:
            Dictionary with A2A metadata
        """
        # This is a placeholder for A2A integration
        # In a real implementation, this would generate proper A2A metadata
        
        # Determine industry tags based on context
        industry_tags = ["manufacturing", "industrial_automation"]
        
        if "zone_name" in context and "factory" in context["zone_name"].lower():
            industry_tags.append("factory_automation")
        elif "zone_name" in context and "warehouse" in context["zone_name"].lower():
            industry_tags.append("warehouse_management")
        
        # Determine priority based on action
        priority = action.get("priority", "medium")
        
        return {
            "agentId": f"hardware_trigger_{context.get('trigger_id', 'unknown')}",
            "industryTags": industry_tags,
            "priority": priority,
            "capabilities": {
                "hardwareTrigger": True,
                "proximityAware": "proximity_type" in context,
                "locationAware": "location_id" in context or "zone_id" in context
            }
        }
