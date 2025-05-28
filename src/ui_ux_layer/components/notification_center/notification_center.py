"""
Notification Center Component for the Industriverse UI/UX Layer.

This module provides a centralized notification management system that displays
and manages notifications from various sources across the Industriverse ecosystem.

Author: Manus
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime

class NotificationPriority(Enum):
    """Enumeration of notification priorities."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationCategory(Enum):
    """Enumeration of notification categories."""
    SYSTEM = "system"
    PROCESS = "process"
    ALERT = "alert"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    TASK = "task"
    WORKFLOW = "workflow"
    AGENT = "agent"
    CUSTOM = "custom"

class NotificationStatus(Enum):
    """Enumeration of notification statuses."""
    UNREAD = "unread"
    READ = "read"
    ACKNOWLEDGED = "acknowledged"
    DISMISSED = "dismissed"
    ACTIONED = "actioned"
    EXPIRED = "expired"

class NotificationEventType(Enum):
    """Enumeration of notification event types."""
    NOTIFICATION_ADDED = "notification_added"
    NOTIFICATION_UPDATED = "notification_updated"
    NOTIFICATION_REMOVED = "notification_removed"
    NOTIFICATION_STATUS_CHANGED = "notification_status_changed"
    NOTIFICATION_ACTIONED = "notification_actioned"
    FILTER_CHANGED = "filter_changed"
    SORT_CHANGED = "sort_changed"
    GROUP_CHANGED = "group_changed"
    VISIBILITY_CHANGED = "visibility_changed"
    CUSTOM = "custom"

@dataclass
class NotificationStyle:
    """Data class representing notification styling options."""
    background_color: str = "#FFFFFF"
    text_color: str = "#333333"
    accent_color: str = "#4285F4"
    border_color: str = "#E0E0E0"
    border_radius: int = 8
    shadow: str = "0 2px 10px rgba(0, 0, 0, 0.1)"
    font_family: str = "Roboto, sans-serif"
    title_font_size: int = 16
    body_font_size: int = 14
    padding: int = 16
    margin: int = 8
    animation_duration: int = 300
    custom_css: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NotificationAction:
    """Data class representing a notification action."""
    action_id: str
    label: str
    icon: str
    handler: Callable[[Dict[str, Any]], Any]
    enabled: bool = True
    primary: bool = False
    style: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the action to a dictionary."""
        return {
            "id": self.action_id,
            "label": self.label,
            "icon": self.icon,
            "enabled": self.enabled,
            "primary": self.primary,
            "style": self.style
        }

@dataclass
class NotificationEvent:
    """Data class representing a notification event."""
    event_type: NotificationEventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class Notification:
    """Data class representing a notification."""
    notification_id: str
    title: str
    message: str
    source: str
    category: NotificationCategory
    priority: NotificationPriority
    timestamp: float
    status: NotificationStatus = NotificationStatus.UNREAD
    actions: List[NotificationAction] = field(default_factory=list)
    icon: Optional[str] = None
    image: Optional[str] = None
    expiration: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the notification to a dictionary."""
        return {
            "id": self.notification_id,
            "title": self.title,
            "message": self.message,
            "source": self.source,
            "category": self.category.value,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "status": self.status.value,
            "actions": [action.to_dict() for action in self.actions],
            "icon": self.icon,
            "image": self.image,
            "expiration": self.expiration,
            "metadata": self.metadata,
            "style": self.style
        }

