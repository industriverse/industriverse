"""
Well-Known Endpoint for Industriverse Core AI Layer

This module implements the well-known endpoint for agent discovery,
exposing agent manifests at /.well-known/agent.json endpoints for A2A discovery.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WellKnownEndpoint:
    """
    Implements the well-known endpoint for agent discovery.
    Exposes agent manifests at /.well-known/agent.json endpoints for A2A discovery.
    """
    
    def __init__(self, agent_id: str, manifest_path: Optional[str] = None):
        """
        Initialize the well-known endpoint.
        
        Args:
            agent_id: Unique identifier for the agent
            manifest_path: Path to the agent manifest file (optional)
        """
        self.agent_id = agent_id
        self.manifest_path = manifest_path or f"manifests/{agent_id}.yaml"
        self.well_known_dir = ".well-known"
        self.agent_json_path = f"{self.well_known_dir}/agent.json"
        
        # Load manifest
        self.manifest = self._load_manifest()
        
        # Create well-known directory if it doesn't exist
        os.makedirs(self.well_known_dir, exist_ok=True)
    
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
                manifest = yaml.safe_load(f)
                logger.info(f"Loaded manifest for {self.agent_id}")
                return manifest
        except Exception as e:
            logger.error(f"Error loading manifest: {e}")
            return {}
    
    def create_agent_card(self) -> Dict[str, Any]:
        """
        Create an Agent Card for A2A discovery.
        
        Returns:
            The Agent Card as a dictionary
        """
        # Extract A2A-specific fields from manifest
        a2a_integration = self.manifest.get("a2a_integration", {})
        agent_card = a2a_integration.get("agent_card", {})
        
        # Extract component name from agent_id
        component_name = self.agent_id.replace("core-ai-", "").replace("-agent", "")
        
        # Add resilience profile
        resilience_profile = self.manifest.get("resilience_profile", {})
        
        # Add edge behavior profile
        edge_behavior_profile = self.manifest.get("edge_behavior_profile", {})
        
        # Create the Agent Card
        return {
            "agent_id": self.agent_id,
            "agent_name": agent_card.get("agent_name", component_name.title()),
            "agent_description": agent_card.get("agent_description", f"Core AI {component_name.title()} Agent"),
            "capabilities": self._extract_capabilities(),
            "industryTags": agent_card.get("industryTags", ["manufacturing", "energy", "aerospace"]),
            "priority": agent_card.get("priority", 5),
            "resilience_profile": resilience_profile,
            "intelligence_type": self.manifest.get("intelligence_type", "analytical"),
            "intelligence_role": self.manifest.get("intelligence_role", "predictor"),
            "mesh_coordination_role": self.manifest.get("mesh_coordination_role", "follower"),
            "edge_behavior_profile": edge_behavior_profile,
            "observability_hooks": self.manifest.get("observability_hooks", []),
            "endpoints": {
                "mcp_base": f"/mcp/v1/agents/{self.agent_id}",
                "a2a_base": f"/a2a/v1/agents/{self.agent_id}",
                "health": f"/health/{self.agent_id}",
                "metrics": f"/metrics/{self.agent_id}"
            }
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
    
    def expose_agent_card(self) -> bool:
        """
        Expose the agent card at the well-known endpoint.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create agent card
            agent_card = self.create_agent_card()
            
            # Write to well-known endpoint
            with open(self.agent_json_path, 'w') as f:
                json.dump(agent_card, f, indent=2)
                
            logger.info(f"Exposed agent card for {self.agent_id} at {self.agent_json_path}")
            return True
        except Exception as e:
            logger.error(f"Error exposing agent card: {e}")
            return False
    
    def update_agent_card(self, updates: Dict[str, Any]) -> bool:
        """
        Update the agent card with new information.
        
        Args:
            updates: Dictionary of updates to apply
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Read existing agent card
            if not os.path.exists(self.agent_json_path):
                logger.warning(f"Agent card not found at {self.agent_json_path}, creating new one")
                agent_card = self.create_agent_card()
            else:
                with open(self.agent_json_path, 'r') as f:
                    agent_card = json.load(f)
            
            # Apply updates
            for key, value in updates.items():
                if isinstance(value, dict) and key in agent_card and isinstance(agent_card[key], dict):
                    # Merge dictionaries
                    agent_card[key].update(value)
                else:
                    # Replace value
                    agent_card[key] = value
            
            # Write updated agent card
            with open(self.agent_json_path, 'w') as f:
                json.dump(agent_card, f, indent=2)
                
            logger.info(f"Updated agent card for {self.agent_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating agent card: {e}")
            return False
    
    def get_agent_card(self) -> Dict[str, Any]:
        """
        Get the current agent card.
        
        Returns:
            The agent card as a dictionary
        """
        try:
            if not os.path.exists(self.agent_json_path):
                logger.warning(f"Agent card not found at {self.agent_json_path}")
                return {}
                
            with open(self.agent_json_path, 'r') as f:
                agent_card = json.load(f)
                
            return agent_card
        except Exception as e:
            logger.error(f"Error reading agent card: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    # Create a well-known endpoint
    endpoint = WellKnownEndpoint("core-ai-test-agent")
    
    # Expose the agent card
    endpoint.expose_agent_card()
    
    # Update the agent card
    endpoint.update_agent_card({
        "status": "online",
        "health": "healthy",
        "capabilities": [
            {
                "name": "test_capability",
                "description": "A test capability"
            }
        ]
    })
    
    # Get the agent card
    agent_card = endpoint.get_agent_card()
    print(json.dumps(agent_card, indent=2))
