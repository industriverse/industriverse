"""
Tests for TTF Routing Engine

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import pytest
import asyncio
import numpy as np
from src.core_ai_layer.service_mesh.ttf.ttf_routing_engine import (
    TTFRoutingEngine,
    NodeMetrics,
    NodeStatus,
    JobSpec,
    RoutingDecision
)


@pytest.fixture
def routing_engine():
    """Create TTF routing engine"""
    return TTFRoutingEngine(alpha=0.3, beta=0.3, gamma=0.2, delta=0.2)


@pytest.fixture
def sample_nodes():
    """Create sample nodes"""
    return [
        NodeMetrics(
            node_id="node1",
            reputation=0.9,
            estimated_runtime=10.0,
            credit_cost=5.0,
            energy_affinity=0.8,
            status=NodeStatus.AVAILABLE
        ),
        NodeMetrics(
            node_id="node2",
            reputation=0.7,
            estimated_runtime=20.0,
            credit_cost=3.0,
            energy_affinity=0.6,
            status=NodeStatus.AVAILABLE
        ),
        NodeMetrics(
            node_id="node3",
            reputation=0.95,
            estimated_runtime=5.0,
            credit_cost=10.0,
            energy_affinity=0.9,
            status=NodeStatus.AVAILABLE
        )
    ]


@pytest.fixture
def sample_job():
    """Create sample job"""
    return JobSpec(
        job_id="job1",
        job_type="simulation",
        energy_map_utid="UTID:energy:map:abc123",
        required_capabilities=["gpu", "high_memory"],
        priority=1,
        max_runtime=100.0,
        max_cost=50.0
    )


def test_routing_engine_initialization():
    """Test routing engine initialization"""
    engine = TTFRoutingEngine(alpha=0.3, beta=0.3, gamma=0.2, delta=0.2)
    
    assert engine.alpha == 0.3
    assert engine.beta == 0.3
    assert engine.gamma == 0.2
    assert engine.delta == 0.2
    assert len(engine.nodes) == 0
    assert len(engine.tunnels) == 0


def test_routing_engine_invalid_weights():
    """Test routing engine with invalid weights"""
    with pytest.raises(ValueError):
        TTFRoutingEngine(alpha=0.5, beta=0.5, gamma=0.5, delta=0.5)


def test_register_node(routing_engine, sample_nodes):
    """Test node registration"""
    node = sample_nodes[0]
    routing_engine.register_node(node)
    
    assert node.node_id in routing_engine.nodes
    assert routing_engine.nodes[node.node_id] == node


def test_unregister_node(routing_engine, sample_nodes):
    """Test node unregistration"""
    node = sample_nodes[0]
    routing_engine.register_node(node)
    routing_engine.unregister_node(node.node_id)
    
    assert node.node_id not in routing_engine.nodes


def test_update_node_metrics(routing_engine, sample_nodes):
    """Test updating node metrics"""
    node = sample_nodes[0]
    routing_engine.register_node(node)
    
    routing_engine.update_node_metrics(
        node.node_id,
        reputation=0.95,
        estimated_runtime=8.0
    )
    
    updated_node = routing_engine.nodes[node.node_id]
    assert updated_node.reputation == 0.95
    assert updated_node.estimated_runtime == 8.0


def test_update_energy_cache(routing_engine, sample_nodes):
    """Test updating energy cache"""
    node = sample_nodes[0]
    routing_engine.register_node(node)
    
    utid = "UTID:energy:map:abc123"
    routing_engine.update_energy_cache(node.node_id, utid)
    
    assert utid in routing_engine.energy_cache[node.node_id]


def test_calculate_routing_score(routing_engine, sample_nodes, sample_job):
    """Test routing score calculation"""
    node = sample_nodes[0]
    routing_engine.register_node(node)
    
    score = routing_engine.calculate_routing_score(node, sample_job)
    
    assert 0.0 <= score <= 1.0
    assert isinstance(score, float)


def test_calculate_routing_score_with_energy_affinity(routing_engine, sample_nodes, sample_job):
    """Test routing score with energy affinity"""
    node = sample_nodes[0]
    routing_engine.register_node(node)
    
    # Add energy map to cache
    routing_engine.update_energy_cache(node.node_id, sample_job.energy_map_utid)
    
    score_with_cache = routing_engine.calculate_routing_score(node, sample_job)
    
    # Remove from cache
    routing_engine.energy_cache[node.node_id].clear()
    
    score_without_cache = routing_engine.calculate_routing_score(node, sample_job)
    
    # Score with cache should be higher
    assert score_with_cache > score_without_cache


def test_select_node(routing_engine, sample_nodes, sample_job):
    """Test node selection"""
    for node in sample_nodes:
        routing_engine.register_node(node)
    
    decision = routing_engine.select_node(sample_job)
    
    assert decision is not None
    assert isinstance(decision, RoutingDecision)
    assert decision.job_id == sample_job.job_id
    assert decision.selected_node in [n.node_id for n in sample_nodes]
    assert 0.0 <= decision.routing_score <= 1.0


def test_select_node_no_available_nodes(routing_engine, sample_job):
    """Test node selection with no available nodes"""
    decision = routing_engine.select_node(sample_job)
    
    assert decision is None


def test_select_node_prefers_best_score(routing_engine, sample_nodes, sample_job):
    """Test that node selection prefers highest score"""
    # Register nodes
    for node in sample_nodes:
        routing_engine.register_node(node)
    
    # Calculate scores manually
    scores = []
    for node in sample_nodes:
        score = routing_engine.calculate_routing_score(node, sample_job)
        scores.append((node.node_id, score))
    
    # Find best node
    best_node_id = max(scores, key=lambda x: x[1])[0]
    
    # Select node
    decision = routing_engine.select_node(sample_job)
    
    # Should select best node
    assert decision.selected_node == best_node_id


@pytest.mark.asyncio
async def test_open_tunnel(routing_engine):
    """Test opening tunnel"""
    tunnel_id = await routing_engine.open_tunnel("node1", "node2", "job1")
    
    assert tunnel_id in routing_engine.tunnels
    tunnel = routing_engine.tunnels[tunnel_id]
    assert tunnel.source_node == "node1"
    assert tunnel.target_node == "node2"
    assert tunnel.job_id == "job1"
    assert tunnel.status == "active"


@pytest.mark.asyncio
async def test_close_tunnel(routing_engine):
    """Test closing tunnel"""
    tunnel_id = await routing_engine.open_tunnel("node1", "node2", "job1")
    await routing_engine.close_tunnel(tunnel_id)
    
    tunnel = routing_engine.tunnels[tunnel_id]
    assert tunnel.status == "closed"


@pytest.mark.asyncio
async def test_tunnel_and_execute(routing_engine, sample_nodes, sample_job):
    """Test complete tunnel and execute workflow"""
    for node in sample_nodes:
        routing_engine.register_node(node)
    
    result = await routing_engine.tunnel_and_execute(sample_job)
    
    assert result["status"] == "success"
    assert result["job_id"] == sample_job.job_id
    assert "node" in result
    assert "tunnel_id" in result
    assert result["tunnel_id"] in routing_engine.tunnels


@pytest.mark.asyncio
async def test_tunnel_and_execute_no_nodes(routing_engine, sample_job):
    """Test tunnel and execute with no available nodes"""
    result = await routing_engine.tunnel_and_execute(sample_job)
    
    assert result["status"] == "failed"
    assert result["reason"] == "No available nodes"


def test_get_node_statistics(routing_engine, sample_nodes):
    """Test getting node statistics"""
    for node in sample_nodes:
        routing_engine.register_node(node)
    
    stats = routing_engine.get_node_statistics()
    
    assert stats["total_nodes"] == 3
    assert stats["available_nodes"] == 3
    assert stats["busy_nodes"] == 0
    assert stats["offline_nodes"] == 0
    assert 0.0 <= stats["avg_reputation"] <= 1.0


def test_get_routing_statistics(routing_engine, sample_nodes, sample_job):
    """Test getting routing statistics"""
    for node in sample_nodes:
        routing_engine.register_node(node)
    
    # Perform some routings
    for i in range(5):
        job = JobSpec(
            job_id=f"job{i}",
            job_type="simulation",
            priority=1
        )
        routing_engine.select_node(job)
    
    stats = routing_engine.get_routing_statistics()
    
    assert stats["total_routings"] == 5
    assert 0.0 <= stats["avg_score"] <= 1.0
    assert stats["avg_runtime"] > 0
    assert stats["avg_cost"] > 0


@pytest.mark.asyncio
async def test_get_tunnel_statistics(routing_engine):
    """Test getting tunnel statistics"""
    # Open some tunnels
    await routing_engine.open_tunnel("node1", "node2", "job1")
    await routing_engine.open_tunnel("node2", "node3", "job2")
    
    stats = routing_engine.get_tunnel_statistics()
    
    assert stats["total_tunnels"] == 2
    assert stats["active_tunnels"] == 2
    assert stats["closed_tunnels"] == 0


def test_routing_score_components(routing_engine, sample_nodes, sample_job):
    """Test that routing score includes all components"""
    node = sample_nodes[0]
    routing_engine.register_node(node)
    
    # Test with perfect scores
    node.reputation = 1.0
    node.estimated_runtime = 1.0
    node.credit_cost = 1.0
    node.energy_affinity = 1.0
    
    score = routing_engine.calculate_routing_score(node, sample_job)
    
    # Score should be high with perfect metrics
    assert score > 0.8


def test_routing_history_tracking(routing_engine, sample_nodes, sample_job):
    """Test that routing history is tracked"""
    for node in sample_nodes:
        routing_engine.register_node(node)
    
    initial_count = len(routing_engine.routing_history)
    
    routing_engine.select_node(sample_job)
    
    assert len(routing_engine.routing_history) == initial_count + 1
    assert routing_engine.routing_history[-1].job_id == sample_job.job_id


def test_node_status_filtering(routing_engine, sample_nodes, sample_job):
    """Test that only available nodes are selected"""
    # Register nodes with different statuses
    sample_nodes[0].status = NodeStatus.AVAILABLE
    sample_nodes[1].status = NodeStatus.BUSY
    sample_nodes[2].status = NodeStatus.OFFLINE
    
    for node in sample_nodes:
        routing_engine.register_node(node)
    
    decision = routing_engine.select_node(sample_job)
    
    # Should only select available node
    assert decision.selected_node == "node1"
