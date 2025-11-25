import os
import logging
from aioapns import APNs, NotificationRequest, PushType
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class APNsService:
    def __init__(self):
        self.client: Optional[APNs] = None
        # In production, these would be loaded from secure storage/env
        self.team_id = os.getenv("APNS_TEAM_ID", "")
        self.key_id = os.getenv("APNS_KEY_ID", "")
        self.use_sandbox = os.getenv("APNS_USE_SANDBOX", "true").lower() == "true"
        self.bundle_id = os.getenv("APNS_BUNDLE_ID", "com.industriverse.capsules")
        
        # Path to the .p8 private key file
        self.key_path = os.getenv("APNS_KEY_PATH", "certs/AuthKey.p8")

    async def connect(self):
        """Initialize APNs client."""
        if not self.team_id or not self.key_id or not os.path.exists(self.key_path):
            logger.warning("APNs credentials not configured. Push notifications will be disabled.")
            return

        try:
            self.client = APNs(
                key=self.key_path,
                key_id=self.key_id,
                team_id=self.team_id,
                topic=self.bundle_id,
                use_sandbox=self.use_sandbox
            )
            logger.info(f"APNs client initialized (Sandbox: {self.use_sandbox})")
        except Exception as e:
            logger.error(f"Failed to initialize APNs client: {e}")

    async def send_notification(self, device_token: str, title: str, body: str, payload: Dict[str, Any] = None):
        """Send a standard push notification."""
        if not self.client:
            logger.debug("APNs client not initialized, skipping notification.")
            return

        request = NotificationRequest(
            device_token=device_token,
            message={
                "aps": {
                    "alert": {
                        "title": title,
                        "body": body
                    },
                    "sound": "default"
                },
                **(payload or {})
            }
        )
        
        try:
            await self.client.send_notification(request)
            logger.info(f"Notification sent to {device_token[:8]}...")
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")

    async def update_live_activity(self, device_token: str, push_token: str, content_state: Dict[str, Any], alert: Optional[Dict[str, str]] = None):
        """Update a Live Activity."""
        if not self.client:
            return

        # Live Activity updates use a specific push type and payload structure
        message = {
            "aps": {
                "timestamp": int(os.time.time()),
                "event": "update",
                "content-state": content_state
            }
        }
        
        if alert:
            message["aps"]["alert"] = alert

        request = NotificationRequest(
            device_token=push_token, # Live Activity push token is different from device token
            message=message,
            push_type=PushType.LIVE_ACTIVITY
        )

        try:
            await self.client.send_notification(request)
            logger.info(f"Live Activity updated for {push_token[:8]}...")
        except Exception as e:
            logger.error(f"Failed to update Live Activity: {e}")

apns_service = APNsService()
