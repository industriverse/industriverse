"""
Mesh Agent Intent Graph for Industriverse Core AI Layer

This module implements the intent graph for Core AI Layer agents,
enabling semantic reasoning and cross-agent coordination.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeshAgentIntentGraph:
    """
    Implements the intent graph for Core AI Layer agents.
    Enables semantic reasoning and cross-agent coordination based on intent.
    """
    
    def __init__(self):
        """Initialize the mesh agent intent graph."""
        self.intent_nodes = {}
        self.intent_edges = {}
        self.agent_intents = {}
        self.intent_history = {}
        
    async def register_agent_intent(self, agent_id: str, intent: Dict[str, Any]) -> str:
        """
        Register an agent's intent in the graph.
        
        Args:
            agent_id: ID of the agent
            intent: Intent data
            
        Returns:
            Intent ID
        """
        intent_id = f"intent-{len(self.intent_nodes) + 1}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Create intent node
        self.intent_nodes[intent_id] = {
            "agent_id": agent_id,
            "intent_type": intent.get("intent_type", "unknown"),
            "description": intent.get("description", ""),
            "parameters": intent.get("parameters", {}),
            "priority": intent.get("priority", 5),
            "timestamp": datetime.utcnow().isoformat(),
            "status": "active"
        }
        
        # Add to agent intents
        if agent_id not in self.agent_intents:
            self.agent_intents[agent_id] = set()
            
        self.agent_intents[agent_id].add(intent_id)
        
        # Add to history
        if agent_id not in self.intent_history:
            self.intent_history[agent_id] = []
            
        self.intent_history[agent_id].append({
            "intent_id": intent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "register"
        })
        
        logger.info(f"Registered intent {intent_id} for agent {agent_id}")
        
        # Find related intents
        await self._find_related_intents(intent_id)
        
        return intent_id
    
    async def _find_related_intents(self, intent_id: str) -> None:
        """
        Find intents related to the given intent and create edges.
        
        Args:
            intent_id: ID of the intent to find relations for
        """
        intent = self.intent_nodes.get(intent_id)
        if not intent:
            logger.warning(f"Intent not found: {intent_id}")
            return
            
        # Find related intents
        for other_id, other_intent in self.intent_nodes.items():
            if other_id == intent_id:
                continue
                
            # Check if intents are related
            relation = self._calculate_intent_relation(intent, other_intent)
            
            if relation["strength"] > 0.5:
                # Create edge
                edge_id = f"{intent_id}:{other_id}"
                self.intent_edges[edge_id] = {
                    "source": intent_id,
                    "target": other_id,
                    "relation_type": relation["type"],
                    "strength": relation["strength"],
                    "timestamp": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Created intent edge: {edge_id} ({relation['type']}, {relation['strength']:.2f})")
    
    def _calculate_intent_relation(self, intent1: Dict[str, Any], intent2: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate the relation between two intents.
        
        Args:
            intent1: First intent
            intent2: Second intent
            
        Returns:
            Dictionary with relation type and strength
        """
        # In a real implementation, this would use semantic similarity
        # and other techniques to determine the relation
        
        # For now, we'll use a simple heuristic
        if intent1["intent_type"] == intent2["intent_type"]:
            return {
                "type": "same_type",
                "strength": 0.8
            }
        
        # Check if parameters overlap
        param_overlap = 0
        for key in intent1["parameters"]:
            if key in intent2["parameters"] and intent1["parameters"][key] == intent2["parameters"][key]:
                param_overlap += 1
                
        if param_overlap > 0:
            return {
                "type": "parameter_overlap",
                "strength": 0.5 + (param_overlap / 10)
            }
        
        # Default: weak relation
        return {
            "type": "weak",
            "strength": 0.2
        }
    
    async def update_intent_status(self, intent_id: str, status: str) -> bool:
        """
        Update the status of an intent.
        
        Args:
            intent_id: ID of the intent
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        if intent_id not in self.intent_nodes:
            logger.warning(f"Intent not found: {intent_id}")
            return False
            
        # Update status
        self.intent_nodes[intent_id]["status"] = status
        
        # Add to history
        agent_id = self.intent_nodes[intent_id]["agent_id"]
        self.intent_history[agent_id].append({
            "intent_id": intent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "update_status",
            "status": status
        })
        
        logger.info(f"Updated intent {intent_id} status to {status}")
        
        # If completed or failed, notify related intents
        if status in ["completed", "failed"]:
            await self._notify_related_intents(intent_id, status)
            
        return True
    
    async def _notify_related_intents(self, intent_id: str, status: str) -> None:
        """
        Notify related intents of a status change.
        
        Args:
            intent_id: ID of the intent
            status: New status
        """
        # Find related intents
        related_intents = []
        
        for edge_id, edge in self.intent_edges.items():
            if edge["source"] == intent_id:
                related_intents.append(edge["target"])
            elif edge["target"] == intent_id:
                related_intents.append(edge["source"])
        
        # Notify related intents
        for related_id in related_intents:
            related_agent_id = self.intent_nodes[related_id]["agent_id"]
            
            # In a real implementation, this would send a notification
            # to the agent using the MCP adapter
            
            logger.info(f"Notified agent {related_agent_id} about intent {intent_id} status: {status}")
    
    def get_agent_intents(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all intents for an agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of intent data
        """
        if agent_id not in self.agent_intents:
            return []
            
        return [
            self.intent_nodes[intent_id]
            for intent_id in self.agent_intents[agent_id]
            if intent_id in self.intent_nodes
        ]
    
    def get_intent_graph(self) -> Dict[str, Any]:
        """
        Get the entire intent graph.
        
        Returns:
            Dictionary with nodes and edges
        """
        return {
            "nodes": self.intent_nodes,
            "edges": self.intent_edges
        }
    
    def get_intent_subgraph(self, intent_id: str, depth: int = 1) -> Dict[str, Any]:
        """
        Get a subgraph centered on an intent.
        
        Args:
            intent_id: ID of the central intent
            depth: Maximum distance from central intent
            
        Returns:
            Dictionary with nodes and edges
        """
        if intent_id not in self.intent_nodes:
            logger.warning(f"Intent not found: {intent_id}")
            return {"nodes": {}, "edges": {}}
            
        # Find nodes and edges within depth
        nodes = {intent_id: self.intent_nodes[intent_id]}
        edges = {}
        
        # BFS to find nodes within depth
        queue = [(intent_id, 0)]
        visited = {intent_id}
        
        while queue:
            node_id, node_depth = queue.pop(0)
            
            if node_depth >= depth:
                continue
                
            # Find connected nodes
            for edge_id, edge in self.intent_edges.items():
                if edge["source"] == node_id:
                    target_id = edge["target"]
                    edges[edge_id] = edge
                    
                    if target_id not in visited:
                        visited.add(target_id)
                        nodes[target_id] = self.intent_nodes[target_id]
                        queue.append((target_id, node_depth + 1))
                        
                elif edge["target"] == node_id:
                    source_id = edge["source"]
                    edges[edge_id] = edge
                    
                    if source_id not in visited:
                        visited.add(source_id)
                        nodes[source_id] = self.intent_nodes[source_id]
                        queue.append((source_id, node_depth + 1))
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_intent_history(self, agent_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get the intent history for an agent.
        
        Args:
            agent_id: ID of the agent
            limit: Maximum number of history items to return
            
        Returns:
            List of history items
        """
        if agent_id not in self.intent_history:
            return []
            
        return self.intent_history[agent_id][-limit:]
    
    def find_conflicting_intents(self) -> List[Tuple[str, str, float]]:
        """
        Find potentially conflicting intents.
        
        Returns:
            List of tuples (intent_id1, intent_id2, conflict_score)
        """
        conflicts = []
        
        # Check all pairs of active intents
        active_intents = [
            intent_id
            for intent_id, intent in self.intent_nodes.items()
            if intent["status"] == "active"
        ]
        
        for i, intent_id1 in enumerate(active_intents):
            intent1 = self.intent_nodes[intent_id1]
            
            for j in range(i + 1, len(active_intents)):
                intent_id2 = active_intents[j]
                intent2 = self.intent_nodes[intent_id2]
                
                # Check if intents might conflict
                conflict_score = self._calculate_conflict_score(intent1, intent2)
                
                if conflict_score > 0.7:
                    conflicts.append((intent_id1, intent_id2, conflict_score))
        
        return conflicts
    
    def _calculate_conflict_score(self, intent1: Dict[str, Any], intent2: Dict[str, Any]) -> float:
        """
        Calculate a conflict score between two intents.
        
        Args:
            intent1: First intent
            intent2: Second intent
            
        Returns:
            Conflict score (0-1)
        """
        # In a real implementation, this would use semantic analysis
        # to determine if intents might conflict
        
        # For now, we'll use a simple heuristic
        if intent1["intent_type"] == intent2["intent_type"]:
            # Same type might conflict if parameters are different
            param_diff = 0
            for key in intent1["parameters"]:
                if key in intent2["parameters"] and intent1["parameters"][key] != intent2["parameters"][key]:
                    param_diff += 1
                    
            if param_diff > 0:
                return 0.5 + (param_diff / 10)
        
        # Different agents with high priority intents might conflict
        if intent1["agent_id"] != intent2["agent_id"] and intent1["priority"] >= 8 and intent2["priority"] >= 8:
            return 0.8
        
        # Default: low conflict
        return 0.1


# Example usage
if __name__ == "__main__":
    async def main():
        # Create an intent graph
        graph = MeshAgentIntentGraph()
        
        # Register some intents
        intent_id1 = await graph.register_agent_intent("core-ai-llm-agent", {
            "intent_type": "model_inference",
            "description": "Run inference on text input",
            "parameters": {
                "model": "gpt-4",
                "max_tokens": 1000
            },
            "priority": 5
        })
        
        intent_id2 = await graph.register_agent_intent("core-ai-ml-agent", {
            "intent_type": "model_training",
            "description": "Train a new model",
            "parameters": {
                "dataset": "manufacturing_defects",
                "epochs": 10
            },
            "priority": 8
        })
        
        intent_id3 = await graph.register_agent_intent("core-ai-llm-agent", {
            "intent_type": "model_inference",
            "description": "Run inference on another text input",
            "parameters": {
                "model": "gpt-4",
                "max_tokens": 500
            },
            "priority": 6
        })
        
        # Update intent status
        await graph.update_intent_status(intent_id1, "completed")
        
        # Get agent intents
        llm_intents = graph.get_agent_intents("core-ai-llm-agent")
        print(f"LLM agent intents: {len(llm_intents)}")
        
        # Get intent subgraph
        subgraph = graph.get_intent_subgraph(intent_id2)
        print(f"Subgraph nodes: {len(subgraph['nodes'])}")
        print(f"Subgraph edges: {len(subgraph['edges'])}")
        
        # Find conflicting intents
        conflicts = graph.find_conflicting_intents()
        print(f"Found {len(conflicts)} potential conflicts")
    
    asyncio.run(main())
