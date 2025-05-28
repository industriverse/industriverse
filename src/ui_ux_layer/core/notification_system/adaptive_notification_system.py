"""
Adaptive Notification System for the Industriverse UI/UX Layer.

This module provides a comprehensive notification system that adapts to user context,
role, device, and industrial environment, delivering ambient awareness through
the Universal Skin and Agent Capsules.

Author: Manus
"""

import logging
import time
import threading
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass
import queue

class NotificationPriority(Enum):
    """Enumeration of notification priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationType(Enum):
    """Enumeration of notification types."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ALERT = "alert"
    ACTION_REQUIRED = "action_required"
    SYSTEM = "system"
    CUSTOM = "custom"

class NotificationChannel(Enum):
    """Enumeration of notification channels."""
    VISUAL = "visual"
    AUDIO = "audio"
    HAPTIC = "haptic"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    AMBIENT = "ambient"
    CUSTOM = "custom"

@dataclass
class Notification:
    """Data class representing a notification."""
    notification_id: str
    title: str
    message: str
    notification_type: NotificationType
    priority: NotificationPriority
    timestamp: float
    source: str
    channels: List[NotificationChannel]
    context_id: Optional[str] = None
    role_id: Optional[str] = None
    user_id: Optional[str] = None
    expiration: Optional[float] = None
    actions: Optional[List[Dict[str, Any]]] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.actions is None:
            self.actions = []

