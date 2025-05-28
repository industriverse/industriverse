"""
Workflow Router Agent Module for the Workflow Automation Layer.

This agent routes workflow tasks to optimal agents based on context, latency,
trust scores, and other factors, ensuring efficient workflow execution.
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


class WorkflowRouterAgent:
    """Agent for routing workflow tasks to optimal agents."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow router agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "workflow-router-agent"
        self.agent_capabilities = ["task_routing", "path_optimization", "trust_weighted_routing"]
        self.supported_protocols = ["MCP", "A2A"]
        self.routing_strategies = {
            "latency_weighted": self._route_by_latency,
            "trust_weighted": self._route_by_trust,
            "fallback_linear": self._route_with_fallbacks,
            "context_aware": self._route_by_context,
            "adaptive": self._route_adaptively
        }
        self.route_history = {}  # History of routing decisions
        self.agent_performance = {}  # Performance metrics for agents
        
        logger.info("Workflow Router Agent initialized")

    async def route_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route a task to the optimal agent.

        Args:
            task_data: Task data including task_id, workflow_id, routing_strategy, etc.

        Returns:
            Dict containing routing decision and details.
        """
        try:
            # Validate required fields
            required_fields = ["task_id", "workflow_id", "routing_strategy"]
            for field in required_fields:
                if field not in task_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            task_id = task_data["task_id"]
            workflow_id = task_data["workflow_id"]
            routing_strategy = task_data["routing_strategy"]
            
            # Validate routing strategy
            if routing_strategy not in self.routing_strategies:
                return {
                    "success": False,
                    "error": f"Invalid routing strategy: {routing_strategy}. Must be one of {list(self.routing_strategies.keys())}"
                }
            
            # Generate route ID
            route_id = str(uuid.uuid4())
            
            # Get workflow manifest
            workflow_manifest = await self.workflow_runtime.get_workflow_manifest(workflow_id)
            if not workflow_manifest:
                return {
                    "success": False,
                    "error": f"Workflow manifest not found for workflow {workflow_id}"
                }
            
            # Get agent mesh topology from workflow manifest
            agent_mesh_topology = workflow_manifest.get("agent_mesh_topology", {})
            
            # Route task based on strategy
            routing_func = self.routing_strategies[routing_strategy]
            route_result = await routing_func(task_data, agent_mesh_topology)
            
            if not route_result["success"]:
                return route_result
            
            # Store route history
            self.route_history[route_id] = {
                "task_id": task_id,
                "workflow_id": workflow_id,
                "routing_strategy": routing_strategy,
                "timestamp": datetime.utcnow().isoformat(),
                "result": route_result
            }
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "route_task",
                "reason": f"Routed task {task_id} using {routing_strategy} strategy to agent {route_result['agent_id']}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Routed task {task_id} using {routing_strategy} strategy to agent {route_result['agent_id']}")
            
            return {
                "success": True,
                "route_id": route_id,
                "task_id": task_id,
                "workflow_id": workflow_id,
                "routing_strategy": routing_strategy,
                "agent_id": route_result["agent_id"],
                "reason": route_result["reason"],
                "metrics": route_result.get("metrics", {})
            }
            
        except Exception as e:
            logger.error(f"Error routing task: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _route_by_latency(self, task_data: Dict[str, Any], agent_mesh_topology: Dict[str, Any]) -> Dict[str, Any]:
        """Route task based on latency metrics.

        Args:
            task_data: Task data.
            agent_mesh_topology: Agent mesh topology from workflow manifest.

        Returns:
            Dict containing routing decision.
        """
        # Get available agents
        available_agents = await self._get_available_agents(task_data)
        if not available_agents:
            return {
                "success": False,
                "error": "No available agents found"
            }
        
        # Get latency metrics for available agents
        latency_metrics = {}
        for agent_id in available_agents:
            # In a real implementation, this would query actual latency metrics
            # For now, use random or stored values
            if agent_id in self.agent_performance:
                latency = self.agent_performance[agent_id].get("avg_latency", 100)
            else:
                # Default latency (would be replaced with actual measurements)
                latency = 100
            
            latency_metrics[agent_id] = latency
        
        # Sort agents by latency (ascending)
        sorted_agents = sorted(latency_metrics.items(), key=lambda x: x[1])
        
        if sorted_agents:
            best_agent_id, latency = sorted_agents[0]
            return {
                "success": True,
                "agent_id": best_agent_id,
                "reason": f"Selected agent with lowest latency: {latency}ms",
                "metrics": {
                    "latency": latency,
                    "all_latencies": latency_metrics
                }
            }
        else:
            return {
                "success": False,
                "error": "No agents available after latency evaluation"
            }

    async def _route_by_trust(self, task_data: Dict[str, Any], agent_mesh_topology: Dict[str, Any]) -> Dict[str, Any]:
        """Route task based on trust scores.

        Args:
            task_data: Task data.
            agent_mesh_topology: Agent mesh topology from workflow manifest.

        Returns:
            Dict containing routing decision.
        """
        # Get available agents
        available_agents = await self._get_available_agents(task_data)
        if not available_agents:
            return {
                "success": False,
                "error": "No available agents found"
            }
        
        # Get trust scores for available agents
        trust_scores = {}
        for agent_id in available_agents:
            # In a real implementation, this would query the trust fabric
            # For now, use random or stored values
            if agent_id in self.agent_performance:
                trust_score = self.agent_performance[agent_id].get("trust_score", 0.7)
            else:
                # Default trust score (would be replaced with actual trust fabric scores)
                trust_score = 0.7
            
            trust_scores[agent_id] = trust_score
        
        # Sort agents by trust score (descending)
        sorted_agents = sorted(trust_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Get minimum trust threshold from task data or agent mesh topology
        min_trust = task_data.get("min_trust_threshold", 
                                 agent_mesh_topology.get("min_trust_threshold", 0.5))
        
        # Filter agents by minimum trust threshold
        trusted_agents = [(agent_id, score) for agent_id, score in sorted_agents if score >= min_trust]
        
        if trusted_agents:
            best_agent_id, trust_score = trusted_agents[0]
            return {
                "success": True,
                "agent_id": best_agent_id,
                "reason": f"Selected agent with highest trust score: {trust_score:.2f}",
                "metrics": {
                    "trust_score": trust_score,
                    "all_trust_scores": trust_scores,
                    "min_trust_threshold": min_trust
                }
            }
        else:
            # No agents meet trust threshold, check if fallback is allowed
            allow_fallback = agent_mesh_topology.get("allow_fallback_below_trust", False)
            
            if allow_fallback and sorted_agents:
                fallback_agent_id, fallback_score = sorted_agents[0]
                return {
                    "success": True,
                    "agent_id": fallback_agent_id,
                    "reason": f"No agents meet trust threshold ({min_trust:.2f}). Using fallback agent with score: {fallback_score:.2f}",
                    "metrics": {
                        "trust_score": fallback_score,
                        "all_trust_scores": trust_scores,
                        "min_trust_threshold": min_trust,
                        "is_fallback": True
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"No agents meet minimum trust threshold of {min_trust:.2f}"
                }

    async def _route_with_fallbacks(self, task_data: Dict[str, Any], agent_mesh_topology: Dict[str, Any]) -> Dict[str, Any]:
        """Route task with explicit fallback agents.

        Args:
            task_data: Task data.
            agent_mesh_topology: Agent mesh topology from workflow manifest.

        Returns:
            Dict containing routing decision.
        """
        # Get fallback agents from agent mesh topology
        fallback_agents = agent_mesh_topology.get("fallback_agents", [])
        if not fallback_agents:
            return {
                "success": False,
                "error": "No fallback agents defined in agent mesh topology"
            }
        
        # Sort fallback agents by priority
        sorted_fallbacks = sorted(fallback_agents, key=lambda x: x.get("priority", 999))
        
        # Check availability of fallback agents in order
        for fallback in sorted_fallbacks:
            agent_id = fallback.get("agent_id")
            if not agent_id:
                continue
            
            # Check if agent is available
            is_available = await self._check_agent_availability(agent_id)
            
            if is_available:
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "reason": f"Selected fallback agent with priority {fallback.get('priority')}",
                    "metrics": {
                        "priority": fallback.get("priority"),
                        "is_fallback": True
                    }
                }
        
        # No fallback agents available
        return {
            "success": False,
            "error": "No fallback agents available"
        }

    async def _route_by_context(self, task_data: Dict[str, Any], agent_mesh_topology: Dict[str, Any]) -> Dict[str, Any]:
        """Route task based on context awareness.

        Args:
            task_data: Task data.
            agent_mesh_topology: Agent mesh topology from workflow manifest.

        Returns:
            Dict containing routing decision.
        """
        # Get available agents
        available_agents = await self._get_available_agents(task_data)
        if not available_agents:
            return {
                "success": False,
                "error": "No available agents found"
            }
        
        # Get task context
        task_context = task_data.get("context", {})
        task_type = task_data.get("task_type", "default")
        
        # Get context-specific routing rules
        context_rules = agent_mesh_topology.get("context_routing_rules", {})
        
        # Check if there's a specific rule for this task type
        if task_type in context_rules:
            rule = context_rules[task_type]
            
            # Check if rule has a specific agent assignment
            if "agent_id" in rule:
                agent_id = rule["agent_id"]
                
                # Verify agent is available
                if agent_id in available_agents:
                    return {
                        "success": True,
                        "agent_id": agent_id,
                        "reason": f"Selected agent based on context rule for task type: {task_type}",
                        "metrics": {
                            "rule_matched": task_type,
                            "context_based": True
                        }
                    }
            
            # Check if rule has context conditions
            if "conditions" in rule:
                conditions = rule["conditions"]
                
                # Evaluate conditions against task context
                for condition in conditions:
                    context_key = condition.get("context_key")
                    operator = condition.get("operator", "equals")
                    value = condition.get("value")
                    target_agent = condition.get("target_agent")
                    
                    if not context_key or not target_agent:
                        continue
                    
                    # Get context value
                    context_value = task_context.get(context_key)
                    
                    # Evaluate condition
                    condition_met = False
                    if operator == "equals" and context_value == value:
                        condition_met = True
                    elif operator == "not_equals" and context_value != value:
                        condition_met = True
                    elif operator == "contains" and value in context_value:
                        condition_met = True
                    elif operator == "greater_than" and context_value > value:
                        condition_met = True
                    elif operator == "less_than" and context_value < value:
                        condition_met = True
                    
                    if condition_met and target_agent in available_agents:
                        return {
                            "success": True,
                            "agent_id": target_agent,
                            "reason": f"Selected agent based on context condition: {context_key} {operator} {value}",
                            "metrics": {
                                "condition_matched": f"{context_key} {operator} {value}",
                                "context_based": True
                            }
                        }
        
        # No context rules matched, fall back to trust-based routing
        return await self._route_by_trust(task_data, agent_mesh_topology)

    async def _route_adaptively(self, task_data: Dict[str, Any], agent_mesh_topology: Dict[str, Any]) -> Dict[str, Any]:
        """Route task adaptively based on multiple factors.

        Args:
            task_data: Task data.
            agent_mesh_topology: Agent mesh topology from workflow manifest.

        Returns:
            Dict containing routing decision.
        """
        # Get congestion behavior from agent mesh topology
        congestion_behavior = agent_mesh_topology.get("congestion_behavior", "queue")
        
        # Get available agents
        available_agents = await self._get_available_agents(task_data)
        if not available_agents:
            return {
                "success": False,
                "error": "No available agents found"
            }
        
        # Calculate adaptive scores based on multiple factors
        adaptive_scores = {}
        for agent_id in available_agents:
            # Get agent performance metrics
            if agent_id in self.agent_performance:
                metrics = self.agent_performance[agent_id]
            else:
                # Default metrics
                metrics = {
                    "avg_latency": 100,
                    "trust_score": 0.7,
                    "success_rate": 0.9,
                    "current_load": 0.5
                }
            
            # Calculate adaptive score
            # Lower latency is better (inverse relationship)
            latency_factor = 1000 / (metrics["avg_latency"] + 10)
            
            # Higher trust is better
            trust_factor = metrics["trust_score"]
            
            # Higher success rate is better
            success_factor = metrics["success_rate"]
            
            # Lower load is better (inverse relationship)
            load_factor = 1 - metrics["current_load"]
            
            # Combined score with weights
            adaptive_score = (
                0.25 * latency_factor +
                0.3 * trust_factor +
                0.25 * success_factor +
                0.2 * load_factor
            )
            
            adaptive_scores[agent_id] = {
                "adaptive_score": adaptive_score,
                "latency_factor": latency_factor,
                "trust_factor": trust_factor,
                "success_factor": success_factor,
                "load_factor": load_factor,
                "metrics": metrics
            }
        
        # Sort agents by adaptive score (descending)
        sorted_agents = sorted(
            adaptive_scores.items(),
            key=lambda x: x[1]["adaptive_score"],
            reverse=True
        )
        
        if sorted_agents:
            best_agent_id, score_data = sorted_agents[0]
            
            # Check if best agent is congested
            is_congested = score_data["metrics"]["current_load"] > 0.8
            
            if is_congested and congestion_behavior == "reroute" and len(sorted_agents) > 1:
                # Reroute to next best agent
                next_best_agent_id, next_score_data = sorted_agents[1]
                return {
                    "success": True,
                    "agent_id": next_best_agent_id,
                    "reason": f"Best agent {best_agent_id} is congested, rerouted to next best agent",
                    "metrics": {
                        "adaptive_score": next_score_data["adaptive_score"],
                        "original_agent": best_agent_id,
                        "congestion_behavior": "reroute",
                        "factors": {
                            "latency": next_score_data["latency_factor"],
                            "trust": next_score_data["trust_factor"],
                            "success": next_score_data["success_factor"],
                            "load": next_score_data["load_factor"]
                        }
                    }
                }
            elif is_congested and congestion_behavior == "degrade_gracefully":
                # Use best agent but with degraded expectations
                return {
                    "success": True,
                    "agent_id": best_agent_id,
                    "reason": f"Selected best agent despite congestion, with degraded expectations",
                    "metrics": {
                        "adaptive_score": score_data["adaptive_score"],
                        "congestion_behavior": "degrade_gracefully",
                        "degraded_expectations": True,
                        "factors": {
                            "latency": score_data["latency_factor"],
                            "trust": score_data["trust_factor"],
                            "success": score_data["success_factor"],
                            "load": score_data["load_factor"]
                        }
                    }
                }
            else:
                # Use best agent with normal expectations
                return {
                    "success": True,
                    "agent_id": best_agent_id,
                    "reason": f"Selected best agent based on adaptive scoring",
                    "metrics": {
                        "adaptive_score": score_data["adaptive_score"],
                        "congestion_behavior": congestion_behavior,
                        "factors": {
                            "latency": score_data["latency_factor"],
                            "trust": score_data["trust_factor"],
                            "success": score_data["success_factor"],
                            "load": score_data["load_factor"]
                        }
                    }
                }
        else:
            return {
                "success": False,
                "error": "No agents available after adaptive evaluation"
            }

    async def _get_available_agents(self, task_data: Dict[str, Any]) -> List[str]:
        """Get list of available agents for the task.

        Args:
            task_data: Task data.

        Returns:
            List of available agent IDs.
        """
        # Get required capabilities for the task
        required_capabilities = task_data.get("required_capabilities", [])
        
        # Get all registered agents
        agents = await self.workflow_runtime.get_registered_agents()
        
        # Filter agents by required capabilities
        if required_capabilities:
            available_agents = []
            for agent_id, agent_info in agents.items():
                agent_capabilities = agent_info.get("capabilities", [])
                if all(cap in agent_capabilities for cap in required_capabilities):
                    available_agents.append(agent_id)
        else:
            # No specific capabilities required
            available_agents = list(agents.keys())
        
        return available_agents

    async def _check_agent_availability(self, agent_id: str) -> bool:
        """Check if an agent is available.

        Args:
            agent_id: ID of the agent to check.

        Returns:
            True if agent is available, False otherwise.
        """
        # In a real implementation, this would check agent health and status
        # For now, assume agent is available if it's registered
        agents = await self.workflow_runtime.get_registered_agents()
        return agent_id in agents

    async def update_agent_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update performance metrics for an agent.

        Args:
            performance_data: Performance data including agent_id, metrics, etc.

        Returns:
            Dict containing update status.
        """
        try:
            # Validate required fields
            required_fields = ["agent_id", "metrics"]
            for field in required_fields:
                if field not in performance_data:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            agent_id = performance_data["agent_id"]
            metrics = performance_data["metrics"]
            
            # Initialize agent performance if not exists
            if agent_id not in self.agent_performance:
                self.agent_performance[agent_id] = {}
            
            # Update metrics
            self.agent_performance[agent_id].update(metrics)
            
            # Add timestamp
            self.agent_performance[agent_id]["last_updated"] = datetime.utcnow().isoformat()
            
            logger.info(f"Updated performance metrics for agent {agent_id}")
            
            return {
                "success": True,
                "agent_id": agent_id,
                "updated_metrics": list(metrics.keys())
            }
            
        except Exception as e:
            logger.error(f"Error updating agent performance: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_route_history(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get history of routing decisions.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing routing history.
        """
        if workflow_id:
            # Filter by workflow ID
            history = {
                route_id: data
                for route_id, data in self.route_history.items()
                if data["workflow_id"] == workflow_id
            }
        else:
            # Return all history
            history = self.route_history
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "route_count": len(history),
            "routes": history
        }

    async def get_agent_performance(self, agent_id: str = None) -> Dict[str, Any]:
        """Get performance metrics for agents.

        Args:
            agent_id: Optional ID of agent to filter by.

        Returns:
            Dict containing agent performance metrics.
        """
        if agent_id:
            # Get metrics for specific agent
            if agent_id in self.agent_performance:
                return {
                    "success": True,
                    "agent_id": agent_id,
                    "metrics": self.agent_performance[agent_id]
                }
            else:
                return {
                    "success": False,
                    "error": f"No performance metrics found for agent {agent_id}"
                }
        else:
            # Return all agent metrics
            return {
                "success": True,
                "agent_count": len(self.agent_performance),
                "agents": self.agent_performance
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
                "editable_nodes": ["routing_strategy_node", "agent_selection_node"]
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
            
            if message_type == "route_task":
                return await self.route_task(message.get("payload", {}))
            elif message_type == "update_agent_performance":
                return await self.update_agent_performance(message.get("payload", {}))
            elif message_type == "get_route_history":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_route_history(workflow_id)
            elif message_type == "get_agent_performance":
                payload = message.get("payload", {})
                agent_id = payload.get("agent_id")
                return await self.get_agent_performance(agent_id)
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
