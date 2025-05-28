"""
Time-Locked Capsule Contracts Module for the Security & Compliance Layer of Industriverse.

This module implements a comprehensive Time-Locked Capsule Contracts system that provides:
- Time-bound and event-bound locks for capsules
- Temporal access control and execution constraints
- Scheduled privilege escalation and de-escalation
- Temporal compliance verification
- Integration with the Capsule Framework

The Time-Locked Capsule Contracts system is a critical component of the Security & Compliance Layer,
enabling temporal governance of capsule execution and access across the Industriverse ecosystem.
"""

import os
import time
import uuid
import json
import logging
import hashlib
import base64
from typing import Dict, List, Optional, Tuple, Union, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading
import heapq

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class LockType(Enum):
    """Enumeration of lock types for time-locked capsule contracts."""
    TIME_BOUND = "time_bound"
    EVENT_BOUND = "event_bound"
    HYBRID = "hybrid"

class LockOperation(Enum):
    """Enumeration of lock operations for time-locked capsule contracts."""
    LOCK = "lock"
    UNLOCK = "unlock"
    ESCALATE = "escalate"
    DEESCALATE = "deescalate"

class TimeLockStatus(Enum):
    """Enumeration of time lock statuses."""
    PENDING = "pending"
    ACTIVE = "active"
    EXPIRED = "expired"
    TRIGGERED = "triggered"
    CANCELED = "canceled"

