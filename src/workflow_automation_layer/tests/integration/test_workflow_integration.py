import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from workflow_engine.workflow_runtime import WorkflowRuntime
from workflow_engine.workflow_manifest_parser import WorkflowManifestParser
from workflow_engine.task_contract_manager import TaskContractManager
from workflow_engine.workflow_registry import WorkflowRegistry
from workflow_engine.workflow_telemetry import WorkflowTelemetry
from workflow_engine.execution_mode_manager import ExecutionModeManager
from workflow_engine.mesh_topology_manager import MeshTopologyManager
from workflow_engine.capsule_debug_trace_manager import CapsuleDebugTraceManager

from agents.workflow_trigger_agent import WorkflowTriggerAgent
from agents.workflow_contract_parser import WorkflowContractParser
from agents.human_intervention_agent import HumanInterventionAgent
from agents.capsule_workflow_controller import CapsuleWorkflowController
from agents.n8n_sync_bridge import N8nSyncBridge

from n8n_integration.n8n_connector import N8nConnector
from n8n_integration.n8n_bridge_service import N8nBridgeService


class TestWorkflowEngineIntegration(unittest.TestCase):
    """Integration tests for the workflow engine components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create real instances of the components
        self.manifest_parser = WorkflowManifestParser()
        self.task_contract_manager = TaskContractManager()
        self.workflow_registry = WorkflowRegistry()
        self.workflow_telemetry = WorkflowTelemetry()
        self.execution_mode_manager = ExecutionModeManager()
        self.mesh_topology_manager = MeshTopologyManager()
        self.debug_trace_manager = CapsuleDebugTraceManager()
        
        # Create the workflow runtime with real components
        self.workflow_runtime = WorkflowRuntime(
            manifest_parser=self.manifest_parser,
            task_contract_manager=self.task_contract_manager,
            workflow_registry=self.workflow_registry,
            workflow_telemetry=self.workflow_telemetry,
            execution_mode_manager=self.execution_mode_manager,
            mesh_topology_manager=self.mesh_topology_manager,
            debug_trace_manager=self.debug_trace_manager
        )
        
        # Sample workflow manifest for testing
        self.test_workflow_manifest = {
            "id": "test-workflow-001",
            "name": "Test Integration Workflow",
            "version": "1.0",
            "description": "A workflow for integration testing",
            "execution_mode": "supervised",
            "mesh_topology": "centralized",
            "tasks": [
                {
                    "id": "task-001",
                    "name": "Start Task",
                    "type": "start",
                    "next": ["task-002"]
                },
                {
                    "id": "task-002",
                    "name": "Process Task",
                    "type": "process",
                    "inputs": ["data1"],
                    "outputs": ["result1"],
                    "next": ["task-003"]
                },
                {
                    "id": "task-003",
                    "name": "End Task",
                    "type": "end",
                    "inputs": ["result1"]
                }
            ]
        }
    
    def test_workflow_creation_and_execution(self):
        """Test the integration of workflow creation and execution."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Verify the workflow was registered
        registered_workflow = self.workflow_registry.get_workflow(workflow_id)
        self.assertIsNotNone(registered_workflow)
        self.assertEqual(registered_workflow["id"], workflow_id)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Verify the execution was registered
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertIsNotNone(execution)
        self.assertEqual(execution["workflow_id"], workflow_id)
        
        # Verify the execution mode was set correctly
        execution_mode = self.execution_mode_manager.get_execution_mode(workflow_id, execution_id)
        self.assertEqual(execution_mode, "supervised")
        
        # Verify telemetry events were recorded
        events = self.workflow_telemetry.get_events(workflow_id, execution_id, "workflow_started")
        self.assertGreater(len(events), 0)
    
    def test_task_contract_integration(self):
        """Test the integration of task contract management."""
        # Extract task contracts from the workflow manifest
        task_contracts = self.manifest_parser.extract_task_contracts(self.test_workflow_manifest)
        
        # Register the task contracts
        for contract_id, contract in task_contracts.items():
            self.task_contract_manager.register_contract(contract_id, contract)
        
        # Verify the contracts were registered
        for task in self.test_workflow_manifest["tasks"]:
            task_id = task["id"]
            contract = self.task_contract_manager.get_contract(task_id)
            self.assertIsNotNone(contract)
            self.assertEqual(contract["id"], task_id)
    
    def test_execution_mode_integration(self):
        """Test the integration of execution mode management."""
        workflow_id = self.test_workflow_manifest["id"]
        execution_id = "test-execution-001"
        
        # Set the execution mode
        self.execution_mode_manager.set_execution_mode(workflow_id, execution_id, "autonomous")
        
        # Calculate trust score
        context = {"data_quality": 0.9, "agent_reliability": 0.8}
        trust_score = self.execution_mode_manager.calculate_trust_score(workflow_id, execution_id, context)
        
        # Determine execution mode based on trust score
        confidence_level = 0.85
        regulatory_constraints = {"require_human_approval": False}
        mode = self.execution_mode_manager.determine_execution_mode(trust_score, confidence_level, regulatory_constraints)
        
        # Verify the execution mode
        self.assertIn(mode, self.execution_mode_manager.valid_modes)
    
    def test_mesh_topology_integration(self):
        """Test the integration of mesh topology management."""
        workflow_id = self.test_workflow_manifest["id"]
        
        # Set the mesh topology
        self.mesh_topology_manager.set_mesh_topology(workflow_id, "distributed")
        
        # Register agents
        agent_id1 = "agent-001"
        agent_type1 = "workflow_trigger"
        capabilities1 = ["event_processing", "workflow_initiation"]
        self.mesh_topology_manager.register_agent(agent_id1, agent_type1, capabilities1)
        
        agent_id2 = "agent-002"
        agent_type2 = "human_intervention"
        capabilities2 = ["approval_handling", "notification"]
        self.mesh_topology_manager.register_agent(agent_id2, agent_type2, capabilities2)
        
        # Find agents by type and capabilities
        agents = self.mesh_topology_manager.find_agents("workflow_trigger", ["event_processing"])
        self.assertGreater(len(agents), 0)
        self.assertEqual(agents[0]["agent_id"], agent_id1)
        
        # Route a task
        task_id = "task-002"
        task_type = "process"
        requirements = ["data_processing"]
        agent = self.mesh_topology_manager.route_task(task_id, task_type, requirements)
        self.assertIsNotNone(agent)
    
    def test_debug_trace_integration(self):
        """Test the integration of debug trace management."""
        workflow_id = self.test_workflow_manifest["id"]
        execution_id = "test-execution-001"
        
        # Start a trace
        trace_level = "verbose"
        self.debug_trace_manager.start_trace(workflow_id, execution_id, trace_level)
        
        # Add trace events
        event_types = ["workflow_started", "task_started", "task_completed", "workflow_completed"]
        for event_type in event_types:
            event_data = {
                "timestamp": "2025-05-22T12:00:00Z",
                "details": f"Test {event_type} event"
            }
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, event_data)
        
        # Get the trace
        trace = self.debug_trace_manager.get_trace(workflow_id, execution_id)
        self.assertIsNotNone(trace)
        self.assertEqual(len(trace["events"]), len(event_types))
        
        # Analyze the trace
        analysis = self.debug_trace_manager.analyze_trace(workflow_id, execution_id, "performance")
        self.assertIsNotNone(analysis)
        
        # End the trace
        self.debug_trace_manager.end_trace(workflow_id, execution_id)


