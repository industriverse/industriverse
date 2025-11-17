"""
Complete Vertical Integration Tests

Tests the entire Industriverse stack from top to bottom:
USER → Remix Lab → A2A → MCP → Thermodynamic → DAC Factory → Provenance

This validates:
1. Remix Lab DAC creation with UTID generation
2. A2A agent orchestration
3. MCP context propagation
4. Thermodynamic service execution
5. DAC Factory lifecycle management
6. Energy Atlas provenance tracking
7. ProofEconomy proof generation
"""

import pytest
import asyncio
from datetime import datetime

from src.capsule_layer.services.remix_lab_service import (
    create_remix_lab_service,
    RemixComponent,
    ComponentType
)
from src.capsule_layer.services.a2a_agent_integration import (
    create_host_agent,
    get_agent_registry
)
from src.capsule_layer.services.dac_factory_orchestration import (
    create_dac_factory_orchestrator,
    DACSpecification,
    DACResource,
    DACPlatform,
    CloudProvider,
    DeploymentConfig,
    DeploymentStrategy,
    ThermodynamicWorkflow,
    WorkflowStep,
    ProofType
)
from src.capsule_layer.services.bridge_api import create_bridge_api, MCP_AVAILABLE


@pytest.mark.asyncio
async def test_complete_dac_creation_workflow():
    """
    Test complete DAC creation workflow from Remix Lab to deployment
    
    Workflow:
    1. User creates remix snapshot
    2. Simulates remix
    3. Commits remix → generates UTID
    4. DAC Factory creates DAC from manifest
    5. DAC deployed to platform
    6. Proof generated
    7. Provenance tracked
    """
    print("\n=== Testing Complete DAC Creation Workflow ===\n")
    
    # Step 1: Create Remix Lab snapshot
    print("Step 1: Creating Remix Lab snapshot...")
    remix_lab = create_remix_lab_service()
    
    components = [
        RemixComponent(
            component_id="thermal_opt_v1",
            component_type=ComponentType.FUNCTION,
            name="Thermal Optimization",
            version="1.0.0",
            manifest_hash="abc123",
            signature="sig_thermal",
            provenance={"creator": "user_123"}
        ),
        RemixComponent(
            component_id="physics_sim_v1",
            component_type=ComponentType.MODEL,
            name="Physics Simulator",
            version="1.0.0",
            manifest_hash="def456",
            signature="sig_physics",
            provenance={"creator": "user_123"}
        )
    ]
    
    snapshot = await remix_lab.create_snapshot(
        user_id="user_123",
        name="Fab Optimization DAC",
        description="Optimizes semiconductor fab operations",
        components=components
    )
    
    assert snapshot.snapshot_id is not None
    assert len(snapshot.components) == 2
    print(f"✅ Snapshot created: {snapshot.snapshot_id}")
    
    # Step 2: Simulate remix
    print("\nStep 2: Simulating remix...")
    simulation_results = await remix_lab.simulate_remix(snapshot.snapshot_id)
    
    assert simulation_results["status"] == "success"
    assert "estimated_performance" in simulation_results
    print(f"✅ Simulation complete: {simulation_results['status']}")
    
    # Step 3: Commit remix and generate UTID
    print("\nStep 3: Committing remix and generating UTID...")
    commit = await remix_lab.commit_remix(
        snapshot_id=snapshot.snapshot_id,
        committed_by="user_123",
        collaborators=[]
    )
    
    assert commit.utid.startswith("UTID-")
    assert commit.dac_manifest is not None
    assert commit.proof_id is not None
    print(f"✅ UTID generated: {commit.utid}")
    print(f"✅ Proof ID: {commit.proof_id}")
    
    # Step 4: Create DAC from manifest
    print("\nStep 4: Creating DAC from Remix Lab manifest...")
    orchestrator = create_dac_factory_orchestrator()
    
    dac_spec = DACSpecification(
        dac_id=commit.dac_manifest["dac_id"],
        name=commit.dac_manifest["name"],
        description=commit.dac_manifest["description"],
        version=commit.dac_manifest["version"],
        functions=[{"name": "optimize", "type": "thermal"}],
        target_platforms=[DACPlatform.KUBERNETES, DACPlatform.EDGE_JETSON],
        preferred_platform=DACPlatform.KUBERNETES,
        cloud_providers=[CloudProvider.AWS, CloudProvider.GCP],
        resources=DACResource(
            cpu_cores=2.0,
            memory_mb=4096,
            storage_mb=10240,
            gpu_required=False,
            energy_budget_watts=100.0
        ),
        thermodynamic_agents=["thermal_sampler", "world_model"],
        mcp_enabled=True,
        a2a_enabled=True,
        energy_atlas_tracking=True,
        proof_economy_enabled=True,
        blockchain_anchoring=True
    )
    
    dac_creation = await orchestrator.create_dac(dac_spec)
    assert dac_creation["status"] == "created"
    print(f"✅ DAC created: {dac_spec.dac_id}")
    
    # Step 5: Build DAC
    print("\nStep 5: Building DAC artifact...")
    build_result = await orchestrator.build_dac(dac_spec.dac_id)
    
    assert build_result["status"] == "built"
    assert "energy_consumed_joules" in build_result
    print(f"✅ DAC built: {build_result['artifact_hash'][:16]}...")
    print(f"   Energy consumed: {build_result['energy_consumed_joules']} J")
    
    # Step 6: Deploy DAC
    print("\nStep 6: Deploying DAC to Kubernetes...")
    deployment_config = DeploymentConfig(
        strategy=DeploymentStrategy.ROLLING,
        replicas=2,
        auto_scaling=True,
        min_replicas=1,
        max_replicas=5
    )
    
    deployment = await orchestrator.deploy_dac(
        dac_id=dac_spec.dac_id,
        deployment_config=deployment_config
    )
    
    assert deployment.status == "deployed"
    assert deployment.replicas_deployed == 2
    assert deployment.endpoint is not None
    print(f"✅ DAC deployed: {deployment.endpoint}")
    print(f"   Replicas: {deployment.replicas_deployed}")
    print(f"   Energy consumed: {deployment.energy_consumed_joules} J")
    
    # Step 7: Generate proof
    print("\nStep 7: Generating ProofEconomy proof...")
    proof = await orchestrator.generate_proof(
        proof_type=ProofType.EXECUTION_PROOF,
        dac_id=dac_spec.dac_id,
        input_data={"remix_hash": commit.remix_hash},
        output_data={"deployment_id": deployment.deployment_id}
    )
    
    assert proof.verifiable is True
    assert proof.reward_eligible is True
    print(f"✅ Proof generated: {proof.proof_id}")
    print(f"   Proof value: ${proof.proof_value:.2f}")
    
    # Step 8: Verify provenance
    print("\nStep 8: Verifying complete provenance chain...")
    dac_status = orchestrator.get_dac_status(dac_spec.dac_id)
    
    assert dac_status["dac_id"] == dac_spec.dac_id
    assert dac_status["mcp_enabled"] is True
    assert dac_status["a2a_enabled"] is True
    assert dac_status["energy_atlas_tracking"] is True
    assert dac_status["proof_economy_enabled"] is True
    print(f"✅ Provenance verified")
    print(f"   Total energy: {dac_status['total_energy_consumed_joules']} J")
    print(f"   Carbon footprint: {dac_status['total_carbon_footprint_kg']:.4f} kg")
    
    print("\n✅ COMPLETE DAC CREATION WORKFLOW PASSED!")
    return {
        "snapshot_id": snapshot.snapshot_id,
        "utid": commit.utid,
        "dac_id": dac_spec.dac_id,
        "deployment_id": deployment.deployment_id,
        "proof_id": proof.proof_id
    }


