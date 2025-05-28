"""
Reactive Protocol Contracts for Industriverse Protocol Layer

This module implements Reactive Protocol Contracts, enabling dynamic, 
event-driven agreements between protocol components with automatic 
enforcement and adaptation capabilities.

Features:
1. Contract definition and validation
2. Event-driven contract execution
3. Automatic enforcement of contract terms
4. Contract state monitoring and reporting
5. Dynamic adaptation based on performance metrics
6. Integration with Trust Fabric for contract verification
"""

import uuid
import time
import asyncio
import logging
from enum import Enum
from typing import Dict, List, Any, Optional, Union, Callable, Awaitable, Tuple, Set
from dataclasses import dataclass, field

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


class ContractStatus(Enum):
    """Status of a reactive protocol contract."""
    DRAFT = "draft"
    PROPOSED = "proposed"
    ACTIVE = "active"
    VIOLATED = "violated"
    COMPLETED = "completed"
    TERMINATED = "terminated"
    EXPIRED = "expired"


class TermType(Enum):
    """Types of contract terms."""
    CONDITION = "condition"  # A condition that must be met
    OBLIGATION = "obligation"  # An action that must be performed
    PROHIBITION = "prohibition"  # An action that must not be performed
    PERMISSION = "permission"  # An action that is allowed


class TermStatus(Enum):
    """Status of a contract term."""
    INACTIVE = "inactive"  # Term is not yet active
    ACTIVE = "active"  # Term is active and being monitored
    FULFILLED = "fulfilled"  # Term has been fulfilled
    VIOLATED = "violated"  # Term has been violated
    WAIVED = "waived"  # Term has been waived


@dataclass
class ContractTerm:
    """
    Represents a term in a reactive protocol contract.
    """
    term_id: str
    term_type: TermType
    description: str
    condition: Dict[str, Any]  # Condition for activation/evaluation
    action: Optional[Dict[str, Any]] = None  # Action to perform (for obligations)
    status: TermStatus = TermStatus.INACTIVE
    activation_time: float = 0.0
    fulfillment_time: float = 0.0
    violation_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "term_id": self.term_id,
            "term_type": self.term_type.value,
            "description": self.description,
            "condition": self.condition,
            "action": self.action,
            "status": self.status.value,
            "activation_time": self.activation_time,
            "fulfillment_time": self.fulfillment_time,
            "violation_time": self.violation_time,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContractTerm':
        """Create from dictionary representation."""
        return cls(
            term_id=data["term_id"],
            term_type=TermType(data["term_type"]),
            description=data["description"],
            condition=data["condition"],
            action=data.get("action"),
            status=TermStatus(data.get("status", "inactive")),
            activation_time=data.get("activation_time", 0.0),
            fulfillment_time=data.get("fulfillment_time", 0.0),
            violation_time=data.get("violation_time", 0.0),
            metadata=data.get("metadata", {})
        )


@dataclass
class ReactiveContract:
    """
    Represents a reactive protocol contract between components.
    """
    contract_id: str
    name: str
    description: str
    parties: List[str]  # Component IDs of parties involved
    terms: List[ContractTerm]
    status: ContractStatus = ContractStatus.DRAFT
    creation_time: float = field(default_factory=time.time)
    activation_time: float = 0.0
    expiration_time: float = 0.0
    termination_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_term(self, term: ContractTerm) -> None:
        """Add a term to the contract."""
        self.terms.append(term)
    
    def get_term(self, term_id: str) -> Optional[ContractTerm]:
        """Get a term by ID."""
        for term in self.terms:
            if term.term_id == term_id:
                return term
        return None
    
    def update_status(self, status: ContractStatus) -> None:
        """Update the contract status."""
        self.status = status
        if status == ContractStatus.ACTIVE:
            self.activation_time = time.time()
        elif status in (ContractStatus.COMPLETED, ContractStatus.TERMINATED):
            self.termination_time = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "contract_id": self.contract_id,
            "name": self.name,
            "description": self.description,
            "parties": self.parties,
            "terms": [term.to_dict() for term in self.terms],
            "status": self.status.value,
            "creation_time": self.creation_time,
            "activation_time": self.activation_time,
            "expiration_time": self.expiration_time,
            "termination_time": self.termination_time,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReactiveContract':
        """Create from dictionary representation."""
        contract = cls(
            contract_id=data["contract_id"],
            name=data["name"],
            description=data["description"],
            parties=data["parties"],
            terms=[],
            status=ContractStatus(data.get("status", "draft")),
            creation_time=data.get("creation_time", time.time()),
            activation_time=data.get("activation_time", 0.0),
            expiration_time=data.get("expiration_time", 0.0),
            termination_time=data.get("termination_time", 0.0),
            metadata=data.get("metadata", {})
        )
        for term_data in data.get("terms", []):
            contract.add_term(ContractTerm.from_dict(term_data))
        return contract


