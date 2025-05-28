"""
Ambient Intelligence Dashboard Component for the Industriverse UI/UX Layer.

This module provides a comprehensive dashboard for ambient intelligence visualization,
monitoring, and interaction in industrial environments.

Author: Manus
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field

class DashboardWidgetType(Enum):
    """Enumeration of dashboard widget types."""
    METRIC = "metric"
    CHART = "chart"
    TABLE = "table"
    ALERT = "alert"
    STATUS = "status"
    CONTROL = "control"
    TIMELINE = "timeline"
    MAP = "map"
    DIGITAL_TWIN = "digital_twin"
    AGENT_STATUS = "agent_status"
    WORKFLOW = "workflow"
    PROTOCOL = "protocol"
    CUSTOM = "custom"

class DashboardLayoutType(Enum):
    """Enumeration of dashboard layout types."""
    GRID = "grid"
    FLEX = "flex"
    MASONRY = "masonry"
    FIXED = "fixed"
    RESPONSIVE = "responsive"
    CUSTOM = "custom"

class AlertLevel(Enum):
    """Enumeration of alert levels."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class DashboardWidget:
    """Data class representing a dashboard widget."""
    widget_id: str
    type: DashboardWidgetType
    title: str
    data: Any
    position: Dict[str, Any]
    size: Dict[str, Any]
    config: Dict[str, Any] = field(default_factory=dict)
    style: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class Dashboard:
    """Data class representing a dashboard."""
    dashboard_id: str
    name: str
    layout_type: DashboardLayoutType
    widgets: Dict[str, DashboardWidget] = field(default_factory=dict)
    layout_config: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class DashboardEvent:
    """Data class representing a dashboard event."""
    event_type: str
    source: str
    target: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class AmbientIntelligenceDashboardComponent:
    """
    Provides a comprehensive dashboard for ambient intelligence in the Industriverse UI/UX Layer.
    
    This class provides:
    - Real-time monitoring of industrial systems
    - Ambient intelligence visualization
    - Customizable dashboards with various widget types
    - Multi-dashboard support
    - Real-time data updates
    - Interactive controls
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Ambient Intelligence Dashboard Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.dashboards: Dict[str, Dashboard] = {}
        self.active_dashboard_id: Optional[str] = None
        self.data_sources: Dict[str, Dict[str, Any]] = {}
        self.update_intervals: Dict[str, int] = {}
        self.update_threads: Dict[str, Any] = {}
        self.event_listeners: Dict[str, List[Callable[[DashboardEvent], None]]] = {}
        self.widget_listeners: Dict[str, List[Callable[[DashboardWidget], None]]] = {}
        self.dashboard_listeners: Dict[str, List[Callable[[Dashboard], None]]] = {}
        self.global_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        
        # Initialize widget renderers
        self.renderers = {
            DashboardWidgetType.METRIC: self._render_metric_widget,
            DashboardWidgetType.CHART: self._render_chart_widget,
            DashboardWidgetType.TABLE: self._render_table_widget,
            DashboardWidgetType.ALERT: self._render_alert_widget,
            DashboardWidgetType.STATUS: self._render_status_widget,
            DashboardWidgetType.CONTROL: self._render_control_widget,
            DashboardWidgetType.TIMELINE: self._render_timeline_widget,
            DashboardWidgetType.MAP: self._render_map_widget,
            DashboardWidgetType.DIGITAL_TWIN: self._render_digital_twin_widget,
            DashboardWidgetType.AGENT_STATUS: self._render_agent_status_widget,
            DashboardWidgetType.WORKFLOW: self._render_workflow_widget,
            DashboardWidgetType.PROTOCOL: self._render_protocol_widget,
            DashboardWidgetType.CUSTOM: self._render_custom_widget
        }
        
        # Create default dashboard
        self.create_dashboard("default", "Default Dashboard", DashboardLayoutType.GRID)
        self.active_dashboard_id = "default"
        
    def start(self) -> bool:
        """
        Start the Ambient Intelligence Dashboard Component.
        
        Returns:
            True if the component was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start all data update threads
        for widget_id, interval in self.update_intervals.items():
            self._start_widget_updates(widget_id, interval)
            
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="dashboard_component_started",
            source="AmbientIntelligenceDashboardComponent"
        ))
        
        self.logger.info("Ambient Intelligence Dashboard Component started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Ambient Intelligence Dashboard Component.
        
        Returns:
            True if the component was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Stop all update threads
        for widget_id, thread in self.update_threads.items():
            if thread and thread.is_alive():
                # Set a flag to stop the thread
                thread.stop_requested = True
                
        self.update_threads.clear()
        
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="dashboard_component_stopped",
            source="AmbientIntelligenceDashboardComponent"
        ))
        
        self.logger.info("Ambient Intelligence Dashboard Component stopped.")
        return True
    
    def create_dashboard(self,
                       dashboard_id: Optional[str] = None,
                       name: Optional[str] = None,
                       layout_type: DashboardLayoutType = DashboardLayoutType.GRID,
                       layout_config: Optional[Dict[str, Any]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new dashboard.
        
        Args:
            dashboard_id: Optional dashboard ID, generated if not provided
            name: Optional dashboard name, defaults to "Dashboard {id}"
            layout_type: Layout type for the dashboard
            layout_config: Optional layout configuration
            metadata: Optional metadata
            
        Returns:
            The dashboard ID
        """
        # Generate dashboard ID if not provided
        if dashboard_id is None:
            dashboard_id = str(uuid.uuid4())
            
        # Generate dashboard name if not provided
        if name is None:
            name = f"Dashboard {dashboard_id[:8]}"
            
        # Convert layout_type to DashboardLayoutType if needed
        if not isinstance(layout_type, DashboardLayoutType):
            try:
                layout_type = DashboardLayoutType(layout_type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid layout type: {layout_type}, using GRID.")
                layout_type = DashboardLayoutType.GRID
                
        # Create dashboard
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            name=name,
            layout_type=layout_type,
            layout_config=layout_config or {},
            metadata=metadata or {}
        )
        
        # Store dashboard
        self.dashboards[dashboard_id] = dashboard
        
        # Set as active dashboard if no active dashboard
        if self.active_dashboard_id is None:
            self.active_dashboard_id = dashboard_id
            
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="dashboard_created",
            source="AmbientIntelligenceDashboardComponent",
            target=dashboard_id,
            data={"dashboard_name": name}
        ))
        
        # Notify dashboard listeners
        self._notify_dashboard_listeners(dashboard)
        
        self.logger.debug(f"Created dashboard: {dashboard_id} ({name})")
        return dashboard_id
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """
        Get a dashboard by ID.
        
        Args:
            dashboard_id: ID of the dashboard to get
            
        Returns:
            The dashboard, or None if not found
        """
        return self.dashboards.get(dashboard_id)
    
    def set_active_dashboard(self, dashboard_id: str) -> bool:
        """
        Set the active dashboard.
        
        Args:
            dashboard_id: ID of the dashboard to set as active
            
        Returns:
            True if the dashboard was set as active, False if not found
        """
        if dashboard_id not in self.dashboards:
            self.logger.warning(f"Dashboard {dashboard_id} not found.")
            return False
            
        old_dashboard_id = self.active_dashboard_id
        self.active_dashboard_id = dashboard_id
        
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="active_dashboard_changed",
            source="AmbientIntelligenceDashboardComponent",
            target=dashboard_id,
            data={"old_dashboard_id": old_dashboard_id}
        ))
        
        self.logger.debug(f"Set active dashboard: {dashboard_id}")
        return True
    
    def update_dashboard(self,
                       dashboard_id: str,
                       name: Optional[str] = None,
                       layout_type: Optional[DashboardLayoutType] = None,
                       layout_config: Optional[Dict[str, Any]] = None,
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard to update
            name: Optional new name
            layout_type: Optional new layout type
            layout_config: Optional new layout configuration
            metadata: Optional new metadata
            
        Returns:
            True if the dashboard was updated, False if not found
        """
        if dashboard_id not in self.dashboards:
            self.logger.warning(f"Dashboard {dashboard_id} not found.")
            return False
            
        dashboard = self.dashboards[dashboard_id]
        
        # Update properties
        if name is not None:
            dashboard.name = name
            
        if layout_type is not None:
            # Convert layout_type to DashboardLayoutType if needed
            if not isinstance(layout_type, DashboardLayoutType):
                try:
                    layout_type = DashboardLayoutType(layout_type)
                except (ValueError, TypeError):
                    self.logger.warning(f"Invalid layout type: {layout_type}, ignoring.")
                else:
                    dashboard.layout_type = layout_type
            else:
                dashboard.layout_type = layout_type
                
        if layout_config is not None:
            dashboard.layout_config.update(layout_config)
            
        if metadata is not None:
            dashboard.metadata.update(metadata)
            
        # Update timestamp
        dashboard.timestamp = time.time()
        
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="dashboard_updated",
            source="AmbientIntelligenceDashboardComponent",
            target=dashboard_id,
            data={"dashboard_name": dashboard.name}
        ))
        
        # Notify dashboard listeners
        self._notify_dashboard_listeners(dashboard)
        
        self.logger.debug(f"Updated dashboard: {dashboard_id} ({dashboard.name})")
        return True
    
    def delete_dashboard(self, dashboard_id: str) -> bool:
        """
        Delete a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard to delete
            
        Returns:
            True if the dashboard was deleted, False if not found
        """
        if dashboard_id not in self.dashboards:
            self.logger.warning(f"Dashboard {dashboard_id} not found.")
            return False
            
        # Cannot delete the last dashboard
        if len(self.dashboards) <= 1:
            self.logger.warning("Cannot delete the last dashboard.")
            return False
            
        dashboard = self.dashboards[dashboard_id]
        
        # Stop all widget update threads for this dashboard
        for widget_id in dashboard.widgets:
            if widget_id in self.update_threads:
                thread = self.update_threads[widget_id]
                if thread and thread.is_alive():
                    thread.stop_requested = True
                del self.update_threads[widget_id]
                
        # Remove dashboard
        del self.dashboards[dashboard_id]
        
        # Update active dashboard if needed
        if self.active_dashboard_id == dashboard_id:
            # Set first available dashboard as active
            self.active_dashboard_id = next(iter(self.dashboards.keys()))
            
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="dashboard_deleted",
            source="AmbientIntelligenceDashboardComponent",
            target=dashboard_id,
            data={"dashboard_name": dashboard.name}
        ))
        
        self.logger.debug(f"Deleted dashboard: {dashboard_id} ({dashboard.name})")
        return True
    
    def create_widget(self,
                    dashboard_id: Optional[str],
                    type: DashboardWidgetType,
                    title: str,
                    data: Any,
                    position: Dict[str, Any],
                    size: Dict[str, Any],
                    widget_id: Optional[str] = None,
                    config: Optional[Dict[str, Any]] = None,
                    style: Optional[Dict[str, Any]] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    update_interval: Optional[int] = None,
                    data_source: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new dashboard widget.
        
        Args:
            dashboard_id: ID of the dashboard to add the widget to, uses active dashboard if None
            type: Type of widget
            title: Widget title
            data: Widget data
            position: Widget position (e.g., {"x": 0, "y": 0})
            size: Widget size (e.g., {"w": 2, "h": 1})
            widget_id: Optional widget ID, generated if not provided
            config: Optional widget configuration
            style: Optional widget style
            metadata: Optional metadata
            update_interval: Optional update interval in milliseconds
            data_source: Optional data source configuration
            
        Returns:
            The widget ID
        """
        # Use active dashboard if not provided
        if dashboard_id is None:
            dashboard_id = self.active_dashboard_id
            
        if dashboard_id not in self.dashboards:
            self.logger.warning(f"Dashboard {dashboard_id} not found, using default dashboard.")
            dashboard_id = "default"
            
        # Generate widget ID if not provided
        if widget_id is None:
            widget_id = str(uuid.uuid4())
            
        # Convert type to DashboardWidgetType if needed
        if not isinstance(type, DashboardWidgetType):
            try:
                type = DashboardWidgetType(type)
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid widget type: {type}, using CUSTOM.")
                type = DashboardWidgetType.CUSTOM
                
        # Create widget
        widget = DashboardWidget(
            widget_id=widget_id,
            type=type,
            title=title,
            data=data,
            position=position,
            size=size,
            config=config or {},
            style=style or {},
            metadata=metadata or {}
        )
        
        # Add to dashboard
        dashboard = self.dashboards[dashboard_id]
        dashboard.widgets[widget_id] = widget
        
        # Update dashboard timestamp
        dashboard.timestamp = time.time()
        
        # Store data source if provided
        if data_source:
            self.data_sources[widget_id] = data_source
            
        # Set up update interval if provided
        if update_interval:
            self.update_intervals[widget_id] = update_interval
            
            # Start updates if component is active
            if self.is_active:
                self._start_widget_updates(widget_id, update_interval)
                
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="widget_created",
            source="AmbientIntelligenceDashboardComponent",
            target=widget_id,
            data={"type": type.value, "title": title, "dashboard_id": dashboard_id}
        ))
        
        # Notify widget listeners
        self._notify_widget_listeners(widget)
        
        # Notify dashboard listeners
        self._notify_dashboard_listeners(dashboard)
        
        self.logger.debug(f"Created widget: {widget_id} ({title}) in dashboard {dashboard_id}")
        return widget_id
    
    def get_widget(self, widget_id: str, dashboard_id: Optional[str] = None) -> Optional[DashboardWidget]:
        """
        Get a widget by ID.
        
        Args:
            widget_id: ID of the widget to get
            dashboard_id: Optional dashboard ID, searches all dashboards if not provided
            
        Returns:
            The widget, or None if not found
        """
        if dashboard_id:
            if dashboard_id not in self.dashboards:
                return None
            return self.dashboards[dashboard_id].widgets.get(widget_id)
            
        # Search all dashboards
        for dashboard in self.dashboards.values():
            if widget_id in dashboard.widgets:
                return dashboard.widgets[widget_id]
                
        return None
    
    def update_widget(self,
                    widget_id: str,
                    title: Optional[str] = None,
                    data: Optional[Any] = None,
                    position: Optional[Dict[str, Any]] = None,
                    size: Optional[Dict[str, Any]] = None,
                    config: Optional[Dict[str, Any]] = None,
                    style: Optional[Dict[str, Any]] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    dashboard_id: Optional[str] = None) -> bool:
        """
        Update a widget.
        
        Args:
            widget_id: ID of the widget to update
            title: Optional new title
            data: Optional new data
            position: Optional new position
            size: Optional new size
            config: Optional new configuration
            style: Optional new style
            metadata: Optional new metadata
            dashboard_id: Optional dashboard ID, searches all dashboards if not provided
            
        Returns:
            True if the widget was updated, False if not found
        """
        # Find the widget
        widget = None
        widget_dashboard_id = None
        
        if dashboard_id:
            if dashboard_id not in self.dashboards:
                self.logger.warning(f"Dashboard {dashboard_id} not found.")
                return False
            if widget_id not in self.dashboards[dashboard_id].widgets:
                self.logger.warning(f"Widget {widget_id} not found in dashboard {dashboard_id}.")
                return False
            widget = self.dashboards[dashboard_id].widgets[widget_id]
            widget_dashboard_id = dashboard_id
        else:
            # Search all dashboards
            for d_id, dashboard in self.dashboards.items():
                if widget_id in dashboard.widgets:
                    widget = dashboard.widgets[widget_id]
                    widget_dashboard_id = d_id
                    break
                    
        if widget is None:
            self.logger.warning(f"Widget {widget_id} not found.")
            return False
            
        # Update properties
        if title is not None:
            widget.title = title
        if data is not None:
            widget.data = data
        if position is not None:
            widget.position.update(position)
        if size is not None:
            widget.size.update(size)
        if config is not None:
            widget.config.update(config)
        if style is not None:
            widget.style.update(style)
        if metadata is not None:
            widget.metadata.update(metadata)
            
        # Update timestamp
        widget.timestamp = time.time()
        
        # Update dashboard timestamp
        self.dashboards[widget_dashboard_id].timestamp = time.time()
        
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="widget_updated",
            source="AmbientIntelligenceDashboardComponent",
            target=widget_id,
            data={"type": widget.type.value, "title": widget.title, "dashboard_id": widget_dashboard_id}
        ))
        
        # Notify widget listeners
        self._notify_widget_listeners(widget)
        
        # Notify dashboard listeners
        self._notify_dashboard_listeners(self.dashboards[widget_dashboard_id])
        
        self.logger.debug(f"Updated widget: {widget_id} ({widget.title}) in dashboard {widget_dashboard_id}")
        return True
    
    def delete_widget(self, widget_id: str, dashboard_id: Optional[str] = None) -> bool:
        """
        Delete a widget.
        
        Args:
            widget_id: ID of the widget to delete
            dashboard_id: Optional dashboard ID, searches all dashboards if not provided
            
        Returns:
            True if the widget was deleted, False if not found
        """
        # Find the widget
        widget = None
        widget_dashboard_id = None
        
        if dashboard_id:
            if dashboard_id not in self.dashboards:
                self.logger.warning(f"Dashboard {dashboard_id} not found.")
                return False
            if widget_id not in self.dashboards[dashboard_id].widgets:
                self.logger.warning(f"Widget {widget_id} not found in dashboard {dashboard_id}.")
                return False
            widget = self.dashboards[dashboard_id].widgets[widget_id]
            widget_dashboard_id = dashboard_id
        else:
            # Search all dashboards
            for d_id, dashboard in self.dashboards.items():
                if widget_id in dashboard.widgets:
                    widget = dashboard.widgets[widget_id]
                    widget_dashboard_id = d_id
                    break
                    
        if widget is None:
            self.logger.warning(f"Widget {widget_id} not found.")
            return False
            
        # Stop update thread if any
        if widget_id in self.update_threads:
            thread = self.update_threads[widget_id]
            if thread and thread.is_alive():
                thread.stop_requested = True
            del self.update_threads[widget_id]
            
        # Remove from update intervals
        if widget_id in self.update_intervals:
            del self.update_intervals[widget_id]
            
        # Remove from data sources
        if widget_id in self.data_sources:
            del self.data_sources[widget_id]
            
        # Remove from dashboard
        dashboard = self.dashboards[widget_dashboard_id]
        del dashboard.widgets[widget_id]
        
        # Update dashboard timestamp
        dashboard.timestamp = time.time()
        
        # Dispatch event
        self._dispatch_event(DashboardEvent(
            event_type="widget_deleted",
            source="AmbientIntelligenceDashboardComponent",
            target=widget_id,
            data={"type": widget.type.value, "title": widget.title, "dashboard_id": widget_dashboard_id}
        ))
        
        # Notify dashboard listeners
        self._notify_dashboard_listeners(dashboard)
        
        self.logger.debug(f"Deleted widget: {widget_id} ({widget.title}) from dashboard {widget_dashboard_id}")
        return True
    
    def set_widget_update_interval(self, widget_id: str, interval: int) -> bool:
        """
        Set the update interval for a widget.
        
        Args:
            widget_id: ID of the widget
            interval: Update interval in milliseconds
            
        Returns:
            True if the interval was set, False if widget not found
        """
        widget = self.get_widget(widget_id)
        if widget is None:
            self.logger.warning(f"Widget {widget_id} not found.")
            return False
            
        old_interval = self.update_intervals.get(widget_id)
        self.update_intervals[widget_id] = interval
        
        # Restart update thread if interval changed
        if old_interval != interval and self.is_active:
            if widget_id in self.update_threads:
                thread = self.update_threads[widget_id]
                if thread and thread.is_alive():
                    thread.stop_requested = True
                    
            self._start_widget_updates(widget_id, interval)
            
        self.logger.debug(f"Set update interval for widget {widget_id} to {interval}ms")
        return True
    
    def set_widget_data_source(self, widget_id: str, data_source: Dict[str, Any]) -> bool:
        """
        Set the data source for a widget.
        
        Args:
            widget_id: ID of the widget
            data_source: Data source configuration
            
        Returns:
            True if the data source was set, False if widget not found
        """
        widget = self.get_widget(widget_id)
        if widget is None:
            self.logger.warning(f"Widget {widget_id} not found.")
            return False
            
        self.data_sources[widget_id] = data_source
        
        self.logger.debug(f"Set data source for widget {widget_id}")
        return True
    
    def render_dashboard(self, dashboard_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Render a dashboard.
        
        Args:
            dashboard_id: ID of the dashboard to render, uses active dashboard if not provided
            
        Returns:
            Rendered dashboard data
        """
        # Use active dashboard if not provided
        if dashboard_id is None:
            dashboard_id = self.active_dashboard_id
            
        if dashboard_id not in self.dashboards:
            self.logger.warning(f"Dashboard {dashboard_id} not found.")
            return {"error": "Dashboard not found"}
            
        dashboard = self.dashboards[dashboard_id]
        
        # Render all widgets
        widgets_data = []
        
        for widget_id, widget in dashboard.widgets.items():
            # Get the appropriate renderer
            renderer = self.renderers.get(widget.type)
            if not renderer:
                self.logger.warning(f"No renderer found for widget type {widget.type.value}.")
                continue
                
            # Render the widget
            try:
                rendered_data = renderer(widget)
                widgets_data.append(rendered_data)
            except Exception as e:
                self.logger.error(f"Error rendering widget {widget_id}: {e}")
                
        # Build the dashboard data
        dashboard_data = {
            "id": dashboard_id,
            "name": dashboard.name,
            "layout_type": dashboard.layout_type.value,
            "layout_config": dashboard.layout_config,
            "widgets": widgets_data,
            "metadata": dashboard.metadata,
            "timestamp": dashboard.timestamp
        }
        
        return dashboard_data
    
    def add_event_listener(self, event_type: str, listener: Callable[[DashboardEvent], None]) -> None:
        """
        Add a listener for a specific event type.
        
        Args:
            event_type: Type of event to listen for
            listener: Callback function that will be called when the event occurs
        """
        if event_type not in self.event_listeners:
            self.event_listeners[event_type] = []
            
        self.event_listeners[event_type].append(listener)
        
    def add_widget_listener(self, widget_id: str, listener: Callable[[DashboardWidget], None]) -> bool:
        """
        Add a listener for a specific widget.
        
        Args:
            widget_id: ID of the widget to listen for
            listener: Callback function that will be called when the widget is updated
            
        Returns:
            True if the listener was added, False if widget not found
        """
        if self.get_widget(widget_id) is None:
            return False
            
        if widget_id not in self.widget_listeners:
            self.widget_listeners[widget_id] = []
            
        self.widget_listeners[widget_id].append(listener)
        return True
    
    def add_dashboard_listener(self, dashboard_id: str, listener: Callable[[Dashboard], None]) -> bool:
        """
        Add a listener for a specific dashboard.
        
        Args:
            dashboard_id: ID of the dashboard to listen for
            listener: Callback function that will be called when the dashboard is updated
            
        Returns:
            True if the listener was added, False if dashboard not found
        """
        if dashboard_id not in self.dashboards:
            return False
            
        if dashboard_id not in self.dashboard_listeners:
            self.dashboard_listeners[dashboard_id] = []
            
        self.dashboard_listeners[dashboard_id].append(listener)
        return True
    
    def add_global_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all events.
        
        Args:
            listener: Callback function that will be called with event data
        """
        self.global_listeners.append(listener)
        
    def remove_event_listener(self, event_type: str, listener: Callable[[DashboardEvent], None]) -> bool:
        """
        Remove an event listener.
        
        Args:
            event_type: Type of event the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if event_type not in self.event_listeners:
            return False
            
        if listener in self.event_listeners[event_type]:
            self.event_listeners[event_type].remove(listener)
            return True
            
        return False
    
    def remove_widget_listener(self, widget_id: str, listener: Callable[[DashboardWidget], None]) -> bool:
        """
        Remove a widget listener.
        
        Args:
            widget_id: ID of the widget the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if widget_id not in self.widget_listeners:
            return False
            
        if listener in self.widget_listeners[widget_id]:
            self.widget_listeners[widget_id].remove(listener)
            return True
            
        return False
    
    def remove_dashboard_listener(self, dashboard_id: str, listener: Callable[[Dashboard], None]) -> bool:
        """
        Remove a dashboard listener.
        
        Args:
            dashboard_id: ID of the dashboard the listener was registered for
            listener: The listener to remove
            
        Returns:
            True if the listener was removed, False if not found
        """
        if dashboard_id not in self.dashboard_listeners:
            return False
            
        if listener in self.dashboard_listeners[dashboard_id]:
            self.dashboard_listeners[dashboard_id].remove(listener)
            return True
            
        return False
    
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
    
    def _start_widget_updates(self, widget_id: str, interval: int) -> None:
        """
        Start auto-updating a widget.
        
        Args:
            widget_id: ID of the widget to auto-update
            interval: Update interval in milliseconds
        """
        widget = self.get_widget(widget_id)
        if widget is None:
            return
            
        # Stop existing thread if any
        if widget_id in self.update_threads:
            thread = self.update_threads[widget_id]
            if thread and thread.is_alive():
                thread.stop_requested = True
                
        # Create and start update thread
        import threading
        
        def update_thread():
            thread = threading.current_thread()
            thread.stop_requested = False
            
            while not thread.stop_requested and self.is_active:
                try:
                    # Get data from the data source
                    data_source = self.data_sources.get(widget_id)
                    if data_source:
                        new_data = self._fetch_data_from_source(widget, data_source)
                        if new_data is not None:
                            # Update widget data
                            self.update_widget(widget_id, data=new_data)
                            
                except Exception as e:
                    self.logger.error(f"Error in update thread for widget {widget_id}: {e}")
                    
                # Sleep for the update interval
                interval_seconds = interval / 1000.0
                time.sleep(interval_seconds)
                
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
        
        self.update_threads[widget_id] = thread
        
        self.logger.debug(f"Started updates for widget: {widget_id}")
    
    def _fetch_data_from_source(self, widget: DashboardWidget, data_source: Dict[str, Any]) -> Optional[Any]:
        """
        Fetch data from a data source.
        
        Args:
            widget: The widget to fetch data for
            data_source: Data source configuration
            
        Returns:
            The fetched data, or None if no data could be fetched
        """
        # In a real implementation, this would connect to various data sources
        # For now, we'll just return some dummy data based on the widget type
        
        source_type = data_source.get("type")
        
        if source_type == "api":
            # Simulate API call
            return {"value": 42, "timestamp": time.time()}
            
        elif source_type == "database":
            # Simulate database query
            return [{"id": 1, "name": "Item 1"}, {"id": 2, "name": "Item 2"}]
            
        elif source_type == "stream":
            # Simulate data stream
            return {"value": 42, "timestamp": time.time()}
            
        elif source_type == "sensor":
            # Simulate sensor data
            import random
            return {"value": random.uniform(0, 100), "timestamp": time.time()}
            
        elif source_type == "digital_twin":
            # Simulate digital twin data
            return {"status": "online", "metrics": {"temperature": 42, "pressure": 101}}
            
        elif source_type == "agent":
            # Simulate agent data
            return {"status": "active", "tasks": 3, "completion": 0.75}
            
        elif source_type == "workflow":
            # Simulate workflow data
            return {"status": "running", "progress": 0.6, "steps": 10, "current_step": 6}
            
        elif source_type == "protocol":
            # Simulate protocol data
            return {"messages": 42, "active_connections": 3}
            
        else:
            # Default dummy data
            return {"timestamp": time.time()}
    
    def _dispatch_event(self, event: DashboardEvent) -> None:
        """
        Dispatch an event to all listeners.
        
        Args:
            event: The event to dispatch
        """
        # Dispatch to event type listeners
        if event.event_type in self.event_listeners:
            for listener in self.event_listeners[event.event_type]:
                try:
                    listener(event)
                except Exception as e:
                    self.logger.error(f"Error in event listener for {event.event_type}: {e}")
                    
        # Dispatch to global listeners
        for listener in self.global_listeners:
            try:
                listener(self._event_to_dict(event))
            except Exception as e:
                self.logger.error(f"Error in global listener: {e}")
    
    def _notify_widget_listeners(self, widget: DashboardWidget) -> None:
        """
        Notify listeners for a specific widget.
        
        Args:
            widget: The widget that was updated
        """
        if widget.widget_id in self.widget_listeners:
            for listener in self.widget_listeners[widget.widget_id]:
                try:
                    listener(widget)
                except Exception as e:
                    self.logger.error(f"Error in widget listener for {widget.widget_id}: {e}")
    
    def _notify_dashboard_listeners(self, dashboard: Dashboard) -> None:
        """
        Notify listeners for a specific dashboard.
        
        Args:
            dashboard: The dashboard that was updated
        """
        if dashboard.dashboard_id in self.dashboard_listeners:
            for listener in self.dashboard_listeners[dashboard.dashboard_id]:
                try:
                    listener(dashboard)
                except Exception as e:
                    self.logger.error(f"Error in dashboard listener for {dashboard.dashboard_id}: {e}")
    
    def _event_to_dict(self, event: DashboardEvent) -> Dict[str, Any]:
        """
        Convert event to dictionary.
        
        Args:
            event: The event to convert
            
        Returns:
            Dictionary representation of the event
        """
        event_dict = {
            "event_type": event.event_type,
            "source": event.source,
            "timestamp": event.timestamp,
            "data": event.data
        }
        
        if event.target:
            event_dict["target"] = event.target
            
        return event_dict
    
    # Widget renderer methods
    
    def _render_metric_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a metric widget."""
        return {
            "id": widget.widget_id,
            "type": "metric",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_chart_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a chart widget."""
        return {
            "id": widget.widget_id,
            "type": "chart",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_table_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a table widget."""
        return {
            "id": widget.widget_id,
            "type": "table",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_alert_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render an alert widget."""
        return {
            "id": widget.widget_id,
            "type": "alert",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_status_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a status widget."""
        return {
            "id": widget.widget_id,
            "type": "status",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_control_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a control widget."""
        return {
            "id": widget.widget_id,
            "type": "control",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_timeline_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a timeline widget."""
        return {
            "id": widget.widget_id,
            "type": "timeline",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_map_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a map widget."""
        return {
            "id": widget.widget_id,
            "type": "map",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_digital_twin_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a digital twin widget."""
        return {
            "id": widget.widget_id,
            "type": "digital_twin",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_agent_status_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render an agent status widget."""
        return {
            "id": widget.widget_id,
            "type": "agent_status",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_workflow_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a workflow widget."""
        return {
            "id": widget.widget_id,
            "type": "workflow",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_protocol_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a protocol widget."""
        return {
            "id": widget.widget_id,
            "type": "protocol",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }
    
    def _render_custom_widget(self, widget: DashboardWidget) -> Dict[str, Any]:
        """Render a custom widget."""
        return {
            "id": widget.widget_id,
            "type": "custom",
            "title": widget.title,
            "position": widget.position,
            "size": widget.size,
            "data": widget.data,
            "config": widget.config,
            "style": widget.style,
            "timestamp": widget.timestamp
        }

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create ambient intelligence dashboard component
    dashboard_component = AmbientIntelligenceDashboardComponent()
    
    # Start the component
    dashboard_component.start()
    
    # Add an event listener
    def on_event(event):
        print(f"Event: {event.event_type}")
        
    dashboard_component.add_event_listener("widget_created", on_event)
    
    # Create a dashboard
    dashboard_id = dashboard_component.create_dashboard("main", "Main Dashboard", DashboardLayoutType.GRID)
    
    # Set as active dashboard
    dashboard_component.set_active_dashboard(dashboard_id)
    
    # Create a metric widget
    metric_widget_id = dashboard_component.create_widget(
        dashboard_id=dashboard_id,
        type=DashboardWidgetType.METRIC,
        title="Temperature",
        data={"value": 25.5, "unit": "°C", "trend": "up"},
        position={"x": 0, "y": 0},
        size={"w": 1, "h": 1},
        style={"color": "#FF0000"}
    )
    
    # Create a chart widget
    chart_widget_id = dashboard_component.create_widget(
        dashboard_id=dashboard_id,
        type=DashboardWidgetType.CHART,
        title="Temperature Over Time",
        data={
            "type": "line",
            "series": [
                {
                    "name": "Temperature",
                    "data": [
                        {"x": "2023-01-01", "y": 22.5},
                        {"x": "2023-01-02", "y": 23.1},
                        {"x": "2023-01-03", "y": 22.8},
                        {"x": "2023-01-04", "y": 24.2},
                        {"x": "2023-01-05", "y": 25.0}
                    ]
                }
            ]
        },
        position={"x": 1, "y": 0},
        size={"w": 2, "h": 1},
        config={"xAxis": {"title": "Date"}, "yAxis": {"title": "Temperature (°C)"}}
    )
    
    # Create a status widget
    status_widget_id = dashboard_component.create_widget(
        dashboard_id=dashboard_id,
        type=DashboardWidgetType.STATUS,
        title="System Status",
        data={"status": "online", "uptime": "3d 4h 12m", "load": 0.75},
        position={"x": 0, "y": 1},
        size={"w": 1, "h": 1},
        style={"color": "#00FF00"}
    )
    
    # Set up data source and update interval for the metric widget
    dashboard_component.set_widget_data_source(
        metric_widget_id,
        {"type": "sensor", "sensor_id": "temp-001"}
    )
    dashboard_component.set_widget_update_interval(metric_widget_id, 5000)  # 5 seconds
    
    # Render the dashboard
    dashboard_data = dashboard_component.render_dashboard(dashboard_id)
    
    print(f"Dashboard: {dashboard_data['name']}")
    print(f"Number of widgets: {len(dashboard_data['widgets'])}")
    
    # Update a widget
    dashboard_component.update_widget(
        metric_widget_id,
        data={"value": 26.2, "unit": "°C", "trend": "up"}
    )
    
    # Stop the component
    dashboard_component.stop()
"""
