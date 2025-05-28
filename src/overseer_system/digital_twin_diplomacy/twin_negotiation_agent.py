"""
Twin Negotiation Agent for the Digital Twin Diplomacy Phase of the Overseer System.

This module provides capabilities for managing negotiations between digital twins
with conflicting goals, ensuring optimal resource allocation and conflict resolution.

Author: Manus AI
Date: May 25, 2025
"""

import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set, Union

# Import MCP and A2A integration
from src.mcp_integration.mcp_protocol_bridge import MCPProtocolBridge
from src.a2a_integration.a2a_protocol_bridge import A2AProtocolBridge
from src.event_bus.kafka_client import KafkaClient
from src.data_access.data_access_service import DataAccessService

# Import diplomacy models
from .diplomacy_models import (
    NegotiationSession, NegotiationProposal, NegotiationAgreement,
    ResourceSpecification, ResourceType, NegotiationStatus, ProposalStatus,
    ResourceConflict, ConflictResolution, ConflictType, ConflictSeverity,
    ResolutionStrategy, create_negotiation_session, create_negotiation_proposal,
    create_negotiation_agreement, create_resource_conflict, create_conflict_resolution
)

class NegotiationStrategy:
    """Base class for negotiation strategies."""
    
    def __init__(self, name: str, description: str):
        """
        Initialize a negotiation strategy.
        
        Args:
            name: Strategy name
            description: Strategy description
        """
        self.name = name
        self.description = description
    
    def generate_proposal(
        self,
        session: NegotiationSession,
        agent_id: str,
        resources: List[ResourceSpecification],
        context: Dict[str, Any]
    ) -> NegotiationProposal:
        """
        Generate a proposal based on the strategy.
        
        Args:
            session: Negotiation session
            agent_id: ID of the proposing agent
            resources: List of resource specifications
            context: Additional context
            
        Returns:
            NegotiationProposal: Generated proposal
        """
        raise NotImplementedError("Subclasses must implement generate_proposal")
    
    def evaluate_proposal(
        self,
        proposal: NegotiationProposal,
        agent_id: str,
        resources: List[ResourceSpecification],
        context: Dict[str, Any]
    ) -> Tuple[str, Optional[str], Optional[NegotiationProposal]]:
        """
        Evaluate a proposal based on the strategy.
        
        Args:
            proposal: Proposal to evaluate
            agent_id: ID of the evaluating agent
            resources: List of resource specifications
            context: Additional context
            
        Returns:
            Tuple[str, Optional[str], Optional[NegotiationProposal]]:
                - Response (accept, reject, counter)
                - Rationale (optional)
                - Counter proposal (optional)
        """
        raise NotImplementedError("Subclasses must implement evaluate_proposal")

class CompromiseStrategy(NegotiationStrategy):
    """Strategy focused on finding middle ground."""
    
    def __init__(self):
        """Initialize the compromise strategy."""
        super().__init__(
            name="compromise",
            description="Seeks middle ground between conflicting resource requirements"
        )
    
    def generate_proposal(
        self,
        session: NegotiationSession,
        agent_id: str,
        resources: List[ResourceSpecification],
        context: Dict[str, Any]
    ) -> NegotiationProposal:
        """
        Generate a compromise proposal.
        
        Args:
            session: Negotiation session
            agent_id: ID of the proposing agent
            resources: List of resource specifications
            context: Additional context
            
        Returns:
            NegotiationProposal: Generated proposal
        """
        # If this is a counter-proposal, adjust based on previous proposals
        latest_proposal = session.get_latest_proposal()
        
        if latest_proposal and latest_proposal.proposer_id != agent_id:
            # Create a compromise between our resources and the latest proposal
            compromise_resources = []
            
            # Map resources by type for easier comparison
            our_resources_by_type = {r.resource_type: r for r in resources}
            their_resources_by_type = {r.resource_type: r for r in latest_proposal.resources}
            
            # Find common resource types
            common_types = set(our_resources_by_type.keys()) & set(their_resources_by_type.keys())
            
            for resource_type in common_types:
                our_resource = our_resources_by_type[resource_type]
                their_resource = their_resources_by_type[resource_type]
                
                # Calculate compromise quantity
                compromise_quantity = (our_resource.quantity + their_resource.quantity) / 2
                
                # Create compromise resource
                compromise_resource = ResourceSpecification(
                    resource_type=resource_type,
                    quantity=compromise_quantity,
                    unit=our_resource.unit,
                    priority=our_resource.priority,
                    min_acceptable=min(our_resource.min_acceptable, their_resource.min_acceptable),
                    max_acceptable=max(our_resource.max_acceptable, their_resource.max_acceptable),
                    temporal_constraints=our_resource.temporal_constraints,
                    quality_requirements=our_resource.quality_requirements,
                    metadata=our_resource.metadata
                )
                
                compromise_resources.append(compromise_resource)
            
            # Add non-common resources with reduced quantities
            for resource_type, resource in our_resources_by_type.items():
                if resource_type not in common_types:
                    adjusted_resource = ResourceSpecification(
                        resource_type=resource.resource_type,
                        quantity=resource.quantity * 0.9,  # Reduce by 10%
                        unit=resource.unit,
                        priority=resource.priority,
                        min_acceptable=resource.min_acceptable,
                        max_acceptable=resource.max_acceptable,
                        temporal_constraints=resource.temporal_constraints,
                        quality_requirements=resource.quality_requirements,
                        metadata=resource.metadata
                    )
                    compromise_resources.append(adjusted_resource)
            
            rationale = "Compromise proposal based on previous negotiations"
            
            return create_negotiation_proposal(
                session_id=session.session_id,
                proposer_id=agent_id,
                resources=compromise_resources,
                counter_to=latest_proposal.proposal_id,
                rationale=rationale,
                metadata={"strategy": self.name}
            )
        
        # If this is the first proposal, use our resources directly
        return create_negotiation_proposal(
            session_id=session.session_id,
            proposer_id=agent_id,
            resources=resources,
            rationale="Initial proposal",
            metadata={"strategy": self.name}
        )
    
    def evaluate_proposal(
        self,
        proposal: NegotiationProposal,
        agent_id: str,
        resources: List[ResourceSpecification],
        context: Dict[str, Any]
    ) -> Tuple[str, Optional[str], Optional[NegotiationProposal]]:
        """
        Evaluate a proposal using compromise strategy.
        
        Args:
            proposal: Proposal to evaluate
            agent_id: ID of the evaluating agent
            resources: List of resource specifications
            context: Additional context
            
        Returns:
            Tuple[str, Optional[str], Optional[NegotiationProposal]]:
                - Response (accept, reject, counter)
                - Rationale (optional)
                - Counter proposal (optional)
        """
        # Map resources by type for easier comparison
        our_resources_by_type = {r.resource_type: r for r in resources}
        their_resources_by_type = {r.resource_type: r for r in proposal.resources}
        
        # Find common resource types
        common_types = set(our_resources_by_type.keys()) & set(their_resources_by_type.keys())
        
        # Calculate compatibility score
        compatibility_score = 0
        max_possible_score = len(common_types)
        
        for resource_type in common_types:
            our_resource = our_resources_by_type[resource_type]
            their_resource = their_resources_by_type[resource_type]
            
            if our_resource.is_compatible_with(their_resource):
                compatibility_score += 1
        
        # If no common types, reject
        if not common_types:
            return "reject", "No common resource types", None
        
        # Calculate compatibility percentage
        compatibility_percentage = (compatibility_score / max_possible_score) * 100
        
        # Accept if compatibility is high
        if compatibility_percentage >= 80:
            return "accept", f"Proposal is compatible ({compatibility_percentage:.1f}%)", None
        
        # Counter if compatibility is moderate
        elif compatibility_percentage >= 40:
            # Create counter proposal
            session = context.get("session")
            if not session:
                return "reject", "Missing session context", None
            
            counter_proposal = self.generate_proposal(
                session=session,
                agent_id=agent_id,
                resources=resources,
                context=context
            )
            
            return "counter", f"Proposing compromise ({compatibility_percentage:.1f}% compatible)", counter_proposal
        
        # Reject if compatibility is low
        else:
            return "reject", f"Proposal is not compatible ({compatibility_percentage:.1f}%)", None

