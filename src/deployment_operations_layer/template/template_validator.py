"""
Template Validator - Validates templates against schemas

This module validates templates against schemas, ensuring they conform to
the required structure and constraints.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import jsonschema

logger = logging.getLogger(__name__)

class TemplateValidator:
    """
    Validates templates against schemas.
    
    This component is responsible for validating templates against schemas,
    ensuring they conform to the required structure and constraints.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Template Validator.
        
        Args:
            config: Configuration dictionary for the validator
        """
        self.config = config or {}
        self.schemas = {}  # Schema ID -> Schema
        self.validation_history = {}  # Template ID -> List of validation events
        self.max_history_length = self.config.get("max_history_length", 100)
        
        logger.info("Initializing Template Validator")
    
    def initialize(self):
        """Initialize the validator and load schemas."""
        logger.info("Initializing Template Validator")
        
        # Load schemas
        self._load_schemas()
        
        logger.info(f"Loaded {len(self.schemas)} schemas")
        return True
    
    def validate_template(self, template: Dict[str, Any], schema_id: str = None) -> Dict[str, Any]:
        """
        Validate a template against a schema.
        
        Args:
            template: Template to validate
            schema_id: ID of the schema to validate against (if None, uses schema_version from template)
            
        Returns:
            Dictionary with validation result
        """
        logger.info(f"Validating template {template.get('id', 'unknown')}")
        
        # Get template ID
        template_id = template.get("id", "unknown")
        
        # Determine schema ID
        if not schema_id:
            schema_id = template.get("schema_version")
            
            if not schema_id:
                logger.error("No schema ID provided and no schema_version in template")
                return {"valid": False, "errors": ["No schema ID provided and no schema_version in template"]}
        
        # Check if schema exists
        if schema_id not in self.schemas:
            logger.error(f"Schema {schema_id} not found")
            return {"valid": False, "errors": [f"Schema {schema_id} not found"]}
        
        # Get schema
        schema = self.schemas[schema_id]
        
        # Validate template
        try:
            jsonschema.validate(instance=template, schema=schema)
            
            # Record validation event
            self._record_validation_event(template_id, schema_id, True)
            
            logger.info(f"Template {template_id} is valid against schema {schema_id}")
            
            return {
                "valid": True,
                "template_id": template_id,
                "schema_id": schema_id
            }
        except jsonschema.exceptions.ValidationError as e:
            # Record validation event
            self._record_validation_event(template_id, schema_id, False, str(e))
            
            logger.error(f"Template {template_id} is invalid against schema {schema_id}: {str(e)}")
            
            return {
                "valid": False,
                "template_id": template_id,
                "schema_id": schema_id,
                "errors": [str(e)]
            }
    
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
        
        # Validate schema
        try:
            jsonschema.Draft7Validator.check_schema(schema)
        except jsonschema.exceptions.SchemaError as e:
            logger.error(f"Invalid schema {schema_id}: {str(e)}")
            return {"success": False, "error": f"Invalid schema: {str(e)}"}
        
        # Register schema
        self.schemas[schema_id] = schema
        
        # Save schemas
        self._save_schemas()
        
        logger.info(f"Registered schema {schema_id}")
        
        return {
            "success": True,
            "schema_id": schema_id
        }
    
    def unregister_schema(self, schema_id: str) -> Dict[str, Any]:
        """
        Unregister a schema.
        
        Args:
            schema_id: ID of the schema
            
        Returns:
            Dictionary with unregistration result
        """
        logger.info(f"Unregistering schema {schema_id}")
        
        # Check if schema exists
        if schema_id not in self.schemas:
            logger.warning(f"Schema {schema_id} not found")
            return {"success": False, "error": "Schema not found"}
        
        # Unregister schema
        del self.schemas[schema_id]
        
        # Save schemas
        self._save_schemas()
        
        logger.info(f"Unregistered schema {schema_id}")
        
        return {
            "success": True,
            "schema_id": schema_id
        }
    
    def get_schema(self, schema_id: str) -> Dict[str, Any]:
        """
        Get a schema.
        
        Args:
            schema_id: ID of the schema
            
        Returns:
            Dictionary with schema retrieval result
        """
        # Check if schema exists
        if schema_id not in self.schemas:
            logger.warning(f"Schema {schema_id} not found")
            return {"success": False, "error": "Schema not found"}
        
        # Get schema
        schema = self.schemas[schema_id]
        
        logger.info(f"Retrieved schema {schema_id}")
        
        return {
            "success": True,
            "schema_id": schema_id,
            "schema": schema
        }
    
    def get_all_schemas(self) -> Dict[str, Any]:
        """
        Get all schemas.
        
        Returns:
            Dictionary with all schemas
        """
        schemas = {}
        
        for schema_id, schema in self.schemas.items():
            schemas[schema_id] = schema
        
        logger.info(f"Retrieved {len(schemas)} schemas")
        
        return {
            "success": True,
            "schemas": schemas
        }
    
    def get_validation_history(self, template_id: str) -> Dict[str, Any]:
        """
        Get validation history for a template.
        
        Args:
            template_id: ID of the template
            
        Returns:
            Dictionary with history retrieval result
        """
        if template_id not in self.validation_history:
            return {
                "success": True,
                "template_id": template_id,
                "history": []
            }
        
        history = self.validation_history[template_id]
        
        logger.info(f"Retrieved validation history for template {template_id}")
        
        return {
            "success": True,
            "template_id": template_id,
            "history": history
        }
    
    def _record_validation_event(self, template_id: str, schema_id: str, valid: bool, error: str = None):
        """
        Record a validation event.
        
        Args:
            template_id: ID of the template
            schema_id: ID of the schema
            valid: Whether validation was successful
            error: Error message (if validation failed)
        """
        # Create event
        event = {
            "template_id": template_id,
            "schema_id": schema_id,
            "timestamp": datetime.now().isoformat(),
            "valid": valid
        }
        
        if not valid and error:
            event["error"] = error
        
        # Initialize history for this template if it doesn't exist
        if template_id not in self.validation_history:
            self.validation_history[template_id] = []
        
        # Add event to history
        self.validation_history[template_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.validation_history[template_id]) > self.max_history_length:
            self.validation_history[template_id] = self.validation_history[template_id][-self.max_history_length:]
        
        logger.info(f"Recorded validation event for template {template_id}: {'valid' if valid else 'invalid'}")
    
    def _load_schemas(self):
        """Load schemas from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll initialize with default schemas
            self.schemas = self._get_default_schemas()
            logger.info("Loaded schemas")
        except Exception as e:
            logger.error(f"Failed to load schemas: {str(e)}")
    
    def _save_schemas(self):
        """Save schemas to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.schemas)} schemas")
        except Exception as e:
            logger.error(f"Failed to save schemas: {str(e)}")
    
    def _get_default_schemas(self) -> Dict[str, Dict[str, Any]]:
        """
        Get default schemas.
        
        Returns:
            Dictionary of schema ID -> schema
        """
        schemas = {}
        
        # Base template schema
        base_template_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "schema_version", "template_type"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "schema_version": {"type": "string"},
                "template_type": {"type": "string", "enum": ["deployment", "environment", "capsule", "workflow"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {"type": "object"},
                "variables": {
                    "type": "object",
                    "properties": {
                        "required": {"type": "array", "items": {"type": "string"}},
                        "types": {"type": "object", "additionalProperties": {"type": "string"}}
                    }
                }
            }
        }
        
        # Deployment template schema
        deployment_template_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "schema_version", "template_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "schema_version": {"type": "string"},
                "template_type": {"type": "string", "enum": ["deployment"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {
                    "type": "object",
                    "required": ["deployment.yaml"],
                    "additionalProperties": {"type": ["string", "object"]}
                },
                "variables": {
                    "type": "object",
                    "properties": {
                        "required": {"type": "array", "items": {"type": "string"}},
                        "types": {"type": "object", "additionalProperties": {"type": "string"}}
                    }
                }
            }
        }
        
        # Environment template schema
        environment_template_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "schema_version", "template_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "schema_version": {"type": "string"},
                "template_type": {"type": "string", "enum": ["environment"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {
                    "type": "object",
                    "required": ["environment.yaml"],
                    "additionalProperties": {"type": ["string", "object"]}
                },
                "variables": {
                    "type": "object",
                    "properties": {
                        "required": {"type": "array", "items": {"type": "string"}},
                        "types": {"type": "object", "additionalProperties": {"type": "string"}}
                    }
                }
            }
        }
        
        # Capsule template schema
        capsule_template_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "schema_version", "template_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "schema_version": {"type": "string"},
                "template_type": {"type": "string", "enum": ["capsule"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {
                    "type": "object",
                    "required": ["capsule.yaml"],
                    "additionalProperties": {"type": ["string", "object"]}
                },
                "variables": {
                    "type": "object",
                    "properties": {
                        "required": {"type": "array", "items": {"type": "string"}},
                        "types": {"type": "object", "additionalProperties": {"type": "string"}}
                    }
                }
            }
        }
        
        # Workflow template schema
        workflow_template_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "schema_version", "template_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "schema_version": {"type": "string"},
                "template_type": {"type": "string", "enum": ["workflow"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {
                    "type": "object",
                    "required": ["workflow.yaml"],
                    "additionalProperties": {"type": ["string", "object"]}
                },
                "variables": {
                    "type": "object",
                    "properties": {
                        "required": {"type": "array", "items": {"type": "string"}},
                        "types": {"type": "object", "additionalProperties": {"type": "string"}}
                    }
                }
            }
        }
        
        # Add schemas
        schemas["base-1.0"] = base_template_schema
        schemas["deployment-1.0"] = deployment_template_schema
        schemas["environment-1.0"] = environment_template_schema
        schemas["capsule-1.0"] = capsule_template_schema
        schemas["workflow-1.0"] = workflow_template_schema
        
        return schemas
