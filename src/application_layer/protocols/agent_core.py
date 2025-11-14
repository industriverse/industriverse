"""
Agent Core for Application Layer.

This module provides the core agent functionality for the Application Layer,
implementing protocol-native interfaces for MCP and A2A integration.
"""

import logging
import json
import os
import time
import uuid
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCore:
    """
    Core agent functionality for the Application Layer.
    """
    
    def __init__(self, agent_id: str, manifest_path: str):
        """
        Initialize the Agent Core.
        
        Args:
            agent_id: Agent ID
            manifest_path: Path to agent manifest
        """
        self.agent_id = agent_id
        self.manifest_path = manifest_path
        self.manifest = self._load_manifest()
        self.components = {}
        self.user_journeys = {}
        self.monitoring_tasks = {}
        self.a2a_tasks = {}
        self.mcp_events = []
        self.trust_scores = {}
        self.context_history = []
        self.max_history_depth = self.manifest.get("context_window", {}).get("max_history_depth", 20)
        
        # Initialize protocol handlers
        self.mcp_handler = None
        self.a2a_handler = None
        self.protocol_translator = None
        self.well_known_endpoint = None
        
        logger.info(f"Agent Core initialized for agent: {agent_id}")
    
    def _load_manifest(self) -> Dict[str, Any]:
        """
        Load agent manifest.
        
        Returns:
            Agent manifest
        """
        try:
            with open(self.manifest_path, "r") as f:
                import yaml
                manifest = yaml.safe_load(f)
                return manifest.get("spec", {})
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return {}
    
    def initialize(self):
        """
        Initialize the Agent Core.
        """
        # Import protocol handlers
        from .mcp_handler import MCPHandler
        from .a2a_handler import A2AHandler
        from .protocol_translator import ProtocolTranslator
        from .well_known_endpoint import WellKnownEndpoint

        # Initialize protocol handlers
        self.mcp_handler = MCPHandler(self)
        self.a2a_handler = A2AHandler(self)
        self.protocol_translator = ProtocolTranslator(self)
        self.well_known_endpoint = WellKnownEndpoint(self)

        # Initialize mesh lifecycle
        self._initialize_mesh_lifecycle()

        logger.info(f"Agent Core fully initialized for agent: {self.agent_id}")

    def _initialize_mesh_lifecycle(self):
        """
        Initialize mesh lifecycle.
        """
        # Import mesh lifecycle handler
        from .mesh_boot_lifecycle import MeshBootLifecycle

        # Initialize mesh lifecycle
        mesh_lifecycle = MeshBootLifecycle(self)
        
        # Trigger on_init hook
        mesh_lifecycle.trigger_hook("on_init")
        
        logger.info(f"Mesh lifecycle initialized for agent: {self.agent_id}")
    
    def register_component(self, component_id: str, component: Any) -> bool:
        """
        Register a component with the Agent Core.
        
        Args:
            component_id: Component ID
            component: Component instance
            
        Returns:
            True if successful, False otherwise
        """
        if component_id in self.components:
            logger.warning(f"Component already registered: {component_id}")
            return False
        
        self.components[component_id] = component
        
        logger.info(f"Registered component: {component_id}")
        
        return True
    
    def get_component(self, component_id: str) -> Optional[Any]:
        """
        Get a component by ID.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component instance or None if not found
        """
        return self.components.get(component_id)
    
    def get_component_info(self, component_id: str) -> Dict[str, Any]:
        """
        Get component information.
        
        Args:
            component_id: Component ID
            
        Returns:
            Component information
        """
        component = self.get_component(component_id)
        
        if not component:
            return {}
        
        # Get component information
        if hasattr(component, "get_info"):
            return component.get_info()
        
        # Default component information
        return {
            "id": component_id,
            "type": component.__class__.__name__,
            "name": component.__class__.__name__,
            "status": "unknown"
        }
    
    def handle_component_action(self, component_id: str, action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle component action.
        
        Args:
            component_id: Component ID
            action_id: Action ID
            data: Action data
            
        Returns:
            Response data
        """
        component = self.get_component(component_id)
        
        if not component:
            return {"error": f"Component not found: {component_id}"}
        
        # Handle action
        if hasattr(component, "handle_action"):
            return component.handle_action(action_id, data)
        
        return {"error": f"Component does not support actions: {component_id}"}
    
    def handle_mcp_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle MCP event.
        
        Args:
            event_type: Event type
            event_data: Event data
            
        Returns:
            Response data
        """
        # Add event to history
        self._add_to_context_history({
            "type": "mcp_event",
            "event_type": event_type,
            "timestamp": time.time()
        })
        
        # Log event
        logger.info(f"Handling MCP event: {event_type}")
        
        # Check if MCP handler is initialized
        if not self.mcp_handler:
            self.initialize()
        
        # Handle event
        response = self.mcp_handler.handle_event(event_type, event_data)
        
        # Record event
        self.mcp_events.append({
            "event_type": event_type,
            "event_data": event_data,
            "response": response,
            "timestamp": time.time()
        })
        
        return response
    
    def handle_a2a_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A task.
        
        Args:
            task_type: Task type
            task_data: Task data
            
        Returns:
            Response data
        """
        # Add task to history
        self._add_to_context_history({
            "type": "a2a_task",
            "task_type": task_type,
            "timestamp": time.time()
        })
        
        # Log task
        logger.info(f"Handling A2A task: {task_type}")
        
        # Check if A2A handler is initialized
        if not self.a2a_handler:
            self.initialize()
        
        # Handle task
        response = self.a2a_handler.handle_task(task_type, task_data)
        
        return response
    
    def update_a2a_task_status(self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update A2A task status.
        
        Args:
            task_id: Task ID
            status: Task status
            result: Task result
            
        Returns:
            True if successful, False otherwise
        """
        # Check if A2A handler is initialized
        if not self.a2a_handler:
            self.initialize()
        
        # Update task status
        return self.a2a_handler.update_task_status(task_id, status, result)
    
    def store_user_journey(self, journey_id: str, journey_context: Dict[str, Any]) -> bool:
        """
        Store user journey.
        
        Args:
            journey_id: Journey ID
            journey_context: Journey context
            
        Returns:
            True if successful, False otherwise
        """
        self.user_journeys[journey_id] = journey_context
        
        logger.info(f"Stored user journey: {journey_id}")
        
        return True
    
    def get_user_journey(self, journey_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user journey.
        
        Args:
            journey_id: Journey ID
            
        Returns:
            Journey context or None if not found
        """
        return self.user_journeys.get(journey_id)
    
    def store_monitoring_task(self, monitoring_id: str, monitoring_config: Dict[str, Any]) -> bool:
        """
        Store monitoring task.
        
        Args:
            monitoring_id: Monitoring ID
            monitoring_config: Monitoring configuration
            
        Returns:
            True if successful, False otherwise
        """
        self.monitoring_tasks[monitoring_id] = monitoring_config
        
        logger.info(f"Stored monitoring task: {monitoring_id}")
        
        return True
    
    def get_monitoring_task(self, monitoring_id: str) -> Optional[Dict[str, Any]]:
        """
        Get monitoring task.
        
        Args:
            monitoring_id: Monitoring ID
            
        Returns:
            Monitoring configuration or None if not found
        """
        return self.monitoring_tasks.get(monitoring_id)
    
    def get_trust_score(self, agent_id: str) -> float:
        """
        Get trust score for an agent.
        
        Args:
            agent_id: Agent ID
            
        Returns:
            Trust score (0.0 to 1.0)
        """
        return self.trust_scores.get(agent_id, 0.5)
    
    def update_trust_score(self, agent_id: str, score: float) -> bool:
        """
        Update trust score for an agent.
        
        Args:
            agent_id: Agent ID
            score: Trust score (0.0 to 1.0)
            
        Returns:
            True if successful, False otherwise
        """
        # Validate score
        if score < 0.0 or score > 1.0:
            logger.warning(f"Invalid trust score: {score}")
            return False
        
        # Update score
        self.trust_scores[agent_id] = score
        
        logger.info(f"Updated trust score for agent {agent_id}: {score}")
        
        return True
    
    def _add_to_context_history(self, context_item: Dict[str, Any]):
        """
        Add item to context history.
        
        Args:
            context_item: Context item
        """
        self.context_history.append(context_item)
        
        # Trim history if needed
        if len(self.context_history) > self.max_history_depth:
            self.context_history = self.context_history[-self.max_history_depth:]
    
    def get_context_history(self) -> List[Dict[str, Any]]:
        """
        Get context history.
        
        Returns:
            Context history
        """
        return self.context_history
    
    def get_agent_manifest(self) -> Dict[str, Any]:
        """
        Get agent manifest.
        
        Returns:
            Agent manifest
        """
        return self.manifest
    
    def get_agent_card(self) -> Dict[str, Any]:
        """
        Get agent card for A2A discovery.
        
        Returns:
            Agent card
        """
        # Check if well-known endpoint is initialized
        if not self.well_known_endpoint:
            self.initialize()
        
        # Get agent card
        return self.well_known_endpoint.get_agent_card()
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get agent capabilities.
        
        Returns:
            Agent capabilities
        """
        return self.manifest.get("capabilities", [])
    
    def get_supported_mcp_events(self) -> List[str]:
        """
        Get supported MCP events.
        
        Returns:
            Supported MCP events
        """
        return self.manifest.get("supported_mcp_events", [])
    
    def get_supported_trust_modes(self) -> List[str]:
        """
        Get supported trust modes.
        
        Returns:
            Supported trust modes
        """
        return self.manifest.get("supported_trust_modes", [])
    
    def get_protocol_hooks(self) -> Dict[str, List[str]]:
        """
        Get protocol hooks.
        
        Returns:
            Protocol hooks
        """
        return self.manifest.get("protocol_hooks", {})
    
    def get_application_type(self) -> str:
        """
        Get application type.
        
        Returns:
            Application type
        """
        return self.manifest.get("application_type", "")
    
    def get_application_role(self) -> str:
        """
        Get application role.
        
        Returns:
            Application role
        """
        return self.manifest.get("application_role", "")
    
    def get_resilience_mode(self) -> str:
        """
        Get resilience mode.
        
        Returns:
            Resilience mode
        """
        return self.manifest.get("resilience_mode", "")
    
    def get_mesh_coordination_role(self) -> str:
        """
        Get mesh coordination role.
        
        Returns:
            Mesh coordination role
        """
        return self.manifest.get("mesh_coordination_role", "")
    
    def get_avatar_representation(self) -> Dict[str, Any]:
        """
        Get avatar representation.
        
        Returns:
            Avatar representation
        """
        return self.manifest.get("avatar_representation", {})
    
    def get_universal_skin_support(self) -> Dict[str, Any]:
        """
        Get universal skin support.
        
        Returns:
            Universal skin support
        """
        return self.manifest.get("universal_skin_support", {})
    
    def get_cross_layer_coordination(self) -> Dict[str, Any]:
        """
        Get cross-layer coordination.
        
        Returns:
            Cross-layer coordination
        """
        return self.manifest.get("cross_layer_coordination", {})
    
    def get_mesh_lifecycle_hooks(self) -> List[Dict[str, str]]:
        """
        Get mesh lifecycle hooks.
        
        Returns:
            Mesh lifecycle hooks
        """
        return self.manifest.get("mesh_lifecycle_hooks", [])
    
    def get_context_window(self) -> Dict[str, Any]:
        """
        Get context window.
        
        Returns:
            Context window
        """
        return self.manifest.get("context_window", {})
    
    def get_upgrade_mode(self) -> str:
        """
        Get upgrade mode.
        
        Returns:
            Upgrade mode
        """
        return self.manifest.get("upgrade_mode", "")
    
    def get_extensibility(self) -> Dict[str, Any]:
        """
        Get extensibility configuration.
        
        Returns:
            Extensibility configuration
        """
        return self.manifest.get("extensibility", {})
    
    def emit_mcp_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Emit MCP event.
        
        Args:
            event_type: Event type
            event_data: Event data
            
        Returns:
            Response data
        """
        # Check if MCP handler is initialized
        if not self.mcp_handler:
            self.initialize()
        
        # Emit event
        return self.mcp_handler.emit_event(event_type, event_data)
    
    def submit_a2a_task(self, agent_id: str, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit A2A task.
        
        Args:
            agent_id: Target agent ID
            task_type: Task type
            task_data: Task data
            
        Returns:
            Response data
        """
        # Check if A2A handler is initialized
        if not self.a2a_handler:
            self.initialize()
        
        # Submit task
        return self.a2a_handler.submit_task(agent_id, task_type, task_data)
    
    def translate_mcp_to_a2a(self, mcp_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate MCP event to A2A task.
        
        Args:
            mcp_event: MCP event
            
        Returns:
            A2A task
        """
        # Check if protocol translator is initialized
        if not self.protocol_translator:
            self.initialize()
        
        # Translate event
        return self.protocol_translator.mcp_to_a2a(mcp_event)
    
    def translate_a2a_to_mcp(self, a2a_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate A2A task to MCP event.
        
        Args:
            a2a_task: A2A task
            
        Returns:
            MCP event
        """
        # Check if protocol translator is initialized
        if not self.protocol_translator:
            self.initialize()
        
        # Translate task
        return self.protocol_translator.a2a_to_mcp(a2a_task)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get agent status.
        
        Returns:
            Agent status
        """
        return {
            "agent_id": self.agent_id,
            "application_type": self.get_application_type(),
            "application_role": self.get_application_role(),
            "status": "operational",
            "components": len(self.components),
            "mcp_events": len(self.mcp_events),
            "user_journeys": len(self.user_journeys),
            "monitoring_tasks": len(self.monitoring_tasks),
            "context_history": len(self.context_history)
        }
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get agent health.
        
        Returns:
            Agent health
        """
        return {
            "status": "healthy",
            "components": {
                "total": len(self.components),
                "healthy": sum(1 for component in self.components.values() if hasattr(component, "get_status") and component.get_status().get("status") == "operational")
            },
            "protocols": {
                "mcp": self.mcp_handler is not None,
                "a2a": self.a2a_handler is not None,
                "translator": self.protocol_translator is not None,
                "well_known": self.well_known_endpoint is not None
            }
        }
    
    def shutdown(self):
        """
        Shutdown the agent.
        """
        logger.info(f"Shutting down agent: {self.agent_id}")
        
        # Emit shutdown event
        self.emit_mcp_event("application_layer/shutdown", {
            "agent_id": self.agent_id,
            "timestamp": time.time()
        })
        
        # Shutdown components
        for component_id, component in self.components.items():
            if hasattr(component, "shutdown"):
                try:
                    component.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down component {component_id}: {e}")
        
        logger.info(f"Agent shutdown complete: {self.agent_id}")
