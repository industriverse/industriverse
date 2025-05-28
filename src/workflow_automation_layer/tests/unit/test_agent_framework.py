import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.base_agent import BaseAgent
from agents.workflow_trigger_agent import WorkflowTriggerAgent
from agents.workflow_contract_parser import WorkflowContractParser
from agents.human_intervention_agent import HumanInterventionAgent
from agents.capsule_workflow_controller import CapsuleWorkflowController
from agents.n8n_sync_bridge import N8nSyncBridge
from agents.workflow_optimizer import WorkflowOptimizer
from agents.workflow_feedback_agent import WorkflowFeedbackAgent
from agents.task_contract_versioning_agent import TaskContractVersioningAgent
from agents.distributed_workflow_splitter_agent import DistributedWorkflowSplitterAgent
from agents.workflow_router_agent import WorkflowRouterAgent
from agents.workflow_fallback_agent import WorkflowFallbackAgent
from agents.workflow_feedback_loop_agent import WorkflowFeedbackLoopAgent
from agents.workflow_chaos_tester_agent import WorkflowChaosTesterAgent
from agents.workflow_visualizer_agent import WorkflowVisualizerAgent
from agents.workflow_negotiator_agent import WorkflowNegotiatorAgent
from agents.n8n_adapter_agent import N8nAdapterAgent
from agents.workflow_forensics_agent import WorkflowForensicsAgent
from agents.capsule_memory_manager import CapsuleMemoryManager
from agents.workflow_evolution_agent import WorkflowEvolutionAgent

from workflow_engine.workflow_runtime import WorkflowRuntime
from workflow_engine.execution_mode_manager import ExecutionModeManager
from workflow_engine.mesh_topology_manager import MeshTopologyManager


class TestBaseAgent(unittest.TestCase):
    """Test cases for the BaseAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "test-agent-001"
        self.agent_type = "test"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.base_agent = BaseAgent(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.base_agent.agent_id, self.agent_id)
        self.assertEqual(self.base_agent.agent_type, self.agent_type)
        self.assertEqual(self.base_agent.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.base_agent.status, "initialized")
        self.assertIsNotNone(self.base_agent.created_at)
        self.assertIsNone(self.base_agent.last_active_at)
    
    def test_start(self):
        """Test that the agent starts correctly."""
        self.base_agent.start()
        self.assertEqual(self.base_agent.status, "running")
        self.assertIsNotNone(self.base_agent.last_active_at)
    
    def test_stop(self):
        """Test that the agent stops correctly."""
        self.base_agent.start()
        self.base_agent.stop()
        self.assertEqual(self.base_agent.status, "stopped")
    
    def test_pause(self):
        """Test that the agent pauses correctly."""
        self.base_agent.start()
        self.base_agent.pause()
        self.assertEqual(self.base_agent.status, "paused")
    
    def test_resume(self):
        """Test that the agent resumes correctly."""
        self.base_agent.start()
        self.base_agent.pause()
        self.base_agent.resume()
        self.assertEqual(self.base_agent.status, "running")
    
    def test_get_status(self):
        """Test that the agent returns its status correctly."""
        self.assertEqual(self.base_agent.get_status(), "initialized")
        self.base_agent.start()
        self.assertEqual(self.base_agent.get_status(), "running")
    
    def test_get_metrics(self):
        """Test that the agent returns metrics correctly."""
        metrics = self.base_agent.get_metrics()
        self.assertIn("agent_id", metrics)
        self.assertIn("agent_type", metrics)
        self.assertIn("status", metrics)
        self.assertIn("created_at", metrics)
        self.assertIn("last_active_at", metrics)
        self.assertIn("tasks_processed", metrics)
        self.assertIn("success_rate", metrics)
    
    def test_update_trust_score(self):
        """Test that the agent updates its trust score correctly."""
        initial_trust_score = self.base_agent.trust_score
        self.base_agent.update_trust_score(0.8)
        self.assertEqual(self.base_agent.trust_score, 0.8)
        # Test clamping to valid range
        self.base_agent.update_trust_score(1.5)
        self.assertEqual(self.base_agent.trust_score, 1.0)
        self.base_agent.update_trust_score(-0.5)
        self.assertEqual(self.base_agent.trust_score, 0.0)
    
    def test_handle_message(self):
        """Test that the agent handles messages correctly."""
        message = {"type": "test", "content": "Hello, agent!"}
        # This should raise NotImplementedError in the base class
        with self.assertRaises(NotImplementedError):
            self.base_agent.handle_message(message)


class TestWorkflowTriggerAgent(unittest.TestCase):
    """Test cases for the WorkflowTriggerAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "trigger-agent-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.trigger_agent = WorkflowTriggerAgent(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.trigger_agent.agent_id, self.agent_id)
        self.assertEqual(self.trigger_agent.agent_type, "workflow_trigger")
        self.assertEqual(self.trigger_agent.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.trigger_agent.status, "initialized")
    
    @patch('agents.workflow_trigger_agent.WorkflowTriggerAgent.register_trigger')
    def test_register_trigger(self, mock_register):
        """Test that the agent registers triggers correctly."""
        trigger_config = {
            "type": "event",
            "event_type": "sensor_data",
            "conditions": {"temperature": "> 30"}
        }
        self.trigger_agent.register_trigger(trigger_config)
        mock_register.assert_called_once_with(trigger_config)
    
    @patch('agents.workflow_trigger_agent.WorkflowTriggerAgent.process_event')
    def test_process_event(self, mock_process):
        """Test that the agent processes events correctly."""
        event = {
            "type": "sensor_data",
            "data": {"temperature": 35}
        }
        self.trigger_agent.process_event(event)
        mock_process.assert_called_once_with(event)
    
    @patch('agents.workflow_trigger_agent.WorkflowTriggerAgent.trigger_workflow')
    def test_trigger_workflow(self, mock_trigger):
        """Test that the agent triggers workflows correctly."""
        workflow_id = "workflow-001"
        trigger_data = {"temperature": 35}
        self.trigger_agent.trigger_workflow(workflow_id, trigger_data)
        mock_trigger.assert_called_once_with(workflow_id, trigger_data)


