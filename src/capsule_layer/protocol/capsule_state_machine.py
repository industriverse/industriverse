"""
Capsule State Machine

Production-ready state machine governing capsule lifecycle transitions.
Ensures consistent behavior across all platforms.

No mocks, no stubs - real state management with validation and history tracking.
"""

from typing import Dict, List, Optional, Set, Tuple
from datetime import datetime, timedelta
from enum import Enum
import logging

from .capsule_protocol import (
    CapsuleStatus,
    CapsuleAction,
    CapsuleContentState,
    CapsuleAttributes,
    Capsule,
    CapsuleActionResult,
    CapsuleEvent,
    CapsuleEventType
)

logger = logging.getLogger(__name__)

# ============================================================================
# STATE TRANSITIONS
# ============================================================================

# Valid state transitions: {from_state: [to_states]}
VALID_TRANSITIONS: Dict[CapsuleStatus, Set[CapsuleStatus]] = {
    CapsuleStatus.PENDING: {
        CapsuleStatus.ACTIVE,
        CapsuleStatus.DISMISSED,
        CapsuleStatus.EXPIRED,
        CapsuleStatus.ARCHIVED
    },
    CapsuleStatus.ACTIVE: {
        CapsuleStatus.IN_PROGRESS,
        CapsuleStatus.RESOLVED,
        CapsuleStatus.DISMISSED,
        CapsuleStatus.EXPIRED,
        CapsuleStatus.FAILED,
        CapsuleStatus.ARCHIVED
    },
    CapsuleStatus.IN_PROGRESS: {
        CapsuleStatus.ACTIVE,
        CapsuleStatus.RESOLVED,
        CapsuleStatus.FAILED,
        CapsuleStatus.EXPIRED,
        CapsuleStatus.ARCHIVED
    },
    CapsuleStatus.RESOLVED: {
        CapsuleStatus.ARCHIVED
    },
    CapsuleStatus.DISMISSED: {
        CapsuleStatus.ACTIVE,  # Can reactivate
        CapsuleStatus.ARCHIVED
    },
    CapsuleStatus.EXPIRED: {
        CapsuleStatus.ARCHIVED
    },
    CapsuleStatus.FAILED: {
        CapsuleStatus.ACTIVE,  # Can retry
        CapsuleStatus.ARCHIVED
    },
    CapsuleStatus.ARCHIVED: set()  # Terminal state
}

# Action to status mapping: {action: (in_progress_status, success_status, failure_status)}
ACTION_STATUS_MAP: Dict[CapsuleAction, Tuple[CapsuleStatus, CapsuleStatus, CapsuleStatus]] = {
    CapsuleAction.MITIGATE: (CapsuleStatus.IN_PROGRESS, CapsuleStatus.RESOLVED, CapsuleStatus.FAILED),
    CapsuleAction.INSPECT: (CapsuleStatus.ACTIVE, CapsuleStatus.ACTIVE, CapsuleStatus.ACTIVE),
    CapsuleAction.DISMISS: (CapsuleStatus.DISMISSED, CapsuleStatus.DISMISSED, CapsuleStatus.DISMISSED),
    CapsuleAction.APPROVE: (CapsuleStatus.IN_PROGRESS, CapsuleStatus.RESOLVED, CapsuleStatus.FAILED),
    CapsuleAction.REJECT: (CapsuleStatus.DISMISSED, CapsuleStatus.DISMISSED, CapsuleStatus.DISMISSED),
    CapsuleAction.ESCALATE: (CapsuleStatus.IN_PROGRESS, CapsuleStatus.ACTIVE, CapsuleStatus.FAILED),
    CapsuleAction.RETRY: (CapsuleStatus.IN_PROGRESS, CapsuleStatus.ACTIVE, CapsuleStatus.FAILED),
    CapsuleAction.CANCEL: (CapsuleStatus.DISMISSED, CapsuleStatus.DISMISSED, CapsuleStatus.DISMISSED),
    CapsuleAction.ACKNOWLEDGE: (CapsuleStatus.ACTIVE, CapsuleStatus.ACTIVE, CapsuleStatus.ACTIVE),
    CapsuleAction.CUSTOM: (CapsuleStatus.IN_PROGRESS, CapsuleStatus.ACTIVE, CapsuleStatus.FAILED),
}

# ============================================================================
# STATE MACHINE
# ============================================================================

