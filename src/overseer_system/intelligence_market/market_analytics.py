"""
Market Analytics Module for the Intelligence Market Phase of the Overseer System.

This module provides analytics capabilities for the intelligence market,
including market metrics calculation, trend analysis, and visualization.

Author: Manus AI
Date: May 25, 2025
"""

import logging
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable

import numpy as np
from scipy import stats

from .market_models import (
    Bid, BidMatch, Transaction, MarketMetrics, MarketStatus, ResourceType,
    AgentProfile, ResourceSpecification, PriceSpecification
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("intelligence_market.market_analytics")

class MarketAnalytics:
    """
    Provides analytics capabilities for the intelligence market.
    """
    
    def __init__(self, metrics_history_size: int = 100):
        """
        Initialize the market analytics.
        
        Args:
            metrics_history_size: Maximum number of historical metrics to keep
        """
        self.metrics_history: List[MarketMetrics] = []
        self.metrics_history_size = metrics_history_size
        logger.info("MarketAnalytics initialized with history size %d", metrics_history_size)
    
    def calculate_market_metrics(
        self,
        active_agents: List[AgentProfile],
        active_bids: List[Bid],
        recent_transactions: List[Transaction],
        time_window: timedelta = timedelta(hours=24)
    ) -> MarketMetrics:
        """
        Calculate current market metrics.
        
        Args:
            active_agents: List of active agents
            active_bids: List of active bids
            recent_transactions: List of recent transactions
            time_window: Time window for recent transactions
            
        Returns:
            MarketMetrics: Calculated market metrics
        """
        now = datetime.now()
        cutoff_time = now - time_window
        
        # Filter transactions within time window
        filtered_transactions = [
            t for t in recent_transactions 
            if t.created_at >= cutoff_time
        ]
        
        # Count active agents and bids
        num_active_agents = len(active_agents)
        num_active_bids = len([b for b in active_bids if b.status == "active"])
        
        # Count completed transactions
        num_completed_transactions = len(filtered_transactions)
        
        # Calculate total transaction value
        total_value = sum(t.price.amount for t in filtered_transactions)
        
        # Calculate average price by resource type
        avg_price_by_type = {}
        for resource_type in ResourceType:
            transactions_with_type = [
                t for t in filtered_transactions
                if any(r.resource_type == resource_type for r in t.resources)
            ]
            
            if transactions_with_type:
                avg_price = sum(t.price.amount for t in transactions_with_type) / len(transactions_with_type)
                avg_price_by_type[resource_type] = avg_price
        
        # Calculate price volatility by resource type
        volatility_by_type = {}
        for resource_type in ResourceType:
            transactions_with_type = [
                t for t in filtered_transactions
                if any(r.resource_type == resource_type for r in t.resources)
            ]
            
            if len(transactions_with_type) >= 2:
                prices = [t.price.amount for t in transactions_with_type]
                volatility = np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0
                volatility_by_type[resource_type] = volatility
        
        # Calculate supply/demand ratio by resource type
        supply_demand_ratio = {}
        for resource_type in ResourceType:
            supply_bids = [
                b for b in active_bids 
                if b.role == "seller" and b.status == "active" and
                any(r.resource_type == resource_type for r in b.resources)
            ]
            
            demand_bids = [
                b for b in active_bids 
                if b.role == "buyer" and b.status == "active" and
                any(r.resource_type == resource_type for r in b.resources)
            ]
            
            if demand_bids:
                ratio = len(supply_bids) / len(demand_bids)
                supply_demand_ratio[resource_type] = ratio
        
        # Calculate market concentration (Herfindahl-Hirschman Index)
        market_concentration = 0.0
        if filtered_transactions:
            agent_transaction_counts = {}
            for t in filtered_transactions:
                agent_transaction_counts[t.seller_id] = agent_transaction_counts.get(t.seller_id, 0) + 1
            
            total_transactions = len(filtered_transactions)
            if total_transactions > 0:
                market_concentration = sum((count / total_transactions) ** 2 for count in agent_transaction_counts.values())
        
        # Determine overall market status
        market_status = self._determine_market_status(
            avg_price_by_type, 
            volatility_by_type, 
            supply_demand_ratio,
            market_concentration
        )
        
        # Calculate resource utilization
        resource_utilization = {}
        for resource_type in ResourceType:
            # In a real implementation, this would calculate actual resource utilization
            # For this implementation, we'll use a placeholder calculation
            utilization = 0.5  # Placeholder value
            resource_utilization[resource_type] = utilization
        
        # Create market metrics
        metrics = MarketMetrics(
            timestamp=now,
            active_agents=num_active_agents,
            active_bids=num_active_bids,
            completed_transactions=num_completed_transactions,
            total_transaction_value=total_value,
            average_price=avg_price_by_type,
            price_volatility=volatility_by_type,
            supply_demand_ratio=supply_demand_ratio,
            market_concentration=market_concentration,
            market_status=market_status,
            resource_utilization=resource_utilization
        )
        
        # Add to history
        self._add_to_history(metrics)
        
        logger.info("Calculated market metrics: %s active agents, %s active bids, %s transactions, status: %s",
                   num_active_agents, num_active_bids, num_completed_transactions, market_status)
        
        return metrics
    
    def _determine_market_status(
        self,
        avg_price_by_type: Dict[ResourceType, float],
        volatility_by_type: Dict[ResourceType, float],
        supply_demand_ratio: Dict[ResourceType, float],
        market_concentration: float
    ) -> MarketStatus:
        """
        Determine the overall market status based on metrics.
        
        Args:
            avg_price_by_type: Average price by resource type
            volatility_by_type: Price volatility by resource type
            supply_demand_ratio: Supply/demand ratio by resource type
            market_concentration: Market concentration (HHI)
            
        Returns:
            MarketStatus: Determined market status
        """
        # Check if we have enough data
        if not avg_price_by_type or not volatility_by_type or not supply_demand_ratio:
            return MarketStatus.UNKNOWN
        
        # Check for high volatility
        avg_volatility = sum(volatility_by_type.values()) / len(volatility_by_type)
        if avg_volatility > 0.2:  # Threshold for high volatility
            return MarketStatus.VOLATILE
        
        # Check for market growth or shrinkage
        if self.metrics_history and len(self.metrics_history) >= 2:
            prev_metrics = self.metrics_history[-2]
            current_metrics = self.metrics_history[-1]
            
            # Compare transaction counts
            if current_metrics.completed_transactions > prev_metrics.completed_transactions * 1.2:
                return MarketStatus.GROWING
            elif current_metrics.completed_transactions < prev_metrics.completed_transactions * 0.8:
                return MarketStatus.SHRINKING
        
        # Check for market freeze
        if market_concentration > 0.8:  # Threshold for high concentration
            return MarketStatus.FROZEN
        
        # Check for recovery
        if self.metrics_history and len(self.metrics_history) >= 3:
            metrics_2_ago = self.metrics_history[-3]
            prev_metrics = self.metrics_history[-2]
            current_metrics = self.metrics_history[-1]
            
            if (metrics_2_ago.market_status in [MarketStatus.VOLATILE, MarketStatus.FROZEN, MarketStatus.SHRINKING] and
                prev_metrics.completed_transactions < metrics_2_ago.completed_transactions and
                current_metrics.completed_transactions > prev_metrics.completed_transactions):
                return MarketStatus.RECOVERING
        
        # Default to stable
        return MarketStatus.STABLE
    
    def _add_to_history(self, metrics: MarketMetrics) -> None:
        """
        Add metrics to history, maintaining maximum history size.
        
        Args:
            metrics: Market metrics to add
        """
        self.metrics_history.append(metrics)
        
        # Trim history if needed
        if len(self.metrics_history) > self.metrics_history_size:
            self.metrics_history = self.metrics_history[-self.metrics_history_size:]
    
    def detect_anomalies(self) -> List[Dict[str, Any]]:
        """
        Detect anomalies in market metrics.
        
        Returns:
            List[Dict[str, Any]]: List of detected anomalies
        """
        if len(self.metrics_history) < 10:
            logger.warning("Not enough history for anomaly detection")
            return []
        
        anomalies = []
        
        # Check for price anomalies
        for resource_type in ResourceType:
            prices = [
                m.average_price.get(resource_type, 0) 
                for m in self.metrics_history 
                if resource_type in m.average_price
            ]
            
            if len(prices) >= 10:
                # Calculate z-scores
                mean = np.mean(prices)
                std = np.std(prices)
                
                if std > 0:
                    z_scores = [(p - mean) / std for p in prices]
                    
                    # Check last 3 points for anomalies
                    for i in range(1, min(4, len(z_scores) + 1)):
                        z = z_scores[-i]
                        if abs(z) > 2.5:  # Threshold for anomaly
                            anomalies.append({
                                "type": "price_anomaly",
                                "resource_type": resource_type,
                                "timestamp": self.metrics_history[-i].timestamp,
                                "value": prices[-i],
                                "z_score": z,
                                "severity": "high" if abs(z) > 3.5 else "medium"
                            })
        
        # Check for transaction volume anomalies
        volumes = [m.completed_transactions for m in self.metrics_history]
        if len(volumes) >= 10:
            # Calculate z-scores
            mean = np.mean(volumes)
            std = np.std(volumes)
            
            if std > 0:
                z_scores = [(v - mean) / std for v in volumes]
                
                # Check last 3 points for anomalies
                for i in range(1, min(4, len(z_scores) + 1)):
                    z = z_scores[-i]
                    if abs(z) > 2.5:  # Threshold for anomaly
                        anomalies.append({
                            "type": "volume_anomaly",
                            "timestamp": self.metrics_history[-i].timestamp,
                            "value": volumes[-i],
                            "z_score": z,
                            "severity": "high" if abs(z) > 3.5 else "medium"
                        })
        
        # Check for market concentration anomalies
        concentrations = [m.market_concentration for m in self.metrics_history]
        if len(concentrations) >= 10:
            # Calculate z-scores
            mean = np.mean(concentrations)
            std = np.std(concentrations)
            
            if std > 0:
                z_scores = [(c - mean) / std for c in concentrations]
                
                # Check last 3 points for anomalies
                for i in range(1, min(4, len(z_scores) + 1)):
                    z = z_scores[-i]
                    if abs(z) > 2.5:  # Threshold for anomaly
                        anomalies.append({
                            "type": "concentration_anomaly",
                            "timestamp": self.metrics_history[-i].timestamp,
                            "value": concentrations[-i],
                            "z_score": z,
                            "severity": "high" if abs(z) > 3.5 else "medium"
                        })
        
        logger.info("Detected %d anomalies in market metrics", len(anomalies))
        return anomalies
    
    def predict_market_trends(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Predict market trends based on historical data.
        
        Args:
            days_ahead: Number of days to predict ahead
            
        Returns:
            Dict[str, Any]: Predicted trends
        """
        if len(self.metrics_history) < 14:
            logger.warning("Not enough history for trend prediction")
            return {}
        
        predictions = {}
        
        # Convert timestamps to days since first timestamp
        first_timestamp = self.metrics_history[0].timestamp
        days = [(m.timestamp - first_timestamp).total_seconds() / (24 * 3600) for m in self.metrics_history]
        
        # Predict transaction volume
        volumes = [m.completed_transactions for m in self.metrics_history]
        if len(volumes) >= 14:
            slope, intercept, r_value, p_value, std_err = stats.linregress(days, volumes)
            
            future_days = [days[-1] + i for i in range(1, days_ahead + 1)]
            predicted_volumes = [slope * d + intercept for d in future_days]
            
            predictions["transaction_volume"] = {
                "current": volumes[-1],
                "predicted": predicted_volumes,
                "trend": "increasing" if slope > 0 else "decreasing",
                "confidence": abs(r_value)
            }
        
        # Predict average prices for each resource type
        for resource_type in ResourceType:
            prices = [
                m.average_price.get(resource_type, 0) 
                for m in self.metrics_history 
                if resource_type in m.average_price
            ]
            
            if len(prices) >= 14:
                # Filter days to match available prices
                filtered_days = days[-len(prices):]
                
                slope, intercept, r_value, p_value, std_err = stats.linregress(filtered_days, prices)
                
                future_days = [filtered_days[-1] + i for i in range(1, days_ahead + 1)]
                predicted_prices = [slope * d + intercept for d in future_days]
                
                predictions[f"price_{resource_type}"] = {
                    "current": prices[-1],
                    "predicted": predicted_prices,
                    "trend": "increasing" if slope > 0 else "decreasing",
                    "confidence": abs(r_value)
                }
        
        # Predict market concentration
        concentrations = [m.market_concentration for m in self.metrics_history]
        if len(concentrations) >= 14:
            slope, intercept, r_value, p_value, std_err = stats.linregress(days, concentrations)
            
            future_days = [days[-1] + i for i in range(1, days_ahead + 1)]
            predicted_concentrations = [min(1.0, max(0.0, slope * d + intercept)) for d in future_days]
            
            predictions["market_concentration"] = {
                "current": concentrations[-1],
                "predicted": predicted_concentrations,
                "trend": "increasing" if slope > 0 else "decreasing",
                "confidence": abs(r_value)
            }
        
        logger.info("Predicted market trends for %d days ahead", days_ahead)
        return predictions
    
    def calculate_market_efficiency(self) -> float:
        """
        Calculate market efficiency based on price convergence and transaction volume.
        
        Returns:
            float: Market efficiency score (0.0 to 1.0)
        """
        if len(self.metrics_history) < 10:
            logger.warning("Not enough history for efficiency calculation")
            return 0.5  # Default to neutral
        
        # Calculate price convergence
        price_convergence_score = 0.0
        count = 0
        
        for resource_type in ResourceType:
            prices = [
                m.average_price.get(resource_type, 0) 
                for m in self.metrics_history[-10:] 
                if resource_type in m.average_price
            ]
            
            if len(prices) >= 5:
                # Calculate coefficient of variation (lower is more converged)
                mean = np.mean(prices)
                std = np.std(prices)
                
                if mean > 0:
                    cv = std / mean
                    # Convert to score (1.0 for perfect convergence, 0.0 for high variation)
                    score = max(0.0, min(1.0, 1.0 - cv))
                    price_convergence_score += score
                    count += 1
        
        if count > 0:
            price_convergence_score /= count
        else:
            price_convergence_score = 0.5  # Default to neutral
        
        # Calculate transaction volume efficiency
        volume_efficiency_score = 0.0
        volumes = [m.completed_transactions for m in self.metrics_history[-10:]]
        
        if volumes:
            # Calculate trend
            x = list(range(len(volumes)))
            slope, _, r_value, _, _ = stats.linregress(x, volumes)
            
            # Positive slope and high correlation indicate efficient market
            if slope > 0 and r_value > 0.7:
                volume_efficiency_score = 0.8
            elif slope > 0:
                volume_efficiency_score = 0.6
            elif slope < 0 and r_value > 0.7:
                volume_efficiency_score = 0.2
            elif slope < 0:
                volume_efficiency_score = 0.4
            else:
                volume_efficiency_score = 0.5
        
        # Calculate overall efficiency (weighted average)
        efficiency = 0.7 * price_convergence_score + 0.3 * volume_efficiency_score
        
        logger.info("Calculated market efficiency: %.2f", efficiency)
        return efficiency
    
    def generate_market_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive market report.
        
        Returns:
            Dict[str, Any]: Market report data
        """
        if not self.metrics_history:
            logger.warning("No metrics history for market report")
            return {}
        
        current_metrics = self.metrics_history[-1]
        
        # Calculate period-over-period changes
        changes = {}
        if len(self.metrics_history) >= 2:
            prev_metrics = self.metrics_history[-2]
            
            changes["active_agents"] = {
                "value": current_metrics.active_agents - prev_metrics.active_agents,
                "percent": (current_metrics.active_agents / prev_metrics.active_agents - 1) * 100 if prev_metrics.active_agents > 0 else 0
            }
            
            changes["active_bids"] = {
                "value": current_metrics.active_bids - prev_metrics.active_bids,
                "percent": (current_metrics.active_bids / prev_metrics.active_bids - 1) * 100 if prev_metrics.active_bids > 0 else 0
            }
            
            changes["completed_transactions"] = {
                "value": current_metrics.completed_transactions - prev_metrics.completed_transactions,
                "percent": (current_metrics.completed_transactions / prev_metrics.completed_transactions - 1) * 100 if prev_metrics.completed_transactions > 0 else 0
            }
            
            changes["total_transaction_value"] = {
                "value": current_metrics.total_transaction_value - prev_metrics.total_transaction_value,
                "percent": (current_metrics.total_transaction_value / prev_metrics.total_transaction_value - 1) * 100 if prev_metrics.total_transaction_value > 0 else 0
            }
        
        # Detect anomalies
        anomalies = self.detect_anomalies()
        
        # Predict trends
        trends = self.predict_market_trends()
        
        # Calculate efficiency
        efficiency = self.calculate_market_efficiency()
        
        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": current_metrics.dict(),
            "changes": changes,
            "anomalies": anomalies,
            "trends": trends,
            "efficiency": efficiency,
            "market_status": current_metrics.market_status,
            "recommendations": self._generate_recommendations(
                current_metrics, changes, anomalies, trends, efficiency
            )
        }
        
        logger.info("Generated market report")
        return report
    
    def _generate_recommendations(
        self,
        current_metrics: MarketMetrics,
        changes: Dict[str, Dict[str, float]],
        anomalies: List[Dict[str, Any]],
        trends: Dict[str, Any],
        efficiency: float
    ) -> List[Dict[str, Any]]:
        """
        Generate market recommendations based on analysis.
        
        Args:
            current_metrics: Current market metrics
            changes: Period-over-period changes
            anomalies: Detected anomalies
            trends: Predicted trends
            efficiency: Market efficiency score
            
        Returns:
            List[Dict[str, Any]]: List of recommendations
        """
        recommendations = []
        
        # Check market status
        if current_metrics.market_status == MarketStatus.VOLATILE:
            recommendations.append({
                "type": "market_stabilization",
                "priority": "high",
                "description": "Implement price stabilization measures to reduce volatility",
                "actions": [
                    "Introduce price floors and ceilings",
                    "Increase market maker participation",
                    "Temporarily limit large transactions"
                ]
            })
        
        elif current_metrics.market_status == MarketStatus.SHRINKING:
            recommendations.append({
                "type": "market_stimulation",
                "priority": "high",
                "description": "Stimulate market activity to reverse shrinking trend",
                "actions": [
                    "Reduce transaction fees",
                    "Introduce incentives for new participants",
                    "Expand resource types offered"
                ]
            })
        
        elif current_metrics.market_status == MarketStatus.FROZEN:
            recommendations.append({
                "type": "market_intervention",
                "priority": "critical",
                "description": "Intervene to unfreeze market activity",
                "actions": [
                    "Break up concentrated positions",
                    "Introduce emergency liquidity",
                    "Reset market parameters"
                ]
            })
        
        # Check efficiency
        if efficiency < 0.4:
            recommendations.append({
                "type": "efficiency_improvement",
                "priority": "medium",
                "description": "Improve market efficiency",
                "actions": [
                    "Enhance price discovery mechanisms",
                    "Reduce information asymmetry",
                    "Optimize matching algorithms"
                ]
            })
        
        # Check for high concentration
        if current_metrics.market_concentration > 0.6:
            recommendations.append({
                "type": "concentration_reduction",
                "priority": "medium",
                "description": "Reduce market concentration",
                "actions": [
                    "Encourage new market participants",
                    "Implement concentration limits",
                    "Provide incentives for smaller participants"
                ]
            })
        
        # Check for supply/demand imbalances
        for resource_type, ratio in current_metrics.supply_demand_ratio.items():
            if ratio > 2.0:
                recommendations.append({
                    "type": "demand_stimulation",
                    "priority": "medium",
                    "description": f"Stimulate demand for {resource_type}",
                    "actions": [
                        "Highlight use cases and benefits",
                        "Provide buyer incentives",
                        "Develop new applications"
                    ]
                })
            elif ratio < 0.5:
                recommendations.append({
                    "type": "supply_increase",
                    "priority": "medium",
                    "description": f"Increase supply of {resource_type}",
                    "actions": [
                        "Incentivize resource production",
                        "Attract new sellers",
                        "Optimize resource allocation"
                    ]
                })
        
        # Check for anomalies
        if any(a["severity"] == "high" for a in anomalies):
            recommendations.append({
                "type": "anomaly_investigation",
                "priority": "high",
                "description": "Investigate high-severity market anomalies",
                "actions": [
                    "Analyze transaction patterns",
                    "Review participant behavior",
                    "Implement additional monitoring"
                ]
            })
        
        return recommendations
