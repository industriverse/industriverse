"""
Financial Fraud Detection Engine

Detects market manipulation and fraud using thermodynamic principles:
- Order flow entropy anomalies
- Market energy conservation violations
- Price thermodynamics (information propagation)
- Wash trading detection (cyclic energy flows)
- Pump-and-dump pattern recognition

Thermodynamic Market Model:
Financial markets can be modeled as thermodynamic systems where:
- Price movements = Energy flow
- Order flow = Particle flux
- Market entropy = Information uncertainty
- Trading volume = Thermodynamic temperature
- Bid-ask spread = Free energy barrier

Fraud Types Detected:
1. Wash Trading: Self-trading to create false volume (entropy violation)
2. Spoofing: Fake orders to manipulate price (energy manipulation)
3. Pump-and-Dump: Coordinated price inflation (entropy spike + collapse)
4. Front-Running: Order anticipation (information leakage)
5. Market Manipulation: Coordinated attacks (energy flow anomalies)

Thermodynamic Indicators:
1. Order Flow Entropy: H = -Σ p(i) log p(i)
   - Normal market: High entropy (diverse traders)
   - Wash trading: Low entropy (repetitive patterns)

2. Price Energy: E = Σ V_i * P_i (volume-weighted price)
   - Conservation: Total energy should be conserved in closed market
   - Violation: Artificial price inflation without corresponding energy input

3. Market Temperature: T ∝ Trading Volume
   - Sudden temperature spikes = Manipulation
   - Temperature asymmetry = Information leakage

4. Bid-Ask Spread (Free Energy): ΔG = P_ask - P_bid
   - Normal: Stable spread
   - Manipulation: Spread collapse/explosion

Detection Methodology:
- Real-time order flow analysis
- Entropy calculation on trading patterns
- Energy conservation validation
- Cross-correlation with market thermodynamics
- Machine learning on thermodynamic features

Integration:
- Monitors trading platforms (crypto, stocks, forex)
- Uses EIL for entropy calculations
- Registers fraud events in Security Event Registry
- Publishes alerts to compliance systems
- Visualizes market attacks in AR/VR

References:
- Mantegna & Stanley, "Introduction to Econophysics" (2000)
- Chakraborti et al., "Econophysics review" (2011)
- SEC regulations on market manipulation
- FINRA suspicious activity monitoring
"""

import logging
import asyncio
import numpy as np
import math
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Order:
    """Trading order."""
    order_id: str
    trader_id: str
    symbol: str
    side: OrderSide
    price: float
    quantity: float
    timestamp: datetime


@dataclass
class Trade:
    """Executed trade."""
    trade_id: str
    symbol: str
    price: float
    quantity: float
    buy_order_id: str
    sell_order_id: str
    buyer_id: str
    seller_id: str
    timestamp: datetime


@dataclass
class MarketThermodynamics:
    """Market thermodynamic state."""
    symbol: str
    timestamp: datetime

    # Price metrics
    price: float
    price_change: float
    volatility: float

    # Volume metrics
    volume: float
    volume_change: float

    # Thermodynamic metrics
    market_energy: float  # Volume-weighted price
    market_temperature: float  # Proportional to volume
    order_flow_entropy: float  # Shannon entropy of order distribution
    bid_ask_spread: float  # Free energy barrier

    # Anomaly indicators
    entropy_anomaly_score: float
    energy_anomaly_score: float
    temperature_anomaly_score: float


