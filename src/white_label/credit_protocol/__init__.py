"""
Credit Protocol Economy

Complete economic system for Industriverse enabling:
- Proof-of-Insight ledger for insight validation
- UTID marketplace for trading validated insights
- Token economics with dynamic pricing
- Revenue distribution for fair compensation

Architecture:
- Ledger: Blockchain-inspired immutable record
- Marketplace: Trading platform with multiple business models
- Economics: Token supply, staking, and rewards
- Distribution: Transparent revenue sharing

Business Models:
1. One-time Sale: Full ownership transfer
2. License: Time-limited access
3. Subscription: Recurring access
4. Auction: Competitive bidding
5. Citation Royalty: Pay per use

Revenue Distribution:
- Creator: 60-70%
- Validators: 10-15%
- Source Authors: 5-10%
- Platform: 10-20%
- Stakers: 5%
"""

from .proof_ledger import (
    ProofOfInsightLedger,
    LedgerEvent,
    LedgerBlock,
    InsightOwnership,
    EventType,
    ValidationMethod,
    get_proof_ledger,
)

from .utid_marketplace import (
    UTIDMarketplace,
    MarketplaceListing,
    Transaction,
    InsightAccess,
    ListingType,
    ListingStatus,
    LicenseType,
    get_utid_marketplace,
)

from .token_economics import (
    TokenEconomics,
    TokenAccount,
    Stake,
    PricingParameters,
    TokenAction,
    StakeStatus,
    get_token_economics,
)

from .revenue_distribution import (
    RevenueDistributor,
    DistributionRecord,
    RevenueShare,
    DistributionPolicy,
    get_revenue_distributor,
)

__all__ = [
    # Proof Ledger
    "ProofOfInsightLedger",
    "LedgerEvent",
    "LedgerBlock",
    "InsightOwnership",
    "EventType",
    "ValidationMethod",
    "get_proof_ledger",

    # UTID Marketplace
    "UTIDMarketplace",
    "MarketplaceListing",
    "Transaction",
    "InsightAccess",
    "ListingType",
    "ListingStatus",
    "LicenseType",
    "get_utid_marketplace",

    # Token Economics
    "TokenEconomics",
    "TokenAccount",
    "Stake",
    "PricingParameters",
    "TokenAction",
    "StakeStatus",
    "get_token_economics",

    # Revenue Distribution
    "RevenueDistributor",
    "DistributionRecord",
    "RevenueShare",
    "DistributionPolicy",
    "get_revenue_distributor",
]


def initialize_credit_protocol():
    """
    Initialize complete credit protocol economy

    Sets up all economic components and their integrations
    """
    # Initialize ledger
    ledger = get_proof_ledger()

    # Initialize marketplace
    marketplace = get_utid_marketplace()

    # Initialize token economics
    economics = get_token_economics()

    # Initialize revenue distributor
    distributor = get_revenue_distributor()

    return {
        'proof_ledger': ledger,
        'utid_marketplace': marketplace,
        'token_economics': economics,
        'revenue_distributor': distributor,
        'status': 'initialized'
    }


