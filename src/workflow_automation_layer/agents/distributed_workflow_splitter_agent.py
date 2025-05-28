"""
Distributed Workflow Splitter Agent Module for the Workflow Automation Layer.

This agent splits workflows across multiple agents based on location, load, or expertise,
enabling distributed execution and optimization of complex workflows.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DistributedWorkflowSplitterAgent:
    """Agent for splitting workflows across distributed agents."""

    def __init__(self, workflow_runtime):
        """Initialize the distributed workflow splitter agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "distributed-workflow-splitter-agent"
        self.agent_capabilities = ["workflow_splitting", "load_balancing", "expertise_matching"]
        self.supported_protocols = ["MCP", "A2A"]
        self.split_strategies = ["location_based", "load_based", "expertise_based", "hybrid"]
        self.agent_registry = {}  # Registry of available agents and their capabilities
        self.split_history = {}  # History of workflow splits for analysis
        
        logger.info("Distributed Workflow Splitter Agent initialized")

    def register_agent_registry(self, agent_registry):
        """Register the agent registry.

        Args:
            agent_registry: The agent registry instance.
        """
        self.agent_registry = agent_registry
        logger.info("Agent registry registered with Distributed Workflow Splitter Agent")

    async def split_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Split a workflow across multiple agents.

        Args:
            workflow_data: Workflow data including workflow_id, tasks, strategy, constraints, etc.

        Returns:
            Dict containing split workflow details.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "tasks", "strategy"]
            for field in required_fields:
                if field not in workflow_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = workflow_data["workflow_id"]
            tasks = workflow_data["tasks"]
            strategy = workflow_data["strategy"]
            constraints = workflow_data.get("constraints", {})
            
            # Validate strategy
            if strategy not in self.split_strategies:
                return {
                    "success": False,
                    "error": f"Invalid strategy: {strategy}. Must be one of {self.split_strategies}"
                }
            
            # Generate split ID
            split_id = str(uuid.uuid4())
            
            # Split workflow based on strategy
            if strategy == "location_based":
                split_result = await self._split_by_location(tasks, constraints)
            elif strategy == "load_based":
                split_result = await self._split_by_load(tasks, constraints)
            elif strategy == "expertise_based":
                split_result = await self._split_by_expertise(tasks, constraints)
            elif strategy == "hybrid":
                split_result = await self._split_hybrid(tasks, constraints)
            else:
                return {
                    "success": False,
                    "error": f"Strategy {strategy} not implemented"
                }
            
            # Store split history
            self.split_history[split_id] = {
                "workflow_id": workflow_id,
                "strategy": strategy,
                "constraints": constraints,
                "timestamp": datetime.utcnow().isoformat(),
                "result": split_result
            }
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "split_workflow",
                "reason": f"Split workflow {workflow_id} using {strategy} strategy",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Split workflow {workflow_id} using {strategy} strategy")
            
            return {
                "success": True,
                "split_id": split_id,
                "workflow_id": workflow_id,
                "strategy": strategy,
                "task_assignments": split_result["task_assignments"],
                "execution_plan": split_result["execution_plan"]
            }
            
        except Exception as e:
            logger.error(f"Error splitting workflow: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _split_by_location(self, tasks: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Split workflow tasks by agent location.

        Args:
            tasks: List of workflow tasks.
            constraints: Constraints for splitting.

        Returns:
            Dict containing task assignments and execution plan.
        """
        # Get location preferences from constraints
        location_preferences = constraints.get("location_preferences", {})
        default_location = constraints.get("default_location", "cloud")
        
        # Get available agents by location
        agents_by_location = {}
        for agent_id, agent_info in self.agent_registry.items():
            location = agent_info.get("location", default_location)
            if location not in agents_by_location:
                agents_by_location[location] = []
            agents_by_location[location].append(agent_id)
        
        # Assign tasks to agents based on location
        task_assignments = {}
        for task in tasks:
            task_id = task["task_id"]
            task_type = task.get("task_type", "default")
            
            # Determine preferred location for this task
            preferred_location = location_preferences.get(task_type, default_location)
            
            # Find agents in preferred location
            agents_in_location = agents_by_location.get(preferred_location, [])
            
            if agents_in_location:
                # Simple round-robin assignment
                agent_id = agents_in_location[hash(task_id) % len(agents_in_location)]
                task_assignments[task_id] = {
                    "agent_id": agent_id,
                    "location": preferred_location,
                    "reason": f"Task type {task_type} assigned to preferred location {preferred_location}"
                }
            else:
                # Fallback to default location
                agents_in_default = agents_by_location.get(default_location, [])
                if agents_in_default:
                    agent_id = agents_in_default[hash(task_id) % len(agents_in_default)]
                    task_assignments[task_id] = {
                        "agent_id": agent_id,
                        "location": default_location,
                        "reason": f"No agents in preferred location {preferred_location}, falling back to {default_location}"
                    }
                else:
                    # No agents available
                    task_assignments[task_id] = {
                        "agent_id": None,
                        "location": None,
                        "reason": "No suitable agents available"
                    }
        
        # Create execution plan
        execution_plan = self._create_execution_plan(tasks, task_assignments)
        
        return {
            "task_assignments": task_assignments,
            "execution_plan": execution_plan
        }

    async def _split_by_load(self, tasks: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Split workflow tasks by agent load.

        Args:
            tasks: List of workflow tasks.
            constraints: Constraints for splitting.

        Returns:
            Dict containing task assignments and execution plan.
        """
        # Get load thresholds from constraints
        max_load = constraints.get("max_load", 0.8)  # 80% max load by default
        
        # Get current agent loads
        agent_loads = {}
        for agent_id, agent_info in self.agent_registry.items():
            # In a real implementation, this would query the agent for its current load
            # For now, use a random value or a default
            agent_loads[agent_id] = agent_info.get("current_load", 0.5)
        
        # Sort agents by load (ascending)
        sorted_agents = sorted(agent_loads.items(), key=lambda x: x[1])
        
        # Estimate task loads
        task_loads = {}
        for task in tasks:
            task_id = task["task_id"]
            # In a real implementation, this would estimate load based on task type, complexity, etc.
            # For now, use a simple estimation
            task_loads[task_id] = task.get("estimated_load", 0.1)
        
        # Assign tasks to agents based on load
        task_assignments = {}
        for task in tasks:
            task_id = task["task_id"]
            task_load = task_loads[task_id]
            
            # Find agent with lowest load that can handle this task
            assigned = False
            for agent_id, current_load in sorted_agents:
                if current_load + task_load <= max_load:
                    # Assign task to this agent
                    task_assignments[task_id] = {
                        "agent_id": agent_id,
                        "current_load": current_load,
                        "new_load": current_load + task_load,
                        "reason": f"Agent has capacity (load: {current_load:.2f}, task load: {task_load:.2f})"
                    }
                    
                    # Update agent load
                    agent_loads[agent_id] += task_load
                    assigned = True
                    break
            
            if not assigned:
                # No agent has capacity, assign to least loaded agent
                least_loaded_agent = sorted_agents[0][0]
                current_load = agent_loads[least_loaded_agent]
                task_assignments[task_id] = {
                    "agent_id": least_loaded_agent,
                    "current_load": current_load,
                    "new_load": current_load + task_load,
                    "reason": f"No agent has capacity, assigning to least loaded agent (load: {current_load:.2f})"
                }
                
                # Update agent load
                agent_loads[least_loaded_agent] += task_load
            
            # Re-sort agents by updated load
            sorted_agents = sorted(agent_loads.items(), key=lambda x: x[1])
        
        # Create execution plan
        execution_plan = self._create_execution_plan(tasks, task_assignments)
        
        return {
            "task_assignments": task_assignments,
            "execution_plan": execution_plan
        }

    async def _split_by_expertise(self, tasks: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Split workflow tasks by agent expertise.

        Args:
            tasks: List of workflow tasks.
            constraints: Constraints for splitting.

        Returns:
            Dict containing task assignments and execution plan.
        """
        # Get expertise requirements for tasks
        task_expertise = {}
        for task in tasks:
            task_id = task["task_id"]
            expertise_required = task.get("expertise_required", [])
            task_expertise[task_id] = expertise_required
        
        # Get agent expertise
        agent_expertise = {}
        for agent_id, agent_info in self.agent_registry.items():
            expertise = agent_info.get("expertise", [])
            agent_expertise[agent_id] = expertise
        
        # Assign tasks to agents based on expertise match
        task_assignments = {}
        for task in tasks:
            task_id = task["task_id"]
            expertise_required = task_expertise[task_id]
            
            # Calculate expertise match score for each agent
            agent_scores = {}
            for agent_id, expertise in agent_expertise.items():
                # Calculate match score (percentage of required expertise covered by agent)
                if not expertise_required:
                    # No specific expertise required, all agents score 1.0
                    agent_scores[agent_id] = 1.0
                else:
                    matches = sum(1 for e in expertise_required if e in expertise)
                    agent_scores[agent_id] = matches / len(expertise_required) if expertise_required else 1.0
            
            # Sort agents by score (descending)
            sorted_agents = sorted(agent_scores.items(), key=lambda x: x[1], reverse=True)
            
            if sorted_agents:
                # Assign to agent with highest score
                best_agent_id, best_score = sorted_agents[0]
                task_assignments[task_id] = {
                    "agent_id": best_agent_id,
                    "expertise_score": best_score,
                    "expertise_required": expertise_required,
                    "reason": f"Agent has highest expertise match score: {best_score:.2f}"
                }
            else:
                # No agents available
                task_assignments[task_id] = {
                    "agent_id": None,
                    "expertise_score": 0,
                    "expertise_required": expertise_required,
                    "reason": "No suitable agents available"
                }
        
        # Create execution plan
        execution_plan = self._create_execution_plan(tasks, task_assignments)
        
        return {
            "task_assignments": task_assignments,
            "execution_plan": execution_plan
        }

    async def _split_hybrid(self, tasks: List[Dict[str, Any]], constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Split workflow tasks using a hybrid approach combining location, load, and expertise.

        Args:
            tasks: List of workflow tasks.
            constraints: Constraints for splitting.

        Returns:
            Dict containing task assignments and execution plan.
        """
        # Get weights for different factors
        weights = constraints.get("weights", {
            "location": 0.3,
            "load": 0.3,
            "expertise": 0.4
        })
        
        # Get location preferences
        location_preferences = constraints.get("location_preferences", {})
        default_location = constraints.get("default_location", "cloud")
        
        # Get agent information
        agent_info = {}
        for agent_id, info in self.agent_registry.items():
            agent_info[agent_id] = {
                "location": info.get("location", default_location),
                "current_load": info.get("current_load", 0.5),
                "expertise": info.get("expertise", [])
            }
        
        # Assign tasks to agents based on combined score
        task_assignments = {}
        for task in tasks:
            task_id = task["task_id"]
            task_type = task.get("task_type", "default")
            expertise_required = task.get("expertise_required", [])
            
            # Calculate scores for each agent
            agent_scores = {}
            for agent_id, info in agent_info.items():
                # Location score
                preferred_location = location_preferences.get(task_type, default_location)
                location_score = 1.0 if info["location"] == preferred_location else 0.0
                
                # Load score (inverse of load, higher is better)
                load_score = 1.0 - info["current_load"]
                
                # Expertise score
                if not expertise_required:
                    expertise_score = 1.0
                else:
                    matches = sum(1 for e in expertise_required if e in info["expertise"])
                    expertise_score = matches / len(expertise_required) if expertise_required else 1.0
                
                # Combined score
                combined_score = (
                    weights["location"] * location_score +
                    weights["load"] * load_score +
                    weights["expertise"] * expertise_score
                )
                
                agent_scores[agent_id] = {
                    "combined_score": combined_score,
                    "location_score": location_score,
                    "load_score": load_score,
                    "expertise_score": expertise_score
                }
            
            # Sort agents by combined score (descending)
            sorted_agents = sorted(
                agent_scores.items(),
                key=lambda x: x[1]["combined_score"],
                reverse=True
            )
            
            if sorted_agents:
                # Assign to agent with highest score
                best_agent_id, scores = sorted_agents[0]
                task_assignments[task_id] = {
                    "agent_id": best_agent_id,
                    "scores": scores,
                    "reason": f"Agent has highest combined score: {scores['combined_score']:.2f}"
                }
                
                # Update agent load
                agent_info[best_agent_id]["current_load"] += task.get("estimated_load", 0.1)
            else:
                # No agents available
                task_assignments[task_id] = {
                    "agent_id": None,
                    "scores": None,
                    "reason": "No suitable agents available"
                }
        
        # Create execution plan
        execution_plan = self._create_execution_plan(tasks, task_assignments)
        
        return {
            "task_assignments": task_assignments,
            "execution_plan": execution_plan
        }

    def _create_execution_plan(self, tasks: List[Dict[str, Any]], task_assignments: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Create an execution plan based on task assignments.

        Args:
            tasks: List of workflow tasks.
            task_assignments: Task assignments to agents.

        Returns:
            Dict containing execution plan.
        """
        # Group tasks by agent
        tasks_by_agent = {}
        for task in tasks:
            task_id = task["task_id"]
            if task_id in task_assignments and task_assignments[task_id]["agent_id"]:
                agent_id = task_assignments[task_id]["agent_id"]
                if agent_id not in tasks_by_agent:
                    tasks_by_agent[agent_id] = []
                tasks_by_agent[agent_id].append(task)
        
        # Create execution stages based on dependencies
        task_dependencies = {}
        for task in tasks:
            task_id = task["task_id"]
            dependencies = task.get("dependencies", [])
            task_dependencies[task_id] = dependencies
        
        # Topological sort to determine execution order
        execution_stages = []
        remaining_tasks = {task["task_id"]: task for task in tasks}
        
        while remaining_tasks:
            # Find tasks with no remaining dependencies
            stage_tasks = {}
            for task_id, task in list(remaining_tasks.items()):
                dependencies = task_dependencies[task_id]
                if all(dep not in remaining_tasks for dep in dependencies):
                    stage_tasks[task_id] = task
                    del remaining_tasks[task_id]
            
            if not stage_tasks and remaining_tasks:
                # Circular dependency detected
                logger.warning("Circular dependency detected in workflow tasks")
                # Break the cycle by adding the first remaining task
                task_id = next(iter(remaining_tasks))
                stage_tasks[task_id] = remaining_tasks[task_id]
                del remaining_tasks[task_id]
            
            # Add stage to execution plan
            if stage_tasks:
                stage = {
                    "stage_id": len(execution_stages),
                    "tasks": list(stage_tasks.values()),
                    "task_ids": list(stage_tasks.keys())
                }
                execution_stages.append(stage)
        
        # Create coordination plan
        coordination_plan = {
            "stages": execution_stages,
            "agent_assignments": tasks_by_agent,
            "synchronization_points": []
        }
        
        # Add synchronization points between stages
        for i in range(len(execution_stages) - 1):
            current_stage = execution_stages[i]
            next_stage = execution_stages[i + 1]
            
            sync_point = {
                "id": f"sync_{i}_{i+1}",
                "after_stage": i,
                "before_stage": i + 1,
                "waiting_for": current_stage["task_ids"],
                "unblocks": next_stage["task_ids"]
            }
            
            coordination_plan["synchronization_points"].append(sync_point)
        
        return coordination_plan

    async def get_split_history(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get history of workflow splits.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing split history.
        """
        if workflow_id:
            # Filter by workflow ID
            history = {
                split_id: data
                for split_id, data in self.split_history.items()
                if data["workflow_id"] == workflow_id
            }
        else:
            # Return all history
            history = self.split_history
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "split_count": len(history),
            "splits": history
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
            "resilience_mode": "quorum_vote",
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["workflow_split_node", "agent_assignment_node"]
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
            
            if message_type == "split_workflow":
                return await self.split_workflow(message.get("payload", {}))
            elif message_type == "get_split_history":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_split_history(workflow_id)
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
