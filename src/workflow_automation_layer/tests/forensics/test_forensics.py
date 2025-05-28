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
from agents.workflow_forensics_agent import WorkflowForensicsAgent

from n8n_integration.n8n_connector import N8nConnector
from n8n_integration.n8n_bridge_service import N8nBridgeService

from security.security_compliance_observability import SecurityComplianceObservability


class TestWorkflowForensics(unittest.TestCase):
    """Forensics tests for the workflow engine components."""
    
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
        
        # Create forensics agent
        self.forensics_agent = WorkflowForensicsAgent(
            agent_id="forensics-agent-001",
            workflow_runtime=self.workflow_runtime
        )
        
        # Create security compliance module
        self.security_compliance = SecurityComplianceObservability(
            workflow_runtime=self.workflow_runtime
        )
        
        # Sample workflow manifest for testing
        self.test_workflow_manifest = {
            "id": "forensics-workflow-001",
            "name": "Forensics Test Workflow",
            "version": "1.0",
            "description": "A workflow for forensics testing",
            "execution_mode": "supervised",
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
                    "name": "Decision Task",
                    "type": "decision",
                    "inputs": ["result1"],
                    "outputs": ["decision"],
                    "next": ["task-004", "task-005"]
                },
                {
                    "id": "task-004",
                    "name": "Approval Task",
                    "type": "approval",
                    "inputs": ["decision"],
                    "outputs": ["approved"],
                    "next": ["task-006"]
                },
                {
                    "id": "task-005",
                    "name": "Rejection Task",
                    "type": "notification",
                    "inputs": ["decision"],
                    "outputs": ["notified"],
                    "next": ["task-006"]
                },
                {
                    "id": "task-006",
                    "name": "End Task",
                    "type": "end",
                    "inputs": ["approved", "notified"]
                }
            ]
        }
    
    def test_execution_trace_reconstruction(self):
        """Test the ability to reconstruct a complete execution trace."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Simulate task executions and generate trace events
        task_events = [
            {"task_id": "task-001", "event_type": "task_started", "timestamp": "2025-05-22T12:00:00Z"},
            {"task_id": "task-001", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:01Z"},
            {"task_id": "task-002", "event_type": "task_started", "timestamp": "2025-05-22T12:00:02Z"},
            {"task_id": "task-002", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:05Z"},
            {"task_id": "task-003", "event_type": "task_started", "timestamp": "2025-05-22T12:00:06Z"},
            {"task_id": "task-003", "event_type": "decision_made", "timestamp": "2025-05-22T12:00:07Z", "decision": "approve"},
            {"task_id": "task-003", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:08Z"},
            {"task_id": "task-004", "event_type": "task_started", "timestamp": "2025-05-22T12:00:09Z"},
            {"task_id": "task-004", "event_type": "human_intervention_requested", "timestamp": "2025-05-22T12:00:10Z"},
            {"task_id": "task-004", "event_type": "human_intervention_received", "timestamp": "2025-05-22T12:00:30Z", "decision": "approved"},
            {"task_id": "task-004", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:31Z"},
            {"task_id": "task-006", "event_type": "task_started", "timestamp": "2025-05-22T12:00:32Z"},
            {"task_id": "task-006", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:33Z"}
        ]
        
        # Add events to the trace
        for event in task_events:
            task_id = event["task_id"]
            event_type = event["event_type"]
            event_data = {k: v for k, v in event.items() if k not in ["task_id", "event_type"]}
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, {**event_data, "task_id": task_id})
        
        # Reconstruct the execution trace
        reconstructed_trace = self.forensics_agent.reconstruct_execution_trace(workflow_id, execution_id)
        
        # Verify the trace was reconstructed correctly
        self.assertIsNotNone(reconstructed_trace)
        self.assertEqual(len(reconstructed_trace["events"]), len(task_events))
        self.assertEqual(reconstructed_trace["workflow_id"], workflow_id)
        self.assertEqual(reconstructed_trace["execution_id"], execution_id)
        
        # Verify the execution path
        execution_path = self.forensics_agent.extract_execution_path(reconstructed_trace)
        expected_path = ["task-001", "task-002", "task-003", "task-004", "task-006"]
        self.assertEqual(execution_path, expected_path)
    
    def test_decision_audit_trail(self):
        """Test the ability to audit decision points in a workflow."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Simulate a decision point with detailed context
        decision_context = {
            "task_id": "task-003",
            "input_data": {"result1": "high_value_transaction"},
            "decision_factors": {
                "transaction_amount": 5000,
                "customer_risk_score": 0.2,
                "transaction_type": "international",
                "historical_pattern_match": 0.85
            },
            "decision": "approve",
            "confidence": 0.78,
            "timestamp": "2025-05-22T12:00:07Z",
            "agent_id": "decision-agent-001",
            "agent_trust_score": 0.9
        }
        
        # Record the decision in the trace
        self.debug_trace_manager.add_trace_event(
            workflow_id, 
            execution_id, 
            "decision_made", 
            decision_context
        )
        
        # Audit the decision trail
        decision_audit = self.forensics_agent.audit_decision_trail(workflow_id, execution_id)
        
        # Verify the decision audit
        self.assertIsNotNone(decision_audit)
        self.assertGreater(len(decision_audit), 0)
        
        # Verify the specific decision details
        decision = decision_audit[0]
        self.assertEqual(decision["task_id"], "task-003")
        self.assertEqual(decision["decision"], "approve")
        self.assertEqual(decision["confidence"], 0.78)
        self.assertIn("decision_factors", decision)
        self.assertIn("transaction_amount", decision["decision_factors"])
    
    def test_data_lineage_tracking(self):
        """Test the ability to track data lineage through a workflow."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Execute the workflow
        input_data = {"data1": "customer_application"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Simulate data transformations through the workflow
        data_events = [
            {
                "task_id": "task-001",
                "event_type": "data_received",
                "data_id": "data1",
                "value": "customer_application",
                "source": "external",
                "timestamp": "2025-05-22T12:00:00Z"
            },
            {
                "task_id": "task-002",
                "event_type": "data_transformed",
                "input_data_id": "data1",
                "output_data_id": "result1",
                "transformation": "validation",
                "value": "validated_application",
                "timestamp": "2025-05-22T12:00:04Z"
            },
            {
                "task_id": "task-003",
                "event_type": "data_transformed",
                "input_data_id": "result1",
                "output_data_id": "decision",
                "transformation": "risk_assessment",
                "value": "low_risk",
                "timestamp": "2025-05-22T12:00:07Z"
            },
            {
                "task_id": "task-004",
                "event_type": "data_transformed",
                "input_data_id": "decision",
                "output_data_id": "approved",
                "transformation": "human_approval",
                "value": "approved_with_comments",
                "timestamp": "2025-05-22T12:00:30Z"
            }
        ]
        
        # Add data events to the trace
        for event in data_events:
            task_id = event["task_id"]
            event_type = event["event_type"]
            event_data = {k: v for k, v in event.items() if k not in ["task_id", "event_type"]}
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, {**event_data, "task_id": task_id})
        
        # Track data lineage
        data_lineage = self.forensics_agent.track_data_lineage(workflow_id, execution_id, "approved")
        
        # Verify the data lineage
        self.assertIsNotNone(data_lineage)
        self.assertEqual(len(data_lineage), 4)  # Should include all transformations
        
        # Verify the lineage path
        lineage_path = [item["data_id"] for item in data_lineage]
        expected_path = ["data1", "result1", "decision", "approved"]
        self.assertEqual(lineage_path, expected_path)
    
    def test_compliance_violation_detection(self):
        """Test the ability to detect compliance violations in workflow executions."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Execute the workflow
        input_data = {"data1": "sensitive_data"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Define compliance rules
        compliance_rules = [
            {
                "id": "rule-001",
                "name": "PII Data Handling",
                "description": "Personal Identifiable Information must be encrypted",
                "data_patterns": ["ssn", "credit_card", "address"],
                "required_actions": ["encrypt", "log_access"]
            },
            {
                "id": "rule-002",
                "name": "Approval Requirements",
                "description": "Transactions over $1000 require manager approval",
                "conditions": {"transaction_amount": "> 1000"},
                "required_actions": ["manager_approval"]
            }
        ]
        
        # Register compliance rules
        for rule in compliance_rules:
            self.security_compliance.register_compliance_rule(rule)
        
        # Simulate events with compliance implications
        compliance_events = [
            {
                "task_id": "task-002",
                "event_type": "data_processed",
                "data": {"ssn": "123-45-6789", "name": "John Doe"},
                "actions": ["log_access"],  # Missing encrypt action
                "timestamp": "2025-05-22T12:00:04Z"
            },
            {
                "task_id": "task-003",
                "event_type": "decision_made",
                "data": {"transaction_amount": 2500},
                "actions": ["automated_approval"],  # Missing manager_approval
                "timestamp": "2025-05-22T12:00:07Z"
            }
        ]
        
        # Add compliance events to the trace
        for event in compliance_events:
            task_id = event["task_id"]
            event_type = event["event_type"]
            event_data = {k: v for k, v in event.items() if k not in ["task_id", "event_type"]}
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, {**event_data, "task_id": task_id})
        
        # Detect compliance violations
        violations = self.forensics_agent.detect_compliance_violations(workflow_id, execution_id)
        
        # Verify violations were detected
        self.assertIsNotNone(violations)
        self.assertEqual(len(violations), 2)  # Should detect both violations
        
        # Verify specific violation details
        rule_ids = [v["rule_id"] for v in violations]
        self.assertIn("rule-001", rule_ids)
        self.assertIn("rule-002", rule_ids)
    
    def test_root_cause_analysis(self):
        """Test the ability to perform root cause analysis on workflow failures."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Simulate a workflow failure
        failure_events = [
            {"task_id": "task-001", "event_type": "task_started", "timestamp": "2025-05-22T12:00:00Z"},
            {"task_id": "task-001", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:01Z"},
            {"task_id": "task-002", "event_type": "task_started", "timestamp": "2025-05-22T12:00:02Z"},
            {"task_id": "task-002", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:05Z"},
            {"task_id": "task-003", "event_type": "task_started", "timestamp": "2025-05-22T12:00:06Z"},
            {"task_id": "task-003", "event_type": "error_occurred", "timestamp": "2025-05-22T12:00:07Z", 
             "error": "DataValidationError", "message": "Invalid input format", 
             "context": {"input_value": "test_value", "expected_format": "numeric"}},
            {"task_id": "task-003", "event_type": "task_failed", "timestamp": "2025-05-22T12:00:08Z"},
            {"task_id": "workflow", "event_type": "workflow_failed", "timestamp": "2025-05-22T12:00:09Z"}
        ]
        
        # Add failure events to the trace
        for event in failure_events:
            task_id = event["task_id"]
            event_type = event["event_type"]
            event_data = {k: v for k, v in event.items() if k not in ["task_id", "event_type"]}
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, {**event_data, "task_id": task_id})
        
        # Perform root cause analysis
        root_cause = self.forensics_agent.perform_root_cause_analysis(workflow_id, execution_id)
        
        # Verify the root cause analysis
        self.assertIsNotNone(root_cause)
        self.assertEqual(root_cause["failure_task"], "task-003")
        self.assertEqual(root_cause["error_type"], "DataValidationError")
        self.assertIn("input_value", root_cause["context"])
        self.assertIn("expected_format", root_cause["context"])
    
    def test_temporal_pattern_analysis(self):
        """Test the ability to analyze temporal patterns in workflow executions."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Simulate multiple workflow executions with timing data
        execution_data = []
        for i in range(10):
            execution_id = f"execution-{i:03d}"
            
            # Generate execution timing data with some variance
            base_time = time.time()
            task_times = {
                "task-001": {"start": base_time, "end": base_time + 1 + (i % 3) * 0.5},
                "task-002": {"start": base_time + 2, "end": base_time + 5 + (i % 4) * 1.0},
                "task-003": {"start": base_time + 6, "end": base_time + 8 + (i % 2) * 2.0},
                "task-004": {"start": base_time + 9, "end": base_time + 31 + (i % 5) * 3.0}
            }
            
            # Add execution data
            execution_data.append({
                "execution_id": execution_id,
                "start_time": base_time,
                "end_time": base_time + 33 + (i % 5) * 3.0,
                "task_times": task_times
            })
            
            # Add timing events to the trace for each execution
            for task_id, times in task_times.items():
                self.debug_trace_manager.add_trace_event(
                    workflow_id, execution_id, "task_started", 
                    {"task_id": task_id, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(times["start"]))}
                )
                self.debug_trace_manager.add_trace_event(
                    workflow_id, execution_id, "task_completed", 
                    {"task_id": task_id, "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime(times["end"]))}
                )
        
        # Analyze temporal patterns
        temporal_analysis = self.forensics_agent.analyze_temporal_patterns(workflow_id)
        
        # Verify the temporal analysis
        self.assertIsNotNone(temporal_analysis)
        self.assertIn("average_execution_time", temporal_analysis)
        self.assertIn("task_timing_statistics", temporal_analysis)
        self.assertIn("bottleneck_tasks", temporal_analysis)
        
        # Verify task statistics
        task_stats = temporal_analysis["task_timing_statistics"]
        for task_id in ["task-001", "task-002", "task-003", "task-004"]:
            self.assertIn(task_id, task_stats)
            self.assertIn("average_duration", task_stats[task_id])
            self.assertIn("min_duration", task_stats[task_id])
            self.assertIn("max_duration", task_stats[task_id])
        
        # Verify bottleneck detection
        self.assertGreater(len(temporal_analysis["bottleneck_tasks"]), 0)
    
    def test_forensic_report_generation(self):
        """Test the ability to generate comprehensive forensic reports."""
        # Register the workflow
        workflow_id = self.test_workflow_manifest["id"]
        self.workflow_runtime.create_workflow(self.test_workflow_manifest)
        
        # Execute the workflow
        input_data = {"data1": "test_value"}
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Simulate various events for a comprehensive report
        events = [
            {"task_id": "task-001", "event_type": "task_started", "timestamp": "2025-05-22T12:00:00Z"},
            {"task_id": "task-001", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:01Z"},
            {"task_id": "task-002", "event_type": "task_started", "timestamp": "2025-05-22T12:00:02Z"},
            {"task_id": "task-002", "event_type": "data_transformed", "timestamp": "2025-05-22T12:00:04Z",
             "input_data_id": "data1", "output_data_id": "result1", "transformation": "validation"},
            {"task_id": "task-002", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:05Z"},
            {"task_id": "task-003", "event_type": "task_started", "timestamp": "2025-05-22T12:00:06Z"},
            {"task_id": "task-003", "event_type": "decision_made", "timestamp": "2025-05-22T12:00:07Z",
             "decision": "approve", "confidence": 0.78},
            {"task_id": "task-003", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:08Z"},
            {"task_id": "task-004", "event_type": "task_started", "timestamp": "2025-05-22T12:00:09Z"},
            {"task_id": "task-004", "event_type": "human_intervention_requested", "timestamp": "2025-05-22T12:00:10Z"},
            {"task_id": "task-004", "event_type": "human_intervention_received", "timestamp": "2025-05-22T12:00:30Z",
             "decision": "approved", "approver": "manager-001"},
            {"task_id": "task-004", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:31Z"},
            {"task_id": "task-006", "event_type": "task_started", "timestamp": "2025-05-22T12:00:32Z"},
            {"task_id": "task-006", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:33Z"},
            {"task_id": "workflow", "event_type": "workflow_completed", "timestamp": "2025-05-22T12:00:34Z"}
        ]
        
        # Add events to the trace
        for event in events:
            task_id = event["task_id"]
            event_type = event["event_type"]
            event_data = {k: v for k, v in event.items() if k not in ["task_id", "event_type"]}
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, {**event_data, "task_id": task_id})
        
        # Generate a forensic report
        report = self.forensics_agent.generate_forensic_report(workflow_id, execution_id)
        
        # Verify the report structure
        self.assertIsNotNone(report)
        self.assertIn("workflow_details", report)
        self.assertIn("execution_summary", report)
        self.assertIn("execution_path", report)
        self.assertIn("decision_points", report)
        self.assertIn("data_lineage", report)
        self.assertIn("timing_analysis", report)
        self.assertIn("compliance_check", report)
        
        # Verify report content
        self.assertEqual(report["workflow_details"]["id"], workflow_id)
        self.assertEqual(report["execution_summary"]["id"], execution_id)
        self.assertEqual(report["execution_summary"]["status"], "completed")
        self.assertGreater(len(report["execution_path"]), 0)
        self.assertGreater(len(report["timing_analysis"]["task_durations"]), 0)


if __name__ == '__main__':
    unittest.main()
