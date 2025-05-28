"""
Metrics Collector

This module provides a comprehensive metrics collection system for the Deployment Operations Layer.
It collects, processes, and stores metrics related to deployments, missions, capsules, and other
components of the system, enabling monitoring, analysis, and optimization of deployment operations.

The Metrics Collector is a critical component for ensuring the performance, reliability, and
efficiency of deployment operations across the Industriverse ecosystem.
"""

import logging
import json
import time
import uuid
import os
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import threading
import queue

logger = logging.getLogger(__name__)

class MetricsCollector:
    """
    Metrics Collector for the Deployment Operations Layer.
    
    This service collects, processes, and stores metrics related to deployments, missions,
    capsules, and other components of the system, enabling monitoring, analysis, and optimization
    of deployment operations.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Metrics Collector.
        
        Args:
            config: Configuration dictionary for the service
        """
        self.config = config or {}
        
        # Initialize service ID and version
        self.service_id = self.config.get("service_id", "metrics-collector")
        self.service_version = self.config.get("service_version", "1.0.0")
        
        # Initialize metrics store (in a real implementation, this would be a time-series database)
        self.metrics_store = {}
        
        # Initialize metrics definitions
        self.metrics_definitions = self._initialize_metrics_definitions()
        
        # Initialize collection intervals
        self.collection_intervals = self.config.get("collection_intervals", {
            "deployment": 60,  # 1 minute
            "mission": 30,     # 30 seconds
            "capsule": 60,     # 1 minute
            "system": 15,      # 15 seconds
            "resource": 30,    # 30 seconds
            "network": 15      # 15 seconds
        })
        
        # Initialize retention policies
        self.retention_policies = self.config.get("retention_policies", {
            "raw": 86400 * 7,       # 7 days
            "1m": 86400 * 30,       # 30 days
            "5m": 86400 * 90,       # 90 days
            "1h": 86400 * 365,      # 1 year
            "1d": 86400 * 365 * 3   # 3 years
        })
        
        # Initialize aggregation policies
        self.aggregation_policies = self.config.get("aggregation_policies", {
            "1m": ["avg", "min", "max", "sum", "count"],
            "5m": ["avg", "min", "max", "sum", "count"],
            "1h": ["avg", "min", "max", "sum", "count"],
            "1d": ["avg", "min", "max", "sum", "count"]
        })
        
        # Initialize collection threads
        self.collection_threads = {}
        self.collection_stop_events = {}
        
        # Initialize processing queue
        self.processing_queue = queue.Queue()
        self.processing_thread = None
        self.processing_stop_event = threading.Event()
        
        # Initialize aggregation threads
        self.aggregation_threads = {}
        self.aggregation_stop_events = {}
        
        logger.info(f"Metrics Collector initialized: {self.service_id}")
    
    def _initialize_metrics_definitions(self) -> Dict[str, Dict[str, Any]]:
        """
        Initialize metrics definitions.
        
        Returns:
            Dictionary of metrics definitions
        """
        return {
            # Deployment metrics
            "deployment.count": {
                "metric_id": "deployment.count",
                "name": "Deployment Count",
                "description": "Number of deployments",
                "unit": "count",
                "type": "counter",
                "category": "deployment",
                "tags": ["deployment"]
            },
            "deployment.success_rate": {
                "metric_id": "deployment.success_rate",
                "name": "Deployment Success Rate",
                "description": "Percentage of successful deployments",
                "unit": "percent",
                "type": "gauge",
                "category": "deployment",
                "tags": ["deployment", "success"]
            },
            "deployment.failure_rate": {
                "metric_id": "deployment.failure_rate",
                "name": "Deployment Failure Rate",
                "description": "Percentage of failed deployments",
                "unit": "percent",
                "type": "gauge",
                "category": "deployment",
                "tags": ["deployment", "failure"]
            },
            "deployment.duration": {
                "metric_id": "deployment.duration",
                "name": "Deployment Duration",
                "description": "Duration of deployments",
                "unit": "seconds",
                "type": "histogram",
                "category": "deployment",
                "tags": ["deployment", "duration"]
            },
            "deployment.resource_usage": {
                "metric_id": "deployment.resource_usage",
                "name": "Deployment Resource Usage",
                "description": "Resource usage of deployments",
                "unit": "percent",
                "type": "gauge",
                "category": "deployment",
                "tags": ["deployment", "resource"]
            },
            
            # Mission metrics
            "mission.count": {
                "metric_id": "mission.count",
                "name": "Mission Count",
                "description": "Number of missions",
                "unit": "count",
                "type": "counter",
                "category": "mission",
                "tags": ["mission"]
            },
            "mission.success_rate": {
                "metric_id": "mission.success_rate",
                "name": "Mission Success Rate",
                "description": "Percentage of successful missions",
                "unit": "percent",
                "type": "gauge",
                "category": "mission",
                "tags": ["mission", "success"]
            },
            "mission.failure_rate": {
                "metric_id": "mission.failure_rate",
                "name": "Mission Failure Rate",
                "description": "Percentage of failed missions",
                "unit": "percent",
                "type": "gauge",
                "category": "mission",
                "tags": ["mission", "failure"]
            },
            "mission.duration": {
                "metric_id": "mission.duration",
                "name": "Mission Duration",
                "description": "Duration of missions",
                "unit": "seconds",
                "type": "histogram",
                "category": "mission",
                "tags": ["mission", "duration"]
            },
            "mission.steps_completed": {
                "metric_id": "mission.steps_completed",
                "name": "Mission Steps Completed",
                "description": "Number of mission steps completed",
                "unit": "count",
                "type": "counter",
                "category": "mission",
                "tags": ["mission", "steps"]
            },
            
            # Capsule metrics
            "capsule.count": {
                "metric_id": "capsule.count",
                "name": "Capsule Count",
                "description": "Number of capsules",
                "unit": "count",
                "type": "counter",
                "category": "capsule",
                "tags": ["capsule"]
            },
            "capsule.instantiation_rate": {
                "metric_id": "capsule.instantiation_rate",
                "name": "Capsule Instantiation Rate",
                "description": "Rate of capsule instantiations",
                "unit": "count/second",
                "type": "gauge",
                "category": "capsule",
                "tags": ["capsule", "instantiation"]
            },
            "capsule.termination_rate": {
                "metric_id": "capsule.termination_rate",
                "name": "Capsule Termination Rate",
                "description": "Rate of capsule terminations",
                "unit": "count/second",
                "type": "gauge",
                "category": "capsule",
                "tags": ["capsule", "termination"]
            },
            "capsule.uptime": {
                "metric_id": "capsule.uptime",
                "name": "Capsule Uptime",
                "description": "Uptime of capsules",
                "unit": "seconds",
                "type": "gauge",
                "category": "capsule",
                "tags": ["capsule", "uptime"]
            },
            "capsule.health": {
                "metric_id": "capsule.health",
                "name": "Capsule Health",
                "description": "Health status of capsules",
                "unit": "percent",
                "type": "gauge",
                "category": "capsule",
                "tags": ["capsule", "health"]
            },
            
            # System metrics
            "system.cpu_usage": {
                "metric_id": "system.cpu_usage",
                "name": "CPU Usage",
                "description": "CPU usage of the system",
                "unit": "percent",
                "type": "gauge",
                "category": "system",
                "tags": ["system", "cpu"]
            },
            "system.memory_usage": {
                "metric_id": "system.memory_usage",
                "name": "Memory Usage",
                "description": "Memory usage of the system",
                "unit": "percent",
                "type": "gauge",
                "category": "system",
                "tags": ["system", "memory"]
            },
            "system.disk_usage": {
                "metric_id": "system.disk_usage",
                "name": "Disk Usage",
                "description": "Disk usage of the system",
                "unit": "percent",
                "type": "gauge",
                "category": "system",
                "tags": ["system", "disk"]
            },
            "system.network_throughput": {
                "metric_id": "system.network_throughput",
                "name": "Network Throughput",
                "description": "Network throughput of the system",
                "unit": "bytes/second",
                "type": "gauge",
                "category": "system",
                "tags": ["system", "network"]
            },
            "system.request_rate": {
                "metric_id": "system.request_rate",
                "name": "Request Rate",
                "description": "Rate of requests to the system",
                "unit": "count/second",
                "type": "gauge",
                "category": "system",
                "tags": ["system", "requests"]
            },
            
            # Resource metrics
            "resource.utilization": {
                "metric_id": "resource.utilization",
                "name": "Resource Utilization",
                "description": "Utilization of resources",
                "unit": "percent",
                "type": "gauge",
                "category": "resource",
                "tags": ["resource", "utilization"]
            },
            "resource.availability": {
                "metric_id": "resource.availability",
                "name": "Resource Availability",
                "description": "Availability of resources",
                "unit": "percent",
                "type": "gauge",
                "category": "resource",
                "tags": ["resource", "availability"]
            },
            "resource.allocation_rate": {
                "metric_id": "resource.allocation_rate",
                "name": "Resource Allocation Rate",
                "description": "Rate of resource allocations",
                "unit": "count/second",
                "type": "gauge",
                "category": "resource",
                "tags": ["resource", "allocation"]
            },
            "resource.deallocation_rate": {
                "metric_id": "resource.deallocation_rate",
                "name": "Resource Deallocation Rate",
                "description": "Rate of resource deallocations",
                "unit": "count/second",
                "type": "gauge",
                "category": "resource",
                "tags": ["resource", "deallocation"]
            },
            "resource.contention": {
                "metric_id": "resource.contention",
                "name": "Resource Contention",
                "description": "Contention for resources",
                "unit": "count",
                "type": "gauge",
                "category": "resource",
                "tags": ["resource", "contention"]
            },
            
            # Network metrics
            "network.latency": {
                "metric_id": "network.latency",
                "name": "Network Latency",
                "description": "Latency of network communications",
                "unit": "milliseconds",
                "type": "histogram",
                "category": "network",
                "tags": ["network", "latency"]
            },
            "network.throughput": {
                "metric_id": "network.throughput",
                "name": "Network Throughput",
                "description": "Throughput of network communications",
                "unit": "bytes/second",
                "type": "gauge",
                "category": "network",
                "tags": ["network", "throughput"]
            },
            "network.packet_loss": {
                "metric_id": "network.packet_loss",
                "name": "Network Packet Loss",
                "description": "Packet loss in network communications",
                "unit": "percent",
                "type": "gauge",
                "category": "network",
                "tags": ["network", "packet_loss"]
            },
            "network.connection_count": {
                "metric_id": "network.connection_count",
                "name": "Network Connection Count",
                "description": "Number of network connections",
                "unit": "count",
                "type": "gauge",
                "category": "network",
                "tags": ["network", "connections"]
            },
            "network.error_rate": {
                "metric_id": "network.error_rate",
                "name": "Network Error Rate",
                "description": "Rate of network errors",
                "unit": "count/second",
                "type": "gauge",
                "category": "network",
                "tags": ["network", "errors"]
            }
        }
    
    def start(self) -> None:
        """
        Start the Metrics Collector.
        """
        logger.info("Starting Metrics Collector")
        
        # Start collection threads
        for category, interval in self.collection_intervals.items():
            self._start_collection_thread(category, interval)
        
        # Start processing thread
        self._start_processing_thread()
        
        # Start aggregation threads
        for resolution, aggregations in self.aggregation_policies.items():
            self._start_aggregation_thread(resolution, aggregations)
        
        logger.info("Metrics Collector started")
    
    def stop(self) -> None:
        """
        Stop the Metrics Collector.
        """
        logger.info("Stopping Metrics Collector")
        
        # Stop collection threads
        for category, stop_event in self.collection_stop_events.items():
            logger.info(f"Stopping collection thread for category: {category}")
            stop_event.set()
        
        # Stop processing thread
        if self.processing_thread is not None:
            logger.info("Stopping processing thread")
            self.processing_stop_event.set()
            self.processing_thread.join()
        
        # Stop aggregation threads
        for resolution, stop_event in self.aggregation_stop_events.items():
            logger.info(f"Stopping aggregation thread for resolution: {resolution}")
            stop_event.set()
        
        # Wait for all threads to stop
        for category, thread in self.collection_threads.items():
            thread.join()
        
        for resolution, thread in self.aggregation_threads.items():
            thread.join()
        
        logger.info("Metrics Collector stopped")
    
    def _start_collection_thread(self, category: str, interval: int) -> None:
        """
        Start a collection thread for a category.
        
        Args:
            category: Metrics category
            interval: Collection interval in seconds
        """
        logger.info(f"Starting collection thread for category: {category}")
        
        stop_event = threading.Event()
        self.collection_stop_events[category] = stop_event
        
        thread = threading.Thread(
            target=self._collection_thread,
            args=(category, interval, stop_event),
            daemon=True
        )
        
        self.collection_threads[category] = thread
        thread.start()
    
    def _collection_thread(self, category: str, interval: int, stop_event: threading.Event) -> None:
        """
        Collection thread function.
        
        Args:
            category: Metrics category
            interval: Collection interval in seconds
            stop_event: Stop event
        """
        logger.info(f"Collection thread started for category: {category}")
        
        while not stop_event.is_set():
            try:
                # Collect metrics for the category
                metrics = self._collect_metrics(category)
                
                # Queue metrics for processing
                for metric in metrics:
                    self.processing_queue.put(metric)
                
                # Sleep until next collection
                stop_event.wait(interval)
            except Exception as e:
                logger.error(f"Error in collection thread for category {category}: {str(e)}", exc_info=True)
                # Sleep a bit before retrying
                stop_event.wait(5)
        
        logger.info(f"Collection thread stopped for category: {category}")
    
    def _start_processing_thread(self) -> None:
        """
        Start the processing thread.
        """
        logger.info("Starting processing thread")
        
        self.processing_stop_event = threading.Event()
        
        self.processing_thread = threading.Thread(
            target=self._processing_thread,
            args=(self.processing_stop_event,),
            daemon=True
        )
        
        self.processing_thread.start()
    
    def _processing_thread(self, stop_event: threading.Event) -> None:
        """
        Processing thread function.
        
        Args:
            stop_event: Stop event
        """
        logger.info("Processing thread started")
        
        while not stop_event.is_set():
            try:
                # Get metric from queue with timeout
                try:
                    metric = self.processing_queue.get(timeout=1)
                except queue.Empty:
                    continue
                
                # Process metric
                self._process_metric(metric)
                
                # Mark task as done
                self.processing_queue.task_done()
            except Exception as e:
                logger.error(f"Error in processing thread: {str(e)}", exc_info=True)
                # Sleep a bit before retrying
                stop_event.wait(1)
        
        logger.info("Processing thread stopped")
    
    def _start_aggregation_thread(self, resolution: str, aggregations: List[str]) -> None:
        """
        Start an aggregation thread for a resolution.
        
        Args:
            resolution: Time resolution (e.g., "1m", "5m", "1h", "1d")
            aggregations: List of aggregation functions
        """
        logger.info(f"Starting aggregation thread for resolution: {resolution}")
        
        stop_event = threading.Event()
        self.aggregation_stop_events[resolution] = stop_event
        
        thread = threading.Thread(
            target=self._aggregation_thread,
            args=(resolution, aggregations, stop_event),
            daemon=True
        )
        
        self.aggregation_threads[resolution] = thread
        thread.start()
    
    def _aggregation_thread(self, resolution: str, aggregations: List[str], stop_event: threading.Event) -> None:
        """
        Aggregation thread function.
        
        Args:
            resolution: Time resolution (e.g., "1m", "5m", "1h", "1d")
            aggregations: List of aggregation functions
            stop_event: Stop event
        """
        logger.info(f"Aggregation thread started for resolution: {resolution}")
        
        # Determine aggregation interval
        interval = self._resolution_to_seconds(resolution)
        
        while not stop_event.is_set():
            try:
                # Perform aggregation
                self._aggregate_metrics(resolution, aggregations)
                
                # Sleep until next aggregation
                stop_event.wait(interval)
            except Exception as e:
                logger.error(f"Error in aggregation thread for resolution {resolution}: {str(e)}", exc_info=True)
                # Sleep a bit before retrying
                stop_event.wait(5)
        
        logger.info(f"Aggregation thread stopped for resolution: {resolution}")
    
    def _resolution_to_seconds(self, resolution: str) -> int:
        """
        Convert a time resolution to seconds.
        
        Args:
            resolution: Time resolution (e.g., "1m", "5m", "1h", "1d")
            
        Returns:
            Number of seconds
        """
        if resolution == "1m":
            return 60
        elif resolution == "5m":
            return 300
        elif resolution == "1h":
            return 3600
        elif resolution == "1d":
            return 86400
        else:
            raise ValueError(f"Invalid resolution: {resolution}")
    
    def _collect_metrics(self, category: str) -> List[Dict[str, Any]]:
        """
        Collect metrics for a category.
        
        Args:
            category: Metrics category
            
        Returns:
            List of collected metrics
        """
        logger.debug(f"Collecting metrics for category: {category}")
        
        # In a real implementation, this would collect metrics from various sources
        # For this example, we'll generate some random metrics
        
        metrics = []
        
        # Get metrics definitions for the category
        category_metrics = [m for m in self.metrics_definitions.values() if m["category"] == category]
        
        # Generate a metric for each definition
        for metric_def in category_metrics:
            metric_id = metric_def["metric_id"]
            
            # Generate a random value based on the metric type
            if metric_def["type"] == "counter":
                value = 1  # Increment by 1
            elif metric_def["type"] == "gauge":
                value = 50 + (time.time() % 50)  # Random value between 50 and 100
            elif metric_def["type"] == "histogram":
                value = 100 + (time.time() % 900)  # Random value between 100 and 1000
            else:
                value = 0
            
            # Create metric
            metric = {
                "metric_id": metric_id,
                "value": value,
                "timestamp": time.time(),
                "tags": metric_def["tags"].copy(),
                "dimensions": {
                    "environment": "production",
                    "region": "us-west-1",
                    "instance": "instance-1"
                }
            }
            
            metrics.append(metric)
        
        logger.debug(f"Collected {len(metrics)} metrics for category: {category}")
        
        return metrics
    
    def _process_metric(self, metric: Dict[str, Any]) -> None:
        """
        Process a metric.
        
        Args:
            metric: Metric to process
        """
        logger.debug(f"Processing metric: {metric['metric_id']}")
        
        # Get metric definition
        metric_def = self.metrics_definitions.get(metric["metric_id"])
        if metric_def is None:
            logger.warning(f"Unknown metric: {metric['metric_id']}")
            return
        
        # Store raw metric
        self._store_metric(metric, "raw")
        
        logger.debug(f"Processed metric: {metric['metric_id']}")
    
    def _store_metric(self, metric: Dict[str, Any], resolution: str) -> None:
        """
        Store a metric.
        
        Args:
            metric: Metric to store
            resolution: Time resolution (e.g., "raw", "1m", "5m", "1h", "1d")
        """
        # In a real implementation, this would store the metric in a time-series database
        # For this example, we'll store it in memory
        
        # Create store for resolution if it doesn't exist
        if resolution not in self.metrics_store:
            self.metrics_store[resolution] = {}
        
        # Create store for metric if it doesn't exist
        metric_id = metric["metric_id"]
        if metric_id not in self.metrics_store[resolution]:
            self.metrics_store[resolution][metric_id] = []
        
        # Store metric
        self.metrics_store[resolution][metric_id].append(metric)
        
        # Apply retention policy
        self._apply_retention_policy(resolution)
    
    def _apply_retention_policy(self, resolution: str) -> None:
        """
        Apply retention policy for a resolution.
        
        Args:
            resolution: Time resolution (e.g., "raw", "1m", "5m", "1h", "1d")
        """
        # Get retention period
        retention_period = self.retention_policies.get(resolution)
        if retention_period is None:
            return
        
        # Get current time
        current_time = time.time()
        
        # Apply retention policy to each metric
        for metric_id, metrics in self.metrics_store[resolution].items():
            # Remove metrics older than retention period
            self.metrics_store[resolution][metric_id] = [
                m for m in metrics
                if current_time - m["timestamp"] <= retention_period
            ]
    
    def _aggregate_metrics(self, resolution: str, aggregations: List[str]) -> None:
        """
        Aggregate metrics for a resolution.
        
        Args:
            resolution: Time resolution (e.g., "1m", "5m", "1h", "1d")
            aggregations: List of aggregation functions
        """
        logger.debug(f"Aggregating metrics for resolution: {resolution}")
        
        # Get current time
        current_time = time.time()
        
        # Get interval
        interval = self._resolution_to_seconds(resolution)
        
        # Get start time for aggregation window
        start_time = current_time - interval
        
        # Aggregate metrics for each metric ID
        for metric_id, metrics in self.metrics_store.get("raw", {}).items():
            # Get metrics in the aggregation window
            window_metrics = [
                m for m in metrics
                if m["timestamp"] >= start_time
            ]
            
            # Skip if no metrics in window
            if not window_metrics:
                continue
            
            # Get metric definition
            metric_def = self.metrics_definitions.get(metric_id)
            if metric_def is None:
                continue
            
            # Perform aggregations
            for aggregation in aggregations:
                # Skip if aggregation not applicable to metric type
                if not self._is_aggregation_applicable(metric_def["type"], aggregation):
                    continue
                
                # Perform aggregation
                aggregated_value = self._perform_aggregation(window_metrics, aggregation)
                
                # Create aggregated metric
                aggregated_metric = {
                    "metric_id": f"{metric_id}.{aggregation}",
                    "value": aggregated_value,
                    "timestamp": current_time,
                    "tags": metric_def["tags"].copy() + [aggregation],
                    "dimensions": {
                        "environment": "production",
                        "region": "us-west-1",
                        "instance": "instance-1",
                        "resolution": resolution,
                        "aggregation": aggregation
                    }
                }
                
                # Store aggregated metric
                self._store_metric(aggregated_metric, resolution)
        
        logger.debug(f"Aggregated metrics for resolution: {resolution}")
    
    def _is_aggregation_applicable(self, metric_type: str, aggregation: str) -> bool:
        """
        Check if an aggregation is applicable to a metric type.
        
        Args:
            metric_type: Metric type
            aggregation: Aggregation function
            
        Returns:
            True if the aggregation is applicable, False otherwise
        """
        if metric_type == "counter":
            return aggregation in ["sum", "count"]
        elif metric_type == "gauge":
            return aggregation in ["avg", "min", "max", "sum", "count"]
        elif metric_type == "histogram":
            return aggregation in ["avg", "min", "max", "sum", "count", "p50", "p90", "p95", "p99"]
        else:
            return False
    
    def _perform_aggregation(self, metrics: List[Dict[str, Any]], aggregation: str) -> float:
        """
        Perform an aggregation on a list of metrics.
        
        Args:
            metrics: List of metrics
            aggregation: Aggregation function
            
        Returns:
            Aggregated value
        """
        values = [m["value"] for m in metrics]
        
        if aggregation == "avg":
            return sum(values) / len(values) if values else 0
        elif aggregation == "min":
            return min(values) if values else 0
        elif aggregation == "max":
            return max(values) if values else 0
        elif aggregation == "sum":
            return sum(values)
        elif aggregation == "count":
            return len(values)
        elif aggregation == "p50":
            return self._percentile(values, 50)
        elif aggregation == "p90":
            return self._percentile(values, 90)
        elif aggregation == "p95":
            return self._percentile(values, 95)
        elif aggregation == "p99":
            return self._percentile(values, 99)
        else:
            return 0
    
    def _percentile(self, values: List[float], percentile: int) -> float:
        """
        Calculate a percentile of a list of values.
        
        Args:
            values: List of values
            percentile: Percentile to calculate
            
        Returns:
            Percentile value
        """
        if not values:
            return 0
        
        # Sort values
        sorted_values = sorted(values)
        
        # Calculate index
        k = (len(sorted_values) - 1) * percentile / 100
        f = int(k)
        c = int(k) + 1 if k > f else f
        
        # Handle edge cases
        if f >= len(sorted_values):
            return sorted_values[-1]
        elif c >= len(sorted_values):
            return sorted_values[-1]
        
        # Interpolate
        d0 = sorted_values[f] * (c - k)
        d1 = sorted_values[c] * (k - f)
        return d0 + d1
    
    def record_metric(self, metric_id: str, value: float, tags: Dict[str, str] = None, dimensions: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Record a metric.
        
        Args:
            metric_id: Metric ID
            value: Metric value
            tags: Additional tags
            dimensions: Additional dimensions
            
        Returns:
            Metric recording result dictionary
        """
        logger.info(f"Recording metric: {metric_id}")
        
        # Get metric definition
        metric_def = self.metrics_definitions.get(metric_id)
        if metric_def is None:
            logger.warning(f"Unknown metric: {metric_id}")
            return {
                "status": "error",
                "message": f"Unknown metric: {metric_id}",
                "recorded": False
            }
        
        # Create metric
        metric = {
            "metric_id": metric_id,
            "value": value,
            "timestamp": time.time(),
            "tags": metric_def["tags"].copy(),
            "dimensions": {
                "environment": "production",
                "region": "us-west-1",
                "instance": "instance-1"
            }
        }
        
        # Add additional tags
        if tags:
            metric["tags"].extend(tags.values())
        
        # Add additional dimensions
        if dimensions:
            metric["dimensions"].update(dimensions)
        
        # Queue metric for processing
        self.processing_queue.put(metric)
        
        logger.info(f"Metric recorded: {metric_id}")
        
        return {
            "status": "success",
            "message": "Metric recorded successfully",
            "recorded": True,
            "metric": metric
        }
    
    def get_metrics(self, metric_id: str, resolution: str = "raw", start_time: float = None, end_time: float = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get metrics.
        
        Args:
            metric_id: Metric ID
            resolution: Time resolution (e.g., "raw", "1m", "5m", "1h", "1d")
            start_time: Start time (Unix timestamp)
            end_time: End time (Unix timestamp)
            limit: Maximum number of metrics to return
            
        Returns:
            Dictionary containing list of metrics
        """
        logger.info(f"Getting metrics: {metric_id}, resolution: {resolution}")
        
        # Check if resolution exists
        if resolution not in self.metrics_store:
            logger.warning(f"Resolution not found: {resolution}")
            return {
                "status": "error",
                "message": f"Resolution not found: {resolution}",
                "found": False
            }
        
        # Check if metric exists
        if metric_id not in self.metrics_store[resolution]:
            logger.warning(f"Metric not found: {metric_id}")
            return {
                "status": "error",
                "message": f"Metric not found: {metric_id}",
                "found": False
            }
        
        # Get metrics
        metrics = self.metrics_store[resolution][metric_id]
        
        # Apply time filters
        if start_time is not None:
            metrics = [m for m in metrics if m["timestamp"] >= start_time]
        
        if end_time is not None:
            metrics = [m for m in metrics if m["timestamp"] <= end_time]
        
        # Sort by timestamp (newest first)
        metrics.sort(key=lambda m: m["timestamp"], reverse=True)
        
        # Apply limit
        metrics = metrics[:limit]
        
        logger.info(f"Got {len(metrics)} metrics: {metric_id}, resolution: {resolution}")
        
        return {
            "status": "success",
            "message": "Metrics retrieved successfully",
            "found": True,
            "metrics": metrics
        }
    
    def get_latest_metric(self, metric_id: str, resolution: str = "raw") -> Dict[str, Any]:
        """
        Get the latest metric.
        
        Args:
            metric_id: Metric ID
            resolution: Time resolution (e.g., "raw", "1m", "5m", "1h", "1d")
            
        Returns:
            Dictionary containing the latest metric
        """
        logger.info(f"Getting latest metric: {metric_id}, resolution: {resolution}")
        
        # Get metrics
        result = self.get_metrics(metric_id, resolution, limit=1)
        
        if not result.get("found", False):
            return result
        
        metrics = result.get("metrics", [])
        
        if not metrics:
            logger.warning(f"No metrics found: {metric_id}")
            return {
                "status": "error",
                "message": "No metrics found",
                "found": False
            }
        
        logger.info(f"Got latest metric: {metric_id}, resolution: {resolution}")
        
        return {
            "status": "success",
            "message": "Latest metric retrieved successfully",
            "found": True,
            "metric": metrics[0]
        }
    
    def get_metric_definition(self, metric_id: str) -> Dict[str, Any]:
        """
        Get a metric definition.
        
        Args:
            metric_id: Metric ID
            
        Returns:
            Metric definition dictionary
        """
        logger.info(f"Getting metric definition: {metric_id}")
        
        # Check if metric exists
        if metric_id not in self.metrics_definitions:
            logger.warning(f"Metric definition not found: {metric_id}")
            return {
                "status": "error",
                "message": f"Metric definition not found: {metric_id}",
                "found": False
            }
        
        # Get metric definition
        definition = self.metrics_definitions[metric_id]
        
        logger.info(f"Got metric definition: {metric_id}")
        
        return {
            "status": "success",
            "message": "Metric definition retrieved successfully",
            "found": True,
            "definition": definition
        }
    
    def list_metric_definitions(self, category: str = None) -> Dict[str, Any]:
        """
        List metric definitions.
        
        Args:
            category: Filter by category
            
        Returns:
            Dictionary containing list of metric definitions
        """
        logger.info("Listing metric definitions")
        
        # Get definitions
        definitions = list(self.metrics_definitions.values())
        
        # Apply category filter
        if category is not None:
            definitions = [d for d in definitions if d["category"] == category]
        
        logger.info(f"Listed {len(definitions)} metric definitions")
        
        return {
            "status": "success",
            "message": "Metric definitions listed successfully",
            "definitions": definitions
        }
    
    def get_collection_status(self) -> Dict[str, Any]:
        """
        Get collection status.
        
        Returns:
            Dictionary containing collection status
        """
        logger.info("Getting collection status")
        
        # Get status for each category
        status = {}
        
        for category, interval in self.collection_intervals.items():
            thread = self.collection_threads.get(category)
            stop_event = self.collection_stop_events.get(category)
            
            status[category] = {
                "interval": interval,
                "running": thread is not None and thread.is_alive(),
                "stopping": stop_event is not None and stop_event.is_set()
            }
        
        logger.info("Got collection status")
        
        return {
            "status": "success",
            "message": "Collection status retrieved successfully",
            "collection_status": status
        }
    
    def get_aggregation_status(self) -> Dict[str, Any]:
        """
        Get aggregation status.
        
        Returns:
            Dictionary containing aggregation status
        """
        logger.info("Getting aggregation status")
        
        # Get status for each resolution
        status = {}
        
        for resolution, aggregations in self.aggregation_policies.items():
            thread = self.aggregation_threads.get(resolution)
            stop_event = self.aggregation_stop_events.get(resolution)
            
            status[resolution] = {
                "aggregations": aggregations,
                "running": thread is not None and thread.is_alive(),
                "stopping": stop_event is not None and stop_event.is_set()
            }
        
        logger.info("Got aggregation status")
        
        return {
            "status": "success",
            "message": "Aggregation status retrieved successfully",
            "aggregation_status": status
        }
    
    def get_processing_status(self) -> Dict[str, Any]:
        """
        Get processing status.
        
        Returns:
            Dictionary containing processing status
        """
        logger.info("Getting processing status")
        
        status = {
            "queue_size": self.processing_queue.qsize(),
            "running": self.processing_thread is not None and self.processing_thread.is_alive(),
            "stopping": self.processing_stop_event is not None and self.processing_stop_event.is_set()
        }
        
        logger.info("Got processing status")
        
        return {
            "status": "success",
            "message": "Processing status retrieved successfully",
            "processing_status": status
        }
    
    def get_storage_status(self) -> Dict[str, Any]:
        """
        Get storage status.
        
        Returns:
            Dictionary containing storage status
        """
        logger.info("Getting storage status")
        
        # Get status for each resolution
        status = {}
        
        for resolution, metrics in self.metrics_store.items():
            status[resolution] = {
                "metric_count": len(metrics),
                "data_points": sum(len(m) for m in metrics.values())
            }
        
        logger.info("Got storage status")
        
        return {
            "status": "success",
            "message": "Storage status retrieved successfully",
            "storage_status": status
        }
