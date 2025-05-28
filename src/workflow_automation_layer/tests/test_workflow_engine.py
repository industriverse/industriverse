"""
Test suite for the Workflow Automation Layer Core Engine components.

This module contains unit tests for the core workflow engine components,
including workflow runtime, manifest parser, task contract manager, etc.
"""

import unittest
import asyncio
import json
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from workflow_engine.workflow_runtime import WorkflowRuntime
from workflow_engine.workflow_manifest_parser import WorkflowManifestParser
from workflow_engine.task_contract_manager import TaskContractManager
from workflow_engine.workflow_registry import WorkflowRegistry
from workflow_engine.workflow_telemetry import WorkflowTelemetry
from workflow_engine.execution_mode_manager import ExecutionModeManager
from workflow_engine.mesh_topology_manager import MeshTopologyManager
from workflow_engine.capsule_debug_trace_manager import CapsuleDebugTraceManager


class TestWorkflowManifestParser(unittest.TestCase):
    """Test cases for the WorkflowManifestParser class."""

    def setUp(self):
        """Set up test fixtures."""
        self.parser = WorkflowManifestParser()
        self.valid_manifest = {
            "name": "test_workflow",
            "description": "Test workflow for unit testing",
            "version": "1.0",
            "tasks": [
                {
                    "id": "task1",
                    "name": "Task 1",
                    "description": "First task",
                    "timeout_seconds": 300,
                    "retry_count": 3
                },
                {
                    "id": "task2",
                    "name": "Task 2",
                    "description": "Second task",
                    "timeout_seconds": 600,
                    "retry_count": 2
                }
            ],
            "workflow": {
                "transitions": [
                    {
                        "from": "task1",
                        "to": "task2",
                        "condition": "success"
                    }
                ]
            },
            "execution_modes": [
                {
                    "name": "reactive",
                    "trust_threshold": 0.5,
                    "confidence_required": 0.6,
                    "human_oversight": True
                }
            ]
        }

    def test_parse_valid_manifest(self):
        """Test parsing a valid workflow manifest."""
        result = self.parser.parse(self.valid_manifest)
        self.assertTrue(result["valid"])
        self.assertEqual(result["workflow_id"], "test_workflow")
        self.assertEqual(len(result["tasks"]), 2)
        self.assertEqual(len(result["transitions"]), 1)
        self.assertEqual(len(result["execution_modes"]), 1)

    def test_parse_invalid_manifest_missing_name(self):
        """Test parsing a manifest with missing name."""
        invalid_manifest = self.valid_manifest.copy()
        del invalid_manifest["name"]
        result = self.parser.parse(invalid_manifest)
        self.assertFalse(result["valid"])
        self.assertIn("name", result["errors"])

    def test_parse_invalid_manifest_missing_tasks(self):
        """Test parsing a manifest with missing tasks."""
        invalid_manifest = self.valid_manifest.copy()
        del invalid_manifest["tasks"]
        result = self.parser.parse(invalid_manifest)
        self.assertFalse(result["valid"])
        self.assertIn("tasks", result["errors"])

    def test_parse_invalid_manifest_invalid_transition(self):
        """Test parsing a manifest with invalid transition."""
        invalid_manifest = self.valid_manifest.copy()
        invalid_manifest["workflow"]["transitions"][0]["from"] = "non_existent_task"
        result = self.parser.parse(invalid_manifest)
        self.assertFalse(result["valid"])
        self.assertIn("transitions", result["errors"])

    def test_validate_execution_modes(self):
        """Test validation of execution modes."""
        # Test with valid execution modes
        result = self.parser._validate_execution_modes(self.valid_manifest["execution_modes"])
        self.assertTrue(result["valid"])
        
        # Test with invalid execution mode (missing required field)
        invalid_modes = [
            {
                "name": "reactive",
                # Missing trust_threshold
                "confidence_required": 0.6,
                "human_oversight": True
            }
        ]
        result = self.parser._validate_execution_modes(invalid_modes)
        self.assertFalse(result["valid"])
        self.assertIn("trust_threshold", result["errors"][0])


