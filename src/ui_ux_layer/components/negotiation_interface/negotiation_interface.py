"""
Negotiation Interface Component for the Industriverse UI/UX Layer.

This module provides a comprehensive interface for negotiation between agents, systems,
and human operators in industrial environments.

Author: Manus
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field

class NegotiationType(Enum):
    """Enumeration of negotiation types."""
    RESOURCE_ALLOCATION = "resource_allocation"
    TASK_ASSIGNMENT = "task_assignment"
    SCHEDULE_COORDINATION = "schedule_coordination"
    PARAMETER_TUNING = "parameter_tuning"
    CONFLICT_RESOLUTION = "conflict_resolution"
    CONSENSUS_BUILDING = "consensus_building"
    PERMISSION_REQUEST = "permission_request"
    CUSTOM = "custom"

class NegotiationStatus(Enum):
    """Enumeration of negotiation statuses."""
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"

class NegotiationRole(Enum):
    """Enumeration of negotiation roles."""
    INITIATOR = "initiator"
    RESPONDER = "responder"
    MEDIATOR = "mediator"
    OBSERVER = "observer"

class NegotiationStrategy(Enum):
    """Enumeration of negotiation strategies."""
    COOPERATIVE = "cooperative"
    COMPETITIVE = "competitive"
    COMPROMISING = "compromising"
    ACCOMMODATING = "accommodating"
    AVOIDING = "avoiding"
    COLLABORATIVE = "collaborative"
    CUSTOM = "custom"

class OfferStatus(Enum):
    """Enumeration of offer statuses."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    COUNTERED = "countered"
    EXPIRED = "expired"
    WITHDRAWN = "withdrawn"

