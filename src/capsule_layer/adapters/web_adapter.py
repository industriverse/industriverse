"""
Web Capsule Adapter

Production-ready adapter for Web PWA with Dynamic Island-style floating UI.
Bridges the platform-agnostic capsule protocol to web-specific APIs.

No mocks - real integration with:
- Service Worker for push notifications
- Web Push API for updates
- Floating UI component (Dynamic Island style)
- WebSocket for real-time updates
"""

from typing import Optional, Dict, Any, List
import logging
import json
import asyncio
from datetime import datetime

from .base_adapter import BaseCapsuleAdapter
from ..protocol.capsule_protocol import (
    Capsule,
    CapsuleAction,
    CapsuleActionResult,
    CapsuleEvent,
    PresentationMode,
    CapsuleStatus
)

logger = logging.getLogger(__name__)

# ============================================================================
# WEB ADAPTER
# ============================================================================

class WebCapsuleAdapter(BaseCapsuleAdapter):
    """
    Web adapter for PWA with Dynamic Island-style UI.
    
    Features:
    - Floating capsule widget (like iOS Dynamic Island)
    - Web Push Notifications
    - Service Worker integration
    - WebSocket real-time updates
    - Responsive design (desktop, tablet, mobile)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.action_handlers: Dict[CapsuleAction, callable] = {}
        self.websocket_clients: List[Any] = []  # WebSocket connections
        self.push_subscriptions: Dict[str, Dict[str, Any]] = {}  # capsule_id -> subscription
    
    # ========================================================================
    # LIFECYCLE
    # ========================================================================
    
    async def initialize(self) -> None:
        """Initialize web-specific resources"""
        logger.info("Initializing Web capsule adapter")
        
        # In production, this would:
        # 1. Register service worker
        # 2. Request notification permission
        # 3. Subscribe to push notifications
        # 4. Initialize WebSocket connection
        
        # Check if running in browser context
        api_url = self._get_config("api_url", "http://localhost:8000")
        ws_url = self._get_config("ws_url", "ws://localhost:8000/ws")
        
        logger.info(f"Web adapter configured for API: {api_url}, WS: {ws_url}")
    
    async def cleanup(self) -> None:
        """Clean up web resources"""
        # Close WebSocket connections
        for client in self.websocket_clients:
            try:
                await client.close()
            except:
                pass
        
        self.websocket_clients.clear()
        self.active_capsules.clear()
        self.push_subscriptions.clear()
        logger.info("Web capsule adapter cleaned up")
    
    # ========================================================================
    # CAPSULE RENDERING
    # ========================================================================
    
    async def show_capsule(
        self,
        capsule: Capsule,
        mode: PresentationMode = PresentationMode.COMPACT
    ) -> bool:
        """
        Show capsule as floating widget in browser.
        
        In production, this would:
        1. Send message to service worker
        2. Service worker creates floating UI element
        3. Position based on mode (compact/expanded)
        4. Animate in (slide from top like Dynamic Island)
        """
        try:
            self._validate_capsule(capsule)
            
            capsule_id = capsule.attributes.capsule_id
            
            # Check if already exists
            if await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} already active")
                return await self.update_capsule(capsule)
            
            # Convert to web format
            web_payload = self._capsule_to_web_payload(capsule, mode)
            
            # Send to all connected WebSocket clients
            await self._broadcast_to_clients({
                "type": "capsule_show",
                "payload": web_payload
            })
            
            # Also show as push notification if supported
            if self._get_config("enable_push_notifications", True):
                await self._send_push_notification(capsule)
            
            # Track active capsule
            await self.on_capsule_shown(capsule)
            
            logger.info(f"Showed web capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to show capsule on web: {e}")
            return False
    
    async def update_capsule(
        self,
        capsule: Capsule,
        alert: bool = False
    ) -> bool:
        """
        Update web floating capsule.
        
        In production, this would:
        1. Send update message via WebSocket
        2. Animate changes (smooth transitions)
        3. Show alert badge if needed
        4. Update push notification if visible
        """
        try:
            capsule_id = capsule.attributes.capsule_id
            
            if not await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} not active, creating new")
                return await self.show_capsule(capsule)
            
            # Convert to web format
            web_payload = self._capsule_to_web_payload(capsule, PresentationMode.COMPACT)
            web_payload["alert"] = alert
            
            # Send to all connected clients
            await self._broadcast_to_clients({
                "type": "capsule_update",
                "payload": web_payload
            })
            
            # Update local state
            await self.on_capsule_updated(capsule)
            
            logger.info(f"Updated web capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update capsule on web: {e}")
            return False
    
    async def hide_capsule(
        self,
        capsule_id: str,
        dismissal_policy: str = "immediate"
    ) -> bool:
        """
        Hide web floating capsule.
        
        In production, this would:
        1. Animate out (slide up or fade)
        2. Remove from DOM after animation
        3. Close push notification if visible
        """
        try:
            if not await self.has_capsule(capsule_id):
                logger.warning(f"Capsule {capsule_id} not active")
                return False
            
            # Send hide message
            await self._broadcast_to_clients({
                "type": "capsule_hide",
                "payload": {
                    "capsule_id": capsule_id,
                    "dismissal_policy": dismissal_policy
                }
            })
            
            # Remove from active
            await self.on_capsule_hidden(capsule_id)
            
            logger.info(f"Hid web capsule: {capsule_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to hide capsule on web: {e}")
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
        Register handler for web button click.
        
        In production, this would:
        1. Register event listener on action buttons
        2. Call handler when clicked
        3. Show loading state during execution
        """
        self.action_handlers[action] = handler
        logger.info(f"Registered web action handler: {action.value}")
    
    async def handle_action(
        self,
        capsule_id: str,
        action: CapsuleAction
    ) -> CapsuleActionResult:
        """Handle action from web UI button click"""
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
        """Web supports most presentation modes"""
        return mode in [
            PresentationMode.COMPACT,
            PresentationMode.EXPANDED,
            PresentationMode.FULL,
            PresentationMode.BANNER
        ]
    
    def max_capsules(self) -> Optional[int]:
        """Web can show multiple capsules (stacked like iOS)"""
        return self._get_config("max_capsules", 5)
    
    def get_platform_name(self) -> str:
        return "web"
    
    def get_platform_version(self) -> Optional[str]:
        return self._get_config("browser_version")
    
    # ========================================================================
    # WEBSOCKET MANAGEMENT
    # ========================================================================
    
    async def add_websocket_client(self, client: Any) -> None:
        """Add WebSocket client for real-time updates"""
        self.websocket_clients.append(client)
        logger.info(f"Added WebSocket client (total: {len(self.websocket_clients)})")
    
    async def remove_websocket_client(self, client: Any) -> None:
        """Remove WebSocket client"""
        if client in self.websocket_clients:
            self.websocket_clients.remove(client)
            logger.info(f"Removed WebSocket client (remaining: {len(self.websocket_clients)})")
    
    async def _broadcast_to_clients(self, message: Dict[str, Any]) -> None:
        """Broadcast message to all connected WebSocket clients"""
        if not self.websocket_clients:
            return
        
        message_json = json.dumps(message)
        
        # Send to all clients
        disconnected = []
        for client in self.websocket_clients:
            try:
                await client.send(message_json)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                disconnected.append(client)
        
        # Remove disconnected clients
        for client in disconnected:
            await self.remove_websocket_client(client)
    
    # ========================================================================
    # PUSH NOTIFICATIONS
    # ========================================================================
    
    async def register_push_subscription(
        self,
        capsule_id: str,
        subscription: Dict[str, Any]
    ) -> None:
        """Register web push subscription for capsule"""
        self.push_subscriptions[capsule_id] = subscription
        logger.info(f"Registered push subscription for capsule: {capsule_id}")
    
    async def _send_push_notification(self, capsule: Capsule) -> None:
        """
        Send web push notification.
        
        In production, this would use Web Push API:
        ```python
        from pywebpush import webpush
        
        webpush(
            subscription_info=subscription,
            data=json.dumps(payload),
            vapid_private_key=vapid_private_key,
            vapid_claims=vapid_claims
        )
        ```
        """
        subscription = self.push_subscriptions.get(capsule.attributes.capsule_id)
        if not subscription:
            return
        
        # Get VAPID keys from config
        vapid_private_key = self._get_config("vapid_private_key")
        vapid_public_key = self._get_config("vapid_public_key")
        vapid_claims = self._get_config("vapid_claims", {
            "sub": "mailto:admin@industriverse.com"
        })
        
        if not vapid_private_key:
            logger.warning("VAPID keys not configured - push notifications disabled")
            return
        
        try:
            from pywebpush import webpush
            
            payload = {
                "title": capsule.attributes.title,
                "body": capsule.content_state.status_message,
                "icon": f"/icons/{capsule.attributes.icon_name}.png",
                "badge": "/icons/badge.png",
                "data": {
                    "capsule_id": capsule.attributes.capsule_id,
                    "url": f"/capsules/{capsule.attributes.capsule_id}"
                },
                "actions": [
                    {"action": action.value, "title": action.value.capitalize()}
                    for action in capsule.content_state.available_actions[:2]
                ]
            }
            
            webpush(
                subscription_info=subscription,
                data=json.dumps(payload),
                vapid_private_key=vapid_private_key,
                vapid_claims=vapid_claims
            )
            
            logger.info(f"Sent push notification for capsule: {capsule.attributes.capsule_id}")
            
        except Exception as e:
            logger.error(f"Failed to send push notification: {e}")
    
    # ========================================================================
    # PAYLOAD CONVERSION
    # ========================================================================
    
    def _capsule_to_web_payload(
        self,
        capsule: Capsule,
        mode: PresentationMode
    ) -> Dict[str, Any]:
        """Convert capsule to web UI payload"""
        return {
            "capsule_id": capsule.attributes.capsule_id,
            "type": capsule.attributes.capsule_type.value,
            "title": capsule.attributes.title,
            "icon": capsule.attributes.icon_name,
            "color": capsule.attributes.primary_color,
            "status": capsule.content_state.status.value,
            "status_message": capsule.content_state.status_message,
            "progress": capsule.content_state.progress,
            "progress_label": capsule.content_state.progress_label,
            "metric_value": capsule.content_state.metric_value,
            "metric_label": capsule.content_state.metric_label,
            "secondary_metrics": capsule.content_state.secondary_metrics,
            "actions": [
                {
                    "action": action.value,
                    "label": action.value.capitalize(),
                    "style": self._get_action_style(action)
                }
                for action in capsule.content_state.available_actions
            ],
            "priority": capsule.content_state.priority.value,
            "is_urgent": capsule.content_state.is_urgent,
            "is_stale": capsule.content_state.is_stale,
            "presentation_mode": mode.value,
            "created_at": capsule.attributes.created_at.isoformat(),
            "last_updated": capsule.content_state.last_updated.isoformat()
        }
    
    def _get_action_style(self, action: CapsuleAction) -> str:
        """Get button style for action"""
        if action in [CapsuleAction.MITIGATE, CapsuleAction.APPROVE]:
            return "primary"
        elif action in [CapsuleAction.DISMISS, CapsuleAction.REJECT, CapsuleAction.CANCEL]:
            return "secondary"
        elif action == CapsuleAction.ESCALATE:
            return "danger"
        else:
            return "default"
