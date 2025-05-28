"""
Workflow Chaos Tester Agent Module for the Workflow Automation Layer.

This agent injects controlled failures and chaos into workflows to test
resilience, fallback mechanisms, and overall system stability.
"""

import asyncio
import json
import logging
import random
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowChaosTesterAgent:
    """Agent for injecting chaos and testing workflow resilience."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow chaos tester agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "workflow-chaos-tester-agent"
        self.agent_capabilities = ["chaos_injection", "resilience_testing", "failure_simulation"]
        self.supported_protocols = ["MCP", "A2A"]
        self.chaos_experiments = {}  # Store for ongoing chaos experiments
        self.experiment_history = {}  # History of completed experiments
        self.failure_modes = [
            "agent_failure",
            "network_latency",
            "network_partition",
            "task_error",
            "resource_exhaustion",
            "data_corruption"
        ]
        
        logger.info("Workflow Chaos Tester Agent initialized")

    async def start_chaos_experiment(self, experiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new chaos experiment.

        Args:
            experiment_data: Experiment configuration including workflow_id, target, failure_mode, etc.

        Returns:
            Dict containing experiment start status.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "target_type", "failure_mode"]
            for field in required_fields:
                if field not in experiment_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = experiment_data["workflow_id"]
            target_type = experiment_data["target_type"]  # e.g., "agent", "task", "network"
            failure_mode = experiment_data["failure_mode"]
            
            # Validate failure mode
            if failure_mode not in self.failure_modes:
                return {
                    "success": False,
                    "error": f"Invalid failure mode: {failure_mode}. Must be one of {self.failure_modes}"
                }
            
            # Generate experiment ID
            experiment_id = str(uuid.uuid4())
            
            # Store experiment details
            self.chaos_experiments[experiment_id] = {
                "workflow_id": workflow_id,
                "target_type": target_type,
                "failure_mode": failure_mode,
                "parameters": experiment_data.get("parameters", {}),
                "start_time": datetime.utcnow().isoformat(),
                "status": "running",
                "injected_failures": []
            }
            
            # Start injecting chaos based on experiment config
            # This would typically run in the background
            asyncio.create_task(self._run_chaos_experiment(experiment_id))
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "start_chaos_experiment",
                "reason": f"Started chaos experiment {experiment_id} ({failure_mode} on {target_type}) for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Started chaos experiment {experiment_id} for workflow {workflow_id}")
            
            return {
                "success": True,
                "experiment_id": experiment_id,
                "workflow_id": workflow_id,
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Error starting chaos experiment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _run_chaos_experiment(self, experiment_id: str):
        """Run the chaos experiment in the background.

        Args:
            experiment_id: ID of the experiment to run.
        """
        if experiment_id not in self.chaos_experiments:
            logger.error(f"Experiment {experiment_id} not found")
            return
        
        experiment = self.chaos_experiments[experiment_id]
        workflow_id = experiment["workflow_id"]
        target_type = experiment["target_type"]
        failure_mode = experiment["failure_mode"]
        parameters = experiment["parameters"]
        
        duration = parameters.get("duration", 60)  # Default duration 60 seconds
        frequency = parameters.get("frequency", 10)  # Inject failure every 10 seconds
        intensity = parameters.get("intensity", 0.5)  # Probability of injection
        
        start_time = datetime.fromisoformat(experiment["start_time"])
        end_time = start_time + timedelta(seconds=duration)
        
        logger.info(f"Running chaos experiment {experiment_id} until {end_time.isoformat()}")
        
        while datetime.utcnow() < end_time and experiment["status"] == "running":
            # Wait for next injection interval
            await asyncio.sleep(frequency)
            
            # Check if experiment is still running
            if experiment_id not in self.chaos_experiments or self.chaos_experiments[experiment_id]["status"] != "running":
                break
            
            # Decide whether to inject failure based on intensity
            if random.random() < intensity:
                # Inject failure
                injection_result = await self._inject_failure(
                    experiment_id, workflow_id, target_type, failure_mode, parameters
                )
                
                # Record injected failure
                if injection_result["success"]:
                    experiment["injected_failures"].append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": injection_result["details"]
                    })
        
        # Experiment finished
        if experiment_id in self.chaos_experiments:
            experiment["status"] = "completed"
            experiment["end_time"] = datetime.utcnow().isoformat()
            
            # Move to history
            self.experiment_history[experiment_id] = experiment
            del self.chaos_experiments[experiment_id]
            
            logger.info(f"Chaos experiment {experiment_id} completed")

    async def _inject_failure(
        self, 
        experiment_id: str, 
        workflow_id: str, 
        target_type: str, 
        failure_mode: str, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Inject a specific failure based on the experiment configuration.

        Args:
            experiment_id: ID of the experiment.
            workflow_id: ID of the target workflow.
            target_type: Type of target (agent, task, network).
            failure_mode: Type of failure to inject.
            parameters: Parameters for the failure injection.

        Returns:
            Dict containing injection result.
        """
        try:
            injection_details = {
                "experiment_id": experiment_id,
                "workflow_id": workflow_id,
                "target_type": target_type,
                "failure_mode": failure_mode,
                "parameters": parameters
            }
            
            if failure_mode == "agent_failure":
                # Simulate agent failure
                target_agent_id = parameters.get("target_agent_id")
                if not target_agent_id:
                    # Select random agent involved in the workflow
                    agents = await self.workflow_runtime.get_workflow_agents(workflow_id)
                    if agents:
                        target_agent_id = random.choice(list(agents.keys()))
                
                if target_agent_id:
                    # In a real implementation, this would interact with the agent or infrastructure
                    # to simulate failure (e.g., stop process, block network)
                    logger.info(f"Injecting agent failure for agent {target_agent_id} in workflow {workflow_id}")
                    injection_details["target_agent_id"] = target_agent_id
                    # Simulate by marking agent as unavailable in runtime (temporary)
                    await self.workflow_runtime.mark_agent_status(target_agent_id, "unavailable", duration=frequency * 2)
                else:
                    return {"success": False, "error": "No target agent specified or found"}
            
            elif failure_mode == "network_latency":
                # Simulate network latency
                target_agent_id = parameters.get("target_agent_id")
                latency_ms = parameters.get("latency_ms", 500)
                
                if not target_agent_id:
                    # Apply to random agent
                    agents = await self.workflow_runtime.get_workflow_agents(workflow_id)
                    if agents:
                        target_agent_id = random.choice(list(agents.keys()))
                
                if target_agent_id:
                    # In a real implementation, this would modify network rules or agent behavior
                    logger.info(f"Injecting network latency ({latency_ms}ms) for agent {target_agent_id} in workflow {workflow_id}")
                    injection_details["target_agent_id"] = target_agent_id
                    injection_details["latency_ms"] = latency_ms
                    # Simulate by updating agent performance metrics (temporary)
                    await self.workflow_runtime.update_agent_performance(target_agent_id, {"simulated_latency": latency_ms})
                else:
                    return {"success": False, "error": "No target agent specified or found"}
            
            elif failure_mode == "network_partition":
                # Simulate network partition
                partitioned_agents = parameters.get("partitioned_agents", [])
                if not partitioned_agents:
                    # Partition random agents
                    agents = await self.workflow_runtime.get_workflow_agents(workflow_id)
                    if len(agents) >= 2:
                        partitioned_agents = random.sample(list(agents.keys()), k=2)
                
                if len(partitioned_agents) >= 2:
                    # In a real implementation, this would modify network rules
                    logger.info(f"Injecting network partition between agents {partitioned_agents} in workflow {workflow_id}")
                    injection_details["partitioned_agents"] = partitioned_agents
                    # Simulate by marking agents as unable to communicate (temporary)
                    await self.workflow_runtime.simulate_network_partition(partitioned_agents, duration=frequency * 2)
                else:
                    return {"success": False, "error": "Need at least two agents to partition"}
            
            elif failure_mode == "task_error":
                # Simulate task error
                target_task_id = parameters.get("target_task_id")
                error_type = parameters.get("error_type", "SimulatedChaosError")
                
                if not target_task_id:
                    # Select random task
                    tasks = await self.workflow_runtime.get_workflow_tasks(workflow_id)
                    if tasks:
                        target_task_id = random.choice([t["task_id"] for t in tasks])
                
                if target_task_id:
                    # In a real implementation, this would trigger an error in the task execution
                    logger.info(f"Injecting task error ({error_type}) for task {target_task_id} in workflow {workflow_id}")
                    injection_details["target_task_id"] = target_task_id
                    injection_details["error_type"] = error_type
                    # Simulate by sending failure event to fallback agent
                    await self.workflow_runtime.report_failure({
                        "workflow_id": workflow_id,
                        "task_id": target_task_id,
                        "error_type": error_type,
                        "error_details": {"message": "Simulated chaos error"},
                        "source": self.agent_id
                    })
                else:
                    return {"success": False, "error": "No target task specified or found"}
            
            elif failure_mode == "resource_exhaustion":
                # Simulate resource exhaustion
                target_agent_id = parameters.get("target_agent_id")
                resource_type = parameters.get("resource_type", "memory")
                
                if not target_agent_id:
                    # Select random agent
                    agents = await self.workflow_runtime.get_workflow_agents(workflow_id)
                    if agents:
                        target_agent_id = random.choice(list(agents.keys()))
                
                if target_agent_id:
                    # In a real implementation, this would stress the agent's resources
                    logger.info(f"Injecting {resource_type} exhaustion for agent {target_agent_id} in workflow {workflow_id}")
                    injection_details["target_agent_id"] = target_agent_id
                    injection_details["resource_type"] = resource_type
                    # Simulate by updating agent performance metrics (temporary)
                    await self.workflow_runtime.update_agent_performance(target_agent_id, {f"simulated_{resource_type}_exhaustion": True})
                else:
                    return {"success": False, "error": "No target agent specified or found"}
            
            elif failure_mode == "data_corruption":
                # Simulate data corruption
                target_task_id = parameters.get("target_task_id")
                corruption_level = parameters.get("corruption_level", 0.1)
                
                if not target_task_id:
                    # Select random task
                    tasks = await self.workflow_runtime.get_workflow_tasks(workflow_id)
                    if tasks:
                        target_task_id = random.choice([t["task_id"] for t in tasks])
                
                if target_task_id:
                    # In a real implementation, this would modify task input/output data
                    logger.info(f"Injecting data corruption (level {corruption_level}) for task {target_task_id} in workflow {workflow_id}")
                    injection_details["target_task_id"] = target_task_id
                    injection_details["corruption_level"] = corruption_level
                    # Simulate by adding flag to task context (temporary)
                    await self.workflow_runtime.update_task_context(workflow_id, target_task_id, {"simulated_data_corruption": corruption_level})
                else:
                    return {"success": False, "error": "No target task specified or found"}
            
            else:
                return {"success": False, "error": f"Failure mode {failure_mode} not implemented"}
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "inject_failure",
                "reason": f"Injected {failure_mode} failure for experiment {experiment_id}",
                "details": injection_details,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            return {
                "success": True,
                "details": injection_details
            }
            
        except Exception as e:
            logger.error(f"Error injecting failure: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def stop_chaos_experiment(self, experiment_id: str) -> Dict[str, Any]:
        """Stop an ongoing chaos experiment.

        Args:
            experiment_id: ID of the experiment to stop.

        Returns:
            Dict containing experiment stop status.
        """
        try:
            # Check if experiment exists and is running
            if experiment_id not in self.chaos_experiments or self.chaos_experiments[experiment_id]["status"] != "running":
                return {
                    "success": False,
                    "error": f"Experiment {experiment_id} not found or not running"
                }
            
            experiment = self.chaos_experiments[experiment_id]
            workflow_id = experiment["workflow_id"]
            
            # Mark experiment as stopped
            experiment["status"] = "stopped"
            experiment["end_time"] = datetime.utcnow().isoformat()
            
            # Move to history
            self.experiment_history[experiment_id] = experiment
            del self.chaos_experiments[experiment_id]
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "stop_chaos_experiment",
                "reason": f"Stopped chaos experiment {experiment_id} for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Stopped chaos experiment {experiment_id}")
            
            return {
                "success": True,
                "experiment_id": experiment_id,
                "status": "stopped"
            }
            
        except Exception as e:
            logger.error(f"Error stopping chaos experiment: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_experiment_status(self, experiment_id: str) -> Dict[str, Any]:
        """Get the status of a chaos experiment.

        Args:
            experiment_id: ID of the experiment.

        Returns:
            Dict containing experiment status.
        """
        if experiment_id in self.chaos_experiments:
            return {
                "success": True,
                "experiment_id": experiment_id,
                "status": self.chaos_experiments[experiment_id]["status"],
                "details": self.chaos_experiments[experiment_id]
            }
        elif experiment_id in self.experiment_history:
            return {
                "success": True,
                "experiment_id": experiment_id,
                "status": self.experiment_history[experiment_id]["status"],
                "details": self.experiment_history[experiment_id]
            }
        else:
            return {
                "success": False,
                "error": f"Experiment {experiment_id} not found"
            }

    async def get_experiment_history(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get history of chaos experiments.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing experiment history.
        """
        if workflow_id:
            # Filter by workflow ID
            history = {
                exp_id: data
                for exp_id, data in self.experiment_history.items()
                if data["workflow_id"] == workflow_id
            }
        else:
            # Return all history
            history = self.experiment_history
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "experiment_count": len(history),
            "experiments": history
        }

    def get_agent_manifest(self) -> Dict[str, Any]:
        """Get the agent manifest.

        Returns:
            Dict containing agent manifest information.
        """
        return {
            "agent_id": self.agent_id,
            "layer": "workflow_layer",
            "capabilities": self.agent_capabilities,
            "supported_protocols": self.supported_protocols,
            "resilience_mode": "monitor_only",  # Chaos agent doesn't need resilience itself
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["chaos_experiment_node", "failure_injection_node"]
            }
        }

    async def handle_protocol_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a protocol message.

        Args:
            message: Protocol message to handle.

        Returns:
            Dict containing handling result.
        """
        try:
            message_type = message.get("message_type")
            
            if message_type == "start_chaos_experiment":
                return await self.start_chaos_experiment(message.get("payload", {}))
            elif message_type == "stop_chaos_experiment":
                payload = message.get("payload", {})
                experiment_id = payload.get("experiment_id")
                return await self.stop_chaos_experiment(experiment_id)
            elif message_type == "get_experiment_status":
                payload = message.get("payload", {})
                experiment_id = payload.get("experiment_id")
                return await self.get_experiment_status(experiment_id)
            elif message_type == "get_experiment_history":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_experiment_history(workflow_id)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported message type: {message_type}"
                }
                
        except Exception as e:
            logger.error(f"Error handling protocol message: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
