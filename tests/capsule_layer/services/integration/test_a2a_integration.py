"""
Test A2A (Agent-to-Agent) Integration

Validates agent discovery, orchestration, and MCP+A2A vertical integration.
"""

import pytest
from src.capsule_layer.services.a2a_agent_integration import (
    create_host_agent,
    get_agent_registry,
    AgentStatus,
    THERMAL_SAMPLER_AGENT_CARD,
    WORLD_MODEL_AGENT_CARD,
    MICROADAPT_EDGE_AGENT_CARD,
    SIMULATED_SNAPSHOT_AGENT_CARD
)

def test_agent_registry():
    """Test agent registry initialization"""
    registry = get_agent_registry()
    
    # Should have 4 agents
    agents = registry.list_agents()
    assert len(agents) == 4, f"Expected 4 agents, got {len(agents)}"
    
    # Check agent IDs
    agent_ids = {agent.agent_id for agent in agents}
    expected_ids = {
        "thermal_sampler_agent",
        "world_model_agent",
        "microadapt_edge_agent",
        "simulated_snapshot_agent"
    }
    assert agent_ids == expected_ids, f"Agent IDs mismatch: {agent_ids}"
    
    print("✅ Agent registry has all 4 thermodynamic agents")

def test_agent_discovery():
    """Test agent discovery by ID"""
    registry = get_agent_registry()
    
    # Get thermal sampler agent
    agent = registry.get_agent("thermal_sampler")
    assert agent is not None, "Thermal sampler agent not found"
    assert agent.agent_id == "thermal_sampler_agent"
    assert agent.name == "Thermal Sampler Agent"
    assert len(agent.capabilities) == 2, "Should have 2 capabilities"
    
    print("✅ Agent discovery working")

def test_agent_capabilities():
    """Test agent capability definitions"""
    # Check thermal sampler capabilities
    assert len(THERMAL_SAMPLER_AGENT_CARD.capabilities) == 2
    skills = {cap.skill for cap in THERMAL_SAMPLER_AGENT_CARD.capabilities}
    assert "thermal_optimization" in skills
    assert "energy_landscape_creation" in skills
    
    # Check world model capabilities
    assert len(WORLD_MODEL_AGENT_CARD.capabilities) == 2
    skills = {cap.skill for cap in WORLD_MODEL_AGENT_CARD.capabilities}
    assert "physics_simulation" in skills
    assert "multi_step_rollout" in skills
    
    # Check microadapt capabilities
    assert len(MICROADAPT_EDGE_AGENT_CARD.capabilities) == 2
    skills = {cap.skill for cap in MICROADAPT_EDGE_AGENT_CARD.capabilities}
    assert "adaptive_update" in skills
    assert "adaptive_forecast" in skills
    
    # Check snapshot capabilities
    assert len(SIMULATED_SNAPSHOT_AGENT_CARD.capabilities) == 2
    skills = {cap.skill for cap in SIMULATED_SNAPSHOT_AGENT_CARD.capabilities}
    assert "snapshot_storage" in skills
    assert "simulator_calibration" in skills
    
    print("✅ All agent capabilities defined correctly")

def test_find_agents_by_skill():
    """Test finding agents by skill"""
    registry = get_agent_registry()
    
    # Find thermal optimization agents
    agents = registry.find_agents_by_skill("thermal_optimization")
    assert len(agents) == 1
    assert agents[0].agent_id == "thermal_sampler_agent"
    
    # Find physics simulation agents
    agents = registry.find_agents_by_skill("physics_simulation")
    assert len(agents) == 1
    assert agents[0].agent_id == "world_model_agent"
    
    # Find adaptive forecast agents
    agents = registry.find_agents_by_skill("adaptive_forecast")
    assert len(agents) == 1
    assert agents[0].agent_id == "microadapt_edge_agent"
    
    print("✅ Skill-based agent discovery working")

def test_mcp_enabled():
    """Test that all agents have MCP enabled"""
    registry = get_agent_registry()
    agents = registry.list_agents()
    
    for agent in agents:
        assert agent.mcp_endpoint is not None, f"{agent.name} missing MCP endpoint"
        for capability in agent.capabilities:
            assert capability.mcp_enabled, f"{capability.skill} not MCP-enabled"
    
    print("✅ All agents MCP-enabled")

@pytest.mark.asyncio
async def test_host_agent_orchestration():
    """Test host agent workflow orchestration"""
    host_agent = create_host_agent()
    
    # Test workflow orchestration
    result = await host_agent.orchestrate_workflow(
        workflow_description="Optimize fab layout using thermal sampling",
        input_data={"fab_id": "fab_123"},
        mcp_context={"energy_budget": 1000}
    )
    
    assert "workflow" in result
    assert "available_agents" in result
    assert result["available_agents"] == 4
    assert result["mcp_enabled"] is True
    assert result["orchestration_ready"] is True
    
    print("✅ Host agent orchestration working")

def test_agent_discovery_by_host():
    """Test agent discovery through host agent"""
    host_agent = create_host_agent()
    
    # Discover all agents
    agents = host_agent.discover_agents()
    assert len(agents) == 4
    
    # Discover by skill
    thermal_agents = host_agent.discover_agents(skill="thermal_optimization")
    assert len(thermal_agents) == 1
    assert thermal_agents[0].agent_id == "thermal_sampler_agent"
    
    print("✅ Host agent discovery working")

def test_agent_metadata():
    """Test agent metadata for edge/real-time capabilities"""
    # Thermal sampler metadata
    assert THERMAL_SAMPLER_AGENT_CARD.metadata["edge_compatible"] is True
    assert THERMAL_SAMPLER_AGENT_CARD.metadata["real_time"] is True
    
    # World model metadata
    assert WORLD_MODEL_AGENT_CARD.metadata["jax_accelerated"] is True
    
    # MicroAdapt metadata
    assert MICROADAPT_EDGE_AGENT_CARD.metadata["edge_native"] is True
    assert MICROADAPT_EDGE_AGENT_CARD.metadata["raspberry_pi_validated"] is True
    assert MICROADAPT_EDGE_AGENT_CARD.metadata["time_complexity"] == "O(1)"
    
    # Snapshot metadata
    assert SIMULATED_SNAPSHOT_AGENT_CARD.metadata["energy_atlas_integrated"] is True
    assert SIMULATED_SNAPSHOT_AGENT_CARD.metadata["blockchain_anchored"] is True
    
    print("✅ Agent metadata complete")

if __name__ == "__main__":
    print("Testing A2A Integration...")
    
    test_agent_registry()
    test_agent_discovery()
    test_agent_capabilities()
    test_find_agents_by_skill()
    test_mcp_enabled()
    test_agent_discovery_by_host()
    test_agent_metadata()
    
    # Async test
    import asyncio
    asyncio.run(test_host_agent_orchestration())
    
    print("\n✅ All A2A integration tests passed!")
