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


class TestWorkflowRuntime(unittest.TestCase):
    """Test cases for the WorkflowRuntime class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manifest_parser = MagicMock(spec=WorkflowManifestParser)
        self.task_contract_manager = MagicMock(spec=TaskContractManager)
        self.workflow_registry = MagicMock(spec=WorkflowRegistry)
        self.workflow_telemetry = MagicMock(spec=WorkflowTelemetry)
        self.execution_mode_manager = MagicMock(spec=ExecutionModeManager)
        self.mesh_topology_manager = MagicMock(spec=MeshTopologyManager)
        self.debug_trace_manager = MagicMock(spec=CapsuleDebugTraceManager)
        
        self.workflow_runtime = WorkflowRuntime(
            manifest_parser=self.manifest_parser,
            task_contract_manager=self.task_contract_manager,
            workflow_registry=self.workflow_registry,
            workflow_telemetry=self.workflow_telemetry,
            execution_mode_manager=self.execution_mode_manager,
            mesh_topology_manager=self.mesh_topology_manager,
            debug_trace_manager=self.debug_trace_manager
        )
    
    def test_initialization(self):
        """Test that the workflow runtime initializes correctly."""
        self.assertEqual(self.workflow_runtime.manifest_parser, self.manifest_parser)
        self.assertEqual(self.workflow_runtime.task_contract_manager, self.task_contract_manager)
        self.assertEqual(self.workflow_runtime.workflow_registry, self.workflow_registry)
        self.assertEqual(self.workflow_runtime.workflow_telemetry, self.workflow_telemetry)
        self.assertEqual(self.workflow_runtime.execution_mode_manager, self.execution_mode_manager)
        self.assertEqual(self.workflow_runtime.mesh_topology_manager, self.mesh_topology_manager)
        self.assertEqual(self.workflow_runtime.debug_trace_manager, self.debug_trace_manager)
        self.assertEqual(self.workflow_runtime.status, "initialized")
    
    @patch('workflow_engine.workflow_runtime.WorkflowRuntime.start')
    def test_start(self, mock_start):
        """Test that the workflow runtime starts correctly."""
        self.workflow_runtime.start()
        mock_start.assert_called_once()
        
    @patch('workflow_engine.workflow_runtime.WorkflowRuntime.stop')
    def test_stop(self, mock_stop):
        """Test that the workflow runtime stops correctly."""
        self.workflow_runtime.stop()
        mock_stop.assert_called_once()
    
    @patch('workflow_engine.workflow_runtime.WorkflowRuntime.create_workflow')
    def test_create_workflow(self, mock_create):
        """Test that the workflow runtime creates workflows correctly."""
        workflow_manifest = {
            "id": "workflow-001",
            "name": "Test Workflow",
            "version": "1.0",
            "tasks": []
        }
        self.workflow_runtime.create_workflow(workflow_manifest)
        mock_create.assert_called_once_with(workflow_manifest)
    
    @patch('workflow_engine.workflow_runtime.WorkflowRuntime.execute_workflow')
    def test_execute_workflow(self, mock_execute):
        """Test that the workflow runtime executes workflows correctly."""
        workflow_id = "workflow-001"
        input_data = {"param1": "value1"}
        execution_mode = "autonomous"
        self.workflow_runtime.execute_workflow(workflow_id, input_data, execution_mode)
        mock_execute.assert_called_once_with(workflow_id, input_data, execution_mode)
    
    @patch('workflow_engine.workflow_runtime.WorkflowRuntime.get_workflow_status')
    def test_get_workflow_status(self, mock_get_status):
        """Test that the workflow runtime gets workflow status correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.workflow_runtime.get_workflow_status(workflow_id, execution_id)
        mock_get_status.assert_called_once_with(workflow_id, execution_id)
    
    @patch('workflow_engine.workflow_runtime.WorkflowRuntime.pause_workflow')
    def test_pause_workflow(self, mock_pause):
        """Test that the workflow runtime pauses workflows correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.workflow_runtime.pause_workflow(workflow_id, execution_id)
        mock_pause.assert_called_once_with(workflow_id, execution_id)
    
    @patch('workflow_engine.workflow_runtime.WorkflowRuntime.resume_workflow')
    def test_resume_workflow(self, mock_resume):
        """Test that the workflow runtime resumes workflows correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.workflow_runtime.resume_workflow(workflow_id, execution_id)
        mock_resume.assert_called_once_with(workflow_id, execution_id)
    
    @patch('workflow_engine.workflow_runtime.WorkflowRuntime.cancel_workflow')
    def test_cancel_workflow(self, mock_cancel):
        """Test that the workflow runtime cancels workflows correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.workflow_runtime.cancel_workflow(workflow_id, execution_id)
        mock_cancel.assert_called_once_with(workflow_id, execution_id)


class TestWorkflowManifestParser(unittest.TestCase):
    """Test cases for the WorkflowManifestParser class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.parser = WorkflowManifestParser()
    
    def test_initialization(self):
        """Test that the parser initializes correctly."""
        self.assertIsNotNone(self.parser)
    
    @patch('workflow_engine.workflow_manifest_parser.WorkflowManifestParser.parse_manifest')
    def test_parse_manifest(self, mock_parse):
        """Test that the parser parses manifests correctly."""
        manifest = {
            "id": "workflow-001",
            "name": "Test Workflow",
            "version": "1.0",
            "tasks": [
                {"id": "task-001", "type": "process", "inputs": ["data1"], "outputs": ["result1"]}
            ]
        }
        self.parser.parse_manifest(manifest)
        mock_parse.assert_called_once_with(manifest)
    
    @patch('workflow_engine.workflow_manifest_parser.WorkflowManifestParser.validate_manifest')
    def test_validate_manifest(self, mock_validate):
        """Test that the parser validates manifests correctly."""
        manifest = {
            "id": "workflow-001",
            "name": "Test Workflow",
            "version": "1.0",
            "tasks": [
                {"id": "task-001", "type": "process", "inputs": ["data1"], "outputs": ["result1"]}
            ]
        }
        self.parser.validate_manifest(manifest)
        mock_validate.assert_called_once_with(manifest)
    
    @patch('workflow_engine.workflow_manifest_parser.WorkflowManifestParser.extract_task_contracts')
    def test_extract_task_contracts(self, mock_extract):
        """Test that the parser extracts task contracts correctly."""
        manifest = {
            "id": "workflow-001",
            "name": "Test Workflow",
            "version": "1.0",
            "tasks": [
                {"id": "task-001", "type": "process", "inputs": ["data1"], "outputs": ["result1"]}
            ]
        }
        self.parser.extract_task_contracts(manifest)
        mock_extract.assert_called_once_with(manifest)


