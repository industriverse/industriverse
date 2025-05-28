"""
A2A Agent Schema

This module defines the schema for A2A agents and messages used in the Deployment Operations Layer.
It provides validation and schema definitions for different agent and message types.
"""

import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class A2AAgentSchema:
    """
    Schema definitions and validation for A2A agents and messages.
    """
    
    @staticmethod
    def get_agent_schema() -> Dict[str, Any]:
        """
        Get the schema for A2A agents.
        
        Returns:
            Dict containing the agent schema
        """
        return {
            "type": "object",
            "required": ["agentId", "displayName", "description", "capabilities"],
            "properties": {
                "agentId": {
                    "type": "string",
                    "description": "Unique identifier for the agent"
                },
                "displayName": {
                    "type": "string",
                    "description": "Display name for the agent"
                },
                "description": {
                    "type": "string",
                    "description": "Description of the agent"
                },
                "capabilities": {
                    "type": "array",
                    "description": "Capabilities of the agent",
                    "items": {
                        "type": "string",
                        "description": "Capability name"
                    }
                },
                "industryTags": {
                    "type": "array",
                    "description": "Industry tags for the agent",
                    "items": {
                        "type": "string",
                        "description": "Industry tag"
                    }
                },
                "priority": {
                    "type": "string",
                    "description": "Priority level for the agent",
                    "enum": ["low", "medium", "high", "critical"]
                },
                "logoUrl": {
                    "type": "string",
                    "description": "URL to the agent's logo"
                },
                "contactEmail": {
                    "type": "string",
                    "description": "Contact email for the agent"
                },
                "workflowTemplates": {
                    "type": "array",
                    "description": "Workflow templates supported by the agent",
                    "items": {
                        "type": "object",
                        "description": "Workflow template",
                        "required": ["name", "description", "steps"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "Name of the workflow template"
                            },
                            "description": {
                                "type": "string",
                                "description": "Description of the workflow template"
                            },
                            "steps": {
                                "type": "array",
                                "description": "Steps in the workflow template",
                                "items": {
                                    "type": "object",
                                    "description": "Workflow step",
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
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "version": {
                    "type": "string",
                    "description": "Version of the agent"
                },
                "apiVersion": {
                    "type": "string",
                    "description": "API version used by the agent"
                }
            }
        }
    
    @staticmethod
    def get_message_schema() -> Dict[str, Any]:
        """
        Get the schema for A2A messages.
        
        Returns:
            Dict containing the message schema
        """
        return {
            "type": "object",
            "required": ["id", "type", "content", "metadata"],
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique identifier for the message"
                },
                "type": {
                    "type": "string",
                    "description": "Type of message",
                    "enum": ["request", "response", "notification", "error"]
                },
                "content": {
                    "type": "object",
                    "description": "Content of the message"
                },
                "metadata": {
                    "type": "object",
                    "description": "Metadata for the message",
                    "properties": {
                        "timestamp": {
                            "type": "string",
                            "format": "date-time",
                            "description": "Timestamp when the message was created"
                        },
                        "source_agent_id": {
                            "type": "string",
                            "description": "ID of the source agent"
                        },
                        "target_agent_id": {
                            "type": "string",
                            "description": "ID of the target agent"
                        },
                        "session_id": {
                            "type": "string",
                            "description": "Session identifier"
                        },
                        "correlation_id": {
                            "type": "string",
                            "description": "Correlation identifier for related messages"
                        },
                        "reply_to": {
                            "type": "string",
                            "description": "Message ID to reply to"
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def get_request_schema() -> Dict[str, Any]:
        """
        Get the schema for A2A request messages.
        
        Returns:
            Dict containing the request schema
        """
        base_schema = A2AAgentSchema.get_message_schema()
        
        # Add request-specific properties
        request_content_schema = {
            "type": "object",
            "required": ["action"],
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform"
                },
                "parameters": {
                    "type": "object",
                    "description": "Parameters for the action"
                },
                "context": {
                    "type": "object",
                    "description": "Context for the action"
                }
            }
        }
        
        # Update base schema with request-specific schema
        base_schema["properties"]["type"]["enum"] = ["request"]
        base_schema["properties"]["content"] = request_content_schema
        
        return base_schema
    
    @staticmethod
    def get_response_schema() -> Dict[str, Any]:
        """
        Get the schema for A2A response messages.
        
        Returns:
            Dict containing the response schema
        """
        base_schema = A2AAgentSchema.get_message_schema()
        
        # Add response-specific properties
        response_content_schema = {
            "type": "object",
            "required": ["status"],
            "properties": {
                "status": {
                    "type": "string",
                    "description": "Status of the response",
                    "enum": ["success", "failure", "pending"]
                },
                "result": {
                    "type": "object",
                    "description": "Result of the action"
                },
                "error": {
                    "type": "object",
                    "description": "Error information if status is failure",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "Error code"
                        },
                        "message": {
                            "type": "string",
                            "description": "Error message"
                        },
                        "details": {
                            "type": "object",
                            "description": "Additional error details"
                        }
                    }
                }
            }
        }
        
        # Update base schema with response-specific schema
        base_schema["properties"]["type"]["enum"] = ["response"]
        base_schema["properties"]["content"] = response_content_schema
        
        return base_schema
    
    @staticmethod
    def validate_agent(agent: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an A2A agent against its schema.
        
        Args:
            agent: Agent to validate
            
        Returns:
            Dict containing validation result
        """
        try:
            # Get the agent schema
            schema = A2AAgentSchema.get_agent_schema()
            
            # In a real implementation, this would use a JSON Schema validator
            # For this implementation, we'll just return a simulated result
            return {
                "valid": True,
                "schema_version": schema.get("version", "1.0")
            }
            
        except Exception as e:
            logger.exception(f"Error validating agent: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate an A2A message against its schema.
        
        Args:
            message: Message to validate
            
        Returns:
            Dict containing validation result
        """
        try:
            # Get the appropriate schema based on message type
            message_type = message.get("type")
            if message_type == "request":
                schema = A2AAgentSchema.get_request_schema()
            elif message_type == "response":
                schema = A2AAgentSchema.get_response_schema()
            else:
                schema = A2AAgentSchema.get_message_schema()
            
            # In a real implementation, this would use a JSON Schema validator
            # For this implementation, we'll just return a simulated result
            return {
                "valid": True,
                "message_type": message_type,
                "schema_version": schema.get("version", "1.0")
            }
            
        except Exception as e:
            logger.exception(f"Error validating message: {str(e)}")
            return {
                "valid": False,
                "error": str(e)
            }
