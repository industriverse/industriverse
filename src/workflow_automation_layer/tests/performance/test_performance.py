import unittest
import sys
import os
import time
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
from agents.workflow_optimizer import WorkflowOptimizer
from agents.workflow_feedback_agent import WorkflowFeedbackAgent
from agents.workflow_router_agent import WorkflowRouterAgent


class TestWorkflowEnginePerformance(unittest.TestCase):
    """Performance tests for the workflow engine components."""
    
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
        
        # Generate a large workflow manifest for performance testing
        self.generate_large_workflow_manifest(100)  # 100 tasks
    
    def generate_large_workflow_manifest(self, num_tasks):
        """Generate a large workflow manifest with the specified number of tasks."""
        tasks = []
        
        # Create start task
        tasks.append({
            "id": "task-001",
            "name": "Start Task",
            "type": "start",
            "next": ["task-002"]
        })
        
        # Create middle tasks
        for i in range(2, num_tasks):
            task_id = f"task-{i:03d}"
            next_task_id = f"task-{i+1:03d}"
            tasks.append({
                "id": task_id,
                "name": f"Process Task {i}",
                "type": "process",
                "inputs": [f"data{i-1}"],
                "outputs": [f"result{i}"],
                "next": [next_task_id]
            })
        
        # Create end task
        tasks.append({
            "id": f"task-{num_tasks:03d}",
            "name": "End Task",
            "type": "end",
            "inputs": [f"result{num_tasks-1}"]
        })
        
        # Create the workflow manifest
        self.test_workflow_manifest = {
            "id": "perf-workflow-001",
            "name": "Performance Test Workflow",
            "version": "1.0",
            "description": "A workflow for performance testing",
            "execution_mode": "autonomous",
            "mesh_topology": "distributed",
            "tasks": tasks
        }
    
    def test_workflow_creation_performance(self):
        """Test the performance of workflow creation."""
        # Measure the time to create a workflow
        start_time = time.time()
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        end_time = time.time()
        
        # Verify the workflow was created
        registered_workflow = self.workflow_registry.get_workflow(workflow_id)
        self.assertIsNotNone(registered_workflow)
        
        # Log the performance metrics
        creation_time = end_time - start_time
        print(f"Workflow creation time: {creation_time:.6f} seconds")
        
        # Assert that the creation time is within acceptable limits
        self.assertLess(creation_time, 1.0)  # Should be less than 1 second
    
    def test_task_contract_extraction_performance(self):
        """Test the performance of task contract extraction."""
        # Measure the time to extract task contracts
        start_time = time.time()
        task_contracts = self.manifest_parser.extract_task_contracts(self.test_workflow_manifest)
        end_time = time.time()
        
        # Verify the contracts were extracted
        self.assertEqual(len(task_contracts), len(self.test_workflow_manifest["tasks"]))
        
        # Log the performance metrics
        extraction_time = end_time - start_time
        print(f"Task contract extraction time: {extraction_time:.6f} seconds")
        
        # Assert that the extraction time is within acceptable limits
        self.assertLess(extraction_time, 0.5)  # Should be less than 0.5 seconds
    
    def test_workflow_execution_performance(self):
        """Test the performance of workflow execution."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Prepare input data
        input_data = {"data1": "test_value"}
        
        # Measure the time to execute the workflow
        start_time = time.time()
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        end_time = time.time()
        
        # Verify the execution was registered
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertIsNotNone(execution)
        
        # Log the performance metrics
        execution_time = end_time - start_time
        print(f"Workflow execution time: {execution_time:.6f} seconds")
        
        # Assert that the execution time is within acceptable limits
        self.assertLess(execution_time, 2.0)  # Should be less than 2 seconds
    
    def test_mesh_topology_routing_performance(self):
        """Test the performance of mesh topology routing."""
        # Register a large number of agents
        num_agents = 100
        for i in range(1, num_agents + 1):
            agent_id = f"agent-{i:03d}"
            agent_type = "process" if i % 3 == 0 else "workflow_trigger" if i % 3 == 1 else "human_intervention"
            capabilities = ["data_processing", "event_handling"] if i % 2 == 0 else ["approval_handling", "notification"]
            self.mesh_topology_manager.register_agent(agent_id, agent_type, capabilities)
        
        # Measure the time to route tasks
        num_tasks = 100
        start_time = time.time()
        for i in range(1, num_tasks + 1):
            task_id = f"task-{i:03d}"
            task_type = "process"
            requirements = ["data_processing"] if i % 2 == 0 else ["event_handling"]
            agent = self.mesh_topology_manager.route_task(task_id, task_type, requirements)
        end_time = time.time()
        
        # Log the performance metrics
        routing_time = end_time - start_time
        avg_routing_time = routing_time / num_tasks
        print(f"Total mesh topology routing time: {routing_time:.6f} seconds")
        print(f"Average routing time per task: {avg_routing_time:.6f} seconds")
        
        # Assert that the average routing time is within acceptable limits
        self.assertLess(avg_routing_time, 0.01)  # Should be less than 10ms per task
    
    def test_debug_trace_performance(self):
        """Test the performance of debug trace management."""
        workflow_id = self.test_workflow_manifest["id"]
        execution_id = "perf-execution-001"
        
        # Start a trace
        self.debug_trace_manager.start_trace(workflow_id, execution_id, "verbose")
        
        # Measure the time to add a large number of trace events
        num_events = 1000
        start_time = time.time()
        for i in range(1, num_events + 1):
            event_type = "task_started" if i % 4 == 0 else "task_completed" if i % 4 == 1 else "data_processed" if i % 4 == 2 else "decision_made"
            event_data = {
                "task_id": f"task-{(i % 100) + 1:03d}",
                "timestamp": f"2025-05-22T{12 + (i % 12):02d}:{i % 60:02d}:00Z",
                "details": f"Test event {i}"
            }
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, event_data)
        end_time = time.time()
        
        # Get the trace
        trace = self.debug_trace_manager.get_trace(workflow_id, execution_id)
        
        # Verify the trace contains all events
        self.assertEqual(len(trace["events"]), num_events)
        
        # Log the performance metrics
        event_addition_time = end_time - start_time
        avg_event_time = event_addition_time / num_events
        print(f"Total trace event addition time: {event_addition_time:.6f} seconds")
        print(f"Average time per event: {avg_event_time:.6f} seconds")
        
        # Assert that the average event addition time is within acceptable limits
        self.assertLess(avg_event_time, 0.001)  # Should be less than 1ms per event
        
        # Measure the time to analyze the trace
        start_time = time.time()
        analysis = self.debug_trace_manager.analyze_trace(workflow_id, execution_id, "performance")
        end_time = time.time()
        
        # Log the performance metrics
        analysis_time = end_time - start_time
        print(f"Trace analysis time: {analysis_time:.6f} seconds")
        
        # Assert that the analysis time is within acceptable limits
        self.assertLess(analysis_time, 1.0)  # Should be less than 1 second


class TestAgentPerformance(unittest.TestCase):
    """Performance tests for the agent framework components."""
    
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
        
        self.workflow_optimizer = WorkflowOptimizer(
            agent_id="workflow-optimizer-001",
            workflow_runtime=self.workflow_runtime
        )
        
        self.feedback_agent = WorkflowFeedbackAgent(
            agent_id="workflow-feedback-001",
            workflow_runtime=self.workflow_runtime
        )
        
        self.router_agent = WorkflowRouterAgent(
            agent_id="workflow-router-001",
            workflow_runtime=self.workflow_runtime,
            mesh_topology_manager=self.mesh_topology_manager
        )
    
    def test_trigger_agent_performance(self):
        """Test the performance of the workflow trigger agent."""
        # Configure the workflow runtime mock
        self.workflow_runtime.execute_workflow.return_value = "execution-001"
        
        # Register a large number of triggers
        num_triggers = 100
        start_time = time.time()
        for i in range(1, num_triggers + 1):
            trigger_config = {
                "id": f"trigger-{i:03d}",
                "type": "event",
                "event_type": f"sensor_data_{i % 10}",
                "conditions": {f"metric_{i % 5}": f"> {i * 10}"}
            }
            self.trigger_agent.register_trigger(trigger_config)
        end_time = time.time()
        
        # Log the performance metrics
        registration_time = end_time - start_time
        avg_registration_time = registration_time / num_triggers
        print(f"Total trigger registration time: {registration_time:.6f} seconds")
        print(f"Average registration time per trigger: {avg_registration_time:.6f} seconds")
        
        # Assert that the average registration time is within acceptable limits
        self.assertLess(avg_registration_time, 0.01)  # Should be less than 10ms per trigger
        
        # Measure the time to process a large number of events
        num_events = 1000
        start_time = time.time()
        for i in range(1, num_events + 1):
            event = {
                "type": f"sensor_data_{i % 10}",
                "data": {f"metric_{i % 5}": i * 20}  # Will trigger for some events
            }
            self.trigger_agent.process_event(event)
        end_time = time.time()
        
        # Log the performance metrics
        processing_time = end_time - start_time
        avg_processing_time = processing_time / num_events
        print(f"Total event processing time: {processing_time:.6f} seconds")
        print(f"Average processing time per event: {avg_processing_time:.6f} seconds")
        
        # Assert that the average processing time is within acceptable limits
        self.assertLess(avg_processing_time, 0.005)  # Should be less than 5ms per event
    
    def test_contract_parser_performance(self):
        """Test the performance of the workflow contract parser."""
        # Generate a large contract for performance testing
        num_tasks = 100
        tasks = []
        for i in range(1, num_tasks + 1):
            tasks.append({
                "id": f"task-{i:03d}",
                "type": "process" if i % 3 == 0 else "approval" if i % 3 == 1 else "notification",
                "inputs": [f"data{i-1}"] if i > 1 else [],
                "outputs": [f"result{i}"] if i < num_tasks else []
            })
        
        contract = {
            "version": "1.0",
            "tasks": tasks
        }
        
        # Measure the time to parse the contract
        start_time = time.time()
        parsed_contract = self.contract_parser.parse_contract(contract)
        end_time = time.time()
        
        # Verify the contract was parsed
        self.assertIsNotNone(parsed_contract)
        
        # Log the performance metrics
        parsing_time = end_time - start_time
        print(f"Contract parsing time: {parsing_time:.6f} seconds")
        
        # Assert that the parsing time is within acceptable limits
        self.assertLess(parsing_time, 0.5)  # Should be less than 0.5 seconds
        
        # Measure the time to validate the contract
        start_time = time.time()
        validation_result = self.contract_parser.validate_contract(contract)
        end_time = time.time()
        
        # Verify the contract was validated
        self.assertTrue(validation_result)
        
        # Log the performance metrics
        validation_time = end_time - start_time
        print(f"Contract validation time: {validation_time:.6f} seconds")
        
        # Assert that the validation time is within acceptable limits
        self.assertLess(validation_time, 0.5)  # Should be less than 0.5 seconds
    
    def test_capsule_controller_performance(self):
        """Test the performance of the capsule workflow controller."""
        # Configure the execution mode manager mock
        self.execution_mode_manager.get_execution_mode.return_value = "autonomous"
        
        # Configure the mesh topology manager mock
        self.mesh_topology_manager.get_mesh_topology.return_value = "distributed"
        
        # Measure the time to create a large number of capsules
        num_capsules = 100
        start_time = time.time()
        capsule_ids = []
        for i in range(1, num_capsules + 1):
            workflow_id = f"workflow-{i:03d}"
            capsule_config = {
                "id": f"capsule-{i:03d}",
                "type": "workflow",
                "workflow_id": workflow_id,
                "execution_mode": "autonomous" if i % 3 == 0 else "supervised" if i % 3 == 1 else "collaborative"
            }
            capsule_id = self.capsule_controller.create_capsule(capsule_config)
            capsule_ids.append(capsule_id)
        end_time = time.time()
        
        # Log the performance metrics
        creation_time = end_time - start_time
        avg_creation_time = creation_time / num_capsules
        print(f"Total capsule creation time: {creation_time:.6f} seconds")
        print(f"Average creation time per capsule: {avg_creation_time:.6f} seconds")
        
        # Assert that the average creation time is within acceptable limits
        self.assertLess(avg_creation_time, 0.01)  # Should be less than 10ms per capsule
        
        # Measure the time to update execution modes for all capsules
        start_time = time.time()
        for capsule_id in capsule_ids:
            new_mode = "supervised"
            self.capsule_controller.update_capsule_execution_mode(capsule_id, new_mode)
        end_time = time.time()
        
        # Log the performance metrics
        update_time = end_time - start_time
        avg_update_time = update_time / num_capsules
        print(f"Total execution mode update time: {update_time:.6f} seconds")
        print(f"Average update time per capsule: {avg_update_time:.6f} seconds")
        
        # Assert that the average update time is within acceptable limits
        self.assertLess(avg_update_time, 0.01)  # Should be less than 10ms per capsule
    
    def test_workflow_optimizer_performance(self):
        """Test the performance of the workflow optimizer."""
        # Configure the workflow runtime mock
        self.workflow_runtime.get_workflow.return_value = {
            "id": "workflow-001",
            "tasks": [{"id": f"task-{i:03d}"} for i in range(1, 101)]  # 100 tasks
        }
        
        # Measure the time to analyze a workflow
        start_time = time.time()
        workflow_id = "workflow-001"
        analysis = self.workflow_optimizer.analyze_workflow(workflow_id)
        end_time = time.time()
        
        # Log the performance metrics
        analysis_time = end_time - start_time
        print(f"Workflow analysis time: {analysis_time:.6f} seconds")
        
        # Assert that the analysis time is within acceptable limits
        self.assertLess(analysis_time, 1.0)  # Should be less than 1 second
        
        # Measure the time to optimize a workflow
        start_time = time.time()
        optimization_params = {"target": "performance", "constraints": {"max_resources": 100}}
        optimized_workflow = self.workflow_optimizer.optimize_workflow(workflow_id, optimization_params)
        end_time = time.time()
        
        # Log the performance metrics
        optimization_time = end_time - start_time
        print(f"Workflow optimization time: {optimization_time:.6f} seconds")
        
        # Assert that the optimization time is within acceptable limits
        self.assertLess(optimization_time, 2.0)  # Should be less than 2 seconds


if __name__ == '__main__':
    unittest.main()
