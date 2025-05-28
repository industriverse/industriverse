"""
Core AI Observability Agent for Industriverse Core AI Layer

This module implements the observability agent for the Core AI Layer,
providing standardized health metrics, monitoring, and alerting capabilities.
"""

import logging
import json
import asyncio
import time
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import os
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CoreAIObservabilityAgent:
    """
    Implements the observability agent for the Core AI Layer.
    Provides standardized health metrics, monitoring, and alerting capabilities.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the observability agent.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or "config/observability_thresholds.yaml"
        self.metrics_dir = "metrics"
        self.alerts_dir = "alerts"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize metrics registry
        self.metrics_registry = {}
        
        # Initialize alert history
        self.alert_history = []
        
        # Create directories if they don't exist
        os.makedirs(self.metrics_dir, exist_ok=True)
        os.makedirs(self.alerts_dir, exist_ok=True)
        
        # Register standard metrics
        self._register_standard_metrics()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration.
        
        Returns:
            The configuration as a dictionary
        """
        try:
            import yaml
            
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
    
    def _register_standard_metrics(self) -> None:
        """Register standard metrics for Core AI Layer components."""
        # LLM Service metrics
        self.register_metric("llm_service.model_latency", "gauge", "LLM model inference latency in milliseconds")
        self.register_metric("llm_service.token_usage", "counter", "LLM token usage count")
        self.register_metric("llm_service.sla_violation_rate", "gauge", "Rate of SLA violations for LLM service")
        self.register_metric("llm_service.request_count", "counter", "Number of LLM inference requests")
        self.register_metric("llm_service.error_rate", "gauge", "Error rate for LLM service")
        
        # ML Service metrics
        self.register_metric("ml_service.model_latency", "gauge", "ML model inference latency in milliseconds")
        self.register_metric("ml_service.request_count", "counter", "Number of ML inference requests")
        self.register_metric("ml_service.error_rate", "gauge", "Error rate for ML service")
        self.register_metric("ml_service.training_duration", "gauge", "Duration of ML model training in seconds")
        
        # Explainability Service metrics
        self.register_metric("explainability_service.latency", "gauge", "Explainability service latency in milliseconds")
        self.register_metric("explainability_service.request_count", "counter", "Number of explainability requests")
        self.register_metric("explainability_service.error_rate", "gauge", "Error rate for explainability service")
        
        # Monitoring Service metrics
        self.register_metric("monitoring_service.data_drift_score", "gauge", "Data drift score")
        self.register_metric("monitoring_service.model_drift_score", "gauge", "Model drift score")
        self.register_metric("monitoring_service.alert_count", "counter", "Number of alerts generated")
        
        # Protocol metrics
        self.register_metric("protocol.mcp_event_count", "counter", "Number of MCP events processed")
        self.register_metric("protocol.a2a_task_count", "counter", "Number of A2A tasks processed")
        self.register_metric("protocol.translation_latency", "gauge", "Protocol translation latency in milliseconds")
        
        # System metrics
        self.register_metric("system.cpu_usage", "gauge", "CPU usage percentage")
        self.register_metric("system.memory_usage", "gauge", "Memory usage percentage")
        self.register_metric("system.disk_usage", "gauge", "Disk usage percentage")
        
        logger.info(f"Registered {len(self.metrics_registry)} standard metrics")
    
    def register_metric(self, name: str, metric_type: str, description: str) -> None:
        """
        Register a metric.
        
        Args:
            name: Metric name
            metric_type: Metric type (gauge, counter, histogram)
            description: Metric description
        """
        self.metrics_registry[name] = {
            "type": metric_type,
            "description": description,
            "value": 0 if metric_type == "counter" else None,
            "timestamp": None,
            "history": []
        }
        logger.debug(f"Registered metric: {name} ({metric_type})")
    
    def update_metric(self, name: str, value: Union[int, float]) -> None:
        """
        Update a metric value.
        
        Args:
            name: Metric name
            value: New metric value
        """
        if name not in self.metrics_registry:
            logger.warning(f"Metric not registered: {name}")
            return
            
        metric = self.metrics_registry[name]
        timestamp = datetime.utcnow().isoformat()
        
        if metric["type"] == "counter":
            # Counters are cumulative
            if metric["value"] is None:
                metric["value"] = value
            else:
                metric["value"] += value
        else:
            # Gauges and histograms are set directly
            metric["value"] = value
            
        metric["timestamp"] = timestamp
        
        # Add to history (keep last 100 values)
        metric["history"].append({
            "value": metric["value"],
            "timestamp": timestamp
        })
        
        if len(metric["history"]) > 100:
            metric["history"] = metric["history"][-100:]
            
        logger.debug(f"Updated metric {name}: {metric['value']}")
        
        # Check for threshold violations
        self._check_threshold(name, metric["value"])
        
        # Export metric
        self._export_metric(name)
    
    def _check_threshold(self, name: str, value: Union[int, float]) -> None:
        """
        Check if a metric value violates a threshold.
        
        Args:
            name: Metric name
            value: Metric value
        """
        # Get thresholds from config
        thresholds = self.config.get("thresholds", {})
        
        if name not in thresholds:
            return
            
        threshold = thresholds[name]
        
        # Check for violations
        if "warning" in threshold and self._check_violation(value, threshold["warning"]):
            self._create_alert(name, value, "warning", threshold["warning"])
            
        if "critical" in threshold and self._check_violation(value, threshold["critical"]):
            self._create_alert(name, value, "critical", threshold["critical"])
    
    def _check_violation(self, value: Union[int, float], threshold: Dict[str, Any]) -> bool:
        """
        Check if a value violates a threshold.
        
        Args:
            value: Value to check
            threshold: Threshold configuration
            
        Returns:
            True if threshold is violated, False otherwise
        """
        operator = threshold.get("operator", "gt")
        threshold_value = threshold.get("value", 0)
        
        if operator == "gt":
            return value > threshold_value
        elif operator == "lt":
            return value < threshold_value
        elif operator == "eq":
            return value == threshold_value
        elif operator == "ne":
            return value != threshold_value
        elif operator == "ge":
            return value >= threshold_value
        elif operator == "le":
            return value <= threshold_value
        else:
            logger.warning(f"Unknown operator: {operator}")
            return False
    
    def _create_alert(self, metric_name: str, value: Union[int, float], level: str, threshold: Dict[str, Any]) -> None:
        """
        Create an alert for a threshold violation.
        
        Args:
            metric_name: Name of the metric
            value: Current value
            level: Alert level (warning, critical)
            threshold: Threshold configuration
        """
        timestamp = datetime.utcnow().isoformat()
        
        alert = {
            "metric": metric_name,
            "value": value,
            "level": level,
            "threshold": threshold,
            "timestamp": timestamp,
            "message": f"{level.upper()} alert for {metric_name}: {value} {threshold['operator']} {threshold['value']}"
        }
        
        # Add to alert history
        self.alert_history.append(alert)
        
        # Keep last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
            
        logger.warning(f"Alert: {alert['message']}")
        
        # Export alert
        self._export_alert(alert)
        
        # In a real implementation, this would also:
        # 1. Send the alert to a notification system
        # 2. Trigger any configured actions
    
    def _export_metric(self, name: str) -> None:
        """
        Export a metric to a file.
        
        Args:
            name: Metric name
        """
        try:
            metric = self.metrics_registry[name]
            
            # Create a file-safe name
            file_name = name.replace(".", "_")
            file_path = f"{self.metrics_dir}/{file_name}.json"
            
            # Export metric data
            with open(file_path, 'w') as f:
                json.dump({
                    "name": name,
                    "type": metric["type"],
                    "description": metric["description"],
                    "value": metric["value"],
                    "timestamp": metric["timestamp"],
                    "history": metric["history"][-10:]  # Export last 10 values
                }, f, indent=2)
                
            logger.debug(f"Exported metric {name} to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting metric {name}: {e}")
    
    def _export_alert(self, alert: Dict[str, Any]) -> None:
        """
        Export an alert to a file.
        
        Args:
            alert: Alert data
        """
        try:
            # Create a unique file name
            timestamp = alert["timestamp"].replace(":", "-").replace(".", "-")
            file_name = f"{alert['level']}_{alert['metric'].replace('.', '_')}_{timestamp}"
            file_path = f"{self.alerts_dir}/{file_name}.json"
            
            # Export alert data
            with open(file_path, 'w') as f:
                json.dump(alert, f, indent=2)
                
            logger.debug(f"Exported alert to {file_path}")
        except Exception as e:
            logger.error(f"Error exporting alert: {e}")
    
    def export_all_metrics(self) -> None:
        """Export all metrics to files."""
        for name in self.metrics_registry:
            self._export_metric(name)
            
        logger.info(f"Exported {len(self.metrics_registry)} metrics")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics.
        
        Returns:
            Dictionary with all metrics
        """
        return {
            name: {
                "type": metric["type"],
                "description": metric["description"],
                "value": metric["value"],
                "timestamp": metric["timestamp"]
            }
            for name, metric in self.metrics_registry.items()
        }
    
    def get_metric(self, name: str) -> Dict[str, Any]:
        """
        Get a specific metric.
        
        Args:
            name: Metric name
            
        Returns:
            Metric data
        """
        if name not in self.metrics_registry:
            logger.warning(f"Metric not found: {name}")
            return {}
            
        metric = self.metrics_registry[name]
        
        return {
            "type": metric["type"],
            "description": metric["description"],
            "value": metric["value"],
            "timestamp": metric["timestamp"],
            "history": metric["history"]
        }
    
    def get_alerts(self, level: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get alerts.
        
        Args:
            level: Filter by alert level (optional)
            limit: Maximum number of alerts to return
            
        Returns:
            List of alerts
        """
        if level:
            alerts = [alert for alert in self.alert_history if alert["level"] == level]
        else:
            alerts = self.alert_history
            
        return alerts[-limit:]
    
    async def collect_system_metrics(self) -> None:
        """Collect system metrics."""
        try:
            import psutil
            
            # Collect CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.update_metric("system.cpu_usage", cpu_percent)
            
            # Collect memory usage
            memory = psutil.virtual_memory()
            self.update_metric("system.memory_usage", memory.percent)
            
            # Collect disk usage
            disk = psutil.disk_usage('/')
            self.update_metric("system.disk_usage", disk.percent)
            
            logger.debug("Collected system metrics")
        except ImportError:
            logger.warning("psutil not available, skipping system metrics collection")
        except Exception as e:
            logger.error(f"Error collecting system metrics: {e}")
    
    async def start_metrics_collection(self, interval: int = 60) -> None:
        """
        Start periodic metrics collection.
        
        Args:
            interval: Collection interval in seconds
        """
        logger.info(f"Starting metrics collection with interval {interval}s")
        
        while True:
            try:
                # Collect system metrics
                await self.collect_system_metrics()
                
                # Export all metrics
                self.export_all_metrics()
                
                # Wait for next collection
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Error in metrics collection: {e}")
                await asyncio.sleep(5)  # Wait a bit before retrying


# Example usage
if __name__ == "__main__":
    async def main():
        # Create an observability agent
        agent = CoreAIObservabilityAgent()
        
        # Update some metrics
        agent.update_metric("llm_service.model_latency", 150)
        agent.update_metric("llm_service.token_usage", 1000)
        agent.update_metric("llm_service.request_count", 1)
        
        # Get metrics
        metrics = agent.get_metrics()
        print(f"Registered metrics: {len(metrics)}")
        
        # Get a specific metric
        latency_metric = agent.get_metric("llm_service.model_latency")
        print(f"LLM latency: {latency_metric['value']}ms")
        
        # Start metrics collection in the background
        collection_task = asyncio.create_task(agent.start_metrics_collection(5))
        
        # Run for a while
        for i in range(5):
            # Simulate some metric updates
            agent.update_metric("llm_service.model_latency", 100 + i * 20)
            agent.update_metric("llm_service.token_usage", 500)
            agent.update_metric("llm_service.request_count", 1)
            
            # Wait a bit
            await asyncio.sleep(1)
        
        # Cancel collection task
        collection_task.cancel()
        
        # Get alerts
        alerts = agent.get_alerts()
        print(f"Generated alerts: {len(alerts)}")
    
    asyncio.run(main())