def create_insight_sale_workflow():
    """
    Complete workflow: Insight → List → Purchase → Distribute Revenue

    Example workflow:
    1. Creator lists insight on marketplace
    2. Buyer purchases insight
    3. Revenue is distributed to all parties
    4. Ownership is transferred
    5. All events recorded on ledger
    """
    ledger = get_proof_ledger()
    marketplace = get_utid_marketplace()
    economics = get_token_economics()
    distributor = get_revenue_distributor()

    def workflow(
        utid: str,
        insight_id: str,
        creator_id: str,
        buyer_id: str,
        validator_ids: List[str],
        proof_score: float,
        listing_price: Decimal
    ):
        from decimal import Decimal

        # Step 1: Check buyer has credits
        buyer_account = economics.get_or_create_account(buyer_id)
        if buyer_account.available_balance < listing_price:
            return {'error': 'Insufficient credits'}

        # Step 2: Create marketplace listing
        listing = marketplace.create_sale_listing(
            utid=utid,
            insight_id=insight_id,
            seller_id=creator_id,
            seller_name=f"Creator {creator_id}",
            price=listing_price,
            title=f"Insight {insight_id}",
            description="Validated research insight",
            proof_score=proof_score
        )

        # Step 3: Purchase insight
        success, message, transaction = marketplace.purchase_insight(
            listing_id=listing.listing_id,
            buyer_id=buyer_id,
            buyer_credits=buyer_account.available_balance
        )

        if not success:
            return {'error': message}

        # Step 4: Transfer credits
        economics.transfer_tokens(
            from_user=buyer_id,
            to_user=creator_id,  # Temporary holder
            amount=listing_price
        )

        # Step 5: Distribute revenue
        distribution = distributor.distribute_sale_revenue(
            transaction_id=transaction.transaction_id,
            utid=utid,
            insight_id=insight_id,
            total_amount=listing_price,
            creator_id=creator_id,
            validator_ids=validator_ids,
            proof_score=proof_score
        )

        # Step 6: Actually transfer to each recipient
        for share in distribution.shares:
            if share.participant_id != creator_id:  # Already has funds
                economics.transfer_tokens(
                    from_user=creator_id,
                    to_user=share.participant_id,
                    amount=share.share_amount,
                    apply_burn=False  # Already burned in initial transfer
                )

        # Step 7: Record on ledger
        ledger.record_utid_transfer(
            utid=utid,
            from_owner=creator_id,
            to_owner=buyer_id,
            transaction_amount=float(listing_price)
        )

        ledger.record_revenue_distribution(
            utid=utid,
            total_amount=float(listing_price),
            revenue_share={s.participant_id: float(s.share_amount) for s in distribution.shares}
        )

        return {
            'success': True,
            'transaction': transaction.to_dict(),
            'distribution': distribution.to_dict(),
            'new_owner': buyer_id,
            'total_paid': float(listing_price),
        }

    return workflow


def create_citation_royalty_workflow():
    """
    Workflow: Paper Citation → Royalty Payment → Revenue Distribution

    When a paper cites an insight, automatic royalty is paid
    """
    ledger = get_proof_ledger()
    economics = get_token_economics()
    distributor = get_revenue_distributor()

    def workflow(
        utid: str,
        insight_id: str,
        creator_id: str,
        citing_author_id: str,
        proof_score: float
    ):
        from decimal import Decimal

        # Step 1: Calculate royalty
        royalty_amount = economics.calculate_citation_royalty(
            proof_score=proof_score,
            citation_impact_factor=1.0
        )

        # Step 2: Check citing author has credits
        author_account = economics.get_or_create_account(citing_author_id)
        if author_account.available_balance < royalty_amount:
            return {'error': 'Insufficient credits for royalty'}

        # Step 3: Distribute royalty
        distribution = distributor.distribute_citation_royalty(
            utid=utid,
            insight_id=insight_id,
            citation_amount=royalty_amount,
            creator_id=creator_id,
            citing_author_id=citing_author_id
        )

        # Step 4: Transfer tokens
        for share in distribution.shares:
            economics.transfer_tokens(
                from_user=citing_author_id,
                to_user=share.participant_id,
                amount=share.share_amount,
                apply_burn=False
            )

        # Step 5: Record on ledger
        ledger.record_citation(
            insight_id=insight_id,
            citing_paper_id=f"paper-{citing_author_id}"
        )

        ledger.record_revenue_distribution(
            utid=utid,
            total_amount=float(royalty_amount),
            revenue_share={s.participant_id: float(s.share_amount) for s in distribution.shares}
        )

        return {
            'success': True,
            'royalty_paid': float(royalty_amount),
            'distribution': distribution.to_dict(),
        }

    return workflow
