"""
Avatar Manager - Manages the representation and interaction with AI Avatars and agents

This module implements the core functionality for managing AI Avatars throughout the system,
including registration, updating, and removal of avatars. It serves as the central
coordination point for avatar-based interactions and expressions.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable

# Initialize logger
logger = logging.getLogger(__name__)

class AvatarManager:
    """
    Manages the registration, updating, and removal of avatars throughout the system.
    """
    
    # Avatar role constants
    ROLE_DATA_LAYER = "data_layer"
    ROLE_CORE_AI_LAYER = "core_ai_layer"
    ROLE_GENERATIVE_LAYER = "generative_layer"
    ROLE_APPLICATION_LAYER = "application_layer"
    ROLE_PROTOCOL_LAYER = "protocol_layer"
    ROLE_WORKFLOW_LAYER = "workflow_layer"
    ROLE_UI_UX_LAYER = "ui_ux_layer"
    ROLE_SECURITY_LAYER = "security_layer"
    ROLE_ASSISTANT = "assistant"
    ROLE_SPECIALIST = "specialist"
    ROLE_COORDINATOR = "coordinator"
    ROLE_MONITOR = "monitor"
    
    # Avatar state constants
    STATE_IDLE = "idle"
    STATE_ACTIVE = "active"
    STATE_THINKING = "thinking"
    STATE_SPEAKING = "speaking"
    STATE_LISTENING = "listening"
    STATE_ALERT = "alert"
    STATE_ERROR = "error"
    STATE_OFFLINE = "offline"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Avatar Manager with optional configuration."""
        self.config = config or {}
        self.avatars = {}
        self.expression_engine = None
        self.state_visualizer = None
        self.interaction_handler = None
        self.cross_layer_coordinator = None
        self.registry = None
        self.animation_controller = None
        self.personality_manager = None
        self.event_subscribers = {}
        self.layer_avatars = {
            self.ROLE_DATA_LAYER: None,
            self.ROLE_CORE_AI_LAYER: None,
            self.ROLE_GENERATIVE_LAYER: None,
            self.ROLE_APPLICATION_LAYER: None,
            self.ROLE_PROTOCOL_LAYER: None,
            self.ROLE_WORKFLOW_LAYER: None,
            self.ROLE_UI_UX_LAYER: None,
            self.ROLE_SECURITY_LAYER: None
        }
        
        logger.info("Avatar Manager initialized with config: %s", self.config)
    
    def initialize(self):
        """Initialize the Avatar Manager and all its components."""
        logger.info("Initializing Avatar Manager components")
        
        # Import dependencies here to avoid circular imports
        from .avatar_expression_engine import AvatarExpressionEngine
        from .agent_state_visualizer import AgentStateVisualizer
        from .agent_interaction_handler import AgentInteractionHandler
        from .cross_layer_avatar_coordinator import CrossLayerAvatarCoordinator
        from .avatar_registry import AvatarRegistry
        from .avatar_animation_controller import AvatarAnimationController
        from .avatar_personality_manager import AvatarPersonalityManager
        
        # Initialize components
        self.expression_engine = AvatarExpressionEngine(self.config.get('expression_engine', {}))
        self.state_visualizer = AgentStateVisualizer(self.config.get('state_visualizer', {}))
        self.interaction_handler = AgentInteractionHandler(self.config.get('interaction_handler', {}))
        self.cross_layer_coordinator = CrossLayerAvatarCoordinator(self.config.get('cross_layer_coordinator', {}))
        self.registry = AvatarRegistry(self.config.get('registry', {}))
        self.animation_controller = AvatarAnimationController(self.config.get('animation_controller', {}))
        self.personality_manager = AvatarPersonalityManager(self.config.get('personality_manager', {}))
        
        # Initialize each component
        self.expression_engine.initialize()
        self.state_visualizer.initialize()
        self.interaction_handler.initialize()
        self.cross_layer_coordinator.initialize()
        self.registry.initialize()
        self.animation_controller.initialize()
        self.personality_manager.initialize()
        
        # Initialize layer avatars if configured
        self._initialize_layer_avatars()
        
        logger.info("Avatar Manager initialization complete")
        return True
    
    def _initialize_layer_avatars(self):
        """Initialize avatars for each layer of the Industrial Foundry Framework."""
        logger.info("Initializing layer avatars")
        
        layer_avatar_configs = self.config.get('layer_avatars', {})
        
        for layer_role, avatar_config in layer_avatar_configs.items():
            if layer_role in self.layer_avatars:
                avatar_id = f"layer_avatar_{layer_role}"
                
                # Merge default layer avatar config with provided config
                config = self._get_default_layer_avatar_config(layer_role)
                if avatar_config:
                    config.update(avatar_config)
                
                # Register the layer avatar
                self.register_avatar(avatar_id, config)
                
                # Store the avatar ID for the layer
                self.layer_avatars[layer_role] = avatar_id
                
                logger.info("Initialized layer avatar for %s: %s", layer_role, avatar_id)
    
    def _get_default_layer_avatar_config(self, layer_role: str) -> Dict[str, Any]:
        """Get default avatar configuration for a specific layer."""
        # Default configurations for each layer avatar
        default_configs = {
            self.ROLE_DATA_LAYER: {
                'name': 'Data Layer Avatar',
                'role': self.ROLE_DATA_LAYER,
                'personality': {
                    'analytical': 0.9,
                    'precise': 0.8,
                    'methodical': 0.7,
                    'curious': 0.6,
                    'helpful': 0.5
                },
                'appearance': {
                    'color_scheme': 'blue',
                    'shape': 'geometric',
                    'animation_style': 'flowing',
                    'icon': 'database'
                },
                'voice': {
                    'pitch': 'medium',
                    'speed': 'medium',
                    'timbre': 'clear'
                },
                'capabilities': [
                    'data_visualization',
                    'schema_explanation',
                    'query_assistance',
                    'data_quality_monitoring'
                ]
            },
            self.ROLE_CORE_AI_LAYER: {
                'name': 'Core AI Layer Avatar',
                'role': self.ROLE_CORE_AI_LAYER,
                'personality': {
                    'analytical': 0.9,
                    'precise': 0.8,
                    'innovative': 0.7,
                    'thoughtful': 0.6,
                    'confident': 0.5
                },
                'appearance': {
                    'color_scheme': 'purple',
                    'shape': 'neural',
                    'animation_style': 'pulsing',
                    'icon': 'brain'
                },
                'voice': {
                    'pitch': 'medium-low',
                    'speed': 'medium',
                    'timbre': 'resonant'
                },
                'capabilities': [
                    'model_explanation',
                    'inference_visualization',
                    'training_monitoring',
                    'decision_confidence_display'
                ]
            },
            self.ROLE_GENERATIVE_LAYER: {
                'name': 'Generative Layer Avatar',
                'role': self.ROLE_GENERATIVE_LAYER,
                'personality': {
                    'creative': 0.9,
                    'expressive': 0.8,
                    'adaptable': 0.7,
                    'intuitive': 0.6,
                    'artistic': 0.5
                },
                'appearance': {
                    'color_scheme': 'magenta',
                    'shape': 'flowing',
                    'animation_style': 'creative',
                    'icon': 'sparkle'
                },
                'voice': {
                    'pitch': 'medium-high',
                    'speed': 'variable',
                    'timbre': 'expressive'
                },
                'capabilities': [
                    'content_generation',
                    'template_management',
                    'style_adaptation',
                    'creative_assistance'
                ]
            },
            self.ROLE_APPLICATION_LAYER: {
                'name': 'Application Layer Avatar',
                'role': self.ROLE_APPLICATION_LAYER,
                'personality': {
                    'practical': 0.9,
                    'efficient': 0.8,
                    'organized': 0.7,
                    'helpful': 0.6,
                    'responsive': 0.5
                },
                'appearance': {
                    'color_scheme': 'green',
                    'shape': 'modular',
                    'animation_style': 'efficient',
                    'icon': 'app'
                },
                'voice': {
                    'pitch': 'medium',
                    'speed': 'medium-fast',
                    'timbre': 'clear'
                },
                'capabilities': [
                    'app_navigation',
                    'feature_explanation',
                    'task_assistance',
                    'process_optimization'
                ]
            },
            self.ROLE_PROTOCOL_LAYER: {
                'name': 'Protocol Layer Avatar',
                'role': self.ROLE_PROTOCOL_LAYER,
                'personality': {
                    'precise': 0.9,
                    'systematic': 0.8,
                    'communicative': 0.7,
                    'reliable': 0.6,
                    'consistent': 0.5
                },
                'appearance': {
                    'color_scheme': 'cyan',
                    'shape': 'connected',
                    'animation_style': 'flowing',
                    'icon': 'network'
                },
                'voice': {
                    'pitch': 'medium',
                    'speed': 'medium',
                    'timbre': 'clear'
                },
                'capabilities': [
                    'protocol_visualization',
                    'message_tracing',
                    'connection_management',
                    'trust_path_display'
                ]
            },
            self.ROLE_WORKFLOW_LAYER: {
                'name': 'Workflow Layer Avatar',
                'role': self.ROLE_WORKFLOW_LAYER,
                'personality': {
                    'organized': 0.9,
                    'efficient': 0.8,
                    'proactive': 0.7,
                    'adaptive': 0.6,
                    'coordinating': 0.5
                },
                'appearance': {
                    'color_scheme': 'orange',
                    'shape': 'flowing',
                    'animation_style': 'sequential',
                    'icon': 'workflow'
                },
                'voice': {
                    'pitch': 'medium',
                    'speed': 'medium-fast',
                    'timbre': 'clear'
                },
                'capabilities': [
                    'workflow_visualization',
                    'task_coordination',
                    'progress_tracking',
                    'bottleneck_identification'
                ]
            },
            self.ROLE_UI_UX_LAYER: {
                'name': 'UI/UX Layer Avatar',
                'role': self.ROLE_UI_UX_LAYER,
                'personality': {
                    'intuitive': 0.9,
                    'empathetic': 0.8,
                    'creative': 0.7,
                    'responsive': 0.6,
                    'helpful': 0.5
                },
                'appearance': {
                    'color_scheme': 'teal',
                    'shape': 'organic',
                    'animation_style': 'smooth',
                    'icon': 'interface'
                },
                'voice': {
                    'pitch': 'medium-high',
                    'speed': 'medium',
                    'timbre': 'warm'
                },
                'capabilities': [
                    'interface_guidance',
                    'personalization',
                    'accessibility_assistance',
                    'interaction_optimization'
                ]
            },
            self.ROLE_SECURITY_LAYER: {
                'name': 'Security Layer Avatar',
                'role': self.ROLE_SECURITY_LAYER,
                'personality': {
                    'vigilant': 0.9,
                    'precise': 0.8,
                    'protective': 0.7,
                    'thorough': 0.6,
                    'trustworthy': 0.5
                },
                'appearance': {
                    'color_scheme': 'blue-gray',
                    'shape': 'shield',
                    'animation_style': 'steady',
                    'icon': 'shield'
                },
                'voice': {
                    'pitch': 'medium-low',
                    'speed': 'medium',
                    'timbre': 'authoritative'
                },
                'capabilities': [
                    'security_monitoring',
                    'threat_visualization',
                    'compliance_checking',
                    'permission_management'
                ]
            }
        }
        
        return default_configs.get(layer_role, {})
    
    def register_avatar(self, avatar_id: str, avatar_config: Dict[str, Any]) -> bool:
        """
        Register a new avatar with the system.
        
        Args:
            avatar_id: Unique identifier for the avatar
            avatar_config: Configuration for the avatar
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        logger.info("Registering avatar: %s", avatar_id)
        
        if avatar_id in self.avatars:
            logger.warning("Avatar already exists: %s", avatar_id)
            return False
        
        # Create avatar entry
        avatar = {
            'id': avatar_id,
            'config': avatar_config,
            'state': self.STATE_IDLE,
            'last_updated': self._get_current_timestamp(),
            'interactions': [],
            'expressions': [],
            'trust_score': avatar_config.get('initial_trust_score', 0.5)
        }
        
        # Store avatar
        self.avatars[avatar_id] = avatar
        
        # Register with registry
        if self.registry:
            self.registry.register_avatar(avatar_id, avatar_config)
        
        # Initialize personality
        if self.personality_manager:
            personality = avatar_config.get('personality', {})
            self.personality_manager.initialize_personality(avatar_id, personality)
        
        # Initialize appearance
        if self.animation_controller:
            appearance = avatar_config.get('appearance', {})
            self.animation_controller.initialize_appearance(avatar_id, appearance)
        
        # Notify subscribers
        self._notify_subscribers('avatar_registered', {
            'avatar_id': avatar_id,
            'config': avatar_config
        })
        
        logger.info("Avatar registered: %s", avatar_id)
        return True
    
    def update_avatar(self, avatar_id: str, state_update: Dict[str, Any]) -> bool:
        """
        Update the state of an existing avatar.
        
        Args:
            avatar_id: Unique identifier for the avatar
            state_update: State update information
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        logger.debug("Updating avatar: %s", avatar_id)
        
        if avatar_id not in self.avatars:
            logger.warning("Avatar not found: %s", avatar_id)
            return False
        
        avatar = self.avatars[avatar_id]
        
        # Update state if provided
        if 'state' in state_update:
            avatar['state'] = state_update['state']
        
        # Update trust score if provided
        if 'trust_score' in state_update:
            avatar['trust_score'] = state_update['trust_score']
        
        # Update config if provided
        if 'config' in state_update:
            avatar['config'].update(state_update['config'])
        
        # Update last updated timestamp
        avatar['last_updated'] = self._get_current_timestamp()
        
        # Add interaction if provided
        if 'interaction' in state_update:
            avatar['interactions'].append({
                'timestamp': self._get_current_timestamp(),
                'interaction': state_update['interaction']
            })
            
            # Limit interactions history
            max_interactions = self.config.get('max_interactions_history', 100)
            if len(avatar['interactions']) > max_interactions:
                avatar['interactions'] = avatar['interactions'][-max_interactions:]
        
        # Add expression if provided
        if 'expression' in state_update:
            avatar['expressions'].append({
                'timestamp': self._get_current_timestamp(),
                'expression': state_update['expression']
            })
            
            # Limit expressions history
            max_expressions = self.config.get('max_expressions_history', 100)
            if len(avatar['expressions']) > max_expressions:
                avatar['expressions'] = avatar['expressions'][-max_expressions:]
        
        # Update visualization
        if self.state_visualizer:
            self.state_visualizer.update_avatar_state(avatar_id, avatar['state'], state_update)
        
        # Update expression
        if self.expression_engine and 'expression' in state_update:
            self.expression_engine.express(avatar_id, state_update['expression'])
        
        # Update animation
        if self.animation_controller and 'animation' in state_update:
            self.animation_controller.animate(avatar_id, state_update['animation'])
        
        # Notify subscribers
        self._notify_subscribers('avatar_updated', {
            'avatar_id': avatar_id,
            'update': state_update
        })
        
        logger.debug("Avatar updated: %s", avatar_id)
        return True
    
    def unregister_avatar(self, avatar_id: str) -> bool:
        """
        Unregister an avatar from the system.
        
        Args:
            avatar_id: Unique identifier for the avatar
        
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        logger.info("Unregistering avatar: %s", avatar_id)
        
        if avatar_id not in self.avatars:
            logger.warning("Avatar not found: %s", avatar_id)
            return False
        
        # Remove from registry
        if self.registry:
            self.registry.unregister_avatar(avatar_id)
        
        # Remove from personality manager
        if self.personality_manager:
            self.personality_manager.remove_personality(avatar_id)
        
        # Remove from animation controller
        if self.animation_controller:
            self.animation_controller.remove_appearance(avatar_id)
        
        # Remove from avatars
        del self.avatars[avatar_id]
        
        # Notify subscribers
        self._notify_subscribers('avatar_unregistered', {
            'avatar_id': avatar_id
        })
        
        logger.info("Avatar unregistered: %s", avatar_id)
        return True
    
    def get_avatar(self, avatar_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an avatar by ID.
        
        Args:
            avatar_id: Unique identifier for the avatar
        
        Returns:
            Optional[Dict[str, Any]]: Avatar information or None if not found
        """
        return self.avatars.get(avatar_id)
    
    def get_all_avatars(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered avatars.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of all avatars
        """
        return self.avatars.copy()
    
    def handle_avatar_interaction(self, avatar_id: str, interaction: Dict[str, Any]) -> bool:
        """
        Handle an interaction with an avatar.
        
        Args:
            avatar_id: Unique identifier for the avatar
            interaction: Interaction information
        
        Returns:
            bool: True if interaction was handled successfully, False otherwise
        """
        logger.info("Handling avatar interaction: %s", avatar_id)
        
        if avatar_id not in self.avatars:
            logger.warning("Avatar not found: %s", avatar_id)
            return False
        
        # Process interaction
        if self.interaction_handler:
            result = self.interaction_handler.handle_interaction(avatar_id, interaction)
            
            # Update avatar state based on interaction result
            if result and 'state_update' in result:
                self.update_avatar(avatar_id, result['state_update'])
            
            return True
        
        logger.warning("Interaction handler not initialized")
        return False
    
    def get_layer_avatar(self, layer_role: str) -> Optional[str]:
        """
        Get avatar ID for a specific layer.
        
        Args:
            layer_role: Layer role identifier
        
        Returns:
            Optional[str]: Avatar ID or None if not found
        """
        return self.layer_avatars.get(layer_role)
    
    def set_layer_avatar(self, layer_role: str, avatar_id: str) -> bool:
        """
        Set avatar ID for a specific layer.
        
        Args:
            layer_role: Layer role identifier
            avatar_id: Avatar ID
        
        Returns:
            bool: True if successful, False otherwise
        """
        if layer_role not in self.layer_avatars:
            logger.warning("Unknown layer role: %s", layer_role)
            return False
        
        if avatar_id not in self.avatars:
            logger.warning("Avatar not found: %s", avatar_id)
            return False
        
        self.layer_avatars[layer_role] = avatar_id
        return True
    
    def get_avatar_by_role(self, role: str) -> List[str]:
        """
        Get avatars by role.
        
        Args:
            role: Role identifier
        
        Returns:
            List[str]: List of avatar IDs with the specified role
        """
        result = []
        
        for avatar_id, avatar in self.avatars.items():
            if avatar['config'].get('role') == role:
                result.append(avatar_id)
        
        return result
    
    def subscribe_to_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to avatar events.
        
        Args:
            event_type: Type of event to subscribe to
            callback: Callback function to be called when event occurs
        
        Returns:
            bool: True if subscription was successful, False otherwise
        """
        if event_type not in self.event_subscribers:
            self.event_subscribers[event_type] = []
        
        self.event_subscribers[event_type].append(callback)
        return True
    
    def unsubscribe_from_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unsubscribe from avatar events.
        
        Args:
            event_type: Type of event to unsubscribe from
            callback: Callback function to be removed
        
        Returns:
            bool: True if unsubscription was successful, False otherwise
        """
        if event_type in self.event_subscribers and callback in self.event_subscribers[event_type]:
            self.event_subscribers[event_type].remove(callback)
            return True
        
        return False
    
    def _notify_subscribers(self, event_type: str, event_data: Dict[str, Any]):
        """
        Notify subscribers of an event.
        
        Args:
            event_type: Type of event
            event_data: Event data
        """
        if event_type in self.event_subscribers:
            for callback in self.event_subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    logger.error("Error in event subscriber callback: %s", e)
    
    def _get_current_timestamp(self) -> int:
        """
        Get current timestamp.
        
        Returns:
            int: Current timestamp in milliseconds
        """
        import time
        return int(time.time() * 1000)
    
    def to_json(self) -> str:
        """
        Serialize avatar manager state to JSON.
        
        Returns:
            str: JSON string representation of avatar manager state
        """
        state = {
            'avatars': self.avatars,
            'layer_avatars': self.layer_avatars
        }
        
        return json.dumps(state)
    
    def from_json(self, json_str: str) -> bool:
        """
        Deserialize avatar manager state from JSON.
        
        Args:
            json_str: JSON string representation of avatar manager state
        
        Returns:
            bool: True if deserialization was successful, False otherwise
        """
        try:
            state = json.loads(json_str)
            
            self.avatars = state.get('avatars', {})
            self.layer_avatars = state.get('layer_avatars', {})
            
            return True
        except Exception as e:
            logger.error("Error deserializing avatar manager state: %s", e)
            return False