class TestWorkflowContractParser(unittest.TestCase):
    """Test cases for the WorkflowContractParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "contract-parser-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.contract_parser = WorkflowContractParser(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.contract_parser.agent_id, self.agent_id)
        self.assertEqual(self.contract_parser.agent_type, "workflow_contract_parser")
        self.assertEqual(self.contract_parser.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.contract_parser.status, "initialized")
    
    @patch('agents.workflow_contract_parser.WorkflowContractParser.parse_contract')
    def test_parse_contract(self, mock_parse):
        """Test that the agent parses contracts correctly."""
        contract = {
            "version": "1.0",
            "tasks": [
                {"id": "task-001", "type": "process", "inputs": ["data1"], "outputs": ["result1"]}
            ]
        }
        self.contract_parser.parse_contract(contract)
        mock_parse.assert_called_once_with(contract)
    
    @patch('agents.workflow_contract_parser.WorkflowContractParser.validate_contract')
    def test_validate_contract(self, mock_validate):
        """Test that the agent validates contracts correctly."""
        contract = {
            "version": "1.0",
            "tasks": [
                {"id": "task-001", "type": "process", "inputs": ["data1"], "outputs": ["result1"]}
            ]
        }
        self.contract_parser.validate_contract(contract)
        mock_validate.assert_called_once_with(contract)


class TestHumanInterventionAgent(unittest.TestCase):
    """Test cases for the HumanInterventionAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "human-intervention-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.human_agent = HumanInterventionAgent(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.human_agent.agent_id, self.agent_id)
        self.assertEqual(self.human_agent.agent_type, "human_intervention")
        self.assertEqual(self.human_agent.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.human_agent.status, "initialized")
    
    @patch('agents.human_intervention_agent.HumanInterventionAgent.request_intervention')
    def test_request_intervention(self, mock_request):
        """Test that the agent requests human intervention correctly."""
        workflow_id = "workflow-001"
        task_id = "task-001"
        reason = "Approval required"
        data = {"temperature": 35}
        self.human_agent.request_intervention(workflow_id, task_id, reason, data)
        mock_request.assert_called_once_with(workflow_id, task_id, reason, data)
    
    @patch('agents.human_intervention_agent.HumanInterventionAgent.process_intervention_response')
    def test_process_intervention_response(self, mock_process):
        """Test that the agent processes intervention responses correctly."""
        intervention_id = "intervention-001"
        response = {"approved": True, "comments": "Looks good"}
        self.human_agent.process_intervention_response(intervention_id, response)
        mock_process.assert_called_once_with(intervention_id, response)