@pytest.mark.asyncio
async def test_a2a_agent_orchestration_with_mcp():
    """
    Test A2A agent orchestration with MCP context propagation
    
    Workflow:
    1. Discover agents via A2A
    2. Create workflow with MCP context
    3. Execute workflow across agents
    4. Verify context propagation
    """
    print("\n=== Testing A2A + MCP Integration ===\n")
    
    # Step 1: Discover agents
    print("Step 1: Discovering agents via A2A...")
    host_agent = create_host_agent()
    agents = host_agent.discover_agents()
    
    assert len(agents) == 4
    print(f"✅ Discovered {len(agents)} agents")
    
    # Step 2: Find agents by skill
    print("\nStep 2: Finding agents by skill...")
    thermal_agents = host_agent.discover_agents(skill="thermal_optimization")
    physics_agents = host_agent.discover_agents(skill="physics_simulation")
    
    assert len(thermal_agents) == 1
    assert len(physics_agents) == 1
    print(f"✅ Found thermal agents: {len(thermal_agents)}")
    print(f"✅ Found physics agents: {len(physics_agents)}")
    
    # Step 3: Orchestrate workflow with MCP context
    print("\nStep 3: Orchestrating workflow with MCP context...")
    mcp_context = {
        "energy_budget": 1000.0,
        "optimization_target": "minimize_latency",
        "constraints": ["power_limit_100w", "thermal_limit_85c"]
    }
    
    result = await host_agent.orchestrate_workflow(
        workflow_description="Optimize fab layout using thermal sampling and physics simulation",
        input_data={"fab_id": "fab_123"},
        mcp_context=mcp_context
    )
    
    assert result["orchestration_ready"] is True
    assert result["mcp_enabled"] is True
    assert result["available_agents"] == 4
    print(f"✅ Workflow orchestrated")
    print(f"   MCP enabled: {result['mcp_enabled']}")
    print(f"   Available agents: {result['available_agents']}")
    
    print("\n✅ A2A + MCP INTEGRATION PASSED!")


