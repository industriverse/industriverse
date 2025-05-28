"""
Workflow Forensics Agent Module for the Workflow Automation Layer.

This agent analyzes workflow execution data, debug traces, and telemetry
to identify anomalies, diagnose failures, and generate forensic reports.
It leverages the Capsule Debug Trace system for detailed analysis.
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


class WorkflowForensicsAgent:
    """Agent for analyzing workflow execution and diagnosing issues."""

    def __init__(self, workflow_runtime):
        """Initialize the workflow forensics agent.

        Args:
            workflow_runtime: The workflow runtime instance.
        """
        self.workflow_runtime = workflow_runtime
        self.agent_id = "workflow-forensics-agent"
        self.agent_capabilities = ["forensic_analysis", "anomaly_detection", "failure_diagnosis", "report_generation"]
        self.supported_protocols = ["MCP", "A2A"]
        self.analysis_cache = {}  # Cache for completed analyses
        self.active_analyses = {}  # Store for ongoing analyses
        self.analysis_types = [
            "failure_root_cause",
            "performance_bottleneck",
            "anomaly_detection",
            "security_incident",
            "compliance_check",
            "optimization_potential"
        ]
        
        logger.info("Workflow Forensics Agent initialized")

    async def start_forensic_analysis(self, analysis_request: Dict[str, Any]) -> Dict[str, Any]:
        """Start a new forensic analysis process.

        Args:
            analysis_request: Request data including workflow_id, analysis_type, time_range, etc.

        Returns:
            Dict containing analysis start status.
        """
        try:
            # Validate required fields
            required_fields = ["workflow_id", "analysis_type"]
            for field in required_fields:
                if field not in analysis_request:
                    return {
                        "success": False,
                        "error": f"Missing required field: {field}"
                    }
            
            workflow_id = analysis_request["workflow_id"]
            analysis_type = analysis_request["analysis_type"]
            
            # Validate analysis type
            if analysis_type not in self.analysis_types:
                return {
                    "success": False,
                    "error": f"Invalid analysis type: {analysis_type}. Must be one of {self.analysis_types}"
                }
            
            # Generate analysis ID
            analysis_id = str(uuid.uuid4())
            
            # Store analysis details
            self.active_analyses[analysis_id] = {
                "workflow_id": workflow_id,
                "analysis_type": analysis_type,
                "parameters": analysis_request.get("parameters", {}),
                "start_time": datetime.utcnow().isoformat(),
                "status": "running",
                "progress": 0,
                "result": None
            }
            
            # Start analysis process in the background
            asyncio.create_task(self._run_analysis(analysis_id))
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "start_forensic_analysis",
                "reason": f"Started {analysis_type} analysis for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Started forensic analysis {analysis_id} for workflow {workflow_id}")
            
            return {
                "success": True,
                "analysis_id": analysis_id,
                "workflow_id": workflow_id,
                "status": "running"
            }
            
        except Exception as e:
            logger.error(f"Error starting forensic analysis: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    async def _run_analysis(self, analysis_id: str):
        """Run the forensic analysis process in the background.

        Args:
            analysis_id: ID of the analysis to run.
        """
        if analysis_id not in self.active_analyses:
            logger.error(f"Analysis {analysis_id} not found")
            return
        
        analysis = self.active_analyses[analysis_id]
        workflow_id = analysis["workflow_id"]
        analysis_type = analysis["analysis_type"]
        parameters = analysis["parameters"]
        
        logger.info(f"Running forensic analysis {analysis_id} ({analysis_type}) for workflow {workflow_id}")
        
        try:
            # Update progress
            analysis["progress"] = 10
            
            # Get required data
            execution_data = await self.workflow_runtime.get_workflow_execution_data(workflow_id)
            if not execution_data:
                raise ValueError(f"Execution data not found for workflow {workflow_id}")
            
            # Get debug traces if needed
            debug_traces = []
            if analysis_type in ["failure_root_cause", "anomaly_detection", "security_incident"]:
                capsule_debug_trace_manager = self.workflow_runtime.get_capsule_debug_trace_manager()
                if capsule_debug_trace_manager:
                    trace_ids = [t["trace_id"] for t in execution_data.get("debug_traces", []) if t.get("trace_id")]
                    for trace_id in trace_ids:
                        trace = await capsule_debug_trace_manager.get_trace(trace_id)
                        if trace:
                            debug_traces.append(trace)
            
            # Update progress
            analysis["progress"] = 30
            
            # Perform analysis based on type
            if analysis_type == "failure_root_cause":
                result = await self._analyze_failure_root_cause(workflow_id, execution_data, debug_traces, parameters)
            elif analysis_type == "performance_bottleneck":
                result = await self._analyze_performance_bottleneck(workflow_id, execution_data, parameters)
            elif analysis_type == "anomaly_detection":
                result = await self._analyze_anomaly_detection(workflow_id, execution_data, debug_traces, parameters)
            elif analysis_type == "security_incident":
                result = await self._analyze_security_incident(workflow_id, execution_data, debug_traces, parameters)
            elif analysis_type == "compliance_check":
                result = await self._analyze_compliance_check(workflow_id, execution_data, parameters)
            elif analysis_type == "optimization_potential":
                result = await self._analyze_optimization_potential(workflow_id, execution_data, parameters)
            else:
                raise ValueError(f"Analysis type {analysis_type} not implemented")
            
            # Update progress
            analysis["progress"] = 90
            
            # Store result
            analysis["result"] = result
            analysis["status"] = "completed"
            analysis["end_time"] = datetime.utcnow().isoformat()
            analysis["progress"] = 100
            
            # Generate agent reason log
            reason_log = {
                "agent_id": self.agent_id,
                "action": "analysis_completed",
                "reason": f"Completed {analysis_type} analysis for workflow {workflow_id}",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Add to workflow telemetry
            self.workflow_runtime.workflow_telemetry.add_agent_log(workflow_id, reason_log)
            
            logger.info(f"Forensic analysis {analysis_id} completed")
            
        except Exception as e:
            logger.error(f"Error during analysis {analysis_id}: {str(e)}")
            analysis["status"] = "failed"
            analysis["end_time"] = datetime.utcnow().isoformat()
            analysis["error"] = str(e)
        
        # Move to cache
        if analysis_id in self.active_analyses:
            self.analysis_cache[analysis_id] = self.active_analyses[analysis_id]
            del self.active_analyses[analysis_id]

    async def _analyze_failure_root_cause(
        self, 
        workflow_id: str, 
        execution_data: Dict[str, Any],
        debug_traces: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze root cause of a workflow failure.

        Args:
            workflow_id: ID of the workflow.
            execution_data: Workflow execution data.
            debug_traces: List of debug traces.
            parameters: Analysis parameters.

        Returns:
            Dict containing analysis result.
        """
        # Find failed tasks
        failed_tasks = [
            task for task in execution_data.get("task_executions", [])
            if task.get("status") == "failed"
        ]
        
        if not failed_tasks:
            return {
                "success": False,
                "error": "No failed tasks found in execution data"
            }
        
        # Analyze each failed task
        root_causes = []
        
        for task in failed_tasks:
            task_id = task.get("task_id")
            error_details = task.get("error_details", {})
            
            # Look for relevant debug trace events
            relevant_events = []
            for trace in debug_traces:
                for event in trace.get("events", []):
                    if event.get("task_id") == task_id and event.get("level") == "error":
                        relevant_events.append(event)
            
            # Simple root cause analysis (can be enhanced with ML/AI)
            cause = {
                "task_id": task_id,
                "error_message": error_details.get("message", "Unknown error"),
                "error_type": error_details.get("type", "Unknown"),
                "potential_causes": [],
                "trace_evidence": relevant_events
            }
            
            # Example potential causes based on error type
            if "TimeoutError" in cause["error_type"]:
                cause["potential_causes"].append("Network latency or unresponsive downstream service")
            elif "ResourceExhaustion" in cause["error_type"]:
                cause["potential_causes"].append("Insufficient resources (CPU, memory) allocated to the agent")
            elif "AuthenticationError" in cause["error_type"]:
                cause["potential_causes"].append("Invalid credentials or permissions issue")
            elif "DataCorruption" in cause["error_type"]:
                cause["potential_causes"].append("Corrupted input data or data transformation error")
            else:
                cause["potential_causes"].append("Application logic error or unexpected input")
            
            root_causes.append(cause)
        
        return {
            "success": True,
            "analysis_type": "failure_root_cause",
            "summary": f"Found {len(root_causes)} potential root causes for workflow failure.",
            "root_causes": root_causes
        }

    async def _analyze_performance_bottleneck(
        self, 
        workflow_id: str, 
        execution_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance bottlenecks in a workflow.

        Args:
            workflow_id: ID of the workflow.
            execution_data: Workflow execution data.
            parameters: Analysis parameters.

        Returns:
            Dict containing analysis result.
        """
        # Extract task executions
        task_executions = execution_data.get("task_executions", [])
        
        # Calculate execution times
        task_timings = {}
        for execution in task_executions:
            task_id = execution.get("task_id")
            start_time = execution.get("start_time")
            end_time = execution.get("end_time")
            
            if task_id and start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = datetime.fromisoformat(end_time)
                    execution_time = (end_dt - start_dt).total_seconds() * 1000  # in milliseconds
                    task_timings[task_id] = execution_time
                except (ValueError, TypeError):
                    pass
        
        if not task_timings:
            return {
                "success": False,
                "error": "No task timing data found"
            }
        
        # Identify tasks with longest execution times
        sorted_tasks = sorted(task_timings.items(), key=lambda item: item[1], reverse=True)
        
        # Define bottleneck threshold (e.g., top 10% or tasks taking > 1 second)
        threshold_percentile = parameters.get("threshold_percentile", 90)
        threshold_absolute_ms = parameters.get("threshold_absolute_ms", 1000)
        
        bottlenecks = []
        percentile_index = int(len(sorted_tasks) * (threshold_percentile / 100))
        
        for i, (task_id, duration) in enumerate(sorted_tasks):
            is_bottleneck = False
            if duration > threshold_absolute_ms:
                is_bottleneck = True
            elif i >= percentile_index:
                is_bottleneck = True
            
            if is_bottleneck:
                # Get task details
                task_details = next((t for t in execution_data.get("task_executions", []) if t.get("task_id") == task_id), {})
                
                bottlenecks.append({
                    "task_id": task_id,
                    "duration_ms": duration,
                    "agent_id": task_details.get("agent_id"),
                    "metrics": task_details.get("metrics", {})
                })
        
        return {
            "success": True,
            "analysis_type": "performance_bottleneck",
            "summary": f"Identified {len(bottlenecks)} potential performance bottlenecks.",
            "bottlenecks": bottlenecks,
            "all_task_timings": task_timings
        }

    async def _analyze_anomaly_detection(
        self, 
        workflow_id: str, 
        execution_data: Dict[str, Any],
        debug_traces: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect anomalies in workflow execution.

        Args:
            workflow_id: ID of the workflow.
            execution_data: Workflow execution data.
            debug_traces: List of debug traces.
            parameters: Analysis parameters.

        Returns:
            Dict containing analysis result.
        """
        # This is a placeholder for a more sophisticated anomaly detection system
        # (e.g., using statistical methods, ML models on telemetry data)
        
        anomalies = []
        
        # Example: Detect unusually long task durations
        task_timings = {}
        for execution in execution_data.get("task_executions", []):
            task_id = execution.get("task_id")
            start_time = execution.get("start_time")
            end_time = execution.get("end_time")
            
            if task_id and start_time and end_time:
                try:
                    start_dt = datetime.fromisoformat(start_time)
                    end_dt = datetime.fromisoformat(end_time)
                    execution_time = (end_dt - start_dt).total_seconds() * 1000
                    task_timings[task_id] = execution_time
                except (ValueError, TypeError):
                    pass
        
        # Compare with historical averages (assuming we have them)
        historical_averages = parameters.get("historical_averages", {})
        duration_threshold_factor = parameters.get("duration_threshold_factor", 3)
        
        for task_id, duration in task_timings.items():
            if task_id in historical_averages:
                avg_duration = historical_averages[task_id]
                if duration > avg_duration * duration_threshold_factor:
                    anomalies.append({
                        "type": "long_duration",
                        "task_id": task_id,
                        "current_duration_ms": duration,
                        "average_duration_ms": avg_duration,
                        "timestamp": datetime.utcnow().isoformat()
                    })
        
        # Example: Detect unexpected error messages in debug traces
        unexpected_error_keywords = parameters.get("unexpected_error_keywords", ["panic", "fatal", "unhandled"])
        
        for trace in debug_traces:
            for event in trace.get("events", []):
                if event.get("level") == "error":
                    message = event.get("message", "").lower()
                    for keyword in unexpected_error_keywords:
                        if keyword in message:
                            anomalies.append({
                                "type": "unexpected_error",
                                "trace_id": trace.get("trace_id"),
                                "event_id": event.get("event_id"),
                                "message": event.get("message"),
                                "timestamp": event.get("timestamp")
                            })
                            break
        
        return {
            "success": True,
            "analysis_type": "anomaly_detection",
            "summary": f"Detected {len(anomalies)} potential anomalies.",
            "anomalies": anomalies
        }

    async def _analyze_security_incident(
        self, 
        workflow_id: str, 
        execution_data: Dict[str, Any],
        debug_traces: List[Dict[str, Any]],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze potential security incidents in workflow execution.

        Args:
            workflow_id: ID of the workflow.
            execution_data: Workflow execution data.
            debug_traces: List of debug traces.
            parameters: Analysis parameters.

        Returns:
            Dict containing analysis result.
        """
        # This requires integration with security monitoring tools and logs
        # Placeholder implementation
        
        incidents = []
        
        # Example: Look for authentication failures in debug traces
        auth_failure_keywords = parameters.get("auth_failure_keywords", ["auth failed", "unauthorized", "access denied"])
        
        for trace in debug_traces:
            for event in trace.get("events", []):
                message = event.get("message", "").lower()
                for keyword in auth_failure_keywords:
                    if keyword in message:
                        incidents.append({
                            "type": "authentication_failure",
                            "trace_id": trace.get("trace_id"),
                            "event_id": event.get("event_id"),
                            "agent_id": event.get("agent_id"),
                            "message": event.get("message"),
                            "timestamp": event.get("timestamp")
                        })
                        break
        
        # Example: Check for unauthorized data access attempts (requires more context)
        # ...
        
        return {
            "success": True,
            "analysis_type": "security_incident",
            "summary": f"Detected {len(incidents)} potential security incidents.",
            "incidents": incidents
        }

    async def _analyze_compliance_check(
        self, 
        workflow_id: str, 
        execution_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Check workflow execution against compliance rules.

        Args:
            workflow_id: ID of the workflow.
            execution_data: Workflow execution data.
            parameters: Analysis parameters (including compliance rules).

        Returns:
            Dict containing analysis result.
        """
        # Requires compliance rules definition
        compliance_rules = parameters.get("compliance_rules", [])
        
        if not compliance_rules:
            return {
                "success": False,
                "error": "No compliance rules provided"
            }
        
        violations = []
        
        # Example rule: Check if sensitive data was handled by approved agents
        sensitive_data_rule = next((r for r in compliance_rules if r["type"] == "sensitive_data_handling"), None)
        if sensitive_data_rule:
            approved_agents = sensitive_data_rule.get("approved_agents", [])
            sensitive_tasks = sensitive_data_rule.get("sensitive_tasks", [])
            
            for task in execution_data.get("task_executions", []):
                task_id = task.get("task_id")
                agent_id = task.get("agent_id")
                
                if task_id in sensitive_tasks and agent_id not in approved_agents:
                    violations.append({
                        "rule_id": sensitive_data_rule.get("id"),
                        "type": "sensitive_data_handling",
                        "task_id": task_id,
                        "agent_id": agent_id,
                        "details": f"Task {task_id} handling sensitive data was executed by non-approved agent {agent_id}",
                        "timestamp": task.get("end_time")
                    })
        
        # Example rule: Check for execution duration limits
        duration_limit_rule = next((r for r in compliance_rules if r["type"] == "duration_limit"), None)
        if duration_limit_rule:
            max_duration_ms = duration_limit_rule.get("max_duration_ms")
            
            for task in execution_data.get("task_executions", []):
                task_id = task.get("task_id")
                start_time = task.get("start_time")
                end_time = task.get("end_time")
                
                if task_id and start_time and end_time:
                    try:
                        start_dt = datetime.fromisoformat(start_time)
                        end_dt = datetime.fromisoformat(end_time)
                        duration_ms = (end_dt - start_dt).total_seconds() * 1000
                        
                        if duration_ms > max_duration_ms:
                            violations.append({
                                "rule_id": duration_limit_rule.get("id"),
                                "type": "duration_limit",
                                "task_id": task_id,
                                "duration_ms": duration_ms,
                                "limit_ms": max_duration_ms,
                                "details": f"Task {task_id} exceeded maximum duration limit",
                                "timestamp": end_time
                            })
                    except (ValueError, TypeError):
                        pass
        
        return {
            "success": True,
            "analysis_type": "compliance_check",
            "summary": f"Found {len(violations)} compliance violations.",
            "violations": violations
        }

    async def _analyze_optimization_potential(
        self, 
        workflow_id: str, 
        execution_data: Dict[str, Any],
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze workflow execution for optimization potential.

        Args:
            workflow_id: ID of the workflow.
            execution_data: Workflow execution data.
            parameters: Analysis parameters.

        Returns:
            Dict containing analysis result.
        """
        # Leverage bottleneck analysis
        bottleneck_result = await self._analyze_performance_bottleneck(workflow_id, execution_data, parameters)
        
        optimization_suggestions = []
        
        # Suggest optimizing bottleneck tasks
        if bottleneck_result["success"]:
            for bottleneck in bottleneck_result.get("bottlenecks", []):
                optimization_suggestions.append({
                    "type": "task_optimization",
                    "task_id": bottleneck["task_id"],
                    "suggestion": f"Optimize task {bottleneck['task_id']} (duration: {bottleneck['duration_ms']}ms) - consider parallelization, resource increase, or algorithm improvement.",
                    "priority": "high"
                })
        
        # Example: Suggest parallelization for independent tasks
        # Requires dependency analysis from workflow manifest
        # ...
        
        # Example: Suggest caching for frequently executed tasks with same inputs
        # Requires analysis of task inputs and execution frequency
        # ...
        
        return {
            "success": True,
            "analysis_type": "optimization_potential",
            "summary": f"Identified {len(optimization_suggestions)} potential optimization opportunities.",
            "suggestions": optimization_suggestions
        }

    async def get_analysis_status(self, analysis_id: str) -> Dict[str, Any]:
        """Get the status of a forensic analysis.

        Args:
            analysis_id: ID of the analysis.

        Returns:
            Dict containing analysis status.
        """
        if analysis_id in self.active_analyses:
            analysis = self.active_analyses[analysis_id]
            return {
                "success": True,
                "analysis_id": analysis_id,
                "status": analysis["status"],
                "workflow_id": analysis["workflow_id"],
                "analysis_type": analysis["analysis_type"],
                "progress": analysis["progress"],
                "start_time": analysis["start_time"]
            }
        elif analysis_id in self.analysis_cache:
            analysis = self.analysis_cache[analysis_id]
            return {
                "success": True,
                "analysis_id": analysis_id,
                "status": analysis["status"],
                "workflow_id": analysis["workflow_id"],
                "analysis_type": analysis["analysis_type"],
                "start_time": analysis["start_time"],
                "end_time": analysis.get("end_time"),
                "result": analysis.get("result"),
                "error": analysis.get("error")
            }
        else:
            return {
                "success": False,
                "error": f"Analysis {analysis_id} not found"
            }

    async def get_analysis_result(self, analysis_id: str) -> Dict[str, Any]:
        """Get the result of a completed forensic analysis.

        Args:
            analysis_id: ID of the analysis.

        Returns:
            Dict containing analysis result.
        """
        status_result = await self.get_analysis_status(analysis_id)
        
        if not status_result["success"]:
            return status_result
        
        if status_result["status"] == "running":
            return {
                "success": False,
                "error": f"Analysis {analysis_id} is still running (progress: {status_result['progress']}%)"
            }
        
        return {
            "success": True,
            "analysis_id": analysis_id,
            "status": status_result["status"],
            "result": status_result.get("result"),
            "error": status_result.get("error")
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
            "resilience_mode": "read_only",  # Forensics agent doesn't modify state
            "ui_capsule_support": {
                "capsule_editable": True,
                "n8n_embedded": True,
                "editable_nodes": ["forensic_analysis_node", "anomaly_detection_node"]
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
            payload = message.get("payload", {})
            
            if message_type == "start_forensic_analysis":
                return await self.start_forensic_analysis(payload)
            elif message_type == "get_analysis_status":
                analysis_id = payload.get("analysis_id")
                return await self.get_analysis_status(analysis_id)
            elif message_type == "get_analysis_result":
                analysis_id = payload.get("analysis_id")
                return await self.get_analysis_result(analysis_id)
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
