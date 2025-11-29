# alerting_service.py

import logging
from typing import List, Dict, Any, Optional
import asyncio # For potential async notification sending

from .monitoring_schemas import (
    AlertEvent,
    AlertSeverity,
    AlertChannel,
    AlertRecipientConfig,
    ModelIdentifier
)
from .monitoring_exceptions import AlertingError, ConfigurationError

# Placeholder for actual notification client libraries
# import smtplib # For email
# from slack_sdk import WebClient # For Slack
# import httpx # For generic webhooks or PagerDuty

logger = logging.getLogger(__name__)

class AlertingService:
    """
    Service responsible for dispatching alerts based on severity and configured channels.
    """

    def __init__(self, global_config: Optional[Dict[str, Any]] = None):
        """
        Initializes the AlertingService.
        Args:
            global_config: Global configuration, potentially for notification client setups (API keys, etc.).
        """
        self.global_config = global_config or {}
        # Initialize notification clients here if needed, e.g.:
        # self.email_client = self._setup_email_client()
        # self.slack_client = WebClient(token=self.global_config.get("SLACK_BOT_TOKEN"))
        logger.info("AlertingService initialized.")

    async def dispatch_alert(
        self, 
        alert_event: AlertEvent, 
        recipients: List[AlertRecipientConfig]
    ) -> None:
        """
        Dispatches an alert event to the configured recipients based on severity and channel.

        Args:
            alert_event: The AlertEvent object containing alert details.
            recipients: A list of AlertRecipientConfig defining who and how to notify.
        """
        if not recipients:
            logger.warning(f"No recipients configured for alert {alert_event.alert_id}. Alert will not be dispatched.")
            return

        logger.info(f"Dispatching alert {alert_event.alert_id} (Severity: {alert_event.severity}, Title: 	{alert_event.title}	) to {len(recipients)} recipient configurations.")
        
        dispatch_tasks = []
        for recipient_config in recipients:
            if self._should_send_to_recipient(alert_event.severity, recipient_config.min_severity):
                task = self._send_notification(alert_event, recipient_config)
                dispatch_tasks.append(task)
            else:
                logger.debug(f"Skipping recipient {recipient_config.target} for alert {alert_event.alert_id}: event severity 	{alert_event.severity}	 below recipient minimum 	{recipient_config.min_severity}	.")

        if dispatch_tasks:
            results = await asyncio.gather(*dispatch_tasks, return_exceptions=True)
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Failed to send notification for alert {alert_event.alert_id} to {recipients[i].target} via {recipients[i].channel}: {result}")
        else:
            logger.info(f"No recipients met severity criteria for alert {alert_event.alert_id}.")

    def _should_send_to_recipient(self, event_severity: AlertSeverity, recipient_min_severity: AlertSeverity) -> bool:
        """Determines if an alert should be sent based on severity levels."""
        severity_order = {AlertSeverity.INFO: 1, AlertSeverity.WARNING: 2, AlertSeverity.CRITICAL: 3}
        return severity_order.get(event_severity, 0) >= severity_order.get(recipient_min_severity, 0)

    async def _send_notification(
        self, 
        alert_event: AlertEvent, 
        recipient_config: AlertRecipientConfig
    ) -> None:
        """
        Sends a single notification based on the channel.
        """
        channel = recipient_config.channel
        target = recipient_config.target
        subject = f"[{alert_event.severity.value}] Monitoring Alert: {alert_event.title}"
        
        # Constructing a more detailed body
        body_parts = [
            f"Alert ID: {alert_event.alert_id}",
            f"Timestamp: {alert_event.timestamp.isoformat()}",
            f"Severity: {alert_event.severity.value}",
            f"Title: {alert_event.title}",
            f"Description: {alert_event.description}"
        ]
        if alert_event.model_identifier:
            body_parts.append(f"Model ID: {alert_event.model_identifier.model_id} (Version: {alert_event.model_identifier.model_version or 'N/A'}, Service: {alert_event.model_identifier.service_name})")
        if alert_event.config_id:
            body_parts.append(f"Monitoring Config ID: {alert_event.config_id}")
        if alert_event.details:
            body_parts.append("\nDetails:")
            for key, value in alert_event.details.items():
                body_parts.append(f"  {key}: {value}")
        body = "\n".join(body_parts)

        logger.info(f"Attempting to send alert {alert_event.alert_id} via {channel} to {target}.")

        try:
            # Persistent Alert Logging (No Mock)
            import json
            import os
            from datetime import datetime
            
            log_dir = os.path.join(os.getcwd(), "logs")
            os.makedirs(log_dir, exist_ok=True)
            alert_file = os.path.join(log_dir, "alerts.json")
            
            entry = {
                "id": str(alert_event.alert_id),
                "timestamp": alert_event.timestamp.isoformat(),
                "severity": alert_event.severity.value,
                "channel": channel.value,
                "target": target,
                "title": alert_event.title,
                "body": body
            }
            
            # Append to JSONL file
            with open(alert_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
                
            logger.info(f"Alert persisted to {alert_file}")
            
            # Simulate async operation
            await asyncio.sleep(0.01) 
        except Exception as e:
            logger.error(f"Error persisting alert {alert_event.alert_id}: {e}", exc_info=True)
            raise AlertingError(f"Failed to persist alert: {str(e)}")

    # --- Placeholder methods for actual client interactions ---
    # async def _send_email(self, to_address: str, subject: str, body: str):
    #     # Implementation using smtplib or other email library
    #     pass

    # async def _send_slack_message(self, channel_or_user: str, message_text: str):
    #     # Implementation using slack_sdk
    #     # await self.slack_client.chat_postMessage(channel=channel_or_user, text=message_text)
    #     pass

    # async def _trigger_pagerduty_incident(self, service_key: str, title: str, alert_event: AlertEvent):
    #     # Implementation using PagerDuty Events API v2
    #     pass

    # async def _send_mcp_a2a_message(self, topic_or_agent_id: str, payload: Dict[str, Any]):
    #     # Implementation using the MCP/A2A client library from Protocol Layer
    #     pass

    # def _setup_email_client(self):
    #     # Setup SMTP client from global_config
    #     # smtp_server = self.global_config.get("SMTP_SERVER")
    #     # ... credentials etc.
    #     # return smtplib.SMTP(smtp_server, port)
    #     return None