class NotificationCenterComponent:
    """
    Provides a centralized notification management system for the Industriverse UI/UX Layer.
    
    This class provides:
    - Notification creation and management
    - Notification filtering, sorting, and grouping
    - Notification actions and status management
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Notification Center Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_visible = False
        self.style = NotificationStyle()
        self.notifications: Dict[str, Notification] = {}
        self.filters: Dict[str, Any] = {}
        self.sort_by: str = "timestamp"
        self.sort_order: str = "desc"
        self.group_by: Optional[str] = "category"
        self.event_listeners: Dict[NotificationEventType, List[Callable[[NotificationEvent], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize from config if provided
        if config:
            if "visible" in config:
                self.is_visible = bool(config["visible"])
                
            if "style" in config:
                for key, value in config["style"].items():
                    if hasattr(self.style, key):
                        setattr(self.style, key, value)
                    else:
                        self.style.custom_css[key] = value
                        
            if "filters" in config:
                self.filters = config["filters"]
                
            if "sort_by" in config:
                self.sort_by = config["sort_by"]
                
            if "sort_order" in config:
                self.sort_order = config["sort_order"]
                
            if "group_by" in config:
                self.group_by = config["group_by"]
                
            if "notifications" in config:
                for notification_config in config["notifications"]:
                    if not self._validate_notification_config(notification_config):
                        continue
                        
                    # Create actions
                    actions = []
                    if "actions" in notification_config:
                        for action_config in notification_config["actions"]:
                            if not self._validate_action_config(action_config):
                                continue
                                
                            # Create a dummy handler if not provided
                            handler = action_config.get("handler", lambda data: None)
                            
                            actions.append(NotificationAction(
                                action_id=action_config["id"],
                                label=action_config["label"],
                                icon=action_config["icon"],
                                handler=handler,
                                enabled=action_config.get("enabled", True),
                                primary=action_config.get("primary", False),
                                style=action_config.get("style", {})
                            ))
                            
                    # Create notification
                    try:
                        category = NotificationCategory(notification_config["category"])
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid category: {notification_config['category']}, using CUSTOM.")
                        category = NotificationCategory.CUSTOM
                        
                    try:
                        priority = NotificationPriority(notification_config["priority"])
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid priority: {notification_config['priority']}, using MEDIUM.")
                        priority = NotificationPriority.MEDIUM
                        
                    try:
                        status = NotificationStatus(notification_config.get("status", "unread"))
                    except (ValueError, TypeError):
                        self.logger.warning(f"Invalid status: {notification_config.get('status')}, using UNREAD.")
                        status = NotificationStatus.UNREAD
                        
                    self.notifications[notification_config["id"]] = Notification(
                        notification_id=notification_config["id"],
                        title=notification_config["title"],
                        message=notification_config["message"],
                        source=notification_config["source"],
                        category=category,
                        priority=priority,
                        timestamp=notification_config.get("timestamp", time.time()),
                        status=status,
                        actions=actions,
                        icon=notification_config.get("icon"),
                        image=notification_config.get("image"),
                        expiration=notification_config.get("expiration"),
                        metadata=notification_config.get("metadata", {}),
                        style=notification_config.get("style", {})
                    )
        
    def add_notification(self,
                       title: str,
                       message: str,
                       source: str,
                       category: Union[NotificationCategory, str],
                       priority: Union[NotificationPriority, str] = NotificationPriority.MEDIUM,
                       actions: Optional[List[Dict[str, Any]]] = None,
                       icon: Optional[str] = None,
                       image: Optional[str] = None,
                       expiration: Optional[float] = None,
                       metadata: Optional[Dict[str, Any]] = None,
                       style: Optional[Dict[str, Any]] = None,
                       notification_id: Optional[str] = None) -> str:
        """
        Add a notification to the notification center.
        
        Args:
            title: Title of the notification
            message: Message of the notification
            source: Source of the notification
            category: Category of the notification
            priority: Priority of the notification
            actions: Optional list of actions
            icon: Optional icon
            image: Optional image
            expiration: Optional expiration timestamp
            metadata: Optional metadata
            style: Optional style configuration
            notification_id: Optional notification ID, generated if not provided
            
        Returns:
            The notification ID
        """
        # Generate notification ID if not provided
        if notification_id is None:
            notification_id = str(uuid.uuid4())
            
        # Convert category to NotificationCategory if needed
        if not isinstance(category, NotificationCategory):
            try:
                category = NotificationCategory(category)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid category: {category}, using CUSTOM.")
                category = NotificationCategory.CUSTOM
                
        # Convert priority to NotificationPriority if needed
        if not isinstance(priority, NotificationPriority):
            try:
                priority = NotificationPriority(priority)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid priority: {priority}, using MEDIUM.")
                priority = NotificationPriority.MEDIUM
                
        # Create actions
        notification_actions = []
        if actions:
            for action_config in actions:
                if not self._validate_action_config(action_config):
                    continue
                    
                # Create a dummy handler if not provided
                handler = action_config.get("handler", lambda data: None)
                
                notification_actions.append(NotificationAction(
                    action_id=action_config.get("id", str(uuid.uuid4())),
                    label=action_config["label"],
                    icon=action_config["icon"],
                    handler=handler,
                    enabled=action_config.get("enabled", True),
                    primary=action_config.get("primary", False),
                    style=action_config.get("style", {})
                ))
                
        # Create notification
        notification = Notification(
            notification_id=notification_id,
            title=title,
            message=message,
            source=source,
            category=category,
            priority=priority,
            timestamp=time.time(),
            status=NotificationStatus.UNREAD,
            actions=notification_actions,
            icon=icon,
            image=image,
            expiration=expiration,
            metadata=metadata or {},
            style=style or {}
        )
        
        # Add to notifications
        self.notifications[notification_id] = notification
        
        # Dispatch event
        self._dispatch_event(NotificationEventType.NOTIFICATION_ADDED, {
            "notification_id": notification_id,
            "notification": notification.to_dict()
        })
        
        self.logger.debug(f"Added notification: {notification_id} ({title})")
        return notification_id
    
    def remove_notification(self, notification_id: str) -> bool:
        """
        Remove a notification from the notification center.
        
        Args:
            notification_id: ID of the notification to remove
            
        Returns:
            True if the notification was removed, False if not found
        """
        if notification_id not in self.notifications:
            self.logger.warning(f"Notification {notification_id} not found.")
            return False
            
        notification = self.notifications[notification_id]
        
        # Remove from notifications
        del self.notifications[notification_id]
        
        # Dispatch event
        self._dispatch_event(NotificationEventType.NOTIFICATION_REMOVED, {
            "notification_id": notification_id,
            "notification": notification.to_dict()
        })
        
        self.logger.debug(f"Removed notification: {notification_id} ({notification.title})")
        return True
    
    def update_notification(self,
                          notification_id: str,
                          title: Optional[str] = None,
                          message: Optional[str] = None,
                          category: Optional[Union[NotificationCategory, str]] = None,
                          priority: Optional[Union[NotificationPriority, str]] = None,
                          actions: Optional[List[Dict[str, Any]]] = None,
                          icon: Optional[str] = None,
                          image: Optional[str] = None,
                          expiration: Optional[float] = None,
                          metadata: Optional[Dict[str, Any]] = None,
                          style: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a notification in the notification center.
        
        Args:
            notification_id: ID of the notification to update
            title: Optional new title
            message: Optional new message
            category: Optional new category
            priority: Optional new priority
            actions: Optional new actions
            icon: Optional new icon
            image: Optional new image
            expiration: Optional new expiration timestamp
            metadata: Optional new metadata
            style: Optional new style
            
        Returns:
            True if the notification was updated, False if not found
        """
        if notification_id not in self.notifications:
            self.logger.warning(f"Notification {notification_id} not found.")
            return False
            
        notification = self.notifications[notification_id]
        
        # Update properties
        if title is not None:
            notification.title = title
            
        if message is not None:
            notification.message = message
            
        if category is not None:
            # Convert category to NotificationCategory if needed
            if not isinstance(category, NotificationCategory):
                try:
                    category = NotificationCategory(category)
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid category: {category}, using CUSTOM.")
                    category = NotificationCategory.CUSTOM
                    
            notification.category = category
            
        if priority is not None:
            # Convert priority to NotificationPriority if needed
            if not isinstance(priority, NotificationPriority):
                try:
                    priority = NotificationPriority(priority)
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid priority: {priority}, using MEDIUM.")
                    priority = NotificationPriority.MEDIUM
                    
            notification.priority = priority
            
        if actions is not None:
            # Create actions
            notification_actions = []
            for action_config in actions:
                if not self._validate_action_config(action_config):
                    continue
                    
                # Create a dummy handler if not provided
                handler = action_config.get("handler", lambda data: None)
                
                notification_actions.append(NotificationAction(
                    action_id=action_config.get("id", str(uuid.uuid4())),
                    label=action_config["label"],
                    icon=action_config["icon"],
                    handler=handler,
                    enabled=action_config.get("enabled", True),
                    primary=action_config.get("primary", False),
                    style=action_config.get("style", {})
                ))
                
            notification.actions = notification_actions
            
        if icon is not None:
            notification.icon = icon
            
        if image is not None:
            notification.image = image
            
        if expiration is not None:
            notification.expiration = expiration
            
        if metadata is not None:
            notification.metadata.update(metadata)
            
        if style is not None:
            notification.style.update(style)
            
        # Dispatch event
        self._dispatch_event(NotificationEventType.NOTIFICATION_UPDATED, {
            "notification_id": notification_id,
            "notification": notification.to_dict()
        })
        
        self.logger.debug(f"Updated notification: {notification_id} ({notification.title})")
        return True
    
    def get_notification(self, notification_id: str) -> Optional[Notification]:
        """
        Get a notification from the notification center.
        
        Args:
            notification_id: ID of the notification to get
            
        Returns:
            The notification, or None if not found
        """
        return self.notifications.get(notification_id)
    
    def get_notifications(self, filter_func: Optional[Callable[[Notification], bool]] = None) -> List[Notification]:
        """
        Get notifications from the notification center, optionally filtered.
        
        Args:
            filter_func: Optional filter function
            
        Returns:
            List of notifications
        """
        if filter_func is None:
            return list(self.notifications.values())
            
        return [notification for notification in self.notifications.values() if filter_func(notification)]
    
    def get_notifications_by_category(self, category: Union[NotificationCategory, str]) -> List[Notification]:
        """
        Get notifications of a specific category.
        
        Args:
            category: Category of notifications to get
            
        Returns:
            List of notifications of the specified category
        """
        # Convert category to NotificationCategory if needed
        if not isinstance(category, NotificationCategory):
            try:
                category = NotificationCategory(category)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid category: {category}, using CUSTOM.")
                category = NotificationCategory.CUSTOM
                
        return [notification for notification in self.notifications.values() if notification.category == category]
    
    def get_notifications_by_priority(self, priority: Union[NotificationPriority, str]) -> List[Notification]:
        """
        Get notifications of a specific priority.
        
        Args:
            priority: Priority of notifications to get
            
        Returns:
            List of notifications of the specified priority
        """
        # Convert priority to NotificationPriority if needed
        if not isinstance(priority, NotificationPriority):
            try:
                priority = NotificationPriority(priority)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid priority: {priority}, using MEDIUM.")
                priority = NotificationPriority.MEDIUM
                
        return [notification for notification in self.notifications.values() if notification.priority == priority]
    
    def get_notifications_by_status(self, status: Union[NotificationStatus, str]) -> List[Notification]:
        """
        Get notifications of a specific status.
        
        Args:
            status: Status of notifications to get
            
        Returns:
            List of notifications of the specified status
        """
        # Convert status to NotificationStatus if needed
        if not isinstance(status, NotificationStatus):
            try:
                status = NotificationStatus(status)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid status: {status}, using UNREAD.")
                status = NotificationStatus.UNREAD
                
        return [notification for notification in self.notifications.values() if notification.status == status]
    
    def get_unread_count(self) -> int:
        """
        Get the number of unread notifications.
        
        Returns:
            Number of unread notifications
        """
        return len(self.get_notifications_by_status(NotificationStatus.UNREAD))
    
    def set_notification_status(self, notification_id: str, status: Union[NotificationStatus, str]) -> bool:
        """
        Set the status of a notification.
        
        Args:
            notification_id: ID of the notification to update
            status: New status
            
        Returns:
            True if the status was set, False if notification not found or invalid status
        """
        if notification_id not in self.notifications:
            self.logger.warning(f"Notification {notification_id} not found.")
            return False
            
        # Convert status to NotificationStatus if needed
        if not isinstance(status, NotificationStatus):
            try:
                status = NotificationStatus(status)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid status: {status}.")
                return False
                
        notification = self.notifications[notification_id]
        old_status = notification.status
        notification.status = status
        
        # Dispatch event
        self._dispatch_event(NotificationEventType.NOTIFICATION_STATUS_CHANGED, {
            "notification_id": notification_id,
            "old_status": old_status.value,
            "new_status": status.value
        })
        
        self.logger.debug(f"Set notification {notification_id} status to {status.value}")
        return True
    
    def mark_as_read(self, notification_id: str) -> bool:
        """
        Mark a notification as read.
        
        Args:
            notification_id: ID of the notification to mark as read
            
        Returns:
            True if the status was set, False if notification not found
        """
        return self.set_notification_status(notification_id, NotificationStatus.READ)
    
    def mark_as_unread(self, notification_id: str) -> bool:
        """
        Mark a notification as unread.
        
        Args:
            notification_id: ID of the notification to mark as unread
            
        Returns:
            True if the status was set, False if notification not found
        """
        return self.set_notification_status(notification_id, NotificationStatus.UNREAD)
    
    def acknowledge_notification(self, notification_id: str) -> bool:
        """
        Acknowledge a notification.
        
        Args:
            notification_id: ID of the notification to acknowledge
            
        Returns:
            True if the status was set, False if notification not found
        """
        return self.set_notification_status(notification_id, NotificationStatus.ACKNOWLEDGED)
    
    def dismiss_notification(self, notification_id: str) -> bool:
        """
        Dismiss a notification.
        
        Args:
            notification_id: ID of the notification to dismiss
            
        Returns:
            True if the status was set, False if notification not found
        """
        return self.set_notification_status(notification_id, NotificationStatus.DISMISSED)
    
    def mark_all_as_read(self) -> int:
        """
        Mark all unread notifications as read.
        
        Returns:
            Number of notifications marked as read
        """
        unread = self.get_notifications_by_status(NotificationStatus.UNREAD)
        count = 0
        
        for notification in unread:
            if self.mark_as_read(notification.notification_id):
                count += 1
                
        return count
    
    def dismiss_all(self) -> int:
        """
        Dismiss all notifications.
        
        Returns:
            Number of notifications dismissed
        """
        count = 0
        
        for notification in self.notifications.values():
            if self.dismiss_notification(notification.notification_id):
                count += 1
                
        return count
    
    def execute_action(self, notification_id: str, action_id: str, data: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute an action on a notification.
        
        Args:
            notification_id: ID of the notification
            action_id: ID of the action to execute
            data: Optional data to pass to the action handler
            
        Returns:
            Result of the action handler
        
        Raises:
            ValueError: If the notification or action is not found, or the action is disabled
        """
        if notification_id not in self.notifications:
            raise ValueError(f"Notification {notification_id} not found.")
            
        notification = self.notifications[notification_id]
        
        # Find the action
        action = None
        for a in notification.actions:
            if a.action_id == action_id:
                action = a
                break
                
        if action is None:
            raise ValueError(f"Action {action_id} not found in notification {notification_id}.")
            
        if not action.enabled:
            raise ValueError(f"Action {action_id} is disabled.")
            
        # Prepare data
        execution_data = {
            "notification_id": notification_id,
            "action_id": action_id,
            "timestamp": time.time()
        }
        
        if data:
            execution_data.update(data)
            
        # Execute handler
        try:
            result = action.handler(execution_data)
            
            # Dispatch event
            self._dispatch_event(NotificationEventType.NOTIFICATION_ACTIONED, {
                "notification_id": notification_id,
                "action_id": action_id,
                "data": execution_data,
                "result": result
            })
            
            self.logger.debug(f"Executed action {action_id} on notification {notification_id}")
            return result
        except Exception as e:
            self.logger.error(f"Error executing action {action_id} on notification {notification_id}: {e}")
            raise
    
    def set_filters(self, filters: Dict[str, Any]) -> None:
        """
        Set the notification filters.
        
        Args:
            filters: Filter configuration
        """
        old_filters = self.filters.copy()
        self.filters = filters
        
        # Dispatch event
        self._dispatch_event(NotificationEventType.FILTER_CHANGED, {
            "old_filters": old_filters,
            "new_filters": filters
        })
        
        self.logger.debug("Updated filters")
    
    def get_filters(self) -> Dict[str, Any]:
        """
        Get the notification filters.
        
        Returns:
            The notification filters
        """
        return self.filters
    
    def set_sort(self, sort_by: str, sort_order: str = "desc") -> None:
        """
        Set the notification sorting.
        
        Args:
            sort_by: Field to sort by
            sort_order: Sort order ("asc" or "desc")
        """
        old_sort_by = self.sort_by
        old_sort_order = self.sort_order
        
        self.sort_by = sort_by
        self.sort_order = sort_order
        
        # Dispatch event
        self._dispatch_event(NotificationEventType.SORT_CHANGED, {
            "old_sort_by": old_sort_by,
            "old_sort_order": old_sort_order,
            "new_sort_by": sort_by,
            "new_sort_order": sort_order
        })
        
        self.logger.debug(f"Set sort: {sort_by} {sort_order}")
    
    def get_sort(self) -> Dict[str, str]:
        """
        Get the notification sorting.
        
        Returns:
            The notification sorting
        """
        return {
            "sort_by": self.sort_by,
            "sort_order": self.sort_order
        }
    
    def set_group_by(self, group_by: Optional[str]) -> None:
        """
        Set the notification grouping.
        
        Args:
            group_by: Field to group by, or None for no grouping
        """
        old_group_by = self.group_by
        self.group_by = group_by
        
        # Dispatch event
        self._dispatch_event(NotificationEventType.GROUP_CHANGED, {
            "old_group_by": old_group_by,
            "new_group_by": group_by
        })
        
        self.logger.debug(f"Set group by: {group_by}")
    
    def get_group_by(self) -> Optional[str]:
        """
        Get the notification grouping.
        
        Returns:
            The notification grouping
        """
        return self.group_by
    
    def show(self) -> bool:
        """
        Show the notification center.
        
        Returns:
            True if the visibility was changed, False if already visible
        """
        if self.is_visible:
            return False
            
        self.is_visible = True
        
        # Dispatch event
        self._dispatch_event(NotificationEventType.VISIBILITY_CHANGED, {
            "visible": True
        })
        
        self.logger.debug("Notification center shown")
        return True
    
    def hide(self) -> bool:
        """
        Hide the notification center.
        
        Returns:
            True if the visibility was changed, False if already hidden
        """
        if not self.is_visible:
            return False
            
        self.is_visible = False
        
        # Dispatch event
        self._dispatch_event(NotificationEventType.VISIBILITY_CHANGED, {
            "visible": False
        })
        
        self.logger.debug("Notification center hidden")
        return True
    
    def set_style(self, style: Dict[str, Any]) -> None:
        """
        Set the notification center style.
        
        Args:
            style: Style configuration
        """
        # Update style properties
        for key, value in style.items():
            if hasattr(self.style, key):
                setattr(self.style, key, value)
            else:
                self.style.custom_css[key] = value
                
        self.logger.debug("Updated notification center style")
    
    def get_style(self) -> NotificationStyle:
        """
        Get the notification center style.
        
        Returns:
            The notification center style
        """
        return self.style
    
    def add_event_listener(self, event_type: Union[NotificationEventType, str], listener: Callable[[NotificationEvent], None]) -> bool:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
            
        Returns:
            True if the listener was added, False if invalid event type
        """
        # Convert event_type to NotificationEventType if needed
        if not isinstance(event_type, NotificationEventType):
            try:
                event_type = NotificationEventType(event_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid event type: {event_type}.")
                return False
                
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        return True
    
    def remove_event_listener(self, event_type: Union[NotificationEventType, str], listener: Callable[[NotificationEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        # Convert event_type to NotificationEventType if needed
        if not isinstance(event_type, NotificationEventType):
            try:
                event_type = NotificationEventType(event_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid event type: {event_type}.")
                return False
                
        if event_type not in self.event_listeners:
            return False
            
        if listener in self.event_listeners[event_type]:
            self.event_listeners[event_type].remove(listener)
            return True
            
        return False
    
    def add_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.global_listeners.append(listener)
        
    def remove_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Remove a global listener.
        
        Args:
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if listener in self.global_listeners:
            self.global_listeners.remove(listener)
            return True
            
        return False
    
    def render(self) -> Dict[str, Any]:
        """
        Render the notification center for display.
        
        Returns:
            Rendered notification center data
        """
        # Get notifications
        notifications = list(self.notifications.values())
        
        # Apply filters
        if self.filters:
            filtered_notifications = []
            for notification in notifications:
                include = True
                
                for key, value in self.filters.items():
                    if key == "category":
                        if isinstance(value, list):
                            if notification.category.value not in value:
                                include = False
                                break
                        elif notification.category.value != value:
                            include = False
                            break
                    elif key == "priority":
                        if isinstance(value, list):
                            if notification.priority.value not in value:
                                include = False
                                break
                        elif notification.priority.value != value:
                            include = False
                            break
                    elif key == "status":
                        if isinstance(value, list):
                            if notification.status.value not in value:
                                include = False
                                break
                        elif notification.status.value != value:
                            include = False
                            break
                    elif key == "source":
                        if isinstance(value, list):
                            if notification.source not in value:
                                include = False
                                break
                        elif notification.source != value:
                            include = False
                            break
                    elif key == "search":
                        search_term = value.lower()
                        if (search_term not in notification.title.lower() and
                            search_term not in notification.message.lower()):
                            include = False
                            break
                    elif key == "from_timestamp":
                        if notification.timestamp < value:
                            include = False
                            break
                    elif key == "to_timestamp":
                        if notification.timestamp > value:
                            include = False
                            break
                    elif key in notification.metadata:
                        if notification.metadata[key] != value:
                            include = False
                            break
                            
                if include:
                    filtered_notifications.append(notification)
                    
            notifications = filtered_notifications
            
        # Sort notifications
        if self.sort_by == "timestamp":
            notifications.sort(key=lambda n: n.timestamp, reverse=(self.sort_order == "desc"))
        elif self.sort_by == "priority":
            priority_order = {
                NotificationPriority.LOW: 0,
                NotificationPriority.MEDIUM: 1,
                NotificationPriority.HIGH: 2,
                NotificationPriority.CRITICAL: 3
            }
            notifications.sort(key=lambda n: priority_order[n.priority], reverse=(self.sort_order == "desc"))
        elif self.sort_by == "category":
            notifications.sort(key=lambda n: n.category.value, reverse=(self.sort_order == "desc"))
        elif self.sort_by == "status":
            status_order = {
                NotificationStatus.UNREAD: 0,
                NotificationStatus.READ: 1,
                NotificationStatus.ACKNOWLEDGED: 2,
                NotificationStatus.ACTIONED: 3,
                NotificationStatus.DISMISSED: 4,
                NotificationStatus.EXPIRED: 5
            }
            notifications.sort(key=lambda n: status_order[n.status], reverse=(self.sort_order == "desc"))
        elif self.sort_by == "source":
            notifications.sort(key=lambda n: n.source, reverse=(self.sort_order == "desc"))
        elif self.sort_by == "title":
            notifications.sort(key=lambda n: n.title, reverse=(self.sort_order == "desc"))
            
        # Group notifications
        if self.group_by:
            grouped_notifications = {}
            
            if self.group_by == "category":
                for notification in notifications:
                    category = notification.category.value
                    if category not in grouped_notifications:
                        grouped_notifications[category] = []
                        
                    grouped_notifications[category].append(notification.to_dict())
                    
            elif self.group_by == "priority":
                for notification in notifications:
                    priority = notification.priority.value
                    if priority not in grouped_notifications:
                        grouped_notifications[priority] = []
                        
                    grouped_notifications[priority].append(notification.to_dict())
                    
            elif self.group_by == "status":
                for notification in notifications:
                    status = notification.status.value
                    if status not in grouped_notifications:
                        grouped_notifications[status] = []
                        
                    grouped_notifications[status].append(notification.to_dict())
                    
            elif self.group_by == "source":
                for notification in notifications:
                    source = notification.source
                    if source not in grouped_notifications:
                        grouped_notifications[source] = []
                        
                    grouped_notifications[source].append(notification.to_dict())
                    
            elif self.group_by == "date":
                for notification in notifications:
                    date = datetime.fromtimestamp(notification.timestamp).strftime("%Y-%m-%d")
                    if date not in grouped_notifications:
                        grouped_notifications[date] = []
                        
                    grouped_notifications[date].append(notification.to_dict())
                    
            # Convert to list of groups
            groups = []
            for group_key, group_notifications in grouped_notifications.items():
                groups.append({
                    "key": group_key,
                    "notifications": group_notifications
                })
                
            # Sort groups
            groups.sort(key=lambda g: g["key"], reverse=(self.sort_order == "desc"))
            
            notification_data = groups
        else:
            # No grouping
            notification_data = [notification.to_dict() for notification in notifications]
            
        # Build the notification center data
        center_data = {
            "visible": self.is_visible,
            "style": {
                "background_color": self.style.background_color,
                "text_color": self.style.text_color,
                "accent_color": self.style.accent_color,
                "border_color": self.style.border_color,
                "border_radius": self.style.border_radius,
                "shadow": self.style.shadow,
                "font_family": self.style.font_family,
                "title_font_size": self.style.title_font_size,
                "body_font_size": self.style.body_font_size,
                "padding": self.style.padding,
                "margin": self.style.margin,
                "animation_duration": self.style.animation_duration,
                "custom_css": self.style.custom_css
            },
            "filters": self.filters,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
            "group_by": self.group_by,
            "unread_count": self.get_unread_count(),
            "total_count": len(self.notifications),
            "filtered_count": len(notifications),
            "notifications": notification_data,
            "grouped": self.group_by is not None
        }
        
        return center_data
    
    def _dispatch_event(self, event_type: NotificationEventType, data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Create event
        event = NotificationEvent(
            event_type=event_type,
            source="NotificationCenterComponent",
            data=data
        )
        
        # Dispatch to event type listeners
        if event_type in self.event_listeners:
            for listener in self.event_listeners[event_type]:
                try:
                    listener(event)
                except Exception as e:
                    self.logger.error(f"Error in event listener for {event_type.value}: {e}")
                    
        # Dispatch to global listeners
        for listener in self.global_listeners:
            try:
                listener(self._event_to_dict(event))
            except Exception as e:
                self.logger.error(f"Error in global listener: {e}")
    
    def _event_to_dict(self, event: NotificationEvent) -> Dict[str, Any]:
        """
        Convert event to dictionary.
        
        Args:
            event: The event to convert
            
        Returns:
            Dictionary representation of the event
        """
        return {
            "event_type": event.event_type.value,
            "source": event.source,
            "data": event.data,
            "timestamp": event.timestamp
        }
    
    def _validate_notification_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate a notification configuration.
        
        Args:
            config: Notification configuration
            
        Returns:
            True if valid, False if invalid
        """
        required_fields = ["id", "title", "message", "source", "category", "priority"]
        
        for field in required_fields:
            if field not in config:
                self.logger.warning(f"Missing required field '{field}' in notification configuration.")
                return False
                
        return True
    
    def _validate_action_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate an action configuration.
        
        Args:
            config: Action configuration
            
        Returns:
            True if valid, False if invalid
        """
        required_fields = ["label", "icon"]
        
        for field in required_fields:
            if field not in config:
                self.logger.warning(f"Missing required field '{field}' in action configuration.")
                return False
                
        return True

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create notification center component
    center = NotificationCenterComponent()
    
    # Add notifications
    center.add_notification(
        title="System Update Available",
        message="A new system update is available. Please update at your earliest convenience.",
        source="System",
        category=NotificationCategory.SYSTEM,
        priority=NotificationPriority.MEDIUM,
        icon="update",
        actions=[
            {
                "label": "Update Now",
                "icon": "update",
                "primary": True
            },
            {
                "label": "Remind Later",
                "icon": "schedule"
            },
            {
                "label": "Dismiss",
                "icon": "close"
            }
        ]
    )
    
    center.add_notification(
        title="Production Line Alert",
        message="Production Line 3 has stopped due to a material shortage.",
        source="Production",
        category=NotificationCategory.ALERT,
        priority=NotificationPriority.HIGH,
        icon="warning",
        actions=[
            {
                "label": "View Details",
                "icon": "visibility",
                "primary": True
            },
            {
                "label": "Acknowledge",
                "icon": "check"
            }
        ]
    )
    
    center.add_notification(
        title="Maintenance Completed",
        message="Scheduled maintenance on Assembly Line 2 has been completed.",
        source="Maintenance",
        category=NotificationCategory.INFO,
        priority=NotificationPriority.LOW,
        icon="build"
    )
    
    # Set filters
    center.set_filters({
        "priority": ["high", "critical"]
    })
    
    # Set sort
    center.set_sort("timestamp", "desc")
    
    # Set group by
    center.set_group_by("category")
    
    # Render the notification center
    rendered = center.render()
    print(f"Notification center has {rendered['filtered_count']} filtered notifications out of {rendered['total_count']} total")
    print(f"Unread count: {rendered['unread_count']}")
"""
