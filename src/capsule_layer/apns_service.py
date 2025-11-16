"""
APNs Push Notification Service
Production-ready iOS push notifications with aioapns

Author: Manus AI (Industriverse Team)
Date: November 16, 2025
"""

import os
import asyncio
from typing import List, Dict, Optional
from aioapns import APNs, NotificationRequest, PushType
from pathlib import Path


class APNsService:
    """
    Production APNs push notification service
    
    Uses aioapns for high-performance async push notifications
    Supports both development and production environments
    """
    
    def __init__(
        self,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
        topic: Optional[str] = None,
        use_sandbox: bool = False
    ):
        """
        Initialize APNs service
        
        Args:
            cert_path: Path to APNs certificate (.pem)
            key_path: Path to APNs private key (.pem)
            topic: APNs topic (bundle ID)
            use_sandbox: Use sandbox environment (default: False)
        """
        self.cert_path = cert_path or os.getenv('APNS_CERT_PATH')
        self.key_path = key_path or os.getenv('APNS_KEY_PATH')
        self.topic = topic or os.getenv('APNS_TOPIC', 'com.industriverse.capsules')
        self.use_sandbox = use_sandbox or os.getenv('APNS_USE_SANDBOX', 'false').lower() == 'true'
        
        self.client: Optional[APNs] = None
        
        # Validate certificate paths
        if self.cert_path and not Path(self.cert_path).exists():
            print(f"⚠️  APNs certificate not found: {self.cert_path}")
        if self.key_path and not Path(self.key_path).exists():
            print(f"⚠️  APNs key not found: {self.key_path}")
    
    async def connect(self):
        """Connect to APNs"""
        try:
            if not self.cert_path or not self.key_path:
                print("⚠️  APNs credentials not configured, push notifications disabled")
                return
            
            self.client = APNs(
                client_cert=self.cert_path,
                use_sandbox=self.use_sandbox,
                topic=self.topic
            )
            
            env = "sandbox" if self.use_sandbox else "production"
            print(f"✅ Connected to APNs ({env})")
            print(f"   Topic: {self.topic}")
            
        except Exception as e:
            print(f"❌ Failed to connect to APNs: {e}")
            self.client = None
    
    async def disconnect(self):
        """Disconnect from APNs"""
        if self.client:
            await self.client.close()
            print("✅ Disconnected from APNs")
    
    async def send_notification(
        self,
        device_token: str,
        title: str,
        message: str,
        priority: str = "medium",
        badge: Optional[int] = None,
        sound: str = "default",
        custom_data: Optional[Dict] = None
    ) -> bool:
        """
        Send push notification to a single device
        
        Args:
            device_token: APNs device token
            title: Notification title
            message: Notification message
            priority: Notification priority (critical, high, medium, low)
            badge: Badge count
            sound: Sound name
            custom_data: Custom data payload
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            print("⚠️  APNs client not connected, skipping notification")
            return False
        
        try:
            # Build notification payload
            alert = {
                "title": title,
                "body": message
            }
            
            aps = {
                "alert": alert,
                "sound": sound
            }
            
            if badge is not None:
                aps["badge"] = badge
            
            # Set interruption level based on priority
            if priority == "critical":
                aps["interruption-level"] = "critical"
            elif priority == "high":
                aps["interruption-level"] = "time-sensitive"
            else:
                aps["interruption-level"] = "active"
            
            # Build full payload
            payload = {"aps": aps}
            
            if custom_data:
                payload.update(custom_data)
            
            # Create notification request
            request = NotificationRequest(
                device_token=device_token,
                message=payload,
                push_type=PushType.ALERT
            )
            
            # Send notification
            response = await self.client.send_notification(request)
            
            if response.is_successful:
                print(f"✅ Push notification sent to {device_token[:16]}...")
                return True
            else:
                print(f"❌ Push notification failed: {response.description}")
                return False
        
        except Exception as e:
            print(f"❌ Error sending push notification: {e}")
            return False
    
    async def send_batch_notifications(
        self,
        device_tokens: List[str],
        title: str,
        message: str,
        priority: str = "medium",
        badge: Optional[int] = None,
        sound: str = "default",
        custom_data: Optional[Dict] = None
    ) -> Dict[str, bool]:
        """
        Send push notifications to multiple devices
        
        Args:
            device_tokens: List of APNs device tokens
            title: Notification title
            message: Notification message
            priority: Notification priority
            badge: Badge count
            sound: Sound name
            custom_data: Custom data payload
            
        Returns:
            Dictionary mapping device_token to success status
        """
        if not self.client:
            print("⚠️  APNs client not connected, skipping notifications")
            return {token: False for token in device_tokens}
        
        results = {}
        
        # Send notifications concurrently
        tasks = []
        for token in device_tokens:
            task = self.send_notification(
                device_token=token,
                title=title,
                message=message,
                priority=priority,
                badge=badge,
                sound=sound,
                custom_data=custom_data
            )
            tasks.append((token, task))
        
        # Wait for all notifications
        for token, task in tasks:
            try:
                success = await task
                results[token] = success
            except Exception as e:
                print(f"❌ Error sending to {token[:16]}...: {e}")
                results[token] = False
        
        successful = sum(1 for v in results.values() if v)
        print(f"📱 Sent {successful}/{len(device_tokens)} push notifications")
        
        return results
    
    async def send_live_activity_update(
        self,
        device_token: str,
        activity_id: str,
        content_state: Dict,
        alert: Optional[Dict] = None,
        priority: int = 10
    ) -> bool:
        """
        Send Live Activity update
        
        Args:
            device_token: APNs device token
            activity_id: Activity identifier
            content_state: Updated content state
            alert: Optional alert dictionary
            priority: Priority (1-10, default: 10)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            print("⚠️  APNs client not connected, skipping Live Activity update")
            return False
        
        try:
            # Build Live Activity payload
            aps = {
                "timestamp": int(asyncio.get_event_loop().time()),
                "event": "update",
                "content-state": content_state
            }
            
            if alert:
                aps["alert"] = alert
            
            payload = {
                "aps": aps,
                "activity-id": activity_id
            }
            
            # Create notification request
            request = NotificationRequest(
                device_token=device_token,
                message=payload,
                push_type=PushType.LIVEACTIVITY,
                priority=priority
            )
            
            # Send update
            response = await self.client.send_notification(request)
            
            if response.is_successful:
                print(f"✅ Live Activity update sent to {device_token[:16]}...")
                return True
            else:
                print(f"❌ Live Activity update failed: {response.description}")
                return False
        
        except Exception as e:
            print(f"❌ Error sending Live Activity update: {e}")
            return False
    
    async def end_live_activity(
        self,
        device_token: str,
        activity_id: str,
        final_content_state: Dict,
        dismissal_date: Optional[int] = None
    ) -> bool:
        """
        End a Live Activity
        
        Args:
            device_token: APNs device token
            activity_id: Activity identifier
            final_content_state: Final content state
            dismissal_date: Unix timestamp for dismissal (default: immediate)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.client:
            print("⚠️  APNs client not connected, skipping Live Activity end")
            return False
        
        try:
            # Build Live Activity end payload
            aps = {
                "timestamp": int(asyncio.get_event_loop().time()),
                "event": "end",
                "content-state": final_content_state
            }
            
            if dismissal_date:
                aps["dismissal-date"] = dismissal_date
            
            payload = {
                "aps": aps,
                "activity-id": activity_id
            }
            
            # Create notification request
            request = NotificationRequest(
                device_token=device_token,
                message=payload,
                push_type=PushType.LIVEACTIVITY
            )
            
            # Send end notification
            response = await self.client.send_notification(request)
            
            if response.is_successful:
                print(f"✅ Live Activity ended for {device_token[:16]}...")
                return True
            else:
                print(f"❌ Live Activity end failed: {response.description}")
                return False
        
        except Exception as e:
            print(f"❌ Error ending Live Activity: {e}")
            return False
