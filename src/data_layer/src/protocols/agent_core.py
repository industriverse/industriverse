"""
Agent Wrapper Pattern Implementation for Industriverse Data Layer

This module provides the base agent wrapper pattern implementation for all
Data Layer components, enabling protocol-native behavior through MCP and A2A.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List, Union, Callable

logger = logging.getLogger(__name__)

class AgentCore:
    """
    Base class implementing the agent wrapper pattern for Data Layer components.
    
    This class provides the foundation for making any Data Layer component
    protocol-native by wrapping it with MCP and A2A capabilities.
    """
    
    def __init__(
        self, 
        agent_id: str,
        component_name: str,
        manifest_path: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the agent core.
        
        Args:
            agent_id: Unique identifier for this agent
            component_name: Name of the wrapped component
            manifest_path: Path to the agent manifest file
            config: Optional configuration dictionary
        """
        self.agent_id = agent_id
        self.component_name = component_name
        self.manifest_path = manifest_path
        self.config = config or {}
        self.manifest = self._load_manifest()
        self.event_handlers = {
            "mcp": {
                "observe": {},
                "recommend": {},
                "simulate": {},
                "act": {}
            },
            "a2a": {}
        }
        self.trust_mode = self.config.get("trust_mode", "approval")
        self.trust_threshold = float(self.config.get("trust_threshold", 0.8))
        
        # Set up well-known endpoint directory
        self.well_known_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".well-known"
        )
        os.makedirs(self.well_known_dir, exist_ok=True)
        
        logger.info(f"Agent Core initialized for {component_name} with ID {agent_id}")
    
    def _load_manifest(self) -> Dict[str, Any]:
        """
        Load the agent manifest from file.
        
        Returns:
            The loaded manifest as a dictionary
        """
        if not self.manifest_path:
            logger.warning(f"No manifest path provided for {self.component_name}")
            return {}
        
        try:
            with open(self.manifest_path, 'r') as f:
                manifest = json.load(f)
                logger.info(f"Loaded manifest for {self.component_name}")
                return manifest
        except Exception as e:
            logger.error(f"Failed to load manifest: {str(e)}")
            return {}
    
    def expose_well_known_endpoint(self) -> None:
        """
        Expose the agent manifest at .well-known/agent.json for A2A discovery.
        """
        agent_card = self._generate_agent_card()
        well_known_path = os.path.join(self.well_known_dir, "agent.json")
        
        try:
            with open(well_known_path, 'w') as f:
                json.dump(agent_card, f, indent=2)
            logger.info(f"Exposed agent card at {well_known_path}")
        except Exception as e:
            logger.error(f"Failed to expose agent card: {str(e)}")
    
    def _generate_agent_card(self) -> Dict[str, Any]:
        """
        Generate an A2A Agent Card from the manifest.
        
        Returns:
            The Agent Card as a dictionary
        """
        # Extract relevant information from manifest
        capabilities = []
        for cap in self.manifest.get("capabilities", []):
            capabilities.append({
                "name": cap.get("name", ""),
                "description": cap.get("description", ""),
                "inputs": cap.get("inputs", []),
                "outputs": cap.get("outputs", [])
            })
        
        # Create the Agent Card
        agent_card = {
            "name": self.manifest.get("name", self.component_name),
            "description": self.manifest.get("description", f"Agent for {self.component_name}"),
            "version": self.manifest.get("version", "1.0.0"),
            "agent_id": self.agent_id,
            "capabilities": capabilities,
            "authentication": self.manifest.get("protocols", {}).get("a2a", {}).get("authentication", ["oauth2"]),
            "communication": ["json-rpc", "sse", "webhooks"]
        }
        
        # Add industry-specific extensions if present
        industry_extensions = self.manifest.get("industry_extensions", {})
        if "industryTags" in industry_extensions:
            agent_card["industryTags"] = industry_extensions["industryTags"]
        
        return agent_card
    
    def register_mcp_handler(
        self, 
        event_type: str, 
        event_name: str, 
        handler: Callable[[Dict[str, Any]], Dict[str, Any]],
        schema: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Register a handler for MCP events.
        
        Args:
            event_type: Type of MCP event (observe, recommend, simulate, act)
            event_name: Name of the specific event
            handler: Function to handle the event
            schema: Optional schema for event validation
        """
        if event_type not in self.event_handlers["mcp"]:
            logger.error(f"Invalid MCP event type: {event_type}")
            return
        
        self.event_handlers["mcp"][event_type][event_name] = {
            "handler": handler,
            "schema": schema
        }
        logger.info(f"Registered MCP handler for {event_type}/{event_name}")
    
    def register_a2a_handler(
        self, 
        capability: str, 
        handler: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> None:
        """
        Register a handler for A2A capabilities.
        
        Args:
            capability: Name of the A2A capability
            handler: Function to handle the capability
        """
        self.event_handlers["a2a"][capability] = handler
        logger.info(f"Registered A2A handler for capability: {capability}")
    
    def handle_mcp_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming MCP event.
        
        Args:
            event: The MCP event to handle
            
        Returns:
            The response to the event
        """
        event_type = event.get("type")
        if event_type not in self.event_handlers["mcp"]:
            logger.error(f"Unsupported MCP event type: {event_type}")
            return {"error": f"Unsupported event type: {event_type}"}
        
        # Check if this is a specific named event
        event_name = event.get("name", "default")
        if event_name not in self.event_handlers["mcp"][event_type]:
            # Try the default handler
            event_name = "default"
            if event_name not in self.event_handlers["mcp"][event_type]:
                logger.error(f"No handler for MCP event: {event_type}/{event_name}")
                return {"error": f"No handler for event: {event_type}/{event_name}"}
        
        # Check trust mode and threshold
        if self._check_trust(event):
            handler_info = self.event_handlers["mcp"][event_type][event_name]
            try:
                # Validate against schema if provided
                if handler_info["schema"]:
                    # Schema validation would go here
                    pass
                
                # Call the handler
                response = handler_info["handler"](event)
                logger.info(f"Handled MCP event: {event_type}/{event_name}")
                return response
            except Exception as e:
                logger.error(f"Error handling MCP event: {str(e)}")
                return {"error": f"Error handling event: {str(e)}"}
        else:
            logger.warning(f"Trust check failed for MCP event: {event_type}/{event_name}")
            return {"error": "Trust check failed", "trust_required": True}
    
    def handle_a2a_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle an incoming A2A task.
        
        Args:
            task: The A2A task to handle
            
        Returns:
            The response to the task
        """
        capability = task.get("capability")
        if capability not in self.event_handlers["a2a"]:
            logger.error(f"Unsupported A2A capability: {capability}")
            return {
                "task_id": task.get("task_id", ""),
                "status": "failed",
                "error": f"Unsupported capability: {capability}"
            }
        
        # Update task status to working
        response = {
            "task_id": task.get("task_id", ""),
            "status": "working"
        }
        
        try:
            # Call the handler
            handler = self.event_handlers["a2a"][capability]
            result = handler(task)
            
            # Update response with result
            response["status"] = "completed"
            response["parts"] = result.get("parts", [])
            logger.info(f"Handled A2A task for capability: {capability}")
        except Exception as e:
            logger.error(f"Error handling A2A task: {str(e)}")
            response["status"] = "failed"
            response["error"] = str(e)
        
        return response
    
    def _check_trust(self, event: Dict[str, Any]) -> bool:
        """
        Check if an event meets the trust requirements.
        
        Args:
            event: The event to check
            
        Returns:
            True if the event meets trust requirements, False otherwise
        """
        # In passive mode, always trust
        if self.trust_mode == "passive":
            return True
        
        # In autonomous mode, check trust score
        if self.trust_mode == "autonomous":
            trust_score = event.get("context", {}).get("trust_score", 0.0)
            return trust_score >= self.trust_threshold
        
        # In approval mode, check for approval flag
        if self.trust_mode == "approval":
            return event.get("context", {}).get("approved", False)
        
        # Default to false for unknown trust modes
        return False
    
    def emit_mcp_event(
        self, 
        event_type: str, 
        payload: Dict[str, Any], 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Emit an MCP event.
        
        Args:
            event_type: Type of MCP event (observe, recommend, simulate, act)
            payload: The event payload
            context: Optional event context
            
        Returns:
            The emitted event
        """
        if event_type not in ["observe", "recommend", "simulate", "act"]:
            logger.error(f"Invalid MCP event type: {event_type}")
            return {}
        
        event = {
            "id": f"evt_{self.agent_id}_{event_type}_{len(payload)}",
            "type": event_type,
            "source": self.agent_id,
            "payload": payload,
            "context": context or {}
        }
        
        logger.info(f"Emitted MCP event: {event_type}")
        return event
    
    def create_a2a_task(
        self, 
        capability: str, 
        inputs: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an A2A task.
        
        Args:
            capability: The capability to invoke
            inputs: The task inputs
            
        Returns:
            The created task
        """
        task = {
            "type": "task",
            "task_id": f"task_{self.agent_id}_{capability}_{len(inputs)}",
            "agent_id": self.agent_id,
            "capability": capability,
            "status": "submitted",
            "parts": []
        }
        
        # Add inputs as parts
        for key, value in inputs.items():
            if isinstance(value, str):
                part = {
                    "type": "TextPart",
                    "name": key,
                    "text": value
                }
            elif isinstance(value, dict) or isinstance(value, list):
                part = {
                    "type": "DataPart",
                    "name": key,
                    "mime_type": "application/json",
                    "data": value
                }
            else:
                part = {
                    "type": "TextPart",
                    "name": key,
                    "text": str(value)
                }
            task["parts"].append(part)
        
        logger.info(f"Created A2A task for capability: {capability}")
        return task
    
    def emit_boot_signal(self) -> Dict[str, Any]:
        """
        Emit the MCP boot signal when the agent starts.
        
        Returns:
            The boot signal event
        """
        boot_event = self.emit_mcp_event(
            "observe",
            {
                "status": "ready",
                "component": self.component_name,
                "timestamp": "2025-05-21T03:44:59Z"  # Use actual timestamp in production
            },
            {
                "event_type": "boot_signal",
                "layer": "data_layer"
            }
        )
        
        # Write mesh config to confirm runtime init state
        mesh_config = {
            "agent_id": self.agent_id,
            "component": self.component_name,
            "status": "initialized",
            "timestamp": "2025-05-21T03:44:59Z"  # Use actual timestamp in production
        }
        
        init_flags_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "init_flags"
        )
        os.makedirs(init_flags_dir, exist_ok=True)
        
        try:
            with open(os.path.join(init_flags_dir, "mesh_config.json"), 'w') as f:
                json.dump(mesh_config, f, indent=2)
            logger.info("Wrote mesh configuration to confirm initialization")
        except Exception as e:
            logger.error(f"Failed to write mesh configuration: {str(e)}")
        
        logger.info("Emitted boot signal")
        return boot_event


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create agent core
    agent = AgentCore(
        agent_id="data-layer-example-agent",
        component_name="example_component",
        config={"trust_mode": "passive"}
    )
    
    # Register handlers
    def handle_observe(event):
        return {"status": "success", "data": {"observed": True}}
    
    agent.register_mcp_handler("observe", "sensor_reading", handle_observe)
    
    # Emit boot signal
    boot_signal = agent.emit_boot_signal()
    print("Boot signal:", json.dumps(boot_signal, indent=2))
    
    # Expose well-known endpoint
    agent.expose_well_known_endpoint()
