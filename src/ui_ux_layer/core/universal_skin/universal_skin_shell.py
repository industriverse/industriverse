"""
Universal Skin Shell - The Adaptive Container for Industriverse UI/UX Layer

The Universal Skin Shell is the top-level container that adapts to different devices, 
contexts, and user roles. It serves as the living membrane between humans and AI,
revealing intelligence gracefully across devices, contexts, and industries.

This module implements the core shell functionality that adapts based on:
1. Device type and capabilities
2. User role and permissions
3. Context and workflow state
4. Trust and confidence levels
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable

# Initialize logger
logger = logging.getLogger(__name__)

class UniversalSkinShell:
    """
    The Universal Skin Shell is the top-level container that adapts to different devices, 
    contexts, and user roles.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Universal Skin Shell with optional configuration."""
        self.config = config or {}
        self.device_adapter = None
        self.role_view_manager = None
        self.global_navigation = None
        self.ambient_indicators = None
        self.state_manager = None
        self.transition_manager = None
        self.event_handler = None
        self.registered_components = {}
        self.active_capsules = []
        self.active_avatars = []
        self.theme_context = {}
        self.trust_context = {}
        self.event_subscribers = {}
        
        logger.info("Universal Skin Shell initialized with config: %s", self.config)
    
    def initialize(self):
        """Initialize the shell and all its components."""
        logger.info("Initializing Universal Skin Shell components")
        
        # Import dependencies here to avoid circular imports
        from .device_adapter import DeviceAdapter
        from .role_view_manager import RoleViewManager
        from .global_navigation import GlobalNavigation
        from .ambient_indicators import AmbientIndicators
        from .shell_state_manager import ShellStateManager
        from .view_transition_manager import ViewTransitionManager
        from .shell_event_handler import ShellEventHandler
        
        # Initialize components
        self.device_adapter = DeviceAdapter(self.config.get('device_adapter', {}))
        self.role_view_manager = RoleViewManager(self.config.get('role_view_manager', {}))
        self.global_navigation = GlobalNavigation(self.config.get('global_navigation', {}))
        self.ambient_indicators = AmbientIndicators(self.config.get('ambient_indicators', {}))
        self.state_manager = ShellStateManager(self.config.get('state_manager', {}))
        self.transition_manager = ViewTransitionManager(self.config.get('transition_manager', {}))
        self.event_handler = ShellEventHandler(self.config.get('event_handler', {}))
        
        # Initialize each component
        self.device_adapter.initialize()
        self.role_view_manager.initialize()
        self.global_navigation.initialize()
        self.ambient_indicators.initialize()
        self.state_manager.initialize()
        self.transition_manager.initialize()
        self.event_handler.initialize()
        
        # Register event handlers
        self._register_event_handlers()
        
        logger.info("Universal Skin Shell initialization complete")
        return True
    
    def _register_event_handlers(self):
        """Register internal event handlers."""
        self.event_handler.register_handler('device_change', self.adapt_to_device)
        self.event_handler.register_handler('role_change', self.switch_to_role_view)
        self.event_handler.register_handler('capsule_added', self._handle_capsule_added)
        self.event_handler.register_handler('capsule_removed', self._handle_capsule_removed)
        self.event_handler.register_handler('avatar_added', self._handle_avatar_added)
        self.event_handler.register_handler('avatar_removed', self._handle_avatar_removed)
        self.event_handler.register_handler('trust_change', self._handle_trust_change)
        self.event_handler.register_handler('theme_change', self._handle_theme_change)
    
    def adapt_to_device(self, device_info: Dict[str, Any]):
        """Adapt the shell to the current device."""
        logger.info("Adapting Universal Skin Shell to device: %s", device_info)
        
        # Update device context
        self.state_manager.update_context('device', device_info)
        
        # Apply device-specific adaptations
        self.device_adapter.adapt(device_info)
        
        # Update layout and components
        layout_config = self.device_adapter.get_layout_config(device_info)
        self._apply_layout_config(layout_config)
        
        # Notify components of device change
        self._notify_components('device_changed', device_info)
        
        logger.info("Device adaptation complete")
        return True
    
    def _apply_layout_config(self, layout_config: Dict[str, Any]):
        """Apply layout configuration to the shell."""
        logger.debug("Applying layout config: %s", layout_config)
        
        # Apply layout to registered components
        for component_id, component_config in layout_config.get('components', {}).items():
            if component_id in self.registered_components:
                component = self.registered_components[component_id]
                if hasattr(component, 'apply_layout'):
                    component.apply_layout(component_config)
        
        # Apply global layout properties
        self.transition_manager.set_transition_style(layout_config.get('transition_style', 'fade'))
        
        # Apply ambient indicator settings
        self.ambient_indicators.configure(layout_config.get('ambient_indicators', {}))
    
    def switch_to_role_view(self, role: str):
        """Switch to the specified role view."""
        logger.info("Switching to role view: %s", role)
        
        # Get role view configuration
        role_config = self.role_view_manager.get_role_config(role)
        
        # Update role context
        self.state_manager.update_context('role', {'current_role': role, 'config': role_config})
        
        # Apply role-specific navigation
        self.global_navigation.switch_to_role(role, role_config.get('navigation', {}))
        
        # Apply role-specific layout
        self._apply_layout_config(role_config.get('layout', {}))
        
        # Apply role-specific ambient indicators
        self.ambient_indicators.configure(role_config.get('ambient_indicators', {}))
        
        # Notify components of role change
        self._notify_components('role_changed', {'role': role, 'config': role_config})
        
        logger.info("Role view switch complete")
        return True
    
    def register_component(self, component_id: str, component: Any):
        """Register a component with the shell."""
        logger.info("Registering component: %s", component_id)
        
        self.registered_components[component_id] = component
        
        # Apply current context to the component
        if hasattr(component, 'apply_context'):
            current_context = self.state_manager.get_full_context()
            component.apply_context(current_context)
        
        logger.info("Component registered: %s", component_id)
        return True
    
    def unregister_component(self, component_id: str):
        """Unregister a component from the shell."""
        logger.info("Unregistering component: %s", component_id)
        
        if component_id in self.registered_components:
            del self.registered_components[component_id]
            logger.info("Component unregistered: %s", component_id)
            return True
        
        logger.warning("Component not found for unregistration: %s", component_id)
        return False
    
    def register_ambient_indicator(self, indicator: Dict[str, Any]):
        """Register a new ambient indicator."""
        logger.info("Registering ambient indicator: %s", indicator.get('id'))
        
        return self.ambient_indicators.register_indicator(indicator)
    
    def handle_event(self, event: Dict[str, Any]):
        """Handle an incoming event."""
        logger.debug("Handling event: %s", event)
        
        # Update state based on event
        self.state_manager.process_event(event)
        
        # Let event handler process the event
        self.event_handler.handle_event(event)
        
        # Notify subscribers
        event_type = event.get('type')
        if event_type in self.event_subscribers:
            for subscriber in self.event_subscribers[event_type]:
                subscriber(event)
        
        return True
    
    def subscribe_to_event(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Subscribe to events of a specific type."""
        logger.debug("Subscribing to event type: %s", event_type)
        
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        
        self.event_subscribers[event_type].append(callback)
        return True
    
    def unsubscribe_from_event(self, event_type: str, callback: Callable[[Dict[str, Any]], None]):
        """Unsubscribe from events of a specific type."""
        logger.debug("Unsubscribing from event type: %s", event_type)
        
        if event_type in self.event_subscribers and callback in self.event_subscribers[event_type]:
            self.event_subscribers[event_type].remove(callback)
            return True
        
        return False
    
    def _notify_components(self, event_type: str, data: Dict[str, Any]):
        """Notify all registered components of an event."""
        logger.debug("Notifying components of event: %s", event_type)
        
        event = {'type': event_type, 'data': data}
        
        for component_id, component in self.registered_components.items():
            if hasattr(component, 'handle_event'):
                component.handle_event(event)
    
    def _handle_capsule_added(self, event: Dict[str, Any]):
        """Handle capsule added event."""
        capsule_id = event.get('data', {}).get('capsule_id')
        logger.info("Handling capsule added: %s", capsule_id)
        
        if capsule_id and capsule_id not in self.active_capsules:
            self.active_capsules.append(capsule_id)
    
    def _handle_capsule_removed(self, event: Dict[str, Any]):
        """Handle capsule removed event."""
        capsule_id = event.get('data', {}).get('capsule_id')
        logger.info("Handling capsule removed: %s", capsule_id)
        
        if capsule_id and capsule_id in self.active_capsules:
            self.active_capsules.remove(capsule_id)
    
    def _handle_avatar_added(self, event: Dict[str, Any]):
        """Handle avatar added event."""
        avatar_id = event.get('data', {}).get('avatar_id')
        logger.info("Handling avatar added: %s", avatar_id)
        
        if avatar_id and avatar_id not in self.active_avatars:
            self.active_avatars.append(avatar_id)
    
    def _handle_avatar_removed(self, event: Dict[str, Any]):
        """Handle avatar removed event."""
        avatar_id = event.get('data', {}).get('avatar_id')
        logger.info("Handling avatar removed: %s", avatar_id)
        
        if avatar_id and avatar_id in self.active_avatars:
            self.active_avatars.remove(avatar_id)
    
    def _handle_trust_change(self, event: Dict[str, Any]):
        """Handle trust change event."""
        trust_data = event.get('data', {})
        logger.info("Handling trust change: %s", trust_data)
        
        # Update trust context
        self.trust_context.update(trust_data)
        
        # Apply trust-based adaptations
        self._apply_trust_adaptations(trust_data)
    
    def _apply_trust_adaptations(self, trust_data: Dict[str, Any]):
        """Apply adaptations based on trust data."""
        logger.debug("Applying trust adaptations: %s", trust_data)
        
        # Adjust ambient indicators based on trust
        self.ambient_indicators.update_trust_indicators(trust_data)
        
        # Notify components of trust change
        self._notify_components('trust_changed', trust_data)
    
    def _handle_theme_change(self, event: Dict[str, Any]):
        """Handle theme change event."""
        theme_data = event.get('data', {})
        logger.info("Handling theme change: %s", theme_data)
        
        # Update theme context
        self.theme_context.update(theme_data)
        
        # Apply theme adaptations
        self._apply_theme_adaptations(theme_data)
    
    def _apply_theme_adaptations(self, theme_data: Dict[str, Any]):
        """Apply adaptations based on theme data."""
        logger.debug("Applying theme adaptations: %s", theme_data)
        
        # Notify components of theme change
        self._notify_components('theme_changed', theme_data)
    
    def get_active_capsules(self) -> List[str]:
        """Get list of active capsule IDs."""
        return self.active_capsules.copy()
    
    def get_active_avatars(self) -> List[str]:
        """Get list of active avatar IDs."""
        return self.active_avatars.copy()
    
    def get_current_context(self) -> Dict[str, Any]:
        """Get the current context of the shell."""
        return self.state_manager.get_full_context()
    
    def get_component(self, component_id: str) -> Any:
        """Get a registered component by ID."""
        return self.registered_components.get(component_id)
    
    def to_json(self) -> str:
        """Serialize the shell state to JSON."""
        state = {
            'active_capsules': self.active_capsules,
            'active_avatars': self.active_avatars,
            'trust_context': self.trust_context,
            'theme_context': self.theme_context,
            'context': self.state_manager.get_full_context() if self.state_manager else {},
        }
        
        return json.dumps(state)
    
    def from_json(self, json_str: str) -> bool:
        """Deserialize the shell state from JSON."""
        try:
            state = json.loads(json_str)
            
            self.active_capsules = state.get('active_capsules', [])
            self.active_avatars = state.get('active_avatars', [])
            self.trust_context = state.get('trust_context', {})
            self.theme_context = state.get('theme_context', {})
            
            if self.state_manager:
                context = state.get('context', {})
                self.state_manager.set_full_context(context)
            
            return True
        except Exception as e:
            logger.error("Error deserializing shell state: %s", e)
            return False
