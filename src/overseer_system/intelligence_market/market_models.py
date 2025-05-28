"""
Market Models for the Intelligence Market Phase of the Overseer System.

This module defines the data models used by the Intelligence Market components,
including bid models, market metrics, and transaction records.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any

from pydantic import BaseModel, Field, validator

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("intelligence_market.models")

class BidStatus(str, Enum):
    """Enumeration of possible bid statuses."""
    PENDING = "pending"
    ACTIVE = "active"
    MATCHED = "matched"
    EXECUTED = "executed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

class BidType(str, Enum):
    """Enumeration of possible bid types."""
    FIXED = "fixed"
    AUCTION = "auction"
    DUTCH = "dutch"
    ENGLISH = "english"
    SEALED = "sealed"
    VICKREY = "vickrey"
    CONTINUOUS = "continuous"

class ResourceType(str, Enum):
    """Enumeration of possible resource types."""
    COMPUTE = "compute"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    MODEL = "model"
    DATA = "data"
    SKILL = "skill"
    KNOWLEDGE = "knowledge"
    TIME = "time"
    ATTENTION = "attention"

class MarketRole(str, Enum):
    """Enumeration of possible market roles."""
    BUYER = "buyer"
    SELLER = "seller"
    BROKER = "broker"
    VALIDATOR = "validator"
    REGULATOR = "regulator"
    OBSERVER = "observer"

class MarketStatus(str, Enum):
    """Enumeration of possible market statuses."""
    STABLE = "stable"
    VOLATILE = "volatile"
    GROWING = "growing"
    SHRINKING = "shrinking"
    FROZEN = "frozen"
    RECOVERING = "recovering"
    UNKNOWN = "unknown"

class InterventionType(str, Enum):
    """Enumeration of possible market intervention types."""
    PRICE_FLOOR = "price_floor"
    PRICE_CEILING = "price_ceiling"
    SUPPLY_INCREASE = "supply_increase"
    SUPPLY_DECREASE = "supply_decrease"
    DEMAND_STIMULATION = "demand_stimulation"
    DEMAND_REDUCTION = "demand_reduction"
    MARKET_PAUSE = "market_pause"
    MARKET_RESET = "market_reset"
    RULE_CHANGE = "rule_change"
    PARTICIPANT_RESTRICTION = "participant_restriction"

class AgentCapability(BaseModel):
    """Model for agent capability."""
    capability_id: str = Field(..., description="Unique capability identifier")
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    version: str = Field(..., description="Capability version")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Capability parameters")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    resource_requirements: Dict[str, float] = Field(default_factory=dict, description="Resource requirements")
    tags: List[str] = Field(default_factory=list, description="Capability tags")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AgentProfile(BaseModel):
    """Model for agent profile."""
    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    version: str = Field(..., description="Agent version")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    trust_score: float = Field(0.0, description="Agent trust score (0.0 to 1.0)")
    performance_history: Dict[str, List[float]] = Field(default_factory=dict, description="Performance history")
    market_roles: List[MarketRole] = Field(default_factory=list, description="Agent market roles")
    resource_availability: Dict[ResourceType, float] = Field(default_factory=dict, description="Resource availability")
    pricing_strategy: Dict[str, Any] = Field(default_factory=dict, description="Pricing strategy")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="Agent preferences")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Agent constraints")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class ResourceSpecification(BaseModel):
    """Model for resource specification."""
    resource_type: ResourceType = Field(..., description="Resource type")
    quantity: float = Field(..., description="Resource quantity")
    unit: str = Field(..., description="Resource unit")
    quality_metrics: Dict[str, float] = Field(default_factory=dict, description="Quality metrics")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Resource constraints")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class PriceSpecification(BaseModel):
    """Model for price specification."""
    currency: str = Field(..., description="Currency code")
    amount: float = Field(..., description="Price amount")
    unit: str = Field(..., description="Price unit")
    min_amount: Optional[float] = Field(None, description="Minimum acceptable amount")
    max_amount: Optional[float] = Field(None, description="Maximum acceptable amount")
    formula: Optional[str] = Field(None, description="Dynamic pricing formula")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Pricing parameters")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class TaskSpecification(BaseModel):
    """Model for task specification."""
    task_id: str = Field(..., description="Unique task identifier")
    name: str = Field(..., description="Task name")
    description: str = Field(..., description="Task description")
    required_capabilities: List[str] = Field(default_factory=list, description="Required capability IDs")
    input_schema: Dict[str, Any] = Field(default_factory=dict, description="Input schema")
    output_schema: Dict[str, Any] = Field(default_factory=dict, description="Output schema")
    constraints: Dict[str, Any] = Field(default_factory=dict, description="Task constraints")
    performance_metrics: Dict[str, Any] = Field(default_factory=dict, description="Performance metrics")
    deadline: Optional[datetime] = Field(None, description="Task deadline")
    priority: int = Field(0, description="Task priority (0-100)")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class Bid(BaseModel):
    """Model for a bid in the intelligence market."""
    bid_id: str = Field(..., description="Unique bid identifier")
    agent_id: str = Field(..., description="Agent ID making the bid")
    bid_type: BidType = Field(..., description="Type of bid")
    role: MarketRole = Field(..., description="Role in the transaction")
    status: BidStatus = Field(BidStatus.PENDING, description="Current bid status")
    created_at: datetime = Field(default_factory=datetime.now, description="Bid creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    expires_at: Optional[datetime] = Field(None, description="Bid expiration timestamp")
    resources: List[ResourceSpecification] = Field(..., description="Resources being bid on")
    price: PriceSpecification = Field(..., description="Bid price specification")
    task: Optional[TaskSpecification] = Field(None, description="Associated task specification")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Bid conditions")
    dependencies: List[str] = Field(default_factory=list, description="Dependent bid IDs")
    signature: Optional[str] = Field(None, description="Cryptographic signature")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    @validator('expires_at')
    def expires_at_must_be_future(cls, v, values):
        """Validate that expiration is in the future."""
        if v and v <= values.get('created_at', datetime.now()):
            raise ValueError('expires_at must be in the future')
        return v

class BidMatch(BaseModel):
    """Model for a match between bids."""
    match_id: str = Field(..., description="Unique match identifier")
    buyer_bid_id: str = Field(..., description="Buyer bid ID")
    seller_bid_id: str = Field(..., description="Seller bid ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Match creation timestamp")
    status: str = Field("pending", description="Match status")
    match_price: PriceSpecification = Field(..., description="Agreed price")
    resources: List[ResourceSpecification] = Field(..., description="Agreed resources")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Match conditions")
    execution_plan: Dict[str, Any] = Field(default_factory=dict, description="Execution plan")
    signatures: Dict[str, str] = Field(default_factory=dict, description="Signatures from parties")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class Transaction(BaseModel):
    """Model for a completed transaction."""
    transaction_id: str = Field(..., description="Unique transaction identifier")
    match_id: str = Field(..., description="Associated match ID")
    buyer_id: str = Field(..., description="Buyer agent ID")
    seller_id: str = Field(..., description="Seller agent ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Transaction creation timestamp")
    price: PriceSpecification = Field(..., description="Transaction price")
    resources: List[ResourceSpecification] = Field(..., description="Transacted resources")
    status: str = Field("completed", description="Transaction status")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")
    feedback: Dict[str, Any] = Field(default_factory=dict, description="Transaction feedback")
    receipt: Dict[str, Any] = Field(default_factory=dict, description="Transaction receipt")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MarketMetrics(BaseModel):
    """Model for market metrics."""
    timestamp: datetime = Field(default_factory=datetime.now, description="Metrics timestamp")
    active_agents: int = Field(0, description="Number of active agents")
    active_bids: int = Field(0, description="Number of active bids")
    completed_transactions: int = Field(0, description="Number of completed transactions")
    total_transaction_value: float = Field(0.0, description="Total value of transactions")
    average_price: Dict[ResourceType, float] = Field(default_factory=dict, description="Average price by resource type")
    price_volatility: Dict[ResourceType, float] = Field(default_factory=dict, description="Price volatility by resource type")
    supply_demand_ratio: Dict[ResourceType, float] = Field(default_factory=dict, description="Supply/demand ratio by resource type")
    market_concentration: float = Field(0.0, description="Market concentration (0.0 to 1.0)")
    market_status: MarketStatus = Field(MarketStatus.UNKNOWN, description="Overall market status")
    resource_utilization: Dict[ResourceType, float] = Field(default_factory=dict, description="Resource utilization by type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MarketIntervention(BaseModel):
    """Model for market intervention."""
    intervention_id: str = Field(..., description="Unique intervention identifier")
    created_at: datetime = Field(default_factory=datetime.now, description="Intervention creation timestamp")
    intervention_type: InterventionType = Field(..., description="Type of intervention")
    target_resources: List[ResourceType] = Field(default_factory=list, description="Target resource types")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Intervention parameters")
    reason: str = Field(..., description="Reason for intervention")
    expected_impact: Dict[str, Any] = Field(default_factory=dict, description="Expected impact")
    actual_impact: Optional[Dict[str, Any]] = Field(None, description="Actual impact (after evaluation)")
    status: str = Field("pending", description="Intervention status")
    duration: Optional[timedelta] = Field(None, description="Intervention duration")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class AuctionConfig(BaseModel):
    """Model for auction configuration."""
    auction_id: str = Field(..., description="Unique auction identifier")
    auction_type: BidType = Field(..., description="Type of auction")
    resource_types: List[ResourceType] = Field(..., description="Resource types being auctioned")
    start_time: datetime = Field(..., description="Auction start time")
    end_time: Optional[datetime] = Field(None, description="Auction end time")
    min_price: Optional[PriceSpecification] = Field(None, description="Minimum price")
    max_price: Optional[PriceSpecification] = Field(None, description="Maximum price")
    increment_rules: Dict[str, Any] = Field(default_factory=dict, description="Bid increment rules")
    participation_requirements: Dict[str, Any] = Field(default_factory=dict, description="Participation requirements")
    visibility: str = Field("public", description="Auction visibility")
    rules: Dict[str, Any] = Field(default_factory=dict, description="Auction rules")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class MarketPolicy(BaseModel):
    """Model for market policy."""
    policy_id: str = Field(..., description="Unique policy identifier")
    name: str = Field(..., description="Policy name")
    description: str = Field(..., description="Policy description")
    created_at: datetime = Field(default_factory=datetime.now, description="Policy creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    active: bool = Field(True, description="Whether policy is active")
    rules: List[Dict[str, Any]] = Field(..., description="Policy rules")
    scope: Dict[str, Any] = Field(default_factory=dict, description="Policy scope")
    enforcement_mechanism: str = Field(..., description="Enforcement mechanism")
    penalties: Dict[str, Any] = Field(default_factory=dict, description="Penalties for violations")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class FeedbackRecord(BaseModel):
    """Model for feedback record."""
    feedback_id: str = Field(..., description="Unique feedback identifier")
    transaction_id: str = Field(..., description="Associated transaction ID")
    agent_id: str = Field(..., description="Agent providing feedback")
    target_id: str = Field(..., description="Target agent ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Feedback creation timestamp")
    rating: float = Field(..., description="Rating (0.0 to 1.0)")
    categories: Dict[str, float] = Field(default_factory=dict, description="Category-specific ratings")
    comments: Optional[str] = Field(None, description="Feedback comments")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting evidence")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class DisputeRecord(BaseModel):
    """Model for dispute record."""
    dispute_id: str = Field(..., description="Unique dispute identifier")
    transaction_id: str = Field(..., description="Associated transaction ID")
    initiator_id: str = Field(..., description="Initiator agent ID")
    respondent_id: str = Field(..., description="Respondent agent ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Dispute creation timestamp")
    status: str = Field("open", description="Dispute status")
    reason: str = Field(..., description="Reason for dispute")
    evidence: Dict[str, Any] = Field(default_factory=dict, description="Supporting evidence")
    resolution: Optional[Dict[str, Any]] = Field(None, description="Dispute resolution")
    arbitrator_id: Optional[str] = Field(None, description="Arbitrator agent ID")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

# Helper functions for model creation

def create_bid(
    agent_id: str,
    bid_type: BidType,
    role: MarketRole,
    resources: List[ResourceSpecification],
    price: PriceSpecification,
    task: Optional[TaskSpecification] = None,
    conditions: Dict[str, Any] = None,
    dependencies: List[str] = None,
    expires_in_hours: Optional[int] = 24,
    metadata: Dict[str, Any] = None
) -> Bid:
    """
    Create a new bid with generated ID and timestamps.
    
    Args:
        agent_id: Agent ID making the bid
        bid_type: Type of bid
        role: Role in the transaction
        resources: Resources being bid on
        price: Bid price specification
        task: Associated task specification
        conditions: Bid conditions
        dependencies: Dependent bid IDs
        expires_in_hours: Hours until expiration
        metadata: Additional metadata
        
    Returns:
        Bid: The created bid
    """
    bid_id = f"bid-{uuid.uuid4()}"
    now = datetime.now()
    expires_at = now + timedelta(hours=expires_in_hours) if expires_in_hours else None
    
    return Bid(
        bid_id=bid_id,
        agent_id=agent_id,
        bid_type=bid_type,
        role=role,
        status=BidStatus.PENDING,
        created_at=now,
        updated_at=now,
        expires_at=expires_at,
        resources=resources,
        price=price,
        task=task,
        conditions=conditions or {},
        dependencies=dependencies or [],
        metadata=metadata or {}
    )

def create_market_metrics() -> MarketMetrics:
    """
    Create a new market metrics object with default values.
    
    Returns:
        MarketMetrics: The created market metrics
    """
    return MarketMetrics(
        timestamp=datetime.now(),
        active_agents=0,
        active_bids=0,
        completed_transactions=0,
        total_transaction_value=0.0,
        average_price={},
        price_volatility={},
        supply_demand_ratio={},
        market_concentration=0.0,
        market_status=MarketStatus.UNKNOWN,
        resource_utilization={}
    )

def create_intervention(
    intervention_type: InterventionType,
    target_resources: List[ResourceType],
    reason: str,
    parameters: Dict[str, Any] = None,
    expected_impact: Dict[str, Any] = None,
    duration_hours: Optional[int] = None,
    metadata: Dict[str, Any] = None
) -> MarketIntervention:
    """
    Create a new market intervention with generated ID and timestamps.
    
    Args:
        intervention_type: Type of intervention
        target_resources: Target resource types
        reason: Reason for intervention
        parameters: Intervention parameters
        expected_impact: Expected impact
        duration_hours: Intervention duration in hours
        metadata: Additional metadata
        
    Returns:
        MarketIntervention: The created intervention
    """
    intervention_id = f"intervention-{uuid.uuid4()}"
    duration = timedelta(hours=duration_hours) if duration_hours else None
    
    return MarketIntervention(
        intervention_id=intervention_id,
        created_at=datetime.now(),
        intervention_type=intervention_type,
        target_resources=target_resources,
        parameters=parameters or {},
        reason=reason,
        expected_impact=expected_impact or {},
        status="pending",
        duration=duration,
        metadata=metadata or {}
    )

def create_transaction_from_match(
    match: BidMatch,
    buyer_id: str,
    seller_id: str,
    status: str = "completed",
    performance_metrics: Dict[str, float] = None,
    feedback: Dict[str, Any] = None,
    metadata: Dict[str, Any] = None
) -> Transaction:
    """
    Create a new transaction from a bid match.
    
    Args:
        match: The bid match
        buyer_id: Buyer agent ID
        seller_id: Seller agent ID
        status: Transaction status
        performance_metrics: Performance metrics
        feedback: Transaction feedback
        metadata: Additional metadata
        
    Returns:
        Transaction: The created transaction
    """
    transaction_id = f"transaction-{uuid.uuid4()}"
    
    return Transaction(
        transaction_id=transaction_id,
        match_id=match.match_id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        created_at=datetime.now(),
        price=match.match_price,
        resources=match.resources,
        status=status,
        performance_metrics=performance_metrics or {},
        feedback=feedback or {},
        receipt={
            "match_id": match.match_id,
            "timestamp": datetime.now().isoformat(),
            "status": status
        },
        metadata=metadata or {}
    )
