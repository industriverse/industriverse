"""
Cross-Layer Integration Example for the Workflow Automation Layer.

This module demonstrates the integration between the Workflow Automation Layer
and other Industriverse layers through practical examples.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime

# Add the parent directory to the path to import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cross_layer_integration import CrossLayerIntegrationManager
from workflow_engine.workflow_runtime import WorkflowRuntime
from workflow_engine.workflow_registry import WorkflowRegistry
from workflow_engine.workflow_telemetry import WorkflowTelemetry
from workflow_engine.execution_mode_manager import ExecutionModeManager
from agents.workflow_trigger_agent import WorkflowTriggerAgent
from agents.human_intervention_agent import HumanInterventionAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_integration_example():
    """Run a complete integration example."""
    logger.info("Starting cross-layer integration example")
    
    # Initialize components
    workflow_registry = WorkflowRegistry()
    workflow_telemetry = WorkflowTelemetry()
    execution_mode_manager = ExecutionModeManager()
    
    # Initialize workflow runtime
    workflow_runtime = WorkflowRuntime(
        workflow_registry=workflow_registry,
        workflow_telemetry=workflow_telemetry,
        execution_mode_manager=execution_mode_manager
    )
    
    # Initialize agents
    trigger_agent = WorkflowTriggerAgent(workflow_runtime)
    human_agent = HumanInterventionAgent(workflow_runtime)
    
    # Register agents with workflow runtime
    workflow_runtime.register_agent("trigger", trigger_agent)
    workflow_runtime.register_agent("human_intervention", human_agent)
    
    # Initialize cross-layer integration
    integration_config = {
        "protocol_layer": {
            "protocol_layer_url": os.environ.get("PROTOCOL_LAYER_URL", "http://protocol-layer-service:8080"),
            "api_key": os.environ.get("PROTOCOL_LAYER_API_KEY", "test_api_key"),
            "max_retries": 5,
            "retry_delay_seconds": 5
        },
        "core_ai_layer": {
            "core_ai_url": os.environ.get("CORE_AI_LAYER_URL", "http://core-ai-layer-service:8080"),
            "api_key": os.environ.get("CORE_AI_LAYER_API_KEY", "test_api_key")
        },
        "application_layer": {
            "application_url": os.environ.get("APPLICATION_LAYER_URL", "http://application-layer-service:8080"),
            "api_key": os.environ.get("APPLICATION_LAYER_API_KEY", "test_api_key")
        }
    }
    
    integration_manager = CrossLayerIntegrationManager(integration_config)
    integration_manager.register_workflow_runtime(workflow_runtime)
    
    # Initialize the integration
    init_result = await integration_manager.initialize()
    logger.info(f"Integration initialization result: {init_result}")
    
    if not init_result["success"]:
        logger.error("Failed to initialize integration. Exiting.")
        return
    
    # Register a sample workflow
    sample_workflow = {
        "workflow_id": "sample_workflow_001",
        "name": "Sample Manufacturing Workflow",
        "description": "A sample workflow for demonstrating cross-layer integration",
        "industry": "manufacturing",
        "tasks": [
            {
                "task_id": "data_collection",
                "name": "Collect Equipment Data",
                "description": "Collect sensor data from manufacturing equipment",
                "timeout_seconds": 300,
                "retry_count": 3,
                "execution_mode": "autonomous"
            },
            {
                "task_id": "anomaly_detection",
                "name": "Detect Anomalies",
                "description": "Analyze sensor data for anomalies",
                "timeout_seconds": 600,
                "retry_count": 2,
                "execution_mode": "reactive"
            },
            {
                "task_id": "alert_generation",
                "name": "Generate Alerts",
                "description": "Generate alerts for detected anomalies",
                "timeout_seconds": 300,
                "retry_count": 1,
                "execution_mode": "human_in_the_loop"
            }
        ],
        "transitions": [
            {
                "from": "data_collection",
                "to": "anomaly_detection",
                "condition": "success"
            },
            {
                "from": "anomaly_detection",
                "to": "alert_generation",
                "condition": "anomalies_detected"
            }
        ],
        "execution_modes": {
            "autonomous": {
                "trust_threshold": 0.8,
                "confidence_required": 0.9,
                "human_oversight": False
            },
            "reactive": {
                "trust_threshold": 0.6,
                "confidence_required": 0.7,
                "human_oversight": True
            },
            "human_in_the_loop": {
                "trust_threshold": 0.4,
                "confidence_required": 0.5,
                "human_oversight": True
            }
        }
    }
    
    # Register the workflow with the registry
    registry_result = workflow_registry.register_workflow(sample_workflow)
    logger.info(f"Workflow registration result: {registry_result}")
    
    # Register the workflow with the Protocol Layer
    protocol_result = await integration_manager.register_workflow(sample_workflow)
    logger.info(f"Protocol Layer registration result: {protocol_result}")
    
    # Simulate workflow execution
    logger.info("Simulating workflow execution")
    
    # Start the workflow
    workflow_id = sample_workflow["workflow_id"]
    start_result = await workflow_runtime.start_workflow(workflow_id, {
        "equipment_id": "machine_001",
        "sensor_types": ["temperature", "vibration", "pressure"],
        "collection_interval_seconds": 60
    })
    logger.info(f"Workflow start result: {start_result}")
    
    # Update workflow status in Protocol Layer
    status_update = {
        "status": "running",
        "progress": 0.0,
        "current_task": "data_collection",
        "timestamp": datetime.utcnow().isoformat(),
        "related_applications": ["manufacturing_dashboard_app"]
    }
    status_result = await integration_manager.update_workflow_status(workflow_id, status_update)
    logger.info(f"Status update result: {status_result}")
    
    # Simulate task completion
    logger.info("Simulating task completion: data_collection")
    task_result = await workflow_runtime.complete_task(workflow_id, "data_collection", {
        "success": True,
        "data_points": 60,
        "collection_duration_seconds": 65,
        "sensor_readings": {
            "temperature": [35.2, 35.3, 35.4, 35.6, 35.8],
            "vibration": [0.05, 0.06, 0.05, 0.07, 0.08],
            "pressure": [101.3, 101.4, 101.3, 101.2, 101.3]
        }
    })
    logger.info(f"Task completion result: {task_result}")
    
    # Update workflow status in Protocol Layer
    status_update = {
        "status": "running",
        "progress": 0.33,
        "current_task": "anomaly_detection",
        "timestamp": datetime.utcnow().isoformat(),
        "related_applications": ["manufacturing_dashboard_app"]
    }
    status_result = await integration_manager.update_workflow_status(workflow_id, status_update)
    logger.info(f"Status update result: {status_result}")
    
    # Get prediction from Core AI Layer
    prediction_data = {
        "sensor_readings": {
            "temperature": [35.2, 35.3, 35.4, 35.6, 35.8],
            "vibration": [0.05, 0.06, 0.05, 0.07, 0.08],
            "pressure": [101.3, 101.4, 101.3, 101.2, 101.3]
        },
        "equipment_id": "machine_001",
        "model_type": "anomaly_detection"
    }
    prediction_result = await integration_manager.get_prediction_for_workflow(workflow_id, prediction_data)
    logger.info(f"Prediction result: {prediction_result}")
    
    # Simulate anomaly detection task completion
    logger.info("Simulating task completion: anomaly_detection")
    task_result = await workflow_runtime.complete_task(workflow_id, "anomaly_detection", {
        "success": True,
        "anomalies_detected": True,
        "anomaly_count": 2,
        "anomaly_details": [
            {
                "sensor": "vibration",
                "timestamp": "2025-05-22T15:30:45Z",
                "value": 0.08,
                "threshold": 0.07,
                "confidence": 0.85
            },
            {
                "sensor": "temperature",
                "timestamp": "2025-05-22T15:30:55Z",
                "value": 35.8,
                "threshold": 35.5,
                "confidence": 0.75
            }
        ]
    })
    logger.info(f"Task completion result: {task_result}")
    
    # Update workflow status in Protocol Layer
    status_update = {
        "status": "running",
        "progress": 0.66,
        "current_task": "alert_generation",
        "timestamp": datetime.utcnow().isoformat(),
        "related_applications": ["manufacturing_dashboard_app", "maintenance_app"]
    }
    status_result = await integration_manager.update_workflow_status(workflow_id, status_update)
    logger.info(f"Status update result: {status_result}")
    
    # Simulate human intervention request
    logger.info("Simulating human intervention request")
    intervention_request = {
        "workflow_id": workflow_id,
        "task_id": "alert_generation",
        "intervention_type": "approval",
        "reason": "High severity alerts require human approval",
        "data": {
            "anomaly_count": 2,
            "max_severity": "high",
            "recommended_action": "schedule_maintenance"
        },
        "timeout_seconds": 300
    }
    intervention_result = await human_agent.request_intervention(intervention_request)
    logger.info(f"Human intervention request result: {intervention_result}")
    
    # Simulate human intervention response
    logger.info("Simulating human intervention response")
    intervention_response = {
        "intervention_id": intervention_result["intervention_id"],
        "workflow_id": workflow_id,
        "task_id": "alert_generation",
        "response": "approved",
        "notes": "Approved maintenance scheduling",
        "user_id": "maintenance_supervisor_001"
    }
    response_result = await human_agent.process_intervention_response(intervention_response)
    logger.info(f"Human intervention response result: {response_result}")
    
    # Simulate alert generation task completion
    logger.info("Simulating task completion: alert_generation")
    task_result = await workflow_runtime.complete_task(workflow_id, "alert_generation", {
        "success": True,
        "alerts_generated": 2,
        "alert_ids": ["alert_001", "alert_002"],
        "maintenance_scheduled": True,
        "maintenance_id": "maint_job_123",
        "scheduled_time": "2025-05-23T09:00:00Z"
    })
    logger.info(f"Task completion result: {task_result}")
    
    # Complete the workflow
    logger.info("Completing workflow")
    completion_result = await workflow_runtime.complete_workflow(workflow_id, {
        "success": True,
        "total_tasks_completed": 3,
        "total_duration_seconds": 1200,
        "anomalies_detected": 2,
        "alerts_generated": 2,
        "maintenance_scheduled": True
    })
    logger.info(f"Workflow completion result: {completion_result}")
    
    # Update workflow status in Protocol Layer
    status_update = {
        "status": "completed",
        "progress": 1.0,
        "current_task": None,
        "timestamp": datetime.utcnow().isoformat(),
        "related_applications": ["manufacturing_dashboard_app", "maintenance_app"],
        "completion_details": {
            "success": True,
            "total_tasks_completed": 3,
            "total_duration_seconds": 1200,
            "anomalies_detected": 2,
            "alerts_generated": 2,
            "maintenance_scheduled": True
        }
    }
    status_result = await integration_manager.update_workflow_status(workflow_id, status_update)
    logger.info(f"Final status update result: {status_result}")
    
    # Check system health
    health_result = await integration_manager.check_system_health()
    logger.info(f"System health check result: {health_result}")
    
    logger.info("Cross-layer integration example completed successfully")


if __name__ == "__main__":
    asyncio.run(run_integration_example())
