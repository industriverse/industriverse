"""
Test suite for the Workflow Automation Layer UI and Security components.

This module contains unit tests for the UI and security components,
including dynamic agent capsule, workflow visualization, and security compliance.
"""

import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.dynamic_agent_capsule import DynamicAgentCapsule
from ui.workflow_visualization import WorkflowVisualization
from security.security_compliance_observability import SecurityComplianceManager


class TestDynamicAgentCapsule(unittest.TestCase):
    """Test cases for the DynamicAgentCapsule class."""

    def setUp(self):
        """Set up test fixtures."""
        self.capsule_manager = MagicMock()
        self.capsule = DynamicAgentCapsule(
            "capsule1",
            "Test Capsule",
            "workflow",
            self.capsule_manager
        )

    def test_initialization(self):
        """Test capsule initialization."""
        self.assertEqual(self.capsule.capsule_id, "capsule1")
        self.assertEqual(self.capsule.name, "Test Capsule")
        self.assertEqual(self.capsule.type, "workflow")
        self.assertEqual(self.capsule.state, "idle")
        self.assertEqual(self.capsule.position, "floating")
        self.assertIsNone(self.capsule.parent_element)

    def test_update_state(self):
        """Test updating capsule state."""
        # Update the state
        self.capsule.update_state("running")
        self.assertEqual(self.capsule.state, "running")
        
        # Update with invalid state
        with self.assertRaises(ValueError):
            self.capsule.update_state("invalid_state")

    def test_update_context(self):
        """Test updating capsule context."""
        # Update the context
        context = {
            "workflow_id": "workflow1",
            "progress": 0.5,
            "current_task": "task2",
            "metrics": {
                "duration_ms": 1500,
                "tasks_completed": 1,
                "tasks_remaining": 2
            }
        }
        
        self.capsule.update_context(context)
        self.assertEqual(self.capsule.context, context)
        self.assertEqual(self.capsule.context["progress"], 0.5)

    def test_set_position(self):
        """Test setting capsule position."""
        # Set to docked position
        self.capsule.set_position("docked", "sidebar")
        self.assertEqual(self.capsule.position, "docked")
        self.assertEqual(self.capsule.parent_element, "sidebar")
        
        # Set to floating position
        self.capsule.set_position("floating")
        self.assertEqual(self.capsule.position, "floating")
        self.assertIsNone(self.capsule.parent_element)
        
        # Set with invalid position
        with self.assertRaises(ValueError):
            self.capsule.set_position("invalid_position")

    def test_get_actions(self):
        """Test getting available actions."""
        # Set up the capsule state and context
        self.capsule.update_state("running")
        self.capsule.update_context({
            "workflow_id": "workflow1",
            "progress": 0.5,
            "current_task": "task2"
        })
        
        # Get available actions
        actions = self.capsule.get_actions()
        self.assertIsInstance(actions, list)
        self.assertGreater(len(actions), 0)
        
        # Check for specific actions based on state
        action_ids = [action["id"] for action in actions]
        self.assertIn("pause", action_ids)
        self.assertIn("stop", action_ids)
        
        # Change state and check actions again
        self.capsule.update_state("paused")
        actions = self.capsule.get_actions()
        action_ids = [action["id"] for action in actions]
        self.assertIn("resume", action_ids)
        self.assertIn("stop", action_ids)

    def test_execute_action(self):
        """Test executing an action."""
        # Set up the capsule state and context
        self.capsule.update_state("running")
        self.capsule.update_context({
            "workflow_id": "workflow1",
            "progress": 0.5,
            "current_task": "task2"
        })
        
        # Mock the capsule manager's execute_action method
        self.capsule_manager.execute_action.return_value = {
            "success": True,
            "action": "pause",
            "result": "Workflow paused"
        }
        
        # Execute an action
        result = self.capsule.execute_action("pause")
        self.assertTrue(result["success"])
        self.assertEqual(result["action"], "pause")
        
        # Verify the capsule manager was called
        self.capsule_manager.execute_action.assert_called_once_with(
            "capsule1",
            "pause",
            {}
        )

    def test_render_capsule(self):
        """Test rendering the capsule."""
        # Set up the capsule state and context
        self.capsule.update_state("running")
        self.capsule.update_context({
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "progress": 0.5,
            "current_task": "task2",
            "metrics": {
                "duration_ms": 1500,
                "tasks_completed": 1,
                "tasks_remaining": 2
            }
        })
        
        # Render the capsule
        render_data = self.capsule.render()
        
        # Verify the render data
        self.assertEqual(render_data["capsule_id"], "capsule1")
        self.assertEqual(render_data["name"], "Test Capsule")
        self.assertEqual(render_data["type"], "workflow")
        self.assertEqual(render_data["state"], "running")
        self.assertEqual(render_data["position"], "floating")
        self.assertIn("context", render_data)
        self.assertIn("actions", render_data)
        self.assertIn("ui_components", render_data)