class ContractEvaluator:
    """
    Evaluates contract terms based on events and conditions.
    """
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.ContractEvaluator")
    
    async def evaluate_condition(self, condition: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate a condition based on context."""
        condition_type = condition.get("type")
        
        if condition_type == "event":
            # Check if an event matches criteria
            event = context.get("event")
            if not event:
                return False
            
            event_type = condition.get("event_type")
            if event_type and event.get("event_type") != event_type:
                return False
            
            # Check event properties
            properties = condition.get("properties", {})
            for key, value in properties.items():
                if event.get(key) != value:
                    return False
            
            return True
        
        elif condition_type == "time":
            # Check time-based condition
            current_time = context.get("current_time", time.time())
            
            if "after" in condition and current_time < condition["after"]:
                return False
            
            if "before" in condition and current_time >= condition["before"]:
                return False
            
            return True
        
        elif condition_type == "state":
            # Check state-based condition
            state = context.get("state", {})
            
            for key, criteria in condition.get("criteria", {}).items():
                if key not in state:
                    return False
                
                value = state[key]
                
                if "equals" in criteria and value != criteria["equals"]:
                    return False
                
                if "not_equals" in criteria and value == criteria["not_equals"]:
                    return False
                
                if "greater_than" in criteria and not (isinstance(value, (int, float)) and value > criteria["greater_than"]):
                    return False
                
                if "less_than" in criteria and not (isinstance(value, (int, float)) and value < criteria["less_than"]):
                    return False
                
                if "in" in criteria and value not in criteria["in"]:
                    return False
                
                if "not_in" in criteria and value in criteria["not_in"]:
                    return False
            
            return True
        
        elif condition_type == "composite":
            # Composite condition (AND, OR, NOT)
            operator = condition.get("operator", "and")
            subconditions = condition.get("conditions", [])
            
            if not subconditions:
                return True
            
            if operator == "and":
                for subcond in subconditions:
                    if not await self.evaluate_condition(subcond, context):
                        return False
                return True
            
            elif operator == "or":
                for subcond in subconditions:
                    if await self.evaluate_condition(subcond, context):
                        return True
                return False
            
            elif operator == "not":
                if len(subconditions) != 1:
                    self.logger.warning("NOT operator should have exactly one subcondition")
                    return False
                return not await self.evaluate_condition(subconditions[0], context)
            
            else:
                self.logger.warning(f"Unknown composite operator: {operator}")
                return False
        
        else:
            self.logger.warning(f"Unknown condition type: {condition_type}")
            return False
    
    async def evaluate_term(self, term: ContractTerm, context: Dict[str, Any]) -> TermStatus:
        """Evaluate a contract term based on context."""
        # Skip evaluation if term is already fulfilled or violated
        if term.status in (TermStatus.FULFILLED, TermStatus.VIOLATED, TermStatus.WAIVED):
            return term.status
        
        # Activate term if inactive and condition is met
        if term.status == TermStatus.INACTIVE:
            if await self.evaluate_condition(term.condition, context):
                term.status = TermStatus.ACTIVE
                term.activation_time = time.time()
                self.logger.info(f"Term {term.term_id} activated")
        
        # Evaluate active term
        if term.status == TermStatus.ACTIVE:
            if term.term_type == TermType.CONDITION:
                # Condition term is fulfilled if condition is met
                if await self.evaluate_condition(term.condition, context):
                    term.status = TermStatus.FULFILLED
                    term.fulfillment_time = time.time()
                    self.logger.info(f"Condition term {term.term_id} fulfilled")
            
            elif term.term_type == TermType.OBLIGATION:
                # Check if obligation action has been performed
                if "action_performed" in context and context["action_performed"].get("term_id") == term.term_id:
                    term.status = TermStatus.FULFILLED
                    term.fulfillment_time = time.time()
                    self.logger.info(f"Obligation term {term.term_id} fulfilled")
                
                # Check if obligation deadline has passed
                elif "deadline" in term.metadata:
                    current_time = context.get("current_time", time.time())
                    if current_time > term.metadata["deadline"]:
                        term.status = TermStatus.VIOLATED
                        term.violation_time = time.time()
                        self.logger.warning(f"Obligation term {term.term_id} violated (deadline passed)")
            
            elif term.term_type == TermType.PROHIBITION:
                # Prohibition is violated if prohibited action is performed
                if "action_performed" in context and context["action_performed"].get("term_id") == term.term_id:
                    term.status = TermStatus.VIOLATED
                    term.violation_time = time.time()
                    self.logger.warning(f"Prohibition term {term.term_id} violated")
            
            elif term.term_type == TermType.PERMISSION:
                # Permission is always fulfilled if used
                if "action_performed" in context and context["action_performed"].get("term_id") == term.term_id:
                    term.status = TermStatus.FULFILLED
                    term.fulfillment_time = time.time()
                    self.logger.info(f"Permission term {term.term_id} fulfilled (used)")
        
        return term.status


class ReactiveContractService(ProtocolService):
    """
    Service for managing reactive protocol contracts.
    """
    
    def __init__(
        self,
        service_id: str = None,
        config: Dict[str, Any] = None
    ):
        super().__init__(service_id or str(uuid.uuid4()), "reactive_contracts")
        self.config = config or {}
        
        # Initialize contracts
        self.contracts: Dict[str, ReactiveContract] = {}
        
        # Initialize evaluator
        self.evaluator = ContractEvaluator(self.config.get("evaluator", {}))
        
        # State
        self.is_async = True
        self.lock = asyncio.Lock()
        
        self.logger = logging.getLogger(f"{__name__}.ReactiveContractService.{self.component_id[:8]}")
        self.logger.info(f"Reactive Contract Service initialized with ID {self.component_id}")
        
        # Add capabilities
        self.add_capability("contract_management", "Create and manage reactive contracts")
        self.add_capability("contract_enforcement", "Enforce contract terms automatically")
        self.add_capability("contract_monitoring", "Monitor contract state and compliance")
        self.add_capability("contract_adaptation", "Adapt contracts based on performance")

    # --- Contract Management ---

    async def create_contract(self, contract_data: Dict[str, Any]) -> str:
        """Create a new contract."""
        contract_id = contract_data.get("contract_id", str(uuid.uuid4()))
        
        async with self.lock:
            if contract_id in self.contracts:
                self.logger.warning(f"Contract {contract_id} already exists")
                return contract_id
            
            contract = ReactiveContract(
                contract_id=contract_id,
                name=contract_data.get("name", "Unnamed Contract"),
                description=contract_data.get("description", ""),
                parties=contract_data.get("parties", []),
                terms=[],
                status=ContractStatus(contract_data.get("status", "draft")),
                metadata=contract_data.get("metadata", {})
            )
            
            # Add terms
            for term_data in contract_data.get("terms", []):
                term = ContractTerm(
                    term_id=term_data.get("term_id", str(uuid.uuid4())),
                    term_type=TermType(term_data.get("term_type", "condition")),
                    description=term_data.get("description", ""),
                    condition=term_data.get("condition", {}),
                    action=term_data.get("action"),
                    status=TermStatus(term_data.get("status", "inactive")),
                    metadata=term_data.get("metadata", {})
                )
                contract.add_term(term)
            
            # Set expiration if provided
            if "expiration_time" in contract_data:
                contract.expiration_time = contract_data["expiration_time"]
            
            self.contracts[contract_id] = contract
            self.logger.info(f"Created contract {contract_id} with {len(contract.terms)} terms")
        
        # Publish contract creation event
        await self._publish_contract_event(contract_id, "contract_created")
        
        return contract_id

    async def update_contract(self, contract_id: str, updates: Dict[str, Any]) -> bool:
        """Update an existing contract."""
        async with self.lock:
            if contract_id not in self.contracts:
                self.logger.error(f"Contract {contract_id} not found")
                return False
            
            contract = self.contracts[contract_id]
            
            # Only allow updates to draft contracts
            if contract.status != ContractStatus.DRAFT:
                self.logger.warning(f"Cannot update non-draft contract {contract_id}")
                return False
            
            # Update basic properties
            if "name" in updates:
                contract.name = updates["name"]
            
            if "description" in updates:
                contract.description = updates["description"]
            
            if "parties" in updates:
                contract.parties = updates["parties"]
            
            if "metadata" in updates:
                contract.metadata.update(updates["metadata"])
            
            if "expiration_time" in updates:
                contract.expiration_time = updates["expiration_time"]
            
            # Update terms
            if "terms" in updates:
                # Replace all terms
                contract.terms = []
                for term_data in updates["terms"]:
                    term = ContractTerm(
                        term_id=term_data.get("term_id", str(uuid.uuid4())),
                        term_type=TermType(term_data.get("term_type", "condition")),
                        description=term_data.get("description", ""),
                        condition=term_data.get("condition", {}),
                        action=term_data.get("action"),
                        status=TermStatus(term_data.get("status", "inactive")),
                        metadata=term_data.get("metadata", {})
                    )
                    contract.add_term(term)
            
            self.logger.info(f"Updated contract {contract_id}")
        
        # Publish contract update event
        await self._publish_contract_event(contract_id, "contract_updated")
        
        return True

    async def add_term(self, contract_id: str, term_data: Dict[str, Any]) -> Optional[str]:
        """Add a term to an existing contract."""
        async with self.lock:
            if contract_id not in self.contracts:
                self.logger.error(f"Contract {contract_id} not found")
                return None
            
            contract = self.contracts[contract_id]
            
            # Only allow updates to draft contracts
            if contract.status != ContractStatus.DRAFT:
                self.logger.warning(f"Cannot add term to non-draft contract {contract_id}")
                return None
            
            term_id = term_data.get("term_id", str(uuid.uuid4()))
            
            # Check if term ID already exists
            if any(term.term_id == term_id for term in contract.terms):
                self.logger.warning(f"Term {term_id} already exists in contract {contract_id}")
                return term_id
            
            term = ContractTerm(
                term_id=term_id,
                term_type=TermType(term_data.get("term_type", "condition")),
                description=term_data.get("description", ""),
                condition=term_data.get("condition", {}),
                action=term_data.get("action"),
                status=TermStatus(term_data.get("status", "inactive")),
                metadata=term_data.get("metadata", {})
            )
            
            contract.add_term(term)
            self.logger.info(f"Added term {term_id} to contract {contract_id}")
        
        # Publish contract update event
        await self._publish_contract_event(contract_id, "contract_updated")
        
        return term_id

    async def update_term(self, contract_id: str, term_id: str, updates: Dict[str, Any]) -> bool:
        """Update a term in an existing contract."""
        async with self.lock:
            if contract_id not in self.contracts:
                self.logger.error(f"Contract {contract_id} not found")
                return False
            
            contract = self.contracts[contract_id]
            
            # Only allow updates to draft contracts
            if contract.status != ContractStatus.DRAFT:
                self.logger.warning(f"Cannot update term in non-draft contract {contract_id}")
                return False
            
            term = contract.get_term(term_id)
            if not term:
                self.logger.error(f"Term {term_id} not found in contract {contract_id}")
                return False
            
            # Update term properties
            if "description" in updates:
                term.description = updates["description"]
            
            if "condition" in updates:
                term.condition = updates["condition"]
            
            if "action" in updates:
                term.action = updates["action"]
            
            if "metadata" in updates:
                term.metadata.update(updates["metadata"])
            
            self.logger.info(f"Updated term {term_id} in contract {contract_id}")
        
        # Publish contract update event
        await self._publish_contract_event(contract_id, "contract_updated")
        
        return True

    async def activate_contract(self, contract_id: str) -> bool:
        """Activate a contract."""
        async with self.lock:
            if contract_id not in self.contracts:
                self.logger.error(f"Contract {contract_id} not found")
                return False
            
            contract = self.contracts[contract_id]
            
            # Only allow activation of draft or proposed contracts
            if contract.status not in (ContractStatus.DRAFT, ContractStatus.PROPOSED):
                self.logger.warning(f"Cannot activate contract {contract_id} with status {contract.status}")
                return False
            
            contract.update_status(ContractStatus.ACTIVE)
            self.logger.info(f"Activated contract {contract_id}")
        
        # Publish contract activation event
        await self._publish_contract_event(contract_id, "contract_activated")
        
        return True

    async def terminate_contract(self, contract_id: str, reason: str = None) -> bool:
        """Terminate a contract."""
        async with self.lock:
            if contract_id not in self.contracts:
                self.logger.error(f"Contract {contract_id} not found")
                return False
            
            contract = self.contracts[contract_id]
            
            # Only allow termination of active contracts
            if contract.status != ContractStatus.ACTIVE:
                self.logger.warning(f"Cannot terminate contract {contract_id} with status {contract.status}")
                return False
            
            contract.update_status(ContractStatus.TERMINATED)
            if reason:
                contract.metadata["termination_reason"] = reason
            
            self.logger.info(f"Terminated contract {contract_id}")
        
        # Publish contract termination event
        await self._publish_contract_event(contract_id, "contract_terminated", {"reason": reason})
        
        return True

    async def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Get a contract by ID."""
        async with self.lock:
            if contract_id not in self.contracts:
                self.logger.error(f"Contract {contract_id} not found")
                return None
            
            return self.contracts[contract_id].to_dict()

    async def list_contracts(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List contracts with optional filtering."""
        filters = filters or {}
        
        async with self.lock:
            contracts = list(self.contracts.values())
        
        # Apply filters
        if "status" in filters:
            status = ContractStatus(filters["status"])
            contracts = [c for c in contracts if c.status == status]
        
        if "party" in filters:
            party = filters["party"]
            contracts = [c for c in contracts if party in c.parties]
        
        # Convert to dict representation
        return [contract.to_dict() for contract in contracts]

    # --- Contract Evaluation and Enforcement ---

    async def process_event(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process an event and evaluate relevant contracts."""
        event_type = event.get("event_type")
        self.logger.debug(f"Processing event of type {event_type}")
        
        # Prepare context for evaluation
        context = {
            "event": event,
            "current_time": time.time()
        }
        
        # Track changes for notification
        changes = []
        
        async with self.lock:
            # Process active contracts
            active_contracts = [c for c in self.contracts.values() if c.status == ContractStatus.ACTIVE]
            
            for contract in active_contracts:
                # Check for contract expiration
                if contract.expiration_time > 0 and context["current_time"] > contract.expiration_time:
                    contract.update_status(ContractStatus.EXPIRED)
                    self.logger.info(f"Contract {contract.contract_id} expired")
                    changes.append({
                        "contract_id": contract.contract_id,
                        "type": "contract_expired"
                    })
                    continue
                
                # Evaluate terms
                for term in contract.terms:
                    old_status = term.status
                    new_status = await self.evaluator.evaluate_term(term, context)
                    
                    if new_status != old_status:
                        changes.append({
                            "contract_id": contract.contract_id,
                            "term_id": term.term_id,
                            "type": "term_status_changed",
                            "old_status": old_status.value,
                            "new_status": new_status.value
                        })
                
                # Check if contract is violated
                violated_terms = [t for t in contract.terms if t.status == TermStatus.VIOLATED]
                if violated_terms and contract.status != ContractStatus.VIOLATED:
                    contract.update_status(ContractStatus.VIOLATED)
                    self.logger.warning(f"Contract {contract.contract_id} violated")
                    changes.append({
                        "contract_id": contract.contract_id,
                        "type": "contract_violated",
                        "violated_terms": [t.term_id for t in violated_terms]
                    })
                
                # Check if contract is completed
                active_terms = [t for t in contract.terms if t.status not in (TermStatus.FULFILLED, TermStatus.WAIVED)]
                if not active_terms and contract.status == ContractStatus.ACTIVE:
                    contract.update_status(ContractStatus.COMPLETED)
                    self.logger.info(f"Contract {contract.contract_id} completed")
                    changes.append({
                        "contract_id": contract.contract_id,
                        "type": "contract_completed"
                    })
        
        # Publish events for changes
        for change in changes:
            await self._publish_contract_event(
                change["contract_id"],
                change["type"],
                {k: v for k, v in change.items() if k not in ("contract_id", "type")}
            )
        
        return changes

    async def perform_action(self, contract_id: str, term_id: str, action_data: Dict[str, Any]) -> bool:
        """Record an action performed for a contract term."""
        async with self.lock:
            if contract_id not in self.contracts:
                self.logger.error(f"Contract {contract_id} not found")
                return False
            
            contract = self.contracts[contract_id]
            term = contract.get_term(term_id)
            
            if not term:
                self.logger.error(f"Term {term_id} not found in contract {contract_id}")
                return False
            
            if contract.status != ContractStatus.ACTIVE:
                self.logger.warning(f"Cannot perform action for inactive contract {contract_id}")
                return False
            
            if term.status != TermStatus.ACTIVE:
                self.logger.warning(f"Cannot perform action for inactive term {term_id}")
                return False
        
        # Process the action as an event
        event = {
            "event_type": "action_performed",
            "contract_id": contract_id,
            "term_id": term_id,
            "action": action_data,
            "timestamp": time.time()
        }
        
        context = {
            "event": event,
            "current_time": event["timestamp"],
            "action_performed": {
                "term_id": term_id,
                "data": action_data
            }
        }
        
        # Evaluate the term with this action
        async with self.lock:
            term = self.contracts[contract_id].get_term(term_id)
            old_status = term.status
            new_status = await self.evaluator.evaluate_term(term, context)
        
        # Publish action event
        await self._publish_contract_event(
            contract_id,
            "action_performed",
            {
                "term_id": term_id,
                "action": action_data,
                "old_status": old_status.value,
                "new_status": new_status.value
            }
        )
        
        return True

    async def waive_term(self, contract_id: str, term_id: str, reason: str = None) -> bool:
        """Waive a contract term."""
        async with self.lock:
            if contract_id not in self.contracts:
                self.logger.error(f"Contract {contract_id} not found")
                return False
            
            contract = self.contracts[contract_id]
            term = contract.get_term(term_id)
            
            if not term:
                self.logger.error(f"Term {term_id} not found in contract {contract_id}")
                return False
            
            if term.status not in (TermStatus.ACTIVE, TermStatus.VIOLATED):
                self.logger.warning(f"Cannot waive term {term_id} with status {term.status}")
                return False
            
            term.status = TermStatus.WAIVED
            term.metadata["waived_time"] = time.time()
            if reason:
                term.metadata["waive_reason"] = reason
            
            self.logger.info(f"Waived term {term_id} in contract {contract_id}")
        
        # Publish term waived event
        await self._publish_contract_event(
            contract_id,
            "term_waived",
            {
                "term_id": term_id,
                "reason": reason
            }
        )
        
        return True

    # --- Event Publishing ---

    async def _publish_contract_event(self, contract_id: str, event_type: str, data: Dict[str, Any] = None) -> None:
        """Publish a contract-related event."""
        data = data or {}
        
        # Create event message
        event = {
            "event_type": f"contract.{event_type}",
            "contract_id": contract_id,
            "timestamp": time.time(),
            "data": data
        }
        
        # In a real implementation, this would publish to an event bus or message broker
        self.logger.debug(f"Published event: {event_type} for contract {contract_id}")
        
        # Process the event (for self-triggering)
        await self.process_event(event)

    # --- ProtocolService Methods ---

    async def process_message_async(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process an incoming message."""
        msg_obj = MessageFactory.create_from_dict(message)
        if not msg_obj:
            return MessageFactory.create_error("invalid_message", "Could not parse message").to_dict()

        response_payload = None
        status = MessageStatus.SUCCESS

        if isinstance(msg_obj, CommandMessage):
            if msg_obj.command == "create_contract":
                contract_id = await self.create_contract(msg_obj.params)
                response_payload = {"contract_id": contract_id}
            
            elif msg_obj.command == "update_contract":
                params = msg_obj.params
                if "contract_id" in params and "updates" in params:
                    success = await self.update_contract(params["contract_id"], params["updates"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing contract_id or updates"}
            
            elif msg_obj.command == "add_term":
                params = msg_obj.params
                if "contract_id" in params and "term" in params:
                    term_id = await self.add_term(params["contract_id"], params["term"])
                    if term_id:
                        response_payload = {"term_id": term_id}
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Failed to add term"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing contract_id or term"}
            
            elif msg_obj.command == "update_term":
                params = msg_obj.params
                if "contract_id" in params and "term_id" in params and "updates" in params:
                    success = await self.update_term(params["contract_id"], params["term_id"], params["updates"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing contract_id, term_id, or updates"}
            
            elif msg_obj.command == "activate_contract":
                params = msg_obj.params
                if "contract_id" in params:
                    success = await self.activate_contract(params["contract_id"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing contract_id"}
            
            elif msg_obj.command == "terminate_contract":
                params = msg_obj.params
                if "contract_id" in params:
                    success = await self.terminate_contract(params["contract_id"], params.get("reason"))
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing contract_id"}
            
            elif msg_obj.command == "perform_action":
                params = msg_obj.params
                if "contract_id" in params and "term_id" in params and "action_data" in params:
                    success = await self.perform_action(params["contract_id"], params["term_id"], params["action_data"])
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing contract_id, term_id, or action_data"}
            
            elif msg_obj.command == "waive_term":
                params = msg_obj.params
                if "contract_id" in params and "term_id" in params:
                    success = await self.waive_term(params["contract_id"], params["term_id"], params.get("reason"))
                    response_payload = {"success": success}
                    if not success:
                        status = MessageStatus.FAILED
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing contract_id or term_id"}
            
            elif msg_obj.command == "process_event":
                params = msg_obj.params
                if "event" in params:
                    changes = await self.process_event(params["event"])
                    response_payload = {"changes": changes}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing event"}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported command: {msg_obj.command}"}
        
        elif isinstance(msg_obj, QueryMessage):
            if msg_obj.query == "get_contract":
                params = msg_obj.params
                if "contract_id" in params:
                    contract = await self.get_contract(params["contract_id"])
                    if contract:
                        response_payload = contract
                    else:
                        status = MessageStatus.FAILED
                        response_payload = {"error": "Contract not found"}
                else:
                    status = MessageStatus.FAILED
                    response_payload = {"error": "Missing contract_id"}
            
            elif msg_obj.query == "list_contracts":
                contracts = await self.list_contracts(msg_obj.params.get("filters"))
                response_payload = {"contracts": contracts}
            
            else:
                status = MessageStatus.FAILED
                response_payload = {"error": f"Unsupported query: {msg_obj.query}"}
        
        elif isinstance(msg_obj, EventMessage):
            # Process events
            if msg_obj.event_type.startswith("contract.") or msg_obj.event_type in ("action_performed", "state_changed"):
                changes = await self.process_event(msg_obj.to_dict())
                # No response needed for events
                return None
        
        else:
            # Ignore other message types
            return None

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
            num_contracts = len(self.contracts)
            num_active = sum(1 for c in self.contracts.values() if c.status == ContractStatus.ACTIVE)
            num_violated = sum(1 for c in self.contracts.values() if c.status == ContractStatus.VIOLATED)
            num_completed = sum(1 for c in self.contracts.values() if c.status == ContractStatus.COMPLETED)
        
        return {
            "status": "healthy",
            "contracts": {
                "total": num_contracts,
                "active": num_active,
                "violated": num_violated,
                "completed": num_completed
            }
        }

    async def get_manifest(self) -> Dict[str, Any]:
        """Get the component manifest."""
        manifest = await super().get_manifest()
        health = await self.health_check()
        manifest.update(health)
        return manifest
"""
