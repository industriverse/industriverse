"""
Market Engine - Phase 5 EIL

Dynamic pricing engine for Computational Energy Units (CEU) and Proof of Fitness Tokens (PFT).
Integrates with Phase 2 ProofEconomy smart contracts.

Pricing Model:
- CEU: Computational Energy Unit (base cost for ACE inference)
- PFT: Proof of Fitness Token (reward for validated predictions)
- Exchange rate: CEU ↔ PFT based on supply/demand + regime quality

Market Dynamics:
1. CEU Cost: Based on energy consumption + regime risk
2. PFT Reward: Based on proof quality + regime confidence
3. Bonding Curve: Automated market maker for CEU/PFT exchange
4. Regime Premium: Higher rewards for stable, approved regimes

Integrates with:
- Phase 2 ProofEconomy (PFT/MUNT smart contracts)
- Phase 5 EIL (regime-aware pricing)
- Phase 5 Proof Validator (quality-based rewards)
"""

import numpy as np
import time
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class CEUPrice:
    """Computational Energy Unit pricing"""
    base_price: float  # Base CEU cost in USD
    regime_multiplier: float  # 0.5-2.0x based on regime
    energy_cost: float  # Actual energy consumption
    total_ceu: float  # Total CEU for this operation
    timestamp: float


@dataclass
class PFTReward:
    """Proof of Fitness Token reward"""
    base_reward: float  # Base PFT amount (usually 1.0)
    quality_bonus: float  # 1.0-1.5x based on tri-check scores
    regime_bonus: float  # 1.0-2.0x based on regime quality
    total_pft: float  # Total PFT to mint
    timestamp: float


@dataclass
class MarketState:
    """Current market state"""
    ceu_supply: float  # Total CEU in circulation
    pft_supply: float  # Total PFT in circulation
    ceu_to_usd: float  # CEU price in USD
    pft_to_usd: float  # PFT price in USD
    ceu_to_pft: float  # CEU/PFT exchange rate
    volume_24h: float  # 24h trading volume
    timestamp: float

    def to_dict(self) -> Dict:
        return {
            'ceu_supply': self.ceu_supply,
            'pft_supply': self.pft_supply,
            'ceu_to_usd': self.ceu_to_usd,
            'pft_to_usd': self.pft_to_usd,
            'ceu_to_pft': self.ceu_to_pft,
            'volume_24h': self.volume_24h,
            'timestamp': self.timestamp
        }