class TestTaskContractManager(unittest.TestCase):
    """Test cases for the TaskContractManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = TaskContractManager()
        self.task_contract = {
            "task_id": "task1",
            "workflow_id": "workflow1",
            "name": "Task 1",
            "description": "Test task",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"},
                    "param2": {"type": "number"}
                },
                "required": ["param1"]
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "result": {"type": "string"}
                },
                "required": ["result"]
            },
            "timeout_seconds": 300,
            "retry_policy": {
                "max_retries": 3,
                "retry_interval_seconds": 60
            }
        }

    def test_register_contract(self):
        """Test registering a task contract."""
        result = self.manager.register_contract(self.task_contract)
        self.assertTrue(result["success"])
        self.assertEqual(result["task_id"], "task1")
        
        # Verify the contract was stored
        contract = self.manager.get_contract("task1")
        self.assertIsNotNone(contract)
        self.assertEqual(contract["task_id"], "task1")

    def test_register_duplicate_contract(self):
        """Test registering a duplicate task contract."""
        # Register the contract first
        self.manager.register_contract(self.task_contract)
        
        # Try to register it again
        result = self.manager.register_contract(self.task_contract)
        self.assertFalse(result["success"])
        self.assertIn("already exists", result["error"])

    def test_validate_input_valid(self):
        """Test validating valid task input."""
        # Register the contract first
        self.manager.register_contract(self.task_contract)
        
        # Valid input
        input_data = {
            "param1": "test",
            "param2": 42
        }
        
        result = self.manager.validate_input("task1", input_data)
        self.assertTrue(result["valid"])

    def test_validate_input_invalid(self):
        """Test validating invalid task input."""
        # Register the contract first
        self.manager.register_contract(self.task_contract)
        
        # Invalid input (missing required param)
        input_data = {
            "param2": 42
        }
        
        result = self.manager.validate_input("task1", input_data)
        self.assertFalse(result["valid"])
        self.assertIn("param1", result["errors"])

    def test_validate_output_valid(self):
        """Test validating valid task output."""
        # Register the contract first
        self.manager.register_contract(self.task_contract)
        
        # Valid output
        output_data = {
            "result": "success"
        }
        
        result = self.manager.validate_output("task1", output_data)
        self.assertTrue(result["valid"])

    def test_validate_output_invalid(self):
        """Test validating invalid task output."""
        # Register the contract first
        self.manager.register_contract(self.task_contract)
        
        # Invalid output (missing required field)
        output_data = {
            "status": "success"  # Wrong field name
        }
        
        result = self.manager.validate_output("task1", output_data)
        self.assertFalse(result["valid"])
        self.assertIn("result", result["errors"])


class TestWorkflowRegistry(unittest.TestCase):
    """Test cases for the WorkflowRegistry class."""

    def setUp(self):
        """Set up test fixtures."""
        self.registry = WorkflowRegistry()
        self.workflow_def = {
            "workflow_id": "workflow1",
            "name": "Test Workflow",
            "description": "Workflow for testing",
            "version": "1.0",
            "tasks": [
                {"task_id": "task1", "name": "Task 1"},
                {"task_id": "task2", "name": "Task 2"}
            ],
            "transitions": [
                {"from": "task1", "to": "task2", "condition": "success"}
            ],
            "execution_modes": [
                {"name": "reactive", "trust_threshold": 0.5}
            ]
        }

    def test_register_workflow(self):
        """Test registering a workflow."""
        result = self.registry.register_workflow(self.workflow_def)
        self.assertTrue(result["success"])
        self.assertEqual(result["workflow_id"], "workflow1")
        
        # Verify the workflow was stored
        workflow = self.registry.get_workflow("workflow1")
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow["workflow_id"], "workflow1")

    def test_register_duplicate_workflow(self):
        """Test registering a duplicate workflow."""
        # Register the workflow first
        self.registry.register_workflow(self.workflow_def)
        
        # Try to register it again
        result = self.registry.register_workflow(self.workflow_def)
        self.assertFalse(result["success"])
        self.assertIn("already exists", result["error"])

    def test_update_workflow(self):
        """Test updating a workflow."""
        # Register the workflow first
        self.registry.register_workflow(self.workflow_def)
        
        # Update the workflow
        updated_workflow = self.workflow_def.copy()
        updated_workflow["description"] = "Updated description"
        updated_workflow["version"] = "1.1"
        
        result = self.registry.update_workflow("workflow1", updated_workflow)
        self.assertTrue(result["success"])
        
        # Verify the workflow was updated
        workflow = self.registry.get_workflow("workflow1")
        self.assertEqual(workflow["description"], "Updated description")
        self.assertEqual(workflow["version"], "1.1")

    def test_update_nonexistent_workflow(self):
        """Test updating a non-existent workflow."""
        result = self.registry.update_workflow("nonexistent", self.workflow_def)
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])

    def test_list_workflows(self):
        """Test listing workflows."""
        # Register multiple workflows
        self.registry.register_workflow(self.workflow_def)
        
        workflow2 = self.workflow_def.copy()
        workflow2["workflow_id"] = "workflow2"
        workflow2["name"] = "Test Workflow 2"
        self.registry.register_workflow(workflow2)
        
        # List all workflows
        workflows = self.registry.list_workflows()
        self.assertEqual(len(workflows), 2)
        self.assertIn("workflow1", [w["workflow_id"] for w in workflows])
        self.assertIn("workflow2", [w["workflow_id"] for w in workflows])

    def test_delete_workflow(self):
        """Test deleting a workflow."""
        # Register the workflow first
        self.registry.register_workflow(self.workflow_def)
        
        # Delete the workflow
        result = self.registry.delete_workflow("workflow1")
        self.assertTrue(result["success"])
        
        # Verify the workflow was deleted
        workflow = self.registry.get_workflow("workflow1")
        self.assertIsNone(workflow)

    def test_delete_nonexistent_workflow(self):
        """Test deleting a non-existent workflow."""
        result = self.registry.delete_workflow("nonexistent")
        self.assertFalse(result["success"])
        self.assertIn("not found", result["error"])


class TestExecutionModeManager(unittest.TestCase):
    """Test cases for the ExecutionModeManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = ExecutionModeManager()
        self.config = {
            "modes": [
                {
                    "name": "reactive",
                    "trust_threshold": 0.5,
                    "confidence_required": 0.6,
                    "human_oversight": True,
                    "description": "Waits for explicit triggers before executing workflows"
                },
                {
                    "name": "proactive",
                    "trust_threshold": 0.7,
                    "confidence_required": 0.8,
                    "human_oversight": True,
                    "description": "Can initiate workflows based on predicted needs"
                },
                {
                    "name": "autonomous",
                    "trust_threshold": 0.9,
                    "confidence_required": 0.95,
                    "human_oversight": False,
                    "description": "Can make decisions and execute workflows independently"
                }
            ],
            "default_mode": "reactive",
            "mode_switching": {
                "enabled": True,
                "cool_down_period_seconds": 300
            }
        }
        self.manager.configure(self.config)

    def test_get_execution_mode(self):
        """Test getting execution mode based on trust and confidence scores."""
        # Should return reactive mode
        mode = self.manager.get_execution_mode(0.6, 0.7)
        self.assertEqual(mode["name"], "reactive")
        
        # Should return proactive mode
        mode = self.manager.get_execution_mode(0.8, 0.85)
        self.assertEqual(mode["name"], "proactive")
        
        # Should return autonomous mode
        mode = self.manager.get_execution_mode(0.95, 0.98)
        self.assertEqual(mode["name"], "autonomous")
        
        # Should return default mode (reactive) when scores are too low
        mode = self.manager.get_execution_mode(0.4, 0.5)
        self.assertEqual(mode["name"], "reactive")

    def test_validate_mode_transition(self):
        """Test validating mode transitions."""
        # Valid transition (reactive to proactive)
        result = self.manager.validate_mode_transition("workflow1", "reactive", "proactive")
        self.assertTrue(result["valid"])
        
        # Valid transition (proactive to autonomous)
        result = self.manager.validate_mode_transition("workflow1", "proactive", "autonomous")
        self.assertTrue(result["valid"])
        
        # Simulate a recent transition
        self.manager._last_transitions["workflow1"] = {
            "timestamp": asyncio.get_event_loop().time(),
            "from_mode": "reactive",
            "to_mode": "proactive"
        }
        
        # Invalid transition (too soon after previous transition)
        result = self.manager.validate_mode_transition("workflow1", "proactive", "autonomous")
        self.assertFalse(result["valid"])
        self.assertIn("cool down period", result["reason"])

    def test_record_mode_transition(self):
        """Test recording mode transitions."""
        # Record a transition
        self.manager.record_mode_transition("workflow1", "reactive", "proactive", 0.8, 0.85)
        
        # Verify the transition was recorded
        self.assertIn("workflow1", self.manager._last_transitions)
        self.assertEqual(self.manager._last_transitions["workflow1"]["from_mode"], "reactive")
        self.assertEqual(self.manager._last_transitions["workflow1"]["to_mode"], "proactive")
        self.assertEqual(self.manager._last_transitions["workflow1"]["trust_score"], 0.8)
        self.assertEqual(self.manager._last_transitions["workflow1"]["confidence_score"], 0.85)