class TestTaskContractManager(unittest.TestCase):
    """Test cases for the TaskContractManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = TaskContractManager()
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.contracts, {})
    
    @patch('workflow_engine.task_contract_manager.TaskContractManager.register_contract')
    def test_register_contract(self, mock_register):
        """Test that the manager registers contracts correctly."""
        contract_id = "contract-001"
        contract = {
            "id": contract_id,
            "version": "1.0",
            "inputs": ["data1"],
            "outputs": ["result1"]
        }
        self.manager.register_contract(contract_id, contract)
        mock_register.assert_called_once_with(contract_id, contract)
    
    @patch('workflow_engine.task_contract_manager.TaskContractManager.get_contract')
    def test_get_contract(self, mock_get):
        """Test that the manager retrieves contracts correctly."""
        contract_id = "contract-001"
        self.manager.get_contract(contract_id)
        mock_get.assert_called_once_with(contract_id)
    
    @patch('workflow_engine.task_contract_manager.TaskContractManager.validate_contract')
    def test_validate_contract(self, mock_validate):
        """Test that the manager validates contracts correctly."""
        contract = {
            "id": "contract-001",
            "version": "1.0",
            "inputs": ["data1"],
            "outputs": ["result1"]
        }
        self.manager.validate_contract(contract)
        mock_validate.assert_called_once_with(contract)


class TestWorkflowRegistry(unittest.TestCase):
    """Test cases for the WorkflowRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = WorkflowRegistry()
    
    def test_initialization(self):
        """Test that the registry initializes correctly."""
        self.assertIsNotNone(self.registry)
        self.assertEqual(self.registry.workflows, {})
        self.assertEqual(self.registry.executions, {})
    
    @patch('workflow_engine.workflow_registry.WorkflowRegistry.register_workflow')
    def test_register_workflow(self, mock_register):
        """Test that the registry registers workflows correctly."""
        workflow_id = "workflow-001"
        workflow = {
            "id": workflow_id,
            "name": "Test Workflow",
            "version": "1.0",
            "tasks": []
        }
        self.registry.register_workflow(workflow_id, workflow)
        mock_register.assert_called_once_with(workflow_id, workflow)
    
    @patch('workflow_engine.workflow_registry.WorkflowRegistry.get_workflow')
    def test_get_workflow(self, mock_get):
        """Test that the registry retrieves workflows correctly."""
        workflow_id = "workflow-001"
        self.registry.get_workflow(workflow_id)
        mock_get.assert_called_once_with(workflow_id)
    
    @patch('workflow_engine.workflow_registry.WorkflowRegistry.register_execution')
    def test_register_execution(self, mock_register):
        """Test that the registry registers executions correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        execution_data = {
            "id": execution_id,
            "workflow_id": workflow_id,
            "status": "running",
            "start_time": "2025-05-22T12:00:00Z"
        }
        self.registry.register_execution(workflow_id, execution_id, execution_data)
        mock_register.assert_called_once_with(workflow_id, execution_id, execution_data)
    
    @patch('workflow_engine.workflow_registry.WorkflowRegistry.get_execution')
    def test_get_execution(self, mock_get):
        """Test that the registry retrieves executions correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.registry.get_execution(workflow_id, execution_id)
        mock_get.assert_called_once_with(workflow_id, execution_id)
    
    @patch('workflow_engine.workflow_registry.WorkflowRegistry.update_execution_status')
    def test_update_execution_status(self, mock_update):
        """Test that the registry updates execution status correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        status = "completed"
        self.registry.update_execution_status(workflow_id, execution_id, status)
        mock_update.assert_called_once_with(workflow_id, execution_id, status)


class TestWorkflowTelemetry(unittest.TestCase):
    """Test cases for the WorkflowTelemetry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.telemetry = WorkflowTelemetry()
    
    def test_initialization(self):
        """Test that the telemetry initializes correctly."""
        self.assertIsNotNone(self.telemetry)
    
    @patch('workflow_engine.workflow_telemetry.WorkflowTelemetry.record_event')
    def test_record_event(self, mock_record):
        """Test that the telemetry records events correctly."""
        event_type = "workflow_started"
        event_data = {
            "workflow_id": "workflow-001",
            "execution_id": "execution-001",
            "timestamp": "2025-05-22T12:00:00Z"
        }
        self.telemetry.record_event(event_type, event_data)
        mock_record.assert_called_once_with(event_type, event_data)
    
    @patch('workflow_engine.workflow_telemetry.WorkflowTelemetry.get_events')
    def test_get_events(self, mock_get):
        """Test that the telemetry retrieves events correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        event_type = "workflow_started"
        self.telemetry.get_events(workflow_id, execution_id, event_type)
        mock_get.assert_called_once_with(workflow_id, execution_id, event_type)
    
    @patch('workflow_engine.workflow_telemetry.WorkflowTelemetry.get_metrics')
    def test_get_metrics(self, mock_get):
        """Test that the telemetry retrieves metrics correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        metric_type = "execution_time"
        self.telemetry.get_metrics(workflow_id, execution_id, metric_type)
        mock_get.assert_called_once_with(workflow_id, execution_id, metric_type)


