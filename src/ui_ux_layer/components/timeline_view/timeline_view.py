"""
Timeline View Component for the Industriverse UI/UX Layer.

This module provides a comprehensive timeline visualization system for industrial environments,
capable of displaying temporal data, events, processes, and workflows with interactive capabilities.

Author: Manus
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timedelta

class TimelineViewMode(Enum):
    """Enumeration of timeline view modes."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    CALENDAR = "calendar"
    GANTT = "gantt"
    SPIRAL = "spiral"
    RADIAL = "radial"
    CUSTOM = "custom"

class TimelineZoomLevel(Enum):
    """Enumeration of timeline zoom levels."""
    YEARS = "years"
    MONTHS = "months"
    WEEKS = "weeks"
    DAYS = "days"
    HOURS = "hours"
    MINUTES = "minutes"
    SECONDS = "seconds"
    MILLISECONDS = "milliseconds"
    CUSTOM = "custom"

class TimelineItemType(Enum):
    """Enumeration of timeline item types."""
    EVENT = "event"
    PROCESS = "process"
    MILESTONE = "milestone"
    TASK = "task"
    ALERT = "alert"
    MEASUREMENT = "measurement"
    ANNOTATION = "annotation"
    CUSTOM = "custom"

class TimelineGroupBy(Enum):
    """Enumeration of timeline grouping options."""
    NONE = "none"
    CATEGORY = "category"
    PRIORITY = "priority"
    STATUS = "status"
    RESOURCE = "resource"
    LOCATION = "location"
    CUSTOM = "custom"

class TimelineFilterType(Enum):
    """Enumeration of timeline filter types."""
    TIME_RANGE = "time_range"
    ITEM_TYPE = "item_type"
    CATEGORY = "category"
    PRIORITY = "priority"
    STATUS = "status"
    RESOURCE = "resource"
    LOCATION = "location"
    SEARCH = "search"
    CUSTOM = "custom"

class TimelineEventType(Enum):
    """Enumeration of timeline event types."""
    ITEM_CLICKED = "item_clicked"
    ITEM_DOUBLE_CLICKED = "item_double_clicked"
    ITEM_CONTEXT_MENU = "item_context_menu"
    ITEM_DRAGGED = "item_dragged"
    ITEM_RESIZED = "item_resized"
    ITEM_CREATED = "item_created"
    ITEM_UPDATED = "item_updated"
    ITEM_DELETED = "item_deleted"
    RANGE_CHANGED = "range_changed"
    ZOOM_CHANGED = "zoom_changed"
    VIEW_MODE_CHANGED = "view_mode_changed"
    GROUP_BY_CHANGED = "group_by_changed"
    FILTER_CHANGED = "filter_changed"
    SELECTION_CHANGED = "selection_changed"
    CUSTOM = "custom"

@dataclass
class TimelineRange:
    """Data class representing a timeline range."""
    start: datetime
    end: datetime
    
    def duration(self) -> timedelta:
        """Get the duration of the range."""
        return self.end - self.start
    
    def contains(self, time: datetime) -> bool:
        """Check if the range contains a specific time."""
        return self.start <= time <= self.end
    
    def overlaps(self, other: 'TimelineRange') -> bool:
        """Check if the range overlaps with another range."""
        return self.start <= other.end and other.start <= self.end
    
    def intersection(self, other: 'TimelineRange') -> Optional['TimelineRange']:
        """Get the intersection of this range with another range."""
        if not self.overlaps(other):
            return None
        
        start = max(self.start, other.start)
        end = min(self.end, other.end)
        
        return TimelineRange(start=start, end=end)
    
    def union(self, other: 'TimelineRange') -> 'TimelineRange':
        """Get the union of this range with another range."""
        start = min(self.start, other.start)
        end = max(self.end, other.end)
        
        return TimelineRange(start=start, end=end)
    
    def expand(self, delta: timedelta) -> 'TimelineRange':
        """Expand the range by a delta on both sides."""
        return TimelineRange(
            start=self.start - delta,
            end=self.end + delta
        )
    
    def shift(self, delta: timedelta) -> 'TimelineRange':
        """Shift the range by a delta."""
        return TimelineRange(
            start=self.start + delta,
            end=self.end + delta
        )

