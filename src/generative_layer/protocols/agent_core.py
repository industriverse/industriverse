"""
Agent Core for Industriverse Generative Layer

This module implements the core agent functionality for the Generative Layer,
providing a wrapper pattern for all components to enable protocol-native
communication and mesh coordination.
"""

import json
import logging
import uuid
import os
import time
from typing import Dict, Any, Optional, List, Union, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCore:
    """
    Core agent functionality for Generative Layer components.
    Implements the agent wrapper pattern for protocol-native communication.
    """
    
    def __init__(self, 
                 agent_id: str, 
                 component_type: str,
                 manifest_path: Optional[str] = None):
        """
        Initialize the agent core.
        
        Args:
            agent_id: Unique identifier for this agent
            component_type: Type of component this agent wraps
            manifest_path: Path to the agent manifest file (optional)
        """
        self.agent_id = agent_id
        self.component_type = component_type
        self.manifest = self._load_manifest(manifest_path)
        self.callbacks = {}
        self.trust_mode = "passive"  # Default to passive mode
        self.context_history = []
        self.max_history_depth = self.manifest.get("context_window", {}).get("max_history_depth", 10)
        self.mesh_coordination_role = self.manifest.get("mesh_coordination_role", "follower")
        self.resilience_mode = self.manifest.get("resilience_mode", "failover_chain")
        
        # Initialize protocol adapters
        self.mcp_adapter = self._init_mcp_adapter()
        self.a2a_adapter = self._init_a2a_adapter()
        
        # Initialize mesh coordination
        self._init_mesh_coordination()
        
        logger.info(f"Agent Core initialized for {agent_id} ({component_type})")
    
    def _load_manifest(self, manifest_path: Optional[str]) -> Dict[str, Any]:
        """
        Load the agent manifest from file or create a default one.
        
        Args:
            manifest_path: Path to the manifest file
            
        Returns:
            The loaded or default manifest
        """
        if manifest_path and os.path.exists(manifest_path):
            try:
                with open(manifest_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading manifest: {e}")
        
        # Create a default manifest based on component type
        default_manifest = {
            "agent_id": self.agent_id,
            "layer_designation": "generative_layer",
            "generation_type": self._get_default_generation_type(),
            "generation_role": self._get_default_generation_role(),
            "resilience_mode": "failover_chain",
            "mesh_coordination_role": "follower",
            "context_window": {
                "max_history_depth": 10,
                "generation_context_tokens": 2048
            }
        }
        
        logger.info(f"Using default manifest for {self.agent_id}")
        return default_manifest
    
    def _get_default_generation_type(self) -> str:
        """
        Get the default generation type based on component type.
        
        Returns:
            The default generation type
        """
        type_mapping = {
            "template": "template",
            "ui": "ui",
            "doc": "documentation",
            "code": "code",
            "variability": "configuration"
        }
        
        for key, value in type_mapping.items():
            if key in self.component_type.lower():
                return value
        
        return "code"  # Default to code generation
    
    def _get_default_generation_role(self) -> str:
        """
        Get the default generation role based on component type.
        
        Returns:
            The default generation role
        """
        role_mapping = {
            "template": "template_renderer",
            "ui": "component_assembler",
            "variability": "variability_resolver"
        }
        
        for key, value in role_mapping.items():
            if key in self.component_type.lower():
                return value
        
        return "template_renderer"  # Default to template renderer
    
    def _init_mcp_adapter(self) -> Dict[str, Any]:
        """
        Initialize the MCP protocol adapter.
        
        Returns:
            The initialized MCP adapter
        """
        # This would be a real adapter in production
        # Here we're simulating the adapter interface
        return {
            "register": lambda: logger.info(f"Registered {self.agent_id} with MCP"),
            "send_event": lambda event: logger.info(f"Sent MCP event: {event.get('type', 'unknown')}"),
            "receive_event": lambda event_type: None,
            "supported_events": self.manifest.get("supported_mcp_events", [])
        }
    
    def _init_a2a_adapter(self) -> Dict[str, Any]:
        """
        Initialize the A2A protocol adapter.
        
        Returns:
            The initialized A2A adapter
        """
        # This would be a real adapter in production
        # Here we're simulating the adapter interface
        return {
            "register": lambda: logger.info(f"Registered {self.agent_id} with A2A"),
            "send_message": lambda message: logger.info(f"Sent A2A message: {message.get('type', 'unknown')}"),
            "receive_message": lambda message_type: None,
            "agent_card": self._create_agent_card()
        }
    
    def _create_agent_card(self) -> Dict[str, Any]:
        """
        Create an A2A Agent Card for this agent.
        
        Returns:
            The Agent Card
        """
        capabilities = []
        for cap in self.manifest.get("capabilities", []):
            capabilities.append({
                "name": cap.get("name", ""),
                "description": cap.get("description", "")
            })
        
        return {
            "agent_id": self.agent_id,
            "name": f"Industriverse {self.component_type} Agent",
            "description": f"Generative Layer agent for {self.component_type}",
            "capabilities": capabilities,
            "industryTags": ["manufacturing", "energy", "aerospace"],
            "priority": 5,  # Default priority
            "generation_profile": {
                "supported_templates": ["industrial_ui", "documentation", "code"],
                "variability_models": ["feature_model", "configuration_based"],
                "industry_adaptations": ["manufacturing", "energy", "aerospace"],
                "capsule_compatibility": {
                    "supported_interfaces": ["AG-UI", "Dynamic Capsule Panel"],
                    "live_preview": True
                }
            }
        }
    
    def _init_mesh_coordination(self) -> None:
        """Initialize mesh coordination based on role."""
        logger.info(f"Initializing mesh coordination as {self.mesh_coordination_role}")
        
        # Execute role-specific initialization
        if self.mesh_coordination_role == "leader":
            logger.info(f"Agent {self.agent_id} initializing as mesh leader")
            # In production, this would set up leader-specific coordination
        elif self.mesh_coordination_role == "follower":
            logger.info(f"Agent {self.agent_id} initializing as mesh follower")
            # In production, this would set up follower-specific coordination
        elif self.mesh_coordination_role == "observer":
            logger.info(f"Agent {self.agent_id} initializing as mesh observer")
            # In production, this would set up observer-specific coordination
    
    def register_with_protocols(self) -> None:
        """Register this agent with both MCP and A2A protocols."""
        self.mcp_adapter["register"]()
        self.a2a_adapter["register"]()
        logger.info(f"Agent {self.agent_id} registered with protocols")
    
    def set_trust_mode(self, mode: str) -> None:
        """
        Set the trust mode for this agent.
        
        Args:
            mode: The trust mode ("passive", "approval", or "autonomous")
        """
        if mode in ["passive", "approval", "autonomous"]:
            self.trust_mode = mode
            logger.info(f"Trust mode set to {mode} for agent {self.agent_id}")
        else:
            logger.warning(f"Invalid trust mode: {mode}")
    
    def register_callback(self, event_type: str, callback: Callable) -> None:
        """
        Register a callback for a specific event type.
        
        Args:
            event_type: The event type to register for
            callback: The callback function
        """
        self.callbacks[event_type] = callback
        logger.debug(f"Registered callback for {event_type}")
    
    def handle_mcp_event(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle an incoming MCP event.
        
        Args:
            event: The MCP event to handle
            
        Returns:
            The response event, if any
        """
        event_type = event.get("type", "")
        logger.info(f"Handling MCP event: {event_type}")
        
        # Add to context history
        self._add_to_context_history(event)
        
        # Check if we have a callback for this event type
        if event_type in self.callbacks:
            # Check trust mode
            if self._check_trust_mode(event):
                try:
                    response = self.callbacks[event_type](event)
                    logger.debug(f"Callback executed for {event_type}")
                    return response
                except Exception as e:
                    logger.error(f"Error in callback for {event_type}: {e}")
        else:
            logger.warning(f"No callback registered for {event_type}")
        
        return None
    
    def handle_a2a_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Handle an incoming A2A message.
        
        Args:
            message: The A2A message to handle
            
        Returns:
            The response message, if any
        """
        message_type = message.get("type", "")
        logger.info(f"Handling A2A message: {message_type}")
        
        # Convert A2A message to MCP event for internal processing
        from protocol_translator import ProtocolTranslator
        translator = ProtocolTranslator()
        mcp_event = translator.a2a_to_mcp(message)
        
        # Handle the converted event
        response_event = self.handle_mcp_event(mcp_event)
        
        # Convert response back to A2A if needed
        if response_event:
            return translator.mcp_to_a2a(response_event)
        
        return None
    
    def send_mcp_event(self, event_type: str, payload: Dict[str, Any], 
                      context: Optional[Dict[str, Any]] = None) -> str:
        """
        Send an MCP event.
        
        Args:
            event_type: The type of event to send
            payload: The event payload
            context: Additional context (optional)
            
        Returns:
            The event ID
        """
        event_id = str(uuid.uuid4())
        
        event = {
            "id": event_id,
            "type": event_type,
            "payload": payload,
            "context": context or {},
            "timestamp": time.time()
        }
        
        self.mcp_adapter["send_event"](event)
        logger.info(f"Sent MCP event: {event_type}")
        
        return event_id
    
    def send_a2a_message(self, message_type: str, parts: List[Dict[str, Any]], 
                        metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Send an A2A message.
        
        Args:
            message_type: The type of message to send
            parts: The message parts
            metadata: Additional metadata (optional)
            
        Returns:
            The message ID
        """
        task_id = str(uuid.uuid4())
        
        message = {
            "task_id": task_id,
            "type": message_type,
            "parts": parts,
            "metadata": metadata or {}
        }
        
        self.a2a_adapter["send_message"](message)
        logger.info(f"Sent A2A message: {message_type}")
        
        return task_id
    
    def _add_to_context_history(self, event: Dict[str, Any]) -> None:
        """
        Add an event to the context history.
        
        Args:
            event: The event to add
        """
        self.context_history.append(event)
        
        # Trim history if it exceeds max depth
        if len(self.context_history) > self.max_history_depth:
            self.context_history = self.context_history[-self.max_history_depth:]
    
    def _check_trust_mode(self, event: Dict[str, Any]) -> bool:
        """
        Check if the event can be processed based on trust mode.
        
        Args:
            event: The event to check
            
        Returns:
            True if the event can be processed, False otherwise
        """
        event_type = event.get("type", "")
        
        # Passive mode only allows observe events
        if self.trust_mode == "passive" and not event_type.startswith("observe/"):
            logger.warning(f"Rejected {event_type} in passive mode")
            return False
        
        # Approval mode requires explicit approval for act events
        if self.trust_mode == "approval" and event_type.startswith("act/"):
            # In a real system, this would check for approval
            # Here we're simulating approval
            logger.info(f"Approval required for {event_type}")
            return True  # Assume approved for this example
        
        # Autonomous mode allows all events
        return True
    
    def get_agent_manifest(self) -> Dict[str, Any]:
        """
        Get the agent manifest.
        
        Returns:
            The agent manifest
        """
        return self.manifest
    
    def get_well_known_endpoint(self) -> Dict[str, Any]:
        """
        Get the .well-known/agent.json endpoint data.
        
        Returns:
            The well-known endpoint data
        """
        return {
            "agent": self.a2a_adapter["agent_card"],
            "protocols": {
                "mcp": {
                    "supported_events": self.mcp_adapter["supported_events"]
                },
                "a2a": {
                    "task_types": ["query", "preview", "recommend", "generate", "collaborate"]
                }
            },
            "generation_status": {
                "active": True,
                "health": "healthy",
                "last_updated": time.time()
            }
        }
    
    def execute_mesh_lifecycle_hook(self, hook_name: str, payload: Dict[str, Any]) -> None:
        """
        Execute a mesh lifecycle hook.
        
        Args:
            hook_name: The name of the hook to execute
            payload: The hook payload
        """
        hooks = self.manifest.get("mesh_lifecycle_hooks", [])
        
        for hook in hooks:
            if hook_name in hook:
                hook_path = hook[hook_name]
                logger.info(f"Executing mesh lifecycle hook: {hook_path}")
                
                # In a real system, this would execute the hook
                # Here we're just logging it
                logger.info(f"Hook payload: {payload}")
                
                # Emit MCP event for hook execution
                self.send_mcp_event(
                    f"generative_layer/lifecycle/{hook_name}",
                    {
                        "hook": hook_path,
                        "status": "executed",
                        "payload": payload
                    }
                )
                
                return
        
        logger.warning(f"No mesh lifecycle hook found for {hook_name}")
    
    def handle_inheritance(self, parent_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle inheritance from parent agent.
        
        Args:
            parent_event: The event from the parent agent
            
        Returns:
            The processed event
        """
        agent_lineage = self.manifest.get("agent_lineage", {})
        parent_agent = agent_lineage.get("parent_agent", "")
        inheritance_behavior = agent_lineage.get("inheritance_behavior", "override")
        
        if not parent_agent:
            logger.warning("No parent agent specified for inheritance")
            return parent_event
        
        logger.info(f"Handling inheritance from {parent_agent} with behavior {inheritance_behavior}")
        
        # In a real system, this would implement the inheritance logic
        # Here we're just simulating it
        
        if inheritance_behavior == "override":
            # Override parent event with our own processing
            logger.info("Overriding parent event")
            return {
                **parent_event,
                "processed_by": self.agent_id,
                "inheritance": "override"
            }
        elif inheritance_behavior == "extend":
            # Extend parent event with additional processing
            logger.info("Extending parent event")
            return {
                **parent_event,
                "processed_by": f"{parent_agent},{self.agent_id}",
                "inheritance": "extend"
            }
        elif inheritance_behavior == "delegate":
            # Delegate processing back to parent
            logger.info("Delegating to parent event")
            return {
                **parent_event,
                "delegated_by": self.agent_id,
                "inheritance": "delegate"
            }
        
        return parent_event
