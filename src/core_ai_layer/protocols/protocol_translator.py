"""
Protocol Translator for Industriverse Core AI Layer

This module implements bidirectional translation between MCP and A2A protocols,
ensuring context preservation when crossing protocol boundaries.
"""

import json
import logging
import uuid
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProtocolTranslator:
    """
    Translates between MCP (Model Context Protocol) and A2A (Agent-to-Agent) protocols.
    Preserves context, intent, history, and metadata during translation.
    """
    
    def __init__(self):
        """Initialize the protocol translator."""
        self.translation_history = {}
        self.context_map = {}
        
    def mcp_to_a2a(self, mcp_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate an MCP event to an A2A message.
        
        Args:
            mcp_event: The MCP event to translate
            
        Returns:
            The translated A2A message
        """
        logger.info(f"Translating MCP event to A2A: {mcp_event.get('event_type', 'unknown')}")
        
        # Generate a unique ID for this translation
        translation_id = str(uuid.uuid4())
        
        # Extract key MCP fields
        event_type = mcp_event.get("event_type")
        context = mcp_event.get("context", {})
        payload = mcp_event.get("payload", {})
        source = mcp_event.get("source", "unknown")
        
        # Map MCP event types to A2A task states
        task_state_mapping = {
            "observe": "submitted",
            "simulate": "working",
            "recommend": "working",
            "act": "completed"
        }
        
        # Create A2A message parts
        message_parts = []
        
        # Add text part if there's a text payload
        if "text" in payload:
            message_parts.append({
                "type": "TextPart",
                "text": payload["text"]
            })
            
        # Add file part if there's a file payload
        if "file" in payload:
            message_parts.append({
                "type": "FilePart",
                "file_name": payload["file"].get("name", "file.txt"),
                "mime_type": payload["file"].get("mime_type", "text/plain"),
                "file_url": payload["file"].get("url", "")
            })
            
        # Add data part for structured data
        if "data" in payload:
            message_parts.append({
                "type": "DataPart",
                "mime_type": "application/json",
                "data": json.dumps(payload["data"])
            })
        
        # Create the A2A message
        a2a_message = {
            "task_id": context.get("conversation_id", translation_id),
            "state": task_state_mapping.get(event_type, "submitted"),
            "agent": {
                "id": source,
                "name": source.replace("-agent", "").title()
            },
            "parts": message_parts,
            "metadata": {
                "original_protocol": "mcp",
                "translation_id": translation_id,
                "mcp_event_type": event_type,
                "industry_tags": context.get("industry_tags", []),
                "priority": context.get("priority", 5)
            }
        }
        
        # Store the mapping for future reference
        self.context_map[translation_id] = {
            "mcp_context": context,
            "a2a_task_id": a2a_message["task_id"]
        }
        
        logger.info(f"Translated MCP to A2A: {translation_id}")
        return a2a_message
    
    def a2a_to_mcp(self, a2a_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate an A2A message to an MCP event.
        
        Args:
            a2a_message: The A2A message to translate
            
        Returns:
            The translated MCP event
        """
        logger.info(f"Translating A2A message to MCP: {a2a_message.get('task_id', 'unknown')}")
        
        # Generate a unique ID for this translation
        translation_id = str(uuid.uuid4())
        
        # Extract key A2A fields
        task_id = a2a_message.get("task_id", translation_id)
        state = a2a_message.get("state", "submitted")
        agent_info = a2a_message.get("agent", {})
        parts = a2a_message.get("parts", [])
        metadata = a2a_message.get("metadata", {})
        
        # Map A2A task states to MCP event types
        event_type_mapping = {
            "submitted": "observe",
            "working": "simulate",
            "input-required": "recommend",
            "completed": "act"
        }
        
        # Build the payload from message parts
        payload = {}
        
        for part in parts:
            part_type = part.get("type")
            
            if part_type == "TextPart":
                payload["text"] = part.get("text", "")
                
            elif part_type == "FilePart":
                payload["file"] = {
                    "name": part.get("file_name", "file.txt"),
                    "mime_type": part.get("mime_type", "text/plain"),
                    "url": part.get("file_url", "")
                }
                
            elif part_type == "DataPart":
                try:
                    payload["data"] = json.loads(part.get("data", "{}"))
                except json.JSONDecodeError:
                    payload["data"] = {}
        
        # Check if we have a stored context for this task
        stored_context = None
        for tid, mapping in self.context_map.items():
            if mapping["a2a_task_id"] == task_id:
                stored_context = mapping["mcp_context"]
                break
        
        # Create context with preserved fields
        context = stored_context or {}
        
        # Update with metadata from A2A
        if "industry_tags" in metadata:
            context["industry_tags"] = metadata["industry_tags"]
        
        if "priority" in metadata:
            context["priority"] = metadata["priority"]
            
        # Create the MCP event
        mcp_event = {
            "event_type": event_type_mapping.get(state, "observe"),
            "source": agent_info.get("id", "unknown"),
            "context": context,
            "payload": payload,
            "metadata": {
                "original_protocol": "a2a",
                "translation_id": translation_id,
                "a2a_task_id": task_id,
                "a2a_state": state
            }
        }
        
        # Store the mapping for future reference
        self.context_map[translation_id] = {
            "a2a_task_id": task_id,
            "mcp_context": context
        }
        
        logger.info(f"Translated A2A to MCP: {translation_id}")
        return mcp_event
    
    def get_translation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the history of translations.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of translation history items
        """
        return list(self.translation_history.values())[-limit:]
    
    def clear_translation_history(self) -> None:
        """Clear the translation history."""
        self.translation_history = {}
        
    def get_context_by_id(self, translation_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the stored context for a translation ID.
        
        Args:
            translation_id: The translation ID to look up
            
        Returns:
            The stored context, or None if not found
        """
        return self.context_map.get(translation_id)


class ContextShimAgent:
    """
    Agent that preserves intent, history, and metadata as flows convert between protocols.
    Acts as a middleware to ensure context continuity across protocol boundaries.
    """
    
    def __init__(self, protocol_translator: ProtocolTranslator):
        """
        Initialize the context shim agent.
        
        Args:
            protocol_translator: The protocol translator to use
        """
        self.protocol_translator = protocol_translator
        self.context_store = {}
        
    def preserve_context(self, source_message: Dict[str, Any], protocol: str) -> str:
        """
        Preserve context from a message.
        
        Args:
            source_message: The message to preserve context from
            protocol: The protocol of the message ("mcp" or "a2a")
            
        Returns:
            Context ID for future reference
        """
        context_id = str(uuid.uuid4())
        
        if protocol.lower() == "mcp":
            context = source_message.get("context", {})
        else:  # a2a
            context = {
                "task_id": source_message.get("task_id"),
                "state": source_message.get("state"),
                "metadata": source_message.get("metadata", {})
            }
        
        # Add timestamp for context versioning
        context["_preserved_at"] = str(uuid.uuid1())
        
        self.context_store[context_id] = {
            "context": context,
            "original_protocol": protocol,
            "history": [source_message]
        }
        
        return context_id
    
    def apply_context(self, target_message: Dict[str, Any], context_id: str, target_protocol: str) -> Dict[str, Any]:
        """
        Apply preserved context to a message.
        
        Args:
            target_message: The message to apply context to
            context_id: The context ID to retrieve
            target_protocol: The protocol of the target message ("mcp" or "a2a")
            
        Returns:
            The message with applied context
        """
        if context_id not in self.context_store:
            logger.warning(f"Context ID not found: {context_id}")
            return target_message
        
        stored_data = self.context_store[context_id]
        context = stored_data["context"]
        
        # Update the message with the preserved context
        if target_protocol.lower() == "mcp":
            if "context" not in target_message:
                target_message["context"] = {}
                
            # Merge contexts, prioritizing original values
            for key, value in context.items():
                if key not in target_message["context"]:
                    target_message["context"][key] = value
                    
            # Add context continuity metadata
            if "metadata" not in target_message:
                target_message["metadata"] = {}
                
            target_message["metadata"]["context_preserved"] = True
            target_message["metadata"]["original_protocol"] = stored_data["original_protocol"]
            
        else:  # a2a
            if "metadata" not in target_message:
                target_message["metadata"] = {}
                
            # Add preserved context as metadata
            target_message["metadata"]["preserved_context"] = context
            target_message["metadata"]["context_preserved"] = True
            target_message["metadata"]["original_protocol"] = stored_data["original_protocol"]
        
        # Update history
        stored_data["history"].append(target_message)
        
        return target_message
    
    def get_context_history(self, context_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of messages for a context.
        
        Args:
            context_id: The context ID to retrieve history for
            
        Returns:
            List of messages in the context history
        """
        if context_id not in self.context_store:
            return []
            
        return self.context_store[context_id]["history"]


# Example usage
if __name__ == "__main__":
    # Create a protocol translator
    translator = ProtocolTranslator()
    
    # Create a context shim agent
    shim_agent = ContextShimAgent(translator)
    
    # Example MCP event
    mcp_event = {
        "event_type": "recommend",
        "source": "core-ai-llm-agent",
        "context": {
            "conversation_id": "conv-123",
            "industry_tags": ["manufacturing", "quality-control"],
            "priority": 8
        },
        "payload": {
            "text": "The machine is showing signs of failure. Recommend maintenance within 24 hours.",
            "data": {
                "confidence": 0.92,
                "failure_probability": 0.78,
                "recommended_action": "schedule_maintenance"
            }
        }
    }
    
    # Translate MCP to A2A
    a2a_message = translator.mcp_to_a2a(mcp_event)
    print("Translated A2A message:", json.dumps(a2a_message, indent=2))
    
    # Preserve context
    context_id = shim_agent.preserve_context(mcp_event, "mcp")
    
    # Translate back to MCP
    mcp_event_2 = translator.a2a_to_mcp(a2a_message)
    
    # Apply preserved context
    mcp_event_2 = shim_agent.apply_context(mcp_event_2, context_id, "mcp")
    print("Translated MCP event with preserved context:", json.dumps(mcp_event_2, indent=2))
