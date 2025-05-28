"""
Intent Overlay Agent for Industriverse Core AI Layer

This module implements the intent overlay agent for knowledge graph integration
and semantic reasoning in the Core AI Layer.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentOverlayAgent:
    """
    Implements the intent overlay agent for Core AI Layer.
    Provides knowledge graph integration and semantic reasoning capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the intent overlay agent.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or "config/intent_overlay.yaml"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.knowledge_graph = {}
        self.intent_registry = {}
        self.semantic_mappings = {}
        self.context_history = []
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration.
        
        Returns:
            The configuration as a dictionary
        """
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def register_knowledge_node(self, node_type: str, node_data: Dict[str, Any]) -> str:
        """
        Register a knowledge node in the graph.
        
        Args:
            node_type: Type of node
            node_data: Node data
            
        Returns:
            Node ID
        """
        node_id = node_data.get("id") or f"{node_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Create node
        node = {
            "node_id": node_id,
            "node_type": node_type,
            "creation_timestamp": datetime.utcnow().isoformat(),
            "data": node_data,
            "connections": []
        }
        
        # Add to graph
        self.knowledge_graph[node_id] = node
        
        logger.info(f"Registered knowledge node {node_id} of type {node_type}")
        
        return node_id
    
    async def connect_knowledge_nodes(self, source_id: str, target_id: str, relation_type: str, 
                                     relation_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Connect two knowledge nodes.
        
        Args:
            source_id: ID of the source node
            target_id: ID of the target node
            relation_type: Type of relation
            relation_data: Additional relation data (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if source_id not in self.knowledge_graph:
            logger.warning(f"Source node not found: {source_id}")
            return False
            
        if target_id not in self.knowledge_graph:
            logger.warning(f"Target node not found: {target_id}")
            return False
            
        # Create connection
        connection = {
            "target_id": target_id,
            "relation_type": relation_type,
            "creation_timestamp": datetime.utcnow().isoformat(),
            "data": relation_data or {}
        }
        
        # Add to source node
        self.knowledge_graph[source_id]["connections"].append(connection)
        
        logger.info(f"Connected nodes {source_id} -> {target_id} with relation {relation_type}")
        
        return True
    
    async def register_intent(self, agent_id: str, intent_type: str, intent_data: Dict[str, Any]) -> str:
        """
        Register an intent.
        
        Args:
            agent_id: ID of the agent
            intent_type: Type of intent
            intent_data: Intent data
            
        Returns:
            Intent ID
        """
        intent_id = f"intent-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        
        # Create intent
        intent = {
            "intent_id": intent_id,
            "agent_id": agent_id,
            "intent_type": intent_type,
            "creation_timestamp": datetime.utcnow().isoformat(),
            "data": intent_data,
            "status": "active",
            "knowledge_nodes": [],
            "context": {}
        }
        
        # Add to registry
        self.intent_registry[intent_id] = intent
        
        logger.info(f"Registered intent {intent_id} of type {intent_type} for agent {agent_id}")
        
        # Process intent
        await self._process_intent(intent_id)
        
        return intent_id
    
    async def _process_intent(self, intent_id: str) -> None:
        """
        Process an intent.
        
        Args:
            intent_id: ID of the intent
        """
        if intent_id not in self.intent_registry:
            logger.warning(f"Intent not found: {intent_id}")
            return
            
        intent = self.intent_registry[intent_id]
        
        logger.info(f"Processing intent {intent_id}")
        
        try:
            # Extract semantic concepts
            concepts = await self._extract_semantic_concepts(intent)
            
            # Find relevant knowledge nodes
            relevant_nodes = await self._find_relevant_knowledge_nodes(concepts)
            
            # Link intent to knowledge nodes
            for node_id in relevant_nodes:
                intent["knowledge_nodes"].append(node_id)
            
            # Build context
            intent["context"] = await self._build_intent_context(intent_id, relevant_nodes)
            
            logger.info(f"Processed intent {intent_id} with {len(relevant_nodes)} relevant nodes")
            
            # Add to context history
            self.context_history.append({
                "intent_id": intent_id,
                "timestamp": datetime.utcnow().isoformat(),
                "context": intent["context"]
            })
            
            # Keep history size manageable
            max_history = self.config.get("max_context_history", 1000)
            if len(self.context_history) > max_history:
                self.context_history = self.context_history[-max_history:]
        except Exception as e:
            logger.error(f"Error processing intent {intent_id}: {e}")
            intent["status"] = "error"
            intent["error"] = str(e)
    
    async def _extract_semantic_concepts(self, intent: Dict[str, Any]) -> List[str]:
        """
        Extract semantic concepts from an intent.
        
        Args:
            intent: Intent data
            
        Returns:
            List of semantic concepts
        """
        # In a real implementation, this would use NLP techniques
        # to extract semantic concepts from the intent data
        
        # For now, use a simple approach
        concepts = []
        
        # Extract from intent type
        concepts.append(intent["intent_type"])
        
        # Extract from intent data
        for key, value in intent["data"].items():
            if isinstance(value, str):
                concepts.append(value)
            elif isinstance(value, (list, tuple)) and all(isinstance(v, str) for v in value):
                concepts.extend(value)
        
        # Remove duplicates and empty strings
        concepts = [c for c in set(concepts) if c]
        
        return concepts
    
    async def _find_relevant_knowledge_nodes(self, concepts: List[str]) -> List[str]:
        """
        Find knowledge nodes relevant to semantic concepts.
        
        Args:
            concepts: List of semantic concepts
            
        Returns:
            List of relevant node IDs
        """
        relevant_nodes = set()
        
        # For each concept, find matching nodes
        for concept in concepts:
            # Check semantic mappings
            if concept in self.semantic_mappings:
                relevant_nodes.update(self.semantic_mappings[concept])
                continue
                
            # Search in knowledge graph
            for node_id, node in self.knowledge_graph.items():
                # Check node type
                if node["node_type"] == concept:
                    relevant_nodes.add(node_id)
                    continue
                    
                # Check node data
                for key, value in node["data"].items():
                    if isinstance(value, str) and concept.lower() in value.lower():
                        relevant_nodes.add(node_id)
                        break
                        
                    elif isinstance(value, (list, tuple)) and any(concept.lower() in str(v).lower() for v in value):
                        relevant_nodes.add(node_id)
                        break
        
        return list(relevant_nodes)
    
    async def _build_intent_context(self, intent_id: str, node_ids: List[str]) -> Dict[str, Any]:
        """
        Build context for an intent.
        
        Args:
            intent_id: ID of the intent
            node_ids: List of relevant node IDs
            
        Returns:
            Intent context
        """
        intent = self.intent_registry[intent_id]
        
        # Build context
        context = {
            "intent_id": intent_id,
            "intent_type": intent["intent_type"],
            "agent_id": intent["agent_id"],
            "timestamp": datetime.utcnow().isoformat(),
            "knowledge_nodes": [],
            "related_intents": []
        }
        
        # Add knowledge nodes
        for node_id in node_ids:
            if node_id in self.knowledge_graph:
                node = self.knowledge_graph[node_id]
                
                context["knowledge_nodes"].append({
                    "node_id": node_id,
                    "node_type": node["node_type"],
                    "data": node["data"]
                })
        
        # Find related intents
        related_intents = await self._find_related_intents(intent_id, node_ids)
        
        for related_id in related_intents:
            related = self.intent_registry[related_id]
            
            context["related_intents"].append({
                "intent_id": related_id,
                "intent_type": related["intent_type"],
                "agent_id": related["agent_id"],
                "timestamp": related["creation_timestamp"]
            })
        
        return context
    
    async def _find_related_intents(self, intent_id: str, node_ids: List[str]) -> List[str]:
        """
        Find intents related to the given intent.
        
        Args:
            intent_id: ID of the intent
            node_ids: List of relevant node IDs
            
        Returns:
            List of related intent IDs
        """
        related_intents = set()
        
        # Find intents that share knowledge nodes
        for other_id, other in self.intent_registry.items():
            if other_id == intent_id:
                continue
                
            # Check if intents share knowledge nodes
            shared_nodes = set(other["knowledge_nodes"]) & set(node_ids)
            
            if shared_nodes:
                related_intents.add(other_id)
        
        return list(related_intents)
    
    async def update_intent_status(self, intent_id: str, status: str) -> bool:
        """
        Update intent status.
        
        Args:
            intent_id: ID of the intent
            status: New status
            
        Returns:
            True if successful, False otherwise
        """
        if intent_id not in self.intent_registry:
            logger.warning(f"Intent not found: {intent_id}")
            return False
            
        # Update status
        self.intent_registry[intent_id]["status"] = status
        
        logger.info(f"Updated intent {intent_id} status to {status}")
        
        return True
    
    async def register_semantic_mapping(self, concept: str, node_ids: List[str]) -> bool:
        """
        Register a semantic mapping.
        
        Args:
            concept: Semantic concept
            node_ids: List of node IDs
            
        Returns:
            True if successful, False otherwise
        """
        # Validate node IDs
        for node_id in node_ids:
            if node_id not in self.knowledge_graph:
                logger.warning(f"Node not found: {node_id}")
                return False
        
        # Register mapping
        self.semantic_mappings[concept] = node_ids
        
        logger.info(f"Registered semantic mapping for concept '{concept}' to {len(node_ids)} nodes")
        
        return True
    
    def get_intent(self, intent_id: str) -> Dict[str, Any]:
        """
        Get an intent.
        
        Args:
            intent_id: ID of the intent
            
        Returns:
            Intent data
        """
        if intent_id not in self.intent_registry:
            logger.warning(f"Intent not found: {intent_id}")
            return {}
            
        return self.intent_registry[intent_id]
    
    def get_knowledge_node(self, node_id: str) -> Dict[str, Any]:
        """
        Get a knowledge node.
        
        Args:
            node_id: ID of the node
            
        Returns:
            Node data
        """
        if node_id not in self.knowledge_graph:
            logger.warning(f"Node not found: {node_id}")
            return {}
            
        return self.knowledge_graph[node_id]
    
    def get_context_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get context history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of context history items
        """
        return self.context_history[-limit:]
    
    async def query_knowledge_graph(self, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Query the knowledge graph.
        
        Args:
            query: Query parameters
            
        Returns:
            List of matching nodes
        """
        results = []
        
        # Extract query parameters
        node_type = query.get("node_type")
        properties = query.get("properties", {})
        relations = query.get("relations", [])
        
        # Filter by node type
        candidates = []
        
        if node_type:
            for node_id, node in self.knowledge_graph.items():
                if node["node_type"] == node_type:
                    candidates.append(node)
        else:
            candidates = list(self.knowledge_graph.values())
        
        # Filter by properties
        if properties:
            filtered = []
            
            for node in candidates:
                match = True
                
                for key, value in properties.items():
                    if key not in node["data"] or node["data"][key] != value:
                        match = False
                        break
                
                if match:
                    filtered.append(node)
                    
            candidates = filtered
        
        # Filter by relations
        if relations:
            filtered = []
            
            for node in candidates:
                match = True
                
                for relation in relations:
                    relation_type = relation.get("type")
                    target_type = relation.get("target_type")
                    target_properties = relation.get("target_properties", {})
                    
                    # Check if node has matching connections
                    has_relation = False
                    
                    for connection in node["connections"]:
                        if relation_type and connection["relation_type"] != relation_type:
                            continue
                            
                        target_id = connection["target_id"]
                        
                        if target_id not in self.knowledge_graph:
                            continue
                            
                        target = self.knowledge_graph[target_id]
                        
                        if target_type and target["node_type"] != target_type:
                            continue
                            
                        # Check target properties
                        props_match = True
                        
                        for key, value in target_properties.items():
                            if key not in target["data"] or target["data"][key] != value:
                                props_match = False
                                break
                        
                        if props_match:
                            has_relation = True
                            break
                    
                    if not has_relation:
                        match = False
                        break
                
                if match:
                    filtered.append(node)
                    
            candidates = filtered
        
        # Convert to results
        for node in candidates:
            results.append({
                "node_id": node["node_id"],
                "node_type": node["node_type"],
                "data": node["data"]
            })
        
        return results


# Example usage
if __name__ == "__main__":
    async def main():
        # Create an intent overlay agent
        agent = IntentOverlayAgent()
        
        # Register some knowledge nodes
        model_node = await agent.register_knowledge_node("model", {
            "name": "gpt-4",
            "type": "language_model",
            "capabilities": ["text_generation", "text_embedding"]
        })
        
        dataset_node = await agent.register_knowledge_node("dataset", {
            "name": "manufacturing_defects",
            "type": "tabular",
            "size": 10000
        })
        
        task_node = await agent.register_knowledge_node("task", {
            "name": "defect_classification",
            "type": "classification",
            "industry": "manufacturing"
        })
        
        # Connect nodes
        await agent.connect_knowledge_nodes(task_node, model_node, "uses_model")
        await agent.connect_knowledge_nodes(task_node, dataset_node, "uses_dataset")
        
        # Register semantic mappings
        await agent.register_semantic_mapping("classification", [task_node])
        await agent.register_semantic_mapping("manufacturing", [task_node, dataset_node])
        
        # Register an intent
        intent_id = await agent.register_intent("core-ai-ml-agent", "model_training", {
            "task": "defect_classification",
            "dataset": "manufacturing_defects",
            "parameters": {
                "epochs": 10,
                "batch_size": 32
            }
        })
        
        # Wait for processing
        await asyncio.sleep(1)
        
        # Get the intent
        intent = agent.get_intent(intent_id)
        
        print(f"Intent {intent_id} has {len(intent['knowledge_nodes'])} knowledge nodes")
        print(f"Intent context: {intent['context']}")
        
        # Query the knowledge graph
        results = await agent.query_knowledge_graph({
            "node_type": "task",
            "properties": {
                "industry": "manufacturing"
            }
        })
        
        print(f"Query results: {len(results)} nodes")
    
    asyncio.run(main())