@dataclass
class NegotiationParticipant:
    """Data class representing a negotiation participant."""
    participant_id: str
    name: str
    type: str  # "human", "agent", "system"
    role: NegotiationRole
    strategy: Optional[NegotiationStrategy] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NegotiationOffer:
    """Data class representing a negotiation offer."""
    offer_id: str
    negotiation_id: str
    sender_id: str
    terms: Dict[str, Any]
    status: OfferStatus = OfferStatus.PENDING
    timestamp: float = field(default_factory=time.time)
    expiration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NegotiationMessage:
    """Data class representing a negotiation message."""
    message_id: str
    negotiation_id: str
    sender_id: str
    content: str
    timestamp: float = field(default_factory=time.time)
    related_offer_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Negotiation:
    """Data class representing a negotiation."""
    negotiation_id: str
    title: str
    description: str
    type: NegotiationType
    status: NegotiationStatus
    participants: Dict[str, NegotiationParticipant]
    offers: Dict[str, NegotiationOffer] = field(default_factory=dict)
    messages: Dict[str, NegotiationMessage] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NegotiationEvent:
    """Data class representing a negotiation event."""
    event_type: str
    negotiation_id: str
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class NegotiationInterfaceComponent:
    """
    Provides a comprehensive interface for negotiation in the Industriverse UI/UX Layer.
    
    This class provides:
    - Negotiation creation and management
    - Participant management
    - Offer creation and evaluation
    - Message exchange
    - Negotiation visualization
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Negotiation Interface Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.negotiations: Dict[str, Negotiation] = {}
        self.active_negotiation_id: Optional[str] = None
        self.event_listeners: Dict[str, List[Callable[[NegotiationEvent], None]]] = {}
        self.negotiation_listeners: Dict[str, List[Callable[[Negotiation], None]]] = {}
        self.offer_listeners: Dict[str, List[Callable[[NegotiationOffer], None]]] = {}
        self.message_listeners: Dict[str, List[Callable[[NegotiationMessage], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize negotiation strategies
        self.strategies = {
            NegotiationStrategy.COOPERATIVE: self._cooperative_strategy,
            NegotiationStrategy.COMPETITIVE: self._competitive_strategy,
            NegotiationStrategy.COMPROMISING: self._compromising_strategy,
            NegotiationStrategy.ACCOMMODATING: self._accommodating_strategy,
            NegotiationStrategy.AVOIDING: self._avoiding_strategy,
            NegotiationStrategy.COLLABORATIVE: self._collaborative_strategy,
            NegotiationStrategy.CUSTOM: self._custom_strategy
        }
        
    def start(self) -> bool:
        """
        Start the Negotiation Interface Component.
        
        Returns:
            True if the component was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="negotiation_interface_started",
            negotiation_id="",
            source="NegotiationInterfaceComponent"
        ))
        
        self.logger.info("Negotiation Interface Component started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Negotiation Interface Component.
        
        Returns:
            True if the component was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="negotiation_interface_stopped",
            negotiation_id="",
            source="NegotiationInterfaceComponent"
        ))
        
        self.logger.info("Negotiation Interface Component stopped.")
        return True
    
    def create_negotiation(self,
                         title: str,
                         description: str,
                         type: NegotiationType,
                         initiator: NegotiationParticipant,
                         context: Optional[Dict[str, Any]] = None,
                         constraints: Optional[Dict[str, Any]] = None,
                         expires_at: Optional[float] = None,
                         metadata: Optional[Dict[str, Any]] = None,
                         negotiation_id: Optional[str] = None) -> str:
        """
        Create a new negotiation.
        
        Args:
            title: Title of the negotiation
            description: Description of the negotiation
            type: Type of negotiation
            initiator: Initiator participant
            context: Optional context information
            constraints: Optional constraints
            expires_at: Optional expiration timestamp
            metadata: Optional metadata
            negotiation_id: Optional negotiation ID, generated if not provided
            
        Returns:
            The negotiation ID
        """
        # Generate negotiation ID if not provided
        if negotiation_id is None:
            negotiation_id = str(uuid.uuid4())
            
        # Convert type to NegotiationType if needed
        if not isinstance(type, NegotiationType):
            try:
                type = NegotiationType(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid negotiation type: {type}, using CUSTOM.")
                type = NegotiationType.CUSTOM
                
        # Ensure initiator has the correct role
        initiator.role = NegotiationRole.INITIATOR
        
        # Create negotiation
        negotiation = Negotiation(
            negotiation_id=negotiation_id,
            title=title,
            description=description,
            type=type,
            status=NegotiationStatus.PENDING,
            participants={initiator.participant_id: initiator},
            context=context or {},
            constraints=constraints or {},
            expires_at=expires_at,
            metadata=metadata or {}
        )
        
        # Store negotiation
        self.negotiations[negotiation_id] = negotiation
        
        # Set as active negotiation if no active negotiation
        if self.active_negotiation_id is None:
            self.active_negotiation_id = negotiation_id
            
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="negotiation_created",
            negotiation_id=negotiation_id,
            source="NegotiationInterfaceComponent",
            data={"title": title, "initiator_id": initiator.participant_id}
        ))
        
        # Notify negotiation listeners
        self._notify_negotiation_listeners(negotiation)
        
        self.logger.debug(f"Created negotiation: {negotiation_id} ({title})")
        return negotiation_id
    
    def get_negotiation(self, negotiation_id: str) -> Optional[Negotiation]:
        """
        Get a negotiation by ID.
        
        Args:
            negotiation_id: ID of the negotiation to get
            
        Returns:
            The negotiation, or None if not found
        """
        return self.negotiations.get(negotiation_id)
    
    def set_active_negotiation(self, negotiation_id: str) -> bool:
        """
        Set the active negotiation.
        
        Args:
            negotiation_id: ID of the negotiation to set as active
            
        Returns:
            True if the negotiation was set as active, False if not found
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return False
            
        old_negotiation_id = self.active_negotiation_id
        self.active_negotiation_id = negotiation_id
        
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="active_negotiation_changed",
            negotiation_id=negotiation_id,
            source="NegotiationInterfaceComponent",
            data={"old_negotiation_id": old_negotiation_id}
        ))
        
        self.logger.debug(f"Set active negotiation: {negotiation_id}")
        return True
    
    def update_negotiation_status(self, negotiation_id: str, status: NegotiationStatus) -> bool:
        """
        Update the status of a negotiation.
        
        Args:
            negotiation_id: ID of the negotiation to update
            status: New status
            
        Returns:
            True if the negotiation was updated, False if not found
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return False
            
        negotiation = self.negotiations[negotiation_id]
        
        # Convert status to NegotiationStatus if needed
        if not isinstance(status, NegotiationStatus):
            try:
                status = NegotiationStatus(status)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid negotiation status: {status}, ignoring.")
                return False
                
        old_status = negotiation.status
        negotiation.status = status
        negotiation.updated_at = time.time()
        
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="negotiation_status_updated",
            negotiation_id=negotiation_id,
            source="NegotiationInterfaceComponent",
            data={"old_status": old_status.value, "new_status": status.value}
        ))
        
        # Notify negotiation listeners
        self._notify_negotiation_listeners(negotiation)
        
        self.logger.debug(f"Updated negotiation status: {negotiation_id} ({status.value})")
        return True
    
    def add_participant(self,
                      negotiation_id: str,
                      participant_id: str,
                      name: str,
                      type: str,
                      role: NegotiationRole,
                      strategy: Optional[NegotiationStrategy] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Add a participant to a negotiation.
        
        Args:
            negotiation_id: ID of the negotiation
            participant_id: ID of the participant
            name: Name of the participant
            type: Type of participant ("human", "agent", "system")
            role: Role of the participant
            strategy: Optional negotiation strategy
            metadata: Optional metadata
            
        Returns:
            True if the participant was added, False if negotiation not found
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return False
            
        negotiation = self.negotiations[negotiation_id]
        
        # Convert role to NegotiationRole if needed
        if not isinstance(role, NegotiationRole):
            try:
                role = NegotiationRole(role)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid negotiation role: {role}, using RESPONDER.")
                role = NegotiationRole.RESPONDER
                
        # Convert strategy to NegotiationStrategy if needed
        if strategy is not None and not isinstance(strategy, NegotiationStrategy):
            try:
                strategy = NegotiationStrategy(strategy)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid negotiation strategy: {strategy}, using None.")
                strategy = None
                
        # Create participant
        participant = NegotiationParticipant(
            participant_id=participant_id,
            name=name,
            type=type,
            role=role,
            strategy=strategy,
            metadata=metadata or {}
        )
        
        # Add to negotiation
        negotiation.participants[participant_id] = participant
        negotiation.updated_at = time.time()
        
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="participant_added",
            negotiation_id=negotiation_id,
            source="NegotiationInterfaceComponent",
            data={"participant_id": participant_id, "name": name, "role": role.value}
        ))
        
        # Notify negotiation listeners
        self._notify_negotiation_listeners(negotiation)
        
        self.logger.debug(f"Added participant: {participant_id} ({name}) to negotiation {negotiation_id}")
        return True
    
    def remove_participant(self, negotiation_id: str, participant_id: str) -> bool:
        """
        Remove a participant from a negotiation.
        
        Args:
            negotiation_id: ID of the negotiation
            participant_id: ID of the participant to remove
            
        Returns:
            True if the participant was removed, False if not found
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return False
            
        negotiation = self.negotiations[negotiation_id]
        
        if participant_id not in negotiation.participants:
            self.logger.warning(f"Participant {participant_id} not found in negotiation {negotiation_id}.")
            return False
            
        # Cannot remove the initiator
        if negotiation.participants[participant_id].role == NegotiationRole.INITIATOR:
            self.logger.warning(f"Cannot remove initiator from negotiation {negotiation_id}.")
            return False
            
        participant = negotiation.participants[participant_id]
        
        # Remove from negotiation
        del negotiation.participants[participant_id]
        negotiation.updated_at = time.time()
        
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="participant_removed",
            negotiation_id=negotiation_id,
            source="NegotiationInterfaceComponent",
            data={"participant_id": participant_id, "name": participant.name}
        ))
        
        # Notify negotiation listeners
        self._notify_negotiation_listeners(negotiation)
        
        self.logger.debug(f"Removed participant: {participant_id} ({participant.name}) from negotiation {negotiation_id}")
        return True
    
    def create_offer(self,
                   negotiation_id: str,
                   sender_id: str,
                   terms: Dict[str, Any],
                   expiration: Optional[float] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   offer_id: Optional[str] = None) -> Optional[str]:
        """
        Create a new offer in a negotiation.
        
        Args:
            negotiation_id: ID of the negotiation
            sender_id: ID of the sender
            terms: Offer terms
            expiration: Optional expiration timestamp
            metadata: Optional metadata
            offer_id: Optional offer ID, generated if not provided
            
        Returns:
            The offer ID, or None if negotiation or sender not found
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return None
            
        negotiation = self.negotiations[negotiation_id]
        
        if sender_id not in negotiation.participants:
            self.logger.warning(f"Sender {sender_id} not found in negotiation {negotiation_id}.")
            return None
            
        # Generate offer ID if not provided
        if offer_id is None:
            offer_id = str(uuid.uuid4())
            
        # Create offer
        offer = NegotiationOffer(
            offer_id=offer_id,
            negotiation_id=negotiation_id,
            sender_id=sender_id,
            terms=terms,
            status=OfferStatus.PENDING,
            expiration=expiration,
            metadata=metadata or {}
        )
        
        # Add to negotiation
        negotiation.offers[offer_id] = offer
        negotiation.updated_at = time.time()
        
        # Update negotiation status if needed
        if negotiation.status == NegotiationStatus.PENDING:
            negotiation.status = NegotiationStatus.ACTIVE
            
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="offer_created",
            negotiation_id=negotiation_id,
            source="NegotiationInterfaceComponent",
            data={"offer_id": offer_id, "sender_id": sender_id}
        ))
        
        # Notify offer listeners
        self._notify_offer_listeners(offer)
        
        # Notify negotiation listeners
        self._notify_negotiation_listeners(negotiation)
        
        self.logger.debug(f"Created offer: {offer_id} in negotiation {negotiation_id}")
        return offer_id
    
    def update_offer_status(self, negotiation_id: str, offer_id: str, status: OfferStatus) -> bool:
        """
        Update the status of an offer.
        
        Args:
            negotiation_id: ID of the negotiation
            offer_id: ID of the offer to update
            status: New status
            
        Returns:
            True if the offer was updated, False if not found
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return False
            
        negotiation = self.negotiations[negotiation_id]
        
        if offer_id not in negotiation.offers:
            self.logger.warning(f"Offer {offer_id} not found in negotiation {negotiation_id}.")
            return False
            
        offer = negotiation.offers[offer_id]
        
        # Convert status to OfferStatus if needed
        if not isinstance(status, OfferStatus):
            try:
                status = OfferStatus(status)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid offer status: {status}, ignoring.")
                return False
                
        old_status = offer.status
        offer.status = status
        offer.timestamp = time.time()
        negotiation.updated_at = time.time()
        
        # Update negotiation status if needed
        if status == OfferStatus.ACCEPTED:
            # Check if this was the final offer needed for completion
            all_accepted = True
            for other_offer in negotiation.offers.values():
                if other_offer.offer_id != offer_id and other_offer.status != OfferStatus.ACCEPTED:
                    all_accepted = False
                    break
                    
            if all_accepted:
                negotiation.status = NegotiationStatus.COMPLETED
                
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="offer_status_updated",
            negotiation_id=negotiation_id,
            source="NegotiationInterfaceComponent",
            data={"offer_id": offer_id, "old_status": old_status.value, "new_status": status.value}
        ))
        
        # Notify offer listeners
        self._notify_offer_listeners(offer)
        
        # Notify negotiation listeners
        self._notify_negotiation_listeners(negotiation)
        
        self.logger.debug(f"Updated offer status: {offer_id} ({status.value}) in negotiation {negotiation_id}")
        return True
    
    def create_message(self,
                     negotiation_id: str,
                     sender_id: str,
                     content: str,
                     related_offer_id: Optional[str] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     message_id: Optional[str] = None) -> Optional[str]:
        """
        Create a new message in a negotiation.
        
        Args:
            negotiation_id: ID of the negotiation
            sender_id: ID of the sender
            content: Message content
            related_offer_id: Optional related offer ID
            metadata: Optional metadata
            message_id: Optional message ID, generated if not provided
            
        Returns:
            The message ID, or None if negotiation or sender not found
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return None
            
        negotiation = self.negotiations[negotiation_id]
        
        if sender_id not in negotiation.participants:
            self.logger.warning(f"Sender {sender_id} not found in negotiation {negotiation_id}.")
            return None
            
        # Check if related offer exists
        if related_offer_id is not None and related_offer_id not in negotiation.offers:
            self.logger.warning(f"Related offer {related_offer_id} not found in negotiation {negotiation_id}.")
            related_offer_id = None
            
        # Generate message ID if not provided
        if message_id is None:
            message_id = str(uuid.uuid4())
            
        # Create message
        message = NegotiationMessage(
            message_id=message_id,
            negotiation_id=negotiation_id,
            sender_id=sender_id,
            content=content,
            related_offer_id=related_offer_id,
            metadata=metadata or {}
        )
        
        # Add to negotiation
        negotiation.messages[message_id] = message
        negotiation.updated_at = time.time()
        
        # Update negotiation status if needed
        if negotiation.status == NegotiationStatus.PENDING:
            negotiation.status = NegotiationStatus.ACTIVE
            
        # Dispatch event
        self._dispatch_event(NegotiationEvent(
            event_type="message_created",
            negotiation_id=negotiation_id,
            source="NegotiationInterfaceComponent",
            data={"message_id": message_id, "sender_id": sender_id}
        ))
        
        # Notify message listeners
        self._notify_message_listeners(message)
        
        # Notify negotiation listeners
        self._notify_negotiation_listeners(negotiation)
        
        self.logger.debug(f"Created message: {message_id} in negotiation {negotiation_id}")
        return message_id
    
    def evaluate_offer(self, negotiation_id: str, offer_id: str, evaluator_id: str) -> Dict[str, Any]:
        """
        Evaluate an offer based on the evaluator's strategy.
        
        Args:
            negotiation_id: ID of the negotiation
            offer_id: ID of the offer to evaluate
            evaluator_id: ID of the participant evaluating the offer
            
        Returns:
            Evaluation result
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return {"error": "Negotiation not found"}
            
        negotiation = self.negotiations[negotiation_id]
        
        if offer_id not in negotiation.offers:
            self.logger.warning(f"Offer {offer_id} not found in negotiation {negotiation_id}.")
            return {"error": "Offer not found"}
            
        if evaluator_id not in negotiation.participants:
            self.logger.warning(f"Evaluator {evaluator_id} not found in negotiation {negotiation_id}.")
            return {"error": "Evaluator not found"}
            
        offer = negotiation.offers[offer_id]
        evaluator = negotiation.participants[evaluator_id]
        
        # Skip if evaluator is the sender
        if evaluator_id == offer.sender_id:
            return {"result": "self", "score": 1.0, "recommendation": "N/A"}
            
        # Get the appropriate strategy
        strategy = None
        if evaluator.strategy:
            strategy = self.strategies.get(evaluator.strategy)
            
        if not strategy:
            # Default to compromising strategy
            strategy = self.strategies[NegotiationStrategy.COMPROMISING]
            
        # Evaluate the offer
        try:
            evaluation = strategy(negotiation, offer, evaluator)
            
            # Dispatch event
            self._dispatch_event(NegotiationEvent(
                event_type="offer_evaluated",
                negotiation_id=negotiation_id,
                source="NegotiationInterfaceComponent",
                data={
                    "offer_id": offer_id,
                    "evaluator_id": evaluator_id,
                    "score": evaluation.get("score", 0),
                    "recommendation": evaluation.get("recommendation", "unknown")
                }
            ))
            
            return evaluation
        except Exception as e:
            self.logger.error(f"Error evaluating offer {offer_id}: {e}")
            return {"error": str(e)}
    
    def suggest_counter_offer(self, negotiation_id: str, offer_id: str, responder_id: str) -> Dict[str, Any]:
        """
        Suggest a counter offer based on the responder's strategy.
        
        Args:
            negotiation_id: ID of the negotiation
            offer_id: ID of the offer to counter
            responder_id: ID of the participant creating the counter offer
            
        Returns:
            Suggested counter offer terms
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return {"error": "Negotiation not found"}
            
        negotiation = self.negotiations[negotiation_id]
        
        if offer_id not in negotiation.offers:
            self.logger.warning(f"Offer {offer_id} not found in negotiation {negotiation_id}.")
            return {"error": "Offer not found"}
            
        if responder_id not in negotiation.participants:
            self.logger.warning(f"Responder {responder_id} not found in negotiation {negotiation_id}.")
            return {"error": "Responder not found"}
            
        offer = negotiation.offers[offer_id]
        responder = negotiation.participants[responder_id]
        
        # Skip if responder is the sender
        if responder_id == offer.sender_id:
            return {"error": "Cannot counter own offer"}
            
        # Get the appropriate strategy
        strategy = None
        if responder.strategy:
            strategy = self.strategies.get(responder.strategy)
            
        if not strategy:
            # Default to compromising strategy
            strategy = self.strategies[NegotiationStrategy.COMPROMISING]
            
        # Generate counter offer
        try:
            # First evaluate the offer
            evaluation = strategy(negotiation, offer, responder)
            
            # If the recommendation is to accept, no counter offer needed
            if evaluation.get("recommendation") == "accept":
                return {"recommendation": "accept", "terms": offer.terms}
                
            # Generate counter offer terms
            counter_terms = self._generate_counter_terms(negotiation, offer, responder)
            
            # Dispatch event
            self._dispatch_event(NegotiationEvent(
                event_type="counter_offer_suggested",
                negotiation_id=negotiation_id,
                source="NegotiationInterfaceComponent",
                data={
                    "original_offer_id": offer_id,
                    "responder_id": responder_id
                }
            ))
            
            return {"recommendation": "counter", "terms": counter_terms}
        except Exception as e:
            self.logger.error(f"Error suggesting counter offer for {offer_id}: {e}")
            return {"error": str(e)}
    
    def visualize_negotiation(self, negotiation_id: str) -> Dict[str, Any]:
        """
        Generate visualization data for a negotiation.
        
        Args:
            negotiation_id: ID of the negotiation to visualize
            
        Returns:
            Visualization data
        """
        if negotiation_id not in self.negotiations:
            self.logger.warning(f"Negotiation {negotiation_id} not found.")
            return {"error": "Negotiation not found"}
            
        negotiation = self.negotiations[negotiation_id]
        
        # Build participant data
        participants_data = []
        for participant_id, participant in negotiation.participants.items():
            participants_data.append({
                "id": participant_id,
                "name": participant.name,
                "type": participant.type,
                "role": participant.role.value,
                "strategy": participant.strategy.value if participant.strategy else None
            })
            
        # Build offer data
        offers_data = []
        for offer_id, offer in negotiation.offers.items():
            offers_data.append({
                "id": offer_id,
                "sender_id": offer.sender_id,
                "status": offer.status.value,
                "timestamp": offer.timestamp,
                "terms": offer.terms
            })
            
        # Build message data
        messages_data = []
        for message_id, message in negotiation.messages.items():
            messages_data.append({
                "id": message_id,
                "sender_id": message.sender_id,
                "content": message.content,
                "timestamp": message.timestamp,
                "related_offer_id": message.related_offer_id
            })
            
        # Build timeline data
        timeline_data = []
        
        # Add creation event
        timeline_data.append({
            "type": "creation",
            "timestamp": negotiation.created_at,
            "data": {
                "title": negotiation.title,
                "description": negotiation.description
            }
        })
        
        # Add participant events
        for participant in participants_data:
            if participant["role"] != "initiator":  # Skip initiator as they're part of creation
                timeline_data.append({
                    "type": "participant_joined",
                    "timestamp": negotiation.created_at,  # Approximate
                    "data": {
                        "participant_id": participant["id"],
                        "name": participant["name"],
                        "role": participant["role"]
                    }
                })
                
        # Add offer events
        for offer in offers_data:
            timeline_data.append({
                "type": "offer_created",
                "timestamp": offer["timestamp"],
                "data": {
                    "offer_id": offer["id"],
                    "sender_id": offer["sender_id"],
                    "status": offer["status"]
                }
            })
            
        # Add message events
        for message in messages_data:
            timeline_data.append({
                "type": "message_sent",
                "timestamp": message["timestamp"],
                "data": {
                    "message_id": message["id"],
                    "sender_id": message["sender_id"],
                    "content": message["content"]
                }
            })
            
        # Sort timeline by timestamp
        timeline_data.sort(key=lambda x: x["timestamp"])
        
        # Build the visualization data
        visualization_data = {
            "id": negotiation_id,
            "title": negotiation.title,
            "description": negotiation.description,
            "type": negotiation.type.value,
            "status": negotiation.status.value,
            "created_at": negotiation.created_at,
            "updated_at": negotiation.updated_at,
            "participants": participants_data,
            "offers": offers_data,
            "messages": messages_data,
            "timeline": timeline_data,
            "context": negotiation.context,
            "constraints": negotiation.constraints
        }
        
        return visualization_data
    
    def add_event_listener(self, event_type: str, listener: Callable[[NegotiationEvent], None]) -> None:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
        """
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        
    def add_negotiation_listener(self, negotiation_id: str, listener: Callable[[Negotiation], None]) -> bool:
        """
        Add a listener for a specific negotiation.
        
        Args:
            negotiation_id: ID of the negotiation to listen for
            listener: Callback function that will be called when the negotiation is updated
            
        Returns:
            True if the listener was added, False if negotiation not found
        """
        if negotiation_id not in self.negotiations:
            return False
            
        if negotiation_id not in self.negotiation_listeners:
            self.negotiation_listeners[negotiation_id] = []
            
        self.negotiation_listeners[negotiation_id].append(listener)
        return True
    
    def add_offer_listener(self, offer_id: str, listener: Callable[[NegotiationOffer], None]) -> bool:
        """
        Add a listener for a specific offer.
        
        Args:
            offer_id: ID of the offer to listen for
            listener: Callback function that will be called when the offer is updated
            
        Returns:
            True if the listener was added, False if offer not found
        """
        # Find the offer
        for negotiation in self.negotiations.values():
            if offer_id in negotiation.offers:
                if offer_id not in self.offer_listeners:
                    self.offer_listeners[offer_id] = []
                    
                self.offer_listeners[offer_id].append(listener)
                return True
                
        return False
    
    def add_message_listener(self, message_id: str, listener: Callable[[NegotiationMessage], None]) -> bool:
        """
        Add a listener for a specific message.
        
        Args:
            message_id: ID of the message to listen for
            listener: Callback function that will be called when the message is updated
            
        Returns:
            True if the listener was added, False if message not found
        """
        # Find the message
        for negotiation in self.negotiations.values():
            if message_id in negotiation.messages:
                if message_id not in self.message_listeners:
                    self.message_listeners[message_id] = []
                    
                self.message_listeners[message_id].append(listener)
                return True
                
        return False
    
    def add_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.global_listeners.append(listener)
        
    def remove_event_listener(self, event_type: str, listener: Callable[[NegotiationEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if event_type not in self.event_listeners:
            return False
            
        if listener in self.event_listeners[event_type]:
            self.event_listeners[event_type].remove(listener)
            return True
            
        return False
    
    def remove_negotiation_listener(self, negotiation_id: str, listener: Callable[[Negotiation], None]) -> bool:
        """
        Remove a negotiation listener.
        
        Args:
            negotiation_id: ID of the negotiation the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if negotiation_id not in self.negotiation_listeners:
            return False
            
        if listener in self.negotiation_listeners[negotiation_id]:
            self.negotiation_listeners[negotiation_id].remove(listener)
            return True
            
        return False
    
    def remove_offer_listener(self, offer_id: str, listener: Callable[[NegotiationOffer], None]) -> bool:
        """
        Remove an offer listener.
        
        Args:
            offer_id: ID of the offer the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if offer_id not in self.offer_listeners:
            return False
            
        if listener in self.offer_listeners[offer_id]:
            self.offer_listeners[offer_id].remove(listener)
            return True
            
        return False
    
    def remove_message_listener(self, message_id: str, listener: Callable[[NegotiationMessage], None]) -> bool:
        """
        Remove a message listener.
        
        Args:
            message_id: ID of the message the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if message_id not in self.message_listeners:
            return False
            
        if listener in self.message_listeners[message_id]:
            self.message_listeners[message_id].remove(listener)
            return True
            
        return False
    
    def remove_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove a global listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.global_listeners:
            self.global_listeners.remove(listener)
            return True
            
        return False
    
    def _dispatch_event(self, event: NegotiationEvent) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event: The event to dispatch
        """
        # Dispatch to event type listeners
        if event.event_type in self.event_listeners:
            for listener in self.event_listeners[event.event_type]:
                try:
                    listener(event)
                except Exception as e:
                    self.logger.error(f"Error in event listener for {event.event_type}: {e}")
                    
        # Dispatch to global listeners
        for listener in self.global_listeners:
            try:
                listener(self._event_to_dict(event))
            except Exception as e:
                self.logger.error(f"Error in global listener: {e}")
    
    def _notify_negotiation_listeners(self, negotiation: Negotiation) -> None:
        """
        Notify listeners for a specific negotiation.
        
        Args:
            negotiation: The negotiation that was updated
        """
        if negotiation.negotiation_id in self.negotiation_listeners:
            for listener in self.negotiation_listeners[negotiation.negotiation_id]:
                try:
                    listener(negotiation)
                except Exception as e:
                    self.logger.error(f"Error in negotiation listener for {negotiation.negotiation_id}: {e}")
    
    def _notify_offer_listeners(self, offer: NegotiationOffer) -> None:
        """
        Notify listeners for a specific offer.
        
        Args:
            offer: The offer that was updated
        """
        if offer.offer_id in self.offer_listeners:
            for listener in self.offer_listeners[offer.offer_id]:
                try:
                    listener(offer)
                except Exception as e:
                    self.logger.error(f"Error in offer listener for {offer.offer_id}: {e}")
    
    def _notify_message_listeners(self, message: NegotiationMessage) -> None:
        """
        Notify listeners for a specific message.
        
        Args:
            message: The message that was updated
        """
        if message.message_id in self.message_listeners:
            for listener in self.message_listeners[message.message_id]:
                try:
                    listener(message)
                except Exception as e:
                    self.logger.error(f"Error in message listener for {message.message_id}: {e}")
    
    def _event_to_dict(self, event: NegotiationEvent) -> Dict[str, Any]:
        """
        Convert event to dictionary.
        
        Args:
            event: The event to convert
            
        Returns:
            Dictionary representation of the event
        """
        return {
            "event_type": event.event_type,
            "negotiation_id": event.negotiation_id,
            "source": event.source,
            "data": event.data,
            "timestamp": event.timestamp
        }
    
    # Negotiation strategy methods
    
    def _cooperative_strategy(self, negotiation: Negotiation, offer: NegotiationOffer, evaluator: NegotiationParticipant) -> Dict[str, Any]:
        """
        Cooperative strategy: Prioritizes relationship and mutual benefit.
        
        Args:
            negotiation: The negotiation
            offer: The offer to evaluate
            evaluator: The participant evaluating the offer
            
        Returns:
            Evaluation result
        """
        # In a real implementation, this would evaluate the offer based on the cooperative strategy
        # For now, we'll just return a dummy evaluation
        
        # Simulate evaluation
        score = 0.8  # High score for cooperative strategy
        
        if score >= 0.7:
            recommendation = "accept"
        elif score >= 0.4:
            recommendation = "counter"
        else:
            recommendation = "reject"
            
        return {
            "strategy": "cooperative",
            "score": score,
            "recommendation": recommendation,
            "reasoning": "Cooperative strategy prioritizes relationship and mutual benefit."
        }
    
    def _competitive_strategy(self, negotiation: Negotiation, offer: NegotiationOffer, evaluator: NegotiationParticipant) -> Dict[str, Any]:
        """
        Competitive strategy: Prioritizes own interests and maximizing value.
        
        Args:
            negotiation: The negotiation
            offer: The offer to evaluate
            evaluator: The participant evaluating the offer
            
        Returns:
            Evaluation result
        """
        # In a real implementation, this would evaluate the offer based on the competitive strategy
        # For now, we'll just return a dummy evaluation
        
        # Simulate evaluation
        score = 0.3  # Low score for competitive strategy
        
        if score >= 0.7:
            recommendation = "accept"
        elif score >= 0.4:
            recommendation = "counter"
        else:
            recommendation = "reject"
            
        return {
            "strategy": "competitive",
            "score": score,
            "recommendation": recommendation,
            "reasoning": "Competitive strategy prioritizes own interests and maximizing value."
        }
    
    def _compromising_strategy(self, negotiation: Negotiation, offer: NegotiationOffer, evaluator: NegotiationParticipant) -> Dict[str, Any]:
        """
        Compromising strategy: Seeks middle ground and partial satisfaction.
        
        Args:
            negotiation: The negotiation
            offer: The offer to evaluate
            evaluator: The participant evaluating the offer
            
        Returns:
            Evaluation result
        """
        # In a real implementation, this would evaluate the offer based on the compromising strategy
        # For now, we'll just return a dummy evaluation
        
        # Simulate evaluation
        score = 0.6  # Medium score for compromising strategy
        
        if score >= 0.7:
            recommendation = "accept"
        elif score >= 0.4:
            recommendation = "counter"
        else:
            recommendation = "reject"
            
        return {
            "strategy": "compromising",
            "score": score,
            "recommendation": recommendation,
            "reasoning": "Compromising strategy seeks middle ground and partial satisfaction."
        }
    
    def _accommodating_strategy(self, negotiation: Negotiation, offer: NegotiationOffer, evaluator: NegotiationParticipant) -> Dict[str, Any]:
        """
        Accommodating strategy: Prioritizes relationship over own interests.
        
        Args:
            negotiation: The negotiation
            offer: The offer to evaluate
            evaluator: The participant evaluating the offer
            
        Returns:
            Evaluation result
        """
        # In a real implementation, this would evaluate the offer based on the accommodating strategy
        # For now, we'll just return a dummy evaluation
        
        # Simulate evaluation
        score = 0.9  # Very high score for accommodating strategy
        
        if score >= 0.7:
            recommendation = "accept"
        elif score >= 0.4:
            recommendation = "counter"
        else:
            recommendation = "reject"
            
        return {
            "strategy": "accommodating",
            "score": score,
            "recommendation": recommendation,
            "reasoning": "Accommodating strategy prioritizes relationship over own interests."
        }
    
    def _avoiding_strategy(self, negotiation: Negotiation, offer: NegotiationOffer, evaluator: NegotiationParticipant) -> Dict[str, Any]:
        """
        Avoiding strategy: Seeks to delay or avoid negotiation.
        
        Args:
            negotiation: The negotiation
            offer: The offer to evaluate
            evaluator: The participant evaluating the offer
            
        Returns:
            Evaluation result
        """
        # In a real implementation, this would evaluate the offer based on the avoiding strategy
        # For now, we'll just return a dummy evaluation
        
        # Simulate evaluation
        score = 0.2  # Very low score for avoiding strategy
        
        if score >= 0.7:
            recommendation = "accept"
        elif score >= 0.4:
            recommendation = "counter"
        else:
            recommendation = "reject"
            
        return {
            "strategy": "avoiding",
            "score": score,
            "recommendation": recommendation,
            "reasoning": "Avoiding strategy seeks to delay or avoid negotiation."
        }
    
    def _collaborative_strategy(self, negotiation: Negotiation, offer: NegotiationOffer, evaluator: NegotiationParticipant) -> Dict[str, Any]:
        """
        Collaborative strategy: Seeks to maximize joint value and mutual benefit.
        
        Args:
            negotiation: The negotiation
            offer: The offer to evaluate
            evaluator: The participant evaluating the offer
            
        Returns:
            Evaluation result
        """
        # In a real implementation, this would evaluate the offer based on the collaborative strategy
        # For now, we'll just return a dummy evaluation
        
        # Simulate evaluation
        score = 0.75  # High score for collaborative strategy
        
        if score >= 0.7:
            recommendation = "accept"
        elif score >= 0.4:
            recommendation = "counter"
        else:
            recommendation = "reject"
            
        return {
            "strategy": "collaborative",
            "score": score,
            "recommendation": recommendation,
            "reasoning": "Collaborative strategy seeks to maximize joint value and mutual benefit."
        }
    
    def _custom_strategy(self, negotiation: Negotiation, offer: NegotiationOffer, evaluator: NegotiationParticipant) -> Dict[str, Any]:
        """
        Custom strategy: User-defined strategy.
        
        Args:
            negotiation: The negotiation
            offer: The offer to evaluate
            evaluator: The participant evaluating the offer
            
        Returns:
            Evaluation result
        """
        # In a real implementation, this would evaluate the offer based on a custom strategy
        # For now, we'll just return a dummy evaluation
        
        # Simulate evaluation
        score = 0.5  # Medium score for custom strategy
        
        if score >= 0.7:
            recommendation = "accept"
        elif score >= 0.4:
            recommendation = "counter"
        else:
            recommendation = "reject"
            
        return {
            "strategy": "custom",
            "score": score,
            "recommendation": recommendation,
            "reasoning": "Custom strategy with user-defined evaluation logic."
        }
    
    def _generate_counter_terms(self, negotiation: Negotiation, offer: NegotiationOffer, responder: NegotiationParticipant) -> Dict[str, Any]:
        """
        Generate counter offer terms based on the original offer and responder's strategy.
        
        Args:
            negotiation: The negotiation
            offer: The original offer
            responder: The participant creating the counter offer
            
        Returns:
            Counter offer terms
        """
        # In a real implementation, this would generate counter offer terms based on the strategy
        # For now, we'll just modify the original terms slightly
        
        counter_terms = offer.terms.copy()
        
        # Modify terms based on strategy
        if responder.strategy == NegotiationStrategy.COOPERATIVE:
            # Cooperative: Small adjustments
            for key, value in counter_terms.items():
                if isinstance(value, (int, float)):
                    counter_terms[key] = value * 0.95  # 5% reduction
                    
        elif responder.strategy == NegotiationStrategy.COMPETITIVE:
            # Competitive: Large adjustments
            for key, value in counter_terms.items():
                if isinstance(value, (int, float)):
                    counter_terms[key] = value * 0.7  # 30% reduction
                    
        elif responder.strategy == NegotiationStrategy.COMPROMISING:
            # Compromising: Medium adjustments
            for key, value in counter_terms.items():
                if isinstance(value, (int, float)):
                    counter_terms[key] = value * 0.85  # 15% reduction
                    
        elif responder.strategy == NegotiationStrategy.ACCOMMODATING:
            # Accommodating: Very small adjustments
            for key, value in counter_terms.items():
                if isinstance(value, (int, float)):
                    counter_terms[key] = value * 0.98  # 2% reduction
                    
        elif responder.strategy == NegotiationStrategy.AVOIDING:
            # Avoiding: No real counter offer
            pass
            
        elif responder.strategy == NegotiationStrategy.COLLABORATIVE:
            # Collaborative: Balanced adjustments
            for key, value in counter_terms.items():
                if isinstance(value, (int, float)):
                    counter_terms[key] = value * 0.9  # 10% reduction
                    
        else:
            # Custom or None: Default adjustments
            for key, value in counter_terms.items():
                if isinstance(value, (int, float)):
                    counter_terms[key] = value * 0.9  # 10% reduction
                    
        return counter_terms

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create negotiation interface component
    negotiation_component = NegotiationInterfaceComponent()
    
    # Start the component
    negotiation_component.start()
    
    # Add an event listener
    def on_event(event):
        print(f"Event: {event.event_type}")
        
    negotiation_component.add_event_listener("negotiation_created", on_event)
    
    # Create a negotiation
    initiator = NegotiationParticipant(
        participant_id="user-001",
        name="John Doe",
        type="human",
        role=NegotiationRole.INITIATOR,
        strategy=NegotiationStrategy.COLLABORATIVE
    )
    
    negotiation_id = negotiation_component.create_negotiation(
        title="Resource Allocation Negotiation",
        description="Negotiation for allocating manufacturing resources",
        type=NegotiationType.RESOURCE_ALLOCATION,
        initiator=initiator,
        context={"facility": "Plant A", "timeframe": "Q3 2023"},
        constraints={"budget": 100000, "deadline": "2023-09-30"}
    )
    
    # Add a responder
    negotiation_component.add_participant(
        negotiation_id=negotiation_id,
        participant_id="agent-001",
        name="Manufacturing Agent",
        type="agent",
        role=NegotiationRole.RESPONDER,
        strategy=NegotiationStrategy.COOPERATIVE
    )
    
    # Create an offer
    offer_id = negotiation_component.create_offer(
        negotiation_id=negotiation_id,
        sender_id="user-001",
        terms={
            "machine_time": 120,
            "labor_hours": 240,
            "materials": 5000,
            "priority": "high"
        }
    )
    
    # Add a message
    message_id = negotiation_component.create_message(
        negotiation_id=negotiation_id,
        sender_id="user-001",
        content="This is my initial offer for the resource allocation.",
        related_offer_id=offer_id
    )
    
    # Evaluate the offer
    evaluation = negotiation_component.evaluate_offer(
        negotiation_id=negotiation_id,
        offer_id=offer_id,
        evaluator_id="agent-001"
    )
    
    print(f"Evaluation: {evaluation}")
    
    # Suggest a counter offer
    counter_suggestion = negotiation_component.suggest_counter_offer(
        negotiation_id=negotiation_id,
        offer_id=offer_id,
        responder_id="agent-001"
    )
    
    print(f"Counter suggestion: {counter_suggestion}")
    
    # Create a counter offer
    counter_offer_id = negotiation_component.create_offer(
        negotiation_id=negotiation_id,
        sender_id="agent-001",
        terms=counter_suggestion["terms"]
    )
    
    # Add a response message
    response_message_id = negotiation_component.create_message(
        negotiation_id=negotiation_id,
        sender_id="agent-001",
        content="I've reviewed your offer and here's my counter proposal.",
        related_offer_id=counter_offer_id
    )
    
    # Accept the counter offer
    negotiation_component.update_offer_status(
        negotiation_id=negotiation_id,
        offer_id=counter_offer_id,
        status=OfferStatus.ACCEPTED
    )
    
    # Visualize the negotiation
    visualization = negotiation_component.visualize_negotiation(negotiation_id)
    
    print(f"Negotiation visualization: {len(visualization['timeline'])} events")
    
    # Stop the component
    negotiation_component.stop()
"""
