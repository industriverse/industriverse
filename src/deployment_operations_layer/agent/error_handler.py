"""
Error Handler for the Deployment Operations Layer.

This module provides error handling capabilities for deployment operations
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    Handler for deployment errors.
    
    This class provides methods for handling errors during deployment operations,
    including error classification, recovery suggestion, and notification.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Error Handler.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.handler_id = config.get("handler_id", f"error-handler-{uuid.uuid4().hex[:8]}")
        self.endpoint = config.get("endpoint", "http://localhost:9003")
        self.auth_token = config.get("auth_token", "")
        self.timeout = config.get("timeout", 30)
        self.retry_attempts = config.get("retry_attempts", 3)
        
        # Initialize error handling configuration
        self.error_categories = config.get("error_categories", [
            "network", "authentication", "authorization", "resource", "timeout",
            "validation", "dependency", "configuration", "system", "unknown"
        ])
        self.notification_channels = config.get("notification_channels", ["log", "email", "slack"])
        self.default_notification_channel = config.get("default_notification_channel", "log")
        self.notification_enabled = config.get("notification_enabled", True)
        
        # Initialize recovery manager
        from .recovery_manager import RecoveryManager
        self.recovery_manager = RecoveryManager(config.get("recovery_manager", {}))
        
        # Initialize analytics manager for error tracking
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        logger.info(f"Error Handler {self.handler_id} initialized")
    
    def handle_error(self, error_context: Dict) -> Dict:
        """
        Handle a deployment error.
        
        Args:
            error_context: Error context
            
        Returns:
            Dict: Error handling results
        """
        try:
            # Extract error details
            error_message = error_context.get("error", "Unknown error")
            context = error_context.get("context", "unknown")
            
            # Classify error
            classification = self._classify_error(error_message, context)
            
            # Log error
            logger.error(f"Error in {context}: {error_message} (classified as {classification['category']})")
            
            # Track error in analytics
            self._track_error(error_context, classification)
            
            # Get recovery suggestions
            recovery_suggestions = self.recovery_manager.get_recovery_suggestions({
                "error": error_message,
                "context": context,
                "classification": classification
            })
            
            # Send notifications
            notification_results = None
            if self.notification_enabled:
                notification_results = self._send_notifications(error_context, classification, recovery_suggestions)
            
            # Construct error handling results
            handling_results = {
                "status": "handled",
                "error": error_message,
                "context": context,
                "classification": classification,
                "recovery_suggestions": recovery_suggestions,
                "notification_results": notification_results,
                "timestamp": datetime.now().isoformat(),
                "handler_id": self.handler_id
            }
            
            return handling_results
        except Exception as e:
            logger.error(f"Error in error handler: {e}")
            return {
                "status": "error",
                "message": f"Error handler failed: {e}",
                "original_error": error_context.get("error", "Unknown error")
            }
    
    def _classify_error(self, error_message: str, context: str) -> Dict:
        """
        Classify an error.
        
        Args:
            error_message: Error message
            context: Error context
            
        Returns:
            Dict: Error classification
        """
        # Default classification
        classification = {
            "category": "unknown",
            "severity": "medium",
            "recoverable": True
        }
        
        # Classify based on error message
        error_lower = error_message.lower()
        
        # Network errors
        if any(term in error_lower for term in ["connection", "network", "timeout", "unreachable", "dns"]):
            classification["category"] = "network"
            classification["severity"] = "high" if "critical" in context.lower() else "medium"
            classification["recoverable"] = True
        
        # Authentication errors
        elif any(term in error_lower for term in ["authentication", "login", "credentials", "password", "unauthorized"]):
            classification["category"] = "authentication"
            classification["severity"] = "high"
            classification["recoverable"] = True
        
        # Authorization errors
        elif any(term in error_lower for term in ["permission", "access", "forbidden", "denied", "authorization"]):
            classification["category"] = "authorization"
            classification["severity"] = "high"
            classification["recoverable"] = True
        
        # Resource errors
        elif any(term in error_lower for term in ["resource", "capacity", "quota", "limit", "memory", "disk", "cpu"]):
            classification["category"] = "resource"
            classification["severity"] = "high"
            classification["recoverable"] = True
        
        # Timeout errors
        elif any(term in error_lower for term in ["timeout", "timed out", "deadline"]):
            classification["category"] = "timeout"
            classification["severity"] = "medium"
            classification["recoverable"] = True
        
        # Validation errors
        elif any(term in error_lower for term in ["validation", "invalid", "schema", "format", "syntax"]):
            classification["category"] = "validation"
            classification["severity"] = "medium"
            classification["recoverable"] = True
        
        # Dependency errors
        elif any(term in error_lower for term in ["dependency", "missing", "not found", "required", "prerequisite"]):
            classification["category"] = "dependency"
            classification["severity"] = "high"
            classification["recoverable"] = True
        
        # Configuration errors
        elif any(term in error_lower for term in ["configuration", "config", "setting", "parameter", "option"]):
            classification["category"] = "configuration"
            classification["severity"] = "medium"
            classification["recoverable"] = True
        
        # System errors
        elif any(term in error_lower for term in ["system", "internal", "server", "crash", "exception"]):
            classification["category"] = "system"
            classification["severity"] = "critical"
            classification["recoverable"] = False
        
        # Adjust severity based on context
        if "critical" in context.lower() or "production" in context.lower():
            classification["severity"] = "critical"
        
        return classification
    
    def _track_error(self, error_context: Dict, classification: Dict) -> None:
        """
        Track an error in analytics.
        
        Args:
            error_context: Error context
            classification: Error classification
        """
        try:
            # Prepare metrics
            metrics = {
                "type": "error",
                "timestamp": datetime.now().isoformat(),
                "error_message": error_context.get("error", "Unknown error"),
                "context": error_context.get("context", "unknown"),
                "classification": classification,
                "handler_id": self.handler_id
            }
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking error metrics: {e}")
    
    def _send_notifications(self, error_context: Dict, classification: Dict, recovery_suggestions: Dict) -> Dict:
        """
        Send error notifications.
        
        Args:
            error_context: Error context
            classification: Error classification
            recovery_suggestions: Recovery suggestions
            
        Returns:
            Dict: Notification results
        """
        try:
            # Determine notification channels based on severity
            channels = []
            severity = classification.get("severity", "medium")
            
            if severity == "critical":
                channels = self.notification_channels
            elif severity == "high":
                channels = [channel for channel in self.notification_channels if channel != "pager"]
            elif severity == "medium":
                channels = [channel for channel in self.notification_channels if channel in ["log", "email"]]
            else:  # low
                channels = ["log"]
            
            # Send notifications to each channel
            notification_results = {}
            
            for channel in channels:
                try:
                    if channel == "log":
                        # Log notification
                        logger.error(f"Error notification: {error_context.get('error')} in {error_context.get('context')} (severity: {severity})")
                        notification_results[channel] = {"status": "success"}
                    elif channel == "email":
                        # Send email notification
                        email_result = self._send_email_notification(error_context, classification, recovery_suggestions)
                        notification_results[channel] = email_result
                    elif channel == "slack":
                        # Send Slack notification
                        slack_result = self._send_slack_notification(error_context, classification, recovery_suggestions)
                        notification_results[channel] = slack_result
                    elif channel == "pager":
                        # Send pager notification
                        pager_result = self._send_pager_notification(error_context, classification, recovery_suggestions)
                        notification_results[channel] = pager_result
                except Exception as e:
                    logger.error(f"Error sending notification to {channel}: {e}")
                    notification_results[channel] = {"status": "error", "message": str(e)}
            
            return {
                "status": "success",
                "channels": notification_results
            }
        except Exception as e:
            logger.error(f"Error sending notifications: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_email_notification(self, error_context: Dict, classification: Dict, recovery_suggestions: Dict) -> Dict:
        """
        Send an email notification.
        
        Args:
            error_context: Error context
            classification: Error classification
            recovery_suggestions: Recovery suggestions
            
        Returns:
            Dict: Email notification results
        """
        try:
            # Get email configuration
            email_config = self.config.get("email", {})
            recipients = email_config.get("recipients", [])
            
            if not recipients:
                return {"status": "skipped", "message": "No email recipients configured"}
            
            # Construct email content
            subject = f"Deployment Error: {classification.get('category')} in {error_context.get('context')} (Severity: {classification.get('severity')})"
            body = f"""
            Deployment Error Notification
            
            Error: {error_context.get('error', 'Unknown error')}
            Context: {error_context.get('context', 'unknown')}
            Timestamp: {datetime.now().isoformat()}
            
            Classification:
            - Category: {classification.get('category', 'unknown')}
            - Severity: {classification.get('severity', 'medium')}
            - Recoverable: {classification.get('recoverable', True)}
            
            Recovery Suggestions:
            {json.dumps(recovery_suggestions, indent=2)}
            
            Handler ID: {self.handler_id}
            """
            
            # In a real implementation, this would send an actual email
            # For now, just log it
            logger.info(f"Would send email notification to {recipients}: {subject}")
            
            return {
                "status": "success",
                "recipients": recipients,
                "subject": subject
            }
        except Exception as e:
            logger.error(f"Error sending email notification: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_slack_notification(self, error_context: Dict, classification: Dict, recovery_suggestions: Dict) -> Dict:
        """
        Send a Slack notification.
        
        Args:
            error_context: Error context
            classification: Error classification
            recovery_suggestions: Recovery suggestions
            
        Returns:
            Dict: Slack notification results
        """
        try:
            # Get Slack configuration
            slack_config = self.config.get("slack", {})
            webhook_url = slack_config.get("webhook_url")
            channel = slack_config.get("channel", "#deployments")
            
            if not webhook_url:
                return {"status": "skipped", "message": "No Slack webhook URL configured"}
            
            # Construct Slack message
            message = {
                "channel": channel,
                "username": "Deployment Ops Error Handler",
                "icon_emoji": ":warning:",
                "attachments": [
                    {
                        "fallback": f"Deployment Error: {error_context.get('error', 'Unknown error')}",
                        "color": "danger" if classification.get("severity") in ["critical", "high"] else "warning",
                        "title": f"Deployment Error: {classification.get('category')} in {error_context.get('context')}",
                        "text": error_context.get("error", "Unknown error"),
                        "fields": [
                            {
                                "title": "Severity",
                                "value": classification.get("severity", "medium"),
                                "short": True
                            },
                            {
                                "title": "Recoverable",
                                "value": str(classification.get("recoverable", True)),
                                "short": True
                            },
                            {
                                "title": "Timestamp",
                                "value": datetime.now().isoformat(),
                                "short": False
                            },
                            {
                                "title": "Recovery Suggestions",
                                "value": json.dumps(recovery_suggestions, indent=2),
                                "short": False
                            }
                        ],
                        "footer": f"Handler ID: {self.handler_id}"
                    }
                ]
            }
            
            # In a real implementation, this would send an actual Slack message
            # For now, just log it
            logger.info(f"Would send Slack notification to {channel}")
            
            return {
                "status": "success",
                "channel": channel
            }
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}")
            return {"status": "error", "message": str(e)}
    
    def _send_pager_notification(self, error_context: Dict, classification: Dict, recovery_suggestions: Dict) -> Dict:
        """
        Send a pager notification.
        
        Args:
            error_context: Error context
            classification: Error classification
            recovery_suggestions: Recovery suggestions
            
        Returns:
            Dict: Pager notification results
        """
        try:
            # Get pager configuration
            pager_config = self.config.get("pager", {})
            service_key = pager_config.get("service_key")
            
            if not service_key:
                return {"status": "skipped", "message": "No pager service key configured"}
            
            # Only send pager notifications for critical errors
            if classification.get("severity") != "critical":
                return {"status": "skipped", "message": "Error severity not critical"}
            
            # Construct pager message
            message = {
                "service_key": service_key,
                "event_type": "trigger",
                "description": f"Critical Deployment Error: {error_context.get('error', 'Unknown error')}",
                "client": "Deployment Ops Error Handler",
                "client_url": self.endpoint,
                "details": {
                    "error": error_context.get("error", "Unknown error"),
                    "context": error_context.get("context", "unknown"),
                    "classification": classification,
                    "recovery_suggestions": recovery_suggestions,
                    "timestamp": datetime.now().isoformat(),
                    "handler_id": self.handler_id
                }
            }
            
            # In a real implementation, this would send an actual pager notification
            # For now, just log it
            logger.info(f"Would send pager notification: {message['description']}")
            
            return {
                "status": "success",
                "description": message["description"]
            }
        except Exception as e:
            logger.error(f"Error sending pager notification: {e}")
            return {"status": "error", "message": str(e)}
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Error Handler.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "error_categories" in config:
                self.error_categories = config["error_categories"]
            
            if "notification_channels" in config:
                self.notification_channels = config["notification_channels"]
            
            if "default_notification_channel" in config:
                self.default_notification_channel = config["default_notification_channel"]
            
            if "notification_enabled" in config:
                self.notification_enabled = config["notification_enabled"]
            
            # Configure recovery manager
            recovery_result = None
            if "recovery_manager" in config:
                recovery_result = self.recovery_manager.configure(config["recovery_manager"])
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            return {
                "status": "success",
                "message": "Error Handler configured successfully",
                "handler_id": self.handler_id,
                "recovery_result": recovery_result,
                "analytics_result": analytics_result
            }
        except Exception as e:
            logger.error(f"Error configuring Error Handler: {e}")
            return {"status": "error", "message": str(e)}
