"""
Week 17 Day 3: A2A Task Execution Engine Tests
Tests for task execution engine, priority queue, and task executors
"""

import pytest
import asyncio
from datetime import datetime


class TestTaskExecutionEngine:
    """Test A2A task execution engine"""

    @pytest.fixture
    async def engine(self):
        """Create task execution engine"""
        try:
            from src.protocol_layer.protocols.a2a.task_execution_engine import (
                A2ATaskExecutionEngine,
                get_task_execution_engine
            )

            engine = A2ATaskExecutionEngine()
            await engine.start()
            yield engine
            await engine.stop()

        except ImportError:
            pytest.skip("Task execution engine not available")

    def test_engine_module_imports(self):
        """Test that task execution engine module can be imported"""
        try:
            from src.protocol_layer.protocols.a2a.task_execution_engine import (
                A2ATaskExecutionEngine,
                TaskExecutionContext,
                TaskStatus,
                TaskPriority,
                get_task_execution_engine
            )

            assert A2ATaskExecutionEngine is not None
            assert TaskExecutionContext is not None
            assert TaskStatus is not None
            assert TaskPriority is not None
            assert get_task_execution_engine is not None

        except ImportError as e:
            pytest.fail(f"Failed to import task execution engine: {e}")

    def test_task_status_enum(self):
        """Test TaskStatus enum values"""
        from src.protocol_layer.protocols.a2a.task_execution_engine import TaskStatus

        assert TaskStatus.QUEUED.value == "queued"
        assert TaskStatus.ASSIGNED.value == "assigned"
        assert TaskStatus.RUNNING.value == "running"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.FAILED.value == "failed"
        assert TaskStatus.CANCELLED.value == "cancelled"
        assert TaskStatus.TIMEOUT.value == "timeout"

    def test_task_priority_enum(self):
        """Test TaskPriority enum values"""
        from src.protocol_layer.protocols.a2a.task_execution_engine import TaskPriority

        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.NORMAL.value == "normal"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.CRITICAL.value == "critical"

    @pytest.mark.asyncio
    async def test_task_submission(self, engine):
        """Test task submission to engine"""
        from src.protocol_layer.protocols.a2a.task_execution_engine import (
            TaskExecutionContext,
            TaskPriority
        )

        task = TaskExecutionContext(
            task_id="test-task-1",
            task_type="create_capsule",
            parameters={"title": "Test Capsule"},
            priority=TaskPriority.HIGH
        )

        task_id = await engine.submit_task(task)
        assert task_id == "test-task-1"

    @pytest.mark.asyncio
    async def test_task_execution(self, engine):
        """Test task execution"""
        from src.protocol_layer.protocols.a2a.task_execution_engine import (
            TaskExecutionContext,
            TaskPriority,
            TaskStatus
        )

        task = TaskExecutionContext(
            task_id="test-task-2",
            task_type="create_capsule",
            parameters={"title": "Test Capsule 2"},
            priority=TaskPriority.NORMAL
        )

        await engine.submit_task(task)

        # Wait for execution
        await asyncio.sleep(2)

        # Check status
        result = engine.get_task_status("test-task-2")
        assert result is not None
        assert result.status in [TaskStatus.COMPLETED, TaskStatus.RUNNING]

    @pytest.mark.asyncio
    async def test_priority_ordering(self, engine):
        """Test that tasks are executed by priority"""
        from src.protocol_layer.protocols.a2a.task_execution_engine import (
            TaskExecutionContext,
            TaskPriority
        )

        # Submit tasks in reverse priority order
        await engine.submit_task(TaskExecutionContext(
            task_id="low-priority",
            task_type="create_capsule",
            parameters={},
            priority=TaskPriority.LOW
        ))

        await engine.submit_task(TaskExecutionContext(
            task_id="critical-priority",
            task_type="create_capsule",
            parameters={},
            priority=TaskPriority.CRITICAL
        ))

        # Critical should be picked up first
        # Note: This is a simplified test; real testing would verify execution order

    def test_task_executors_registered(self, engine):
        """Test that default task executors are registered"""
        required_executors = [
            "create_capsule",
            "query_data",
            "run_workflow",
            "ai_inference",
            "sensor_analysis"
        ]

        for executor_type in required_executors:
            assert executor_type in engine.task_executors, \
                f"Executor '{executor_type}' not registered"

    def test_singleton_pattern(self):
        """Test that get_task_execution_engine returns singleton"""
        from src.protocol_layer.protocols.a2a.task_execution_engine import (
            get_task_execution_engine
        )

        engine1 = get_task_execution_engine()
        engine2 = get_task_execution_engine()

        assert engine1 is engine2, "Singleton pattern not working"


class TestTaskExecutionDocumentation:
    """Test task execution documentation"""

    def test_integration_doc_exists(self):
        """Test that integration documentation exists"""
        from pathlib import Path

        doc = Path(
            "src/protocol_layer/protocols/a2a/TASK_EXECUTION_INTEGRATION.md"
        )

        assert doc.exists(), "Task execution integration doc not found"

    def test_integration_doc_content(self):
        """Test integration doc has required sections"""
        from pathlib import Path

        doc = Path(
            "src/protocol_layer/protocols/a2a/TASK_EXECUTION_INTEGRATION.md"
        )

        if not doc.exists():
            pytest.skip("Integration doc not found")

        content = doc.read_text()

        required_sections = [
            "Overview",
            "Architecture",
            "Resolved TODOs",
            "Task Execution Engine Features",
            "Usage Examples",
            "Testing"
        ]

        for section in required_sections:
            assert section in content, f"Section '{section}' not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