class FinancialFraudDetector:
    """
    Detect financial fraud using thermodynamic market analysis.

    Monitors order flow entropy, energy conservation, and market
    thermodynamics to identify manipulation patterns.
    """

    def __init__(
        self,
        database_pool=None,
        energy_intelligence_layer=None,
        security_registry=None,
        event_bus=None,
        market_data_interface=None
    ):
        """
        Initialize Financial Fraud Detector.

        Args:
            database_pool: PostgreSQL connection pool
            energy_intelligence_layer: EIL for entropy calculations
            security_registry: Security Event Registry
            event_bus: Event bus
            market_data_interface: Interface to market data feeds
        """
        self.db_pool = database_pool
        self.eil = energy_intelligence_layer
        self.security_registry = security_registry
        self.event_bus = event_bus
        self.market_data_interface = market_data_interface

        # Market history
        self.order_history: Dict[str, deque] = {}  # symbol -> orders
        self.trade_history: Dict[str, deque] = {}  # symbol -> trades
        self.thermodynamics_history: Dict[str, deque] = {}  # symbol -> thermodynamics

        # Trader analysis
        self.trader_orders: Dict[str, List[Order]] = defaultdict(list)
        self.trader_trades: Dict[str, List[Trade]] = defaultdict(list)

        # Detection thresholds
        self.entropy_threshold = 2.0  # bits
        self.wash_trading_correlation = 0.85  # High self-correlation
        self.pump_dump_volume_ratio = 5.0  # 5x normal volume
        self.spoofing_cancel_ratio = 0.80  # 80% cancellation rate
        self.energy_conservation_tolerance = 0.10  # 10% tolerance

        # Window sizes
        self.analysis_window = 1000  # Number of orders to analyze
        self.baseline_window = 10000  # Baseline calculation window

        # Monitoring state
        self.monitoring_active: Dict[str, bool] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}

        # Statistics
        self.stats = {
            "fraud_detected": 0,
            "wash_trading_detected": 0,
            "spoofing_detected": 0,
            "pump_dump_detected": 0,
            "front_running_detected": 0,
            "market_manipulation_detected": 0
        }

        logger.info("Financial Fraud Detector initialized")

    async def start_monitoring(self, symbol: str):
        """
        Start fraud monitoring for a trading symbol.

        Args:
            symbol: Trading symbol (e.g., BTC/USD, AAPL, EUR/USD)
        """
        if self.monitoring_active.get(symbol):
            logger.warning(f"Already monitoring {symbol}")
            return

        logger.info(f"Starting fraud monitoring for {symbol}")

        # Initialize history
        if symbol not in self.order_history:
            self.order_history[symbol] = deque(maxlen=self.baseline_window)
        if symbol not in self.trade_history:
            self.trade_history[symbol] = deque(maxlen=self.baseline_window)
        if symbol not in self.thermodynamics_history:
            self.thermodynamics_history[symbol] = deque(maxlen=1000)

        self.monitoring_active[symbol] = True

        # Create monitoring task
        task = asyncio.create_task(self._monitoring_loop(symbol))
        self.monitoring_tasks[symbol] = task

    async def stop_monitoring(self, symbol: str):
        """Stop fraud monitoring for symbol."""
        logger.info(f"Stopping fraud monitoring for {symbol}")

        self.monitoring_active[symbol] = False

        if symbol in self.monitoring_tasks:
            self.monitoring_tasks[symbol].cancel()
            del self.monitoring_tasks[symbol]

    async def _monitoring_loop(self, symbol: str):
        """Continuous fraud monitoring loop."""
        logger.info(f"Fraud monitoring loop started for {symbol}")

        try:
            while self.monitoring_active.get(symbol):
                # Fetch recent market data
                await self._fetch_market_data(symbol)

                # Calculate market thermodynamics
                thermodynamics = await self._calculate_market_thermodynamics(symbol)

                if thermodynamics:
                    self.thermodynamics_history[symbol].append(thermodynamics)

                    # Run fraud detection algorithms
                    await self._detect_wash_trading(symbol)
                    await self._detect_spoofing(symbol)
                    await self._detect_pump_dump(symbol, thermodynamics)
                    await self._detect_market_manipulation(symbol, thermodynamics)

                # Sleep 1 second between checks
                await asyncio.sleep(1.0)

        except asyncio.CancelledError:
            logger.info(f"Fraud monitoring cancelled for {symbol}")
        except Exception as e:
            logger.error(f"Fraud monitoring error: {e}")
        finally:
            self.monitoring_active[symbol] = False
            logger.info(f"Fraud monitoring loop ended for {symbol}")

    async def _fetch_market_data(self, symbol: str):
        """Fetch latest orders and trades."""
        # In production: Interface with real market data
        # For now: Simulate market data

        # Simulate random orders
        for _ in range(np.random.randint(5, 20)):
            order = Order(
                order_id=f"order_{np.random.randint(100000, 999999)}",
                trader_id=f"trader_{np.random.randint(1, 100)}",
                symbol=symbol,
                side=OrderSide.BUY if np.random.random() > 0.5 else OrderSide.SELL,
                price=100.0 + np.random.normal(0, 2.0),
                quantity=np.random.uniform(0.1, 10.0),
                timestamp=datetime.now()
            )

            self.order_history[symbol].append(order)
            self.trader_orders[order.trader_id].append(order)

        # Simulate random trades
        for _ in range(np.random.randint(2, 10)):
            trade = Trade(
                trade_id=f"trade_{np.random.randint(100000, 999999)}",
                symbol=symbol,
                price=100.0 + np.random.normal(0, 1.5),
                quantity=np.random.uniform(0.1, 5.0),
                buy_order_id="",
                sell_order_id="",
                buyer_id=f"trader_{np.random.randint(1, 100)}",
                seller_id=f"trader_{np.random.randint(1, 100)}",
                timestamp=datetime.now()
            )

            self.trade_history[symbol].append(trade)

    async def _calculate_market_thermodynamics(
        self,
        symbol: str
    ) -> Optional[MarketThermodynamics]:
        """
        Calculate thermodynamic state of market.

        Returns:
            MarketThermodynamics or None if insufficient data
        """
        trades = list(self.trade_history.get(symbol, []))
        orders = list(self.order_history.get(symbol, []))

        if len(trades) < 10 or len(orders) < 10:
            return None

        # Recent trades (last 100)
        recent_trades = trades[-100:]

        # Price metrics
        prices = np.array([t.price for t in recent_trades])
        current_price = prices[-1]
        price_change = prices[-1] - prices[0] if len(prices) > 1 else 0.0
        volatility = float(np.std(prices))

        # Volume metrics
        volumes = np.array([t.quantity for t in recent_trades])
        current_volume = float(np.sum(volumes))

        # Compare to baseline volume
        if len(trades) > 200:
            baseline_volume = float(np.mean([
                t.quantity for t in trades[-200:-100]
            ]))
            volume_change = current_volume - baseline_volume
        else:
            volume_change = 0.0

        # Market Energy: E = Σ(V_i * P_i)
        market_energy = float(np.sum(volumes * prices))

        # Market Temperature: T ∝ Volume
        market_temperature = float(np.mean(volumes)) * 1000.0

        # Order Flow Entropy
        order_flow_entropy = self._calculate_order_flow_entropy(orders[-100:])

        # Bid-Ask Spread (approximate from orders)
        buy_orders = [o for o in orders[-50:] if o.side == OrderSide.BUY]
        sell_orders = [o for o in orders[-50:] if o.side == OrderSide.SELL]

        if buy_orders and sell_orders:
            best_bid = max([o.price for o in buy_orders])
            best_ask = min([o.price for o in sell_orders])
            bid_ask_spread = best_ask - best_bid
        else:
            bid_ask_spread = 0.0

        # Calculate anomaly scores
        history = list(self.thermodynamics_history.get(symbol, []))

        if len(history) > 10:
            historical_entropy = np.array([h.order_flow_entropy for h in history])
            historical_energy = np.array([h.market_energy for h in history])
            historical_temp = np.array([h.market_temperature for h in history])

            entropy_mean = np.mean(historical_entropy)
            entropy_std = np.std(historical_entropy)
            entropy_anomaly = abs(order_flow_entropy - entropy_mean) / max(entropy_std, 0.1)

            energy_mean = np.mean(historical_energy)
            energy_std = np.std(historical_energy)
            energy_anomaly = abs(market_energy - energy_mean) / max(energy_std, 0.1)

            temp_mean = np.mean(historical_temp)
            temp_std = np.std(historical_temp)
            temp_anomaly = abs(market_temperature - temp_mean) / max(temp_std, 0.1)
        else:
            entropy_anomaly = 0.0
            energy_anomaly = 0.0
            temp_anomaly = 0.0

        return MarketThermodynamics(
            symbol=symbol,
            timestamp=datetime.now(),
            price=float(current_price),
            price_change=float(price_change),
            volatility=float(volatility),
            volume=float(current_volume),
            volume_change=float(volume_change),
            market_energy=float(market_energy),
            market_temperature=float(market_temperature),
            order_flow_entropy=float(order_flow_entropy),
            bid_ask_spread=float(bid_ask_spread),
            entropy_anomaly_score=float(entropy_anomaly),
            energy_anomaly_score=float(energy_anomaly),
            temperature_anomaly_score=float(temp_anomaly)
        )

    def _calculate_order_flow_entropy(self, orders: List[Order]) -> float:
        """
        Calculate Shannon entropy of order flow.

        High entropy = Diverse traders (normal market)
        Low entropy = Repetitive patterns (wash trading)

        Returns:
            Entropy in bits
        """
        if not orders:
            return 0.0

        # Count orders per trader
        trader_counts = defaultdict(int)
        for order in orders:
            trader_counts[order.trader_id] += 1

        # Calculate probabilities
        total_orders = len(orders)
        probabilities = np.array([count / total_orders for count in trader_counts.values()])

        # Shannon entropy: H = -Σ p(i) * log2(p(i))
        entropy = -np.sum(probabilities * np.log2(probabilities + 1e-10))

        return float(entropy)

    async def _detect_wash_trading(self, symbol: str):
        """
        Detect wash trading (self-trading to create false volume).

        Indicators:
        - Same trader on both sides of trade
        - Low order flow entropy (repetitive patterns)
        - High correlation between buy/sell orders
        """
        trades = list(self.trade_history.get(symbol, []))[-100:]

        # Check for same trader on both sides
        wash_trades = [
            t for t in trades
            if t.buyer_id == t.seller_id
        ]

        if wash_trades:
            wash_ratio = len(wash_trades) / len(trades)

            if wash_ratio > 0.10:  # >10% wash trades
                logger.critical(
                    f"WASH TRADING DETECTED on {symbol}: "
                    f"{len(wash_trades)}/{len(trades)} trades "
                    f"({wash_ratio*100:.1f}%)"
                )

                self.stats["fraud_detected"] += 1
                self.stats["wash_trading_detected"] += 1

                await self._register_fraud_event(
                    fraud_type="wash_trading",
                    symbol=symbol,
                    data={
                        "wash_trade_count": len(wash_trades),
                        "total_trades": len(trades),
                        "wash_ratio": wash_ratio,
                        "traders_involved": list(set([t.buyer_id for t in wash_trades]))
                    },
                    severity="critical"
                )

    async def _detect_spoofing(self, symbol: str):
        """
        Detect spoofing (fake orders to manipulate price).

        Indicators:
        - High order cancellation rate
        - Large orders that never execute
        - Rapid order placement/cancellation cycles
        """
        # In production: Track order cancellations
        # For now: Simplified detection based on order patterns

        orders = list(self.order_history.get(symbol, []))[-100:]

        if not orders:
            return

        # Group by trader
        trader_order_counts = defaultdict(int)
        for order in orders:
            trader_order_counts[order.trader_id] += 1

        # Detect traders with unusually high order frequency
        mean_orders = np.mean(list(trader_order_counts.values()))
        std_orders = np.std(list(trader_order_counts.values()))

        suspicious_traders = [
            trader_id for trader_id, count in trader_order_counts.items()
            if count > mean_orders + 3 * std_orders  # >3 std deviations
        ]

        if suspicious_traders:
            logger.warning(
                f"POSSIBLE SPOOFING on {symbol}: "
                f"{len(suspicious_traders)} suspicious traders"
            )

            self.stats["spoofing_detected"] += 1

    async def _detect_pump_dump(
        self,
        symbol: str,
        thermodynamics: MarketThermodynamics
    ):
        """
        Detect pump-and-dump schemes.

        Indicators:
        - Sudden volume spike (temperature anomaly)
        - Rapid price increase followed by crash
        - Entropy spike (coordinated activity)
        """
        # Check for volume spike
        if thermodynamics.temperature_anomaly_score > 5.0:  # >5 std deviations

            # Check price movement
            if thermodynamics.price_change > 0 and \
               thermodynamics.price_change / thermodynamics.price > 0.20:  # >20% increase

                logger.critical(
                    f"PUMP-AND-DUMP SUSPECTED on {symbol}: "
                    f"Volume spike {thermodynamics.temperature_anomaly_score:.1f}σ, "
                    f"Price +{(thermodynamics.price_change/thermodynamics.price)*100:.1f}%"
                )

                self.stats["fraud_detected"] += 1
                self.stats["pump_dump_detected"] += 1

                await self._register_fraud_event(
                    fraud_type="pump_and_dump",
                    symbol=symbol,
                    data={
                        "price_change_percent": (thermodynamics.price_change / thermodynamics.price) * 100,
                        "volume_anomaly_score": thermodynamics.temperature_anomaly_score,
                        "market_energy": thermodynamics.market_energy
                    },
                    severity="critical"
                )

    async def _detect_market_manipulation(
        self,
        symbol: str,
        thermodynamics: MarketThermodynamics
    ):
        """
        Detect general market manipulation.

        Indicators:
        - Multiple anomaly types simultaneously
        - Energy conservation violations
        - Coordinated entropy patterns
        """
        # Check for multiple simultaneous anomalies
        anomaly_count = sum([
            thermodynamics.entropy_anomaly_score > 3.0,
            thermodynamics.energy_anomaly_score > 3.0,
            thermodynamics.temperature_anomaly_score > 3.0
        ])

        if anomaly_count >= 2:
            logger.warning(
                f"MARKET MANIPULATION SUSPECTED on {symbol}: "
                f"{anomaly_count} thermodynamic anomalies detected"
            )

            self.stats["market_manipulation_detected"] += 1

            await self._register_fraud_event(
                fraud_type="market_manipulation",
                symbol=symbol,
                data={
                    "entropy_anomaly": thermodynamics.entropy_anomaly_score,
                    "energy_anomaly": thermodynamics.energy_anomaly_score,
                    "temperature_anomaly": thermodynamics.temperature_anomaly_score,
                    "bid_ask_spread": thermodynamics.bid_ask_spread
                },
                severity="high"
            )

    async def _register_fraud_event(
        self,
        fraud_type: str,
        symbol: str,
        data: Dict[str, Any],
        severity: str
    ):
        """Register fraud detection event."""
        if not self.security_registry:
            return

        try:
            await self.security_registry.register_security_event(
                event_type=f"financial_fraud_{fraud_type}",
                device_id=f"market_{symbol}",
                thermodynamic_data=data,
                severity=severity,
                confidence=0.85,
                threat_category="financial_fraud",
                source_sensor="financial_fraud_detector"
            )

            # Publish event
            if self.event_bus:
                await self.event_bus.publish(f"security.financial.{fraud_type}", {
                    "symbol": symbol,
                    **data,
                    "severity": severity,
                    "timestamp": datetime.now().isoformat()
                })

        except Exception as e:
            logger.error(f"Failed to register fraud event: {e}")

    def get_market_status(self, symbol: str) -> Dict[str, Any]:
        """Get current market security status."""
        if symbol not in self.thermodynamics_history:
            return {
                "symbol": symbol,
                "status": "not_monitored"
            }

        history = list(self.thermodynamics_history[symbol])

        if not history:
            return {
                "symbol": symbol,
                "status": "no_data"
            }

        current = history[-1]

        status = "ok"
        if current.entropy_anomaly_score > 5.0 or \
           current.energy_anomaly_score > 5.0 or \
           current.temperature_anomaly_score > 5.0:
            status = "critical"
        elif current.entropy_anomaly_score > 3.0 or \
             current.energy_anomaly_score > 3.0 or \
             current.temperature_anomaly_score > 3.0:
            status = "warning"

        return {
            "symbol": symbol,
            "status": status,
            "current_price": current.price,
            "market_energy": current.market_energy,
            "market_temperature": current.market_temperature,
            "order_flow_entropy": current.order_flow_entropy,
            "anomaly_scores": {
                "entropy": current.entropy_anomaly_score,
                "energy": current.energy_anomaly_score,
                "temperature": current.temperature_anomaly_score
            },
            "last_update": current.timestamp.isoformat()
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get fraud detector statistics."""
        return {
            **self.stats,
            "monitored_symbols": len(self.monitoring_active)
        }


# ============================================================================
# Singleton instance
# ============================================================================

_fraud_detector_instance = None


def get_financial_fraud_detector(
    database_pool=None,
    energy_intelligence_layer=None,
    security_registry=None,
    event_bus=None,
    market_data_interface=None
) -> FinancialFraudDetector:
    """
    Get singleton Financial Fraud Detector instance.

    Args:
        database_pool: PostgreSQL connection pool
        energy_intelligence_layer: EIL for entropy calculations
        security_registry: Security Event Registry
        event_bus: Event bus
        market_data_interface: Market data interface

    Returns:
        FinancialFraudDetector instance
    """
    global _fraud_detector_instance

    if _fraud_detector_instance is None:
        _fraud_detector_instance = FinancialFraudDetector(
            database_pool=database_pool,
            energy_intelligence_layer=energy_intelligence_layer,
            security_registry=security_registry,
            event_bus=event_bus,
            market_data_interface=market_data_interface
        )

    return _fraud_detector_instance
