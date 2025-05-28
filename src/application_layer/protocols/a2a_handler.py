"""
A2A (Agent-to-Agent) Handler for the Industriverse Application Layer.

This module provides A2A protocol integration for the Application Layer,
implementing handlers for A2A tasks and protocol-specific interfaces.
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class A2AHandler:
    """
    A2A protocol handler for the Application Layer.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the A2A Handler.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        self.task_handlers = self._register_task_handlers()
        self.tasks = {}
        self.task_history = []
        self.max_history = 100
        
        logger.info("A2A Handler initialized")
    
    def _register_task_handlers(self) -> Dict[str, callable]:
        """
        Register task handlers.
        
        Returns:
            Dictionary of task handlers
        """
        return {
            "task_submission": self._handle_task_submission,
            "task_status_update": self._handle_task_status_update,
            "task_completion": self._handle_task_completion,
            "agent_discovery": self._handle_agent_discovery
        }
    
    def handle_task(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle A2A task.
        
        Args:
            task_type: Task type
            task_data: Task data
            
        Returns:
            Response data
        """
        # Log task
        logger.info(f"Handling A2A task: {task_type}")
        
        # Add to history
        self._add_to_history(task_type, task_data)
        
        # Check if task type is supported
        if task_type not in self.task_handlers:
            logger.warning(f"Unsupported A2A task type: {task_type}")
            return {"error": f"Unsupported task type: {task_type}"}
        
        # Handle task
        try:
            response = self.task_handlers[task_type](task_data)
            return response
        except Exception as e:
            logger.error(f"Error handling A2A task {task_type}: {e}")
            return {"error": f"Error handling task: {str(e)}"}
    
    def submit_task(self, agent_id: str, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Submit A2A task.
        
        Args:
            agent_id: Target agent ID
            task_type: Task type
            task_data: Task data
            
        Returns:
            Response data
        """
        # Log task
        logger.info(f"Submitting A2A task to agent {agent_id}: {task_type}")
        
        # Generate task ID
        task_id = f"task-{str(uuid.uuid4())}"
        
        # Create task
        task = {
            "task_id": task_id,
            "agent_id": agent_id,
            "task_type": task_type,
            "task_data": task_data,
            "status": "submitted",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Store task
        self.tasks[task_id] = task
        
        # Add to history
        self._add_to_history(task_type, task_data, is_outgoing=True)
        
        # TODO: Implement actual task submission to A2A
        # This is a placeholder for the actual implementation
        
        return {
            "status": "success",
            "task_id": task_id
        }
    
    def update_task_status(self, task_id: str, status: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update A2A task status.
        
        Args:
            task_id: Task ID
            status: Task status
            result: Task result
            
        Returns:
            True if successful, False otherwise
        """
        # Check if task exists
        if task_id not in self.tasks:
            logger.warning(f"Task not found: {task_id}")
            return False
        
        # Get task
        task = self.tasks[task_id]
        
        # Update task
        task["status"] = status
        task["updated_at"] = time.time()
        
        if result:
            task["result"] = result
        
        # Log update
        logger.info(f"Updated task {task_id} status to {status}")
        
        # TODO: Implement actual task status update to A2A
        # This is a placeholder for the actual implementation
        
        return True
    
    def _add_to_history(self, task_type: str, task_data: Dict[str, Any], is_outgoing: bool = False):
        """
        Add task to history.
        
        Args:
            task_type: Task type
            task_data: Task data
            is_outgoing: Whether the task is outgoing
        """
        # Create history entry
        entry = {
            "task_type": task_type,
            "task_data": task_data,
            "timestamp": time.time(),
            "direction": "outgoing" if is_outgoing else "incoming"
        }
        
        # Add to history
        self.task_history.append(entry)
        
        # Trim history if needed
        if len(self.task_history) > self.max_history:
            self.task_history = self.task_history[-self.max_history:]
    
    def get_task_history(self) -> List[Dict[str, Any]]:
        """
        Get task history.
        
        Returns:
            Task history
        """
        return self.task_history
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task or None if not found
        """
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: str) -> List[Dict[str, Any]]:
        """
        Get tasks by status.
        
        Args:
            status: Task status
            
        Returns:
            List of tasks
        """
        return [task for task in self.tasks.values() if task["status"] == status]
    
    def _handle_task_submission(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task submission.
        
        Args:
            task_data: Task data
            
        Returns:
            Response data
        """
        logger.info("Handling task submission")
        
        # Extract task information
        task_id = task_data.get("task_id", f"task-{str(uuid.uuid4())}")
        task_type = task_data.get("task_type", "")
        task_params = task_data.get("task_params", {})
        
        # Validate task type
        if not task_type:
            return {
                "status": "error",
                "error": "Missing task type"
            }
        
        # Create task
        task = {
            "task_id": task_id,
            "task_type": task_type,
            "task_params": task_params,
            "status": "working",
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Store task
        self.tasks[task_id] = task
        
        # Process task based on type
        if task_type == "workflow_execution":
            # Get workflow component
            workflow_component = self.agent_core.get_component("workflow_orchestrator")
            
            if not workflow_component:
                task["status"] = "failed"
                task["error"] = "Workflow orchestrator not found"
                return {
                    "status": "error",
                    "error": "Workflow orchestrator not found",
                    "task_id": task_id
                }
            
            # Execute workflow
            if hasattr(workflow_component, "execute_workflow"):
                workflow_id = task_params.get("workflow_id", "")
                workflow_data = task_params.get("workflow_data", {})
                
                try:
                    # Start workflow execution asynchronously
                    workflow_component.start_workflow_execution(task_id, workflow_id, workflow_data)
                    
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "message": "Workflow execution started"
                    }
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    return {
                        "status": "error",
                        "error": str(e),
                        "task_id": task_id
                    }
            else:
                task["status"] = "failed"
                task["error"] = "Workflow execution not supported"
                return {
                    "status": "error",
                    "error": "Workflow execution not supported",
                    "task_id": task_id
                }
        elif task_type == "data_request":
            # Get data component
            data_connector = self.agent_core.get_component("data_layer_connector")
            
            if not data_connector:
                task["status"] = "failed"
                task["error"] = "Data layer connector not found"
                return {
                    "status": "error",
                    "error": "Data layer connector not found",
                    "task_id": task_id
                }
            
            # Request data
            if hasattr(data_connector, "request_data"):
                data_query = task_params.get("query", {})
                
                try:
                    # Start data request asynchronously
                    data_connector.start_data_request(task_id, data_query)
                    
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "message": "Data request started"
                    }
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    return {
                        "status": "error",
                        "error": str(e),
                        "task_id": task_id
                    }
            else:
                task["status"] = "failed"
                task["error"] = "Data request not supported"
                return {
                    "status": "error",
                    "error": "Data request not supported",
                    "task_id": task_id
                }
        elif task_type == "ai_inference":
            # Get AI component
            ai_connector = self.agent_core.get_component("core_ai_layer_connector")
            
            if not ai_connector:
                task["status"] = "failed"
                task["error"] = "Core AI layer connector not found"
                return {
                    "status": "error",
                    "error": "Core AI layer connector not found",
                    "task_id": task_id
                }
            
            # Request inference
            if hasattr(ai_connector, "request_inference"):
                inference_params = task_params.get("inference_params", {})
                
                try:
                    # Start inference request asynchronously
                    ai_connector.start_inference_request(task_id, inference_params)
                    
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "message": "AI inference request started"
                    }
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    return {
                        "status": "error",
                        "error": str(e),
                        "task_id": task_id
                    }
            else:
                task["status"] = "failed"
                task["error"] = "AI inference not supported"
                return {
                    "status": "error",
                    "error": "AI inference not supported",
                    "task_id": task_id
                }
        elif task_type == "generate_artifact":
            # Get generative component
            generative_connector = self.agent_core.get_component("generative_layer_connector")
            
            if not generative_connector:
                task["status"] = "failed"
                task["error"] = "Generative layer connector not found"
                return {
                    "status": "error",
                    "error": "Generative layer connector not found",
                    "task_id": task_id
                }
            
            # Request artifact generation
            if hasattr(generative_connector, "generate_artifact"):
                generation_params = task_params.get("generation_params", {})
                
                try:
                    # Start artifact generation asynchronously
                    generative_connector.start_artifact_generation(task_id, generation_params)
                    
                    return {
                        "status": "success",
                        "task_id": task_id,
                        "message": "Artifact generation started"
                    }
                except Exception as e:
                    task["status"] = "failed"
                    task["error"] = str(e)
                    return {
                        "status": "error",
                        "error": str(e),
                        "task_id": task_id
                    }
            else:
                task["status"] = "failed"
                task["error"] = "Artifact generation not supported"
                return {
                    "status": "error",
                    "error": "Artifact generation not supported",
                    "task_id": task_id
                }
        else:
            # Unknown task type
            task["status"] = "failed"
            task["error"] = f"Unsupported task type: {task_type}"
            return {
                "status": "error",
                "error": f"Unsupported task type: {task_type}",
                "task_id": task_id
            }
    
    def _handle_task_status_update(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task status update.
        
        Args:
            task_data: Task data
            
        Returns:
            Response data
        """
        logger.info("Handling task status update")
        
        # Extract task information
        task_id = task_data.get("task_id", "")
        status = task_data.get("status", "")
        
        # Validate task ID
        if not task_id:
            return {
                "status": "error",
                "error": "Missing task ID"
            }
        
        # Validate status
        if not status:
            return {
                "status": "error",
                "error": "Missing status"
            }
        
        # Check if task exists
        if task_id not in self.tasks:
            return {
                "status": "error",
                "error": f"Task not found: {task_id}"
            }
        
        # Get task
        task = self.tasks[task_id]
        
        # Update task
        task["status"] = status
        task["updated_at"] = time.time()
        
        # Add additional data if provided
        if "result" in task_data:
            task["result"] = task_data["result"]
        
        if "error" in task_data:
            task["error"] = task_data["error"]
        
        if "progress" in task_data:
            task["progress"] = task_data["progress"]
        
        # Log update
        logger.info(f"Updated task {task_id} status to {status}")
        
        return {
            "status": "success",
            "task_id": task_id,
            "message": f"Task status updated to {status}"
        }
    
    def _handle_task_completion(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task completion.
        
        Args:
            task_data: Task data
            
        Returns:
            Response data
        """
        logger.info("Handling task completion")
        
        # Extract task information
        task_id = task_data.get("task_id", "")
        result = task_data.get("result", {})
        
        # Validate task ID
        if not task_id:
            return {
                "status": "error",
                "error": "Missing task ID"
            }
        
        # Check if task exists
        if task_id not in self.tasks:
            return {
                "status": "error",
                "error": f"Task not found: {task_id}"
            }
        
        # Get task
        task = self.tasks[task_id]
        
        # Update task
        task["status"] = "completed"
        task["updated_at"] = time.time()
        task["completed_at"] = time.time()
        task["result"] = result
        
        # Log completion
        logger.info(f"Completed task {task_id}")
        
        # Process completion based on task type
        task_type = task.get("task_type", "")
        
        if task_type == "workflow_execution":
            # Get workflow component
            workflow_component = self.agent_core.get_component("workflow_orchestrator")
            
            if workflow_component and hasattr(workflow_component, "handle_workflow_completion"):
                workflow_component.handle_workflow_completion(task_id, result)
        elif task_type == "data_request":
            # Get data component
            data_connector = self.agent_core.get_component("data_layer_connector")
            
            if data_connector and hasattr(data_connector, "handle_data_response"):
                data_connector.handle_data_response(task_id, result)
        elif task_type == "ai_inference":
            # Get AI component
            ai_connector = self.agent_core.get_component("core_ai_layer_connector")
            
            if ai_connector and hasattr(ai_connector, "handle_inference_result"):
                ai_connector.handle_inference_result(task_id, result)
        elif task_type == "generate_artifact":
            # Get generative component
            generative_connector = self.agent_core.get_component("generative_layer_connector")
            
            if generative_connector and hasattr(generative_connector, "handle_artifact_generation_result"):
                generative_connector.handle_artifact_generation_result(task_id, result)
        
        return {
            "status": "success",
            "task_id": task_id,
            "message": "Task completion acknowledged"
        }
    
    def _handle_agent_discovery(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle agent discovery.
        
        Args:
            task_data: Task data
            
        Returns:
            Response data
        """
        logger.info("Handling agent discovery")
        
        # Get agent card
        agent_card = self.agent_core.get_agent_card()
        
        return {
            "status": "success",
            "agent_card": agent_card
        }
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get handler status.
        
        Returns:
            Handler status
        """
        tasks_by_status = {}
        for task in self.tasks.values():
            status = task.get("status", "unknown")
            if status not in tasks_by_status:
                tasks_by_status[status] = 0
            tasks_by_status[status] += 1
        
        return {
            "status": "operational",
            "tasks_handled": len(self.task_history),
            "active_tasks": len(self.tasks),
            "tasks_by_status": tasks_by_status,
            "supported_tasks": list(self.task_handlers.keys())
        }
