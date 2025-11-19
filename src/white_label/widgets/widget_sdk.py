"""
Widget SDK - Base infrastructure for embeddable components

Provides:
- Base widget class with lifecycle hooks
- Theme system integration with design tokens
- Configuration management
- Event handling and data binding
- Widget registry for discovery
"""

import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod
import asyncio


@dataclass
class WidgetTheme:
    """Theme configuration from design tokens"""
    name: str
    colors: Dict[str, Any]
    typography: Dict[str, Any]
    spacing: Dict[str, Any]
    motion: Dict[str, Any]
    shadows: Dict[str, Any]
    borders: Dict[str, Any]
    gradients: Optional[Dict[str, Any]] = None


@dataclass
class WidgetConfig:
    """Widget configuration"""
    widget_id: str
    partner_id: str
    theme: str = "cosmic"
    data_refresh_interval: int = 5000  # milliseconds
    enable_animations: bool = True
    enable_websocket: bool = True
    custom_colors: Optional[Dict[str, str]] = None
    custom_branding: Optional[Dict[str, str]] = None
    features: Dict[str, bool] = field(default_factory=dict)
    api_endpoint: str = "https://api.industriverse.ai"
    api_key: Optional[str] = None


class WidgetBase(ABC):
    """
    Base class for all white-label widgets

    Lifecycle:
    1. __init__() - Initialize widget
    2. on_mount() - Called when widget is added to DOM
    3. on_data_update() - Called when new data arrives
    4. on_theme_change() - Called when theme changes
    5. on_unmount() - Called when widget is removed
    """

    def __init__(self, config: WidgetConfig):
        self.config = config
        self.theme = self._load_theme(config.theme)
        self._apply_custom_colors()
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._data_cache: Dict[str, Any] = {}
        self._mounted = False
        self._websocket_connection = None

    def _load_theme(self, theme_name: str) -> WidgetTheme:
        """Load theme from design tokens"""
        tokens_path = Path(__file__).parent.parent / "design_tokens.json"

        with open(tokens_path, 'r') as f:
            tokens = json.load(f)

        theme_data = tokens['themes'].get(theme_name, tokens['themes']['cosmic'])

        return WidgetTheme(
            name=theme_name,
            colors=theme_data.get('colors', {}),
            typography=theme_data.get('typography', {}),
            spacing=theme_data.get('spacing', {}),
            motion=theme_data.get('motion', {}),
            shadows=theme_data.get('shadows', {}),
            borders=theme_data.get('borders', {}),
            gradients=theme_data.get('gradients', {})
        )

    def _apply_custom_colors(self):
        """Apply partner-specific color overrides"""
        if self.config.custom_colors:
            for key, value in self.config.custom_colors.items():
                if self._is_allowed_override(key):
                    self._set_nested_value(self.theme.colors, key, value)

    def _is_allowed_override(self, key: str) -> bool:
        """Check if color override is allowed per design tokens"""
        # Load allowed overrides from design tokens
        tokens_path = Path(__file__).parent.parent / "design_tokens.json"
        with open(tokens_path, 'r') as f:
            tokens = json.load(f)

        allowed = tokens.get('partner_customization', {}).get('allowed_overrides', [])
        return any(key.startswith(pattern.replace('*', '')) for pattern in allowed)

    def _set_nested_value(self, obj: Dict, key: str, value: Any):
        """Set nested dictionary value from dot notation"""
        keys = key.split('.')
        for k in keys[:-1]:
            obj = obj.setdefault(k, {})
        obj[keys[-1]] = value

    # Lifecycle hooks

    async def on_mount(self):
        """Called when widget is mounted to DOM"""
        self._mounted = True

        if self.config.enable_websocket:
            await self._connect_websocket()

        # Start data refresh loop
        if self.config.data_refresh_interval > 0:
            asyncio.create_task(self._refresh_loop())

    async def on_unmount(self):
        """Called when widget is removed from DOM"""
        self._mounted = False

        if self._websocket_connection:
            await self._websocket_connection.close()

    @abstractmethod
    async def on_data_update(self, data: Dict[str, Any]):
        """Called when new data arrives - implement in subclass"""
        pass

    async def on_theme_change(self, theme_name: str):
        """Called when theme changes"""
        self.theme = self._load_theme(theme_name)
        self._apply_custom_colors()
        await self.render()

    # Data management

    async def fetch_data(self) -> Dict[str, Any]:
        """Fetch widget data from API - implement in subclass"""
        return {}

    async def _refresh_loop(self):
        """Background data refresh loop"""
        while self._mounted:
            try:
                data = await self.fetch_data()
                self._data_cache.update(data)
                await self.on_data_update(data)
            except Exception as e:
                self.emit('error', {'message': str(e)})

            await asyncio.sleep(self.config.data_refresh_interval / 1000)

    async def _connect_websocket(self):
        """Connect to WebSocket for real-time updates"""
        # WebSocket connection logic - implement based on backend
        pass

    # Event handling

    def on(self, event: str, handler: Callable):
        """Register event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def emit(self, event: str, data: Any):
        """Emit event to registered handlers"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                handler(data)

    # Rendering

    @abstractmethod
    async def render(self) -> str:
        """
        Render widget HTML/CSS/JS - implement in subclass

        Returns:
            HTML string with embedded styles and scripts
        """
        pass

    def get_css_variables(self) -> str:
        """Generate CSS variables from theme"""
        colors = self.theme.colors
        typography = self.theme.typography
        spacing = self.theme.spacing

        css_vars = [
            f"--widget-primary: {colors.get('primary', {}).get('value', '#0A4B5C')};",
            f"--widget-accent: {colors.get('accent', {}).get('value', '#FF6B35')};",
            f"--widget-background: {colors.get('background', {}).get('value', '#0D1117')};",
            f"--widget-surface: {colors.get('surface', {}).get('value', '#161B22')};",
            f"--widget-text-primary: {colors.get('text', {}).get('primary', '#E6EDF3')};",
            f"--widget-text-secondary: {colors.get('text', {}).get('secondary', '#8B949E')};",
            f"--widget-spacing-sm: {spacing.get('sm', '0.5rem')};",
            f"--widget-spacing-md: {spacing.get('md', '1rem')};",
            f"--widget-spacing-lg: {spacing.get('lg', '1.5rem')};",
        ]

        return '\n'.join(css_vars)

    def get_embed_code(self) -> str:
        """Generate embed code for partners"""
        return f"""
<!-- Industriverse Widget: {self.__class__.__name__} -->
<div id="industriverse-widget-{self.config.widget_id}"></div>
<script src="{self.config.api_endpoint}/widgets/sdk.js"></script>
<script>
  Industriverse.Widget.mount({{
    widgetId: '{self.config.widget_id}',
    partnerId: '{self.config.partner_id}',
    theme: '{self.config.theme}',
    apiKey: '{self.config.api_key or "YOUR_API_KEY"}',
    target: '#industriverse-widget-{self.config.widget_id}'
  }});
</script>
"""


class WidgetRegistry:
    """Registry for widget discovery and instantiation"""

    def __init__(self):
        self._widgets: Dict[str, type] = {}

    def register(self, name: str, widget_class: type):
        """Register a widget class"""
        self._widgets[name] = widget_class

    def get(self, name: str) -> Optional[type]:
        """Get widget class by name"""
        return self._widgets.get(name)

    def list_widgets(self) -> List[str]:
        """List all registered widget names"""
        return list(self._widgets.keys())

    def create_widget(self, name: str, config: WidgetConfig) -> Optional[WidgetBase]:
        """Instantiate a widget by name"""
        widget_class = self.get(name)
        if widget_class:
            return widget_class(config)
        return None


# Global registry instance
_registry = WidgetRegistry()


def get_widget_registry() -> WidgetRegistry:
    """Get global widget registry"""
    return _registry
