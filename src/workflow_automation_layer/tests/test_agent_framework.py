"""
Test suite for the Workflow Automation Layer Agent Framework components.

This module contains unit tests for the agent framework components,
including base agent, workflow trigger agent, human intervention agent, etc.
"""

import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from agents.workflow_trigger_agent import WorkflowTriggerAgent
from agents.workflow_contract_parser import WorkflowContractParser
from agents.human_intervention_agent import HumanInterventionAgent
from agents.capsule_workflow_controller import CapsuleWorkflowController
from agents.n8n_sync_bridge import N8nSyncBridge
from agents.workflow_optimizer import WorkflowOptimizer


class TestBaseAgent(unittest.TestCase):
    """Test cases for the BaseAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.agent = BaseAgent("agent1", "Test Agent", "test")
        self.agent.initialize({
            "trust_score": 0.8,
            "confidence_score": 0.85,
            "execution_mode": "reactive"
        })

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.agent_id, "agent1")
        self.assertEqual(self.agent.name, "Test Agent")
        self.assertEqual(self.agent.agent_type, "test")
        self.assertEqual(self.agent.trust_score, 0.8)
        self.assertEqual(self.agent.confidence_score, 0.85)
        self.assertEqual(self.agent.execution_mode, "reactive")

    def test_update_scores(self):
        """Test updating trust and confidence scores."""
        self.agent.update_scores(0.9, 0.95)
        self.assertEqual(self.agent.trust_score, 0.9)
        self.assertEqual(self.agent.confidence_score, 0.95)

    def test_set_execution_mode(self):
        """Test setting execution mode."""
        self.agent.set_execution_mode("proactive")
        self.assertEqual(self.agent.execution_mode, "proactive")

    def test_register_capability(self):
        """Test registering a capability."""
        self.agent.register_capability("data_processing", {
            "description": "Process data",
            "parameters": {
                "data_type": "string",
                "algorithm": "string"
            }
        })
        
        self.assertIn("data_processing", self.agent.capabilities)
        self.assertEqual(self.agent.capabilities["data_processing"]["description"], "Process data")

    @patch.object(BaseAgent, '_execute_task')
    async def test_process_task(self, mock_execute):
        """Test processing a task."""
        # Setup mock
        mock_execute.return_value = {"status": "success", "result": "test_result"}
        
        # Create a task
        task = {
            "task_id": "task1",
            "workflow_id": "workflow1",
            "action": "test_action",
            "parameters": {"param1": "value1"},
            "deadline": "2025-05-22T16:00:00Z"
        }
        
        # Process the task
        result = await self.agent.process_task(task)
        
        # Verify the result
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["result"], "test_result")
        
        # Verify the mock was called
        mock_execute.assert_called_once_with(task)

    @patch.object(BaseAgent, '_execute_task')
    async def test_process_task_error(self, mock_execute):
        """Test processing a task with an error."""
        # Setup mock to raise an exception
        mock_execute.side_effect = Exception("Test error")
        
        # Create a task
        task = {
            "task_id": "task1",
            "workflow_id": "workflow1",
            "action": "test_action",
            "parameters": {"param1": "value1"},
            "deadline": "2025-05-22T16:00:00Z"
        }
        
        # Process the task
        result = await self.agent.process_task(task)
        
        # Verify the result
        self.assertEqual(result["status"], "error")
        self.assertIn("Test error", result["error"])


class TestWorkflowTriggerAgent(unittest.TestCase):
    """Test cases for the WorkflowTriggerAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_registry = MagicMock()
        self.workflow_runtime = MagicMock()
        
        self.agent = WorkflowTriggerAgent(
            "trigger1",
            "Workflow Trigger Agent",
            self.workflow_registry,
            self.workflow_runtime
        )
        
        self.agent.initialize({
            "trust_score": 0.8,
            "confidence_score": 0.85,
            "execution_mode": "reactive"
        })

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.agent_id, "trigger1")
        self.assertEqual(self.agent.name, "Workflow Trigger Agent")
        self.assertEqual(self.agent.agent_type, "workflow_trigger")
        self.assertEqual(self.agent.trust_score, 0.8)
        self.assertEqual(self.agent.confidence_score, 0.85)
        self.assertEqual(self.agent.execution_mode, "reactive")

    def test_register_trigger(self):
        """Test registering a workflow trigger."""
        trigger_config = {
            "workflow_id": "workflow1",
            "trigger_type": "event",
            "event_source": "sensor",
            "event_type": "threshold_exceeded",
            "parameters": {
                "threshold": 100,
                "sensor_id": "sensor1"
            }
        }
        
        result = self.agent.register_trigger(trigger_config)
        self.assertTrue(result["success"])
        self.assertIn("trigger_id", result)
        
        # Verify the trigger was registered
        self.assertIn(result["trigger_id"], self.agent.triggers)
        self.assertEqual(self.agent.triggers[result["trigger_id"]]["workflow_id"], "workflow1")

    @patch.object(WorkflowTriggerAgent, '_evaluate_trigger_condition')
    async def test_process_event(self, mock_evaluate):
        """Test processing an event."""
        # Setup mock
        mock_evaluate.return_value = True
        
        # Register a trigger
        trigger_config = {
            "workflow_id": "workflow1",
            "trigger_type": "event",
            "event_source": "sensor",
            "event_type": "threshold_exceeded",
            "parameters": {
                "threshold": 100,
                "sensor_id": "sensor1"
            }
        }
        
        trigger_result = self.agent.register_trigger(trigger_config)
        trigger_id = trigger_result["trigger_id"]
        
        # Create an event
        event = {
            "event_source": "sensor",
            "event_type": "threshold_exceeded",
            "data": {
                "sensor_id": "sensor1",
                "value": 150
            },
            "timestamp": "2025-05-22T15:30:00Z"
        }
        
        # Process the event
        result = await self.agent.process_event(event)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(len(result["triggered_workflows"]), 1)
        self.assertEqual(result["triggered_workflows"][0]["workflow_id"], "workflow1")
        self.assertEqual(result["triggered_workflows"][0]["trigger_id"], trigger_id)
        
        # Verify the workflow was started
        self.workflow_runtime.start_workflow.assert_called_once_with(
            "workflow1",
            {
                "trigger_id": trigger_id,
                "event": event
            },
            self.agent.execution_mode
        )

    @patch.object(WorkflowTriggerAgent, '_evaluate_trigger_condition')
    async def test_process_event_no_match(self, mock_evaluate):
        """Test processing an event with no matching triggers."""
        # Setup mock
        mock_evaluate.return_value = False
        
        # Register a trigger
        trigger_config = {
            "workflow_id": "workflow1",
            "trigger_type": "event",
            "event_source": "sensor",
            "event_type": "threshold_exceeded",
            "parameters": {
                "threshold": 100,
                "sensor_id": "sensor1"
            }
        }
        
        self.agent.register_trigger(trigger_config)
        
        # Create an event with different type
        event = {
            "event_source": "sensor",
            "event_type": "status_change",  # Different event type
            "data": {
                "sensor_id": "sensor1",
                "status": "offline"
            },
            "timestamp": "2025-05-22T15:30:00Z"
        }
        
        # Process the event
        result = await self.agent.process_event(event)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertEqual(len(result["triggered_workflows"]), 0)
        
        # Verify the workflow was not started
        self.workflow_runtime.start_workflow.assert_not_called()


