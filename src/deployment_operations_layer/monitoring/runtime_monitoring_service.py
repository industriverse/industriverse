"""
Runtime Monitoring Service for the Deployment Operations Layer

This module provides comprehensive runtime monitoring capabilities for deployed
components across all Industriverse layers. It collects metrics, logs, and
telemetry data to provide real-time visibility into deployment health and
performance.

The monitoring service integrates with the analytics manager to store historical
data and supports alerting based on configurable thresholds.
"""

import os
import sys
import json
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

from ..analytics.analytics_manager import AnalyticsManager
from ..agent.agent_utils import AgentUtils
from ..execution.layer_execution_adapter import create_layer_execution_adapter

# Configure logging
logger = logging.getLogger(__name__)

class RuntimeMonitoringService:
    """Runtime monitoring service for deployed components"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the runtime monitoring service
        
        Args:
            config: Configuration for the monitoring service
        """
        self.config = config
        self.analytics_manager = AnalyticsManager()
        self.agent_utils = AgentUtils()
        self.monitoring_interval = config.get("monitoring_interval", 30)  # seconds
        self.alert_thresholds = config.get("alert_thresholds", {})
        self.layer_adapters = {}
        self.monitoring_task = None
        self.metrics_history = {}
        self.alert_history = []
        self.status = "initialized"
        
        # Initialize layer adapters for monitoring
        for layer_name, layer_config in config.get("layers", {}).items():
            self.layer_adapters[layer_name] = create_layer_execution_adapter(
                layer_name, layer_config
            )
        
        logger.info("Initialized runtime monitoring service")
    
    async def start_monitoring(self):
        """Start the monitoring service"""
        if self.monitoring_task is not None:
            logger.warning("Monitoring service is already running")
            return
        
        self.status = "running"
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started runtime monitoring service")
    
    async def stop_monitoring(self):
        """Stop the monitoring service"""
        if self.monitoring_task is None:
            logger.warning("Monitoring service is not running")
            return
        
        self.status = "stopping"
        self.monitoring_task.cancel()
        try:
            await self.monitoring_task
        except asyncio.CancelledError:
            pass
        
        self.monitoring_task = None
        self.status = "stopped"
        logger.info("Stopped runtime monitoring service")
    
    async def _monitoring_loop(self):
        """Internal monitoring loop"""
        while True:
            try:
                await self._collect_metrics()
                await self._check_alerts()
            except Exception as e:
                logger.error(f"Error in monitoring loop: {str(e)}")
            
            await asyncio.sleep(self.monitoring_interval)
    
    async def _collect_metrics(self):
        """Collect metrics from all monitored layers and components"""
        timestamp = self.agent_utils.get_current_timestamp()
        metrics = {
            "timestamp": timestamp,
            "layers": {}
        }
        
        # Collect metrics from each layer
        for layer_name, adapter in self.layer_adapters.items():
            try:
                layer_status = await adapter.get_layer_status()
                metrics["layers"][layer_name] = layer_status
            except Exception as e:
                logger.error(f"Error collecting metrics from {layer_name}: {str(e)}")
                metrics["layers"][layer_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        # Store metrics in history
        if timestamp not in self.metrics_history:
            self.metrics_history[timestamp] = metrics
        
        # Send metrics to analytics manager
        self.analytics_manager.record_runtime_metrics(metrics)
        
        return metrics
    
    async def _check_alerts(self):
        """Check for alert conditions based on collected metrics"""
        if not self.metrics_history:
            return
        
        # Get the most recent metrics
        latest_timestamp = max(self.metrics_history.keys())
        latest_metrics = self.metrics_history[latest_timestamp]
        
        alerts = []
        
        # Check layer status alerts
        for layer_name, layer_metrics in latest_metrics["layers"].items():
            if layer_metrics.get("status") not in ["healthy", "success"]:
                alert = {
                    "timestamp": self.agent_utils.get_current_timestamp(),
                    "type": "layer_status",
                    "severity": "warning",
                    "layer": layer_name,
                    "message": f"Layer {layer_name} is reporting status: {layer_metrics.get('status')}",
                    "details": layer_metrics
                }
                alerts.append(alert)
                self.alert_history.append(alert)
                self.analytics_manager.record_alert(alert)
        
        # Check custom alert thresholds
        for threshold_name, threshold_config in self.alert_thresholds.items():
            try:
                if await self._check_threshold(threshold_name, threshold_config, latest_metrics):
                    alert = {
                        "timestamp": self.agent_utils.get_current_timestamp(),
                        "type": "threshold",
                        "severity": threshold_config.get("severity", "warning"),
                        "threshold": threshold_name,
                        "message": threshold_config.get("message", f"Threshold {threshold_name} exceeded"),
                        "details": {
                            "threshold": threshold_config,
                            "metrics": latest_metrics
                        }
                    }
                    alerts.append(alert)
                    self.alert_history.append(alert)
                    self.analytics_manager.record_alert(alert)
            except Exception as e:
                logger.error(f"Error checking threshold {threshold_name}: {str(e)}")
        
        return alerts
    
    async def _check_threshold(self, threshold_name: str, threshold_config: Dict[str, Any], metrics: Dict[str, Any]) -> bool:
        """
        Check if a threshold is exceeded based on metrics
        
        Args:
            threshold_name: Name of the threshold
            threshold_config: Threshold configuration
            metrics: Collected metrics
            
        Returns:
            True if threshold is exceeded, False otherwise
        """
        # Extract the metric value using the path
        path = threshold_config.get("metric_path", "")
        value = self._get_value_by_path(metrics, path)
        
        if value is None:
            logger.warning(f"Metric path {path} not found in metrics")
            return False
        
        # Check the threshold condition
        operator = threshold_config.get("operator", "gt")
        threshold_value = threshold_config.get("value")
        
        if threshold_value is None:
            logger.warning(f"No threshold value specified for {threshold_name}")
            return False
        
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
            logger.warning(f"Unknown operator {operator} for threshold {threshold_name}")
            return False
    
    def _get_value_by_path(self, data: Dict[str, Any], path: str) -> Any:
        """
        Get a value from a nested dictionary using a dot-separated path
        
        Args:
            data: Nested dictionary
            path: Dot-separated path to the value
            
        Returns:
            Value at the specified path, or None if not found
        """
        if not path:
            return None
        
        parts = path.split(".")
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
        
        return current
    
    async def get_metrics(self, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get metrics within a time range
        
        Args:
            start_time: Start time (ISO format), or None for all
            end_time: End time (ISO format), or None for all
            
        Returns:
            List of metrics within the time range
        """
        if not self.metrics_history:
            return []
        
        # Convert time strings to timestamps if provided
        start_timestamp = None
        end_timestamp = None
        
        if start_time:
            try:
                start_timestamp = self.agent_utils.parse_timestamp(start_time)
            except ValueError:
                logger.warning(f"Invalid start time format: {start_time}")
        
        if end_time:
            try:
                end_timestamp = self.agent_utils.parse_timestamp(end_time)
            except ValueError:
                logger.warning(f"Invalid end time format: {end_time}")
        
        # Filter metrics by time range
        filtered_metrics = []
        
        for timestamp, metrics in self.metrics_history.items():
            if start_timestamp and timestamp < start_timestamp:
                continue
            if end_timestamp and timestamp > end_timestamp:
                continue
            
            filtered_metrics.append(metrics)
        
        # Sort by timestamp
        filtered_metrics.sort(key=lambda m: m["timestamp"])
        
        return filtered_metrics
    
    async def get_alerts(self, start_time: Optional[str] = None, end_time: Optional[str] = None, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get alerts within a time range and with specified severity
        
        Args:
            start_time: Start time (ISO format), or None for all
            end_time: End time (ISO format), or None for all
            severity: Alert severity, or None for all
            
        Returns:
            List of alerts matching the criteria
        """
        if not self.alert_history:
            return []
        
        # Convert time strings to timestamps if provided
        start_timestamp = None
        end_timestamp = None
        
        if start_time:
            try:
                start_timestamp = self.agent_utils.parse_timestamp(start_time)
            except ValueError:
                logger.warning(f"Invalid start time format: {start_time}")
        
        if end_time:
            try:
                end_timestamp = self.agent_utils.parse_timestamp(end_time)
            except ValueError:
                logger.warning(f"Invalid end time format: {end_time}")
        
        # Filter alerts by time range and severity
        filtered_alerts = []
        
        for alert in self.alert_history:
            if start_timestamp and alert["timestamp"] < start_timestamp:
                continue
            if end_timestamp and alert["timestamp"] > end_timestamp:
                continue
            if severity and alert.get("severity") != severity:
                continue
            
            filtered_alerts.append(alert)
        
        # Sort by timestamp
        filtered_alerts.sort(key=lambda a: a["timestamp"])
        
        return filtered_alerts
    
    async def get_layer_health(self, layer_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get the current health status of layers
        
        Args:
            layer_name: Name of the layer, or None for all layers
            
        Returns:
            Dict containing layer health status
        """
        if not self.metrics_history:
            return {"status": "unknown", "layers": {}}
        
        # Get the most recent metrics
        latest_timestamp = max(self.metrics_history.keys())
        latest_metrics = self.metrics_history[latest_timestamp]
        
        if layer_name:
            if layer_name not in latest_metrics["layers"]:
                return {"status": "unknown", "layer": layer_name}
            
            return {
                "status": latest_metrics["layers"][layer_name].get("status", "unknown"),
                "layer": layer_name,
                "details": latest_metrics["layers"][layer_name]
            }
        else:
            # Determine overall health status
            layer_statuses = [
                layer_metrics.get("status", "unknown")
                for layer_metrics in latest_metrics["layers"].values()
            ]
            
            if all(status in ["healthy", "success"] for status in layer_statuses):
                overall_status = "healthy"
            elif any(status in ["error", "failed"] for status in layer_statuses):
                overall_status = "error"
            else:
                overall_status = "warning"
            
            return {
                "status": overall_status,
                "timestamp": latest_timestamp,
                "layers": latest_metrics["layers"]
            }
    
    async def cleanup(self):
        """Clean up resources used by the monitoring service"""
        await self.stop_monitoring()
        
        # Clean up layer adapters
        for adapter in self.layer_adapters.values():
            await adapter.cleanup()
        
        logger.info("Cleaned up runtime monitoring service")


# Singleton instance
_instance = None

def get_runtime_monitoring_service(config: Optional[Dict[str, Any]] = None) -> RuntimeMonitoringService:
    """
    Get the singleton instance of the runtime monitoring service
    
    Args:
        config: Configuration for the monitoring service (only used if creating a new instance)
        
    Returns:
        RuntimeMonitoringService instance
    """
    global _instance
    
    if _instance is None:
        if config is None:
            config = {}
        
        _instance = RuntimeMonitoringService(config)
    
    return _instance
