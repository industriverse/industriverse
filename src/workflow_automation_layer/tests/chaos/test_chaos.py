import unittest
import sys
import os
import time
import random
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
from agents.workflow_chaos_tester_agent import WorkflowChaosTesterAgent
from agents.workflow_fallback_agent import WorkflowFallbackAgent


class TestWorkflowChaosTesting(unittest.TestCase):
    """Chaos tests for the workflow engine components."""
    
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
        
        # Create chaos tester agent
        self.chaos_tester = WorkflowChaosTesterAgent(
            agent_id="chaos-tester-001",
            workflow_runtime=self.workflow_runtime
        )
        
        # Create fallback agent
        self.fallback_agent = WorkflowFallbackAgent(
            agent_id="fallback-agent-001",
            workflow_runtime=self.workflow_runtime
        )
        
        # Sample workflow manifest for testing
        self.test_workflow_manifest = {
            "id": "chaos-workflow-001",
            "name": "Chaos Test Workflow",
            "version": "1.0",
            "description": "A workflow for chaos testing",
            "execution_mode": "autonomous",
            "mesh_topology": "distributed",
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
    
    def test_random_task_failure(self):
        """Test the system's resilience to random task failures."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Configure the chaos tester to inject random task failures
        failure_config = {
            "failure_type": "task_failure",
            "failure_rate": 0.5,  # 50% chance of failure
            "target_tasks": ["task-002"]
        }
        self.chaos_tester.configure_chaos_test(workflow_id, failure_config)
        
        # Configure the fallback agent to handle failures
        fallback_config = {
            "workflow_id": workflow_id,
            "retry_limit": 3,
            "fallback_strategy": "retry"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Execute the workflow multiple times to test resilience
        num_executions = 10
        success_count = 0
        
        for i in range(num_executions):
            input_data = {"data1": f"test_value_{i}"}
            execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
            
            # Check if the execution eventually succeeded
            execution = self.workflow_registry.get_execution(workflow_id, execution_id)
            if execution["status"] == "completed":
                success_count += 1
        
        # Verify that at least some executions succeeded despite failures
        self.assertGreater(success_count, 0)
        print(f"Success rate under random task failures: {success_count / num_executions * 100}%")
    
    def test_network_partition(self):
        """Test the system's resilience to network partitions."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Configure the mesh topology for distributed execution
        self.mesh_topology_manager.set_mesh_topology(workflow_id, "distributed")
        
        # Register agents in different partitions
        partition1_agents = []
        partition2_agents = []
        
        for i in range(1, 11):
            agent_id = f"agent-{i:03d}"
            agent_type = "process" if i % 3 == 0 else "workflow_trigger" if i % 3 == 1 else "human_intervention"
            capabilities = ["data_processing", "event_handling"] if i % 2 == 0 else ["approval_handling", "notification"]
            
            self.mesh_topology_manager.register_agent(agent_id, agent_type, capabilities)
            
            if i <= 5:
                partition1_agents.append(agent_id)
            else:
                partition2_agents.append(agent_id)
        
        # Configure the chaos tester to simulate network partition
        partition_config = {
            "failure_type": "network_partition",
            "partition1": partition1_agents,
            "partition2": partition2_agents,
            "partition_duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test(workflow_id, partition_config)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Wait for the partition to heal
        time.sleep(3)
        
        # Check if the execution eventually completed
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertEqual(execution["status"], "completed")
    
    def test_agent_crash(self):
        """Test the system's resilience to agent crashes."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Register agents
        num_agents = 5
        agent_ids = []
        
        for i in range(1, num_agents + 1):
            agent_id = f"agent-{i:03d}"
            agent_type = "process" if i % 3 == 0 else "workflow_trigger" if i % 3 == 1 else "human_intervention"
            capabilities = ["data_processing", "event_handling"] if i % 2 == 0 else ["approval_handling", "notification"]
            
            self.mesh_topology_manager.register_agent(agent_id, agent_type, capabilities)
            agent_ids.append(agent_id)
        
        # Configure the chaos tester to simulate agent crashes
        crash_config = {
            "failure_type": "agent_crash",
            "target_agents": agent_ids,
            "crash_rate": 0.4,  # 40% chance of crash
            "crash_duration": 1  # seconds
        }
        self.chaos_tester.configure_chaos_test(workflow_id, crash_config)
        
        # Configure the fallback agent to handle failures
        fallback_config = {
            "workflow_id": workflow_id,
            "retry_limit": 3,
            "fallback_strategy": "reassign"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Execute the workflow multiple times to test resilience
        num_executions = 10
        success_count = 0
        
        for i in range(num_executions):
            input_data = {"data1": f"test_value_{i}"}
            execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
            
            # Check if the execution eventually succeeded
            execution = self.workflow_registry.get_execution(workflow_id, execution_id)
            if execution["status"] == "completed":
                success_count += 1
        
        # Verify that at least some executions succeeded despite agent crashes
        self.assertGreater(success_count, 0)
        print(f"Success rate under agent crashes: {success_count / num_executions * 100}%")
    
    def test_resource_exhaustion(self):
        """Test the system's resilience to resource exhaustion."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Configure the chaos tester to simulate resource exhaustion
        resource_config = {
            "failure_type": "resource_exhaustion",
            "resource_type": "memory",
            "exhaustion_level": 0.9,  # 90% exhaustion
            "duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test(workflow_id, resource_config)
        
        # Configure the fallback agent to handle resource exhaustion
        fallback_config = {
            "workflow_id": workflow_id,
            "retry_limit": 3,
            "fallback_strategy": "throttle"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Wait for resource exhaustion to end
        time.sleep(3)
        
        # Check if the execution eventually completed
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertEqual(execution["status"], "completed")
    
    def test_clock_skew(self):
        """Test the system's resilience to clock skew between agents."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Register agents
        num_agents = 5
        agent_ids = []
        
        for i in range(1, num_agents + 1):
            agent_id = f"agent-{i:03d}"
            agent_type = "process" if i % 3 == 0 else "workflow_trigger" if i % 3 == 1 else "human_intervention"
            capabilities = ["data_processing", "event_handling"] if i % 2 == 0 else ["approval_handling", "notification"]
            
            self.mesh_topology_manager.register_agent(agent_id, agent_type, capabilities)
            agent_ids.append(agent_id)
        
        # Configure the chaos tester to simulate clock skew
        skew_config = {
            "failure_type": "clock_skew",
            "target_agents": agent_ids[1:3],  # Apply skew to a subset of agents
            "max_skew_seconds": 60,  # Up to 60 seconds of skew
            "duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test(workflow_id, skew_config)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Wait for clock skew test to end
        time.sleep(3)
        
        # Check if the execution eventually completed
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertEqual(execution["status"], "completed")
    
    def test_byzantine_behavior(self):
        """Test the system's resilience to byzantine (malicious) agent behavior."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Register agents
        num_agents = 10
        agent_ids = []
        
        for i in range(1, num_agents + 1):
            agent_id = f"agent-{i:03d}"
            agent_type = "process" if i % 3 == 0 else "workflow_trigger" if i % 3 == 1 else "human_intervention"
            capabilities = ["data_processing", "event_handling"] if i % 2 == 0 else ["approval_handling", "notification"]
            
            self.mesh_topology_manager.register_agent(agent_id, agent_type, capabilities)
            agent_ids.append(agent_id)
        
        # Configure the chaos tester to simulate byzantine behavior
        byzantine_config = {
            "failure_type": "byzantine_behavior",
            "target_agents": agent_ids[0:3],  # Make 30% of agents byzantine
            "behavior_type": "inconsistent_responses",
            "duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test(workflow_id, byzantine_config)
        
        # Configure the fallback agent to handle byzantine behavior
        fallback_config = {
            "workflow_id": workflow_id,
            "retry_limit": 3,
            "fallback_strategy": "consensus"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Wait for byzantine test to end
        time.sleep(3)
        
        # Check if the execution eventually completed
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertEqual(execution["status"], "completed")
    
    def test_cascading_failures(self):
        """Test the system's resilience to cascading failures."""
        # Register the workflow with more tasks for cascading failure testing
        cascade_workflow = {
            "id": "cascade-workflow-001",
            "name": "Cascade Test Workflow",
            "version": "1.0",
            "description": "A workflow for testing cascading failures",
            "execution_mode": "autonomous",
            "mesh_topology": "distributed",
            "tasks": [
                {"id": "task-001", "name": "Start Task", "type": "start", "next": ["task-002"]},
                {"id": "task-002", "name": "Process Task 1", "type": "process", "inputs": ["data1"], "outputs": ["result1"], "next": ["task-003", "task-004"]},
                {"id": "task-003", "name": "Process Task 2", "type": "process", "inputs": ["result1"], "outputs": ["result2"], "next": ["task-005"]},
                {"id": "task-004", "name": "Process Task 3", "type": "process", "inputs": ["result1"], "outputs": ["result3"], "next": ["task-006"]},
                {"id": "task-005", "name": "Process Task 4", "type": "process", "inputs": ["result2"], "outputs": ["result4"], "next": ["task-007"]},
                {"id": "task-006", "name": "Process Task 5", "type": "process", "inputs": ["result3"], "outputs": ["result5"], "next": ["task-007"]},
                {"id": "task-007", "name": "End Task", "type": "end", "inputs": ["result4", "result5"]}
            ]
        }
        
        workflow_id = cascade_workflow["id"]
        self.workflow_runtime.create_workflow(cascade_workflow)
        
        # Configure the chaos tester to simulate cascading failures
        cascade_config = {
            "failure_type": "cascading_failure",
            "initial_failure": "task-003",
            "cascade_probability": 0.7,  # 70% chance of cascade to dependent tasks
            "duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test(workflow_id, cascade_config)
        
        # Configure the fallback agent with circuit breaker pattern
        fallback_config = {
            "workflow_id": workflow_id,
            "retry_limit": 3,
            "fallback_strategy": "circuit_breaker"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Wait for cascading failure test to end
        time.sleep(3)
        
        # Check if the execution eventually completed
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertEqual(execution["status"], "completed")


class TestAgentChaosTesting(unittest.TestCase):
    """Chaos tests for the agent framework components."""
    
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
        
        # Create chaos tester agent
        self.chaos_tester = WorkflowChaosTesterAgent(
            agent_id="chaos-tester-001",
            workflow_runtime=self.workflow_runtime
        )
        
        # Create fallback agent
        self.fallback_agent = WorkflowFallbackAgent(
            agent_id="fallback-agent-001",
            workflow_runtime=self.workflow_runtime
        )
    
    def test_agent_communication_disruption(self):
        """Test the system's resilience to agent communication disruptions."""
        # Configure the workflow runtime mock
        self.workflow_runtime.get_workflow.return_value = {
            "id": "workflow-001",
            "tasks": [{"id": "task-001", "type": "process"}]
        }
        
        # Configure the chaos tester to simulate communication disruptions
        disruption_config = {
            "failure_type": "communication_disruption",
            "target_agents": ["trigger-agent-001", "contract-parser-001"],
            "disruption_rate": 0.5,  # 50% of messages lost
            "duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test("workflow-001", disruption_config)
        
        # Configure the fallback agent to handle communication disruptions
        fallback_config = {
            "workflow_id": "workflow-001",
            "retry_limit": 3,
            "fallback_strategy": "message_retry"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Simulate agent communication
        for i in range(10):
            message = {
                "id": f"message-{i:03d}",
                "type": "task_assignment",
                "task_id": "task-001",
                "data": {"input": f"value-{i}"}
            }
            
            # Attempt to send message with potential disruption
            if not self.chaos_tester.should_disrupt_communication("trigger-agent-001", "contract-parser-001"):
                self.contract_parser.handle_message(message)
        
        # Wait for disruption test to end
        time.sleep(3)
        
        # Verify that the fallback agent handled the disruptions
        self.fallback_agent.handle_communication_failure.assert_called()
    
    def test_agent_overload(self):
        """Test the system's resilience to agent overload."""
        # Configure the workflow runtime mock
        self.workflow_runtime.get_workflow.return_value = {
            "id": "workflow-001",
            "tasks": [{"id": "task-001", "type": "process"}]
        }
        
        # Configure the chaos tester to simulate agent overload
        overload_config = {
            "failure_type": "agent_overload",
            "target_agents": ["human-agent-001"],
            "request_multiplier": 10,  # 10x normal load
            "duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test("workflow-001", overload_config)
        
        # Configure the fallback agent to handle overload
        fallback_config = {
            "workflow_id": "workflow-001",
            "retry_limit": 3,
            "fallback_strategy": "load_shedding"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Simulate high load of intervention requests
        num_requests = 100
        processed_requests = 0
        
        for i in range(num_requests):
            if not self.chaos_tester.is_agent_overloaded("human-agent-001"):
                # Agent can process the request
                self.human_agent.request_intervention(
                    "workflow-001", "task-001", "Test intervention", {"data": f"value-{i}"}
                )
                processed_requests += 1
        
        # Wait for overload test to end
        time.sleep(3)
        
        # Verify that load shedding occurred (not all requests were processed)
        self.assertLess(processed_requests, num_requests)
        print(f"Processed {processed_requests} out of {num_requests} requests during overload")
    
    def test_agent_state_corruption(self):
        """Test the system's resilience to agent state corruption."""
        # Configure the workflow runtime mock
        self.workflow_runtime.get_workflow.return_value = {
            "id": "workflow-001",
            "tasks": [{"id": "task-001", "type": "process"}]
        }
        
        # Configure the chaos tester to simulate state corruption
        corruption_config = {
            "failure_type": "state_corruption",
            "target_agents": ["capsule-controller-001"],
            "corruption_fields": ["active_capsules", "execution_modes"],
            "corruption_rate": 0.3,  # 30% of fields corrupted
            "duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test("workflow-001", corruption_config)
        
        # Configure the fallback agent to handle state corruption
        fallback_config = {
            "workflow_id": "workflow-001",
            "retry_limit": 3,
            "fallback_strategy": "state_recovery"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Create capsules that might experience state corruption
        num_capsules = 10
        capsule_ids = []
        
        for i in range(num_capsules):
            capsule_config = {
                "id": f"capsule-{i:03d}",
                "type": "workflow",
                "workflow_id": "workflow-001",
                "execution_mode": "autonomous"
            }
            capsule_id = self.capsule_controller.create_capsule(capsule_config)
            capsule_ids.append(capsule_id)
        
        # Wait for corruption test to end
        time.sleep(3)
        
        # Attempt to recover from corruption
        recovered_capsules = self.fallback_agent.recover_agent_state("capsule-controller-001")
        
        # Verify that at least some capsules were recovered
        self.assertGreater(len(recovered_capsules), 0)
        print(f"Recovered {len(recovered_capsules)} out of {num_capsules} capsules after state corruption")
    
    def test_agent_priority_inversion(self):
        """Test the system's resilience to agent priority inversion."""
        # Configure the workflow runtime mock
        self.workflow_runtime.get_workflow.return_value = {
            "id": "workflow-001",
            "tasks": [
                {"id": "task-001", "type": "process", "priority": "high"},
                {"id": "task-002", "type": "process", "priority": "medium"},
                {"id": "task-003", "type": "process", "priority": "low"}
            ]
        }
        
        # Configure the chaos tester to simulate priority inversion
        inversion_config = {
            "failure_type": "priority_inversion",
            "target_agents": ["trigger-agent-001"],
            "inversion_probability": 0.8,  # 80% chance of priority inversion
            "duration": 2  # seconds
        }
        self.chaos_tester.configure_chaos_test("workflow-001", inversion_config)
        
        # Configure the fallback agent to handle priority inversion
        fallback_config = {
            "workflow_id": "workflow-001",
            "retry_limit": 3,
            "fallback_strategy": "priority_inheritance"
        }
        self.fallback_agent.configure_fallback(fallback_config)
        
        # Simulate task processing with potential priority inversion
        tasks = [
            {"id": "task-001", "priority": "high"},
            {"id": "task-002", "priority": "medium"},
            {"id": "task-003", "priority": "low"}
        ]
        
        # Process tasks with potential priority inversion
        processed_tasks = []
        for task in tasks:
            if not self.chaos_tester.should_invert_priority(task):
                # Process task with original priority
                processed_tasks.append(task)
            else:
                # Process task with inverted priority
                inverted_task = task.copy()
                inverted_task["priority"] = "low" if task["priority"] == "high" else "high"
                processed_tasks.append(inverted_task)
        
        # Wait for inversion test to end
        time.sleep(3)
        
        # Verify that the fallback agent corrected the priority inversion
        corrected_tasks = self.fallback_agent.correct_priority_inversion(processed_tasks)
        
        # Check that high priority tasks are processed first
        self.assertEqual(corrected_tasks[0]["priority"], "high")


if __name__ == '__main__':
    unittest.main()
