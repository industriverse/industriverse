"""
A2A Task Execution Engine
Week 17 Day 3: A2A Protocol Task Execution Integration

This module implements the task execution engine that integrates A2A protocol
task assignments with the Industriverse Capsule Creation Engine and other services.

It provides:
1. Task queuing and scheduling
2. Task execution coordination
3. Status updates and result handling
4. Integration with Capsule Creation Engine
5. Workflow orchestration
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Any, Optional, Callable, Awaitable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, field, asdict
import json

logger = logging.getLogger(__name__)


# =============================================================================
# Task Status and Priority Enums
# =============================================================================

class TaskStatus(str, Enum):
    """Task execution status."""
    QUEUED = "queued"
    ASSIGNED = "assigned"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


# =============================================================================
# Task Data Structures
# =============================================================================

@dataclass
class TaskExecutionContext:
    """Context for task execution."""
    task_id: str
    task_type: str
    parameters: Dict[str, Any]
    priority: TaskPriority = TaskPriority.NORMAL
    timeout_seconds: int = 300
    retry_count: int = 0
    max_retries: int = 3

    # Execution metadata
    assigned_agent_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Status tracking
    status: TaskStatus = TaskStatus.QUEUED
    progress_percentage: float = 0.0
    status_message: Optional[str] = None

    # Results
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO format
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        # Convert enums to values
        data['status'] = self.status.value
        data['priority'] = self.priority.value
        return data


# =============================================================================
# Task Execution Engine
# =============================================================================

class A2ATaskExecutionEngine:
    """
    Executes tasks assigned via A2A protocol.

    Integrates with:
    - Capsule Creation Engine (for sensor-based capsule generation)
    - Workflow Automation Layer (for workflow execution)
    - Data Layer (for data retrieval)
    - Core AI Layer (for AI inference tasks)
    """

    def __init__(self):
        """Initialize the task execution engine."""
        # Task queue (priority queue)
        self.task_queue: asyncio.PriorityQueue = asyncio.PriorityQueue()

        # Active tasks (task_id -> TaskExecutionContext)
        self.active_tasks: Dict[str, TaskExecutionContext] = {}

        # Completed tasks (circular buffer of last 1000)
        self.completed_tasks: List[TaskExecutionContext] = []
        self.max_completed_tasks = 1000

        # Task executors (task_type -> executor function)
        self.task_executors: Dict[str, Callable] = {}

        # Task status callbacks (for notifying A2A handler)
        self.status_callbacks: List[Callable[[TaskExecutionContext], Awaitable[None]]] = []

        # Worker task
        self.worker_task: Optional[asyncio.Task] = None
        self.running = False

        # Register default task executors
        self._register_default_executors()

        logger.info("A2ATaskExecutionEngine initialized")

    def _register_default_executors(self):
        """Register default task executors."""
        self.register_executor("create_capsule", self._execute_create_capsule_task)
        self.register_executor("query_data", self._execute_query_data_task)
        self.register_executor("run_workflow", self._execute_run_workflow_task)
        self.register_executor("ai_inference", self._execute_ai_inference_task)
        self.register_executor("sensor_analysis", self._execute_sensor_analysis_task)

    def register_executor(self, task_type: str, executor: Callable):
        """
        Register a task executor function.

        Args:
            task_type: Type of task (e.g., "create_capsule")
            executor: Async function that executes the task
        """
        self.task_executors[task_type] = executor
        logger.info(f"Registered executor for task type: {task_type}")

    def register_status_callback(self, callback: Callable[[TaskExecutionContext], Awaitable[None]]):
        """
        Register a callback for task status updates.

        Args:
            callback: Async function called when task status changes
        """
        self.status_callbacks.append(callback)
        logger.info("Registered status callback")

    async def submit_task(self, task_context: TaskExecutionContext) -> str:
        """
        Submit a task for execution.

        Args:
            task_context: Task execution context

        Returns:
            Task ID
        """
        task_context.status = TaskStatus.QUEUED

        # Add to queue (priority is negative so higher priority comes first)
        priority_value = {
            TaskPriority.CRITICAL: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.NORMAL: 2,
            TaskPriority.LOW: 3
        }[task_context.priority]

        await self.task_queue.put((priority_value, task_context))

        logger.info(f"Submitted task {task_context.task_id} ({task_context.task_type}) "
                   f"with priority {task_context.priority.value}")

        return task_context.task_id

    async def start(self):
        """Start the task execution worker."""
        if self.running:
            logger.warning("Task execution engine already running")
            return

        self.running = True
        self.worker_task = asyncio.create_task(self._worker_loop())
        logger.info("Task execution engine started")

    async def stop(self):
        """Stop the task execution worker."""
        if not self.running:
            return

        self.running = False

        if self.worker_task:
            self.worker_task.cancel()
            try:
                await self.worker_task
            except asyncio.CancelledError:
                pass

        logger.info("Task execution engine stopped")

    async def _worker_loop(self):
        """Main worker loop that processes tasks from the queue."""
        logger.info("Task execution worker loop started")

        while self.running:
            try:
                # Get next task from queue (with timeout to check running flag)
                try:
                    priority, task_context = await asyncio.wait_for(
                        self.task_queue.get(),
                        timeout=1.0
                    )
                except asyncio.TimeoutError:
                    continue

                # Execute task
                asyncio.create_task(self._execute_task(task_context))

            except Exception as e:
                logger.error(f"Error in worker loop: {e}")
                await asyncio.sleep(1)

    async def _execute_task(self, task_context: TaskExecutionContext):
        """
        Execute a single task.

        Args:
            task_context: Task execution context
        """
        task_id = task_context.task_id

        try:
            # Mark as running
            task_context.status = TaskStatus.RUNNING
            task_context.started_at = datetime.utcnow()
            self.active_tasks[task_id] = task_context
            await self._notify_status_change(task_context)

            logger.info(f"Executing task {task_id} ({task_context.task_type})")

            # Get executor for this task type
            executor = self.task_executors.get(task_context.task_type)

            if not executor:
                raise ValueError(f"No executor registered for task type: {task_context.task_type}")

            # Execute with timeout
            result = await asyncio.wait_for(
                executor(task_context),
                timeout=task_context.timeout_seconds
            )

            # Mark as completed
            task_context.status = TaskStatus.COMPLETED
            task_context.completed_at = datetime.utcnow()
            task_context.result = result
            task_context.progress_percentage = 100.0
            task_context.status_message = "Task completed successfully"

            logger.info(f"Task {task_id} completed successfully")

        except asyncio.TimeoutError:
            task_context.status = TaskStatus.TIMEOUT
            task_context.completed_at = datetime.utcnow()
            task_context.error = f"Task exceeded timeout of {task_context.timeout_seconds}s"
            task_context.status_message = "Task timed out"

            logger.error(f"Task {task_id} timed out")

        except Exception as e:
            task_context.status = TaskStatus.FAILED
            task_context.completed_at = datetime.utcnow()
            task_context.error = str(e)
            task_context.status_message = f"Task failed: {e}"

            logger.error(f"Task {task_id} failed: {e}")

            # Retry if allowed
            if task_context.retry_count < task_context.max_retries:
                task_context.retry_count += 1
                task_context.status = TaskStatus.QUEUED
                logger.info(f"Retrying task {task_id} (attempt {task_context.retry_count})")
                await self.submit_task(task_context)
                return

        finally:
            # Move from active to completed
            if task_id in self.active_tasks:
                del self.active_tasks[task_id]

            # Add to completed tasks (circular buffer)
            self.completed_tasks.append(task_context)
            if len(self.completed_tasks) > self.max_completed_tasks:
                self.completed_tasks.pop(0)

            # Notify status change
            await self._notify_status_change(task_context)

    async def _notify_status_change(self, task_context: TaskExecutionContext):
        """Notify all registered callbacks about task status change."""
        for callback in self.status_callbacks:
            try:
                await callback(task_context)
            except Exception as e:
                logger.error(f"Error in status callback: {e}")

    # =========================================================================
    # Task Executors (Integrate with Industriverse Services)
    # =========================================================================

    async def _execute_create_capsule_task(self, task_context: TaskExecutionContext) -> Dict[str, Any]:
        """
        Execute a capsule creation task.

        Integrates with Capsule Creation Engine from Week 16.
        """
        params = task_context.parameters

        # Extract capsule parameters
        title = params.get('title', 'Untitled Capsule')
        description = params.get('description', '')
        capsule_type = params.get('capsule_type', 'task')
        severity = params.get('severity', 'info')
        sensor_id = params.get('sensor_id')
        sensor_data = params.get('sensor_data', {})

        logger.info(f"Creating capsule: {title} (type: {capsule_type})")

        # TODO: Integrate with actual Capsule Creation Engine
        # For now, create a mock capsule
        capsule_id = str(uuid.uuid4())

        result = {
            "capsule_id": capsule_id,
            "title": title,
            "description": description,
            "capsule_type": capsule_type,
            "severity": severity,
            "sensor_id": sensor_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }

        # Update progress
        task_context.progress_percentage = 50.0
        task_context.status_message = "Capsule created, validating..."
        await self._notify_status_change(task_context)

        # Simulate validation delay
        await asyncio.sleep(0.5)

        task_context.progress_percentage = 100.0
        task_context.status_message = "Capsule validated and stored"

        return result

    async def _execute_query_data_task(self, task_context: TaskExecutionContext) -> Dict[str, Any]:
        """
        Execute a data query task.

        Integrates with Data Layer.
        """
        params = task_context.parameters

        query_type = params.get('query_type', 'sensor_readings')
        filters = params.get('filters', {})
        limit = params.get('limit', 100)

        logger.info(f"Executing data query: {query_type}")

        # TODO: Integrate with actual Data Layer
        # For now, return mock data
        result = {
            "query_type": query_type,
            "filters": filters,
            "results": [
                {
                    "sensor_id": "sensor_001",
                    "metric": "temperature",
                    "value": 75.5,
                    "unit": "celsius",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "count": 1,
            "limit": limit
        }

        return result

    async def _execute_run_workflow_task(self, task_context: TaskExecutionContext) -> Dict[str, Any]:
        """
        Execute a workflow run task.

        Integrates with Workflow Automation Layer.
        """
        params = task_context.parameters

        workflow_id = params.get('workflow_id')
        workflow_type = params.get('workflow_type', 'custom')
        workflow_params = params.get('workflow_params', {})

        logger.info(f"Running workflow: {workflow_id}")

        # TODO: Integrate with actual Workflow Automation Layer
        # For now, simulate workflow execution
        result = {
            "workflow_id": workflow_id,
            "workflow_type": workflow_type,
            "execution_id": str(uuid.uuid4()),
            "status": "completed",
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": (datetime.utcnow() + timedelta(seconds=2)).isoformat(),
            "output": {
                "message": f"Workflow {workflow_id} executed successfully"
            }
        }

        # Simulate workflow execution time
        await asyncio.sleep(1)

        return result

    async def _execute_ai_inference_task(self, task_context: TaskExecutionContext) -> Dict[str, Any]:
        """
        Execute an AI inference task.

        Integrates with Core AI Layer.
        """
        params = task_context.parameters

        model_name = params.get('model_name', 'default')
        input_data = params.get('input_data', {})

        logger.info(f"Running AI inference with model: {model_name}")

        # TODO: Integrate with actual Core AI Layer (LLM Inference Service)
        # For now, return mock inference result
        result = {
            "model_name": model_name,
            "inference_id": str(uuid.uuid4()),
            "input_data": input_data,
            "prediction": {
                "class": "normal",
                "confidence": 0.95,
                "probabilities": {
                    "normal": 0.95,
                    "warning": 0.04,
                    "critical": 0.01
                }
            },
            "inference_time_ms": 150
        }

        # Simulate inference time
        await asyncio.sleep(0.2)

        return result

    async def _execute_sensor_analysis_task(self, task_context: TaskExecutionContext) -> Dict[str, Any]:
        """
        Execute a sensor data analysis task.

        Analyzes sensor readings and generates insights.
        """
        params = task_context.parameters

        sensor_id = params.get('sensor_id')
        time_range = params.get('time_range', '1h')
        metrics = params.get('metrics', ['temperature', 'vibration', 'pressure'])

        logger.info(f"Analyzing sensor {sensor_id} for metrics: {metrics}")

        # TODO: Integrate with actual sensor data analysis
        # For now, return mock analysis
        result = {
            "sensor_id": sensor_id,
            "time_range": time_range,
            "metrics_analyzed": metrics,
            "analysis": {
                "temperature": {
                    "min": 65.0,
                    "max": 85.0,
                    "avg": 75.0,
                    "std_dev": 5.2,
                    "trend": "stable",
                    "anomalies_detected": 0
                },
                "vibration": {
                    "min": 20.0,
                    "max": 45.0,
                    "avg": 32.5,
                    "std_dev": 7.8,
                    "trend": "increasing",
                    "anomalies_detected": 2
                },
                "pressure": {
                    "min": 95.0,
                    "max": 105.0,
                    "avg": 100.0,
                    "std_dev": 2.1,
                    "trend": "stable",
                    "anomalies_detected": 0
                }
            },
            "insights": [
                {
                    "metric": "vibration",
                    "severity": "warning",
                    "message": "Vibration levels trending upward, maintenance recommended"
                }
            ]
        }

        # Simulate analysis time
        await asyncio.sleep(1)

        return result

    # =========================================================================
    # Task Query Methods
    # =========================================================================

    def get_task_status(self, task_id: str) -> Optional[TaskExecutionContext]:
        """
        Get status of a task.

        Args:
            task_id: Task identifier

        Returns:
            Task context or None if not found
        """
        # Check active tasks
        if task_id in self.active_tasks:
            return self.active_tasks[task_id]

        # Check completed tasks
        for task in self.completed_tasks:
            if task.task_id == task_id:
                return task

        return None

    def get_active_tasks(self) -> List[TaskExecutionContext]:
        """Get list of currently active tasks."""
        return list(self.active_tasks.values())

    def get_completed_tasks(self, limit: int = 100) -> List[TaskExecutionContext]:
        """Get list of recently completed tasks."""
        return self.completed_tasks[-limit:]

    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a running or queued task.

        Args:
            task_id: Task identifier

        Returns:
            True if cancelled, False if not found or already completed
        """
        if task_id in self.active_tasks:
            task_context = self.active_tasks[task_id]
            task_context.status = TaskStatus.CANCELLED
            task_context.completed_at = datetime.utcnow()
            task_context.status_message = "Task cancelled by request"

            await self._notify_status_change(task_context)

            logger.info(f"Cancelled task {task_id}")
            return True

        return False


# =============================================================================
# Singleton Instance
# =============================================================================

_task_execution_engine: Optional[A2ATaskExecutionEngine] = None


def get_task_execution_engine() -> A2ATaskExecutionEngine:
    """Get singleton instance of task execution engine."""
    global _task_execution_engine

    if _task_execution_engine is None:
        _task_execution_engine = A2ATaskExecutionEngine()

    return _task_execution_engine