class CollaborativeStrategy(NegotiationStrategy):
    """Strategy focused on maximizing joint value."""
    
    def __init__(self):
        """Initialize the collaborative strategy."""
        super().__init__(
            name="collaborative",
            description="Seeks to maximize joint value through creative solutions"
        )
    
    def generate_proposal(
        self,
        session: NegotiationSession,
        agent_id: str,
        resources: List[ResourceSpecification],
        context: Dict[str, Any]
    ) -> NegotiationProposal:
        """
        Generate a collaborative proposal.
        
        Args:
            session: Negotiation session
            agent_id: ID of the proposing agent
            resources: List of resource specifications
            context: Additional context
            
        Returns:
            NegotiationProposal: Generated proposal
        """
        # If this is a counter-proposal, adjust based on previous proposals
        latest_proposal = session.get_latest_proposal()
        
        if latest_proposal and latest_proposal.proposer_id != agent_id:
            # Create a collaborative proposal that tries to satisfy both parties
            collaborative_resources = []
            
            # Map resources by type for easier comparison
            our_resources_by_type = {r.resource_type: r for r in resources}
            their_resources_by_type = {r.resource_type: r for r in latest_proposal.resources}
            
            # Find common resource types
            common_types = set(our_resources_by_type.keys()) & set(their_resources_by_type.keys())
            
            for resource_type in common_types:
                our_resource = our_resources_by_type[resource_type]
                their_resource = their_resources_by_type[resource_type]
                
                # Check if temporal constraints allow time-sharing
                if (our_resource.temporal_constraints and their_resource.temporal_constraints and
                    "start_time" in our_resource.temporal_constraints and
                    "end_time" in our_resource.temporal_constraints and
                    "start_time" in their_resource.temporal_constraints and
                    "end_time" in their_resource.temporal_constraints):
                    
                    # Try to create time-sharing arrangement
                    our_start = datetime.fromisoformat(our_resource.temporal_constraints["start_time"])
                    our_end = datetime.fromisoformat(our_resource.temporal_constraints["end_time"])
                    their_start = datetime.fromisoformat(their_resource.temporal_constraints["start_time"])
                    their_end = datetime.fromisoformat(their_resource.temporal_constraints["end_time"])
                    
                    # If our time window is before theirs, we can time-share
                    if our_end <= their_start:
                        # Keep both resources with original quantities but adjusted time windows
                        our_adjusted = ResourceSpecification(
                            resource_type=our_resource.resource_type,
                            quantity=our_resource.quantity,
                            unit=our_resource.unit,
                            priority=our_resource.priority,
                            min_acceptable=our_resource.min_acceptable,
                            max_acceptable=our_resource.max_acceptable,
                            temporal_constraints=our_resource.temporal_constraints,
                            quality_requirements=our_resource.quality_requirements,
                            metadata={"time_sharing": "first_window"}
                        )
                        
                        their_adjusted = ResourceSpecification(
                            resource_type=their_resource.resource_type,
                            quantity=their_resource.quantity,
                            unit=their_resource.unit,
                            priority=their_resource.priority,
                            min_acceptable=their_resource.min_acceptable,
                            max_acceptable=their_resource.max_acceptable,
                            temporal_constraints=their_resource.temporal_constraints,
                            quality_requirements=their_resource.quality_requirements,
                            metadata={"time_sharing": "second_window"}
                        )
                        
                        collaborative_resources.append(our_adjusted)
                        collaborative_resources.append(their_adjusted)
                        continue
                    
                    # If their time window is before ours, we can time-share
                    elif their_end <= our_start:
                        # Keep both resources with original quantities but adjusted time windows
                        their_adjusted = ResourceSpecification(
                            resource_type=their_resource.resource_type,
                            quantity=their_resource.quantity,
                            unit=their_resource.unit,
                            priority=their_resource.priority,
                            min_acceptable=their_resource.min_acceptable,
                            max_acceptable=their_resource.max_acceptable,
                            temporal_constraints=their_resource.temporal_constraints,
                            quality_requirements=their_resource.quality_requirements,
                            metadata={"time_sharing": "first_window"}
                        )
                        
                        our_adjusted = ResourceSpecification(
                            resource_type=our_resource.resource_type,
                            quantity=our_resource.quantity,
                            unit=our_resource.unit,
                            priority=our_resource.priority,
                            min_acceptable=our_resource.min_acceptable,
                            max_acceptable=our_resource.max_acceptable,
                            temporal_constraints=our_resource.temporal_constraints,
                            quality_requirements=our_resource.quality_requirements,
                            metadata={"time_sharing": "second_window"}
                        )
                        
                        collaborative_resources.append(their_adjusted)
                        collaborative_resources.append(our_adjusted)
                        continue
                
                # If time-sharing isn't possible, try to find a creative solution
                # based on priorities
                if our_resource.priority > their_resource.priority:
                    # We need this resource more, so allocate more to us
                    allocation_ratio = our_resource.priority / (our_resource.priority + their_resource.priority)
                    our_quantity = our_resource.quantity * allocation_ratio
                    their_quantity = their_resource.quantity * (1 - allocation_ratio)
                else:
                    # They need this resource more, so allocate more to them
                    allocation_ratio = their_resource.priority / (our_resource.priority + their_resource.priority)
                    their_quantity = their_resource.quantity * allocation_ratio
                    our_quantity = our_resource.quantity * (1 - allocation_ratio)
                
                # Create collaborative resource
                collaborative_resource = ResourceSpecification(
                    resource_type=resource_type,
                    quantity=our_quantity,
                    unit=our_resource.unit,
                    priority=our_resource.priority,
                    min_acceptable=our_resource.min_acceptable,
                    max_acceptable=our_resource.max_acceptable,
                    temporal_constraints=our_resource.temporal_constraints,
                    quality_requirements=our_resource.quality_requirements,
                    metadata={"original_quantity": our_resource.quantity, "allocation_ratio": allocation_ratio}
                )
                
                collaborative_resources.append(collaborative_resource)
            
            # Add non-common resources with original quantities
            for resource_type, resource in our_resources_by_type.items():
                if resource_type not in common_types:
                    collaborative_resources.append(resource)
            
            rationale = "Collaborative proposal based on time-sharing and priority-based allocation"
            
            return create_negotiation_proposal(
                session_id=session.session_id,
                proposer_id=agent_id,
                resources=collaborative_resources,
                counter_to=latest_proposal.proposal_id,
                rationale=rationale,
                metadata={"strategy": self.name}
            )
        
        # If this is the first proposal, use our resources directly
        return create_negotiation_proposal(
            session_id=session.session_id,
            proposer_id=agent_id,
            resources=resources,
            rationale="Initial collaborative proposal",
            metadata={"strategy": self.name}
        )
    
    def evaluate_proposal(
        self,
        proposal: NegotiationProposal,
        agent_id: str,
        resources: List[ResourceSpecification],
        context: Dict[str, Any]
    ) -> Tuple[str, Optional[str], Optional[NegotiationProposal]]:
        """
        Evaluate a proposal using collaborative strategy.
        
        Args:
            proposal: Proposal to evaluate
            agent_id: ID of the evaluating agent
            resources: List of resource specifications
            context: Additional context
            
        Returns:
            Tuple[str, Optional[str], Optional[NegotiationProposal]]:
                - Response (accept, reject, counter)
                - Rationale (optional)
                - Counter proposal (optional)
        """
        # Look for time-sharing arrangements
        time_sharing_resources = [r for r in proposal.resources if r.metadata.get("time_sharing")]
        
        if time_sharing_resources:
            # Proposal includes time-sharing, which is favorable
            return "accept", "Accepting time-sharing arrangement", None
        
        # Map resources by type for easier comparison
        our_resources_by_type = {r.resource_type: r for r in resources}
        their_resources_by_type = {r.resource_type: r for r in proposal.resources}
        
        # Find common resource types
        common_types = set(our_resources_by_type.keys()) & set(their_resources_by_type.keys())
        
        # Calculate value score based on priorities
        value_score = 0
        max_possible_score = sum(our_resources_by_type[t].priority for t in common_types)
        
        for resource_type in common_types:
            our_resource = our_resources_by_type[resource_type]
            their_resource = their_resources_by_type[resource_type]
            
            # Calculate how much of our need is satisfied
            if their_resource.quantity >= our_resource.min_acceptable:
                value_score += our_resource.priority
            elif their_resource.quantity > 0:
                # Partial satisfaction
                satisfaction_ratio = their_resource.quantity / our_resource.min_acceptable
                value_score += our_resource.priority * satisfaction_ratio
        
        # If no common types or no value, reject
        if not common_types or max_possible_score == 0:
            return "reject", "No common resource types or no value", None
        
        # Calculate value percentage
        value_percentage = (value_score / max_possible_score) * 100
        
        # Accept if value is high
        if value_percentage >= 75:
            return "accept", f"Proposal provides good value ({value_percentage:.1f}%)", None
        
        # Counter if value is moderate
        elif value_percentage >= 30:
            # Create counter proposal
            session = context.get("session")
            if not session:
                return "reject", "Missing session context", None
            
            counter_proposal = self.generate_proposal(
                session=session,
                agent_id=agent_id,
                resources=resources,
                context=context
            )
            
            return "counter", f"Proposing collaborative solution ({value_percentage:.1f}% value)", counter_proposal
        
        # Reject if value is low
        else:
            return "reject", f"Proposal does not provide sufficient value ({value_percentage:.1f}%)", None