class TestAgentIntegration(unittest.TestCase):
    """Integration tests for the agent framework components."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock workflow runtime
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        
        # Create real agent instances
        self.trigger_agent = WorkflowTriggerAgent(
            agent_id="trigger-agent-001",
            workflow_runtime=self.workflow_runtime
        )
        
        self.contract_parser = WorkflowContractParser(
            agent_id="contract-parser-001",
            workflow_runtime=self.workflow_runtime
        )
        
        self.human_agent = HumanInterventionAgent(
            agent_id="human-agent-001",
            workflow_runtime=self.workflow_runtime
        )
        
        # Create mock execution mode and mesh topology managers
        self.execution_mode_manager = MagicMock(spec=ExecutionModeManager)
        self.mesh_topology_manager = MagicMock(spec=MeshTopologyManager)
        
        self.capsule_controller = CapsuleWorkflowController(
            agent_id="capsule-controller-001",
            workflow_runtime=self.workflow_runtime,
            execution_mode_manager=self.execution_mode_manager,
            mesh_topology_manager=self.mesh_topology_manager
        )
        
        # Create n8n connector and sync bridge
        self.n8n_connector = MagicMock(spec=N8nConnector)
        self.n8n_bridge_service = MagicMock(spec=N8nBridgeService)
        
        self.n8n_sync_bridge = N8nSyncBridge(
            agent_id="n8n-sync-bridge-001",
            workflow_runtime=self.workflow_runtime,
            n8n_api_url="http://localhost:5678/api/v1"
        )
        
        # Sample workflow and task data
        self.workflow_id = "test-workflow-001"
        self.task_id = "test-task-001"
        self.execution_id = "test-execution-001"
    
    def test_trigger_agent_integration(self):
        """Test the integration of the workflow trigger agent."""
        # Configure the workflow runtime mock
        self.workflow_runtime.create_workflow.return_value = self.workflow_id
        self.workflow_runtime.execute_workflow.return_value = self.execution_id
        
        # Register a trigger
        trigger_config = {
            "type": "event",
            "event_type": "sensor_data",
            "conditions": {"temperature": "> 30"}
        }
        self.trigger_agent.register_trigger(trigger_config)
        
        # Process an event that matches the trigger
        event = {
            "type": "sensor_data",
            "data": {"temperature": 35}
        }
        self.trigger_agent.process_event(event)
        
        # Verify the workflow was triggered
        self.workflow_runtime.execute_workflow.assert_called_once()
    
    def test_contract_parser_integration(self):
        """Test the integration of the workflow contract parser."""
        # Configure the workflow runtime mock
        self.workflow_runtime.get_workflow.return_value = {
            "id": self.workflow_id,
            "tasks": [
                {"id": self.task_id, "type": "process", "inputs": ["data1"], "outputs": ["result1"]}
            ]
        }
        
        # Parse a contract
        contract = {
            "version": "1.0",
            "tasks": [
                {"id": self.task_id, "type": "process", "inputs": ["data1"], "outputs": ["result1"]}
            ]
        }
        parsed_contract = self.contract_parser.parse_contract(contract)
        
        # Validate the contract
        validation_result = self.contract_parser.validate_contract(contract)
        
        # Verify the contract was processed
        self.assertIsNotNone(parsed_contract)
        self.assertTrue(validation_result)
    
    def test_human_intervention_integration(self):
        """Test the integration of the human intervention agent."""
        # Configure the workflow runtime mock
        self.workflow_runtime.get_workflow.return_value = {
            "id": self.workflow_id,
            "tasks": [
                {"id": self.task_id, "type": "approval", "requires_human": True}
            ]
        }
        
        # Request human intervention
        reason = "Approval required"
        data = {"document": "contract.pdf", "amount": 5000}
        intervention_id = self.human_agent.request_intervention(
            self.workflow_id, self.task_id, reason, data
        )
        
        # Process intervention response
        response = {"approved": True, "comments": "Looks good"}
        self.human_agent.process_intervention_response(intervention_id, response)
        
        # Verify the workflow was resumed
        self.workflow_runtime.resume_workflow.assert_called_once()
    
    def test_capsule_controller_integration(self):
        """Test the integration of the capsule workflow controller."""
        # Configure the execution mode manager mock
        self.execution_mode_manager.get_execution_mode.return_value = "autonomous"
        
        # Configure the mesh topology manager mock
        self.mesh_topology_manager.get_mesh_topology.return_value = "distributed"
        
        # Create a capsule
        capsule_config = {
            "id": "capsule-001",
            "type": "workflow",
            "workflow_id": self.workflow_id,
            "execution_mode": "autonomous"
        }
        capsule_id = self.capsule_controller.create_capsule(capsule_config)
        
        # Update capsule execution mode
        new_mode = "supervised"
        self.capsule_controller.update_capsule_execution_mode(capsule_id, new_mode)
        
        # Verify the execution mode was updated
        self.execution_mode_manager.set_execution_mode.assert_called_with(
            self.workflow_id, capsule_id, new_mode
        )
        
        # Destroy the capsule
        self.capsule_controller.destroy_capsule(capsule_id)
    
    def test_n8n_sync_bridge_integration(self):
        """Test the integration of the n8n sync bridge."""
        # Configure the n8n connector mock
        self.n8n_sync_bridge.n8n_connector = self.n8n_connector
        self.n8n_connector.get_workflow.return_value = {
            "id": "1",
            "name": "Test n8n Workflow",
            "nodes": [],
            "connections": {}
        }
        self.n8n_connector.create_workflow.return_value = {
            "id": "2",
            "name": "New n8n Workflow"
        }
        
        # Sync workflow to n8n
        workflow_data = {
            "name": "Industriverse Workflow",
            "tasks": [
                {"id": self.task_id, "type": "process", "inputs": ["data1"], "outputs": ["result1"]}
            ]
        }
        n8n_workflow_id = self.n8n_sync_bridge.sync_workflow_to_n8n(self.workflow_id, workflow_data)
        
        # Sync workflow from n8n
        n8n_workflow_id = "1"
        workflow_id = self.n8n_sync_bridge.sync_workflow_from_n8n(n8n_workflow_id)
        
        # Verify the workflows were synced
        self.n8n_connector.create_workflow.assert_called_once()
        self.workflow_runtime.create_workflow.assert_called_once()


class TestN8nBridgeIntegration(unittest.TestCase):
    """Integration tests for the n8n bridge service."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock n8n connector and workflow runtime
        self.n8n_connector = MagicMock(spec=N8nConnector)
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        
        # Create real bridge service
        self.bridge_service = N8nBridgeService(
            n8n_connector=self.n8n_connector,
            workflow_runtime=self.workflow_runtime
        )
        
        # Sample workflow and webhook data
        self.workflow_id = "test-workflow-001"
        self.n8n_workflow_id = "1"
        self.webhook_url = "http://example.com/webhook"
    
    def test_workflow_sync_integration(self):
        """Test the integration of workflow synchronization."""
        # Configure the n8n connector mock
        self.n8n_connector.get_workflow.return_value = {
            "id": self.n8n_workflow_id,
            "name": "Test n8n Workflow",
            "nodes": [],
            "connections": {}
        }
        self.n8n_connector.create_workflow.return_value = {
            "id": "2",
            "name": "New n8n Workflow"
        }
        
        # Configure the workflow runtime mock
        self.workflow_runtime.get_workflow.return_value = {
            "id": self.workflow_id,
            "name": "Industriverse Workflow",
            "tasks": []
        }
        
        # Sync workflow from n8n to Industriverse
        self.bridge_service.sync_workflow_from_n8n(self.n8n_workflow_id)
        
        # Sync workflow from Industriverse to n8n
        workflow_data = {
            "name": "Industriverse Workflow",
            "tasks": []
        }
        self.bridge_service.sync_workflow_to_n8n(self.workflow_id, workflow_data)
        
        # Verify the workflows were synced
        self.workflow_runtime.create_workflow.assert_called_once()
        self.n8n_connector.create_workflow.assert_called_once()
    
    def test_webhook_integration(self):
        """Test the integration of webhook management."""
        # Configure the n8n connector mock
        self.n8n_connector.register_webhook.return_value = True
        
        # Register a webhook
        events = ["workflow.started", "workflow.completed"]
        result = self.bridge_service.register_webhook(self.workflow_id, self.webhook_url, events)
        
        # Handle a webhook event
        event_type = "workflow.completed"
        event_data = {
            "workflow_id": self.n8n_workflow_id,
            "execution_id": "123",
            "status": "success",
            "data": {"result": "approved"}
        }
        self.bridge_service.handle_webhook_event(event_type, event_data)
        
        # Verify the webhook was registered and event was handled
        self.n8n_connector.register_webhook.assert_called_once()
        self.workflow_runtime.update_workflow_status.assert_called_once()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