class AdaptiveNotificationSystem:
    """
    Provides a comprehensive notification system for the Industriverse UI/UX Layer.
    
    This class provides:
    - Context-aware notification delivery
    - Role-based notification filtering
    - Multi-channel notification support (visual, audio, haptic)
    - Priority-based notification management
    - Ambient notification display
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Adaptive Notification System.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.notifications: Dict[str, Notification] = {}
        self.notification_queue = queue.PriorityQueue()
        self.notification_listeners: Dict[str, List[Callable[[Notification], None]]] = {}
        self.channel_listeners: Dict[NotificationChannel, List[Callable[[Notification], None]]] = {}
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        self.update_interval: float = self.config.get("update_interval", 0.1)  # 100ms by default
        
        # Initialize notification channels
        for channel in NotificationChannel:
            self.channel_listeners[channel] = []
            
        # Initialize notification queue processor thread
        self.queue_processor_thread = None
        
    def start(self) -> bool:
        """
        Start the Adaptive Notification System.
        
        Returns:
            True if the system was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start notification queue processor thread
        self.queue_processor_thread = threading.Thread(target=self._process_notification_queue, daemon=True)
        self.queue_processor_thread.start()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "notification_system_started"
        })
        
        self.logger.info("Adaptive Notification System started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Adaptive Notification System.
        
        Returns:
            True if the system was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "notification_system_stopped"
        })
        
        self.logger.info("Adaptive Notification System stopped.")
        return True
    
    def create_notification(self,
                          title: str,
                          message: str,
                          notification_type: NotificationType,
                          priority: NotificationPriority,
                          source: str,
                          channels: List[NotificationChannel],
                          context_id: Optional[str] = None,
                          role_id: Optional[str] = None,
                          user_id: Optional[str] = None,
                          expiration: Optional[float] = None,
                          actions: Optional[List[Dict[str, Any]]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new notification.
        
        Args:
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Notification priority
            source: Source of the notification
            channels: Channels to deliver the notification through
            context_id: Optional context ID for context-specific notifications
            role_id: Optional role ID for role-specific notifications
            user_id: Optional user ID for user-specific notifications
            expiration: Optional expiration time (Unix timestamp)
            actions: Optional list of actions that can be taken on this notification
            metadata: Additional metadata for this notification
            
        Returns:
            The notification ID
        """
        notification_id = str(uuid.uuid4())
        timestamp = time.time()
        
        notification = Notification(
            notification_id=notification_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            timestamp=timestamp,
            source=source,
            channels=channels,
            context_id=context_id,
            role_id=role_id,
            user_id=user_id,
            expiration=expiration,
            actions=actions,
            metadata=metadata or {}
        )
        
        self.notifications[notification_id] = notification
        
        # Add to notification queue with priority
        priority_value = self._get_priority_value(priority)
        self.notification_queue.put((priority_value, notification))
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "notification_created",
            "notification_id": notification_id,
            "title": title,
            "notification_type": notification_type.value,
            "priority": priority.value,
            "source": source
        })
        
        self.logger.debug(f"Created notification: {notification_id} ({title})")
        return notification_id
    
    def update_notification(self,
                          notification_id: str,
                          title: Optional[str] = None,
                          message: Optional[str] = None,
                          notification_type: Optional[NotificationType] = None,
                          priority: Optional[NotificationPriority] = None,
                          channels: Optional[List[NotificationChannel]] = None,
                          expiration: Optional[float] = None,
                          actions: Optional[List[Dict[str, Any]]] = None,
                          metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an existing notification.
        
        Args:
            notification_id: ID of the notification to update
            title: Optional new title
            message: Optional new message
            notification_type: Optional new notification type
            priority: Optional new priority
            channels: Optional new channels
            expiration: Optional new expiration time
            actions: Optional new actions
            metadata: Optional new metadata
            
        Returns:
            True if the notification was updated, False if not found
        """
        if notification_id not in self.notifications:
            self.logger.warning(f"Notification {notification_id} not found.")
            return False
            
        notification = self.notifications[notification_id]
        
        # Update notification properties
        if title is not None:
            notification.title = title
        if message is not None:
            notification.message = message
        if notification_type is not None:
            notification.notification_type = notification_type
        if priority is not None:
            notification.priority = priority
        if channels is not None:
            notification.channels = channels
        if expiration is not None:
            notification.expiration = expiration
        if actions is not None:
            notification.actions = actions
        if metadata is not None:
            notification.metadata.update(metadata)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "notification_updated",
            "notification_id": notification_id,
            "title": notification.title,
            "notification_type": notification.notification_type.value,
            "priority": notification.priority.value
        })
        
        self.logger.debug(f"Updated notification: {notification_id}")
        return True
    
    def delete_notification(self, notification_id: str) -> bool:
        """
        Delete a notification.
        
        Args:
            notification_id: ID of the notification to delete
            
        Returns:
            True if the notification was deleted, False if not found
        """
        if notification_id not in self.notifications:
            self.logger.warning(f"Notification {notification_id} not found.")
            return False
            
        notification = self.notifications[notification_id]
        
        # Remove notification
        del self.notifications[notification_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "notification_deleted",
            "notification_id": notification_id,
            "title": notification.title,
            "notification_type": notification.notification_type.value,
            "priority": notification.priority.value
        })
        
        self.logger.debug(f"Deleted notification: {notification_id}")
        return True
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Get a notification by ID.
        
        Args:
            notification_id: ID of the notification to get
            
        Returns:
            The notification, or None if not found
        """
        return self.notifications.get(notification_id)
    
    def get_notifications(self,
                        limit: int = 100,
                        notification_type: Optional[NotificationType] = None,
                        priority: Optional[NotificationPriority] = None,
                        source: Optional[str] = None,
                        context_id: Optional[str] = None,
                        role_id: Optional[str] = None,
                        user_id: Optional[str] = None,
                        start_time: Optional[float] = None,
                        end_time: Optional[float] = None) -> List[Notification]:
        """
        Get notifications with optional filtering.
        
        Args:
            limit: Maximum number of notifications to return
            notification_type: Optional filter by notification type
            priority: Optional filter by priority
            source: Optional filter by source
            context_id: Optional filter by context ID
            role_id: Optional filter by role ID
            user_id: Optional filter by user ID
            start_time: Optional start time (Unix timestamp)
            end_time: Optional end time (Unix timestamp)
            
        Returns:
            List of notifications matching the filters
        """
        # Get all notifications
        notifications = list(self.notifications.values())
        
        # Apply filters
        filtered_notifications = []
        for notification in notifications:
            # Filter by notification type
            if notification_type is not None and notification.notification_type != notification_type:
                continue
                
            # Filter by priority
            if priority is not None and notification.priority != priority:
                continue
                
            # Filter by source
            if source is not None and notification.source != source:
                continue
                
            # Filter by context ID
            if context_id is not None and notification.context_id != context_id:
                continue
                
            # Filter by role ID
            if role_id is not None and notification.role_id != role_id:
                continue
                
            # Filter by user ID
            if user_id is not None and notification.user_id != user_id:
                continue
                
            # Filter by time range
            if start_time is not None and notification.timestamp < start_time:
                continue
                
            if end_time is not None and notification.timestamp > end_time:
                continue
                
            # Check if notification has expired
            if notification.expiration is not None and time.time() > notification.expiration:
                continue
                
            filtered_notifications.append(notification)
            
        # Sort by timestamp (newest first)
        filtered_notifications.sort(key=lambda n: n.timestamp, reverse=True)
        
        # Limit number of notifications
        return filtered_notifications[:limit]
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of the notification to mark as read
            
        Returns:
            True if the notification was marked as read, False if not found
        """
        if notification_id not in self.notifications:
            self.logger.warning(f"Notification {notification_id} not found.")
            return False
            
        notification = self.notifications[notification_id]
        
        # Update metadata to mark as read
        notification.metadata["read"] = True
        notification.metadata["read_timestamp"] = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "notification_marked_as_read",
            "notification_id": notification_id,
            "title": notification.title
        })
        
        self.logger.debug(f"Marked notification as read: {notification_id}")
        return True
    
    def mark_all_as_read(self,
                       context_id: Optional[str] = None,
                       role_id: Optional[str] = None,
                       user_id: Optional[str] = None) -> int:
        """
        Mark all notifications as read, with optional filtering.
        
        Args:
            context_id: Optional filter by context ID
            role_id: Optional filter by role ID
            user_id: Optional filter by user ID
            
        Returns:
            Number of notifications marked as read
        """
        count = 0
        
        for notification_id, notification in self.notifications.items():
            # Apply filters
            if context_id is not None and notification.context_id != context_id:
                continue
                
            if role_id is not None and notification.role_id != role_id:
                continue
                
            if user_id is not None and notification.user_id != user_id:
                continue
                
            # Skip if already read
            if notification.metadata.get("read", False):
                continue
                
            # Mark as read
            notification.metadata["read"] = True
            notification.metadata["read_timestamp"] = time.time()
            count += 1
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "notifications_marked_as_read",
            "count": count,
            "context_id": context_id,
            "role_id": role_id,
            "user_id": user_id
        })
        
        self.logger.debug(f"Marked {count} notifications as read")
        return count
    
    def execute_action(self, notification_id: str, action_id: str) -> bool:
        """
        Execute an action on a notification.
        
        Args:
            notification_id: ID of the notification
            action_id: ID of the action to execute
            
        Returns:
            True if the action was executed, False if notification or action not found
        """
        if notification_id not in self.notifications:
            self.logger.warning(f"Notification {notification_id} not found.")
            return False
            
        notification = self.notifications[notification_id]
        
        # Find the action
        action = None
        for a in notification.actions:
            if a.get("id") == action_id:
                action = a
                break
                
        if action is None:
            self.logger.warning(f"Action {action_id} not found in notification {notification_id}.")
            return False
            
        # Execute the action
        try:
            # In a real implementation, this would execute the action
            # For now, we'll just log it
            self.logger.info(f"Executing action {action_id} on notification {notification_id}")
            
            # Update metadata to record action execution
            notification.metadata["action_executed"] = action_id
            notification.metadata["action_timestamp"] = time.time()
            
            # Dispatch event
            self._dispatch_event({
                "event_type": "notification_action_executed",
                "notification_id": notification_id,
                "action_id": action_id,
                "title": notification.title
            })
            
            return True
        except Exception as e:
            self.logger.error(f"Error executing action {action_id} on notification {notification_id}: {e}")
            return False
    
    def add_notification_listener(self, notification_id: str, listener: Callable[[Notification], None]) -> bool:
        """
        Add a listener for a specific notification.
        
        Args:
            notification_id: ID of the notification
            listener: Callback function that will be called when the notification is updated
            
        Returns:
            True if the listener was added, False if notification not found
        """
        if notification_id not in self.notifications:
            self.logger.warning(f"Notification {notification_id} not found.")
            return False
            
        if notification_id not in self.notification_listeners:
            self.notification_listeners[notification_id] = []
            
        self.notification_listeners[notification_id].append(listener)
        return True
    
    def add_channel_listener(self, channel: NotificationChannel, listener: Callable[[Notification], None]) -> bool:
        """
        Add a listener for a specific notification channel.
        
        Args:
            channel: The notification channel
            listener: Callback function that will be called when a notification is delivered through this channel
            
        Returns:
            True if the listener was added
        """
        self.channel_listeners[channel].append(listener)
        return True
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all notification system events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.event_listeners.append(listener)
        
    def remove_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.event_listeners:
            self.event_listeners.remove(listener)
            return True
            
        return False
    
    def _dispatch_event(self, event_data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_data: The event data to dispatch
        """
        # Add source if not present
        if "source" not in event_data:
            event_data["source"] = "AdaptiveNotificationSystem"
            
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = time.time()
            
        # Dispatch to global event listeners
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in notification event listener: {e}")
                
    def _get_priority_value(self, priority: NotificationPriority) -> int:
        """
        Get the numeric priority value for a notification priority.
        
        Args:
            priority: The notification priority
            
        Returns:
            The numeric priority value (lower is higher priority)
        """
        if priority == NotificationPriority.CRITICAL:
            return 0
        elif priority == NotificationPriority.HIGH:
            return 1
        elif priority == NotificationPriority.MEDIUM:
            return 2
        elif priority == NotificationPriority.LOW:
            return 3
        else:
            return 4
            
    def _process_notification_queue(self) -> None:
        """Background thread for processing the notification queue."""
        while self.is_active:
            try:
                # Get the next notification from the queue (if any)
                try:
                    _, notification = self.notification_queue.get(block=True, timeout=0.1)
                except queue.Empty:
                    continue
                    
                # Check if notification has expired
                if notification.expiration is not None and time.time() > notification.expiration:
                    self.notification_queue.task_done()
                    continue
                    
                # Process the notification
                self._deliver_notification(notification)
                
                # Mark the task as done
                self.notification_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in notification queue processor: {e}")
                
    def _deliver_notification(self, notification: Notification) -> None:
        """
        Deliver a notification through its channels.
        
        Args:
            notification: The notification to deliver
        """
        # Notify notification-specific listeners
        if notification.notification_id in self.notification_listeners:
            for listener in self.notification_listeners[notification.notification_id]:
                try:
                    listener(notification)
                except Exception as e:
                    self.logger.error(f"Error in notification listener for {notification.notification_id}: {e}")
                    
        # Deliver through each channel
        for channel in notification.channels:
            # Notify channel-specific listeners
            for listener in self.channel_listeners[channel]:
                try:
                    listener(notification)
                except Exception as e:
                    self.logger.error(f"Error in channel listener for {channel.value}: {e}")
                    
            # Dispatch channel delivery event
            self._dispatch_event({
                "event_type": "notification_delivered",
                "notification_id": notification.notification_id,
                "channel": channel.value,
                "title": notification.title,
                "notification_type": notification.notification_type.value,
                "priority": notification.priority.value
            })
            
        self.logger.debug(f"Delivered notification: {notification.notification_id} ({notification.title})")

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create adaptive notification system
    notification_system = AdaptiveNotificationSystem()
    
    # Start the system
    notification_system.start()
    
    # Add a channel listener for visual notifications
    def on_visual_notification(notification):
        print(f"Visual Notification: {notification.title} - {notification.message}")
        
    notification_system.add_channel_listener(NotificationChannel.VISUAL, on_visual_notification)
    
    # Add a channel listener for audio notifications
    def on_audio_notification(notification):
        print(f"Audio Notification: {notification.title} - {notification.message}")
        
    notification_system.add_channel_listener(NotificationChannel.AUDIO, on_audio_notification)
    
    # Create a notification
    notification_id = notification_system.create_notification(
        title="System Update Available",
        message="A new system update is available. Please install at your earliest convenience.",
        notification_type=NotificationType.INFO,
        priority=NotificationPriority.MEDIUM,
        source="SystemUpdateManager",
        channels=[NotificationChannel.VISUAL, NotificationChannel.AMBIENT],
        context_id="manufacturing",
        role_id="system_administrator",
        actions=[
            {
                "id": "install_now",
                "label": "Install Now",
                "type": "button",
                "primary": True
            },
            {
                "id": "remind_later",
                "label": "Remind Later",
                "type": "button",
                "primary": False
            }
        ]
    )
    
    # Create a high-priority notification
    critical_notification_id = notification_system.create_notification(
        title="Critical Temperature Alert",
        message="Machine XYZ temperature has exceeded critical threshold (95°C).",
        notification_type=NotificationType.ALERT,
        priority=NotificationPriority.CRITICAL,
        source="TemperatureMonitor",
        channels=[NotificationChannel.VISUAL, NotificationChannel.AUDIO, NotificationChannel.HAPTIC],
        context_id="manufacturing",
        role_id="line_operator",
        actions=[
            {
                "id": "shutdown",
                "label": "Emergency Shutdown",
                "type": "button",
                "primary": True,
                "color": "red"
            },
            {
                "id": "acknowledge",
                "label": "Acknowledge",
                "type": "button",
                "primary": False
            }
        ]
    )
    
    # Wait a bit to see notifications being processed
    time.sleep(1)
    
    # Execute an action on a notification
    notification_system.execute_action(critical_notification_id, "acknowledge")
    
    # Mark a notification as read
    notification_system.mark_as_read(notification_id)
    
    # Get all notifications
    notifications = notification_system.get_notifications()
    print(f"Retrieved {len(notifications)} notifications")
    
    # Stop the system
    notification_system.stop()
