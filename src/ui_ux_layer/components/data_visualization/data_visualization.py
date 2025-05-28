"""
Data Visualization Component for the Industriverse UI/UX Layer.

This module provides comprehensive data visualization capabilities for industrial data,
enabling intuitive understanding of complex datasets through interactive visualizations.

Author: Manus
"""

import logging
import time
import uuid
import json
from typing import Dict, List, Optional, Any, Callable, Tuple, Set, Union
from enum import Enum
from dataclasses import dataclass, field

class VisualizationType(Enum):
    """Enumeration of visualization types."""
    LINE_CHART = "line_chart"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    SCATTER_PLOT = "scatter_plot"
    HEATMAP = "heatmap"
    GAUGE = "gauge"
    TABLE = "table"
    SANKEY = "sankey"
    NETWORK = "network"
    TREEMAP = "treemap"
    TIMELINE = "timeline"
    GEOGRAPHIC = "geographic"
    CUSTOM = "custom"

class DataSourceType(Enum):
    """Enumeration of data source types."""
    REAL_TIME = "real_time"
    HISTORICAL = "historical"
    PREDICTIVE = "predictive"
    SIMULATION = "simulation"
    STATIC = "static"
    CUSTOM = "custom"

@dataclass
class DataPoint:
    """Data class representing a data point."""
    x: Any
    y: Any
    series: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class DataSeries:
    """Data class representing a data series."""
    series_id: str
    name: str
    data: List[DataPoint]
    color: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class VisualizationConfig:
    """Data class representing visualization configuration."""
    title: str
    type: VisualizationType
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    show_legend: bool = True
    interactive: bool = True
    auto_update: bool = False
    update_interval: Optional[int] = None
    height: Optional[int] = None
    width: Optional[int] = None
    theme: Optional[str] = None
    custom_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Visualization:
    """Data class representing a complete visualization."""
    visualization_id: str
    config: VisualizationConfig
    data_series: List[DataSeries]
    data_source_type: DataSourceType
    data_source_config: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

