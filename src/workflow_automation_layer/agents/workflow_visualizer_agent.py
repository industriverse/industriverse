"""
Workflow Visualizer Agent Module for the Workflow Automation Layer.

This agent generates visual representations of workflows, their execution status,
and performance metrics for monitoring and analysis purposes.
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


class WorkflowVisualizerAgent:
    """Agent for visualizing workflows and their execution."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow visualizer agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "workflow-visualizer-agent"
        self.agent_capabilities = ["workflow_visualization", "execution_tracking", "performance_visualization"]
        self.supported_protocols = ["MCP", "A2A"]
        self.visualization_cache = {}  # Cache for generated visualizations
        self.active_visualizations = {}  # Currently active visualizations
        self.visualization_types = [
            "workflow_graph",
            "execution_timeline",
            "performance_heatmap",
            "agent_network",
            "task_dependencies",
            "resource_utilization",
            "trust_scores",
            "debug_trace"
        ]
        
        logger.info("Workflow Visualizer Agent initialized")

    async def generate_visualization(self, visualization_request: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a visualization for a workflow.

        Args:
            visualization_request: Request data including workflow_id, visualization_type, etc.

        Returns:
            Dict containing visualization data.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "visualization_type"]
            for field in required_fields:
                if field not in visualization_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = visualization_request["workflow_id"]
            visualization_type = visualization_request["visualization_type"]
            
            # Validate visualization type
            if visualization_type not in self.visualization_types:
                return {
                    "success": False,
                    "error": f"Invalid visualization type: {visualization_type}. Must be one of {self.visualization_types}"
                }
            
            # Generate visualization ID
            visualization_id = str(uuid.uuid4())
            
            # Get workflow data
            workflow_manifest = await self.workflow_runtime.get_workflow_manifest(workflow_id)
            if not workflow_manifest:
                return {
                    "success": False,
                    "error": f"Workflow manifest not found for workflow {workflow_id}"
                }
            
            # Get workflow execution data
            execution_data = await self.workflow_runtime.get_workflow_execution_data(workflow_id)
            
            # Generate visualization based on type
            visualization_data = await self._generate_visualization_data(
                workflow_id, visualization_type, workflow_manifest, execution_data, visualization_request
            )
            
            if not visualization_data["success"]:
                return visualization_data
            
            # Store in cache
            self.visualization_cache[visualization_id] = {
                "workflow_id": workflow_id,
                "visualization_type": visualization_type,
                "timestamp": datetime.utcnow().isoformat(),
                "data": visualization_data["data"]
            }
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "generate_visualization",
                "reason": f"Generated {visualization_type} visualization for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Generated {visualization_type} visualization for workflow {workflow_id}")
            
            return {
                "success": True,
                "visualization_id": visualization_id,
                "workflow_id": workflow_id,
                "visualization_type": visualization_type,
                "data": visualization_data["data"]
            }
            
        except Exception as e:
            logger.error(f"Error generating visualization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_visualization_data(
        self, 
        workflow_id: str, 
        visualization_type: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate visualization data based on type.

        Args:
            workflow_id: ID of the workflow.
            visualization_type: Type of visualization to generate.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        try:
            if visualization_type == "workflow_graph":
                return await self._generate_workflow_graph(workflow_id, workflow_manifest, execution_data, request_params)
            elif visualization_type == "execution_timeline":
                return await self._generate_execution_timeline(workflow_id, workflow_manifest, execution_data, request_params)
            elif visualization_type == "performance_heatmap":
                return await self._generate_performance_heatmap(workflow_id, workflow_manifest, execution_data, request_params)
            elif visualization_type == "agent_network":
                return await self._generate_agent_network(workflow_id, workflow_manifest, execution_data, request_params)
            elif visualization_type == "task_dependencies":
                return await self._generate_task_dependencies(workflow_id, workflow_manifest, execution_data, request_params)
            elif visualization_type == "resource_utilization":
                return await self._generate_resource_utilization(workflow_id, workflow_manifest, execution_data, request_params)
            elif visualization_type == "trust_scores":
                return await self._generate_trust_scores(workflow_id, workflow_manifest, execution_data, request_params)
            elif visualization_type == "debug_trace":
                return await self._generate_debug_trace(workflow_id, workflow_manifest, execution_data, request_params)
            else:
                return {
                    "success": False,
                    "error": f"Visualization type {visualization_type} not implemented"
                }
        except Exception as e:
            logger.error(f"Error generating {visualization_type} visualization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _generate_workflow_graph(
        self, 
        workflow_id: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate workflow graph visualization.

        Args:
            workflow_id: ID of the workflow.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        # Extract tasks from manifest
        tasks = workflow_manifest.get("tasks", [])
        
        # Extract task status from execution data
        task_status = {}
        for task_execution in execution_data.get("task_executions", []):
            task_id = task_execution.get("task_id")
            if task_id:
                task_status[task_id] = task_execution.get("status", "unknown")
        
        # Create nodes for tasks
        nodes = []
        for task in tasks:
            task_id = task.get("task_id")
            if not task_id:
                continue
                
            status = task_status.get(task_id, "pending")
            
            nodes.append({
                "id": task_id,
                "label": task.get("name", task_id),
                "type": task.get("task_type", "default"),
                "status": status,
                "agent_id": task.get("agent_id"),
                "position": task.get("position", {"x": 0, "y": 0})
            })
        
        # Create edges for task dependencies
        edges = []
        for task in tasks:
            task_id = task.get("task_id")
            dependencies = task.get("dependencies", [])
            
            for dep_id in dependencies:
                edges.append({
                    "source": dep_id,
                    "target": task_id,
                    "label": ""
                })
        
        # Create visualization data
        visualization_data = {
            "type": "workflow_graph",
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_manifest.get("name", "Unnamed Workflow"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": visualization_data
        }

    async def _generate_execution_timeline(
        self, 
        workflow_id: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate execution timeline visualization.

        Args:
            workflow_id: ID of the workflow.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        # Extract task executions
        task_executions = execution_data.get("task_executions", [])
        
        # Create timeline events
        events = []
        for execution in task_executions:
            task_id = execution.get("task_id")
            if not task_id:
                continue
                
            start_time = execution.get("start_time")
            end_time = execution.get("end_time")
            status = execution.get("status", "unknown")
            
            if start_time:
                events.append({
                    "task_id": task_id,
                    "event_type": "start",
                    "timestamp": start_time,
                    "status": "started"
                })
            
            if end_time:
                events.append({
                    "task_id": task_id,
                    "event_type": "end",
                    "timestamp": end_time,
                    "status": status
                })
            
            # Add intermediate events if available
            for event in execution.get("events", []):
                events.append({
                    "task_id": task_id,
                    "event_type": event.get("type", "unknown"),
                    "timestamp": event.get("timestamp"),
                    "status": event.get("status", "unknown"),
                    "details": event.get("details", {})
                })
        
        # Sort events by timestamp
        events.sort(key=lambda x: x.get("timestamp", ""))
        
        # Create task lanes
        task_ids = set(execution.get("task_id") for execution in task_executions if execution.get("task_id"))
        lanes = []
        
        for task_id in task_ids:
            # Find task details in manifest
            task_details = next((t for t in workflow_manifest.get("tasks", []) if t.get("task_id") == task_id), {})
            
            lanes.append({
                "id": task_id,
                "label": task_details.get("name", task_id),
                "type": task_details.get("task_type", "default")
            })
        
        # Create visualization data
        visualization_data = {
            "type": "execution_timeline",
            "lanes": lanes,
            "events": events,
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_manifest.get("name", "Unnamed Workflow"),
                "start_time": execution_data.get("start_time"),
                "end_time": execution_data.get("end_time"),
                "status": execution_data.get("status", "unknown"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": visualization_data
        }

    async def _generate_performance_heatmap(
        self, 
        workflow_id: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate performance heatmap visualization.

        Args:
            workflow_id: ID of the workflow.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        # Extract task executions
        task_executions = execution_data.get("task_executions", [])
        
        # Calculate performance metrics for each task
        task_metrics = {}
        for execution in task_executions:
            task_id = execution.get("task_id")
            if not task_id:
                continue
                
            # Calculate execution time
            start_time = execution.get("start_time")
            end_time = execution.get("end_time")
            
            if start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = datetime.fromisoformat(end_time)
                    execution_time = (end_dt - start_dt).total_seconds() * 1000  # in milliseconds
                except (ValueError, TypeError):
                    execution_time = None
            else:
                execution_time = None
            
            # Get other metrics
            metrics = execution.get("metrics", {})
            
            task_metrics[task_id] = {
                "execution_time": execution_time,
                "memory_usage": metrics.get("memory_usage"),
                "cpu_usage": metrics.get("cpu_usage"),
                "error_count": metrics.get("error_count", 0),
                "retry_count": metrics.get("retry_count", 0)
            }
        
        # Create heatmap cells
        cells = []
        for task_id, metrics in task_metrics.items():
            # Find task details in manifest
            task_details = next((t for t in workflow_manifest.get("tasks", []) if t.get("task_id") == task_id), {})
            
            # Calculate performance score (normalized between 0 and 1, higher is worse)
            # This is a simplified calculation, would be more sophisticated in a real implementation
            score = 0
            factors = 0
            
            if metrics["execution_time"] is not None:
                # Normalize execution time (assuming 5000ms is the worst case)
                normalized_time = min(metrics["execution_time"] / 5000, 1)
                score += normalized_time
                factors += 1
            
            if metrics["memory_usage"] is not None:
                # Normalize memory usage (assuming 1GB is the worst case)
                normalized_memory = min(metrics["memory_usage"] / 1024, 1)
                score += normalized_memory
                factors += 1
            
            if metrics["cpu_usage"] is not None:
                # Normalize CPU usage (already between 0 and 1)
                score += metrics["cpu_usage"]
                factors += 1
            
            # Add penalty for errors and retries
            error_penalty = min(metrics["error_count"] * 0.2, 0.6)
            retry_penalty = min(metrics["retry_count"] * 0.1, 0.3)
            
            if metrics["error_count"] > 0:
                score += error_penalty
                factors += 1
            
            if metrics["retry_count"] > 0:
                score += retry_penalty
                factors += 1
            
            # Calculate final score
            if factors > 0:
                final_score = score / factors
            else:
                final_score = 0
            
            cells.append({
                "id": task_id,
                "label": task_details.get("name", task_id),
                "type": task_details.get("task_type", "default"),
                "score": final_score,
                "metrics": metrics,
                "position": task_details.get("position", {"x": 0, "y": 0})
            })
        
        # Create visualization data
        visualization_data = {
            "type": "performance_heatmap",
            "cells": cells,
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_manifest.get("name", "Unnamed Workflow"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": visualization_data
        }

    async def _generate_agent_network(
        self, 
        workflow_id: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate agent network visualization.

        Args:
            workflow_id: ID of the workflow.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        # Get agent mesh topology from workflow manifest
        agent_mesh_topology = workflow_manifest.get("agent_mesh_topology", {})
        
        # Get agents involved in workflow
        workflow_agents = await self.workflow_runtime.get_workflow_agents(workflow_id)
        
        # Create nodes for agents
        nodes = []
        for agent_id, agent_info in workflow_agents.items():
            nodes.append({
                "id": agent_id,
                "label": agent_info.get("name", agent_id),
                "type": agent_info.get("type", "default"),
                "capabilities": agent_info.get("capabilities", []),
                "status": agent_info.get("status", "unknown"),
                "location": agent_info.get("location", "cloud"),
                "position": agent_info.get("position", {"x": 0, "y": 0})
            })
        
        # Create edges for agent connections
        edges = []
        
        # Add edges from mesh topology
        for connection in agent_mesh_topology.get("connections", []):
            source = connection.get("source")
            target = connection.get("target")
            
            if source and target:
                edges.append({
                    "source": source,
                    "target": target,
                    "label": connection.get("type", ""),
                    "strength": connection.get("strength", 1),
                    "trust_score": connection.get("trust_score", 0.7)
                })
        
        # Add edges from message exchanges in execution data
        for message in execution_data.get("messages", []):
            source = message.get("source_agent")
            target = message.get("target_agent")
            
            if source and target:
                # Check if edge already exists
                existing_edge = next((e for e in edges if e["source"] == source and e["target"] == target), None)
                
                if existing_edge:
                    # Increment message count
                    if "message_count" not in existing_edge:
                        existing_edge["message_count"] = 1
                    else:
                        existing_edge["message_count"] += 1
                else:
                    # Create new edge
                    edges.append({
                        "source": source,
                        "target": target,
                        "label": "message",
                        "message_count": 1,
                        "message_types": [message.get("message_type", "unknown")]
                    })
        
        # Create visualization data
        visualization_data = {
            "type": "agent_network",
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_manifest.get("name", "Unnamed Workflow"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": visualization_data
        }

    async def _generate_task_dependencies(
        self, 
        workflow_id: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate task dependencies visualization.

        Args:
            workflow_id: ID of the workflow.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        # Extract tasks from manifest
        tasks = workflow_manifest.get("tasks", [])
        
        # Extract task status from execution data
        task_status = {}
        task_timing = {}
        
        for task_execution in execution_data.get("task_executions", []):
            task_id = task_execution.get("task_id")
            if task_id:
                task_status[task_id] = task_execution.get("status", "unknown")
                
                # Calculate timing
                start_time = task_execution.get("start_time")
                end_time = task_execution.get("end_time")
                
                if start_time and end_time:
                    try:
                        start_dt = datetime.fromisoformat(start_time)
                        end_dt = datetime.fromisoformat(end_time)
                        execution_time = (end_dt - start_dt).total_seconds() * 1000  # in milliseconds
                        task_timing[task_id] = execution_time
                    except (ValueError, TypeError):
                        pass
        
        # Create nodes for tasks
        nodes = []
        for task in tasks:
            task_id = task.get("task_id")
            if not task_id:
                continue
                
            status = task_status.get(task_id, "pending")
            execution_time = task_timing.get(task_id)
            
            nodes.append({
                "id": task_id,
                "label": task.get("name", task_id),
                "type": task.get("task_type", "default"),
                "status": status,
                "execution_time": execution_time,
                "agent_id": task.get("agent_id"),
                "position": task.get("position", {"x": 0, "y": 0})
            })
        
        # Create edges for task dependencies
        edges = []
        for task in tasks:
            task_id = task.get("task_id")
            dependencies = task.get("dependencies", [])
            
            for dep_id in dependencies:
                # Check if dependency was critical path
                is_critical = False
                
                # In a real implementation, this would use more sophisticated critical path analysis
                # For now, we'll use a simple heuristic: if both tasks have timing data and the dependency
                # took a significant portion of the total time, consider it critical
                if task_id in task_timing and dep_id in task_timing:
                    if task_timing[dep_id] > 0.5 * task_timing[task_id]:
                        is_critical = True
                
                edges.append({
                    "source": dep_id,
                    "target": task_id,
                    "label": "",
                    "is_critical": is_critical
                })
        
        # Create visualization data
        visualization_data = {
            "type": "task_dependencies",
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_manifest.get("name", "Unnamed Workflow"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": visualization_data
        }

    async def _generate_resource_utilization(
        self, 
        workflow_id: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate resource utilization visualization.

        Args:
            workflow_id: ID of the workflow.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        # Extract resource metrics from execution data
        resource_metrics = execution_data.get("resource_metrics", [])
        
        # Group metrics by resource type and timestamp
        metrics_by_type = {}
        
        for metric in resource_metrics:
            resource_type = metric.get("resource_type", "unknown")
            timestamp = metric.get("timestamp")
            value = metric.get("value")
            
            if not timestamp or value is None:
                continue
                
            if resource_type not in metrics_by_type:
                metrics_by_type[resource_type] = []
            
            metrics_by_type[resource_type].append({
                "timestamp": timestamp,
                "value": value,
                "agent_id": metric.get("agent_id"),
                "task_id": metric.get("task_id")
            })
        
        # Sort metrics by timestamp
        for resource_type, metrics in metrics_by_type.items():
            metrics.sort(key=lambda x: x["timestamp"])
        
        # Create visualization data
        visualization_data = {
            "type": "resource_utilization",
            "resource_types": list(metrics_by_type.keys()),
            "metrics": metrics_by_type,
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_manifest.get("name", "Unnamed Workflow"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": visualization_data
        }

    async def _generate_trust_scores(
        self, 
        workflow_id: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate trust scores visualization.

        Args:
            workflow_id: ID of the workflow.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        # Get agent mesh topology from workflow manifest
        agent_mesh_topology = workflow_manifest.get("agent_mesh_topology", {})
        
        # Get trust scores from execution data
        trust_scores = execution_data.get("trust_scores", [])
        
        # Group trust scores by agent
        scores_by_agent = {}
        
        for score in trust_scores:
            agent_id = score.get("agent_id")
            timestamp = score.get("timestamp")
            value = score.get("value")
            
            if not agent_id or not timestamp or value is None:
                continue
                
            if agent_id not in scores_by_agent:
                scores_by_agent[agent_id] = []
            
            scores_by_agent[agent_id].append({
                "timestamp": timestamp,
                "value": value,
                "reason": score.get("reason"),
                "evaluator": score.get("evaluator")
            })
        
        # Sort scores by timestamp
        for agent_id, scores in scores_by_agent.items():
            scores.sort(key=lambda x: x["timestamp"])
        
        # Calculate current trust score for each agent
        current_scores = {}
        for agent_id, scores in scores_by_agent.items():
            if scores:
                current_scores[agent_id] = scores[-1]["value"]
        
        # Create nodes for agents
        nodes = []
        for agent_id, agent_info in agent_mesh_topology.get("agents", {}).items():
            trust_score = current_scores.get(agent_id, agent_info.get("initial_trust", 0.7))
            
            nodes.append({
                "id": agent_id,
                "label": agent_info.get("name", agent_id),
                "type": agent_info.get("type", "default"),
                "trust_score": trust_score,
                "position": agent_info.get("position", {"x": 0, "y": 0})
            })
        
        # Create edges for trust relationships
        edges = []
        for connection in agent_mesh_topology.get("connections", []):
            source = connection.get("source")
            target = connection.get("target")
            
            if source and target:
                # Get trust score for this connection
                trust_score = connection.get("trust_score", 0.7)
                
                # Check if there's an updated score in execution data
                for score in trust_scores:
                    if score.get("source_agent") == source and score.get("target_agent") == target:
                        trust_score = score.get("value", trust_score)
                
                edges.append({
                    "source": source,
                    "target": target,
                    "trust_score": trust_score
                })
        
        # Create visualization data
        visualization_data = {
            "type": "trust_scores",
            "nodes": nodes,
            "edges": edges,
            "trust_history": scores_by_agent,
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_manifest.get("name", "Unnamed Workflow"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": visualization_data
        }

    async def _generate_debug_trace(
        self, 
        workflow_id: str, 
        workflow_manifest: Dict[str, Any],
        execution_data: Dict[str, Any],
        request_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate debug trace visualization.

        Args:
            workflow_id: ID of the workflow.
            workflow_manifest: Workflow manifest data.
            execution_data: Workflow execution data.
            request_params: Additional request parameters.

        Returns:
            Dict containing visualization data.
        """
        # Get debug traces from execution data
        debug_traces = execution_data.get("debug_traces", [])
        
        # Get capsule debug trace manager
        capsule_debug_trace_manager = self.workflow_runtime.get_capsule_debug_trace_manager()
        
        # Get detailed trace data if available
        detailed_traces = []
        if capsule_debug_trace_manager:
            for trace in debug_traces:
                trace_id = trace.get("trace_id")
                if trace_id:
                    detailed_trace = await capsule_debug_trace_manager.get_trace(trace_id)
                    if detailed_trace:
                        detailed_traces.append(detailed_trace)
        
        # Create trace events
        events = []
        for trace in detailed_traces:
            for event in trace.get("events", []):
                events.append({
                    "trace_id": trace.get("trace_id"),
                    "timestamp": event.get("timestamp"),
                    "agent_id": event.get("agent_id"),
                    "task_id": event.get("task_id"),
                    "event_type": event.get("type"),
                    "level": event.get("level", "info"),
                    "message": event.get("message"),
                    "details": event.get("details", {})
                })
        
        # Sort events by timestamp
        events.sort(key=lambda x: x.get("timestamp", ""))
        
        # Group events by trace ID
        events_by_trace = {}
        for event in events:
            trace_id = event.get("trace_id")
            if trace_id:
                if trace_id not in events_by_trace:
                    events_by_trace[trace_id] = []
                events_by_trace[trace_id].append(event)
        
        # Create visualization data
        visualization_data = {
            "type": "debug_trace",
            "traces": detailed_traces,
            "events": events,
            "events_by_trace": events_by_trace,
            "metadata": {
                "workflow_id": workflow_id,
                "workflow_name": workflow_manifest.get("name", "Unnamed Workflow"),
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
        return {
            "success": True,
            "data": visualization_data
        }

    async def start_live_visualization(self, visualization_request: Dict[str, Any]) -> Dict[str, Any]:
        """Start a live visualization for a workflow.

        Args:
            visualization_request: Request data including workflow_id, visualization_type, etc.

        Returns:
            Dict containing live visualization status.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "visualization_type"]
            for field in required_fields:
                if field not in visualization_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = visualization_request["workflow_id"]
            visualization_type = visualization_request["visualization_type"]
            
            # Validate visualization type
            if visualization_type not in self.visualization_types:
                return {
                    "success": False,
                    "error": f"Invalid visualization type: {visualization_type}. Must be one of {self.visualization_types}"
                }
            
            # Generate visualization ID
            visualization_id = str(uuid.uuid4())
            
            # Store live visualization details
            self.active_visualizations[visualization_id] = {
                "workflow_id": workflow_id,
                "visualization_type": visualization_type,
                "start_time": datetime.utcnow().isoformat(),
                "status": "active",
                "update_interval": visualization_request.get("update_interval", 5),  # seconds
                "last_update": None,
                "data": None
            }
            
            # Start background task to update visualization
            asyncio.create_task(self._update_live_visualization(visualization_id))
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "start_live_visualization",
                "reason": f"Started live {visualization_type} visualization for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Started live {visualization_type} visualization for workflow {workflow_id}")
            
            return {
                "success": True,
                "visualization_id": visualization_id,
                "workflow_id": workflow_id,
                "visualization_type": visualization_type,
                "status": "active"
            }
            
        except Exception as e:
            logger.error(f"Error starting live visualization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _update_live_visualization(self, visualization_id: str):
        """Update a live visualization in the background.

        Args:
            visualization_id: ID of the visualization to update.
        """
        if visualization_id not in self.active_visualizations:
            logger.error(f"Visualization {visualization_id} not found")
            return
        
        visualization = self.active_visualizations[visualization_id]
        workflow_id = visualization["workflow_id"]
        visualization_type = visualization["visualization_type"]
        update_interval = visualization["update_interval"]
        
        logger.info(f"Starting live visualization updates for {visualization_id}")
        
        while visualization_id in self.active_visualizations and self.active_visualizations[visualization_id]["status"] == "active":
            try:
                # Get workflow data
                workflow_manifest = await self.workflow_runtime.get_workflow_manifest(workflow_id)
                if not workflow_manifest:
                    logger.error(f"Workflow manifest not found for workflow {workflow_id}")
                    break
                
                # Get workflow execution data
                execution_data = await self.workflow_runtime.get_workflow_execution_data(workflow_id)
                
                # Generate visualization
                visualization_data = await self._generate_visualization_data(
                    workflow_id, visualization_type, workflow_manifest, execution_data, {}
                )
                
                if visualization_data["success"]:
                    # Update visualization
                    self.active_visualizations[visualization_id]["data"] = visualization_data["data"]
                    self.active_visualizations[visualization_id]["last_update"] = datetime.utcnow().isoformat()
                else:
                    logger.error(f"Error updating visualization {visualization_id}: {visualization_data.get('error')}")
                
                # Wait for next update
                await asyncio.sleep(update_interval)
                
            except Exception as e:
                logger.error(f"Error in live visualization update: {str(e)}")
                await asyncio.sleep(update_interval)
        
        logger.info(f"Stopped live visualization updates for {visualization_id}")

    async def stop_live_visualization(self, visualization_id: str) -> Dict[str, Any]:
        """Stop a live visualization.

        Args:
            visualization_id: ID of the visualization to stop.

        Returns:
            Dict containing stop status.
        """
        try:
            # Check if visualization exists and is active
            if visualization_id not in self.active_visualizations:
                return {
                    "success": False,
                    "error": f"Visualization {visualization_id} not found"
                }
            
            visualization = self.active_visualizations[visualization_id]
            workflow_id = visualization["workflow_id"]
            
            # Mark visualization as stopped
            visualization["status"] = "stopped"
            visualization["end_time"] = datetime.utcnow().isoformat()
            
            # Move to cache
            self.visualization_cache[visualization_id] = visualization
            del self.active_visualizations[visualization_id]
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "stop_live_visualization",
                "reason": f"Stopped live visualization {visualization_id} for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Stopped live visualization {visualization_id}")
            
            return {
                "success": True,
                "visualization_id": visualization_id,
                "status": "stopped"
            }
            
        except Exception as e:
            logger.error(f"Error stopping live visualization: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def get_visualization(self, visualization_id: str) -> Dict[str, Any]:
        """Get a visualization by ID.

        Args:
            visualization_id: ID of the visualization.

        Returns:
            Dict containing visualization data.
        """
        # Check active visualizations
        if visualization_id in self.active_visualizations:
            visualization = self.active_visualizations[visualization_id]
            return {
                "success": True,
                "visualization_id": visualization_id,
                "workflow_id": visualization["workflow_id"],
                "visualization_type": visualization["visualization_type"],
                "status": "active",
                "last_update": visualization["last_update"],
                "data": visualization["data"]
            }
        
        # Check visualization cache
        if visualization_id in self.visualization_cache:
            visualization = self.visualization_cache[visualization_id]
            return {
                "success": True,
                "visualization_id": visualization_id,
                "workflow_id": visualization["workflow_id"],
                "visualization_type": visualization["visualization_type"],
                "timestamp": visualization["timestamp"],
                "status": "cached",
                "data": visualization["data"]
            }
        
        return {
            "success": False,
            "error": f"Visualization {visualization_id} not found"
        }

    async def get_visualizations(self, workflow_id: str = None) -> Dict[str, Any]:
        """Get all visualizations, optionally filtered by workflow ID.

        Args:
            workflow_id: Optional ID of workflow to filter by.

        Returns:
            Dict containing visualization list.
        """
        # Filter active visualizations
        active_visualizations = {}
        for viz_id, viz in self.active_visualizations.items():
            if workflow_id is None or viz["workflow_id"] == workflow_id:
                active_visualizations[viz_id] = {
                    "workflow_id": viz["workflow_id"],
                    "visualization_type": viz["visualization_type"],
                    "start_time": viz["start_time"],
                    "status": "active",
                    "last_update": viz["last_update"]
                }
        
        # Filter cached visualizations
        cached_visualizations = {}
        for viz_id, viz in self.visualization_cache.items():
            if workflow_id is None or viz["workflow_id"] == workflow_id:
                cached_visualizations[viz_id] = {
                    "workflow_id": viz["workflow_id"],
                    "visualization_type": viz["visualization_type"],
                    "timestamp": viz["timestamp"],
                    "status": "cached"
                }
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "active_count": len(active_visualizations),
            "cached_count": len(cached_visualizations),
            "active_visualizations": active_visualizations,
            "cached_visualizations": cached_visualizations
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
            "supported_protocols": self.supported_protocols],
            "resilience_mode": "quorum_vote",
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["visualization_node", "live_visualization_node"]
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
            
            if message_type == "generate_visualization":
                return await self.generate_visualization(message.get("payload", {}))
            elif message_type == "start_live_visualization":
                return await self.start_live_visualization(message.get("payload", {}))
            elif message_type == "stop_live_visualization":
                payload = message.get("payload", {})
                visualization_id = payload.get("visualization_id")
                return await self.stop_live_visualization(visualization_id)
            elif message_type == "get_visualization":
                payload = message.get("payload", {})
                visualization_id = payload.get("visualization_id")
                return await self.get_visualization(visualization_id)
            elif message_type == "get_visualizations":
                payload = message.get("payload", {})
                workflow_id = payload.get("workflow_id")
                return await self.get_visualizations(workflow_id)
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
