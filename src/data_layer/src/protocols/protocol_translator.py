"""
Protocol Translation Layer for Industriverse Data Layer

This module provides bidirectional translation between MCP and A2A protocols,
ensuring context preservation and consistent identity mapping when crossing
protocol boundaries.
"""

import json
import logging
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger(__name__)

class ProtocolTranslator:
    """
    Translates between MCP and A2A protocols while preserving context.
    
    This class implements the context-shim-agent pattern to ensure intent,
    history, and metadata are preserved when messages cross protocol boundaries.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the protocol translator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.identity_map = {}
        logger.info("Protocol translator initialized")
    
    def mcp_to_a2a(self, mcp_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate an MCP event to an A2A message.
        
        Args:
            mcp_event: The MCP event to translate
            
        Returns:
            The translated A2A message
        """
        logger.debug(f"Translating MCP event to A2A: {mcp_event.get('type', 'unknown')}")
        
        # Extract MCP event details
        event_type = mcp_event.get("type", "")
        context = mcp_event.get("context", {})
        payload = mcp_event.get("payload", {})
        source_id = mcp_event.get("source", "")
        
        # Map MCP identity to A2A identity
        agent_id = self._map_identity(source_id, "mcp_to_a2a")
        
        # Create A2A task based on MCP event type
        a2a_message = {
            "type": "task",
            "agent_id": agent_id,
            "task_id": mcp_event.get("id", ""),
            "status": "submitted",
            "parts": []
        }
        
        # Translate MCP event type to A2A capability
        if event_type == "observe":
            a2a_message["capability"] = "observe_data"
        elif event_type == "recommend":
            a2a_message["capability"] = "provide_recommendation"
        elif event_type == "simulate":
            a2a_message["capability"] = "run_simulation"
        elif event_type == "act":
            a2a_message["capability"] = "perform_action"
        
        # Preserve context as metadata
        context_part = {
            "type": "DataPart",
            "mime_type": "application/json",
            "data": {
                "mcp_context": context,
                "original_event_type": event_type,
                "protocol_source": "mcp"
            }
        }
        a2a_message["parts"].append(context_part)
        
        # Add payload as appropriate part type
        if isinstance(payload, str):
            payload_part = {
                "type": "TextPart",
                "text": payload
            }
        elif isinstance(payload, dict) or isinstance(payload, list):
            payload_part = {
                "type": "DataPart",
                "mime_type": "application/json",
                "data": payload
            }
        else:
            payload_part = {
                "type": "TextPart",
                "text": str(payload)
            }
        
        a2a_message["parts"].append(payload_part)
        
        # Add industry-specific extensions if present
        if "industryTags" in context:
            a2a_message["industryTags"] = context["industryTags"]
        
        if "priority" in context:
            a2a_message["priority"] = context["priority"]
        
        logger.debug(f"Translated to A2A message with capability: {a2a_message.get('capability')}")
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
        
        # Extract A2A message details
        message_type = a2a_message.get("type", "")
        agent_id = a2a_message.get("agent_id", "")
        capability = a2a_message.get("capability", "")
        parts = a2a_message.get("parts", [])
        
        # Map A2A identity to MCP identity
        source_id = self._map_identity(agent_id, "a2a_to_mcp")
        
        # Create base MCP event
        mcp_event = {
            "id": a2a_message.get("task_id", ""),
            "source": source_id,
            "context": {},
            "payload": {}
        }
        
        # Translate A2A capability to MCP event type
        if capability == "observe_data":
            mcp_event["type"] = "observe"
        elif capability == "provide_recommendation":
            mcp_event["type"] = "recommend"
        elif capability == "run_simulation":
            mcp_event["type"] = "simulate"
        elif capability == "perform_action":
            mcp_event["type"] = "act"
        else:
            # Default to observe for unknown capabilities
            mcp_event["type"] = "observe"
        
        # Extract context from parts
        for part in parts:
            if part.get("type") == "DataPart" and part.get("mime_type") == "application/json":
                data = part.get("data", {})
                if "mcp_context" in data:
                    mcp_event["context"] = data["mcp_context"]
                    break
        
        # Extract payload from parts
        payload = None
        for part in parts:
            if part.get("type") == "TextPart":
                payload = part.get("text", "")
                break
            elif part.get("type") == "DataPart" and part.get("mime_type") == "application/json":
                data = part.get("data", {})
                if "mcp_context" not in data:  # Skip the context part
                    payload = data
                    break
            elif part.get("type") == "FilePart":
                # For file parts, include a reference in the payload
                payload = {"file_reference": part.get("file_name", "")}
                break
        
        if payload is not None:
            mcp_event["payload"] = payload
        
        # Add industry-specific extensions if present
        if "industryTags" in a2a_message:
            mcp_event["context"]["industryTags"] = a2a_message["industryTags"]
        
        if "priority" in a2a_message:
            mcp_event["context"]["priority"] = a2a_message["priority"]
        
        logger.debug(f"Translated to MCP event of type: {mcp_event.get('type')}")
        return mcp_event
    
    def _map_identity(self, identity: str, direction: str) -> str:
        """
        Map identities between protocols to maintain consistency.
        
        Args:
            identity: The identity to map
            direction: The direction of mapping ('mcp_to_a2a' or 'a2a_to_mcp')
            
        Returns:
            The mapped identity
        """
        key = f"{identity}_{direction}"
        
        if key not in self.identity_map:
            if direction == "mcp_to_a2a":
                # Convert MCP identity to A2A format
                if identity.startswith("mcp:"):
                    a2a_id = f"a2a:{identity[4:]}"
                else:
                    a2a_id = f"a2a:{identity}"
                self.identity_map[key] = a2a_id
            else:
                # Convert A2A identity to MCP format
                if identity.startswith("a2a:"):
                    mcp_id = f"mcp:{identity[4:]}"
                else:
                    mcp_id = f"mcp:{identity}"
                self.identity_map[key] = mcp_id
        
        return self.identity_map[key]


