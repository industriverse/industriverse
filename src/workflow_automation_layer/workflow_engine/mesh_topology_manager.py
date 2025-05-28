"""
Mesh Topology Manager Module for Industriverse Workflow Automation Layer

This module is responsible for managing the mesh topology of workflow agents,
including routing strategies, fallback mechanisms, and congestion handling.
It implements the logic for trust-weighted, latency-weighted, and fallback-linear
routing across distributed agent networks.

The MeshTopologyManager class provides the core logic for agent selection,
routing decisions, and mesh optimization.
"""

import logging
import random
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple, Callable
from datetime import datetime, timedelta

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class RoutingStrategy(str, Enum):
    """Enum representing the possible routing strategies for the agent mesh."""
    LATENCY_WEIGHTED = "latency_weighted"
    TRUST_WEIGHTED = "trust_weighted"
    FALLBACK_LINEAR = "fallback_linear"


class CongestionBehavior(str, Enum):
    """Enum representing the possible behaviors during mesh congestion."""
    QUEUE = "queue"
    REROUTE = "reroute"
    DEGRADE_GRACEFULLY = "degrade_gracefully"


class FallbackAgent(BaseModel):
    """Model representing a fallback agent in the mesh topology."""
    agent_id: str
    priority: int = 1


class AgentMeshTopology(BaseModel):
    """Model representing the mesh topology configuration for a workflow."""
    routing_strategy: RoutingStrategy = RoutingStrategy.TRUST_WEIGHTED
    allow_rerouting: bool = True
    fallback_agents: List[FallbackAgent] = Field(default_factory=list)
    congestion_behavior: CongestionBehavior = CongestionBehavior.QUEUE


class AgentMetrics(BaseModel):
    """Model representing metrics for an agent in the mesh."""
    agent_id: str
    trust_score: float = 0.8
    avg_latency_ms: float = 100.0
    success_rate: float = 0.95
    load: float = 0.0  # 0.0 to 1.0, representing current load
    last_selected: Optional[datetime] = None
    last_failed: Optional[datetime] = None
    consecutive_failures: int = 0
    capabilities: List[str] = Field(default_factory=list)
    location: Optional[str] = None  # e.g., "edge", "cloud", "region-us-east"


class RoutingDecision(BaseModel):
    """Model representing a routing decision."""
    selected_agent_id: str
    fallback_agent_ids: List[str] = Field(default_factory=list)
    strategy_used: RoutingStrategy
    reason: str
    score: float
    timestamp: datetime = Field(default_factory=datetime.now)


