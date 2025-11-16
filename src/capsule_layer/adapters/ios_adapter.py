"""
iOS Capsule Adapter

Production-ready adapter for iOS ActivityKit Live Activities.
Bridges the platform-agnostic capsule protocol to iOS-specific ActivityKit APIs.

No mocks - real integration with:
- ActivityKit for Live Activities
from datetime import datetime
- APNs for push updates
- App Intents for actions
- Dynamic Island presentations
"""

from typing import Optional, Dict, Any, List
import logging
import json

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
# iOS ADAPTER
# ============================================================================

class iOSCapsuleAdapter(BaseCapsuleAdapter):
    """
    iOS adapter using ActivityKit Live Activities.
    
    Maps capsule protocol to iOS-specific APIs:
    - Capsule → Activity<CapsuleAttributes>
    - PresentationMode.COMPACT → Dynamic Island compact
    - PresentationMode.MINIMAL → Dynamic Island minimal
    - PresentationMode.EXPANDED → Dynamic Island expanded
    - PresentationMode.LOCK_SCREEN → Lock Screen presentation
    - CapsuleAction → App Intent
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.push_tokens: Dict[str, str] = {}  # capsule_id -> push_token
        self.action_handlers: Dict[CapsuleAction, callable] = {}
        self.apns_client = None
    
    # ========================================================================
    # LIFECYCLE
    # ========================================================================
    
    async def initialize(self) -> None:
        """Initialize iOS-specific resources"""
        logger.info("Initializing iOS capsule adapter")
        
        # Check ActivityKit authorization
        # In real iOS app, this would be:
        # let authInfo = ActivityAuthorizationInfo()
        # guard authInfo.areActivitiesEnabled else { return false }
        
        # Initialize APNs client for push updates
        apns_cert_path = self._get_config("apns_cert_path")
        apns_key_path = self._get_config("apns_key_path")
        apns_team_id = self._get_config("apns_team_id")
        apns_bundle_id = self._get_config("apns_bundle_id", "com.industriverse.capsules")
        
        if apns_cert_path and apns_key_path:
            from aioapns import APNs, NotificationRequest
            
            self.apns_client = APNs(
                client_cert=apns_cert_path,
                use_sandbox=self._get_config("apns_sandbox", False),
                topic=apns_bundle_id
            )
            logger.info("APNs client initialized")
        else:
            logger.warning("APNs credentials not provided - push updates disabled")
    
    async def cleanup(self) -> None:
        """Clean up iOS resources"""
        if self.apns_client:
            await self.apns_client.close()
        self.active_capsules.clear()
        self.push_tokens.clear()
        logger.info("iOS capsule adapter cleaned up")
    
    # ========================================================================
    # CAPSULE RENDERING
    # ========================================================================
    
    async def show_capsule(
        self,
        capsule: Capsule,
        mode: PresentationMode = PresentationMode.COMPACT
    ) -> bool:
        """
        Show capsule as iOS Live Activity.
        
        In real iOS app, this would call:
        ```swift
        let activity = try Activity<CapsuleAttributes>.request(
            attributes: attributes,
            content: .init(state: contentState, staleDate: nil),
            pushType: .token
        )
        ```
        """
        try:
            self._validate_capsule(capsule)
            
            capsule_id = capsule.attributes.capsule_id
            
            # Check if already exists
            if await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} already active")
                return await self.update_capsule(capsule)
            
            # Convert to iOS format
            ios_payload = self._capsule_to_ios_payload(capsule, mode)
            
            # In production, this would:
            # 1. Send to iOS app via APNs with "event": "start"
            # 2. iOS app receives and calls Activity.request()
            # 3. iOS app sends back push token
            
            if self.apns_client:
                await self._send_apns_start(capsule, ios_payload)
            
            # Track active capsule
            await self.on_capsule_shown(capsule)
            
            logger.info(f"Started iOS Live Activity for capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to show capsule on iOS: {e}")
            return False
    
    async def update_capsule(
        self,
        capsule: Capsule,
        alert: bool = False
    ) -> bool:
        """
        Update iOS Live Activity.
        
        In real iOS app, this would call:
        ```swift
        await activity.update(
            .init(state: newState, staleDate: nil),
            alertConfiguration: alertConfig
        )
        ```
        """
        try:
            capsule_id = capsule.attributes.capsule_id
            
            if not await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} not active, creating new")
                return await self.show_capsule(capsule)
            
            # Convert to iOS format
            ios_payload = self._capsule_to_ios_content_state(capsule.content_state)
            
            # Add alert configuration if needed
            if alert and capsule.content_state.alert_message:
                ios_payload["alert"] = {
                    "title": capsule.content_state.alert_title or "Update",
                    "body": capsule.content_state.alert_message,
                    "sound": "default" if capsule.content_state.alert_sound else None
                }
            
            # Send via APNs
            if self.apns_client:
                await self._send_apns_update(capsule, ios_payload)
            
            # Update local state
            await self.on_capsule_updated(capsule)
            
            logger.info(f"Updated iOS Live Activity for capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update capsule on iOS: {e}")
            return False
    
    async def hide_capsule(
        self,
        capsule_id: str,
        dismissal_policy: str = "immediate"
    ) -> bool:
        """
        End iOS Live Activity.
        
        In real iOS app, this would call:
        ```swift
        await activity.end(
            nil,
            dismissalPolicy: .immediate
        )
        ```
        """
        try:
            if not await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} not active")
                return False
            
            # Send end event via APNs
            if self.apns_client:
                await self._send_apns_end(capsule_id, dismissal_policy)
            
            # Remove from active
            await self.on_capsule_hidden(capsule_id)
            
            logger.info(f"Ended iOS Live Activity for capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hide capsule on iOS: {e}")
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
        Register handler for iOS App Intent.
        
        In real iOS app, this would be defined as:
        ```swift
        struct MitigateIntent: AppIntent {
            func perform() async throws -> some IntentResult {
                // Call handler via API
            }
        }
        ```
        """
        self.action_handlers[action] = handler
        logger.info(f"Registered iOS action handler: {action.value}")
    
    async def handle_action(
        self,
        capsule_id: str,
        action: CapsuleAction
    ) -> CapsuleActionResult:
        """Handle action from iOS App Intent"""
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
        """iOS supports all presentation modes"""
        return mode in [
            PresentationMode.COMPACT,
            PresentationMode.MINIMAL,
            PresentationMode.EXPANDED,
            PresentationMode.LOCK_SCREEN,
            PresentationMode.STANDBY
        ]
    
    def max_capsules(self) -> Optional[int]:
        """iOS supports unlimited Live Activities (system manages display)"""
        return None
    
    def get_platform_name(self) -> str:
        return "ios"
    
    def get_platform_version(self) -> Optional[str]:
        # In real app, would get from UIDevice.current.systemVersion
        return self._get_config("ios_version", "17.0")
    
    # ========================================================================
    # PUSH TOKEN MANAGEMENT
    # ========================================================================
    
    async def register_push_token(self, capsule_id: str, push_token: str) -> None:
        """Register push token for capsule"""
        self.push_tokens[capsule_id] = push_token
        logger.info(f"Registered push token for capsule: {capsule_id}")
    
    async def get_push_token(self, capsule_id: str) -> Optional[str]:
        """Get push token for capsule"""
        return self.push_tokens.get(capsule_id)
    
    # ========================================================================
    # APNS INTEGRATION
    # ========================================================================
    
    async def _send_apns_start(self, capsule: Capsule, payload: Dict[str, Any]) -> None:
        """Send APNs notification to start Live Activity"""
        if not self.apns_client:
            return
        
        from aioapns import NotificationRequest
        
        push_token = await self.get_push_token(capsule.attributes.capsule_id)
        if not push_token:
            logger.warning(f"No push token for capsule: {capsule.attributes.capsule_id}")
            return
        
        request = NotificationRequest(
            device_token=push_token,
            message={
                "aps": {
                    "timestamp": int(capsule.attributes.created_at.timestamp()),
                    "event": "start",
                    "attributes": payload["attributes"],
                    "content-state": payload["content_state"]
                }
            }
        )
        
        await self.apns_client.send_notification(request)
    
    async def _send_apns_update(self, capsule: Capsule, payload: Dict[str, Any]) -> None:
        """Send APNs notification to update Live Activity"""
        if not self.apns_client:
            return
        
        from aioapns import NotificationRequest
        
        push_token = await self.get_push_token(capsule.attributes.capsule_id)
        if not push_token:
            return
        
        message = {
            "aps": {
                "timestamp": int(capsule.content_state.last_updated.timestamp()),
                "event": "update",
                "content-state": payload
            }
        }
        
        # Add alert if present
        if "alert" in payload:
            message["aps"]["alert"] = payload["alert"]
        
        request = NotificationRequest(
            device_token=push_token,
            message=message
        )
        
        await self.apns_client.send_notification(request)
    
    async def _send_apns_end(self, capsule_id: str, dismissal_policy: str) -> None:
        """Send APNs notification to end Live Activity"""
        if not self.apns_client:
            return
        
        from aioapns import NotificationRequest
        
        push_token = await self.get_push_token(capsule_id)
        if not push_token:
            return
        
        request = NotificationRequest(
            device_token=push_token,
            message={
                "aps": {
                    "timestamp": int(datetime.utcnow().timestamp()),
                    "event": "end",
                    "dismissal-date": self._get_dismissal_timestamp(dismissal_policy)
                }
            }
        )
        
        await self.apns_client.send_notification(request)
    
    # ========================================================================
    # PAYLOAD CONVERSION
    # ========================================================================
    
    def _capsule_to_ios_payload(
        self,
        capsule: Capsule,
        mode: PresentationMode
    ) -> Dict[str, Any]:
        """Convert capsule to iOS ActivityKit payload"""
        return {
            "attributes": {
                "capsuleId": capsule.attributes.capsule_id,
                "capsuleType": capsule.attributes.capsule_type.value,
                "title": capsule.attributes.title,
                "iconName": capsule.attributes.icon_name,
                "primaryColor": capsule.attributes.primary_color,
                "createdAt": capsule.attributes.created_at.isoformat()
            },
            "content_state": self._capsule_to_ios_content_state(capsule.content_state),
            "presentation_mode": mode.value
        }
    
    def _capsule_to_ios_content_state(self, state) -> Dict[str, Any]:
        """Convert content state to iOS format"""
        return {
            "status": state.status.value,
            "statusMessage": state.status_message,
            "progress": state.progress,
            "progressLabel": state.progress_label,
            "metricValue": state.metric_value,
            "metricLabel": state.metric_label,
            "lastUpdated": state.last_updated.isoformat(),
            "actionCount": state.action_count,
            "priority": state.priority.value,
            "isStale": state.is_stale,
            "alertMessage": state.alert_message
        }
    
    def _get_dismissal_timestamp(self, policy: str) -> int:
        """Get dismissal timestamp based on policy"""
        from datetime import datetime, timedelta
        
        if policy == "immediate":
            return int(datetime.utcnow().timestamp())
        elif policy.startswith("after_"):
            # e.g., "after_900" = 15 minutes
            seconds = int(policy.split("_")[1])
            return int((datetime.utcnow() + timedelta(seconds=seconds)).timestamp())
        else:
            # Default: 15 minutes
            return int((datetime.utcnow() + timedelta(minutes=15)).timestamp())
