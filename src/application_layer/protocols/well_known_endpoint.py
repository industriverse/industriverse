"""
Well-Known Endpoint Handler for the Industriverse Application Layer.

This module provides well-known endpoint implementation for A2A discovery,
exposing agent manifests and capabilities through standardized endpoints.
"""

import logging
import json
import time
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WellKnownEndpoint:
    """
    Well-known endpoint handler for the Application Layer.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the Well-Known Endpoint handler.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        
        logger.info("Well-Known Endpoint handler initialized")
    
    def get_agent_card(self) -> Dict[str, Any]:
        """
        Get agent card for A2A discovery.
        
        Returns:
            Agent card
        """
        # Get agent manifest
        manifest = self.agent_core.get_agent_manifest()
        
        # Create agent card
        agent_card = {
            "agent_id": self.agent_core.agent_id,
            "name": f"Industriverse Application Layer - {manifest.get('application_type', 'Unknown')}",
            "description": "Application Layer component for the Industriverse Industrial Foundry Framework",
            "version": "1.0.0",
            "capabilities": manifest.get("capabilities", []),
            "api_endpoints": self._get_api_endpoints(),
            "auth_methods": ["oauth2", "api_key"],
            "status": "active",
            "industryTags": self._get_industry_tags(),
            "priority": self._get_priority(),
            "application_profile": {
                "supported_industries": ["manufacturing", "energy", "aerospace", "defense", "data_centers"],
                "ui_capabilities": ["web", "desktop", "mobile", "ar_hud"],
                "avatar_enabled": True,
                "universal_skin_support": True,
                "edge_deployable": True
            }
        }
        
        return agent_card
    
    def _get_api_endpoints(self) -> Dict[str, Any]:
        """
        Get API endpoints.
        
        Returns:
            API endpoints
        """
        return {
            "invoke": "/api/v1/invoke",
            "status": "/api/v1/status",
            "capsule_info": "/api/v1/capsule_info",
            "context/update": "/api/v1/context/update",
            "logs": "/api/v1/logs",
            "explain": "/api/v1/explain"
        }
    
    def _get_industry_tags(self) -> List[str]:
        """
        Get industry tags.
        
        Returns:
            Industry tags
        """
        # Get application type
        application_type = self.agent_core.get_application_type()
        
        # Define industry tags based on application type
        if application_type == "manufacturing":
            return ["manufacturing/production", "manufacturing/quality", "manufacturing/maintenance"]
        elif application_type == "energy":
            return ["energy/generation", "energy/distribution", "energy/monitoring"]
        elif application_type == "aerospace":
            return ["aerospace/operations", "aerospace/maintenance", "aerospace/safety"]
        elif application_type == "defense":
            return ["defense/operations", "defense/logistics", "defense/security"]
        elif application_type == "data_center":
            return ["data_center/operations", "data_center/cooling", "data_center/power"]
        else:
            return ["industrial/general"]
    
    def _get_priority(self) -> int:
        """
        Get priority.
        
        Returns:
            Priority
        """
        # Get application role
        application_role = self.agent_core.get_application_role()
        
        # Define priority based on application role
        if application_role == "coordinator":
            return 10
        elif application_role == "orchestrator":
            return 8
        elif application_role == "avatar_interface":
            return 7
        elif application_role == "ui_provider":
            return 5
        else:
            return 3
    
    def handle_discovery_request(self) -> Dict[str, Any]:
        """
        Handle discovery request.
        
        Returns:
            Discovery response
        """
        # Get agent card
        agent_card = self.get_agent_card()
        
        # Add discovery metadata
        discovery_response = {
            "agent_card": agent_card,
            "discovery_timestamp": time.time(),
            "discovery_version": "1.0.0"
        }
        
        return discovery_response
    
    def handle_capabilities_request(self) -> Dict[str, Any]:
        """
        Handle capabilities request.
        
        Returns:
            Capabilities response
        """
        # Get capabilities
        capabilities = self.agent_core.get_capabilities()
        
        # Add capabilities metadata
        capabilities_response = {
            "agent_id": self.agent_core.agent_id,
            "capabilities": capabilities,
            "capabilities_timestamp": time.time(),
            "capabilities_version": "1.0.0"
        }
        
        return capabilities_response
    
    def handle_status_request(self) -> Dict[str, Any]:
        """
        Handle status request.
        
        Returns:
            Status response
        """
        # Get status
        status = self.agent_core.get_status()
        
        # Add status metadata
        status_response = {
            "agent_id": self.agent_core.agent_id,
            "status": status,
            "status_timestamp": time.time(),
            "status_version": "1.0.0"
        }
        
        return status_response
    
    def handle_health_request(self) -> Dict[str, Any]:
        """
        Handle health request.
        
        Returns:
            Health response
        """
        # Get health
        health = self.agent_core.get_health()
        
        # Add health metadata
        health_response = {
            "agent_id": self.agent_core.agent_id,
            "health": health,
            "health_timestamp": time.time(),
            "health_version": "1.0.0"
        }
        
        return health_response
    
    def handle_explain_request(self, explain_target: str) -> Dict[str, Any]:
        """
        Handle explain request.
        
        Args:
            explain_target: Explain target
            
        Returns:
            Explain response
        """
        # Get agent manifest
        manifest = self.agent_core.get_agent_manifest()
        
        # Handle different explain targets
        if explain_target == "agent":
            return {
                "agent_id": self.agent_core.agent_id,
                "name": f"Industriverse Application Layer - {manifest.get('application_type', 'Unknown')}",
                "description": "Application Layer component for the Industriverse Industrial Foundry Framework",
                "purpose": "Provides application-level functionality for industrial applications",
                "capabilities_summary": "Orchestrates user journeys, manages UI components, and coordinates cross-layer interactions",
                "explain_timestamp": time.time()
            }
        elif explain_target == "capabilities":
            capabilities_explanation = {}
            for capability in manifest.get("capabilities", []):
                capabilities_explanation[capability.get("name", "")] = capability.get("description", "")
            
            return {
                "agent_id": self.agent_core.agent_id,
                "capabilities_explanation": capabilities_explanation,
                "explain_timestamp": time.time()
            }
        elif explain_target == "protocols":
            return {
                "agent_id": self.agent_core.agent_id,
                "supported_protocols": {
                    "mcp": "Model Context Protocol for internal communication",
                    "a2a": "Agent-to-Agent Protocol for external communication"
                },
                "protocol_hooks": manifest.get("protocol_hooks", {}),
                "explain_timestamp": time.time()
            }
        else:
            return {
                "agent_id": self.agent_core.agent_id,
                "error": f"Unsupported explain target: {explain_target}",
                "explain_timestamp": time.time()
            }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get handler status.
        
        Returns:
            Handler status
        """
        return {
            "status": "operational",
            "endpoints": {
                "discovery": True,
                "capabilities": True,
                "status": True,
                "health": True,
                "explain": True
            }
        }
