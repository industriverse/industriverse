"""
Workflow Optimizer Agent Module for Industriverse Workflow Automation Layer

This module implements the Workflow Optimizer Agent, which is responsible for
analyzing workflow execution patterns, identifying optimization opportunities,
and applying improvements to workflow definitions and execution strategies.

The WorkflowOptimizerAgent class extends the BaseAgent to provide specialized
functionality for workflow optimization.
"""

import logging
import asyncio
import json
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime, timedelta
import statistics

from pydantic import BaseModel, Field, validator

from .base_agent import BaseAgent, AgentMetadata, AgentConfig, AgentContext, AgentResult, AgentCapability

# Configure logging
logger = logging.getLogger(__name__)


class OptimizationStrategy(str, Enum):
    """Enum representing the possible optimization strategies."""
    PERFORMANCE = "performance"
    RESOURCE_USAGE = "resource_usage"
    RELIABILITY = "reliability"
    COST = "cost"
    BALANCED = "balanced"


class OptimizationLevel(str, Enum):
    """Enum representing the possible optimization levels."""
    CONSERVATIVE = "conservative"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class OptimizationSuggestion(BaseModel):
    """Model representing a workflow optimization suggestion."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    workflow_id: str
    timestamp: datetime = Field(default_factory=datetime.now)
    type: str  # e.g., "task_reordering", "parallel_execution", "resource_allocation"
    description: str
    expected_improvement: str
    confidence: float  # 0.0 to 1.0
    impact: float  # 0.0 to 1.0
    implementation_complexity: float  # 0.0 to 1.0
    applied: bool = False
    applied_at: Optional[datetime] = None
    result: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class WorkflowPerformanceMetrics(BaseModel):
    """Model representing performance metrics for a workflow execution."""
    workflow_id: str
    execution_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    task_metrics: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    resource_usage: Dict[str, Any] = Field(default_factory=dict)
    error_count: int = 0
    retry_count: int = 0
    success: bool = True
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def calculate_duration(self):
        """Calculate the duration if start and end times are available."""
        if self.start_time and self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def add_task_metric(self, task_id: str, metrics: Dict[str, Any]):
        """Add metrics for a specific task."""
        self.task_metrics[task_id] = metrics
    
    def update_resource_usage(self, resource_usage: Dict[str, Any]):
        """Update resource usage metrics."""
        self.resource_usage.update(resource_usage)
    
    def mark_completed(self, success: bool = True, end_time: Optional[datetime] = None):
        """Mark the workflow execution as completed."""
        self.end_time = end_time or datetime.now()
        self.success = success
        self.calculate_duration()


class OptimizationConfig(BaseModel):
    """Model representing configuration for the workflow optimizer."""
    strategy: OptimizationStrategy = OptimizationStrategy.BALANCED
    level: OptimizationLevel = OptimizationLevel.MODERATE
    auto_apply: bool = False
    min_confidence: float = 0.7
    min_impact: float = 0.2
    max_implementation_complexity: float = 0.8
    metrics_retention_days: int = 30
    enabled_optimization_types: List[str] = Field(default_factory=lambda: [
        "task_reordering", 
        "parallel_execution", 
        "resource_allocation",
        "execution_mode_selection",
        "mesh_topology_optimization"
    ])


class WorkflowOptimizerAgent(BaseAgent):
    """
    Agent responsible for analyzing workflow execution patterns and optimizing workflows.
    
    This agent monitors workflow executions, identifies optimization opportunities,
    and can apply improvements to workflow definitions and execution strategies.
    """
    
    def __init__(self, 
                 config: Optional[OptimizationConfig] = None,
                 metadata: Optional[AgentMetadata] = None, 
                 agent_config: Optional[AgentConfig] = None):
        """
        Initialize the WorkflowOptimizerAgent.
        
        Args:
            config: Configuration for the optimizer
            metadata: Optional metadata for the agent
            agent_config: Optional configuration for the agent
        """
        if metadata is None:
            metadata = AgentMetadata(
                id="workflow_optimizer_agent",
                name="Workflow Optimizer Agent",
                description="Analyzes and optimizes workflow execution patterns",
                capabilities=[AgentCapability.WORKFLOW_OPTIMIZATION]
            )
        
        super().__init__(metadata, agent_config)
        
        self.config = config or OptimizationConfig()
        
        # Store performance metrics
        self.performance_metrics: Dict[str, List[WorkflowPerformanceMetrics]] = {}
        
        # Store optimization suggestions
        self.optimization_suggestions: Dict[str, List[OptimizationSuggestion]] = {}
        
        # Callbacks
        self.on_suggestion_created: Optional[Callable[[OptimizationSuggestion], None]] = None
        self.on_suggestion_applied: Optional[Callable[[OptimizationSuggestion], None]] = None
        
        # Background tasks
        self.background_tasks = []
        
        logger.info(f"WorkflowOptimizerAgent initialized with strategy {self.config.strategy}")
    
    async def _initialize_impl(self) -> bool:
        """
        Implementation of agent initialization.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        # Start background tasks for metrics cleanup
        self._start_metrics_cleanup_task()
        
        return True
    
    def _start_metrics_cleanup_task(self):
        """Start the background task for cleaning up old metrics."""
        task = asyncio.create_task(self._cleanup_old_metrics())
        self.background_tasks.append(task)
    
    async def _cleanup_old_metrics(self):
        """Periodically clean up old metrics."""
        while True:
            try:
                # Sleep for a day
                await asyncio.sleep(86400)  # 24 hours
                
                # Calculate cutoff date
                cutoff_date = datetime.now() - timedelta(days=self.config.metrics_retention_days)
                
                # Clean up old metrics
                for workflow_id, metrics_list in list(self.performance_metrics.items()):
                    # Filter out old metrics
                    new_metrics_list = [
                        m for m in metrics_list
                        if m.start_time >= cutoff_date
                    ]
                    
                    # Update or remove the list
                    if new_metrics_list:
                        self.performance_metrics[workflow_id] = new_metrics_list
                    else:
                        del self.performance_metrics[workflow_id]
                
                logger.info(f"Cleaned up metrics older than {cutoff_date}")
            
            except Exception as e:
                logger.error(f"Error in metrics cleanup task: {e}")
                await asyncio.sleep(3600)  # Sleep for an hour on error
    
    async def record_workflow_start(self, workflow_id: str, execution_id: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Record the start of a workflow execution.
        
        Args:
            workflow_id: The ID of the workflow
            execution_id: The ID of the workflow execution
            metadata: Optional metadata about the workflow execution
            
        Returns:
            The execution ID
        """
        # Create metrics object
        metrics = WorkflowPerformanceMetrics(
            workflow_id=workflow_id,
            execution_id=execution_id,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        
        # Initialize metrics list if needed
        if workflow_id not in self.performance_metrics:
            self.performance_metrics[workflow_id] = []
        
        # Add metrics
        self.performance_metrics[workflow_id].append(metrics)
        
        logger.info(f"Recorded start of workflow {workflow_id}, execution {execution_id}")
        return execution_id
    
    async def record_workflow_completion(self, workflow_id: str, execution_id: str, success: bool = True, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record the completion of a workflow execution.
        
        Args:
            workflow_id: The ID of the workflow
            execution_id: The ID of the workflow execution
            success: Whether the workflow completed successfully
            metadata: Optional metadata about the workflow execution
            
        Returns:
            True if the metrics were updated, False if the execution wasn't found
        """
        # Find the metrics object
        metrics_list = self.performance_metrics.get(workflow_id, [])
        for metrics in metrics_list:
            if metrics.execution_id == execution_id:
                # Update metrics
                metrics.mark_completed(success=success)
                
                # Update metadata if provided
                if metadata:
                    metrics.metadata.update(metadata)
                
                logger.info(f"Recorded completion of workflow {workflow_id}, execution {execution_id}, success: {success}")
                
                # Analyze for optimization opportunities
                await self._analyze_workflow_execution(metrics)
                
                return True
        
        logger.warning(f"Attempted to record completion of unknown workflow execution: {workflow_id}, {execution_id}")
        return False
    
    async def record_task_metrics(self, workflow_id: str, execution_id: str, task_id: str, metrics: Dict[str, Any]) -> bool:
        """
        Record metrics for a specific task in a workflow execution.
        
        Args:
            workflow_id: The ID of the workflow
            execution_id: The ID of the workflow execution
            task_id: The ID of the task
            metrics: The metrics to record
            
        Returns:
            True if the metrics were recorded, False if the execution wasn't found
        """
        # Find the metrics object
        metrics_list = self.performance_metrics.get(workflow_id, [])
        for workflow_metrics in metrics_list:
            if workflow_metrics.execution_id == execution_id:
                # Add task metrics
                workflow_metrics.add_task_metric(task_id, metrics)
                
                logger.debug(f"Recorded metrics for task {task_id} in workflow {workflow_id}, execution {execution_id}")
                return True
        
        logger.warning(f"Attempted to record task metrics for unknown workflow execution: {workflow_id}, {execution_id}")
        return False
    
    async def record_resource_usage(self, workflow_id: str, execution_id: str, resource_usage: Dict[str, Any]) -> bool:
        """
        Record resource usage for a workflow execution.
        
        Args:
            workflow_id: The ID of the workflow
            execution_id: The ID of the workflow execution
            resource_usage: The resource usage metrics
            
        Returns:
            True if the metrics were recorded, False if the execution wasn't found
        """
        # Find the metrics object
        metrics_list = self.performance_metrics.get(workflow_id, [])
        for metrics in metrics_list:
            if metrics.execution_id == execution_id:
                # Update resource usage
                metrics.update_resource_usage(resource_usage)
                
                logger.debug(f"Recorded resource usage for workflow {workflow_id}, execution {execution_id}")
                return True
        
        logger.warning(f"Attempted to record resource usage for unknown workflow execution: {workflow_id}, {execution_id}")
        return False
    
    async def _analyze_workflow_execution(self, metrics: WorkflowPerformanceMetrics):
        """
        Analyze a completed workflow execution for optimization opportunities.
        
        Args:
            metrics: The performance metrics for the workflow execution
        """
        # Skip analysis if the workflow didn't complete successfully
        if not metrics.success:
            logger.debug(f"Skipping optimization analysis for failed workflow {metrics.workflow_id}, execution {metrics.execution_id}")
            return
        
        # Get historical metrics for this workflow
        historical_metrics = [
            m for m in self.performance_metrics.get(metrics.workflow_id, [])
            if m.execution_id != metrics.execution_id and m.success and m.duration_seconds is not None
        ]
        
        # Skip if we don't have enough historical data
        if len(historical_metrics) < 3:
            logger.debug(f"Not enough historical data for workflow {metrics.workflow_id} to perform optimization analysis")
            return
        
        # Analyze for task reordering opportunities
        if "task_reordering" in self.config.enabled_optimization_types:
            await self._analyze_task_reordering(metrics, historical_metrics)
        
        # Analyze for parallel execution opportunities
        if "parallel_execution" in self.config.enabled_optimization_types:
            await self._analyze_parallel_execution(metrics, historical_metrics)
        
        # Analyze for resource allocation opportunities
        if "resource_allocation" in self.config.enabled_optimization_types:
            await self._analyze_resource_allocation(metrics, historical_metrics)
        
        # Analyze for execution mode selection opportunities
        if "execution_mode_selection" in self.config.enabled_optimization_types:
            await self._analyze_execution_mode_selection(metrics, historical_metrics)
        
        # Analyze for mesh topology optimization opportunities
        if "mesh_topology_optimization" in self.config.enabled_optimization_types:
            await self._analyze_mesh_topology_optimization(metrics, historical_metrics)
    
    async def _analyze_task_reordering(self, metrics: WorkflowPerformanceMetrics, historical_metrics: List[WorkflowPerformanceMetrics]):
        """
        Analyze for task reordering optimization opportunities.
        
        Args:
            metrics: The current execution metrics
            historical_metrics: Historical execution metrics for the same workflow
        """
        # This is a simplified example of task reordering analysis
        # In a real implementation, this would involve more sophisticated analysis
        
        # Skip if we don't have task metrics
        if not metrics.task_metrics:
            return
        
        # Identify tasks with high variance in execution time
        task_durations = {}
        for task_id, task_metrics in metrics.task_metrics.items():
            if "duration_seconds" in task_metrics:
                task_durations[task_id] = task_metrics["duration_seconds"]
        
        # Skip if we don't have enough task duration data
        if len(task_durations) < 2:
            return
        
        # Find the longest-running task
        longest_task_id = max(task_durations.items(), key=lambda x: x[1])[0]
        longest_task_duration = task_durations[longest_task_id]
        
        # Check if the longest task is significantly longer than the average
        avg_duration = statistics.mean(task_durations.values())
        if longest_task_duration > avg_duration * 2:
            # This task is a bottleneck, suggest reordering to start it earlier
            suggestion = OptimizationSuggestion(
                workflow_id=metrics.workflow_id,
                type="task_reordering",
                description=f"Task {longest_task_id} is a bottleneck (duration: {longest_task_duration:.2f}s, avg: {avg_duration:.2f}s). Consider reordering to start it earlier or in parallel with other tasks.",
                expected_improvement=f"Potential reduction in overall workflow duration by up to {longest_task_duration - avg_duration:.2f}s",
                confidence=0.8,
                impact=min(1.0, (longest_task_duration - avg_duration) / avg_duration),
                implementation_complexity=0.5
            )
            
            await self._add_suggestion(suggestion)
    
    async def _analyze_parallel_execution(self, metrics: WorkflowPerformanceMetrics, historical_metrics: List[WorkflowPerformanceMetrics]):
        """
        Analyze for parallel execution optimization opportunities.
        
        Args:
            metrics: The current execution metrics
            historical_metrics: Historical execution metrics for the same workflow
        """
        # This is a simplified example of parallel execution analysis
        # In a real implementation, this would involve dependency analysis
        
        # Skip if we don't have task metrics
        if not metrics.task_metrics:
            return
        
        # Identify independent tasks that could potentially run in parallel
        # For this simplified example, we'll just look for tasks with similar start times
        task_start_times = {}
        for task_id, task_metrics in metrics.task_metrics.items():
            if "start_time" in task_metrics:
                task_start_times[task_id] = task_metrics["start_time"]
        
        # Skip if we don't have enough task start time data
        if len(task_start_times) < 3:
            return
        
        # Group tasks by similar start times
        # This is a simplified approach; in reality, you'd need to analyze task dependencies
        sequential_groups = []
        sorted_tasks = sorted(task_start_times.items(), key=lambda x: x[1])
        current_group = [sorted_tasks[0][0]]
        
        for i in range(1, len(sorted_tasks)):
            current_task_id, current_start_time = sorted_tasks[i]
            prev_task_id, prev_start_time = sorted_tasks[i-1]
            
            # If tasks start close together, they might be sequential
            if (current_start_time - prev_start_time).total_seconds() < 1.0:
                current_group.append(current_task_id)
            else:
                if len(current_group) > 1:
                    sequential_groups.append(current_group)
                current_group = [current_task_id]
        
        if len(current_group) > 1:
            sequential_groups.append(current_group)
        
        # For each group of sequential tasks, suggest parallelization if appropriate
        for group in sequential_groups:
            if len(group) >= 2:
                # Calculate potential time savings
                group_durations = [
                    metrics.task_metrics[task_id].get("duration_seconds", 0)
                    for task_id in group
                    if "duration_seconds" in metrics.task_metrics[task_id]
                ]
                
                if not group_durations:
                    continue
                
                total_sequential_time = sum(group_durations)
                max_parallel_time = max(group_durations)
                potential_savings = total_sequential_time - max_parallel_time
                
                if potential_savings > 1.0:  # Only suggest if savings > 1 second
                    suggestion = OptimizationSuggestion(
                        workflow_id=metrics.workflow_id,
                        type="parallel_execution",
                        description=f"Tasks {', '.join(group)} appear to run sequentially but might be parallelizable.",
                        expected_improvement=f"Potential reduction in workflow duration by up to {potential_savings:.2f}s by parallelizing these tasks.",
                        confidence=0.7,
                        impact=min(1.0, potential_savings / (metrics.duration_seconds or 1)),
                        implementation_complexity=0.6
                    )
                    
                    await self._add_suggestion(suggestion)
    
    async def _analyze_resource_allocation(self, metrics: WorkflowPerformanceMetrics, historical_metrics: List[WorkflowPerformanceMetrics]):
        """
        Analyze for resource allocation optimization opportunities.
        
        Args:
            metrics: The current execution metrics
            historical_metrics: Historical execution metrics for the same workflow
        """
        # This is a simplified example of resource allocation analysis
        
        # Skip if we don't have resource usage data
        if not metrics.resource_usage:
            return
        
        # Check for CPU bottlenecks
        cpu_usage = metrics.resource_usage.get("cpu_percent")
        if cpu_usage and cpu_usage > 90:
            suggestion = OptimizationSuggestion(
                workflow_id=metrics.workflow_id,
                type="resource_allocation",
                description=f"High CPU usage detected ({cpu_usage}%). Consider allocating more CPU resources or optimizing CPU-intensive tasks.",
                expected_improvement="Potential reduction in workflow duration by alleviating CPU bottlenecks.",
                confidence=0.8,
                impact=0.7,
                implementation_complexity=0.5
            )
            
            await self._add_suggestion(suggestion)
        
        # Check for memory bottlenecks
        memory_usage = metrics.resource_usage.get("memory_percent")
        if memory_usage and memory_usage > 90:
            suggestion = OptimizationSuggestion(
                workflow_id=metrics.workflow_id,
                type="resource_allocation",
                description=f"High memory usage detected ({memory_usage}%). Consider allocating more memory or optimizing memory-intensive tasks.",
                expected_improvement="Potential reduction in workflow duration and improved stability by alleviating memory bottlenecks.",
                confidence=0.8,
                impact=0.8,
                implementation_complexity=0.5
            )
            
            await self._add_suggestion(suggestion)
    
    async def _analyze_execution_mode_selection(self, metrics: WorkflowPerformanceMetrics, historical_metrics: List[WorkflowPerformanceMetrics]):
        """
        Analyze for execution mode selection optimization opportunities.
        
        Args:
            metrics: The current execution metrics
            historical_metrics: Historical execution metrics for the same workflow
        """
        # This is a simplified example of execution mode selection analysis
        
        # Get the current execution mode
        current_mode = metrics.metadata.get("execution_mode", "reactive")
        
        # Check if we have executions with different modes to compare
        other_mode_metrics = [
            m for m in historical_metrics
            if m.metadata.get("execution_mode") and m.metadata.get("execution_mode") != current_mode
        ]
        
        if not other_mode_metrics:
            return
        
        # Compare performance across different execution modes
        current_mode_duration = metrics.duration_seconds or 0
        other_mode_durations = {
            m.metadata.get("execution_mode"): m.duration_seconds
            for m in other_mode_metrics
            if m.duration_seconds is not None
        }
        
        for mode, duration in other_mode_durations.items():
            # If another mode is significantly faster
            if duration < current_mode_duration * 0.8:  # At least 20% faster
                suggestion = OptimizationSuggestion(
                    workflow_id=metrics.workflow_id,
                    type="execution_mode_selection",
                    description=f"Execution mode '{mode}' appears to be faster than current mode '{current_mode}' ({duration:.2f}s vs {current_mode_duration:.2f}s).",
                    expected_improvement=f"Potential reduction in workflow duration by up to {current_mode_duration - duration:.2f}s by switching execution mode.",
                    confidence=0.7,
                    impact=min(1.0, (current_mode_duration - duration) / current_mode_duration),
                    implementation_complexity=0.3
                )
                
                await self._add_suggestion(suggestion)
    
    async def _analyze_mesh_topology_optimization(self, metrics: WorkflowPerformanceMetrics, historical_metrics: List[WorkflowPerformanceMetrics]):
        """
        Analyze for mesh topology optimization opportunities.
        
        Args:
            metrics: The current execution metrics
            historical_metrics: Historical execution metrics for the same workflow
        """
        # This is a simplified example of mesh topology optimization analysis
        
        # Check if we have mesh topology information
        current_topology = metrics.metadata.get("mesh_topology")
        if not current_topology:
            return
        
        # Check for communication overhead
        communication_overhead = metrics.metadata.get("communication_overhead_ms")
        if communication_overhead and communication_overhead > 1000:  # > 1 second
            suggestion = OptimizationSuggestion(
                workflow_id=metrics.workflow_id,
                type="mesh_topology_optimization",
                description=f"High communication overhead detected ({communication_overhead}ms) with current mesh topology '{current_topology}'. Consider optimizing agent placement or topology.",
                expected_improvement=f"Potential reduction in workflow duration by up to {communication_overhead/1000:.2f}s by reducing communication overhead.",
                confidence=0.7,
                impact=min(1.0, communication_overhead / ((metrics.duration_seconds or 1) * 1000)),
                implementation_complexity=0.7
            )
            
            await self._add_suggestion(suggestion)
        
        # Check for edge vs. cloud execution
        location = metrics.metadata.get("execution_location", "cloud")
        
        # Compare performance across different locations
        other_location_metrics = [
            m for m in historical_metrics
            if m.metadata.get("execution_location") and m.metadata.get("execution_location") != location
        ]
        
        if other_location_metrics:
            current_location_duration = metrics.duration_seconds or 0
            other_location_durations = {
                m.metadata.get("execution_location"): m.duration_seconds
                for m in other_location_metrics
                if m.duration_seconds is not None
            }
            
            for other_location, duration in other_location_durations.items():
                # If another location is significantly faster
                if duration < current_location_duration * 0.8:  # At least 20% faster
                    suggestion = OptimizationSuggestion(
                        workflow_id=metrics.workflow_id,
                        type="mesh_topology_optimization",
                        description=f"Execution at '{other_location}' appears to be faster than current location '{location}' ({duration:.2f}s vs {current_location_duration:.2f}s).",
                        expected_improvement=f"Potential reduction in workflow duration by up to {current_location_duration - duration:.2f}s by changing execution location.",
                        confidence=0.7,
                        impact=min(1.0, (current_location_duration - duration) / current_location_duration),
                        implementation_complexity=0.6
                    )
                    
                    await self._add_suggestion(suggestion)
    
    async def _add_suggestion(self, suggestion: OptimizationSuggestion):
        """
        Add an optimization suggestion.
        
        Args:
            suggestion: The optimization suggestion
        """
        # Initialize suggestions list if needed
        workflow_id = suggestion.workflow_id
        if workflow_id not in self.optimization_suggestions:
            self.optimization_suggestions[workflow_id] = []
        
        # Check if a similar suggestion already exists
        for existing in self.optimization_suggestions[workflow_id]:
            if existing.type == suggestion.type and existing.description == suggestion.description:
                # Update the existing suggestion instead of adding a new one
                existing.confidence = max(existing.confidence, suggestion.confidence)
                existing.impact = max(existing.impact, suggestion.impact)
                existing.timestamp = datetime.now()
                
                logger.info(f"Updated existing optimization suggestion: {existing.description}")
                
                # Notify callback
                if self.on_suggestion_created:
                    self.on_suggestion_created(existing)
                
                # Auto-apply if configured
                if self.config.auto_apply and not existing.applied:
                    await self._auto_apply_suggestion(existing)
                
                return
        
        # Add the new suggestion
        self.optimization_suggestions[workflow_id].append(suggestion)
        
        logger.info(f"Added new optimization suggestion: {suggestion.description}")
        
        # Notify callback
        if self.on_suggestion_created:
            self.on_suggestion_created(suggestion)
        
        # Auto-apply if configured
        if self.config.auto_apply:
            await self._auto_apply_suggestion(suggestion)
    
    async def _auto_apply_suggestion(self, suggestion: OptimizationSuggestion):
        """
        Automatically apply an optimization suggestion if it meets the criteria.
        
        Args:
            suggestion: The optimization suggestion
        """
        # Check if the suggestion meets the auto-apply criteria
        if (suggestion.confidence >= self.config.min_confidence and
            suggestion.impact >= self.config.min_impact and
            suggestion.implementation_complexity <= self.config.max_implementation_complexity):
            
            # Apply the suggestion
            # In a real implementation, this would involve modifying the workflow definition
            # or execution parameters based on the suggestion type
            
            # For now, just mark it as applied
            suggestion.applied = True
            suggestion.applied_at = datetime.now()
            suggestion.result = "Auto-applied by WorkflowOptimizerAgent"
            
            logger.info(f"Auto-applied optimization suggestion: {suggestion.description}")
            
            # Notify callback
            if self.on_suggestion_applied:
                self.on_suggestion_applied(suggestion)
    
    async def get_workflow_metrics(self, workflow_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get performance metrics for a workflow.
        
        Args:
            workflow_id: The ID of the workflow
            limit: Maximum number of metrics to return
            
        Returns:
            A list of performance metrics
        """
        metrics_list = self.performance_metrics.get(workflow_id, [])
        
        # Sort by start time (newest first) and limit
        sorted_metrics = sorted(metrics_list, key=lambda m: m.start_time, reverse=True)[:limit]
        
        return [m.dict() for m in sorted_metrics]
    
    async def get_optimization_suggestions(self, workflow_id: str, include_applied: bool = True) -> List[Dict[str, Any]]:
        """
        Get optimization suggestions for a workflow.
        
        Args:
            workflow_id: The ID of the workflow
            include_applied: Whether to include applied suggestions
            
        Returns:
            A list of optimization suggestions
        """
        suggestions_list = self.optimization_suggestions.get(workflow_id, [])
        
        # Filter by applied status if needed
        if not include_applied:
            suggestions_list = [s for s in suggestions_list if not s.applied]
        
        # Sort by timestamp (newest first)
        sorted_suggestions = sorted(suggestions_list, key=lambda s: s.timestamp, reverse=True)
        
        return [s.dict() for s in sorted_suggestions]
    
    async def apply_suggestion(self, suggestion_id: str, result: Optional[str] = None) -> bool:
        """
        Mark an optimization suggestion as applied.
        
        Args:
            suggestion_id: The ID of the suggestion
            result: Optional result of applying the suggestion
            
        Returns:
            True if the suggestion was found and marked as applied, False otherwise
        """
        # Find the suggestion
        for suggestions_list in self.optimization_suggestions.values():
            for suggestion in suggestions_list:
                if suggestion.id == suggestion_id:
                    # Mark as applied
                    suggestion.applied = True
                    suggestion.applied_at = datetime.now()
                    suggestion.result = result or "Applied manually"
                    
                    logger.info(f"Marked optimization suggestion {suggestion_id} as applied")
                    
                    # Notify callback
                    if self.on_suggestion_applied:
                        self.on_suggestion_applied(suggestion)
                    
                    return True
        
        logger.warning(f"Attempted to mark unknown optimization suggestion {suggestion_id} as applied")
        return False
    
    async def update_optimization_config(self, config: Dict[str, Any]) -> bool:
        """
        Update the optimization configuration.
        
        Args:
            config: The new configuration parameters
            
        Returns:
            True if the configuration was updated successfully, False otherwise
        """
        try:
            # Update configuration
            for key, value in config.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
            
            logger.info(f"Updated optimization configuration: {config}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to update optimization configuration: {e}")
            return False
    
    async def execute(self, context: AgentContext) -> AgentResult:
        """
        Execute the agent's main functionality.
        
        Args:
            context: The execution context for the agent
            
        Returns:
            The result of the agent execution
        """
        # Extract parameters from context
        action = context.variables.get("action", "analyze_workflow")
        
        if action == "record_workflow_start":
            # Record workflow start
            workflow_id = context.variables.get("workflow_id")
            execution_id = context.variables.get("execution_id")
            metadata = context.variables.get("metadata")
            
            if not workflow_id or not execution_id:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="workflow_id and execution_id are required for record_workflow_start action"
                )
            
            execution_id = await self.record_workflow_start(workflow_id, execution_id, metadata)
            
            return AgentResult(
                success=True,
                message=f"Recorded start of workflow {workflow_id}, execution {execution_id}",
                data={"execution_id": execution_id}
            )
        
        elif action == "record_workflow_completion":
            # Record workflow completion
            workflow_id = context.variables.get("workflow_id")
            execution_id = context.variables.get("execution_id")
            success = context.variables.get("success", True)
            metadata = context.variables.get("metadata")
            
            if not workflow_id or not execution_id:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="workflow_id and execution_id are required for record_workflow_completion action"
                )
            
            result = await self.record_workflow_completion(workflow_id, execution_id, success, metadata)
            
            if result:
                return AgentResult(
                    success=True,
                    message=f"Recorded completion of workflow {workflow_id}, execution {execution_id}, success: {success}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to record completion of workflow {workflow_id}, execution {execution_id}",
                    error=f"Execution {execution_id} not found"
                )
        
        elif action == "record_task_metrics":
            # Record task metrics
            workflow_id = context.variables.get("workflow_id")
            execution_id = context.variables.get("execution_id")
            task_id = context.variables.get("task_id")
            metrics = context.variables.get("metrics")
            
            if not workflow_id or not execution_id or not task_id or not metrics:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="workflow_id, execution_id, task_id, and metrics are required for record_task_metrics action"
                )
            
            result = await self.record_task_metrics(workflow_id, execution_id, task_id, metrics)
            
            if result:
                return AgentResult(
                    success=True,
                    message=f"Recorded metrics for task {task_id} in workflow {workflow_id}, execution {execution_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to record metrics for task {task_id} in workflow {workflow_id}, execution {execution_id}",
                    error=f"Execution {execution_id} not found"
                )
        
        elif action == "record_resource_usage":
            # Record resource usage
            workflow_id = context.variables.get("workflow_id")
            execution_id = context.variables.get("execution_id")
            resource_usage = context.variables.get("resource_usage")
            
            if not workflow_id or not execution_id or not resource_usage:
                return AgentResult(
                    success=False,
                    message="Missing required parameters",
                    error="workflow_id, execution_id, and resource_usage are required for record_resource_usage action"
                )
            
            result = await self.record_resource_usage(workflow_id, execution_id, resource_usage)
            
            if result:
                return AgentResult(
                    success=True,
                    message=f"Recorded resource usage for workflow {workflow_id}, execution {execution_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to record resource usage for workflow {workflow_id}, execution {execution_id}",
                    error=f"Execution {execution_id} not found"
                )
        
        elif action == "get_workflow_metrics":
            # Get workflow metrics
            workflow_id = context.variables.get("workflow_id")
            limit = context.variables.get("limit", 10)
            
            if not workflow_id:
                return AgentResult(
                    success=False,
                    message="Missing workflow ID",
                    error="workflow_id is required for get_workflow_metrics action"
                )
            
            metrics = await self.get_workflow_metrics(workflow_id, limit)
            
            return AgentResult(
                success=True,
                message=f"Retrieved {len(metrics)} metrics for workflow {workflow_id}",
                data={"metrics": metrics}
            )
        
        elif action == "get_optimization_suggestions":
            # Get optimization suggestions
            workflow_id = context.variables.get("workflow_id")
            include_applied = context.variables.get("include_applied", True)
            
            if not workflow_id:
                return AgentResult(
                    success=False,
                    message="Missing workflow ID",
                    error="workflow_id is required for get_optimization_suggestions action"
                )
            
            suggestions = await self.get_optimization_suggestions(workflow_id, include_applied)
            
            return AgentResult(
                success=True,
                message=f"Retrieved {len(suggestions)} optimization suggestions for workflow {workflow_id}",
                data={"suggestions": suggestions}
            )
        
        elif action == "apply_suggestion":
            # Apply optimization suggestion
            suggestion_id = context.variables.get("suggestion_id")
            result = context.variables.get("result")
            
            if not suggestion_id:
                return AgentResult(
                    success=False,
                    message="Missing suggestion ID",
                    error="suggestion_id is required for apply_suggestion action"
                )
            
            success = await self.apply_suggestion(suggestion_id, result)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Applied optimization suggestion {suggestion_id}"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to apply optimization suggestion {suggestion_id}",
                    error=f"Suggestion {suggestion_id} not found"
                )
        
        elif action == "update_optimization_config":
            # Update optimization configuration
            config = context.variables.get("config")
            
            if not config:
                return AgentResult(
                    success=False,
                    message="Missing configuration",
                    error="config is required for update_optimization_config action"
                )
            
            success = await self.update_optimization_config(config)
            
            if success:
                return AgentResult(
                    success=True,
                    message=f"Updated optimization configuration"
                )
            else:
                return AgentResult(
                    success=False,
                    message=f"Failed to update optimization configuration",
                    error="Invalid configuration"
                )
        
        else:
            # Unknown action
            return AgentResult(
                success=False,
                message=f"Unknown action: {action}",
                error=f"Action {action} is not supported"
            )
