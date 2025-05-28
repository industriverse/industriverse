"""
Diplomacy Models for the Digital Twin Diplomacy Phase of the Overseer System.

This module provides data models for negotiation processes, agreements, shadow capsules,
and diplomacy policies used in digital twin diplomacy.

Author: Manus AI
Date: May 25, 2025
"""

import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union, Set

class NegotiationStatus(str, Enum):
    """Status of a negotiation session."""
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    AGREEMENT_REACHED = "agreement_reached"
    DEADLOCKED = "deadlocked"
    TERMINATED = "terminated"
    EXPIRED = "expired"

class ProposalStatus(str, Enum):
    """Status of a negotiation proposal."""
    PROPOSED = "proposed"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTERED = "countered"
    EXPIRED = "expired"

class ResourceType(str, Enum):
    """Types of resources that can be negotiated."""
    COMPUTE = "compute"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    DATA_ACCESS = "data_access"
    SENSOR_ACCESS = "sensor_access"
    ACTUATOR_ACCESS = "actuator_access"
    TIME_SLICE = "time_slice"
    API_QUOTA = "api_quota"
    MODEL_ACCESS = "model_access"
    PRIORITY = "priority"

class ConflictType(str, Enum):
    """Types of conflicts between digital twins."""
    RESOURCE_CONTENTION = "resource_contention"
    GOAL_CONFLICT = "goal_conflict"
    POLICY_VIOLATION = "policy_violation"
    TRUST_ISSUE = "trust_issue"
    TIMING_CONFLICT = "timing_conflict"
    DATA_INCONSISTENCY = "data_inconsistency"

class ConflictSeverity(str, Enum):
    """Severity levels for conflicts."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ResolutionStrategy(str, Enum):
    """Strategies for conflict resolution."""
    COMPROMISE = "compromise"
    CONCESSION = "concession"
    COLLABORATION = "collaboration"
    COMPETITION = "competition"
    AVOIDANCE = "avoidance"
    ACCOMMODATION = "accommodation"
    ARBITRATION = "arbitration"

class ShadowType(str, Enum):
    """Types of shadow capsules."""
    FULL_CLONE = "full_clone"
    BEHAVIORAL_CLONE = "behavioral_clone"
    INTERFACE_CLONE = "interface_clone"
    LIGHTWEIGHT_PROXY = "lightweight_proxy"
    STATELESS_SHADOW = "stateless_shadow"

class ShadowStatus(str, Enum):
    """Status of a shadow capsule."""
    CREATED = "created"
    SYNCHRONIZING = "synchronizing"
    ACTIVE = "active"
    DIVERGED = "diverged"
    RECONCILING = "reconciling"
    RETIRED = "retired"

class ResourceSpecification:
    """Specification for a resource in negotiation."""
    
    def __init__(
        self,
        resource_type: ResourceType,
        quantity: float,
        unit: str,
        priority: int = 0,
        min_acceptable: Optional[float] = None,
        max_acceptable: Optional[float] = None,
        temporal_constraints: Optional[Dict[str, Any]] = None,
        quality_requirements: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a resource specification.
        
        Args:
            resource_type: Type of resource
            quantity: Quantity of resource
            unit: Unit of measurement
            priority: Priority level (0-10)
            min_acceptable: Minimum acceptable quantity
            max_acceptable: Maximum acceptable quantity
            temporal_constraints: Time-based constraints
            quality_requirements: Quality requirements
            metadata: Additional metadata
        """
        self.resource_type = resource_type
        self.quantity = quantity
        self.unit = unit
        self.priority = priority
        self.min_acceptable = min_acceptable if min_acceptable is not None else quantity * 0.8
        self.max_acceptable = max_acceptable if max_acceptable is not None else quantity * 1.2
        self.temporal_constraints = temporal_constraints or {}
        self.quality_requirements = quality_requirements or {}
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resource_type": self.resource_type,
            "quantity": self.quantity,
            "unit": self.unit,
            "priority": self.priority,
            "min_acceptable": self.min_acceptable,
            "max_acceptable": self.max_acceptable,
            "temporal_constraints": self.temporal_constraints,
            "quality_requirements": self.quality_requirements,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceSpecification':
        """Create from dictionary."""
        return cls(
            resource_type=ResourceType(data["resource_type"]),
            quantity=data["quantity"],
            unit=data["unit"],
            priority=data.get("priority", 0),
            min_acceptable=data.get("min_acceptable"),
            max_acceptable=data.get("max_acceptable"),
            temporal_constraints=data.get("temporal_constraints"),
            quality_requirements=data.get("quality_requirements"),
            metadata=data.get("metadata")
        )
    
    def is_compatible_with(self, other: 'ResourceSpecification') -> bool:
        """
        Check if this resource specification is compatible with another.
        
        Args:
            other: Other resource specification
            
        Returns:
            bool: True if compatible, False otherwise
        """
        if self.resource_type != other.resource_type:
            return False
        
        if self.unit != other.unit:
            return False
        
        # Check if there's overlap in acceptable ranges
        if self.max_acceptable < other.min_acceptable or other.max_acceptable < self.min_acceptable:
            return False
        
        # Check temporal constraints compatibility
        if self.temporal_constraints and other.temporal_constraints:
            # Implement temporal constraint compatibility check
            # This is a simplified placeholder
            if "start_time" in self.temporal_constraints and "start_time" in other.temporal_constraints:
                self_start = datetime.fromisoformat(self.temporal_constraints["start_time"])
                other_start = datetime.fromisoformat(other.temporal_constraints["start_time"])
                
                if abs((self_start - other_start).total_seconds()) > 3600:  # 1 hour difference
                    return False
        
        return True