class MarketEngine:
    """
    Dynamic pricing engine for CEU/PFT economy.

    Pricing Philosophy:
    - CEU costs more during high-risk regimes (chaotic, anomalous)
    - CEU costs less during stable, approved regimes
    - PFT rewards higher for stable, validated predictions
    - PFT rewards lower for uncertain or failed predictions

    Bonding Curve:
    - Automated Market Maker (AMM) for CEU ↔ PFT exchange
    - Price discovery based on supply/demand
    - Liquidity bootstrapping for new markets
    """

    def __init__(
        self,
        base_ceu_usd: float = 0.01,  # Base CEU price: $0.01 USD
        base_pft_usd: float = 1.00,  # Base PFT price: $1.00 USD
        initial_ceu_supply: float = 1_000_000.0,
        initial_pft_supply: float = 10_000.0,
        bonding_curve_k: float = 1000.0  # AMM constant k = x * y
    ):
        """
        Initialize Market Engine

        Args:
            base_ceu_usd: Base CEU price in USD
            base_pft_usd: Base PFT price in USD
            initial_ceu_supply: Initial CEU supply
            initial_pft_supply: Initial PFT supply
            bonding_curve_k: AMM bonding curve constant
        """
        self.base_ceu_usd = base_ceu_usd
        self.base_pft_usd = base_pft_usd

        # Market state
        self.market_state = MarketState(
            ceu_supply=initial_ceu_supply,
            pft_supply=initial_pft_supply,
            ceu_to_usd=base_ceu_usd,
            pft_to_usd=base_pft_usd,
            ceu_to_pft=base_pft_usd / base_ceu_usd,  # Initial exchange rate
            volume_24h=0.0,
            timestamp=time.time()
        )

        # AMM bonding curve: x * y = k
        self.bonding_curve_k = bonding_curve_k

        # Statistics
        self.stats = {
            'ceu_minted_total': 0.0,
            'pft_minted_total': 0.0,
            'ceu_burned_total': 0.0,
            'pft_burned_total': 0.0,
            'trades_total': 0,
            'volume_usd_total': 0.0
        }

        print(f"✅ MarketEngine initialized")
        print(f"  Base CEU: ${base_ceu_usd:.4f} USD")
        print(f"  Base PFT: ${base_pft_usd:.2f} USD")
        print(f"  CEU/PFT rate: {self.market_state.ceu_to_pft:.2f}")

    def calculate_ceu_cost(
        self,
        energy_consumption: float,  # kWh
        regime: str,
        regime_approved: bool,
        num_steps: int = 10
    ) -> CEUPrice:
        """
        Calculate CEU cost for ACE inference operation.

        Args:
            energy_consumption: Energy used (kWh)
            regime: Detected regime label
            regime_approved: Whether regime was approved by EIL
            num_steps: Number of prediction steps

        Returns:
            CEUPrice with breakdown
        """
        # Base CEU per kWh (assuming $0.10/kWh electricity)
        base_ceu_per_kwh = 10.0  # 1 kWh = 10 CEU at base rate

        # Regime-based multiplier
        if regime_approved:
            if "stable" in regime:
                regime_multiplier = 0.8  # 20% discount for stable regime
            elif "transitional" in regime:
                regime_multiplier = 1.0  # Normal price
            else:
                regime_multiplier = 1.2  # 20% premium for uncertain
        else:
            # Not approved - higher cost
            regime_multiplier = 1.5  # 50% premium for risky regime

        # Calculate total CEU
        base_ceu = energy_consumption * base_ceu_per_kwh
        total_ceu = base_ceu * regime_multiplier * (num_steps / 10.0)

        # Update market state (mint CEU)
        self.market_state.ceu_supply += total_ceu
        self.stats['ceu_minted_total'] += total_ceu

        return CEUPrice(
            base_price=self.market_state.ceu_to_usd,
            regime_multiplier=regime_multiplier,
            energy_cost=energy_consumption,
            total_ceu=total_ceu,
            timestamp=time.time()
        )

    def calculate_pft_reward(
        self,
        proof_quality: float,  # 0-1 (average of tri-check scores)
        regime: str,
        regime_approved: bool,
        regime_confidence: float
    ) -> PFTReward:
        """
        Calculate PFT reward for validated proof.

        Args:
            proof_quality: Average tri-check score (0-1)
            regime: Detected regime label
            regime_approved: Whether regime was approved
            regime_confidence: Regime confidence (0-1)

        Returns:
            PFTReward with breakdown
        """
        # Base reward
        base_reward = 1.0

        # Quality bonus (1.0-1.5x)
        if proof_quality > 0.95:
            quality_bonus = 1.5
        elif proof_quality > 0.90:
            quality_bonus = 1.3
        elif proof_quality > 0.85:
            quality_bonus = 1.1
        else:
            quality_bonus = 1.0

        # Regime bonus (1.0-2.0x)
        if regime_approved:
            if "stable" in regime and regime_confidence > 0.9:
                regime_bonus = 2.0  # Double reward for high-quality stable regime
            elif "stable" in regime:
                regime_bonus = 1.5
            elif "transitional" in regime:
                regime_bonus = 1.2
            else:
                regime_bonus = 1.0
        else:
            # Not approved - reduced reward
            regime_bonus = 0.5

        # Calculate total PFT
        total_pft = base_reward * quality_bonus * regime_bonus

        # Update market state (mint PFT)
        self.market_state.pft_supply += total_pft
        self.stats['pft_minted_total'] += total_pft

        # Update PFT price based on supply (simple supply/demand)
        self._update_pft_price()

        return PFTReward(
            base_reward=base_reward,
            quality_bonus=quality_bonus,
            regime_bonus=regime_bonus,
            total_pft=total_pft,
            timestamp=time.time()
        )

    def swap_ceu_for_pft(self, ceu_amount: float) -> Tuple[float, float]:
        """
        Swap CEU for PFT using bonding curve AMM.

        AMM Formula: x * y = k
        where x = CEU reserve, y = PFT reserve

        Args:
            ceu_amount: CEU to swap

        Returns:
            (pft_received, new_ceu_to_pft_rate)
        """
        # Current reserves (simplified - in production would use liquidity pools)
        ceu_reserve = self.market_state.ceu_supply * 0.1  # 10% in AMM pool
        pft_reserve = self.market_state.pft_supply * 0.1

        # Calculate PFT output using constant product formula
        # k = x * y
        # (x + dx) * (y - dy) = k
        # dy = y - k / (x + dx)

        k = ceu_reserve * pft_reserve
        new_ceu_reserve = ceu_reserve + ceu_amount
        new_pft_reserve = k / new_ceu_reserve
        pft_out = pft_reserve - new_pft_reserve

        # Update exchange rate
        new_rate = new_ceu_reserve / new_pft_reserve
        self.market_state.ceu_to_pft = new_rate

        # Update volume
        volume_usd = ceu_amount * self.market_state.ceu_to_usd
        self.market_state.volume_24h += volume_usd
        self.stats['volume_usd_total'] += volume_usd
        self.stats['trades_total'] += 1

        return (pft_out, new_rate)

    def swap_pft_for_ceu(self, pft_amount: float) -> Tuple[float, float]:
        """
        Swap PFT for CEU using bonding curve AMM.

        Args:
            pft_amount: PFT to swap

        Returns:
            (ceu_received, new_ceu_to_pft_rate)
        """
        # Current reserves
        ceu_reserve = self.market_state.ceu_supply * 0.1
        pft_reserve = self.market_state.pft_supply * 0.1

        # Calculate CEU output
        k = ceu_reserve * pft_reserve
        new_pft_reserve = pft_reserve + pft_amount
        new_ceu_reserve = k / new_pft_reserve
        ceu_out = ceu_reserve - new_ceu_reserve

        # Update exchange rate
        new_rate = new_ceu_reserve / new_pft_reserve
        self.market_state.ceu_to_pft = new_rate

        # Update volume
        volume_usd = pft_amount * self.market_state.pft_to_usd
        self.market_state.volume_24h += volume_usd
        self.stats['volume_usd_total'] += volume_usd
        self.stats['trades_total'] += 1

        return (ceu_out, new_rate)

    def _update_pft_price(self):
        """Update PFT price based on supply (simple model)"""
        # Price inversely proportional to supply growth
        supply_ratio = self.market_state.pft_supply / 10_000.0  # Relative to initial
        self.market_state.pft_to_usd = self.base_pft_usd / np.sqrt(supply_ratio)

        # Update CEU price (correlated but damped)
        self.market_state.ceu_to_usd = self.base_ceu_usd * np.sqrt(supply_ratio) * 0.5

    def get_market_state(self) -> MarketState:
        """Get current market state"""
        self.market_state.timestamp = time.time()
        return self.market_state

    def get_pricing(self) -> Dict:
        """Get current pricing information"""
        return {
            'ceu_price': self.market_state.ceu_to_usd,
            'pft_price': self.market_state.pft_to_usd,
            'ceu_pft_rate': self.market_state.ceu_to_pft,
            'pool_liquidity_ceu': self.market_state.ceu_supply * 0.1,  # 10% in AMM pool
            'pool_liquidity_pft': self.market_state.pft_supply * 0.1,
            'last_updated': datetime.fromtimestamp(self.market_state.timestamp).isoformat()
        }

    def get_stats(self) -> Dict:
        """Get market statistics"""
        return {
            **self.stats,
            'market_state': self.market_state.to_dict()
        }


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("MARKET ENGINE - CEU/PFT PRICING TEST")
    print("=" * 70)

    # Initialize market
    market = MarketEngine(
        base_ceu_usd=0.01,
        base_pft_usd=1.00,
        initial_ceu_supply=1_000_000.0,
        initial_pft_supply=10_000.0
    )

    # Test Case 1: CEU cost for stable regime
    print("\n[Test 1] CEU Cost - Stable Regime")
    ceu_cost = market.calculate_ceu_cost(
        energy_consumption=0.5,  # 0.5 kWh
        regime="stable_confirmed",
        regime_approved=True,
        num_steps=10
    )
    print(f"  Energy: 0.5 kWh")
    print(f"  Regime: stable_confirmed (approved)")
    print(f"  Regime Multiplier: {ceu_cost.regime_multiplier}x")
    print(f"  Total CEU: {ceu_cost.total_ceu:.2f}")
    print(f"  USD Cost: ${ceu_cost.total_ceu * ceu_cost.base_price:.4f}")

    # Test Case 2: CEU cost for chaotic regime
    print("\n[Test 2] CEU Cost - Chaotic Regime")
    ceu_cost2 = market.calculate_ceu_cost(
        energy_consumption=0.5,
        regime="chaotic_unconfirmed",
        regime_approved=False,
        num_steps=10
    )
    print(f"  Energy: 0.5 kWh")
    print(f"  Regime: chaotic_unconfirmed (not approved)")
    print(f"  Regime Multiplier: {ceu_cost2.regime_multiplier}x")
    print(f"  Total CEU: {ceu_cost2.total_ceu:.2f}")
    print(f"  USD Cost: ${ceu_cost2.total_ceu * ceu_cost2.base_price:.4f}")

    # Test Case 3: PFT reward for high-quality proof
    print("\n[Test 3] PFT Reward - High Quality")
    pft_reward = market.calculate_pft_reward(
        proof_quality=0.96,  # 96% tri-check score
        regime="stable_confirmed",
        regime_approved=True,
        regime_confidence=0.95
    )
    print(f"  Proof Quality: 96%")
    print(f"  Regime: stable_confirmed (95% confidence)")
    print(f"  Quality Bonus: {pft_reward.quality_bonus}x")
    print(f"  Regime Bonus: {pft_reward.regime_bonus}x")
    print(f"  Total PFT: {pft_reward.total_pft:.2f}")
    print(f"  USD Value: ${pft_reward.total_pft * market.market_state.pft_to_usd:.2f}")

    # Test Case 4: PFT reward for poor quality
    print("\n[Test 4] PFT Reward - Poor Quality")
    pft_reward2 = market.calculate_pft_reward(
        proof_quality=0.75,
        regime="chaotic_unconfirmed",
        regime_approved=False,
        regime_confidence=0.60
    )
    print(f"  Proof Quality: 75%")
    print(f"  Regime: chaotic_unconfirmed (60% confidence)")
    print(f"  Quality Bonus: {pft_reward2.quality_bonus}x")
    print(f"  Regime Bonus: {pft_reward2.regime_bonus}x")
    print(f"  Total PFT: {pft_reward2.total_pft:.2f}")

    # Test Case 5: CEU ↔ PFT swap
    print("\n[Test 5] CEU → PFT Swap")
    pft_out, new_rate = market.swap_ceu_for_pft(100.0)
    print(f"  CEU In: 100.0")
    print(f"  PFT Out: {pft_out:.4f}")
    print(f"  New Rate: {new_rate:.2f} CEU/PFT")

    # Market state
    print("\n[Market State]")
    state = market.get_market_state()
    print(f"  CEU Supply: {state.ceu_supply:,.0f}")
    print(f"  PFT Supply: {state.pft_supply:,.2f}")
    print(f"  CEU Price: ${state.ceu_to_usd:.4f}")
    print(f"  PFT Price: ${state.pft_to_usd:.2f}")
    print(f"  Exchange Rate: {state.ceu_to_pft:.2f} CEU/PFT")
    print(f"  24h Volume: ${state.volume_24h:.2f}")

    # Stats
    print("\n[Statistics]")
    stats = market.get_stats()
    print(f"  CEU Minted: {stats['ceu_minted_total']:,.2f}")
    print(f"  PFT Minted: {stats['pft_minted_total']:,.2f}")
    print(f"  Total Trades: {stats['trades_total']}")
    print(f"  Total Volume: ${stats['volume_usd_total']:.2f}")

    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
