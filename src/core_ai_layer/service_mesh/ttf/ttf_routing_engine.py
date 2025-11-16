"""
TTF (Thermodynamic Tunneling Fabric) - Routing Engine
Energy-aware routing and execution fabric for Industriverse

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import asyncio
import time
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class NodeStatus(Enum):
    """Node status enumeration"""
    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


@dataclass
class NodeMetrics:
    """Metrics for a compute node"""
    node_id: str
    reputation: float  # 0-1 score based on past performance
    estimated_runtime: float  # seconds
    credit_cost: float  # cost in credits
    energy_affinity: float  # 0-1 score for energy map locality
    cpu_utilization: float = 0.0
    memory_utilization: float = 0.0
    energy_state: float = 0.0  # Current energy state (J)
    energy_rate: float = 0.0  # dE/dt (W)
    status: NodeStatus = NodeStatus.AVAILABLE
    last_updated: float = field(default_factory=time.time)


@dataclass
class JobSpec:
    """Job specification for routing"""
    job_id: str
    job_type: str
    energy_map_utid: Optional[str] = None
    required_capabilities: List[str] = field(default_factory=list)
    priority: int = 1
    max_runtime: float = 300.0  # seconds
    max_cost: float = 100.0  # credits


@dataclass
class RoutingDecision:
    """Routing decision result"""
    job_id: str
    selected_node: str
    routing_score: float
    estimated_runtime: float
    estimated_cost: float
    energy_affinity: float
    timestamp: float = field(default_factory=time.time)


@dataclass
class TunnelConnection:
    """Active tunnel connection"""
    tunnel_id: str
    source_node: str
    target_node: str
    job_id: str
    established_at: float
    energy_transferred: float = 0.0
    data_transferred: int = 0  # bytes
    status: str = "active"


class TTFRoutingEngine:
    """
    Thermodynamic Tunneling Fabric Routing Engine
    
    Routes jobs to optimal nodes based on:
    - Reputation (30%)
    - Runtime efficiency (30%)
    - Credit cost (20%)
    - Energy affinity (20%)
    """
    
    def __init__(
        self,
        alpha: float = 0.3,  # Reputation weight
        beta: float = 0.3,   # Runtime weight
        gamma: float = 0.2,  # Cost weight
        delta: float = 0.2   # Energy affinity weight
    ):
        """
        Initialize TTF Routing Engine
        
        Args:
            alpha: Weight for reputation
            beta: Weight for runtime efficiency
            gamma: Weight for cost efficiency
            delta: Weight for energy affinity
        """
        # Validate weights sum to 1.0
        total_weight = alpha + beta + gamma + delta
        if not np.isclose(total_weight, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {total_weight}")
        
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        
        # Node registry
        self.nodes: Dict[str, NodeMetrics] = {}
        
        # Active tunnels
        self.tunnels: Dict[str, TunnelConnection] = {}
        
        # Energy map cache (node_id -> set of energy_map_utids)
        self.energy_cache: Dict[str, set] = {}
        
        # Routing history
        self.routing_history: List[RoutingDecision] = []
        
        print(f"✅ TTF Routing Engine initialized")
        print(f"  Weights: α={alpha}, β={beta}, γ={gamma}, δ={delta}")
    
    def register_node(self, node: NodeMetrics):
        """Register a compute node"""
        self.nodes[node.node_id] = node
        if node.node_id not in self.energy_cache:
            self.energy_cache[node.node_id] = set()
        print(f"✅ Registered node: {node.node_id}")
    
    def unregister_node(self, node_id: str):
        """Unregister a compute node"""
        if node_id in self.nodes:
            del self.nodes[node_id]
            print(f"❌ Unregistered node: {node_id}")
    
    def update_node_metrics(self, node_id: str, **kwargs):
        """Update node metrics"""
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not registered")
        
        node = self.nodes[node_id]
        for key, value in kwargs.items():
            if hasattr(node, key):
                setattr(node, key, value)
        node.last_updated = time.time()
    
    def update_energy_cache(self, node_id: str, energy_map_utid: str):
        """Update energy map cache for a node"""
        if node_id not in self.energy_cache:
            self.energy_cache[node_id] = set()
        self.energy_cache[node_id].add(energy_map_utid)
    
    def calculate_routing_score(self, node: NodeMetrics, job: JobSpec) -> float:
        """
        Calculate routing score for a node-job pair
        
        Score = α·reputation + β·(1/runtime) + γ·(1/cost) + δ·energy_affinity
        
        Args:
            node: Node metrics
            job: Job specification
            
        Returns:
            Routing score (0-1, higher is better)
        """
        # Reputation component (already 0-1)
        reputation_score = node.reputation
        
        # Runtime efficiency (normalize inverse runtime)
        # Assume max runtime is 1000s for normalization
        runtime_score = 1.0 / (1.0 + node.estimated_runtime / 1000.0)
        
        # Cost efficiency (normalize inverse cost)
        # Assume max cost is 1000 credits for normalization
        cost_score = 1.0 / (1.0 + node.credit_cost / 1000.0)
        
        # Energy affinity (check if node has energy map cached)
        energy_affinity_score = node.energy_affinity
        if job.energy_map_utid and node.node_id in self.energy_cache:
            if job.energy_map_utid in self.energy_cache[node.node_id]:
                energy_affinity_score = 1.0  # Perfect affinity
        
        # Weighted sum
        score = (
            self.alpha * reputation_score +
            self.beta * runtime_score +
            self.gamma * cost_score +
            self.delta * energy_affinity_score
        )
        
        return score
    
    def select_node(self, job: JobSpec) -> Optional[RoutingDecision]:
        """
        Select optimal node for job execution
        
        Args:
            job: Job specification
            
        Returns:
            Routing decision or None if no suitable node
        """
        # Filter available nodes
        available_nodes = [
            node for node in self.nodes.values()
            if node.status == NodeStatus.AVAILABLE
        ]
        
        if not available_nodes:
            print(f"⚠️  No available nodes for job {job.job_id}")
            return None
        
        # Calculate scores for all nodes
        scores = []
        for node in available_nodes:
            score = self.calculate_routing_score(node, job)
            scores.append((node, score))
        
        # Sort by score (descending)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select best node
        best_node, best_score = scores[0]
        
        # Create routing decision
        decision = RoutingDecision(
            job_id=job.job_id,
            selected_node=best_node.node_id,
            routing_score=best_score,
            estimated_runtime=best_node.estimated_runtime,
            estimated_cost=best_node.credit_cost,
            energy_affinity=best_node.energy_affinity
        )
        
        # Record decision
        self.routing_history.append(decision)
        
        print(f"✅ Routed job {job.job_id} to node {best_node.node_id} (score: {best_score:.3f})")
        
        return decision
    
    async def open_tunnel(
        self,
        source_node: str,
        target_node: str,
        job_id: str
    ) -> str:
        """
        Open a tunnel connection between nodes
        
        Args:
            source_node: Source node ID
            target_node: Target node ID
            job_id: Job ID
            
        Returns:
            Tunnel ID
        """
        tunnel_id = f"tunnel_{source_node}_{target_node}_{int(time.time())}"
        
        tunnel = TunnelConnection(
            tunnel_id=tunnel_id,
            source_node=source_node,
            target_node=target_node,
            job_id=job_id,
            established_at=time.time()
        )
        
        self.tunnels[tunnel_id] = tunnel
        
        print(f"🔗 Opened tunnel: {tunnel_id}")
        
        return tunnel_id
    
    async def close_tunnel(self, tunnel_id: str):
        """Close a tunnel connection"""
        if tunnel_id in self.tunnels:
            tunnel = self.tunnels[tunnel_id]
            tunnel.status = "closed"
            print(f"🔒 Closed tunnel: {tunnel_id}")
            print(f"  Energy transferred: {tunnel.energy_transferred:.2f} J")
            print(f"  Data transferred: {tunnel.data_transferred} bytes")
    
    async def tunnel_and_execute(
        self,
        job: JobSpec,
        source_node: str = "local"
    ) -> Dict:
        """
        Complete tunnel and execute workflow
        
        Args:
            job: Job specification
            source_node: Source node ID
            
        Returns:
            Execution result
        """
        # Select target node
        decision = self.select_node(job)
        if not decision:
            return {
                "status": "failed",
                "reason": "No available nodes",
                "job_id": job.job_id
            }
        
        target_node = decision.selected_node
        
        # Open tunnel
        tunnel_id = await self.open_tunnel(source_node, target_node, job.job_id)
        
        # Simulate job execution
        await asyncio.sleep(0.1)  # Simulate network latency
        
        # Update tunnel metrics
        tunnel = self.tunnels[tunnel_id]
        tunnel.energy_transferred = decision.estimated_runtime * 0.5  # Simulated
        tunnel.data_transferred = 1024 * 1024  # 1 MB simulated
        
        # Close tunnel
        await self.close_tunnel(tunnel_id)
        
        return {
            "status": "success",
            "job_id": job.job_id,
            "node": target_node,
            "tunnel_id": tunnel_id,
            "runtime": decision.estimated_runtime,
            "cost": decision.estimated_cost,
            "energy_transferred": tunnel.energy_transferred
        }
    
    def get_node_statistics(self) -> Dict:
        """Get node statistics"""
        total_nodes = len(self.nodes)
        available_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.AVAILABLE)
        busy_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.BUSY)
        offline_nodes = sum(1 for n in self.nodes.values() if n.status == NodeStatus.OFFLINE)
        
        avg_reputation = np.mean([n.reputation for n in self.nodes.values()]) if self.nodes else 0.0
        avg_energy_state = np.mean([n.energy_state for n in self.nodes.values()]) if self.nodes else 0.0
        
        return {
            "total_nodes": total_nodes,
            "available_nodes": available_nodes,
            "busy_nodes": busy_nodes,
            "offline_nodes": offline_nodes,
            "avg_reputation": avg_reputation,
            "avg_energy_state": avg_energy_state
        }
    
    def get_routing_statistics(self) -> Dict:
        """Get routing statistics"""
        if not self.routing_history:
            return {
                "total_routings": 0,
                "avg_score": 0.0,
                "avg_runtime": 0.0,
                "avg_cost": 0.0,
                "avg_energy_affinity": 0.0
            }
        
        return {
            "total_routings": len(self.routing_history),
            "avg_score": np.mean([d.routing_score for d in self.routing_history]),
            "avg_runtime": np.mean([d.estimated_runtime for d in self.routing_history]),
            "avg_cost": np.mean([d.estimated_cost for d in self.routing_history]),
            "avg_energy_affinity": np.mean([d.energy_affinity for d in self.routing_history])
        }
    
    def get_tunnel_statistics(self) -> Dict:
        """Get tunnel statistics"""
        active_tunnels = sum(1 for t in self.tunnels.values() if t.status == "active")
        closed_tunnels = sum(1 for t in self.tunnels.values() if t.status == "closed")
        
        total_energy = sum(t.energy_transferred for t in self.tunnels.values())
        total_data = sum(t.data_transferred for t in self.tunnels.values())
        
        return {
            "total_tunnels": len(self.tunnels),
            "active_tunnels": active_tunnels,
            "closed_tunnels": closed_tunnels,
            "total_energy_transferred": total_energy,
            "total_data_transferred": total_data
        }