class TestWorkflowVisualization(unittest.TestCase):
    """Test cases for the WorkflowVisualization class."""

    def setUp(self):
        """Set up test fixtures."""
        self.workflow_registry = MagicMock()
        self.workflow_telemetry = MagicMock()
        
        self.visualization = WorkflowVisualization(
            self.workflow_registry,
            self.workflow_telemetry
        )

    def test_generate_workflow_graph(self):
        """Test generating a workflow graph."""
        # Mock the workflow registry's get_workflow method
        self.workflow_registry.get_workflow.return_value = {
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "tasks": [
                {"task_id": "task1", "name": "Task 1"},
                {"task_id": "task2", "name": "Task 2"},
                {"task_id": "task3", "name": "Task 3"}
            ],
            "transitions": [
                {"from": "task1", "to": "task2", "condition": "success"},
                {"from": "task2", "to": "task3", "condition": "success"},
                {"from": "task2", "to": "task1", "condition": "failure"}
            ]
        }
        
        # Generate the graph
        graph = self.visualization.generate_workflow_graph("workflow1")
        
        # Verify the graph structure
        self.assertEqual(graph["workflow_id"], "workflow1")
        self.assertEqual(graph["name"], "Test Workflow")
        self.assertEqual(len(graph["nodes"]), 3)
        self.assertEqual(len(graph["edges"]), 3)
        
        # Check node properties
        node_ids = [node["id"] for node in graph["nodes"]]
        self.assertIn("task1", node_ids)
        self.assertIn("task2", node_ids)
        self.assertIn("task3", node_ids)
        
        # Check edge properties
        for edge in graph["edges"]:
            self.assertIn(edge["source"], ["task1", "task2"])
            self.assertIn(edge["target"], ["task1", "task2", "task3"])
            self.assertIn("condition", edge)

    def test_generate_workflow_timeline(self):
        """Test generating a workflow timeline."""
        # Mock the workflow telemetry's get_workflow_execution_history method
        self.workflow_telemetry.get_workflow_execution_history.return_value = {
            "workflow_id": "workflow1",
            "executions": [
                {
                    "execution_id": "exec1",
                    "start_time": "2025-05-22T15:00:00Z",
                    "end_time": "2025-05-22T15:05:00Z",
                    "status": "success",
                    "tasks": [
                        {
                            "task_id": "task1",
                            "start_time": "2025-05-22T15:00:00Z",
                            "end_time": "2025-05-22T15:02:00Z",
                            "status": "success"
                        },
                        {
                            "task_id": "task2",
                            "start_time": "2025-05-22T15:02:00Z",
                            "end_time": "2025-05-22T15:05:00Z",
                            "status": "success"
                        }
                    ]
                },
                {
                    "execution_id": "exec2",
                    "start_time": "2025-05-22T15:10:00Z",
                    "end_time": "2025-05-22T15:16:00Z",
                    "status": "failure",
                    "tasks": [
                        {
                            "task_id": "task1",
                            "start_time": "2025-05-22T15:10:00Z",
                            "end_time": "2025-05-22T15:12:00Z",
                            "status": "success"
                        },
                        {
                            "task_id": "task2",
                            "start_time": "2025-05-22T15:12:00Z",
                            "end_time": "2025-05-22T15:16:00Z",
                            "status": "failure"
                        }
                    ]
                }
            ]
        }
        
        # Generate the timeline
        timeline = self.visualization.generate_workflow_timeline("workflow1")
        
        # Verify the timeline structure
        self.assertEqual(timeline["workflow_id"], "workflow1")
        self.assertEqual(len(timeline["executions"]), 2)
        
        # Check execution properties
        self.assertEqual(timeline["executions"][0]["execution_id"], "exec1")
        self.assertEqual(timeline["executions"][0]["status"], "success")
        self.assertEqual(len(timeline["executions"][0]["tasks"]), 2)
        
        self.assertEqual(timeline["executions"][1]["execution_id"], "exec2")
        self.assertEqual(timeline["executions"][1]["status"], "failure")
        self.assertEqual(len(timeline["executions"][1]["tasks"]), 2)

    def test_generate_workflow_metrics_dashboard(self):
        """Test generating a workflow metrics dashboard."""
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
        
        # Generate the dashboard
        dashboard = self.visualization.generate_workflow_metrics_dashboard("workflow1")
        
        # Verify the dashboard structure
        self.assertEqual(dashboard["workflow_id"], "workflow1")
        self.assertEqual(dashboard["metrics"]["execution_count"], 10)
        self.assertEqual(dashboard["metrics"]["average_duration_ms"], 5000)
        self.assertEqual(dashboard["metrics"]["success_rate"], 0.8)
        
        # Check task metrics
        self.assertIn("task1", dashboard["task_metrics"])
        self.assertIn("task2", dashboard["task_metrics"])
        self.assertEqual(dashboard["task_metrics"]["task1"]["average_duration_ms"], 2000)
        self.assertEqual(dashboard["task_metrics"]["task1"]["success_rate"], 0.9)
        
        # Check visualization components
        self.assertIn("charts", dashboard)
        self.assertGreater(len(dashboard["charts"]), 0)

    def test_export_workflow_visualization(self):
        """Test exporting a workflow visualization."""
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
        
        # Export formats to test
        formats = ["json", "svg", "png"]
        
        for format_type in formats:
            # Export the visualization
            result = self.visualization.export_workflow_visualization("workflow1", format_type)
            
            # Verify the result
            self.assertTrue(result["success"])
            self.assertEqual(result["workflow_id"], "workflow1")
            self.assertEqual(result["format"], format_type)
            self.assertIn("data", result)


