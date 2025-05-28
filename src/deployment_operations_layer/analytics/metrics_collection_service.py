"""
Metrics Collection Service for the Deployment Operations Layer

This module provides comprehensive metrics collection capabilities for the Deployment Operations Layer,
enabling real-time monitoring and analysis of deployment operations across the Industriverse ecosystem.

The metrics collection service gathers telemetry data from all components and layers, processes it,
and makes it available for visualization, alerting, and analysis through the analytics framework.
"""

import os
import time
import json
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

from ..protocol.protocol_bridge import ProtocolBridge
from ..agent.agent_utils import AgentUtils
from ..integration.layer_integration_manager import LayerIntegrationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricsCollectionService:
    """
    Metrics Collection Service for the Deployment Operations Layer.
    
    This service is responsible for collecting, processing, and storing metrics from all components
    and layers of the Industriverse ecosystem, providing real-time visibility into deployment operations.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Metrics Collection Service.
        
        Args:
            config_path: Path to the configuration file for the metrics collection service.
        """
        self.config = self._load_config(config_path)
        self.protocol_bridge = ProtocolBridge()
        self.layer_integration_manager = LayerIntegrationManager()
        self.agent_utils = AgentUtils()
        
        # Initialize metrics storage
        self.metrics_store = {}
        
        # Initialize collection threads
        self.collection_threads = {}
        self.running = False
        
        # Initialize metrics schema
        self.metrics_schema = self._initialize_metrics_schema()
        
        logger.info("Metrics Collection Service initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration for the metrics collection service.
        
        Args:
            config_path: Path to the configuration file.
            
        Returns:
            Dict containing the configuration.
        """
        default_config = {
            "collection_interval": 30,  # seconds
            "storage_retention": 86400,  # 24 hours in seconds
            "enabled_metrics": ["cpu", "memory", "network", "disk", "deployment", "mission", "layer"],
            "storage_path": "/var/lib/industriverse/metrics",
            "max_metrics_per_category": 10000,
            "aggregation_interval": 300,  # 5 minutes in seconds
            "alert_thresholds": {
                "cpu_usage": 80,
                "memory_usage": 80,
                "disk_usage": 80,
                "mission_failure_rate": 5,
                "deployment_failure_rate": 5
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    # Merge user config with default config
                    for key, value in user_config.items():
                        if key in default_config and isinstance(default_config[key], dict) and isinstance(value, dict):
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            except Exception as e:
                logger.error(f"Error loading metrics collection config: {str(e)}")
        
        return default_config
    
    def _initialize_metrics_schema(self) -> Dict[str, Any]:
        """
        Initialize the metrics schema for all collected metrics.
        
        Returns:
            Dict containing the metrics schema.
        """
        return {
            "system": {
                "cpu": {
                    "usage_percent": "float",
                    "load_average": "float",
                    "core_count": "int",
                    "process_count": "int"
                },
                "memory": {
                    "total": "float",
                    "used": "float",
                    "free": "float",
                    "usage_percent": "float"
                },
                "disk": {
                    "total": "float",
                    "used": "float",
                    "free": "float",
                    "usage_percent": "float",
                    "read_ops": "int",
                    "write_ops": "int"
                },
                "network": {
                    "bytes_sent": "int",
                    "bytes_received": "int",
                    "packets_sent": "int",
                    "packets_received": "int",
                    "errors": "int"
                }
            },
            "deployment": {
                "count": "int",
                "success_rate": "float",
                "failure_rate": "float",
                "average_duration": "float",
                "status_distribution": "dict"
            },
            "mission": {
                "count": "int",
                "success_rate": "float",
                "failure_rate": "float",
                "average_duration": "float",
                "status_distribution": "dict"
            },
            "layer": {
                "data_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int"
                },
                "core_ai_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int",
                    "model_load": "float"
                },
                "generative_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int",
                    "generation_rate": "float"
                },
                "application_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int",
                    "request_rate": "float"
                },
                "protocol_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int",
                    "message_rate": "float"
                },
                "workflow_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int",
                    "workflow_execution_rate": "float"
                },
                "ui_ux_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int",
                    "user_session_count": "int"
                },
                "security_compliance_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int",
                    "compliance_score": "float"
                },
                "native_app_layer": {
                    "health": "float",
                    "deployment_count": "int",
                    "active_capsules": "int",
                    "connected_devices": "int"
                }
            },
            "agent": {
                "count": "int",
                "active_count": "int",
                "health_distribution": "dict"
            },
            "capsule": {
                "count": "int",
                "active_count": "int",
                "health_distribution": "dict",
                "type_distribution": "dict"
            }
        }
    
    def start(self):
        """
        Start the metrics collection service.
        """
        if self.running:
            logger.warning("Metrics Collection Service is already running")
            return
        
        self.running = True
        
        # Start collection threads for each metric category
        for metric_category in self.config["enabled_metrics"]:
            collection_thread = threading.Thread(
                target=self._collect_metrics_loop,
                args=(metric_category,),
                daemon=True
            )
            self.collection_threads[metric_category] = collection_thread
            collection_thread.start()
            
        # Start aggregation thread
        aggregation_thread = threading.Thread(
            target=self._aggregate_metrics_loop,
            daemon=True
        )
        self.collection_threads["aggregation"] = aggregation_thread
        aggregation_thread.start()
        
        # Start storage cleanup thread
        cleanup_thread = threading.Thread(
            target=self._cleanup_metrics_loop,
            daemon=True
        )
        self.collection_threads["cleanup"] = cleanup_thread
        cleanup_thread.start()
        
        logger.info("Metrics Collection Service started")
    
    def stop(self):
        """
        Stop the metrics collection service.
        """
        if not self.running:
            logger.warning("Metrics Collection Service is not running")
            return
        
        self.running = False
        
        # Wait for all threads to complete
        for thread_name, thread in self.collection_threads.items():
            logger.info(f"Stopping {thread_name} collection thread")
            thread.join(timeout=5.0)
        
        self.collection_threads = {}
        
        logger.info("Metrics Collection Service stopped")
    
    def _collect_metrics_loop(self, metric_category: str):
        """
        Continuous loop for collecting metrics for a specific category.
        
        Args:
            metric_category: Category of metrics to collect.
        """
        logger.info(f"Starting metrics collection for {metric_category}")
        
        while self.running:
            try:
                # Collect metrics based on category
                if metric_category == "cpu":
                    metrics = self._collect_cpu_metrics()
                elif metric_category == "memory":
                    metrics = self._collect_memory_metrics()
                elif metric_category == "disk":
                    metrics = self._collect_disk_metrics()
                elif metric_category == "network":
                    metrics = self._collect_network_metrics()
                elif metric_category == "deployment":
                    metrics = self._collect_deployment_metrics()
                elif metric_category == "mission":
                    metrics = self._collect_mission_metrics()
                elif metric_category == "layer":
                    metrics = self._collect_layer_metrics()
                else:
                    logger.warning(f"Unknown metric category: {metric_category}")
                    metrics = {}
                
                # Store metrics with timestamp
                timestamp = datetime.now().isoformat()
                if metric_category not in self.metrics_store:
                    self.metrics_store[metric_category] = []
                
                metrics_entry = {
                    "timestamp": timestamp,
                    "data": metrics
                }
                
                self.metrics_store[metric_category].append(metrics_entry)
                
                # Check if we need to trim the metrics store
                max_metrics = self.config["max_metrics_per_category"]
                if len(self.metrics_store[metric_category]) > max_metrics:
                    # Remove oldest metrics
                    self.metrics_store[metric_category] = self.metrics_store[metric_category][-max_metrics:]
                
                # Check for alert conditions
                self._check_alerts(metric_category, metrics)
                
            except Exception as e:
                logger.error(f"Error collecting {metric_category} metrics: {str(e)}")
            
            # Sleep until next collection interval
            time.sleep(self.config["collection_interval"])
    
    def _aggregate_metrics_loop(self):
        """
        Continuous loop for aggregating metrics at regular intervals.
        """
        logger.info("Starting metrics aggregation")
        
        while self.running:
            try:
                self._aggregate_metrics()
            except Exception as e:
                logger.error(f"Error aggregating metrics: {str(e)}")
            
            # Sleep until next aggregation interval
            time.sleep(self.config["aggregation_interval"])
    
    def _cleanup_metrics_loop(self):
        """
        Continuous loop for cleaning up old metrics data.
        """
        logger.info("Starting metrics cleanup")
        
        while self.running:
            try:
                self._cleanup_old_metrics()
            except Exception as e:
                logger.error(f"Error cleaning up metrics: {str(e)}")
            
            # Sleep for an hour before next cleanup
            time.sleep(3600)
    
    def _collect_cpu_metrics(self) -> Dict[str, Any]:
        """
        Collect CPU metrics from the system.
        
        Returns:
            Dict containing CPU metrics.
        """
        # In a real implementation, this would use system libraries to collect actual metrics
        # For this implementation, we'll return sample data
        return {
            "usage_percent": 45.2,
            "load_average": 1.25,
            "core_count": 8,
            "process_count": 120
        }
    
    def _collect_memory_metrics(self) -> Dict[str, Any]:
        """
        Collect memory metrics from the system.
        
        Returns:
            Dict containing memory metrics.
        """
        # In a real implementation, this would use system libraries to collect actual metrics
        # For this implementation, we'll return sample data
        return {
            "total": 16384.0,  # MB
            "used": 8192.0,    # MB
            "free": 8192.0,    # MB
            "usage_percent": 50.0
        }
    
    def _collect_disk_metrics(self) -> Dict[str, Any]:
        """
        Collect disk metrics from the system.
        
        Returns:
            Dict containing disk metrics.
        """
        # In a real implementation, this would use system libraries to collect actual metrics
        # For this implementation, we'll return sample data
        return {
            "total": 1024.0,  # GB
            "used": 512.0,    # GB
            "free": 512.0,    # GB
            "usage_percent": 50.0,
            "read_ops": 1200,
            "write_ops": 800
        }
    
    def _collect_network_metrics(self) -> Dict[str, Any]:
        """
        Collect network metrics from the system.
        
        Returns:
            Dict containing network metrics.
        """
        # In a real implementation, this would use system libraries to collect actual metrics
        # For this implementation, we'll return sample data
        return {
            "bytes_sent": 1024000,
            "bytes_received": 2048000,
            "packets_sent": 8000,
            "packets_received": 12000,
            "errors": 0
        }
    
    def _collect_deployment_metrics(self) -> Dict[str, Any]:
        """
        Collect deployment metrics from the Deployment Operations Layer.
        
        Returns:
            Dict containing deployment metrics.
        """
        # In a real implementation, this would query the deployment engine for actual metrics
        # For this implementation, we'll return sample data
        return {
            "count": 120,
            "success_rate": 95.5,
            "failure_rate": 4.5,
            "average_duration": 180.0,  # seconds
            "status_distribution": {
                "completed": 100,
                "in_progress": 15,
                "failed": 5
            }
        }
    
    def _collect_mission_metrics(self) -> Dict[str, Any]:
        """
        Collect mission metrics from the Deployment Operations Layer.
        
        Returns:
            Dict containing mission metrics.
        """
        # In a real implementation, this would query the mission planner for actual metrics
        # For this implementation, we'll return sample data
        return {
            "count": 45,
            "success_rate": 97.8,
            "failure_rate": 2.2,
            "average_duration": 600.0,  # seconds
            "status_distribution": {
                "completed": 40,
                "in_progress": 3,
                "failed": 2
            }
        }
    
    def _collect_layer_metrics(self) -> Dict[str, Any]:
        """
        Collect metrics from all Industriverse layers.
        
        Returns:
            Dict containing layer metrics.
        """
        # In a real implementation, this would query each layer adapter for actual metrics
        # For this implementation, we'll return sample data
        return {
            "data_layer": {
                "health": 98.5,
                "deployment_count": 25,
                "active_capsules": 18
            },
            "core_ai_layer": {
                "health": 99.2,
                "deployment_count": 15,
                "active_capsules": 12,
                "model_load": 65.3
            },
            "generative_layer": {
                "health": 97.8,
                "deployment_count": 10,
                "active_capsules": 8,
                "generation_rate": 120.5
            },
            "application_layer": {
                "health": 99.5,
                "deployment_count": 30,
                "active_capsules": 25,
                "request_rate": 450.2
            },
            "protocol_layer": {
                "health": 100.0,
                "deployment_count": 5,
                "active_capsules": 5,
                "message_rate": 1250.8
            },
            "workflow_layer": {
                "health": 98.9,
                "deployment_count": 12,
                "active_capsules": 10,
                "workflow_execution_rate": 85.3
            },
            "ui_ux_layer": {
                "health": 99.8,
                "deployment_count": 8,
                "active_capsules": 7,
                "user_session_count": 250
            },
            "security_compliance_layer": {
                "health": 99.9,
                "deployment_count": 6,
                "active_capsules": 6,
                "compliance_score": 98.5
            },
            "native_app_layer": {
                "health": 97.5,
                "deployment_count": 9,
                "active_capsules": 7,
                "connected_devices": 120
            }
        }
    
    def _check_alerts(self, metric_category: str, metrics: Dict[str, Any]):
        """
        Check metrics against alert thresholds and trigger alerts if needed.
        
        Args:
            metric_category: Category of metrics to check.
            metrics: Metrics data to check against thresholds.
        """
        thresholds = self.config["alert_thresholds"]
        
        if metric_category == "cpu" and metrics["usage_percent"] > thresholds["cpu_usage"]:
            self._trigger_alert("CPU usage above threshold", {
                "metric": "cpu_usage",
                "value": metrics["usage_percent"],
                "threshold": thresholds["cpu_usage"]
            })
        
        elif metric_category == "memory" and metrics["usage_percent"] > thresholds["memory_usage"]:
            self._trigger_alert("Memory usage above threshold", {
                "metric": "memory_usage",
                "value": metrics["usage_percent"],
                "threshold": thresholds["memory_usage"]
            })
        
        elif metric_category == "disk" and metrics["usage_percent"] > thresholds["disk_usage"]:
            self._trigger_alert("Disk usage above threshold", {
                "metric": "disk_usage",
                "value": metrics["usage_percent"],
                "threshold": thresholds["disk_usage"]
            })
        
        elif metric_category == "mission" and metrics["failure_rate"] > thresholds["mission_failure_rate"]:
            self._trigger_alert("Mission failure rate above threshold", {
                "metric": "mission_failure_rate",
                "value": metrics["failure_rate"],
                "threshold": thresholds["mission_failure_rate"]
            })
        
        elif metric_category == "deployment" and metrics["failure_rate"] > thresholds["deployment_failure_rate"]:
            self._trigger_alert("Deployment failure rate above threshold", {
                "metric": "deployment_failure_rate",
                "value": metrics["failure_rate"],
                "threshold": thresholds["deployment_failure_rate"]
            })
    
    def _trigger_alert(self, message: str, data: Dict[str, Any]):
        """
        Trigger an alert based on metrics exceeding thresholds.
        
        Args:
            message: Alert message.
            data: Alert data.
        """
        alert = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "data": data,
            "severity": "warning"
        }
        
        # In a real implementation, this would send the alert to the alerting system
        # For this implementation, we'll just log it
        logger.warning(f"ALERT: {message} - {json.dumps(data)}")
        
        # Store the alert
        if "alerts" not in self.metrics_store:
            self.metrics_store["alerts"] = []
        
        self.metrics_store["alerts"].append(alert)
    
    def _aggregate_metrics(self):
        """
        Aggregate metrics for long-term storage and analysis.
        """
        aggregated_metrics = {}
        
        # Get current timestamp
        timestamp = datetime.now().isoformat()
        
        # Iterate through all metric categories
        for category, metrics_list in self.metrics_store.items():
            if category == "alerts":
                continue
            
            # Skip if no metrics
            if not metrics_list:
                continue
            
            # Get metrics from the aggregation interval
            interval_start = time.time() - self.config["aggregation_interval"]
            interval_metrics = [
                m for m in metrics_list
                if datetime.fromisoformat(m["timestamp"]).timestamp() >= interval_start
            ]
            
            # Skip if no metrics in interval
            if not interval_metrics:
                continue
            
            # Aggregate based on category
            if category in ["cpu", "memory", "disk"]:
                usage_values = [m["data"]["usage_percent"] for m in interval_metrics]
                aggregated_metrics[category] = {
                    "avg_usage_percent": sum(usage_values) / len(usage_values),
                    "max_usage_percent": max(usage_values),
                    "min_usage_percent": min(usage_values)
                }
            
            elif category in ["deployment", "mission"]:
                success_rates = [m["data"]["success_rate"] for m in interval_metrics]
                failure_rates = [m["data"]["failure_rate"] for m in interval_metrics]
                durations = [m["data"]["average_duration"] for m in interval_metrics]
                
                aggregated_metrics[category] = {
                    "avg_success_rate": sum(success_rates) / len(success_rates),
                    "avg_failure_rate": sum(failure_rates) / len(failure_rates),
                    "avg_duration": sum(durations) / len(durations)
                }
            
            elif category == "layer":
                # Aggregate health metrics for each layer
                layer_health = {}
                for layer_name in interval_metrics[0]["data"].keys():
                    health_values = [m["data"][layer_name]["health"] for m in interval_metrics]
                    layer_health[layer_name] = sum(health_values) / len(health_values)
                
                aggregated_metrics["layer_health"] = layer_health
        
        # Store aggregated metrics
        if "aggregated" not in self.metrics_store:
            self.metrics_store["aggregated"] = []
        
        self.metrics_store["aggregated"].append({
            "timestamp": timestamp,
            "data": aggregated_metrics
        })
        
        logger.info("Metrics aggregation completed")
    
    def _cleanup_old_metrics(self):
        """
        Clean up old metrics data based on retention policy.
        """
        retention_time = time.time() - self.config["storage_retention"]
        
        for category, metrics_list in self.metrics_store.items():
            # Filter out old metrics
            self.metrics_store[category] = [
                m for m in metrics_list
                if datetime.fromisoformat(m["timestamp"]).timestamp() >= retention_time
            ]
        
        logger.info("Metrics cleanup completed")
    
    def get_metrics(self, category: str = None, start_time: str = None, end_time: str = None) -> Dict[str, Any]:
        """
        Get metrics data for a specific category and time range.
        
        Args:
            category: Category of metrics to retrieve (optional).
            start_time: Start time for metrics range (ISO format, optional).
            end_time: End time for metrics range (ISO format, optional).
            
        Returns:
            Dict containing the requested metrics.
        """
        result = {}
        
        # Convert times to timestamps if provided
        start_timestamp = None
        if start_time:
            start_timestamp = datetime.fromisoformat(start_time).timestamp()
        
        end_timestamp = None
        if end_time:
            end_timestamp = datetime.fromisoformat(end_time).timestamp()
        
        # If category is specified, return only that category
        if category:
            if category in self.metrics_store:
                # Filter by time range if specified
                if start_timestamp or end_timestamp:
                    filtered_metrics = []
                    for metric in self.metrics_store[category]:
                        metric_timestamp = datetime.fromisoformat(metric["timestamp"]).timestamp()
                        
                        if start_timestamp and metric_timestamp < start_timestamp:
                            continue
                        
                        if end_timestamp and metric_timestamp > end_timestamp:
                            continue
                        
                        filtered_metrics.append(metric)
                    
                    result[category] = filtered_metrics
                else:
                    result[category] = self.metrics_store[category]
            else:
                result[category] = []
        else:
            # Return all categories
            for cat, metrics in self.metrics_store.items():
                # Filter by time range if specified
                if start_timestamp or end_timestamp:
                    filtered_metrics = []
                    for metric in metrics:
                        metric_timestamp = datetime.fromisoformat(metric["timestamp"]).timestamp()
                        
                        if start_timestamp and metric_timestamp < start_timestamp:
                            continue
                        
                        if end_timestamp and metric_timestamp > end_timestamp:
                            continue
                        
                        filtered_metrics.append(metric)
                    
                    result[cat] = filtered_metrics
                else:
                    result[cat] = metrics
        
        return result
    
    def get_latest_metrics(self, category: str = None) -> Dict[str, Any]:
        """
        Get the latest metrics for a specific category or all categories.
        
        Args:
            category: Category of metrics to retrieve (optional).
            
        Returns:
            Dict containing the latest metrics.
        """
        result = {}
        
        # If category is specified, return only that category
        if category:
            if category in self.metrics_store and self.metrics_store[category]:
                result[category] = self.metrics_store[category][-1]
            else:
                result[category] = None
        else:
            # Return latest for all categories
            for cat, metrics in self.metrics_store.items():
                if metrics:
                    result[cat] = metrics[-1]
                else:
                    result[cat] = None
        
        return result
    
    def get_metrics_schema(self) -> Dict[str, Any]:
        """
        Get the schema for all metrics collected by the service.
        
        Returns:
            Dict containing the metrics schema.
        """
        return self.metrics_schema
    
    def export_metrics(self, category: str = None, format: str = "json", file_path: str = None) -> Optional[str]:
        """
        Export metrics data to a file in the specified format.
        
        Args:
            category: Category of metrics to export (optional).
            format: Export format (json, csv).
            file_path: Path to save the exported file.
            
        Returns:
            Path to the exported file, or None if export failed.
        """
        if format not in ["json", "csv"]:
            logger.error(f"Unsupported export format: {format}")
            return None
        
        # Get metrics to export
        metrics_to_export = self.get_metrics(category)
        
        # Generate default file path if not provided
        if not file_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            category_str = category if category else "all"
            file_path = f"/tmp/metrics_{category_str}_{timestamp}.{format}"
        
        try:
            if format == "json":
                with open(file_path, 'w') as f:
                    json.dump(metrics_to_export, f, indent=2)
            
            elif format == "csv":
                # CSV export would be implemented here
                # This is a simplified placeholder
                with open(file_path, 'w') as f:
                    f.write("category,timestamp,metric,value\n")
                    
                    for cat, metrics_list in metrics_to_export.items():
                        for metric_entry in metrics_list:
                            timestamp = metric_entry["timestamp"]
                            
                            if isinstance(metric_entry["data"], dict):
                                for metric_name, metric_value in metric_entry["data"].items():
                                    if isinstance(metric_value, dict):
                                        for sub_name, sub_value in metric_value.items():
                                            f.write(f"{cat},{timestamp},{metric_name}.{sub_name},{sub_value}\n")
                                    else:
                                        f.write(f"{cat},{timestamp},{metric_name},{metric_value}\n")
            
            logger.info(f"Metrics exported to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}")
            return None
