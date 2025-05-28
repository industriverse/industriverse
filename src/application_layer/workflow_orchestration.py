"""
Application Layer Workflow Orchestration for the Industriverse platform.

This module provides workflow orchestration functionality for the Application Layer,
enabling the creation, execution, and monitoring of complex workflows with protocol-native interfaces.
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WorkflowOrchestration:
    """
    Workflow Orchestration for the Industriverse platform.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the Workflow Orchestration.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        self.workflow_templates = {}
        self.workflow_instances = {}
        self.workflow_executions = {}
        self.workflow_tasks = {}
        
        # Register with agent core
        self.agent_core.register_component("workflow_orchestration", self)
        
        logger.info("Workflow Orchestration initialized")
    
    def register_workflow_template(self, template_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new workflow template.
        
        Args:
            template_config: Template configuration
            
        Returns:
            Registration result
        """
        # Validate template configuration
        required_fields = ["template_id", "name", "description", "tasks", "connections"]
        for field in required_fields:
            if field not in template_config:
                return {"error": f"Missing required field: {field}"}
        
        # Generate template ID if not provided
        template_id = template_config.get("template_id", f"workflow-{str(uuid.uuid4())}")
        
        # Add metadata
        template_config["registered_at"] = time.time()
        
        # Store template
        self.workflow_templates[template_id] = template_config
        
        # Log registration
        logger.info(f"Registered workflow template: {template_id}")
        
        return {
            "status": "success",
            "template_id": template_id
        }
    
    def create_workflow_instance(self, template_id: str, instance_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new workflow instance from a template.
        
        Args:
            template_id: Template ID
            instance_config: Instance configuration
            
        Returns:
            Creation result
        """
        # Check if template exists
        if template_id not in self.workflow_templates:
            return {"error": f"Template not found: {template_id}"}
        
        # Get template
        template = self.workflow_templates[template_id]
        
        # Generate instance ID
        instance_id = f"workflow-{str(uuid.uuid4())}"
        
        # Create instance
        instance = {
            "instance_id": instance_id,
            "template_id": template_id,
            "name": instance_config.get("name", template["name"]),
            "description": instance_config.get("description", template["description"]),
            "tasks": template["tasks"].copy(),
            "connections": template["connections"].copy(),
            "status": "created",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Add instance-specific configuration
        for key, value in instance_config.items():
            if key not in ["instance_id", "template_id", "created_at", "updated_at"]:
                instance[key] = value
        
        # Store instance
        self.workflow_instances[instance_id] = instance
        
        # Log creation
        logger.info(f"Created workflow instance: {instance_id} from template: {template_id}")
        
        # Emit MCP event for workflow creation
        self.agent_core.emit_mcp_event("application/workflow", {
            "action": "create_instance",
            "instance_id": instance_id,
            "template_id": template_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "instance": instance
        }
    
    def get_workflow_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow instance by ID.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            Instance data or None if not found
        """
        return self.workflow_instances.get(instance_id)
    
    def update_workflow_instance(self, instance_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a workflow instance.
        
        Args:
            instance_id: Instance ID
            update_data: Update data
            
        Returns:
            Update result
        """
        # Check if instance exists
        if instance_id not in self.workflow_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Get instance
        instance = self.workflow_instances[instance_id]
        
        # Update instance
        for key, value in update_data.items():
            if key not in ["instance_id", "template_id", "created_at"]:
                instance[key] = value
        
        # Update timestamp
        instance["updated_at"] = time.time()
        
        # Log update
        logger.info(f"Updated workflow instance: {instance_id}")
        
        # Emit MCP event for workflow update
        self.agent_core.emit_mcp_event("application/workflow", {
            "action": "update_instance",
            "instance_id": instance_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "instance_id": instance_id,
            "instance": instance
        }
    
    def execute_workflow(self, instance_id: str, execution_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow instance.
        
        Args:
            instance_id: Instance ID
            execution_config: Execution configuration
            
        Returns:
            Execution result
        """
        # Check if instance exists
        if instance_id not in self.workflow_instances:
            return {"error": f"Instance not found: {instance_id}"}
        
        # Get instance
        instance = self.workflow_instances[instance_id]
        
        # Generate execution ID
        execution_id = f"exec-{str(uuid.uuid4())}"
        
        # Create execution
        execution = {
            "execution_id": execution_id,
            "instance_id": instance_id,
            "status": "running",
            "start_time": time.time(),
            "end_time": None,
            "task_statuses": {},
            "task_results": {},
            "current_tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "input_data": execution_config.get("input_data", {}),
            "output_data": {}
        }
        
        # Initialize task statuses
        for task in instance["tasks"]:
            task_id = task["task_id"]
            execution["task_statuses"][task_id] = "pending"
        
        # Find start tasks (tasks with no incoming connections)
        start_tasks = []
        for task in instance["tasks"]:
            task_id = task["task_id"]
            has_incoming = False
            for connection in instance["connections"]:
                if connection["target"] == task_id:
                    has_incoming = True
                    break
            
            if not has_incoming:
                start_tasks.append(task_id)
                execution["task_statuses"][task_id] = "ready"
                execution["current_tasks"].append(task_id)
        
        # Store execution
        self.workflow_executions[execution_id] = execution
        
        # Log execution start
        logger.info(f"Started workflow execution: {execution_id} for instance: {instance_id}")
        
        # Emit MCP event for workflow execution
        self.agent_core.emit_mcp_event("application/workflow", {
            "action": "execute",
            "instance_id": instance_id,
            "execution_id": execution_id,
            "timestamp": time.time()
        })
        
        # Start execution in background
        self._process_workflow_execution(execution_id)
        
        return {
            "status": "success",
            "execution_id": execution_id,
            "execution": execution
        }
    
    def _process_workflow_execution(self, execution_id: str):
        """
        Process a workflow execution.
        
        Args:
            execution_id: Execution ID
        """
        # This would typically be run in a background thread or async task
        # For simplicity, we'll just simulate the execution here
        
        # Get execution
        execution = self.workflow_executions[execution_id]
        
        # Get instance
        instance_id = execution["instance_id"]
        instance = self.workflow_instances[instance_id]
        
        # Process current tasks
        for task_id in execution["current_tasks"]:
            # Find task
            task = None
            for t in instance["tasks"]:
                if t["task_id"] == task_id:
                    task = t
                    break
            
            if not task:
                logger.error(f"Task not found: {task_id}")
                continue
            
            # Update task status
            execution["task_statuses"][task_id] = "running"
            
            # Execute task
            task_result = self._execute_task(task, execution["input_data"])
            
            # Store task result
            execution["task_results"][task_id] = task_result
            
            # Update task status
            if task_result.get("status") == "success":
                execution["task_statuses"][task_id] = "completed"
                execution["completed_tasks"].append(task_id)
            else:
                execution["task_statuses"][task_id] = "failed"
                execution["failed_tasks"].append(task_id)
            
            # Remove from current tasks
            execution["current_tasks"].remove(task_id)
            
            # Find next tasks
            if task_result.get("status") == "success":
                next_tasks = []
                for connection in instance["connections"]:
                    if connection["source"] == task_id:
                        next_tasks.append(connection["target"])
                
                # Add to current tasks if all dependencies are completed
                for next_task_id in next_tasks:
                    # Check if all dependencies are completed
                    all_dependencies_completed = True
                    for connection in instance["connections"]:
                        if connection["target"] == next_task_id and connection["source"] != task_id:
                            if execution["task_statuses"].get(connection["source"]) != "completed":
                                all_dependencies_completed = False
                                break
                    
                    if all_dependencies_completed:
                        execution["task_statuses"][next_task_id] = "ready"
                        execution["current_tasks"].append(next_task_id)
        
        # Check if execution is complete
        if not execution["current_tasks"] and not execution["failed_tasks"]:
            # All tasks completed successfully
            execution["status"] = "completed"
            execution["end_time"] = time.time()
            
            # Collect output data
            for task_id, task_result in execution["task_results"].items():
                if "output" in task_result:
                    execution["output_data"].update(task_result["output"])
            
            logger.info(f"Workflow execution completed: {execution_id}")
            
            # Emit MCP event for workflow completion
            self.agent_core.emit_mcp_event("application/workflow", {
                "action": "complete",
                "instance_id": instance_id,
                "execution_id": execution_id,
                "timestamp": time.time()
            })
        elif not execution["current_tasks"] and execution["failed_tasks"]:
            # Some tasks failed
            execution["status"] = "failed"
            execution["end_time"] = time.time()
            
            logger.info(f"Workflow execution failed: {execution_id}")
            
            # Emit MCP event for workflow failure
            self.agent_core.emit_mcp_event("application/workflow", {
                "action": "fail",
                "instance_id": instance_id,
                "execution_id": execution_id,
                "timestamp": time.time()
            })
    
    def _execute_task(self, task: Dict[str, Any], input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow task.
        
        Args:
            task: Task configuration
            input_data: Input data
            
        Returns:
            Task execution result
        """
        # This would typically call the actual task implementation
        # For simplicity, we'll just simulate the execution here
        
        task_type = task.get("type", "unknown")
        task_config = task.get("config", {})
        
        # Log task execution
        logger.info(f"Executing task: {task['task_id']} of type: {task_type}")
        
        # Simulate task execution
        time.sleep(0.1)  # Simulate some processing time
        
        # Generate result based on task type
        if task_type == "data_processing":
            # Simulate data processing
            return {
                "status": "success",
                "output": {
                    f"processed_{task['task_id']}": f"Processed data for {task['name']}"
                }
            }
        elif task_type == "decision":
            # Simulate decision
            condition = task_config.get("condition", "true")
            if condition == "true" or eval(condition, {"input": input_data}):
                return {
                    "status": "success",
                    "output": {
                        f"decision_{task['task_id']}": True
                    }
                }
            else:
                return {
                    "status": "success",
                    "output": {
                        f"decision_{task['task_id']}": False
                    }
                }
        elif task_type == "notification":
            # Simulate notification
            return {
                "status": "success",
                "output": {
                    f"notification_{task['task_id']}": f"Notification sent: {task_config.get('message', 'Default message')}"
                }
            }
        elif task_type == "api_call":
            # Simulate API call
            return {
                "status": "success",
                "output": {
                    f"api_result_{task['task_id']}": f"API call result for {task_config.get('endpoint', 'default/endpoint')}"
                }
            }
        else:
            # Unknown task type
            return {
                "status": "error",
                "error": f"Unknown task type: {task_type}"
            }
    
    def get_workflow_execution(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow execution by ID.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Execution data or None if not found
        """
        return self.workflow_executions.get(execution_id)
    
    def get_workflow_executions(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        Get all executions for a workflow instance.
        
        Args:
            instance_id: Instance ID
            
        Returns:
            List of executions
        """
        return [execution for execution in self.workflow_executions.values() if execution["instance_id"] == instance_id]
    
    def cancel_workflow_execution(self, execution_id: str) -> Dict[str, Any]:
        """
        Cancel a workflow execution.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            Cancellation result
        """
        # Check if execution exists
        if execution_id not in self.workflow_executions:
            return {"error": f"Execution not found: {execution_id}"}
        
        # Get execution
        execution = self.workflow_executions[execution_id]
        
        # Check if execution is already completed or failed
        if execution["status"] in ["completed", "failed", "cancelled"]:
            return {"error": f"Execution already {execution['status']}: {execution_id}"}
        
        # Update execution status
        execution["status"] = "cancelled"
        execution["end_time"] = time.time()
        
        # Log cancellation
        logger.info(f"Cancelled workflow execution: {execution_id}")
        
        # Emit MCP event for workflow cancellation
        self.agent_core.emit_mcp_event("application/workflow", {
            "action": "cancel",
            "instance_id": execution["instance_id"],
            "execution_id": execution_id,
            "timestamp": time.time()
        })
        
        return {
            "status": "success",
            "execution_id": execution_id
        }
    
    def get_workflow_templates(self) -> List[Dict[str, Any]]:
        """
        Get all workflow templates.
        
        Returns:
            List of templates
        """
        return list(self.workflow_templates.values())
    
    def get_workflow_instances(self) -> List[Dict[str, Any]]:
        """
        Get all workflow instances.
        
        Returns:
            List of instances
        """
        return list(self.workflow_instances.values())
    
    def initialize_default_templates(self) -> Dict[str, Any]:
        """
        Initialize default workflow templates.
        
        Returns:
            Initialization result
        """
        logger.info("Initializing default workflow templates")
        
        # Define default templates
        default_templates = [
            {
                "template_id": "workflow-predictive-maintenance",
                "name": "Predictive Maintenance Workflow",
                "description": "Workflow for predictive maintenance of industrial equipment",
                "tasks": [
                    {
                        "task_id": "task-data-collection",
                        "name": "Data Collection",
                        "description": "Collect data from equipment sensors",
                        "type": "data_processing",
                        "config": {
                            "data_source": "equipment_sensors",
                            "collection_interval": 60
                        }
                    },
                    {
                        "task_id": "task-data-analysis",
                        "name": "Data Analysis",
                        "description": "Analyze collected data",
                        "type": "data_processing",
                        "config": {
                            "analysis_type": "anomaly_detection",
                            "threshold": 0.8
                        }
                    },
                    {
                        "task_id": "task-decision",
                        "name": "Maintenance Decision",
                        "description": "Decide if maintenance is needed",
                        "type": "decision",
                        "config": {
                            "condition": "input['anomaly_score'] > 0.8"
                        }
                    },
                    {
                        "task_id": "task-notification",
                        "name": "Maintenance Notification",
                        "description": "Send maintenance notification",
                        "type": "notification",
                        "config": {
                            "message": "Maintenance required for equipment",
                            "recipients": ["maintenance_team"]
                        }
                    },
                    {
                        "task_id": "task-schedule",
                        "name": "Maintenance Scheduling",
                        "description": "Schedule maintenance",
                        "type": "api_call",
                        "config": {
                            "endpoint": "maintenance/schedule",
                            "method": "POST"
                        }
                    }
                ],
                "connections": [
                    {
                        "source": "task-data-collection",
                        "target": "task-data-analysis"
                    },
                    {
                        "source": "task-data-analysis",
                        "target": "task-decision"
                    },
                    {
                        "source": "task-decision",
                        "target": "task-notification"
                    },
                    {
                        "source": "task-notification",
                        "target": "task-schedule"
                    }
                ]
            },
            {
                "template_id": "workflow-quality-control",
                "name": "Quality Control Workflow",
                "description": "Workflow for quality control in manufacturing",
                "tasks": [
                    {
                        "task_id": "task-data-collection",
                        "name": "Data Collection",
                        "description": "Collect data from quality sensors",
                        "type": "data_processing",
                        "config": {
                            "data_source": "quality_sensors",
                            "collection_interval": 30
                        }
                    },
                    {
                        "task_id": "task-data-analysis",
                        "name": "Quality Analysis",
                        "description": "Analyze quality data",
                        "type": "data_processing",
                        "config": {
                            "analysis_type": "quality_check",
                            "threshold": 0.9
                        }
                    },
                    {
                        "task_id": "task-decision",
                        "name": "Quality Decision",
                        "description": "Decide if quality is acceptable",
                        "type": "decision",
                        "config": {
                            "condition": "input['quality_score'] > 0.9"
                        }
                    },
                    {
                        "task_id": "task-notification-fail",
                        "name": "Quality Failure Notification",
                        "description": "Send quality failure notification",
                        "type": "notification",
                        "config": {
                            "message": "Quality check failed",
                            "recipients": ["quality_team"]
                        }
                    },
                    {
                        "task_id": "task-notification-pass",
                        "name": "Quality Pass Notification",
                        "description": "Send quality pass notification",
                        "type": "notification",
                        "config": {
                            "message": "Quality check passed",
                            "recipients": ["production_team"]
                        }
                    }
                ],
                "connections": [
                    {
                        "source": "task-data-collection",
                        "target": "task-data-analysis"
                    },
                    {
                        "source": "task-data-analysis",
                        "target": "task-decision"
                    },
                    {
                        "source": "task-decision",
                        "target": "task-notification-fail"
                    },
                    {
                        "source": "task-decision",
                        "target": "task-notification-pass"
                    }
                ]
            },
            {
                "template_id": "workflow-energy-optimization",
                "name": "Energy Optimization Workflow",
                "description": "Workflow for energy optimization in industrial facilities",
                "tasks": [
                    {
                        "task_id": "task-data-collection",
                        "name": "Energy Data Collection",
                        "description": "Collect data from energy meters",
                        "type": "data_processing",
                        "config": {
                            "data_source": "energy_meters",
                            "collection_interval": 300
                        }
                    },
                    {
                        "task_id": "task-data-analysis",
                        "name": "Energy Analysis",
                        "description": "Analyze energy consumption data",
                        "type": "data_processing",
                        "config": {
                            "analysis_type": "consumption_pattern",
                            "window_size": 24
                        }
                    },
                    {
                        "task_id": "task-optimization",
                        "name": "Energy Optimization",
                        "description": "Optimize energy consumption",
                        "type": "data_processing",
                        "config": {
                            "optimization_type": "load_balancing",
                            "target_efficiency": 0.9
                        }
                    },
                    {
                        "task_id": "task-decision",
                        "name": "Optimization Decision",
                        "description": "Decide if optimization is needed",
                        "type": "decision",
                        "config": {
                            "condition": "input['efficiency_gap'] > 0.1"
                        }
                    },
                    {
                        "task_id": "task-apply-optimization",
                        "name": "Apply Optimization",
                        "description": "Apply energy optimization",
                        "type": "api_call",
                        "config": {
                            "endpoint": "energy/optimize",
                            "method": "POST"
                        }
                    },
                    {
                        "task_id": "task-notification",
                        "name": "Optimization Notification",
                        "description": "Send optimization notification",
                        "type": "notification",
                        "config": {
                            "message": "Energy optimization applied",
                            "recipients": ["facility_team"]
                        }
                    }
                ],
                "connections": [
                    {
                        "source": "task-data-collection",
                        "target": "task-data-analysis"
                    },
                    {
                        "source": "task-data-analysis",
                        "target": "task-optimization"
                    },
                    {
                        "source": "task-optimization",
                        "target": "task-decision"
                    },
                    {
                        "source": "task-decision",
                        "target": "task-apply-optimization"
                    },
                    {
                        "source": "task-apply-optimization",
                        "target": "task-notification"
                    }
                ]
            }
        ]
        
        # Register templates
        registered_templates = []
        for template_config in default_templates:
            result = self.register_workflow_template(template_config)
            if "error" not in result:
                registered_templates.append(result["template_id"])
        
        return {
            "status": "success",
            "registered_templates": registered_templates,
            "count": len(registered_templates)
        }
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get component information.
        
        Returns:
            Component information
        """
        return {
            "id": "workflow_orchestration",
            "type": "WorkflowOrchestration",
            "name": "Workflow Orchestration",
            "status": "operational",
            "templates": len(self.workflow_templates),
            "instances": len(self.workflow_instances),
            "executions": len(self.workflow_executions)
        }
    
    def handle_action(self, action_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle component action.
        
        Args:
            action_id: Action ID
            data: Action data
            
        Returns:
            Response data
        """
        # Handle different actions
        if action_id == "register_workflow_template":
            return self.register_workflow_template(data)
        elif action_id == "create_workflow_instance":
            return self.create_workflow_instance(
                data.get("template_id", ""),
                data.get("instance_config", {})
            )
        elif action_id == "get_workflow_instance":
            instance = self.get_workflow_instance(data.get("instance_id", ""))
            return {"instance": instance} if instance else {"error": "Instance not found"}
        elif action_id == "update_workflow_instance":
            return self.update_workflow_instance(
                data.get("instance_id", ""),
                data.get("update_data", {})
            )
        elif action_id == "execute_workflow":
            return self.execute_workflow(
                data.get("instance_id", ""),
                data.get("execution_config", {})
            )
        elif action_id == "get_workflow_execution":
            execution = self.get_workflow_execution(data.get("execution_id", ""))
            return {"execution": execution} if execution else {"error": "Execution not found"}
        elif action_id == "get_workflow_executions":
            return {"executions": self.get_workflow_executions(data.get("instance_id", ""))}
        elif action_id == "cancel_workflow_execution":
            return self.cancel_workflow_execution(data.get("execution_id", ""))
        elif action_id == "get_workflow_templates":
            return {"templates": self.get_workflow_templates()}
        elif action_id == "get_workflow_instances":
            return {"instances": self.get_workflow_instances()}
        elif action_id == "initialize_default_templates":
            return self.initialize_default_templates()
        else:
            return {"error": f"Unsupported action: {action_id}"}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get component status.
        
        Returns:
            Component status
        """
        return {
            "status": "operational",
            "templates": len(self.workflow_templates),
            "instances": len(self.workflow_instances),
            "executions": len(self.workflow_executions),
            "active_executions": len([e for e in self.workflow_executions.values() if e["status"] == "running"])
        }