class TestMeshTopologyManager(unittest.TestCase):
    """Test cases for the MeshTopologyManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = MeshTopologyManager()
        self.config = {
            "mesh_type": "hybrid",
            "edge_enabled": True,
            "routing_constraints": {
                "max_hops": 5,
                "preferred_paths": ["protocol_layer", "core_ai_layer"],
                "fallback_paths": ["direct"]
            },
            "trust_routing": {
                "enabled": True,
                "min_trust_score": 0.6,
                "preferred_high_trust": True
            }
        }
        self.manager.configure(self.config)

    def test_register_node(self):
        """Test registering a node in the mesh."""
        node_info = {
            "node_id": "node1",
            "node_type": "agent",
            "capabilities": ["task_execution", "data_processing"],
            "location": "edge",
            "trust_score": 0.8
        }
        
        result = self.manager.register_node(node_info)
        self.assertTrue(result["success"])
        
        # Verify the node was registered
        node = self.manager.get_node("node1")
        self.assertIsNotNone(node)
        self.assertEqual(node["node_id"], "node1")
        self.assertEqual(node["trust_score"], 0.8)

    def test_find_route(self):
        """Test finding a route between nodes."""
        # Register nodes
        self.manager.register_node({
            "node_id": "source",
            "node_type": "agent",
            "capabilities": ["task_execution"],
            "location": "edge",
            "trust_score": 0.8
        })
        
        self.manager.register_node({
            "node_id": "target",
            "node_type": "service",
            "capabilities": ["data_processing"],
            "location": "cloud",
            "trust_score": 0.9
        })
        
        self.manager.register_node({
            "node_id": "intermediate",
            "node_type": "router",
            "capabilities": ["routing"],
            "location": "fog",
            "trust_score": 0.85
        })
        
        # Register connections
        self.manager.register_connection("source", "intermediate")
        self.manager.register_connection("intermediate", "target")
        
        # Find route
        route = self.manager.find_route("source", "target")
        self.assertTrue(route["success"])
        self.assertEqual(len(route["path"]), 3)  # source -> intermediate -> target
        self.assertEqual(route["path"][0], "source")
        self.assertEqual(route["path"][1], "intermediate")
        self.assertEqual(route["path"][2], "target")

    def test_find_route_no_path(self):
        """Test finding a route when no path exists."""
        # Register disconnected nodes
        self.manager.register_node({
            "node_id": "source",
            "node_type": "agent",
            "capabilities": ["task_execution"],
            "location": "edge",
            "trust_score": 0.8
        })
        
        self.manager.register_node({
            "node_id": "target",
            "node_type": "service",
            "capabilities": ["data_processing"],
            "location": "cloud",
            "trust_score": 0.9
        })
        
        # No connection registered between them
        
        # Find route
        route = self.manager.find_route("source", "target")
        self.assertFalse(route["success"])
        self.assertIn("No path found", route["error"])

    def test_find_route_trust_based(self):
        """Test finding a route based on trust scores."""
        # Register nodes with different trust scores
        self.manager.register_node({
            "node_id": "source",
            "node_type": "agent",
            "capabilities": ["task_execution"],
            "location": "edge",
            "trust_score": 0.8
        })
        
        self.manager.register_node({
            "node_id": "target",
            "node_type": "service",
            "capabilities": ["data_processing"],
            "location": "cloud",
            "trust_score": 0.9
        })
        
        self.manager.register_node({
            "node_id": "intermediate1",
            "node_type": "router",
            "capabilities": ["routing"],
            "location": "fog",
            "trust_score": 0.85
        })
        
        self.manager.register_node({
            "node_id": "intermediate2",
            "node_type": "router",
            "capabilities": ["routing"],
            "location": "fog",
            "trust_score": 0.7
        })
        
        # Register connections
        self.manager.register_connection("source", "intermediate1")
        self.manager.register_connection("source", "intermediate2")
        self.manager.register_connection("intermediate1", "target")
        self.manager.register_connection("intermediate2", "target")
        
        # Find route (should prefer the higher trust path)
        route = self.manager.find_route("source", "target")
        self.assertTrue(route["success"])
        self.assertEqual(len(route["path"]), 3)
        self.assertEqual(route["path"][0], "source")
        self.assertEqual(route["path"][1], "intermediate1")  # Higher trust score
        self.assertEqual(route["path"][2], "target")


class TestCapsuleDebugTraceManager(unittest.TestCase):
    """Test cases for the CapsuleDebugTraceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = CapsuleDebugTraceManager()
        self.config = {
            "enabled": True,
            "trace_level": "detailed",
            "retention_days": 30,
            "pattern_detection": {
                "enabled": True,
                "min_confidence": 0.7
            },
            "forensics_engine": {
                "enabled": True,
                "analysis_frequency_hours": 24
            }
        }
        self.manager.configure(self.config)

    def test_create_trace(self):
        """Test creating a debug trace."""
        trace_info = {
            "workflow_id": "workflow1",
            "task_id": "task1",
            "agent_id": "agent1",
            "execution_mode": "reactive",
            "trust_score": 0.8,
            "confidence_score": 0.85
        }
        
        trace_id = self.manager.create_trace(trace_info)
        self.assertIsNotNone(trace_id)
        
        # Verify the trace was created
        trace = self.manager.get_trace(trace_id)
        self.assertIsNotNone(trace)
        self.assertEqual(trace["workflow_id"], "workflow1")
        self.assertEqual(trace["task_id"], "task1")
        self.assertEqual(trace["agent_id"], "agent1")

    def test_add_trace_entry(self):
        """Test adding an entry to a debug trace."""
        # Create a trace first
        trace_info = {
            "workflow_id": "workflow1",
            "task_id": "task1",
            "agent_id": "agent1",
            "execution_mode": "reactive",
            "trust_score": 0.8,
            "confidence_score": 0.85
        }
        
        trace_id = self.manager.create_trace(trace_info)
        
        # Add an entry
        entry_info = {
            "timestamp": "2025-05-22T15:30:00Z",
            "level": "info",
            "message": "Task started",
            "data": {
                "input_params": {"param1": "value1"}
            }
        }
        
        entry_id = self.manager.add_trace_entry(trace_id, entry_info)
        self.assertIsNotNone(entry_id)
        
        # Verify the entry was added
        trace = self.manager.get_trace(trace_id)
        self.assertEqual(len(trace["entries"]), 1)
        self.assertEqual(trace["entries"][0]["message"], "Task started")

    def test_detect_patterns(self):
        """Test detecting patterns in debug traces."""
        # Create a trace with multiple entries
        trace_info = {
            "workflow_id": "workflow1",
            "task_id": "task1",
            "agent_id": "agent1",
            "execution_mode": "reactive",
            "trust_score": 0.8,
            "confidence_score": 0.85
        }
        
        trace_id = self.manager.create_trace(trace_info)
        
        # Add entries that form a pattern (repeated retries)
        for i in range(3):
            self.manager.add_trace_entry(trace_id, {
                "timestamp": f"2025-05-22T15:{30+i}:00Z",
                "level": "warning",
                "message": f"Task retry {i+1}",
                "data": {
                    "error": "Connection timeout"
                }
            })
        
        # Detect patterns
        patterns = self.manager.detect_patterns([trace_id])
        self.assertGreater(len(patterns), 0)
        
        # Verify the pattern was detected
        retry_pattern = next((p for p in patterns if p["pattern_type"] == "retry_chain"), None)
        self.assertIsNotNone(retry_pattern)
        self.assertEqual(retry_pattern["entity_id"], "task1")
        self.assertGreaterEqual(retry_pattern["confidence"], 0.7)

    def test_generate_forensics_report(self):
        """Test generating a forensics report."""
        # Create multiple traces
        for i in range(3):
            trace_info = {
                "workflow_id": "workflow1",
                "task_id": f"task{i+1}",
                "agent_id": "agent1",
                "execution_mode": "reactive",
                "trust_score": 0.8,
                "confidence_score": 0.85
            }
            
            trace_id = self.manager.create_trace(trace_info)
            
            # Add some entries
            self.manager.add_trace_entry(trace_id, {
                "timestamp": f"2025-05-22T15:{30+i}:00Z",
                "level": "info",
                "message": f"Task {i+1} started",
                "data": {}
            })
            
            self.manager.add_trace_entry(trace_id, {
                "timestamp": f"2025-05-22T15:{35+i}:00Z",
                "level": "info",
                "message": f"Task {i+1} completed",
                "data": {
                    "duration_ms": 5000 + i * 1000
                }
            })
        
        # Generate forensics report
        report = self.manager.generate_forensics_report("workflow1")
        self.assertIsNotNone(report)
        self.assertEqual(report["workflow_id"], "workflow1")
        self.assertIn("tasks", report)
        self.assertIn("patterns", report)
        self.assertIn("recommendations", report)


if __name__ == "__main__":
    unittest.main()
