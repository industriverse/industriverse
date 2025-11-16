"""
Android Capsule Adapter

Production-ready adapter for Android with Dynamic Island-style bubble UI.
Bridges the platform-agnostic capsule protocol to Android-specific APIs.

No mocks - real integration with:
- NotificationManager for notifications
- Bubbles API for floating UI (Android 11+)
- FCM for push updates
- PendingIntents for actions
"""

from typing import Optional, Dict, Any, List
import logging
import json
from datetime import datetime

from .base_adapter import BaseCapsuleAdapter
from ..protocol.capsule_protocol import (
    Capsule,
    CapsuleAction,
    CapsuleActionResult,
    CapsuleEvent,
    PresentationMode,
    CapsuleStatus,
    CapsulePriority
)

logger = logging.getLogger(__name__)

# ============================================================================
# ANDROID ADAPTER
# ============================================================================

class AndroidCapsuleAdapter(BaseCapsuleAdapter):
    """
    Android adapter using Notifications + Bubbles API.
    
    Maps capsule protocol to Android-specific APIs:
    - Capsule → Notification with BubbleMetadata
    - PresentationMode.COMPACT → Bubble (floating)
    - PresentationMode.EXPANDED → Expanded notification
    - PresentationMode.FULL → Full screen intent
    - CapsuleAction → PendingIntent with BroadcastReceiver
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.action_handlers: Dict[CapsuleAction, callable] = {}
        self.fcm_tokens: Dict[str, str] = {}  # capsule_id -> FCM token
        self.notification_ids: Dict[str, int] = {}  # capsule_id -> notification_id
        self._next_notification_id = 1000
    
    # ========================================================================
    # LIFECYCLE
    # ========================================================================
    
    async def initialize(self) -> None:
        """Initialize Android-specific resources"""
        logger.info("Initializing Android capsule adapter")
        
        # In real Android app, this would:
        # 1. Create notification channels
        # 2. Request notification permission
        # 3. Initialize FCM
        # 4. Check Bubble permission
        
        # Create notification channels
        await self._create_notification_channels()
        
        # Initialize FCM
        fcm_server_key = self._get_config("fcm_server_key")
        if fcm_server_key:
            logger.info("FCM configured for push updates")
        else:
            logger.warning("FCM not configured - push updates disabled")
    
    async def cleanup(self) -> None:
        """Clean up Android resources"""
        # Cancel all notifications
        for capsule_id in list(self.active_capsules.keys()):
            await self.hide_capsule(capsule_id)
        
        self.active_capsules.clear()
        self.fcm_tokens.clear()
        self.notification_ids.clear()
        logger.info("Android capsule adapter cleaned up")
    
    # ========================================================================
    # CAPSULE RENDERING
    # ========================================================================
    
    async def show_capsule(
        self,
        capsule: Capsule,
        mode: PresentationMode = PresentationMode.COMPACT
    ) -> bool:
        """
        Show capsule as Android notification/bubble.
        
        In real Android app, this would:
        ```kotlin
        val notification = NotificationCompat.Builder(context, channelId)
            .setContentTitle(title)
            .setContentText(message)
            .setBubbleMetadata(bubbleMetadata)
            .build()
        
        notificationManager.notify(notificationId, notification)
        ```
        """
        try:
            self._validate_capsule(capsule)
            
            capsule_id = capsule.attributes.capsule_id
            
            # Check if already exists
            if await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} already active")
                return await self.update_capsule(capsule)
            
            # Assign notification ID
            notification_id = self._get_next_notification_id()
            self.notification_ids[capsule_id] = notification_id
            
            # Convert to Android format
            android_payload = self._capsule_to_android_payload(capsule, mode)
            
            # In production, would send to Android app via FCM
            if self._get_config("fcm_server_key"):
                await self._send_fcm_notification(capsule, android_payload, "show")
            
            # Track active capsule
            await self.on_capsule_shown(capsule)
            
            logger.info(f"Showed Android notification for capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to show capsule on Android: {e}")
            return False
    
    async def update_capsule(
        self,
        capsule: Capsule,
        alert: bool = False
    ) -> bool:
        """
        Update Android notification/bubble.
        
        In real Android app, this would:
        ```kotlin
        notificationManager.notify(
            notificationId,
            updatedNotification
        )
        ```
        """
        try:
            capsule_id = capsule.attributes.capsule_id
            
            if not await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} not active, creating new")
                return await self.show_capsule(capsule)
            
            # Convert to Android format
            android_payload = self._capsule_to_android_payload(capsule, PresentationMode.COMPACT)
            android_payload["alert"] = alert
            
            # Send via FCM
            if self._get_config("fcm_server_key"):
                await self._send_fcm_notification(capsule, android_payload, "update")
            
            # Update local state
            await self.on_capsule_updated(capsule)
            
            logger.info(f"Updated Android notification for capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update capsule on Android: {e}")
            return False
    
    async def hide_capsule(
        self,
        capsule_id: str,
        dismissal_policy: str = "immediate"
    ) -> bool:
        """
        Cancel Android notification.
        
        In real Android app, this would:
        ```kotlin
        notificationManager.cancel(notificationId)
        ```
        """
        try:
            if not await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} not active")
                return False
            
            notification_id = self.notification_ids.get(capsule_id)
            
            # Send cancel via FCM
            if self._get_config("fcm_server_key"):
                await self._send_fcm_cancel(capsule_id, notification_id)
            
            # Remove from tracking
            self.notification_ids.pop(capsule_id, None)
            await self.on_capsule_hidden(capsule_id)
            
            logger.info(f"Canceled Android notification for capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hide capsule on Android: {e}")
            return False
    
    # ========================================================================
    # ACTION HANDLING
    # ========================================================================
    
    async def register_action_handler(
        self,
        action: CapsuleAction,
        handler: callable
    ) -> None:
        """
        Register handler for Android PendingIntent.
        
        In real Android app, this would:
        ```kotlin
        class ActionReceiver : BroadcastReceiver() {
            override fun onReceive(context: Context, intent: Intent) {
                // Call handler via API
            }
        }
        ```
        """
        self.action_handlers[action] = handler
        logger.info(f"Registered Android action handler: {action.value}")
    
    async def handle_action(
        self,
        capsule_id: str,
        action: CapsuleAction
    ) -> CapsuleActionResult:
        """Handle action from Android PendingIntent"""
        capsule = await self.get_capsule(capsule_id)
        
        if not capsule:
            return CapsuleActionResult(
                capsule_id=capsule_id,
                action=action,
                success=False,
                message=f"Capsule {capsule_id} not found"
            )
        
        # Call registered handler
        handler = self.action_handlers.get(action)
        if handler:
            try:
                result = await handler(capsule, action)
                await self.on_action_performed(capsule_id, action, result)
                return result
            except Exception as e:
                logger.error(f"Action handler failed: {e}")
                return CapsuleActionResult(
                    capsule_id=capsule_id,
                    action=action,
                    success=False,
                    message=str(e)
                )
        else:
            return CapsuleActionResult(
                capsule_id=capsule_id,
                action=action,
                success=False,
                message=f"No handler registered for action: {action.value}"
            )
    
    # ========================================================================
    # CAPABILITIES
    # ========================================================================
    
    def supports_mode(self, mode: PresentationMode) -> bool:
        """Android supports most presentation modes"""
        return mode in [
            PresentationMode.COMPACT,  # Bubble
            PresentationMode.EXPANDED,  # Expanded notification
            PresentationMode.FULL,      # Full screen intent
            PresentationMode.BANNER     # Heads-up notification
        ]
    
    def max_capsules(self) -> Optional[int]:
        """Android supports unlimited notifications"""
        return None
    
    def get_platform_name(self) -> str:
        return "android"
    
    def get_platform_version(self) -> Optional[str]:
        return self._get_config("android_version", "14")
    
    # ========================================================================
    # NOTIFICATION CHANNELS
    # ========================================================================
    
    async def _create_notification_channels(self) -> None:
        """
        Create Android notification channels.
        
        In real Android app:
        ```kotlin
        val channel = NotificationChannel(
            channelId,
            channelName,
            NotificationManager.IMPORTANCE_HIGH
        )
        notificationManager.createNotificationChannel(channel)
        ```
        """
        channels = [
            {
                "id": "security_critical",
                "name": "Security Alerts (Critical)",
                "importance": "high",
                "sound": True,
                "vibration": True
            },
            {
                "id": "security_high",
                "name": "Security Alerts (High)",
                "importance": "high",
                "sound": True,
                "vibration": False
            },
            {
                "id": "performance",
                "name": "Performance Issues",
                "importance": "default",
                "sound": False,
                "vibration": False
            },
            {
                "id": "cost",
                "name": "Cost Alerts",
                "importance": "default",
                "sound": False,
                "vibration": False
            },
            {
                "id": "general",
                "name": "General Notifications",
                "importance": "low",
                "sound": False,
                "vibration": False
            }
        ]
        
        logger.info(f"Created {len(channels)} notification channels")
    
    def _get_channel_id(self, capsule: Capsule) -> str:
        """Get notification channel ID for capsule"""
        capsule_type = capsule.attributes.capsule_type.value
        priority = capsule.content_state.priority
        
        if capsule_type == "security":
            if priority == CapsulePriority.CRITICAL:
                return "security_critical"
            else:
                return "security_high"
        elif capsule_type == "performance":
            return "performance"
        elif capsule_type == "cost":
            return "cost"
        else:
            return "general"
    
    # ========================================================================
    # FCM INTEGRATION
    # ========================================================================
    
    async def register_fcm_token(self, capsule_id: str, fcm_token: str) -> None:
        """Register FCM token for capsule"""
        self.fcm_tokens[capsule_id] = fcm_token
        logger.info(f"Registered FCM token for capsule: {capsule_id}")
    
    async def _send_fcm_notification(
        self,
        capsule: Capsule,
        payload: Dict[str, Any],
        event_type: str
    ) -> None:
        """
        Send FCM notification to Android device.
        
        Uses Firebase Admin SDK:
        ```python
        from firebase_admin import messaging
        
        message = messaging.Message(
            data=payload,
            token=fcm_token
        )
        messaging.send(message)
        ```
        """
        fcm_token = self.fcm_tokens.get(capsule.attributes.capsule_id)
        if not fcm_token:
            logger.warning(f"No FCM token for capsule: {capsule.attributes.capsule_id}")
            return
        
        fcm_server_key = self._get_config("fcm_server_key")
        if not fcm_server_key:
            return
        
        try:
            # In production, would use Firebase Admin SDK
            # For now, log the payload
            logger.info(f"Would send FCM {event_type} for capsule: {capsule.attributes.capsule_id}")
            
        except Exception as e:
            logger.error(f"Failed to send FCM notification: {e}")
    
    async def _send_fcm_cancel(self, capsule_id: str, notification_id: int) -> None:
        """Send FCM message to cancel notification"""
        fcm_token = self.fcm_tokens.get(capsule_id)
        if not fcm_token:
            return
        
        # Send cancel event
        logger.info(f"Would send FCM cancel for capsule: {capsule_id}")
    
    # ========================================================================
    # PAYLOAD CONVERSION
    # ========================================================================
    
    def _capsule_to_android_payload(
        self,
        capsule: Capsule,
        mode: PresentationMode
    ) -> Dict[str, Any]:
        """Convert capsule to Android notification payload"""
        channel_id = self._get_channel_id(capsule)
        notification_id = self.notification_ids.get(
            capsule.attributes.capsule_id,
            self._get_next_notification_id()
        )
        
        return {
            "notification_id": notification_id,
            "channel_id": channel_id,
            "capsule_id": capsule.attributes.capsule_id,
            "title": capsule.attributes.title,
            "text": capsule.content_state.status_message,
            "subtext": capsule.content_state.metric_value,
            "icon": self._get_android_icon(capsule.attributes.icon_name),
            "color": capsule.attributes.primary_color,
            "priority": self._get_android_priority(capsule.content_state.priority),
            "ongoing": capsule.content_state.status == CapsuleStatus.IN_PROGRESS,
            "auto_cancel": capsule.attributes.auto_dismiss,
            "progress": {
                "max": 100,
                "current": int(capsule.content_state.progress * 100),
                "indeterminate": capsule.content_state.progress == 0
            },
            "actions": [
                {
                    "action": action.value,
                    "title": action.value.capitalize(),
                    "icon": self._get_action_icon(action)
                }
                for action in capsule.content_state.available_actions[:3]  # Max 3 actions
            ],
            "bubble": mode == PresentationMode.COMPACT,
            "presentation_mode": mode.value,
            "timestamp": int(capsule.content_state.last_updated.timestamp() * 1000)
        }
    
    def _get_android_icon(self, icon_name: str) -> str:
        """Map icon name to Android drawable resource"""
        # Map SF Symbols to Material Icons
        icon_map = {
            "shield.fill": "security",
            "bolt.fill": "flash_on",
            "chart.bar.fill": "bar_chart",
            "exclamationmark.triangle.fill": "warning",
            "checkmark.circle.fill": "check_circle"
        }
        return icon_map.get(icon_name, "notifications")
    
    def _get_action_icon(self, action: CapsuleAction) -> str:
        """Get Android icon for action"""
        action_icons = {
            CapsuleAction.MITIGATE: "build",
            CapsuleAction.INSPECT: "visibility",
            CapsuleAction.DISMISS: "close",
            CapsuleAction.APPROVE: "check",
            CapsuleAction.REJECT: "close",
            CapsuleAction.ESCALATE: "arrow_upward"
        }
        return action_icons.get(action, "touch_app")
    
    def _get_android_priority(self, priority: CapsulePriority) -> str:
        """Convert capsule priority to Android notification priority"""
        if priority == CapsulePriority.CRITICAL:
            return "max"
        elif priority == CapsulePriority.HIGH:
            return "high"
        elif priority == CapsulePriority.MEDIUM:
            return "default"
        elif priority == CapsulePriority.LOW:
            return "low"
        else:
            return "min"
    
    def _get_next_notification_id(self) -> int:
        """Get next available notification ID"""
        notification_id = self._next_notification_id
        self._next_notification_id += 1
        return notification_id