class TestSecurityComplianceManager(unittest.TestCase):
    """Test cases for the SecurityComplianceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            "ekis_security_enabled": True,
            "ekis_api_url": "http://ekis-service:8080/api",
            "ekis_api_key": "test_api_key",
            "trust_threshold": 0.7,
            "compliance_frameworks": ["GDPR", "ISO27001"],
            "audit_log_retention_days": 90
        }
        
        self.manager = SecurityComplianceManager(self.config)

    def test_initialization(self):
        """Test manager initialization."""
        self.assertTrue(self.manager.ekis_security_enabled)
        self.assertEqual(self.manager.ekis_api_url, "http://ekis-service:8080/api")
        self.assertEqual(self.manager.trust_threshold, 0.7)
        self.assertIn("GDPR", self.manager.compliance_frameworks)
        self.assertIn("ISO27001", self.manager.compliance_frameworks)

    @patch('security.security_compliance_observability.requests.post')
    def test_validate_trust_score(self, mock_post):
        """Test validating a trust score."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "valid": True,
            "trust_score": 0.85,
            "confidence_score": 0.9,
            "verification_id": "verify123"
        }
        mock_post.return_value = mock_response
        
        # Trust data to validate
        trust_data = {
            "entity_id": "agent1",
            "entity_type": "agent",
            "claimed_trust_score": 0.85,
            "claimed_confidence_score": 0.9,
            "context": {
                "workflow_id": "workflow1",
                "task_id": "task1"
            }
        }
        
        # Validate the trust score
        result = self.manager.validate_trust_score(trust_data)
        
        # Verify the result
        self.assertTrue(result["valid"])
        self.assertEqual(result["trust_score"], 0.85)
        self.assertEqual(result["confidence_score"], 0.9)
        
        # Verify the request was made correctly
        mock_post.assert_called_once_with(
            "http://ekis-service:8080/api/trust/validate",
            headers={
                "X-EKIS-API-KEY": "test_api_key",
                "Content-Type": "application/json"
            },
            json=trust_data
        )

    def test_check_execution_mode_compliance(self):
        """Test checking execution mode compliance."""
        # Test with compliant execution mode
        result = self.manager.check_execution_mode_compliance(
            "reactive",
            0.8,
            0.85,
            ["GDPR"]
        )
        self.assertTrue(result["compliant"])
        
        # Test with non-compliant execution mode (trust score too low)
        result = self.manager.check_execution_mode_compliance(
            "autonomous",
            0.6,  # Below threshold for autonomous mode
            0.95,
            ["GDPR"]
        )
        self.assertFalse(result["compliant"])
        self.assertIn("trust_score", result["violations"])
        
        # Test with non-compliant execution mode (confidence score too low)
        result = self.manager.check_execution_mode_compliance(
            "autonomous",
            0.95,
            0.7,  # Below threshold for autonomous mode
            ["GDPR"]
        )
        self.assertFalse(result["compliant"])
        self.assertIn("confidence_score", result["violations"])

    def test_log_audit_event(self):
        """Test logging an audit event."""
        # Event data
        event_data = {
            "event_type": "workflow_started",
            "workflow_id": "workflow1",
            "user_id": "user1",
            "timestamp": "2025-05-22T15:30:00Z",
            "details": {
                "execution_mode": "reactive",
                "trust_score": 0.8,
                "confidence_score": 0.85
            }
        }
        
        # Log the event
        result = self.manager.log_audit_event(event_data)
        
        # Verify the result
        self.assertTrue(result["success"])
        self.assertIn("event_id", result)
        
        # Verify the event was stored
        event_id = result["event_id"]
        self.assertIn(event_id, self.manager.audit_log)
        self.assertEqual(self.manager.audit_log[event_id]["event_type"], "workflow_started")
        self.assertEqual(self.manager.audit_log[event_id]["workflow_id"], "workflow1")

    def test_query_audit_log(self):
        """Test querying the audit log."""
        # Add some events to the audit log
        for i in range(5):
            self.manager.log_audit_event({
                "event_type": "workflow_started" if i % 2 == 0 else "workflow_completed",
                "workflow_id": f"workflow{i % 3 + 1}",
                "user_id": "user1",
                "timestamp": f"2025-05-22T{15+i}:30:00Z",
                "details": {
                    "execution_mode": "reactive",
                    "trust_score": 0.8,
                    "confidence_score": 0.85
                }
            })
        
        # Query for workflow_started events
        query = {
            "event_type": "workflow_started",
            "time_range": {
                "start": "2025-05-22T00:00:00Z",
                "end": "2025-05-23T00:00:00Z"
            }
        }
        
        results = self.manager.query_audit_log(query)
        
        # Verify the results
        self.assertEqual(len(results), 3)  # 3 workflow_started events
        for event in results:
            self.assertEqual(event["event_type"], "workflow_started")
        
        # Query for a specific workflow
        query = {
            "workflow_id": "workflow1",
            "time_range": {
                "start": "2025-05-22T00:00:00Z",
                "end": "2025-05-23T00:00:00Z"
            }
        }
        
        results = self.manager.query_audit_log(query)
        
        # Verify the results
        for event in results:
            self.assertEqual(event["workflow_id"], "workflow1")

    def test_generate_compliance_report(self):
        """Test generating a compliance report."""
        # Add some events to the audit log
        for i in range(10):
            self.manager.log_audit_event({
                "event_type": ["workflow_started", "workflow_completed", "task_started", "task_completed", "human_intervention"][i % 5],
                "workflow_id": f"workflow{i % 3 + 1}",
                "user_id": "user1",
                "timestamp": f"2025-05-22T{15+i//2}:30:00Z",
                "details": {
                    "execution_mode": "reactive" if i % 3 != 0 else "autonomous",
                    "trust_score": 0.8 if i % 4 != 0 else 0.6,
                    "confidence_score": 0.85 if i % 4 != 0 else 0.7
                }
            })
        
        # Generate a compliance report for GDPR
        report = self.manager.generate_compliance_report("GDPR", {
            "start_date": "2025-05-22T00:00:00Z",
            "end_date": "2025-05-23T00:00:00Z"
        })
        
        # Verify the report structure
        self.assertEqual(report["compliance_framework"], "GDPR")
        self.assertIn("compliance_score", report)
        self.assertIn("violations", report)
        self.assertIn("recommendations", report)
        self.assertIn("audit_events", report)
        
        # Check for specific sections in the report
        self.assertIn("data_processing_events", report["sections"])
        self.assertIn("human_oversight_events", report["sections"])
        self.assertIn("trust_score_violations", report["sections"])


if __name__ == "__main__":
    unittest.main()