class TestHumanInterventionAgent(unittest.TestCase):
    """Test cases for the HumanInterventionAgent class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_runtime = MagicMock()
        
        self.agent = HumanInterventionAgent(
            "human1",
            "Human Intervention Agent",
            self.workflow_runtime
        )
        
        self.agent.initialize({
            "trust_score": 0.9,
            "confidence_score": 0.95,
            "execution_mode": "reactive"
        })

    def test_initialization(self):
        """Test agent initialization."""
        self.assertEqual(self.agent.agent_id, "human1")
        self.assertEqual(self.agent.name, "Human Intervention Agent")
        self.assertEqual(self.agent.agent_type, "human_intervention")
        self.assertEqual(self.agent.trust_score, 0.9)
        self.assertEqual(self.agent.confidence_score, 0.95)
        self.assertEqual(self.agent.execution_mode, "reactive")

    async def test_create_intervention_request(self):
        """Test creating an intervention request."""
        request_data = {
            "workflow_id": "workflow1",
            "task_id": "task1",
            "title": "Approval Required",
            "description": "Please approve this action",
            "options": ["approve", "reject"],
            "deadline": "2025-05-22T16:00:00Z",
            "priority": "high",
            "context": {
                "entity_id": "entity1",
                "action": "delete"
            }
        }
        
        result = await self.agent.create_intervention_request(request_data)
        self.assertTrue(result["success"])
        self.assertIn("request_id", result)
        
        # Verify the request was created
        request_id = result["request_id"]
        self.assertIn(request_id, self.agent.intervention_requests)
        self.assertEqual(self.agent.intervention_requests[request_id]["status"], "pending")

    async def test_submit_intervention_response(self):
        """Test submitting an intervention response."""
        # Create a request first
        request_data = {
            "workflow_id": "workflow1",
            "task_id": "task1",
            "title": "Approval Required",
            "description": "Please approve this action",
            "options": ["approve", "reject"],
            "deadline": "2025-05-22T16:00:00Z",
            "priority": "high",
            "context": {
                "entity_id": "entity1",
                "action": "delete"
            }
        }
        
        create_result = await self.agent.create_intervention_request(request_data)
        request_id = create_result["request_id"]
        
        # Submit a response
        response_data = {
            "request_id": request_id,
            "response": "approve",
            "comment": "Looks good",
            "responder_id": "user1"
        }
        
        result = await self.agent.submit_intervention_response(response_data)
        self.assertTrue(result["success"])
        
        # Verify the request was updated
        self.assertEqual(self.agent.intervention_requests[request_id]["status"], "completed")
        self.assertEqual(self.agent.intervention_requests[request_id]["response"], "approve")
        
        # Verify the workflow was resumed
        self.workflow_runtime.resume_workflow.assert_called_once_with(
            "workflow1",
            "task1",
            {
                "intervention_result": "approve",
                "comment": "Looks good",
                "responder_id": "user1"
            }
        )

    async def test_submit_intervention_response_invalid_request(self):
        """Test submitting a response for an invalid request."""
        # Submit a response for a non-existent request
        response_data = {
            "request_id": "non_existent",
            "response": "approve",
            "comment": "Looks good",
            "responder_id": "user1"
        }
        
        result = await self.agent.submit_intervention_response(response_data)
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])
        
        # Verify the workflow was not resumed
        self.workflow_runtime.resume_workflow.assert_not_called()

    async def test_get_pending_requests(self):
        """Test getting pending intervention requests."""
        # Create multiple requests
        for i in range(3):
            await self.agent.create_intervention_request({
                "workflow_id": f"workflow{i+1}",
                "task_id": f"task{i+1}",
                "title": f"Approval Required {i+1}",
                "description": f"Please approve this action {i+1}",
                "options": ["approve", "reject"],
                "deadline": "2025-05-22T16:00:00Z",
                "priority": "high",
                "context": {
                    "entity_id": f"entity{i+1}",
                    "action": "delete"
                }
            })
        
        # Get pending requests
        pending = self.agent.get_pending_requests()
        self.assertEqual(len(pending), 3)


class TestCapsuleWorkflowController(unittest.TestCase):
    """Test cases for the CapsuleWorkflowController class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_runtime = MagicMock()
        self.capsule_manager = MagicMock()
        
        self.controller = CapsuleWorkflowController(
            "controller1",
            "Capsule Workflow Controller",
            self.workflow_runtime,
            self.capsule_manager
        )
        
        self.controller.initialize({
            "trust_score": 0.85,
            "confidence_score": 0.9,
            "execution_mode": "reactive"
        })

    def test_initialization(self):
        """Test controller initialization."""
        self.assertEqual(self.controller.agent_id, "controller1")
        self.assertEqual(self.controller.name, "Capsule Workflow Controller")
        self.assertEqual(self.controller.agent_type, "capsule_workflow_controller")
        self.assertEqual(self.controller.trust_score, 0.85)
        self.assertEqual(self.controller.confidence_score, 0.9)
        self.assertEqual(self.controller.execution_mode, "reactive")

    async def test_create_workflow_capsule(self):
        """Test creating a workflow capsule."""
        workflow_info = {
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "status": "active",
            "progress": 0.0,
            "trust_score": 0.85,
            "confidence_score": 0.9,
            "execution_mode": "reactive"
        }
        
        # Mock the capsule manager's create_capsule method
        self.capsule_manager.create_capsule.return_value = {
            "capsule_id": "capsule1",
            "agent_id": "workflow1",
            "agent_name": "Test Workflow",
            "agent_type": "workflow"
        }
        
        result = await self.controller.create_workflow_capsule(workflow_info)
        self.assertTrue(result["success"])
        self.assertEqual(result["capsule_id"], "capsule1")
        
        # Verify the capsule manager was called
        self.capsule_manager.create_capsule.assert_called_once()
        args = self.capsule_manager.create_capsule.call_args[0]
        self.assertEqual(args[0], "workflow1")
        self.assertEqual(args[1], "Test Workflow")
        self.assertEqual(args[2], "workflow")

    async def test_update_workflow_capsule(self):
        """Test updating a workflow capsule."""
        update_info = {
            "workflow_id": "workflow1",
            "status": "running",
            "progress": 0.5,
            "current_task": "task2",
            "metrics": {
                "duration_ms": 1500,
                "tasks_completed": 1,
                "tasks_remaining": 2
            }
        }
        
        # Mock the capsule manager's update_capsule method
        self.capsule_manager.update_capsule.return_value = True
        
        result = await self.controller.update_workflow_capsule(update_info)
        self.assertTrue(result["success"])
        
        # Verify the capsule manager was called
        self.capsule_manager.update_capsule.assert_called_once()
        args = self.capsule_manager.update_capsule.call_args[0]
        self.assertEqual(args[0], "workflow1")
        self.assertEqual(args[1]["state"], "running")
        self.assertEqual(args[1]["context"]["progress"], 0.5)

    async def test_handle_workflow_event(self):
        """Test handling a workflow event."""
        event = {
            "event_type": "task_completed",
            "workflow_id": "workflow1",
            "task_id": "task1",
            "timestamp": "2025-05-22T15:30:00Z",
            "details": {
                "duration_ms": 1500,
                "result": "success"
            }
        }
        
        # Mock the capsule manager's update_capsule method
        self.capsule_manager.update_capsule.return_value = True
        
        result = await self.controller.handle_workflow_event(event)
        self.assertTrue(result["success"])
        
        # Verify the capsule manager was called
        self.capsule_manager.update_capsule.assert_called_once()


