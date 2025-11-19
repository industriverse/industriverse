"""
Revenue Distribution

Fair and transparent revenue sharing for the Industriverse economy.

Distribution Model:
- Creator: 60-70% (original insight creator)
- Validators: 10-15% (split among all validators)
- Source Papers: 5-10% (authors of cited papers)
- Platform: 10-20% (Industriverse)
- Stakers: 5% (redistributed as staking rewards)

Special Cases:
- Multiple creators: Split creator share
- Collaborative insights: Weighted by contribution
- Citation royalties: Ongoing micro-payments
- Platform tools: Higher platform share for tool-assisted insights
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
import secrets


@dataclass
class RevenueShare:
    """Revenue share for a participant"""
    participant_id: str
    participant_type: str  # 'creator', 'validator', 'source_author', 'platform', 'staker'
    share_amount: Decimal
    share_percentage: float
    reason: str


@dataclass
class DistributionPolicy:
    """Policy for revenue distribution"""
    # Base shares (percentages)
    creator_share: float = 0.65  # 65%
    validator_share: float = 0.12  # 12%
    source_author_share: float = 0.08  # 8%
    platform_share: float = 0.10  # 10%
    staker_share: float = 0.05  # 5%

    # Modifiers
    collaborative_bonus: float = 0.05  # Bonus for collaborative insights
    high_proof_bonus: float = 0.10  # Bonus for high proof scores (>0.95)
    citation_royalty_rate: float = 0.30  # 30% of future citations go to creator

    # Minimums
    minimum_creator_share: float = 0.60  # Creator gets at least 60%
    minimum_platform_share: float = 0.05  # Platform gets at least 5%


@dataclass
class DistributionRecord:
    """Record of a revenue distribution"""
    distribution_id: str
    transaction_id: str  # Source transaction
    utid: str
    insight_id: str

    # Amounts
    total_amount: Decimal
    shares: List[RevenueShare]

    # Metadata
    policy: DistributionPolicy
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "completed"  # 'pending', 'completed', 'failed'

    def to_dict(self) -> Dict[str, Any]:
        return {
            'distribution_id': self.distribution_id,
            'transaction_id': self.transaction_id,
            'utid': self.utid,
            'insight_id': self.insight_id,
            'total_amount': float(self.total_amount),
            'shares': [
                {
                    'participant_id': s.participant_id,
                    'participant_type': s.participant_type,
                    'share_amount': float(s.share_amount),
                    'share_percentage': s.share_percentage,
                    'reason': s.reason,
                }
                for s in self.shares
            ],
            'timestamp': self.timestamp.isoformat(),
            'status': self.status,
        }


class RevenueDistributor:
    """
    Revenue Distribution Engine

    Handles fair and transparent revenue sharing:
    - Creator compensation
    - Validator rewards
    - Source paper royalties
    - Platform fees
    - Staker redistribution
    """

    def __init__(self):
        # Distribution records
        self.distributions: List[DistributionRecord] = []
        self.distributions_by_user: Dict[str, List[DistributionRecord]] = defaultdict(list)

        # Statistics
        self.total_distributed: Decimal = Decimal(0)
        self.total_by_type: Dict[str, Decimal] = defaultdict(Decimal)

        # Default policy
        self.default_policy = DistributionPolicy()

    def distribute_sale_revenue(
        self,
        transaction_id: str,
        utid: str,
        insight_id: str,
        total_amount: Decimal,
        creator_id: str,
        validator_ids: List[str],
        source_paper_authors: Optional[Dict[str, float]] = None,  # author_id -> contribution weight
        proof_score: float = 0.0,
        policy: Optional[DistributionPolicy] = None
    ) -> DistributionRecord:
        """
        Distribute revenue from insight sale

        Args:
            transaction_id: Source transaction
            utid: Insight UTID
            insight_id: Insight ID
            total_amount: Total revenue to distribute
            creator_id: Original insight creator
            validator_ids: List of validators
            source_paper_authors: Authors of cited papers (optional)
            proof_score: Proof score of insight
            policy: Custom distribution policy (optional)
        """
        if policy is None:
            policy = self.default_policy

        shares: List[RevenueShare] = []

        # Adjust shares based on proof score
        creator_pct = policy.creator_share
        if proof_score >= 0.95:
            # High proof score: Give creator bonus
            creator_pct += policy.high_proof_bonus

        # Ensure minimum shares
        creator_pct = max(creator_pct, policy.minimum_creator_share)

        # 1. Creator share
        creator_amount = total_amount * Decimal(creator_pct)
        shares.append(RevenueShare(
            participant_id=creator_id,
            participant_type='creator',
            share_amount=creator_amount,
            share_percentage=creator_pct,
            reason='Original insight creation'
        ))

        # 2. Validator share (split equally among validators)
        if validator_ids:
            validator_total = total_amount * Decimal(policy.validator_share)
            per_validator = validator_total / len(validator_ids)

            for validator_id in validator_ids:
                shares.append(RevenueShare(
                    participant_id=validator_id,
                    participant_type='validator',
                    share_amount=per_validator,
                    share_percentage=policy.validator_share / len(validator_ids),
                    reason='Insight validation'
                ))

        # 3. Source paper authors (if cited)
        if source_paper_authors:
            source_total = total_amount * Decimal(policy.source_author_share)

            # Distribute weighted by contribution
            total_weight = sum(source_paper_authors.values())

            for author_id, weight in source_paper_authors.items():
                author_pct = (weight / total_weight) * policy.source_author_share
                author_amount = total_amount * Decimal(author_pct)

                shares.append(RevenueShare(
                    participant_id=author_id,
                    participant_type='source_author',
                    share_amount=author_amount,
                    share_percentage=author_pct,
                    reason=f'Source paper contribution (weight: {weight})'
                ))

        # 4. Platform share
        platform_pct = policy.platform_share
        platform_pct = max(platform_pct, policy.minimum_platform_share)
        platform_amount = total_amount * Decimal(platform_pct)

        shares.append(RevenueShare(
            participant_id='platform',
            participant_type='platform',
            share_amount=platform_amount,
            share_percentage=platform_pct,
            reason='Platform operations and development'
        ))

        # 5. Staker share (goes to reward pool)
        staker_amount = total_amount * Decimal(policy.staker_share)
        shares.append(RevenueShare(
            participant_id='staker_pool',
            participant_type='staker',
            share_amount=staker_amount,
            share_percentage=policy.staker_share,
            reason='Staker rewards pool'
        ))

        # Verify total adds up (with small rounding tolerance)
        total_distributed = sum(s.share_amount for s in shares)
        difference = abs(total_amount - total_distributed)

        if difference > Decimal('0.01'):  # Allow 1 cent rounding error
            # Adjust platform share to account for rounding
            for share in shares:
                if share.participant_type == 'platform':
                    share.share_amount += (total_amount - total_distributed)
                    break

        # Create distribution record
        distribution = DistributionRecord(
            distribution_id=f"dist-{secrets.token_hex(8)}",
            transaction_id=transaction_id,
            utid=utid,
            insight_id=insight_id,
            total_amount=total_amount,
            shares=shares,
            policy=policy
        )

        # Record
        self.distributions.append(distribution)

        # Update indexes
        for share in shares:
            self.distributions_by_user[share.participant_id].append(distribution)
            self.total_by_type[share.participant_type] += share.share_amount

        self.total_distributed += total_amount

        return distribution

    def distribute_citation_royalty(
        self,
        utid: str,
        insight_id: str,
        citation_amount: Decimal,
        creator_id: str,
        citing_author_id: str,
        policy: Optional[DistributionPolicy] = None
    ) -> DistributionRecord:
        """
        Distribute citation royalty payment

        When an insight is cited, the citing author pays a royalty.
        This is split between creator and platform.
        """
        if policy is None:
            policy = self.default_policy

        shares: List[RevenueShare] = []

        # Creator gets majority
        creator_pct = 1.0 - policy.platform_share
        creator_amount = citation_amount * Decimal(creator_pct)

        shares.append(RevenueShare(
            participant_id=creator_id,
            participant_type='creator',
            share_amount=creator_amount,
            share_percentage=creator_pct,
            reason=f'Citation royalty from {citing_author_id}'
        ))

        # Platform gets remainder
        platform_amount = citation_amount * Decimal(policy.platform_share)

        shares.append(RevenueShare(
            participant_id='platform',
            participant_type='platform',
            share_amount=platform_amount,
            share_percentage=policy.platform_share,
            reason='Citation processing fee'
        ))

        # Create distribution
        distribution = DistributionRecord(
            distribution_id=f"dist-{secrets.token_hex(8)}",
            transaction_id=f"citation-{secrets.token_hex(4)}",
            utid=utid,
            insight_id=insight_id,
            total_amount=citation_amount,
            shares=shares,
            policy=policy
        )

        self.distributions.append(distribution)

        # Update indexes
        for share in shares:
            self.distributions_by_user[share.participant_id].append(distribution)
            self.total_by_type[share.participant_type] += share.share_amount

        self.total_distributed += citation_amount

        return distribution

    def distribute_license_revenue(
        self,
        transaction_id: str,
        utid: str,
        insight_id: str,
        license_amount: Decimal,
        creator_id: str,
        validator_ids: List[str],
        license_duration_days: int,
        policy: Optional[DistributionPolicy] = None
    ) -> DistributionRecord:
        """
        Distribute license revenue

        Similar to sale revenue but adjusted for license duration.
        Shorter licenses = higher platform share (more overhead)
        """
        if policy is None:
            policy = DistributionPolicy()  # Create new instance to modify

        # Adjust platform share based on license duration
        if license_duration_days <= 30:
            policy.platform_share = 0.15  # 15% for short licenses
        elif license_duration_days <= 90:
            policy.platform_share = 0.12  # 12% for medium licenses
        else:
            policy.platform_share = 0.10  # 10% for long licenses

        # Use sale distribution logic
        return self.distribute_sale_revenue(
            transaction_id=transaction_id,
            utid=utid,
            insight_id=insight_id,
            total_amount=license_amount,
            creator_id=creator_id,
            validator_ids=validator_ids,
            policy=policy
        )

    def distribute_collaborative_revenue(
        self,
        transaction_id: str,
        utid: str,
        insight_id: str,
        total_amount: Decimal,
        contributors: Dict[str, float],  # contributor_id -> contribution weight
        validator_ids: List[str],
        policy: Optional[DistributionPolicy] = None
    ) -> DistributionRecord:
        """
        Distribute revenue for collaborative insight

        Contributors split the creator share based on their contribution weights
        """
        if policy is None:
            policy = self.default_policy

        shares: List[RevenueShare] = []

        # 1. Contributors split creator share
        creator_total = total_amount * Decimal(policy.creator_share + policy.collaborative_bonus)
        total_weight = sum(contributors.values())

        for contributor_id, weight in contributors.items():
            contributor_pct = (weight / total_weight) * (policy.creator_share + policy.collaborative_bonus)
            contributor_amount = total_amount * Decimal(contributor_pct)

            shares.append(RevenueShare(
                participant_id=contributor_id,
                participant_type='creator',
                share_amount=contributor_amount,
                share_percentage=contributor_pct,
                reason=f'Collaborative contribution (weight: {weight})'
            ))

        # 2. Validators
        if validator_ids:
            validator_total = total_amount * Decimal(policy.validator_share)
            per_validator = validator_total / len(validator_ids)

            for validator_id in validator_ids:
                shares.append(RevenueShare(
                    participant_id=validator_id,
                    participant_type='validator',
                    share_amount=per_validator,
                    share_percentage=policy.validator_share / len(validator_ids),
                    reason='Insight validation'
                ))

        # 3. Platform (reduced due to collaborative bonus)
        platform_pct = policy.platform_share - policy.collaborative_bonus
        platform_pct = max(platform_pct, policy.minimum_platform_share)
        platform_amount = total_amount * Decimal(platform_pct)

        shares.append(RevenueShare(
            participant_id='platform',
            participant_type='platform',
            share_amount=platform_amount,
            share_percentage=platform_pct,
            reason='Platform operations'
        ))

        # 4. Stakers
        staker_amount = total_amount * Decimal(policy.staker_share)
        shares.append(RevenueShare(
            participant_id='staker_pool',
            participant_type='staker',
            share_amount=staker_amount,
            share_percentage=policy.staker_share,
            reason='Staker rewards pool'
        ))

        # Adjust for rounding
        total_distributed = sum(s.share_amount for s in shares)
        difference = total_amount - total_distributed

        if abs(difference) > Decimal('0.01'):
            for share in shares:
                if share.participant_type == 'platform':
                    share.share_amount += difference
                    break

        # Create distribution
        distribution = DistributionRecord(
            distribution_id=f"dist-{secrets.token_hex(8)}",
            transaction_id=transaction_id,
            utid=utid,
            insight_id=insight_id,
            total_amount=total_amount,
            shares=shares,
            policy=policy
        )

        self.distributions.append(distribution)

        for share in shares:
            self.distributions_by_user[share.participant_id].append(distribution)
            self.total_by_type[share.participant_type] += share.share_amount

        self.total_distributed += total_amount

        return distribution

    def get_user_earnings(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get earnings summary for a user"""
        distributions = self.distributions_by_user.get(user_id, [])

        # Filter by date range
        if start_date or end_date:
            filtered = []
            for dist in distributions:
                if start_date and dist.timestamp < start_date:
                    continue
                if end_date and dist.timestamp > end_date:
                    continue
                filtered.append(dist)
            distributions = filtered

        # Calculate totals by type
        earnings_by_type = defaultdict(Decimal)
        total_earnings = Decimal(0)

        for dist in distributions:
            for share in dist.shares:
                if share.participant_id == user_id:
                    earnings_by_type[share.participant_type] += share.share_amount
                    total_earnings += share.share_amount

        return {
            'user_id': user_id,
            'total_earnings': float(total_earnings),
            'earnings_by_type': {k: float(v) for k, v in earnings_by_type.items()},
            'distribution_count': len(distributions),
            'date_range': {
                'start': start_date.isoformat() if start_date else None,
                'end': end_date.isoformat() if end_date else None,
            }
        }

    def get_insight_revenue(self, utid: str) -> Dict[str, Any]:
        """Get total revenue for an insight"""
        distributions = [d for d in self.distributions if d.utid == utid]

        total_revenue = sum(d.total_amount for d in distributions)

        # Revenue by participant type
        revenue_by_type = defaultdict(Decimal)
        for dist in distributions:
            for share in dist.shares:
                revenue_by_type[share.participant_type] += share.share_amount

        return {
            'utid': utid,
            'total_revenue': float(total_revenue),
            'revenue_by_type': {k: float(v) for k, v in revenue_by_type.items()},
            'distribution_count': len(distributions),
            'first_sale': distributions[0].timestamp.isoformat() if distributions else None,
            'latest_sale': distributions[-1].timestamp.isoformat() if distributions else None,
        }

    def get_distribution_stats(self) -> Dict[str, Any]:
        """Get overall distribution statistics"""
        return {
            'total_distributed': float(self.total_distributed),
            'distribution_count': len(self.distributions),
            'distributions_by_type': {k: float(v) for k, v in self.total_by_type.items()},
            'unique_recipients': len(self.distributions_by_user),
            'average_distribution': float(self.total_distributed / len(self.distributions)) if self.distributions else 0,
        }

    def simulate_distribution(
        self,
        total_amount: Decimal,
        creator_id: str,
        validator_count: int,
        source_author_count: int = 0,
        proof_score: float = 0.90,
        policy: Optional[DistributionPolicy] = None
    ) -> Dict[str, Any]:
        """
        Simulate revenue distribution without recording

        Useful for previewing how revenue would be split
        """
        if policy is None:
            policy = self.default_policy

        # Create dummy IDs
        validator_ids = [f"validator-{i}" for i in range(validator_count)]
        source_authors = {f"author-{i}": 1.0 for i in range(source_author_count)} if source_author_count > 0 else None

        # Temporarily distribute
        temp_distributor = RevenueDistributor()
        temp_distributor.default_policy = policy

        distribution = temp_distributor.distribute_sale_revenue(
            transaction_id="simulation",
            utid="simulation-utid",
            insight_id="simulation-insight",
            total_amount=total_amount,
            creator_id=creator_id,
            validator_ids=validator_ids,
            source_paper_authors=source_authors,
            proof_score=proof_score,
            policy=policy
        )

        return {
            'total_amount': float(total_amount),
            'shares': [
                {
                    'participant_type': s.participant_type,
                    'amount': float(s.share_amount),
                    'percentage': s.share_percentage * 100,
                    'reason': s.reason,
                }
                for s in distribution.shares
            ],
            'policy': {
                'creator_share': policy.creator_share * 100,
                'validator_share': policy.validator_share * 100,
                'source_author_share': policy.source_author_share * 100,
                'platform_share': policy.platform_share * 100,
                'staker_share': policy.staker_share * 100,
            }
        }


# Global revenue distributor instance
_revenue_distributor: Optional[RevenueDistributor] = None


def get_revenue_distributor() -> RevenueDistributor:
    """Get or create global revenue distributor"""
    global _revenue_distributor
    if _revenue_distributor is None:
        _revenue_distributor = RevenueDistributor()
    return _revenue_distributor
