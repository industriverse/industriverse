"""
Capsule Debug Trace Manager Module for Industriverse Workflow Automation Layer

This module is responsible for managing debug traces for workflow capsules,
providing comprehensive logging, pattern detection, and forensic analysis
capabilities. It implements the structured debug trace schema defined in
the deployment prompt, enabling step-by-step agent logs, trust replay,
and fault injection diagnostics.

The CapsuleDebugTraceManager class provides the core functionality for
capturing, storing, analyzing, and visualizing debug traces.
"""

import logging
import json
import os
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class AgentTrace(BaseModel):
    """Model representing a trace entry for an agent in a workflow execution."""
    agent_id: str
    input_received: bool = True
    decision: Optional[str] = None
    reason: Optional[str] = None
    time: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StateHistory(BaseModel):
    """Model representing a state change in the workflow execution."""
    state: str
    time: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContextVariable(BaseModel):
    """Model representing a context variable in the workflow execution."""
    name: str
    value: Any
    type: str = "string"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


class CapsuleMemory(BaseModel):
    """Model representing the memory of a workflow capsule."""
    context_variables: Dict[str, Any] = Field(default_factory=dict)
    state_history: List[StateHistory] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CapsuleDebugTrace(BaseModel):
    """
    Model representing a complete debug trace for a workflow capsule.
    
    This is the central data structure that captures the execution history,
    agent interactions, state changes, and context variables for a workflow.
    """
    workflow_id: str
    execution_id: str
    agent_trace: List[AgentTrace] = Field(default_factory=list)
    capsule_memory: Optional[CapsuleMemory] = None
    start_time: str = Field(default_factory=lambda: datetime.now().isoformat())
    end_time: Optional[str] = None
    status: str = "running"
    error: Optional[str] = None


class TraceStorageType(str, Enum):
    """Enum representing the storage types for debug traces."""
    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"