class TestN8nSyncBridge(unittest.TestCase):
    """Test cases for the N8nSyncBridge class."""

    def setUp(self):
        """Set up test fixtures."""
        self.n8n_connector = MagicMock()
        self.workflow_registry = MagicMock()
        
        self.bridge = N8nSyncBridge(
            "n8n_bridge",
            "n8n Sync Bridge",
            self.n8n_connector,
            self.workflow_registry
        )
        
        self.bridge.initialize({
            "trust_score": 0.8,
            "confidence_score": 0.85,
            "execution_mode": "reactive"
        })

    def test_initialization(self):
        """Test bridge initialization."""
        self.assertEqual(self.bridge.agent_id, "n8n_bridge")
        self.assertEqual(self.bridge.name, "n8n Sync Bridge")
        self.assertEqual(self.bridge.agent_type, "n8n_sync_bridge")
        self.assertEqual(self.bridge.trust_score, 0.8)
        self.assertEqual(self.bridge.confidence_score, 0.85)
        self.assertEqual(self.bridge.execution_mode, "reactive")

    async def test_sync_workflow_to_n8n(self):
        """Test syncing a workflow to n8n."""
        # Mock the workflow registry's get_workflow method
        self.workflow_registry.get_workflow.return_value = {
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "tasks": [
                {"task_id": "task1", "name": "Task 1"},
                {"task_id": "task2", "name": "Task 2"}
            ],
            "transitions": [
                {"from": "task1", "to": "task2", "condition": "success"}
            ]
        }
        
        # Mock the n8n connector's create_workflow method
        self.n8n_connector.create_workflow.return_value = {
            "id": "n8n123",
            "name": "Test Workflow"
        }
        
        result = await self.bridge.sync_workflow_to_n8n("workflow1")
        self.assertTrue(result["success"])
        self.assertEqual(result["n8n_workflow_id"], "n8n123")
        
        # Verify the n8n connector was called
        self.n8n_connector.create_workflow.assert_called_once()

    async def test_sync_workflow_from_n8n(self):
        """Test syncing a workflow from n8n."""
        # Mock the n8n connector's get_workflow method
        self.n8n_connector.get_workflow.return_value = {
            "id": "n8n123",
            "name": "Test Workflow",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start"},
                {"name": "Task 1", "type": "n8n-nodes-base.function"},
                {"name": "Task 2", "type": "n8n-nodes-base.function"}
            ],
            "connections": {
                "Start": {
                    "main": [[{"node": "Task 1", "type": "main", "index": 0}]]
                },
                "Task 1": {
                    "main": [[{"node": "Task 2", "type": "main", "index": 0}]]
                }
            }
        }
        
        # Mock the workflow registry's register_workflow method
        self.workflow_registry.register_workflow.return_value = {
            "success": True,
            "workflow_id": "workflow1"
        }
        
        result = await self.bridge.sync_workflow_from_n8n("n8n123", "workflow1")
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow_id"], "workflow1")
        
        # Verify the workflow registry was called
        self.workflow_registry.register_workflow.assert_called_once()

    async def test_handle_n8n_webhook(self):
        """Test handling an n8n webhook."""
        webhook_data = {
            "workflow_id": "n8n123",
            "execution_id": "exec456",
            "event_type": "workflow.started",
            "timestamp": "2025-05-22T15:30:00Z",
            "payload": {
                "workflow": {"id": "n8n123", "name": "Test Workflow"},
                "execution": {"id": "exec456", "status": "running"}
            }
        }
        
        # Mock the n8n connector's get_execution_data method
        self.n8n_connector.get_execution_data.return_value = {
            "id": "exec456",
            "status": "running",
            "data": {"input": {"param1": "value1"}}
        }
        
        result = await self.bridge.handle_n8n_webhook(webhook_data)
        self.assertTrue(result["success"])
        
        # Verify the n8n connector was called
        self.n8n_connector.get_execution_data.assert_called_once_with("n8n123", "exec456")


