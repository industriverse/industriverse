"""
Token Economics

Credit token mechanics and pricing algorithms for the Industriverse economy.

Features:
- Dynamic pricing based on proof scores, citations, demand
- Credit minting and burning mechanisms
- Staking for validators
- Reward distribution
- Exchange rate management
- Supply control and inflation prevention

Token: CREDITS (IV-C)
- Used for purchasing insights, licenses, and services
- Earned by creating and validating insights
- Staked by validators for governance rights
- Burned on certain transactions to control supply
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal
import math
from enum import Enum


class TokenAction(Enum):
    """Types of token actions"""
    MINT = "mint"  # Create new tokens
    BURN = "burn"  # Destroy tokens
    TRANSFER = "transfer"  # Move tokens
    STAKE = "stake"  # Lock tokens
    UNSTAKE = "unstake"  # Unlock tokens
    REWARD = "reward"  # Distribute rewards
    PURCHASE = "purchase"  # Buy insights


class StakeStatus(Enum):
    """Status of stake"""
    ACTIVE = "active"
    PENDING_UNSTAKE = "pending_unstake"
    UNSTAKED = "unstaked"


@dataclass
class TokenAccount:
    """User token account"""
    user_id: str

    # Balances
    available_balance: Decimal = Decimal(0)  # Liquid tokens
    staked_balance: Decimal = Decimal(0)  # Locked in staking
    pending_rewards: Decimal = Decimal(0)  # Unclaimed rewards

    # Stats
    total_earned: Decimal = Decimal(0)
    total_spent: Decimal = Decimal(0)
    total_staked: Decimal = Decimal(0)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    last_transaction: Optional[datetime] = None

    def total_balance(self) -> Decimal:
        """Total balance including staked and pending"""
        return self.available_balance + self.staked_balance + self.pending_rewards


@dataclass
class Stake:
    """Staking position"""
    stake_id: str
    user_id: str
    amount: Decimal

    # Timing
    staked_at: datetime
    unlock_at: Optional[datetime] = None  # Lock period
    unstaked_at: Optional[datetime] = None

    # Status
    status: StakeStatus = StakeStatus.ACTIVE

    # Rewards
    rewards_earned: Decimal = Decimal(0)
    last_reward_time: datetime = field(default_factory=datetime.now)

    # APY
    apy: float = 0.15  # 15% base APY


@dataclass
class PricingParameters:
    """Parameters for dynamic pricing"""
    # Base parameters
    base_price: Decimal = Decimal(10)  # Base price for insights

    # Proof score multiplier (0.85-1.0 proof score)
    proof_score_weight: float = 2.0  # Price increases with proof score

    # Citation multiplier
    citation_weight: float = 0.5  # Price increases with citations
    citation_decay: float = 0.9  # Diminishing returns

    # Demand multiplier
    demand_weight: float = 1.5  # Price increases with demand
    demand_half_life_days: int = 30  # Demand decay

    # Supply penalty
    supply_weight: float = 0.3  # Price decreases if similar insights available

    # Time decay (for older insights)
    time_decay_rate: float = 0.05  # Price decreases over time
    time_decay_max: float = 0.5  # Maximum 50% decay

    # License discounts
    license_discount: Dict[str, float] = field(default_factory=lambda: {
        'personal': 0.7,  # 30% discount
        'team': 0.8,  # 20% discount
        'enterprise': 1.2,  # 20% premium
        'research': 0.5,  # 50% discount
        'commercial': 1.5,  # 50% premium
    })


class TokenEconomics:
    """
    Token Economics Engine

    Manages:
    - Credit token supply and distribution
    - Dynamic pricing algorithms
    - Staking and rewards
    - Exchange rates
    - Inflation control
    """

    def __init__(self):
        # Token accounts
        self.accounts: Dict[str, TokenAccount] = {}

        # Staking
        self.stakes: Dict[str, Stake] = {}
        self.stakes_by_user: Dict[str, List[str]] = {}

        # Supply metrics
        self.total_supply: Decimal = Decimal(1_000_000)  # Initial supply
        self.circulating_supply: Decimal = Decimal(1_000_000)
        self.total_staked: Decimal = Decimal(0)
        self.total_burned: Decimal = Decimal(0)

        # Pricing
        self.pricing_params = PricingParameters()

        # Exchange rates (Credits to USD)
        self.exchange_rate_usd: Decimal = Decimal(0.10)  # $0.10 per credit

        # Inflation control
        self.max_supply: Decimal = Decimal(100_000_000)  # 100M cap
        self.annual_inflation_rate: float = 0.05  # 5% annual inflation
        self.burn_rate: float = 0.02  # 2% transaction burn

        # Reward pool
        self.reward_pool: Decimal = Decimal(100_000)  # Reserved for rewards

    def get_or_create_account(self, user_id: str) -> TokenAccount:
        """Get or create token account"""
        if user_id not in self.accounts:
            self.accounts[user_id] = TokenAccount(user_id=user_id)
        return self.accounts[user_id]

    def mint_tokens(
        self,
        user_id: str,
        amount: Decimal,
        reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """Mint new tokens (create supply)"""
        # Check supply cap
        if self.total_supply + amount > self.max_supply:
            return False, f"Would exceed max supply ({self.max_supply})"

        account = self.get_or_create_account(user_id)
        account.available_balance += amount
        account.total_earned += amount
        account.last_transaction = datetime.now()

        # Update supply metrics
        self.total_supply += amount
        self.circulating_supply += amount

        return True, f"Minted {amount} credits for {reason}"

    def burn_tokens(
        self,
        user_id: str,
        amount: Decimal,
        reason: str
    ) -> Tuple[bool, str]:
        """Burn tokens (destroy supply)"""
        account = self.get_or_create_account(user_id)

        if account.available_balance < amount:
            return False, f"Insufficient balance (have {account.available_balance}, need {amount})"

        account.available_balance -= amount
        account.last_transaction = datetime.now()

        # Update supply metrics
        self.total_supply -= amount
        self.circulating_supply -= amount
        self.total_burned += amount

        return True, f"Burned {amount} credits for {reason}"

    def transfer_tokens(
        self,
        from_user: str,
        to_user: str,
        amount: Decimal,
        apply_burn: bool = True
    ) -> Tuple[bool, str]:
        """Transfer tokens between accounts"""
        from_account = self.get_or_create_account(from_user)
        to_account = self.get_or_create_account(to_user)

        if from_account.available_balance < amount:
            return False, "Insufficient balance"

        # Calculate burn amount
        burn_amount = Decimal(0)
        if apply_burn:
            burn_amount = amount * Decimal(self.burn_rate)
            amount_after_burn = amount - burn_amount
        else:
            amount_after_burn = amount

        # Transfer
        from_account.available_balance -= amount
        from_account.total_spent += amount
        from_account.last_transaction = datetime.now()

        to_account.available_balance += amount_after_burn
        to_account.total_earned += amount_after_burn
        to_account.last_transaction = datetime.now()

        # Burn
        if burn_amount > 0:
            self.total_supply -= burn_amount
            self.circulating_supply -= burn_amount
            self.total_burned += burn_amount

        return True, f"Transferred {amount_after_burn} credits (burned {burn_amount})"

    def stake_tokens(
        self,
        user_id: str,
        amount: Decimal,
        lock_duration_days: int = 0
    ) -> Tuple[bool, str, Optional[Stake]]:
        """Stake tokens for rewards"""
        account = self.get_or_create_account(user_id)

        if account.available_balance < amount:
            return False, "Insufficient balance", None

        # Create stake
        import secrets
        stake_id = f"stake-{secrets.token_hex(8)}"

        unlock_at = None
        if lock_duration_days > 0:
            unlock_at = datetime.now() + timedelta(days=lock_duration_days)

        # APY bonus for longer locks
        apy = 0.15  # Base 15%
        if lock_duration_days >= 365:
            apy = 0.25  # 25% for 1 year+
        elif lock_duration_days >= 180:
            apy = 0.20  # 20% for 6 months+

        stake = Stake(
            stake_id=stake_id,
            user_id=user_id,
            amount=amount,
            staked_at=datetime.now(),
            unlock_at=unlock_at,
            apy=apy
        )

        # Update account
        account.available_balance -= amount
        account.staked_balance += amount
        account.total_staked += amount
        account.last_transaction = datetime.now()

        # Record stake
        self.stakes[stake_id] = stake
        if user_id not in self.stakes_by_user:
            self.stakes_by_user[user_id] = []
        self.stakes_by_user[user_id].append(stake_id)

        # Update supply metrics
        self.total_staked += amount
        self.circulating_supply -= amount

        return True, f"Staked {amount} credits at {apy*100}% APY", stake

    def unstake_tokens(
        self,
        stake_id: str
    ) -> Tuple[bool, str]:
        """Unstake tokens"""
        if stake_id not in self.stakes:
            return False, "Stake not found"

        stake = self.stakes[stake_id]
        account = self.get_or_create_account(stake.user_id)

        # Check if unlocked
        if stake.unlock_at and datetime.now() < stake.unlock_at:
            return False, f"Stake locked until {stake.unlock_at.isoformat()}"

        # Calculate pending rewards
        self._calculate_stake_rewards(stake)

        # Unstake
        account.staked_balance -= stake.amount
        account.available_balance += stake.amount
        account.pending_rewards += stake.rewards_earned
        account.last_transaction = datetime.now()

        stake.status = StakeStatus.UNSTAKED
        stake.unstaked_at = datetime.now()

        # Update supply metrics
        self.total_staked -= stake.amount
        self.circulating_supply += stake.amount

        return True, f"Unstaked {stake.amount} credits, earned {stake.rewards_earned} in rewards"

    def _calculate_stake_rewards(self, stake: Stake):
        """Calculate rewards for a stake"""
        if stake.status != StakeStatus.ACTIVE:
            return

        # Time staked since last reward
        time_diff = datetime.now() - stake.last_reward_time
        days_staked = time_diff.total_seconds() / 86400

        # Calculate rewards (APY proportional)
        annual_reward = stake.amount * Decimal(stake.apy)
        daily_reward = annual_reward / Decimal(365)
        reward = daily_reward * Decimal(days_staked)

        stake.rewards_earned += reward
        stake.last_reward_time = datetime.now()

        # Deduct from reward pool
        self.reward_pool -= reward

    def calculate_all_rewards(self):
        """Calculate rewards for all active stakes"""
        for stake in self.stakes.values():
            if stake.status == StakeStatus.ACTIVE:
                self._calculate_stake_rewards(stake)

    def claim_rewards(self, user_id: str) -> Tuple[bool, str, Decimal]:
        """Claim pending rewards"""
        account = self.get_or_create_account(user_id)

        # Calculate all pending rewards
        if user_id in self.stakes_by_user:
            for stake_id in self.stakes_by_user[user_id]:
                stake = self.stakes[stake_id]
                if stake.status == StakeStatus.ACTIVE:
                    self._calculate_stake_rewards(stake)
                    account.pending_rewards += stake.rewards_earned
                    stake.rewards_earned = Decimal(0)

        total_rewards = account.pending_rewards

        if total_rewards == 0:
            return False, "No rewards to claim", Decimal(0)

        # Transfer rewards to available balance
        account.available_balance += total_rewards
        account.pending_rewards = Decimal(0)
        account.total_earned += total_rewards
        account.last_transaction = datetime.now()

        return True, f"Claimed {total_rewards} credits in rewards", total_rewards

    def calculate_insight_price(
        self,
        proof_score: float,
        citation_count: int,
        age_days: int,
        demand_count: int,
        similar_insights_count: int,
        license_type: Optional[str] = None
    ) -> Decimal:
        """
        Calculate dynamic price for an insight

        Price factors:
        1. Proof score: Higher proof = higher price
        2. Citations: More citations = higher price (with diminishing returns)
        3. Age: Older insights = lower price
        4. Demand: More purchases = higher price
        5. Supply: More similar insights = lower price
        6. License type: Different multipliers
        """
        params = self.pricing_params

        # 1. Proof score multiplier (exponential)
        # 0.85 proof → 1.0x, 0.95 proof → 2.5x, 1.0 proof → 4.0x
        proof_multiplier = math.exp(params.proof_score_weight * (proof_score - 0.85))

        # 2. Citation multiplier (logarithmic with decay)
        citation_multiplier = 1.0
        if citation_count > 0:
            citation_multiplier = 1 + params.citation_weight * math.log(1 + citation_count) * (params.citation_decay ** (citation_count / 10))

        # 3. Time decay (linear)
        time_penalty = max(1.0 - params.time_decay_rate * (age_days / 365), 1.0 - params.time_decay_max)

        # 4. Demand multiplier (exponential with half-life)
        demand_decay = math.exp(-age_days / params.demand_half_life_days)
        demand_multiplier = 1 + params.demand_weight * (demand_count / 10) * demand_decay

        # 5. Supply penalty (inverse)
        supply_penalty = 1.0
        if similar_insights_count > 0:
            supply_penalty = 1.0 / (1.0 + params.supply_weight * math.log(1 + similar_insights_count))

        # Combine all factors
        base_price = params.base_price
        calculated_price = base_price * Decimal(
            proof_multiplier *
            citation_multiplier *
            time_penalty *
            demand_multiplier *
            supply_penalty
        )

        # Apply license discount/premium
        if license_type and license_type in params.license_discount:
            calculated_price *= Decimal(params.license_discount[license_type])

        return calculated_price.quantize(Decimal('0.01'))

    def calculate_citation_royalty(
        self,
        proof_score: float,
        citation_impact_factor: float = 1.0
    ) -> Decimal:
        """
        Calculate royalty payment for a single citation

        Based on:
        - Proof score of insight
        - Impact factor of citing work
        """
        base_royalty = Decimal(0.50)  # $0.50 base per citation

        # Higher proof score = higher royalty
        proof_multiplier = Decimal(proof_score / 0.85)

        # Impact factor of citing work
        impact_multiplier = Decimal(citation_impact_factor)

        royalty = base_royalty * proof_multiplier * impact_multiplier

        return royalty.quantize(Decimal('0.01'))

    def reward_insight_creation(
        self,
        creator_id: str,
        proof_score: float
    ) -> Tuple[bool, str, Decimal]:
        """
        Reward user for creating validated insight

        Reward scales with proof score:
        - 0.85: 10 credits
        - 0.90: 25 credits
        - 0.95: 50 credits
        - 1.00: 100 credits
        """
        # Calculate reward based on proof score
        if proof_score < 0.85:
            return False, "Proof score too low for reward", Decimal(0)

        base_reward = Decimal(10)
        proof_multiplier = Decimal(math.exp(5 * (proof_score - 0.85)))  # Exponential reward
        reward = (base_reward * proof_multiplier).quantize(Decimal('0.01'))

        # Cap reward at 100 credits
        reward = min(reward, Decimal(100))

        # Mint tokens
        success, message = self.mint_tokens(
            creator_id,
            reward,
            f"insight_creation_reward (proof: {proof_score})"
        )

        return success, message, reward

    def reward_validation(
        self,
        validator_id: str,
        insight_proof_score: float
    ) -> Tuple[bool, str, Decimal]:
        """
        Reward validator for validating insight

        Smaller reward than creation, but scales with proof score
        """
        if insight_proof_score < 0.85:
            return False, "Proof score too low for reward", Decimal(0)

        base_reward = Decimal(2)  # 2 credits base
        proof_multiplier = Decimal(math.exp(3 * (insight_proof_score - 0.85)))
        reward = (base_reward * proof_multiplier).quantize(Decimal('0.01'))

        # Cap at 20 credits
        reward = min(reward, Decimal(20))

        # Mint tokens
        success, message = self.mint_tokens(
            validator_id,
            reward,
            f"validation_reward (proof: {insight_proof_score})"
        )

        return success, message, reward

    def get_account_summary(self, user_id: str) -> Dict[str, Any]:
        """Get account summary"""
        account = self.get_or_create_account(user_id)

        # Get active stakes
        active_stakes = []
        total_pending_rewards = Decimal(0)
        if user_id in self.stakes_by_user:
            for stake_id in self.stakes_by_user[user_id]:
                stake = self.stakes[stake_id]
                if stake.status == StakeStatus.ACTIVE:
                    self._calculate_stake_rewards(stake)
                    active_stakes.append({
                        'stake_id': stake_id,
                        'amount': float(stake.amount),
                        'apy': stake.apy,
                        'staked_at': stake.staked_at.isoformat(),
                        'unlock_at': stake.unlock_at.isoformat() if stake.unlock_at else None,
                        'rewards_earned': float(stake.rewards_earned),
                    })
                    total_pending_rewards += stake.rewards_earned

        return {
            'user_id': user_id,
            'balances': {
                'available': float(account.available_balance),
                'staked': float(account.staked_balance),
                'pending_rewards': float(account.pending_rewards + total_pending_rewards),
                'total': float(account.total_balance() + total_pending_rewards),
            },
            'stats': {
                'total_earned': float(account.total_earned),
                'total_spent': float(account.total_spent),
                'total_staked': float(account.total_staked),
            },
            'active_stakes': active_stakes,
            'created_at': account.created_at.isoformat(),
            'last_transaction': account.last_transaction.isoformat() if account.last_transaction else None,
        }

    def get_economy_stats(self) -> Dict[str, Any]:
        """Get overall economy statistics"""
        return {
            'supply': {
                'total_supply': float(self.total_supply),
                'circulating_supply': float(self.circulating_supply),
                'total_staked': float(self.total_staked),
                'total_burned': float(self.total_burned),
                'max_supply': float(self.max_supply),
                'utilization_rate': float(self.total_staked / self.total_supply) if self.total_supply > 0 else 0,
            },
            'accounts': {
                'total_accounts': len(self.accounts),
                'total_stakes': len([s for s in self.stakes.values() if s.status == StakeStatus.ACTIVE]),
            },
            'rates': {
                'exchange_rate_usd': float(self.exchange_rate_usd),
                'annual_inflation_rate': self.annual_inflation_rate,
                'burn_rate': self.burn_rate,
            },
            'reward_pool': float(self.reward_pool),
        }


# Global token economics instance
_token_economics: Optional[TokenEconomics] = None


def get_token_economics() -> TokenEconomics:
    """Get or create global token economics engine"""
    global _token_economics
    if _token_economics is None:
        _token_economics = TokenEconomics()
    return _token_economics