class ContextShimAgent:
    """
    Specialized agent that preserves context when crossing protocol boundaries.
    
    This agent maintains the full context, intent, history, and metadata as
    messages are translated between MCP and A2A protocols.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the context shim agent.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.translator = ProtocolTranslator(config)
        self.context_store = {}
        logger.info("Context shim agent initialized")
    
    def process_cross_protocol_message(
        self, 
        message: Dict[str, Any], 
        source_protocol: str, 
        target_protocol: str
    ) -> Dict[str, Any]:
        """
        Process a message crossing protocol boundaries.
        
        Args:
            message: The message to process
            source_protocol: The source protocol ('mcp' or 'a2a')
            target_protocol: The target protocol ('mcp' or 'a2a')
            
        Returns:
            The processed message in the target protocol format
        """
        logger.debug(f"Processing cross-protocol message from {source_protocol} to {target_protocol}")
        
        # Generate a context ID for this message
        context_id = message.get("id", "") or message.get("task_id", "")
        if not context_id:
            context_id = f"ctx_{len(self.context_store) + 1}"
        
        # Store original message context
        if context_id not in self.context_store:
            self.context_store[context_id] = {
                "history": [],
                "metadata": {},
                "intent": None
            }
        
        # Update context store with this message
        self.context_store[context_id]["history"].append({
            "timestamp": "2025-05-21T03:43:54Z",  # Use actual timestamp in production
            "protocol": source_protocol,
            "message": message
        })
        
        # Extract and store intent if available
        if source_protocol == "mcp" and "intent" in message.get("context", {}):
            self.context_store[context_id]["intent"] = message["context"]["intent"]
        elif source_protocol == "a2a":
            for part in message.get("parts", []):
                if part.get("type") == "DataPart" and "intent" in part.get("data", {}):
                    self.context_store[context_id]["intent"] = part["data"]["intent"]
                    break
        
        # Translate the message
        if source_protocol == "mcp" and target_protocol == "a2a":
            translated = self.translator.mcp_to_a2a(message)
        elif source_protocol == "a2a" and target_protocol == "mcp":
            translated = self.translator.a2a_to_mcp(message)
        else:
            logger.error(f"Unsupported protocol translation: {source_protocol} to {target_protocol}")
            return message  # Return original if translation not supported
        
        # Enrich the translated message with full context
        if target_protocol == "mcp":
            if "context" not in translated:
                translated["context"] = {}
            translated["context"]["context_history"] = self.context_store[context_id]["history"]
            if self.context_store[context_id]["intent"]:
                translated["context"]["intent"] = self.context_store[context_id]["intent"]
        elif target_protocol == "a2a":
            context_part = None
            for part in translated.get("parts", []):
                if part.get("type") == "DataPart" and "mcp_context" in part.get("data", {}):
                    context_part = part
                    break
            
            if context_part:
                context_part["data"]["context_history"] = self.context_store[context_id]["history"]
                if self.context_store[context_id]["intent"]:
                    context_part["data"]["intent"] = self.context_store[context_id]["intent"]
        
        logger.debug(f"Processed cross-protocol message with context ID: {context_id}")
        return translated


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create translator
    translator = ProtocolTranslator()
    
    # Example MCP event
    mcp_event = {
        "id": "evt_12345",
        "type": "observe",
        "source": "mcp:data_layer",
        "context": {
            "industryTags": ["manufacturing", "energy"],
            "priority": "high",
            "intent": "monitor_equipment_status"
        },
        "payload": {
            "equipment_id": "pump_101",
            "status": "operational",
            "temperature": 42.5,
            "pressure": 101.3
        }
    }
    
    # Translate MCP to A2A
    a2a_message = translator.mcp_to_a2a(mcp_event)
    print("Translated A2A message:", json.dumps(a2a_message, indent=2))
    
    # Translate back to MCP
    mcp_event_roundtrip = translator.a2a_to_mcp(a2a_message)
    print("Round-trip MCP event:", json.dumps(mcp_event_roundtrip, indent=2))