class TestCapsuleWorkflowController(unittest.TestCase):
    """Test cases for the CapsuleWorkflowController class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "capsule-controller-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.execution_mode_manager = MagicMock(spec=ExecutionModeManager)
        self.mesh_topology_manager = MagicMock(spec=MeshTopologyManager)
        
        self.capsule_controller = CapsuleWorkflowController(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime,
            execution_mode_manager=self.execution_mode_manager,
            mesh_topology_manager=self.mesh_topology_manager
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.capsule_controller.agent_id, self.agent_id)
        self.assertEqual(self.capsule_controller.agent_type, "capsule_workflow_controller")
        self.assertEqual(self.capsule_controller.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.capsule_controller.execution_mode_manager, self.execution_mode_manager)
        self.assertEqual(self.capsule_controller.mesh_topology_manager, self.mesh_topology_manager)
        self.assertEqual(self.capsule_controller.status, "initialized")
    
    @patch('agents.capsule_workflow_controller.CapsuleWorkflowController.create_capsule')
    def test_create_capsule(self, mock_create):
        """Test that the agent creates capsules correctly."""
        capsule_config = {
            "id": "capsule-001",
            "type": "workflow",
            "workflow_id": "workflow-001",
            "execution_mode": "autonomous"
        }
        self.capsule_controller.create_capsule(capsule_config)
        mock_create.assert_called_once_with(capsule_config)
    
    @patch('agents.capsule_workflow_controller.CapsuleWorkflowController.destroy_capsule')
    def test_destroy_capsule(self, mock_destroy):
        """Test that the agent destroys capsules correctly."""
        capsule_id = "capsule-001"
        self.capsule_controller.destroy_capsule(capsule_id)
        mock_destroy.assert_called_once_with(capsule_id)
    
    @patch('agents.capsule_workflow_controller.CapsuleWorkflowController.update_capsule_execution_mode')
    def test_update_capsule_execution_mode(self, mock_update):
        """Test that the agent updates capsule execution modes correctly."""
        capsule_id = "capsule-001"
        execution_mode = "supervised"
        self.capsule_controller.update_capsule_execution_mode(capsule_id, execution_mode)
        mock_update.assert_called_once_with(capsule_id, execution_mode)


class TestN8nSyncBridge(unittest.TestCase):
    """Test cases for the N8nSyncBridge class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "n8n-sync-bridge-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.n8n_sync_bridge = N8nSyncBridge(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime,
            n8n_api_url="http://localhost:5678/api/v1"
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.n8n_sync_bridge.agent_id, self.agent_id)
        self.assertEqual(self.n8n_sync_bridge.agent_type, "n8n_sync_bridge")
        self.assertEqual(self.n8n_sync_bridge.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.n8n_sync_bridge.n8n_api_url, "http://localhost:5678/api/v1")
        self.assertEqual(self.n8n_sync_bridge.status, "initialized")
    
    @patch('agents.n8n_sync_bridge.N8nSyncBridge.sync_workflow_to_n8n')
    def test_sync_workflow_to_n8n(self, mock_sync):
        """Test that the agent syncs workflows to n8n correctly."""
        workflow_id = "workflow-001"
        workflow_data = {"name": "Test Workflow", "nodes": [], "connections": {}}
        self.n8n_sync_bridge.sync_workflow_to_n8n(workflow_id, workflow_data)
        mock_sync.assert_called_once_with(workflow_id, workflow_data)
    
    @patch('agents.n8n_sync_bridge.N8nSyncBridge.sync_workflow_from_n8n')
    def test_sync_workflow_from_n8n(self, mock_sync):
        """Test that the agent syncs workflows from n8n correctly."""
        n8n_workflow_id = "123"
        self.n8n_sync_bridge.sync_workflow_from_n8n(n8n_workflow_id)
        mock_sync.assert_called_once_with(n8n_workflow_id)