class TimeLockedCapsuleContracts:
    """
    Time-Locked Capsule Contracts for the Security & Compliance Layer.
    
    This class provides comprehensive time-locked contract services including:
    - Time-bound and event-bound locks for capsules
    - Temporal access control and execution constraints
    - Scheduled privilege escalation and de-escalation
    - Temporal compliance verification
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Time-Locked Capsule Contracts system with configuration.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.time_locks = {}
        self.event_locks = {}
        self.lock_history = {}
        self.scheduled_operations = []
        self.event_listeners = {}
        
        # Initialize scheduler thread
        self._scheduler_running = False
        self._scheduler_thread = None
        
        # Initialize from configuration
        self._initialize_from_config()
        
        # Start scheduler if enabled
        if self.config["scheduler"]["enabled"]:
            self._start_scheduler()
        
        logger.info("Time-Locked Capsule Contracts system initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """
        Load configuration from file or use defaults.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing configuration
        """
        default_config = {
            "lock_types": {
                "time_bound": {
                    "enabled": True,
                    "default_duration_seconds": 3600,  # 1 hour
                    "max_duration_seconds": 31536000,  # 1 year
                    "grace_period_seconds": 300  # 5 minutes
                },
                "event_bound": {
                    "enabled": True,
                    "default_timeout_seconds": 86400,  # 1 day
                    "max_timeout_seconds": 2592000,  # 30 days
                    "max_events_per_lock": 10
                },
                "hybrid": {
                    "enabled": True,
                    "default_duration_seconds": 3600,  # 1 hour
                    "max_duration_seconds": 31536000,  # 1 year
                    "default_timeout_seconds": 86400,  # 1 day
                    "max_timeout_seconds": 2592000  # 30 days
                }
            },
            "operations": {
                "lock": {
                    "enabled": True,
                    "requires_approval": False,
                    "approval_threshold": "medium"  # low, medium, high
                },
                "unlock": {
                    "enabled": True,
                    "requires_approval": True,
                    "approval_threshold": "high"  # low, medium, high
                },
                "escalate": {
                    "enabled": True,
                    "requires_approval": True,
                    "approval_threshold": "high"  # low, medium, high
                },
                "deescalate": {
                    "enabled": True,
                    "requires_approval": False,
                    "approval_threshold": "medium"  # low, medium, high
                }
            },
            "scheduler": {
                "enabled": True,
                "check_interval_seconds": 10,
                "max_operations_per_batch": 100
            },
            "compliance": {
                "verification_enabled": True,
                "verification_interval_seconds": 3600,  # 1 hour
                "audit_trail_enabled": True,
                "retention_days": 365
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_config.items():
                        if isinstance(value, dict) and key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
                logger.info(f"Configuration loaded from {config_path}")
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        return default_config
    
    def _initialize_from_config(self):
        """Initialize time-locked capsule contracts system from configuration."""
        # Nothing specific to initialize from config at this point
        pass
    
    def _start_scheduler(self):
        """Start the scheduler thread for time-based operations."""
        if self._scheduler_running:
            return
        
        self._scheduler_running = True
        self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self._scheduler_thread.start()
        
        logger.info("Time-locked capsule contracts scheduler started")
    
    def _stop_scheduler(self):
        """Stop the scheduler thread."""
        if not self._scheduler_running:
            return
        
        self._scheduler_running = False
        if self._scheduler_thread:
            self._scheduler_thread.join(timeout=5.0)
            self._scheduler_thread = None
        
        logger.info("Time-locked capsule contracts scheduler stopped")
    
    def _scheduler_loop(self):
        """Main loop for the scheduler thread."""
        while self._scheduler_running:
            try:
                self._process_scheduled_operations()
                self._check_time_locks()
                
                # Sleep for the configured interval
                time.sleep(self.config["scheduler"]["check_interval_seconds"])
            except Exception as e:
                logger.error(f"Error in scheduler loop: {str(e)}")
                # Sleep briefly to avoid tight loop in case of persistent errors
                time.sleep(1.0)
    
    def _process_scheduled_operations(self):
        """Process scheduled operations that are due."""
        if not self.scheduled_operations:
            return
        
        current_time = datetime.utcnow()
        operations_to_process = []
        
        # Find operations that are due
        while self.scheduled_operations and len(operations_to_process) < self.config["scheduler"]["max_operations_per_batch"]:
            # Peek at the next operation
            next_time, operation = self.scheduled_operations[0]
            
            if next_time <= current_time:
                # Remove from the heap and add to processing list
                heapq.heappop(self.scheduled_operations)
                operations_to_process.append(operation)
            else:
                # No more operations are due
                break
        
        # Process the operations
        for operation in operations_to_process:
            try:
                self._execute_scheduled_operation(operation)
            except Exception as e:
                logger.error(f"Error executing scheduled operation: {str(e)}")
    
    def _execute_scheduled_operation(self, operation: Dict):
        """
        Execute a scheduled operation.
        
        Args:
            operation: Operation to execute
        """
        operation_type = operation.get("type")
        lock_id = operation.get("lock_id")
        
        if operation_type == "check_time_lock":
            # Check if a time lock has expired
            self._check_time_lock_expiration(lock_id)
        
        elif operation_type == "execute_lock_operation":
            # Execute a lock operation
            lock_operation = operation.get("lock_operation")
            capsule_id = operation.get("capsule_id")
            parameters = operation.get("parameters", {})
            
            if lock_operation == LockOperation.LOCK.value:
                self._execute_lock(lock_id, capsule_id, parameters)
            
            elif lock_operation == LockOperation.UNLOCK.value:
                self._execute_unlock(lock_id, capsule_id, parameters)
            
            elif lock_operation == LockOperation.ESCALATE.value:
                self._execute_escalate(lock_id, capsule_id, parameters)
            
            elif lock_operation == LockOperation.DEESCALATE.value:
                self._execute_deescalate(lock_id, capsule_id, parameters)
    
    def _check_time_locks(self):
        """Check all active time locks for expiration."""
        current_time = datetime.utcnow()
        
        for lock_id, lock in list(self.time_locks.items()):
            if lock["status"] == TimeLockStatus.ACTIVE.value:
                expiration_time = datetime.fromisoformat(lock["expiration_time"])
                
                if current_time >= expiration_time:
                    self._handle_time_lock_expiration(lock_id, lock)
    
    def _check_time_lock_expiration(self, lock_id: str):
        """
        Check if a specific time lock has expired.
        
        Args:
            lock_id: Lock identifier
        """
        if lock_id not in self.time_locks:
            logger.warning(f"Time lock {lock_id} not found for expiration check")
            return
        
        lock = self.time_locks[lock_id]
        
        if lock["status"] != TimeLockStatus.ACTIVE.value:
            return
        
        current_time = datetime.utcnow()
        expiration_time = datetime.fromisoformat(lock["expiration_time"])
        
        if current_time >= expiration_time:
            self._handle_time_lock_expiration(lock_id, lock)
    
    def _handle_time_lock_expiration(self, lock_id: str, lock: Dict):
        """
        Handle the expiration of a time lock.
        
        Args:
            lock_id: Lock identifier
            lock: Lock data
        """
        # Update lock status
        lock["status"] = TimeLockStatus.EXPIRED.value
        lock["expired_at"] = datetime.utcnow().isoformat()
        
        # Execute the configured expiration action
        expiration_action = lock.get("expiration_action")
        
        if expiration_action:
            action_type = expiration_action.get("type")
            
            if action_type == "unlock":
                # Automatically unlock the capsule
                capsule_id = lock["capsule_id"]
                self._execute_unlock(lock_id, capsule_id, {"automatic": True})
            
            elif action_type == "deescalate":
                # Automatically de-escalate privileges
                capsule_id = lock["capsule_id"]
                self._execute_deescalate(lock_id, capsule_id, {"automatic": True})
            
            elif action_type == "notify":
                # Notification would be handled by an external system
                logger.info(f"Time lock {lock_id} expired with notify action")
        
        logger.info(f"Time lock {lock_id} for capsule {lock['capsule_id']} has expired")
    
    def _execute_lock(self, lock_id: str, capsule_id: str, parameters: Dict):
        """
        Execute a lock operation.
        
        Args:
            lock_id: Lock identifier
            capsule_id: Capsule identifier
            parameters: Operation parameters
        """
        if lock_id not in self.time_locks:
            logger.warning(f"Time lock {lock_id} not found for lock operation")
            return
        
        lock = self.time_locks[lock_id]
        
        # Update lock status
        lock["status"] = TimeLockStatus.ACTIVE.value
        lock["activated_at"] = datetime.utcnow().isoformat()
        
        # Record the operation in history
        self._record_lock_operation(lock_id, LockOperation.LOCK.value, parameters)
        
        logger.info(f"Executed lock operation for lock {lock_id} on capsule {capsule_id}")
    
    def _execute_unlock(self, lock_id: str, capsule_id: str, parameters: Dict):
        """
        Execute an unlock operation.
        
        Args:
            lock_id: Lock identifier
            capsule_id: Capsule identifier
            parameters: Operation parameters
        """
        if lock_id not in self.time_locks:
            logger.warning(f"Time lock {lock_id} not found for unlock operation")
            return
        
        lock = self.time_locks[lock_id]
        
        # Update lock status
        previous_status = lock["status"]
        lock["status"] = TimeLockStatus.EXPIRED.value
        lock["unlocked_at"] = datetime.utcnow().isoformat()
        
        # Record the operation in history
        self._record_lock_operation(lock_id, LockOperation.UNLOCK.value, parameters)
        
        logger.info(f"Executed unlock operation for lock {lock_id} on capsule {capsule_id} (previous status: {previous_status})")
    
    def _execute_escalate(self, lock_id: str, capsule_id: str, parameters: Dict):
        """
        Execute a privilege escalation operation.
        
        Args:
            lock_id: Lock identifier
            capsule_id: Capsule identifier
            parameters: Operation parameters
        """
        if lock_id not in self.time_locks:
            logger.warning(f"Time lock {lock_id} not found for escalate operation")
            return
        
        lock = self.time_locks[lock_id]
        
        # Update lock privileges
        if "privileges" not in lock:
            lock["privileges"] = {}
        
        # Apply the escalation
        escalation = parameters.get("escalation", {})
        for privilege, level in escalation.items():
            lock["privileges"][privilege] = level
        
        lock["escalated_at"] = datetime.utcnow().isoformat()
        
        # Record the operation in history
        self._record_lock_operation(lock_id, LockOperation.ESCALATE.value, parameters)
        
        logger.info(f"Executed privilege escalation for lock {lock_id} on capsule {capsule_id}")
    
    def _execute_deescalate(self, lock_id: str, capsule_id: str, parameters: Dict):
        """
        Execute a privilege de-escalation operation.
        
        Args:
            lock_id: Lock identifier
            capsule_id: Capsule identifier
            parameters: Operation parameters
        """
        if lock_id not in self.time_locks:
            logger.warning(f"Time lock {lock_id} not found for deescalate operation")
            return
        
        lock = self.time_locks[lock_id]
        
        # Update lock privileges
        if "privileges" not in lock:
            lock["privileges"] = {}
        
        # Apply the de-escalation
        deescalation = parameters.get("deescalation", {})
        for privilege, level in deescalation.items():
            if privilege in lock["privileges"]:
                lock["privileges"][privilege] = level
        
        lock["deescalated_at"] = datetime.utcnow().isoformat()
        
        # Record the operation in history
        self._record_lock_operation(lock_id, LockOperation.DEESCALATE.value, parameters)
        
        logger.info(f"Executed privilege de-escalation for lock {lock_id} on capsule {capsule_id}")
    
    def _record_lock_operation(self, lock_id: str, operation: str, parameters: Dict):
        """
        Record a lock operation in the history.
        
        Args:
            lock_id: Lock identifier
            operation: Operation type
            parameters: Operation parameters
        """
        if lock_id not in self.lock_history:
            self.lock_history[lock_id] = []
        
        operation_record = {
            "operation_id": str(uuid.uuid4()),
            "lock_id": lock_id,
            "operation": operation,
            "parameters": parameters,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": {
                "type": "lock_operation",
                "source": "time_locked_capsule_contracts"
            }
        }
        
        self.lock_history[lock_id].append(operation_record)
    
    def create_time_bound_lock(self, capsule_id: str, duration_seconds: int = None, 
                              expiration_action: Dict = None, metadata: Dict = None) -> Dict:
        """
        Create a time-bound lock for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            duration_seconds: Lock duration in seconds (default: from config)
            expiration_action: Action to take when the lock expires
            metadata: Additional metadata for the lock
            
        Returns:
            Dict containing the created lock
        """
        # Check if time-bound locks are enabled
        if not self.config["lock_types"]["time_bound"]["enabled"]:
            raise ValueError("Time-bound locks are not enabled")
        
        # Use default duration if not specified
        if duration_seconds is None:
            duration_seconds = self.config["lock_types"]["time_bound"]["default_duration_seconds"]
        
        # Validate duration
        max_duration = self.config["lock_types"]["time_bound"]["max_duration_seconds"]
        if duration_seconds > max_duration:
            raise ValueError(f"Lock duration exceeds maximum allowed ({max_duration} seconds)")
        
        # Generate lock ID
        lock_id = str(uuid.uuid4())
        
        # Calculate expiration time
        creation_time = datetime.utcnow()
        expiration_time = creation_time + timedelta(seconds=duration_seconds)
        
        # Create the lock
        lock = {
            "lock_id": lock_id,
            "capsule_id": capsule_id,
            "type": LockType.TIME_BOUND.value,
            "status": TimeLockStatus.PENDING.value,
            "creation_time": creation_time.isoformat(),
            "expiration_time": expiration_time.isoformat(),
            "duration_seconds": duration_seconds,
            "expiration_action": expiration_action,
            "metadata": metadata or {}
        }
        
        # Add type-specific metadata
        lock["metadata"]["type"] = "time_bound_lock"
        lock["metadata"]["source"] = "time_locked_capsule_contracts"
        
        # Store the lock
        self.time_locks[lock_id] = lock
        
        # Schedule expiration check
        self._schedule_time_lock_expiration_check(lock_id, expiration_time)
        
        logger.info(f"Created time-bound lock {lock_id} for capsule {capsule_id} with duration {duration_seconds} seconds")
        
        return lock
    
    def create_event_bound_lock(self, capsule_id: str, event_conditions: List[Dict], 
                               timeout_seconds: int = None, expiration_action: Dict = None, 
                               metadata: Dict = None) -> Dict:
        """
        Create an event-bound lock for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            event_conditions: List of event conditions that trigger the lock
            timeout_seconds: Lock timeout in seconds (default: from config)
            expiration_action: Action to take when the lock expires
            metadata: Additional metadata for the lock
            
        Returns:
            Dict containing the created lock
        """
        # Check if event-bound locks are enabled
        if not self.config["lock_types"]["event_bound"]["enabled"]:
            raise ValueError("Event-bound locks are not enabled")
        
        # Validate event conditions
        if not event_conditions:
            raise ValueError("At least one event condition is required")
        
        max_events = self.config["lock_types"]["event_bound"]["max_events_per_lock"]
        if len(event_conditions) > max_events:
            raise ValueError(f"Number of event conditions exceeds maximum allowed ({max_events})")
        
        # Use default timeout if not specified
        if timeout_seconds is None:
            timeout_seconds = self.config["lock_types"]["event_bound"]["default_timeout_seconds"]
        
        # Validate timeout
        max_timeout = self.config["lock_types"]["event_bound"]["max_timeout_seconds"]
        if timeout_seconds > max_timeout:
            raise ValueError(f"Lock timeout exceeds maximum allowed ({max_timeout} seconds)")
        
        # Generate lock ID
        lock_id = str(uuid.uuid4())
        
        # Calculate timeout time
        creation_time = datetime.utcnow()
        timeout_time = creation_time + timedelta(seconds=timeout_seconds)
        
        # Create the lock
        lock = {
            "lock_id": lock_id,
            "capsule_id": capsule_id,
            "type": LockType.EVENT_BOUND.value,
            "status": TimeLockStatus.PENDING.value,
            "creation_time": creation_time.isoformat(),
            "timeout_time": timeout_time.isoformat(),
            "timeout_seconds": timeout_seconds,
            "event_conditions": event_conditions,
            "expiration_action": expiration_action,
            "metadata": metadata or {}
        }
        
        # Add type-specific metadata
        lock["metadata"]["type"] = "event_bound_lock"
        lock["metadata"]["source"] = "time_locked_capsule_contracts"
        
        # Store the lock
        self.event_locks[lock_id] = lock
        
        # Register event listeners
        self._register_event_listeners(lock_id, event_conditions)
        
        # Schedule timeout check
        self._schedule_event_lock_timeout_check(lock_id, timeout_time)
        
        logger.info(f"Created event-bound lock {lock_id} for capsule {capsule_id} with {len(event_conditions)} conditions")
        
        return lock
    
    def create_hybrid_lock(self, capsule_id: str, duration_seconds: int = None, 
                          event_conditions: List[Dict] = None, timeout_seconds: int = None,
                          expiration_action: Dict = None, metadata: Dict = None) -> Dict:
        """
        Create a hybrid (time and event bound) lock for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            duration_seconds: Lock duration in seconds (default: from config)
            event_conditions: List of event conditions that trigger the lock
            timeout_seconds: Lock timeout in seconds (default: from config)
            expiration_action: Action to take when the lock expires
            metadata: Additional metadata for the lock
            
        Returns:
            Dict containing the created lock
        """
        # Check if hybrid locks are enabled
        if not self.config["lock_types"]["hybrid"]["enabled"]:
            raise ValueError("Hybrid locks are not enabled")
        
        # Use default duration if not specified
        if duration_seconds is None:
            duration_seconds = self.config["lock_types"]["hybrid"]["default_duration_seconds"]
        
        # Validate duration
        max_duration = self.config["lock_types"]["hybrid"]["max_duration_seconds"]
        if duration_seconds > max_duration:
            raise ValueError(f"Lock duration exceeds maximum allowed ({max_duration} seconds)")
        
        # Use default timeout if not specified
        if timeout_seconds is None:
            timeout_seconds = self.config["lock_types"]["hybrid"]["default_timeout_seconds"]
        
        # Validate timeout
        max_timeout = self.config["lock_types"]["hybrid"]["max_timeout_seconds"]
        if timeout_seconds > max_timeout:
            raise ValueError(f"Lock timeout exceeds maximum allowed ({max_timeout} seconds)")
        
        # Validate event conditions
        if not event_conditions:
            event_conditions = []
        
        max_events = self.config["lock_types"]["event_bound"]["max_events_per_lock"]
        if len(event_conditions) > max_events:
            raise ValueError(f"Number of event conditions exceeds maximum allowed ({max_events})")
        
        # Generate lock ID
        lock_id = str(uuid.uuid4())
        
        # Calculate expiration and timeout times
        creation_time = datetime.utcnow()
        expiration_time = creation_time + timedelta(seconds=duration_seconds)
        timeout_time = creation_time + timedelta(seconds=timeout_seconds)
        
        # Create the lock
        lock = {
            "lock_id": lock_id,
            "capsule_id": capsule_id,
            "type": LockType.HYBRID.value,
            "status": TimeLockStatus.PENDING.value,
            "creation_time": creation_time.isoformat(),
            "expiration_time": expiration_time.isoformat(),
            "timeout_time": timeout_time.isoformat(),
            "duration_seconds": duration_seconds,
            "timeout_seconds": timeout_seconds,
            "event_conditions": event_conditions,
            "expiration_action": expiration_action,
            "metadata": metadata or {}
        }
        
        # Add type-specific metadata
        lock["metadata"]["type"] = "hybrid_lock"
        lock["metadata"]["source"] = "time_locked_capsule_contracts"
        
        # Store the lock
        self.time_locks[lock_id] = lock
        
        # Register event listeners if there are event conditions
        if event_conditions:
            self._register_event_listeners(lock_id, event_conditions)
        
        # Schedule expiration check
        self._schedule_time_lock_expiration_check(lock_id, expiration_time)
        
        logger.info(f"Created hybrid lock {lock_id} for capsule {capsule_id} with duration {duration_seconds} seconds and {len(event_conditions)} conditions")
        
        return lock
    
    def _schedule_time_lock_expiration_check(self, lock_id: str, expiration_time: datetime):
        """
        Schedule a check for time lock expiration.
        
        Args:
            lock_id: Lock identifier
            expiration_time: Expiration time
        """
        operation = {
            "type": "check_time_lock",
            "lock_id": lock_id
        }
        
        heapq.heappush(self.scheduled_operations, (expiration_time, operation))
    
    def _schedule_event_lock_timeout_check(self, lock_id: str, timeout_time: datetime):
        """
        Schedule a check for event lock timeout.
        
        Args:
            lock_id: Lock identifier
            timeout_time: Timeout time
        """
        operation = {
            "type": "check_event_lock_timeout",
            "lock_id": lock_id
        }
        
        heapq.heappush(self.scheduled_operations, (timeout_time, operation))
    
    def _register_event_listeners(self, lock_id: str, event_conditions: List[Dict]):
        """
        Register event listeners for an event-bound lock.
        
        Args:
            lock_id: Lock identifier
            event_conditions: List of event conditions
        """
        # In a production environment, this would register actual event listeners
        # For this implementation, we'll just store the conditions
        
        for condition in event_conditions:
            event_type = condition.get("event_type")
            
            if event_type not in self.event_listeners:
                self.event_listeners[event_type] = {}
            
            self.event_listeners[event_type][lock_id] = condition
    
    def _unregister_event_listeners(self, lock_id: str):
        """
        Unregister event listeners for a lock.
        
        Args:
            lock_id: Lock identifier
        """
        # In a production environment, this would unregister actual event listeners
        # For this implementation, we'll just remove the conditions
        
        for event_type, listeners in list(self.event_listeners.items()):
            if lock_id in listeners:
                del listeners[lock_id]
            
            # Clean up empty event types
            if not listeners:
                del self.event_listeners[event_type]
    
    def process_event(self, event: Dict) -> List[Dict]:
        """
        Process an event and trigger any matching event-bound locks.
        
        Args:
            event: Event data
            
        Returns:
            List of triggered locks
        """
        event_type = event.get("event_type")
        
        if event_type not in self.event_listeners:
            return []
        
        triggered_locks = []
        
        # Check each listener for this event type
        for lock_id, condition in list(self.event_listeners[event_type].items()):
            # Check if the lock exists
            lock = self.event_locks.get(lock_id)
            if not lock:
                # Lock may have been deleted, remove the listener
                del self.event_listeners[event_type][lock_id]
                continue
            
            # Check if the lock is in a state that can be triggered
            if lock["status"] != TimeLockStatus.PENDING.value and lock["status"] != TimeLockStatus.ACTIVE.value:
                continue
            
            # Check if the event matches the condition
            if self._event_matches_condition(event, condition):
                # Trigger the lock
                self._trigger_event_lock(lock_id, lock, event)
                triggered_locks.append(lock)
        
        return triggered_locks
    
    def _event_matches_condition(self, event: Dict, condition: Dict) -> bool:
        """
        Check if an event matches a condition.
        
        Args:
            event: Event data
            condition: Event condition
            
        Returns:
            True if the event matches the condition, False otherwise
        """
        # Check event type
        if event.get("event_type") != condition.get("event_type"):
            return False
        
        # Check additional criteria if specified
        criteria = condition.get("criteria", {})
        
        for key, value in criteria.items():
            # Navigate the event data using dot notation
            event_value = self._get_nested_value(event, key)
            
            # Check if the value matches
            if isinstance(value, dict) and "operator" in value:
                # Complex condition with operator
                operator = value["operator"]
                operand = value.get("value")
                
                if not self._evaluate_condition(event_value, operator, operand):
                    return False
            else:
                # Simple equality check
                if event_value != value:
                    return False
        
        return True
    
    def _get_nested_value(self, obj: Dict, path: str) -> Any:
        """
        Get a nested value from an object using dot notation.
        
        Args:
            obj: Object to get value from
            path: Dot-separated path to the value
            
        Returns:
            The value at the specified path, or None if not found
        """
        if not path:
            return None
        
        parts = path.split(".")
        current = obj
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    def _evaluate_condition(self, value: Any, operator: str, operand: Any) -> bool:
        """
        Evaluate a condition using the specified operator.
        
        Args:
            value: Value to evaluate
            operator: Operator to use
            operand: Operand to compare with
            
        Returns:
            True if the condition is satisfied, False otherwise
        """
        if operator == "eq":
            return value == operand
        elif operator == "ne":
            return value != operand
        elif operator == "gt":
            return value > operand
        elif operator == "ge":
            return value >= operand
        elif operator == "lt":
            return value < operand
        elif operator == "le":
            return value <= operand
        elif operator == "in":
            return value in operand
        elif operator == "not_in":
            return value not in operand
        elif operator == "contains":
            return operand in value
        elif operator == "not_contains":
            return operand not in value
        elif operator == "starts_with":
            return value.startswith(operand)
        elif operator == "ends_with":
            return value.endswith(operand)
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _trigger_event_lock(self, lock_id: str, lock: Dict, event: Dict):
        """
        Trigger an event-bound lock.
        
        Args:
            lock_id: Lock identifier
            lock: Lock data
            event: Triggering event
        """
        # Update lock status
        lock["status"] = TimeLockStatus.TRIGGERED.value
        lock["triggered_at"] = datetime.utcnow().isoformat()
        lock["triggering_event"] = event
        
        # Execute the configured trigger action
        trigger_action = lock.get("trigger_action")
        
        if trigger_action:
            action_type = trigger_action.get("type")
            
            if action_type == "lock":
                # Automatically lock the capsule
                capsule_id = lock["capsule_id"]
                self._execute_lock(lock_id, capsule_id, {"automatic": True, "event": event})
            
            elif action_type == "escalate":
                # Automatically escalate privileges
                capsule_id = lock["capsule_id"]
                escalation = trigger_action.get("escalation", {})
                self._execute_escalate(lock_id, capsule_id, {"automatic": True, "event": event, "escalation": escalation})
            
            elif action_type == "notify":
                # Notification would be handled by an external system
                logger.info(f"Event lock {lock_id} triggered with notify action")
        
        # Unregister event listeners for this lock
        self._unregister_event_listeners(lock_id)
        
        logger.info(f"Event lock {lock_id} for capsule {lock['capsule_id']} triggered by event {event.get('event_type')}")
    
    def activate_lock(self, lock_id: str) -> Dict:
        """
        Activate a pending lock.
        
        Args:
            lock_id: Lock identifier
            
        Returns:
            Updated lock data
        """
        # Check if the lock exists
        if lock_id in self.time_locks:
            lock = self.time_locks[lock_id]
        elif lock_id in self.event_locks:
            lock = self.event_locks[lock_id]
        else:
            raise ValueError(f"Lock {lock_id} not found")
        
        # Check if the lock is in pending status
        if lock["status"] != TimeLockStatus.PENDING.value:
            raise ValueError(f"Lock {lock_id} is not in pending status")
        
        # Update lock status
        lock["status"] = TimeLockStatus.ACTIVE.value
        lock["activated_at"] = datetime.utcnow().isoformat()
        
        # Record the operation in history
        self._record_lock_operation(lock_id, "activate", {})
        
        logger.info(f"Activated lock {lock_id} for capsule {lock['capsule_id']}")
        
        return lock
    
    def deactivate_lock(self, lock_id: str) -> Dict:
        """
        Deactivate an active lock.
        
        Args:
            lock_id: Lock identifier
            
        Returns:
            Updated lock data
        """
        # Check if the lock exists
        if lock_id in self.time_locks:
            lock = self.time_locks[lock_id]
        elif lock_id in self.event_locks:
            lock = self.event_locks[lock_id]
        else:
            raise ValueError(f"Lock {lock_id} not found")
        
        # Check if the lock is in active status
        if lock["status"] != TimeLockStatus.ACTIVE.value:
            raise ValueError(f"Lock {lock_id} is not in active status")
        
        # Update lock status
        lock["status"] = TimeLockStatus.PENDING.value
        lock["deactivated_at"] = datetime.utcnow().isoformat()
        
        # Record the operation in history
        self._record_lock_operation(lock_id, "deactivate", {})
        
        logger.info(f"Deactivated lock {lock_id} for capsule {lock['capsule_id']}")
        
        return lock
    
    def cancel_lock(self, lock_id: str) -> Dict:
        """
        Cancel a lock.
        
        Args:
            lock_id: Lock identifier
            
        Returns:
            Updated lock data
        """
        # Check if the lock exists
        if lock_id in self.time_locks:
            lock = self.time_locks[lock_id]
        elif lock_id in self.event_locks:
            lock = self.event_locks[lock_id]
        else:
            raise ValueError(f"Lock {lock_id} not found")
        
        # Check if the lock can be canceled
        if lock["status"] not in [TimeLockStatus.PENDING.value, TimeLockStatus.ACTIVE.value]:
            raise ValueError(f"Lock {lock_id} cannot be canceled in its current status")
        
        # Update lock status
        lock["status"] = TimeLockStatus.CANCELED.value
        lock["canceled_at"] = datetime.utcnow().isoformat()
        
        # Unregister event listeners if this is an event-bound lock
        if lock["type"] in [LockType.EVENT_BOUND.value, LockType.HYBRID.value]:
            self._unregister_event_listeners(lock_id)
        
        # Record the operation in history
        self._record_lock_operation(lock_id, "cancel", {})
        
        logger.info(f"Canceled lock {lock_id} for capsule {lock['capsule_id']}")
        
        return lock
    
    def schedule_lock_operation(self, lock_id: str, operation: LockOperation, 
                               scheduled_time: datetime, parameters: Dict = None) -> Dict:
        """
        Schedule a lock operation for future execution.
        
        Args:
            lock_id: Lock identifier
            operation: Operation to schedule
            scheduled_time: Time to execute the operation
            parameters: Operation parameters
            
        Returns:
            Dict containing the scheduled operation
        """
        # Check if the lock exists
        if lock_id in self.time_locks:
            lock = self.time_locks[lock_id]
        elif lock_id in self.event_locks:
            lock = self.event_locks[lock_id]
        else:
            raise ValueError(f"Lock {lock_id} not found")
        
        # Check if the operation is enabled
        operation_config = self.config["operations"].get(operation.value)
        if not operation_config or not operation_config["enabled"]:
            raise ValueError(f"Operation {operation.value} is not enabled")
        
        # Create the scheduled operation
        scheduled_operation = {
            "type": "execute_lock_operation",
            "lock_id": lock_id,
            "capsule_id": lock["capsule_id"],
            "lock_operation": operation.value,
            "parameters": parameters or {}
        }
        
        # Add to the scheduler
        heapq.heappush(self.scheduled_operations, (scheduled_time, scheduled_operation))
        
        # Create a record of the scheduled operation
        operation_id = str(uuid.uuid4())
        operation_record = {
            "operation_id": operation_id,
            "lock_id": lock_id,
            "capsule_id": lock["capsule_id"],
            "operation": operation.value,
            "scheduled_time": scheduled_time.isoformat(),
            "parameters": parameters or {},
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat(),
            "metadata": {
                "type": "scheduled_lock_operation",
                "source": "time_locked_capsule_contracts"
            }
        }
        
        logger.info(f"Scheduled {operation.value} operation for lock {lock_id} at {scheduled_time.isoformat()}")
        
        return operation_record
    
    def get_lock(self, lock_id: str) -> Optional[Dict]:
        """
        Get a lock by ID.
        
        Args:
            lock_id: Lock identifier
            
        Returns:
            Lock data if found, None otherwise
        """
        if lock_id in self.time_locks:
            return self.time_locks[lock_id]
        elif lock_id in self.event_locks:
            return self.event_locks[lock_id]
        else:
            return None
    
    def get_locks_for_capsule(self, capsule_id: str) -> List[Dict]:
        """
        Get all locks for a capsule.
        
        Args:
            capsule_id: Capsule identifier
            
        Returns:
            List of locks for the capsule
        """
        locks = []
        
        # Check time locks
        for lock in self.time_locks.values():
            if lock["capsule_id"] == capsule_id:
                locks.append(lock)
        
        # Check event locks
        for lock in self.event_locks.values():
            if lock["capsule_id"] == capsule_id:
                locks.append(lock)
        
        return locks
    
    def get_lock_history(self, lock_id: str) -> List[Dict]:
        """
        Get the history of operations for a lock.
        
        Args:
            lock_id: Lock identifier
            
        Returns:
            List of operation records for the lock
        """
        return self.lock_history.get(lock_id, [])
    
    def verify_temporal_compliance(self, capsule_id: str) -> Dict:
        """
        Verify the temporal compliance of a capsule.
        
        Args:
            capsule_id: Capsule identifier
            
        Returns:
            Dict containing compliance verification results
        """
        # Check if compliance verification is enabled
        if not self.config["compliance"]["verification_enabled"]:
            raise ValueError("Compliance verification is not enabled")
        
        # Get all locks for the capsule
        locks = self.get_locks_for_capsule(capsule_id)
        
        # Check compliance for each lock
        compliance_results = []
        overall_status = "compliant"
        
        for lock in locks:
            # Check lock status
            lock_status = lock["status"]
            
            # Determine compliance status
            if lock_status == TimeLockStatus.ACTIVE.value:
                # Check if the lock is expired
                current_time = datetime.utcnow()
                
                if "expiration_time" in lock:
                    expiration_time = datetime.fromisoformat(lock["expiration_time"])
                    
                    if current_time > expiration_time:
                        compliance_status = "non_compliant"
                        compliance_reason = "Lock is active but has expired"
                        overall_status = "non_compliant"
                    else:
                        compliance_status = "compliant"
                        compliance_reason = "Lock is active and within expiration time"
                else:
                    compliance_status = "compliant"
                    compliance_reason = "Lock is active with no expiration time"
            
            elif lock_status == TimeLockStatus.EXPIRED.value:
                # Check if any required actions were taken
                if "expiration_action" in lock and lock.get("expiration_action_taken", False) == False:
                    compliance_status = "non_compliant"
                    compliance_reason = "Required expiration action was not taken"
                    overall_status = "non_compliant"
                else:
                    compliance_status = "compliant"
                    compliance_reason = "Lock expired normally"
            
            elif lock_status == TimeLockStatus.TRIGGERED.value:
                # Check if any required actions were taken
                if "trigger_action" in lock and lock.get("trigger_action_taken", False) == False:
                    compliance_status = "non_compliant"
                    compliance_reason = "Required trigger action was not taken"
                    overall_status = "non_compliant"
                else:
                    compliance_status = "compliant"
                    compliance_reason = "Lock triggered normally"
            
            else:
                compliance_status = "compliant"
                compliance_reason = f"Lock is in {lock_status} status"
            
            # Create compliance result
            result = {
                "lock_id": lock["lock_id"],
                "lock_type": lock["type"],
                "lock_status": lock_status,
                "compliance_status": compliance_status,
                "compliance_reason": compliance_reason,
                "verification_time": datetime.utcnow().isoformat()
            }
            
            compliance_results.append(result)
        
        # Create verification record
        verification_id = str(uuid.uuid4())
        verification_record = {
            "verification_id": verification_id,
            "capsule_id": capsule_id,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": overall_status,
            "results": compliance_results,
            "metadata": {
                "type": "temporal_compliance_verification",
                "source": "time_locked_capsule_contracts"
            }
        }
        
        logger.info(f"Completed temporal compliance verification for capsule {capsule_id} with status: {overall_status}")
        
        return verification_record


# Example usage
if __name__ == "__main__":
    # Initialize Time-Locked Capsule Contracts system
    tlcc = TimeLockedCapsuleContracts()
    
    # Create a time-bound lock
    capsule_id = "capsule123"
    time_lock = tlcc.create_time_bound_lock(
        capsule_id=capsule_id,
        duration_seconds=3600,  # 1 hour
        expiration_action={
            "type": "unlock",
            "parameters": {"reason": "time_expiration"}
        }
    )
    
    print(f"Created time-bound lock:")
    print(f"Lock ID: {time_lock['lock_id']}")
    print(f"Expiration time: {time_lock['expiration_time']}")
    
    # Activate the lock
    activated_lock = tlcc.activate_lock(time_lock['lock_id'])
    print(f"\nActivated lock with status: {activated_lock['status']}")
    
    # Create an event-bound lock
    event_conditions = [
        {
            "event_type": "capsule_state_change",
            "criteria": {
                "state": "completed",
                "result.status": {"operator": "eq", "value": "success"}
            }
        }
    ]
    
    event_lock = tlcc.create_event_bound_lock(
        capsule_id=capsule_id,
        event_conditions=event_conditions,
        timeout_seconds=86400,  # 1 day
        expiration_action={
            "type": "notify",
            "parameters": {"reason": "timeout"}
        }
    )
    
    print(f"\nCreated event-bound lock:")
    print(f"Lock ID: {event_lock['lock_id']}")
    print(f"Timeout time: {event_lock['timeout_time']}")
    
    # Schedule a privilege escalation
    escalation_time = datetime.utcnow() + timedelta(minutes=30)
    scheduled_op = tlcc.schedule_lock_operation(
        lock_id=time_lock['lock_id'],
        operation=LockOperation.ESCALATE,
        scheduled_time=escalation_time,
        parameters={
            "escalation": {
                "admin_access": "high",
                "data_access": "medium"
            }
        }
    )
    
    print(f"\nScheduled privilege escalation:")
    print(f"Operation ID: {scheduled_op['operation_id']}")
    print(f"Scheduled time: {scheduled_op['scheduled_time']}")
    
    # Simulate an event
    event = {
        "event_type": "capsule_state_change",
        "capsule_id": capsule_id,
        "state": "completed",
        "result": {
            "status": "success",
            "completion_time": datetime.utcnow().isoformat()
        },
        "timestamp": datetime.utcnow().isoformat()
    }
    
    triggered_locks = tlcc.process_event(event)
    
    print(f"\nProcessed event, triggered {len(triggered_locks)} locks")
    
    # Verify temporal compliance
    compliance = tlcc.verify_temporal_compliance(capsule_id)
    
    print(f"\nTemporal compliance verification:")
    print(f"Overall status: {compliance['overall_status']}")
    print(f"Results: {len(compliance['results'])} locks checked")
