"""
Budget Monitor Agent for Industriverse Core AI Layer

This module implements the budget monitor agent for tracking latency SLAs,
token usage, and energy estimates in the Core AI Layer.
"""

import logging
import json
import asyncio
import time
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BudgetMonitorAgent:
    """
    Implements the budget monitor agent for Core AI Layer.
    Provides tracking for latency SLAs, token usage, and energy estimates.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the budget monitor agent.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or "config/budget_monitor.yaml"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.budget_registry = {}
        self.usage_registry = {}
        self.alerts = []
        self.last_rollup_time = time.time()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration.
        
        Returns:
            The configuration as a dictionary
        """
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def register_budget(self, entity_id: str, budget_type: str, budget_config: Dict[str, Any]) -> str:
        """
        Register a budget for an entity.
        
        Args:
            entity_id: ID of the entity (agent, task, etc.)
            budget_type: Type of budget (latency, token, energy)
            budget_config: Budget configuration
            
        Returns:
            Budget ID
        """
        budget_id = f"budget-{entity_id}-{budget_type}"
        
        # Create budget
        budget = {
            "budget_id": budget_id,
            "entity_id": entity_id,
            "budget_type": budget_type,
            "creation_timestamp": datetime.utcnow().isoformat(),
            "config": budget_config,
            "status": "active"
        }
        
        # Add to registry
        self.budget_registry[budget_id] = budget
        
        # Initialize usage
        self.usage_registry[budget_id] = {
            "budget_id": budget_id,
            "total_usage": 0,
            "current_period_usage": 0,
            "last_reset": datetime.utcnow().isoformat(),
            "usage_history": []
        }
        
        logger.info(f"Registered {budget_type} budget for {entity_id}")
        
        return budget_id
    
    async def record_usage(self, budget_id: str, usage_amount: float, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record usage against a budget.
        
        Args:
            budget_id: ID of the budget
            usage_amount: Amount of usage
            metadata: Additional metadata (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if budget_id not in self.budget_registry:
            logger.warning(f"Budget not found: {budget_id}")
            return False
            
        if budget_id not in self.usage_registry:
            logger.warning(f"Usage registry not found for budget: {budget_id}")
            return False
            
        budget = self.budget_registry[budget_id]
        usage = self.usage_registry[budget_id]
        
        # Record usage
        usage["total_usage"] += usage_amount
        usage["current_period_usage"] += usage_amount
        
        # Add to history
        usage["usage_history"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "amount": usage_amount,
            "metadata": metadata or {}
        })
        
        # Keep history size manageable
        max_history = self.config.get("max_usage_history", 1000)
        if len(usage["usage_history"]) > max_history:
            usage["usage_history"] = usage["usage_history"][-max_history:]
        
        # Check for budget alerts
        await self._check_budget_alerts(budget_id)
        
        logger.debug(f"Recorded {usage_amount} usage for budget {budget_id}")
        
        return True
    
    async def _check_budget_alerts(self, budget_id: str) -> None:
        """
        Check for budget alerts.
        
        Args:
            budget_id: ID of the budget
        """
        if budget_id not in self.budget_registry:
            return
            
        if budget_id not in self.usage_registry:
            return
            
        budget = self.budget_registry[budget_id]
        usage = self.usage_registry[budget_id]
        
        # Get budget limits
        budget_config = budget["config"]
        budget_type = budget["budget_type"]
        entity_id = budget["entity_id"]
        
        # Check for different budget types
        if budget_type == "latency":
            await self._check_latency_budget(budget_id, budget_config, usage)
        elif budget_type == "token":
            await self._check_token_budget(budget_id, budget_config, usage)
        elif budget_type == "energy":
            await self._check_energy_budget(budget_id, budget_config, usage)
    
    async def _check_latency_budget(self, budget_id: str, config: Dict[str, Any], usage: Dict[str, Any]) -> None:
        """
        Check latency budget.
        
        Args:
            budget_id: ID of the budget
            config: Budget configuration
            usage: Usage data
        """
        # Extract limits
        sla_ms = config.get("sla_ms")
        if not sla_ms:
            return
            
        # Calculate average latency from recent history
        recent_history = usage["usage_history"][-10:]
        if not recent_history:
            return
            
        avg_latency = sum(entry["amount"] for entry in recent_history) / len(recent_history)
        
        # Check if average latency exceeds SLA
        if avg_latency > sla_ms:
            # Create alert
            alert = {
                "alert_id": f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "budget_id": budget_id,
                "entity_id": self.budget_registry[budget_id]["entity_id"],
                "budget_type": "latency",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Latency SLA violation: {avg_latency:.2f}ms exceeds {sla_ms}ms SLA",
                "severity": "high" if avg_latency > sla_ms * 1.5 else "medium",
                "data": {
                    "avg_latency": avg_latency,
                    "sla_ms": sla_ms,
                    "violation_ratio": avg_latency / sla_ms
                }
            }
            
            self.alerts.append(alert)
            
            logger.warning(f"Latency SLA violation for {self.budget_registry[budget_id]['entity_id']}: {avg_latency:.2f}ms exceeds {sla_ms}ms SLA")
    
    async def _check_token_budget(self, budget_id: str, config: Dict[str, Any], usage: Dict[str, Any]) -> None:
        """
        Check token budget.
        
        Args:
            budget_id: ID of the budget
            config: Budget configuration
            usage: Usage data
        """
        # Extract limits
        period_limit = config.get("period_limit")
        total_limit = config.get("total_limit")
        
        if not period_limit and not total_limit:
            return
            
        # Check period limit
        if period_limit and usage["current_period_usage"] > period_limit:
            # Create alert
            alert = {
                "alert_id": f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "budget_id": budget_id,
                "entity_id": self.budget_registry[budget_id]["entity_id"],
                "budget_type": "token",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Token period budget exceeded: {usage['current_period_usage']} tokens exceeds {period_limit} token limit",
                "severity": "high" if usage["current_period_usage"] > period_limit * 1.2 else "medium",
                "data": {
                    "current_usage": usage["current_period_usage"],
                    "period_limit": period_limit,
                    "usage_ratio": usage["current_period_usage"] / period_limit
                }
            }
            
            self.alerts.append(alert)
            
            logger.warning(f"Token period budget exceeded for {self.budget_registry[budget_id]['entity_id']}: {usage['current_period_usage']} tokens exceeds {period_limit} token limit")
        
        # Check total limit
        if total_limit and usage["total_usage"] > total_limit:
            # Create alert
            alert = {
                "alert_id": f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "budget_id": budget_id,
                "entity_id": self.budget_registry[budget_id]["entity_id"],
                "budget_type": "token",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Token total budget exceeded: {usage['total_usage']} tokens exceeds {total_limit} token limit",
                "severity": "critical" if usage["total_usage"] > total_limit * 1.5 else "high",
                "data": {
                    "total_usage": usage["total_usage"],
                    "total_limit": total_limit,
                    "usage_ratio": usage["total_usage"] / total_limit
                }
            }
            
            self.alerts.append(alert)
            
            logger.warning(f"Token total budget exceeded for {self.budget_registry[budget_id]['entity_id']}: {usage['total_usage']} tokens exceeds {total_limit} token limit")
    
    async def _check_energy_budget(self, budget_id: str, config: Dict[str, Any], usage: Dict[str, Any]) -> None:
        """
        Check energy budget.
        
        Args:
            budget_id: ID of the budget
            config: Budget configuration
            usage: Usage data
        """
        # Extract limits
        daily_kwh_limit = config.get("daily_kwh_limit")
        monthly_kwh_limit = config.get("monthly_kwh_limit")
        
        if not daily_kwh_limit and not monthly_kwh_limit:
            return
            
        # Calculate daily and monthly usage
        now = datetime.utcnow()
        
        # Daily usage
        daily_usage = sum(
            entry["amount"] 
            for entry in usage["usage_history"] 
            if (now - datetime.fromisoformat(entry["timestamp"])).total_seconds() < 86400
        )
        
        # Monthly usage
        monthly_usage = sum(
            entry["amount"] 
            for entry in usage["usage_history"] 
            if (now - datetime.fromisoformat(entry["timestamp"])).total_seconds() < 2592000
        )
        
        # Check daily limit
        if daily_kwh_limit and daily_usage > daily_kwh_limit:
            # Create alert
            alert = {
                "alert_id": f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "budget_id": budget_id,
                "entity_id": self.budget_registry[budget_id]["entity_id"],
                "budget_type": "energy",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Daily energy budget exceeded: {daily_usage:.2f} kWh exceeds {daily_kwh_limit} kWh limit",
                "severity": "high" if daily_usage > daily_kwh_limit * 1.2 else "medium",
                "data": {
                    "daily_usage": daily_usage,
                    "daily_limit": daily_kwh_limit,
                    "usage_ratio": daily_usage / daily_kwh_limit
                }
            }
            
            self.alerts.append(alert)
            
            logger.warning(f"Daily energy budget exceeded for {self.budget_registry[budget_id]['entity_id']}: {daily_usage:.2f} kWh exceeds {daily_kwh_limit} kWh limit")
        
        # Check monthly limit
        if monthly_kwh_limit and monthly_usage > monthly_kwh_limit:
            # Create alert
            alert = {
                "alert_id": f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "budget_id": budget_id,
                "entity_id": self.budget_registry[budget_id]["entity_id"],
                "budget_type": "energy",
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Monthly energy budget exceeded: {monthly_usage:.2f} kWh exceeds {monthly_kwh_limit} kWh limit",
                "severity": "critical" if monthly_usage > monthly_kwh_limit * 1.5 else "high",
                "data": {
                    "monthly_usage": monthly_usage,
                    "monthly_limit": monthly_kwh_limit,
                    "usage_ratio": monthly_usage / monthly_kwh_limit
                }
            }
            
            self.alerts.append(alert)
            
            logger.warning(f"Monthly energy budget exceeded for {self.budget_registry[budget_id]['entity_id']}: {monthly_usage:.2f} kWh exceeds {monthly_kwh_limit} kWh limit")
    
    async def reset_period_usage(self, budget_id: str) -> bool:
        """
        Reset period usage for a budget.
        
        Args:
            budget_id: ID of the budget
            
        Returns:
            True if successful, False otherwise
        """
        if budget_id not in self.usage_registry:
            logger.warning(f"Usage registry not found for budget: {budget_id}")
            return False
            
        usage = self.usage_registry[budget_id]
        
        # Reset period usage
        usage["current_period_usage"] = 0
        usage["last_reset"] = datetime.utcnow().isoformat()
        
        logger.info(f"Reset period usage for budget {budget_id}")
        
        return True
    
    async def rollup_usage_metrics(self) -> Dict[str, Any]:
        """
        Roll up usage metrics across all budgets.
        
        Returns:
            Rollup metrics
        """
        now = time.time()
        
        # Calculate time since last rollup
        time_since_last_rollup = now - self.last_rollup_time
        self.last_rollup_time = now
        
        # Initialize rollup
        rollup = {
            "timestamp": datetime.utcnow().isoformat(),
            "time_since_last_rollup_seconds": time_since_last_rollup,
            "latency": {
                "total_budgets": 0,
                "sla_violations": 0,
                "avg_latency_ms": 0
            },
            "token": {
                "total_budgets": 0,
                "period_violations": 0,
                "total_violations": 0,
                "total_usage": 0
            },
            "energy": {
                "total_budgets": 0,
                "daily_violations": 0,
                "monthly_violations": 0,
                "total_usage_kwh": 0
            }
        }
        
        # Process each budget
        for budget_id, budget in self.budget_registry.items():
            budget_type = budget["budget_type"]
            
            if budget_id not in self.usage_registry:
                continue
                
            usage = self.usage_registry[budget_id]
            
            if budget_type == "latency":
                rollup["latency"]["total_budgets"] += 1
                
                # Check for SLA violations
                recent_alerts = [
                    alert for alert in self.alerts
                    if alert["budget_id"] == budget_id
                    and (datetime.utcnow() - datetime.fromisoformat(alert["timestamp"])).total_seconds() < time_since_last_rollup
                ]
                
                if recent_alerts:
                    rollup["latency"]["sla_violations"] += 1
                
                # Calculate average latency
                recent_history = usage["usage_history"][-10:]
                if recent_history:
                    avg_latency = sum(entry["amount"] for entry in recent_history) / len(recent_history)
                    rollup["latency"]["avg_latency_ms"] += avg_latency
            
            elif budget_type == "token":
                rollup["token"]["total_budgets"] += 1
                rollup["token"]["total_usage"] += usage["total_usage"]
                
                # Check for violations
                recent_alerts = [
                    alert for alert in self.alerts
                    if alert["budget_id"] == budget_id
                    and (datetime.utcnow() - datetime.fromisoformat(alert["timestamp"])).total_seconds() < time_since_last_rollup
                ]
                
                for alert in recent_alerts:
                    if "period" in alert["message"].lower():
                        rollup["token"]["period_violations"] += 1
                    elif "total" in alert["message"].lower():
                        rollup["token"]["total_violations"] += 1
            
            elif budget_type == "energy":
                rollup["energy"]["total_budgets"] += 1
                rollup["energy"]["total_usage_kwh"] += usage["total_usage"]
                
                # Check for violations
                recent_alerts = [
                    alert for alert in self.alerts
                    if alert["budget_id"] == budget_id
                    and (datetime.utcnow() - datetime.fromisoformat(alert["timestamp"])).total_seconds() < time_since_last_rollup
                ]
                
                for alert in recent_alerts:
                    if "daily" in alert["message"].lower():
                        rollup["energy"]["daily_violations"] += 1
                    elif "monthly" in alert["message"].lower():
                        rollup["energy"]["monthly_violations"] += 1
        
        # Calculate averages
        if rollup["latency"]["total_budgets"] > 0:
            rollup["latency"]["avg_latency_ms"] /= rollup["latency"]["total_budgets"]
        
        logger.info(f"Rolled up usage metrics: {len(self.budget_registry)} budgets processed")
        
        return rollup
    
    def get_budget(self, budget_id: str) -> Dict[str, Any]:
        """
        Get a budget.
        
        Args:
            budget_id: ID of the budget
            
        Returns:
            Budget data
        """
        if budget_id not in self.budget_registry:
            logger.warning(f"Budget not found: {budget_id}")
            return {}
            
        return self.budget_registry[budget_id]
    
    def get_usage(self, budget_id: str) -> Dict[str, Any]:
        """
        Get usage data for a budget.
        
        Args:
            budget_id: ID of the budget
            
        Returns:
            Usage data
        """
        if budget_id not in self.usage_registry:
            logger.warning(f"Usage registry not found for budget: {budget_id}")
            return {}
            
        return self.usage_registry[budget_id]
    
    def get_alerts(self, entity_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get alerts.
        
        Args:
            entity_id: Filter by entity ID (optional)
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts
        """
        if entity_id:
            filtered = [alert for alert in self.alerts if alert["entity_id"] == entity_id]
            return filtered[-limit:]
        else:
            return self.alerts[-limit:]
    
    def get_entity_budgets(self, entity_id: str) -> List[Dict[str, Any]]:
        """
        Get all budgets for an entity.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            List of budgets
        """
        return [budget for budget in self.budget_registry.values() if budget["entity_id"] == entity_id]


# Example usage
if __name__ == "__main__":
    async def main():
        # Create a budget monitor agent
        monitor = BudgetMonitorAgent()
        
        # Register some budgets
        latency_budget = await monitor.register_budget("llm-service", "latency", {
            "sla_ms": 200,
            "description": "Response time SLA for LLM service"
        })
        
        token_budget = await monitor.register_budget("llm-service", "token", {
            "period_limit": 1000000,
            "total_limit": 10000000,
            "period": "daily",
            "description": "Token usage budget for LLM service"
        })
        
        energy_budget = await monitor.register_budget("ml-training", "energy", {
            "daily_kwh_limit": 50,
            "monthly_kwh_limit": 1000,
            "description": "Energy usage budget for ML training"
        })
        
        # Record some usage
        await monitor.record_usage(latency_budget, 150, {
            "request_id": "req-1",
            "model": "gpt-4"
        })
        
        await monitor.record_usage(latency_budget, 250, {
            "request_id": "req-2",
            "model": "gpt-4"
        })
        
        await monitor.record_usage(token_budget, 5000, {
            "request_id": "req-1",
            "model": "gpt-4"
        })
        
        await monitor.record_usage(energy_budget, 5.2, {
            "job_id": "job-1",
            "model": "xgboost"
        })
        
        # Roll up metrics
        rollup = await monitor.rollup_usage_metrics()
        
        print(f"Rollup metrics: {rollup}")
        
        # Get alerts
        alerts = monitor.get_alerts()
        
        print(f"Alerts: {len(alerts)}")
        for alert in alerts:
            print(f"- {alert['message']}")
    
    asyncio.run(main())
