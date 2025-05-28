"""
Mission Executor for the Deployment Operations Layer.

This module provides mission execution capabilities for orchestrating deployments
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
import threading
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MissionExecutor:
    """
    Executor for deployment missions.
    
    This class provides methods for executing deployment missions, including
    step execution, status tracking, and error handling.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Mission Executor.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.executor_id = config.get("executor_id", f"executor-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9002")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize execution configuration
        self.max_concurrent_steps = config.get("max_concurrent_steps", 10)
        self.execution_timeout = config.get("execution_timeout", 3600)  # 1 hour
        self.step_timeout = config.get("step_timeout", 300)  # 5 minutes
        
        # Initialize active missions
        self.active_missions = {}
        self.mission_lock = threading.RLock()
        
        # Initialize thread pool
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_steps)
        
        # Initialize protocol bridge
        from ..protocol.protocol_bridge import ProtocolBridge
        self.protocol_bridge = ProtocolBridge(config.get("protocol_bridge", {}))
        
        # Initialize layer integration manager
        from ..integration.layer_integration_manager import LayerIntegrationManager
        self.layer_integration = LayerIntegrationManager(config.get("layer_integration", {}))
        
        logger.info(f"Mission Executor {self.executor_id} initialized")
    
    def execute_mission(self, mission_plan: Dict) -> Dict:
        """
        Execute a deployment mission.
        
        Args:
            mission_plan: Mission plan
            
        Returns:
            Dict: Mission execution results
        """
        try:
            # Validate mission plan
            validation_result = self._validate_mission_plan(mission_plan)
            if validation_result.get("status") != "success":
                return validation_result
            
            # Extract mission details
            mission_id = mission_plan.get("mission_id")
            mission_name = mission_plan.get("mission_name", f"mission-{mission_id}")
            execution_plan = mission_plan.get("execution_plan", {})
            steps = execution_plan.get("steps", [])
            
            # Create mission context
            mission_context = {
                "mission_id": mission_id,
                "mission_name": mission_name,
                "mission_plan": mission_plan,
                "start_time": datetime.now().isoformat(),
                "status": "running",
                "steps": {},
                "current_stage": 0,
                "completed_steps": 0,
                "total_steps": len(steps),
                "errors": [],
                "warnings": [],
                "executor_id": self.executor_id
            }
            
            # Register mission
            with self.mission_lock:
                self.active_missions[mission_id] = mission_context
            
            # Execute mission in background thread
            execution_thread = threading.Thread(
                target=self._execute_mission_async,
                args=(mission_id, mission_context, execution_plan),
                daemon=True
            )
            execution_thread.start()
            
            return {
                "status": "success",
                "message": f"Mission {mission_id} started successfully",
                "mission_id": mission_id,
                "mission_name": mission_name,
                "start_time": mission_context["start_time"],
                "total_steps": mission_context["total_steps"]
            }
        except Exception as e:
            logger.error(f"Error starting mission execution: {e}")
            return {"status": "error", "message": str(e)}
    
    def _execute_mission_async(self, mission_id: str, mission_context: Dict, execution_plan: Dict) -> None:
        """
        Execute a mission asynchronously.
        
        Args:
            mission_id: Mission ID
            mission_context: Mission context
            execution_plan: Execution plan
        """
        try:
            # Extract execution details
            strategy = execution_plan.get("strategy", "sequential")
            stages = execution_plan.get("stages", [])
            steps = execution_plan.get("steps", [])
            
            # Execute stages
            for stage_index, stage in enumerate(stages):
                # Update current stage
                with self.mission_lock:
                    if mission_id in self.active_missions:
                        self.active_missions[mission_id]["current_stage"] = stage_index
                
                # Get steps for current stage
                stage_steps = [step for step in steps if step.get("stage") == stage_index]
                
                # Execute stage based on strategy
                if strategy == "sequential":
                    self._execute_sequential_stage(mission_id, mission_context, stage_steps)
                else:  # parallel or hybrid
                    self._execute_parallel_stage(mission_id, mission_context, stage_steps)
            
            # Complete mission
            with self.mission_lock:
                if mission_id in self.active_missions:
                    self.active_missions[mission_id]["status"] = "completed"
                    self.active_missions[mission_id]["end_time"] = datetime.now().isoformat()
                    
                    # Check for errors
                    if self.active_missions[mission_id]["errors"]:
                        self.active_missions[mission_id]["status"] = "completed_with_errors"
            
            logger.info(f"Mission {mission_id} completed")
        except Exception as e:
            logger.error(f"Error executing mission {mission_id}: {e}")
            
            # Update mission status
            with self.mission_lock:
                if mission_id in self.active_missions:
                    self.active_missions[mission_id]["status"] = "failed"
                    self.active_missions[mission_id]["end_time"] = datetime.now().isoformat()
                    self.active_missions[mission_id]["errors"].append(str(e))
    
    def _execute_sequential_stage(self, mission_id: str, mission_context: Dict, steps: List[Dict]) -> None:
        """
        Execute a stage sequentially.
        
        Args:
            mission_id: Mission ID
            mission_context: Mission context
            steps: Steps to execute
        """
        for step in steps:
            step_id = step.get("step_id")
            
            # Execute step
            step_result = self._execute_step(mission_id, mission_context, step)
            
            # Update mission context
            with self.mission_lock:
                if mission_id in self.active_missions:
                    self.active_missions[mission_id]["steps"][step_id] = step_result
                    self.active_missions[mission_id]["completed_steps"] += 1
                    
                    # Check for errors
                    if step_result.get("status") == "error":
                        self.active_missions[mission_id]["errors"].append({
                            "step_id": step_id,
                            "error": step_result.get("message", "Unknown error")
                        })
                        
                        # Stop execution on error
                        if not step.get("continue_on_error", False):
                            logger.error(f"Stopping mission {mission_id} due to error in step {step_id}")
                            self.active_missions[mission_id]["status"] = "failed"
                            return
    
    def _execute_parallel_stage(self, mission_id: str, mission_context: Dict, steps: List[Dict]) -> None:
        """
        Execute a stage in parallel.
        
        Args:
            mission_id: Mission ID
            mission_context: Mission context
            steps: Steps to execute
        """
        # Submit all steps to thread pool
        futures = {}
        for step in steps:
            step_id = step.get("step_id")
            future = self.executor.submit(self._execute_step, mission_id, mission_context, step)
            futures[future] = step_id
        
        # Wait for all steps to complete
        for future in as_completed(futures):
            step_id = futures[future]
            try:
                step_result = future.result()
                
                # Update mission context
                with self.mission_lock:
                    if mission_id in self.active_missions:
                        self.active_missions[mission_id]["steps"][step_id] = step_result
                        self.active_missions[mission_id]["completed_steps"] += 1
                        
                        # Check for errors
                        if step_result.get("status") == "error":
                            self.active_missions[mission_id]["errors"].append({
                                "step_id": step_id,
                                "error": step_result.get("message", "Unknown error")
                            })
            except Exception as e:
                logger.error(f"Error executing step {step_id}: {e}")
                
                # Update mission context
                with self.mission_lock:
                    if mission_id in self.active_missions:
                        self.active_missions[mission_id]["steps"][step_id] = {
                            "status": "error",
                            "message": str(e)
                        }
                        self.active_missions[mission_id]["completed_steps"] += 1
                        self.active_missions[mission_id]["errors"].append({
                            "step_id": step_id,
                            "error": str(e)
                        })
    
    def _execute_step(self, mission_id: str, mission_context: Dict, step: Dict) -> Dict:
        """
        Execute a single step.
        
        Args:
            mission_id: Mission ID
            mission_context: Mission context
            step: Step to execute
            
        Returns:
            Dict: Step execution results
        """
        step_id = step.get("step_id")
        component_id = step.get("component_id")
        component_type = step.get("component_type")
        action = step.get("action", "deploy")
        parameters = step.get("parameters", {})
        timeout = step.get("timeout", self.step_timeout)
        retry_policy = step.get("retry_policy", {"attempts": 3, "delay": 5})
        
        logger.info(f"Executing step {step_id} for mission {mission_id}")
        
        # Update step status
        with self.mission_lock:
            if mission_id in self.active_missions:
                self.active_missions[mission_id]["steps"][step_id] = {
                    "status": "running",
                    "start_time": datetime.now().isoformat()
                }
        
        # Execute step with retry
        attempts = 0
        max_attempts = retry_policy.get("attempts", 3)
        delay = retry_policy.get("delay", 5)
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                # Execute step based on component type
                step_result = self._execute_component_action(component_type, action, parameters, timeout)
                
                # Update step status
                with self.mission_lock:
                    if mission_id in self.active_missions:
                        self.active_missions[mission_id]["steps"][step_id].update({
                            "status": step_result.get("status", "unknown"),
                            "end_time": datetime.now().isoformat(),
                            "result": step_result,
                            "attempts": attempts
                        })
                
                # Return result
                return step_result
            except Exception as e:
                logger.warning(f"Error executing step {step_id} (attempt {attempts}/{max_attempts}): {e}")
                
                # Update step status
                with self.mission_lock:
                    if mission_id in self.active_missions:
                        self.active_missions[mission_id]["steps"][step_id].update({
                            "status": "retrying" if attempts < max_attempts else "error",
                            "last_error": str(e),
                            "attempts": attempts
                        })
                
                # Retry if not last attempt
                if attempts < max_attempts:
                    time.sleep(delay * attempts)  # Exponential backoff
                else:
                    # Return error result
                    error_result = {
                        "status": "error",
                        "message": f"Step execution failed after {attempts} attempts: {e}",
                        "component_id": component_id,
                        "component_type": component_type,
                        "action": action
                    }
                    
                    # Update step status
                    with self.mission_lock:
                        if mission_id in self.active_missions:
                            self.active_missions[mission_id]["steps"][step_id].update({
                                "status": "error",
                                "end_time": datetime.now().isoformat(),
                                "result": error_result,
                                "attempts": attempts
                            })
                    
                    return error_result
    
    def _execute_component_action(self, component_type: str, action: str, parameters: Dict, timeout: int) -> Dict:
        """
        Execute a component action.
        
        Args:
            component_type: Component type
            action: Action to execute
            parameters: Action parameters
            timeout: Execution timeout
            
        Returns:
            Dict: Action execution results
            
        Raises:
            Exception: If action execution fails
        """
        # Determine layer and action
        layer_name = None
        if component_type.startswith("data_layer."):
            layer_name = "data_layer"
        elif component_type.startswith("core_ai_layer."):
            layer_name = "core_ai_layer"
        elif component_type.startswith("generative_layer."):
            layer_name = "generative_layer"
        elif component_type.startswith("application_layer."):
            layer_name = "application_layer"
        elif component_type.startswith("protocol_layer."):
            layer_name = "protocol_layer"
        elif component_type.startswith("workflow_layer."):
            layer_name = "workflow_layer"
        elif component_type.startswith("ui_ux_layer."):
            layer_name = "ui_ux_layer"
        elif component_type.startswith("security_compliance_layer."):
            layer_name = "security_compliance_layer"
        elif component_type.startswith("native_app_layer."):
            layer_name = "native_app_layer"
        elif component_type.startswith("deployment_ops_layer."):
            layer_name = "deployment_ops_layer"
        
        # Execute action based on layer
        if layer_name:
            # Execute through layer integration
            return self.layer_integration.execute_action(layer_name, component_type, action, parameters, timeout)
        else:
            # Execute through protocol bridge
            return self.protocol_bridge.execute_action(component_type, action, parameters, timeout)
    
    def get_mission_status(self, mission_id: str) -> Dict:
        """
        Get the status of a mission.
        
        Args:
            mission_id: Mission ID
            
        Returns:
            Dict: Mission status
            
        Raises:
            Exception: If mission not found
        """
        with self.mission_lock:
            if mission_id in self.active_missions:
                return self.active_missions[mission_id]
            else:
                raise Exception(f"Mission {mission_id} not found")
    
    def cancel_mission(self, mission_id: str) -> Dict:
        """
        Cancel a mission.
        
        Args:
            mission_id: Mission ID
            
        Returns:
            Dict: Cancellation results
            
        Raises:
            Exception: If mission not found or cannot be cancelled
        """
        with self.mission_lock:
            if mission_id not in self.active_missions:
                raise Exception(f"Mission {mission_id} not found")
            
            mission_context = self.active_missions[mission_id]
            
            # Check if mission can be cancelled
            if mission_context["status"] in ["completed", "failed", "cancelled"]:
                return {
                    "status": "error",
                    "message": f"Mission {mission_id} cannot be cancelled (status: {mission_context['status']})"
                }
            
            # Update mission status
            mission_context["status"] = "cancelling"
        
        # Cancel running steps
        # Note: This is a best-effort approach, as some steps may not be cancellable
        try:
            # Get running steps
            with self.mission_lock:
                if mission_id in self.active_missions:
                    running_steps = [
                        step_id for step_id, step in self.active_missions[mission_id]["steps"].items()
                        if step.get("status") == "running"
                    ]
                else:
                    running_steps = []
            
            # Cancel each running step
            for step_id in running_steps:
                try:
                    # Get step details
                    with self.mission_lock:
                        if mission_id in self.active_missions and step_id in self.active_missions[mission_id]["steps"]:
                            step = self.active_missions[mission_id]["steps"][step_id]
                            component_type = step.get("component_type")
                            component_id = step.get("component_id")
                        else:
                            continue
                    
                    # Cancel step
                    cancel_result = self._cancel_step(component_type, component_id)
                    
                    # Update step status
                    with self.mission_lock:
                        if mission_id in self.active_missions and step_id in self.active_missions[mission_id]["steps"]:
                            self.active_missions[mission_id]["steps"][step_id].update({
                                "status": "cancelled",
                                "end_time": datetime.now().isoformat(),
                                "cancel_result": cancel_result
                            })
                except Exception as e:
                    logger.error(f"Error cancelling step {step_id}: {e}")
            
            # Update mission status
            with self.mission_lock:
                if mission_id in self.active_missions:
                    self.active_missions[mission_id]["status"] = "cancelled"
                    self.active_missions[mission_id]["end_time"] = datetime.now().isoformat()
            
            return {
                "status": "success",
                "message": f"Mission {mission_id} cancelled successfully"
            }
        except Exception as e:
            logger.error(f"Error cancelling mission {mission_id}: {e}")
            
            # Update mission status
            with self.mission_lock:
                if mission_id in self.active_missions:
                    self.active_missions[mission_id]["status"] = "cancel_failed"
                    self.active_missions[mission_id]["errors"].append(str(e))
            
            return {"status": "error", "message": str(e)}
    
    def _cancel_step(self, component_type: str, component_id: str) -> Dict:
        """
        Cancel a step.
        
        Args:
            component_type: Component type
            component_id: Component ID
            
        Returns:
            Dict: Cancellation results
        """
        # Determine layer
        layer_name = None
        if component_type.startswith("data_layer."):
            layer_name = "data_layer"
        elif component_type.startswith("core_ai_layer."):
            layer_name = "core_ai_layer"
        elif component_type.startswith("generative_layer."):
            layer_name = "generative_layer"
        elif component_type.startswith("application_layer."):
            layer_name = "application_layer"
        elif component_type.startswith("protocol_layer."):
            layer_name = "protocol_layer"
        elif component_type.startswith("workflow_layer."):
            layer_name = "workflow_layer"
        elif component_type.startswith("ui_ux_layer."):
            layer_name = "ui_ux_layer"
        elif component_type.startswith("security_compliance_layer."):
            layer_name = "security_compliance_layer"
        elif component_type.startswith("native_app_layer."):
            layer_name = "native_app_layer"
        elif component_type.startswith("deployment_ops_layer."):
            layer_name = "deployment_ops_layer"
        
        # Cancel action based on layer
        if layer_name:
            # Cancel through layer integration
            return self.layer_integration.cancel_action(layer_name, component_type, component_id)
        else:
            # Cancel through protocol bridge
            return self.protocol_bridge.cancel_action(component_type, component_id)
    
    def _validate_mission_plan(self, mission_plan: Dict) -> Dict:
        """
        Validate a mission plan.
        
        Args:
            mission_plan: Mission plan
            
        Returns:
            Dict: Validation results
        """
        # Check for required fields
        if "mission_id" not in mission_plan:
            return {
                "status": "error",
                "message": "No mission_id specified in mission plan"
            }
        
        if "execution_plan" not in mission_plan:
            return {
                "status": "error",
                "message": "No execution_plan specified in mission plan"
            }
        
        execution_plan = mission_plan.get("execution_plan", {})
        
        if "steps" not in execution_plan:
            return {
                "status": "error",
                "message": "No steps specified in execution plan"
            }
        
        steps = execution_plan.get("steps", [])
        
        if not steps:
            return {
                "status": "error",
                "message": "Empty steps list in execution plan"
            }
        
        # Validate steps
        for step in steps:
            if "step_id" not in step:
                return {
                    "status": "error",
                    "message": "Step missing required field: step_id"
                }
            
            if "component_id" not in step:
                return {
                    "status": "error",
                    "message": f"Step {step.get('step_id')} missing required field: component_id"
                }
            
            if "component_type" not in step:
                return {
                    "status": "error",
                    "message": f"Step {step.get('step_id')} missing required field: component_type"
                }
        
        return {"status": "success", "message": "Validation successful"}
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Mission Executor.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "max_concurrent_steps" in config:
                self.max_concurrent_steps = config["max_concurrent_steps"]
                
                # Reconfigure thread pool
                self.executor.shutdown(wait=True)
                self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_steps)
            
            if "execution_timeout" in config:
                self.execution_timeout = config["execution_timeout"]
            
            if "step_timeout" in config:
                self.step_timeout = config["step_timeout"]
            
            # Configure protocol bridge
            protocol_result = None
            if "protocol_bridge" in config:
                protocol_result = self.protocol_bridge.configure(config["protocol_bridge"])
            
            # Configure layer integration
            layer_result = None
            if "layer_integration" in config:
                layer_result = self.layer_integration.configure(config["layer_integration"])
            
            return {
                "status": "success",
                "message": "Mission Executor configured successfully",
                "executor_id": self.executor_id,
                "protocol_result": protocol_result,
                "layer_result": layer_result
            }
        except Exception as e:
            logger.error(f"Error configuring Mission Executor: {e}")
            return {"status": "error", "message": str(e)}
