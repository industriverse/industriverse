"""
Protocol Translator for Industriverse Generative Layer

This module implements bidirectional translation between MCP and A2A protocols,
ensuring context preservation when crossing protocol boundaries and maintaining
consistent identity mapping between protocols.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProtocolTranslator:
    """
    Translates between MCP and A2A protocols for the Generative Layer.
    Ensures context preservation and consistent identity mapping.
    """
    
    def __init__(self):
        """Initialize the protocol translator."""
        self.context_cache = {}
        logger.info("Protocol Translator initialized")
        
    def mcp_to_a2a(self, mcp_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate an MCP event to an A2A message.
        
        Args:
            mcp_event: The MCP event to translate
            
        Returns:
            The translated A2A message
        """
        logger.debug(f"Translating MCP event to A2A: {mcp_event.get('type', 'unknown')}")
        
        # Extract key information from MCP event
        event_type = mcp_event.get("type", "")
        event_payload = mcp_event.get("payload", {})
        event_context = mcp_event.get("context", {})
        event_id = mcp_event.get("id", "")
        
        # Cache the context for later reference
        if event_id:
            self.context_cache[event_id] = event_context
        
        # Map MCP event types to A2A task types
        task_type_mapping = {
            "observe/template_status": "query",
            "simulate/generation_preview": "preview",
            "recommend/template_selection": "recommend",
            "act/generate_artifact": "generate",
            "generate/artifact": "generate",
            "generation/workflow_collaboration": "collaborate"
        }
        
        # Default to "task" if no specific mapping exists
        task_type = task_type_mapping.get(event_type, "task")
        
        # Create A2A message parts based on payload
        parts = []
        
        # Add text part if there's a prompt or description
        if "prompt" in event_payload or "description" in event_payload:
            text_content = event_payload.get("prompt", event_payload.get("description", ""))
            parts.append({
                "type": "text",
                "text": text_content
            })
        
        # Add data part for structured data
        if "data" in event_payload or "parameters" in event_payload:
            data_content = event_payload.get("data", event_payload.get("parameters", {}))
            parts.append({
                "type": "data",
                "data": data_content
            })
        
        # Add file parts if files are included
        if "files" in event_payload:
            for file_info in event_payload["files"]:
                parts.append({
                    "type": "file",
                    "file": {
                        "name": file_info.get("name", ""),
                        "url": file_info.get("url", ""),
                        "mime_type": file_info.get("mime_type", "application/octet-stream")
                    }
                })
        
        # Construct the A2A message
        a2a_message = {
            "task_id": event_id,
            "type": task_type,
            "parts": parts,
            "metadata": {
                "source_protocol": "mcp",
                "source_event_type": event_type,
                "context_id": event_id,
                "industry_tags": event_context.get("industry_tags", []),
                "priority": event_context.get("priority", 5)
            }
        }
        
        logger.debug(f"Translated A2A message: {a2a_message}")
        return a2a_message
    
    def a2a_to_mcp(self, a2a_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate an A2A message to an MCP event.
        
        Args:
            a2a_message: The A2A message to translate
            
        Returns:
            The translated MCP event
        """
        logger.debug(f"Translating A2A message to MCP: {a2a_message.get('type', 'unknown')}")
        
        # Extract key information from A2A message
        task_id = a2a_message.get("task_id", "")
        task_type = a2a_message.get("type", "")
        parts = a2a_message.get("parts", [])
        metadata = a2a_message.get("metadata", {})
        
        # Map A2A task types to MCP event types
        event_type_mapping = {
            "query": "observe/template_status",
            "preview": "simulate/generation_preview",
            "recommend": "recommend/template_selection",
            "generate": "act/generate_artifact",
            "collaborate": "generation/workflow_collaboration"
        }
        
        # Default to "generate/artifact" if no specific mapping exists
        event_type = event_type_mapping.get(task_type, "generate/artifact")
        
        # Construct payload from parts
        payload = {}
        
        # Process text parts
        text_parts = [p for p in parts if p.get("type") == "text"]
        if text_parts:
            payload["prompt"] = text_parts[0].get("text", "")
            
            # If there are multiple text parts, concatenate them
            if len(text_parts) > 1:
                payload["additional_context"] = "\n".join([p.get("text", "") for p in text_parts[1:]])
        
        # Process data parts
        data_parts = [p for p in parts if p.get("type") == "data"]
        if data_parts:
            payload["parameters"] = data_parts[0].get("data", {})
            
            # If there are multiple data parts, merge them
            if len(data_parts) > 1:
                for p in data_parts[1:]:
                    payload["parameters"].update(p.get("data", {}))
        
        # Process file parts
        file_parts = [p for p in parts if p.get("type") == "file"]
        if file_parts:
            payload["files"] = []
            for p in file_parts:
                file_info = p.get("file", {})
                payload["files"].append({
                    "name": file_info.get("name", ""),
                    "url": file_info.get("url", ""),
                    "mime_type": file_info.get("mime_type", "application/octet-stream")
                })
        
        # Retrieve cached context if available
        context = self.context_cache.get(metadata.get("context_id", ""), {})
        
        # Update context with metadata
        context.update({
            "industry_tags": metadata.get("industry_tags", []),
            "priority": metadata.get("priority", 5),
            "source_protocol": "a2a"
        })
        
        # Construct the MCP event
        mcp_event = {
            "id": task_id,
            "type": event_type,
            "payload": payload,
            "context": context
        }
        
        logger.debug(f"Translated MCP event: {mcp_event}")
        return mcp_event
    
    def preserve_context(self, source_id: str, target_id: str) -> None:
        """
        Preserve context when crossing protocol boundaries.
        
        Args:
            source_id: The ID of the source message/event
            target_id: The ID of the target message/event
        """
        if source_id in self.context_cache:
            self.context_cache[target_id] = self.context_cache[source_id].copy()
            logger.debug(f"Context preserved from {source_id} to {target_id}")
    
    def clear_context(self, message_id: str) -> None:
        """
        Clear cached context for a specific message/event.
        
        Args:
            message_id: The ID of the message/event
        """
        if message_id in self.context_cache:
            del self.context_cache[message_id]
            logger.debug(f"Context cleared for {message_id}")
    
    def get_identity_mapping(self, protocol_id: str, protocol_type: str) -> Optional[str]:
        """
        Get the corresponding ID in the other protocol.
        
        Args:
            protocol_id: The ID in the source protocol
            protocol_type: The source protocol type ("mcp" or "a2a")
            
        Returns:
            The corresponding ID in the other protocol, if available
        """
        # This is a simplified implementation
        # In a real system, this would query a persistent mapping store
        if protocol_type == "mcp":
            # MCP to A2A mapping
            return f"a2a-{protocol_id}"
        elif protocol_type == "a2a":
            # A2A to MCP mapping
            return f"mcp-{protocol_id}"
        return None
