"""
Agent Reflex Timers (ART) for Industriverse Protocol Layer

This module implements the Agent Reflex Timers component of the Protocol Layer,
enabling interruptible workflows, escalation paths, and adaptive timeouts.

Features:
1. Embedded reflex timers in protocol envelopes
2. Interruptible workflow management
3. Escalation path configuration and execution
4. Adaptive timeout calculation based on historical performance
5. Priority-based interrupt handling
"""

import uuid
import time
import asyncio
import logging
import json
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field
import threading
import heapq
import statistics

from protocols.protocol_base import ProtocolComponent, ProtocolService
from protocols.message_formats import (
    BaseMessage, RequestMessage, ResponseMessage, EventMessage,
    CommandMessage, QueryMessage, ErrorMessage, MessageFactory,
    MessagePriority, SecurityLevel, MessageStatus
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ReflexStatus(Enum):
    """Status of a reflex timer."""
    PENDING = "pending"  # Timer is active but not yet triggered
    TRIGGERED = "triggered"  # Timer has triggered
    COMPLETED = "completed"  # Associated task completed before trigger
    CANCELLED = "cancelled"  # Timer was explicitly cancelled
    ESCALATED = "escalated"  # Timer triggered and escalation occurred
    FAILED = "failed"  # Timer or associated task failed


class EscalationLevel(Enum):
    """Escalation levels for reflex timers."""
    NONE = "none"  # No escalation
    NOTIFY = "notify"  # Notify specified targets
    RETRY = "retry"  # Retry the operation
    ALTERNATE = "alternate"  # Use alternate path
    ABORT = "abort"  # Abort the operation
    EMERGENCY = "emergency"  # Trigger emergency protocols


@dataclass
class ReflexTimer:
    """
    Represents a reflex timer for an operation.
    """
    timer_id: str
    operation_id: str
    timeout_ms: int
    start_time: float
    status: ReflexStatus = ReflexStatus.PENDING
    escalation_level: EscalationLevel = EscalationLevel.NOTIFY
    escalation_target: Optional[str] = None
    escalation_data: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    context: Dict[str, Any] = field(default_factory=dict)
    completion_time: Optional[float] = None
    
    @property
    def elapsed_ms(self) -> int:
        """Get elapsed time in milliseconds."""
        end_time = self.completion_time or time.time()
        return int((end_time - self.start_time) * 1000)
    
    @property
    def remaining_ms(self) -> int:
        """Get remaining time in milliseconds."""
        if self.status != ReflexStatus.PENDING:
            return 0
        elapsed = self.elapsed_ms
        return max(0, self.timeout_ms - elapsed)
    
    @property
    def is_expired(self) -> bool:
        """Check if the timer has expired."""
        return self.elapsed_ms >= self.timeout_ms
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "timer_id": self.timer_id,
            "operation_id": self.operation_id,
            "timeout_ms": self.timeout_ms,
            "start_time": self.start_time,
            "status": self.status.value,
            "escalation_level": self.escalation_level.value,
            "escalation_target": self.escalation_target,
            "escalation_data": self.escalation_data,
            "priority": self.priority.value,
            "context": self.context,
            "completion_time": self.completion_time,
            "elapsed_ms": self.elapsed_ms,
            "remaining_ms": self.remaining_ms,
            "is_expired": self.is_expired
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReflexTimer':
        """Create from dictionary representation."""
        return cls(
            timer_id=data["timer_id"],
            operation_id=data["operation_id"],
            timeout_ms=data["timeout_ms"],
            start_time=data["start_time"],
            status=ReflexStatus(data["status"]),
            escalation_level=EscalationLevel(data["escalation_level"]),
            escalation_target=data.get("escalation_target"),
            escalation_data=data.get("escalation_data", {}),
            priority=MessagePriority(data["priority"]),
            context=data.get("context", {}),
            completion_time=data.get("completion_time")
        )


@dataclass
class TimerStatistics:
    """
    Statistics for a type of operation.
    """
    operation_type: str
    count: int = 0
    total_time_ms: int = 0
    min_time_ms: Optional[int] = None
    max_time_ms: Optional[int] = None
    times_ms: List[int] = field(default_factory=list)
    timeout_count: int = 0
    success_count: int = 0
    
    @property
    def avg_time_ms(self) -> Optional[float]:
        """Get average time in milliseconds."""
        if self.count == 0:
            return None
        return self.total_time_ms / self.count
    
    @property
    def median_time_ms(self) -> Optional[float]:
        """Get median time in milliseconds."""
        if not self.times_ms:
            return None
        return statistics.median(self.times_ms)
    
    @property
    def percentile_90_ms(self) -> Optional[float]:
        """Get 90th percentile time in milliseconds."""
        if not self.times_ms:
            return None
        sorted_times = sorted(self.times_ms)
        index = int(len(sorted_times) * 0.9)
        return sorted_times[index]
    
    @property
    def timeout_rate(self) -> float:
        """Get timeout rate."""
        if self.count == 0:
            return 0.0
        return self.timeout_count / self.count
    
    @property
    def success_rate(self) -> float:
        """Get success rate."""
        if self.count == 0:
            return 0.0
        return self.success_count / self.count
    
    def add_time(self, time_ms: int, success: bool = True) -> None:
        """Add a time measurement."""
        self.count += 1
        self.total_time_ms += time_ms
        
        if self.min_time_ms is None or time_ms < self.min_time_ms:
            self.min_time_ms = time_ms
        
        if self.max_time_ms is None or time_ms > self.max_time_ms:
            self.max_time_ms = time_ms
        
        self.times_ms.append(time_ms)
        
        # Keep the list from growing too large
        if len(self.times_ms) > 1000:
            self.times_ms = self.times_ms[-1000:]
        
        if success:
            self.success_count += 1
        else:
            self.timeout_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "operation_type": self.operation_type,
            "count": self.count,
            "total_time_ms": self.total_time_ms,
            "min_time_ms": self.min_time_ms,
            "max_time_ms": self.max_time_ms,
            "avg_time_ms": self.avg_time_ms,
            "median_time_ms": self.median_time_ms,
            "percentile_90_ms": self.percentile_90_ms,
            "timeout_count": self.timeout_count,
            "success_count": self.success_count,
            "timeout_rate": self.timeout_rate,
            "success_rate": self.success_rate
        }


