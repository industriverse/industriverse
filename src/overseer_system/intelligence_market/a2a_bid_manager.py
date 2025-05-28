"""
A2A Bid Manager for the Intelligence Market Phase of the Overseer System.

This module provides bid management capabilities for the intelligence market,
including bid creation, validation, matching, and execution using the A2A protocol.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable

from .market_models import (
    Bid, BidMatch, Transaction, BidStatus, BidType, MarketRole, ResourceType,
    AgentProfile, ResourceSpecification, PriceSpecification, TaskSpecification,
    AuctionConfig, create_bid, create_transaction_from_match
)
from .bid_validation import validate_bid_complete
from .auction_mechanisms import create_auction_mechanism, AuctionMechanism

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("intelligence_market.a2a_bid_manager")

class A2ABidManager:
    """
    Provides bid management capabilities for the intelligence market using the A2A protocol.
    """
    
    def __init__(
        self,
        config: Dict[str, Any] = None,
        mcp_integration_manager=None,
        a2a_integration_manager=None,
        event_bus=None,
        data_access_service=None
    ):
        """
        Initialize the A2A bid manager.
        
        Args:
            config: Configuration parameters
            mcp_integration_manager: MCP integration manager
            a2a_integration_manager: A2A integration manager
            event_bus: Event bus instance
            data_access_service: Data access service
        """
        self.config = config or {}
        self.mcp_integration_manager = mcp_integration_manager
        self.a2a_integration_manager = a2a_integration_manager
        self.event_bus = event_bus
        self.data_access_service = data_access_service
        
        # Initialize state
        self.bids: Dict[str, Bid] = {}
        self.matches: Dict[str, BidMatch] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.agent_profiles: Dict[str, AgentProfile] = {}
        self.auctions: Dict[str, AuctionMechanism] = {}
        self.market_policies: Dict[str, Any] = self.config.get("market_policies", {})
        
        # Initialize bid expiration checker
        self.bid_expiration_check_interval = self.config.get("bid_expiration_check_interval", 60)  # seconds
        self.last_expiration_check = datetime.now()
        
        logger.info("A2ABidManager initialized with %d market policies", len(self.market_policies))
        
        # Register with A2A integration manager if available
        if self.a2a_integration_manager:
            try:
                self.a2a_integration_manager.register_handler(
                    message_type="bid_submission",
                    handler=self.handle_bid_submission
                )
                self.a2a_integration_manager.register_handler(
                    message_type="bid_query",
                    handler=self.handle_bid_query
                )
                self.a2a_integration_manager.register_handler(
                    message_type="match_confirmation",
                    handler=self.handle_match_confirmation
                )
                logger.info("Registered handlers with A2A integration manager")
            except Exception as e:
                logger.error("Failed to register with A2A integration manager: %s", str(e))
    
    def create_bid(
        self,
        agent_id: str,
        bid_type: BidType,
        role: MarketRole,
        resources: List[ResourceSpecification],
        price: PriceSpecification,
        task: Optional[TaskSpecification] = None,
        conditions: Dict[str, Any] = None,
        dependencies: List[str] = None,
        expires_in_hours: Optional[int] = 24,
        metadata: Dict[str, Any] = None,
        signature: Optional[str] = None
    ) -> Tuple[bool, Optional[str], Optional[Bid]]:
        """
        Create a new bid in the intelligence market.
        
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
            signature: Cryptographic signature
            
        Returns:
            Tuple[bool, Optional[str], Optional[Bid]]: (success, error_message, created_bid)
        """
        # Create the bid
        bid = create_bid(
            agent_id=agent_id,
            bid_type=bid_type,
            role=role,
            resources=resources,
            price=price,
            task=task,
            conditions=conditions,
            dependencies=dependencies,
            expires_in_hours=expires_in_hours,
            metadata=metadata
        )
        
        # Add signature if provided
        if signature:
            bid.signature = signature
        
        # Get agent profile if available
        agent_profile = self.agent_profiles.get(agent_id)
        
        # Validate the bid
        is_valid, validation_errors = validate_bid_complete(
            bid=bid,
            agent_profile=agent_profile,
            market_policies=self.market_policies
        )
        
        if not is_valid:
            error_message = f"Bid validation failed: {', '.join(validation_errors)}"
            logger.warning("Bid validation failed for agent %s: %s", agent_id, error_message)
            return False, error_message, None
        
        # Store the bid
        self.bids[bid.bid_id] = bid
        
        # Publish bid to event bus if available
        if self.event_bus:
            try:
                self.event_bus.publish(
                    topic="intelligence_market.bids.created",
                    message=json.dumps(bid.dict())
                )
                logger.info("Published bid %s to event bus", bid.bid_id)
            except Exception as e:
                logger.error("Failed to publish bid to event bus: %s", str(e))
        
        # Integrate with MCP if available
        if self.mcp_integration_manager:
            try:
                context_update = {
                    "bid_created": {
                        "bid_id": bid.bid_id,
                        "agent_id": bid.agent_id,
                        "bid_type": bid.bid_type,
                        "role": bid.role,
                        "resources": [r.dict() for r in bid.resources],
                        "price": bid.price.dict()
                    }
                }
                self.mcp_integration_manager.update_context(context_update)
                logger.info("Updated MCP context with bid creation")
            except Exception as e:
                logger.error("Failed to update MCP context: %s", str(e))
        
        # Integrate with A2A if available
        if self.a2a_integration_manager:
            try:
                # Notify relevant agents about the new bid
                target_role = "buyer" if role == MarketRole.SELLER else "seller"
                self.a2a_integration_manager.notify_agents(
                    agent_types=[f"market_{target_role}", "market_maker"],
                    message={
                        "type": "new_bid_notification",
                        "bid_id": bid.bid_id,
                        "agent_id": bid.agent_id,
                        "bid_type": bid.bid_type,
                        "role": bid.role,
                        "resources": [r.resource_type for r in bid.resources],
                        "price_summary": {
                            "currency": bid.price.currency,
                            "amount": bid.price.amount
                        }
                    }
                )
                logger.info("Notified agents about new bid via A2A")
            except Exception as e:
                logger.error("Failed to notify agents via A2A: %s", str(e))
        
        # Store bid in database if data access service is available
        if self.data_access_service:
            try:
                self.data_access_service.create(
                    collection="bids",
                    document=bid.dict()
                )
                logger.info("Stored bid %s in database", bid.bid_id)
            except Exception as e:
                logger.error("Failed to store bid in database: %s", str(e))
        
        logger.info("Created bid %s for agent %s with role %s", bid.bid_id, agent_id, role)
        
        # Process the bid for potential matches
        self._process_bid(bid)
        
        return True, None, bid
    
    def _process_bid(self, bid: Bid) -> None:
        """
        Process a new bid for potential matches.
        
        Args:
            bid: The new bid to process
        """
        # Check if the bid is for an auction
        if bid.bid_type in [BidType.ENGLISH, BidType.DUTCH, BidType.VICKREY, BidType.CONTINUOUS]:
            # Find relevant auctions
            for auction_id, auction in self.auctions.items():
                if auction.config.auction_type == bid.bid_type:
                    # Check if auction is active
                    if auction.active:
                        # Add bid to auction
                        success, error = auction.add_bid(bid)
                        if success:
                            logger.info("Added bid %s to auction %s", bid.bid_id, auction_id)
                        else:
                            logger.warning("Failed to add bid %s to auction %s: %s", bid.bid_id, auction_id, error)
        
        # For fixed price bids, try to match directly
        elif bid.bid_type == BidType.FIXED:
            if bid.role == MarketRole.BUYER:
                # Look for matching seller bids
                self._match_with_sellers(bid)
            else:  # SELLER
                # Look for matching buyer bids
                self._match_with_buyers(bid)
    
    def _match_with_sellers(self, buyer_bid: Bid) -> None:
        """
        Try to match a buyer bid with seller bids.
        
        Args:
            buyer_bid: The buyer bid to match
        """
        # Find active seller bids
        seller_bids = [
            b for b in self.bids.values()
            if b.role == MarketRole.SELLER and b.status == BidStatus.ACTIVE
        ]
        
        # Sort by price (ascending)
        seller_bids.sort(key=lambda b: b.price.amount)
        
        for seller_bid in seller_bids:
            # Check if bids are compatible
            if self._are_bids_compatible(buyer_bid, seller_bid):
                # Create a match
                match = self._create_match(buyer_bid, seller_bid)
                
                # Update bid statuses
                buyer_bid.status = BidStatus.MATCHED
                seller_bid.status = BidStatus.MATCHED
                
                # Store the match
                self.matches[match.match_id] = match
                
                # Publish match to event bus if available
                if self.event_bus:
                    try:
                        self.event_bus.publish(
                            topic="intelligence_market.matches.created",
                            message=json.dumps(match.dict())
                        )
                        logger.info("Published match %s to event bus", match.match_id)
                    except Exception as e:
                        logger.error("Failed to publish match to event bus: %s", str(e))
                
                # Notify agents via A2A if available
                if self.a2a_integration_manager:
                    try:
                        # Notify buyer and seller
                        for agent_id in [buyer_bid.agent_id, seller_bid.agent_id]:
                            self.a2a_integration_manager.send_message(
                                agent_id=agent_id,
                                message={
                                    "type": "match_notification",
                                    "match_id": match.match_id,
                                    "buyer_bid_id": buyer_bid.bid_id,
                                    "seller_bid_id": seller_bid.bid_id,
                                    "price": match.match_price.dict(),
                                    "resources": [r.dict() for r in match.resources],
                                    "requires_confirmation": True
                                }
                            )
                        logger.info("Notified agents about match %s via A2A", match.match_id)
                    except Exception as e:
                        logger.error("Failed to notify agents via A2A: %s", str(e))
                
                # Store match in database if data access service is available
                if self.data_access_service:
                    try:
                        self.data_access_service.create(
                            collection="matches",
                            document=match.dict()
                        )
                        logger.info("Stored match %s in database", match.match_id)
                    except Exception as e:
                        logger.error("Failed to store match in database: %s", str(e))
                
                logger.info("Created match %s between buyer bid %s and seller bid %s",
                           match.match_id, buyer_bid.bid_id, seller_bid.bid_id)
                
                # Stop after first match
                break
    
    def _match_with_buyers(self, seller_bid: Bid) -> None:
        """
        Try to match a seller bid with buyer bids.
        
        Args:
            seller_bid: The seller bid to match
        """
        # Find active buyer bids
        buyer_bids = [
            b for b in self.bids.values()
            if b.role == MarketRole.BUYER and b.status == BidStatus.ACTIVE
        ]
        
        # Sort by price (descending)
        buyer_bids.sort(key=lambda b: b.price.amount, reverse=True)
        
        for buyer_bid in buyer_bids:
            # Check if bids are compatible
            if self._are_bids_compatible(buyer_bid, seller_bid):
                # Create a match
                match = self._create_match(buyer_bid, seller_bid)
                
                # Update bid statuses
                buyer_bid.status = BidStatus.MATCHED
                seller_bid.status = BidStatus.MATCHED
                
                # Store the match
                self.matches[match.match_id] = match
                
                # Publish match to event bus if available
                if self.event_bus:
                    try:
                        self.event_bus.publish(
                            topic="intelligence_market.matches.created",
                            message=json.dumps(match.dict())
                        )
                        logger.info("Published match %s to event bus", match.match_id)
                    except Exception as e:
                        logger.error("Failed to publish match to event bus: %s", str(e))
                
                # Notify agents via A2A if available
                if self.a2a_integration_manager:
                    try:
                        # Notify buyer and seller
                        for agent_id in [buyer_bid.agent_id, seller_bid.agent_id]:
                            self.a2a_integration_manager.send_message(
                                agent_id=agent_id,
                                message={
                                    "type": "match_notification",
                                    "match_id": match.match_id,
                                    "buyer_bid_id": buyer_bid.bid_id,
                                    "seller_bid_id": seller_bid.bid_id,
                                    "price": match.match_price.dict(),
                                    "resources": [r.dict() for r in match.resources],
                                    "requires_confirmation": True
                                }
                            )
                        logger.info("Notified agents about match %s via A2A", match.match_id)
                    except Exception as e:
                        logger.error("Failed to notify agents via A2A: %s", str(e))
                
                # Store match in database if data access service is available
                if self.data_access_service:
                    try:
                        self.data_access_service.create(
                            collection="matches",
                            document=match.dict()
                        )
                        logger.info("Stored match %s in database", match.match_id)
                    except Exception as e:
                        logger.error("Failed to store match in database: %s", str(e))
                
                logger.info("Created match %s between buyer bid %s and seller bid %s",
                           match.match_id, buyer_bid.bid_id, seller_bid.bid_id)
                
                # Stop after first match
                break
    
    def _are_bids_compatible(self, buyer_bid: Bid, seller_bid: Bid) -> bool:
        """
        Check if buyer and seller bids are compatible.
        
        Args:
            buyer_bid: The buyer's bid
            seller_bid: The seller's bid
            
        Returns:
            bool: True if compatible, False otherwise
        """
        # Check bid types
        if buyer_bid.bid_type != seller_bid.bid_type:
            return False
        
        # Check price
        if buyer_bid.price.amount < seller_bid.price.amount:
            return False
        
        # Check currency
        if buyer_bid.price.currency != seller_bid.price.currency:
            return False
        
        # Check resource types
        buyer_resource_types = {r.resource_type for r in buyer_bid.resources}
        seller_resource_types = {r.resource_type for r in seller_bid.resources}
        
        if not all(rt in seller_resource_types for rt in buyer_resource_types):
            return False
        
        # Check resource quantities
        for buyer_resource in buyer_bid.resources:
            matching_seller_resources = [
                r for r in seller_bid.resources 
                if r.resource_type == buyer_resource.resource_type
            ]
            
            if not matching_seller_resources:
                return False
            
            seller_resource = matching_seller_resources[0]
            if seller_resource.quantity < buyer_resource.quantity:
                return False
        
        # Check expiration
        now = datetime.now()
        if (buyer_bid.expires_at and buyer_bid.expires_at <= now) or (seller_bid.expires_at and seller_bid.expires_at <= now):
            return False
        
        # Check dependencies
        for dep_id in buyer_bid.dependencies:
            if dep_id not in self.bids or self.bids[dep_id].status != BidStatus.EXECUTED:
                return False
        
        for dep_id in seller_bid.dependencies:
            if dep_id not in self.bids or self.bids[dep_id].status != BidStatus.EXECUTED:
                return False
        
        return True
    
    def _create_match(self, buyer_bid: Bid, seller_bid: Bid) -> BidMatch:
        """
        Create a match between buyer and seller bids.
        
        Args:
            buyer_bid: The buyer's bid
            seller_bid: The seller's bid
            
        Returns:
            BidMatch: The created match
        """
        match_id = f"match-{uuid.uuid4()}"
        
        # Determine match price (midpoint)
        match_price = PriceSpecification(
            currency=buyer_bid.price.currency,
            amount=(buyer_bid.price.amount + seller_bid.price.amount) / 2,
            unit=buyer_bid.price.unit
        )
        
        # Use the resources from the seller's bid
        resources = seller_bid.resources
        
        # Create the match
        match = BidMatch(
            match_id=match_id,
            buyer_bid_id=buyer_bid.bid_id,
            seller_bid_id=seller_bid.bid_id,
            created_at=datetime.now(),
            status="pending",
            match_price=match_price,
            resources=resources,
            conditions={},
            execution_plan={
                "start_time": datetime.now().isoformat(),
                "estimated_completion": (datetime.now() + timedelta(hours=1)).isoformat()
            },
            signatures={}
        )
        
        return match
    
    def confirm_match(
        self,
        match_id: str,
        agent_id: str,
        signature: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Confirm a match by an agent.
        
        Args:
            match_id: Match ID to confirm
            agent_id: Agent ID confirming the match
            signature: Optional cryptographic signature
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        # Check if match exists
        if match_id not in self.matches:
            error_message = f"Match {match_id} not found"
            logger.warning(error_message)
            return False, error_message
        
        match = self.matches[match_id]
        
        # Get the buyer and seller bids
        buyer_bid = self.bids.get(match.buyer_bid_id)
        seller_bid = self.bids.get(match.seller_bid_id)
        
        if not buyer_bid or not seller_bid:
            error_message = f"Buyer or seller bid not found for match {match_id}"
            logger.warning(error_message)
            return False, error_message
        
        # Check if agent is involved in the match
        if agent_id != buyer_bid.agent_id and agent_id != seller_bid.agent_id:
            error_message = f"Agent {agent_id} is not involved in match {match_id}"
            logger.warning(error_message)
            return False, error_message
        
        # Add signature
        if signature:
            match.signatures[agent_id] = signature
        else:
            match.signatures[agent_id] = f"confirmed-{datetime.now().isoformat()}"
        
        logger.info("Agent %s confirmed match %s", agent_id, match_id)
        
        # Check if both parties have confirmed
        if buyer_bid.agent_id in match.signatures and seller_bid.agent_id in match.signatures:
            # Execute the match
            transaction = self._execute_match(match)
            
            if transaction:
                logger.info("Match %s executed, created transaction %s", match_id, transaction.transaction_id)
                return True, None
            else:
                error_message = f"Failed to execute match {match_id}"
                logger.warning(error_message)
                return False, error_message
        
        return True, None
    
    def _execute_match(self, match: BidMatch) -> Optional[Transaction]:
        """
        Execute a confirmed match to create a transaction.
        
        Args:
            match: The match to execute
            
        Returns:
            Optional[Transaction]: The created transaction, or None if execution failed
        """
        # Get the buyer and seller bids
        buyer_bid = self.bids.get(match.buyer_bid_id)
        seller_bid = self.bids.get(match.seller_bid_id)
        
        if not buyer_bid or not seller_bid:
            logger.error("Buyer or seller bid not found for match %s", match.match_id)
            return None
        
        # Create the transaction
        transaction = create_transaction_from_match(
            match=match,
            buyer_id=buyer_bid.agent_id,
            seller_id=seller_bid.agent_id,
            status="completed",
            performance_metrics={},
            feedback={}
        )
        
        # Update match status
        match.status = "executed"
        
        # Update bid statuses
        buyer_bid.status = BidStatus.EXECUTED
        seller_bid.status = BidStatus.EXECUTED
        
        # Store the transaction
        self.transactions[transaction.transaction_id] = transaction
        
        # Publish transaction to event bus if available
        if self.event_bus:
            try:
                self.event_bus.publish(
                    topic="intelligence_market.transactions.created",
                    message=json.dumps(transaction.dict())
                )
                logger.info("Published transaction %s to event bus", transaction.transaction_id)
            except Exception as e:
                logger.error("Failed to publish transaction to event bus: %s", str(e))
        
        # Integrate with MCP if available
        if self.mcp_integration_manager:
            try:
                context_update = {
                    "transaction_executed": {
                        "transaction_id": transaction.transaction_id,
                        "match_id": match.match_id,
                        "buyer_id": buyer_bid.agent_id,
                        "seller_id": seller_bid.agent_id,
                        "price": transaction.price.dict(),
                        "resources": [r.dict() for r in transaction.resources]
                    }
                }
                self.mcp_integration_manager.update_context(context_update)
                logger.info("Updated MCP context with transaction execution")
            except Exception as e:
                logger.error("Failed to update MCP context: %s", str(e))
        
        # Notify agents via A2A if available
        if self.a2a_integration_manager:
            try:
                # Notify buyer and seller
                for agent_id in [buyer_bid.agent_id, seller_bid.agent_id]:
                    self.a2a_integration_manager.send_message(
                        agent_id=agent_id,
                        message={
                            "type": "transaction_notification",
                            "transaction_id": transaction.transaction_id,
                            "match_id": match.match_id,
                            "price": transaction.price.dict(),
                            "resources": [r.dict() for r in transaction.resources],
                            "status": transaction.status
                        }
                    )
                logger.info("Notified agents about transaction %s via A2A", transaction.transaction_id)
            except Exception as e:
                logger.error("Failed to notify agents via A2A: %s", str(e))
        
        # Store transaction in database if data access service is available
        if self.data_access_service:
            try:
                self.data_access_service.create(
                    collection="transactions",
                    document=transaction.dict()
                )
                logger.info("Stored transaction %s in database", transaction.transaction_id)
            except Exception as e:
                logger.error("Failed to store transaction in database: %s", str(e))
        
        return transaction
    
    def cancel_bid(
        self,
        bid_id: str,
        agent_id: str,
        reason: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Cancel a bid.
        
        Args:
            bid_id: Bid ID to cancel
            agent_id: Agent ID cancelling the bid
            reason: Optional reason for cancellation
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        # Check if bid exists
        if bid_id not in self.bids:
            error_message = f"Bid {bid_id} not found"
            logger.warning(error_message)
            return False, error_message
        
        bid = self.bids[bid_id]
        
        # Check if agent owns the bid
        if bid.agent_id != agent_id:
            error_message = f"Agent {agent_id} does not own bid {bid_id}"
            logger.warning(error_message)
            return False, error_message
        
        # Check if bid can be cancelled
        if bid.status not in [BidStatus.PENDING, BidStatus.ACTIVE]:
            error_message = f"Bid {bid_id} cannot be cancelled in status {bid.status}"
            logger.warning(error_message)
            return False, error_message
        
        # Cancel the bid
        bid.status = BidStatus.CANCELLED
        bid.updated_at = datetime.now()
        
        # Add reason to metadata
        if reason:
            if not bid.metadata:
                bid.metadata = {}
            bid.metadata["cancellation_reason"] = reason
        
        # Publish cancellation to event bus if available
        if self.event_bus:
            try:
                self.event_bus.publish(
                    topic="intelligence_market.bids.cancelled",
                    message=json.dumps({
                        "bid_id": bid_id,
                        "agent_id": agent_id,
                        "reason": reason
                    })
                )
                logger.info("Published bid cancellation to event bus")
            except Exception as e:
                logger.error("Failed to publish bid cancellation to event bus: %s", str(e))
        
        # Update in database if data access service is available
        if self.data_access_service:
            try:
                self.data_access_service.update(
                    collection="bids",
                    document_id=bid_id,
                    update={
                        "status": BidStatus.CANCELLED,
                        "updated_at": bid.updated_at.isoformat(),
                        "metadata": bid.metadata
                    }
                )
                logger.info("Updated bid %s in database", bid_id)
            except Exception as e:
                logger.error("Failed to update bid in database: %s", str(e))
        
        logger.info("Cancelled bid %s by agent %s", bid_id, agent_id)
        return True, None
    
    def create_auction(
        self,
        auction_type: BidType,
        resource_types: List[ResourceType],
        start_time: datetime,
        end_time: Optional[datetime] = None,
        min_price: Optional[PriceSpecification] = None,
        max_price: Optional[PriceSpecification] = None,
        parameters: Dict[str, Any] = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create a new auction.
        
        Args:
            auction_type: Type of auction
            resource_types: Resource types being auctioned
            start_time: Auction start time
            end_time: Optional auction end time
            min_price: Optional minimum price
            max_price: Optional maximum price
            parameters: Optional additional parameters
            
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (success, error_message, auction_id)
        """
        # Generate auction ID
        auction_id = f"auction-{uuid.uuid4()}"
        
        # Create auction configuration
        config = AuctionConfig(
            auction_id=auction_id,
            auction_type=auction_type,
            resource_types=resource_types,
            start_time=start_time,
            end_time=end_time,
            min_price=min_price,
            max_price=max_price,
            increment_rules=parameters.get("increment_rules", {}) if parameters else {},
            participation_requirements=parameters.get("participation_requirements", {}) if parameters else {},
            visibility=parameters.get("visibility", "public") if parameters else "public",
            rules=parameters.get("rules", {}) if parameters else {}
        )
        
        # Create auction mechanism
        try:
            auction = create_auction_mechanism(config)
        except ValueError as e:
            error_message = f"Failed to create auction: {str(e)}"
            logger.error(error_message)
            return False, error_message, None
        
        # Store the auction
        self.auctions[auction_id] = auction
        
        # Publish auction to event bus if available
        if self.event_bus:
            try:
                self.event_bus.publish(
                    topic="intelligence_market.auctions.created",
                    message=json.dumps({
                        "auction_id": auction_id,
                        "auction_type": auction_type,
                        "resource_types": [rt.value for rt in resource_types],
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat() if end_time else None
                    })
                )
                logger.info("Published auction creation to event bus")
            except Exception as e:
                logger.error("Failed to publish auction creation to event bus: %s", str(e))
        
        # Integrate with A2A if available
        if self.a2a_integration_manager:
            try:
                self.a2a_integration_manager.broadcast_message(
                    message={
                        "type": "auction_announcement",
                        "auction_id": auction_id,
                        "auction_type": auction_type,
                        "resource_types": [rt.value for rt in resource_types],
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat() if end_time else None,
                        "min_price": min_price.dict() if min_price else None,
                        "max_price": max_price.dict() if max_price else None
                    }
                )
                logger.info("Broadcast auction announcement via A2A")
            except Exception as e:
                logger.error("Failed to broadcast auction announcement via A2A: %s", str(e))
        
        # Store in database if data access service is available
        if self.data_access_service:
            try:
                self.data_access_service.create(
                    collection="auctions",
                    document={
                        "auction_id": auction_id,
                        "auction_type": auction_type,
                        "resource_types": [rt.value for rt in resource_types],
                        "start_time": start_time.isoformat(),
                        "end_time": end_time.isoformat() if end_time else None,
                        "min_price": min_price.dict() if min_price else None,
                        "max_price": max_price.dict() if max_price else None,
                        "parameters": parameters or {}
                    }
                )
                logger.info("Stored auction %s in database", auction_id)
            except Exception as e:
                logger.error("Failed to store auction in database: %s", str(e))
        
        logger.info("Created auction %s of type %s", auction_id, auction_type)
        return True, None, auction_id
    
    def start_auction(self, auction_id: str) -> Tuple[bool, Optional[str]]:
        """
        Start an auction.
        
        Args:
            auction_id: Auction ID to start
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        # Check if auction exists
        if auction_id not in self.auctions:
            error_message = f"Auction {auction_id} not found"
            logger.warning(error_message)
            return False, error_message
        
        auction = self.auctions[auction_id]
        
        # Start the auction
        if not auction.start_auction():
            error_message = f"Failed to start auction {auction_id}"
            logger.warning(error_message)
            return False, error_message
        
        # Publish to event bus if available
        if self.event_bus:
            try:
                self.event_bus.publish(
                    topic="intelligence_market.auctions.started",
                    message=json.dumps({"auction_id": auction_id})
                )
                logger.info("Published auction start to event bus")
            except Exception as e:
                logger.error("Failed to publish auction start to event bus: %s", str(e))
        
        # Integrate with A2A if available
        if self.a2a_integration_manager:
            try:
                self.a2a_integration_manager.broadcast_message(
                    message={
                        "type": "auction_started",
                        "auction_id": auction_id,
                        "auction_type": auction.config.auction_type,
                        "resource_types": [rt.value for rt in auction.config.resource_types]
                    }
                )
                logger.info("Broadcast auction start via A2A")
            except Exception as e:
                logger.error("Failed to broadcast auction start via A2A: %s", str(e))
        
        # Update in database if data access service is available
        if self.data_access_service:
            try:
                self.data_access_service.update(
                    collection="auctions",
                    document_id=auction_id,
                    update={"status": "active", "started_at": datetime.now().isoformat()}
                )
                logger.info("Updated auction %s in database", auction_id)
            except Exception as e:
                logger.error("Failed to update auction in database: %s", str(e))
        
        logger.info("Started auction %s", auction_id)
        return True, None
    
    def end_auction(self, auction_id: str) -> Tuple[bool, Optional[str]]:
        """
        End an auction.
        
        Args:
            auction_id: Auction ID to end
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        # Check if auction exists
        if auction_id not in self.auctions:
            error_message = f"Auction {auction_id} not found"
            logger.warning(error_message)
            return False, error_message
        
        auction = self.auctions[auction_id]
        
        # End the auction
        if not auction.end_auction():
            error_message = f"Failed to end auction {auction_id}"
            logger.warning(error_message)
            return False, error_message
        
        # Publish to event bus if available
        if self.event_bus:
            try:
                self.event_bus.publish(
                    topic="intelligence_market.auctions.ended",
                    message=json.dumps({
                        "auction_id": auction_id,
                        "transactions": [t.dict() for t in auction.transactions]
                    })
                )
                logger.info("Published auction end to event bus")
            except Exception as e:
                logger.error("Failed to publish auction end to event bus: %s", str(e))
        
        # Integrate with A2A if available
        if self.a2a_integration_manager:
            try:
                self.a2a_integration_manager.broadcast_message(
                    message={
                        "type": "auction_ended",
                        "auction_id": auction_id,
                        "auction_type": auction.config.auction_type,
                        "transaction_count": len(auction.transactions)
                    }
                )
                logger.info("Broadcast auction end via A2A")
            except Exception as e:
                logger.error("Failed to broadcast auction end via A2A: %s", str(e))
        
        # Update in database if data access service is available
        if self.data_access_service:
            try:
                self.data_access_service.update(
                    collection="auctions",
                    document_id=auction_id,
                    update={
                        "status": "ended",
                        "ended_at": datetime.now().isoformat(),
                        "transaction_count": len(auction.transactions)
                    }
                )
                logger.info("Updated auction %s in database", auction_id)
            except Exception as e:
                logger.error("Failed to update auction in database: %s", str(e))
        
        logger.info("Ended auction %s", auction_id)
        return True, None
    
    def check_expired_bids(self) -> int:
        """
        Check for and handle expired bids.
        
        Returns:
            int: Number of expired bids handled
        """
        now = datetime.now()
        
        # Check if it's time to run the expiration check
        if (now - self.last_expiration_check).total_seconds() < self.bid_expiration_check_interval:
            return 0
        
        self.last_expiration_check = now
        
        # Find expired bids
        expired_bids = []
        for bid_id, bid in self.bids.items():
            if bid.status in [BidStatus.PENDING, BidStatus.ACTIVE] and bid.expires_at and bid.expires_at <= now:
                expired_bids.append(bid)
        
        # Handle expired bids
        for bid in expired_bids:
            bid.status = BidStatus.EXPIRED
            bid.updated_at = now
            
            # Publish expiration to event bus if available
            if self.event_bus:
                try:
                    self.event_bus.publish(
                        topic="intelligence_market.bids.expired",
                        message=json.dumps({"bid_id": bid.bid_id, "agent_id": bid.agent_id})
                    )
                except Exception as e:
                    logger.error("Failed to publish bid expiration to event bus: %s", str(e))
            
            # Notify agent via A2A if available
            if self.a2a_integration_manager:
                try:
                    self.a2a_integration_manager.send_message(
                        agent_id=bid.agent_id,
                        message={
                            "type": "bid_expired",
                            "bid_id": bid.bid_id,
                            "expired_at": now.isoformat()
                        }
                    )
                except Exception as e:
                    logger.error("Failed to notify agent via A2A: %s", str(e))
            
            # Update in database if data access service is available
            if self.data_access_service:
                try:
                    self.data_access_service.update(
                        collection="bids",
                        document_id=bid.bid_id,
                        update={"status": BidStatus.EXPIRED, "updated_at": now.isoformat()}
                    )
                except Exception as e:
                    logger.error("Failed to update bid in database: %s", str(e))
            
            logger.info("Expired bid %s from agent %s", bid.bid_id, bid.agent_id)
        
        if expired_bids:
            logger.info("Expired %d bids", len(expired_bids))
        
        return len(expired_bids)
    
    def get_market_status(self) -> Dict[str, Any]:
        """
        Get the current status of the intelligence market.
        
        Returns:
            Dict[str, Any]: Market status information
        """
        # Count bids by status
        bid_counts = {}
        for status in BidStatus:
            bid_counts[status] = len([b for b in self.bids.values() if b.status == status])
        
        # Count active auctions
        active_auctions = len([a for a in self.auctions.values() if a.active])
        
        # Prepare status information
        status = {
            "timestamp": datetime.now().isoformat(),
            "bid_counts": bid_counts,
            "match_count": len(self.matches),
            "transaction_count": len(self.transactions),
            "auction_count": len(self.auctions),
            "active_auction_count": active_auctions,
            "agent_count": len(self.agent_profiles)
        }
        
        return status
    
    def handle_bid_submission(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bid submission message from A2A protocol.
        
        Args:
            message: Bid submission message
            
        Returns:
            Dict[str, Any]: Response message
        """
        try:
            # Extract bid information
            agent_id = message.get("agent_id")
            bid_type = message.get("bid_type")
            role = message.get("role")
            resources = message.get("resources", [])
            price = message.get("price")
            task = message.get("task")
            conditions = message.get("conditions")
            dependencies = message.get("dependencies")
            expires_in_hours = message.get("expires_in_hours", 24)
            metadata = message.get("metadata")
            signature = message.get("signature")
            
            # Validate required fields
            if not all([agent_id, bid_type, role, resources, price]):
                return {
                    "success": False,
                    "error": "Missing required fields"
                }
            
            # Convert resources to ResourceSpecification objects
            resource_specs = []
            for r in resources:
                resource_specs.append(ResourceSpecification(
                    resource_type=r.get("resource_type"),
                    quantity=r.get("quantity"),
                    unit=r.get("unit"),
                    quality_metrics=r.get("quality_metrics", {}),
                    constraints=r.get("constraints", {}),
                    metadata=r.get("metadata", {})
                ))
            
            # Convert price to PriceSpecification object
            price_spec = PriceSpecification(
                currency=price.get("currency"),
                amount=price.get("amount"),
                unit=price.get("unit"),
                min_amount=price.get("min_amount"),
                max_amount=price.get("max_amount"),
                formula=price.get("formula"),
                parameters=price.get("parameters", {}),
                metadata=price.get("metadata", {})
            )
            
            # Convert task to TaskSpecification object if present
            task_spec = None
            if task:
                task_spec = TaskSpecification(
                    task_id=task.get("task_id"),
                    name=task.get("name"),
                    description=task.get("description"),
                    required_capabilities=task.get("required_capabilities", []),
                    input_schema=task.get("input_schema", {}),
                    output_schema=task.get("output_schema", {}),
                    constraints=task.get("constraints", {}),
                    performance_metrics=task.get("performance_metrics", {}),
                    deadline=datetime.fromisoformat(task.get("deadline")) if task.get("deadline") else None,
                    priority=task.get("priority", 0),
                    metadata=task.get("metadata", {})
                )
            
            # Create the bid
            success, error, bid = self.create_bid(
                agent_id=agent_id,
                bid_type=bid_type,
                role=role,
                resources=resource_specs,
                price=price_spec,
                task=task_spec,
                conditions=conditions,
                dependencies=dependencies,
                expires_in_hours=expires_in_hours,
                metadata=metadata,
                signature=signature
            )
            
            if success and bid:
                return {
                    "success": True,
                    "bid_id": bid.bid_id,
                    "status": bid.status
                }
            else:
                return {
                    "success": False,
                    "error": error
                }
        
        except Exception as e:
            logger.error("Error handling bid submission: %s", str(e))
            return {
                "success": False,
                "error": f"Internal error: {str(e)}"
            }
    
    def handle_bid_query(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bid query message from A2A protocol.
        
        Args:
            message: Bid query message
            
        Returns:
            Dict[str, Any]: Response message
        """
        try:
            # Extract query parameters
            query_type = message.get("query_type")
            bid_id = message.get("bid_id")
            agent_id = message.get("agent_id")
            bid_type = message.get("bid_type")
            role = message.get("role")
            resource_type = message.get("resource_type")
            status = message.get("status")
            
            # Query by bid ID
            if query_type == "by_id" and bid_id:
                bid = self.bids.get(bid_id)
                if bid:
                    return {
                        "success": True,
                        "bid": bid.dict()
                    }
                else:
                    return {
                        "success": False,
                        "error": f"Bid {bid_id} not found"
                    }
            
            # Query by filters
            elif query_type == "by_filter":
                filtered_bids = self.bids.values()
                
                if agent_id:
                    filtered_bids = [b for b in filtered_bids if b.agent_id == agent_id]
                
                if bid_type:
                    filtered_bids = [b for b in filtered_bids if b.bid_type == bid_type]
                
                if role:
                    filtered_bids = [b for b in filtered_bids if b.role == role]
                
                if resource_type:
                    filtered_bids = [b for b in filtered_bids if any(r.resource_type == resource_type for r in b.resources)]
                
                if status:
                    filtered_bids = [b for b in filtered_bids if b.status == status]
                
                return {
                    "success": True,
                    "bids": [b.dict() for b in filtered_bids]
                }
            
            else:
                return {
                    "success": False,
                    "error": f"Invalid query type: {query_type}"
                }
        
        except Exception as e:
            logger.error("Error handling bid query: %s", str(e))
            return {
                "success": False,
                "error": f"Internal error: {str(e)}"
            }
    
    def handle_match_confirmation(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle match confirmation message from A2A protocol.
        
        Args:
            message: Match confirmation message
            
        Returns:
            Dict[str, Any]: Response message
        """
        try:
            # Extract confirmation information
            match_id = message.get("match_id")
            agent_id = message.get("agent_id")
            signature = message.get("signature")
            
            # Validate required fields
            if not all([match_id, agent_id]):
                return {
                    "success": False,
                    "error": "Missing required fields"
                }
            
            # Confirm the match
            success, error = self.confirm_match(
                match_id=match_id,
                agent_id=agent_id,
                signature=signature
            )
            
            if success:
                return {
                    "success": True,
                    "match_id": match_id,
                    "status": self.matches[match_id].status if match_id in self.matches else "unknown"
                }
            else:
                return {
                    "success": False,
                    "error": error
                }
        
        except Exception as e:
            logger.error("Error handling match confirmation: %s", str(e))
            return {
                "success": False,
                "error": f"Internal error: {str(e)}"
            }
    
    def register_agent_profile(self, agent_profile: AgentProfile) -> bool:
        """
        Register an agent profile.
        
        Args:
            agent_profile: Agent profile to register
            
        Returns:
            bool: Success flag
        """
        try:
            self.agent_profiles[agent_profile.agent_id] = agent_profile
            
            # Store in database if data access service is available
            if self.data_access_service:
                try:
                    self.data_access_service.create_or_update(
                        collection="agent_profiles",
                        document_id=agent_profile.agent_id,
                        document=agent_profile.dict()
                    )
                    logger.info("Stored agent profile for %s in database", agent_profile.agent_id)
                except Exception as e:
                    logger.error("Failed to store agent profile in database: %s", str(e))
            
            logger.info("Registered agent profile for %s", agent_profile.agent_id)
            return True
        
        except Exception as e:
            logger.error("Error registering agent profile: %s", str(e))
            return False