class DataVisualizationComponent:
    """
    Provides comprehensive data visualization capabilities for the Industriverse UI/UX Layer.
    
    This class provides:
    - Creation and management of various visualization types
    - Real-time data visualization with automatic updates
    - Interactive visualization controls
    - Integration with industrial data sources
    - Customizable visualization themes and styles
    - Integration with the Universal Skin and Capsule Framework
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Data Visualization Component.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.is_active = False
        self.visualizations: Dict[str, Visualization] = {}
        self.visualization_listeners: Dict[str, List[Callable[[Visualization], None]]] = {}
        self.data_update_listeners: Dict[str, List[Callable[[str, List[DataSeries]], None]]] = {}
        self.event_listeners: List[Callable[[Dict[str, Any]], None]] = []
        self.logger = logging.getLogger(__name__)
        self.update_threads: Dict[str, Any] = {}
        
        # Initialize visualization renderers
        self.renderers = {
            VisualizationType.LINE_CHART: self._render_line_chart,
            VisualizationType.BAR_CHART: self._render_bar_chart,
            VisualizationType.PIE_CHART: self._render_pie_chart,
            VisualizationType.SCATTER_PLOT: self._render_scatter_plot,
            VisualizationType.HEATMAP: self._render_heatmap,
            VisualizationType.GAUGE: self._render_gauge,
            VisualizationType.TABLE: self._render_table,
            VisualizationType.SANKEY: self._render_sankey,
            VisualizationType.NETWORK: self._render_network,
            VisualizationType.TREEMAP: self._render_treemap,
            VisualizationType.TIMELINE: self._render_timeline,
            VisualizationType.GEOGRAPHIC: self._render_geographic,
            VisualizationType.CUSTOM: self._render_custom
        }
        
        # Initialize data source handlers
        self.data_source_handlers = {
            DataSourceType.REAL_TIME: self._handle_real_time_data,
            DataSourceType.HISTORICAL: self._handle_historical_data,
            DataSourceType.PREDICTIVE: self._handle_predictive_data,
            DataSourceType.SIMULATION: self._handle_simulation_data,
            DataSourceType.STATIC: self._handle_static_data,
            DataSourceType.CUSTOM: self._handle_custom_data
        }
        
    def start(self) -> bool:
        """
        Start the Data Visualization Component.
        
        Returns:
            True if the component was started, False if already active
        """
        if self.is_active:
            return False
            
        self.is_active = True
        
        # Start auto-updating visualizations
        for visualization_id, visualization in self.visualizations.items():
            if visualization.config.auto_update and visualization.config.update_interval:
                self._start_auto_update(visualization_id)
                
        # Dispatch event
        self._dispatch_event({
            "event_type": "visualization_component_started"
        })
        
        self.logger.info("Data Visualization Component started.")
        return True
    
    def stop(self) -> bool:
        """
        Stop the Data Visualization Component.
        
        Returns:
            True if the component was stopped, False if not active
        """
        if not self.is_active:
            return False
            
        self.is_active = False
        
        # Stop all auto-update threads
        for visualization_id, thread in self.update_threads.items():
            if thread and thread.is_alive():
                # Set a flag to stop the thread
                thread.stop_requested = True
                
        self.update_threads.clear()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "visualization_component_stopped"
        })
        
        self.logger.info("Data Visualization Component stopped.")
        return True
    
    def create_visualization(self,
                           title: str,
                           visualization_type: VisualizationType,
                           data_series: List[DataSeries],
                           data_source_type: DataSourceType,
                           data_source_config: Dict[str, Any],
                           x_axis_label: Optional[str] = None,
                           y_axis_label: Optional[str] = None,
                           show_legend: bool = True,
                           interactive: bool = True,
                           auto_update: bool = False,
                           update_interval: Optional[int] = None,
                           height: Optional[int] = None,
                           width: Optional[int] = None,
                           theme: Optional[str] = None,
                           custom_config: Optional[Dict[str, Any]] = None,
                           metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a new visualization.
        
        Args:
            title: Visualization title
            visualization_type: Type of visualization
            data_series: List of data series
            data_source_type: Type of data source
            data_source_config: Configuration for the data source
            x_axis_label: Optional label for x-axis
            y_axis_label: Optional label for y-axis
            show_legend: Whether to show the legend
            interactive: Whether the visualization is interactive
            auto_update: Whether to automatically update the visualization
            update_interval: Interval in milliseconds for auto-updates
            height: Optional height in pixels
            width: Optional width in pixels
            theme: Optional theme name
            custom_config: Additional configuration options
            metadata: Additional metadata
            
        Returns:
            The visualization ID
        """
        # Generate visualization ID
        visualization_id = str(uuid.uuid4())
        
        # Create visualization config
        config = VisualizationConfig(
            title=title,
            type=visualization_type,
            x_axis_label=x_axis_label,
            y_axis_label=y_axis_label,
            show_legend=show_legend,
            interactive=interactive,
            auto_update=auto_update,
            update_interval=update_interval,
            height=height,
            width=width,
            theme=theme,
            custom_config=custom_config or {}
        )
        
        # Create visualization
        visualization = Visualization(
            visualization_id=visualization_id,
            config=config,
            data_series=data_series,
            data_source_type=data_source_type,
            data_source_config=data_source_config,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        # Store visualization
        self.visualizations[visualization_id] = visualization
        
        # Start auto-update if enabled
        if auto_update and update_interval:
            self._start_auto_update(visualization_id)
            
        # Dispatch event
        self._dispatch_event({
            "event_type": "visualization_created",
            "visualization_id": visualization_id,
            "title": title,
            "type": visualization_type.value,
            "data_source_type": data_source_type.value
        })
        
        self.logger.debug(f"Created visualization: {visualization_id} ({title})")
        return visualization_id
    
    def get_visualization(self, visualization_id: str) -> Optional[Visualization]:
        """
        Get a visualization by ID.
        
        Args:
            visualization_id: ID of the visualization to get
            
        Returns:
            The visualization, or None if not found
        """
        return self.visualizations.get(visualization_id)
    
    def update_visualization_config(self,
                                  visualization_id: str,
                                  title: Optional[str] = None,
                                  visualization_type: Optional[VisualizationType] = None,
                                  x_axis_label: Optional[str] = None,
                                  y_axis_label: Optional[str] = None,
                                  show_legend: Optional[bool] = None,
                                  interactive: Optional[bool] = None,
                                  auto_update: Optional[bool] = None,
                                  update_interval: Optional[int] = None,
                                  height: Optional[int] = None,
                                  width: Optional[int] = None,
                                  theme: Optional[str] = None,
                                  custom_config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Update visualization configuration.
        
        Args:
            visualization_id: ID of the visualization to update
            title: Optional new title
            visualization_type: Optional new visualization type
            x_axis_label: Optional new x-axis label
            y_axis_label: Optional new y-axis label
            show_legend: Optional new show legend setting
            interactive: Optional new interactive setting
            auto_update: Optional new auto-update setting
            update_interval: Optional new update interval
            height: Optional new height
            width: Optional new width
            theme: Optional new theme
            custom_config: Optional new custom configuration
            
        Returns:
            True if the visualization was updated, False if not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        visualization = self.visualizations[visualization_id]
        config = visualization.config
        
        # Update config properties
        if title is not None:
            config.title = title
        if visualization_type is not None:
            config.type = visualization_type
        if x_axis_label is not None:
            config.x_axis_label = x_axis_label
        if y_axis_label is not None:
            config.y_axis_label = y_axis_label
        if show_legend is not None:
            config.show_legend = show_legend
        if interactive is not None:
            config.interactive = interactive
        if height is not None:
            config.height = height
        if width is not None:
            config.width = width
        if theme is not None:
            config.theme = theme
        if custom_config is not None:
            config.custom_config.update(custom_config)
            
        # Handle auto-update changes
        old_auto_update = config.auto_update
        old_update_interval = config.update_interval
        
        if auto_update is not None:
            config.auto_update = auto_update
        if update_interval is not None:
            config.update_interval = update_interval
            
        # Start or stop auto-update if needed
        if (not old_auto_update or not old_update_interval) and config.auto_update and config.update_interval:
            self._start_auto_update(visualization_id)
        elif old_auto_update and (not config.auto_update or not config.update_interval):
            self._stop_auto_update(visualization_id)
            
        # Update timestamp
        visualization.timestamp = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "visualization_config_updated",
            "visualization_id": visualization_id,
            "title": config.title,
            "type": config.type.value
        })
        
        # Notify visualization listeners
        if visualization_id in self.visualization_listeners:
            for listener in self.visualization_listeners[visualization_id]:
                try:
                    listener(visualization)
                except Exception as e:
                    self.logger.error(f"Error in visualization listener for {visualization_id}: {e}")
                    
        self.logger.debug(f"Updated visualization config: {visualization_id} ({config.title})")
        return True
    
    def update_visualization_data(self,
                                visualization_id: str,
                                data_series: List[DataSeries]) -> bool:
        """
        Update visualization data.
        
        Args:
            visualization_id: ID of the visualization to update
            data_series: New data series
            
        Returns:
            True if the visualization was updated, False if not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        visualization = self.visualizations[visualization_id]
        
        # Update data series
        visualization.data_series = data_series
        
        # Update timestamp
        visualization.timestamp = time.time()
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "visualization_data_updated",
            "visualization_id": visualization_id,
            "title": visualization.config.title,
            "type": visualization.config.type.value,
            "series_count": len(data_series)
        })
        
        # Notify visualization listeners
        if visualization_id in self.visualization_listeners:
            for listener in self.visualization_listeners[visualization_id]:
                try:
                    listener(visualization)
                except Exception as e:
                    self.logger.error(f"Error in visualization listener for {visualization_id}: {e}")
                    
        # Notify data update listeners
        if visualization_id in self.data_update_listeners:
            for listener in self.data_update_listeners[visualization_id]:
                try:
                    listener(visualization_id, data_series)
                except Exception as e:
                    self.logger.error(f"Error in data update listener for {visualization_id}: {e}")
                    
        self.logger.debug(f"Updated visualization data: {visualization_id} ({visualization.config.title})")
        return True
    
    def delete_visualization(self, visualization_id: str) -> bool:
        """
        Delete a visualization.
        
        Args:
            visualization_id: ID of the visualization to delete
            
        Returns:
            True if the visualization was deleted, False if not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        visualization = self.visualizations[visualization_id]
        
        # Stop auto-update if enabled
        self._stop_auto_update(visualization_id)
        
        # Remove visualization
        del self.visualizations[visualization_id]
        
        # Dispatch event
        self._dispatch_event({
            "event_type": "visualization_deleted",
            "visualization_id": visualization_id,
            "title": visualization.config.title,
            "type": visualization.config.type.value
        })
        
        self.logger.debug(f"Deleted visualization: {visualization_id} ({visualization.config.title})")
        return True
    
    def render_visualization(self, visualization_id: str) -> Dict[str, Any]:
        """
        Render a visualization.
        
        Args:
            visualization_id: ID of the visualization to render
            
        Returns:
            Rendered visualization data
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return {"error": "Visualization not found"}
            
        visualization = self.visualizations[visualization_id]
        
        # Get the appropriate renderer
        renderer = self.renderers.get(visualization.config.type)
        if not renderer:
            self.logger.warning(f"No renderer found for visualization type {visualization.config.type.value}.")
            return {"error": f"No renderer found for visualization type {visualization.config.type.value}"}
            
        # Render the visualization
        try:
            rendered_data = renderer(visualization)
            
            # Add common properties
            rendered_data.update({
                "visualization_id": visualization_id,
                "title": visualization.config.title,
                "type": visualization.config.type.value,
                "timestamp": visualization.timestamp,
                "config": {
                    "x_axis_label": visualization.config.x_axis_label,
                    "y_axis_label": visualization.config.y_axis_label,
                    "show_legend": visualization.config.show_legend,
                    "interactive": visualization.config.interactive,
                    "height": visualization.config.height,
                    "width": visualization.config.width,
                    "theme": visualization.config.theme
                }
            })
            
            return rendered_data
            
        except Exception as e:
            self.logger.error(f"Error rendering visualization {visualization_id}: {e}")
            return {"error": f"Error rendering visualization: {str(e)}"}
    
    def add_visualization_listener(self, visualization_id: str, listener: Callable[[Visualization], None]) -> bool:
        """
        Add a listener for a specific visualization.
        
        Args:
            visualization_id: ID of the visualization
            listener: Callback function that will be called when the visualization is updated
            
        Returns:
            True if the listener was added, False if visualization not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if visualization_id not in self.visualization_listeners:
            self.visualization_listeners[visualization_id] = []
            
        self.visualization_listeners[visualization_id].append(listener)
        return True
    
    def add_data_update_listener(self, visualization_id: str, listener: Callable[[str, List[DataSeries]], None]) -> bool:
        """
        Add a listener for data updates to a specific visualization.
        
        Args:
            visualization_id: ID of the visualization
            listener: Callback function that will be called when the visualization data is updated
            
        Returns:
            True if the listener was added, False if visualization not found
        """
        if visualization_id not in self.visualizations:
            self.logger.warning(f"Visualization {visualization_id} not found.")
            return False
            
        if visualization_id not in self.data_update_listeners:
            self.data_update_listeners[visualization_id] = []
            
        self.data_update_listeners[visualization_id].append(listener)
        return True
    
    def add_event_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        """
        Add a listener for all visualization component events.
        
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
            event_data["source"] = "DataVisualizationComponent"
            
        # Add timestamp if not present
        if "timestamp" not in event_data:
            event_data["timestamp"] = time.time()
            
        # Dispatch to global event listeners
        for listener in self.event_listeners:
            try:
                listener(event_data)
            except Exception as e:
                self.logger.error(f"Error in visualization event listener: {e}")
                
    def _start_auto_update(self, visualization_id: str) -> None:
        """
        Start auto-updating a visualization.
        
        Args:
            visualization_id: ID of the visualization to auto-update
        """
        if visualization_id not in self.visualizations:
            return
            
        # Stop existing thread if any
        self._stop_auto_update(visualization_id)
        
        visualization = self.visualizations[visualization_id]
        
        if not visualization.config.auto_update or not visualization.config.update_interval:
            return
            
        # Create and start update thread
        import threading
        
        def update_thread():
            thread = threading.current_thread()
            thread.stop_requested = False
            
            while not thread.stop_requested and self.is_active:
                try:
                    # Get data from the appropriate data source handler
                    handler = self.data_source_handlers.get(visualization.data_source_type)
                    if handler:
                        data_series = handler(visualization)
                        if data_series:
                            self.update_visualization_data(visualization_id, data_series)
                            
                except Exception as e:
                    self.logger.error(f"Error in auto-update thread for visualization {visualization_id}: {e}")
                    
                # Sleep for the update interval
                interval_seconds = visualization.config.update_interval / 1000.0
                time.sleep(interval_seconds)
                
        thread = threading.Thread(target=update_thread)
        thread.daemon = True
        thread.start()
        
        self.update_threads[visualization_id] = thread
        
        self.logger.debug(f"Started auto-update for visualization: {visualization_id}")
    
    def _stop_auto_update(self, visualization_id: str) -> None:
        """
        Stop auto-updating a visualization.
        
        Args:
            visualization_id: ID of the visualization to stop auto-updating
        """
        if visualization_id in self.update_threads:
            thread = self.update_threads[visualization_id]
            if thread and thread.is_alive():
                # Set a flag to stop the thread
                thread.stop_requested = True
                
            del self.update_threads[visualization_id]
            
            self.logger.debug(f"Stopped auto-update for visualization: {visualization_id}")
    
    # Renderer methods
    
    def _render_line_chart(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a line chart visualization."""
        series_data = []
        
        for series in visualization.data_series:
            data_points = []
            for point in series.data:
                data_points.append({
                    "x": point.x,
                    "y": point.y,
                    "metadata": point.metadata
                })
                
            series_data.append({
                "id": series.series_id,
                "name": series.name,
                "color": series.color,
                "data": data_points,
                "metadata": series.metadata
            })
            
        return {
            "chart_type": "line",
            "series": series_data
        }
    
    def _render_bar_chart(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a bar chart visualization."""
        series_data = []
        
        for series in visualization.data_series:
            data_points = []
            for point in series.data:
                data_points.append({
                    "x": point.x,
                    "y": point.y,
                    "metadata": point.metadata
                })
                
            series_data.append({
                "id": series.series_id,
                "name": series.name,
                "color": series.color,
                "data": data_points,
                "metadata": series.metadata
            })
            
        return {
            "chart_type": "bar",
            "series": series_data
        }
    
    def _render_pie_chart(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a pie chart visualization."""
        data_points = []
        
        # For pie charts, we typically use a single series
        if visualization.data_series:
            series = visualization.data_series[0]
            
            for point in series.data:
                data_points.append({
                    "name": point.x,
                    "value": point.y,
                    "color": point.metadata.get("color"),
                    "metadata": point.metadata
                })
                
        return {
            "chart_type": "pie",
            "data": data_points
        }
    
    def _render_scatter_plot(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a scatter plot visualization."""
        series_data = []
        
        for series in visualization.data_series:
            data_points = []
            for point in series.data:
                data_points.append({
                    "x": point.x,
                    "y": point.y,
                    "size": point.metadata.get("size", 5),
                    "color": point.metadata.get("color"),
                    "metadata": point.metadata
                })
                
            series_data.append({
                "id": series.series_id,
                "name": series.name,
                "color": series.color,
                "data": data_points,
                "metadata": series.metadata
            })
            
        return {
            "chart_type": "scatter",
            "series": series_data
        }
    
    def _render_heatmap(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a heatmap visualization."""
        # For heatmaps, we need to transform the data into a matrix
        x_values = set()
        y_values = set()
        value_map = {}
        
        for series in visualization.data_series:
            for point in series.data:
                x_values.add(point.x)
                y_values.add(point.y)
                value_map[(point.x, point.y)] = point.metadata.get("value", 0)
                
        x_values = sorted(list(x_values))
        y_values = sorted(list(y_values))
        
        data = []
        for y in y_values:
            row = []
            for x in x_values:
                row.append(value_map.get((x, y), 0))
            data.append(row)
            
        return {
            "chart_type": "heatmap",
            "x_labels": x_values,
            "y_labels": y_values,
            "data": data
        }
    
    def _render_gauge(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a gauge visualization."""
        # For gauges, we typically use a single value
        value = 0
        min_value = 0
        max_value = 100
        thresholds = []
        
        if visualization.data_series and visualization.data_series[0].data:
            point = visualization.data_series[0].data[0]
            value = point.y
            min_value = point.metadata.get("min", 0)
            max_value = point.metadata.get("max", 100)
            thresholds = point.metadata.get("thresholds", [])
            
        return {
            "chart_type": "gauge",
            "value": value,
            "min": min_value,
            "max": max_value,
            "thresholds": thresholds
        }
    
    def _render_table(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a table visualization."""
        columns = []
        rows = []
        
        # Extract column definitions from custom config
        columns = visualization.config.custom_config.get("columns", [])
        
        # Extract rows from data series
        for series in visualization.data_series:
            for point in series.data:
                row = {
                    "id": point.metadata.get("id", str(uuid.uuid4())),
                    "values": {}
                }
                
                # Add x and y values
                row["values"]["x"] = point.x
                row["values"]["y"] = point.y
                
                # Add metadata values
                for key, value in point.metadata.items():
                    if key != "id":
                        row["values"][key] = value
                        
                rows.append(row)
                
        return {
            "chart_type": "table",
            "columns": columns,
            "rows": rows
        }
    
    def _render_sankey(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a Sankey diagram visualization."""
        nodes = []
        links = []
        
        # Extract nodes and links from data series
        for series in visualization.data_series:
            # For Sankey diagrams, each series represents a set of links
            for point in series.data:
                # Each point represents a link from x to y with value in metadata
                source = point.x
                target = point.y
                value = point.metadata.get("value", 1)
                
                # Ensure nodes exist
                if source not in [node["id"] for node in nodes]:
                    nodes.append({
                        "id": source,
                        "name": point.metadata.get("source_name", source),
                        "color": point.metadata.get("source_color")
                    })
                    
                if target not in [node["id"] for node in nodes]:
                    nodes.append({
                        "id": target,
                        "name": point.metadata.get("target_name", target),
                        "color": point.metadata.get("target_color")
                    })
                    
                # Add link
                links.append({
                    "source": source,
                    "target": target,
                    "value": value,
                    "color": point.metadata.get("link_color")
                })
                
        return {
            "chart_type": "sankey",
            "nodes": nodes,
            "links": links
        }
    
    def _render_network(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a network visualization."""
        nodes = []
        edges = []
        
        # Extract nodes and edges from data series
        for series in visualization.data_series:
            # For network diagrams, each series can represent nodes or edges
            if series.metadata.get("type") == "nodes":
                # Each point represents a node
                for point in series.data:
                    nodes.append({
                        "id": point.x,
                        "name": point.metadata.get("name", point.x),
                        "group": point.y,
                        "size": point.metadata.get("size", 5),
                        "color": point.metadata.get("color"),
                        "metadata": point.metadata
                    })
            elif series.metadata.get("type") == "edges":
                # Each point represents an edge
                for point in series.data:
                    edges.append({
                        "source": point.x,
                        "target": point.y,
                        "value": point.metadata.get("value", 1),
                        "color": point.metadata.get("color"),
                        "metadata": point.metadata
                    })
                    
        return {
            "chart_type": "network",
            "nodes": nodes,
            "edges": edges
        }
    
    def _render_treemap(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a treemap visualization."""
        # For treemaps, we need to build a hierarchical structure
        root = {
            "name": visualization.config.title,
            "children": []
        }
        
        # Extract data from series
        for series in visualization.data_series:
            # Each series represents a branch in the tree
            branch = {
                "name": series.name,
                "children": []
            }
            
            # Each point represents a leaf
            for point in series.data:
                leaf = {
                    "name": point.x,
                    "value": point.y,
                    "color": point.metadata.get("color"),
                    "metadata": point.metadata
                }
                
                branch["children"].append(leaf)
                
            root["children"].append(branch)
            
        return {
            "chart_type": "treemap",
            "data": root
        }
    
    def _render_timeline(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a timeline visualization."""
        events = []
        
        # Extract events from data series
        for series in visualization.data_series:
            # Each point represents an event
            for point in series.data:
                event = {
                    "id": point.metadata.get("id", str(uuid.uuid4())),
                    "title": point.x,
                    "start": point.y,
                    "end": point.metadata.get("end"),
                    "group": series.name,
                    "color": point.metadata.get("color", series.color),
                    "metadata": point.metadata
                }
                
                events.append(event)
                
        return {
            "chart_type": "timeline",
            "events": events
        }
    
    def _render_geographic(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a geographic visualization."""
        features = []
        
        # Extract features from data series
        for series in visualization.data_series:
            # Each point represents a geographic feature
            for point in series.data:
                feature = {
                    "id": point.metadata.get("id", str(uuid.uuid4())),
                    "type": point.metadata.get("type", "point"),
                    "coordinates": [point.x, point.y],
                    "properties": {
                        "name": point.metadata.get("name", ""),
                        "value": point.metadata.get("value", 0),
                        "color": point.metadata.get("color"),
                        "radius": point.metadata.get("radius", 5),
                        "metadata": point.metadata
                    }
                }
                
                features.append(feature)
                
        return {
            "chart_type": "geographic",
            "features": features,
            "center": visualization.config.custom_config.get("center", [0, 0]),
            "zoom": visualization.config.custom_config.get("zoom", 2)
        }
    
    def _render_custom(self, visualization: Visualization) -> Dict[str, Any]:
        """Render a custom visualization."""
        # For custom visualizations, we just pass through the data
        return {
            "chart_type": "custom",
            "data": [
                {
                    "id": series.series_id,
                    "name": series.name,
                    "color": series.color,
                    "data": [
                        {
                            "x": point.x,
                            "y": point.y,
                            "metadata": point.metadata
                        } for point in series.data
                    ],
                    "metadata": series.metadata
                } for series in visualization.data_series
            ],
            "custom_config": visualization.config.custom_config
        }
    
    # Data source handler methods
    
    def _handle_real_time_data(self, visualization: Visualization) -> List[DataSeries]:
        """Handle real-time data source."""
        # In a real implementation, this would connect to a real-time data source
        # For now, we'll just return the existing data
        return visualization.data_series
    
    def _handle_historical_data(self, visualization: Visualization) -> List[DataSeries]:
        """Handle historical data source."""
        # In a real implementation, this would fetch historical data
        # For now, we'll just return the existing data
        return visualization.data_series
    
    def _handle_predictive_data(self, visualization: Visualization) -> List[DataSeries]:
        """Handle predictive data source."""
        # In a real implementation, this would generate predictive data
        # For now, we'll just return the existing data
        return visualization.data_series
    
    def _handle_simulation_data(self, visualization: Visualization) -> List[DataSeries]:
        """Handle simulation data source."""
        # In a real implementation, this would run a simulation
        # For now, we'll just return the existing data
        return visualization.data_series
    
    def _handle_static_data(self, visualization: Visualization) -> List[DataSeries]:
        """Handle static data source."""
        # Static data doesn't change, so just return the existing data
        return visualization.data_series
    
    def _handle_custom_data(self, visualization: Visualization) -> List[DataSeries]:
        """Handle custom data source."""
        # In a real implementation, this would handle custom data sources
        # For now, we'll just return the existing data
        return visualization.data_series

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create data visualization component
    visualization_component = DataVisualizationComponent()
    
    # Start the component
    visualization_component.start()
    
    # Add an event listener
    def on_event(event):
        print(f"Event: {event['event_type']}")
        
    visualization_component.add_event_listener(on_event)
    
    # Create a line chart visualization
    line_chart_id = visualization_component.create_visualization(
        title="Temperature Over Time",
        visualization_type=VisualizationType.LINE_CHART,
        data_series=[
            DataSeries(
                series_id="temp",
                name="Temperature",
                color="#FF0000",
                data=[
                    DataPoint(x="2023-01-01", y=22.5),
                    DataPoint(x="2023-01-02", y=23.1),
                    DataPoint(x="2023-01-03", y=22.8),
                    DataPoint(x="2023-01-04", y=24.2),
                    DataPoint(x="2023-01-05", y=25.0)
                ]
            )
        ],
        data_source_type=DataSourceType.STATIC,
        data_source_config={},
        x_axis_label="Date",
        y_axis_label="Temperature (°C)",
        show_legend=True,
        interactive=True
    )
    
    # Create a bar chart visualization
    bar_chart_id = visualization_component.create_visualization(
        title="Production by Department",
        visualization_type=VisualizationType.BAR_CHART,
        data_series=[
            DataSeries(
                series_id="production",
                name="Production",
                color="#0000FF",
                data=[
                    DataPoint(x="Dept A", y=120),
                    DataPoint(x="Dept B", y=150),
                    DataPoint(x="Dept C", y=90),
                    DataPoint(x="Dept D", y=180),
                    DataPoint(x="Dept E", y=110)
                ]
            )
        ],
        data_source_type=DataSourceType.STATIC,
        data_source_config={},
        x_axis_label="Department",
        y_axis_label="Units Produced",
        show_legend=True,
        interactive=True
    )
    
    # Render the visualizations
    line_chart_data = visualization_component.render_visualization(line_chart_id)
    bar_chart_data = visualization_component.render_visualization(bar_chart_id)
    
    print(f"Line Chart: {line_chart_data['title']}")
    print(f"Bar Chart: {bar_chart_data['title']}")
    
    # Update visualization data
    visualization_component.update_visualization_data(
        line_chart_id,
        [
            DataSeries(
                series_id="temp",
                name="Temperature",
                color="#FF0000",
                data=[
                    DataPoint(x="2023-01-01", y=22.5),
                    DataPoint(x="2023-01-02", y=23.1),
                    DataPoint(x="2023-01-03", y=22.8),
                    DataPoint(x="2023-01-04", y=24.2),
                    DataPoint(x="2023-01-05", y=25.0),
                    DataPoint(x="2023-01-06", y=24.8)
                ]
            )
        ]
    )
    
    # Stop the component
    visualization_component.stop()
"""
