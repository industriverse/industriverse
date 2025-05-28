"""
Model Health Prediction Agent for Industriverse Core AI Layer

This module implements the model health prediction agent for proactive maintenance
and early warning of potential model degradation.
"""

import logging
import json
import asyncio
import numpy as np
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelHealthPredictionAgent:
    """
    Implements the model health prediction agent for Core AI Layer.
    Provides proactive maintenance and early warning of potential model degradation.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the model health prediction agent.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or "config/model_health_prediction.yaml"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.model_registry = {}
        self.health_metrics = {}
        self.predictions = {}
        self.alerts = []
    
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
    
    async def register_model(self, model_id: str, model_type: str, model_metadata: Dict[str, Any]) -> bool:
        """
        Register a model for health monitoring.
        
        Args:
            model_id: ID of the model
            model_type: Type of model (llm, ml, etc.)
            model_metadata: Model metadata
            
        Returns:
            True if successful, False otherwise
        """
        # Create model entry
        model = {
            "model_id": model_id,
            "model_type": model_type,
            "registration_timestamp": datetime.utcnow().isoformat(),
            "metadata": model_metadata,
            "status": "active",
            "health_score": 1.0,
            "last_updated": datetime.utcnow().isoformat()
        }
        
        # Add to registry
        self.model_registry[model_id] = model
        
        # Initialize health metrics
        self.health_metrics[model_id] = {
            "accuracy": [],
            "latency": [],
            "error_rate": [],
            "drift_score": [],
            "resource_usage": [],
            "timestamp": []
        }
        
        logger.info(f"Registered model {model_id} of type {model_type}")
        
        return True
    
    async def record_health_metrics(self, model_id: str, metrics: Dict[str, Any]) -> bool:
        """
        Record health metrics for a model.
        
        Args:
            model_id: ID of the model
            metrics: Health metrics
            
        Returns:
            True if successful, False otherwise
        """
        if model_id not in self.model_registry:
            logger.warning(f"Model not found: {model_id}")
            return False
            
        if model_id not in self.health_metrics:
            logger.warning(f"Health metrics not found for model: {model_id}")
            return False
            
        # Update model last updated timestamp
        self.model_registry[model_id]["last_updated"] = datetime.utcnow().isoformat()
        
        # Record metrics
        health_metrics = self.health_metrics[model_id]
        timestamp = datetime.utcnow().isoformat()
        
        # Record each metric if provided
        for metric_name in ["accuracy", "latency", "error_rate", "drift_score", "resource_usage"]:
            if metric_name in metrics:
                health_metrics[metric_name].append(metrics[metric_name])
                
                # Keep history size manageable
                max_history = self.config.get("max_metric_history", 1000)
                if len(health_metrics[metric_name]) > max_history:
                    health_metrics[metric_name] = health_metrics[metric_name][-max_history:]
        
        # Record timestamp
        health_metrics["timestamp"].append(timestamp)
        if len(health_metrics["timestamp"]) > self.config.get("max_metric_history", 1000):
            health_metrics["timestamp"] = health_metrics["timestamp"][-self.config.get("max_metric_history", 1000):]
        
        logger.debug(f"Recorded health metrics for model {model_id}")
        
        # Update health score
        await self._update_health_score(model_id)
        
        # Predict future health
        await self._predict_future_health(model_id)
        
        return True
    
    async def _update_health_score(self, model_id: str) -> None:
        """
        Update health score for a model.
        
        Args:
            model_id: ID of the model
        """
        if model_id not in self.model_registry:
            return
            
        if model_id not in self.health_metrics:
            return
            
        model = self.model_registry[model_id]
        health_metrics = self.health_metrics[model_id]
        
        # Calculate health score based on recent metrics
        score_components = []
        
        # Accuracy (higher is better)
        if health_metrics["accuracy"]:
            recent_accuracy = health_metrics["accuracy"][-min(10, len(health_metrics["accuracy"])):]
            if recent_accuracy:
                accuracy_score = sum(recent_accuracy) / len(recent_accuracy)
                score_components.append(accuracy_score)
        
        # Latency (lower is better)
        if health_metrics["latency"]:
            recent_latency = health_metrics["latency"][-min(10, len(health_metrics["latency"])):]
            if recent_latency:
                # Normalize latency to 0-1 range (0 is worst, 1 is best)
                max_acceptable_latency = self.config.get("max_acceptable_latency", {}).get(model["model_type"], 1000)
                latency_score = 1.0 - min(1.0, sum(recent_latency) / len(recent_latency) / max_acceptable_latency)
                score_components.append(latency_score)
        
        # Error rate (lower is better)
        if health_metrics["error_rate"]:
            recent_error_rate = health_metrics["error_rate"][-min(10, len(health_metrics["error_rate"])):]
            if recent_error_rate:
                # Normalize error rate to 0-1 range (0 is worst, 1 is best)
                error_score = 1.0 - min(1.0, sum(recent_error_rate) / len(recent_error_rate))
                score_components.append(error_score)
        
        # Drift score (lower is better)
        if health_metrics["drift_score"]:
            recent_drift = health_metrics["drift_score"][-min(10, len(health_metrics["drift_score"])):]
            if recent_drift:
                # Normalize drift to 0-1 range (0 is worst, 1 is best)
                max_acceptable_drift = self.config.get("max_acceptable_drift", 1.0)
                drift_score = 1.0 - min(1.0, sum(recent_drift) / len(recent_drift) / max_acceptable_drift)
                score_components.append(drift_score)
        
        # Calculate overall health score
        if score_components:
            health_score = sum(score_components) / len(score_components)
            
            # Update model health score
            self.model_registry[model_id]["health_score"] = health_score
            
            logger.debug(f"Updated health score for model {model_id}: {health_score:.2f}")
            
            # Check for health alerts
            await self._check_health_alerts(model_id, health_score)
    
    async def _check_health_alerts(self, model_id: str, health_score: float) -> None:
        """
        Check for health alerts.
        
        Args:
            model_id: ID of the model
            health_score: Current health score
        """
        if model_id not in self.model_registry:
            return
            
        model = self.model_registry[model_id]
        
        # Get alert thresholds
        warning_threshold = self.config.get("health_score_warning_threshold", 0.7)
        critical_threshold = self.config.get("health_score_critical_threshold", 0.5)
        
        # Check for alerts
        if health_score < critical_threshold:
            # Create critical alert
            alert = {
                "alert_id": f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "model_id": model_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Critical health score: {health_score:.2f} is below threshold {critical_threshold}",
                "severity": "critical",
                "data": {
                    "health_score": health_score,
                    "threshold": critical_threshold
                }
            }
            
            self.alerts.append(alert)
            
            logger.warning(f"Critical health score for model {model_id}: {health_score:.2f}")
            
        elif health_score < warning_threshold:
            # Create warning alert
            alert = {
                "alert_id": f"alert-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                "model_id": model_id,
                "timestamp": datetime.utcnow().isoformat(),
                "message": f"Warning health score: {health_score:.2f} is below threshold {warning_threshold}",
                "severity": "warning",
                "data": {
                    "health_score": health_score,
                    "threshold": warning_threshold
                }
            }
            
            self.alerts.append(alert)
            
            logger.warning(f"Warning health score for model {model_id}: {health_score:.2f}")
    
    async def _predict_future_health(self, model_id: str) -> None:
        """
        Predict future health for a model.
        
        Args:
            model_id: ID of the model
        """
        if model_id not in self.model_registry:
            return
            
        if model_id not in self.health_metrics:
            return
            
        health_metrics = self.health_metrics[model_id]
        
        # Check if we have enough data for prediction
        min_data_points = self.config.get("min_data_points_for_prediction", 10)
        
        if len(health_metrics["timestamp"]) < min_data_points:
            logger.debug(f"Not enough data for health prediction for model {model_id}")
            return
        
        try:
            # Predict future health score
            prediction_days = [1, 7, 30]  # Predict for 1 day, 7 days, and 30 days
            predictions = {}
            
            # Convert timestamps to datetime objects
            timestamps = [datetime.fromisoformat(ts) for ts in health_metrics["timestamp"]]
            
            # Calculate days since first timestamp
            days_since_start = [(ts - timestamps[0]).total_seconds() / 86400 for ts in timestamps]
            
            # Predict for each metric
            for metric_name in ["accuracy", "latency", "error_rate", "drift_score"]:
                if not health_metrics[metric_name]:
                    continue
                    
                # Fit linear regression
                x = np.array(days_since_start).reshape(-1, 1)
                y = np.array(health_metrics[metric_name])
                
                from sklearn.linear_model import LinearRegression
                model = LinearRegression()
                model.fit(x, y)
                
                # Predict for future days
                future_predictions = {}
                
                for days in prediction_days:
                    future_day = days_since_start[-1] + days
                    prediction = model.predict([[future_day]])[0]
                    
                    # Ensure prediction is within reasonable bounds
                    if metric_name == "accuracy":
                        prediction = max(0.0, min(1.0, prediction))
                    elif metric_name in ["latency", "error_rate", "drift_score"]:
                        prediction = max(0.0, prediction)
                    
                    future_predictions[f"{days}_day"] = prediction
                
                predictions[metric_name] = future_predictions
            
            # Calculate predicted health scores
            health_predictions = {}
            
            for days in prediction_days:
                day_key = f"{days}_day"
                score_components = []
                
                # Accuracy (higher is better)
                if "accuracy" in predictions:
                    score_components.append(predictions["accuracy"][day_key])
                
                # Latency (lower is better)
                if "latency" in predictions:
                    max_acceptable_latency = self.config.get("max_acceptable_latency", {}).get(
                        self.model_registry[model_id]["model_type"], 1000)
                    latency_score = 1.0 - min(1.0, predictions["latency"][day_key] / max_acceptable_latency)
                    score_components.append(latency_score)
                
                # Error rate (lower is better)
                if "error_rate" in predictions:
                    error_score = 1.0 - min(1.0, predictions["error_rate"][day_key])
                    score_components.append(error_score)
                
                # Drift score (lower is better)
                if "drift_score" in predictions:
                    max_acceptable_drift = self.config.get("max_acceptable_drift", 1.0)
                    drift_score = 1.0 - min(1.0, predictions["drift_score"][day_key] / max_acceptable_drift)
                    score_components.append(drift_score)
                
                # Calculate overall health score
                if score_components:
                    health_score = sum(score_components) / len(score_components)
                    health_predictions[day_key] = health_score
            
            # Store predictions
            self.predictions[model_id] = {
                "timestamp": datetime.utcnow().isoformat(),
                "metrics": predictions,
                "health_score": health_predictions
            }
            
            logger.info(f"Generated health predictions for model {model_id}")
            
            # Check for prediction alerts
            await self._check_prediction_alerts(model_id, health_predictions)
            
        except Exception as e:
            logger.error(f"Error predicting future health for model {model_id}: {e}")
    
    async def _check_prediction_alerts(self, model_id: str, health_predictions: Dict[str, float]) -> None:
        """
        Check for prediction alerts.
        
        Args:
            model_id: ID of the model
            health_predictions: Predicted health scores
        """
        if model_id not in self.model_registry:
            return
            
        # Get alert thresholds
        warning_threshold = self.config.get("health_score_warning_threshold", 0.7)
        critical_threshold = self.config.get("health_score_critical_threshold", 0.5)
        
        # Check for alerts
        for days_key, predicted_score in health_predictions.items():
            days = int(days_key.split("_")[0])
            
            if predicted_score < critical_threshold:
                # Create critical prediction alert
                alert = {
                    "alert_id": f"alert-prediction-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    "model_id": model_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": f"Predicted critical health score in {days} days: {predicted_score:.2f}",
                    "severity": "critical",
                    "data": {
                        "predicted_health_score": predicted_score,
                        "days_in_future": days,
                        "threshold": critical_threshold
                    }
                }
                
                self.alerts.append(alert)
                
                logger.warning(f"Predicted critical health score for model {model_id} in {days} days: {predicted_score:.2f}")
                
            elif predicted_score < warning_threshold:
                # Create warning prediction alert
                alert = {
                    "alert_id": f"alert-prediction-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    "model_id": model_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": f"Predicted warning health score in {days} days: {predicted_score:.2f}",
                    "severity": "warning",
                    "data": {
                        "predicted_health_score": predicted_score,
                        "days_in_future": days,
                        "threshold": warning_threshold
                    }
                }
                
                self.alerts.append(alert)
                
                logger.warning(f"Predicted warning health score for model {model_id} in {days} days: {predicted_score:.2f}")
    
    async def get_maintenance_recommendations(self, model_id: str) -> Dict[str, Any]:
        """
        Get maintenance recommendations for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Maintenance recommendations
        """
        if model_id not in self.model_registry:
            logger.warning(f"Model not found: {model_id}")
            return {"success": False, "error": "Model not found"}
            
        if model_id not in self.health_metrics:
            logger.warning(f"Health metrics not found for model: {model_id}")
            return {"success": False, "error": "Health metrics not found"}
            
        if model_id not in self.predictions:
            logger.warning(f"Predictions not found for model: {model_id}")
            return {"success": False, "error": "Predictions not found"}
            
        model = self.model_registry[model_id]
        health_metrics = self.health_metrics[model_id]
        predictions = self.predictions[model_id]
        
        # Get current health score
        current_health = model["health_score"]
        
        # Get predicted health scores
        predicted_health = predictions["health_score"]
        
        # Determine maintenance urgency
        urgency = "none"
        
        if current_health < self.config.get("health_score_critical_threshold", 0.5):
            urgency = "immediate"
        elif current_health < self.config.get("health_score_warning_threshold", 0.7):
            urgency = "high"
        elif "7_day" in predicted_health and predicted_health["7_day"] < self.config.get("health_score_warning_threshold", 0.7):
            urgency = "medium"
        elif "30_day" in predicted_health and predicted_health["30_day"] < self.config.get("health_score_warning_threshold", 0.7):
            urgency = "low"
        
        # Generate recommendations
        recommendations = []
        
        # Check for accuracy issues
        if health_metrics["accuracy"] and len(health_metrics["accuracy"]) >= 2:
            recent_accuracy = health_metrics["accuracy"][-min(10, len(health_metrics["accuracy"])):]
            if sum(recent_accuracy) / len(recent_accuracy) < 0.9:
                recommendations.append({
                    "type": "retraining",
                    "description": "Model accuracy is below target. Consider retraining with recent data.",
                    "priority": "high" if urgency in ["immediate", "high"] else "medium"
                })
        
        # Check for latency issues
        if health_metrics["latency"] and len(health_metrics["latency"]) >= 2:
            recent_latency = health_metrics["latency"][-min(10, len(health_metrics["latency"])):]
            max_acceptable_latency = self.config.get("max_acceptable_latency", {}).get(model["model_type"], 1000)
            if sum(recent_latency) / len(recent_latency) > 0.8 * max_acceptable_latency:
                recommendations.append({
                    "type": "optimization",
                    "description": "Model latency is approaching threshold. Consider optimization or hardware upgrade.",
                    "priority": "medium" if urgency in ["immediate", "high"] else "low"
                })
        
        # Check for drift issues
        if health_metrics["drift_score"] and len(health_metrics["drift_score"]) >= 2:
            recent_drift = health_metrics["drift_score"][-min(10, len(health_metrics["drift_score"])):]
            if sum(recent_drift) / len(recent_drift) > 0.5:
                recommendations.append({
                    "type": "data_refresh",
                    "description": "Significant data drift detected. Consider updating training data.",
                    "priority": "high" if urgency in ["immediate", "high"] else "medium"
                })
        
        # Check for error rate issues
        if health_metrics["error_rate"] and len(health_metrics["error_rate"]) >= 2:
            recent_error_rate = health_metrics["error_rate"][-min(10, len(health_metrics["error_rate"])):]
            if sum(recent_error_rate) / len(recent_error_rate) > 0.05:
                recommendations.append({
                    "type": "error_analysis",
                    "description": "Error rate is above acceptable threshold. Conduct error analysis.",
                    "priority": "high" if urgency in ["immediate", "high"] else "medium"
                })
        
        # Add general recommendation based on urgency
        if urgency == "immediate":
            recommendations.append({
                "type": "immediate_action",
                "description": "Model health is critical. Consider taking the model offline and replacing with a fallback.",
                "priority": "critical"
            })
        elif urgency == "high":
            recommendations.append({
                "type": "scheduled_maintenance",
                "description": "Schedule maintenance within 24 hours to address model health issues.",
                "priority": "high"
            })
        elif urgency == "medium":
            recommendations.append({
                "type": "planned_maintenance",
                "description": "Plan maintenance within the next week to prevent model degradation.",
                "priority": "medium"
            })
        elif urgency == "low":
            recommendations.append({
                "type": "monitoring",
                "description": "Continue monitoring model health. Plan for maintenance in the next month.",
                "priority": "low"
            })
        
        # Calculate estimated time to critical
        days_to_critical = None
        
        if current_health > self.config.get("health_score_critical_threshold", 0.5):
            # Check predictions
            for days in [1, 7, 30]:
                day_key = f"{days}_day"
                if day_key in predicted_health and predicted_health[day_key] < self.config.get("health_score_critical_threshold", 0.5):
                    days_to_critical = days
                    break
            
            # If not found in predictions, estimate based on trend
            if days_to_critical is None and len(health_metrics["timestamp"]) >= 2:
                timestamps = [datetime.fromisoformat(ts) for ts in health_metrics["timestamp"]]
                days_span = (timestamps[-1] - timestamps[0]).total_seconds() / 86400
                
                if days_span > 0:
                    # Calculate health score trend
                    first_health = self.model_registry[model_id].get("initial_health_score", 1.0)
                    current_health = model["health_score"]
                    
                    if first_health > current_health:
                        # Estimate days until critical
                        daily_decline = (first_health - current_health) / days_span
                        if daily_decline > 0:
                            days_to_critical = (current_health - self.config.get("health_score_critical_threshold", 0.5)) / daily_decline
                            days_to_critical = max(0, int(days_to_critical))
        
        return {
            "success": True,
            "model_id": model_id,
            "current_health": current_health,
            "predicted_health": predicted_health,
            "urgency": urgency,
            "days_to_critical": days_to_critical,
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_model(self, model_id: str) -> Dict[str, Any]:
        """
        Get a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Model data
        """
        if model_id not in self.model_registry:
            logger.warning(f"Model not found: {model_id}")
            return {}
            
        return self.model_registry[model_id]
    
    def get_health_metrics(self, model_id: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get health metrics for a model.
        
        Args:
            model_id: ID of the model
            limit: Maximum number of data points to return
            
        Returns:
            Health metrics
        """
        if model_id not in self.health_metrics:
            logger.warning(f"Health metrics not found for model: {model_id}")
            return {}
            
        # Return limited history
        metrics = {}
        
        for key, values in self.health_metrics[model_id].items():
            metrics[key] = values[-limit:]
            
        return metrics
    
    def get_predictions(self, model_id: str) -> Dict[str, Any]:
        """
        Get predictions for a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Predictions
        """
        if model_id not in self.predictions:
            logger.warning(f"Predictions not found for model: {model_id}")
            return {}
            
        return self.predictions[model_id]
    
    def get_alerts(self, model_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get alerts.
        
        Args:
            model_id: Filter by model ID (optional)
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts
        """
        if model_id:
            filtered = [alert for alert in self.alerts if alert["model_id"] == model_id]
            return filtered[-limit:]
        else:
            return self.alerts[-limit:]


# Example usage
if __name__ == "__main__":
    async def main():
        # Create a model health prediction agent
        agent = ModelHealthPredictionAgent()
        
        # Register a model
        await agent.register_model("gpt-4", "llm", {
            "version": "1.0",
            "parameters": "1.5T",
            "training_date": "2023-01-01"
        })
        
        # Record some health metrics
        for i in range(30):
            # Simulate declining accuracy
            accuracy = 0.95 - (i * 0.005)
            
            # Simulate increasing latency
            latency = 100 + (i * 10)
            
            # Simulate increasing error rate
            error_rate = 0.01 + (i * 0.002)
            
            # Simulate increasing drift
            drift_score = 0.1 + (i * 0.03)
            
            await agent.record_health_metrics("gpt-4", {
                "accuracy": accuracy,
                "latency": latency,
                "error_rate": error_rate,
                "drift_score": drift_score,
                "resource_usage": 0.5 + (i * 0.01)
            })
        
        # Get maintenance recommendations
        recommendations = await agent.get_maintenance_recommendations("gpt-4")
        
        print(f"Current health: {recommendations['current_health']:.2f}")
        print(f"Predicted health (7 days): {recommendations['predicted_health'].get('7_day', 'N/A')}")
        print(f"Urgency: {recommendations['urgency']}")
        print(f"Days to critical: {recommendations['days_to_critical']}")
        print("Recommendations:")
        for rec in recommendations["recommendations"]:
            print(f"- [{rec['priority']}] {rec['description']}")
        
        # Get alerts
        alerts = agent.get_alerts("gpt-4")
        
        print(f"Alerts: {len(alerts)}")
        for alert in alerts:
            print(f"- {alert['severity']}: {alert['message']}")
    
    asyncio.run(main())