class NegotiationProposal:
    """A proposal in a negotiation session."""
    
    def __init__(
        self,
        proposal_id: str,
        session_id: str,
        proposer_id: str,
        resources: List[ResourceSpecification],
        counter_to: Optional[str] = None,
        rationale: Optional[str] = None,
        status: ProposalStatus = ProposalStatus.PROPOSED,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a negotiation proposal.
        
        Args:
            proposal_id: Unique identifier for the proposal
            session_id: ID of the negotiation session
            proposer_id: ID of the proposing agent
            resources: List of resource specifications
            counter_to: ID of the proposal this counters
            rationale: Explanation for the proposal
            status: Status of the proposal
            created_at: Creation timestamp
            expires_at: Expiration timestamp
            metadata: Additional metadata
        """
        self.proposal_id = proposal_id
        self.session_id = session_id
        self.proposer_id = proposer_id
        self.resources = resources
        self.counter_to = counter_to
        self.rationale = rationale
        self.status = status
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at
        self.metadata = metadata or {}
        self.responses: Dict[str, Dict[str, Any]] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "proposal_id": self.proposal_id,
            "session_id": self.session_id,
            "proposer_id": self.proposer_id,
            "resources": [r.to_dict() for r in self.resources],
            "counter_to": self.counter_to,
            "rationale": self.rationale,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
            "responses": self.responses
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NegotiationProposal':
        """Create from dictionary."""
        proposal = cls(
            proposal_id=data["proposal_id"],
            session_id=data["session_id"],
            proposer_id=data["proposer_id"],
            resources=[ResourceSpecification.from_dict(r) for r in data["resources"]],
            counter_to=data.get("counter_to"),
            rationale=data.get("rationale"),
            status=ProposalStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            metadata=data.get("metadata", {})
        )
        proposal.responses = data.get("responses", {})
        return proposal
    
    def add_response(self, responder_id: str, response: str, rationale: Optional[str] = None) -> None:
        """
        Add a response to the proposal.
        
        Args:
            responder_id: ID of the responding agent
            response: Response (accept, reject, counter)
            rationale: Explanation for the response
        """
        self.responses[responder_id] = {
            "response": response,
            "rationale": rationale,
            "timestamp": datetime.now().isoformat()
        }
    
    def is_accepted_by_all(self, participant_ids: List[str]) -> bool:
        """
        Check if the proposal is accepted by all participants.
        
        Args:
            participant_ids: List of participant IDs
            
        Returns:
            bool: True if accepted by all, False otherwise
        """
        if self.proposer_id in participant_ids:
            participant_ids = [p for p in participant_ids if p != self.proposer_id]
        
        for participant_id in participant_ids:
            if participant_id not in self.responses or self.responses[participant_id]["response"] != "accept":
                return False
        
        return True

class NegotiationAgreement:
    """An agreement reached in a negotiation session."""
    
    def __init__(
        self,
        agreement_id: str,
        session_id: str,
        proposal_id: str,
        participants: List[str],
        resources: List[ResourceSpecification],
        terms: Dict[str, Any],
        created_at: Optional[datetime] = None,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        signatures: Optional[Dict[str, str]] = None,
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a negotiation agreement.
        
        Args:
            agreement_id: Unique identifier for the agreement
            session_id: ID of the negotiation session
            proposal_id: ID of the accepted proposal
            participants: List of participant IDs
            resources: List of resource specifications
            terms: Agreement terms
            created_at: Creation timestamp
            valid_from: Validity start timestamp
            valid_until: Validity end timestamp
            signatures: Participant signatures
            status: Agreement status
            metadata: Additional metadata
        """
        self.agreement_id = agreement_id
        self.session_id = session_id
        self.proposal_id = proposal_id
        self.participants = participants
        self.resources = resources
        self.terms = terms
        self.created_at = created_at or datetime.now()
        self.valid_from = valid_from or self.created_at
        self.valid_until = valid_until
        self.signatures = signatures or {}
        self.status = status
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "agreement_id": self.agreement_id,
            "session_id": self.session_id,
            "proposal_id": self.proposal_id,
            "participants": self.participants,
            "resources": [r.to_dict() for r in self.resources],
            "terms": self.terms,
            "created_at": self.created_at.isoformat(),
            "valid_from": self.valid_from.isoformat(),
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "signatures": self.signatures,
            "status": self.status,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NegotiationAgreement':
        """Create from dictionary."""
        return cls(
            agreement_id=data["agreement_id"],
            session_id=data["session_id"],
            proposal_id=data["proposal_id"],
            participants=data["participants"],
            resources=[ResourceSpecification.from_dict(r) for r in data["resources"]],
            terms=data["terms"],
            created_at=datetime.fromisoformat(data["created_at"]),
            valid_from=datetime.fromisoformat(data["valid_from"]),
            valid_until=datetime.fromisoformat(data["valid_until"]) if data.get("valid_until") else None,
            signatures=data.get("signatures", {}),
            status=data["status"],
            metadata=data.get("metadata", {})
        )
    
    def is_valid(self) -> bool:
        """
        Check if the agreement is currently valid.
        
        Returns:
            bool: True if valid, False otherwise
        """
        now = datetime.now()
        if self.status != "active":
            return False
        
        if now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        return True
    
    def add_signature(self, participant_id: str, signature: str) -> None:
        """
        Add a participant signature.
        
        Args:
            participant_id: ID of the participant
            signature: Signature value
        """
        self.signatures[participant_id] = signature
    
    def is_fully_signed(self) -> bool:
        """
        Check if all participants have signed.
        
        Returns:
            bool: True if fully signed, False otherwise
        """
        return all(p in self.signatures for p in self.participants)

class NegotiationSession:
    """A session for negotiating between digital twins."""
    
    def __init__(
        self,
        session_id: str,
        initiator_id: str,
        participants: List[str],
        context: Dict[str, Any],
        status: NegotiationStatus = NegotiationStatus.INITIATED,
        created_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a negotiation session.
        
        Args:
            session_id: Unique identifier for the session
            initiator_id: ID of the initiating agent
            participants: List of participant IDs
            context: Negotiation context
            status: Session status
            created_at: Creation timestamp
            expires_at: Expiration timestamp
            metadata: Additional metadata
        """
        self.session_id = session_id
        self.initiator_id = initiator_id
        self.participants = participants
        self.context = context
        self.status = status
        self.created_at = created_at or datetime.now()
        self.expires_at = expires_at
        self.metadata = metadata or {}
        self.proposals: List[NegotiationProposal] = []
        self.agreement: Optional[NegotiationAgreement] = None
        self.logs: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "initiator_id": self.initiator_id,
            "participants": self.participants,
            "context": self.context,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
            "proposals": [p.to_dict() for p in self.proposals],
            "agreement": self.agreement.to_dict() if self.agreement else None,
            "logs": self.logs
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NegotiationSession':
        """Create from dictionary."""
        session = cls(
            session_id=data["session_id"],
            initiator_id=data["initiator_id"],
            participants=data["participants"],
            context=data["context"],
            status=NegotiationStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            expires_at=datetime.fromisoformat(data["expires_at"]) if data.get("expires_at") else None,
            metadata=data.get("metadata", {})
        )
        session.proposals = [NegotiationProposal.from_dict(p) for p in data.get("proposals", [])]
        session.agreement = NegotiationAgreement.from_dict(data["agreement"]) if data.get("agreement") else None
        session.logs = data.get("logs", [])
        return session
    
    def add_proposal(self, proposal: NegotiationProposal) -> None:
        """
        Add a proposal to the session.
        
        Args:
            proposal: The proposal to add
        """
        self.proposals.append(proposal)
        self.log_event("proposal_added", {
            "proposal_id": proposal.proposal_id,
            "proposer_id": proposal.proposer_id
        })
    
    def set_agreement(self, agreement: NegotiationAgreement) -> None:
        """
        Set the agreement for the session.
        
        Args:
            agreement: The agreement
        """
        self.agreement = agreement
        self.status = NegotiationStatus.AGREEMENT_REACHED
        self.log_event("agreement_reached", {
            "agreement_id": agreement.agreement_id,
            "proposal_id": agreement.proposal_id
        })
    
    def log_event(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log an event in the session.
        
        Args:
            event_type: Type of event
            details: Event details
        """
        self.logs.append({
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "details": details
        })
    
    def get_latest_proposal(self) -> Optional[NegotiationProposal]:
        """
        Get the latest proposal in the session.
        
        Returns:
            Optional[NegotiationProposal]: Latest proposal or None
        """
        if not self.proposals:
            return None
        
        return max(self.proposals, key=lambda p: p.created_at)
    
    def is_expired(self) -> bool:
        """
        Check if the session is expired.
        
        Returns:
            bool: True if expired, False otherwise
        """
        if not self.expires_at:
            return False
        
        return datetime.now() > self.expires_at

class ResourceConflict:
    """A conflict between digital twins over resources."""
    
    def __init__(
        self,
        conflict_id: str,
        participants: List[str],
        conflict_type: ConflictType,
        resources: List[ResourceSpecification],
        severity: ConflictSeverity,
        description: str,
        detected_at: Optional[datetime] = None,
        resolution: Optional['ConflictResolution'] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a resource conflict.
        
        Args:
            conflict_id: Unique identifier for the conflict
            participants: List of participant IDs
            conflict_type: Type of conflict
            resources: List of contested resources
            severity: Conflict severity
            description: Conflict description
            detected_at: Detection timestamp
            resolution: Conflict resolution
            metadata: Additional metadata
        """
        self.conflict_id = conflict_id
        self.participants = participants
        self.conflict_type = conflict_type
        self.resources = resources
        self.severity = severity
        self.description = description
        self.detected_at = detected_at or datetime.now()
        self.resolution = resolution
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "conflict_id": self.conflict_id,
            "participants": self.participants,
            "conflict_type": self.conflict_type,
            "resources": [r.to_dict() for r in self.resources],
            "severity": self.severity,
            "description": self.description,
            "detected_at": self.detected_at.isoformat(),
            "resolution": self.resolution.to_dict() if self.resolution else None,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResourceConflict':
        """Create from dictionary."""
        conflict = cls(
            conflict_id=data["conflict_id"],
            participants=data["participants"],
            conflict_type=ConflictType(data["conflict_type"]),
            resources=[ResourceSpecification.from_dict(r) for r in data["resources"]],
            severity=ConflictSeverity(data["severity"]),
            description=data["description"],
            detected_at=datetime.fromisoformat(data["detected_at"]),
            metadata=data.get("metadata", {})
        )
        if data.get("resolution"):
            conflict.resolution = ConflictResolution.from_dict(data["resolution"])
        return conflict
    
    def is_resolved(self) -> bool:
        """
        Check if the conflict is resolved.
        
        Returns:
            bool: True if resolved, False otherwise
        """
        return self.resolution is not None and self.resolution.status == "resolved"

class ConflictResolution:
    """A resolution for a resource conflict."""
    
    def __init__(
        self,
        resolution_id: str,
        conflict_id: str,
        strategy: ResolutionStrategy,
        description: str,
        agreement_id: Optional[str] = None,
        resolved_at: Optional[datetime] = None,
        status: str = "pending",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a conflict resolution.
        
        Args:
            resolution_id: Unique identifier for the resolution
            conflict_id: ID of the conflict
            strategy: Resolution strategy
            description: Resolution description
            agreement_id: ID of the associated agreement
            resolved_at: Resolution timestamp
            status: Resolution status
            metadata: Additional metadata
        """
        self.resolution_id = resolution_id
        self.conflict_id = conflict_id
        self.strategy = strategy
        self.description = description
        self.agreement_id = agreement_id
        self.resolved_at = resolved_at
        self.status = status
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "resolution_id": self.resolution_id,
            "conflict_id": self.conflict_id,
            "strategy": self.strategy,
            "description": self.description,
            "agreement_id": self.agreement_id,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "status": self.status,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConflictResolution':
        """Create from dictionary."""
        return cls(
            resolution_id=data["resolution_id"],
            conflict_id=data["conflict_id"],
            strategy=ResolutionStrategy(data["strategy"]),
            description=data["description"],
            agreement_id=data.get("agreement_id"),
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None,
            status=data["status"],
            metadata=data.get("metadata", {})
        )
    
    def mark_as_resolved(self, agreement_id: Optional[str] = None) -> None:
        """
        Mark the resolution as resolved.
        
        Args:
            agreement_id: ID of the associated agreement
        """
        self.status = "resolved"
        self.resolved_at = datetime.now()
        if agreement_id:
            self.agreement_id = agreement_id

class ShadowCapsule:
    """A shadow copy of a capsule for diplomacy purposes."""
    
    def __init__(
        self,
        shadow_id: str,
        original_id: str,
        shadow_type: ShadowType,
        status: ShadowStatus = ShadowStatus.CREATED,
        created_at: Optional[datetime] = None,
        last_sync: Optional[datetime] = None,
        capabilities: Optional[Dict[str, Any]] = None,
        state: Optional[Dict[str, Any]] = None,
        divergence_metrics: Optional[Dict[str, float]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a shadow capsule.
        
        Args:
            shadow_id: Unique identifier for the shadow
            original_id: ID of the original capsule
            shadow_type: Type of shadow
            status: Shadow status
            created_at: Creation timestamp
            last_sync: Last synchronization timestamp
            capabilities: Shadow capabilities
            state: Shadow state
            divergence_metrics: Metrics of divergence from original
            metadata: Additional metadata
        """
        self.shadow_id = shadow_id
        self.original_id = original_id
        self.shadow_type = shadow_type
        self.status = status
        self.created_at = created_at or datetime.now()
        self.last_sync = last_sync or self.created_at
        self.capabilities = capabilities or {}
        self.state = state or {}
        self.divergence_metrics = divergence_metrics or {}
        self.metadata = metadata or {}
        self.sync_history: List[Dict[str, Any]] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "shadow_id": self.shadow_id,
            "original_id": self.original_id,
            "shadow_type": self.shadow_type,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_sync": self.last_sync.isoformat(),
            "capabilities": self.capabilities,
            "state": self.state,
            "divergence_metrics": self.divergence_metrics,
            "metadata": self.metadata,
            "sync_history": self.sync_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ShadowCapsule':
        """Create from dictionary."""
        shadow = cls(
            shadow_id=data["shadow_id"],
            original_id=data["original_id"],
            shadow_type=ShadowType(data["shadow_type"]),
            status=ShadowStatus(data["status"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_sync=datetime.fromisoformat(data["last_sync"]),
            capabilities=data.get("capabilities", {}),
            state=data.get("state", {}),
            divergence_metrics=data.get("divergence_metrics", {}),
            metadata=data.get("metadata", {})
        )
        shadow.sync_history = data.get("sync_history", [])
        return shadow
    
    def sync_with_original(self, original_state: Dict[str, Any]) -> None:
        """
        Synchronize with the original capsule.
        
        Args:
            original_state: State of the original capsule
        """
        previous_state = self.state.copy()
        self.state = original_state.copy()
        self.last_sync = datetime.now()
        self.status = ShadowStatus.ACTIVE
        
        # Calculate divergence metrics
        self.divergence_metrics = self._calculate_divergence(previous_state, original_state)
        
        # Record sync history
        self.sync_history.append({
            "timestamp": self.last_sync.isoformat(),
            "divergence_metrics": self.divergence_metrics
        })
    
    def _calculate_divergence(self, previous_state: Dict[str, Any], new_state: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate divergence metrics between states.
        
        Args:
            previous_state: Previous state
            new_state: New state
            
        Returns:
            Dict[str, float]: Divergence metrics
        """
        metrics = {}
        
        # Calculate overall state change percentage
        all_keys = set(previous_state.keys()) | set(new_state.keys())
        changed_keys = set()
        
        for key in all_keys:
            if key not in previous_state or key not in new_state:
                changed_keys.add(key)
            elif previous_state[key] != new_state[key]:
                changed_keys.add(key)
        
        if all_keys:
            metrics["state_change_percentage"] = len(changed_keys) / len(all_keys) * 100
        else:
            metrics["state_change_percentage"] = 0
        
        # Add more sophisticated metrics as needed
        
        return metrics
    
    def mark_as_diverged(self) -> None:
        """Mark the shadow as diverged from the original."""
        self.status = ShadowStatus.DIVERGED
    
    def mark_as_reconciling(self) -> None:
        """Mark the shadow as reconciling with the original."""
        self.status = ShadowStatus.RECONCILING
    
    def mark_as_retired(self) -> None:
        """Mark the shadow as retired."""
        self.status = ShadowStatus.RETIRED

class DiplomacyPolicy:
    """A policy for digital twin diplomacy."""
    
    def __init__(
        self,
        policy_id: str,
        name: str,
        description: str,
        scope: List[str],
        rules: List[Dict[str, Any]],
        priority: int = 0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        status: str = "active",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a diplomacy policy.
        
        Args:
            policy_id: Unique identifier for the policy
            name: Policy name
            description: Policy description
            scope: List of scope identifiers
            rules: List of policy rules
            priority: Policy priority
            created_at: Creation timestamp
            updated_at: Last update timestamp
            status: Policy status
            metadata: Additional metadata
        """
        self.policy_id = policy_id
        self.name = name
        self.description = description
        self.scope = scope
        self.rules = rules
        self.priority = priority
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or self.created_at
        self.status = status
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "scope": self.scope,
            "rules": self.rules,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DiplomacyPolicy':
        """Create from dictionary."""
        return cls(
            policy_id=data["policy_id"],
            name=data["name"],
            description=data["description"],
            scope=data["scope"],
            rules=data["rules"],
            priority=data.get("priority", 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            status=data["status"],
            metadata=data.get("metadata", {})
        )
    
    def applies_to(self, entity_id: str) -> bool:
        """
        Check if the policy applies to an entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            bool: True if applies, False otherwise
        """
        return entity_id in self.scope or "*" in self.scope
    
    def evaluate_rules(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluate policy rules against a context.
        
        Args:
            context: Evaluation context
            
        Returns:
            List[Dict[str, Any]]: List of rule evaluation results
        """
        results = []
        
        for rule in self.rules:
            rule_id = rule.get("id", "unknown")
            rule_type = rule.get("type", "unknown")
            rule_condition = rule.get("condition", {})
            rule_action = rule.get("action", {})
            
            # Evaluate condition
            condition_met = self._evaluate_condition(rule_condition, context)
            
            results.append({
                "rule_id": rule_id,
                "rule_type": rule_type,
                "condition_met": condition_met,
                "action": rule_action if condition_met else None
            })
        
        return results
    
    def _evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition against a context.
        
        Args:
            condition: Condition to evaluate
            context: Evaluation context
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        # This is a simplified implementation
        # In a real system, this would be more sophisticated
        
        operator = condition.get("operator", "equals")
        left = condition.get("left")
        right = condition.get("right")
        
        # Handle path-based left operand
        if isinstance(left, str) and left.startswith("$."):
            path = left[2:].split(".")
            value = context
            for key in path:
                if key in value:
                    value = value[key]
                else:
                    return False
            left = value
        
        # Evaluate based on operator
        if operator == "equals":
            return left == right
        elif operator == "not_equals":
            return left != right
        elif operator == "greater_than":
            return left > right
        elif operator == "less_than":
            return left < right
        elif operator == "contains":
            return right in left
        elif operator == "not_contains":
            return right not in left
        
        return False

# Helper functions

def create_negotiation_session(
    initiator_id: str,
    participants: List[str],
    context: Dict[str, Any],
    expires_in_hours: Optional[int] = 24,
    metadata: Optional[Dict[str, Any]] = None
) -> NegotiationSession:
    """
    Create a new negotiation session.
    
    Args:
        initiator_id: ID of the initiating agent
        participants: List of participant IDs
        context: Negotiation context
        expires_in_hours: Hours until expiration
        metadata: Additional metadata
        
    Returns:
        NegotiationSession: Created session
    """
    session_id = f"session-{uuid.uuid4()}"
    created_at = datetime.now()
    expires_at = created_at + timedelta(hours=expires_in_hours) if expires_in_hours else None
    
    return NegotiationSession(
        session_id=session_id,
        initiator_id=initiator_id,
        participants=participants,
        context=context,
        status=NegotiationStatus.INITIATED,
        created_at=created_at,
        expires_at=expires_at,
        metadata=metadata
    )

def create_negotiation_proposal(
    session_id: str,
    proposer_id: str,
    resources: List[ResourceSpecification],
    counter_to: Optional[str] = None,
    rationale: Optional[str] = None,
    expires_in_hours: Optional[int] = 24,
    metadata: Optional[Dict[str, Any]] = None
) -> NegotiationProposal:
    """
    Create a new negotiation proposal.
    
    Args:
        session_id: ID of the negotiation session
        proposer_id: ID of the proposing agent
        resources: List of resource specifications
        counter_to: ID of the proposal this counters
        rationale: Explanation for the proposal
        expires_in_hours: Hours until expiration
        metadata: Additional metadata
        
    Returns:
        NegotiationProposal: Created proposal
    """
    proposal_id = f"proposal-{uuid.uuid4()}"
    created_at = datetime.now()
    expires_at = created_at + timedelta(hours=expires_in_hours) if expires_in_hours else None
    
    return NegotiationProposal(
        proposal_id=proposal_id,
        session_id=session_id,
        proposer_id=proposer_id,
        resources=resources,
        counter_to=counter_to,
        rationale=rationale,
        status=ProposalStatus.PROPOSED,
        created_at=created_at,
        expires_at=expires_at,
        metadata=metadata
    )

def create_negotiation_agreement(
    session_id: str,
    proposal_id: str,
    participants: List[str],
    resources: List[ResourceSpecification],
    terms: Dict[str, Any],
    valid_for_hours: Optional[int] = 168,  # 1 week
    metadata: Optional[Dict[str, Any]] = None
) -> NegotiationAgreement:
    """
    Create a new negotiation agreement.
    
    Args:
        session_id: ID of the negotiation session
        proposal_id: ID of the accepted proposal
        participants: List of participant IDs
        resources: List of resource specifications
        terms: Agreement terms
        valid_for_hours: Hours of validity
        metadata: Additional metadata
        
    Returns:
        NegotiationAgreement: Created agreement
    """
    agreement_id = f"agreement-{uuid.uuid4()}"
    created_at = datetime.now()
    valid_from = created_at
    valid_until = created_at + timedelta(hours=valid_for_hours) if valid_for_hours else None
    
    return NegotiationAgreement(
        agreement_id=agreement_id,
        session_id=session_id,
        proposal_id=proposal_id,
        participants=participants,
        resources=resources,
        terms=terms,
        created_at=created_at,
        valid_from=valid_from,
        valid_until=valid_until,
        signatures={},
        status="active",
        metadata=metadata
    )

def create_resource_conflict(
    participants: List[str],
    conflict_type: ConflictType,
    resources: List[ResourceSpecification],
    severity: ConflictSeverity,
    description: str,
    metadata: Optional[Dict[str, Any]] = None
) -> ResourceConflict:
    """
    Create a new resource conflict.
    
    Args:
        participants: List of participant IDs
        conflict_type: Type of conflict
        resources: List of contested resources
        severity: Conflict severity
        description: Conflict description
        metadata: Additional metadata
        
    Returns:
        ResourceConflict: Created conflict
    """
    conflict_id = f"conflict-{uuid.uuid4()}"
    detected_at = datetime.now()
    
    return ResourceConflict(
        conflict_id=conflict_id,
        participants=participants,
        conflict_type=conflict_type,
        resources=resources,
        severity=severity,
        description=description,
        detected_at=detected_at,
        resolution=None,
        metadata=metadata
    )

def create_conflict_resolution(
    conflict_id: str,
    strategy: ResolutionStrategy,
    description: str,
    agreement_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ConflictResolution:
    """
    Create a new conflict resolution.
    
    Args:
        conflict_id: ID of the conflict
        strategy: Resolution strategy
        description: Resolution description
        agreement_id: ID of the associated agreement
        metadata: Additional metadata
        
    Returns:
        ConflictResolution: Created resolution
    """
    resolution_id = f"resolution-{uuid.uuid4()}"
    
    return ConflictResolution(
        resolution_id=resolution_id,
        conflict_id=conflict_id,
        strategy=strategy,
        description=description,
        agreement_id=agreement_id,
        resolved_at=None,
        status="pending",
        metadata=metadata
    )

def create_shadow_capsule(
    original_id: str,
    shadow_type: ShadowType,
    capabilities: Optional[Dict[str, Any]] = None,
    state: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> ShadowCapsule:
    """
    Create a new shadow capsule.
    
    Args:
        original_id: ID of the original capsule
        shadow_type: Type of shadow
        capabilities: Shadow capabilities
        state: Shadow state
        metadata: Additional metadata
        
    Returns:
        ShadowCapsule: Created shadow
    """
    shadow_id = f"shadow-{uuid.uuid4()}"
    created_at = datetime.now()
    
    return ShadowCapsule(
        shadow_id=shadow_id,
        original_id=original_id,
        shadow_type=shadow_type,
        status=ShadowStatus.CREATED,
        created_at=created_at,
        last_sync=created_at,
        capabilities=capabilities,
        state=state,
        divergence_metrics={},
        metadata=metadata
    )

def create_diplomacy_policy(
    name: str,
    description: str,
    scope: List[str],
    rules: List[Dict[str, Any]],
    priority: int = 0,
    metadata: Optional[Dict[str, Any]] = None
) -> DiplomacyPolicy:
    """
    Create a new diplomacy policy.
    
    Args:
        name: Policy name
        description: Policy description
        scope: List of scope identifiers
        rules: List of policy rules
        priority: Policy priority
        metadata: Additional metadata
        
    Returns:
        DiplomacyPolicy: Created policy
    """
    policy_id = f"policy-{uuid.uuid4()}"
    created_at = datetime.now()
    
    return DiplomacyPolicy(
        policy_id=policy_id,
        name=name,
        description=description,
        scope=scope,
        rules=rules,
        priority=priority,
        created_at=created_at,
        updated_at=created_at,
        status="active",
        metadata=metadata
    )
