"""
Agent Lineage Manager for Industriverse Generative Layer

This module implements the agent lineage manager that handles agent identity and inheritance trees,
enabling downstream introspection and inheritance-based override behaviors.
"""

import json
import logging
import time
import os
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentLineageManager:
    """
    Implements agent lineage management for the Generative Layer.
    Handles agent identity and inheritance trees for downstream introspection.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the agent lineage manager.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.agent_registry = {}
        self.lineage_trees = {}
        self.inheritance_behaviors = {}
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "lineage_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info("Agent Lineage Manager initialized")
    
    def register_agent(self, 
                      agent_id: str, 
                      agent_type: str,
                      metadata: Dict[str, Any],
                      parent_agent_id: Optional[str] = None,
                      derived_from: Optional[List[str]] = None,
                      inheritance_behavior: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new agent in the lineage system.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_type: Type of agent
            metadata: Metadata about the agent
            parent_agent_id: ID of the parent agent (optional)
            derived_from: List of agent IDs this agent is derived from (optional)
            inheritance_behavior: Inheritance behavior configuration (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        if agent_id in self.agent_registry:
            logger.warning(f"Agent {agent_id} already registered")
            return False
        
        timestamp = time.time()
        
        # Create agent record
        agent = {
            "id": agent_id,
            "type": agent_type,
            "metadata": metadata,
            "parent_agent_id": parent_agent_id,
            "derived_from": derived_from or [],
            "timestamp": timestamp,
            "status": "registered"
        }
        
        # Store agent
        self.agent_registry[agent_id] = agent
        
        # Store inheritance behavior if provided
        if inheritance_behavior:
            self.inheritance_behaviors[agent_id] = inheritance_behavior
        
        # Update lineage trees
        self._update_lineage_trees(agent_id, parent_agent_id, derived_from)
        
        # Store agent file
        agent_path = os.path.join(self.storage_path, f"{agent_id}_agent.json")
        with open(agent_path, 'w') as f:
            json.dump(agent, f, indent=2)
        
        logger.info(f"Registered agent {agent_id} of type {agent_type}")
        
        # Emit MCP event for agent registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/agent/registered",
                {
                    "agent_id": agent_id,
                    "agent_type": agent_type,
                    "parent_agent_id": parent_agent_id
                }
            )
        
        return True
    
    def _update_lineage_trees(self, 
                             agent_id: str, 
                             parent_agent_id: Optional[str] = None,
                             derived_from: Optional[List[str]] = None) -> None:
        """
        Update lineage trees with a new agent.
        
        Args:
            agent_id: ID of the agent
            parent_agent_id: ID of the parent agent (optional)
            derived_from: List of agent IDs this agent is derived from (optional)
        """
        # Initialize lineage tree for this agent
        if agent_id not in self.lineage_trees:
            self.lineage_trees[agent_id] = {
                "parent": parent_agent_id,
                "derived_from": derived_from or [],
                "children": [],
                "derived_agents": []
            }
        
        # Update parent's lineage tree
        if parent_agent_id and parent_agent_id in self.lineage_trees:
            if agent_id not in self.lineage_trees[parent_agent_id]["children"]:
                self.lineage_trees[parent_agent_id]["children"].append(agent_id)
        
        # Update derived_from agents' lineage trees
        if derived_from:
            for derived_agent_id in derived_from:
                if derived_agent_id in self.lineage_trees:
                    if agent_id not in self.lineage_trees[derived_agent_id]["derived_agents"]:
                        self.lineage_trees[derived_agent_id]["derived_agents"].append(agent_id)
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an agent by ID.
        
        Args:
            agent_id: ID of the agent to retrieve
            
        Returns:
            Agent data if found, None otherwise
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent {agent_id} not found")
            return None
        
        return self.agent_registry[agent_id]
    
    def get_agent_lineage(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the lineage of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent lineage if found, None otherwise
        """
        if agent_id not in self.lineage_trees:
            logger.warning(f"Agent lineage for {agent_id} not found")
            return None
        
        return self.lineage_trees[agent_id]
    
    def get_inheritance_behavior(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the inheritance behavior of an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Inheritance behavior if found, None otherwise
        """
        if agent_id not in self.inheritance_behaviors:
            logger.warning(f"Inheritance behavior for {agent_id} not found")
            return None
        
        return self.inheritance_behaviors[agent_id]
    
    def set_inheritance_behavior(self, 
                                agent_id: str, 
                                inheritance_behavior: Dict[str, Any]) -> bool:
        """
        Set the inheritance behavior of an agent.
        
        Args:
            agent_id: ID of the agent
            inheritance_behavior: Inheritance behavior configuration
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent {agent_id} not found")
            return False
        
        # Store inheritance behavior
        self.inheritance_behaviors[agent_id] = inheritance_behavior
        
        # Store inheritance behavior file
        behavior_path = os.path.join(self.storage_path, f"{agent_id}_inheritance.json")
        with open(behavior_path, 'w') as f:
            json.dump(inheritance_behavior, f, indent=2)
        
        logger.info(f"Set inheritance behavior for agent {agent_id}")
        
        return True
    
    def get_agent_ancestors(self, agent_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """
        Get all ancestors of an agent up to a maximum depth.
        
        Args:
            agent_id: ID of the agent
            max_depth: Maximum depth to traverse up the lineage tree
            
        Returns:
            List of ancestor agents
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent {agent_id} not found")
            return []
        
        ancestors = []
        current_id = self.agent_registry[agent_id].get("parent_agent_id")
        depth = 0
        
        while current_id and depth < max_depth:
            if current_id in self.agent_registry:
                ancestors.append(self.agent_registry[current_id])
                current_id = self.agent_registry[current_id].get("parent_agent_id")
            else:
                break
            
            depth += 1
        
        return ancestors
    
    def get_agent_descendants(self, agent_id: str, max_depth: int = 10) -> List[Dict[str, Any]]:
        """
        Get all descendants of an agent up to a maximum depth.
        
        Args:
            agent_id: ID of the agent
            max_depth: Maximum depth to traverse down the lineage tree
            
        Returns:
            List of descendant agents
        """
        if agent_id not in self.lineage_trees:
            logger.warning(f"Agent lineage for {agent_id} not found")
            return []
        
        descendants = []
        self._collect_descendants(agent_id, descendants, 0, max_depth)
        
        return [self.agent_registry[d_id] for d_id in descendants if d_id in self.agent_registry]
    
    def _collect_descendants(self, 
                            agent_id: str, 
                            descendants: List[str], 
                            current_depth: int, 
                            max_depth: int) -> None:
        """
        Recursively collect descendants of an agent.
        
        Args:
            agent_id: ID of the agent
            descendants: List to collect descendant IDs
            current_depth: Current depth in the recursion
            max_depth: Maximum depth to traverse
        """
        if current_depth >= max_depth or agent_id not in self.lineage_trees:
            return
        
        children = self.lineage_trees[agent_id].get("children", [])
        
        for child_id in children:
            if child_id not in descendants:
                descendants.append(child_id)
                self._collect_descendants(child_id, descendants, current_depth + 1, max_depth)
    
    def get_derived_agents(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all agents derived from a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of derived agents
        """
        if agent_id not in self.lineage_trees:
            logger.warning(f"Agent lineage for {agent_id} not found")
            return []
        
        derived_ids = self.lineage_trees[agent_id].get("derived_agents", [])
        
        return [self.agent_registry[d_id] for d_id in derived_ids if d_id in self.agent_registry]
    
    def resolve_inheritance(self, 
                           agent_id: str, 
                           property_path: str,
                           default_value: Any = None) -> Any:
        """
        Resolve a property value through the inheritance chain.
        
        Args:
            agent_id: ID of the agent
            property_path: Path to the property (dot-separated)
            default_value: Default value if property not found
            
        Returns:
            Resolved property value
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent {agent_id} not found")
            return default_value
        
        # Check if this agent has the property
        agent = self.agent_registry[agent_id]
        value = self._get_nested_property(agent, property_path)
        
        if value is not None:
            return value
        
        # Check inheritance behavior
        inheritance_behavior = self.inheritance_behaviors.get(agent_id, {})
        inheritance_mode = inheritance_behavior.get("mode", "parent_first")
        
        if inheritance_mode == "parent_first":
            # Check parent first, then derived_from
            parent_id = agent.get("parent_agent_id")
            if parent_id:
                parent_value = self.resolve_inheritance(parent_id, property_path, None)
                if parent_value is not None:
                    return parent_value
            
            # Check derived_from agents
            for derived_id in agent.get("derived_from", []):
                derived_value = self.resolve_inheritance(derived_id, property_path, None)
                if derived_value is not None:
                    return derived_value
        
        elif inheritance_mode == "derived_first":
            # Check derived_from first, then parent
            for derived_id in agent.get("derived_from", []):
                derived_value = self.resolve_inheritance(derived_id, property_path, None)
                if derived_value is not None:
                    return derived_value
            
            parent_id = agent.get("parent_agent_id")
            if parent_id:
                parent_value = self.resolve_inheritance(parent_id, property_path, None)
                if parent_value is not None:
                    return parent_value
        
        # If still not found, return default value
        return default_value
    
    def _get_nested_property(self, obj: Dict[str, Any], property_path: str) -> Any:
        """
        Get a nested property from an object using a dot-separated path.
        
        Args:
            obj: The object to get the property from
            property_path: Path to the property (dot-separated)
            
        Returns:
            Property value if found, None otherwise
        """
        parts = property_path.split('.')
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def merge_agent_properties(self, 
                              agent_id: str, 
                              property_path: str,
                              merge_strategy: str = "override") -> Any:
        """
        Merge a property across the inheritance chain.
        
        Args:
            agent_id: ID of the agent
            property_path: Path to the property (dot-separated)
            merge_strategy: Strategy for merging properties
            
        Returns:
            Merged property value
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent {agent_id} not found")
            return None
        
        # Get all values from the inheritance chain
        values = []
        
        # Get value from this agent
        agent = self.agent_registry[agent_id]
        value = self._get_nested_property(agent, property_path)
        if value is not None:
            values.append(("self", value))
        
        # Get value from parent
        parent_id = agent.get("parent_agent_id")
        if parent_id and parent_id in self.agent_registry:
            parent_value = self._get_nested_property(self.agent_registry[parent_id], property_path)
            if parent_value is not None:
                values.append(("parent", parent_value))
        
        # Get values from derived_from agents
        for derived_id in agent.get("derived_from", []):
            if derived_id in self.agent_registry:
                derived_value = self._get_nested_property(self.agent_registry[derived_id], property_path)
                if derived_value is not None:
                    values.append(("derived", derived_value))
        
        # Apply merge strategy
        if not values:
            return None
        
        if merge_strategy == "override":
            # Self overrides parent overrides derived
            for source, value in values:
                if source == "self":
                    return value
            
            for source, value in values:
                if source == "parent":
                    return value
            
            return values[0][1]  # Return first value
        
        elif merge_strategy == "list_concat":
            # Concatenate lists
            result = []
            for _, value in values:
                if isinstance(value, list):
                    result.extend(value)
                else:
                    result.append(value)
            
            return result
        
        elif merge_strategy == "dict_merge":
            # Merge dictionaries
            result = {}
            for _, value in reversed(values):  # Reverse to apply self last
                if isinstance(value, dict):
                    result.update(value)
            
            return result
        
        # Default: return self value or first value
        for source, value in values:
            if source == "self":
                return value
        
        return values[0][1]  # Return first value
    
    def export_lineage_data(self) -> Dict[str, Any]:
        """
        Export lineage data for persistence.
        
        Returns:
            Lineage data
        """
        return {
            "agent_registry": self.agent_registry,
            "lineage_trees": self.lineage_trees,
            "inheritance_behaviors": self.inheritance_behaviors
        }
    
    def import_lineage_data(self, lineage_data: Dict[str, Any]) -> None:
        """
        Import lineage data from persistence.
        
        Args:
            lineage_data: Lineage data to import
        """
        if "agent_registry" in lineage_data:
            self.agent_registry = lineage_data["agent_registry"]
        
        if "lineage_trees" in lineage_data:
            self.lineage_trees = lineage_data["lineage_trees"]
        
        if "inheritance_behaviors" in lineage_data:
            self.inheritance_behaviors = lineage_data["inheritance_behaviors"]
        
        logger.info("Imported lineage data")
    
    def create_agent_lineage_graph(self, agent_id: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Create a graph representation of an agent's lineage.
        
        Args:
            agent_id: ID of the agent
            max_depth: Maximum depth to traverse
            
        Returns:
            Graph representation of the agent's lineage
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent {agent_id} not found")
            return {"nodes": [], "edges": []}
        
        nodes = []
        edges = []
        visited = set()
        
        # Start with the agent itself
        self._add_node_to_graph(agent_id, nodes)
        visited.add(agent_id)
        
        # Add ancestors
        current_id = self.agent_registry[agent_id].get("parent_agent_id")
        depth = 0
        
        while current_id and depth < max_depth:
            if current_id in self.agent_registry and current_id not in visited:
                self._add_node_to_graph(current_id, nodes)
                edges.append({
                    "source": agent_id if depth == 0 else self.agent_registry[agent_id].get("parent_agent_id"),
                    "target": current_id,
                    "type": "parent"
                })
                visited.add(current_id)
                
                # Add derived_from edges for this ancestor
                for derived_id in self.agent_registry[current_id].get("derived_from", []):
                    if derived_id in self.agent_registry and derived_id not in visited:
                        self._add_node_to_graph(derived_id, nodes)
                        edges.append({
                            "source": current_id,
                            "target": derived_id,
                            "type": "derived_from"
                        })
                        visited.add(derived_id)
                
                current_id = self.agent_registry[current_id].get("parent_agent_id")
            else:
                break
            
            depth += 1
        
        # Add derived_from for the original agent
        for derived_id in self.agent_registry[agent_id].get("derived_from", []):
            if derived_id in self.agent_registry and derived_id not in visited:
                self._add_node_to_graph(derived_id, nodes)
                edges.append({
                    "source": agent_id,
                    "target": derived_id,
                    "type": "derived_from"
                })
                visited.add(derived_id)
        
        # Add children
        if agent_id in self.lineage_trees:
            children = self.lineage_trees[agent_id].get("children", [])
            for child_id in children:
                if child_id in self.agent_registry and child_id not in visited:
                    self._add_node_to_graph(child_id, nodes)
                    edges.append({
                        "source": child_id,
                        "target": agent_id,
                        "type": "parent"
                    })
                    visited.add(child_id)
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def _add_node_to_graph(self, agent_id: str, nodes: List[Dict[str, Any]]) -> None:
        """
        Add a node to the graph representation.
        
        Args:
            agent_id: ID of the agent
            nodes: List of nodes to add to
        """
        agent = self.agent_registry[agent_id]
        nodes.append({
            "id": agent_id,
            "type": agent.get("type", "unknown"),
            "label": agent.get("metadata", {}).get("name", agent_id),
            "metadata": {
                "status": agent.get("status", "unknown"),
                "timestamp": agent.get("timestamp", 0)
            }
        })