class TestExecutionModeManager(unittest.TestCase):
    """Test cases for the ExecutionModeManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = ExecutionModeManager()
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.default_mode, "supervised")
        self.assertEqual(set(self.manager.valid_modes), set(["autonomous", "supervised", "collaborative", "assistive", "manual"]))
    
    @patch('workflow_engine.execution_mode_manager.ExecutionModeManager.set_execution_mode')
    def test_set_execution_mode(self, mock_set):
        """Test that the manager sets execution modes correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        mode = "autonomous"
        self.manager.set_execution_mode(workflow_id, execution_id, mode)
        mock_set.assert_called_once_with(workflow_id, execution_id, mode)
    
    @patch('workflow_engine.execution_mode_manager.ExecutionModeManager.get_execution_mode')
    def test_get_execution_mode(self, mock_get):
        """Test that the manager retrieves execution modes correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.manager.get_execution_mode(workflow_id, execution_id)
        mock_get.assert_called_once_with(workflow_id, execution_id)
    
    @patch('workflow_engine.execution_mode_manager.ExecutionModeManager.calculate_trust_score')
    def test_calculate_trust_score(self, mock_calculate):
        """Test that the manager calculates trust scores correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        context = {"data_quality": 0.9, "agent_reliability": 0.8}
        self.manager.calculate_trust_score(workflow_id, execution_id, context)
        mock_calculate.assert_called_once_with(workflow_id, execution_id, context)
    
    @patch('workflow_engine.execution_mode_manager.ExecutionModeManager.determine_execution_mode')
    def test_determine_execution_mode(self, mock_determine):
        """Test that the manager determines execution modes correctly."""
        trust_score = 0.85
        confidence_level = 0.9
        regulatory_constraints = {"require_human_approval": False}
        self.manager.determine_execution_mode(trust_score, confidence_level, regulatory_constraints)
        mock_determine.assert_called_once_with(trust_score, confidence_level, regulatory_constraints)