class TestWorkflowOptimizer(unittest.TestCase):
    """Test cases for the WorkflowOptimizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "workflow-optimizer-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.workflow_optimizer = WorkflowOptimizer(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.workflow_optimizer.agent_id, self.agent_id)
        self.assertEqual(self.workflow_optimizer.agent_type, "workflow_optimizer")
        self.assertEqual(self.workflow_optimizer.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.workflow_optimizer.status, "initialized")
    
    @patch('agents.workflow_optimizer.WorkflowOptimizer.analyze_workflow')
    def test_analyze_workflow(self, mock_analyze):
        """Test that the agent analyzes workflows correctly."""
        workflow_id = "workflow-001"
        self.workflow_optimizer.analyze_workflow(workflow_id)
        mock_analyze.assert_called_once_with(workflow_id)
    
    @patch('agents.workflow_optimizer.WorkflowOptimizer.optimize_workflow')
    def test_optimize_workflow(self, mock_optimize):
        """Test that the agent optimizes workflows correctly."""
        workflow_id = "workflow-001"
        optimization_params = {"target": "performance", "constraints": {"max_resources": 100}}
        self.workflow_optimizer.optimize_workflow(workflow_id, optimization_params)
        mock_optimize.assert_called_once_with(workflow_id, optimization_params)


class TestWorkflowFeedbackAgent(unittest.TestCase):
    """Test cases for the WorkflowFeedbackAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "workflow-feedback-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.feedback_agent = WorkflowFeedbackAgent(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.feedback_agent.agent_id, self.agent_id)
        self.assertEqual(self.feedback_agent.agent_type, "workflow_feedback")
        self.assertEqual(self.feedback_agent.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.feedback_agent.status, "initialized")
    
    @patch('agents.workflow_feedback_agent.WorkflowFeedbackAgent.collect_feedback')
    def test_collect_feedback(self, mock_collect):
        """Test that the agent collects feedback correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.feedback_agent.collect_feedback(workflow_id, execution_id)
        mock_collect.assert_called_once_with(workflow_id, execution_id)
    
    @patch('agents.workflow_feedback_agent.WorkflowFeedbackAgent.process_feedback')
    def test_process_feedback(self, mock_process):
        """Test that the agent processes feedback correctly."""
        feedback_id = "feedback-001"
        feedback_data = {"rating": 4, "comments": "Good performance"}
        self.feedback_agent.process_feedback(feedback_id, feedback_data)
        mock_process.assert_called_once_with(feedback_id, feedback_data)


class TestTaskContractVersioningAgent(unittest.TestCase):
    """Test cases for the TaskContractVersioningAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "task-contract-versioning-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.versioning_agent = TaskContractVersioningAgent(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.versioning_agent.agent_id, self.agent_id)
        self.assertEqual(self.versioning_agent.agent_type, "task_contract_versioning")
        self.assertEqual(self.versioning_agent.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.versioning_agent.status, "initialized")
    
    @patch('agents.task_contract_versioning_agent.TaskContractVersioningAgent.create_contract_version')
    def test_create_contract_version(self, mock_create):
        """Test that the agent creates contract versions correctly."""
        contract_id = "contract-001"
        contract_data = {"version": "1.1", "tasks": []}
        self.versioning_agent.create_contract_version(contract_id, contract_data)
        mock_create.assert_called_once_with(contract_id, contract_data)
    
    @patch('agents.task_contract_versioning_agent.TaskContractVersioningAgent.get_contract_version')
    def test_get_contract_version(self, mock_get):
        """Test that the agent retrieves contract versions correctly."""
        contract_id = "contract-001"
        version = "1.0"
        self.versioning_agent.get_contract_version(contract_id, version)
        mock_get.assert_called_once_with(contract_id, version)


class TestDistributedWorkflowSplitterAgent(unittest.TestCase):
    """Test cases for the DistributedWorkflowSplitterAgent class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.agent_id = "workflow-splitter-001"
        self.workflow_runtime = MagicMock(spec=WorkflowRuntime)
        self.mesh_topology_manager = MagicMock(spec=MeshTopologyManager)
        self.splitter_agent = DistributedWorkflowSplitterAgent(
            agent_id=self.agent_id,
            workflow_runtime=self.workflow_runtime,
            mesh_topology_manager=self.mesh_topology_manager
        )
    
    def test_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertEqual(self.splitter_agent.agent_id, self.agent_id)
        self.assertEqual(self.splitter_agent.agent_type, "distributed_workflow_splitter")
        self.assertEqual(self.splitter_agent.workflow_runtime, self.workflow_runtime)
        self.assertEqual(self.splitter_agent.mesh_topology_manager, self.mesh_topology_manager)
        self.assertEqual(self.splitter_agent.status, "initialized")
    
    @patch('agents.distributed_workflow_splitter_agent.DistributedWorkflowSplitterAgent.split_workflow')
    def test_split_workflow(self, mock_split):
        """Test that the agent splits workflows correctly."""
        workflow_id = "workflow-001"
        split_strategy = "resource_balanced"
        self.splitter_agent.split_workflow(workflow_id, split_strategy)
        mock_split.assert_called_once_with(workflow_id, split_strategy)
    
    @patch('agents.distributed_workflow_splitter_agent.DistributedWorkflowSplitterAgent.merge_workflow_results')
    def test_merge_workflow_results(self, mock_merge):
        """Test that the agent merges workflow results correctly."""
        workflow_id = "workflow-001"
        split_execution_ids = ["execution-001", "execution-002"]
        self.splitter_agent.merge_workflow_results(workflow_id, split_execution_ids)
        mock_merge.assert_called_once_with(workflow_id, split_execution_ids)


if __name__ == '__main__':
    unittest.main()
