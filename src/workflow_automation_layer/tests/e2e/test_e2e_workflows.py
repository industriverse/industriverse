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

from n8n_integration.n8n_connector import N8nConnector
from n8n_integration.n8n_bridge_service import N8nBridgeService

from security.security_compliance_observability import SecurityComplianceObservability
from ui.workflow_visualization import WorkflowVisualization
from ui.dynamic_agent_capsule import DynamicAgentCapsule


class TestEndToEndWorkflows(unittest.TestCase):
    """End-to-end tests for complete workflow scenarios."""
    
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
        
        # Create agents
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
        
        self.capsule_controller = CapsuleWorkflowController(
            agent_id="capsule-controller-001",
            workflow_runtime=self.workflow_runtime,
            execution_mode_manager=self.execution_mode_manager,
            mesh_topology_manager=self.mesh_topology_manager
        )
        
        # Create n8n connector and bridge
        self.n8n_connector = MagicMock(spec=N8nConnector)
        self.n8n_bridge_service = N8nBridgeService(
            n8n_connector=self.n8n_connector,
            workflow_runtime=self.workflow_runtime
        )
        
        self.n8n_sync_bridge = N8nSyncBridge(
            agent_id="n8n-sync-bridge-001",
            workflow_runtime=self.workflow_runtime,
            n8n_api_url="http://localhost:5678/api/v1"
        )
        self.n8n_sync_bridge.n8n_connector = self.n8n_connector
        
        # Create security compliance module
        self.security_compliance = SecurityComplianceObservability(
            workflow_runtime=self.workflow_runtime
        )
        
        # Create UI components
        self.workflow_visualization = WorkflowVisualization()
        self.dynamic_agent_capsule = DynamicAgentCapsule(
            workflow_runtime=self.workflow_runtime
        )
        
        # Load industry-specific workflow templates
        self.manufacturing_workflow = self.load_manufacturing_workflow()
        self.logistics_workflow = self.load_logistics_workflow()
        self.energy_workflow = self.load_energy_workflow()
    
    def load_manufacturing_workflow(self):
        """Load a manufacturing workflow template."""
        return {
            "id": "manufacturing-workflow-001",
            "name": "Quality Control Inspection Workflow",
            "version": "1.0",
            "description": "A workflow for automated quality control inspection in manufacturing",
            "execution_mode": "autonomous",
            "mesh_topology": "distributed",
            "industry": "manufacturing",
            "tasks": [
                {
                    "id": "task-001",
                    "name": "Sensor Data Collection",
                    "type": "data_collection",
                    "inputs": ["sensor_trigger"],
                    "outputs": ["raw_sensor_data"],
                    "next": ["task-002"]
                },
                {
                    "id": "task-002",
                    "name": "Data Preprocessing",
                    "type": "data_processing",
                    "inputs": ["raw_sensor_data"],
                    "outputs": ["processed_data"],
                    "next": ["task-003"]
                },
                {
                    "id": "task-003",
                    "name": "Quality Analysis",
                    "type": "analysis",
                    "inputs": ["processed_data"],
                    "outputs": ["quality_score"],
                    "next": ["task-004"]
                },
                {
                    "id": "task-004",
                    "name": "Decision Point",
                    "type": "decision",
                    "inputs": ["quality_score"],
                    "outputs": ["decision"],
                    "next": ["task-005", "task-006"]
                },
                {
                    "id": "task-005",
                    "name": "Pass Product",
                    "type": "action",
                    "inputs": ["decision"],
                    "outputs": ["pass_notification"],
                    "next": ["task-007"]
                },
                {
                    "id": "task-006",
                    "name": "Reject Product",
                    "type": "action",
                    "inputs": ["decision"],
                    "outputs": ["reject_notification"],
                    "next": ["task-007"]
                },
                {
                    "id": "task-007",
                    "name": "Record Results",
                    "type": "data_storage",
                    "inputs": ["pass_notification", "reject_notification"],
                    "outputs": ["record_confirmation"],
                    "next": ["task-008"]
                },
                {
                    "id": "task-008",
                    "name": "End Process",
                    "type": "end",
                    "inputs": ["record_confirmation"]
                }
            ]
        }
    
    def load_logistics_workflow(self):
        """Load a logistics workflow template."""
        return {
            "id": "logistics-workflow-001",
            "name": "Shipment Tracking and Optimization Workflow",
            "version": "1.0",
            "description": "A workflow for tracking and optimizing shipments in logistics",
            "execution_mode": "supervised",
            "mesh_topology": "hierarchical",
            "industry": "logistics",
            "tasks": [
                {
                    "id": "task-001",
                    "name": "Shipment Request",
                    "type": "start",
                    "outputs": ["shipment_request"],
                    "next": ["task-002"]
                },
                {
                    "id": "task-002",
                    "name": "Route Planning",
                    "type": "planning",
                    "inputs": ["shipment_request"],
                    "outputs": ["route_plan"],
                    "next": ["task-003"]
                },
                {
                    "id": "task-003",
                    "name": "Resource Allocation",
                    "type": "allocation",
                    "inputs": ["route_plan"],
                    "outputs": ["allocated_resources"],
                    "next": ["task-004"]
                },
                {
                    "id": "task-004",
                    "name": "Dispatch Approval",
                    "type": "approval",
                    "inputs": ["allocated_resources"],
                    "outputs": ["dispatch_approval"],
                    "next": ["task-005"]
                },
                {
                    "id": "task-005",
                    "name": "Dispatch Execution",
                    "type": "execution",
                    "inputs": ["dispatch_approval"],
                    "outputs": ["dispatch_confirmation"],
                    "next": ["task-006"]
                },
                {
                    "id": "task-006",
                    "name": "Tracking Updates",
                    "type": "monitoring",
                    "inputs": ["dispatch_confirmation"],
                    "outputs": ["tracking_data"],
                    "next": ["task-007"]
                },
                {
                    "id": "task-007",
                    "name": "Delivery Confirmation",
                    "type": "verification",
                    "inputs": ["tracking_data"],
                    "outputs": ["delivery_status"],
                    "next": ["task-008"]
                },
                {
                    "id": "task-008",
                    "name": "End Shipment",
                    "type": "end",
                    "inputs": ["delivery_status"]
                }
            ]
        }
    
    def load_energy_workflow(self):
        """Load an energy workflow template."""
        return {
            "id": "energy-workflow-001",
            "name": "Grid Demand Response Workflow",
            "version": "1.0",
            "description": "A workflow for managing demand response events in energy grid",
            "execution_mode": "collaborative",
            "mesh_topology": "distributed",
            "industry": "energy",
            "tasks": [
                {
                    "id": "task-001",
                    "name": "Demand Forecast",
                    "type": "forecasting",
                    "inputs": ["grid_data"],
                    "outputs": ["demand_forecast"],
                    "next": ["task-002"]
                },
                {
                    "id": "task-002",
                    "name": "Threshold Analysis",
                    "type": "analysis",
                    "inputs": ["demand_forecast"],
                    "outputs": ["threshold_status"],
                    "next": ["task-003"]
                },
                {
                    "id": "task-003",
                    "name": "Event Decision",
                    "type": "decision",
                    "inputs": ["threshold_status"],
                    "outputs": ["event_decision"],
                    "next": ["task-004", "task-008"]
                },
                {
                    "id": "task-004",
                    "name": "Event Planning",
                    "type": "planning",
                    "inputs": ["event_decision"],
                    "outputs": ["event_plan"],
                    "next": ["task-005"]
                },
                {
                    "id": "task-005",
                    "name": "Participant Notification",
                    "type": "notification",
                    "inputs": ["event_plan"],
                    "outputs": ["notification_status"],
                    "next": ["task-006"]
                },
                {
                    "id": "task-006",
                    "name": "Event Execution",
                    "type": "execution",
                    "inputs": ["notification_status"],
                    "outputs": ["execution_status"],
                    "next": ["task-007"]
                },
                {
                    "id": "task-007",
                    "name": "Performance Measurement",
                    "type": "measurement",
                    "inputs": ["execution_status"],
                    "outputs": ["performance_data"],
                    "next": ["task-008"]
                },
                {
                    "id": "task-008",
                    "name": "End Process",
                    "type": "end",
                    "inputs": ["event_decision", "performance_data"]
                }
            ]
        }
    
    def test_manufacturing_quality_control_workflow(self):
        """Test the end-to-end manufacturing quality control workflow."""
        # Register the workflow
        workflow_id = self.manufacturing_workflow["id"]
        self.workflow_runtime.create_workflow(self.manufacturing_workflow)
        
        # Register agents with manufacturing capabilities
        self.mesh_topology_manager.register_agent(
            "sensor-agent-001", "data_collection", ["sensor_data_processing"]
        )
        self.mesh_topology_manager.register_agent(
            "analysis-agent-001", "analysis", ["quality_assessment"]
        )
        self.mesh_topology_manager.register_agent(
            "action-agent-001", "action", ["product_handling"]
        )
        
        # Configure trigger for sensor data
        trigger_config = {
            "type": "event",
            "event_type": "sensor_data",
            "conditions": {"sensor_id": "production_line_1"}
        }
        self.trigger_agent.register_trigger(trigger_config)
        
        # Execute the workflow by triggering a sensor event
        sensor_event = {
            "type": "sensor_data",
            "data": {
                "sensor_id": "production_line_1",
                "timestamp": "2025-05-22T12:00:00Z",
                "measurements": {
                    "dimension_x": 10.02,
                    "dimension_y": 5.01,
                    "weight": 120.5,
                    "surface_quality": 0.95
                }
            }
        }
        
        # Process the event through the trigger agent
        self.trigger_agent.process_event(sensor_event)
        
        # Verify the workflow was triggered
        self.workflow_runtime.execute_workflow.assert_called_once()
        
        # Simulate the workflow execution
        execution_id = "manufacturing-execution-001"
        
        # Simulate task executions
        task_events = [
            {"task_id": "task-001", "event_type": "task_started", "timestamp": "2025-05-22T12:00:01Z"},
            {"task_id": "task-001", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:02Z", 
             "output": {"raw_sensor_data": sensor_event["data"]["measurements"]}},
            
            {"task_id": "task-002", "event_type": "task_started", "timestamp": "2025-05-22T12:00:03Z"},
            {"task_id": "task-002", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:04Z", 
             "output": {"processed_data": {
                 "dimension_x_normalized": 1.002,
                 "dimension_y_normalized": 1.001,
                 "weight_normalized": 1.005,
                 "surface_quality_normalized": 0.95
             }}},
            
            {"task_id": "task-003", "event_type": "task_started", "timestamp": "2025-05-22T12:00:05Z"},
            {"task_id": "task-003", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:06Z", 
             "output": {"quality_score": 0.92}},
            
            {"task_id": "task-004", "event_type": "task_started", "timestamp": "2025-05-22T12:00:07Z"},
            {"task_id": "task-004", "event_type": "decision_made", "timestamp": "2025-05-22T12:00:08Z", 
             "decision": "pass", "confidence": 0.92},
            {"task_id": "task-004", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:09Z", 
             "output": {"decision": "pass"}},
            
            {"task_id": "task-005", "event_type": "task_started", "timestamp": "2025-05-22T12:00:10Z"},
            {"task_id": "task-005", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:11Z", 
             "output": {"pass_notification": {"product_id": "P12345", "status": "passed", "timestamp": "2025-05-22T12:00:11Z"}}},
            
            {"task_id": "task-007", "event_type": "task_started", "timestamp": "2025-05-22T12:00:12Z"},
            {"task_id": "task-007", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:13Z", 
             "output": {"record_confirmation": {"record_id": "R67890", "status": "recorded"}}},
            
            {"task_id": "task-008", "event_type": "task_started", "timestamp": "2025-05-22T12:00:14Z"},
            {"task_id": "task-008", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:15Z"},
            
            {"task_id": "workflow", "event_type": "workflow_completed", "timestamp": "2025-05-22T12:00:16Z"}
        ]
        
        # Add events to the trace
        for event in task_events:
            task_id = event["task_id"]
            event_type = event["event_type"]
            event_data = {k: v for k, v in event.items() if k not in ["task_id", "event_type"]}
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, {**event_data, "task_id": task_id})
        
        # Verify the workflow visualization
        visualization = self.workflow_visualization.generate_workflow_visualization(workflow_id, execution_id)
        self.assertIsNotNone(visualization)
        
        # Verify the workflow execution status
        self.workflow_registry.get_execution.return_value = {"status": "completed"}
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertEqual(execution["status"], "completed")
    
    def test_logistics_shipment_workflow(self):
        """Test the end-to-end logistics shipment workflow."""
        # Register the workflow
        workflow_id = self.logistics_workflow["id"]
        self.workflow_runtime.create_workflow(self.logistics_workflow)
        
        # Register agents with logistics capabilities
        self.mesh_topology_manager.register_agent(
            "planning-agent-001", "planning", ["route_optimization"]
        )
        self.mesh_topology_manager.register_agent(
            "allocation-agent-001", "allocation", ["resource_management"]
        )
        self.mesh_topology_manager.register_agent(
            "approval-agent-001", "approval", ["dispatch_approval"]
        )
        
        # Execute the workflow with shipment request
        input_data = {
            "shipment_request": {
                "request_id": "SR12345",
                "customer": "ACME Corp",
                "origin": "Warehouse A",
                "destination": "Customer Site B",
                "items": [
                    {"item_id": "I001", "quantity": 10, "weight": 100},
                    {"item_id": "I002", "quantity": 5, "weight": 50}
                ],
                "priority": "standard",
                "requested_delivery_date": "2025-05-25"
            }
        }
        
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Simulate task executions
        task_events = [
            {"task_id": "task-001", "event_type": "task_started", "timestamp": "2025-05-22T12:00:01Z"},
            {"task_id": "task-001", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:02Z", 
             "output": {"shipment_request": input_data["shipment_request"]}},
            
            {"task_id": "task-002", "event_type": "task_started", "timestamp": "2025-05-22T12:00:03Z"},
            {"task_id": "task-002", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:05Z", 
             "output": {"route_plan": {
                 "route_id": "R789",
                 "waypoints": [
                     {"location": "Warehouse A", "eta": "2025-05-23T08:00:00Z"},
                     {"location": "Distribution Center", "eta": "2025-05-24T10:00:00Z"},
                     {"location": "Customer Site B", "eta": "2025-05-25T14:00:00Z"}
                 ],
                 "total_distance": 450,
                 "estimated_fuel": 45
             }}},
            
            {"task_id": "task-003", "event_type": "task_started", "timestamp": "2025-05-22T12:00:06Z"},
            {"task_id": "task-003", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:08Z", 
             "output": {"allocated_resources": {
                 "vehicle": "Truck-T789",
                 "driver": "Driver-D456",
                 "loading_dock": "Dock-L3",
                 "loading_time": "2025-05-23T07:00:00Z"
             }}},
            
            {"task_id": "task-004", "event_type": "task_started", "timestamp": "2025-05-22T12:00:09Z"},
            {"task_id": "task-004", "event_type": "human_intervention_requested", "timestamp": "2025-05-22T12:00:10Z"},
            {"task_id": "task-004", "event_type": "human_intervention_received", "timestamp": "2025-05-22T12:00:40Z", 
             "decision": "approved", "approver": "manager-001"},
            {"task_id": "task-004", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:41Z", 
             "output": {"dispatch_approval": {
                 "approved": True,
                 "approver": "manager-001",
                 "timestamp": "2025-05-22T12:00:40Z",
                 "comments": "Approved for dispatch"
             }}},
            
            {"task_id": "task-005", "event_type": "task_started", "timestamp": "2025-05-22T12:00:42Z"},
            {"task_id": "task-005", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:44Z", 
             "output": {"dispatch_confirmation": {
                 "dispatch_id": "D12345",
                 "timestamp": "2025-05-22T12:00:44Z",
                 "status": "dispatched"
             }}},
            
            {"task_id": "task-006", "event_type": "task_started", "timestamp": "2025-05-22T12:00:45Z"},
            {"task_id": "task-006", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:47Z", 
             "output": {"tracking_data": {
                 "tracking_id": "T67890",
                 "current_location": "Warehouse A",
                 "status": "preparing",
                 "timestamp": "2025-05-22T12:00:47Z"
             }}},
            
            {"task_id": "task-007", "event_type": "task_started", "timestamp": "2025-05-22T12:00:48Z"},
            {"task_id": "task-007", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:50Z", 
             "output": {"delivery_status": {
                 "status": "in_progress",
                 "estimated_delivery": "2025-05-25T14:00:00Z"
             }}},
            
            {"task_id": "task-008", "event_type": "task_started", "timestamp": "2025-05-22T12:00:51Z"},
            {"task_id": "task-008", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:52Z"},
            
            {"task_id": "workflow", "event_type": "workflow_completed", "timestamp": "2025-05-22T12:00:53Z"}
        ]
        
        # Add events to the trace
        for event in task_events:
            task_id = event["task_id"]
            event_type = event["event_type"]
            event_data = {k: v for k, v in event.items() if k not in ["task_id", "event_type"]}
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, {**event_data, "task_id": task_id})
        
        # Verify the workflow visualization
        visualization = self.workflow_visualization.generate_workflow_visualization(workflow_id, execution_id)
        self.assertIsNotNone(visualization)
        
        # Verify the n8n integration
        n8n_workflow_data = {
            "name": "Logistics Shipment Tracking",
            "nodes": [
                {"name": "Start", "type": "n8n-nodes-base.start", "position": [100, 100]},
                {"name": "Shipment Status", "type": "n8n-nodes-base.function", "position": [300, 100]},
                {"name": "Notification", "type": "n8n-nodes-base.email", "position": [500, 100]}
            ],
            "connections": {}
        }
        
        # Sync the workflow to n8n
        self.n8n_connector.create_workflow.return_value = {"id": "123", "name": "Logistics Shipment Tracking"}
        n8n_workflow_id = self.n8n_sync_bridge.sync_workflow_to_n8n(workflow_id, n8n_workflow_data)
        
        # Verify the n8n workflow was created
        self.n8n_connector.create_workflow.assert_called_once()
        self.assertEqual(n8n_workflow_id, "123")
    
    def test_energy_demand_response_workflow(self):
        """Test the end-to-end energy demand response workflow."""
        # Register the workflow
        workflow_id = self.energy_workflow["id"]
        self.workflow_runtime.create_workflow(self.energy_workflow)
        
        # Register agents with energy capabilities
        self.mesh_topology_manager.register_agent(
            "forecast-agent-001", "forecasting", ["demand_forecasting"]
        )
        self.mesh_topology_manager.register_agent(
            "analysis-agent-001", "analysis", ["threshold_analysis"]
        )
        self.mesh_topology_manager.register_agent(
            "notification-agent-001", "notification", ["participant_notification"]
        )
        
        # Execute the workflow with grid data
        input_data = {
            "grid_data": {
                "grid_id": "G12345",
                "timestamp": "2025-05-22T12:00:00Z",
                "measurements": {
                    "current_load": 85.7,
                    "capacity": 100.0,
                    "frequency": 60.02,
                    "voltage": 120.3,
                    "temperature": 32.5
                },
                "weather_forecast": {
                    "temperature_high": 38.2,
                    "temperature_low": 28.5,
                    "humidity": 65,
                    "precipitation_chance": 10
                }
            }
        }
        
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Simulate task executions
        task_events = [
            {"task_id": "task-001", "event_type": "task_started", "timestamp": "2025-05-22T12:00:01Z"},
            {"task_id": "task-001", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:03Z", 
             "output": {"demand_forecast": {
                 "forecast_id": "F789",
                 "timestamp": "2025-05-22T12:00:03Z",
                 "hourly_forecast": [
                     {"hour": 13, "load": 87.2},
                     {"hour": 14, "load": 90.5},
                     {"hour": 15, "load": 94.8},
                     {"hour": 16, "load": 97.3},
                     {"hour": 17, "load": 98.1},
                     {"hour": 18, "load": 96.5}
                 ],
                 "peak_hour": 17,
                 "peak_load": 98.1,
                 "confidence": 0.85
             }}},
            
            {"task_id": "task-002", "event_type": "task_started", "timestamp": "2025-05-22T12:00:04Z"},
            {"task_id": "task-002", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:06Z", 
             "output": {"threshold_status": {
                 "threshold_exceeded": True,
                 "threshold_value": 95.0,
                 "exceeded_hours": [15, 16, 17, 18],
                 "max_exceedance": 3.1,
                 "duration": 4
             }}},
            
            {"task_id": "task-003", "event_type": "task_started", "timestamp": "2025-05-22T12:00:07Z"},
            {"task_id": "task-003", "event_type": "decision_made", "timestamp": "2025-05-22T12:00:08Z", 
             "decision": "initiate_event", "confidence": 0.92},
            {"task_id": "task-003", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:09Z", 
             "output": {"event_decision": {
                 "initiate_event": True,
                 "event_type": "demand_response",
                 "priority": "high",
                 "target_reduction": 5.0
             }}},
            
            {"task_id": "task-004", "event_type": "task_started", "timestamp": "2025-05-22T12:00:10Z"},
            {"task_id": "task-004", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:12Z", 
             "output": {"event_plan": {
                 "event_id": "DR12345",
                 "start_time": "2025-05-22T15:00:00Z",
                 "end_time": "2025-05-22T19:00:00Z",
                 "target_participants": ["participant-001", "participant-002", "participant-003"],
                 "reduction_targets": {
                     "participant-001": 2.0,
                     "participant-002": 1.5,
                     "participant-003": 1.5
                 }
             }}},
            
            {"task_id": "task-005", "event_type": "task_started", "timestamp": "2025-05-22T12:00:13Z"},
            {"task_id": "task-005", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:15Z", 
             "output": {"notification_status": {
                 "notifications_sent": 3,
                 "notifications_confirmed": 2,
                 "pending_confirmations": 1
             }}},
            
            {"task_id": "task-006", "event_type": "task_started", "timestamp": "2025-05-22T12:00:16Z"},
            {"task_id": "task-006", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:18Z", 
             "output": {"execution_status": {
                 "status": "scheduled",
                 "participants_ready": 2,
                 "participants_pending": 1
             }}},
            
            {"task_id": "task-007", "event_type": "task_started", "timestamp": "2025-05-22T12:00:19Z"},
            {"task_id": "task-007", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:21Z", 
             "output": {"performance_data": {
                 "event_id": "DR12345",
                 "status": "scheduled",
                 "estimated_reduction": 4.5,
                 "estimated_compliance": 0.9
             }}},
            
            {"task_id": "task-008", "event_type": "task_started", "timestamp": "2025-05-22T12:00:22Z"},
            {"task_id": "task-008", "event_type": "task_completed", "timestamp": "2025-05-22T12:00:23Z"},
            
            {"task_id": "workflow", "event_type": "workflow_completed", "timestamp": "2025-05-22T12:00:24Z"}
        ]
        
        # Add events to the trace
        for event in task_events:
            task_id = event["task_id"]
            event_type = event["event_type"]
            event_data = {k: v for k, v in event.items() if k not in ["task_id", "event_type"]}
            self.debug_trace_manager.add_trace_event(workflow_id, execution_id, event_type, {**event_data, "task_id": task_id})
        
        # Verify the workflow visualization
        visualization = self.workflow_visualization.generate_workflow_visualization(workflow_id, execution_id)
        self.assertIsNotNone(visualization)
        
        # Verify the dynamic agent capsule
        capsule_config = {
            "id": "energy-capsule-001",
            "workflow_id": workflow_id,
            "execution_id": execution_id,
            "execution_mode": "collaborative"
        }
        capsule = self.dynamic_agent_capsule.create_agent_capsule(capsule_config)
        
        # Verify the capsule was created
        self.assertIsNotNone(capsule)
        self.assertEqual(capsule["id"], "energy-capsule-001")
        self.assertEqual(capsule["workflow_id"], workflow_id)
        self.assertEqual(capsule["execution_mode"], "collaborative")
    
    def test_cross_industry_workflow_integration(self):
        """Test the integration between workflows from different industries."""
        # Register all workflows
        manufacturing_workflow_id = self.manufacturing_workflow["id"]
        logistics_workflow_id = self.logistics_workflow["id"]
        energy_workflow_id = self.energy_workflow["id"]
        
        self.workflow_runtime.create_workflow(self.manufacturing_workflow)
        self.workflow_runtime.create_workflow(self.logistics_workflow)
        self.workflow_runtime.create_workflow(self.energy_workflow)
        
        # Create a cross-industry integration workflow
        cross_industry_workflow = {
            "id": "cross-industry-workflow-001",
            "name": "Integrated Manufacturing and Logistics Workflow",
            "version": "1.0",
            "description": "A workflow integrating manufacturing and logistics processes",
            "execution_mode": "supervised",
            "mesh_topology": "hybrid",
            "tasks": [
                {
                    "id": "task-001",
                    "name": "Production Order",
                    "type": "start",
                    "outputs": ["production_order"],
                    "next": ["task-002"]
                },
                {
                    "id": "task-002",
                    "name": "Manufacturing Process",
                    "type": "subprocess",
                    "inputs": ["production_order"],
                    "outputs": ["manufacturing_result"],
                    "subprocess_workflow_id": manufacturing_workflow_id,
                    "next": ["task-003"]
                },
                {
                    "id": "task-003",
                    "name": "Quality Check",
                    "type": "decision",
                    "inputs": ["manufacturing_result"],
                    "outputs": ["quality_decision"],
                    "next": ["task-004", "task-007"]
                },
                {
                    "id": "task-004",
                    "name": "Prepare Shipment",
                    "type": "process",
                    "inputs": ["quality_decision"],
                    "outputs": ["shipment_request"],
                    "next": ["task-005"]
                },
                {
                    "id": "task-005",
                    "name": "Logistics Process",
                    "type": "subprocess",
                    "inputs": ["shipment_request"],
                    "outputs": ["logistics_result"],
                    "subprocess_workflow_id": logistics_workflow_id,
                    "next": ["task-006"]
                },
                {
                    "id": "task-006",
                    "name": "Energy Optimization",
                    "type": "subprocess",
                    "inputs": ["logistics_result"],
                    "outputs": ["energy_result"],
                    "subprocess_workflow_id": energy_workflow_id,
                    "next": ["task-007"]
                },
                {
                    "id": "task-007",
                    "name": "Process Completion",
                    "type": "end",
                    "inputs": ["quality_decision", "energy_result"]
                }
            ]
        }
        
        workflow_id = cross_industry_workflow["id"]
        self.workflow_runtime.create_workflow(cross_industry_workflow)
        
        # Execute the cross-industry workflow
        input_data = {
            "production_order": {
                "order_id": "PO12345",
                "product_id": "PROD-001",
                "quantity": 100,
                "due_date": "2025-05-30"
            }
        }
        
        execution_id = self.workflow_runtime.execute_workflow(workflow_id, input_data)
        
        # Verify the workflow visualization
        visualization = self.workflow_visualization.generate_workflow_visualization(workflow_id, execution_id)
        self.assertIsNotNone(visualization)
        
        # Verify the execution status
        self.workflow_registry.get_execution.return_value = {"status": "completed"}
        execution = self.workflow_registry.get_execution(workflow_id, execution_id)
        self.assertEqual(execution["status"], "completed")


if __name__ == '__main__':
    unittest.main()