class CapsuleStateMachine:
    """
    Production-ready state machine for capsule lifecycle management.
    
    Features:
    - State transition validation
    - Action execution with status updates
    - State history tracking
    - Event emission
    - Expiration handling
    """
    
    def __init__(self):
        self.state_history: Dict[str, List[Tuple[CapsuleStatus, datetime]]] = {}
        self.action_history: Dict[str, List[Tuple[CapsuleAction, datetime, bool]]] = {}
    
    # ========================================================================
    # STATE VALIDATION
    # ========================================================================
    
    def is_valid_transition(
        self,
        from_status: CapsuleStatus,
        to_status: CapsuleStatus
    ) -> bool:
        """Check if state transition is valid"""
        return to_status in VALID_TRANSITIONS.get(from_status, set())
    
    def validate_transition(
        self,
        from_status: CapsuleStatus,
        to_status: CapsuleStatus
    ) -> None:
        """Validate state transition or raise exception"""
        if not self.is_valid_transition(from_status, to_status):
            raise ValueError(
                f"Invalid state transition: {from_status.value} -> {to_status.value}"
            )
    
    # ========================================================================
    # STATE TRANSITIONS
    # ========================================================================
    
    def transition(
        self,
        capsule: Capsule,
        new_status: CapsuleStatus,
        message: Optional[str] = None
    ) -> Capsule:
        """
        Transition capsule to new status.
        
        Args:
            capsule: Current capsule
            new_status: Target status
            message: Optional status message
            
        Returns:
            Updated capsule
            
        Raises:
            ValueError: If transition is invalid
        """
        current_status = capsule.content_state.status
        
        # Validate transition
        self.validate_transition(current_status, new_status)
        
        # Update state
        capsule.content_state.status = new_status
        if message:
            capsule.content_state.status_message = message
        capsule.content_state.last_updated = datetime.utcnow()
        
        # Track history
        self._record_state_change(capsule.attributes.capsule_id, new_status)
        
        logger.info(
            f"Capsule {capsule.attributes.capsule_id} transitioned: "
            f"{current_status.value} -> {new_status.value}"
        )
        
        return capsule
    
    # ========================================================================
    # ACTION EXECUTION
    # ========================================================================
    
    def execute_action(
        self,
        capsule: Capsule,
        action: CapsuleAction,
        success: bool = True,
        message: Optional[str] = None
    ) -> Tuple[Capsule, CapsuleActionResult]:
        """
        Execute action on capsule and update state.
        
        Args:
            capsule: Current capsule
            action: Action to execute
            success: Whether action succeeded
            message: Optional result message
            
        Returns:
            Tuple of (updated capsule, action result)
        """
        # Get status mapping for this action
        if action not in ACTION_STATUS_MAP:
            raise ValueError(f"Unknown action: {action.value}")
        
        in_progress_status, success_status, failure_status = ACTION_STATUS_MAP[action]
        
        # Determine new status
        if success:
            new_status = success_status
            default_message = f"{action.value.capitalize()} completed successfully"
        else:
            new_status = failure_status
            default_message = f"{action.value.capitalize()} failed"
        
        # Transition to new status
        capsule = self.transition(
            capsule,
            new_status,
            message or default_message
        )
        
        # Track action history
        self._record_action(capsule.attributes.capsule_id, action, success)
        
        # Create action result
        result = CapsuleActionResult(
            capsule_id=capsule.attributes.capsule_id,
            action=action,
            success=success,
            message=message or default_message,
            new_state=capsule.content_state,
            timestamp=datetime.utcnow()
        )
        
        logger.info(
            f"Action {action.value} on capsule {capsule.attributes.capsule_id}: "
            f"{'success' if success else 'failure'}"
        )
        
        return capsule, result
    
    def start_action(
        self,
        capsule: Capsule,
        action: CapsuleAction
    ) -> Capsule:
        """
        Mark action as started (transition to in-progress).
        
        Args:
            capsule: Current capsule
            action: Action being started
            
        Returns:
            Updated capsule
        """
        if action not in ACTION_STATUS_MAP:
            raise ValueError(f"Unknown action: {action.value}")
        
        in_progress_status, _, _ = ACTION_STATUS_MAP[action]
        
        return self.transition(
            capsule,
            in_progress_status,
            f"{action.value.capitalize()} in progress..."
        )
    
    # ========================================================================
    # EXPIRATION HANDLING
    # ========================================================================
    
    def check_expiration(self, capsule: Capsule) -> Optional[Capsule]:
        """
        Check if capsule has expired and update status if needed.
        
        Args:
            capsule: Capsule to check
            
        Returns:
            Updated capsule if expired, None otherwise
        """
        if capsule.is_expired and capsule.content_state.status not in [
            CapsuleStatus.EXPIRED,
            CapsuleStatus.ARCHIVED
        ]:
            return self.transition(
                capsule,
                CapsuleStatus.EXPIRED,
                "Capsule has expired"
            )
        return None
    
    def mark_stale(self, capsule: Capsule, threshold_seconds: int = 300) -> Capsule:
        """
        Mark capsule as stale if not updated recently.
        
        Args:
            capsule: Capsule to check
            threshold_seconds: Staleness threshold (default 5 minutes)
            
        Returns:
            Updated capsule
        """
        age = (datetime.utcnow() - capsule.content_state.last_updated).total_seconds()
        capsule.content_state.is_stale = age > threshold_seconds
        return capsule
    
    # ========================================================================
    # HISTORY TRACKING
    # ========================================================================
    
    def _record_state_change(self, capsule_id: str, status: CapsuleStatus) -> None:
        """Record state change in history"""
        if capsule_id not in self.state_history:
            self.state_history[capsule_id] = []
        self.state_history[capsule_id].append((status, datetime.utcnow()))
    
    def _record_action(
        self,
        capsule_id: str,
        action: CapsuleAction,
        success: bool
    ) -> None:
        """Record action in history"""
        if capsule_id not in self.action_history:
            self.action_history[capsule_id] = []
        self.action_history[capsule_id].append((action, datetime.utcnow(), success))
    
    def get_state_history(self, capsule_id: str) -> List[Tuple[CapsuleStatus, datetime]]:
        """Get state change history for capsule"""
        return self.state_history.get(capsule_id, [])
    
    def get_action_history(
        self,
        capsule_id: str
    ) -> List[Tuple[CapsuleAction, datetime, bool]]:
        """Get action history for capsule"""
        return self.action_history.get(capsule_id, [])
    
    # ========================================================================
    # EVENT GENERATION
    # ========================================================================
    
    def create_event(
        self,
        event_type: CapsuleEventType,
        capsule: Capsule,
        action_result: Optional[CapsuleActionResult] = None,
        metadata: Optional[Dict] = None
    ) -> CapsuleEvent:
        """
        Create capsule event for external systems.
        
        Args:
            event_type: Type of event
            capsule: Current capsule
            action_result: Optional action result
            metadata: Optional additional metadata
            
        Returns:
            Capsule event
        """
        return CapsuleEvent(
            event_type=event_type,
            capsule_id=capsule.attributes.capsule_id,
            capsule=capsule,
            action_result=action_result,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def get_available_actions(self, capsule: Capsule) -> List[CapsuleAction]:
        """
        Get list of actions available for current capsule state.
        
        Args:
            capsule: Current capsule
            
        Returns:
            List of available actions
        """
        status = capsule.content_state.status
        
        # Actions available in each state
        if status == CapsuleStatus.PENDING:
            return [CapsuleAction.DISMISS]
        
        elif status == CapsuleStatus.ACTIVE:
            return capsule.content_state.available_actions or [
                CapsuleAction.MITIGATE,
                CapsuleAction.INSPECT,
                CapsuleAction.DISMISS,
                CapsuleAction.ESCALATE
            ]
        
        elif status == CapsuleStatus.IN_PROGRESS:
            return [CapsuleAction.CANCEL, CapsuleAction.INSPECT]
        
        elif status == CapsuleStatus.FAILED:
            return [CapsuleAction.RETRY, CapsuleAction.DISMISS]
        
        elif status == CapsuleStatus.DISMISSED:
            return [CapsuleAction.ACKNOWLEDGE]
        
        else:
            return []
    
    def can_perform_action(
        self,
        capsule: Capsule,
        action: CapsuleAction
    ) -> bool:
        """Check if action can be performed on capsule"""
        available = self.get_available_actions(capsule)
        return action in available
    
    def is_terminal_state(self, status: CapsuleStatus) -> bool:
        """Check if status is terminal (no further transitions)"""
        return len(VALID_TRANSITIONS.get(status, set())) == 0
    
    def get_next_states(self, status: CapsuleStatus) -> Set[CapsuleStatus]:
        """Get possible next states from current status"""
        return VALID_TRANSITIONS.get(status, set())


# ============================================================================
# GLOBAL STATE MACHINE INSTANCE
# ============================================================================

# Singleton instance for global use
_state_machine: Optional[CapsuleStateMachine] = None

def get_state_machine() -> CapsuleStateMachine:
    """Get global state machine instance"""
    global _state_machine
    if _state_machine is None:
        _state_machine = CapsuleStateMachine()
    return _state_machine
