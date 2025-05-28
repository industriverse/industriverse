"""
Capsule Memory Manager Module for the Workflow Automation Layer.

This agent manages the memory and state persistence for Dynamic Agent Capsules,
enabling context retention across workflow executions and providing a memory
system for long-running workflows and agent interactions.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CapsuleMemoryManager:
    """Agent for managing memory and state persistence for Dynamic Agent Capsules."""

    def __init__(self, workflow_runtime):
        """Initialize the capsule memory manager.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "capsule-memory-manager"
        self.agent_capabilities = ["memory_management", "state_persistence", "context_retention"]
        self.supported_protocols = ["MCP", "A2A"]
        
        # Memory storage structures
        self.short_term_memory = {}  # Fast access, limited retention
        self.long_term_memory = {}   # Persistent storage
        self.episodic_memory = {}    # Execution episode records
        self.semantic_memory = {}    # Concept and relationship storage
        
        # Memory configuration
        self.short_term_retention = timedelta(hours=24)  # Default retention period
        self.memory_compression_enabled = True
        self.memory_encryption_enabled = True
        
        logger.info("Capsule Memory Manager initialized")

    async def store_memory(self, memory_request: Dict[str, Any]) -> Dict[str, Any]:
        """Store a memory item.

        Args:
            memory_request: Request data including memory_type, capsule_id, key, value, etc.

        Returns:
            Dict containing storage status.
        """
        try:
            # Validate required fields
            required_fields = ["memory_type", "capsule_id", "key", "value"]
            for field in required_fields:
                if field not in memory_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            memory_type = memory_request["memory_type"]
            capsule_id = memory_request["capsule_id"]
            key = memory_request["key"]
            value = memory_request["value"]
            ttl = memory_request.get("ttl")  # Time to live in seconds (optional)
            
            # Validate memory type
            valid_memory_types = ["short_term", "long_term", "episodic", "semantic"]
            if memory_type not in valid_memory_types:
                return {
                    "success": False,
                    "error": f"Invalid memory type: {memory_type}. Must be one of {valid_memory_types}"
                }
            
            # Process based on memory type
            memory_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            memory_item = {
                "memory_id": memory_id,
                "capsule_id": capsule_id,
                "key": key,
                "value": value,
                "created_at": timestamp,
                "last_accessed": timestamp,
                "access_count": 0
            }
            
            # Add TTL if provided
            if ttl is not None:
                if memory_type == "short_term":
                    expiry = datetime.utcnow() + timedelta(seconds=ttl)
                    memory_item["expires_at"] = expiry.isoformat()
            elif memory_type == "short_term":
                # Default TTL for short-term memory
                expiry = datetime.utcnow() + self.short_term_retention
                memory_item["expires_at"] = expiry.isoformat()
            
            # Store in appropriate memory store
            if memory_type == "short_term":
                if capsule_id not in self.short_term_memory:
                    self.short_term_memory[capsule_id] = {}
                self.short_term_memory[capsule_id][key] = memory_item
            elif memory_type == "long_term":
                if capsule_id not in self.long_term_memory:
                    self.long_term_memory[capsule_id] = {}
                self.long_term_memory[capsule_id][key] = memory_item
            elif memory_type == "episodic":
                if capsule_id not in self.episodic_memory:
                    self.episodic_memory[capsule_id] = {}
                self.episodic_memory[capsule_id][key] = memory_item
            elif memory_type == "semantic":
                if capsule_id not in self.semantic_memory:
                    self.semantic_memory[capsule_id] = {}
                self.semantic_memory[capsule_id][key] = memory_item
            
            # Apply memory compression if enabled and value is large
            if self.memory_compression_enabled and isinstance(value, str) and len(value) > 1000:
                # In a real implementation, this would compress the value
                memory_item["compressed"] = True
            
            # Apply memory encryption if enabled
            if self.memory_encryption_enabled:
                # In a real implementation, this would encrypt sensitive values
                memory_item["encrypted"] = True
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "store_memory",
                "reason": f"Stored {memory_type} memory for capsule {capsule_id} with key {key}",
                "timestamp": timestamp
            }
            
            # Add to workflow telemetry if associated with a workflow
            workflow_id = memory_request.get("workflow_id")
            if workflow_id:
                self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Stored {memory_type} memory {memory_id} for capsule {capsule_id}")
            
            return {
                "success": True,
                "memory_id": memory_id,
                "memory_type": memory_type,
                "capsule_id": capsule_id,
                "key": key
            }
            
        except Exception as e:
            logger.error(f"Error storing memory: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def retrieve_memory(self, memory_request: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve a memory item.

        Args:
            memory_request: Request data including memory_type, capsule_id, key, etc.

        Returns:
            Dict containing retrieved memory or error.
        """
        try:
            # Validate required fields
            required_fields = ["memory_type", "capsule_id", "key"]
            for field in required_fields:
                if field not in memory_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            memory_type = memory_request["memory_type"]
            capsule_id = memory_request["capsule_id"]
            key = memory_request["key"]
            
            # Validate memory type
            valid_memory_types = ["short_term", "long_term", "episodic", "semantic"]
            if memory_type not in valid_memory_types:
                return {
                    "success": False,
                    "error": f"Invalid memory type: {memory_type}. Must be one of {valid_memory_types}"
                }
            
            # Retrieve from appropriate memory store
            memory_store = None
            if memory_type == "short_term":
                memory_store = self.short_term_memory
            elif memory_type == "long_term":
                memory_store = self.long_term_memory
            elif memory_type == "episodic":
                memory_store = self.episodic_memory
            elif memory_type == "semantic":
                memory_store = self.semantic_memory
            
            if not memory_store or capsule_id not in memory_store or key not in memory_store[capsule_id]:
                return {
                    "success": False,
                    "error": f"Memory not found for {memory_type}/{capsule_id}/{key}"
                }
            
            memory_item = memory_store[capsule_id][key]
            
            # Check if memory has expired (for short-term)
            if memory_type == "short_term" and "expires_at" in memory_item:
                expiry = datetime.fromisoformat(memory_item["expires_at"])
                if datetime.utcnow() > expiry:
                    # Memory has expired, remove it
                    del memory_store[capsule_id][key]
                    return {
                        "success": False,
                        "error": f"Memory has expired for {memory_type}/{capsule_id}/{key}"
                    }
            
            # Update access metadata
            memory_item["last_accessed"] = datetime.utcnow().isoformat()
            memory_item["access_count"] += 1
            
            # Decompress if needed
            value = memory_item["value"]
            if memory_item.get("compressed", False):
                # In a real implementation, this would decompress the value
                pass
            
            # Decrypt if needed
            if memory_item.get("encrypted", False):
                # In a real implementation, this would decrypt the value
                pass
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "retrieve_memory",
                "reason": f"Retrieved {memory_type} memory for capsule {capsule_id} with key {key}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry if associated with a workflow
            workflow_id = memory_request.get("workflow_id")
            if workflow_id:
                self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Retrieved {memory_type} memory for capsule {capsule_id} with key {key}")
            
            return {
                "success": True,
                "memory_type": memory_type,
                "capsule_id": capsule_id,
                "key": key,
                "value": value,
                "created_at": memory_item["created_at"],
                "last_accessed": memory_item["last_accessed"],
                "access_count": memory_item["access_count"]
            }
            
        except Exception as e:
            logger.error(f"Error retrieving memory: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def update_memory(self, memory_request: Dict[str, Any]) -> Dict[str, Any]:
        """Update a memory item.

        Args:
            memory_request: Request data including memory_type, capsule_id, key, value, etc.

        Returns:
            Dict containing update status.
        """
        try:
            # Validate required fields
            required_fields = ["memory_type", "capsule_id", "key", "value"]
            for field in required_fields:
                if field not in memory_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            memory_type = memory_request["memory_type"]
            capsule_id = memory_request["capsule_id"]
            key = memory_request["key"]
            value = memory_request["value"]
            ttl = memory_request.get("ttl")  # Time to live in seconds (optional)
            
            # Validate memory type
            valid_memory_types = ["short_term", "long_term", "episodic", "semantic"]
            if memory_type not in valid_memory_types:
                return {
                    "success": False,
                    "error": f"Invalid memory type: {memory_type}. Must be one of {valid_memory_types}"
                }
            
            # Get appropriate memory store
            memory_store = None
            if memory_type == "short_term":
                memory_store = self.short_term_memory
            elif memory_type == "long_term":
                memory_store = self.long_term_memory
            elif memory_type == "episodic":
                memory_store = self.episodic_memory
            elif memory_type == "semantic":
                memory_store = self.semantic_memory
            
            if not memory_store or capsule_id not in memory_store or key not in memory_store[capsule_id]:
                return {
                    "success": False,
                    "error": f"Memory not found for {memory_type}/{capsule_id}/{key}"
                }
            
            memory_item = memory_store[capsule_id][key]
            
            # Update value and metadata
            memory_item["value"] = value
            memory_item["last_accessed"] = datetime.utcnow().isoformat()
            memory_item["access_count"] += 1
            
            # Update TTL if provided
            if ttl is not None:
                if memory_type == "short_term":
                    expiry = datetime.utcnow() + timedelta(seconds=ttl)
                    memory_item["expires_at"] = expiry.isoformat()
            
            # Apply memory compression if enabled and value is large
            if self.memory_compression_enabled and isinstance(value, str) and len(value) > 1000:
                # In a real implementation, this would compress the value
                memory_item["compressed"] = True
            else:
                memory_item["compressed"] = False
            
            # Apply memory encryption if enabled
            if self.memory_encryption_enabled:
                # In a real implementation, this would encrypt sensitive values
                memory_item["encrypted"] = True
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "update_memory",
                "reason": f"Updated {memory_type} memory for capsule {capsule_id} with key {key}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry if associated with a workflow
            workflow_id = memory_request.get("workflow_id")
            if workflow_id:
                self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Updated {memory_type} memory for capsule {capsule_id} with key {key}")
            
            return {
                "success": True,
                "memory_type": memory_type,
                "capsule_id": capsule_id,
                "key": key
            }
            
        except Exception as e:
            logger.error(f"Error updating memory: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def delete_memory(self, memory_request: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a memory item.

        Args:
            memory_request: Request data including memory_type, capsule_id, key, etc.

        Returns:
            Dict containing deletion status.
        """
        try:
            # Validate required fields
            required_fields = ["memory_type", "capsule_id", "key"]
            for field in required_fields:
                if field not in memory_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            memory_type = memory_request["memory_type"]
            capsule_id = memory_request["capsule_id"]
            key = memory_request["key"]
            
            # Validate memory type
            valid_memory_types = ["short_term", "long_term", "episodic", "semantic"]
            if memory_type not in valid_memory_types:
                return {
                    "success": False,
                    "error": f"Invalid memory type: {memory_type}. Must be one of {valid_memory_types}"
                }
            
            # Get appropriate memory store
            memory_store = None
            if memory_type == "short_term":
                memory_store = self.short_term_memory
            elif memory_type == "long_term":
                memory_store = self.long_term_memory
            elif memory_type == "episodic":
                memory_store = self.episodic_memory
            elif memory_type == "semantic":
                memory_store = self.semantic_memory
            
            if not memory_store or capsule_id not in memory_store or key not in memory_store[capsule_id]:
                return {
                    "success": False,
                    "error": f"Memory not found for {memory_type}/{capsule_id}/{key}"
                }
            
            # Delete the memory
            del memory_store[capsule_id][key]
            
            # Clean up empty dictionaries
            if not memory_store[capsule_id]:
                del memory_store[capsule_id]
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "delete_memory",
                "reason": f"Deleted {memory_type} memory for capsule {capsule_id} with key {key}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry if associated with a workflow
            workflow_id = memory_request.get("workflow_id")
            if workflow_id:
                self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Deleted {memory_type} memory for capsule {capsule_id} with key {key}")
            
            return {
                "success": True,
                "memory_type": memory_type,
                "capsule_id": capsule_id,
                "key": key
            }
            
        except Exception as e:
            logger.error(f"Error deleting memory: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def list_memories(self, memory_request: Dict[str, Any]) -> Dict[str, Any]:
        """List memory items for a capsule.

        Args:
            memory_request: Request data including memory_type, capsule_id, etc.

        Returns:
            Dict containing list of memories.
        """
        try:
            # Validate required fields
            required_fields = ["memory_type", "capsule_id"]
            for field in required_fields:
                if field not in memory_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            memory_type = memory_request["memory_type"]
            capsule_id = memory_request["capsule_id"]
            
            # Validate memory type
            valid_memory_types = ["short_term", "long_term", "episodic", "semantic", "all"]
            if memory_type not in valid_memory_types:
                return {
                    "success": False,
                    "error": f"Invalid memory type: {memory_type}. Must be one of {valid_memory_types}"
                }
            
            memories = {}
            
            # Get memories from appropriate stores
            if memory_type == "short_term" or memory_type == "all":
                if capsule_id in self.short_term_memory:
                    memories["short_term"] = list(self.short_term_memory[capsule_id].keys())
            
            if memory_type == "long_term" or memory_type == "all":
                if capsule_id in self.long_term_memory:
                    memories["long_term"] = list(self.long_term_memory[capsule_id].keys())
            
            if memory_type == "episodic" or memory_type == "all":
                if capsule_id in self.episodic_memory:
                    memories["episodic"] = list(self.episodic_memory[capsule_id].keys())
            
            if memory_type == "semantic" or memory_type == "all":
                if capsule_id in self.semantic_memory:
                    memories["semantic"] = list(self.semantic_memory[capsule_id].keys())
            
            logger.info(f"Listed memories for capsule {capsule_id} of type {memory_type}")
            
            return {
                "success": True,
                "capsule_id": capsule_id,
                "memories": memories
            }
            
        except Exception as e:
            logger.error(f"Error listing memories: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def transfer_memory(self, memory_request: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer memory from one capsule to another.

        Args:
            memory_request: Request data including source_capsule_id, target_capsule_id, etc.

        Returns:
            Dict containing transfer status.
        """
        try:
            # Validate required fields
            required_fields = ["memory_type", "source_capsule_id", "target_capsule_id", "key"]
            for field in required_fields:
                if field not in memory_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            memory_type = memory_request["memory_type"]
            source_capsule_id = memory_request["source_capsule_id"]
            target_capsule_id = memory_request["target_capsule_id"]
            key = memory_request["key"]
            
            # Validate memory type
            valid_memory_types = ["short_term", "long_term", "episodic", "semantic"]
            if memory_type not in valid_memory_types:
                return {
                    "success": False,
                    "error": f"Invalid memory type: {memory_type}. Must be one of {valid_memory_types}"
                }
            
            # Get appropriate memory store
            memory_store = None
            if memory_type == "short_term":
                memory_store = self.short_term_memory
            elif memory_type == "long_term":
                memory_store = self.long_term_memory
            elif memory_type == "episodic":
                memory_store = self.episodic_memory
            elif memory_type == "semantic":
                memory_store = self.semantic_memory
            
            if not memory_store or source_capsule_id not in memory_store or key not in memory_store[source_capsule_id]:
                return {
                    "success": False,
                    "error": f"Memory not found for {memory_type}/{source_capsule_id}/{key}"
                }
            
            # Get the memory item
            memory_item = memory_store[source_capsule_id][key]
            
            # Create a copy for the target capsule
            new_memory_id = str(uuid.uuid4())
            timestamp = datetime.utcnow().isoformat()
            
            new_memory_item = {
                "memory_id": new_memory_id,
                "capsule_id": target_capsule_id,
                "key": key,
                "value": memory_item["value"],
                "created_at": timestamp,
                "last_accessed": timestamp,
                "access_count": 0,
                "transferred_from": source_capsule_id,
                "original_memory_id": memory_item["memory_id"]
            }
            
            # Add TTL if applicable
            if "expires_at" in memory_item:
                new_memory_item["expires_at"] = memory_item["expires_at"]
            
            # Copy compression and encryption flags
            if "compressed" in memory_item:
                new_memory_item["compressed"] = memory_item["compressed"]
            
            if "encrypted" in memory_item:
                new_memory_item["encrypted"] = memory_item["encrypted"]
            
            # Store in target capsule
            if target_capsule_id not in memory_store:
                memory_store[target_capsule_id] = {}
            memory_store[target_capsule_id][key] = new_memory_item
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "transfer_memory",
                "reason": f"Transferred {memory_type} memory for key {key} from capsule {source_capsule_id} to {target_capsule_id}",
                "timestamp": timestamp
            }
            
            # Add to workflow telemetry if associated with a workflow
            workflow_id = memory_request.get("workflow_id")
            if workflow_id:
                self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Transferred {memory_type} memory for key {key} from capsule {source_capsule_id} to {target_capsule_id}")
            
            return {
                "success": True,
                "memory_type": memory_type,
                "source_capsule_id": source_capsule_id,
                "target_capsule_id": target_capsule_id,
                "key": key,
                "new_memory_id": new_memory_id
            }
            
        except Exception as e:
            logger.error(f"Error transferring memory: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def clean_expired_memories(self) -> Dict[str, Any]:
        """Clean up expired memories from short-term storage.

        Returns:
            Dict containing cleanup status.
        """
        try:
            cleaned_count = 0
            now = datetime.utcnow()
            
            # Only short-term memories have expiration
            for capsule_id in list(self.short_term_memory.keys()):
                for key in list(self.short_term_memory[capsule_id].keys()):
                    memory_item = self.short_term_memory[capsule_id][key]
                    if "expires_at" in memory_item:
                        expiry = datetime.fromisoformat(memory_item["expires_at"])
                        if now > expiry:
                            del self.short_term_memory[capsule_id][key]
                            cleaned_count += 1
                
                # Clean up empty dictionaries
                if not self.short_term_memory[capsule_id]:
                    del self.short_term_memory[capsule_id]
            
            logger.info(f"Cleaned {cleaned_count} expired memories")
            
            return {
                "success": True,
                "cleaned_count": cleaned_count
            }
            
        except Exception as e:
            logger.error(f"Error cleaning expired memories: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_agent_manifest(self) -> Dict[str, Any]:
        """Get the agent manifest.

        Returns:
            Dict containing agent manifest information.
        """
        return {
            "agent_id": self.agent_id,
            "layer": "workflow_layer",
            "capabilities": self.agent_capabilities,
            "supported_protocols": self.supported_protocols,
            "resilience_mode": "persistent",
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": False,
                "editable_nodes": ["memory_manager_node"]
            }
        }

    async def handle_protocol_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a protocol message.

        Args:
            message: Protocol message to handle.

        Returns:
            Dict containing handling result.
        """
        try:
            message_type = message.get("message_type")
            payload = message.get("payload", {})
            
            if message_type == "store_memory":
                return await self.store_memory(payload)
            elif message_type == "retrieve_memory":
                return await self.retrieve_memory(payload)
            elif message_type == "update_memory":
                return await self.update_memory(payload)
            elif message_type == "delete_memory":
                return await self.delete_memory(payload)
            elif message_type == "list_memories":
                return await self.list_memories(payload)
            elif message_type == "transfer_memory":
                return await self.transfer_memory(payload)
            elif message_type == "clean_expired_memories":
                return await self.clean_expired_memories()
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type}"
                }
                
        except Exception as e:
            logger.error(f"Error handling protocol message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
