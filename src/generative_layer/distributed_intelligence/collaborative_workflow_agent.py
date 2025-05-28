"""
Collaborative Workflow Agent for Industriverse Generative Layer

This module implements the collaborative workflow agent that enables coordinated generation
of bundled artifacts with automatic compliance checks through agent swarms.
"""

import json
import logging
import time
import os
import uuid
from typing import Dict, Any, List, Optional, Tuple, Callable

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CollaborativeWorkflowAgent:
    """
    Implements collaborative workflow capabilities for the Generative Layer.
    Enables coordinated generation of bundled artifacts with automatic compliance checks.
    """
    
    def __init__(self, agent_core=None):
        """
        Initialize the collaborative workflow agent.
        
        Args:
            agent_core: The agent core instance (optional)
        """
        self.agent_core = agent_core
        self.workflows = {}
        self.workflow_instances = {}
        self.agent_participants = {}
        self.workflow_results = {}
        
        # Initialize storage paths
        self.storage_path = os.path.join(os.getcwd(), "workflow_storage")
        os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info("Collaborative Workflow Agent initialized")
    
    def register_workflow(self, 
                         workflow_id: str, 
                         name: str,
                         description: str,
                         steps: List[Dict[str, Any]],
                         metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Register a new collaborative workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Name of the workflow
            description: Description of the workflow
            steps: List of workflow steps
            metadata: Additional metadata (optional)
            
        Returns:
            True if registration was successful, False otherwise
        """
        if workflow_id in self.workflows:
            logger.warning(f"Workflow {workflow_id} already registered")
            return False
        
        timestamp = time.time()
        
        # Create workflow record
        workflow = {
            "id": workflow_id,
            "name": name,
            "description": description,
            "steps": steps,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "status": "registered"
        }
        
        # Store workflow
        self.workflows[workflow_id] = workflow
        
        # Store workflow file
        workflow_path = os.path.join(self.storage_path, f"{workflow_id}_workflow.json")
        with open(workflow_path, 'w') as f:
            json.dump(workflow, f, indent=2)
        
        logger.info(f"Registered workflow {workflow_id}: {name}")
        
        # Emit MCP event for workflow registration
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/workflow/registered",
                {
                    "workflow_id": workflow_id,
                    "name": name
                }
            )
        
        return True
    
    def create_workflow_instance(self, 
                               workflow_id: str, 
                               instance_name: str,
                               parameters: Optional[Dict[str, Any]] = None,
                               participants: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
        """
        Create a new instance of a workflow.
        
        Args:
            workflow_id: ID of the workflow to instantiate
            instance_name: Name for this workflow instance
            parameters: Parameters for the workflow (optional)
            participants: List of participant agents (optional)
            
        Returns:
            Instance ID if successful, None otherwise
        """
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return None
        
        workflow = self.workflows[workflow_id]
        timestamp = time.time()
        instance_id = f"{workflow_id}_{uuid.uuid4().hex[:8]}"
        
        # Create instance record
        instance = {
            "id": instance_id,
            "workflow_id": workflow_id,
            "name": instance_name,
            "parameters": parameters or {},
            "timestamp": timestamp,
            "status": "created",
            "current_step": 0,
            "steps_completed": [],
            "steps_failed": [],
            "participants": participants or []
        }
        
        # Store instance
        self.workflow_instances[instance_id] = instance
        
        # Register participants
        if participants:
            for participant in participants:
                agent_id = participant.get("agent_id")
                if agent_id:
                    if agent_id not in self.agent_participants:
                        self.agent_participants[agent_id] = []
                    
                    self.agent_participants[agent_id].append(instance_id)
        
        # Store instance file
        instance_path = os.path.join(self.storage_path, f"{instance_id}_instance.json")
        with open(instance_path, 'w') as f:
            json.dump(instance, f, indent=2)
        
        logger.info(f"Created workflow instance {instance_id} for workflow {workflow_id}")
        
        # Emit MCP event for instance creation
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/workflow/instance_created",
                {
                    "instance_id": instance_id,
                    "workflow_id": workflow_id,
                    "name": instance_name
                }
            )
        
        return instance_id
    
    def start_workflow_instance(self, instance_id: str) -> bool:
        """
        Start a workflow instance.
        
        Args:
            instance_id: ID of the workflow instance to start
            
        Returns:
            True if successful, False otherwise
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return False
        
        instance = self.workflow_instances[instance_id]
        workflow_id = instance["workflow_id"]
        
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return False
        
        workflow = self.workflows[workflow_id]
        
        # Update instance status
        instance["status"] = "running"
        instance["start_time"] = time.time()
        
        # Store updated instance
        instance_path = os.path.join(self.storage_path, f"{instance_id}_instance.json")
        with open(instance_path, 'w') as f:
            json.dump(instance, f, indent=2)
        
        logger.info(f"Started workflow instance {instance_id}")
        
        # Emit MCP event for instance start
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/workflow/instance_started",
                {
                    "instance_id": instance_id,
                    "workflow_id": workflow_id
                }
            )
        
        # Execute first step
        self._execute_workflow_step(instance_id, 0)
        
        return True
    
    def _execute_workflow_step(self, instance_id: str, step_index: int) -> None:
        """
        Execute a step in a workflow instance.
        
        Args:
            instance_id: ID of the workflow instance
            step_index: Index of the step to execute
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return
        
        instance = self.workflow_instances[instance_id]
        workflow_id = instance["workflow_id"]
        
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return
        
        workflow = self.workflows[workflow_id]
        
        if step_index >= len(workflow["steps"]):
            logger.warning(f"Step index {step_index} out of range for workflow {workflow_id}")
            return
        
        step = workflow["steps"][step_index]
        
        # Update instance current step
        instance["current_step"] = step_index
        
        # Store updated instance
        instance_path = os.path.join(self.storage_path, f"{instance_id}_instance.json")
        with open(instance_path, 'w') as f:
            json.dump(instance, f, indent=2)
        
        logger.info(f"Executing step {step_index} of workflow instance {instance_id}")
        
        # Emit MCP event for step execution
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/workflow/step_executing",
                {
                    "instance_id": instance_id,
                    "workflow_id": workflow_id,
                    "step_index": step_index,
                    "step_name": step.get("name", f"Step {step_index}")
                }
            )
        
        # Execute step based on type
        step_type = step.get("type", "unknown")
        
        if step_type == "agent_task":
            self._execute_agent_task_step(instance_id, step_index, step)
        elif step_type == "parallel_tasks":
            self._execute_parallel_tasks_step(instance_id, step_index, step)
        elif step_type == "conditional":
            self._execute_conditional_step(instance_id, step_index, step)
        elif step_type == "artifact_generation":
            self._execute_artifact_generation_step(instance_id, step_index, step)
        elif step_type == "compliance_check":
            self._execute_compliance_check_step(instance_id, step_index, step)
        else:
            logger.warning(f"Unknown step type {step_type} for step {step_index} of workflow {workflow_id}")
            self._mark_step_failed(instance_id, step_index, f"Unknown step type: {step_type}")
    
    def _execute_agent_task_step(self, instance_id: str, step_index: int, step: Dict[str, Any]) -> None:
        """
        Execute an agent task step.
        
        Args:
            instance_id: ID of the workflow instance
            step_index: Index of the step
            step: Step configuration
        """
        agent_id = step.get("agent_id")
        task = step.get("task", {})
        
        if not agent_id:
            self._mark_step_failed(instance_id, step_index, "Missing agent_id in agent_task step")
            return
        
        # In a real implementation, this would delegate to the agent
        # For now, we'll simulate success
        
        # Simulate task execution
        time.sleep(1)  # Simulate work
        
        # Mark step as completed
        result = {
            "status": "success",
            "agent_id": agent_id,
            "task_id": str(uuid.uuid4()),
            "output": {
                "message": f"Task completed by agent {agent_id}",
                "timestamp": time.time()
            }
        }
        
        self._mark_step_completed(instance_id, step_index, result)
    
    def _execute_parallel_tasks_step(self, instance_id: str, step_index: int, step: Dict[str, Any]) -> None:
        """
        Execute parallel tasks step.
        
        Args:
            instance_id: ID of the workflow instance
            step_index: Index of the step
            step: Step configuration
        """
        tasks = step.get("tasks", [])
        
        if not tasks:
            self._mark_step_failed(instance_id, step_index, "No tasks defined in parallel_tasks step")
            return
        
        # In a real implementation, this would execute tasks in parallel
        # For now, we'll simulate sequential execution
        
        results = []
        
        for i, task in enumerate(tasks):
            # Simulate task execution
            time.sleep(0.5)  # Simulate work
            
            agent_id = task.get("agent_id", "unknown")
            
            # Add result
            results.append({
                "task_index": i,
                "agent_id": agent_id,
                "status": "success",
                "output": {
                    "message": f"Task {i} completed by agent {agent_id}",
                    "timestamp": time.time()
                }
            })
        
        # Mark step as completed
        result = {
            "status": "success",
            "task_count": len(tasks),
            "task_results": results
        }
        
        self._mark_step_completed(instance_id, step_index, result)
    
    def _execute_conditional_step(self, instance_id: str, step_index: int, step: Dict[str, Any]) -> None:
        """
        Execute a conditional step.
        
        Args:
            instance_id: ID of the workflow instance
            step_index: Index of the step
            step: Step configuration
        """
        condition = step.get("condition", {})
        condition_type = condition.get("type", "unknown")
        
        # Evaluate condition
        condition_result = False
        
        if condition_type == "parameter_check":
            # Check a parameter value
            parameter = condition.get("parameter", "")
            operator = condition.get("operator", "equals")
            value = condition.get("value")
            
            if instance_id in self.workflow_instances:
                instance = self.workflow_instances[instance_id]
                parameter_value = instance.get("parameters", {}).get(parameter)
                
                if operator == "equals":
                    condition_result = parameter_value == value
                elif operator == "not_equals":
                    condition_result = parameter_value != value
                elif operator == "contains":
                    condition_result = value in parameter_value if parameter_value else False
                elif operator == "greater_than":
                    condition_result = parameter_value > value if parameter_value is not None else False
                elif operator == "less_than":
                    condition_result = parameter_value < value if parameter_value is not None else False
        
        elif condition_type == "result_check":
            # Check a previous step result
            previous_step = condition.get("step_index", -1)
            result_path = condition.get("result_path", "")
            operator = condition.get("operator", "equals")
            value = condition.get("value")
            
            if instance_id in self.workflow_instances:
                instance = self.workflow_instances[instance_id]
                
                if previous_step >= 0 and previous_step < step_index and previous_step in instance.get("steps_completed", []):
                    previous_result = self.workflow_results.get(f"{instance_id}_{previous_step}", {})
                    
                    # Get value from result path
                    result_value = self._get_nested_value(previous_result, result_path)
                    
                    if operator == "equals":
                        condition_result = result_value == value
                    elif operator == "not_equals":
                        condition_result = result_value != value
                    elif operator == "contains":
                        condition_result = value in result_value if result_value else False
                    elif operator == "greater_than":
                        condition_result = result_value > value if result_value is not None else False
                    elif operator == "less_than":
                        condition_result = result_value < value if result_value is not None else False
        
        # Execute branch based on condition result
        if condition_result:
            # Execute true branch
            true_branch = step.get("true_branch", {})
            branch_type = true_branch.get("type", "next_step")
            
            if branch_type == "next_step":
                # Continue to next step
                result = {
                    "status": "success",
                    "condition_result": True,
                    "branch_taken": "true_branch",
                    "action": "next_step"
                }
                
                self._mark_step_completed(instance_id, step_index, result)
            
            elif branch_type == "goto_step":
                # Go to a specific step
                goto_step = true_branch.get("step_index", step_index + 1)
                
                result = {
                    "status": "success",
                    "condition_result": True,
                    "branch_taken": "true_branch",
                    "action": "goto_step",
                    "goto_step": goto_step
                }
                
                self._mark_step_completed(instance_id, step_index, result)
                
                # Execute the target step
                self._execute_workflow_step(instance_id, goto_step)
                return  # Skip normal next step execution
            
            elif branch_type == "execute_steps":
                # Execute a sequence of steps
                steps_to_execute = true_branch.get("steps", [])
                
                # In a real implementation, this would execute the steps
                # For now, we'll simulate success
                
                result = {
                    "status": "success",
                    "condition_result": True,
                    "branch_taken": "true_branch",
                    "action": "execute_steps",
                    "steps_executed": len(steps_to_execute)
                }
                
                self._mark_step_completed(instance_id, step_index, result)
        
        else:
            # Execute false branch
            false_branch = step.get("false_branch", {})
            branch_type = false_branch.get("type", "next_step")
            
            if branch_type == "next_step":
                # Continue to next step
                result = {
                    "status": "success",
                    "condition_result": False,
                    "branch_taken": "false_branch",
                    "action": "next_step"
                }
                
                self._mark_step_completed(instance_id, step_index, result)
            
            elif branch_type == "goto_step":
                # Go to a specific step
                goto_step = false_branch.get("step_index", step_index + 1)
                
                result = {
                    "status": "success",
                    "condition_result": False,
                    "branch_taken": "false_branch",
                    "action": "goto_step",
                    "goto_step": goto_step
                }
                
                self._mark_step_completed(instance_id, step_index, result)
                
                # Execute the target step
                self._execute_workflow_step(instance_id, goto_step)
                return  # Skip normal next step execution
            
            elif branch_type == "execute_steps":
                # Execute a sequence of steps
                steps_to_execute = false_branch.get("steps", [])
                
                # In a real implementation, this would execute the steps
                # For now, we'll simulate success
                
                result = {
                    "status": "success",
                    "condition_result": False,
                    "branch_taken": "false_branch",
                    "action": "execute_steps",
                    "steps_executed": len(steps_to_execute)
                }
                
                self._mark_step_completed(instance_id, step_index, result)
    
    def _execute_artifact_generation_step(self, instance_id: str, step_index: int, step: Dict[str, Any]) -> None:
        """
        Execute an artifact generation step.
        
        Args:
            instance_id: ID of the workflow instance
            step_index: Index of the step
            step: Step configuration
        """
        artifact_type = step.get("artifact_type", "unknown")
        generator_agent_id = step.get("generator_agent_id")
        parameters = step.get("parameters", {})
        
        if not generator_agent_id:
            self._mark_step_failed(instance_id, step_index, "Missing generator_agent_id in artifact_generation step")
            return
        
        # In a real implementation, this would delegate to the generator agent
        # For now, we'll simulate artifact generation
        
        # Generate a unique artifact ID
        artifact_id = f"{artifact_type}_{uuid.uuid4().hex[:8]}"
        
        # Simulate artifact generation
        time.sleep(1.5)  # Simulate work
        
        # Generate ZK proof hash for traceability
        zk_proof_hash = f"zk_{uuid.uuid4().hex}"
        
        # Mark step as completed
        result = {
            "status": "success",
            "artifact_id": artifact_id,
            "artifact_type": artifact_type,
            "generator_agent_id": generator_agent_id,
            "zk_proof_hash": zk_proof_hash,
            "timestamp": time.time(),
            "metadata": {
                "size": 1024,
                "format": "json",
                "parameters_used": parameters
            }
        }
        
        self._mark_step_completed(instance_id, step_index, result)
    
    def _execute_compliance_check_step(self, instance_id: str, step_index: int, step: Dict[str, Any]) -> None:
        """
        Execute a compliance check step.
        
        Args:
            instance_id: ID of the workflow instance
            step_index: Index of the step
            step: Step configuration
        """
        compliance_type = step.get("compliance_type", "unknown")
        artifact_step_index = step.get("artifact_step_index", -1)
        checker_agent_id = step.get("checker_agent_id")
        
        if not checker_agent_id:
            self._mark_step_failed(instance_id, step_index, "Missing checker_agent_id in compliance_check step")
            return
        
        if artifact_step_index < 0:
            self._mark_step_failed(instance_id, step_index, "Invalid artifact_step_index in compliance_check step")
            return
        
        # Get the artifact from the previous step
        artifact_result_key = f"{instance_id}_{artifact_step_index}"
        artifact_result = self.workflow_results.get(artifact_result_key, {})
        
        if not artifact_result:
            self._mark_step_failed(instance_id, step_index, f"No result found for artifact step {artifact_step_index}")
            return
        
        artifact_id = artifact_result.get("artifact_id")
        
        if not artifact_id:
            self._mark_step_failed(instance_id, step_index, f"No artifact_id found in result for step {artifact_step_index}")
            return
        
        # In a real implementation, this would delegate to the checker agent
        # For now, we'll simulate compliance checking
        
        # Simulate compliance check
        time.sleep(1)  # Simulate work
        
        # Randomly determine compliance (90% chance of success)
        import random
        is_compliant = random.random() < 0.9
        
        if is_compliant:
            # Mark step as completed
            result = {
                "status": "success",
                "compliance_type": compliance_type,
                "artifact_id": artifact_id,
                "checker_agent_id": checker_agent_id,
                "is_compliant": True,
                "timestamp": time.time(),
                "details": {
                    "checks_performed": 5,
                    "checks_passed": 5,
                    "compliance_score": 1.0
                }
            }
            
            self._mark_step_completed(instance_id, step_index, result)
        else:
            # Mark step as failed
            failure_reason = f"Artifact {artifact_id} failed compliance check: {compliance_type}"
            
            result = {
                "status": "failed",
                "compliance_type": compliance_type,
                "artifact_id": artifact_id,
                "checker_agent_id": checker_agent_id,
                "is_compliant": False,
                "timestamp": time.time(),
                "details": {
                    "checks_performed": 5,
                    "checks_passed": 4,
                    "compliance_score": 0.8,
                    "failed_checks": ["check3"]
                }
            }
            
            self._mark_step_failed(instance_id, step_index, failure_reason, result)
    
    def _mark_step_completed(self, instance_id: str, step_index: int, result: Dict[str, Any]) -> None:
        """
        Mark a workflow step as completed.
        
        Args:
            instance_id: ID of the workflow instance
            step_index: Index of the step
            result: Result of the step execution
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return
        
        instance = self.workflow_instances[instance_id]
        workflow_id = instance["workflow_id"]
        
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return
        
        workflow = self.workflows[workflow_id]
        
        # Store result
        result_key = f"{instance_id}_{step_index}"
        self.workflow_results[result_key] = result
        
        # Update instance
        if step_index not in instance["steps_completed"]:
            instance["steps_completed"].append(step_index)
        
        # Store result file
        result_path = os.path.join(self.storage_path, f"{result_key}_result.json")
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Store updated instance
        instance_path = os.path.join(self.storage_path, f"{instance_id}_instance.json")
        with open(instance_path, 'w') as f:
            json.dump(instance, f, indent=2)
        
        logger.info(f"Completed step {step_index} of workflow instance {instance_id}")
        
        # Emit MCP event for step completion
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/workflow/step_completed",
                {
                    "instance_id": instance_id,
                    "workflow_id": workflow_id,
                    "step_index": step_index,
                    "step_name": workflow["steps"][step_index].get("name", f"Step {step_index}")
                }
            )
        
        # Check if workflow is complete
        if len(instance["steps_completed"]) + len(instance["steps_failed"]) >= len(workflow["steps"]):
            self._complete_workflow_instance(instance_id)
        else:
            # Execute next step
            next_step = step_index + 1
            
            # Check if next step exists
            if next_step < len(workflow["steps"]):
                self._execute_workflow_step(instance_id, next_step)
    
    def _mark_step_failed(self, instance_id: str, step_index: int, reason: str, result: Optional[Dict[str, Any]] = None) -> None:
        """
        Mark a workflow step as failed.
        
        Args:
            instance_id: ID of the workflow instance
            step_index: Index of the step
            reason: Reason for failure
            result: Result of the step execution (optional)
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return
        
        instance = self.workflow_instances[instance_id]
        workflow_id = instance["workflow_id"]
        
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return
        
        workflow = self.workflows[workflow_id]
        
        # Create result if not provided
        if result is None:
            result = {
                "status": "failed",
                "reason": reason,
                "timestamp": time.time()
            }
        
        # Store result
        result_key = f"{instance_id}_{step_index}"
        self.workflow_results[result_key] = result
        
        # Update instance
        if step_index not in instance["steps_failed"]:
            instance["steps_failed"].append(step_index)
        
        # Store result file
        result_path = os.path.join(self.storage_path, f"{result_key}_result.json")
        with open(result_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        # Store updated instance
        instance_path = os.path.join(self.storage_path, f"{instance_id}_instance.json")
        with open(instance_path, 'w') as f:
            json.dump(instance, f, indent=2)
        
        logger.warning(f"Failed step {step_index} of workflow instance {instance_id}: {reason}")
        
        # Emit MCP event for step failure
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/workflow/step_failed",
                {
                    "instance_id": instance_id,
                    "workflow_id": workflow_id,
                    "step_index": step_index,
                    "step_name": workflow["steps"][step_index].get("name", f"Step {step_index}"),
                    "reason": reason
                }
            )
        
        # Check if workflow should be failed
        fail_on_error = workflow.get("fail_on_error", True)
        
        if fail_on_error:
            self._fail_workflow_instance(instance_id, f"Step {step_index} failed: {reason}")
        else:
            # Check if workflow is complete
            if len(instance["steps_completed"]) + len(instance["steps_failed"]) >= len(workflow["steps"]):
                self._complete_workflow_instance(instance_id)
            else:
                # Execute next step
                next_step = step_index + 1
                
                # Check if next step exists
                if next_step < len(workflow["steps"]):
                    self._execute_workflow_step(instance_id, next_step)
    
    def _complete_workflow_instance(self, instance_id: str) -> None:
        """
        Mark a workflow instance as completed.
        
        Args:
            instance_id: ID of the workflow instance
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return
        
        instance = self.workflow_instances[instance_id]
        workflow_id = instance["workflow_id"]
        
        # Update instance status
        instance["status"] = "completed"
        instance["end_time"] = time.time()
        
        # Calculate duration
        if "start_time" in instance:
            instance["duration"] = instance["end_time"] - instance["start_time"]
        
        # Store updated instance
        instance_path = os.path.join(self.storage_path, f"{instance_id}_instance.json")
        with open(instance_path, 'w') as f:
            json.dump(instance, f, indent=2)
        
        logger.info(f"Completed workflow instance {instance_id}")
        
        # Emit MCP event for instance completion
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/workflow/instance_completed",
                {
                    "instance_id": instance_id,
                    "workflow_id": workflow_id
                }
            )
    
    def _fail_workflow_instance(self, instance_id: str, reason: str) -> None:
        """
        Mark a workflow instance as failed.
        
        Args:
            instance_id: ID of the workflow instance
            reason: Reason for failure
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return
        
        instance = self.workflow_instances[instance_id]
        workflow_id = instance["workflow_id"]
        
        # Update instance status
        instance["status"] = "failed"
        instance["end_time"] = time.time()
        instance["failure_reason"] = reason
        
        # Calculate duration
        if "start_time" in instance:
            instance["duration"] = instance["end_time"] - instance["start_time"]
        
        # Store updated instance
        instance_path = os.path.join(self.storage_path, f"{instance_id}_instance.json")
        with open(instance_path, 'w') as f:
            json.dump(instance, f, indent=2)
        
        logger.warning(f"Failed workflow instance {instance_id}: {reason}")
        
        # Emit MCP event for instance failure
        if self.agent_core:
            self.agent_core.send_mcp_event(
                "generative_layer/workflow/instance_failed",
                {
                    "instance_id": instance_id,
                    "workflow_id": workflow_id,
                    "reason": reason
                }
            )
    
    def get_workflow_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow instance by ID.
        
        Args:
            instance_id: ID of the workflow instance
            
        Returns:
            Instance data if found, None otherwise
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return None
        
        return self.workflow_instances[instance_id]
    
    def get_workflow_instance_results(self, instance_id: str) -> Dict[str, Any]:
        """
        Get all results for a workflow instance.
        
        Args:
            instance_id: ID of the workflow instance
            
        Returns:
            Dictionary of step results
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return {}
        
        instance = self.workflow_instances[instance_id]
        workflow_id = instance["workflow_id"]
        
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return {}
        
        workflow = self.workflows[workflow_id]
        
        results = {}
        
        for step_index in range(len(workflow["steps"])):
            result_key = f"{instance_id}_{step_index}"
            if result_key in self.workflow_results:
                results[step_index] = self.workflow_results[result_key]
        
        return results
    
    def get_workflow_instance_artifacts(self, instance_id: str) -> List[Dict[str, Any]]:
        """
        Get all artifacts generated in a workflow instance.
        
        Args:
            instance_id: ID of the workflow instance
            
        Returns:
            List of artifacts
        """
        if instance_id not in self.workflow_instances:
            logger.warning(f"Workflow instance {instance_id} not found")
            return []
        
        instance = self.workflow_instances[instance_id]
        workflow_id = instance["workflow_id"]
        
        if workflow_id not in self.workflows:
            logger.warning(f"Workflow {workflow_id} not found")
            return []
        
        workflow = self.workflows[workflow_id]
        
        artifacts = []
        
        for step_index in range(len(workflow["steps"])):
            result_key = f"{instance_id}_{step_index}"
            if result_key in self.workflow_results:
                result = self.workflow_results[result_key]
                
                # Check if this result contains an artifact
                if "artifact_id" in result:
                    artifacts.append(result)
        
        return artifacts
    
    def _get_nested_value(self, obj: Dict[str, Any], path: str) -> Any:
        """
        Get a nested value from an object using a dot-separated path.
        
        Args:
            obj: The object to get the value from
            path: Path to the value (dot-separated)
            
        Returns:
            Value if found, None otherwise
        """
        if not path:
            return obj
        
        parts = path.split('.')
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def export_workflow_data(self) -> Dict[str, Any]:
        """
        Export workflow data for persistence.
        
        Returns:
            Workflow data
        """
        return {
            "workflows": self.workflows,
            "workflow_instances": self.workflow_instances,
            "agent_participants": self.agent_participants
        }
    
    def import_workflow_data(self, workflow_data: Dict[str, Any]) -> None:
        """
        Import workflow data from persistence.
        
        Args:
            workflow_data: Workflow data to import
        """
        if "workflows" in workflow_data:
            self.workflows = workflow_data["workflows"]
        
        if "workflow_instances" in workflow_data:
            self.workflow_instances = workflow_data["workflow_instances"]
        
        if "agent_participants" in workflow_data:
            self.agent_participants = workflow_data["agent_participants"]
        
        logger.info("Imported workflow data")
    
    def create_workflow_for_offer(self, 
                                offer_id: str, 
                                offer_type: str,
                                offer_parameters: Dict[str, Any]) -> Optional[str]:
        """
        Create a workflow for a specific low-ticket offer.
        
        Args:
            offer_id: ID of the offer
            offer_type: Type of offer
            offer_parameters: Parameters for the offer
            
        Returns:
            Workflow ID if successful, None otherwise
        """
        # Generate a unique workflow ID
        workflow_id = f"offer_{offer_type}_{uuid.uuid4().hex[:8]}"
        
        # Create workflow steps based on offer type
        steps = []
        
        if offer_type == "document_generation":
            # Document generation workflow
            steps = [
                {
                    "name": "Content Planning",
                    "type": "agent_task",
                    "agent_id": "content_planner_agent",
                    "task": {
                        "action": "plan_document",
                        "parameters": offer_parameters
                    }
                },
                {
                    "name": "Content Generation",
                    "type": "artifact_generation",
                    "artifact_type": "document",
                    "generator_agent_id": "document_generator_agent",
                    "parameters": offer_parameters
                },
                {
                    "name": "Compliance Check",
                    "type": "compliance_check",
                    "compliance_type": "document_compliance",
                    "artifact_step_index": 1,
                    "checker_agent_id": "compliance_checker_agent"
                },
                {
                    "name": "Document Formatting",
                    "type": "agent_task",
                    "agent_id": "document_formatter_agent",
                    "task": {
                        "action": "format_document",
                        "parameters": {
                            "artifact_step_index": 1
                        }
                    }
                }
            ]
        
        elif offer_type == "code_generation":
            # Code generation workflow
            steps = [
                {
                    "name": "Requirements Analysis",
                    "type": "agent_task",
                    "agent_id": "requirements_analyzer_agent",
                    "task": {
                        "action": "analyze_requirements",
                        "parameters": offer_parameters
                    }
                },
                {
                    "name": "Architecture Design",
                    "type": "artifact_generation",
                    "artifact_type": "architecture",
                    "generator_agent_id": "architecture_designer_agent",
                    "parameters": offer_parameters
                },
                {
                    "name": "Code Generation",
                    "type": "artifact_generation",
                    "artifact_type": "code",
                    "generator_agent_id": "code_generator_agent",
                    "parameters": offer_parameters
                },
                {
                    "name": "Code Quality Check",
                    "type": "compliance_check",
                    "compliance_type": "code_quality",
                    "artifact_step_index": 2,
                    "checker_agent_id": "code_quality_checker_agent"
                },
                {
                    "name": "Security Check",
                    "type": "compliance_check",
                    "compliance_type": "security",
                    "artifact_step_index": 2,
                    "checker_agent_id": "security_checker_agent"
                },
                {
                    "name": "Documentation Generation",
                    "type": "artifact_generation",
                    "artifact_type": "documentation",
                    "generator_agent_id": "documentation_generator_agent",
                    "parameters": {
                        "code_artifact_step_index": 2
                    }
                }
            ]
        
        elif offer_type == "data_analysis":
            # Data analysis workflow
            steps = [
                {
                    "name": "Data Validation",
                    "type": "agent_task",
                    "agent_id": "data_validator_agent",
                    "task": {
                        "action": "validate_data",
                        "parameters": offer_parameters
                    }
                },
                {
                    "name": "Data Preprocessing",
                    "type": "agent_task",
                    "agent_id": "data_preprocessor_agent",
                    "task": {
                        "action": "preprocess_data",
                        "parameters": offer_parameters
                    }
                },
                {
                    "name": "Analysis Execution",
                    "type": "artifact_generation",
                    "artifact_type": "analysis_results",
                    "generator_agent_id": "data_analyzer_agent",
                    "parameters": offer_parameters
                },
                {
                    "name": "Visualization Generation",
                    "type": "artifact_generation",
                    "artifact_type": "visualizations",
                    "generator_agent_id": "visualization_generator_agent",
                    "parameters": {
                        "analysis_step_index": 2
                    }
                },
                {
                    "name": "Report Generation",
                    "type": "artifact_generation",
                    "artifact_type": "report",
                    "generator_agent_id": "report_generator_agent",
                    "parameters": {
                        "analysis_step_index": 2,
                        "visualization_step_index": 3
                    }
                }
            ]
        
        else:
            # Generic workflow for other offer types
            steps = [
                {
                    "name": "Requirements Analysis",
                    "type": "agent_task",
                    "agent_id": "requirements_analyzer_agent",
                    "task": {
                        "action": "analyze_requirements",
                        "parameters": offer_parameters
                    }
                },
                {
                    "name": "Content Generation",
                    "type": "artifact_generation",
                    "artifact_type": "content",
                    "generator_agent_id": "content_generator_agent",
                    "parameters": offer_parameters
                },
                {
                    "name": "Quality Check",
                    "type": "compliance_check",
                    "compliance_type": "quality",
                    "artifact_step_index": 1,
                    "checker_agent_id": "quality_checker_agent"
                }
            ]
        
        # Register workflow
        success = self.register_workflow(
            workflow_id=workflow_id,
            name=f"{offer_type.replace('_', ' ').title()} Workflow for {offer_id}",
            description=f"Workflow for {offer_type} offer {offer_id}",
            steps=steps,
            metadata={
                "offer_id": offer_id,
                "offer_type": offer_type,
                "offer_parameters": offer_parameters
            }
        )
        
        if success:
            return workflow_id
        else:
            return None
