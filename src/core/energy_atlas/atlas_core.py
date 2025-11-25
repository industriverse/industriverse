import logging
from typing import Dict, List, Optional, Any
import numpy as np
import os
from datetime import datetime
from .hardware_schema import HardwareNode
from .hardware_loader import HardwareLoader

# Mock Neo4j driver for development without live DB
class MockNeo4jDriver:
    def __init__(self, uri, auth):
        self.uri = uri
        self.nodes = {}
        self.relationships = []
        logging.info(f"Initialized MockNeo4jDriver for {uri}")

    def close(self):
        pass

    def verify_connectivity(self):
        return True
        
    def session(self):
        return MockSession(self)

class MockSession:
    def __init__(self, driver):
        self.driver = driver
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_value, traceback):
        pass
        
    def run(self, query, **kwargs):
        # Simple mock query handler
        logging.debug(f"Mock Cypher: {query} | Params: {kwargs}")
        if "MERGE (n:HardwareNode" in query:
            node_id = kwargs.get("node_id")
            if node_id:
                self.driver.nodes[node_id] = kwargs
        return MockResult()

class MockResult:
    def single(self):
        return None
    def consume(self):
        return None

class EnergyAtlas:
    """
    The Energy Atlas manages the "Energy Maps" overlaying the physical hardware.
    It persists node relationships and energy states to Neo4j.
    """
    
    def __init__(self, neo4j_uri: str = "bolt://localhost:7687", neo4j_auth: tuple = ("neo4j", "password"), use_mock: bool = True):
        self.loader = HardwareLoader()
        self.nodes: Dict[str, HardwareNode] = {}
        self.energy_maps: Dict[str, Any] = {} # Registry for loaded physics maps
        
        if use_mock:
            self.driver = MockNeo4jDriver(neo4j_uri, neo4j_auth)
        else:
            try:
                from neo4j import GraphDatabase
                self.driver = GraphDatabase.driver(neo4j_uri, auth=neo4j_auth)
            except ImportError:
                logging.warning("neo4j module not found, falling back to mock driver")
                self.driver = MockNeo4jDriver(neo4j_uri, neo4j_auth)

    def load_manifest(self, manifest_path: str):
        """
        Load hardware nodes from a manifest and sync to Neo4j.
        """
        new_nodes = self.loader.load_manifest(manifest_path)
        for node in new_nodes:
            self.nodes[node.node_id] = node
            self._sync_node_to_graph(node)
            
    def _sync_node_to_graph(self, node: HardwareNode):
        """
        Persist hardware node to Neo4j.
        """
        query = """
        MERGE (n:HardwareNode {id: $node_id})
        SET n.type = $node_type,
            n.c_gate = $c_gate,
            n.c_wire = $c_wire,
            n.v_min = $v_min,
            n.v_max = $v_max,
            n.updated_at = $timestamp
        """
        params = {
            "node_id": node.node_id,
            "node_type": node.node_type,
            "c_gate": node.electrical.capacitance_gate,
            "c_wire": node.electrical.capacitance_wire,
            "v_min": node.electrical.voltage_min,
            "v_max": node.electrical.voltage_max,
            "timestamp": datetime.now().isoformat()
        }
        
        with self.driver.session() as session:
            session.run(query, **params)
            
    def get_energy_map(self) -> Dict[str, Any]:
        """
        Return the current energy map (all nodes and their static properties).
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "node_count": len(self.nodes),
            "nodes": {nid: node.dict() for nid, node in self.nodes.items()}
        }

    def close(self):
        self.driver.close()
