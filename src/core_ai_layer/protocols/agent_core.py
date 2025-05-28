"""
Agent Core for Industriverse Core AI Layer

This module implements the agent wrapper pattern for Core AI Layer components,
providing protocol-native interfaces and standardized lifecycle management.
"""

import json
import logging
import os
import uuid
import asyncio
from typing import Dict, Any, Optional, List, Union, Callable, Awaitable
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCore:
    """
    Base class for all Core AI Layer agents, implementing the agent wrapper pattern.
    Provides protocol-native interfaces, lifecycle management, and resilience features.
    """
    
    def __init__(self, 
                 agent_id: str, 
                 component_name: str,
                 manifest_path: Optional[str] = None,
                 config_path: Optional[str] = None):
        """
        Initialize the agent core.
        
        Args:
            agent_id: Unique identifier for this agent
            component_name: Name of the component this agent wraps
            manifest_path: Path to the agent manifest file (optional)
            config_path: Path to the agent configuration file (optional)
        """
        self.agent_id = agent_id
        self.component_name = component_name
        self.manifest_path = manifest_path or f"manifests/{agent_id}.yaml"
        self.config_path = config_path or f"config/{agent_id}.yaml"
        
        # Load manifest and config
        self.manifest = self._load_manifest()
        self.config = self._load_config()
        
        # Initialize state
        self.state = {
            "status": "initializing",
            "health": "unknown",
            "last_heartbeat": None,
            "metrics": {},
            "resilience_state": "standby"
        }
        
        # Event handlers
        self.event_handlers = {}
        
        # Protocol adapters
        self.mcp_adapter = None
        self.a2a_adapter = None
        
        # Resilience settings
        self.resilience_mode = self.manifest.get("resilience_mode", "standalone")
        self.mesh_coordination_role = self.manifest.get("mesh_coordination_role", "follower")
        
        # Observability
        self.metrics_registry = {}
        self.observability_hooks = self.manifest.get("observability_hooks", [])
        
        # Edge behavior
        self.edge_behavior_profile = self.manifest.get("edge_behavior_profile", {})
        
        logger.info(f"Agent Core initialized for {agent_id} ({component_name})")
    
    def _load_manifest(self) -> Dict[str, Any]:
        """
        Load the agent manifest.
        
        Returns:
            The agent manifest as a dictionary
        """
        try:
            manifest_path = Path(self.manifest_path)
            if not manifest_path.exists():
                logger.warning(f"Manifest file not found: {manifest_path}")
                return {}
                
            with open(manifest_path, 'r') as f:
                import yaml
                manifest = yaml.safe_load(f)
                logger.info(f"Loaded manifest for {self.agent_id}")
                return manifest
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return {}
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the agent configuration.
        
        Returns:
            The agent configuration as a dictionary
        """
        try:
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r') as f:
                import yaml
                config = yaml.safe_load(f)
                logger.info(f"Loaded config for {self.agent_id}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def initialize(self) -> bool:
        """
        Initialize the agent.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            logger.info(f"Initializing agent {self.agent_id}")
            
            # Initialize protocol adapters
            await self._initialize_protocol_adapters()
            
            # Register with A2A registry
            await self._register_with_a2a_registry()
            
            # Set up well-known endpoint
            await self._setup_well_known_endpoint()
            
            # Initialize resilience
            await self._initialize_resilience()
            
            # Initialize observability
            await self._initialize_observability()
            
            # Execute mesh lifecycle hook: on_init
            await self._execute_lifecycle_hook("on_init")
            
            # Update state
            self.state["status"] = "initialized"
            self.state["health"] = "healthy"
            self.state["last_heartbeat"] = self._get_timestamp()
            
            logger.info(f"Agent {self.agent_id} initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing agent {self.agent_id}: {e}")
            self.state["status"] = "initialization_failed"
            self.state["health"] = "unhealthy"
            return False
    
    async def _initialize_protocol_adapters(self) -> None:
        """Initialize the protocol adapters."""
        # Import adapters here to avoid circular imports
        from .mcp_adapter import MCPAdapter
        from .a2a_adapter import A2AAdapter
        
        try:
            # Initialize MCP adapter
            self.mcp_adapter = MCPAdapter(self.agent_id, self.manifest)
            
            # Initialize A2A adapter
            self.a2a_adapter = A2AAdapter(self.agent_id, self.manifest)
            
            logger.info(f"Protocol adapters initialized for {self.agent_id}")
        except Exception as e:
            logger.error(f"Error initializing protocol adapters: {e}")
            raise
    
    async def _register_with_a2a_registry(self) -> None:
        """Register with the A2A registry."""
        if not self.a2a_adapter:
            logger.warning("A2A adapter not initialized, skipping registry registration")
            return
            
        try:
            await self.a2a_adapter.register_with_registry()
            logger.info(f"Registered {self.agent_id} with A2A registry")
        except Exception as e:
            logger.error(f"Error registering with A2A registry: {e}")
            # Non-fatal error, continue initialization
    
    async def _setup_well_known_endpoint(self) -> None:
        """Set up the well-known endpoint for agent discovery."""
        try:
            # Create .well-known directory if it doesn't exist
            os.makedirs(".well-known", exist_ok=True)
            
            # Create agent.json with agent manifest
            agent_card = self._create_agent_card()
            
            with open(".well-known/agent.json", 'w') as f:
                json.dump(agent_card, f, indent=2)
                
            logger.info(f"Well-known endpoint set up for {self.agent_id}")
        except Exception as e:
            logger.error(f"Error setting up well-known endpoint: {e}")
            raise
    
    def _create_agent_card(self) -> Dict[str, Any]:
        """
        Create an Agent Card for A2A discovery.
        
        Returns:
            The Agent Card as a dictionary
        """
        # Extract A2A-specific fields from manifest
        a2a_integration = self.manifest.get("a2a_integration", {})
        agent_card = a2a_integration.get("agent_card", {})
        
        # Add resilience profile
        resilience_profile = self.manifest.get("resilience_profile", {})
        
        # Create the Agent Card
        return {
            "agent_id": self.agent_id,
            "agent_name": agent_card.get("agent_name", self.component_name),
            "agent_description": agent_card.get("agent_description", f"Core AI {self.component_name} Agent"),
            "capabilities": self._extract_capabilities(),
            "industryTags": agent_card.get("industryTags", ["manufacturing", "energy", "aerospace"]),
            "priority": agent_card.get("priority", 5),
            "resilience_profile": resilience_profile,
            "intelligence_type": self.manifest.get("intelligence_type", "analytical"),
            "intelligence_role": self.manifest.get("intelligence_role", "predictor"),
            "mesh_coordination_role": self.mesh_coordination_role,
            "edge_behavior_profile": self.edge_behavior_profile
        }
    
    def _extract_capabilities(self) -> List[Dict[str, Any]]:
        """
        Extract capabilities from the manifest.
        
        Returns:
            List of capabilities
        """
        capabilities = self.manifest.get("capabilities", [])
        return [
            {
                "name": cap.get("name", "unknown"),
                "description": cap.get("description", ""),
                "input_schema": cap.get("input_schema", {}),
                "output_schema": cap.get("output_schema", {})
            }
            for cap in capabilities
        ]
    
    async def _initialize_resilience(self) -> None:
        """Initialize resilience features."""
        try:
            logger.info(f"Initializing resilience for {self.agent_id} with mode: {self.resilience_mode}")
            
            # Set up resilience based on mode
            if self.resilience_mode == "redundant_pair":
                await self._setup_redundant_pair()
            elif self.resilience_mode == "failover_chain":
                await self._setup_failover_chain()
            elif self.resilience_mode == "quorum_vote":
                await self._setup_quorum_vote()
            else:
                logger.info(f"Using standalone resilience mode for {self.agent_id}")
                
            # Update state
            self.state["resilience_state"] = "active"
            
        except Exception as e:
            logger.error(f"Error initializing resilience: {e}")
            self.state["resilience_state"] = "degraded"
            # Non-fatal error, continue initialization
    
    async def _setup_redundant_pair(self) -> None:
        """Set up redundant pair resilience mode."""
        # Implementation details for redundant pair mode
        logger.info(f"Setting up redundant pair mode for {self.agent_id}")
        
        # Find paired agent
        resilience_profile = self.manifest.get("resilience_profile", {})
        fallback_chain = resilience_profile.get("fallback_chain", [])
        
        if not fallback_chain:
            logger.warning("No fallback agents specified for redundant pair mode")
            return
            
        paired_agent_id = fallback_chain[0]
        logger.info(f"Paired with agent: {paired_agent_id}")
        
        # Register heartbeat exchange
        # This would typically involve setting up a periodic task to exchange heartbeats
        
    async def _setup_failover_chain(self) -> None:
        """Set up failover chain resilience mode."""
        # Implementation details for failover chain mode
        logger.info(f"Setting up failover chain mode for {self.agent_id}")
        
        # Get fallback chain
        resilience_profile = self.manifest.get("resilience_profile", {})
        fallback_chain = resilience_profile.get("fallback_chain", [])
        
        if not fallback_chain:
            logger.warning("No fallback agents specified for failover chain mode")
            return
            
        logger.info(f"Failover chain: {', '.join(fallback_chain)}")
        
        # Register with chain
        # This would typically involve registering with a chain coordinator
    
    async def _setup_quorum_vote(self) -> None:
        """Set up quorum vote resilience mode."""
        # Implementation details for quorum vote mode
        logger.info(f"Setting up quorum vote mode for {self.agent_id}")
        
        # Get quorum members
        resilience_profile = self.manifest.get("resilience_profile", {})
        fallback_chain = resilience_profile.get("fallback_chain", [])
        confidence_level = resilience_profile.get("confidence_level", 0.97)
        
        if not fallback_chain:
            logger.warning("No quorum members specified for quorum vote mode")
            return
            
        logger.info(f"Quorum members: {', '.join(fallback_chain)}")
        logger.info(f"Confidence level: {confidence_level}")
        
        # Register with quorum
        # This would typically involve registering with a quorum coordinator
    
    async def _initialize_observability(self) -> None:
        """Initialize observability features."""
        try:
            logger.info(f"Initializing observability for {self.agent_id}")
            
            # Register standard metrics
            self._register_metric("model_latency", "gauge", "Model inference latency in milliseconds")
            self._register_metric("token_usage", "counter", "Token usage count")
            self._register_metric("sla_violation_rate", "gauge", "Rate of SLA violations")
            
            # Set up metric export based on observability hooks
            for hook in self.observability_hooks:
                if "export_metrics" in hook:
                    # This would typically involve setting up a metrics exporter
                    logger.info(f"Setting up metrics export to {hook['export_metrics']}")
                    
            # Set up alert thresholds
            # This would typically involve loading threshold configurations
            
        except Exception as e:
            logger.error(f"Error initializing observability: {e}")
            # Non-fatal error, continue initialization
    
    def _register_metric(self, name: str, metric_type: str, description: str) -> None:
        """
        Register a metric.
        
        Args:
            name: Metric name
            metric_type: Metric type (gauge, counter, histogram)
            description: Metric description
        """
        self.metrics_registry[name] = {
            "type": metric_type,
            "description": description,
            "value": 0 if metric_type == "counter" else None
        }
        logger.info(f"Registered metric: {name} ({metric_type})")
    
    def update_metric(self, name: str, value: Union[int, float]) -> None:
        """
        Update a metric value.
        
        Args:
            name: Metric name
            value: New metric value
        """
        if name not in self.metrics_registry:
            logger.warning(f"Metric not registered: {name}")
            return
            
        metric = self.metrics_registry[name]
        
        if metric["type"] == "counter":
            # Counters are cumulative
            if metric["value"] is None:
                metric["value"] = value
            else:
                metric["value"] += value
        else:
            # Gauges and histograms are set directly
            metric["value"] = value
            
        # Update state
        self.state["metrics"][name] = metric["value"]
        
        logger.debug(f"Updated metric {name}: {metric['value']}")
    
    async def _execute_lifecycle_hook(self, hook_name: str) -> None:
        """
        Execute a mesh lifecycle hook.
        
        Args:
            hook_name: Name of the hook to execute
        """
        mesh_lifecycle_hooks = self.manifest.get("mesh_lifecycle_hooks", [])
        
        for hook in mesh_lifecycle_hooks:
            if hook_name in hook:
                event = hook[hook_name]
                logger.info(f"Executing lifecycle hook {hook_name}: {event}")
                
                # Emit MCP event
                if self.mcp_adapter:
                    await self.mcp_adapter.emit_event(event, {})
    
    def register_event_handler(self, event_type: str, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """
        Register an event handler.
        
        Args:
            event_type: Type of event to handle
            handler: Async function to handle the event
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
            
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event type: {event_type}")
    
    async def handle_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Handle an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if event_type not in self.event_handlers:
            logger.warning(f"No handlers registered for event type: {event_type}")
            return
            
        handlers = self.event_handlers[event_type]
        
        for handler in handlers:
            try:
                await handler(event_data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    async def emit_mcp_event(self, event_type: str, payload: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> None:
        """
        Emit an MCP event.
        
        Args:
            event_type: Type of event
            payload: Event payload
            context: Event context (optional)
        """
        if not self.mcp_adapter:
            logger.warning("MCP adapter not initialized, cannot emit event")
            return
            
        context = context or {}
        
        try:
            await self.mcp_adapter.emit_event(event_type, payload, context)
            logger.info(f"Emitted MCP event: {event_type}")
        except Exception as e:
            logger.error(f"Error emitting MCP event: {e}")
    
    async def submit_a2a_task(self, task_data: Dict[str, Any]) -> str:
        """
        Submit an A2A task.
        
        Args:
            task_data: Task data
            
        Returns:
            Task ID
        """
        if not self.a2a_adapter:
            logger.warning("A2A adapter not initialized, cannot submit task")
            return str(uuid.uuid4())  # Return a dummy task ID
            
        try:
            task_id = await self.a2a_adapter.submit_task(task_data)
            logger.info(f"Submitted A2A task: {task_id}")
            return task_id
        except Exception as e:
            logger.error(f"Error submitting A2A task: {e}")
            return str(uuid.uuid4())  # Return a dummy task ID
    
    async def update_a2a_task(self, task_id: str, state: str, parts: Optional[List[Dict[str, Any]]] = None) -> None:
        """
        Update an A2A task.
        
        Args:
            task_id: Task ID
            state: New task state
            parts: New message parts (optional)
        """
        if not self.a2a_adapter:
            logger.warning("A2A adapter not initialized, cannot update task")
            return
            
        try:
            await self.a2a_adapter.update_task(task_id, state, parts)
            logger.info(f"Updated A2A task {task_id}: {state}")
        except Exception as e:
            logger.error(f"Error updating A2A task: {e}")
    
    async def heartbeat(self) -> None:
        """Send a heartbeat to indicate the agent is alive."""
        self.state["last_heartbeat"] = self._get_timestamp()
        self.state["health"] = "healthy"
        
        # Log heartbeat (debug level to avoid log spam)
        logger.debug(f"Heartbeat from {self.agent_id}")
        
        # In a real implementation, this would also:
        # 1. Update a shared state store
        # 2. Notify paired agents in redundant_pair mode
        # 3. Update metrics
    
    async def shutdown(self) -> None:
        """Shut down the agent."""
        logger.info(f"Shutting down agent {self.agent_id}")
        
        try:
            # Execute mesh lifecycle hook: on_shutdown (if exists)
            for hook in self.manifest.get("mesh_lifecycle_hooks", []):
                if "on_shutdown" in hook:
                    await self._execute_lifecycle_hook("on_shutdown")
            
            # Update state
            self.state["status"] = "shutdown"
            self.state["health"] = "offline"
            
            # Clean up resources
            # This would typically involve closing connections, etc.
            
            logger.info(f"Agent {self.agent_id} shut down successfully")
        except Exception as e:
            logger.error(f"Error shutting down agent {self.agent_id}: {e}")
    
    def _get_timestamp(self) -> str:
        """
        Get the current timestamp.
        
        Returns:
            Current timestamp as ISO format string
        """
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Example usage
if __name__ == "__main__":
    async def main():
        # Create an agent
        agent = AgentCore("core-ai-test-agent", "Test")
        
        # Initialize the agent
        success = await agent.initialize()
        
        if success:
            # Register an event handler
            async def handle_test_event(event_data):
                print(f"Handling test event: {event_data}")
            
            agent.register_event_handler("test_event", handle_test_event)
            
            # Emit an MCP event
            await agent.emit_mcp_event("test_event", {"message": "Hello, world!"})
            
            # Submit an A2A task
            task_id = await agent.submit_a2a_task({
                "action": "test",
                "data": {"message": "Hello, world!"}
            })
            
            # Update the task
            await agent.update_a2a_task(task_id, "completed", [
                {"type": "TextPart", "text": "Task completed successfully"}
            ])
            
            # Send a heartbeat
            await agent.heartbeat()
            
            # Update a metric
            agent.update_metric("model_latency", 42.5)
            
            # Shut down
            await agent.shutdown()
    
    asyncio.run(main())