class AgentReflexTimers(ProtocolService):
    """
    Service for managing agent reflex timers.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "agent_reflex_timers")
        self.config = config or {}
        
        # Initialize storage
        self.timers: Dict[str, ReflexTimer] = {}
        self.timer_queue: List[Tuple[float, str]] = []  # (expiry_time, timer_id)
        self.operation_stats: Dict[str, TimerStatistics] = {}
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        self.timer_thread = None
        self.running = False
        self.stop_event = threading.Event()
        
        # Callbacks
        self.escalation_callbacks: Dict[EscalationLevel, Callable[[ReflexTimer], Awaitable[bool]]] = {}
        
        self.logger = logging.getLogger(f"{__name__}.AgentReflexTimers.{self.component_id[:8]}")
        self.logger.info(f"Agent Reflex Timers initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("reflex_timers", "Manage operation timeouts and escalations")
        self.add_capability("adaptive_timeouts", "Calculate optimal timeouts based on history")
        self.add_capability("escalation_paths", "Configure and execute escalation paths")
        self.add_capability("interruptible_workflows", "Support for interruptible workflows")

    async def initialize(self) -> bool:
        """Initialize the timer service."""
        self.logger.info("Initializing Agent Reflex Timers")
        
        # Start timer thread
        self.running = True
        self.stop_event.clear()
        self.timer_thread = threading.Thread(target=self._timer_loop)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        self.logger.info("Agent Reflex Timers initialized successfully")
        return True
    
    async def shutdown(self) -> bool:
        """Shutdown the timer service."""
        self.logger.info("Shutting down Agent Reflex Timers")
        
        # Stop timer thread
        self.running = False
        self.stop_event.set()
        if self.timer_thread:
            self.timer_thread.join(timeout=2.0)
        
        self.logger.info("Agent Reflex Timers shut down successfully")
        return True

    # --- Timer Management ---

    async def create_timer(
        self,
        operation_id: str,
        operation_type: str,
        timeout_ms: Optional[int] = None,
        escalation_level: EscalationLevel = EscalationLevel.NOTIFY,
        escalation_target: Optional[str] = None,
        escalation_data: Dict[str, Any] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        context: Dict[str, Any] = None
    ) -> ReflexTimer:
        """Create a new reflex timer."""
        # Generate timer ID
        timer_id = str(uuid.uuid4())
        
        # Determine timeout if not provided
        if timeout_ms is None:
            timeout_ms = await self.calculate_adaptive_timeout(operation_type)
        
        # Create timer
        timer = ReflexTimer(
            timer_id=timer_id,
            operation_id=operation_id,
            timeout_ms=timeout_ms,
            start_time=time.time(),
            status=ReflexStatus.PENDING,
            escalation_level=escalation_level,
            escalation_target=escalation_target,
            escalation_data=escalation_data or {},
            priority=priority,
            context=context or {"operation_type": operation_type}
        )
        
        # Store timer
        async with self.lock:
            self.timers[timer_id] = timer
            expiry_time = timer.start_time + (timer.timeout_ms / 1000.0)
            heapq.heappush(self.timer_queue, (expiry_time, timer_id))
        
        self.logger.debug(f"Created timer {timer_id} for operation {operation_id} with timeout {timeout_ms}ms")
        return timer

    async def complete_timer(self, timer_id: str, success: bool = True) -> Optional[ReflexTimer]:
        """Complete a timer."""
        async with self.lock:
            if timer_id not in self.timers:
                self.logger.error(f"Timer {timer_id} not found for completion")
                return None
            
            timer = self.timers[timer_id]
            
            # Skip if already completed or cancelled
            if timer.status in (ReflexStatus.COMPLETED, ReflexStatus.CANCELLED):
                return timer
            
            # Update timer
            timer.completion_time = time.time()
            timer.status = ReflexStatus.COMPLETED if success else ReflexStatus.FAILED
            
            # Update statistics
            operation_type = timer.context.get("operation_type", "unknown")
            if operation_type not in self.operation_stats:
                self.operation_stats[operation_type] = TimerStatistics(operation_type=operation_type)
            
            self.operation_stats[operation_type].add_time(timer.elapsed_ms, success)
        
        self.logger.debug(f"Completed timer {timer_id} for operation {timer.operation_id} with status {timer.status.value}")
        return timer

    async def cancel_timer(self, timer_id: str) -> Optional[ReflexTimer]:
        """Cancel a timer."""
        async with self.lock:
            if timer_id not in self.timers:
                self.logger.error(f"Timer {timer_id} not found for cancellation")
                return None
            
            timer = self.timers[timer_id]
            
            # Skip if already completed or cancelled
            if timer.status in (ReflexStatus.COMPLETED, ReflexStatus.CANCELLED):
                return timer
            
            # Update timer
            timer.completion_time = time.time()
            timer.status = ReflexStatus.CANCELLED
        
        self.logger.debug(f"Cancelled timer {timer_id} for operation {timer.operation_id}")
        return timer

    async def get_timer(self, timer_id: str) -> Optional[ReflexTimer]:
        """Get a timer by ID."""
        async with self.lock:
            if timer_id not in self.timers:
                self.logger.error(f"Timer {timer_id} not found")
                return None
            
            return self.timers[timer_id]

    async def get_timers_for_operation(self, operation_id: str) -> List[ReflexTimer]:
        """Get all timers for an operation."""
        async with self.lock:
            return [timer for timer in self.timers.values() if timer.operation_id == operation_id]

    async def get_active_timers(self) -> List[ReflexTimer]:
        """Get all active timers."""
        async with self.lock:
            return [timer for timer in self.timers.values() if timer.status == ReflexStatus.PENDING]

    # --- Timeout Calculation ---

    async def calculate_adaptive_timeout(self, operation_type: str) -> int:
        """Calculate an adaptive timeout based on historical performance."""
        async with self.lock:
            # Get statistics for this operation type
            stats = self.operation_stats.get(operation_type)
            
            if not stats or stats.count < 10:
                # Not enough data, use default timeout
                default_timeout = self.config.get("default_timeout_ms", 30000)  # 30 seconds
                self.logger.debug(f"Using default timeout {default_timeout}ms for operation type {operation_type}")
                return default_timeout
            
            # Calculate timeout based on percentiles
            if stats.percentile_90_ms:
                # Use 90th percentile with a safety factor
                safety_factor = self.config.get("timeout_safety_factor", 1.5)
                timeout = int(stats.percentile_90_ms * safety_factor)
                
                # Apply min/max bounds
                min_timeout = self.config.get("min_timeout_ms", 1000)  # 1 second
                max_timeout = self.config.get("max_timeout_ms", 300000)  # 5 minutes
                timeout = max(min_timeout, min(timeout, max_timeout))
                
                self.logger.debug(f"Calculated adaptive timeout {timeout}ms for operation type {operation_type}")
                return timeout
            else:
                # Fallback to default
                default_timeout = self.config.get("default_timeout_ms", 30000)  # 30 seconds
                self.logger.debug(f"Using default timeout {default_timeout}ms for operation type {operation_type}")
                return default_timeout

    async def get_operation_statistics(self, operation_type: Optional[str] = None) -> Union[Dict[str, Any], Dict[str, Dict[str, Any]]]:
        """Get statistics for operations."""
        async with self.lock:
            if operation_type:
                stats = self.operation_stats.get(operation_type)
                if not stats:
                    return {}
                return stats.to_dict()
            else:
                return {op_type: stats.to_dict() for op_type, stats in self.operation_stats.items()}

    # --- Escalation Management ---

    async def register_escalation_callback(
        self,
        escalation_level: EscalationLevel,
        callback: Callable[[ReflexTimer], Awaitable[bool]]
    ) -> bool:
        """Register a callback for an escalation level."""
        async with self.lock:
            self.escalation_callbacks[escalation_level] = callback
        
        self.logger.debug(f"Registered escalation callback for level {escalation_level.value}")
        return True

    async def trigger_escalation(self, timer_id: str) -> bool:
        """Trigger escalation for a timer."""
        async with self.lock:
            if timer_id not in self.timers:
                self.logger.error(f"Timer {timer_id} not found for escalation")
                return False
            
            timer = self.timers[timer_id]
            
            # Skip if not pending
            if timer.status != ReflexStatus.PENDING:
                self.logger.warning(f"Cannot escalate timer {timer_id} with status {timer.status.value}")
                return False
            
            # Update timer
            timer.status = ReflexStatus.ESCALATED
            
            # Get callback for this escalation level
            callback = self.escalation_callbacks.get(timer.escalation_level)
        
        # Execute callback outside of lock
        if callback:
            try:
                success = await callback(timer)
                self.logger.info(f"Escalation for timer {timer_id} completed with success={success}")
                return success
            except Exception as e:
                self.logger.error(f"Error in escalation callback for timer {timer_id}: {str(e)}")
                return False
        else:
            self.logger.warning(f"No escalation callback registered for level {timer.escalation_level.value}")
            return False

    # --- Timer Thread ---

    def _timer_loop(self) -> None:
        """Background thread for processing timers."""
        self.logger.info("Timer thread started")
        
        while self.running:
            try:
                self._process_timers()
                
                # Wait for stop event or timeout
                self.stop_event.wait(timeout=0.1)
            except Exception as e:
                self.logger.error(f"Error in timer thread: {str(e)}")
        
        self.logger.info("Timer thread stopped")

    def _process_timers(self) -> None:
        """Process expired timers."""
        now = time.time()
        expired_timers = []
        
        # Get expired timers
        with self._sync_lock():
            while self.timer_queue and self.timer_queue[0][0] <= now:
                expiry_time, timer_id = heapq.heappop(self.timer_queue)
                
                if timer_id in self.timers:
                    timer = self.timers[timer_id]
                    
                    # Only process pending timers
                    if timer.status == ReflexStatus.PENDING:
                        expired_timers.append(timer_id)
        
        # Process expired timers
        for timer_id in expired_timers:
            self._trigger_timer_expiry(timer_id)

    def _trigger_timer_expiry(self, timer_id: str) -> None:
        """Trigger expiry for a timer."""
        # Create task in event loop
        asyncio.run_coroutine_threadsafe(self._handle_timer_expiry(timer_id), asyncio.get_event_loop())

    async def _handle_timer_expiry(self, timer_id: str) -> None:
        """Handle timer expiry."""
        async with self.lock:
            if timer_id not in self.timers:
                return
            
            timer = self.timers[timer_id]
            
            # Skip if not pending
            if timer.status != ReflexStatus.PENDING:
                return
            
            # Update timer
            timer.status = ReflexStatus.TRIGGERED
            
            # Update statistics
            operation_type = timer.context.get("operation_type", "unknown")
            if operation_type not in self.operation_stats:
                self.operation_stats[operation_type] = TimerStatistics(operation_type=operation_type)
            
            self.operation_stats[operation_type].add_time(timer.timeout_ms, False)
        
        self.logger.info(f"Timer {timer_id} for operation {timer.operation_id} expired")
        
        # Trigger escalation
        await self.trigger_escalation(timer_id)

    def _sync_lock(self):
        """Create a synchronous lock for the timer thread."""
        class SyncLock:
            def __enter__(self_):
                # Acquire lock in the event loop
                future = asyncio.run_coroutine_threadsafe(self.lock.acquire(), asyncio.get_event_loop())
                future.result()  # Wait for lock
                return self_
            
            def __exit__(self_, exc_type, exc_val, exc_tb):
                # Release lock in the event loop
                asyncio.run_coroutine_threadsafe(self.lock.release(), asyncio.get_event_loop())
        
        return SyncLock()

    # --- Message Handling ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "create_timer":
                params = msg_obj.params
                timer = await self.create_timer(
                    operation_id=params.get("operation_id", str(uuid.uuid4())),
                    operation_type=params.get("operation_type", "unknown"),
                    timeout_ms=params.get("timeout_ms"),
                    escalation_level=EscalationLevel(params.get("escalation_level", "notify")),
                    escalation_target=params.get("escalation_target"),
                    escalation_data=params.get("escalation_data"),
                    priority=MessagePriority(params.get("priority", "normal")),
                    context=params.get("context")
                )
                response_payload = timer.to_dict()
            
            elif msg_obj.command == "complete_timer":
                params = msg_obj.params
                if "timer_id" in params:
                    timer = await self.complete_timer(
                        timer_id=params["timer_id"],
                        success=params.get("success", True)
                    )
                    if timer:
                        response_payload = timer.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Timer not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing timer_id parameter"}
            
            elif msg_obj.command == "cancel_timer":
                params = msg_obj.params
                if "timer_id" in params:
                    timer = await self.cancel_timer(params["timer_id"])
                    if timer:
                        response_payload = timer.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Timer not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing timer_id parameter"}
            
            elif msg_obj.command == "trigger_escalation":
                params = msg_obj.params
                if "timer_id" in params:
                    success = await self.trigger_escalation(params["timer_id"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing timer_id parameter"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_timer":
                params = msg_obj.params
                if "timer_id" in params:
                    timer = await self.get_timer(params["timer_id"])
                    if timer:
                        response_payload = timer.to_dict()
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Timer not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing timer_id parameter"}
            
            elif msg_obj.query == "get_timers_for_operation":
                params = msg_obj.params
                if "operation_id" in params:
                    timers = await self.get_timers_for_operation(params["operation_id"])
                    response_payload = {"timers": [timer.to_dict() for timer in timers]}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing operation_id parameter"}
            
            elif msg_obj.query == "get_active_timers":
                timers = await self.get_active_timers()
                response_payload = {"timers": [timer.to_dict() for timer in timers]}
            
            elif msg_obj.query == "get_operation_statistics":
                params = msg_obj.params
                stats = await self.get_operation_statistics(params.get("operation_type"))
                response_payload = {"statistics": stats}
            
            elif msg_obj.query == "calculate_adaptive_timeout":
                params = msg_obj.params
                if "operation_type" in params:
                    timeout = await self.calculate_adaptive_timeout(params["operation_type"])
                    response_payload = {"timeout_ms": timeout}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing operation_type parameter"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        else:
            status = MessageStatus.FAILED
            response_payload = {"error": "Unsupported message type"}

        # Create response
        response = MessageFactory.create_response(
            correlation_id=msg_obj.message_id,
            status=status,
            payload=response_payload,
            sender_id=self.component_id,
            receiver_id=msg_obj.sender_id
        )
        return response.to_dict()

    def process_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a message (synchronous wrapper)."""
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(self.process_message_async(message))
        finally:
            loop.close()

    async def health_check(self) -> Dict[str, Any]:
        """Perform a health check."""
        async with self.lock:
            num_timers = len(self.timers)
            num_active = len([t for t in self.timers.values() if t.status == ReflexStatus.PENDING])
            num_stats = len(self.operation_stats)
        
        return {
            "status": "healthy",
            "total_timers": num_timers,
            "active_timers": num_active,
            "operation_types": num_stats,
            "timer_thread_running": self.running and self.timer_thread and self.timer_thread.is_alive()
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
