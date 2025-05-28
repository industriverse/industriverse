"""
Mesh Workload Router Agent for Industriverse Core AI Layer

This module implements the workload router agent for task delegation
and load balancing across the Core AI Layer mesh.
"""

import logging
import json
import asyncio
import random
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MeshWorkloadRouterAgent:
    """
    Implements the workload router agent for Core AI Layer.
    Provides task delegation and load balancing across the mesh.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the workload router agent.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or "config/mesh_workload_router.yaml"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.agent_registry = {}
        self.task_registry = {}
        self.routing_history = []
        self.resilience_confidence = {}
        self.latency_metrics = {}
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration.
        
        Returns:
            The configuration as a dictionary
        """
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def register_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> bool:
        """
        Register an agent with the router.
        
        Args:
            agent_id: ID of the agent
            agent_data: Agent data including capabilities and status
            
        Returns:
            True if successful, False otherwise
        """
        timestamp = datetime.utcnow().isoformat()
        
        # Create agent entry
        agent_entry = {
            "agent_id": agent_id,
            "registration_timestamp": timestamp,
            "last_heartbeat": timestamp,
            "status": "active",
            "capabilities": agent_data.get("capabilities", {}),
            "capacity": agent_data.get("capacity", 100),
            "current_load": 0,
            "tasks": [],
            "intelligence_role": agent_data.get("intelligence_role", "worker"),
            "mesh_coordination_role": agent_data.get("mesh_coordination_role", "follower"),
            "resilience_mode": agent_data.get("resilience_mode", "standard"),
            "edge_behavior_profile": agent_data.get("edge_behavior_profile", {})
        }
        
        # Add to registry
        self.agent_registry[agent_id] = agent_entry
        
        # Initialize resilience confidence
        self.resilience_confidence[agent_id] = 1.0
        
        # Initialize latency metrics
        self.latency_metrics[agent_id] = {
            "avg_latency_ms": agent_data.get("initial_latency_ms", 100),
            "measurements": []
        }
        
        logger.info(f"Registered agent {agent_id} with {len(agent_entry['capabilities'])} capabilities")
        
        return True
    
    async def update_agent_heartbeat(self, agent_id: str) -> bool:
        """
        Update agent heartbeat.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent not found: {agent_id}")
            return False
            
        # Update heartbeat
        self.agent_registry[agent_id]["last_heartbeat"] = datetime.utcnow().isoformat()
        
        return True
    
    async def update_agent_status(self, agent_id: str, status: str, metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update agent status.
        
        Args:
            agent_id: ID of the agent
            status: New status
            metrics: Optional performance metrics
            
        Returns:
            True if successful, False otherwise
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent not found: {agent_id}")
            return False
            
        # Update status
        self.agent_registry[agent_id]["status"] = status
        
        # Update metrics if provided
        if metrics:
            # Update load
            if "current_load" in metrics:
                self.agent_registry[agent_id]["current_load"] = metrics["current_load"]
                
            # Update latency metrics
            if "latency_ms" in metrics:
                latency = metrics["latency_ms"]
                
                # Add to measurements
                self.latency_metrics[agent_id]["measurements"].append(latency)
                
                # Keep last 100 measurements
                if len(self.latency_metrics[agent_id]["measurements"]) > 100:
                    self.latency_metrics[agent_id]["measurements"] = self.latency_metrics[agent_id]["measurements"][-100:]
                
                # Update average
                self.latency_metrics[agent_id]["avg_latency_ms"] = sum(self.latency_metrics[agent_id]["measurements"]) / len(self.latency_metrics[agent_id]["measurements"])
        
        logger.debug(f"Updated agent {agent_id} status to {status}")
        
        return True
    
    async def route_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Route a task to an appropriate agent.
        
        Args:
            task_id: ID of the task
            task_data: Task data including requirements
            
        Returns:
            Routing result
        """
        logger.info(f"Routing task {task_id}")
        
        # Extract task requirements
        required_capabilities = task_data.get("required_capabilities", [])
        preferred_agents = task_data.get("preferred_agents", [])
        priority = task_data.get("priority", 5)
        industry_tags = task_data.get("industryTags", [])
        
        # Find eligible agents
        eligible_agents = await self._find_eligible_agents(required_capabilities, preferred_agents)
        
        if not eligible_agents:
            logger.warning(f"No eligible agents found for task {task_id}")
            return {
                "success": False,
                "error": "No eligible agents found",
                "task_id": task_id
            }
        
        # Apply routing strategy
        strategy = task_data.get("routing_strategy") or self.config.get("default_routing_strategy", "balanced")
        
        if strategy == "balanced":
            selected_agent = await self._apply_balanced_routing(eligible_agents, priority, industry_tags)
        elif strategy == "latency_optimized":
            selected_agent = await self._apply_latency_routing(eligible_agents, priority)
        elif strategy == "resilience_optimized":
            selected_agent = await self._apply_resilience_routing(eligible_agents, priority)
        elif strategy == "edge_aware":
            selected_agent = await self._apply_edge_aware_routing(eligible_agents, task_data)
        else:
            logger.warning(f"Unknown routing strategy: {strategy}")
            selected_agent = eligible_agents[0]
        
        if not selected_agent:
            logger.warning(f"Failed to select agent for task {task_id}")
            return {
                "success": False,
                "error": "Failed to select agent",
                "task_id": task_id
            }
        
        # Register task
        timestamp = datetime.utcnow().isoformat()
        
        task_entry = {
            "task_id": task_id,
            "agent_id": selected_agent,
            "routing_timestamp": timestamp,
            "status": "routed",
            "priority": priority,
            "industry_tags": industry_tags,
            "routing_strategy": strategy
        }
        
        self.task_registry[task_id] = task_entry
        
        # Update agent load
        self.agent_registry[selected_agent]["tasks"].append(task_id)
        self.agent_registry[selected_agent]["current_load"] += self._calculate_task_load(task_data)
        
        # Add to routing history
        self.routing_history.append({
            "task_id": task_id,
            "agent_id": selected_agent,
            "timestamp": timestamp,
            "strategy": strategy,
            "eligible_count": len(eligible_agents)
        })
        
        logger.info(f"Routed task {task_id} to agent {selected_agent} using {strategy} strategy")
        
        return {
            "success": True,
            "task_id": task_id,
            "agent_id": selected_agent,
            "timestamp": timestamp
        }
    
    async def _find_eligible_agents(self, required_capabilities: List[str], preferred_agents: List[str]) -> List[str]:
        """
        Find agents eligible for a task.
        
        Args:
            required_capabilities: List of required capabilities
            preferred_agents: List of preferred agents
            
        Returns:
            List of eligible agent IDs
        """
        eligible = []
        
        # First check preferred agents
        for agent_id in preferred_agents:
            if agent_id in self.agent_registry:
                agent = self.agent_registry[agent_id]
                
                # Check if active
                if agent["status"] != "active":
                    continue
                    
                # Check capabilities
                if self._has_capabilities(agent, required_capabilities):
                    eligible.append(agent_id)
        
        # If no preferred agents are eligible, check all agents
        if not eligible:
            for agent_id, agent in self.agent_registry.items():
                # Check if active
                if agent["status"] != "active":
                    continue
                    
                # Check capabilities
                if self._has_capabilities(agent, required_capabilities):
                    eligible.append(agent_id)
        
        return eligible
    
    def _has_capabilities(self, agent: Dict[str, Any], required_capabilities: List[str]) -> bool:
        """
        Check if an agent has all required capabilities.
        
        Args:
            agent: Agent data
            required_capabilities: List of required capabilities
            
        Returns:
            True if agent has all required capabilities, False otherwise
        """
        agent_capabilities = set(agent["capabilities"].keys())
        required = set(required_capabilities)
        
        return required.issubset(agent_capabilities)
    
    def _calculate_task_load(self, task_data: Dict[str, Any]) -> float:
        """
        Calculate the load impact of a task.
        
        Args:
            task_data: Task data
            
        Returns:
            Load impact (0-100)
        """
        # In a real implementation, this would consider:
        # - Task complexity
        # - Expected duration
        # - Resource requirements
        
        # For now, use a simple calculation based on priority
        priority = task_data.get("priority", 5)
        base_load = 10  # Base load for any task
        
        return base_load * (priority / 5)
    
    async def _apply_balanced_routing(self, eligible_agents: List[str], priority: int, industry_tags: List[str]) -> Optional[str]:
        """
        Apply balanced routing strategy.
        
        Args:
            eligible_agents: List of eligible agent IDs
            priority: Task priority
            industry_tags: Industry tags
            
        Returns:
            Selected agent ID
        """
        if not eligible_agents:
            return None
            
        # Calculate weighted scores
        scores = []
        
        for agent_id in eligible_agents:
            agent = self.agent_registry[agent_id]
            
            # Load score (lower load is better)
            load_score = 100 - agent["current_load"]
            
            # Industry specialization score
            specialization_score = self._calculate_industry_specialization(agent, industry_tags)
            
            # Resilience score
            resilience_score = self.resilience_confidence.get(agent_id, 0.5) * 100
            
            # Combined score with weights
            weights = self.config.get("balanced_weights", {
                "load": 0.5,
                "specialization": 0.3,
                "resilience": 0.2
            })
            
            score = (
                load_score * weights["load"] +
                specialization_score * weights["specialization"] +
                resilience_score * weights["resilience"]
            )
            
            scores.append((agent_id, score))
        
        # Sort by score (highest first)
        scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return the agent with the highest score
        return scores[0][0] if scores else None
    
    def _calculate_industry_specialization(self, agent: Dict[str, Any], industry_tags: List[str]) -> float:
        """
        Calculate industry specialization score.
        
        Args:
            agent: Agent data
            industry_tags: Industry tags
            
        Returns:
            Specialization score (0-100)
        """
        if not industry_tags:
            return 50  # Neutral score if no tags
            
        agent_tags = agent.get("capabilities", {}).get("industryTags", [])
        
        if not agent_tags:
            return 50  # Neutral score if agent has no tags
            
        # Count matching tags
        matches = sum(1 for tag in industry_tags if tag in agent_tags)
        
        # Calculate score
        if matches == 0:
            return 30  # Below neutral if no matches
        elif matches == len(industry_tags):
            return 100  # Perfect score if all match
        else:
            return 50 + (50 * matches / len(industry_tags))  # Proportional score
    
    async def _apply_latency_routing(self, eligible_agents: List[str], priority: int) -> Optional[str]:
        """
        Apply latency-optimized routing strategy.
        
        Args:
            eligible_agents: List of eligible agent IDs
            priority: Task priority
            
        Returns:
            Selected agent ID
        """
        if not eligible_agents:
            return None
            
        # Sort by average latency (lowest first)
        sorted_agents = sorted(
            eligible_agents,
            key=lambda agent_id: self.latency_metrics.get(agent_id, {}).get("avg_latency_ms", float('inf'))
        )
        
        # For high-priority tasks, always pick the lowest latency agent
        if priority >= 8:
            return sorted_agents[0]
            
        # For medium-priority tasks, pick from the top 3 with some randomization
        elif priority >= 5:
            top_n = min(3, len(sorted_agents))
            return random.choice(sorted_agents[:top_n])
            
        # For low-priority tasks, pick from all eligible with preference for lower latency
        else:
            weights = [100 - i for i in range(len(sorted_agents))]
            return random.choices(sorted_agents, weights=weights, k=1)[0]
    
    async def _apply_resilience_routing(self, eligible_agents: List[str], priority: int) -> Optional[str]:
        """
        Apply resilience-optimized routing strategy.
        
        Args:
            eligible_agents: List of eligible agent IDs
            priority: Task priority
            
        Returns:
            Selected agent ID
        """
        if not eligible_agents:
            return None
            
        # For critical tasks, find redundant pairs
        if priority >= 9:
            # Find agents with redundant pairs
            redundant_pairs = self._find_redundant_pairs(eligible_agents)
            
            if redundant_pairs:
                # Sort pairs by combined resilience confidence
                sorted_pairs = sorted(
                    redundant_pairs,
                    key=lambda pair: self.resilience_confidence.get(pair[0], 0) + self.resilience_confidence.get(pair[1], 0),
                    reverse=True
                )
                
                # Return the primary agent from the best pair
                return sorted_pairs[0][0]
        
        # For high-priority tasks, sort by resilience confidence
        sorted_agents = sorted(
            eligible_agents,
            key=lambda agent_id: self.resilience_confidence.get(agent_id, 0),
            reverse=True
        )
        
        # For high-priority tasks, pick the most resilient agent
        if priority >= 7:
            return sorted_agents[0]
            
        # For medium-priority tasks, pick from the top 3
        elif priority >= 4:
            top_n = min(3, len(sorted_agents))
            return random.choice(sorted_agents[:top_n])
            
        # For low-priority tasks, pick randomly
        else:
            return random.choice(eligible_agents)
    
    def _find_redundant_pairs(self, agent_ids: List[str]) -> List[Tuple[str, str]]:
        """
        Find redundant agent pairs.
        
        Args:
            agent_ids: List of agent IDs
            
        Returns:
            List of redundant pairs (primary, backup)
        """
        pairs = []
        
        for i, primary_id in enumerate(agent_ids):
            primary = self.agent_registry.get(primary_id)
            
            if not primary:
                continue
                
            # Skip agents that aren't in primary resilience mode
            if primary.get("resilience_mode") != "primary":
                continue
                
            # Find backup agents
            for j, backup_id in enumerate(agent_ids):
                if i == j:
                    continue
                    
                backup = self.agent_registry.get(backup_id)
                
                if not backup:
                    continue
                    
                # Check if backup agent is in backup resilience mode
                if backup.get("resilience_mode") != "backup":
                    continue
                    
                # Check if capabilities match
                primary_caps = set(primary.get("capabilities", {}).keys())
                backup_caps = set(backup.get("capabilities", {}).keys())
                
                if primary_caps.issubset(backup_caps):
                    pairs.append((primary_id, backup_id))
        
        return pairs
    
    async def _apply_edge_aware_routing(self, eligible_agents: List[str], task_data: Dict[str, Any]) -> Optional[str]:
        """
        Apply edge-aware routing strategy.
        
        Args:
            eligible_agents: List of eligible agent IDs
            task_data: Task data
            
        Returns:
            Selected agent ID
        """
        if not eligible_agents:
            return None
            
        # Check if task has edge requirements
        edge_requirements = task_data.get("edge_requirements", {})
        
        if not edge_requirements:
            # Fall back to balanced routing if no edge requirements
            return await self._apply_balanced_routing(
                eligible_agents, 
                task_data.get("priority", 5),
                task_data.get("industryTags", [])
            )
        
        # Filter agents by edge capabilities
        edge_capable_agents = []
        
        for agent_id in eligible_agents:
            agent = self.agent_registry.get(agent_id)
            
            if not agent:
                continue
                
            edge_profile = agent.get("edge_behavior_profile", {})
            
            # Check if agent meets edge requirements
            meets_requirements = True
            
            for req_key, req_value in edge_requirements.items():
                if req_key not in edge_profile or edge_profile[req_key] < req_value:
                    meets_requirements = False
                    break
            
            if meets_requirements:
                edge_capable_agents.append(agent_id)
        
        if not edge_capable_agents:
            logger.warning(f"No agents meet edge requirements, falling back to standard routing")
            return await self._apply_balanced_routing(
                eligible_agents, 
                task_data.get("priority", 5),
                task_data.get("industryTags", [])
            )
        
        # Sort by proximity if location is specified
        if "location" in task_data:
            task_location = task_data["location"]
            
            # Calculate proximity scores
            proximity_scores = []
            
            for agent_id in edge_capable_agents:
                agent = self.agent_registry.get(agent_id)
                agent_location = agent.get("edge_behavior_profile", {}).get("location")
                
                if agent_location:
                    proximity = self._calculate_proximity(task_location, agent_location)
                    proximity_scores.append((agent_id, proximity))
                else:
                    proximity_scores.append((agent_id, 0))
            
            # Sort by proximity (highest first)
            proximity_scores.sort(key=lambda x: x[1], reverse=True)
            
            return proximity_scores[0][0]
        else:
            # If no location specified, pick randomly from edge-capable agents
            return random.choice(edge_capable_agents)
    
    def _calculate_proximity(self, location1: Dict[str, Any], location2: Dict[str, Any]) -> float:
        """
        Calculate proximity between two locations.
        
        Args:
            location1: First location
            location2: Second location
            
        Returns:
            Proximity score (0-1)
        """
        # In a real implementation, this would calculate geographic distance
        # For now, use a simple comparison
        if location1.get("region") == location2.get("region"):
            return 1.0
        elif location1.get("country") == location2.get("country"):
            return 0.8
        elif location1.get("continent") == location2.get("continent"):
            return 0.5
        else:
            return 0.2
    
    async def update_task_status(self, task_id: str, status: str, metrics: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update task status.
        
        Args:
            task_id: ID of the task
            status: New status
            metrics: Optional performance metrics
            
        Returns:
            True if successful, False otherwise
        """
        if task_id not in self.task_registry:
            logger.warning(f"Task not found: {task_id}")
            return False
            
        task = self.task_registry[task_id]
        agent_id = task["agent_id"]
        
        # Update task status
        task["status"] = status
        
        # Update agent if task is completed or failed
        if status in ["completed", "failed"]:
            if agent_id in self.agent_registry:
                agent = self.agent_registry[agent_id]
                
                # Remove task from agent
                if task_id in agent["tasks"]:
                    agent["tasks"].remove(task_id)
                
                # Update load
                load_impact = self._calculate_task_load(task)
                agent["current_load"] = max(0, agent["current_load"] - load_impact)
                
                # Update resilience confidence based on outcome
                if status == "completed" and metrics and "success" in metrics:
                    if metrics["success"]:
                        # Increase confidence for successful tasks
                        self.resilience_confidence[agent_id] = min(1.0, self.resilience_confidence[agent_id] + 0.01)
                    else:
                        # Decrease confidence for unsuccessful tasks
                        self.resilience_confidence[agent_id] = max(0.0, self.resilience_confidence[agent_id] - 0.05)
        
        logger.debug(f"Updated task {task_id} status to {status}")
        
        return True
    
    async def check_agent_health(self) -> List[Dict[str, Any]]:
        """
        Check health of all agents.
        
        Returns:
            List of unhealthy agents
        """
        unhealthy = []
        now = datetime.utcnow()
        
        for agent_id, agent in self.agent_registry.items():
            # Check heartbeat
            last_heartbeat = datetime.fromisoformat(agent["last_heartbeat"])
            heartbeat_age = (now - last_heartbeat).total_seconds()
            
            heartbeat_threshold = self.config.get("heartbeat_threshold_seconds", 60)
            
            if heartbeat_age > heartbeat_threshold:
                logger.warning(f"Agent {agent_id} heartbeat is stale: {heartbeat_age:.1f}s")
                
                unhealthy.append({
                    "agent_id": agent_id,
                    "issue": "stale_heartbeat",
                    "details": {
                        "heartbeat_age": heartbeat_age,
                        "threshold": heartbeat_threshold
                    }
                })
                
                # Update agent status
                agent["status"] = "unhealthy"
        
        return unhealthy
    
    async def handle_agent_failure(self, agent_id: str) -> Dict[str, Any]:
        """
        Handle agent failure.
        
        Args:
            agent_id: ID of the failed agent
            
        Returns:
            Failure handling result
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent not found: {agent_id}")
            return {
                "success": False,
                "error": "Agent not found"
            }
            
        agent = self.agent_registry[agent_id]
        
        logger.warning(f"Handling failure of agent {agent_id} with {len(agent['tasks'])} active tasks")
        
        # Update agent status
        agent["status"] = "failed"
        
        # Get active tasks
        active_tasks = agent["tasks"].copy()
        
        # Clear agent tasks
        agent["tasks"] = []
        agent["current_load"] = 0
        
        # Update resilience confidence
        self.resilience_confidence[agent_id] = max(0.0, self.resilience_confidence[agent_id] - 0.2)
        
        # Reroute tasks
        rerouted = []
        failed = []
        
        for task_id in active_tasks:
            if task_id in self.task_registry:
                task = self.task_registry[task_id]
                
                # Get task data
                task_data = {
                    "required_capabilities": task.get("required_capabilities", []),
                    "priority": task.get("priority", 5),
                    "industryTags": task.get("industry_tags", []),
                    "routing_strategy": "resilience_optimized"  # Use resilience strategy for rerouting
                }
                
                # Route task
                result = await self.route_task(task_id, task_data)
                
                if result["success"]:
                    rerouted.append(task_id)
                else:
                    failed.append(task_id)
        
        logger.info(f"Rerouted {len(rerouted)} tasks, {len(failed)} failed")
        
        return {
            "success": True,
            "agent_id": agent_id,
            "rerouted_tasks": rerouted,
            "failed_tasks": failed
        }
    
    def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        """
        Get agent status.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            Agent status
        """
        if agent_id not in self.agent_registry:
            logger.warning(f"Agent not found: {agent_id}")
            return {}
            
        agent = self.agent_registry[agent_id]
        
        return {
            "agent_id": agent_id,
            "status": agent["status"],
            "current_load": agent["current_load"],
            "task_count": len(agent["tasks"]),
            "resilience_confidence": self.resilience_confidence.get(agent_id, 0),
            "avg_latency_ms": self.latency_metrics.get(agent_id, {}).get("avg_latency_ms", 0)
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Get task status.
        
        Args:
            task_id: ID of the task
            
        Returns:
            Task status
        """
        if task_id not in self.task_registry:
            logger.warning(f"Task not found: {task_id}")
            return {}
            
        return self.task_registry[task_id]
    
    def get_routing_metrics(self) -> Dict[str, Any]:
        """
        Get routing metrics.
        
        Returns:
            Routing metrics
        """
        # Calculate metrics
        total_tasks = len(self.task_registry)
        active_agents = sum(1 for a in self.agent_registry.values() if a["status"] == "active")
        
        # Calculate average load
        total_load = sum(a["current_load"] for a in self.agent_registry.values())
        avg_load = total_load / active_agents if active_agents > 0 else 0
        
        # Calculate strategy distribution
        strategies = {}
        
        for entry in self.routing_history:
            strategy = entry["strategy"]
            strategies[strategy] = strategies.get(strategy, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "active_agents": active_agents,
            "avg_load": avg_load,
            "routing_strategies": strategies
        }


# Example usage
if __name__ == "__main__":
    async def main():
        # Create a workload router agent
        router = MeshWorkloadRouterAgent()
        
        # Register some agents
        await router.register_agent("llm-agent-1", {
            "capabilities": {
                "text_generation": True,
                "text_embedding": True,
                "industryTags": ["manufacturing", "energy"]
            },
            "capacity": 100,
            "intelligence_role": "worker",
            "mesh_coordination_role": "follower",
            "resilience_mode": "primary"
        })
        
        await router.register_agent("llm-agent-2", {
            "capabilities": {
                "text_generation": True,
                "industryTags": ["healthcare", "finance"]
            },
            "capacity": 80,
            "intelligence_role": "worker",
            "mesh_coordination_role": "follower",
            "resilience_mode": "backup"
        })
        
        await router.register_agent("ml-agent-1", {
            "capabilities": {
                "classification": True,
                "regression": True,
                "industryTags": ["manufacturing"]
            },
            "capacity": 120,
            "intelligence_role": "worker",
            "mesh_coordination_role": "leader",
            "resilience_mode": "standard"
        })
        
        # Route some tasks
        result1 = await router.route_task("task-1", {
            "required_capabilities": ["text_generation"],
            "priority": 7,
            "industryTags": ["manufacturing"]
        })
        
        result2 = await router.route_task("task-2", {
            "required_capabilities": ["classification"],
            "priority": 5,
            "industryTags": ["manufacturing"]
        })
        
        # Update task status
        await router.update_task_status("task-1", "completed", {
            "success": True
        })
        
        # Check agent health
        unhealthy = await router.check_agent_health()
        print(f"Unhealthy agents: {len(unhealthy)}")
        
        # Get routing metrics
        metrics = router.get_routing_metrics()
        print(f"Routing metrics: {metrics}")
    
    asyncio.run(main())
