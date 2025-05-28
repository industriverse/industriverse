"""
.well-known Endpoint Implementation for Industriverse Data Layer

This module provides the implementation for exposing .well-known endpoints
for A2A discovery and protocol-native integration.
"""

import json
import logging
import os
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class WellKnownEndpoint:
    """
    Implements .well-known endpoints for A2A discovery and protocol integration.
    
    This class handles the creation and management of .well-known endpoints
    for agent discovery, manifest exposure, and protocol capabilities.
    """
    
    def __init__(
        self,
        agent_id: str,
        component_name: str,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the .well-known endpoint manager.
        
        Args:
            agent_id: Unique identifier for this agent
            component_name: Name of the component
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for .well-known endpoints
        """
        self.agent_id = agent_id
        self.component_name = component_name
        self.manifest_path = manifest_path
        
        # Set up well-known directory
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                ".well-known"
            )
        
        os.makedirs(self.base_dir, exist_ok=True)
        logger.info(f"Initialized .well-known endpoint manager for {component_name}")
    
    def expose_agent_json(self) -> str:
        """
        Expose the agent.json file for A2A discovery.
        
        Returns:
            Path to the created agent.json file
        """
        agent_card = self._generate_agent_card()
        agent_json_path = os.path.join(self.base_dir, "agent.json")
        
        try:
            with open(agent_json_path, 'w') as f:
                json.dump(agent_card, f, indent=2)
            logger.info(f"Exposed agent.json at {agent_json_path}")
            return agent_json_path
        except Exception as e:
            logger.error(f"Failed to expose agent.json: {str(e)}")
            return ""
    
    def expose_mcp_manifest(self) -> str:
        """
        Expose the MCP manifest file for MCP discovery.
        
        Returns:
            Path to the created mcp-manifest.json file
        """
        mcp_manifest = self._generate_mcp_manifest()
        mcp_manifest_path = os.path.join(self.base_dir, "mcp-manifest.json")
        
        try:
            with open(mcp_manifest_path, 'w') as f:
                json.dump(mcp_manifest, f, indent=2)
            logger.info(f"Exposed mcp-manifest.json at {mcp_manifest_path}")
            return mcp_manifest_path
        except Exception as e:
            logger.error(f"Failed to expose mcp-manifest.json: {str(e)}")
            return ""
    
    def expose_protocol_capabilities(self) -> str:
        """
        Expose the protocol capabilities file.
        
        Returns:
            Path to the created protocol-capabilities.json file
        """
        capabilities = self._generate_protocol_capabilities()
        capabilities_path = os.path.join(self.base_dir, "protocol-capabilities.json")
        
        try:
            with open(capabilities_path, 'w') as f:
                json.dump(capabilities, f, indent=2)
            logger.info(f"Exposed protocol-capabilities.json at {capabilities_path}")
            return capabilities_path
        except Exception as e:
            logger.error(f"Failed to expose protocol-capabilities.json: {str(e)}")
            return ""
    
    def expose_all_endpoints(self) -> List[str]:
        """
        Expose all .well-known endpoints.
        
        Returns:
            List of paths to all created endpoint files
        """
        paths = []
        
        # Expose agent.json
        agent_json_path = self.expose_agent_json()
        if agent_json_path:
            paths.append(agent_json_path)
        
        # Expose mcp-manifest.json
        mcp_manifest_path = self.expose_mcp_manifest()
        if mcp_manifest_path:
            paths.append(mcp_manifest_path)
        
        # Expose protocol-capabilities.json
        capabilities_path = self.expose_protocol_capabilities()
        if capabilities_path:
            paths.append(capabilities_path)
        
        logger.info(f"Exposed all .well-known endpoints: {len(paths)} files")
        return paths
    
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
                if self.manifest_path.endswith('.json'):
                    manifest = json.load(f)
                elif self.manifest_path.endswith('.yaml') or self.manifest_path.endswith('.yml'):
                    import yaml
                    manifest = yaml.safe_load(f)
                else:
                    logger.error(f"Unsupported manifest format: {self.manifest_path}")
                    return {}
                
                logger.info(f"Loaded manifest for {self.component_name}")
                return manifest
        except Exception as e:
            logger.error(f"Failed to load manifest: {str(e)}")
            return {}
    
    def _generate_agent_card(self) -> Dict[str, Any]:
        """
        Generate an A2A Agent Card from the manifest.
        
        Returns:
            The Agent Card as a dictionary
        """
        manifest = self._load_manifest()
        
        # Extract relevant information from manifest
        capabilities = []
        for cap in manifest.get("capabilities", []):
            capabilities.append({
                "name": cap.get("name", ""),
                "description": cap.get("description", ""),
                "inputs": cap.get("inputs", []),
                "outputs": cap.get("outputs", [])
            })
        
        # Create the Agent Card
        agent_card = {
            "name": manifest.get("name", self.component_name),
            "description": manifest.get("description", f"Agent for {self.component_name}"),
            "version": manifest.get("version", "1.0.0"),
            "agent_id": self.agent_id,
            "capabilities": capabilities,
            "authentication": manifest.get("protocols", {}).get("a2a", {}).get("authentication", ["oauth2"]),
            "communication": ["json-rpc", "sse", "webhooks"]
        }
        
        # Add industry-specific extensions if present
        industry_extensions = manifest.get("industry_extensions", {})
        if "industryTags" in industry_extensions:
            agent_card["industryTags"] = industry_extensions["industryTags"]
        
        return agent_card
    
    def _generate_mcp_manifest(self) -> Dict[str, Any]:
        """
        Generate an MCP manifest from the agent manifest.
        
        Returns:
            The MCP manifest as a dictionary
        """
        manifest = self._load_manifest()
        
        # Extract MCP-specific information
        mcp_config = manifest.get("protocols", {}).get("mcp", {})
        events = mcp_config.get("events", [])
        
        # Create the MCP manifest
        mcp_manifest = {
            "agent_id": self.agent_id,
            "name": manifest.get("name", self.component_name),
            "description": manifest.get("description", f"Agent for {self.component_name}"),
            "version": manifest.get("version", "1.0.0"),
            "events": {
                "observe": "observe" in events,
                "recommend": "recommend" in events,
                "simulate": "simulate" in events,
                "act": "act" in events
            },
            "security": mcp_config.get("security", {
                "consent_required": True,
                "registry": "controlled"
            }),
            "intelligence_type": manifest.get("intelligence_type", "stateless")
        }
        
        return mcp_manifest
    
    def _generate_protocol_capabilities(self) -> Dict[str, Any]:
        """
        Generate a protocol capabilities document.
        
        Returns:
            The protocol capabilities as a dictionary
        """
        manifest = self._load_manifest()
        
        # Extract protocol information
        protocols = manifest.get("protocols", {})
        
        # Create the capabilities document
        capabilities = {
            "agent_id": self.agent_id,
            "component": self.component_name,
            "protocols": {
                "mcp": {
                    "enabled": protocols.get("mcp", {}).get("enabled", False),
                    "events": protocols.get("mcp", {}).get("events", []),
                    "version": "1.0"
                },
                "a2a": {
                    "enabled": protocols.get("a2a", {}).get("enabled", False),
                    "task_lifecycle": protocols.get("a2a", {}).get("task_lifecycle", False),
                    "message_parts": protocols.get("a2a", {}).get("message_parts", []),
                    "version": "1.0"
                }
            },
            "extensions": {
                "industry": manifest.get("industry_extensions", {}).get("industryTags", []),
                "custom_parts": manifest.get("industry_extensions", {}).get("custom_part_types", [])
            }
        }
        
        return capabilities


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create endpoint manager
    endpoint_manager = WellKnownEndpoint(
        agent_id="data-layer-example-agent",
        component_name="example_component",
        manifest_path="path/to/manifest.yaml"
    )
    
    # Expose all endpoints
    paths = endpoint_manager.expose_all_endpoints()
    print(f"Exposed {len(paths)} endpoints:")
    for path in paths:
        print(f"  - {path}")