class TestMeshTopologyManager(unittest.TestCase):
    """Test cases for the MeshTopologyManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = MeshTopologyManager()
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.default_topology, "centralized")
        self.assertEqual(set(self.manager.valid_topologies), set(["centralized", "distributed", "hierarchical", "hybrid"]))
    
    @patch('workflow_engine.mesh_topology_manager.MeshTopologyManager.set_mesh_topology')
    def test_set_mesh_topology(self, mock_set):
        """Test that the manager sets mesh topologies correctly."""
        workflow_id = "workflow-001"
        topology = "distributed"
        self.manager.set_mesh_topology(workflow_id, topology)
        mock_set.assert_called_once_with(workflow_id, topology)
    
    @patch('workflow_engine.mesh_topology_manager.MeshTopologyManager.get_mesh_topology')
    def test_get_mesh_topology(self, mock_get):
        """Test that the manager retrieves mesh topologies correctly."""
        workflow_id = "workflow-001"
        self.manager.get_mesh_topology(workflow_id)
        mock_get.assert_called_once_with(workflow_id)
    
    @patch('workflow_engine.mesh_topology_manager.MeshTopologyManager.register_agent')
    def test_register_agent(self, mock_register):
        """Test that the manager registers agents correctly."""
        agent_id = "agent-001"
        agent_type = "workflow_trigger"
        capabilities = ["event_processing", "workflow_initiation"]
        self.manager.register_agent(agent_id, agent_type, capabilities)
        mock_register.assert_called_once_with(agent_id, agent_type, capabilities)
    
    @patch('workflow_engine.mesh_topology_manager.MeshTopologyManager.find_agents')
    def test_find_agents(self, mock_find):
        """Test that the manager finds agents correctly."""
        agent_type = "workflow_trigger"
        capabilities = ["event_processing"]
        self.manager.find_agents(agent_type, capabilities)
        mock_find.assert_called_once_with(agent_type, capabilities)
    
    @patch('workflow_engine.mesh_topology_manager.MeshTopologyManager.route_task')
    def test_route_task(self, mock_route):
        """Test that the manager routes tasks correctly."""
        task_id = "task-001"
        task_type = "process"
        requirements = ["data_processing"]
        self.manager.route_task(task_id, task_type, requirements)
        mock_route.assert_called_once_with(task_id, task_type, requirements)


class TestCapsuleDebugTraceManager(unittest.TestCase):
    """Test cases for the CapsuleDebugTraceManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.manager = CapsuleDebugTraceManager()
    
    def test_initialization(self):
        """Test that the manager initializes correctly."""
        self.assertIsNotNone(self.manager)
        self.assertEqual(self.manager.default_trace_level, "standard")
        self.assertEqual(set(self.manager.valid_trace_levels), set(["minimal", "standard", "verbose", "forensic"]))
    
    @patch('workflow_engine.capsule_debug_trace_manager.CapsuleDebugTraceManager.start_trace')
    def test_start_trace(self, mock_start):
        """Test that the manager starts traces correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        trace_level = "verbose"
        self.manager.start_trace(workflow_id, execution_id, trace_level)
        mock_start.assert_called_once_with(workflow_id, execution_id, trace_level)
    
    @patch('workflow_engine.capsule_debug_trace_manager.CapsuleDebugTraceManager.end_trace')
    def test_end_trace(self, mock_end):
        """Test that the manager ends traces correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.manager.end_trace(workflow_id, execution_id)
        mock_end.assert_called_once_with(workflow_id, execution_id)
    
    @patch('workflow_engine.capsule_debug_trace_manager.CapsuleDebugTraceManager.add_trace_event')
    def test_add_trace_event(self, mock_add):
        """Test that the manager adds trace events correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        event_type = "task_started"
        event_data = {"task_id": "task-001", "timestamp": "2025-05-22T12:00:00Z"}
        self.manager.add_trace_event(workflow_id, execution_id, event_type, event_data)
        mock_add.assert_called_once_with(workflow_id, execution_id, event_type, event_data)
    
    @patch('workflow_engine.capsule_debug_trace_manager.CapsuleDebugTraceManager.get_trace')
    def test_get_trace(self, mock_get):
        """Test that the manager retrieves traces correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        self.manager.get_trace(workflow_id, execution_id)
        mock_get.assert_called_once_with(workflow_id, execution_id)
    
    @patch('workflow_engine.capsule_debug_trace_manager.CapsuleDebugTraceManager.analyze_trace')
    def test_analyze_trace(self, mock_analyze):
        """Test that the manager analyzes traces correctly."""
        workflow_id = "workflow-001"
        execution_id = "execution-001"
        analysis_type = "performance"
        self.manager.analyze_trace(workflow_id, execution_id, analysis_type)
        mock_analyze.assert_called_once_with(workflow_id, execution_id, analysis_type)


if __name__ == '__main__':
    unittest.main()