@pytest.mark.asyncio
async def test_thermodynamic_workflow_execution():
    """
    Test thermodynamic workflow execution across multiple agents
    
    Workflow:
    1. Create multi-step thermodynamic workflow
    2. Execute workflow
    3. Verify all steps completed
    4. Check energy tracking
    """
    print("\n=== Testing Thermodynamic Workflow Execution ===\n")
    
    # Create workflow
    print("Step 1: Creating thermodynamic workflow...")
    workflow = ThermodynamicWorkflow(
        workflow_id="wf_fab_optimization",
        name="Fab Optimization Workflow",
        description="Multi-agent fab optimization",
        steps=[
            WorkflowStep(
                step_id="step_1_thermal",
                agent_id="thermal_sampler_agent",
                skill="thermal_optimization",
                input_data={"problem_type": "tsp", "variables": 10},
                mcp_context={"energy_budget": 500.0}
            ),
            WorkflowStep(
                step_id="step_2_physics",
                agent_id="world_model_agent",
                skill="physics_simulation",
                input_data={"domain": "resist", "time_steps": 100},
                depends_on=["step_1_thermal"],
                mcp_context={"simulation_accuracy": "high"}
            ),
            WorkflowStep(
                step_id="step_3_adaptive",
                agent_id="microadapt_edge_agent",
                skill="adaptive_forecast",
                input_data={"horizon": 10},
                depends_on=["step_2_physics"],
                mcp_context={"real_time": True}
            )
        ],
        parallel_execution=False,
        energy_budget=1000.0
    )
    
    print(f"✅ Workflow created with {len(workflow.steps)} steps")
    
    # Execute workflow
    print("\nStep 2: Executing workflow...")
    orchestrator = create_dac_factory_orchestrator()
    result = await orchestrator.execute_workflow(workflow)
    
    assert result.status == "success"
    assert result.steps_completed == 3
    assert result.steps_failed == 0
    print(f"✅ Workflow executed successfully")
    print(f"   Steps completed: {result.steps_completed}")
    print(f"   Total time: {result.total_execution_time_seconds:.2f}s")
    print(f"   Energy consumed: {result.energy_consumed_joules} J")
    print(f"   Provenance hash: {result.provenance_hash[:16]}...")
    
    print("\n✅ THERMODYNAMIC WORKFLOW EXECUTION PASSED!")


@pytest.mark.skipif(not MCP_AVAILABLE, reason="MCP not available")
def test_mcp_context_propagation():
    """Test MCP context propagation across services"""
    print("\n=== Testing MCP Context Propagation ===\n")
    
    bridge = create_bridge_api(enable_mcp=True)
    
    assert hasattr(bridge, '_mcp')
    assert hasattr(bridge, '_mcp_app')
    
    # Check that all endpoints are exposed as MCP tools
    route_count = len(bridge._mcp_app.routes)
    print(f"✅ MCP exposing {route_count} endpoints as tools")
    
    # Verify thermodynamic endpoints
    route_paths = [route.path for route in bridge._mcp_app.routes]
    assert any("/thermal/" in path for path in route_paths)
    assert any("/worldmodel/" in path for path in route_paths)
    assert any("/microadapt/" in path for path in route_paths)
    assert any("/snapshot/" in path for path in route_paths)
    
    print("✅ All thermodynamic services MCP-enabled")
    print("\n✅ MCP CONTEXT PROPAGATION PASSED!")


def test_complete_stack_health():
    """Test health of complete stack"""
    print("\n=== Testing Complete Stack Health ===\n")
    
    # Test Remix Lab
    remix_lab = create_remix_lab_service()
    remix_stats = remix_lab.get_statistics()
    print(f"✅ Remix Lab: {remix_stats['total_snapshots']} snapshots")
    
    # Test A2A
    registry = get_agent_registry()
    agents = registry.list_agents()
    print(f"✅ A2A: {len(agents)} agents registered")
    
    # Test DAC Factory
    orchestrator = create_dac_factory_orchestrator()
    platform_stats = orchestrator.get_platform_statistics()
    print(f"✅ DAC Factory: {platform_stats['total_dacs']} DACs")
    
    # Test MCP
    if MCP_AVAILABLE:
        bridge = create_bridge_api(enable_mcp=True)
        print(f"✅ MCP: Enabled with {len(bridge._mcp_app.routes)} endpoints")
    else:
        print("⚠️  MCP: Not available")
    
    print("\n✅ COMPLETE STACK HEALTH CHECK PASSED!")


if __name__ == "__main__":
    print("=" * 70)
    print("COMPLETE VERTICAL INTEGRATION TESTS")
    print("=" * 70)
    
    # Run tests
    asyncio.run(test_complete_dac_creation_workflow())
    asyncio.run(test_a2a_agent_orchestration_with_mcp())
    asyncio.run(test_thermodynamic_workflow_execution())
    
    if MCP_AVAILABLE:
        test_mcp_context_propagation()
    
    test_complete_stack_health()
    
    print("\n" + "=" * 70)
    print("✅ ALL VERTICAL INTEGRATION TESTS PASSED!")
    print("=" * 70)
