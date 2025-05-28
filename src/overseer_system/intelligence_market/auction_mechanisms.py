"""
Auction Mechanisms Module for the Intelligence Market Phase of the Overseer System.

This module provides various auction mechanisms for the intelligence market,
including fixed price, English, Dutch, Vickrey, and continuous double auctions.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable

from .market_models import (
    Bid, BidMatch, BidStatus, BidType, MarketRole, ResourceType,
    AgentProfile, ResourceSpecification, PriceSpecification, AuctionConfig,
    Transaction, create_transaction_from_match
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("intelligence_market.auction_mechanisms")

class AuctionMechanism:
    """Base class for auction mechanisms."""
    
    def __init__(self, config: AuctionConfig):
        """
        Initialize the auction mechanism.
        
        Args:
            config: Auction configuration
        """
        self.config = config
        self.bids: List[Bid] = []
        self.matches: List[BidMatch] = []
        self.transactions: List[Transaction] = []
        self.active = False
        logger.info("Auction mechanism initialized for auction %s", config.auction_id)
    
    def start_auction(self) -> bool:
        """
        Start the auction.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.active:
            logger.warning("Auction %s already active", self.config.auction_id)
            return False
        
        if self.config.start_time > datetime.now():
            logger.warning("Auction %s start time is in the future", self.config.auction_id)
            return False
        
        self.active = True
        logger.info("Auction %s started", self.config.auction_id)
        return True
    
    def end_auction(self) -> bool:
        """
        End the auction.
        
        Returns:
            bool: True if ended successfully, False otherwise
        """
        if not self.active:
            logger.warning("Auction %s not active", self.config.auction_id)
            return False
        
        self.active = False
        logger.info("Auction %s ended", self.config.auction_id)
        return True
    
    def add_bid(self, bid: Bid) -> Tuple[bool, Optional[str]]:
        """
        Add a bid to the auction.
        
        Args:
            bid: The bid to add
            
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        if not self.active:
            return False, "Auction not active"
        
        if self.config.end_time and datetime.now() > self.config.end_time:
            return False, "Auction has ended"
        
        # Check bid type compatibility
        if bid.bid_type != self.config.auction_type:
            return False, f"Bid type {bid.bid_type} does not match auction type {self.config.auction_type}"
        
        # Check resource type compatibility
        bid_resource_types = {r.resource_type for r in bid.resources}
        if not all(rt in self.config.resource_types for rt in bid_resource_types):
            return False, "Bid includes resource types not supported by this auction"
        
        # Check price constraints
        if self.config.min_price and bid.price.amount < self.config.min_price.amount:
            return False, f"Bid price {bid.price.amount} is below minimum {self.config.min_price.amount}"
        
        if self.config.max_price and bid.price.amount > self.config.max_price.amount:
            return False, f"Bid price {bid.price.amount} exceeds maximum {self.config.max_price.amount}"
        
        # Add the bid
        self.bids.append(bid)
        logger.info("Added bid %s to auction %s", bid.bid_id, self.config.auction_id)
        
        # Process the bid (to be implemented by subclasses)
        self._process_bid(bid)
        
        return True, None
    
    def _process_bid(self, bid: Bid) -> None:
        """
        Process a new bid (to be implemented by subclasses).
        
        Args:
            bid: The new bid to process
        """
        raise NotImplementedError("Subclasses must implement _process_bid")
    
    def _create_match(self, buyer_bid: Bid, seller_bid: Bid, match_price: PriceSpecification) -> BidMatch:
        """
        Create a match between buyer and seller bids.
        
        Args:
            buyer_bid: The buyer's bid
            seller_bid: The seller's bid
            match_price: The agreed price
            
        Returns:
            BidMatch: The created match
        """
        match_id = f"match-{uuid.uuid4()}"
        
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
        
        # Update bid statuses
        buyer_bid.status = BidStatus.MATCHED
        seller_bid.status = BidStatus.MATCHED
        
        # Add to matches list
        self.matches.append(match)
        
        logger.info("Created match %s between buyer bid %s and seller bid %s", 
                   match_id, buyer_bid.bid_id, seller_bid.bid_id)
        
        return match
    
    def execute_match(self, match: BidMatch) -> Optional[Transaction]:
        """
        Execute a match to create a transaction.
        
        Args:
            match: The match to execute
            
        Returns:
            Optional[Transaction]: The created transaction, or None if execution failed
        """
        # Find the buyer and seller bids
        buyer_bid = next((b for b in self.bids if b.bid_id == match.buyer_bid_id), None)
        seller_bid = next((b for b in self.bids if b.bid_id == match.seller_bid_id), None)
        
        if not buyer_bid or not seller_bid:
            logger.error("Could not find buyer or seller bid for match %s", match.match_id)
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
        
        # Add to transactions list
        self.transactions.append(transaction)
        
        logger.info("Executed match %s, created transaction %s", 
                   match.match_id, transaction.transaction_id)
        
        return transaction
    
    def get_auction_status(self) -> Dict[str, Any]:
        """
        Get the current status of the auction.
        
        Returns:
            Dict[str, Any]: Auction status information
        """
        return {
            "auction_id": self.config.auction_id,
            "auction_type": self.config.auction_type,
            "active": self.active,
            "start_time": self.config.start_time.isoformat(),
            "end_time": self.config.end_time.isoformat() if self.config.end_time else None,
            "bid_count": len(self.bids),
            "match_count": len(self.matches),
            "transaction_count": len(self.transactions),
            "current_time": datetime.now().isoformat()
        }

class FixedPriceAuction(AuctionMechanism):
    """Fixed price auction mechanism."""
    
    def _process_bid(self, bid: Bid) -> None:
        """
        Process a new bid in a fixed price auction.
        
        In a fixed price auction, we match compatible buyer and seller bids immediately.
        
        Args:
            bid: The new bid to process
        """
        if bid.role == MarketRole.BUYER:
            # Look for matching seller bids
            for seller_bid in self.bids:
                if (seller_bid.role == MarketRole.SELLER and 
                    seller_bid.status == BidStatus.ACTIVE and
                    self._are_bids_compatible(bid, seller_bid)):
                    
                    # Create a match
                    match = self._create_match(bid, seller_bid, seller_bid.price)
                    
                    # Execute the match
                    self.execute_match(match)
                    
                    # Stop after first match
                    break
        
        elif bid.role == MarketRole.SELLER:
            # Look for matching buyer bids
            for buyer_bid in self.bids:
                if (buyer_bid.role == MarketRole.BUYER and 
                    buyer_bid.status == BidStatus.ACTIVE and
                    self._are_bids_compatible(buyer_bid, bid)):
                    
                    # Create a match
                    match = self._create_match(buyer_bid, bid, bid.price)
                    
                    # Execute the match
                    self.execute_match(match)
                    
                    # Stop after first match
                    break
        
        # If no match was found, mark the bid as active
        if bid.status == BidStatus.PENDING:
            bid.status = BidStatus.ACTIVE
    
    def _are_bids_compatible(self, buyer_bid: Bid, seller_bid: Bid) -> bool:
        """
        Check if buyer and seller bids are compatible.
        
        Args:
            buyer_bid: The buyer's bid
            seller_bid: The seller's bid
            
        Returns:
            bool: True if compatible, False otherwise
        """
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
        
        # Check price
        if buyer_bid.price.amount < seller_bid.price.amount:
            return False
        
        # Check currency
        if buyer_bid.price.currency != seller_bid.price.currency:
            return False
        
        return True

class EnglishAuction(AuctionMechanism):
    """English (ascending price) auction mechanism."""
    
    def __init__(self, config: AuctionConfig):
        """
        Initialize the English auction.
        
        Args:
            config: Auction configuration
        """
        super().__init__(config)
        self.current_highest_bid: Optional[Bid] = None
        self.seller_bid: Optional[Bid] = None
        self.reserve_price = config.min_price
    
    def _process_bid(self, bid: Bid) -> None:
        """
        Process a new bid in an English auction.
        
        In an English auction, the first seller bid sets the item and reserve price,
        and subsequent buyer bids compete with ascending prices.
        
        Args:
            bid: The new bid to process
        """
        if bid.role == MarketRole.SELLER:
            # If this is the first seller bid, set it as the seller bid
            if not self.seller_bid:
                self.seller_bid = bid
                self.reserve_price = bid.price
                bid.status = BidStatus.ACTIVE
                logger.info("Set seller bid %s with reserve price %s %s", 
                           bid.bid_id, bid.price.amount, bid.price.currency)
            else:
                # Only one seller bid allowed
                bid.status = BidStatus.REJECTED
                logger.warning("Rejected seller bid %s, auction already has a seller", bid.bid_id)
        
        elif bid.role == MarketRole.BUYER:
            # Check if we have a seller bid
            if not self.seller_bid:
                bid.status = BidStatus.REJECTED
                logger.warning("Rejected buyer bid %s, no seller bid yet", bid.bid_id)
                return
            
            # Check if the bid is higher than the current highest bid
            if (not self.current_highest_bid or 
                bid.price.amount > self.current_highest_bid.price.amount):
                
                # Check if the bid meets the reserve price
                if bid.price.amount >= self.reserve_price.amount:
                    # Set as the new highest bid
                    if self.current_highest_bid:
                        self.current_highest_bid.status = BidStatus.ACTIVE
                    
                    self.current_highest_bid = bid
                    bid.status = BidStatus.ACTIVE
                    logger.info("New highest bid %s with price %s %s", 
                               bid.bid_id, bid.price.amount, bid.price.currency)
                else:
                    # Bid doesn't meet reserve price
                    bid.status = BidStatus.REJECTED
                    logger.warning("Rejected buyer bid %s, below reserve price", bid.bid_id)
            else:
                # Bid not high enough
                bid.status = BidStatus.REJECTED
                logger.warning("Rejected buyer bid %s, not higher than current highest", bid.bid_id)
    
    def end_auction(self) -> bool:
        """
        End the English auction and create a match if there's a winning bid.
        
        Returns:
            bool: True if ended successfully, False otherwise
        """
        if not super().end_auction():
            return False
        
        # Check if we have a seller bid and a highest bid
        if self.seller_bid and self.current_highest_bid:
            # Create a match
            match = self._create_match(
                self.current_highest_bid, 
                self.seller_bid, 
                self.current_highest_bid.price
            )
            
            # Execute the match
            self.execute_match(match)
            
            logger.info("English auction %s ended with winning bid %s", 
                       self.config.auction_id, self.current_highest_bid.bid_id)
        else:
            logger.info("English auction %s ended with no winner", self.config.auction_id)
        
        return True

class DutchAuction(AuctionMechanism):
    """Dutch (descending price) auction mechanism."""
    
    def __init__(self, config: AuctionConfig):
        """
        Initialize the Dutch auction.
        
        Args:
            config: Auction configuration
        """
        super().__init__(config)
        self.seller_bid: Optional[Bid] = None
        self.current_price: Optional[PriceSpecification] = None
        self.winner_bid: Optional[Bid] = None
        self.price_decrement = config.parameters.get("price_decrement", 1.0)
        self.price_update_interval = config.parameters.get("price_update_interval", 60)  # seconds
        self.last_price_update = datetime.now()
    
    def _process_bid(self, bid: Bid) -> None:
        """
        Process a new bid in a Dutch auction.
        
        In a Dutch auction, the first seller bid sets the item and starting price,
        which decreases over time until a buyer accepts it.
        
        Args:
            bid: The new bid to process
        """
        if bid.role == MarketRole.SELLER:
            # If this is the first seller bid, set it as the seller bid
            if not self.seller_bid:
                self.seller_bid = bid
                self.current_price = bid.price
                bid.status = BidStatus.ACTIVE
                logger.info("Set seller bid %s with starting price %s %s", 
                           bid.bid_id, bid.price.amount, bid.price.currency)
            else:
                # Only one seller bid allowed
                bid.status = BidStatus.REJECTED
                logger.warning("Rejected seller bid %s, auction already has a seller", bid.bid_id)
        
        elif bid.role == MarketRole.BUYER:
            # Check if we have a seller bid and no winner yet
            if not self.seller_bid or self.winner_bid:
                bid.status = BidStatus.REJECTED
                logger.warning("Rejected buyer bid %s, no seller bid or auction already has a winner", bid.bid_id)
                return
            
            # In a Dutch auction, a buyer bid is an acceptance of the current price
            bid.status = BidStatus.ACTIVE
            self.winner_bid = bid
            
            # Create a match
            match = self._create_match(
                bid, 
                self.seller_bid, 
                self.current_price
            )
            
            # Execute the match
            self.execute_match(match)
            
            logger.info("Dutch auction %s ended with winning bid %s at price %s %s", 
                       self.config.auction_id, bid.bid_id, 
                       self.current_price.amount, self.current_price.currency)
            
            # End the auction
            self.end_auction()
    
    def update_price(self) -> None:
        """Update the current price in the Dutch auction."""
        if not self.active or not self.seller_bid or self.winner_bid:
            return
        
        now = datetime.now()
        if (now - self.last_price_update).total_seconds() < self.price_update_interval:
            return
        
        # Decrease the price
        self.current_price.amount -= self.price_decrement
        self.last_price_update = now
        
        # Check if we've reached the minimum price
        if self.config.min_price and self.current_price.amount < self.config.min_price.amount:
            self.current_price.amount = self.config.min_price.amount
            logger.info("Dutch auction %s reached minimum price %s %s", 
                       self.config.auction_id, self.current_price.amount, self.current_price.currency)
            
            # End the auction if we've reached the minimum price
            if self.config.parameters.get("end_at_min_price", False):
                logger.info("Dutch auction %s ending due to reaching minimum price", self.config.auction_id)
                self.end_auction()
        else:
            logger.info("Dutch auction %s price updated to %s %s", 
                       self.config.auction_id, self.current_price.amount, self.current_price.currency)

class VickreyAuction(AuctionMechanism):
    """Vickrey (second-price sealed bid) auction mechanism."""
    
    def __init__(self, config: AuctionConfig):
        """
        Initialize the Vickrey auction.
        
        Args:
            config: Auction configuration
        """
        super().__init__(config)
        self.seller_bid: Optional[Bid] = None
        self.buyer_bids: List[Bid] = []
    
    def _process_bid(self, bid: Bid) -> None:
        """
        Process a new bid in a Vickrey auction.
        
        In a Vickrey auction, the first seller bid sets the item,
        and buyer bids are sealed until the auction ends.
        The highest bidder wins but pays the second-highest price.
        
        Args:
            bid: The new bid to process
        """
        if bid.role == MarketRole.SELLER:
            # If this is the first seller bid, set it as the seller bid
            if not self.seller_bid:
                self.seller_bid = bid
                bid.status = BidStatus.ACTIVE
                logger.info("Set seller bid %s", bid.bid_id)
            else:
                # Only one seller bid allowed
                bid.status = BidStatus.REJECTED
                logger.warning("Rejected seller bid %s, auction already has a seller", bid.bid_id)
        
        elif bid.role == MarketRole.BUYER:
            # Check if we have a seller bid
            if not self.seller_bid:
                bid.status = BidStatus.REJECTED
                logger.warning("Rejected buyer bid %s, no seller bid yet", bid.bid_id)
                return
            
            # Add to buyer bids
            self.buyer_bids.append(bid)
            bid.status = BidStatus.ACTIVE
            logger.info("Added buyer bid %s to Vickrey auction", bid.bid_id)
    
    def end_auction(self) -> bool:
        """
        End the Vickrey auction and determine the winner.
        
        Returns:
            bool: True if ended successfully, False otherwise
        """
        if not super().end_auction():
            return False
        
        # Check if we have a seller bid and at least one buyer bid
        if not self.seller_bid or not self.buyer_bids:
            logger.info("Vickrey auction %s ended with no winner", self.config.auction_id)
            return True
        
        # Sort buyer bids by price (descending)
        sorted_bids = sorted(self.buyer_bids, key=lambda b: b.price.amount, reverse=True)
        
        # Check if we have at least one bid
        if not sorted_bids:
            logger.info("Vickrey auction %s ended with no buyer bids", self.config.auction_id)
            return True
        
        # The highest bidder wins
        winner_bid = sorted_bids[0]
        
        # Determine the second-highest price
        second_price = self.seller_bid.price  # Default to reserve price
        if len(sorted_bids) > 1:
            second_price = sorted_bids[1].price
        
        # Create a match with the second-highest price
        match = self._create_match(
            winner_bid, 
            self.seller_bid, 
            second_price
        )
        
        # Execute the match
        self.execute_match(match)
        
        logger.info("Vickrey auction %s ended with winning bid %s at second price %s %s", 
                   self.config.auction_id, winner_bid.bid_id, 
                   second_price.amount, second_price.currency)
        
        return True

class ContinuousDoubleAuction(AuctionMechanism):
    """Continuous double auction mechanism."""
    
    def __init__(self, config: AuctionConfig):
        """
        Initialize the continuous double auction.
        
        Args:
            config: Auction configuration
        """
        super().__init__(config)
        self.buyer_bids: List[Bid] = []
        self.seller_bids: List[Bid] = []
        self.order_book: Dict[ResourceType, Dict[str, List[Bid]]] = {}
        
        # Initialize order book for each resource type
        for resource_type in config.resource_types:
            self.order_book[resource_type] = {
                "buy": [],  # Buy orders (bids)
                "sell": []  # Sell orders (asks)
            }
    
    def _process_bid(self, bid: Bid) -> None:
        """
        Process a new bid in a continuous double auction.
        
        In a continuous double auction, buy and sell orders are continuously matched.
        
        Args:
            bid: The new bid to process
        """
        # Add to appropriate list
        if bid.role == MarketRole.BUYER:
            self.buyer_bids.append(bid)
        elif bid.role == MarketRole.SELLER:
            self.seller_bids.append(bid)
        
        # Add to order book for each resource type
        for resource in bid.resources:
            resource_type = resource.resource_type
            if resource_type in self.order_book:
                order_type = "buy" if bid.role == MarketRole.BUYER else "sell"
                self.order_book[resource_type][order_type].append(bid)
        
        # Set bid status to active
        bid.status = BidStatus.ACTIVE
        
        # Try to match orders
        self._match_orders()
    
    def _match_orders(self) -> None:
        """Match buy and sell orders in the order book."""
        for resource_type, orders in self.order_book.items():
            # Sort buy orders by price (descending)
            buy_orders = sorted(
                [b for b in orders["buy"] if b.status == BidStatus.ACTIVE],
                key=lambda b: b.price.amount,
                reverse=True
            )
            
            # Sort sell orders by price (ascending)
            sell_orders = sorted(
                [b for b in orders["sell"] if b.status == BidStatus.ACTIVE],
                key=lambda b: b.price.amount
            )
            
            # Match orders
            for buy_order in buy_orders:
                if buy_order.status != BidStatus.ACTIVE:
                    continue
                
                for sell_order in sell_orders:
                    if sell_order.status != BidStatus.ACTIVE:
                        continue
                    
                    # Check if orders can be matched
                    if self._can_match_orders(buy_order, sell_order, resource_type):
                        # Determine match price (midpoint)
                        match_price = PriceSpecification(
                            currency=buy_order.price.currency,
                            amount=(buy_order.price.amount + sell_order.price.amount) / 2,
                            unit=buy_order.price.unit
                        )
                        
                        # Create a match
                        match = self._create_match(buy_order, sell_order, match_price)
                        
                        # Execute the match
                        self.execute_match(match)
                        
                        # Break inner loop, move to next buy order
                        break
    
    def _can_match_orders(self, buy_order: Bid, sell_order: Bid, resource_type: ResourceType) -> bool:
        """
        Check if buy and sell orders can be matched.
        
        Args:
            buy_order: The buy order
            sell_order: The sell order
            resource_type: The resource type to match
            
        Returns:
            bool: True if orders can be matched, False otherwise
        """
        # Check price
        if buy_order.price.amount < sell_order.price.amount:
            return False
        
        # Check currency
        if buy_order.price.currency != sell_order.price.currency:
            return False
        
        # Check resource quantities
        buy_resource = next((r for r in buy_order.resources if r.resource_type == resource_type), None)
        sell_resource = next((r for r in sell_order.resources if r.resource_type == resource_type), None)
        
        if not buy_resource or not sell_resource:
            return False
        
        if sell_resource.quantity < buy_resource.quantity:
            return False
        
        return True

def create_auction_mechanism(config: AuctionConfig) -> AuctionMechanism:
    """
    Create an auction mechanism based on the auction type.
    
    Args:
        config: Auction configuration
        
    Returns:
        AuctionMechanism: The created auction mechanism
    """
    auction_type = config.auction_type
    
    if auction_type == BidType.FIXED:
        return FixedPriceAuction(config)
    elif auction_type == BidType.ENGLISH:
        return EnglishAuction(config)
    elif auction_type == BidType.DUTCH:
        return DutchAuction(config)
    elif auction_type == BidType.VICKREY:
        return VickreyAuction(config)
    elif auction_type == BidType.CONTINUOUS:
        return ContinuousDoubleAuction(config)
    else:
        raise ValueError(f"Unsupported auction type: {auction_type}")
