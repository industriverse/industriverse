"""
Intelligence Market Service for the Intelligence Market Phase of the Overseer System.

This module provides the main service interface for the intelligence market,
integrating all market components and providing a unified API.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable

from .market_models import (
    Bid, BidMatch, Transaction, MarketMetrics, MarketStatus, ResourceType,
    AgentProfile, ResourceSpecification, PriceSpecification, TaskSpecification,
    AuctionConfig, MarketIntervention
)
from .market_analytics import MarketAnalytics
from .agent_market_stabilizer import AgentMarketStabilizer
from .a2a_bid_manager import A2ABidManager
from .auction_mechanisms import create_auction_mechanism

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("intelligence_market.intelligence_market_service")

class IntelligenceMarketService:
    """
    Main service interface for the intelligence market.
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
        Initialize the intelligence market service.
        
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
        
        # Initialize components
        self.market_analytics = MarketAnalytics(
            metrics_history_size=self.config.get("metrics_history_size", 100)
        )
        
        self.agent_market_stabilizer = AgentMarketStabilizer(
            market_analytics=self.market_analytics,
            config=self.config.get("market_stabilizer_config", {}),
            mcp_integration_manager=mcp_integration_manager,
            a2a_integration_manager=a2a_integration_manager,
            event_bus=event_bus
        )
        
        self.a2a_bid_manager = A2ABidManager(
            config=self.config.get("bid_manager_config", {}),
            mcp_integration_manager=mcp_integration_manager,
            a2a_integration_manager=a2a_integration_manager,
            event_bus=event_bus,
            data_access_service=data_access_service
        )
        
        # Initialize state
        self.active_agents: List[AgentProfile] = []
        self.market_status_history: List[Tuple[datetime, MarketStatus]] = []
        self.last_metrics_calculation = datetime.now()
        self.metrics_calculation_interval = self.config.get("metrics_calculation_interval", 300)  # seconds
        
        logger.info("IntelligenceMarketService initialized")
        
        # Register with event bus if available
        if self.event_bus:
            try:
                self.event_bus.subscribe(
                    topic="intelligence_market.#",
                    callback=self._handle_market_event
                )
                logger.info("Subscribed to intelligence market events")
            except Exception as e:
                logger.error("Failed to subscribe to events: %s", str(e))
    
    def start(self) -> bool:
        """
        Start the intelligence market service.
        
        Returns:
            bool: Success flag
        """
        try:
            logger.info("Starting Intelligence Market Service")
            
            # Load initial data if data access service is available
            if self.data_access_service:
                self._load_initial_data()
            
            # Calculate initial market metrics
            self._calculate_market_metrics()
            
            # Publish service status to event bus if available
            if self.event_bus:
                try:
                    self.event_bus.publish(
                        topic="intelligence_market.service.started",
                        message=json.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "service": "intelligence_market",
                            "status": "started"
                        })
                    )
                    logger.info("Published service start to event bus")
                except Exception as e:
                    logger.error("Failed to publish service start to event bus: %s", str(e))
            
            # Integrate with MCP if available
            if self.mcp_integration_manager:
                try:
                    context_update = {
                        "intelligence_market": {
                            "status": "active",
                            "started_at": datetime.now().isoformat()
                        }
                    }
                    self.mcp_integration_manager.update_context(context_update)
                    logger.info("Updated MCP context with service start")
                except Exception as e:
                    logger.error("Failed to update MCP context: %s", str(e))
            
            return True
        
        except Exception as e:
            logger.error("Failed to start Intelligence Market Service: %s", str(e))
            return False
    
    def stop(self) -> bool:
        """
        Stop the intelligence market service.
        
        Returns:
            bool: Success flag
        """
        try:
            logger.info("Stopping Intelligence Market Service")
            
            # Publish service status to event bus if available
            if self.event_bus:
                try:
                    self.event_bus.publish(
                        topic="intelligence_market.service.stopped",
                        message=json.dumps({
                            "timestamp": datetime.now().isoformat(),
                            "service": "intelligence_market",
                            "status": "stopped"
                        })
                    )
                    logger.info("Published service stop to event bus")
                except Exception as e:
                    logger.error("Failed to publish service stop to event bus: %s", str(e))
            
            # Integrate with MCP if available
            if self.mcp_integration_manager:
                try:
                    context_update = {
                        "intelligence_market": {
                            "status": "inactive",
                            "stopped_at": datetime.now().isoformat()
                        }
                    }
                    self.mcp_integration_manager.update_context(context_update)
                    logger.info("Updated MCP context with service stop")
                except Exception as e:
                    logger.error("Failed to update MCP context: %s", str(e))
            
            return True
        
        except Exception as e:
            logger.error("Failed to stop Intelligence Market Service: %s", str(e))
            return False
    
    def _load_initial_data(self) -> None:
        """Load initial data from the database."""
        try:
            # Load agent profiles
            agent_profiles = self.data_access_service.find_all(collection="agent_profiles")
            for profile_data in agent_profiles:
                profile = AgentProfile(**profile_data)
                self.active_agents.append(profile)
                self.a2a_bid_manager.register_agent_profile(profile)
            
            logger.info("Loaded %d agent profiles", len(self.active_agents))
            
            # Load active bids
            active_bids = self.data_access_service.find(
                collection="bids",
                query={"status": {"$in": ["pending", "active"]}}
            )
            
            for bid_data in active_bids:
                bid = Bid(**bid_data)
                self.a2a_bid_manager.bids[bid.bid_id] = bid
            
            logger.info("Loaded %d active bids", len(active_bids))
            
            # Load pending matches
            pending_matches = self.data_access_service.find(
                collection="matches",
                query={"status": "pending"}
            )
            
            for match_data in pending_matches:
                match = BidMatch(**match_data)
                self.a2a_bid_manager.matches[match.match_id] = match
            
            logger.info("Loaded %d pending matches", len(pending_matches))
            
            # Load recent transactions
            recent_transactions = self.data_access_service.find(
                collection="transactions",
                query={"created_at": {"$gte": (datetime.now() - timedelta(days=7)).isoformat()}}
            )
            
            for transaction_data in recent_transactions:
                transaction = Transaction(**transaction_data)
                self.a2a_bid_manager.transactions[transaction.transaction_id] = transaction
            
            logger.info("Loaded %d recent transactions", len(recent_transactions))
        
        except Exception as e:
            logger.error("Failed to load initial data: %s", str(e))
    
    def _calculate_market_metrics(self) -> Optional[MarketMetrics]:
        """
        Calculate current market metrics.
        
        Returns:
            Optional[MarketMetrics]: Calculated metrics or None if calculation failed
        """
        now = datetime.now()
        
        # Check if it's time to calculate metrics
        if (now - self.last_metrics_calculation).total_seconds() < self.metrics_calculation_interval:
            return None
        
        self.last_metrics_calculation = now
        
        try:
            # Get active bids
            active_bids = list(self.a2a_bid_manager.bids.values())
            
            # Get recent transactions
            recent_transactions = list(self.a2a_bid_manager.transactions.values())
            
            # Calculate metrics
            metrics = self.market_analytics.calculate_market_metrics(
                active_agents=self.active_agents,
                active_bids=active_bids,
                recent_transactions=recent_transactions
            )
            
            # Update market status history
            self.market_status_history.append((now, metrics.market_status))
            
            # Trim history if needed
            if len(self.market_status_history) > 100:
                self.market_status_history = self.market_status_history[-100:]
            
            # Monitor market stability
            monitoring_results = self.agent_market_stabilizer.monitor_market(metrics)
            
            # Implement stabilization measures if needed
            if monitoring_results["intervention_needed"]:
                interventions = self.agent_market_stabilizer.stabilize_market(
                    market_metrics=metrics,
                    monitoring_results=monitoring_results
                )
                
                if interventions:
                    logger.info("Implemented %d market interventions", len(interventions))
            
            # Check for expired bids
            expired_count = self.a2a_bid_manager.check_expired_bids()
            if expired_count > 0:
                logger.info("Expired %d bids", expired_count)
            
            # Publish metrics to event bus if available
            if self.event_bus:
                try:
                    self.event_bus.publish(
                        topic="intelligence_market.metrics",
                        message=json.dumps(metrics.dict())
                    )
                    logger.info("Published market metrics to event bus")
                except Exception as e:
                    logger.error("Failed to publish metrics to event bus: %s", str(e))
            
            # Integrate with MCP if available
            if self.mcp_integration_manager:
                try:
                    context_update = {
                        "market_metrics": metrics.dict()
                    }
                    self.mcp_integration_manager.update_context(context_update)
                    logger.info("Updated MCP context with market metrics")
                except Exception as e:
                    logger.error("Failed to update MCP context: %s", str(e))
            
            return metrics
        
        except Exception as e:
            logger.error("Failed to calculate market metrics: %s", str(e))
            return None
    
    def _handle_market_event(self, topic: str, message: str) -> None:
        """
        Handle market events from the event bus.
        
        Args:
            topic: Event topic
            message: Event message
        """
        try:
            # Parse message
            data = json.loads(message)
            
            # Handle different event types
            if topic == "intelligence_market.agent.registered":
                agent_id = data.get("agent_id")
                if agent_id:
                    # Load agent profile
                    if self.data_access_service:
                        profile_data = self.data_access_service.find_one(
                            collection="agent_profiles",
                            query={"agent_id": agent_id}
                        )
                        
                        if profile_data:
                            profile = AgentProfile(**profile_data)
                            self.active_agents.append(profile)
                            self.a2a_bid_manager.register_agent_profile(profile)
                            logger.info("Added agent profile for %s", agent_id)
            
            elif topic == "intelligence_market.agent.deregistered":
                agent_id = data.get("agent_id")
                if agent_id:
                    # Remove agent profile
                    self.active_agents = [a for a in self.active_agents if a.agent_id != agent_id]
                    if agent_id in self.a2a_bid_manager.agent_profiles:
                        del self.a2a_bid_manager.agent_profiles[agent_id]
                    logger.info("Removed agent profile for %s", agent_id)
            
            # Other event types can be handled as needed
        
        except Exception as e:
            logger.error("Failed to handle market event: %s", str(e))
    
    def get_market_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive market report.
        
        Returns:
            Dict[str, Any]: Market report
        """
        try:
            # Calculate latest metrics
            metrics = self._calculate_market_metrics()
            
            # Generate report
            report = self.market_analytics.generate_market_report()
            
            # Add bid manager status
            report["bid_manager_status"] = self.a2a_bid_manager.get_market_status()
            
            # Add active interventions
            report["active_interventions"] = [i.dict() for i in self.agent_market_stabilizer.active_interventions]
            
            return report
        
        except Exception as e:
            logger.error("Failed to generate market report: %s", str(e))
            return {
                "error": f"Failed to generate market report: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def create_bid(self, *args, **kwargs) -> Tuple[bool, Optional[str], Optional[Bid]]:
        """
        Create a new bid in the intelligence market.
        
        Returns:
            Tuple[bool, Optional[str], Optional[Bid]]: (success, error_message, created_bid)
        """
        return self.a2a_bid_manager.create_bid(*args, **kwargs)
    
    def confirm_match(self, *args, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Confirm a match by an agent.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        return self.a2a_bid_manager.confirm_match(*args, **kwargs)
    
    def cancel_bid(self, *args, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Cancel a bid.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        return self.a2a_bid_manager.cancel_bid(*args, **kwargs)
    
    def create_auction(self, *args, **kwargs) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Create a new auction.
        
        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (success, error_message, auction_id)
        """
        return self.a2a_bid_manager.create_auction(*args, **kwargs)
    
    def start_auction(self, *args, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        Start an auction.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        return self.a2a_bid_manager.start_auction(*args, **kwargs)
    
    def end_auction(self, *args, **kwargs) -> Tuple[bool, Optional[str]]:
        """
        End an auction.
        
        Returns:
            Tuple[bool, Optional[str]]: (success, error_message)
        """
        return self.a2a_bid_manager.end_auction(*args, **kwargs)
    
    def register_agent_profile(self, *args, **kwargs) -> bool:
        """
        Register an agent profile.
        
        Returns:
            bool: Success flag
        """
        return self.a2a_bid_manager.register_agent_profile(*args, **kwargs)
    
    def detect_market_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect anomalies in market metrics.
        
        Returns:
            List[Dict[str, Any]]: List of detected anomalies
        """
        return self.market_analytics.detect_anomalies()
    
    def predict_market_trends(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict market trends based on historical data.
        
        Args:
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dict[str, Any]: Predicted trends
        """
        return self.market_analytics.predict_market_trends(days_ahead=days_ahead)
    
    def evaluate_intervention_effectiveness(
        self,
        intervention: MarketIntervention,
        before_metrics: MarketMetrics,
        after_metrics: MarketMetrics
    ) -> Dict[str, Any]:
        """
        Evaluate the effectiveness of a market intervention.
        
        Args:
            intervention: The intervention to evaluate
            before_metrics: Market metrics before intervention
            after_metrics: Market metrics after intervention
            
        Returns:
            Dict[str, Any]: Evaluation results
        """
        return self.agent_market_stabilizer.evaluate_intervention_effectiveness(
            intervention=intervention,
            before_metrics=before_metrics,
            after_metrics=after_metrics
        )
