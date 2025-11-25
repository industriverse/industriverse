"""
Shadow Twin Backend

Real-time 3D knowledge graph visualization engine.
Powers the Shadow Twin 3D widget with WebSocket streaming updates.

Provides:
- Force-directed graph layout computation
- Real-time node and edge updates
- Spatial clustering of related concepts
- Multi-layer visualization (papers, insights, concepts)
- Interactive drill-down navigation
- VR/AR-ready 3D coordinates
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from collections import defaultdict
import json
from enum import Enum


class NodeType(Enum):
    """Types of nodes in Shadow Twin"""
    PAPER = "paper"
    INSIGHT = "insight"
    CONCEPT = "concept"
    AUTHOR = "author"
    CLUSTER = "cluster"


class EdgeType(Enum):
    """Types of edges in Shadow Twin"""
    CITES = "cites"
    CITED_BY = "cited_by"
    RELATED = "related"
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    AUTHORS = "authors"
    CONTAINS = "contains"


@dataclass
class Node:
    """Shadow Twin graph node"""
    node_id: str
    node_type: str
    label: str

    # 3D position
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    # Physics
    vx: float = 0.0  # Velocity
    vy: float = 0.0
    vz: float = 0.0
    mass: float = 1.0  # Node importance

    # Visual properties
    color: str = "#FF6B35"
    size: float = 1.0
    opacity: float = 1.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    connected_nodes: Set[str] = field(default_factory=set)

    # State
    fixed: bool = False  # Whether position is locked
    highlighted: bool = False
    selected: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            'node_id': self.node_id,
            'node_type': self.node_type,
            'label': self.label,
            'position': {'x': self.x, 'y': self.y, 'z': self.z},
            'velocity': {'vx': self.vx, 'vy': self.vy, 'vz': self.vz},
            'mass': self.mass,
            'visual': {
                'color': self.color,
                'size': self.size,
                'opacity': self.opacity,
            },
            'metadata': self.metadata,
            'connected_count': len(self.connected_nodes),
            'fixed': self.fixed,
            'highlighted': self.highlighted,
            'selected': self.selected,
        }


@dataclass
class Edge:
    """Shadow Twin graph edge"""
    edge_id: str
    source: str
    target: str
    edge_type: str

    # Visual properties
    color: str = "#8B949E"
    width: float = 1.0
    opacity: float = 0.6

    # Weight (for force computation)
    weight: float = 1.0

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'edge_id': self.edge_id,
            'source': self.source,
            'target': self.target,
            'edge_type': self.edge_type,
            'visual': {
                'color': self.color,
                'width': self.width,
                'opacity': self.opacity,
            },
            'weight': self.weight,
            'metadata': self.metadata,
        }


class ShadowTwinBackend:
    """
    Shadow Twin 3D Knowledge Graph Backend

    Implements:
    - Force-directed graph layout (3D)
    - Real-time physics simulation
    - Spatial clustering
    - Multi-layer visualization
    - Interactive updates via WebSocket
    """

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.edges: Dict[str, Edge] = {}

        # Physics parameters
        self.repulsion_strength = 100.0
        self.attraction_strength = 0.1
        self.damping = 0.95
        self.time_step = 0.016  # ~60 FPS

        # Clustering
        self.clusters: Dict[str, Set[str]] = defaultdict(set)

        # Layers (for multi-layer visualization)
        self.layers: Dict[str, Set[str]] = {
            'papers': set(),
            'insights': set(),
            'concepts': set(),
            'authors': set(),
        }

        # Simulation state
        self.simulation_running = False
        self.iteration_count = 0

    def add_node(
        self,
        node_id: str,
        node_type: NodeType,
        label: str,
        metadata: Optional[Dict[str, Any]] = None,
        position: Optional[Tuple[float, float, float]] = None
    ) -> Node:
        """Add node to Shadow Twin"""

        # Assign color based on type
        colors = {
            NodeType.PAPER: "#4299E1",  # Blue
            NodeType.INSIGHT: "#9B59B6",  # Purple
            NodeType.CONCEPT: "#2ECC71",  # Green
            NodeType.AUTHOR: "#FF6B35",  # Orange
            NodeType.CLUSTER: "#E74C3C",  # Red
        }

        # Random initial position if not specified
        if position:
            x, y, z = position
        else:
            x = np.random.randn() * 10
            y = np.random.randn() * 10
            z = np.random.randn() * 10

        # Create node
        node = Node(
            node_id=node_id,
            node_type=node_type.value,
            label=label,
            x=x, y=y, z=z,
            color=colors.get(node_type, "#8B949E"),
            metadata=metadata or {}
        )

        self.nodes[node_id] = node

        # Add to layer
        layer_map = {
            NodeType.PAPER: 'papers',
            NodeType.INSIGHT: 'insights',
            NodeType.CONCEPT: 'concepts',
            NodeType.AUTHOR: 'authors',
        }
        if node_type in layer_map:
            self.layers[layer_map[node_type]].add(node_id)

        return node

    def add_edge(
        self,
        source: str,
        target: str,
        edge_type: EdgeType,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Edge:
        """Add edge to Shadow Twin"""

        edge_id = f"{source}-{target}-{edge_type.value}"

        # Color based on type
        colors = {
            EdgeType.CITES: "#8B949E",
            EdgeType.CITED_BY: "#8B949E",
            EdgeType.RELATED: "#4299E1",
            EdgeType.SUPPORTS: "#2ECC71",
            EdgeType.CONTRADICTS: "#E74C3C",
            EdgeType.AUTHORS: "#FF6B35",
            EdgeType.CONTAINS: "#9B59B6",
        }

        edge = Edge(
            edge_id=edge_id,
            source=source,
            target=target,
            edge_type=edge_type.value,
            weight=weight,
            color=colors.get(edge_type, "#8B949E"),
            metadata=metadata or {}
        )

        self.edges[edge_id] = edge

        # Update node connections
        if source in self.nodes:
            self.nodes[source].connected_nodes.add(target)
        if target in self.nodes:
            self.nodes[target].connected_nodes.add(source)

        return edge

    def run_physics_iteration(self):
        """Run one iteration of force-directed layout"""

        # Reset forces
        forces = {node_id: np.array([0.0, 0.0, 0.0]) for node_id in self.nodes}

        # 1. Repulsion forces (all pairs)
        node_ids = list(self.nodes.keys())
        for i, id1 in enumerate(node_ids):
            node1 = self.nodes[id1]
            if node1.fixed:
                continue

            for id2 in node_ids[i+1:]:
                node2 = self.nodes[id2]

                # Vector from node2 to node1
                dx = node1.x - node2.x
                dy = node1.y - node2.y
                dz = node1.z - node2.z

                distance = np.sqrt(dx*dx + dy*dy + dz*dz) + 0.01

                # Repulsion force (inverse square)
                force_magnitude = self.repulsion_strength / (distance * distance)

                force_x = (dx / distance) * force_magnitude
                force_y = (dy / distance) * force_magnitude
                force_z = (dz / distance) * force_magnitude

                forces[id1] += np.array([force_x, force_y, force_z])
                if not node2.fixed:
                    forces[id2] -= np.array([force_x, force_y, force_z])

        # 2. Attraction forces (edges)
        for edge in self.edges.values():
            if edge.source not in self.nodes or edge.target not in self.nodes:
                continue

            source_node = self.nodes[edge.source]
            target_node = self.nodes[edge.target]

            # Vector from source to target
            dx = target_node.x - source_node.x
            dy = target_node.y - source_node.y
            dz = target_node.z - source_node.z

            distance = np.sqrt(dx*dx + dy*dy + dz*dz) + 0.01

            # Hooke's law (spring force)
            force_magnitude = self.attraction_strength * distance * edge.weight

            force_x = (dx / distance) * force_magnitude
            force_y = (dy / distance) * force_magnitude
            force_z = (dz / distance) * force_magnitude

            if not source_node.fixed:
                forces[edge.source] += np.array([force_x, force_y, force_z])
            if not target_node.fixed:
                forces[edge.target] -= np.array([force_x, force_y, force_z])

        # 3. Update velocities and positions
        for node_id, force in forces.items():
            node = self.nodes[node_id]
            if node.fixed:
                continue

            # Update velocity
            acceleration = force / node.mass
            node.vx += acceleration[0] * self.time_step
            node.vy += acceleration[1] * self.time_step
            node.vz += acceleration[2] * self.time_step

            # Apply damping
            node.vx *= self.damping
            node.vy *= self.damping
            node.vz *= self.damping

            # Update position
            node.x += node.vx * self.time_step
            node.y += node.vy * self.time_step
            node.z += node.vz * self.time_step

        self.iteration_count += 1

    def run_layout(self, iterations: int = 100):
        """Run physics simulation for N iterations"""
        self.simulation_running = True
        for _ in range(iterations):
            self.run_physics_iteration()
        self.simulation_running = False

    def detect_clusters(self, min_cluster_size: int = 3) -> Dict[str, Set[str]]:
        """
        Detect spatial clusters using DBSCAN-like approach

        Groups nodes that are spatially close in 3D space
        """
        clusters = {}
        visited = set()
        cluster_id = 0

        def get_neighbors(node_id: str, epsilon: float = 20.0) -> Set[str]:
            """Find all nodes within epsilon distance"""
            node = self.nodes[node_id]
            neighbors = set()

            for other_id, other_node in self.nodes.items():
                if other_id == node_id:
                    continue

                distance = np.sqrt(
                    (node.x - other_node.x)**2 +
                    (node.y - other_node.y)**2 +
                    (node.z - other_node.z)**2
                )

                if distance < epsilon:
                    neighbors.add(other_id)

            return neighbors

        # DBSCAN clustering
        for node_id in self.nodes:
            if node_id in visited:
                continue

            visited.add(node_id)
            neighbors = get_neighbors(node_id)

            if len(neighbors) < min_cluster_size:
                continue

            # Start new cluster
            cluster = {node_id}
            cluster_queue = list(neighbors)

            while cluster_queue:
                current = cluster_queue.pop(0)
                if current in visited:
                    continue

                visited.add(current)
                cluster.add(current)

                current_neighbors = get_neighbors(current)
                if len(current_neighbors) >= min_cluster_size:
                    cluster_queue.extend(current_neighbors)

            if len(cluster) >= min_cluster_size:
                clusters[f"cluster-{cluster_id}"] = cluster
                cluster_id += 1

        self.clusters = clusters
        return clusters

    def get_subgraph(self, node_id: str, depth: int = 2) -> Dict[str, Any]:
        """Get subgraph around a node"""
        subgraph_nodes = set()
        subgraph_edges = set()
        queue = [(node_id, 0)]
        visited = set()

        while queue:
            current_id, current_depth = queue.pop(0)

            if current_id in visited or current_depth > depth:
                continue

            visited.add(current_id)
            subgraph_nodes.add(current_id)

            # Add connected nodes
            if current_id in self.nodes:
                node = self.nodes[current_id]
                for connected_id in node.connected_nodes:
                    if current_depth < depth:
                        queue.append((connected_id, current_depth + 1))

                    # Add edge
                    for edge in self.edges.values():
                        if (edge.source == current_id and edge.target == connected_id) or \
                           (edge.target == current_id and edge.source == connected_id):
                            subgraph_edges.add(edge.edge_id)

        return {
            'nodes': [self.nodes[nid].to_dict() for nid in subgraph_nodes if nid in self.nodes],
            'edges': [self.edges[eid].to_dict() for eid in subgraph_edges if eid in self.edges]
        }

    def highlight_path(self, source_id: str, target_id: str) -> List[str]:
        """Find and highlight shortest path between nodes"""
        # BFS for shortest path
        queue = [(source_id, [source_id])]
        visited = {source_id}

        while queue:
            current_id, path = queue.pop(0)

            if current_id == target_id:
                # Highlight path
                for node_id in path:
                    if node_id in self.nodes:
                        self.nodes[node_id].highlighted = True
                return path

            if current_id in self.nodes:
                for neighbor_id in self.nodes[current_id].connected_nodes:
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append((neighbor_id, path + [neighbor_id]))

        return []  # No path found

    def clear_highlights(self):
        """Clear all node highlights"""
        for node in self.nodes.values():
            node.highlighted = False
            node.selected = False

    def get_state(self) -> Dict[str, Any]:
        """Get full Shadow Twin state for client"""
        return {
            'nodes': [node.to_dict() for node in self.nodes.values()],
            'edges': [edge.to_dict() for edge in self.edges.values()],
            'clusters': {cid: list(nodes) for cid, nodes in self.clusters.items()},
            'layers': {layer: list(nodes) for layer, nodes in self.layers.items()},
            'iteration_count': self.iteration_count,
            'simulation_running': self.simulation_running,
            'stats': {
                'node_count': len(self.nodes),
                'edge_count': len(self.edges),
                'cluster_count': len(self.clusters),
            }
        }

    def get_layer_state(self, layer: str) -> Dict[str, Any]:
        """Get state for specific layer"""
        layer_node_ids = self.layers.get(layer, set())
        layer_nodes = [self.nodes[nid].to_dict() for nid in layer_node_ids if nid in self.nodes]

        # Get edges between layer nodes
        layer_edges = []
        for edge in self.edges.values():
            if edge.source in layer_node_ids and edge.target in layer_node_ids:
                layer_edges.append(edge.to_dict())

        return {
            'layer': layer,
            'nodes': layer_nodes,
            'edges': layer_edges,
            'node_count': len(layer_nodes),
            'edge_count': len(layer_edges),
        }

    def export_for_vr(self) -> Dict[str, Any]:
        """Export Shadow Twin in VR-optimized format"""
        return {
            'nodes': [
                {
                    'id': node.node_id,
                    'type': node.node_type,
                    'label': node.label,
                    'position': [node.x, node.y, node.z],
                    'color': node.color,
                    'size': node.size,
                }
                for node in self.nodes.values()
            ],
            'edges': [
                {
                    'source': edge.source,
                    'target': edge.target,
                    'type': edge.edge_type,
                    'color': edge.color,
                }
                for edge in self.edges.values()
            ]
        }


# Global Shadow Twin instance
_shadow_twin: Optional[ShadowTwinBackend] = None


def get_shadow_twin() -> ShadowTwinBackend:
    """Get or create global Shadow Twin backend"""
    global _shadow_twin
    if _shadow_twin is None:
        _shadow_twin = ShadowTwinBackend()
    return _shadow_twin
