"""
Agent Market Stabilizer for the Intelligence Market Phase of the Overseer System.

This module provides market stabilization capabilities for the intelligence market,
including volatility monitoring, price stabilization, and market intervention.

Author: Manus AI
Date: May 25, 2025
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any, Union, Callable

from .market_models import (
    Bid, BidMatch, Transaction, MarketMetrics, MarketStatus, ResourceType,
    MarketIntervention, InterventionType, PriceSpecification, create_intervention
)
from .market_analytics import MarketAnalytics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("intelligence_market.agent_market_stabilizer")

class AgentMarketStabilizer:
    """
    Provides market stabilization capabilities for the intelligence market.
    """
    
    def __init__(
        self,
        market_analytics: MarketAnalytics,
        config: Dict[str, Any] = None,
        mcp_integration_manager=None,
        a2a_integration_manager=None,
        event_bus=None
    ):
        """
        Initialize the agent market stabilizer.
        
        Args:
            market_analytics: Market analytics instance
            config: Configuration parameters
            mcp_integration_manager: MCP integration manager
            a2a_integration_manager: A2A integration manager
            event_bus: Event bus instance
        """
        self.market_analytics = market_analytics
        self.config = config or {}
        self.mcp_integration_manager = mcp_integration_manager
        self.a2a_integration_manager = a2a_integration_manager
        self.event_bus = event_bus
        
        # Initialize stabilization parameters
        self.volatility_threshold = self.config.get("volatility_threshold", 0.15)
        self.concentration_threshold = self.config.get("concentration_threshold", 0.6)
        self.supply_demand_ratio_min = self.config.get("supply_demand_ratio_min", 0.5)
        self.supply_demand_ratio_max = self.config.get("supply_demand_ratio_max", 2.0)
        self.price_change_threshold = self.config.get("price_change_threshold", 0.2)
        self.intervention_cooldown = self.config.get("intervention_cooldown", 3600)  # seconds
        
        # Initialize state
        self.active_interventions: List[MarketIntervention] = []
        self.intervention_history: List[MarketIntervention] = []
        self.last_intervention_time: Dict[InterventionType, datetime] = {}
        self.market_status_history: List[Tuple[datetime, MarketStatus]] = []
        
        logger.info("AgentMarketStabilizer initialized with volatility threshold %.2f", self.volatility_threshold)
    
    def monitor_market(self, market_metrics: MarketMetrics) -> Dict[str, Any]:
        """
        Monitor market conditions and detect instability.
        
        Args:
            market_metrics: Current market metrics
            
        Returns:
            Dict[str, Any]: Monitoring results
        """
        # Update market status history
        self.market_status_history.append((datetime.now(), market_metrics.market_status))
        
        # Trim history if needed
        if len(self.market_status_history) > 100:
            self.market_status_history = self.market_status_history[-100:]
        
        # Check for market instability
        instability_factors = []
        
        # Check volatility
        avg_volatility = 0.0
        if market_metrics.price_volatility:
            avg_volatility = sum(market_metrics.price_volatility.values()) / len(market_metrics.price_volatility)
            if avg_volatility > self.volatility_threshold:
                instability_factors.append({
                    "factor": "high_volatility",
                    "value": avg_volatility,
                    "threshold": self.volatility_threshold,
                    "severity": "high" if avg_volatility > self.volatility_threshold * 1.5 else "medium"
                })
        
        # Check market concentration
        if market_metrics.market_concentration > self.concentration_threshold:
            instability_factors.append({
                "factor": "high_concentration",
                "value": market_metrics.market_concentration,
                "threshold": self.concentration_threshold,
                "severity": "high" if market_metrics.market_concentration > 0.8 else "medium"
            })
        
        # Check supply/demand imbalance
        for resource_type, ratio in market_metrics.supply_demand_ratio.items():
            if ratio < self.supply_demand_ratio_min:
                instability_factors.append({
                    "factor": "supply_shortage",
                    "resource_type": resource_type,
                    "value": ratio,
                    "threshold": self.supply_demand_ratio_min,
                    "severity": "high" if ratio < self.supply_demand_ratio_min * 0.5 else "medium"
                })
            elif ratio > self.supply_demand_ratio_max:
                instability_factors.append({
                    "factor": "demand_shortage",
                    "resource_type": resource_type,
                    "value": ratio,
                    "threshold": self.supply_demand_ratio_max,
                    "severity": "high" if ratio > self.supply_demand_ratio_max * 2 else "medium"
                })
        
        # Check price changes
        if len(self.market_analytics.metrics_history) >= 2:
            prev_metrics = self.market_analytics.metrics_history[-2]
            
            for resource_type, current_price in market_metrics.average_price.items():
                if resource_type in prev_metrics.average_price:
                    prev_price = prev_metrics.average_price[resource_type]
                    if prev_price > 0:
                        price_change = abs(current_price - prev_price) / prev_price
                        if price_change > self.price_change_threshold:
                            instability_factors.append({
                                "factor": "rapid_price_change",
                                "resource_type": resource_type,
                                "value": price_change,
                                "threshold": self.price_change_threshold,
                                "direction": "increase" if current_price > prev_price else "decrease",
                                "severity": "high" if price_change > self.price_change_threshold * 2 else "medium"
                            })
        
        # Check market status
        if market_metrics.market_status in [MarketStatus.VOLATILE, MarketStatus.FROZEN]:
            instability_factors.append({
                "factor": "unstable_market_status",
                "value": market_metrics.market_status,
                "severity": "high"
            })
        
        # Determine overall stability
        stability_score = self._calculate_stability_score(market_metrics, instability_factors)
        
        # Determine if intervention is needed
        intervention_needed = stability_score < 0.6 and instability_factors
        
        # Update active interventions
        self._update_active_interventions()
        
        # Prepare monitoring results
        monitoring_results = {
            "timestamp": datetime.now().isoformat(),
            "market_status": market_metrics.market_status,
            "stability_score": stability_score,
            "instability_factors": instability_factors,
            "intervention_needed": intervention_needed,
            "active_interventions": [i.dict() for i in self.active_interventions],
            "intervention_history": [i.dict() for i in self.intervention_history[-5:]]
        }
        
        # Publish monitoring results to event bus if available
        if self.event_bus:
            try:
                self.event_bus.publish(
                    topic="intelligence_market.stability_monitoring",
                    message=json.dumps(monitoring_results)
                )
                logger.info("Published stability monitoring results to event bus")
            except Exception as e:
                logger.error("Failed to publish to event bus: %s", str(e))
        
        # Integrate with MCP if available
        if self.mcp_integration_manager:
            try:
                context_update = {
                    "market_stability": {
                        "score": stability_score,
                        "status": market_metrics.market_status,
                        "factors": instability_factors
                    }
                }
                self.mcp_integration_manager.update_context(context_update)
                logger.info("Updated MCP context with market stability information")
            except Exception as e:
                logger.error("Failed to update MCP context: %s", str(e))
        
        # Integrate with A2A if available
        if self.a2a_integration_manager:
            try:
                if intervention_needed:
                    self.a2a_integration_manager.notify_agents(
                        agent_types=["market_regulator", "market_maker"],
                        message={
                            "type": "market_instability_alert",
                            "stability_score": stability_score,
                            "factors": instability_factors
                        }
                    )
                    logger.info("Notified agents about market instability via A2A")
            except Exception as e:
                logger.error("Failed to notify agents via A2A: %s", str(e))
        
        logger.info("Market monitoring completed with stability score %.2f", stability_score)
        return monitoring_results
    
    def _calculate_stability_score(
        self,
        market_metrics: MarketMetrics,
        instability_factors: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate market stability score.
        
        Args:
            market_metrics: Current market metrics
            instability_factors: Detected instability factors
            
        Returns:
            float: Stability score (0.0 to 1.0)
        """
        # Start with perfect stability
        score = 1.0
        
        # Deduct for each instability factor
        for factor in instability_factors:
            if factor["severity"] == "high":
                score -= 0.2
            else:  # medium
                score -= 0.1
        
        # Adjust based on market status
        if market_metrics.market_status == MarketStatus.STABLE:
            score += 0.1
        elif market_metrics.market_status == MarketStatus.VOLATILE:
            score -= 0.2
        elif market_metrics.market_status == MarketStatus.FROZEN:
            score -= 0.3
        
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        return score
    
    def _update_active_interventions(self) -> None:
        """Update the list of active interventions."""
        now = datetime.now()
        
        # Filter out expired interventions
        active_interventions = []
        for intervention in self.active_interventions:
            if intervention.duration and now > intervention.created_at + intervention.duration:
                # Intervention has expired
                intervention.status = "completed"
                self.intervention_history.append(intervention)
                logger.info("Intervention %s has expired", intervention.intervention_id)
            else:
                active_interventions.append(intervention)
        
        self.active_interventions = active_interventions
    
    def stabilize_market(
        self,
        market_metrics: MarketMetrics,
        monitoring_results: Dict[str, Any]
    ) -> List[MarketIntervention]:
        """
        Implement market stabilization measures based on monitoring results.
        
        Args:
            market_metrics: Current market metrics
            monitoring_results: Market monitoring results
            
        Returns:
            List[MarketIntervention]: Implemented interventions
        """
        # Check if intervention is needed
        if not monitoring_results["intervention_needed"]:
            logger.info("No market intervention needed")
            return []
        
        # Determine appropriate interventions
        interventions = []
        
        # Group instability factors by type
        volatility_factors = [f for f in monitoring_results["instability_factors"] if f["factor"] == "high_volatility" or f["factor"] == "rapid_price_change"]
        concentration_factors = [f for f in monitoring_results["instability_factors"] if f["factor"] == "high_concentration"]
        supply_shortage_factors = [f for f in monitoring_results["instability_factors"] if f["factor"] == "supply_shortage"]
        demand_shortage_factors = [f for f in monitoring_results["instability_factors"] if f["factor"] == "demand_shortage"]
        
        # Handle high volatility
        if volatility_factors and self._check_intervention_cooldown(InterventionType.PRICE_CEILING):
            # Implement price ceiling
            affected_resources = []
            for factor in volatility_factors:
                if factor.get("resource_type"):
                    affected_resources.append(ResourceType(factor["resource_type"]))
            
            if not affected_resources:
                affected_resources = list(market_metrics.average_price.keys())
            
            intervention = create_intervention(
                intervention_type=InterventionType.PRICE_CEILING,
                target_resources=affected_resources,
                reason="High price volatility detected",
                parameters={
                    "ceiling_multiplier": 1.2,  # 20% above current average
                    "affected_resources": [r.value for r in affected_resources]
                },
                expected_impact={
                    "volatility_reduction": "high",
                    "price_stability": "improved",
                    "market_efficiency": "temporary_decrease"
                },
                duration_hours=24
            )
            
            interventions.append(intervention)
            self.active_interventions.append(intervention)
            self.last_intervention_time[InterventionType.PRICE_CEILING] = datetime.now()
            
            logger.info("Implemented price ceiling intervention %s for %d resources",
                       intervention.intervention_id, len(affected_resources))
        
        # Handle high concentration
        if concentration_factors and self._check_intervention_cooldown(InterventionType.PARTICIPANT_RESTRICTION):
            # Implement participant restrictions
            intervention = create_intervention(
                intervention_type=InterventionType.PARTICIPANT_RESTRICTION,
                target_resources=[],  # Applies to all resources
                reason="High market concentration detected",
                parameters={
                    "max_market_share": 0.3,  # No participant can control more than 30%
                    "restriction_type": "soft_limit"  # Soft limit with warnings
                },
                expected_impact={
                    "concentration_reduction": "medium",
                    "market_fairness": "improved",
                    "participation_diversity": "increased"
                },
                duration_hours=72
            )
            
            interventions.append(intervention)
            self.active_interventions.append(intervention)
            self.last_intervention_time[InterventionType.PARTICIPANT_RESTRICTION] = datetime.now()
            
            logger.info("Implemented participant restriction intervention %s",
                       intervention.intervention_id)
        
        # Handle supply shortage
        if supply_shortage_factors and self._check_intervention_cooldown(InterventionType.SUPPLY_INCREASE):
            # Implement supply increase
            affected_resources = [ResourceType(f["resource_type"]) for f in supply_shortage_factors if f.get("resource_type")]
            
            intervention = create_intervention(
                intervention_type=InterventionType.SUPPLY_INCREASE,
                target_resources=affected_resources,
                reason="Supply shortage detected",
                parameters={
                    "incentive_multiplier": 1.15,  # 15% incentive
                    "affected_resources": [r.value for r in affected_resources]
                },
                expected_impact={
                    "supply_increase": "medium",
                    "price_stability": "improved",
                    "market_balance": "improved"
                },
                duration_hours=48
            )
            
            interventions.append(intervention)
            self.active_interventions.append(intervention)
            self.last_intervention_time[InterventionType.SUPPLY_INCREASE] = datetime.now()
            
            logger.info("Implemented supply increase intervention %s for %d resources",
                       intervention.intervention_id, len(affected_resources))
        
        # Handle demand shortage
        if demand_shortage_factors and self._check_intervention_cooldown(InterventionType.DEMAND_STIMULATION):
            # Implement demand stimulation
            affected_resources = [ResourceType(f["resource_type"]) for f in demand_shortage_factors if f.get("resource_type")]
            
            intervention = create_intervention(
                intervention_type=InterventionType.DEMAND_STIMULATION,
                target_resources=affected_resources,
                reason="Demand shortage detected",
                parameters={
                    "discount_rate": 0.1,  # 10% discount
                    "affected_resources": [r.value for r in affected_resources]
                },
                expected_impact={
                    "demand_increase": "medium",
                    "price_stability": "improved",
                    "market_balance": "improved"
                },
                duration_hours=48
            )
            
            interventions.append(intervention)
            self.active_interventions.append(intervention)
            self.last_intervention_time[InterventionType.DEMAND_STIMULATION] = datetime.now()
            
            logger.info("Implemented demand stimulation intervention %s for %d resources",
                       intervention.intervention_id, len(affected_resources))
        
        # In extreme cases, consider market pause
        if monitoring_results["stability_score"] < 0.3 and self._check_intervention_cooldown(InterventionType.MARKET_PAUSE):
            # Implement market pause
            intervention = create_intervention(
                intervention_type=InterventionType.MARKET_PAUSE,
                target_resources=[],  # Applies to all resources
                reason="Critical market instability detected",
                parameters={
                    "pause_type": "soft_pause",  # Allow existing transactions to complete
                    "notification_message": "Market temporarily paused due to extreme instability"
                },
                expected_impact={
                    "volatility_reduction": "immediate",
                    "market_reset": "complete",
                    "participant_confidence": "preserved"
                },
                duration_hours=6
            )
            
            interventions.append(intervention)
            self.active_interventions.append(intervention)
            self.last_intervention_time[InterventionType.MARKET_PAUSE] = datetime.now()
            
            logger.info("Implemented market pause intervention %s due to critical instability",
                       intervention.intervention_id)
        
        # Publish interventions to event bus if available
        if self.event_bus and interventions:
            try:
                self.event_bus.publish(
                    topic="intelligence_market.interventions",
                    message=json.dumps([i.dict() for i in interventions])
                )
                logger.info("Published %d interventions to event bus", len(interventions))
            except Exception as e:
                logger.error("Failed to publish interventions to event bus: %s", str(e))
        
        # Integrate with MCP if available
        if self.mcp_integration_manager and interventions:
            try:
                context_update = {
                    "market_interventions": [i.dict() for i in interventions]
                }
                self.mcp_integration_manager.update_context(context_update)
                logger.info("Updated MCP context with market interventions")
            except Exception as e:
                logger.error("Failed to update MCP context: %s", str(e))
        
        # Integrate with A2A if available
        if self.a2a_integration_manager and interventions:
            try:
                self.a2a_integration_manager.notify_agents(
                    agent_types=["market_participant", "market_regulator"],
                    message={
                        "type": "market_intervention_notification",
                        "interventions": [i.dict() for i in interventions]
                    }
                )
                logger.info("Notified agents about market interventions via A2A")
            except Exception as e:
                logger.error("Failed to notify agents via A2A: %s", str(e))
        
        return interventions
    
    def _check_intervention_cooldown(self, intervention_type: InterventionType) -> bool:
        """
        Check if an intervention type is on cooldown.
        
        Args:
            intervention_type: Type of intervention to check
            
        Returns:
            bool: True if intervention is not on cooldown, False otherwise
        """
        if intervention_type not in self.last_intervention_time:
            return True
        
        elapsed_seconds = (datetime.now() - self.last_intervention_time[intervention_type]).total_seconds()
        return elapsed_seconds >= self.intervention_cooldown
    
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
        # Calculate changes in key metrics
        changes = {}
        
        # Volatility change
        before_volatility = 0.0
        after_volatility = 0.0
        
        if before_metrics.price_volatility:
            before_volatility = sum(before_metrics.price_volatility.values()) / len(before_metrics.price_volatility)
        
        if after_metrics.price_volatility:
            after_volatility = sum(after_metrics.price_volatility.values()) / len(after_metrics.price_volatility)
        
        volatility_change = after_volatility - before_volatility
        volatility_percent_change = (volatility_change / before_volatility) * 100 if before_volatility > 0 else 0
        
        changes["volatility"] = {
            "before": before_volatility,
            "after": after_volatility,
            "absolute_change": volatility_change,
            "percent_change": volatility_percent_change,
            "improved": volatility_change < 0
        }
        
        # Market concentration change
        concentration_change = after_metrics.market_concentration - before_metrics.market_concentration
        concentration_percent_change = (concentration_change / before_metrics.market_concentration) * 100 if before_metrics.market_concentration > 0 else 0
        
        changes["concentration"] = {
            "before": before_metrics.market_concentration,
            "after": after_metrics.market_concentration,
            "absolute_change": concentration_change,
            "percent_change": concentration_percent_change,
            "improved": concentration_change < 0
        }
        
        # Transaction volume change
        volume_change = after_metrics.completed_transactions - before_metrics.completed_transactions
        volume_percent_change = (volume_change / before_metrics.completed_transactions) * 100 if before_metrics.completed_transactions > 0 else 0
        
        changes["transaction_volume"] = {
            "before": before_metrics.completed_transactions,
            "after": after_metrics.completed_transactions,
            "absolute_change": volume_change,
            "percent_change": volume_percent_change,
            "improved": volume_change > 0
        }
        
        # Supply/demand ratio changes
        ratio_changes = {}
        for resource_type in set(before_metrics.supply_demand_ratio.keys()) | set(after_metrics.supply_demand_ratio.keys()):
            before_ratio = before_metrics.supply_demand_ratio.get(resource_type, 1.0)
            after_ratio = after_metrics.supply_demand_ratio.get(resource_type, 1.0)
            
            ratio_change = after_ratio - before_ratio
            ratio_percent_change = (ratio_change / before_ratio) * 100 if before_ratio > 0 else 0
            
            # Improvement means getting closer to 1.0 (perfect balance)
            before_distance = abs(before_ratio - 1.0)
            after_distance = abs(after_ratio - 1.0)
            improved = after_distance < before_distance
            
            ratio_changes[resource_type] = {
                "before": before_ratio,
                "after": after_ratio,
                "absolute_change": ratio_change,
                "percent_change": ratio_percent_change,
                "improved": improved
            }
        
        changes["supply_demand_ratio"] = ratio_changes
        
        # Market status change
        status_improved = False
        if before_metrics.market_status in [MarketStatus.VOLATILE, MarketStatus.FROZEN, MarketStatus.SHRINKING]:
            status_improved = after_metrics.market_status in [MarketStatus.STABLE, MarketStatus.GROWING, MarketStatus.RECOVERING]
        
        changes["market_status"] = {
            "before": before_metrics.market_status,
            "after": after_metrics.market_status,
            "improved": status_improved
        }
        
        # Calculate overall effectiveness score
        effectiveness_score = self._calculate_effectiveness_score(intervention, changes)
        
        # Update intervention with actual impact
        intervention.actual_impact = {
            "effectiveness_score": effectiveness_score,
            "volatility_change": volatility_percent_change,
            "concentration_change": concentration_percent_change,
            "volume_change": volume_percent_change,
            "status_improved": status_improved
        }
        
        # Prepare evaluation results
        evaluation_results = {
            "intervention_id": intervention.intervention_id,
            "intervention_type": intervention.intervention_type,
            "created_at": intervention.created_at.isoformat(),
            "duration": str(intervention.duration) if intervention.duration else None,
            "changes": changes,
            "effectiveness_score": effectiveness_score,
            "recommendations": self._generate_intervention_recommendations(intervention, changes, effectiveness_score)
        }
        
        logger.info("Evaluated intervention %s with effectiveness score %.2f",
                   intervention.intervention_id, effectiveness_score)
        
        return evaluation_results
    
    def _calculate_effectiveness_score(
        self,
        intervention: MarketIntervention,
        changes: Dict[str, Any]
    ) -> float:
        """
        Calculate intervention effectiveness score.
        
        Args:
            intervention: The intervention
            changes: Metric changes
            
        Returns:
            float: Effectiveness score (0.0 to 1.0)
        """
        score = 0.5  # Start neutral
        
        # Adjust based on volatility change
        if changes["volatility"]["improved"]:
            score += 0.1
            if abs(changes["volatility"]["percent_change"]) > 20:
                score += 0.1
        else:
            score -= 0.1
        
        # Adjust based on concentration change
        if changes["concentration"]["improved"]:
            score += 0.1
            if abs(changes["concentration"]["percent_change"]) > 10:
                score += 0.1
        else:
            score -= 0.1
        
        # Adjust based on transaction volume change
        if changes["transaction_volume"]["improved"]:
            score += 0.1
            if abs(changes["transaction_volume"]["percent_change"]) > 15:
                score += 0.1
        else:
            score -= 0.1
        
        # Adjust based on market status change
        if changes["market_status"]["improved"]:
            score += 0.2
        
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        return score
    
    def _generate_intervention_recommendations(
        self,
        intervention: MarketIntervention,
        changes: Dict[str, Any],
        effectiveness_score: float
    ) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on intervention evaluation.
        
        Args:
            intervention: The intervention
            changes: Metric changes
            effectiveness_score: Effectiveness score
            
        Returns:
            List[Dict[str, Any]]: List of recommendations
        """
        recommendations = []
        
        if effectiveness_score < 0.4:
            # Intervention was not effective
            recommendations.append({
                "type": "intervention_adjustment",
                "priority": "high",
                "description": f"Adjust parameters for {intervention.intervention_type} interventions",
                "actions": [
                    "Increase intervention strength",
                    "Extend intervention duration",
                    "Consider alternative intervention types"
                ]
            })
        
        elif effectiveness_score > 0.7:
            # Intervention was very effective
            recommendations.append({
                "type": "intervention_standardization",
                "priority": "medium",
                "description": f"Standardize {intervention.intervention_type} intervention parameters",
                "actions": [
                    "Document effective parameters",
                    "Create intervention template",
                    "Consider automated triggering"
                ]
            })
        
        # Check for specific metric improvements
        if not changes["volatility"]["improved"]:
            recommendations.append({
                "type": "volatility_management",
                "priority": "medium",
                "description": "Improve volatility management approach",
                "actions": [
                    "Implement more aggressive price controls",
                    "Increase market maker participation",
                    "Enhance early warning system"
                ]
            })
        
        if not changes["concentration"]["improved"]:
            recommendations.append({
                "type": "concentration_management",
                "priority": "medium",
                "description": "Improve concentration management approach",
                "actions": [
                    "Strengthen participant restrictions",
                    "Incentivize new market entrants",
                    "Implement progressive fee structure"
                ]
            })
        
        return recommendations