class CapsuleDebugTraceManager:
    """
    Manager for workflow capsule debug traces.
    
    This class provides methods to capture, store, analyze, and visualize
    debug traces for workflow capsules, enabling comprehensive debugging,
    pattern detection, and forensic analysis.
    """
    
    def __init__(self, storage_type: TraceStorageType = TraceStorageType.MEMORY, storage_path: Optional[str] = None):
        """
        Initialize the CapsuleDebugTraceManager.
        
        Args:
            storage_type: The type of storage to use for debug traces
            storage_path: The path to use for file storage (if applicable)
        """
        self.storage_type = storage_type
        self.storage_path = storage_path
        
        # In-memory storage
        self.traces: Dict[str, CapsuleDebugTrace] = {}
        
        # Initialize storage
        if storage_type == TraceStorageType.FILE and storage_path:
            os.makedirs(storage_path, exist_ok=True)
        
        logger.info(f"CapsuleDebugTraceManager initialized with {storage_type} storage")
    
    def create_trace(self, workflow_id: str, execution_id: str) -> CapsuleDebugTrace:
        """
        Create a new debug trace for a workflow execution.
        
        Args:
            workflow_id: The ID of the workflow
            execution_id: The ID of the workflow execution
            
        Returns:
            The created CapsuleDebugTrace
        """
        trace = CapsuleDebugTrace(
            workflow_id=workflow_id,
            execution_id=execution_id,
            capsule_memory=CapsuleMemory()
        )
        
        # Store the trace
        self.traces[execution_id] = trace
        
        # Save to storage
        if self.storage_type == TraceStorageType.FILE:
            self._save_trace_to_file(trace)
        
        logger.info(f"Created debug trace for workflow {workflow_id}, execution {execution_id}")
        return trace
    
    def get_trace(self, execution_id: str) -> Optional[CapsuleDebugTrace]:
        """
        Get a debug trace by execution ID.
        
        Args:
            execution_id: The ID of the workflow execution
            
        Returns:
            The CapsuleDebugTrace if found, None otherwise
        """
        # Check in-memory cache first
        if execution_id in self.traces:
            return self.traces[execution_id]
        
        # If not in memory and using file storage, try to load from file
        if self.storage_type == TraceStorageType.FILE and self.storage_path:
            trace = self._load_trace_from_file(execution_id)
            if trace:
                # Cache in memory
                self.traces[execution_id] = trace
                return trace
        
        return None
    
    def add_agent_trace(self, execution_id: str, agent_trace: AgentTrace) -> bool:
        """
        Add an agent trace entry to a debug trace.
        
        Args:
            execution_id: The ID of the workflow execution
            agent_trace: The agent trace entry to add
            
        Returns:
            True if the trace was updated, False if it wasn't found
        """
        trace = self.get_trace(execution_id)
        if not trace:
            logger.warning(f"Attempted to add agent trace to non-existent debug trace for execution {execution_id}")
            return False
        
        # Add the agent trace
        trace.agent_trace.append(agent_trace)
        
        # Save to storage
        if self.storage_type == TraceStorageType.FILE:
            self._save_trace_to_file(trace)
        
        logger.debug(f"Added agent trace for agent {agent_trace.agent_id} to execution {execution_id}")
        return True
    
    def update_capsule_memory(self, execution_id: str, context_variables: Optional[Dict[str, Any]] = None, state: Optional[str] = None) -> bool:
        """
        Update the capsule memory for a debug trace.
        
        Args:
            execution_id: The ID of the workflow execution
            context_variables: Optional dictionary of context variables to update
            state: Optional new state to add to the state history
            
        Returns:
            True if the trace was updated, False if it wasn't found
        """
        trace = self.get_trace(execution_id)
        if not trace:
            logger.warning(f"Attempted to update capsule memory for non-existent debug trace for execution {execution_id}")
            return False
        
        # Ensure capsule memory exists
        if not trace.capsule_memory:
            trace.capsule_memory = CapsuleMemory()
        
        # Update context variables
        if context_variables:
            trace.capsule_memory.context_variables.update(context_variables)
        
        # Add state to history
        if state:
            state_entry = StateHistory(
                state=state,
                time=datetime.now().isoformat()
            )
            trace.capsule_memory.state_history.append(state_entry)
        
        # Save to storage
        if self.storage_type == TraceStorageType.FILE:
            self._save_trace_to_file(trace)
        
        logger.debug(f"Updated capsule memory for execution {execution_id}")
        return True
    
    def complete_trace(self, execution_id: str, status: str = "completed", error: Optional[str] = None) -> bool:
        """
        Mark a debug trace as completed.
        
        Args:
            execution_id: The ID of the workflow execution
            status: The final status of the execution
            error: Optional error message if the execution failed
            
        Returns:
            True if the trace was updated, False if it wasn't found
        """
        trace = self.get_trace(execution_id)
        if not trace:
            logger.warning(f"Attempted to complete non-existent debug trace for execution {execution_id}")
            return False
        
        # Update trace
        trace.end_time = datetime.now().isoformat()
        trace.status = status
        trace.error = error
        
        # Save to storage
        if self.storage_type == TraceStorageType.FILE:
            self._save_trace_to_file(trace)
        
        logger.info(f"Completed debug trace for execution {execution_id} with status {status}")
        return True
    
    def save_trace(self, workflow_id: str, execution_id: str, agent_trace: List[AgentTrace]) -> bool:
        """
        Save a complete debug trace for a workflow execution.
        
        Args:
            workflow_id: The ID of the workflow
            execution_id: The ID of the workflow execution
            agent_trace: The list of agent trace entries
            
        Returns:
            True if the trace was saved successfully
        """
        # Create or get the trace
        trace = self.get_trace(execution_id)
        if not trace:
            trace = self.create_trace(workflow_id, execution_id)
        
        # Update the agent trace
        trace.agent_trace = agent_trace
        
        # Mark as completed
        trace.end_time = datetime.now().isoformat()
        trace.status = "completed"
        
        # Save to storage
        if self.storage_type == TraceStorageType.FILE:
            self._save_trace_to_file(trace)
        
        logger.info(f"Saved complete debug trace for workflow {workflow_id}, execution {execution_id}")
        return True
    
    def _save_trace_to_file(self, trace: CapsuleDebugTrace) -> bool:
        """
        Save a debug trace to a file.
        
        Args:
            trace: The debug trace to save
            
        Returns:
            True if the trace was saved successfully
        """
        if not self.storage_path:
            logger.error("No storage path configured for file storage")
            return False
        
        try:
            # Create directory for workflow if it doesn't exist
            workflow_dir = os.path.join(self.storage_path, trace.workflow_id)
            os.makedirs(workflow_dir, exist_ok=True)
            
            # Save trace to file
            trace_path = os.path.join(workflow_dir, f"{trace.execution_id}.json")
            with open(trace_path, "w") as f:
                f.write(trace.json(indent=2))
            
            logger.debug(f"Saved debug trace to {trace_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save debug trace to file: {e}")
            return False
    
    def _load_trace_from_file(self, execution_id: str) -> Optional[CapsuleDebugTrace]:
        """
        Load a debug trace from a file.
        
        Args:
            execution_id: The ID of the workflow execution
            
        Returns:
            The CapsuleDebugTrace if found and loaded successfully, None otherwise
        """
        if not self.storage_path:
            logger.error("No storage path configured for file storage")
            return None
        
        try:
            # Search for the trace file in all workflow directories
            for workflow_dir in os.listdir(self.storage_path):
                workflow_path = os.path.join(self.storage_path, workflow_dir)
                if not os.path.isdir(workflow_path):
                    continue
                
                trace_path = os.path.join(workflow_path, f"{execution_id}.json")
                if os.path.exists(trace_path):
                    with open(trace_path, "r") as f:
                        trace_data = json.load(f)
                        return CapsuleDebugTrace(**trace_data)
            
            logger.debug(f"Debug trace for execution {execution_id} not found in file storage")
            return None
        
        except Exception as e:
            logger.error(f"Failed to load debug trace from file: {e}")
            return None
    
    def list_traces(self, 
                   workflow_id: Optional[str] = None,
                   status: Optional[str] = None,
                   start_time: Optional[datetime] = None,
                   end_time: Optional[datetime] = None,
                   limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List debug traces, optionally filtered by various criteria.
        
        Args:
            workflow_id: Filter by workflow ID
            status: Filter by status
            start_time: Filter by start time (inclusive)
            end_time: Filter by end time (inclusive)
            limit: Maximum number of traces to return
            
        Returns:
            A list of dictionaries with basic trace information
        """
        result = []
        
        # If using file storage, load all traces from files
        if self.storage_type == TraceStorageType.FILE and self.storage_path:
            self._load_all_traces_from_files()
        
        # Filter and collect traces
        for trace in self.traces.values():
            # Apply filters
            if workflow_id and trace.workflow_id != workflow_id:
                continue
            
            if status and trace.status != status:
                continue
            
            trace_start_time = datetime.fromisoformat(trace.start_time)
            if start_time and trace_start_time < start_time:
                continue
            
            if end_time:
                if trace.end_time:
                    trace_end_time = datetime.fromisoformat(trace.end_time)
                    if trace_end_time > end_time:
                        continue
                else:
                    # If no end time and filtering by end time, skip running traces
                    continue
            
            # Add to result
            result.append({
                "workflow_id": trace.workflow_id,
                "execution_id": trace.execution_id,
                "start_time": trace.start_time,
                "end_time": trace.end_time,
                "status": trace.status,
                "agent_count": len(trace.agent_trace)
            })
        
        # Sort by start time (newest first)
        result.sort(key=lambda t: t["start_time"], reverse=True)
        
        # Apply limit
        if limit:
            result = result[:limit]
        
        return result
    
    def _load_all_traces_from_files(self):
        """Load all debug traces from files into memory."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            return
        
        try:
            # Iterate through workflow directories
            for workflow_dir in os.listdir(self.storage_path):
                workflow_path = os.path.join(self.storage_path, workflow_dir)
                if not os.path.isdir(workflow_path):
                    continue
                
                # Iterate through trace files
                for trace_file in os.listdir(workflow_path):
                    if not trace_file.endswith(".json"):
                        continue
                    
                    trace_path = os.path.join(workflow_path, trace_file)
                    execution_id = trace_file[:-5]  # Remove .json extension
                    
                    # Skip if already loaded
                    if execution_id in self.traces:
                        continue
                    
                    # Load trace
                    try:
                        with open(trace_path, "r") as f:
                            trace_data = json.load(f)
                            self.traces[execution_id] = CapsuleDebugTrace(**trace_data)
                    except Exception as e:
                        logger.error(f"Failed to load debug trace from {trace_path}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to load debug traces from files: {e}")
    
    def analyze_trace(self, execution_id: str) -> Dict[str, Any]:
        """
        Analyze a debug trace to extract insights and patterns.
        
        Args:
            execution_id: The ID of the workflow execution
            
        Returns:
            A dictionary with analysis results
            
        Raises:
            ValueError: If the trace doesn't exist
        """
        trace = self.get_trace(execution_id)
        if not trace:
            raise ValueError(f"Debug trace for execution {execution_id} not found")
        
        # Calculate basic metrics
        agent_counts = {}
        decision_counts = {}
        state_durations = {}
        
        # Analyze agent trace
        for entry in trace.agent_trace:
            # Count by agent
            agent_counts[entry.agent_id] = agent_counts.get(entry.agent_id, 0) + 1
            
            # Count by decision
            if entry.decision:
                decision_counts[entry.decision] = decision_counts.get(entry.decision, 0) + 1
        
        # Analyze state history
        if trace.capsule_memory and trace.capsule_memory.state_history:
            history = trace.capsule_memory.state_history
            for i in range(len(history) - 1):
                state = history[i].state
                start_time = datetime.fromisoformat(history[i].time)
                end_time = datetime.fromisoformat(history[i + 1].time)
                duration = (end_time - start_time).total_seconds()
                
                if state in state_durations:
                    state_durations[state] += duration
                else:
                    state_durations[state] = duration
        
        # Calculate execution duration
        duration = None
        if trace.end_time:
            start_time = datetime.fromisoformat(trace.start_time)
            end_time = datetime.fromisoformat(trace.end_time)
            duration = (end_time - start_time).total_seconds()
        
        # Identify potential issues
        issues = []
        
        # Check for long-running states
        for state, duration in state_durations.items():
            if duration > 10:  # More than 10 seconds in a single state
                issues.append(f"Long-running state: {state} ({duration:.2f}s)")
        
        # Check for repeated failures
        failure_count = decision_counts.get("failed", 0)
        if failure_count > 3:
            issues.append(f"Multiple failures detected: {failure_count}")
        
        # Check for escalations
        escalation_count = decision_counts.get("escalated", 0)
        if escalation_count > 0:
            issues.append(f"Escalations detected: {escalation_count}")
        
        return {
            "execution_id": execution_id,
            "workflow_id": trace.workflow_id,
            "status": trace.status,
            "duration": duration,
            "agent_counts": agent_counts,
            "decision_counts": decision_counts,
            "state_durations": state_durations,
            "issues": issues,
            "context_variables": trace.capsule_memory.context_variables if trace.capsule_memory else {}
        }
    
    def compare_traces(self, execution_id1: str, execution_id2: str) -> Dict[str, Any]:
        """
        Compare two debug traces to identify differences and similarities.
        
        Args:
            execution_id1: The ID of the first workflow execution
            execution_id2: The ID of the second workflow execution
            
        Returns:
            A dictionary with comparison results
            
        Raises:
            ValueError: If either trace doesn't exist
        """
        trace1 = self.get_trace(execution_id1)
        trace2 = self.get_trace(execution_id2)
        
        if not trace1:
            raise ValueError(f"Debug trace for execution {execution_id1} not found")
        
        if not trace2:
            raise ValueError(f"Debug trace for execution {execution_id2} not found")
        
        # Compare basic properties
        same_workflow = trace1.workflow_id == trace2.workflow_id
        same_status = trace1.status == trace2.status
        
        # Compare durations
        duration1 = None
        duration2 = None
        
        if trace1.end_time:
            start_time = datetime.fromisoformat(trace1.start_time)
            end_time = datetime.fromisoformat(trace1.end_time)
            duration1 = (end_time - start_time).total_seconds()
        
        if trace2.end_time:
            start_time = datetime.fromisoformat(trace2.start_time)
            end_time = datetime.fromisoformat(trace2.end_time)
            duration2 = (end_time - start_time).total_seconds()
        
        duration_diff = None
        if duration1 is not None and duration2 is not None:
            duration_diff = duration2 - duration1
        
        # Compare agent traces
        agents1 = set(entry.agent_id for entry in trace1.agent_trace)
        agents2 = set(entry.agent_id for entry in trace2.agent_trace)
        
        common_agents = agents1.intersection(agents2)
        unique_agents1 = agents1 - agents2
        unique_agents2 = agents2 - agents1
        
        # Compare decisions
        decisions1 = [entry.decision for entry in trace1.agent_trace if entry.decision]
        decisions2 = [entry.decision for entry in trace2.agent_trace if entry.decision]
        
        different_decisions = []
        for i in range(min(len(decisions1), len(decisions2))):
            if decisions1[i] != decisions2[i]:
                different_decisions.append({
                    "index": i,
                    "trace1": decisions1[i],
                    "trace2": decisions2[i]
                })
        
        # Compare state history
        states1 = []
        states2 = []
        
        if trace1.capsule_memory and trace1.capsule_memory.state_history:
            states1 = [entry.state for entry in trace1.capsule_memory.state_history]
        
        if trace2.capsule_memory and trace2.capsule_memory.state_history:
            states2 = [entry.state for entry in trace2.capsule_memory.state_history]
        
        different_states = []
        for i in range(min(len(states1), len(states2))):
            if states1[i] != states2[i]:
                different_states.append({
                    "index": i,
                    "trace1": states1[i],
                    "trace2": states2[i]
                })
        
        return {
            "same_workflow": same_workflow,
            "same_status": same_status,
            "duration1": duration1,
            "duration2": duration2,
            "duration_diff": duration_diff,
            "common_agents": list(common_agents),
            "unique_agents1": list(unique_agents1),
            "unique_agents2": list(unique_agents2),
            "agent_count1": len(trace1.agent_trace),
            "agent_count2": len(trace2.agent_trace),
            "different_decisions": different_decisions,
            "different_states": different_states
        }
    
    def export_trace_to_json(self, execution_id: str, file_path: str) -> bool:
        """
        Export a debug trace to a JSON file.
        
        Args:
            execution_id: The ID of the workflow execution
            file_path: The path to save the JSON file
            
        Returns:
            True if the trace was exported successfully
            
        Raises:
            ValueError: If the trace doesn't exist
        """
        trace = self.get_trace(execution_id)
        if not trace:
            raise ValueError(f"Debug trace for execution {execution_id} not found")
        
        try:
            with open(file_path, "w") as f:
                f.write(trace.json(indent=2))
            
            logger.info(f"Exported debug trace for execution {execution_id} to {file_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export debug trace to {file_path}: {e}")
            return False
    
    def import_trace_from_json(self, file_path: str) -> str:
        """
        Import a debug trace from a JSON file.
        
        Args:
            file_path: The path to the JSON file
            
        Returns:
            The execution ID of the imported trace
            
        Raises:
            ValueError: If the file is invalid or doesn't contain a valid trace
        """
        try:
            with open(file_path, "r") as f:
                trace_data = json.load(f)
            
            trace = CapsuleDebugTrace(**trace_data)
            self.traces[trace.execution_id] = trace
            
            # Save to storage if using file storage
            if self.storage_type == TraceStorageType.FILE:
                self._save_trace_to_file(trace)
            
            logger.info(f"Imported debug trace for execution {trace.execution_id} from {file_path}")
            return trace.execution_id
        
        except Exception as e:
            logger.error(f"Failed to import debug trace from {file_path}: {e}")
            raise ValueError(f"Failed to import debug trace: {e}")
    
    def generate_trace_visualization(self, execution_id: str) -> Dict[str, Any]:
        """
        Generate visualization data for a debug trace.
        
        Args:
            execution_id: The ID of the workflow execution
            
        Returns:
            A dictionary with visualization data
            
        Raises:
            ValueError: If the trace doesn't exist
        """
        trace = self.get_trace(execution_id)
        if not trace:
            raise ValueError(f"Debug trace for execution {execution_id} not found")
        
        # Generate nodes and edges for a graph visualization
        nodes = []
        edges = []
        
        # Add agent nodes
        agent_ids = set()
        for entry in trace.agent_trace:
            agent_id = entry.agent_id
            if agent_id not in agent_ids:
                nodes.append({
                    "id": agent_id,
                    "label": agent_id,
                    "type": "agent"
                })
                agent_ids.add(agent_id)
        
        # Add state nodes
        state_ids = set()
        if trace.capsule_memory and trace.capsule_memory.state_history:
            for entry in trace.capsule_memory.state_history:
                state = entry.state
                state_id = f"state_{state}"
                if state_id not in state_ids:
                    nodes.append({
                        "id": state_id,
                        "label": state,
                        "type": "state"
                    })
                    state_ids.add(state_id)
        
        # Add edges between agents based on trace order
        for i in range(len(trace.agent_trace) - 1):
            source = trace.agent_trace[i].agent_id
            target = trace.agent_trace[i + 1].agent_id
            if source != target:  # Avoid self-loops
                edges.append({
                    "source": source,
                    "target": target,
                    "label": trace.agent_trace[i].decision or "next"
                })
        
        # Add edges between states
        if trace.capsule_memory and trace.capsule_memory.state_history:
            for i in range(len(trace.capsule_memory.state_history) - 1):
                source = f"state_{trace.capsule_memory.state_history[i].state}"
                target = f"state_{trace.capsule_memory.state_history[i + 1].state}"
                edges.append({
                    "source": source,
                    "target": target,
                    "label": "transition"
                })
        
        # Add timeline data
        timeline = []
        
        # Add agent events to timeline
        for entry in trace.agent_trace:
            timeline.append({
                "time": entry.time,
                "agent_id": entry.agent_id,
                "event": entry.decision or "processing",
                "type": "agent"
            })
        
        # Add state events to timeline
        if trace.capsule_memory and trace.capsule_memory.state_history:
            for entry in trace.capsule_memory.state_history:
                timeline.append({
                    "time": entry.time,
                    "state": entry.state,
                    "type": "state"
                })
        
        # Sort timeline by time
        timeline.sort(key=lambda e: e["time"])
        
        return {
            "execution_id": execution_id,
            "workflow_id": trace.workflow_id,
            "status": trace.status,
            "nodes": nodes,
            "edges": edges,
            "timeline": timeline
        }
    
    def create_forensics_report(self, execution_id: str) -> Dict[str, Any]:
        """
        Create a forensics report for a debug trace.
        
        Args:
            execution_id: The ID of the workflow execution
            
        Returns:
            A dictionary with the forensics report
            
        Raises:
            ValueError: If the trace doesn't exist
        """
        trace = self.get_trace(execution_id)
        if not trace:
            raise ValueError(f"Debug trace for execution {execution_id} not found")
        
        # Basic information
        report = {
            "execution_id": execution_id,
            "workflow_id": trace.workflow_id,
            "start_time": trace.start_time,
            "end_time": trace.end_time,
            "status": trace.status,
            "error": trace.error
        }
        
        # Calculate duration
        if trace.end_time:
            start_time = datetime.fromisoformat(trace.start_time)
            end_time = datetime.fromisoformat(trace.end_time)
            report["duration_seconds"] = (end_time - start_time).total_seconds()
        
        # Agent statistics
        agent_stats = {}
        for entry in trace.agent_trace:
            agent_id = entry.agent_id
            if agent_id not in agent_stats:
                agent_stats[agent_id] = {
                    "count": 0,
                    "decisions": {}
                }
            
            agent_stats[agent_id]["count"] += 1
            
            if entry.decision:
                decision = entry.decision
                agent_stats[agent_id]["decisions"][decision] = agent_stats[agent_id]["decisions"].get(decision, 0) + 1
        
        report["agent_statistics"] = agent_stats
        
        # State statistics
        state_stats = {}
        if trace.capsule_memory and trace.capsule_memory.state_history:
            for i in range(len(trace.capsule_memory.state_history)):
                state = trace.capsule_memory.state_history[i].state
                if state not in state_stats:
                    state_stats[state] = {
                        "count": 0,
                        "duration_seconds": 0
                    }
                
                state_stats[state]["count"] += 1
                
                # Calculate state duration
                if i < len(trace.capsule_memory.state_history) - 1:
                    start_time = datetime.fromisoformat(trace.capsule_memory.state_history[i].time)
                    end_time = datetime.fromisoformat(trace.capsule_memory.state_history[i + 1].time)
                    duration = (end_time - start_time).total_seconds()
                    state_stats[state]["duration_seconds"] += duration
        
        report["state_statistics"] = state_stats
        
        # Context variables
        if trace.capsule_memory:
            report["context_variables"] = trace.capsule_memory.context_variables
        
        # Identify critical events
        critical_events = []
        
        # Look for failures
        for entry in trace.agent_trace:
            if entry.decision == "failed":
                critical_events.append({
                    "type": "failure",
                    "agent_id": entry.agent_id,
                    "time": entry.time,
                    "reason": entry.reason
                })
        
        # Look for escalations
        for entry in trace.agent_trace:
            if entry.decision == "escalated":
                critical_events.append({
                    "type": "escalation",
                    "agent_id": entry.agent_id,
                    "time": entry.time,
                    "reason": entry.reason
                })
        
        report["critical_events"] = critical_events
        
        # Recommendations
        recommendations = []
        
        # Check for repeated failures
        failure_agents = [event["agent_id"] for event in critical_events if event["type"] == "failure"]
        if len(failure_agents) > 0:
            failure_counts = {}
            for agent_id in failure_agents:
                failure_counts[agent_id] = failure_counts.get(agent_id, 0) + 1
            
            for agent_id, count in failure_counts.items():
                if count > 1:
                    recommendations.append(f"Agent {agent_id} failed {count} times. Consider reviewing its implementation or providing fallback mechanisms.")
        
        # Check for long-running states
        for state, stats in state_stats.items():
            if stats["duration_seconds"] > 10:  # More than 10 seconds in a single state
                recommendations.append(f"State '{state}' ran for {stats['duration_seconds']:.2f} seconds. Consider optimizing or adding timeouts.")
        
        # Check for excessive agent interactions
        for agent_id, stats in agent_stats.items():
            if stats["count"] > 10:  # More than 10 interactions with the same agent
                recommendations.append(f"Agent {agent_id} was involved in {stats['count']} interactions. Consider simplifying the workflow or distributing the load.")
        
        report["recommendations"] = recommendations
        
        return report
