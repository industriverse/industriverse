"""
Well-Known Endpoint for Industriverse Generative Layer

This module implements the well-known endpoint exposure for the Generative Layer,
providing discovery mechanisms for A2A protocol and exposing agent capabilities.
"""

import json
import logging
import os
import time
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WellKnownEndpoint:
    """
    Implements the .well-known/agent.json endpoint for the Generative Layer.
    Provides discovery mechanisms for A2A protocol.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the well-known endpoint.
        
        Args:
            agent_core: The agent core instance
        """
        self.agent_core = agent_core
        self.last_updated = time.time()
        logger.info(f"Well-Known Endpoint initialized for {agent_core.agent_id}")
    
    def get_agent_json(self) -> Dict[str, Any]:
        """
        Get the .well-known/agent.json content.
        
        Returns:
            The agent.json content
        """
        manifest = self.agent_core.get_agent_manifest()
        
        # Create the Agent Card according to A2A specification
        agent_card = {
            "agent_id": self.agent_core.agent_id,
            "name": f"Industriverse {self.agent_core.component_type} Agent",
            "description": f"Generative Layer agent for {self.agent_core.component_type}",
            "version": manifest.get("version", "1.0.0"),
            "capabilities": self._get_capabilities(),
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
        
        # Add resilience status indicators
        resilience_status = {
            "mode": manifest.get("resilience_mode", "failover_chain"),
            "confidence_level": 0.95,
            "status": "healthy",
            "last_checked": time.time()
        }
        
        # Add generation status indicators
        generation_status = {
            "active": True,
            "health": "healthy",
            "last_updated": self.last_updated,
            "supported_generation_types": [manifest.get("generation_type", "code")]
        }
        
        # Construct the complete agent.json response
        agent_json = {
            "agent": agent_card,
            "protocols": {
                "mcp": {
                    "supported_events": manifest.get("supported_mcp_events", []),
                    "trust_modes": manifest.get("supported_trust_modes", ["passive", "approval", "autonomous"])
                },
                "a2a": {
                    "task_types": ["query", "preview", "recommend", "generate", "collaborate"],
                    "communication_methods": ["json-rpc", "sse", "webhooks"]
                }
            },
            "resilience_profile": resilience_status,
            "generation_status": generation_status,
            "mesh_coordination": {
                "role": manifest.get("mesh_coordination_role", "follower"),
                "lifecycle_hooks": manifest.get("mesh_lifecycle_hooks", [])
            }
        }
        
        logger.debug(f"Generated agent.json for {self.agent_core.agent_id}")
        return agent_json
    
    def _get_capabilities(self) -> List[Dict[str, Any]]:
        """
        Get the capabilities list for the Agent Card.
        
        Returns:
            The capabilities list
        """
        manifest = self.agent_core.get_agent_manifest()
        capabilities = []
        
        for cap in manifest.get("capabilities", []):
            capability = {
                "name": cap.get("name", ""),
                "description": cap.get("description", ""),
                "inputs": self._get_schema_ref(cap.get("input_schema", "")),
                "outputs": self._get_schema_ref(cap.get("output_schema", ""))
            }
            capabilities.append(capability)
        
        return capabilities
    
    def _get_schema_ref(self, schema_name: str) -> Dict[str, Any]:
        """
        Get a schema reference for a capability.
        
        Args:
            schema_name: The name of the schema file
            
        Returns:
            The schema reference
        """
        if not schema_name:
            return {"type": "object"}
        
        # In a real system, this would reference actual schema files
        # Here we're just creating a reference
        return {
            "$ref": f"/schemas/{schema_name}"
        }
    
    def update_status(self, status: str = "healthy") -> None:
        """
        Update the agent status.
        
        Args:
            status: The new status
        """
        self.last_updated = time.time()
        logger.info(f"Updated status to {status} for {self.agent_core.agent_id}")
    
    def serve_agent_json(self) -> str:
        """
        Serve the agent.json content as a JSON string.
        
        Returns:
            The agent.json content as a JSON string
        """
        agent_json = self.get_agent_json()
        return json.dumps(agent_json, indent=2)
    
    def handle_discovery_request(self, request_headers: Dict[str, str]) -> Dict[str, Any]:
        """
        Handle an agent discovery request.
        
        Args:
            request_headers: The request headers
            
        Returns:
            The discovery response
        """
        logger.info(f"Handling discovery request for {self.agent_core.agent_id}")
        
        # Check for specific protocol headers
        protocol = "unknown"
        if "X-A2A-Discovery" in request_headers:
            protocol = "a2a"
        elif "X-MCP-Discovery" in request_headers:
            protocol = "mcp"
        
        logger.debug(f"Discovery protocol: {protocol}")
        
        # Get the basic agent.json content
        response = self.get_agent_json()
        
        # Add protocol-specific information
        if protocol == "a2a":
            response["discovery_protocol"] = "a2a"
            response["a2a_version"] = "1.0"
        elif protocol == "mcp":
            response["discovery_protocol"] = "mcp"
            response["mcp_version"] = "1.0"
        
        return response
    
    def register_with_directory(self, directory_url: str) -> bool:
        """
        Register this agent with a directory service.
        
        Args:
            directory_url: The URL of the directory service
            
        Returns:
            True if registration was successful, False otherwise
        """
        logger.info(f"Registering {self.agent_core.agent_id} with directory at {directory_url}")
        
        # In a real system, this would make an HTTP request to the directory
        # Here we're just simulating it
        
        agent_json = self.get_agent_json()
        
        # Simulate a successful registration
        logger.info(f"Successfully registered {self.agent_core.agent_id} with directory")
        return True