class TestWorkflowOptimizer(unittest.TestCase):
    """Test cases for the WorkflowOptimizer class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_registry = MagicMock()
        self.workflow_telemetry = MagicMock()
        
        self.optimizer = WorkflowOptimizer(
            "optimizer1",
            "Workflow Optimizer",
            self.workflow_registry,
            self.workflow_telemetry
        )
        
        self.optimizer.initialize({
            "trust_score": 0.85,
            "confidence_score": 0.9,
            "execution_mode": "proactive"
        })

    def test_initialization(self):
        """Test optimizer initialization."""
        self.assertEqual(self.optimizer.agent_id, "optimizer1")
        self.assertEqual(self.optimizer.name, "Workflow Optimizer")
        self.assertEqual(self.optimizer.agent_type, "workflow_optimizer")
        self.assertEqual(self.optimizer.trust_score, 0.85)
        self.assertEqual(self.optimizer.confidence_score, 0.9)
        self.assertEqual(self.optimizer.execution_mode, "proactive")

    async def test_analyze_workflow_performance(self):
        """Test analyzing workflow performance."""
        # Mock the workflow registry's get_workflow method
        self.workflow_registry.get_workflow.return_value = {
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "tasks": [
                {"task_id": "task1", "name": "Task 1"},
                {"task_id": "task2", "name": "Task 2"}
            ],
            "transitions": [
                {"from": "task1", "to": "task2", "condition": "success"}
            ]
        }
        
        # Mock the workflow telemetry's get_workflow_metrics method
        self.workflow_telemetry.get_workflow_metrics.return_value = {
            "workflow_id": "workflow1",
            "execution_count": 10,
            "average_duration_ms": 5000,
            "success_rate": 0.8,
            "task_metrics": {
                "task1": {
                    "average_duration_ms": 2000,
                    "success_rate": 0.9
                },
                "task2": {
                    "average_duration_ms": 3000,
                    "success_rate": 0.8
                }
            }
        }
        
        result = await self.optimizer.analyze_workflow_performance("workflow1")
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow_id"], "workflow1")
        self.assertIn("metrics", result)
        self.assertIn("bottlenecks", result)
        self.assertIn("recommendations", result)

    async def test_generate_optimization_recommendations(self):
        """Test generating optimization recommendations."""
        # Mock the workflow registry's get_workflow method
        self.workflow_registry.get_workflow.return_value = {
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "tasks": [
                {"task_id": "task1", "name": "Task 1"},
                {"task_id": "task2", "name": "Task 2"}
            ],
            "transitions": [
                {"from": "task1", "to": "task2", "condition": "success"}
            ]
        }
        
        # Mock the workflow telemetry's get_workflow_metrics method
        self.workflow_telemetry.get_workflow_metrics.return_value = {
            "workflow_id": "workflow1",
            "execution_count": 10,
            "average_duration_ms": 5000,
            "success_rate": 0.8,
            "task_metrics": {
                "task1": {
                    "average_duration_ms": 2000,
                    "success_rate": 0.9
                },
                "task2": {
                    "average_duration_ms": 3000,
                    "success_rate": 0.8
                }
            }
        }
        
        analysis = {
            "workflow_id": "workflow1",
            "metrics": {
                "execution_count": 10,
                "average_duration_ms": 5000,
                "success_rate": 0.8
            },
            "bottlenecks": [
                {
                    "task_id": "task2",
                    "issue": "high_failure_rate",
                    "details": {
                        "success_rate": 0.8,
                        "threshold": 0.9
                    }
                }
            ]
        }
        
        result = await self.optimizer.generate_optimization_recommendations(analysis)
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow_id"], "workflow1")
        self.assertGreater(len(result["recommendations"]), 0)

    async def test_apply_optimization(self):
        """Test applying an optimization."""
        optimization = {
            "workflow_id": "workflow1",
            "optimization_type": "retry_policy",
            "target_task_id": "task2",
            "changes": {
                "retry_count": 5,
                "retry_interval_seconds": 30
            }
        }
        
        # Mock the workflow registry's get_workflow and update_workflow methods
        self.workflow_registry.get_workflow.return_value = {
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "tasks": [
                {"task_id": "task1", "name": "Task 1"},
                {
                    "task_id": "task2",
                    "name": "Task 2",
                    "retry_count": 3,
                    "retry_interval_seconds": 60
                }
            ],
            "transitions": [
                {"from": "task1", "to": "task2", "condition": "success"}
            ]
        }
        
        self.workflow_registry.update_workflow.return_value = {
            "success": True,
            "workflow_id": "workflow1"
        }
        
        result = await self.optimizer.apply_optimization(optimization)
        self.assertTrue(result["success"])
        
        # Verify the workflow registry was called
        self.workflow_registry.update_workflow.assert_called_once()
        args = self.workflow_registry.update_workflow.call_args[0]
        self.assertEqual(args[0], "workflow1")
        
        # Verify the task was updated
        updated_workflow = args[1]
        updated_task = next(t for t in updated_workflow["tasks"] if t["task_id"] == "task2")
        self.assertEqual(updated_task["retry_count"], 5)
        self.assertEqual(updated_task["retry_interval_seconds"], 30)


if __name__ == "__main__":
    unittest.main()