class CompetitiveStrategy(NegotiationStrategy):
    """Strategy focused on maximizing own value."""
    
    def __init__(self):
        """Initialize the competitive strategy."""
        super().__init__(
            name="competitive",
            description="Seeks to maximize own value through assertive negotiation"
        )
    
    def generate_proposal(
        self,
        session: NegotiationSession,
        agent_id: str,
        resources: List[ResourceSpecification],
        context: Dict[str, Any]
    ) -> NegotiationProposal:
        """
        Generate a competitive proposal.
        
        Args:
            session: Negotiation session
            agent_id: ID of the proposing agent
            resources: List of resource specifications
            context: Additional context
            
        Returns:
            NegotiationProposal: Generated proposal
        """
        # If this is a counter-proposal, adjust based on previous proposals
        latest_proposal = session.get_latest_proposal()
        
        if latest_proposal and latest_proposal.proposer_id != agent_id:
            # Create a competitive counter-proposal
            competitive_resources = []
            
            # Map resources by type for easier comparison
            our_resources_by_type = {r.resource_type: r for r in resources}
            their_resources_by_type = {r.resource_type: r for r in latest_proposal.resources}
            
            # Find common resource types
            common_types = set(our_resources_by_type.keys()) & set(their_resources_by_type.keys())
            
            # Calculate how many rounds of negotiation have occurred
            round_count = len(session.proposals)
            
            # Adjust concession rate based on round count
            # Start with small concessions, increase as rounds progress
            concession_rate = min(0.05 * round_count, 0.3)
            
            for resource_type in common_types:
                our_resource = our_resources_by_type[resource_type]
                their_resource = their_resources_by_type[resource_type]
                
                # Calculate new quantity with minimal concession
                original_quantity = our_resource.quantity
                concession_amount = (original_quantity - our_resource.min_acceptable) * concession_rate
                new_quantity = original_quantity - concession_amount
                
                # Ensure we don't go below our minimum
                new_quantity = max(new_quantity, our_resource.min_acceptable)
                
                # Create competitive resource
                competitive_resource = ResourceSpecification(
                    resource_type=resource_type,
                    quantity=new_quantity,
                    unit=our_resource.unit,
                    priority=our_resource.priority,
                    min_acceptable=our_resource.min_acceptable,
                    max_acceptable=our_resource.max_acceptable,
                    temporal_constraints=our_resource.temporal_constraints,
                    quality_requirements=our_resource.quality_requirements,
                    metadata={"original_quantity": original_quantity, "concession_rate": concession_rate}
                )
                
                competitive_resources.append(competitive_resource)
            
            # Add non-common resources with original quantities
            for resource_type, resource in our_resources_by_type.items():
                if resource_type not in common_types:
                    competitive_resources.append(resource)
            
            rationale = f"Competitive counter-proposal with {concession_rate:.1%} concession rate"
            
            return create_negotiation_proposal(
                session_id=session.session_id,
                proposer_id=agent_id,
                resources=competitive_resources,
                counter_to=latest_proposal.proposal_id,
                rationale=rationale,
                metadata={"strategy": self.name, "round": round_count}
            )
        
        # If this is the first proposal, use our resources with a slight increase
        competitive_resources = []
        
        for resource in resources:
            # Start with a slightly higher ask
            inflation_factor = 1.1  # 10% higher
            
            # Create competitive resource
            competitive_resource = ResourceSpecification(
                resource_type=resource.resource_type,
                quantity=resource.quantity * inflation_factor,
                unit=resource.unit,
                priority=resource.priority,
                min_acceptable=resource.min_acceptable,
                max_acceptable=resource.max_acceptable * inflation_factor,
                temporal_constraints=resource.temporal_constraints,
                quality_requirements=resource.quality_requirements,
                metadata={"original_quantity": resource.quantity, "inflation_factor": inflation_factor}
            )
            
            competitive_resources.append(competitive_resource)
        
        return create_negotiation_proposal(
            session_id=session.session_id,
            proposer_id=agent_id,
            resources=competitive_resources,
            rationale="Initial competitive proposal",
            metadata={"strategy": self.name, "round": 1}
        )
    
    def evaluate_proposal(
        self,
        proposal: NegotiationProposal,
        agent_id: str,
        resources: List[ResourceSpecification],
        context: Dict[str, Any]
    ) -> Tuple[str, Optional[str], Optional[NegotiationProposal]]:
        """
        Evaluate a proposal using competitive strategy.
        
        Args:
            proposal: Proposal to evaluate
            agent_id: ID of the evaluating agent
            resources: List of resource specifications
            context: Additional context
            
        Returns:
            Tuple[str, Optional[str], Optional[NegotiationProposal]]:
                - Response (accept, reject, counter)
                - Rationale (optional)
                - Counter proposal (optional)
        """
        # Map resources by type for easier comparison
        our_resources_by_type = {r.resource_type: r for r in resources}
        their_resources_by_type = {r.resource_type: r for r in proposal.resources}
        
        # Find common resource types
        common_types = set(our_resources_by_type.keys()) & set(their_resources_by_type.keys())
        
        # Calculate satisfaction score
        satisfaction_score = 0
        max_possible_score = sum(our_resources_by_type[t].priority for t in common_types)
        
        for resource_type in common_types:
            our_resource = our_resources_by_type[resource_type]
            their_resource = their_resources_by_type[resource_type]
            
            # Calculate how much of our need is satisfied
            if their_resource.quantity >= our_resource.quantity:
                # Full satisfaction
                satisfaction_score += our_resource.priority
            elif their_resource.quantity >= our_resource.min_acceptable:
                # Acceptable satisfaction
                satisfaction_ratio = (their_resource.quantity - our_resource.min_acceptable) / (our_resource.quantity - our_resource.min_acceptable)
                satisfaction_score += our_resource.priority * (0.7 + 0.3 * satisfaction_ratio)  # At least 70% satisfaction
            elif their_resource.quantity > 0:
                # Below minimum but not zero
                satisfaction_ratio = their_resource.quantity / our_resource.min_acceptable
                satisfaction_score += our_resource.priority * 0.5 * satisfaction_ratio  # At most 50% satisfaction
        
        # If no common types or no value, reject
        if not common_types or max_possible_score == 0:
            return "reject", "No common resource types or no value", None
        
        # Calculate satisfaction percentage
        satisfaction_percentage = (satisfaction_score / max_possible_score) * 100
        
        # Get session and round information
        session = context.get("session")
        if not session:
            return "reject", "Missing session context", None
        
        round_count = len(session.proposals)
        
        # Accept threshold increases with rounds
        accept_threshold = 85 - min(round_count * 5, 25)  # Starts at 85%, can go down to 60%
        
        # Counter threshold also increases with rounds
        counter_threshold = 40 - min(round_count * 5, 30)  # Starts at 40%, can go down to 10%
        
        # Accept if satisfaction is high enough
        if satisfaction_percentage >= accept_threshold:
            return "accept", f"Proposal is acceptable ({satisfaction_percentage:.1f}%)", None
        
        # Counter if satisfaction is moderate
        elif satisfaction_percentage >= counter_threshold:
            counter_proposal = self.generate_proposal(
                session=session,
                agent_id=agent_id,
                resources=resources,
                context=context
            )
            
            return "counter", f"Countering ({satisfaction_percentage:.1f}% satisfaction)", counter_proposal
        
        # Reject if satisfaction is low
        else:
            return "reject", f"Proposal is not acceptable ({satisfaction_percentage:.1f}%)", None

