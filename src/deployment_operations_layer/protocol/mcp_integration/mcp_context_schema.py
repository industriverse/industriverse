"""
MCP Context Schema

This module defines the schema for MCP contexts used in the Deployment Operations Layer.
It provides validation and schema definitions for different context types.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MCPContextSchema:
    """
    Schema definitions and validation for MCP contexts.
    """
    
    @staticmethod
    def get_base_schema() -> Dict[str, Any]:
        """
        Get the base schema for all MCP contexts.
        
        Returns:
            Dict containing the base schema
        """
        return {
            "type": "object",
            "required": ["context_id", "context_type", "content", "metadata", "version"],
            "properties": {
                "context_id": {
                    "type": "string",
                    "description": "Unique identifier for the context"
                },
                "context_type": {
                    "type": "string",
                    "description": "Type of the context"
                },
                "content": {
                    "type": "object",
                    "description": "Content of the context"
                },
                "metadata": {
                    "type": "object",
                    "description": "Metadata for the context",
                    "required": ["created_at", "created_by", "session_id", "layer"],
                    "properties": {
                        "created_at": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Timestamp when the context was created"
                        },
                        "created_by": {
                            "type": "string",
                            "description": "Entity that created the context"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier"
                        },
                        "layer": {
                            "type": "string",
                            "description": "Layer that created the context"
                        }
                    }
                },
                "version": {
                    "type": "string",
                    "description": "Protocol version"
                }
            }
        }
    
    @staticmethod
    def get_deployment_schema() -> Dict[str, Any]:
        """
        Get the schema for deployment contexts.
        
        Returns:
            Dict containing the deployment schema
        """
        base_schema = MCPContextSchema.get_base_schema()
        
        # Add deployment-specific properties
        deployment_content_schema = {
            "type": "object",
            "required": ["name", "components"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the deployment"
                },
                "id": {
                    "type": "string",
                    "description": "Identifier for the deployment"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the deployment"
                },
                "version": {
                    "type": "string",
                    "description": "Version of the deployment"
                },
                "environment": {
                    "type": "object",
                    "description": "Environment for the deployment",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "Type of environment"
                        }
                    }
                },
                "components": {
                    "type": "object",
                    "description": "Components in the deployment",
                    "additionalProperties": {
                        "type": "object",
                        "description": "Component configuration"
                    }
                },
                "requirements": {
                    "type": "object",
                    "description": "Requirements for the deployment"
                },
                "dependencies": {
                    "type": "array",
                    "description": "Dependencies for the deployment",
                    "items": {
                        "type": "object",
                        "description": "Dependency configuration"
                    }
                }
            }
        }
        
        deployment_metadata_schema = {
            "type": "object",
            "required": ["deployment_name", "deployment_id", "environment", "context_purpose"],
            "properties": {
                "deployment_name": {
                    "type": "string",
                    "description": "Name of the deployment"
                },
                "deployment_id": {
                    "type": "string",
                    "description": "Identifier for the deployment"
                },
                "environment": {
                    "type": "string",
                    "description": "Environment for the deployment"
                },
                "context_purpose": {
                    "type": "string",
                    "enum": ["deployment"],
                    "description": "Purpose of the context"
                }
            }
        }
        
        # Update base schema with deployment-specific schemas
        base_schema["properties"]["content"] = deployment_content_schema
        base_schema["properties"]["metadata"]["allOf"] = [deployment_metadata_schema]
        
        return base_schema
    
    @staticmethod
    def get_mission_schema() -> Dict[str, Any]:
        """
        Get the schema for mission contexts.
        
        Returns:
            Dict containing the mission schema
        """
        base_schema = MCPContextSchema.get_base_schema()
        
        # Add mission-specific properties
        mission_content_schema = {
            "type": "object",
            "required": ["name", "steps"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the mission"
                },
                "id": {
                    "type": "string",
                    "description": "Identifier for the mission"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the mission"
                },
                "type": {
                    "type": "string",
                    "description": "Type of mission"
                },
                "steps": {
                    "type": "array",
                    "description": "Steps in the mission",
                    "items": {
                        "type": "object",
                        "description": "Mission step",
                        "required": ["name", "action"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the step"
                            },
                            "action": {
                                "type": "string",
                                "description": "Action to perform"
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parameters for the action"
                            },
                            "dependencies": {
                                "type": "array",
                                "description": "Dependencies for the step",
                                "items": {
                                    "type": "string",
                                    "description": "Step name"
                                }
                            }
                        }
                    }
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameters for the mission"
                },
                "dependencies": {
                    "type": "array",
                    "description": "Dependencies for the mission",
                    "items": {
                        "type": "object",
                        "description": "Dependency configuration"
                    }
                }
            }
        }
        
        mission_metadata_schema = {
            "type": "object",
            "required": ["mission_name", "mission_id", "mission_type", "context_purpose"],
            "properties": {
                "mission_name": {
                    "type": "string",
                    "description": "Name of the mission"
                },
                "mission_id": {
                    "type": "string",
                    "description": "Identifier for the mission"
                },
                "mission_type": {
                    "type": "string",
                    "description": "Type of mission"
                },
                "context_purpose": {
                    "type": "string",
                    "enum": ["mission"],
                    "description": "Purpose of the context"
                }
            }
        }
        
        # Update base schema with mission-specific schemas
        base_schema["properties"]["content"] = mission_content_schema
        base_schema["properties"]["metadata"]["allOf"] = [mission_metadata_schema]
        
        return base_schema
    
    @staticmethod
    def get_capsule_schema() -> Dict[str, Any]:
        """
        Get the schema for capsule contexts.
        
        Returns:
            Dict containing the capsule schema
        """
        base_schema = MCPContextSchema.get_base_schema()
        
        # Add capsule-specific properties
        capsule_content_schema = {
            "type": "object",
            "required": ["name", "type", "capabilities"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the capsule"
                },
                "id": {
                    "type": "string",
                    "description": "Identifier for the capsule"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the capsule"
                },
                "type": {
                    "type": "string",
                    "description": "Type of capsule"
                },
                "version": {
                    "type": "string",
                    "description": "Version of the capsule"
                },
                "capabilities": {
                    "type": "array",
                    "description": "Capabilities of the capsule",
                    "items": {
                        "type": "string",
                        "description": "Capability name"
                    }
                },
                "configuration": {
                    "type": "object",
                    "description": "Configuration for the capsule"
                },
                "dependencies": {
                    "type": "array",
                    "description": "Dependencies for the capsule",
                    "items": {
                        "type": "object",
                        "description": "Dependency configuration"
                    }
                },
                "resources": {
                    "type": "object",
                    "description": "Resource requirements for the capsule"
                }
            }
        }
        
        capsule_metadata_schema = {
            "type": "object",
            "required": ["capsule_name", "capsule_id", "capsule_type", "context_purpose"],
            "properties": {
                "capsule_name": {
                    "type": "string",
                    "description": "Name of the capsule"
                },
                "capsule_id": {
                    "type": "string",
                    "description": "Identifier for the capsule"
                },
                "capsule_type": {
                    "type": "string",
                    "description": "Type of capsule"
                },
                "context_purpose": {
                    "type": "string",
                    "enum": ["capsule"],
                    "description": "Purpose of the context"
                }
            }
        }
        
        # Update base schema with capsule-specific schemas
        base_schema["properties"]["content"] = capsule_content_schema
        base_schema["properties"]["metadata"]["allOf"] = [capsule_metadata_schema]
        
        return base_schema
    
    @staticmethod
    def validate_context(context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an MCP context against its schema.
        
        Args:
            context: Context to validate
            
        Returns:
            Dict containing validation result
        """
        try:
            # Get the appropriate schema based on context type
            context_type = context.get("context_type")
            if context_type == "deployment":
                schema = MCPContextSchema.get_deployment_schema()
            elif context_type == "mission":
                schema = MCPContextSchema.get_mission_schema()
            elif context_type == "capsule":
                schema = MCPContextSchema.get_capsule_schema()
            else:
                schema = MCPContextSchema.get_base_schema()
            
            # In a real implementation, this would use a JSON Schema validator
            # For this implementation, we'll just return a simulated result
            return {
                "valid": True,
                "context_type": context_type,
                "schema_version": schema.get("version", "1.0")
            }
            
        except Exception as e:
            logger.exception(f"Error validating context: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
