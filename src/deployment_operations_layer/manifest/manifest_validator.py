"""
Manifest Validator - Validates deployment manifests against schemas

This module validates deployment manifests against schemas, ensuring they
conform to the required structure and constraints.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import jsonschema
import yaml

logger = logging.getLogger(__name__)

class ManifestValidator:
    """
    Validates deployment manifests against schemas.
    
    This component is responsible for validating deployment manifests against schemas,
    ensuring they conform to the required structure and constraints.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Manifest Validator.
        
        Args:
            config: Configuration dictionary for the validator
        """
        self.config = config or {}
        self.schemas = {}  # Schema ID -> Schema
        self.validation_history = {}  # Manifest ID -> List of validation events
        self.max_history_length = self.config.get("max_history_length", 100)
        
        logger.info("Initializing Manifest Validator")
    
    def initialize(self):
        """Initialize the validator and load schemas."""
        logger.info("Initializing Manifest Validator")
        
        # Load schemas
        self._load_schemas()
        
        logger.info(f"Loaded {len(self.schemas)} schemas")
        return True
    
    def validate_manifest(self, manifest: Dict[str, Any], schema_id: str = None) -> Dict[str, Any]:
        """
        Validate a manifest against a schema.
        
        Args:
            manifest: Manifest to validate
            schema_id: ID of the schema to validate against (if None, uses manifest_type from manifest)
            
        Returns:
            Dictionary with validation result
        """
        logger.info(f"Validating manifest {manifest.get('id', 'unknown')}")
        
        # Get manifest ID
        manifest_id = manifest.get("id", "unknown")
        
        # Determine schema ID
        if not schema_id:
            manifest_type = manifest.get("manifest_type")
            
            if not manifest_type:
                logger.error("No schema ID provided and no manifest_type in manifest")
                return {"valid": False, "errors": ["No schema ID provided and no manifest_type in manifest"]}
            
            schema_id = f"{manifest_type}-schema"
        
        # Check if schema exists
        if schema_id not in self.schemas:
            logger.error(f"Schema {schema_id} not found")
            return {"valid": False, "errors": [f"Schema {schema_id} not found"]}
        
        # Get schema
        schema = self.schemas[schema_id]
        
        # Validate manifest
        try:
            jsonschema.validate(instance=manifest, schema=schema)
            
            # Record validation event
            self._record_validation_event(manifest_id, schema_id, True)
            
            logger.info(f"Manifest {manifest_id} is valid against schema {schema_id}")
            
            return {
                "valid": True,
                "manifest_id": manifest_id,
                "schema_id": schema_id
            }
        except jsonschema.exceptions.ValidationError as e:
            # Record validation event
            self._record_validation_event(manifest_id, schema_id, False, str(e))
            
            logger.error(f"Manifest {manifest_id} is invalid against schema {schema_id}: {str(e)}")
            
            return {
                "valid": False,
                "manifest_id": manifest_id,
                "schema_id": schema_id,
                "errors": [str(e)]
            }
    
    def validate_kubernetes_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a Kubernetes manifest.
        
        Args:
            manifest: Kubernetes manifest to validate
            
        Returns:
            Dictionary with validation result
        """
        logger.info("Validating Kubernetes manifest")
        
        # Check required fields
        if "apiVersion" not in manifest:
            logger.error("Missing apiVersion in Kubernetes manifest")
            return {"valid": False, "errors": ["Missing apiVersion in Kubernetes manifest"]}
        
        if "kind" not in manifest:
            logger.error("Missing kind in Kubernetes manifest")
            return {"valid": False, "errors": ["Missing kind in Kubernetes manifest"]}
        
        if "metadata" not in manifest:
            logger.error("Missing metadata in Kubernetes manifest")
            return {"valid": False, "errors": ["Missing metadata in Kubernetes manifest"]}
        
        # Check metadata
        metadata = manifest["metadata"]
        if "name" not in metadata:
            logger.error("Missing name in Kubernetes manifest metadata")
            return {"valid": False, "errors": ["Missing name in Kubernetes manifest metadata"]}
        
        # Determine schema based on kind
        kind = manifest["kind"]
        schema_id = f"kubernetes-{kind.lower()}"
        
        # Check if schema exists
        if schema_id in self.schemas:
            # Validate against schema
            schema = self.schemas[schema_id]
            
            try:
                jsonschema.validate(instance=manifest, schema=schema)
            except jsonschema.exceptions.ValidationError as e:
                logger.error(f"Kubernetes manifest is invalid against schema: {str(e)}")
                return {"valid": False, "errors": [str(e)]}
        else:
            logger.warning(f"No schema found for Kubernetes kind {kind}, performing basic validation only")
        
        logger.info("Kubernetes manifest is valid")
        
        return {
            "valid": True,
            "kind": kind,
            "name": metadata["name"]
        }
    
    def validate_yaml_manifest(self, yaml_content: str) -> Dict[str, Any]:
        """
        Validate a manifest in YAML format.
        
        Args:
            yaml_content: YAML content to validate
            
        Returns:
            Dictionary with validation result
        """
        logger.info("Validating YAML manifest")
        
        try:
            # Parse YAML
            manifest = yaml.safe_load(yaml_content)
            
            # Validate manifest
            if isinstance(manifest, dict):
                # Check if it's a Kubernetes manifest
                if "apiVersion" in manifest and "kind" in manifest:
                    return self.validate_kubernetes_manifest(manifest)
                else:
                    # Assume it's a regular manifest
                    return self.validate_manifest(manifest)
            else:
                logger.error("YAML content is not a valid manifest")
                return {"valid": False, "errors": ["YAML content is not a valid manifest"]}
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML: {str(e)}")
            return {"valid": False, "errors": [f"Invalid YAML: {str(e)}"]}
        except Exception as e:
            logger.error(f"Failed to validate YAML manifest: {str(e)}")
            return {"valid": False, "errors": [f"Failed to validate YAML manifest: {str(e)}"]}
    
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
    
    def get_validation_history(self, manifest_id: str) -> Dict[str, Any]:
        """
        Get validation history for a manifest.
        
        Args:
            manifest_id: ID of the manifest
            
        Returns:
            Dictionary with history retrieval result
        """
        if manifest_id not in self.validation_history:
            return {
                "success": True,
                "manifest_id": manifest_id,
                "history": []
            }
        
        history = self.validation_history[manifest_id]
        
        logger.info(f"Retrieved validation history for manifest {manifest_id}")
        
        return {
            "success": True,
            "manifest_id": manifest_id,
            "history": history
        }
    
    def _record_validation_event(self, manifest_id: str, schema_id: str, valid: bool, error: str = None):
        """
        Record a validation event.
        
        Args:
            manifest_id: ID of the manifest
            schema_id: ID of the schema
            valid: Whether validation was successful
            error: Error message (if validation failed)
        """
        # Create event
        event = {
            "manifest_id": manifest_id,
            "schema_id": schema_id,
            "timestamp": datetime.now().isoformat(),
            "valid": valid
        }
        
        if not valid and error:
            event["error"] = error
        
        # Initialize history for this manifest if it doesn't exist
        if manifest_id not in self.validation_history:
            self.validation_history[manifest_id] = []
        
        # Add event to history
        self.validation_history[manifest_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.validation_history[manifest_id]) > self.max_history_length:
            self.validation_history[manifest_id] = self.validation_history[manifest_id][-self.max_history_length:]
        
        logger.info(f"Recorded validation event for manifest {manifest_id}: {'valid' if valid else 'invalid'}")
    
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
        
        # Base manifest schema
        base_manifest_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "manifest_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "manifest_type": {"type": "string", "enum": ["deployment", "service", "configmap", "secret", "ingress", "volume"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {"type": "object"}
            }
        }
        
        # Deployment manifest schema
        deployment_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "manifest_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "manifest_type": {"type": "string", "enum": ["deployment"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {
                    "type": "object",
                    "required": ["apiVersion", "kind", "metadata", "spec"],
                    "properties": {
                        "apiVersion": {"type": "string"},
                        "kind": {"type": "string", "enum": ["Deployment"]},
                        "metadata": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string"},
                                "namespace": {"type": "string"},
                                "labels": {"type": "object"}
                            }
                        },
                        "spec": {
                            "type": "object",
                            "required": ["selector", "template"],
                            "properties": {
                                "replicas": {"type": "integer", "minimum": 1},
                                "selector": {"type": "object"},
                                "template": {"type": "object"}
                            }
                        }
                    }
                }
            }
        }
        
        # Service manifest schema
        service_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "manifest_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "manifest_type": {"type": "string", "enum": ["service"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {
                    "type": "object",
                    "required": ["apiVersion", "kind", "metadata", "spec"],
                    "properties": {
                        "apiVersion": {"type": "string"},
                        "kind": {"type": "string", "enum": ["Service"]},
                        "metadata": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string"},
                                "namespace": {"type": "string"},
                                "labels": {"type": "object"}
                            }
                        },
                        "spec": {
                            "type": "object",
                            "required": ["selector", "ports"],
                            "properties": {
                                "selector": {"type": "object"},
                                "ports": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "required": ["port"],
                                        "properties": {
                                            "name": {"type": "string"},
                                            "port": {"type": "integer", "minimum": 1},
                                            "targetPort": {"type": ["integer", "string"]},
                                            "protocol": {"type": "string", "enum": ["TCP", "UDP"]}
                                        }
                                    }
                                },
                                "type": {"type": "string", "enum": ["ClusterIP", "NodePort", "LoadBalancer", "ExternalName"]}
                            }
                        }
                    }
                }
            }
        }
        
        # ConfigMap manifest schema
        configmap_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "manifest_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "manifest_type": {"type": "string", "enum": ["configmap"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {
                    "type": "object",
                    "required": ["apiVersion", "kind", "metadata"],
                    "properties": {
                        "apiVersion": {"type": "string"},
                        "kind": {"type": "string", "enum": ["ConfigMap"]},
                        "metadata": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string"},
                                "namespace": {"type": "string"},
                                "labels": {"type": "object"}
                            }
                        },
                        "data": {"type": "object"}
                    }
                }
            }
        }
        
        # Secret manifest schema
        secret_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["id", "name", "description", "manifest_type", "content"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "manifest_type": {"type": "string", "enum": ["secret"]},
                "category": {"type": "string"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "created": {"type": "string", "format": "date-time"},
                "updated": {"type": "string", "format": "date-time"},
                "author": {"type": "string"},
                "version": {"type": "string"},
                "content": {
                    "type": "object",
                    "required": ["apiVersion", "kind", "metadata"],
                    "properties": {
                        "apiVersion": {"type": "string"},
                        "kind": {"type": "string", "enum": ["Secret"]},
                        "metadata": {
                            "type": "object",
                            "required": ["name"],
                            "properties": {
                                "name": {"type": "string"},
                                "namespace": {"type": "string"},
                                "labels": {"type": "object"}
                            }
                        },
                        "type": {"type": "string"},
                        "data": {"type": "object"},
                        "stringData": {"type": "object"}
                    }
                }
            }
        }
        
        # Kubernetes Deployment schema
        kubernetes_deployment_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["apiVersion", "kind", "metadata", "spec"],
            "properties": {
                "apiVersion": {"type": "string"},
                "kind": {"type": "string", "enum": ["Deployment"]},
                "metadata": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string"},
                        "namespace": {"type": "string"},
                        "labels": {"type": "object"}
                    }
                },
                "spec": {
                    "type": "object",
                    "required": ["selector", "template"],
                    "properties": {
                        "replicas": {"type": "integer", "minimum": 1},
                        "selector": {"type": "object"},
                        "template": {"type": "object"}
                    }
                }
            }
        }
        
        # Kubernetes Service schema
        kubernetes_service_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["apiVersion", "kind", "metadata", "spec"],
            "properties": {
                "apiVersion": {"type": "string"},
                "kind": {"type": "string", "enum": ["Service"]},
                "metadata": {
                    "type": "object",
                    "required": ["name"],
                    "properties": {
                        "name": {"type": "string"},
                        "namespace": {"type": "string"},
                        "labels": {"type": "object"}
                    }
                },
                "spec": {
                    "type": "object",
                    "required": ["selector", "ports"],
                    "properties": {
                        "selector": {"type": "object"},
                        "ports": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["port"],
                                "properties": {
                                    "name": {"type": "string"},
                                    "port": {"type": "integer", "minimum": 1},
                                    "targetPort": {"type": ["integer", "string"]},
                                    "protocol": {"type": "string", "enum": ["TCP", "UDP"]}
                                }
                            }
                        },
                        "type": {"type": "string", "enum": ["ClusterIP", "NodePort", "LoadBalancer", "ExternalName"]}
                    }
                }
            }
        }
        
        # Add schemas
        schemas["base-schema"] = base_manifest_schema
        schemas["deployment-schema"] = deployment_schema
        schemas["service-schema"] = service_schema
        schemas["configmap-schema"] = configmap_schema
        schemas["secret-schema"] = secret_schema
        schemas["kubernetes-deployment"] = kubernetes_deployment_schema
        schemas["kubernetes-service"] = kubernetes_service_schema
        
        return schemas