class StrategyFactory:
    """Factory for creating negotiation strategies."""
    
    @staticmethod
    def create_strategy(strategy_name: str) -> NegotiationStrategy:
        """
        Create a strategy by name.
        
        Args:
            strategy_name: Name of the strategy
            
        Returns:
            NegotiationStrategy: Created strategy
            
        Raises:
            ValueError: If strategy name is unknown
        """
        if strategy_name == "compromise":
            return CompromiseStrategy()
        elif strategy_name == "collaborative":
            return CollaborativeStrategy()
        elif strategy_name == "competitive":
            return CompetitiveStrategy()
        else:
            raise ValueError(f"Unknown strategy: {strategy_name}")

class TwinNegotiationAgent:
    """Agent for managing negotiations between digital twins."""
    
    def __init__(
        self,
        agent_id: str,
        mcp_bridge: MCPProtocolBridge,
        a2a_bridge: A2AProtocolBridge,
        event_bus: KafkaClient,
        data_access: DataAccessService,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the Twin Negotiation Agent.
        
        Args:
            agent_id: Unique identifier for the agent
            mcp_bridge: MCP protocol bridge
            a2a_bridge: A2A protocol bridge
            event_bus: Event bus client
            data_access: Data access service
            logger: Logger instance
        """
        self.agent_id = agent_id
        self.mcp_bridge = mcp_bridge
        self.a2a_bridge = a2a_bridge
        self.event_bus = event_bus
        self.data_access = data_access
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize strategy factory
        self.strategy_factory = StrategyFactory()
        
        # Initialize active sessions
        self.active_sessions: Dict[str, NegotiationSession] = {}
        
        # Initialize conflict registry
        self.conflicts: Dict[str, ResourceConflict] = {}
        
        # Subscribe to events
        self._subscribe_to_events()
    
    def _subscribe_to_events(self) -> None:
        """Subscribe to relevant events."""
        self.event_bus.subscribe(
            topic="diplomacy.negotiation.request",
            group_id=f"twin-negotiation-agent-{self.agent_id}",
            callback=self._handle_negotiation_request
        )
        
        self.event_bus.subscribe(
            topic="diplomacy.negotiation.proposal",
            group_id=f"twin-negotiation-agent-{self.agent_id}",
            callback=self._handle_negotiation_proposal
        )
        
        self.event_bus.subscribe(
            topic="diplomacy.negotiation.response",
            group_id=f"twin-negotiation-agent-{self.agent_id}",
            callback=self._handle_negotiation_response
        )
        
        self.event_bus.subscribe(
            topic="diplomacy.conflict.detected",
            group_id=f"twin-negotiation-agent-{self.agent_id}",
            callback=self._handle_conflict_detected
        )
        
        # Subscribe to A2A messages
        self.a2a_bridge.subscribe_to_message_type(
            message_type="negotiation_request",
            callback=self._handle_a2a_negotiation_request
        )
        
        self.a2a_bridge.subscribe_to_message_type(
            message_type="negotiation_proposal",
            callback=self._handle_a2a_negotiation_proposal
        )
        
        self.a2a_bridge.subscribe_to_message_type(
            message_type="negotiation_response",
            callback=self._handle_a2a_negotiation_response
        )
    
    def create_negotiation_session(
        self,
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
        session = create_negotiation_session(
            initiator_id=initiator_id,
            participants=participants,
            context=context,
            expires_in_hours=expires_in_hours,
            metadata=metadata
        )
        
        # Store session
        self.active_sessions[session.session_id] = session
        
        # Store in data access service
        self.data_access.create(
            collection="negotiation_sessions",
            document_id=session.session_id,
            data=session.to_dict()
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.negotiation.session_created",
            key=session.session_id,
            value={
                "session_id": session.session_id,
                "initiator_id": initiator_id,
                "participants": participants,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="negotiation_session",
            context_id=session.session_id,
            context_data={
                "session_id": session.session_id,
                "initiator_id": initiator_id,
                "participants": participants,
                "status": session.status,
                "created_at": session.created_at.isoformat(),
                "expires_at": session.expires_at.isoformat() if session.expires_at else None
            }
        )
        
        # Notify participants via A2A
        for participant_id in participants:
            if participant_id != initiator_id:
                self.a2a_bridge.send_message(
                    message_type="negotiation_invitation",
                    sender_id=self.agent_id,
                    recipient_id=participant_id,
                    content={
                        "session_id": session.session_id,
                        "initiator_id": initiator_id,
                        "context": context,
                        "expires_at": session.expires_at.isoformat() if session.expires_at else None
                    }
                )
        
        self.logger.info(f"Created negotiation session {session.session_id} with {len(participants)} participants")
        
        return session
    
    def submit_proposal(
        self,
        session_id: str,
        proposer_id: str,
        resources: List[ResourceSpecification],
        strategy_name: str = "compromise",
        counter_to: Optional[str] = None,
        rationale: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> NegotiationProposal:
        """
        Submit a proposal to a negotiation session.
        
        Args:
            session_id: ID of the negotiation session
            proposer_id: ID of the proposing agent
            resources: List of resource specifications
            strategy_name: Name of the strategy to use
            counter_to: ID of the proposal this counters
            rationale: Explanation for the proposal
            metadata: Additional metadata
            
        Returns:
            NegotiationProposal: Submitted proposal
            
        Raises:
            ValueError: If session not found or expired
        """
        # Get session
        session = self.active_sessions.get(session_id)
        if not session:
            # Try to load from data access service
            session_data = self.data_access.read(
                collection="negotiation_sessions",
                document_id=session_id
            )
            
            if not session_data:
                raise ValueError(f"Negotiation session {session_id} not found")
            
            session = NegotiationSession.from_dict(session_data)
            self.active_sessions[session_id] = session
        
        # Check if session is expired
        if session.is_expired():
            raise ValueError(f"Negotiation session {session_id} has expired")
        
        # Check if proposer is a participant
        if proposer_id not in session.participants and proposer_id != session.initiator_id:
            raise ValueError(f"Agent {proposer_id} is not a participant in session {session_id}")
        
        # Create strategy
        strategy = self.strategy_factory.create_strategy(strategy_name)
        
        # Generate proposal using strategy
        proposal = strategy.generate_proposal(
            session=session,
            agent_id=proposer_id,
            resources=resources,
            context={"counter_to": counter_to, "rationale": rationale, "metadata": metadata}
        )
        
        # Add proposal to session
        session.add_proposal(proposal)
        
        # Update session in data access service
        self.data_access.update(
            collection="negotiation_sessions",
            document_id=session_id,
            data=session.to_dict()
        )
        
        # Store proposal in data access service
        self.data_access.create(
            collection="negotiation_proposals",
            document_id=proposal.proposal_id,
            data=proposal.to_dict()
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.negotiation.proposal",
            key=proposal.proposal_id,
            value={
                "proposal_id": proposal.proposal_id,
                "session_id": session_id,
                "proposer_id": proposer_id,
                "counter_to": counter_to,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="negotiation_proposal",
            context_id=proposal.proposal_id,
            context_data={
                "proposal_id": proposal.proposal_id,
                "session_id": session_id,
                "proposer_id": proposer_id,
                "counter_to": counter_to,
                "status": proposal.status,
                "created_at": proposal.created_at.isoformat(),
                "expires_at": proposal.expires_at.isoformat() if proposal.expires_at else None
            }
        )
        
        # Notify participants via A2A
        for participant_id in session.participants:
            if participant_id != proposer_id:
                self.a2a_bridge.send_message(
                    message_type="negotiation_proposal",
                    sender_id=self.agent_id,
                    recipient_id=participant_id,
                    content={
                        "proposal_id": proposal.proposal_id,
                        "session_id": session_id,
                        "proposer_id": proposer_id,
                        "resources": [r.to_dict() for r in proposal.resources],
                        "counter_to": counter_to,
                        "rationale": proposal.rationale,
                        "strategy": strategy_name
                    }
                )
        
        self.logger.info(f"Submitted proposal {proposal.proposal_id} to session {session_id} using {strategy_name} strategy")
        
        return proposal
    
    def respond_to_proposal(
        self,
        proposal_id: str,
        responder_id: str,
        response: str,
        strategy_name: str = "compromise",
        rationale: Optional[str] = None,
        resources: Optional[List[ResourceSpecification]] = None
    ) -> Optional[NegotiationProposal]:
        """
        Respond to a proposal.
        
        Args:
            proposal_id: ID of the proposal
            responder_id: ID of the responding agent
            response: Response (accept, reject, counter)
            strategy_name: Name of the strategy to use
            rationale: Explanation for the response
            resources: List of resource specifications (for counter)
            
        Returns:
            Optional[NegotiationProposal]: Counter proposal if response is "counter", None otherwise
            
        Raises:
            ValueError: If proposal not found
        """
        # Get proposal
        proposal_data = self.data_access.read(
            collection="negotiation_proposals",
            document_id=proposal_id
        )
        
        if not proposal_data:
            raise ValueError(f"Proposal {proposal_id} not found")
        
        proposal = NegotiationProposal.from_dict(proposal_data)
        
        # Get session
        session_id = proposal.session_id
        session = self.active_sessions.get(session_id)
        
        if not session:
            # Try to load from data access service
            session_data = self.data_access.read(
                collection="negotiation_sessions",
                document_id=session_id
            )
            
            if not session_data:
                raise ValueError(f"Negotiation session {session_id} not found")
            
            session = NegotiationSession.from_dict(session_data)
            self.active_sessions[session_id] = session
        
        # Check if responder is a participant
        if responder_id not in session.participants and responder_id != session.initiator_id:
            raise ValueError(f"Agent {responder_id} is not a participant in session {session_id}")
        
        # Check if responder is the proposer
        if responder_id == proposal.proposer_id:
            raise ValueError(f"Agent {responder_id} cannot respond to their own proposal")
        
        # Add response to proposal
        proposal.add_response(responder_id, response, rationale)
        
        # Update proposal in data access service
        self.data_access.update(
            collection="negotiation_proposals",
            document_id=proposal_id,
            data=proposal.to_dict()
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.negotiation.response",
            key=proposal_id,
            value={
                "proposal_id": proposal_id,
                "session_id": session_id,
                "responder_id": responder_id,
                "response": response,
                "rationale": rationale,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="negotiation_response",
            context_id=f"{proposal_id}_{responder_id}",
            context_data={
                "proposal_id": proposal_id,
                "session_id": session_id,
                "responder_id": responder_id,
                "response": response,
                "rationale": rationale,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Notify proposer via A2A
        self.a2a_bridge.send_message(
            message_type="negotiation_response",
            sender_id=self.agent_id,
            recipient_id=proposal.proposer_id,
            content={
                "proposal_id": proposal_id,
                "session_id": session_id,
                "responder_id": responder_id,
                "response": response,
                "rationale": rationale
            }
        )
        
        self.logger.info(f"Agent {responder_id} responded '{response}' to proposal {proposal_id}")
        
        # If all participants have accepted, create agreement
        if response == "accept" and proposal.is_accepted_by_all(session.participants):
            self._create_agreement_from_proposal(proposal, session)
            return None
        
        # If response is counter, create counter proposal
        if response == "counter" and resources:
            counter_proposal = self.submit_proposal(
                session_id=session_id,
                proposer_id=responder_id,
                resources=resources,
                strategy_name=strategy_name,
                counter_to=proposal_id,
                rationale=rationale
            )
            return counter_proposal
        
        return None
    
    def _create_agreement_from_proposal(
        self,
        proposal: NegotiationProposal,
        session: NegotiationSession
    ) -> NegotiationAgreement:
        """
        Create an agreement from an accepted proposal.
        
        Args:
            proposal: Accepted proposal
            session: Negotiation session
            
        Returns:
            NegotiationAgreement: Created agreement
        """
        # Create agreement
        agreement = create_negotiation_agreement(
            session_id=session.session_id,
            proposal_id=proposal.proposal_id,
            participants=session.participants,
            resources=proposal.resources,
            terms={"derived_from_proposal": proposal.proposal_id},
            metadata=proposal.metadata
        )
        
        # Add agreement to session
        session.set_agreement(agreement)
        
        # Update session in data access service
        self.data_access.update(
            collection="negotiation_sessions",
            document_id=session.session_id,
            data=session.to_dict()
        )
        
        # Store agreement in data access service
        self.data_access.create(
            collection="negotiation_agreements",
            document_id=agreement.agreement_id,
            data=agreement.to_dict()
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.negotiation.agreement_created",
            key=agreement.agreement_id,
            value={
                "agreement_id": agreement.agreement_id,
                "session_id": session.session_id,
                "proposal_id": proposal.proposal_id,
                "participants": session.participants,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="negotiation_agreement",
            context_id=agreement.agreement_id,
            context_data={
                "agreement_id": agreement.agreement_id,
                "session_id": session.session_id,
                "proposal_id": proposal.proposal_id,
                "participants": session.participants,
                "status": agreement.status,
                "created_at": agreement.created_at.isoformat(),
                "valid_from": agreement.valid_from.isoformat(),
                "valid_until": agreement.valid_until.isoformat() if agreement.valid_until else None
            }
        )
        
        # Notify participants via A2A
        for participant_id in session.participants:
            self.a2a_bridge.send_message(
                message_type="negotiation_agreement",
                sender_id=self.agent_id,
                recipient_id=participant_id,
                content={
                    "agreement_id": agreement.agreement_id,
                    "session_id": session.session_id,
                    "proposal_id": proposal.proposal_id,
                    "resources": [r.to_dict() for r in agreement.resources],
                    "terms": agreement.terms,
                    "valid_from": agreement.valid_from.isoformat(),
                    "valid_until": agreement.valid_until.isoformat() if agreement.valid_until else None
                }
            )
        
        self.logger.info(f"Created agreement {agreement.agreement_id} from proposal {proposal.proposal_id}")
        
        # If there's a conflict associated with this session, resolve it
        conflict_id = session.context.get("conflict_id")
        if conflict_id and conflict_id in self.conflicts:
            self._resolve_conflict(
                conflict_id=conflict_id,
                agreement_id=agreement.agreement_id,
                strategy=ResolutionStrategy.COMPROMISE,
                description=f"Resolved through negotiation agreement {agreement.agreement_id}"
            )
        
        return agreement
    
    def detect_conflict(
        self,
        participants: List[str],
        conflict_type: ConflictType,
        resources: List[ResourceSpecification],
        severity: ConflictSeverity,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ResourceConflict:
        """
        Detect and register a resource conflict.
        
        Args:
            participants: List of participant IDs
            conflict_type: Type of conflict
            resources: List of contested resources
            severity: Conflict severity
            description: Conflict description
            metadata: Additional metadata
            
        Returns:
            ResourceConflict: Detected conflict
        """
        # Create conflict
        conflict = create_resource_conflict(
            participants=participants,
            conflict_type=conflict_type,
            resources=resources,
            severity=severity,
            description=description,
            metadata=metadata
        )
        
        # Store conflict
        self.conflicts[conflict.conflict_id] = conflict
        
        # Store in data access service
        self.data_access.create(
            collection="resource_conflicts",
            document_id=conflict.conflict_id,
            data=conflict.to_dict()
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.conflict.detected",
            key=conflict.conflict_id,
            value={
                "conflict_id": conflict.conflict_id,
                "participants": participants,
                "conflict_type": conflict_type,
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="resource_conflict",
            context_id=conflict.conflict_id,
            context_data={
                "conflict_id": conflict.conflict_id,
                "participants": participants,
                "conflict_type": conflict_type,
                "severity": severity,
                "description": description,
                "detected_at": conflict.detected_at.isoformat()
            }
        )
        
        # Notify participants via A2A
        for participant_id in participants:
            self.a2a_bridge.send_message(
                message_type="conflict_notification",
                sender_id=self.agent_id,
                recipient_id=participant_id,
                content={
                    "conflict_id": conflict.conflict_id,
                    "conflict_type": conflict_type,
                    "severity": severity,
                    "description": description,
                    "resources": [r.to_dict() for r in resources]
                }
            )
        
        self.logger.info(f"Detected {severity} {conflict_type} conflict {conflict.conflict_id} between {len(participants)} participants")
        
        # For high severity conflicts, automatically initiate negotiation
        if severity in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL]:
            self._initiate_conflict_negotiation(conflict)
        
        return conflict
    
    def _initiate_conflict_negotiation(self, conflict: ResourceConflict) -> NegotiationSession:
        """
        Initiate negotiation for a conflict.
        
        Args:
            conflict: Resource conflict
            
        Returns:
            NegotiationSession: Created negotiation session
        """
        # Create negotiation session
        session = self.create_negotiation_session(
            initiator_id=self.agent_id,
            participants=conflict.participants,
            context={
                "conflict_id": conflict.conflict_id,
                "conflict_type": conflict.conflict_type,
                "severity": conflict.severity,
                "description": conflict.description
            },
            metadata={"initiated_for_conflict": True}
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.conflict.negotiation_initiated",
            key=conflict.conflict_id,
            value={
                "conflict_id": conflict.conflict_id,
                "session_id": session.session_id,
                "participants": conflict.participants,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        self.logger.info(f"Initiated negotiation session {session.session_id} for conflict {conflict.conflict_id}")
        
        return session
    
    def _resolve_conflict(
        self,
        conflict_id: str,
        agreement_id: Optional[str],
        strategy: ResolutionStrategy,
        description: str
    ) -> ConflictResolution:
        """
        Resolve a conflict.
        
        Args:
            conflict_id: ID of the conflict
            agreement_id: ID of the associated agreement
            strategy: Resolution strategy
            description: Resolution description
            
        Returns:
            ConflictResolution: Created resolution
            
        Raises:
            ValueError: If conflict not found
        """
        # Get conflict
        conflict = self.conflicts.get(conflict_id)
        if not conflict:
            # Try to load from data access service
            conflict_data = self.data_access.read(
                collection="resource_conflicts",
                document_id=conflict_id
            )
            
            if not conflict_data:
                raise ValueError(f"Conflict {conflict_id} not found")
            
            conflict = ResourceConflict.from_dict(conflict_data)
            self.conflicts[conflict_id] = conflict
        
        # Create resolution
        resolution = create_conflict_resolution(
            conflict_id=conflict_id,
            strategy=strategy,
            description=description,
            agreement_id=agreement_id
        )
        
        # Mark as resolved
        resolution.mark_as_resolved(agreement_id)
        
        # Update conflict
        conflict.resolution = resolution
        
        # Update conflict in data access service
        self.data_access.update(
            collection="resource_conflicts",
            document_id=conflict_id,
            data=conflict.to_dict()
        )
        
        # Store resolution in data access service
        self.data_access.create(
            collection="conflict_resolutions",
            document_id=resolution.resolution_id,
            data=resolution.to_dict()
        )
        
        # Publish event
        self.event_bus.publish(
            topic="diplomacy.conflict.resolved",
            key=conflict_id,
            value={
                "conflict_id": conflict_id,
                "resolution_id": resolution.resolution_id,
                "agreement_id": agreement_id,
                "strategy": strategy,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Update MCP context
        self.mcp_bridge.update_context(
            context_type="conflict_resolution",
            context_id=resolution.resolution_id,
            context_data={
                "resolution_id": resolution.resolution_id,
                "conflict_id": conflict_id,
                "agreement_id": agreement_id,
                "strategy": strategy,
                "description": description,
                "resolved_at": resolution.resolved_at.isoformat(),
                "status": resolution.status
            }
        )
        
        # Notify participants via A2A
        for participant_id in conflict.participants:
            self.a2a_bridge.send_message(
                message_type="conflict_resolution",
                sender_id=self.agent_id,
                recipient_id=participant_id,
                content={
                    "conflict_id": conflict_id,
                    "resolution_id": resolution.resolution_id,
                    "agreement_id": agreement_id,
                    "strategy": strategy,
                    "description": description
                }
            )
        
        self.logger.info(f"Resolved conflict {conflict_id} with resolution {resolution.resolution_id}")
        
        return resolution
    
    def evaluate_proposal_with_strategy(
        self,
        proposal: NegotiationProposal,
        agent_id: str,
        resources: List[ResourceSpecification],
        strategy_name: str,
        context: Dict[str, Any]
    ) -> Tuple[str, Optional[str], Optional[NegotiationProposal]]:
        """
        Evaluate a proposal using a specific strategy.
        
        Args:
            proposal: Proposal to evaluate
            agent_id: ID of the evaluating agent
            resources: List of resource specifications
            strategy_name: Name of the strategy to use
            context: Additional context
            
        Returns:
            Tuple[str, Optional[str], Optional[NegotiationProposal]]:
                - Response (accept, reject, counter)
                - Rationale (optional)
                - Counter proposal (optional)
        """
        # Create strategy
        strategy = self.strategy_factory.create_strategy(strategy_name)
        
        # Evaluate proposal
        return strategy.evaluate_proposal(
            proposal=proposal,
            agent_id=agent_id,
            resources=resources,
            context=context
        )
    
    def _handle_negotiation_request(self, event: Dict[str, Any]) -> None:
        """
        Handle negotiation request event.
        
        Args:
            event: Event data
        """
        try:
            initiator_id = event.get("initiator_id")
            participants = event.get("participants", [])
            context = event.get("context", {})
            expires_in_hours = event.get("expires_in_hours")
            metadata = event.get("metadata")
            
            if not initiator_id or not participants:
                self.logger.error("Invalid negotiation request: missing initiator_id or participants")
                return
            
            self.create_negotiation_session(
                initiator_id=initiator_id,
                participants=participants,
                context=context,
                expires_in_hours=expires_in_hours,
                metadata=metadata
            )
        except Exception as e:
            self.logger.error(f"Error handling negotiation request: {str(e)}")
    
    def _handle_negotiation_proposal(self, event: Dict[str, Any]) -> None:
        """
        Handle negotiation proposal event.
        
        Args:
            event: Event data
        """
        try:
            session_id = event.get("session_id")
            proposer_id = event.get("proposer_id")
            resources_data = event.get("resources", [])
            strategy_name = event.get("strategy", "compromise")
            counter_to = event.get("counter_to")
            rationale = event.get("rationale")
            metadata = event.get("metadata")
            
            if not session_id or not proposer_id or not resources_data:
                self.logger.error("Invalid negotiation proposal: missing session_id, proposer_id, or resources")
                return
            
            # Convert resources data to ResourceSpecification objects
            resources = [ResourceSpecification.from_dict(r) for r in resources_data]
            
            self.submit_proposal(
                session_id=session_id,
                proposer_id=proposer_id,
                resources=resources,
                strategy_name=strategy_name,
                counter_to=counter_to,
                rationale=rationale,
                metadata=metadata
            )
        except Exception as e:
            self.logger.error(f"Error handling negotiation proposal: {str(e)}")
    
    def _handle_negotiation_response(self, event: Dict[str, Any]) -> None:
        """
        Handle negotiation response event.
        
        Args:
            event: Event data
        """
        try:
            proposal_id = event.get("proposal_id")
            responder_id = event.get("responder_id")
            response = event.get("response")
            strategy_name = event.get("strategy", "compromise")
            rationale = event.get("rationale")
            resources_data = event.get("resources", [])
            
            if not proposal_id or not responder_id or not response:
                self.logger.error("Invalid negotiation response: missing proposal_id, responder_id, or response")
                return
            
            # Convert resources data to ResourceSpecification objects if present
            resources = None
            if resources_data:
                resources = [ResourceSpecification.from_dict(r) for r in resources_data]
            
            self.respond_to_proposal(
                proposal_id=proposal_id,
                responder_id=responder_id,
                response=response,
                strategy_name=strategy_name,
                rationale=rationale,
                resources=resources
            )
        except Exception as e:
            self.logger.error(f"Error handling negotiation response: {str(e)}")
    
    def _handle_conflict_detected(self, event: Dict[str, Any]) -> None:
        """
        Handle conflict detected event.
        
        Args:
            event: Event data
        """
        try:
            participants = event.get("participants", [])
            conflict_type_str = event.get("conflict_type")
            resources_data = event.get("resources", [])
            severity_str = event.get("severity")
            description = event.get("description", "Resource conflict detected")
            metadata = event.get("metadata")
            
            if not participants or not conflict_type_str or not severity_str or not resources_data:
                self.logger.error("Invalid conflict detection: missing participants, conflict_type, severity, or resources")
                return
            
            # Convert string enums to enum values
            conflict_type = ConflictType(conflict_type_str)
            severity = ConflictSeverity(severity_str)
            
            # Convert resources data to ResourceSpecification objects
            resources = [ResourceSpecification.from_dict(r) for r in resources_data]
            
            self.detect_conflict(
                participants=participants,
                conflict_type=conflict_type,
                resources=resources,
                severity=severity,
                description=description,
                metadata=metadata
            )
        except Exception as e:
            self.logger.error(f"Error handling conflict detection: {str(e)}")
    
    def _handle_a2a_negotiation_request(self, message: Dict[str, Any]) -> None:
        """
        Handle A2A negotiation request message.
        
        Args:
            message: Message data
        """
        try:
            content = message.get("content", {})
            sender_id = message.get("sender_id")
            
            initiator_id = sender_id
            participants = content.get("participants", [])
            context = content.get("context", {})
            expires_in_hours = content.get("expires_in_hours")
            metadata = content.get("metadata")
            
            if not initiator_id or not participants:
                self.logger.error("Invalid A2A negotiation request: missing initiator_id or participants")
                return
            
            self.create_negotiation_session(
                initiator_id=initiator_id,
                participants=participants,
                context=context,
                expires_in_hours=expires_in_hours,
                metadata=metadata
            )
        except Exception as e:
            self.logger.error(f"Error handling A2A negotiation request: {str(e)}")
    
    def _handle_a2a_negotiation_proposal(self, message: Dict[str, Any]) -> None:
        """
        Handle A2A negotiation proposal message.
        
        Args:
            message: Message data
        """
        try:
            content = message.get("content", {})
            sender_id = message.get("sender_id")
            
            session_id = content.get("session_id")
            proposer_id = sender_id
            resources_data = content.get("resources", [])
            strategy_name = content.get("strategy", "compromise")
            counter_to = content.get("counter_to")
            rationale = content.get("rationale")
            metadata = content.get("metadata")
            
            if not session_id or not proposer_id or not resources_data:
                self.logger.error("Invalid A2A negotiation proposal: missing session_id, proposer_id, or resources")
                return
            
            # Convert resources data to ResourceSpecification objects
            resources = [ResourceSpecification.from_dict(r) for r in resources_data]
            
            self.submit_proposal(
                session_id=session_id,
                proposer_id=proposer_id,
                resources=resources,
                strategy_name=strategy_name,
                counter_to=counter_to,
                rationale=rationale,
                metadata=metadata
            )
        except Exception as e:
            self.logger.error(f"Error handling A2A negotiation proposal: {str(e)}")
    
    def _handle_a2a_negotiation_response(self, message: Dict[str, Any]) -> None:
        """
        Handle A2A negotiation response message.
        
        Args:
            message: Message data
        """
        try:
            content = message.get("content", {})
            sender_id = message.get("sender_id")
            
            proposal_id = content.get("proposal_id")
            responder_id = sender_id
            response = content.get("response")
            strategy_name = content.get("strategy", "compromise")
            rationale = content.get("rationale")
            resources_data = content.get("resources", [])
            
            if not proposal_id or not responder_id or not response:
                self.logger.error("Invalid A2A negotiation response: missing proposal_id, responder_id, or response")
                return
            
            # Convert resources data to ResourceSpecification objects if present
            resources = None
            if resources_data:
                resources = [ResourceSpecification.from_dict(r) for r in resources_data]
            
            self.respond_to_proposal(
                proposal_id=proposal_id,
                responder_id=responder_id,
                response=response,
                strategy_name=strategy_name,
                rationale=rationale,
                resources=resources
            )
        except Exception as e:
            self.logger.error(f"Error handling A2A negotiation response: {str(e)}")