class MeshTopologyManager:
    """
    Manages the mesh topology of workflow agents.
    
    This class provides methods for agent selection, routing decisions,
    and mesh optimization based on various strategies and metrics.
    """
    
    def __init__(self):
        """Initialize the MeshTopologyManager."""
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        self.routing_history: List[RoutingDecision] = []
        self.max_history_size = 1000  # Maximum number of routing decisions to keep
        
        # Callbacks for telemetry and monitoring
        self.on_routing_decision: Optional[Callable[[RoutingDecision], None]] = None
        self.on_agent_metrics_updated: Optional[Callable[[str, AgentMetrics], None]] = None
        
        logger.info("MeshTopologyManager initialized")
    
    def register_agent(self, agent_metrics: AgentMetrics):
        """
        Register an agent with the mesh topology manager.
        
        Args:
            agent_metrics: The metrics for the agent
        """
        self.agent_metrics[agent_metrics.agent_id] = agent_metrics
        logger.info(f"Registered agent {agent_metrics.agent_id} with mesh topology manager")
        
        if self.on_agent_metrics_updated:
            self.on_agent_metrics_updated(agent_metrics.agent_id, agent_metrics)
    
    def update_agent_metrics(self, agent_id: str, **kwargs):
        """
        Update metrics for an agent.
        
        Args:
            agent_id: The ID of the agent to update
            **kwargs: The metrics to update
            
        Returns:
            True if the agent was updated, False if it wasn't found
        """
        if agent_id not in self.agent_metrics:
            logger.warning(f"Attempted to update metrics for unknown agent {agent_id}")
            return False
        
        agent_metrics = self.agent_metrics[agent_id]
        
        # Update metrics
        for key, value in kwargs.items():
            if hasattr(agent_metrics, key):
                setattr(agent_metrics, key, value)
        
        logger.debug(f"Updated metrics for agent {agent_id}")
        
        if self.on_agent_metrics_updated:
            self.on_agent_metrics_updated(agent_id, agent_metrics)
        
        return True
    
    def select_agent(self, 
                    task_type: str,
                    required_capabilities: List[str],
                    topology: AgentMeshTopology,
                    trust_threshold: float = 0.5,
                    context: Optional[Dict[str, Any]] = None) -> RoutingDecision:
        """
        Select an agent for a task based on the mesh topology and routing strategy.
        
        Args:
            task_type: The type of task to route
            required_capabilities: The capabilities required for the task
            topology: The mesh topology configuration
            trust_threshold: The minimum trust score required for an agent
            context: Additional context for the routing decision
            
        Returns:
            A RoutingDecision with the selected agent and fallbacks
        """
        # Filter agents by capabilities and trust threshold
        eligible_agents = [
            agent for agent in self.agent_metrics.values()
            if all(cap in agent.capabilities for cap in required_capabilities)
            and agent.trust_score >= trust_threshold
        ]
        
        if not eligible_agents:
            # No eligible agents, use fallback agents from topology
            fallback_decision = self._select_fallback_agent(task_type, topology, context)
            
            # Record the decision
            self._record_routing_decision(fallback_decision)
            
            return fallback_decision
        
        # Select agent based on routing strategy
        if topology.routing_strategy == RoutingStrategy.TRUST_WEIGHTED:
            decision = self._select_trust_weighted(eligible_agents, topology, context)
        elif topology.routing_strategy == RoutingStrategy.LATENCY_WEIGHTED:
            decision = self._select_latency_weighted(eligible_agents, topology, context)
        else:  # FALLBACK_LINEAR
            decision = self._select_fallback_linear(eligible_agents, topology, context)
        
        # Record the decision
        self._record_routing_decision(decision)
        
        return decision
    
    def _select_trust_weighted(self, 
                              eligible_agents: List[AgentMetrics],
                              topology: AgentMeshTopology,
                              context: Optional[Dict[str, Any]] = None) -> RoutingDecision:
        """
        Select an agent using trust-weighted strategy.
        
        Args:
            eligible_agents: List of eligible agents
            topology: The mesh topology configuration
            context: Additional context for the routing decision
            
        Returns:
            A RoutingDecision with the selected agent
        """
        # Calculate weighted scores based on trust and load
        weighted_scores = []
        for agent in eligible_agents:
            # Higher trust and lower load is better
            # Scale load to be between 0 and 1 (0 = no load, 1 = full load)
            # Final score is trust_score * (1 - load)
            score = agent.trust_score * (1 - agent.load)
            weighted_scores.append((agent, score))
        
        # Sort by score (descending)
        weighted_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select the agent with the highest score
        selected_agent = weighted_scores[0][0]
        score = weighted_scores[0][1]
        
        # Update the agent's last_selected timestamp
        self.update_agent_metrics(selected_agent.agent_id, last_selected=datetime.now())
        
        # Determine fallback agents (next highest scores)
        fallback_agent_ids = [agent.agent_id for agent, _ in weighted_scores[1:4]]
        
        return RoutingDecision(
            selected_agent_id=selected_agent.agent_id,
            fallback_agent_ids=fallback_agent_ids,
            strategy_used=RoutingStrategy.TRUST_WEIGHTED,
            reason=f"Selected based on trust score ({selected_agent.trust_score:.2f}) and load ({selected_agent.load:.2f})",
            score=score
        )
    
    def _select_latency_weighted(self, 
                               eligible_agents: List[AgentMetrics],
                               topology: AgentMeshTopology,
                               context: Optional[Dict[str, Any]] = None) -> RoutingDecision:
        """
        Select an agent using latency-weighted strategy.
        
        Args:
            eligible_agents: List of eligible agents
            topology: The mesh topology configuration
            context: Additional context for the routing decision
            
        Returns:
            A RoutingDecision with the selected agent
        """
        # Calculate weighted scores based on latency and load
        weighted_scores = []
        for agent in eligible_agents:
            # Lower latency and lower load is better
            # Normalize latency to be between 0 and 1 (1 = lowest latency)
            # Use 1000ms as a reference point for normalization
            normalized_latency = max(0, 1 - (agent.avg_latency_ms / 1000))
            score = normalized_latency * (1 - agent.load)
            weighted_scores.append((agent, score))
        
        # Sort by score (descending)
        weighted_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Select the agent with the highest score
        selected_agent = weighted_scores[0][0]
        score = weighted_scores[0][1]
        
        # Update the agent's last_selected timestamp
        self.update_agent_metrics(selected_agent.agent_id, last_selected=datetime.now())
        
        # Determine fallback agents (next highest scores)
        fallback_agent_ids = [agent.agent_id for agent, _ in weighted_scores[1:4]]
        
        return RoutingDecision(
            selected_agent_id=selected_agent.agent_id,
            fallback_agent_ids=fallback_agent_ids,
            strategy_used=RoutingStrategy.LATENCY_WEIGHTED,
            reason=f"Selected based on latency ({selected_agent.avg_latency_ms:.2f}ms) and load ({selected_agent.load:.2f})",
            score=score
        )
    
    def _select_fallback_linear(self, 
                              eligible_agents: List[AgentMetrics],
                              topology: AgentMeshTopology,
                              context: Optional[Dict[str, Any]] = None) -> RoutingDecision:
        """
        Select an agent using fallback-linear strategy.
        
        Args:
            eligible_agents: List of eligible agents
            topology: The mesh topology configuration
            context: Additional context for the routing decision
            
        Returns:
            A RoutingDecision with the selected agent
        """
        # Sort agents by trust score (descending)
        sorted_agents = sorted(eligible_agents, key=lambda a: a.trust_score, reverse=True)
        
        # Select the agent with the highest trust score
        selected_agent = sorted_agents[0]
        
        # Update the agent's last_selected timestamp
        self.update_agent_metrics(selected_agent.agent_id, last_selected=datetime.now())
        
        # Determine fallback agents (next highest trust scores)
        fallback_agent_ids = [agent.agent_id for agent in sorted_agents[1:4]]
        
        return RoutingDecision(
            selected_agent_id=selected_agent.agent_id,
            fallback_agent_ids=fallback_agent_ids,
            strategy_used=RoutingStrategy.FALLBACK_LINEAR,
            reason=f"Selected based on trust score ({selected_agent.trust_score:.2f})",
            score=selected_agent.trust_score
        )
    
    def _select_fallback_agent(self, 
                             task_type: str,
                             topology: AgentMeshTopology,
                             context: Optional[Dict[str, Any]] = None) -> RoutingDecision:
        """
        Select a fallback agent when no eligible agents are available.
        
        Args:
            task_type: The type of task to route
            topology: The mesh topology configuration
            context: Additional context for the routing decision
            
        Returns:
            A RoutingDecision with the selected fallback agent
        """
        # Check if there are any fallback agents defined in the topology
        if topology.fallback_agents:
            # Sort fallback agents by priority (ascending)
            sorted_fallbacks = sorted(topology.fallback_agents, key=lambda a: a.priority)
            
            # Select the fallback agent with the highest priority (lowest number)
            selected_fallback = sorted_fallbacks[0]
            
            # Check if the fallback agent exists in our metrics
            if selected_fallback.agent_id in self.agent_metrics:
                # Update the agent's last_selected timestamp
                self.update_agent_metrics(selected_fallback.agent_id, last_selected=datetime.now())
            
            return RoutingDecision(
                selected_agent_id=selected_fallback.agent_id,
                fallback_agent_ids=[a.agent_id for a in sorted_fallbacks[1:]],
                strategy_used=RoutingStrategy.FALLBACK_LINEAR,
                reason=f"Selected fallback agent due to no eligible agents for task type {task_type}",
                score=0.0
            )
        
        # No fallback agents defined, use a default fallback
        return RoutingDecision(
            selected_agent_id="workflow_fallback_agent",
            fallback_agent_ids=["human_intervention_agent"],
            strategy_used=RoutingStrategy.FALLBACK_LINEAR,
            reason=f"Selected default fallback agent due to no eligible or defined fallback agents for task type {task_type}",
            score=0.0
        )
    
    def report_agent_success(self, agent_id: str, latency_ms: float):
        """
        Report a successful agent execution.
        
        Args:
            agent_id: The ID of the agent
            latency_ms: The latency of the execution in milliseconds
            
        Returns:
            True if the agent was updated, False if it wasn't found
        """
        if agent_id not in self.agent_metrics:
            logger.warning(f"Attempted to report success for unknown agent {agent_id}")
            return False
        
        agent = self.agent_metrics[agent_id]
        
        # Update metrics
        # Weighted average for latency (more weight to recent executions)
        agent.avg_latency_ms = 0.8 * agent.avg_latency_ms + 0.2 * latency_ms
        
        # Increase success rate (weighted)
        agent.success_rate = 0.95 * agent.success_rate + 0.05 * 1.0
        
        # Reset consecutive failures
        agent.consecutive_failures = 0
        
        # Decrease load slightly (task completed)
        agent.load = max(0.0, agent.load - 0.1)
        
        logger.debug(f"Reported success for agent {agent_id}, new latency: {agent.avg_latency_ms:.2f}ms, success rate: {agent.success_rate:.2f}")
        
        if self.on_agent_metrics_updated:
            self.on_agent_metrics_updated(agent_id, agent)
        
        return True
    
    def report_agent_failure(self, agent_id: str, error_message: Optional[str] = None):
        """
        Report a failed agent execution.
        
        Args:
            agent_id: The ID of the agent
            error_message: Optional error message
            
        Returns:
            True if the agent was updated, False if it wasn't found
        """
        if agent_id not in self.agent_metrics:
            logger.warning(f"Attempted to report failure for unknown agent {agent_id}")
            return False
        
        agent = self.agent_metrics[agent_id]
        
        # Update metrics
        # Decrease success rate (weighted)
        agent.success_rate = 0.95 * agent.success_rate + 0.05 * 0.0
        
        # Increase consecutive failures
        agent.consecutive_failures += 1
        
        # Update last failed timestamp
        agent.last_failed = datetime.now()
        
        # Decrease trust score based on consecutive failures
        if agent.consecutive_failures > 3:
            # More aggressive trust reduction for repeated failures
            trust_reduction = 0.1 * min(agent.consecutive_failures, 10)
            agent.trust_score = max(0.0, agent.trust_score - trust_reduction)
        
        logger.debug(f"Reported failure for agent {agent_id}, consecutive failures: {agent.consecutive_failures}, new trust score: {agent.trust_score:.2f}")
        
        if self.on_agent_metrics_updated:
            self.on_agent_metrics_updated(agent_id, agent)
        
        return True
    
    def update_agent_load(self, agent_id: str, load_delta: float):
        """
        Update the load for an agent.
        
        Args:
            agent_id: The ID of the agent
            load_delta: The change in load (positive or negative)
            
        Returns:
            True if the agent was updated, False if it wasn't found
        """
        if agent_id not in self.agent_metrics:
            logger.warning(f"Attempted to update load for unknown agent {agent_id}")
            return False
        
        agent = self.agent_metrics[agent_id]
        
        # Update load (clamp between 0 and 1)
        agent.load = max(0.0, min(1.0, agent.load + load_delta))
        
        logger.debug(f"Updated load for agent {agent_id}, new load: {agent.load:.2f}")
        
        if self.on_agent_metrics_updated:
            self.on_agent_metrics_updated(agent_id, agent)
        
        return True
    
    def handle_congestion(self, 
                         agent_id: str, 
                         topology: AgentMeshTopology,
                         task_type: str,
                         required_capabilities: List[str]) -> Optional[RoutingDecision]:
        """
        Handle congestion for an agent based on the mesh topology.
        
        Args:
            agent_id: The ID of the congested agent
            topology: The mesh topology configuration
            task_type: The type of task being routed
            required_capabilities: The capabilities required for the task
            
        Returns:
            A new RoutingDecision if rerouting, None otherwise
        """
        if agent_id not in self.agent_metrics:
            logger.warning(f"Attempted to handle congestion for unknown agent {agent_id}")
            return None
        
        agent = self.agent_metrics[agent_id]
        
        # Check if the agent is actually congested
        if agent.load < 0.8:
            logger.debug(f"Agent {agent_id} is not congested (load: {agent.load:.2f})")
            return None
        
        # Handle congestion based on the configured behavior
        if topology.congestion_behavior == CongestionBehavior.QUEUE:
            # Just queue the task, no rerouting
            logger.info(f"Queuing task for congested agent {agent_id} (load: {agent.load:.2f})")
            return None
        
        elif topology.congestion_behavior == CongestionBehavior.REROUTE and topology.allow_rerouting:
            # Reroute to another agent
            logger.info(f"Rerouting task from congested agent {agent_id} (load: {agent.load:.2f})")
            
            # Select a new agent, excluding the congested one
            eligible_agents = [
                a for a in self.agent_metrics.values()
                if a.agent_id != agent_id
                and all(cap in a.capabilities for cap in required_capabilities)
            ]
            
            if not eligible_agents:
                logger.warning(f"No alternative agents available for rerouting from congested agent {agent_id}")
                return None
            
            # Use the same routing strategy to select an alternative
            if topology.routing_strategy == RoutingStrategy.TRUST_WEIGHTED:
                decision = self._select_trust_weighted(eligible_agents, topology)
            elif topology.routing_strategy == RoutingStrategy.LATENCY_WEIGHTED:
                decision = self._select_latency_weighted(eligible_agents, topology)
            else:  # FALLBACK_LINEAR
                decision = self._select_fallback_linear(eligible_agents, topology)
            
            # Update the reason to indicate rerouting
            decision.reason = f"Rerouted from congested agent {agent_id} (load: {agent.load:.2f})"
            
            # Record the decision
            self._record_routing_decision(decision)
            
            return decision
        
        elif topology.congestion_behavior == CongestionBehavior.DEGRADE_GRACEFULLY:
            # Continue with the congested agent but note the degradation
            logger.info(f"Degrading gracefully for congested agent {agent_id} (load: {agent.load:.2f})")
            
            # Optionally, we could adjust parameters or expectations here
            # For now, we'll just return None to indicate no rerouting
            return None
        
        return None
    
    def _record_routing_decision(self, decision: RoutingDecision):
        """
        Record a routing decision in the history.
        
        Args:
            decision: The routing decision to record
        """
        self.routing_history.append(decision)
        
        # Trim history if it exceeds the maximum size
        if len(self.routing_history) > self.max_history_size:
            self.routing_history = self.routing_history[-self.max_history_size:]
        
        # Notify callback if registered
        if self.on_routing_decision:
            self.on_routing_decision(decision)
    
    def get_routing_history(self, 
                          agent_id: Optional[str] = None,
                          strategy: Optional[RoutingStrategy] = None,
                          start_time: Optional[datetime] = None,
                          end_time: Optional[datetime] = None,
                          limit: Optional[int] = None) -> List[RoutingDecision]:
        """
        Get routing decision history, optionally filtered by various criteria.
        
        Args:
            agent_id: Filter by selected agent ID
            strategy: Filter by routing strategy
            start_time: Filter by start time (inclusive)
            end_time: Filter by end time (inclusive)
            limit: Maximum number of decisions to return
            
        Returns:
            A list of RoutingDecision objects matching the criteria
        """
        result = self.routing_history
        
        # Apply filters
        if agent_id:
            result = [d for d in result if d.selected_agent_id == agent_id]
        
        if strategy:
            result = [d for d in result if d.strategy_used == strategy]
        
        if start_time:
            result = [d for d in result if d.timestamp >= start_time]
        
        if end_time:
            result = [d for d in result if d.timestamp <= end_time]
        
        # Sort by timestamp (newest first)
        result.sort(key=lambda d: d.timestamp, reverse=True)
        
        # Apply limit
        if limit:
            result = result[:limit]
        
        return result
    
    def get_agent_selection_stats(self, time_window_minutes: int = 60) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics on agent selections over a time window.
        
        Args:
            time_window_minutes: The time window in minutes
            
        Returns:
            A dictionary mapping agent IDs to selection statistics
        """
        # Calculate start time
        start_time = datetime.now() - timedelta(minutes=time_window_minutes)
        
        # Get relevant routing decisions
        decisions = self.get_routing_history(start_time=start_time)
        
        # Count selections by agent
        stats = {}
        for agent_id in self.agent_metrics:
            selections = [d for d in decisions if d.selected_agent_id == agent_id]
            
            # Calculate average score
            avg_score = sum(d.score for d in selections) / len(selections) if selections else 0
            
            # Count by strategy
            strategy_counts = {}
            for strategy in RoutingStrategy:
                strategy_counts[strategy] = len([d for d in selections if d.strategy_used == strategy])
            
            stats[agent_id] = {
                "total_selections": len(selections),
                "average_score": avg_score,
                "strategy_counts": strategy_counts,
                "last_selected": self.agent_metrics[agent_id].last_selected,
                "current_load": self.agent_metrics[agent_id].load,
                "current_trust_score": self.agent_metrics[agent_id].trust_score
            }
        
        return stats
    
    def optimize_mesh(self):
        """
        Optimize the mesh topology based on historical performance.
        
        This method analyzes routing history and agent metrics to suggest
        optimizations to the mesh topology.
        
        Returns:
            A dictionary with optimization suggestions
        """
        # This is a placeholder for more sophisticated optimization logic
        # In a real implementation, this would analyze patterns and suggest changes
        
        suggestions = {
            "underutilized_agents": [],
            "overloaded_agents": [],
            "low_trust_agents": [],
            "high_latency_agents": [],
            "recommended_fallbacks": []
        }
        
        # Find underutilized agents (low load, high trust)
        for agent_id, metrics in self.agent_metrics.items():
            if metrics.load < 0.3 and metrics.trust_score > 0.8:
                suggestions["underutilized_agents"].append(agent_id)
            
            if metrics.load > 0.8:
                suggestions["overloaded_agents"].append(agent_id)
            
            if metrics.trust_score < 0.6:
                suggestions["low_trust_agents"].append(agent_id)
            
            if metrics.avg_latency_ms > 500:
                suggestions["high_latency_agents"].append(agent_id)
        
        # Recommend fallbacks based on trust scores
        high_trust_agents = sorted(
            [(agent_id, metrics.trust_score) for agent_id, metrics in self.agent_metrics.items() if metrics.trust_score > 0.8],
            key=lambda x: x[1],
            reverse=True
        )
        
        suggestions["recommended_fallbacks"] = [agent_id for agent_id, _ in high_trust_agents[:3]]
        
        return suggestions
    
    def simulate_routing(self, 
                       task_type: str,
                       required_capabilities: List[str],
                       topology: AgentMeshTopology,
                       num_simulations: int = 100) -> Dict[str, Any]:
        """
        Simulate routing decisions to evaluate different strategies.
        
        Args:
            task_type: The type of task to route
            required_capabilities: The capabilities required for the task
            topology: The mesh topology configuration
            num_simulations: Number of simulations to run
            
        Returns:
            A dictionary with simulation results
        """
        results = {
            "trust_weighted": {"selections": {}, "avg_score": 0},
            "latency_weighted": {"selections": {}, "avg_score": 0},
            "fallback_linear": {"selections": {}, "avg_score": 0}
        }
        
        # Initialize selection counters
        for strategy in results:
            for agent_id in self.agent_metrics:
                results[strategy]["selections"][agent_id] = 0
        
        # Run simulations
        for _ in range(num_simulations):
            # Simulate each strategy
            for strategy_name, strategy_enum in [
                ("trust_weighted", RoutingStrategy.TRUST_WEIGHTED),
                ("latency_weighted", RoutingStrategy.LATENCY_WEIGHTED),
                ("fallback_linear", RoutingStrategy.FALLBACK_LINEAR)
            ]:
                # Create a topology with the current strategy
                sim_topology = AgentMeshTopology(
                    routing_strategy=strategy_enum,
                    allow_rerouting=topology.allow_rerouting,
                    fallback_agents=topology.fallback_agents,
                    congestion_behavior=topology.congestion_behavior
                )
                
                # Select an agent
                decision = self.select_agent(task_type, required_capabilities, sim_topology)
                
                # Record the selection
                results[strategy_name]["selections"][decision.selected_agent_id] += 1
                results[strategy_name]["avg_score"] += decision.score
        
        # Calculate average scores
        for strategy in results:
            results[strategy]["avg_score"] /= num_simulations
        
        return results