@dataclass
class TimelineStyle:
    """Data class representing timeline styling options."""
    background_color: str = "#FFFFFF"
    text_color: str = "#333333"
    grid_color: str = "#EEEEEE"
    axis_color: str = "#CCCCCC"
    highlight_color: str = "#4285F4"
    selection_color: str = "#A8C7FA"
    font_family: str = "Arial, sans-serif"
    font_size: str = "12px"
    line_width: int = 1
    item_height: int = 30
    item_spacing: int = 5
    custom_css: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TimelineItemStyle:
    """Data class representing timeline item styling options."""
    background_color: str = "#4285F4"
    text_color: str = "#FFFFFF"
    border_color: str = "#2A56C6"
    border_width: int = 1
    border_radius: int = 3
    opacity: float = 1.0
    icon: Optional[str] = None
    font_weight: str = "normal"
    custom_css: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TimelineItem:
    """Data class representing a timeline item."""
    item_id: str
    title: str
    start_time: datetime
    end_time: Optional[datetime] = None
    type: TimelineItemType = TimelineItemType.EVENT
    content: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    resource: Optional[str] = None
    location: Optional[str] = None
    style: TimelineItemStyle = field(default_factory=TimelineItemStyle)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def duration(self) -> Optional[timedelta]:
        """Get the duration of the item."""
        if self.end_time is None:
            return None
        
        return self.end_time - self.start_time
    
    def is_point_in_time(self) -> bool:
        """Check if the item is a point in time (no duration)."""
        return self.end_time is None
    
    def overlaps(self, other: 'TimelineItem') -> bool:
        """Check if the item overlaps with another item."""
        if self.is_point_in_time() or other.is_point_in_time():
            return False
        
        return self.start_time <= other.end_time and other.start_time <= self.end_time
    
    def contains(self, time: datetime) -> bool:
        """Check if the item contains a specific time."""
        if self.is_point_in_time():
            return self.start_time == time
        
        return self.start_time <= time <= self.end_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the item to a dictionary."""
        result = {
            "id": self.item_id,
            "title": self.title,
            "start": self.start_time.isoformat(),
            "type": self.type.value,
        }
        
        if self.end_time is not None:
            result["end"] = self.end_time.isoformat()
            
        if self.content is not None:
            result["content"] = self.content
            
        if self.category is not None:
            result["category"] = self.category
            
        if self.priority is not None:
            result["priority"] = self.priority
            
        if self.status is not None:
            result["status"] = self.status
            
        if self.resource is not None:
            result["resource"] = self.resource
            
        if self.location is not None:
            result["location"] = self.location
            
        result["style"] = {
            "backgroundColor": self.style.background_color,
            "color": self.style.text_color,
            "borderColor": self.style.border_color,
            "borderWidth": self.style.border_width,
            "borderRadius": self.style.border_radius,
            "opacity": self.style.opacity,
        }
        
        if self.style.icon is not None:
            result["style"]["icon"] = self.style.icon
            
        if self.style.custom_css:
            result["style"]["custom"] = self.style.custom_css
            
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result

@dataclass
class TimelineGroup:
    """Data class representing a timeline group."""
    group_id: str
    title: str
    items: List[str] = field(default_factory=list)
    subgroups: List[str] = field(default_factory=list)
    expanded: bool = True
    visible: bool = True
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TimelineFilter:
    """Data class representing a timeline filter."""
    filter_id: str
    type: TimelineFilterType
    title: str
    enabled: bool = True
    params: Dict[str, Any] = field(default_factory=dict)
    
    def apply(self, item: TimelineItem) -> bool:
        """Apply the filter to an item."""
        if not self.enabled:
            return True
            
        if self.type == TimelineFilterType.TIME_RANGE:
            start = self.params.get("start")
            end = self.params.get("end")
            
            if start is None or end is None:
                return True
                
            if isinstance(start, str):
                start = datetime.fromisoformat(start)
                
            if isinstance(end, str):
                end = datetime.fromisoformat(end)
                
            range = TimelineRange(start=start, end=end)
            
            if item.is_point_in_time():
                return range.contains(item.start_time)
            else:
                item_range = TimelineRange(start=item.start_time, end=item.end_time)
                return range.overlaps(item_range)
                
        elif self.type == TimelineFilterType.ITEM_TYPE:
            types = self.params.get("types", [])
            
            if not types:
                return True
                
            return item.type.value in types
            
        elif self.type == TimelineFilterType.CATEGORY:
            categories = self.params.get("categories", [])
            
            if not categories:
                return True
                
            return item.category in categories
            
        elif self.type == TimelineFilterType.PRIORITY:
            priorities = self.params.get("priorities", [])
            
            if not priorities:
                return True
                
            return item.priority in priorities
            
        elif self.type == TimelineFilterType.STATUS:
            statuses = self.params.get("statuses", [])
            
            if not statuses:
                return True
                
            return item.status in statuses
            
        elif self.type == TimelineFilterType.RESOURCE:
            resources = self.params.get("resources", [])
            
            if not resources:
                return True
                
            return item.resource in resources
            
        elif self.type == TimelineFilterType.LOCATION:
            locations = self.params.get("locations", [])
            
            if not locations:
                return True
                
            return item.location in locations
            
        elif self.type == TimelineFilterType.SEARCH:
            query = self.params.get("query", "").lower()
            
            if not query:
                return True
                
            # Search in title, content, and metadata
            if query in item.title.lower():
                return True
                
            if item.content and query in item.content.lower():
                return True
                
            # Search in metadata
            for key, value in item.metadata.items():
                if isinstance(value, str) and query in value.lower():
                    return True
                    
            return False
            
        elif self.type == TimelineFilterType.CUSTOM:
            # Custom filter logic would be implemented here
            return True
            
        return True

@dataclass
class TimelineEvent:
    """Data class representing a timeline event."""
    event_type: TimelineEventType
    source: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class TimelineViewComponent:
    """
    Provides a comprehensive timeline visualization system for the Industriverse UI/UX Layer.
    
    This class provides:
    - Multiple timeline visualization modes (horizontal, vertical, calendar, Gantt, etc.)
    - Interactive timeline manipulation (zoom, pan, select)
    - Timeline item management (add, update, delete)
    - Timeline grouping and filtering
    - Event handling for timeline interactions
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Timeline View Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.items: Dict[str, TimelineItem] = {}
        self.groups: Dict[str, TimelineGroup] = {}
        self.filters: Dict[str, TimelineFilter] = {}
        self.selected_items: Set[str] = set()
        self.view_mode = TimelineViewMode.HORIZONTAL
        self.zoom_level = TimelineZoomLevel.DAYS
        self.group_by = TimelineGroupBy.NONE
        self.visible_range: Optional[TimelineRange] = None
        self.style = TimelineStyle()
        self.event_listeners: Dict[TimelineEventType, List[Callable[[TimelineEvent], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
    def start(self) -> bool:
        """
        Start the Timeline View Component.
        
        Returns:
            True if the component was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Initialize default visible range if not set
        if self.visible_range is None:
            now = datetime.now()
            self.visible_range = TimelineRange(
                start=now - timedelta(days=7),
                end=now + timedelta(days=7)
            )
            
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "component_started"
        })
        
        self.logger.info("Timeline View Component started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Timeline View Component.
        
        Returns:
            True if the component was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "component_stopped"
        })
        
        self.logger.info("Timeline View Component stopped.")
        return True
    
    def add_item(self,
               title: str,
               start_time: Union[datetime, str],
               end_time: Optional[Union[datetime, str]] = None,
               type: Union[TimelineItemType, str] = TimelineItemType.EVENT,
               content: Optional[str] = None,
               category: Optional[str] = None,
               priority: Optional[str] = None,
               status: Optional[str] = None,
               resource: Optional[str] = None,
               location: Optional[str] = None,
               style: Optional[Dict[str, Any]] = None,
               metadata: Optional[Dict[str, Any]] = None,
               item_id: Optional[str] = None) -> str:
        """
        Add an item to the timeline.
        
        Args:
            title: Title of the item
            start_time: Start time of the item
            end_time: Optional end time of the item
            type: Type of the item
            content: Optional content/description of the item
            category: Optional category of the item
            priority: Optional priority of the item
            status: Optional status of the item
            resource: Optional resource associated with the item
            location: Optional location of the item
            style: Optional style configuration
            metadata: Optional metadata
            item_id: Optional item ID, generated if not provided
            
        Returns:
            The item ID
        """
        # Generate item ID if not provided
        if item_id is None:
            item_id = str(uuid.uuid4())
            
        # Convert start_time to datetime if needed
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
            
        # Convert end_time to datetime if needed
        if end_time is not None and isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
            
        # Convert type to TimelineItemType if needed
        if not isinstance(type, TimelineItemType):
            try:
                type = TimelineItemType(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid item type: {type}, using EVENT.")
                type = TimelineItemType.EVENT
                
        # Create item style
        item_style = TimelineItemStyle()
        if style:
            # Update style properties
            for key, value in style.items():
                if hasattr(item_style, key):
                    setattr(item_style, key, value)
                else:
                    item_style.custom_css[key] = value
                    
        # Create item
        item = TimelineItem(
            item_id=item_id,
            title=title,
            start_time=start_time,
            end_time=end_time,
            type=type,
            content=content,
            category=category,
            priority=priority,
            status=status,
            resource=resource,
            location=location,
            style=item_style,
            metadata=metadata or {}
        )
        
        # Add to items
        self.items[item_id] = item
        
        # Update groups if needed
        if self.group_by != TimelineGroupBy.NONE:
            self._update_groups()
            
        # Dispatch event
        self._dispatch_event(TimelineEventType.ITEM_CREATED, {
            "item_id": item_id,
            "item": item.to_dict()
        })
        
        self.logger.debug(f"Added item: {item_id} ({title})")
        return item_id
    
    def update_item(self,
                  item_id: str,
                  title: Optional[str] = None,
                  start_time: Optional[Union[datetime, str]] = None,
                  end_time: Optional[Union[datetime, str]] = None,
                  type: Optional[Union[TimelineItemType, str]] = None,
                  content: Optional[str] = None,
                  category: Optional[str] = None,
                  priority: Optional[str] = None,
                  status: Optional[str] = None,
                  resource: Optional[str] = None,
                  location: Optional[str] = None,
                  style: Optional[Dict[str, Any]] = None,
                  metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update an item in the timeline.
        
        Args:
            item_id: ID of the item to update
            title: Optional new title
            start_time: Optional new start time
            end_time: Optional new end time
            type: Optional new type
            content: Optional new content
            category: Optional new category
            priority: Optional new priority
            status: Optional new status
            resource: Optional new resource
            location: Optional new location
            style: Optional new style
            metadata: Optional new metadata
            
        Returns:
            True if the item was updated, False if not found
        """
        if item_id not in self.items:
            self.logger.warning(f"Item {item_id} not found.")
            return False
            
        item = self.items[item_id]
        
        # Update properties
        if title is not None:
            item.title = title
            
        if start_time is not None:
            # Convert start_time to datetime if needed
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
                
            item.start_time = start_time
            
        if end_time is not None:
            # Convert end_time to datetime if needed
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
                
            item.end_time = end_time
            
        if type is not None:
            # Convert type to TimelineItemType if needed
            if not isinstance(type, TimelineItemType):
                try:
                    type = TimelineItemType(type)
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid item type: {type}, ignoring.")
                else:
                    item.type = type
            else:
                item.type = type
                
        if content is not None:
            item.content = content
            
        if category is not None:
            item.category = category
            
        if priority is not None:
            item.priority = priority
            
        if status is not None:
            item.status = status
            
        if resource is not None:
            item.resource = resource
            
        if location is not None:
            item.location = location
            
        if style is not None:
            # Update style properties
            for key, value in style.items():
                if hasattr(item.style, key):
                    setattr(item.style, key, value)
                else:
                    item.style.custom_css[key] = value
                    
        if metadata is not None:
            item.metadata.update(metadata)
            
        # Update groups if needed
        if self.group_by != TimelineGroupBy.NONE:
            self._update_groups()
            
        # Dispatch event
        self._dispatch_event(TimelineEventType.ITEM_UPDATED, {
            "item_id": item_id,
            "item": item.to_dict()
        })
        
        self.logger.debug(f"Updated item: {item_id} ({item.title})")
        return True
    
    def delete_item(self, item_id: str) -> bool:
        """
        Delete an item from the timeline.
        
        Args:
            item_id: ID of the item to delete
            
        Returns:
            True if the item was deleted, False if not found
        """
        if item_id not in self.items:
            self.logger.warning(f"Item {item_id} not found.")
            return False
            
        item = self.items[item_id]
        
        # Remove from items
        del self.items[item_id]
        
        # Remove from selected items
        if item_id in self.selected_items:
            self.selected_items.remove(item_id)
            
        # Update groups if needed
        if self.group_by != TimelineGroupBy.NONE:
            self._update_groups()
            
        # Dispatch event
        self._dispatch_event(TimelineEventType.ITEM_DELETED, {
            "item_id": item_id,
            "item": item.to_dict()
        })
        
        self.logger.debug(f"Deleted item: {item_id} ({item.title})")
        return True
    
    def get_item(self, item_id: str) -> Optional[TimelineItem]:
        """
        Get an item from the timeline.
        
        Args:
            item_id: ID of the item to get
            
        Returns:
            The item, or None if not found
        """
        return self.items.get(item_id)
    
    def get_items(self, filter_func: Optional[Callable[[TimelineItem], bool]] = None) -> List[TimelineItem]:
        """
        Get items from the timeline, optionally filtered.
        
        Args:
            filter_func: Optional filter function
            
        Returns:
            List of items
        """
        if filter_func is None:
            return list(self.items.values())
            
        return [item for item in self.items.values() if filter_func(item)]
    
    def get_items_in_range(self, start: datetime, end: datetime) -> List[TimelineItem]:
        """
        Get items in a specific time range.
        
        Args:
            start: Start time
            end: End time
            
        Returns:
            List of items in the range
        """
        range = TimelineRange(start=start, end=end)
        
        result = []
        for item in self.items.values():
            if item.is_point_in_time():
                if range.contains(item.start_time):
                    result.append(item)
            else:
                item_range = TimelineRange(start=item.start_time, end=item.end_time)
                if range.overlaps(item_range):
                    result.append(item)
                    
        return result
    
    def get_filtered_items(self) -> List[TimelineItem]:
        """
        Get items after applying all active filters.
        
        Returns:
            List of filtered items
        """
        # Get active filters
        active_filters = [f for f in self.filters.values() if f.enabled]
        
        if not active_filters:
            return list(self.items.values())
            
        # Apply filters
        result = []
        for item in self.items.values():
            # Item passes if it passes all active filters
            if all(f.apply(item) for f in active_filters):
                result.append(item)
                
        return result
    
    def set_view_mode(self, mode: Union[TimelineViewMode, str]) -> bool:
        """
        Set the timeline view mode.
        
        Args:
            mode: New view mode
            
        Returns:
            True if the mode was set, False if invalid
        """
        # Convert mode to TimelineViewMode if needed
        if not isinstance(mode, TimelineViewMode):
            try:
                mode = TimelineViewMode(mode)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid view mode: {mode}.")
                return False
                
        old_mode = self.view_mode
        self.view_mode = mode
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.VIEW_MODE_CHANGED, {
            "old_mode": old_mode.value,
            "new_mode": mode.value
        })
        
        self.logger.debug(f"Set view mode: {mode.value}")
        return True
    
    def set_zoom_level(self, level: Union[TimelineZoomLevel, str]) -> bool:
        """
        Set the timeline zoom level.
        
        Args:
            level: New zoom level
            
        Returns:
            True if the level was set, False if invalid
        """
        # Convert level to TimelineZoomLevel if needed
        if not isinstance(level, TimelineZoomLevel):
            try:
                level = TimelineZoomLevel(level)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid zoom level: {level}.")
                return False
                
        old_level = self.zoom_level
        self.zoom_level = level
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.ZOOM_CHANGED, {
            "old_level": old_level.value,
            "new_level": level.value
        })
        
        self.logger.debug(f"Set zoom level: {level.value}")
        return True
    
    def set_visible_range(self, start: Union[datetime, str], end: Union[datetime, str]) -> bool:
        """
        Set the visible time range.
        
        Args:
            start: Start time
            end: End time
            
        Returns:
            True if the range was set
        """
        # Convert start to datetime if needed
        if isinstance(start, str):
            start = datetime.fromisoformat(start)
            
        # Convert end to datetime if needed
        if isinstance(end, str):
            end = datetime.fromisoformat(end)
            
        old_range = self.visible_range
        self.visible_range = TimelineRange(start=start, end=end)
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.RANGE_CHANGED, {
            "old_start": old_range.start.isoformat() if old_range else None,
            "old_end": old_range.end.isoformat() if old_range else None,
            "new_start": start.isoformat(),
            "new_end": end.isoformat()
        })
        
        self.logger.debug(f"Set visible range: {start.isoformat()} - {end.isoformat()}")
        return True
    
    def set_group_by(self, group_by: Union[TimelineGroupBy, str]) -> bool:
        """
        Set the timeline grouping.
        
        Args:
            group_by: New grouping
            
        Returns:
            True if the grouping was set, False if invalid
        """
        # Convert group_by to TimelineGroupBy if needed
        if not isinstance(group_by, TimelineGroupBy):
            try:
                group_by = TimelineGroupBy(group_by)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid group by: {group_by}.")
                return False
                
        old_group_by = self.group_by
        self.group_by = group_by
        
        # Update groups
        self._update_groups()
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.GROUP_BY_CHANGED, {
            "old_group_by": old_group_by.value,
            "new_group_by": group_by.value
        })
        
        self.logger.debug(f"Set group by: {group_by.value}")
        return True
    
    def add_filter(self,
                 type: Union[TimelineFilterType, str],
                 title: str,
                 params: Dict[str, Any],
                 enabled: bool = True,
                 filter_id: Optional[str] = None) -> str:
        """
        Add a filter to the timeline.
        
        Args:
            type: Type of filter
            title: Title of the filter
            params: Filter parameters
            enabled: Whether the filter is enabled
            filter_id: Optional filter ID, generated if not provided
            
        Returns:
            The filter ID
        """
        # Generate filter ID if not provided
        if filter_id is None:
            filter_id = str(uuid.uuid4())
            
        # Convert type to TimelineFilterType if needed
        if not isinstance(type, TimelineFilterType):
            try:
                type = TimelineFilterType(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid filter type: {type}, using CUSTOM.")
                type = TimelineFilterType.CUSTOM
                
        # Create filter
        filter = TimelineFilter(
            filter_id=filter_id,
            type=type,
            title=title,
            enabled=enabled,
            params=params
        )
        
        # Add to filters
        self.filters[filter_id] = filter
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.FILTER_CHANGED, {
            "action": "added",
            "filter_id": filter_id,
            "filter": {
                "id": filter_id,
                "type": type.value,
                "title": title,
                "enabled": enabled,
                "params": params
            }
        })
        
        self.logger.debug(f"Added filter: {filter_id} ({title})")
        return filter_id
    
    def update_filter(self,
                    filter_id: str,
                    title: Optional[str] = None,
                    params: Optional[Dict[str, Any]] = None,
                    enabled: Optional[bool] = None) -> bool:
        """
        Update a filter.
        
        Args:
            filter_id: ID of the filter to update
            title: Optional new title
            params: Optional new parameters
            enabled: Optional new enabled state
            
        Returns:
            True if the filter was updated, False if not found
        """
        if filter_id not in self.filters:
            self.logger.warning(f"Filter {filter_id} not found.")
            return False
            
        filter = self.filters[filter_id]
        
        # Update properties
        if title is not None:
            filter.title = title
            
        if params is not None:
            filter.params.update(params)
            
        if enabled is not None:
            filter.enabled = enabled
            
        # Dispatch event
        self._dispatch_event(TimelineEventType.FILTER_CHANGED, {
            "action": "updated",
            "filter_id": filter_id,
            "filter": {
                "id": filter_id,
                "type": filter.type.value,
                "title": filter.title,
                "enabled": filter.enabled,
                "params": filter.params
            }
        })
        
        self.logger.debug(f"Updated filter: {filter_id} ({filter.title})")
        return True
    
    def delete_filter(self, filter_id: str) -> bool:
        """
        Delete a filter.
        
        Args:
            filter_id: ID of the filter to delete
            
        Returns:
            True if the filter was deleted, False if not found
        """
        if filter_id not in self.filters:
            self.logger.warning(f"Filter {filter_id} not found.")
            return False
            
        filter = self.filters[filter_id]
        
        # Remove from filters
        del self.filters[filter_id]
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.FILTER_CHANGED, {
            "action": "deleted",
            "filter_id": filter_id,
            "filter": {
                "id": filter_id,
                "type": filter.type.value,
                "title": filter.title
            }
        })
        
        self.logger.debug(f"Deleted filter: {filter_id} ({filter.title})")
        return True
    
    def get_filter(self, filter_id: str) -> Optional[TimelineFilter]:
        """
        Get a filter.
        
        Args:
            filter_id: ID of the filter to get
            
        Returns:
            The filter, or None if not found
        """
        return self.filters.get(filter_id)
    
    def enable_filter(self, filter_id: str) -> bool:
        """
        Enable a filter.
        
        Args:
            filter_id: ID of the filter to enable
            
        Returns:
            True if the filter was enabled, False if not found
        """
        if filter_id not in self.filters:
            self.logger.warning(f"Filter {filter_id} not found.")
            return False
            
        filter = self.filters[filter_id]
        
        # Update enabled state
        filter.enabled = True
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.FILTER_CHANGED, {
            "action": "enabled",
            "filter_id": filter_id,
            "filter": {
                "id": filter_id,
                "type": filter.type.value,
                "title": filter.title
            }
        })
        
        self.logger.debug(f"Enabled filter: {filter_id} ({filter.title})")
        return True
    
    def disable_filter(self, filter_id: str) -> bool:
        """
        Disable a filter.
        
        Args:
            filter_id: ID of the filter to disable
            
        Returns:
            True if the filter was disabled, False if not found
        """
        if filter_id not in self.filters:
            self.logger.warning(f"Filter {filter_id} not found.")
            return False
            
        filter = self.filters[filter_id]
        
        # Update enabled state
        filter.enabled = False
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.FILTER_CHANGED, {
            "action": "disabled",
            "filter_id": filter_id,
            "filter": {
                "id": filter_id,
                "type": filter.type.value,
                "title": filter.title
            }
        })
        
        self.logger.debug(f"Disabled filter: {filter_id} ({filter.title})")
        return True
    
    def select_item(self, item_id: str) -> bool:
        """
        Select an item.
        
        Args:
            item_id: ID of the item to select
            
        Returns:
            True if the item was selected, False if not found
        """
        if item_id not in self.items:
            self.logger.warning(f"Item {item_id} not found.")
            return False
            
        # Add to selected items
        self.selected_items.add(item_id)
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.SELECTION_CHANGED, {
            "action": "selected",
            "item_id": item_id,
            "selected_items": list(self.selected_items)
        })
        
        self.logger.debug(f"Selected item: {item_id}")
        return True
    
    def deselect_item(self, item_id: str) -> bool:
        """
        Deselect an item.
        
        Args:
            item_id: ID of the item to deselect
            
        Returns:
            True if the item was deselected, False if not found or not selected
        """
        if item_id not in self.items:
            self.logger.warning(f"Item {item_id} not found.")
            return False
            
        if item_id not in self.selected_items:
            return False
            
        # Remove from selected items
        self.selected_items.remove(item_id)
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.SELECTION_CHANGED, {
            "action": "deselected",
            "item_id": item_id,
            "selected_items": list(self.selected_items)
        })
        
        self.logger.debug(f"Deselected item: {item_id}")
        return True
    
    def select_items(self, item_ids: List[str]) -> List[str]:
        """
        Select multiple items.
        
        Args:
            item_ids: IDs of the items to select
            
        Returns:
            List of successfully selected item IDs
        """
        selected = []
        
        for item_id in item_ids:
            if item_id in self.items:
                self.selected_items.add(item_id)
                selected.append(item_id)
                
        if selected:
            # Dispatch event
            self._dispatch_event(TimelineEventType.SELECTION_CHANGED, {
                "action": "selected_multiple",
                "item_ids": selected,
                "selected_items": list(self.selected_items)
            })
            
            self.logger.debug(f"Selected items: {', '.join(selected)}")
            
        return selected
    
    def deselect_items(self, item_ids: List[str]) -> List[str]:
        """
        Deselect multiple items.
        
        Args:
            item_ids: IDs of the items to deselect
            
        Returns:
            List of successfully deselected item IDs
        """
        deselected = []
        
        for item_id in item_ids:
            if item_id in self.selected_items:
                self.selected_items.remove(item_id)
                deselected.append(item_id)
                
        if deselected:
            # Dispatch event
            self._dispatch_event(TimelineEventType.SELECTION_CHANGED, {
                "action": "deselected_multiple",
                "item_ids": deselected,
                "selected_items": list(self.selected_items)
            })
            
            self.logger.debug(f"Deselected items: {', '.join(deselected)}")
            
        return deselected
    
    def clear_selection(self) -> None:
        """Clear all selected items."""
        if not self.selected_items:
            return
            
        deselected = list(self.selected_items)
        self.selected_items.clear()
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.SELECTION_CHANGED, {
            "action": "cleared",
            "item_ids": deselected,
            "selected_items": []
        })
        
        self.logger.debug("Cleared selection")
    
    def get_selected_items(self) -> List[TimelineItem]:
        """
        Get selected items.
        
        Returns:
            List of selected items
        """
        return [self.items[item_id] for item_id in self.selected_items if item_id in self.items]
    
    def is_item_selected(self, item_id: str) -> bool:
        """
        Check if an item is selected.
        
        Args:
            item_id: ID of the item to check
            
        Returns:
            True if the item is selected, False otherwise
        """
        return item_id in self.selected_items
    
    def add_group(self,
                title: str,
                items: Optional[List[str]] = None,
                subgroups: Optional[List[str]] = None,
                expanded: bool = True,
                visible: bool = True,
                style: Optional[Dict[str, Any]] = None,
                metadata: Optional[Dict[str, Any]] = None,
                group_id: Optional[str] = None) -> str:
        """
        Add a group to the timeline.
        
        Args:
            title: Title of the group
            items: Optional list of item IDs in the group
            subgroups: Optional list of subgroup IDs
            expanded: Whether the group is expanded
            visible: Whether the group is visible
            style: Optional style configuration
            metadata: Optional metadata
            group_id: Optional group ID, generated if not provided
            
        Returns:
            The group ID
        """
        # Generate group ID if not provided
        if group_id is None:
            group_id = str(uuid.uuid4())
            
        # Create group
        group = TimelineGroup(
            group_id=group_id,
            title=title,
            items=items or [],
            subgroups=subgroups or [],
            expanded=expanded,
            visible=visible,
            style=style or {},
            metadata=metadata or {}
        )
        
        # Add to groups
        self.groups[group_id] = group
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "group_added",
            "group_id": group_id,
            "group": {
                "id": group_id,
                "title": title,
                "items": group.items,
                "subgroups": group.subgroups,
                "expanded": expanded,
                "visible": visible
            }
        })
        
        self.logger.debug(f"Added group: {group_id} ({title})")
        return group_id
    
    def update_group(self,
                   group_id: str,
                   title: Optional[str] = None,
                   items: Optional[List[str]] = None,
                   subgroups: Optional[List[str]] = None,
                   expanded: Optional[bool] = None,
                   visible: Optional[bool] = None,
                   style: Optional[Dict[str, Any]] = None,
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a group.
        
        Args:
            group_id: ID of the group to update
            title: Optional new title
            items: Optional new list of item IDs
            subgroups: Optional new list of subgroup IDs
            expanded: Optional new expanded state
            visible: Optional new visible state
            style: Optional new style
            metadata: Optional new metadata
            
        Returns:
            True if the group was updated, False if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Update properties
        if title is not None:
            group.title = title
            
        if items is not None:
            group.items = items
            
        if subgroups is not None:
            group.subgroups = subgroups
            
        if expanded is not None:
            group.expanded = expanded
            
        if visible is not None:
            group.visible = visible
            
        if style is not None:
            group.style.update(style)
            
        if metadata is not None:
            group.metadata.update(metadata)
            
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "group_updated",
            "group_id": group_id,
            "group": {
                "id": group_id,
                "title": group.title,
                "items": group.items,
                "subgroups": group.subgroups,
                "expanded": group.expanded,
                "visible": group.visible
            }
        })
        
        self.logger.debug(f"Updated group: {group_id} ({group.title})")
        return True
    
    def delete_group(self, group_id: str) -> bool:
        """
        Delete a group.
        
        Args:
            group_id: ID of the group to delete
            
        Returns:
            True if the group was deleted, False if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Remove from groups
        del self.groups[group_id]
        
        # Remove from subgroups of other groups
        for other_group in self.groups.values():
            if group_id in other_group.subgroups:
                other_group.subgroups.remove(group_id)
                
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "group_deleted",
            "group_id": group_id,
            "group": {
                "id": group_id,
                "title": group.title
            }
        })
        
        self.logger.debug(f"Deleted group: {group_id} ({group.title})")
        return True
    
    def get_group(self, group_id: str) -> Optional[TimelineGroup]:
        """
        Get a group.
        
        Args:
            group_id: ID of the group to get
            
        Returns:
            The group, or None if not found
        """
        return self.groups.get(group_id)
    
    def get_groups(self) -> List[TimelineGroup]:
        """
        Get all groups.
        
        Returns:
            List of groups
        """
        return list(self.groups.values())
    
    def add_item_to_group(self, item_id: str, group_id: str) -> bool:
        """
        Add an item to a group.
        
        Args:
            item_id: ID of the item to add
            group_id: ID of the group to add the item to
            
        Returns:
            True if the item was added, False if item or group not found
        """
        if item_id not in self.items:
            self.logger.warning(f"Item {item_id} not found.")
            return False
            
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Add to group
        if item_id not in group.items:
            group.items.append(item_id)
            
            # Dispatch event
            self._dispatch_event(TimelineEventType.CUSTOM, {
                "action": "item_added_to_group",
                "item_id": item_id,
                "group_id": group_id
            })
            
            self.logger.debug(f"Added item {item_id} to group {group_id}")
            
        return True
    
    def remove_item_from_group(self, item_id: str, group_id: str) -> bool:
        """
        Remove an item from a group.
        
        Args:
            item_id: ID of the item to remove
            group_id: ID of the group to remove the item from
            
        Returns:
            True if the item was removed, False if item or group not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Remove from group
        if item_id in group.items:
            group.items.remove(item_id)
            
            # Dispatch event
            self._dispatch_event(TimelineEventType.CUSTOM, {
                "action": "item_removed_from_group",
                "item_id": item_id,
                "group_id": group_id
            })
            
            self.logger.debug(f"Removed item {item_id} from group {group_id}")
            
        return True
    
    def add_subgroup(self, parent_id: str, child_id: str) -> bool:
        """
        Add a subgroup to a group.
        
        Args:
            parent_id: ID of the parent group
            child_id: ID of the child group
            
        Returns:
            True if the subgroup was added, False if parent or child not found
        """
        if parent_id not in self.groups:
            self.logger.warning(f"Parent group {parent_id} not found.")
            return False
            
        if child_id not in self.groups:
            self.logger.warning(f"Child group {child_id} not found.")
            return False
            
        parent = self.groups[parent_id]
        
        # Add to subgroups
        if child_id not in parent.subgroups:
            parent.subgroups.append(child_id)
            
            # Dispatch event
            self._dispatch_event(TimelineEventType.CUSTOM, {
                "action": "subgroup_added",
                "parent_id": parent_id,
                "child_id": child_id
            })
            
            self.logger.debug(f"Added subgroup {child_id} to group {parent_id}")
            
        return True
    
    def remove_subgroup(self, parent_id: str, child_id: str) -> bool:
        """
        Remove a subgroup from a group.
        
        Args:
            parent_id: ID of the parent group
            child_id: ID of the child group
            
        Returns:
            True if the subgroup was removed, False if parent not found
        """
        if parent_id not in self.groups:
            self.logger.warning(f"Parent group {parent_id} not found.")
            return False
            
        parent = self.groups[parent_id]
        
        # Remove from subgroups
        if child_id in parent.subgroups:
            parent.subgroups.remove(child_id)
            
            # Dispatch event
            self._dispatch_event(TimelineEventType.CUSTOM, {
                "action": "subgroup_removed",
                "parent_id": parent_id,
                "child_id": child_id
            })
            
            self.logger.debug(f"Removed subgroup {child_id} from group {parent_id}")
            
        return True
    
    def expand_group(self, group_id: str) -> bool:
        """
        Expand a group.
        
        Args:
            group_id: ID of the group to expand
            
        Returns:
            True if the group was expanded, False if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Update expanded state
        group.expanded = True
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "group_expanded",
            "group_id": group_id
        })
        
        self.logger.debug(f"Expanded group: {group_id}")
        return True
    
    def collapse_group(self, group_id: str) -> bool:
        """
        Collapse a group.
        
        Args:
            group_id: ID of the group to collapse
            
        Returns:
            True if the group was collapsed, False if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Update expanded state
        group.expanded = False
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "group_collapsed",
            "group_id": group_id
        })
        
        self.logger.debug(f"Collapsed group: {group_id}")
        return True
    
    def show_group(self, group_id: str) -> bool:
        """
        Show a group.
        
        Args:
            group_id: ID of the group to show
            
        Returns:
            True if the group was shown, False if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Update visible state
        group.visible = True
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "group_shown",
            "group_id": group_id
        })
        
        self.logger.debug(f"Showed group: {group_id}")
        return True
    
    def hide_group(self, group_id: str) -> bool:
        """
        Hide a group.
        
        Args:
            group_id: ID of the group to hide
            
        Returns:
            True if the group was hidden, False if not found
        """
        if group_id not in self.groups:
            self.logger.warning(f"Group {group_id} not found.")
            return False
            
        group = self.groups[group_id]
        
        # Update visible state
        group.visible = False
        
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "group_hidden",
            "group_id": group_id
        })
        
        self.logger.debug(f"Hid group: {group_id}")
        return True
    
    def set_style(self, style: Dict[str, Any]) -> None:
        """
        Set the timeline style.
        
        Args:
            style: Style configuration
        """
        # Update style properties
        for key, value in style.items():
            if hasattr(self.style, key):
                setattr(self.style, key, value)
            else:
                self.style.custom_css[key] = value
                
        # Dispatch event
        self._dispatch_event(TimelineEventType.CUSTOM, {
            "action": "style_updated",
            "style": {
                "background_color": self.style.background_color,
                "text_color": self.style.text_color,
                "grid_color": self.style.grid_color,
                "axis_color": self.style.axis_color,
                "highlight_color": self.style.highlight_color,
                "selection_color": self.style.selection_color,
                "font_family": self.style.font_family,
                "font_size": self.style.font_size,
                "line_width": self.style.line_width,
                "item_height": self.style.item_height,
                "item_spacing": self.style.item_spacing,
                "custom_css": self.style.custom_css
            }
        })
        
        self.logger.debug("Updated timeline style")
    
    def get_style(self) -> TimelineStyle:
        """
        Get the timeline style.
        
        Returns:
            The timeline style
        """
        return self.style
    
    def add_event_listener(self, event_type: Union[TimelineEventType, str], listener: Callable[[TimelineEvent], None]) -> bool:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
            
        Returns:
            True if the listener was added, False if invalid event type
        """
        # Convert event_type to TimelineEventType if needed
        if not isinstance(event_type, TimelineEventType):
            try:
                event_type = TimelineEventType(event_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid event type: {event_type}.")
                return False
                
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        return True
    
    def remove_event_listener(self, event_type: Union[TimelineEventType, str], listener: Callable[[TimelineEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        # Convert event_type to TimelineEventType if needed
        if not isinstance(event_type, TimelineEventType):
            try:
                event_type = TimelineEventType(event_type)
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
        Render the timeline for display.
        
        Returns:
            Rendered timeline data
        """
        # Get filtered items
        filtered_items = self.get_filtered_items()
        
        # Convert items to dictionaries
        items_data = [item.to_dict() for item in filtered_items]
        
        # Convert groups to dictionaries
        groups_data = []
        for group_id, group in self.groups.items():
            if not group.visible:
                continue
                
            groups_data.append({
                "id": group_id,
                "title": group.title,
                "items": group.items,
                "subgroups": group.subgroups,
                "expanded": group.expanded,
                "style": group.style
            })
            
        # Build the timeline data
        timeline_data = {
            "items": items_data,
            "groups": groups_data,
            "selected_items": list(self.selected_items),
            "view_mode": self.view_mode.value,
            "zoom_level": self.zoom_level.value,
            "group_by": self.group_by.value,
            "visible_range": {
                "start": self.visible_range.start.isoformat() if self.visible_range else None,
                "end": self.visible_range.end.isoformat() if self.visible_range else None
            },
            "style": {
                "background_color": self.style.background_color,
                "text_color": self.style.text_color,
                "grid_color": self.style.grid_color,
                "axis_color": self.style.axis_color,
                "highlight_color": self.style.highlight_color,
                "selection_color": self.style.selection_color,
                "font_family": self.style.font_family,
                "font_size": self.style.font_size,
                "line_width": self.style.line_width,
                "item_height": self.style.item_height,
                "item_spacing": self.style.item_spacing,
                "custom_css": self.style.custom_css
            }
        }
        
        return timeline_data
    
    def _update_groups(self) -> None:
        """Update groups based on the current grouping."""
        # Clear existing groups
        self.groups.clear()
        
        if self.group_by == TimelineGroupBy.NONE:
            return
            
        # Group items based on the grouping
        if self.group_by == TimelineGroupBy.CATEGORY:
            self._group_by_property("category")
        elif self.group_by == TimelineGroupBy.PRIORITY:
            self._group_by_property("priority")
        elif self.group_by == TimelineGroupBy.STATUS:
            self._group_by_property("status")
        elif self.group_by == TimelineGroupBy.RESOURCE:
            self._group_by_property("resource")
        elif self.group_by == TimelineGroupBy.LOCATION:
            self._group_by_property("location")
        elif self.group_by == TimelineGroupBy.CUSTOM:
            # Custom grouping logic would be implemented here
            pass
    
    def _group_by_property(self, property_name: str) -> None:
        """
        Group items by a specific property.
        
        Args:
            property_name: Name of the property to group by
        """
        # Group items by property
        groups = {}
        
        for item_id, item in self.items.items():
            property_value = getattr(item, property_name)
            
            if property_value is None:
                property_value = "None"
                
            if property_value not in groups:
                groups[property_value] = []
                
            groups[property_value].append(item_id)
            
        # Create groups
        for property_value, item_ids in groups.items():
            group_id = f"{property_name}_{property_value}"
            
            self.groups[group_id] = TimelineGroup(
                group_id=group_id,
                title=str(property_value),
                items=item_ids
            )
    
    def _dispatch_event(self, event_type: TimelineEventType, data: Dict[str, Any]) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event_type: Type of event
            data: Event data
        """
        # Create event
        event = TimelineEvent(
            event_type=event_type,
            source="TimelineViewComponent",
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
    
    def _event_to_dict(self, event: TimelineEvent) -> Dict[str, Any]:
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

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create timeline view component
    timeline = TimelineViewComponent()
    
    # Start the component
    timeline.start()
    
    # Add an event listener
    def on_item_click(event):
        print(f"Item clicked: {event.data['item_id']}")
        
    timeline.add_event_listener(TimelineEventType.ITEM_CLICKED, on_item_click)
    
    # Set the visible range
    now = datetime.now()
    timeline.set_visible_range(
        start=now - timedelta(days=7),
        end=now + timedelta(days=7)
    )
    
    # Add some items
    timeline.add_item(
        title="Equipment Maintenance",
        start_time=now - timedelta(days=2),
        end_time=now - timedelta(days=1),
        type=TimelineItemType.TASK,
        category="Maintenance",
        priority="High",
        status="Completed",
        resource="Technician A",
        location="Building 1",
        content="Regular maintenance of production equipment"
    )
    
    timeline.add_item(
        title="Power Outage",
        start_time=now - timedelta(days=3, hours=4),
        type=TimelineItemType.EVENT,
        category="Incident",
        priority="Critical",
        status="Resolved",
        location="Building 2",
        content="Unexpected power outage affecting production line"
    )
    
    timeline.add_item(
        title="Production Run",
        start_time=now,
        end_time=now + timedelta(days=3),
        type=TimelineItemType.PROCESS,
        category="Production",
        priority="Medium",
        status="In Progress",
        resource="Production Team",
        location="Building 1",
        content="Manufacturing of Product X"
    )
    
    # Add a filter
    timeline.add_filter(
        type=TimelineFilterType.CATEGORY,
        title="Show Production Only",
        params={"categories": ["Production"]}
    )
    
    # Group by category
    timeline.set_group_by(TimelineGroupBy.CATEGORY)
    
    # Render the timeline
    rendered = timeline.render()
    print(f"Timeline has {len(rendered['items'])} items and {len(rendered['groups'])} groups")
    
    # Stop the component
    timeline.stop()
"""
