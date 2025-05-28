"""
Mesh Agent Intent Graph for Industriverse Data Layer

This module implements the agent intent graph at the mesh level,
providing a comprehensive view of inter-agent relationships,
capabilities, and communication patterns.
"""

import json
import logging
import os
import yaml
from typing import Dict, Any, Optional, List, Set

logger = logging.getLogger(__name__)

class MeshAgentIntentGraph:
    """
    Implements the mesh-level agent intent graph.
    
    This class manages the relationships, capabilities, and communication
    patterns between agents in the Data Layer mesh, enabling orchestration,
    discovery, and simulation.
    """
    
    def __init__(
        self,
        mesh_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the mesh agent intent graph.
        
        Args:
            mesh_dir: Directory containing mesh configuration files
            output_dir: Directory for output files
            config: Optional configuration dictionary
        """
        self.config = config or {}
        
        # Set up mesh directory
        if mesh_dir:
            self.mesh_dir = mesh_dir
        else:
            self.mesh_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "config", "mesh"
            )
        
        # Set up output directory
        if output_dir:
            self.output_dir = output_dir
        else:
            self.output_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "docs"
            )
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize graph data
        self.agents = {}
        self.capabilities = {}
        self.intents = {}
        self.connections = []
        
        logger.info("Initialized mesh agent intent graph")
    
    def discover_agents(self) -> List[str]:
        """
        Discover all agents in the mesh.
        
        Returns:
            List of discovered agent IDs
        """
        agent_ids = []
        
        # Look for agent JSON files in mesh directory
        for filename in os.listdir(self.mesh_dir):
            if filename.endswith(".json") and not filename.startswith("mesh_") and not filename.startswith("boundary_"):
                agent_id = filename.split(".")[0]
                agent_ids.append(agent_id)
                
                # Load agent data
                agent_path = os.path.join(self.mesh_dir, filename)
                try:
                    with open(agent_path, 'r') as f:
                        agent_data = json.load(f)
                        self.agents[agent_id] = agent_data
                        logger.info(f"Discovered agent: {agent_id}")
                except Exception as e:
                    logger.error(f"Failed to load agent data for {agent_id}: {str(e)}")
        
        return agent_ids
    
    def discover_capabilities(self) -> Dict[str, List[str]]:
        """
        Discover capabilities for all agents.
        
        Returns:
            Dictionary mapping agent IDs to capability lists
        """
        agent_capabilities = {}
        
        # Look for agent manifests in well-known directories
        well_known_base = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".well-known"
        )
        
        if os.path.exists(well_known_base):
            for agent_id in self.agents:
                agent_dir = os.path.join(well_known_base, agent_id)
                if os.path.exists(agent_dir):
                    # Check for agent.json
                    agent_json_path = os.path.join(agent_dir, "agent.json")
                    if os.path.exists(agent_json_path):
                        try:
                            with open(agent_json_path, 'r') as f:
                                agent_card = json.load(f)
                                capabilities = []
                                
                                for cap in agent_card.get("capabilities", []):
                                    cap_name = cap.get("name", "")
                                    if cap_name:
                                        capabilities.append(cap_name)
                                        
                                        # Store capability details
                                        self.capabilities[f"{agent_id}:{cap_name}"] = cap
                                
                                agent_capabilities[agent_id] = capabilities
                                logger.info(f"Discovered capabilities for agent {agent_id}: {capabilities}")
                        except Exception as e:
                            logger.error(f"Failed to load capabilities for {agent_id}: {str(e)}")
        
        return agent_capabilities
    
    def analyze_intents(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Analyze intents between agents based on capabilities.
        
        Returns:
            Dictionary mapping agent IDs to intent lists
        """
        agent_intents = {}
        
        # Analyze each agent's capabilities for potential intents
        for agent_id, capabilities in self.discover_capabilities().items():
            intents = []
            
            for cap_name in capabilities:
                cap_key = f"{agent_id}:{cap_name}"
                if cap_key in self.capabilities:
                    cap_details = self.capabilities[cap_key]
                    
                    # Analyze inputs to determine potential sources
                    for input_param in cap_details.get("inputs", []):
                        input_name = input_param.get("name", "")
                        input_type = input_param.get("type", "")
                        
                        # Find potential source agents for this input
                        source_agents = self._find_potential_sources(input_type)
                        
                        if source_agents:
                            for source_id in source_agents:
                                intent = {
                                    "type": "input",
                                    "capability": cap_name,
                                    "parameter": input_name,
                                    "data_type": input_type,
                                    "source_agent": source_id
                                }
                                intents.append(intent)
                                
                                # Add to connections
                                self.connections.append({
                                    "source": source_id,
                                    "target": agent_id,
                                    "type": "data_flow",
                                    "label": f"{input_type}"
                                })
                    
                    # Analyze outputs to determine potential targets
                    for output_param in cap_details.get("outputs", []):
                        output_name = output_param.get("name", "")
                        output_type = output_param.get("type", "")
                        
                        # Find potential target agents for this output
                        target_agents = self._find_potential_targets(output_type)
                        
                        if target_agents:
                            for target_id in target_agents:
                                intent = {
                                    "type": "output",
                                    "capability": cap_name,
                                    "parameter": output_name,
                                    "data_type": output_type,
                                    "target_agent": target_id
                                }
                                intents.append(intent)
                                
                                # Add to connections
                                self.connections.append({
                                    "source": agent_id,
                                    "target": target_id,
                                    "type": "data_flow",
                                    "label": f"{output_type}"
                                })
            
            agent_intents[agent_id] = intents
            self.intents[agent_id] = intents
            logger.info(f"Analyzed intents for agent {agent_id}: {len(intents)} intents")
        
        return agent_intents
    
    def _find_potential_sources(self, data_type: str) -> List[str]:
        """
        Find potential source agents for a given data type.
        
        Args:
            data_type: The data type to find sources for
            
        Returns:
            List of potential source agent IDs
        """
        sources = []
        
        for agent_id, capabilities in self.discover_capabilities().items():
            for cap_name in capabilities:
                cap_key = f"{agent_id}:{cap_name}"
                if cap_key in self.capabilities:
                    cap_details = self.capabilities[cap_key]
                    
                    # Check if this capability produces the required data type
                    for output_param in cap_details.get("outputs", []):
                        output_type = output_param.get("type", "")
                        if output_type == data_type or output_type == "object":  # object can contain any type
                            sources.append(agent_id)
                            break
        
        return sources
    
    def _find_potential_targets(self, data_type: str) -> List[str]:
        """
        Find potential target agents for a given data type.
        
        Args:
            data_type: The data type to find targets for
            
        Returns:
            List of potential target agent IDs
        """
        targets = []
        
        for agent_id, capabilities in self.discover_capabilities().items():
            for cap_name in capabilities:
                cap_key = f"{agent_id}:{cap_name}"
                if cap_key in self.capabilities:
                    cap_details = self.capabilities[cap_key]
                    
                    # Check if this capability consumes the produced data type
                    for input_param in cap_details.get("inputs", []):
                        input_type = input_param.get("type", "")
                        if input_type == data_type or input_type == "object":  # object can accept any type
                            targets.append(agent_id)
                            break
        
        return targets
    
    def generate_intent_yaml(self) -> str:
        """
        Generate the mesh_agent_intents.yaml file.
        
        Returns:
            Path to the generated YAML file
        """
        # Discover agents and capabilities
        self.discover_agents()
        self.discover_capabilities()
        self.analyze_intents()
        
        # Create the intent graph data
        intent_graph = {
            "version": "1.0.0",
            "generated_at": self._get_timestamp(),
            "agents": {},
            "connections": self.connections
        }
        
        # Add agent data
        for agent_id, agent_data in self.agents.items():
            agent_entry = {
                "id": agent_id,
                "component": agent_data.get("component", "unknown"),
                "status": agent_data.get("status", "unknown"),
                "intelligence_type": agent_data.get("intelligence_type", "stateless"),
                "protocols": agent_data.get("protocols", ["mcp", "a2a"]),
                "capabilities": [],
                "intents": []
            }
            
            # Add capabilities
            if agent_id in self.discover_capabilities():
                for cap_name in self.discover_capabilities()[agent_id]:
                    cap_key = f"{agent_id}:{cap_name}"
                    if cap_key in self.capabilities:
                        agent_entry["capabilities"].append(self.capabilities[cap_key])
            
            # Add intents
            if agent_id in self.intents:
                agent_entry["intents"] = self.intents[agent_id]
            
            intent_graph["agents"][agent_id] = agent_entry
        
        # Write to YAML file
        output_path = os.path.join(self.output_dir, "mesh_agent_intents.yaml")
        try:
            with open(output_path, 'w') as f:
                yaml.dump(intent_graph, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Generated mesh agent intents YAML at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate mesh agent intents YAML: {str(e)}")
            return ""
    
    def generate_dot_graph(self) -> str:
        """
        Generate a DOT graph visualization of the intent graph.
        
        Returns:
            Path to the generated DOT file
        """
        # Ensure we have analyzed intents
        if not self.connections:
            self.analyze_intents()
        
        # Create DOT graph content
        dot_content = [
            "digraph MeshAgentIntents {",
            "  rankdir=LR;",
            "  node [shape=box, style=filled, fillcolor=lightblue];",
            ""
        ]
        
        # Add nodes (agents)
        for agent_id in self.agents:
            component = self.agents[agent_id].get("component", "unknown")
            dot_content.append(f'  "{agent_id}" [label="{component}\\n({agent_id})"];')
        
        dot_content.append("")
        
        # Add edges (connections)
        for conn in self.connections:
            source = conn["source"]
            target = conn["target"]
            label = conn.get("label", "")
            dot_content.append(f'  "{source}" -> "{target}" [label="{label}"];')
        
        dot_content.append("}")
        
        # Write to DOT file
        output_path = os.path.join(self.output_dir, "mesh_agent_intents.dot")
        try:
            with open(output_path, 'w') as f:
                f.write("\n".join(dot_content))
            logger.info(f"Generated mesh agent intents DOT graph at {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate mesh agent intents DOT graph: {str(e)}")
            return ""
    
    def _get_timestamp(self) -> str:
        """
        Get the current timestamp in ISO format.
        
        Returns:
            Current timestamp string
        """
        import time
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create mesh agent intent graph
    intent_graph = MeshAgentIntentGraph()
    
    # Generate intent YAML
    yaml_path = intent_graph.generate_intent_yaml()
    print(f"Generated YAML: {yaml_path}")
    
    # Generate DOT graph
    dot_path = intent_graph.generate_dot_graph()
    print(f"Generated DOT graph: {dot_path}")
