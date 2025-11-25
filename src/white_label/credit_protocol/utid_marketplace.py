"""
UTID Marketplace

Trading platform for validated research insights with UTIDs.

Features:
- List insights for sale or license
- Purchase/license transactions
- Auction mechanisms for high-value insights
- Access control for purchased insights
- Revenue distribution to creators and validators
- Citation-based royalties
- Insight bundles and collections

Business Models:
1. One-time purchase: Full ownership transfer
2. License: Time-limited or usage-based access
3. Subscription: Recurring access to insight collections
4. Citation royalty: Ongoing payments when insight is cited
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import secrets
from decimal import Decimal
import json
import os
import logging
import asyncio
from src.bridge_api.event_bus import GlobalEventBus

logger = logging.getLogger(__name__)


class ListingType(Enum):
    """Types of marketplace listings"""
    SALE = "sale"  # One-time purchase, ownership transfer
    LICENSE = "license"  # Time-limited access
    SUBSCRIPTION = "subscription"  # Recurring access
    AUCTION = "auction"  # Bidding mechanism
    CITATION_ROYALTY = "citation_royalty"  # Pay per citation


class ListingStatus(Enum):
    """Status of marketplace listing"""
    ACTIVE = "active"
    SOLD = "sold"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class LicenseType(Enum):
    """Types of licenses"""
    PERSONAL = "personal"  # Single user
    TEAM = "team"  # Up to 10 users
    ENTERPRISE = "enterprise"  # Unlimited users
    RESEARCH = "research"  # Academic use only
    COMMERCIAL = "commercial"  # Commercial use allowed


@dataclass
class MarketplaceListing:
    """Listing for an insight in the marketplace"""
    listing_id: str
    utid: str
    insight_id: str

    # Listing details
    listing_type: ListingType
    status: ListingStatus

    # Seller information
    seller_id: str
    seller_name: str

    # Pricing
    price: Decimal  # In credits
    currency: str = "CREDITS"

    # License details (if applicable)
    license_type: Optional[LicenseType] = None
    license_duration_days: Optional[int] = None
    max_users: Optional[int] = None

    # Auction details (if applicable)
    minimum_bid: Optional[Decimal] = None
    current_bid: Optional[Decimal] = None
    highest_bidder: Optional[str] = None
    auction_end_time: Optional[datetime] = None

    # Citation royalty (if applicable)
    royalty_per_citation: Optional[Decimal] = None

    # Metadata
    title: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    proof_score: float = 0.0
    citation_count: int = 0

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None

    # Sales tracking
    total_sales: int = 0
    total_revenue: Decimal = Decimal(0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'listing_id': self.listing_id,
            'utid': self.utid,
            'insight_id': self.insight_id,
            'listing_type': self.listing_type.value,
            'status': self.status.value,
            'seller_id': self.seller_id,
            'seller_name': self.seller_name,
            'price': float(self.price),
            'currency': self.currency,
            'license_type': self.license_type.value if self.license_type else None,
            'license_duration_days': self.license_duration_days,
            'max_users': self.max_users,
            'minimum_bid': float(self.minimum_bid) if self.minimum_bid else None,
            'current_bid': float(self.current_bid) if self.current_bid else None,
            'highest_bidder': self.highest_bidder,
            'auction_end_time': self.auction_end_time.isoformat() if self.auction_end_time else None,
            'royalty_per_citation': float(self.royalty_per_citation) if self.royalty_per_citation else None,
            'title': self.title,
            'description': self.description,
            'tags': self.tags,
            'proof_score': self.proof_score,
            'citation_count': self.citation_count,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'total_sales': self.total_sales,
            'total_revenue': float(self.total_revenue),
        }


@dataclass
class Transaction:
    """Marketplace transaction record"""
    transaction_id: str
    listing_id: str
    utid: str

    # Parties
    buyer_id: str
    seller_id: str

    # Transaction details
    transaction_type: str  # 'purchase', 'license', 'bid', 'royalty'
    amount: Decimal
    currency: str = "CREDITS"

    # Status
    status: str = "completed"  # 'pending', 'completed', 'failed', 'refunded'

    # License details (if applicable)
    license_type: Optional[LicenseType] = None
    license_expires: Optional[datetime] = None

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'transaction_id': self.transaction_id,
            'listing_id': self.listing_id,
            'utid': self.utid,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount),
            'currency': self.currency,
            'status': self.status,
            'license_type': self.license_type.value if self.license_type else None,
            'license_expires': self.license_expires.isoformat() if self.license_expires else None,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
        }


@dataclass
class InsightAccess:
    """Access control for purchased/licensed insights"""
    access_id: str
    utid: str
    insight_id: str
    user_id: str

    # Access type
    access_type: str  # 'owner', 'license', 'subscription'
    license_type: Optional[LicenseType] = None

    # Validity
    granted_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    is_active: bool = True

    # Usage tracking
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    # Source transaction
    transaction_id: str = ""

    def is_valid(self) -> bool:
        """Check if access is still valid"""
        if not self.is_active:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True


class UTIDMarketplace:
    """
    UTID Marketplace

    Trading platform for validated research insights:
    - List insights for sale/license
    - Purchase and license transactions
    - Auction mechanisms
    - Access control
    - Revenue distribution
    """

    def __init__(self):
        # Listings
        self.listings: Dict[str, MarketplaceListing] = {}
        self.listings_by_utid: Dict[str, List[str]] = {}  # UTID -> listing IDs
        self.listings_by_seller: Dict[str, List[str]] = {}  # seller_id -> listing IDs

        # Transactions
        self.transactions: List[Transaction] = []
        self.transactions_by_user: Dict[str, List[Transaction]] = {}

        # Access control
        self.access_grants: Dict[str, InsightAccess] = {}
        self.access_by_user: Dict[str, List[str]] = {}  # user_id -> access IDs
        self.access_by_utid: Dict[str, List[str]] = {}  # utid -> access IDs

        # Revenue tracking
        self.total_volume: Decimal = Decimal(0)
        
        # Persistence
        self.persistence_path = "data/marketplace_storage.json"
        self._load_from_disk()
        
        # Event Subscription
        GlobalEventBus.subscribe(self._on_event)

    async def _on_event(self, event: Dict[str, Any]):
        """Handle global events"""
        if event.get("type") == "proof_generated":
            await self._handle_proof_generated(event)

    async def _handle_proof_generated(self, event: Dict[str, Any]):
        """Auto-list high quality proofs"""
        try:
            proof = event.get("proof", {})
            metadata = proof.get("metadata", {})
            score = metadata.get("proof_score", 0.0)
            
            # Auto-list if score is high enough (> 0.9)
            if score > 0.9:
                utid = proof.get("utid")
                # Check if already listed
                if utid in self.listings_by_utid:
                    return

                logger.info(f"Auto-listing high quality proof: {utid} (Score: {score})")
                
                self.create_sale_listing(
                    utid=utid,
                    insight_id=proof.get("proof_id"),
                    seller_id="system_auto_lister",
                    seller_name="Industriverse System",
                    price=Decimal(100 * score), # Dynamic pricing
                    title=f"High Quality Insight: {proof.get('domain', 'General')}",
                    description=f"Auto-listed high fidelity proof. Score: {score:.4f}",
                    tags=["auto-listed", "premium", proof.get("domain", "general")],
                    proof_score=score
                )
        except Exception as e:
            logger.error(f"Error handling proof event: {e}")

    def _save_to_disk(self):
        """Save state to disk"""
        try:
            os.makedirs(os.path.dirname(self.persistence_path), exist_ok=True)
            
            data = {
                "listings": [l.to_dict() for l in self.listings.values()],
                "transactions": [t.to_dict() for t in self.transactions],
                "access_grants": {k: {
                    "access_id": v.access_id,
                    "utid": v.utid,
                    "insight_id": v.insight_id,
                    "user_id": v.user_id,
                    "access_type": v.access_type,
                    "is_active": v.is_active,
                    "access_count": v.access_count
                } for k, v in self.access_grants.items()}
            }
            
            with open(self.persistence_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save marketplace state: {e}")

    def _load_from_disk(self):
        """Load state from disk"""
        if not os.path.exists(self.persistence_path):
            return
            
        try:
            with open(self.persistence_path, 'r') as f:
                data = json.load(f)
                
            # Restore Listings
            for l_data in data.get("listings", []):
                listing = MarketplaceListing(
                    listing_id=l_data['listing_id'],
                    utid=l_data['utid'],
                    insight_id=l_data['insight_id'],
                    listing_type=ListingType(l_data['listing_type']),
                    status=ListingStatus(l_data['status']),
                    seller_id=l_data['seller_id'],
                    seller_name=l_data['seller_name'],
                    price=Decimal(str(l_data['price'])),
                    currency=l_data['currency'],
                    license_type=LicenseType(l_data['license_type']) if l_data.get('license_type') else None,
                    license_duration_days=l_data.get('license_duration_days'),
                    max_users=l_data.get('max_users'),
                    minimum_bid=Decimal(str(l_data['minimum_bid'])) if l_data.get('minimum_bid') else None,
                    current_bid=Decimal(str(l_data['current_bid'])) if l_data.get('current_bid') else None,
                    highest_bidder=l_data.get('highest_bidder'),
                    auction_end_time=datetime.fromisoformat(l_data['auction_end_time']) if l_data.get('auction_end_time') else None,
                    royalty_per_citation=Decimal(str(l_data['royalty_per_citation'])) if l_data.get('royalty_per_citation') else None,
                    title=l_data['title'],
                    description=l_data['description'],
                    tags=l_data['tags'],
                    proof_score=l_data['proof_score'],
                    citation_count=l_data['citation_count'],
                    created_at=datetime.fromisoformat(l_data['created_at']),
                    updated_at=datetime.fromisoformat(l_data['updated_at']),
                    expires_at=datetime.fromisoformat(l_data['expires_at']) if l_data.get('expires_at') else None,
                    total_sales=l_data['total_sales'],
                    total_revenue=Decimal(str(l_data['total_revenue']))
                )
                self._add_listing(listing)
                
            # Restore Transactions
            for t_data in data.get("transactions", []):
                transaction = Transaction(
                    transaction_id=t_data['transaction_id'],
                    listing_id=t_data['listing_id'],
                    utid=t_data['utid'],
                    buyer_id=t_data['buyer_id'],
                    seller_id=t_data['seller_id'],
                    transaction_type=t_data['transaction_type'],
                    amount=Decimal(str(t_data['amount'])),
                    currency=t_data['currency'],
                    status=t_data['status'],
                    license_type=LicenseType(t_data['license_type']) if t_data.get('license_type') else None,
                    license_expires=datetime.fromisoformat(t_data['license_expires']) if t_data.get('license_expires') else None,
                    metadata=t_data.get('metadata', {}),
                    timestamp=datetime.fromisoformat(t_data['timestamp'])
                )
                self.transactions.append(transaction)
                if transaction.buyer_id not in self.transactions_by_user:
                    self.transactions_by_user[transaction.buyer_id] = []
                self.transactions_by_user[transaction.buyer_id].append(transaction)
                self.total_volume += transaction.amount

            # Restore Access Grants
            for k, v in data.get("access_grants", {}).items():
                access = InsightAccess(
                    access_id=v['access_id'],
                    utid=v['utid'],
                    insight_id=v['insight_id'],
                    user_id=v['user_id'],
                    access_type=v['access_type'],
                    is_active=v['is_active'],
                    access_count=v['access_count']
                )
                self.access_grants[k] = access
                if access.user_id not in self.access_by_user:
                    self.access_by_user[access.user_id] = []
                self.access_by_user[access.user_id].append(access.access_id)
                
        except Exception as e:
            logger.error(f"Failed to load marketplace state: {e}")

    def create_sale_listing(
        self,
        utid: str,
        insight_id: str,
        seller_id: str,
        seller_name: str,
        price: Decimal,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        proof_score: float = 0.0,
        expires_in_days: Optional[int] = None
    ) -> MarketplaceListing:
        """Create a sale listing (ownership transfer)"""
        listing_id = f"sale-{utid}-{secrets.token_hex(4)}"

        expires_at = None
        if expires_in_days:
            expires_at = datetime.now() + timedelta(days=expires_in_days)

        listing = MarketplaceListing(
            listing_id=listing_id,
            utid=utid,
            insight_id=insight_id,
            listing_type=ListingType.SALE,
            status=ListingStatus.ACTIVE,
            seller_id=seller_id,
            seller_name=seller_name,
            price=price,
            title=title,
            description=description,
            tags=tags or [],
            proof_score=proof_score,
            expires_at=expires_at
        )

        self._add_listing(listing)
        self._save_to_disk()
        return listing

    def create_license_listing(
        self,
        utid: str,
        insight_id: str,
        seller_id: str,
        seller_name: str,
        price: Decimal,
        license_type: LicenseType,
        license_duration_days: int,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        proof_score: float = 0.0
    ) -> MarketplaceListing:
        """Create a license listing (time-limited access)"""
        listing_id = f"license-{utid}-{secrets.token_hex(4)}"

        # Max users based on license type
        max_users_map = {
            LicenseType.PERSONAL: 1,
            LicenseType.TEAM: 10,
            LicenseType.ENTERPRISE: None,  # Unlimited
            LicenseType.RESEARCH: 50,
            LicenseType.COMMERCIAL: None,
        }

        listing = MarketplaceListing(
            listing_id=listing_id,
            utid=utid,
            insight_id=insight_id,
            listing_type=ListingType.LICENSE,
            status=ListingStatus.ACTIVE,
            seller_id=seller_id,
            seller_name=seller_name,
            price=price,
            license_type=license_type,
            license_duration_days=license_duration_days,
            max_users=max_users_map[license_type],
            title=title,
            description=description,
            tags=tags or [],
            proof_score=proof_score
        )

        self._add_listing(listing)
        self._save_to_disk()
        return listing

    def create_auction_listing(
        self,
        utid: str,
        insight_id: str,
        seller_id: str,
        seller_name: str,
        minimum_bid: Decimal,
        auction_duration_hours: int,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        proof_score: float = 0.0
    ) -> MarketplaceListing:
        """Create an auction listing"""
        listing_id = f"auction-{utid}-{secrets.token_hex(4)}"

        listing = MarketplaceListing(
            listing_id=listing_id,
            utid=utid,
            insight_id=insight_id,
            listing_type=ListingType.AUCTION,
            status=ListingStatus.ACTIVE,
            seller_id=seller_id,
            seller_name=seller_name,
            price=minimum_bid,
            minimum_bid=minimum_bid,
            current_bid=minimum_bid,
            auction_end_time=datetime.now() + timedelta(hours=auction_duration_hours),
            title=title,
            description=description,
            tags=tags or [],
            proof_score=proof_score,
            expires_at=datetime.now() + timedelta(hours=auction_duration_hours)
        )

        self._add_listing(listing)
        self._save_to_disk()
        return listing

    def create_citation_royalty_listing(
        self,
        utid: str,
        insight_id: str,
        seller_id: str,
        seller_name: str,
        royalty_per_citation: Decimal,
        title: str,
        description: str,
        tags: Optional[List[str]] = None,
        proof_score: float = 0.0
    ) -> MarketplaceListing:
        """Create citation royalty listing (pay per use)"""
        listing_id = f"royalty-{utid}-{secrets.token_hex(4)}"

        listing = MarketplaceListing(
            listing_id=listing_id,
            utid=utid,
            insight_id=insight_id,
            listing_type=ListingType.CITATION_ROYALTY,
            status=ListingStatus.ACTIVE,
            seller_id=seller_id,
            seller_name=seller_name,
            price=Decimal(0),  # No upfront cost
            royalty_per_citation=royalty_per_citation,
            title=title,
            description=description,
            tags=tags or [],
            proof_score=proof_score
        )

        self._add_listing(listing)
        self._save_to_disk()
        return listing

    def _add_listing(self, listing: MarketplaceListing):
        """Add listing to marketplace"""
        self.listings[listing.listing_id] = listing

        # Update indexes
        if listing.utid not in self.listings_by_utid:
            self.listings_by_utid[listing.utid] = []
        self.listings_by_utid[listing.utid].append(listing.listing_id)

        if listing.seller_id not in self.listings_by_seller:
            self.listings_by_seller[listing.seller_id] = []
        self.listings_by_seller[listing.seller_id].append(listing.listing_id)

    def purchase_insight(
        self,
        listing_id: str,
        buyer_id: str,
        buyer_credits: Decimal
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """Purchase insight (ownership transfer)"""
        if listing_id not in self.listings:
            return False, "Listing not found", None

        listing = self.listings[listing_id]

        # Validate listing
        if listing.status != ListingStatus.ACTIVE:
            return False, f"Listing is {listing.status.value}", None

        if listing.listing_type != ListingType.SALE:
            return False, "Listing is not for sale", None

        # Check expiration
        if listing.expires_at and datetime.now() > listing.expires_at:
            listing.status = ListingStatus.EXPIRED
            return False, "Listing expired", None

        # Check buyer has enough credits
        if buyer_credits < listing.price:
            return False, f"Insufficient credits (need {listing.price}, have {buyer_credits})", None

        # Create transaction
        transaction = Transaction(
            transaction_id=f"tx-{secrets.token_hex(8)}",
            listing_id=listing_id,
            utid=listing.utid,
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            transaction_type="purchase",
            amount=listing.price,
            status="completed"
        )

        # Update listing
        listing.status = ListingStatus.SOLD
        listing.total_sales += 1
        listing.total_revenue += listing.price
        listing.updated_at = datetime.now()

        # Grant access to buyer
        self._grant_access(
            utid=listing.utid,
            insight_id=listing.insight_id,
            user_id=buyer_id,
            access_type="owner",
            transaction_id=transaction.transaction_id
        )

        # Record transaction
        self.transactions.append(transaction)
        if buyer_id not in self.transactions_by_user:
            self.transactions_by_user[buyer_id] = []
        self.transactions_by_user[buyer_id].append(transaction)

        # Update volume
        self.total_volume += listing.price
        
        self._save_to_disk()

        return True, "Purchase successful", transaction

    def license_insight(
        self,
        listing_id: str,
        buyer_id: str,
        buyer_credits: Decimal
    ) -> Tuple[bool, str, Optional[Transaction]]:
        """License insight (time-limited access)"""
        if listing_id not in self.listings:
            return False, "Listing not found", None

        listing = self.listings[listing_id]

        # Validate listing
        if listing.status != ListingStatus.ACTIVE:
            return False, f"Listing is {listing.status.value}", None

        if listing.listing_type != ListingType.LICENSE:
            return False, "Listing is not a license", None

        # Check buyer has enough credits
        if buyer_credits < listing.price:
            return False, f"Insufficient credits", None

        # Calculate license expiration
        license_expires = datetime.now() + timedelta(days=listing.license_duration_days)

        # Create transaction
        transaction = Transaction(
            transaction_id=f"tx-{secrets.token_hex(8)}",
            listing_id=listing_id,
            utid=listing.utid,
            buyer_id=buyer_id,
            seller_id=listing.seller_id,
            transaction_type="license",
            amount=listing.price,
            status="completed",
            license_type=listing.license_type,
            license_expires=license_expires
        )

        # Update listing stats
        listing.total_sales += 1
        listing.total_revenue += listing.price
        listing.updated_at = datetime.now()

        # Grant time-limited access
        self._grant_access(
            utid=listing.utid,
            insight_id=listing.insight_id,
            user_id=buyer_id,
            access_type="license",
            license_type=listing.license_type,
            expires_at=license_expires,
            transaction_id=transaction.transaction_id
        )

        # Record transaction
        self.transactions.append(transaction)
        if buyer_id not in self.transactions_by_user:
            self.transactions_by_user[buyer_id] = []
        self.transactions_by_user[buyer_id].append(transaction)

        # Update volume
        self.total_volume += listing.price
        
        self._save_to_disk()

        return True, "License acquired", transaction

    def place_bid(
        self,
        listing_id: str,
        bidder_id: str,
        bid_amount: Decimal
    ) -> Tuple[bool, str]:
        """Place bid in auction"""
        if listing_id not in self.listings:
            return False, "Listing not found"

        listing = self.listings[listing_id]

        # Validate listing
        if listing.listing_type != ListingType.AUCTION:
            return False, "Listing is not an auction"

        if listing.status != ListingStatus.ACTIVE:
            return False, f"Auction is {listing.status.value}"

        # Check auction hasn't ended
        if listing.auction_end_time and datetime.now() > listing.auction_end_time:
            listing.status = ListingStatus.EXPIRED
            return False, "Auction has ended"

        # Validate bid amount
        if bid_amount < listing.minimum_bid:
            return False, f"Bid below minimum ({listing.minimum_bid})"

        if listing.current_bid and bid_amount <= listing.current_bid:
            return False, f"Bid must be higher than current bid ({listing.current_bid})"

        # Update listing
        listing.current_bid = bid_amount
        listing.highest_bidder = bidder_id
        listing.updated_at = datetime.now()
        
        self._save_to_disk()

        return True, "Bid placed successfully"

    def finalize_auction(self, listing_id: str) -> Tuple[bool, str, Optional[Transaction]]:
        """Finalize auction and transfer to highest bidder"""
        if listing_id not in self.listings:
            return False, "Listing not found", None

        listing = self.listings[listing_id]

        if listing.listing_type != ListingType.AUCTION:
            return False, "Listing is not an auction", None

        if not listing.highest_bidder:
            listing.status = ListingStatus.EXPIRED
            return False, "No bids placed", None

        # Create transaction
        transaction = Transaction(
            transaction_id=f"tx-{secrets.token_hex(8)}",
            listing_id=listing_id,
            utid=listing.utid,
            buyer_id=listing.highest_bidder,
            seller_id=listing.seller_id,
            transaction_type="auction",
            amount=listing.current_bid,
            status="completed"
        )

        # Update listing
        listing.status = ListingStatus.SOLD
        listing.total_sales = 1
        listing.total_revenue = listing.current_bid
        listing.updated_at = datetime.now()

        # Grant access to winner
        self._grant_access(
            utid=listing.utid,
            insight_id=listing.insight_id,
            user_id=listing.highest_bidder,
            access_type="owner",
            transaction_id=transaction.transaction_id
        )

        # Record transaction
        self.transactions.append(transaction)
        self.total_volume += listing.current_bid
        
        self._save_to_disk()

        return True, "Auction finalized", transaction

    def _grant_access(
        self,
        utid: str,
        insight_id: str,
        user_id: str,
        access_type: str,
        transaction_id: str,
        license_type: Optional[LicenseType] = None,
        expires_at: Optional[datetime] = None
    ):
        """Grant access to insight"""
        access_id = f"access-{secrets.token_hex(8)}"

        access = InsightAccess(
            access_id=access_id,
            utid=utid,
            insight_id=insight_id,
            user_id=user_id,
            access_type=access_type,
            license_type=license_type,
            expires_at=expires_at,
            transaction_id=transaction_id
        )

        self.access_grants[access_id] = access

        # Update indexes
        if user_id not in self.access_by_user:
            self.access_by_user[user_id] = []
        self.access_by_user[user_id].append(access_id)

        if utid not in self.access_by_utid:
            self.access_by_utid[utid] = []
        self.access_by_utid[utid].append(access_id)

    def check_access(self, utid: str, user_id: str) -> bool:
        """Check if user has access to insight"""
        if user_id not in self.access_by_user:
            return False

        for access_id in self.access_by_user[user_id]:
            access = self.access_grants[access_id]
            if access.utid == utid and access.is_valid():
                # Update access tracking
                access.access_count += 1
                access.last_accessed = datetime.now()
                return True

        return False

    def get_user_insights(self, user_id: str) -> List[InsightAccess]:
        """Get all insights user has access to"""
        if user_id not in self.access_by_user:
            return []

        return [
            self.access_grants[access_id]
            for access_id in self.access_by_user[user_id]
            if self.access_grants[access_id].is_valid()
        ]

    def search_listings(
        self,
        tags: Optional[List[str]] = None,
        min_proof_score: float = 0.0,
        max_price: Optional[Decimal] = None,
        listing_type: Optional[ListingType] = None,
        status: ListingStatus = ListingStatus.ACTIVE
    ) -> List[MarketplaceListing]:
        """Search marketplace listings"""
        results = []

        for listing in self.listings.values():
            # Filter by status
            if listing.status != status:
                continue

            # Filter by listing type
            if listing_type and listing.listing_type != listing_type:
                continue

            # Filter by proof score
            if listing.proof_score < min_proof_score:
                continue

            # Filter by price
            if max_price and listing.price > max_price:
                continue

            # Filter by tags
            if tags:
                if not any(tag in listing.tags for tag in tags):
                    continue

            results.append(listing)

        # Sort by proof score (highest first)
        results.sort(key=lambda x: x.proof_score, reverse=True)

        return results

    def get_marketplace_stats(self) -> Dict[str, Any]:
        """Get marketplace statistics"""
        active_listings = sum(1 for l in self.listings.values() if l.status == ListingStatus.ACTIVE)
        sold_listings = sum(1 for l in self.listings.values() if l.status == ListingStatus.SOLD)

        total_transactions = len(self.transactions)
        completed_transactions = sum(1 for t in self.transactions if t.status == "completed")

        return {
            'total_listings': len(self.listings),
            'active_listings': active_listings,
            'sold_listings': sold_listings,
            'total_transactions': total_transactions,
            'completed_transactions': completed_transactions,
            'total_volume': float(self.total_volume),
            'total_access_grants': len(self.access_grants),
            'active_access_grants': sum(1 for a in self.access_grants.values() if a.is_valid()),
        }


# Global marketplace instance
_utid_marketplace: Optional[UTIDMarketplace] = None


def get_utid_marketplace() -> UTIDMarketplace:
    """Get or create global UTID marketplace"""
    global _utid_marketplace
    if _utid_marketplace is None:
        _utid_marketplace = UTIDMarketplace()
    return _utid_marketplace
