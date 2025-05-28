"""
MCP Integration Manager

This module manages the integration with the Model Context Protocol (MCP) for the Deployment Operations Layer.
It provides standardized communication between components and layers using the MCP protocol.
"""

import logging
import json
import os
import uuid
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class MCPIntegrationManager:
    """
    Manager for MCP protocol integration.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MCP Integration Manager.
        
        Args:
            config_path: Path to MCP configuration file
        """
        self.config_path = config_path or os.environ.get(
            "MCP_CONFIG_PATH", "/var/lib/industriverse/protocol/mcp_config.json"
        )
        self.config = self._load_config()
        self.session_id = str(uuid.uuid4())
        logger.info("MCP Integration Manager initialized with session ID: %s", self.session_id)
    
    def create_context(self, 
                     context_type: str, 
                     content: Dict[str, Any],
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new MCP context.
        
        Args:
            context_type: Type of context
            content: Context content
            metadata: Optional metadata
            
        Returns:
            Dict containing the created context
        """
        logger.info(f"Creating MCP context of type: {context_type}")
        
        try:
            # Generate a unique context ID
            context_id = str(uuid.uuid4())
            
            # Create metadata if not provided
            if metadata is None:
                metadata = {}
            
            # Add standard metadata
            metadata.update({
                "created_at": self._get_timestamp(),
                "created_by": "deployment_ops_layer",
                "session_id": self.session_id,
                "layer": "deployment_ops"
            })
            
            # Create the context
            context = {
                "context_id": context_id,
                "context_type": context_type,
                "content": content,
                "metadata": metadata,
                "version": self.config.get("protocol_version", "1.0")
            }
            
            # Register the context
            self._register_context(context)
            
            return {
                "success": True,
                "context": context
            }
            
        except Exception as e:
            logger.exception(f"Error creating MCP context: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def update_context(self, 
                     context_id: str, 
                     content: Dict[str, Any],
                     metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Update an existing MCP context.
        
        Args:
            context_id: ID of the context to update
            content: New context content
            metadata: Optional new metadata
            
        Returns:
            Dict containing the updated context
        """
        logger.info(f"Updating MCP context: {context_id}")
        
        try:
            # Get the existing context
            existing_context = self._get_context(context_id)
            if not existing_context:
                return {
                    "success": False,
                    "error": f"Context not found: {context_id}"
                }
            
            # Update content
            existing_context["content"] = content
            
            # Update metadata if provided
            if metadata:
                existing_context["metadata"].update(metadata)
            
            # Add update timestamp
            existing_context["metadata"]["updated_at"] = self._get_timestamp()
            
            # Register the updated context
            self._register_context(existing_context)
            
            return {
                "success": True,
                "context": existing_context
            }
            
        except Exception as e:
            logger.exception(f"Error updating MCP context: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_context(self, context_id: str) -> Dict[str, Any]:
        """
        Get an MCP context by ID.
        
        Args:
            context_id: ID of the context to get
            
        Returns:
            Dict containing the context
        """
        logger.info(f"Getting MCP context: {context_id}")
        
        try:
            # Get the context
            context = self._get_context(context_id)
            if not context:
                return {
                    "success": False,
                    "error": f"Context not found: {context_id}"
                }
            
            return {
                "success": True,
                "context": context
            }
            
        except Exception as e:
            logger.exception(f"Error getting MCP context: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def delete_context(self, context_id: str) -> Dict[str, Any]:
        """
        Delete an MCP context.
        
        Args:
            context_id: ID of the context to delete
            
        Returns:
            Dict containing the result
        """
        logger.info(f"Deleting MCP context: {context_id}")
        
        try:
            # Get the context
            context = self._get_context(context_id)
            if not context:
                return {
                    "success": False,
                    "error": f"Context not found: {context_id}"
                }
            
            # Delete the context
            self._delete_context(context_id)
            
            return {
                "success": True,
                "context_id": context_id
            }
            
        except Exception as e:
            logger.exception(f"Error deleting MCP context: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def list_contexts(self, 
                    context_type: Optional[str] = None, 
                    metadata_filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        List MCP contexts.
        
        Args:
            context_type: Optional type filter
            metadata_filter: Optional metadata filter
            
        Returns:
            Dict containing the contexts
        """
        logger.info(f"Listing MCP contexts with type filter: {context_type}")
        
        try:
            # Get all contexts
            contexts = self._list_contexts()
            
            # Apply type filter
            if context_type:
                contexts = [c for c in contexts if c.get("context_type") == context_type]
            
            # Apply metadata filter
            if metadata_filter:
                filtered_contexts = []
                for context in contexts:
                    metadata = context.get("metadata", {})
                    match = True
                    for key, value in metadata_filter.items():
                        if key not in metadata or metadata[key] != value:
                            match = False
                            break
                    if match:
                        filtered_contexts.append(context)
                contexts = filtered_contexts
            
            return {
                "success": True,
                "contexts": contexts
            }
            
        except Exception as e:
            logger.exception(f"Error listing MCP contexts: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_deployment_context(self, 
                                deployment_manifest: Dict[str, Any],
                                metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a deployment context.
        
        Args:
            deployment_manifest: Deployment manifest
            metadata: Optional metadata
            
        Returns:
            Dict containing the created context
        """
        logger.info(f"Creating deployment context for: {deployment_manifest.get('name', 'unnamed')}")
        
        # Create standard metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "deployment_name": deployment_manifest.get("name", "unnamed"),
            "deployment_id": deployment_manifest.get("id", str(uuid.uuid4())),
            "environment": deployment_manifest.get("environment", {}).get("type", "unknown"),
            "context_purpose": "deployment"
        })
        
        # Create the context
        return self.create_context("deployment", deployment_manifest, metadata)
    
    def create_mission_context(self, 
                             mission_plan: Dict[str, Any],
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a mission context.
        
        Args:
            mission_plan: Mission plan
            metadata: Optional metadata
            
        Returns:
            Dict containing the created context
        """
        logger.info(f"Creating mission context for: {mission_plan.get('name', 'unnamed')}")
        
        # Create standard metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "mission_name": mission_plan.get("name", "unnamed"),
            "mission_id": mission_plan.get("id", str(uuid.uuid4())),
            "mission_type": mission_plan.get("type", "unknown"),
            "context_purpose": "mission"
        })
        
        # Create the context
        return self.create_context("mission", mission_plan, metadata)
    
    def create_capsule_context(self, 
                             capsule_definition: Dict[str, Any],
                             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a capsule context.
        
        Args:
            capsule_definition: Capsule definition
            metadata: Optional metadata
            
        Returns:
            Dict containing the created context
        """
        logger.info(f"Creating capsule context for: {capsule_definition.get('name', 'unnamed')}")
        
        # Create standard metadata
        if metadata is None:
            metadata = {}
        
        metadata.update({
            "capsule_name": capsule_definition.get("name", "unnamed"),
            "capsule_id": capsule_definition.get("id", str(uuid.uuid4())),
            "capsule_type": capsule_definition.get("type", "unknown"),
            "context_purpose": "capsule"
        })
        
        # Create the context
        return self.create_context("capsule", capsule_definition, metadata)
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load MCP configuration from file.
        
        Returns:
            Dict containing MCP configuration
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"MCP configuration file not found: {self.config_path}")
                return self._get_default_config()
                
        except Exception as e:
            logger.exception(f"Error loading MCP configuration: {str(e)}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default MCP configuration.
        
        Returns:
            Dict containing default MCP configuration
        """
        return {
            "protocol_version": "1.0",
            "storage_type": "memory",
            "context_ttl": 86400,  # 24 hours
            "max_context_size": 10485760,  # 10 MB
            "encryption": {
                "enabled": True,
                "algorithm": "AES-256-GCM"
            },
            "compression": {
                "enabled": True,
                "algorithm": "gzip",
                "threshold": 1024  # 1 KB
            },
            "validation": {
                "enabled": True,
                "schema_validation": True
            },
            "extensions": {
                "deployment_ops": {
                    "enabled": True,
                    "version": "1.0"
                }
            }
        }
    
    def _register_context(self, context: Dict[str, Any]):
        """
        Register a context in the storage.
        
        Args:
            context: Context to register
        """
        # In a real implementation, this would store the context in a database or other storage
        # For this implementation, we'll just log it
        logger.info(f"Registered MCP context: {context['context_id']}")
    
    def _get_context(self, context_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a context from storage.
        
        Args:
            context_id: ID of the context to get
            
        Returns:
            Context if found, None otherwise
        """
        # In a real implementation, this would retrieve the context from a database or other storage
        # For this implementation, we'll just return a simulated context
        return {
            "context_id": context_id,
            "context_type": "simulated",
            "content": {
                "name": "Simulated Context",
                "description": "This is a simulated context for demonstration purposes"
            },
            "metadata": {
                "created_at": self._get_timestamp(),
                "created_by": "deployment_ops_layer",
                "session_id": self.session_id,
                "layer": "deployment_ops"
            },
            "version": self.config.get("protocol_version", "1.0")
        }
    
    def _delete_context(self, context_id: str):
        """
        Delete a context from storage.
        
        Args:
            context_id: ID of the context to delete
        """
        # In a real implementation, this would delete the context from a database or other storage
        # For this implementation, we'll just log it
        logger.info(f"Deleted MCP context: {context_id}")
    
    def _list_contexts(self) -> List[Dict[str, Any]]:
        """
        List contexts from storage.
        
        Returns:
            List of contexts
        """
        # In a real implementation, this would retrieve contexts from a database or other storage
        # For this implementation, we'll just return simulated contexts
        return [
            {
                "context_id": str(uuid.uuid4()),
                "context_type": "deployment",
                "content": {
                    "name": "Simulated Deployment",
                    "description": "This is a simulated deployment context"
                },
                "metadata": {
                    "created_at": self._get_timestamp(),
                    "created_by": "deployment_ops_layer",
                    "session_id": self.session_id,
                    "layer": "deployment_ops",
                    "deployment_name": "Simulated Deployment",
                    "environment": "simulated"
                },
                "version": self.config.get("protocol_version", "1.0")
            },
            {
                "context_id": str(uuid.uuid4()),
                "context_type": "mission",
                "content": {
                    "name": "Simulated Mission",
                    "description": "This is a simulated mission context"
                },
                "metadata": {
                    "created_at": self._get_timestamp(),
                    "created_by": "deployment_ops_layer",
                    "session_id": self.session_id,
                    "layer": "deployment_ops",
                    "mission_name": "Simulated Mission",
                    "mission_type": "simulated"
                },
                "version": self.config.get("protocol_version", "1.0")
            }
        ]
    
    def _get_timestamp(self):
        """Get the current timestamp."""
        import datetime
        return datetime.datetime.utcnow().isoformat()
