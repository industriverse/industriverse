"""
Analytics Manager for the Deployment Operations Layer

This module provides comprehensive analytics and monitoring capabilities for the
Deployment Operations Layer, implementing real-time metrics collection, visualization,
customizable dashboards, alerting, and predictive analytics.

The analytics framework supports metrics collection, data processing, visualization,
alerting, and predictive analytics for deployment operations.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta

# Configure logging
logger = logging.getLogger(__name__)

class AnalyticsManager:
    """Analytics manager for comprehensive monitoring and analytics"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the analytics manager
        
        Args:
            config: Configuration for the analytics manager
        """
        self.config = config or {}
        self.metrics = {}
        self.alerts = {}
        self.dashboards = {}
        self.reports = {}
        self.predictions = {}
        self.status = "initialized"
        
        # Initialize metrics storage
        self.metrics_store = {
            "deployment": {},
            "mission": {},
            "capsule": {},
            "layer": {},
            "compliance": {},
            "performance": {},
            "security": {},
            "user": {}
        }
        
        logger.info("Initialized analytics manager")
    
    async def initialize(self):
        """Initialize the analytics manager"""
        try:
            # Initialize metrics collection
            await self._initialize_metrics_collection()
            
            # Initialize alerting
            await self._initialize_alerting()
            
            # Initialize dashboards
            await self._initialize_dashboards()
            
            # Initialize predictive analytics
            await self._initialize_predictive_analytics()
            
            self.status = "ready"
            logger.info("Analytics manager initialized successfully")
            
            return {
                "status": "success"
            }
        except Exception as e:
            self.status = "error"
            logger.error(f"Failed to initialize analytics manager: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _initialize_metrics_collection(self):
        """Initialize metrics collection"""
        try:
            # In a real implementation, this would set up metrics collectors
            # For demonstration, we'll create sample metrics definitions
            self.metrics = {
                "deployment_count": {
                    "id": "deployment_count",
                    "name": "Deployment Count",
                    "description": "Number of deployments",
                    "type": "counter",
                    "unit": "count",
                    "category": "deployment"
                },
                "deployment_success_rate": {
                    "id": "deployment_success_rate",
                    "name": "Deployment Success Rate",
                    "description": "Percentage of successful deployments",
                    "type": "gauge",
                    "unit": "percent",
                    "category": "deployment"
                },
                "deployment_duration": {
                    "id": "deployment_duration",
                    "name": "Deployment Duration",
                    "description": "Duration of deployments",
                    "type": "histogram",
                    "unit": "seconds",
                    "category": "deployment"
                },
                "mission_count": {
                    "id": "mission_count",
                    "name": "Mission Count",
                    "description": "Number of missions",
                    "type": "counter",
                    "unit": "count",
                    "category": "mission"
                },
                "mission_success_rate": {
                    "id": "mission_success_rate",
                    "name": "Mission Success Rate",
                    "description": "Percentage of successful missions",
                    "type": "gauge",
                    "unit": "percent",
                    "category": "mission"
                },
                "mission_duration": {
                    "id": "mission_duration",
                    "name": "Mission Duration",
                    "description": "Duration of missions",
                    "type": "histogram",
                    "unit": "seconds",
                    "category": "mission"
                },
                "capsule_count": {
                    "id": "capsule_count",
                    "name": "Capsule Count",
                    "description": "Number of capsules",
                    "type": "counter",
                    "unit": "count",
                    "category": "capsule"
                },
                "capsule_health": {
                    "id": "capsule_health",
                    "name": "Capsule Health",
                    "description": "Health score of capsules",
                    "type": "gauge",
                    "unit": "score",
                    "category": "capsule"
                },
                "layer_deployment_count": {
                    "id": "layer_deployment_count",
                    "name": "Layer Deployment Count",
                    "description": "Number of deployments per layer",
                    "type": "counter",
                    "unit": "count",
                    "category": "layer"
                },
                "layer_deployment_success_rate": {
                    "id": "layer_deployment_success_rate",
                    "name": "Layer Deployment Success Rate",
                    "description": "Percentage of successful deployments per layer",
                    "type": "gauge",
                    "unit": "percent",
                    "category": "layer"
                },
                "compliance_check_count": {
                    "id": "compliance_check_count",
                    "name": "Compliance Check Count",
                    "description": "Number of compliance checks",
                    "type": "counter",
                    "unit": "count",
                    "category": "compliance"
                },
                "compliance_pass_rate": {
                    "id": "compliance_pass_rate",
                    "name": "Compliance Pass Rate",
                    "description": "Percentage of passed compliance checks",
                    "type": "gauge",
                    "unit": "percent",
                    "category": "compliance"
                },
                "resource_utilization": {
                    "id": "resource_utilization",
                    "name": "Resource Utilization",
                    "description": "Utilization of resources",
                    "type": "gauge",
                    "unit": "percent",
                    "category": "performance"
                },
                "response_time": {
                    "id": "response_time",
                    "name": "Response Time",
                    "description": "Response time of operations",
                    "type": "histogram",
                    "unit": "milliseconds",
                    "category": "performance"
                },
                "security_incident_count": {
                    "id": "security_incident_count",
                    "name": "Security Incident Count",
                    "description": "Number of security incidents",
                    "type": "counter",
                    "unit": "count",
                    "category": "security"
                },
                "security_score": {
                    "id": "security_score",
                    "name": "Security Score",
                    "description": "Security score",
                    "type": "gauge",
                    "unit": "score",
                    "category": "security"
                },
                "user_action_count": {
                    "id": "user_action_count",
                    "name": "User Action Count",
                    "description": "Number of user actions",
                    "type": "counter",
                    "unit": "count",
                    "category": "user"
                },
                "user_satisfaction": {
                    "id": "user_satisfaction",
                    "name": "User Satisfaction",
                    "description": "User satisfaction score",
                    "type": "gauge",
                    "unit": "score",
                    "category": "user"
                }
            }
            
            logger.info(f"Initialized {len(self.metrics)} metrics definitions")
        except Exception as e:
            logger.error(f"Failed to initialize metrics collection: {str(e)}")
            raise
    
    async def _initialize_alerting(self):
        """Initialize alerting"""
        try:
            # In a real implementation, this would set up alerting rules
            # For demonstration, we'll create sample alert definitions
            self.alerts = {
                "deployment_failure": {
                    "id": "deployment_failure",
                    "name": "Deployment Failure",
                    "description": "Alert when a deployment fails",
                    "metric_id": "deployment_success_rate",
                    "condition": "< 100",
                    "severity": "high",
                    "notification_channels": ["email", "slack"]
                },
                "mission_failure": {
                    "id": "mission_failure",
                    "name": "Mission Failure",
                    "description": "Alert when a mission fails",
                    "metric_id": "mission_success_rate",
                    "condition": "< 100",
                    "severity": "high",
                    "notification_channels": ["email", "slack"]
                },
                "capsule_health_critical": {
                    "id": "capsule_health_critical",
                    "name": "Capsule Health Critical",
                    "description": "Alert when capsule health is critical",
                    "metric_id": "capsule_health",
                    "condition": "< 50",
                    "severity": "critical",
                    "notification_channels": ["email", "slack", "pager"]
                },
                "compliance_failure": {
                    "id": "compliance_failure",
                    "name": "Compliance Failure",
                    "description": "Alert when compliance checks fail",
                    "metric_id": "compliance_pass_rate",
                    "condition": "< 100",
                    "severity": "high",
                    "notification_channels": ["email", "slack"]
                },
                "high_resource_utilization": {
                    "id": "high_resource_utilization",
                    "name": "High Resource Utilization",
                    "description": "Alert when resource utilization is high",
                    "metric_id": "resource_utilization",
                    "condition": "> 80",
                    "severity": "medium",
                    "notification_channels": ["email", "slack"]
                },
                "slow_response_time": {
                    "id": "slow_response_time",
                    "name": "Slow Response Time",
                    "description": "Alert when response time is slow",
                    "metric_id": "response_time",
                    "condition": "> 1000",
                    "severity": "medium",
                    "notification_channels": ["email", "slack"]
                },
                "security_incident": {
                    "id": "security_incident",
                    "name": "Security Incident",
                    "description": "Alert when a security incident occurs",
                    "metric_id": "security_incident_count",
                    "condition": "> 0",
                    "severity": "critical",
                    "notification_channels": ["email", "slack", "pager"]
                },
                "low_security_score": {
                    "id": "low_security_score",
                    "name": "Low Security Score",
                    "description": "Alert when security score is low",
                    "metric_id": "security_score",
                    "condition": "< 70",
                    "severity": "high",
                    "notification_channels": ["email", "slack"]
                },
                "low_user_satisfaction": {
                    "id": "low_user_satisfaction",
                    "name": "Low User Satisfaction",
                    "description": "Alert when user satisfaction is low",
                    "metric_id": "user_satisfaction",
                    "condition": "< 70",
                    "severity": "medium",
                    "notification_channels": ["email", "slack"]
                }
            }
            
            logger.info(f"Initialized {len(self.alerts)} alert definitions")
        except Exception as e:
            logger.error(f"Failed to initialize alerting: {str(e)}")
            raise
    
    async def _initialize_dashboards(self):
        """Initialize dashboards"""
        try:
            # In a real implementation, this would set up dashboard definitions
            # For demonstration, we'll create sample dashboard definitions
            self.dashboards = {
                "deployment_overview": {
                    "id": "deployment_overview",
                    "name": "Deployment Overview",
                    "description": "Overview of deployment metrics",
                    "panels": [
                        {
                            "id": "deployment_count_panel",
                            "name": "Deployment Count",
                            "type": "counter",
                            "metric_id": "deployment_count",
                            "position": {"x": 0, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "deployment_success_rate_panel",
                            "name": "Deployment Success Rate",
                            "type": "gauge",
                            "metric_id": "deployment_success_rate",
                            "position": {"x": 6, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "deployment_duration_panel",
                            "name": "Deployment Duration",
                            "type": "histogram",
                            "metric_id": "deployment_duration",
                            "position": {"x": 0, "y": 4, "w": 12, "h": 8}
                        }
                    ]
                },
                "mission_overview": {
                    "id": "mission_overview",
                    "name": "Mission Overview",
                    "description": "Overview of mission metrics",
                    "panels": [
                        {
                            "id": "mission_count_panel",
                            "name": "Mission Count",
                            "type": "counter",
                            "metric_id": "mission_count",
                            "position": {"x": 0, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "mission_success_rate_panel",
                            "name": "Mission Success Rate",
                            "type": "gauge",
                            "metric_id": "mission_success_rate",
                            "position": {"x": 6, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "mission_duration_panel",
                            "name": "Mission Duration",
                            "type": "histogram",
                            "metric_id": "mission_duration",
                            "position": {"x": 0, "y": 4, "w": 12, "h": 8}
                        }
                    ]
                },
                "capsule_overview": {
                    "id": "capsule_overview",
                    "name": "Capsule Overview",
                    "description": "Overview of capsule metrics",
                    "panels": [
                        {
                            "id": "capsule_count_panel",
                            "name": "Capsule Count",
                            "type": "counter",
                            "metric_id": "capsule_count",
                            "position": {"x": 0, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "capsule_health_panel",
                            "name": "Capsule Health",
                            "type": "gauge",
                            "metric_id": "capsule_health",
                            "position": {"x": 6, "y": 0, "w": 6, "h": 4}
                        }
                    ]
                },
                "layer_overview": {
                    "id": "layer_overview",
                    "name": "Layer Overview",
                    "description": "Overview of layer metrics",
                    "panels": [
                        {
                            "id": "layer_deployment_count_panel",
                            "name": "Layer Deployment Count",
                            "type": "counter",
                            "metric_id": "layer_deployment_count",
                            "position": {"x": 0, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "layer_deployment_success_rate_panel",
                            "name": "Layer Deployment Success Rate",
                            "type": "gauge",
                            "metric_id": "layer_deployment_success_rate",
                            "position": {"x": 6, "y": 0, "w": 6, "h": 4}
                        }
                    ]
                },
                "compliance_overview": {
                    "id": "compliance_overview",
                    "name": "Compliance Overview",
                    "description": "Overview of compliance metrics",
                    "panels": [
                        {
                            "id": "compliance_check_count_panel",
                            "name": "Compliance Check Count",
                            "type": "counter",
                            "metric_id": "compliance_check_count",
                            "position": {"x": 0, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "compliance_pass_rate_panel",
                            "name": "Compliance Pass Rate",
                            "type": "gauge",
                            "metric_id": "compliance_pass_rate",
                            "position": {"x": 6, "y": 0, "w": 6, "h": 4}
                        }
                    ]
                },
                "performance_overview": {
                    "id": "performance_overview",
                    "name": "Performance Overview",
                    "description": "Overview of performance metrics",
                    "panels": [
                        {
                            "id": "resource_utilization_panel",
                            "name": "Resource Utilization",
                            "type": "gauge",
                            "metric_id": "resource_utilization",
                            "position": {"x": 0, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "response_time_panel",
                            "name": "Response Time",
                            "type": "histogram",
                            "metric_id": "response_time",
                            "position": {"x": 6, "y": 0, "w": 6, "h": 4}
                        }
                    ]
                },
                "security_overview": {
                    "id": "security_overview",
                    "name": "Security Overview",
                    "description": "Overview of security metrics",
                    "panels": [
                        {
                            "id": "security_incident_count_panel",
                            "name": "Security Incident Count",
                            "type": "counter",
                            "metric_id": "security_incident_count",
                            "position": {"x": 0, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "security_score_panel",
                            "name": "Security Score",
                            "type": "gauge",
                            "metric_id": "security_score",
                            "position": {"x": 6, "y": 0, "w": 6, "h": 4}
                        }
                    ]
                },
                "user_overview": {
                    "id": "user_overview",
                    "name": "User Overview",
                    "description": "Overview of user metrics",
                    "panels": [
                        {
                            "id": "user_action_count_panel",
                            "name": "User Action Count",
                            "type": "counter",
                            "metric_id": "user_action_count",
                            "position": {"x": 0, "y": 0, "w": 6, "h": 4}
                        },
                        {
                            "id": "user_satisfaction_panel",
                            "name": "User Satisfaction",
                            "type": "gauge",
                            "metric_id": "user_satisfaction",
                            "position": {"x": 6, "y": 0, "w": 6, "h": 4}
                        }
                    ]
                },
                "executive_overview": {
                    "id": "executive_overview",
                    "name": "Executive Overview",
                    "description": "Executive overview of key metrics",
                    "panels": [
                        {
                            "id": "deployment_success_rate_panel",
                            "name": "Deployment Success Rate",
                            "type": "gauge",
                            "metric_id": "deployment_success_rate",
                            "position": {"x": 0, "y": 0, "w": 4, "h": 4}
                        },
                        {
                            "id": "mission_success_rate_panel",
                            "name": "Mission Success Rate",
                            "type": "gauge",
                            "metric_id": "mission_success_rate",
                            "position": {"x": 4, "y": 0, "w": 4, "h": 4}
                        },
                        {
                            "id": "compliance_pass_rate_panel",
                            "name": "Compliance Pass Rate",
                            "type": "gauge",
                            "metric_id": "compliance_pass_rate",
                            "position": {"x": 8, "y": 0, "w": 4, "h": 4}
                        },
                        {
                            "id": "security_score_panel",
                            "name": "Security Score",
                            "type": "gauge",
                            "metric_id": "security_score",
                            "position": {"x": 0, "y": 4, "w": 4, "h": 4}
                        },
                        {
                            "id": "resource_utilization_panel",
                            "name": "Resource Utilization",
                            "type": "gauge",
                            "metric_id": "resource_utilization",
                            "position": {"x": 4, "y": 4, "w": 4, "h": 4}
                        },
                        {
                            "id": "user_satisfaction_panel",
                            "name": "User Satisfaction",
                            "type": "gauge",
                            "metric_id": "user_satisfaction",
                            "position": {"x": 8, "y": 4, "w": 4, "h": 4}
                        }
                    ]
                }
            }
            
            logger.info(f"Initialized {len(self.dashboards)} dashboard definitions")
        except Exception as e:
            logger.error(f"Failed to initialize dashboards: {str(e)}")
            raise
    
    async def _initialize_predictive_analytics(self):
        """Initialize predictive analytics"""
        try:
            # In a real implementation, this would set up predictive analytics models
            # For demonstration, we'll create sample prediction definitions
            self.predictions = {
                "deployment_success_prediction": {
                    "id": "deployment_success_prediction",
                    "name": "Deployment Success Prediction",
                    "description": "Predict deployment success probability",
                    "model_type": "classification",
                    "input_metrics": ["deployment_duration", "resource_utilization", "capsule_health"],
                    "output_metric": "deployment_success_rate"
                },
                "mission_duration_prediction": {
                    "id": "mission_duration_prediction",
                    "name": "Mission Duration Prediction",
                    "description": "Predict mission duration",
                    "model_type": "regression",
                    "input_metrics": ["capsule_count", "layer_deployment_count", "resource_utilization"],
                    "output_metric": "mission_duration"
                },
                "resource_utilization_prediction": {
                    "id": "resource_utilization_prediction",
                    "name": "Resource Utilization Prediction",
                    "description": "Predict resource utilization",
                    "model_type": "regression",
                    "input_metrics": ["capsule_count", "layer_deployment_count", "deployment_count"],
                    "output_metric": "resource_utilization"
                },
                "security_incident_prediction": {
                    "id": "security_incident_prediction",
                    "name": "Security Incident Prediction",
                    "description": "Predict security incident probability",
                    "model_type": "classification",
                    "input_metrics": ["security_score", "compliance_pass_rate", "user_action_count"],
                    "output_metric": "security_incident_count"
                },
                "user_satisfaction_prediction": {
                    "id": "user_satisfaction_prediction",
                    "name": "User Satisfaction Prediction",
                    "description": "Predict user satisfaction",
                    "model_type": "regression",
                    "input_metrics": ["response_time", "deployment_success_rate", "mission_success_rate"],
                    "output_metric": "user_satisfaction"
                }
            }
            
            logger.info(f"Initialized {len(self.predictions)} prediction definitions")
        except Exception as e:
            logger.error(f"Failed to initialize predictive analytics: {str(e)}")
            raise
    
    def record_metric(self, metric_id: str, value: Union[int, float], timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a metric value
        
        Args:
            metric_id: ID of the metric to record
            value: Value to record
            timestamp: Timestamp for the metric, or None for current time
            labels: Additional labels for the metric, or None
        """
        try:
            if metric_id not in self.metrics:
                logger.warning(f"Unknown metric ID: {metric_id}")
                return
            
            metric = self.metrics[metric_id]
            category = metric.get("category", "unknown")
            
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Create metric entry
            entry = {
                "value": value,
                "timestamp": timestamp,
                "labels": labels
            }
            
            # Store metric entry
            if category not in self.metrics_store:
                self.metrics_store[category] = {}
            
            if metric_id not in self.metrics_store[category]:
                self.metrics_store[category][metric_id] = []
            
            self.metrics_store[category][metric_id].append(entry)
            
            # Check alerts
            self._check_alerts(metric_id, value, labels)
            
            logger.debug(f"Recorded metric {metric_id} with value {value}")
        except Exception as e:
            logger.error(f"Failed to record metric {metric_id}: {str(e)}")
    
    def _check_alerts(self, metric_id: str, value: Union[int, float], labels: Dict[str, str]):
        """
        Check alerts for a metric value
        
        Args:
            metric_id: ID of the metric to check
            value: Value to check
            labels: Labels for the metric
        """
        try:
            # Find alerts for this metric
            for alert_id, alert in self.alerts.items():
                if alert.get("metric_id") != metric_id:
                    continue
                
                # Parse condition
                condition = alert.get("condition", "")
                if not condition:
                    continue
                
                # Check condition
                triggered = False
                
                if condition.startswith("<"):
                    threshold = float(condition[1:].strip())
                    triggered = value < threshold
                elif condition.startswith(">"):
                    threshold = float(condition[1:].strip())
                    triggered = value > threshold
                elif condition.startswith("="):
                    threshold = float(condition[1:].strip())
                    triggered = value == threshold
                elif condition.startswith("!="):
                    threshold = float(condition[2:].strip())
                    triggered = value != threshold
                elif condition.startswith("<="):
                    threshold = float(condition[2:].strip())
                    triggered = value <= threshold
                elif condition.startswith(">="):
                    threshold = float(condition[2:].strip())
                    triggered = value >= threshold
                
                if triggered:
                    # In a real implementation, this would send notifications
                    # For demonstration, we'll just log the alert
                    logger.info(f"Alert triggered: {alert['name']} - {alert['description']} - Value: {value} - Condition: {condition}")
        except Exception as e:
            logger.error(f"Failed to check alerts for metric {metric_id}: {str(e)}")
    
    def record_deployment(self, deployment_id: str, status: str, duration: float, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a deployment
        
        Args:
            deployment_id: ID of the deployment
            status: Status of the deployment (success, failure, etc.)
            duration: Duration of the deployment in seconds
            timestamp: Timestamp for the deployment, or None for current time
            labels: Additional labels for the deployment, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with deployment ID
            labels["deployment_id"] = deployment_id
            
            # Record deployment count
            self.record_metric("deployment_count", 1, timestamp, labels)
            
            # Record deployment success rate
            if status == "success":
                self.record_metric("deployment_success_rate", 100, timestamp, labels)
            else:
                self.record_metric("deployment_success_rate", 0, timestamp, labels)
            
            # Record deployment duration
            self.record_metric("deployment_duration", duration, timestamp, labels)
            
            logger.info(f"Recorded deployment {deployment_id} with status {status} and duration {duration}")
        except Exception as e:
            logger.error(f"Failed to record deployment {deployment_id}: {str(e)}")
    
    def record_mission(self, mission_id: str, status: str, duration: float, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a mission
        
        Args:
            mission_id: ID of the mission
            status: Status of the mission (success, failure, etc.)
            duration: Duration of the mission in seconds
            timestamp: Timestamp for the mission, or None for current time
            labels: Additional labels for the mission, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with mission ID
            labels["mission_id"] = mission_id
            
            # Record mission count
            self.record_metric("mission_count", 1, timestamp, labels)
            
            # Record mission success rate
            if status == "success":
                self.record_metric("mission_success_rate", 100, timestamp, labels)
            else:
                self.record_metric("mission_success_rate", 0, timestamp, labels)
            
            # Record mission duration
            self.record_metric("mission_duration", duration, timestamp, labels)
            
            logger.info(f"Recorded mission {mission_id} with status {status} and duration {duration}")
        except Exception as e:
            logger.error(f"Failed to record mission {mission_id}: {str(e)}")
    
    def record_capsule(self, capsule_id: str, health: float, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a capsule
        
        Args:
            capsule_id: ID of the capsule
            health: Health score of the capsule (0-100)
            timestamp: Timestamp for the capsule, or None for current time
            labels: Additional labels for the capsule, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with capsule ID
            labels["capsule_id"] = capsule_id
            
            # Record capsule count
            self.record_metric("capsule_count", 1, timestamp, labels)
            
            # Record capsule health
            self.record_metric("capsule_health", health, timestamp, labels)
            
            logger.info(f"Recorded capsule {capsule_id} with health {health}")
        except Exception as e:
            logger.error(f"Failed to record capsule {capsule_id}: {str(e)}")
    
    def record_layer_deployment(self, layer_id: str, status: str, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a layer deployment
        
        Args:
            layer_id: ID of the layer
            status: Status of the deployment (success, failure, etc.)
            timestamp: Timestamp for the deployment, or None for current time
            labels: Additional labels for the deployment, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with layer ID
            labels["layer_id"] = layer_id
            
            # Record layer deployment count
            self.record_metric("layer_deployment_count", 1, timestamp, labels)
            
            # Record layer deployment success rate
            if status == "success":
                self.record_metric("layer_deployment_success_rate", 100, timestamp, labels)
            else:
                self.record_metric("layer_deployment_success_rate", 0, timestamp, labels)
            
            logger.info(f"Recorded layer deployment for layer {layer_id} with status {status}")
        except Exception as e:
            logger.error(f"Failed to record layer deployment for layer {layer_id}: {str(e)}")
    
    def record_compliance_check_run(self, check_run_id: str, check_id: str, status: str, passed: bool, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a compliance check run
        
        Args:
            check_run_id: ID of the check run
            check_id: ID of the compliance check
            status: Status of the check run (passed, failed, etc.)
            passed: Whether the check passed
            timestamp: Timestamp for the check run, or None for current time
            labels: Additional labels for the check run, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with check run ID and check ID
            labels["check_run_id"] = check_run_id
            labels["check_id"] = check_id
            
            # Record compliance check count
            self.record_metric("compliance_check_count", 1, timestamp, labels)
            
            # Record compliance pass rate
            if passed:
                self.record_metric("compliance_pass_rate", 100, timestamp, labels)
            else:
                self.record_metric("compliance_pass_rate", 0, timestamp, labels)
            
            logger.info(f"Recorded compliance check run {check_run_id} for check {check_id} with status {status} and passed {passed}")
        except Exception as e:
            logger.error(f"Failed to record compliance check run {check_run_id}: {str(e)}")
    
    def record_compliance_check_batch(self, batch_id: str, policy_id: Optional[str], status: str, summary: Dict[str, int], timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a compliance check batch
        
        Args:
            batch_id: ID of the batch
            policy_id: ID of the policy, or None
            status: Status of the batch (passed, failed, etc.)
            summary: Summary of the batch (total, passed, failed, error)
            timestamp: Timestamp for the batch, or None for current time
            labels: Additional labels for the batch, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with batch ID and policy ID
            labels["batch_id"] = batch_id
            if policy_id:
                labels["policy_id"] = policy_id
            
            # Record compliance check count
            self.record_metric("compliance_check_count", summary.get("total", 0), timestamp, labels)
            
            # Record compliance pass rate
            total = summary.get("total", 0)
            passed = summary.get("passed", 0)
            
            if total > 0:
                pass_rate = (passed / total) * 100
            else:
                pass_rate = 0
            
            self.record_metric("compliance_pass_rate", pass_rate, timestamp, labels)
            
            logger.info(f"Recorded compliance check batch {batch_id} with status {status} and summary {summary}")
        except Exception as e:
            logger.error(f"Failed to record compliance check batch {batch_id}: {str(e)}")
    
    def record_remediation_workflow_run(self, workflow_run_id: str, workflow_id: str, status: str, success: bool, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a remediation workflow run
        
        Args:
            workflow_run_id: ID of the workflow run
            workflow_id: ID of the remediation workflow
            status: Status of the workflow run (completed, failed, etc.)
            success: Whether the workflow was successful
            timestamp: Timestamp for the workflow run, or None for current time
            labels: Additional labels for the workflow run, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with workflow run ID and workflow ID
            labels["workflow_run_id"] = workflow_run_id
            labels["workflow_id"] = workflow_id
            
            # In a real implementation, this would record specific metrics for remediation workflows
            # For demonstration, we'll just log the workflow run
            logger.info(f"Recorded remediation workflow run {workflow_run_id} for workflow {workflow_id} with status {status} and success {success}")
        except Exception as e:
            logger.error(f"Failed to record remediation workflow run {workflow_run_id}: {str(e)}")
    
    def record_compliance_report_generation(self, report_id: str, policy_id: str, status: str, summary: Dict[str, int], timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a compliance report generation
        
        Args:
            report_id: ID of the report
            policy_id: ID of the policy
            status: Status of the report (passed, failed, etc.)
            summary: Summary of the report (total, passed, failed, error)
            timestamp: Timestamp for the report, or None for current time
            labels: Additional labels for the report, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with report ID and policy ID
            labels["report_id"] = report_id
            labels["policy_id"] = policy_id
            
            # In a real implementation, this would record specific metrics for compliance reports
            # For demonstration, we'll just log the report generation
            logger.info(f"Recorded compliance report generation {report_id} for policy {policy_id} with status {status} and summary {summary}")
        except Exception as e:
            logger.error(f"Failed to record compliance report generation {report_id}: {str(e)}")
    
    def record_security_incident(self, incident_id: str, severity: str, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a security incident
        
        Args:
            incident_id: ID of the incident
            severity: Severity of the incident (low, medium, high, critical)
            timestamp: Timestamp for the incident, or None for current time
            labels: Additional labels for the incident, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with incident ID and severity
            labels["incident_id"] = incident_id
            labels["severity"] = severity
            
            # Record security incident count
            self.record_metric("security_incident_count", 1, timestamp, labels)
            
            logger.info(f"Recorded security incident {incident_id} with severity {severity}")
        except Exception as e:
            logger.error(f"Failed to record security incident {incident_id}: {str(e)}")
    
    def record_security_score(self, score: float, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a security score
        
        Args:
            score: Security score (0-100)
            timestamp: Timestamp for the score, or None for current time
            labels: Additional labels for the score, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Record security score
            self.record_metric("security_score", score, timestamp, labels)
            
            logger.info(f"Recorded security score {score}")
        except Exception as e:
            logger.error(f"Failed to record security score: {str(e)}")
    
    def record_user_action(self, user_id: str, action: str, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record a user action
        
        Args:
            user_id: ID of the user
            action: Action performed by the user
            timestamp: Timestamp for the action, or None for current time
            labels: Additional labels for the action, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with user ID and action
            labels["user_id"] = user_id
            labels["action"] = action
            
            # Record user action count
            self.record_metric("user_action_count", 1, timestamp, labels)
            
            logger.info(f"Recorded user action {action} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to record user action for user {user_id}: {str(e)}")
    
    def record_user_satisfaction(self, user_id: str, satisfaction: float, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record user satisfaction
        
        Args:
            user_id: ID of the user
            satisfaction: Satisfaction score (0-100)
            timestamp: Timestamp for the satisfaction, or None for current time
            labels: Additional labels for the satisfaction, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with user ID
            labels["user_id"] = user_id
            
            # Record user satisfaction
            self.record_metric("user_satisfaction", satisfaction, timestamp, labels)
            
            logger.info(f"Recorded user satisfaction {satisfaction} for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to record user satisfaction for user {user_id}: {str(e)}")
    
    def record_resource_utilization(self, resource_id: str, utilization: float, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record resource utilization
        
        Args:
            resource_id: ID of the resource
            utilization: Utilization percentage (0-100)
            timestamp: Timestamp for the utilization, or None for current time
            labels: Additional labels for the utilization, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with resource ID
            labels["resource_id"] = resource_id
            
            # Record resource utilization
            self.record_metric("resource_utilization", utilization, timestamp, labels)
            
            logger.info(f"Recorded resource utilization {utilization} for resource {resource_id}")
        except Exception as e:
            logger.error(f"Failed to record resource utilization for resource {resource_id}: {str(e)}")
    
    def record_response_time(self, operation_id: str, response_time: float, timestamp: Optional[str] = None, labels: Optional[Dict[str, str]] = None):
        """
        Record response time
        
        Args:
            operation_id: ID of the operation
            response_time: Response time in milliseconds
            timestamp: Timestamp for the response time, or None for current time
            labels: Additional labels for the response time, or None
        """
        try:
            if timestamp is None:
                timestamp = self._get_current_timestamp()
            
            if labels is None:
                labels = {}
            
            # Update labels with operation ID
            labels["operation_id"] = operation_id
            
            # Record response time
            self.record_metric("response_time", response_time, timestamp, labels)
            
            logger.info(f"Recorded response time {response_time} for operation {operation_id}")
        except Exception as e:
            logger.error(f"Failed to record response time for operation {operation_id}: {str(e)}")
    
    async def get_metric_values(self, metric_id: str, start_time: Optional[str] = None, end_time: Optional[str] = None, labels: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
        """
        Get metric values
        
        Args:
            metric_id: ID of the metric to get values for
            start_time: Start time for the values, or None for all values
            end_time: End time for the values, or None for all values
            labels: Filter by labels, or None for all values
            
        Returns:
            List of metric values
        """
        try:
            if metric_id not in self.metrics:
                return []
            
            metric = self.metrics[metric_id]
            category = metric.get("category", "unknown")
            
            if category not in self.metrics_store:
                return []
            
            if metric_id not in self.metrics_store[category]:
                return []
            
            values = self.metrics_store[category][metric_id]
            
            # Filter by time range
            if start_time is not None:
                values = [v for v in values if v["timestamp"] >= start_time]
            
            if end_time is not None:
                values = [v for v in values if v["timestamp"] <= end_time]
            
            # Filter by labels
            if labels is not None:
                filtered_values = []
                
                for value in values:
                    value_labels = value.get("labels", {})
                    match = True
                    
                    for key, val in labels.items():
                        if key not in value_labels or value_labels[key] != val:
                            match = False
                            break
                    
                    if match:
                        filtered_values.append(value)
                
                values = filtered_values
            
            return values
        except Exception as e:
            logger.error(f"Failed to get metric values for metric {metric_id}: {str(e)}")
            return []
    
    async def get_dashboard(self, dashboard_id: str) -> Dict[str, Any]:
        """
        Get a dashboard
        
        Args:
            dashboard_id: ID of the dashboard to get
            
        Returns:
            Dict containing dashboard definition
        """
        if dashboard_id not in self.dashboards:
            return {
                "status": "not_found",
                "dashboard_id": dashboard_id
            }
        
        return {
            "status": "success",
            "dashboard": self.dashboards[dashboard_id]
        }
    
    async def list_dashboards(self) -> List[Dict[str, Any]]:
        """
        List dashboards
        
        Returns:
            List of dashboard definitions
        """
        return list(self.dashboards.values())
    
    async def get_prediction(self, prediction_id: str) -> Dict[str, Any]:
        """
        Get a prediction
        
        Args:
            prediction_id: ID of the prediction to get
            
        Returns:
            Dict containing prediction definition
        """
        if prediction_id not in self.predictions:
            return {
                "status": "not_found",
                "prediction_id": prediction_id
            }
        
        return {
            "status": "success",
            "prediction": self.predictions[prediction_id]
        }
    
    async def list_predictions(self) -> List[Dict[str, Any]]:
        """
        List predictions
        
        Returns:
            List of prediction definitions
        """
        return list(self.predictions.values())
    
    async def run_prediction(self, prediction_id: str, input_values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run a prediction
        
        Args:
            prediction_id: ID of the prediction to run
            input_values: Input values for the prediction
            
        Returns:
            Dict containing prediction results
        """
        try:
            if prediction_id not in self.predictions:
                return {
                    "status": "not_found",
                    "prediction_id": prediction_id
                }
            
            prediction = self.predictions[prediction_id]
            
            logger.info(f"Running prediction {prediction_id}: {prediction['name']}")
            
            # In a real implementation, this would run the actual prediction model
            # For demonstration, we'll simulate the prediction
            
            # Generate prediction run ID
            prediction_run_id = f"prediction-run-{prediction_id}-{self._generate_id()}"
            
            # Create prediction run record
            prediction_run = {
                "id": prediction_run_id,
                "prediction_id": prediction_id,
                "status": "running",
                "input_values": input_values,
                "started_at": self._get_current_timestamp()
            }
            
            # Simulate prediction execution
            await asyncio.sleep(1)
            
            # Simulate prediction results
            import random
            
            if prediction["model_type"] == "classification":
                # Classification prediction (probability)
                prediction_run["status"] = "completed"
                prediction_run["results"] = {
                    "probability": random.uniform(0, 1),
                    "confidence": random.uniform(0.7, 0.95)
                }
            else:
                # Regression prediction (value)
                prediction_run["status"] = "completed"
                prediction_run["results"] = {
                    "value": random.uniform(0, 100),
                    "confidence": random.uniform(0.7, 0.95)
                }
            
            prediction_run["completed_at"] = self._get_current_timestamp()
            
            logger.info(f"Prediction {prediction_id} completed with status: {prediction_run['status']}")
            
            return {
                "status": "success",
                "prediction_run_id": prediction_run_id,
                "prediction_run": prediction_run
            }
        except Exception as e:
            logger.error(f"Failed to run prediction {prediction_id}: {str(e)}")
            
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_current_timestamp(self) -> str:
        """
        Get current timestamp in ISO 8601 format
        
        Returns:
            Current timestamp string
        """
        return datetime.utcnow().isoformat() + "Z"
    
    def _generate_id(self) -> str:
        """
        Generate a unique ID
        
        Returns:
            Unique ID string
        """
        import uuid
        return str(uuid.uuid4())
    
    async def cleanup(self):
        """Clean up resources used by the analytics manager"""
        logger.info("Cleaned up analytics manager")


# Singleton instance
_instance = None

def get_analytics_manager(config: Optional[Dict[str, Any]] = None) -> AnalyticsManager:
    """
    Get the singleton instance of the analytics manager
    
    Args:
        config: Configuration for the analytics manager (only used if creating a new instance)
        
    Returns:
        AnalyticsManager instance
    """
    global _instance
    
    if _instance is None:
        _instance = AnalyticsManager(config)
    
    return _instance
