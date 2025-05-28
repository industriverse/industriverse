"""
Context Engine - Manages contextual awareness and adaptation

This module implements the core functionality for managing contextual awareness
and adaptation throughout the UI/UX Layer. It serves as the central coordination
point for context-based adaptations and intelligent responses to changing conditions.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable

# Initialize logger
logger = logging.getLogger(__name__)

class ContextEngine:
    """
    Manages contextual awareness and adaptation throughout the UI/UX Layer.
    """
    
    # Context type constants
    TYPE_USER = "user"
    TYPE_DEVICE = "device"
    TYPE_ENVIRONMENT = "environment"
    TYPE_WORKFLOW = "workflow"
    TYPE_TASK = "task"
    TYPE_SYSTEM = "system"
    TYPE_TEMPORAL = "temporal"
    TYPE_SPATIAL = "spatial"
    
    # Context priority levels
    PRIORITY_CRITICAL = "critical"
    PRIORITY_HIGH = "high"
    PRIORITY_MEDIUM = "medium"
    PRIORITY_LOW = "low"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Context Engine with optional configuration."""
        self.config = config or {}
        self.context_store = {}
        self.context_history = {}
        self.context_rules = {}
        self.context_providers = {}
        self.context_subscribers = {}
        self.event_subscribers = {}
        self.active_adaptations = {}
        
        # Initialize context store with empty contexts for each type
        for context_type in [self.TYPE_USER, self.TYPE_DEVICE, self.TYPE_ENVIRONMENT, 
                            self.TYPE_WORKFLOW, self.TYPE_TASK, self.TYPE_SYSTEM,
                            self.TYPE_TEMPORAL, self.TYPE_SPATIAL]:
            self.context_store[context_type] = {}
            self.context_history[context_type] = []
        
        logger.info("Context Engine initialized with config: %s", self.config)
    
    def initialize(self):
        """Initialize the Context Engine and all its components."""
        logger.info("Initializing Context Engine components")
        
        # Import dependencies here to avoid circular imports
        from .context_provider_manager import ContextProviderManager
        from .context_rule_engine import ContextRuleEngine
        from .context_adaptation_manager import ContextAdaptationManager
        from .context_history_manager import ContextHistoryManager
        from .context_event_bus import ContextEventBus
        
        # Initialize components
        self.provider_manager = ContextProviderManager(self.config.get('provider_manager', {}))
        self.rule_engine = ContextRuleEngine(self.config.get('rule_engine', {}))
        self.adaptation_manager = ContextAdaptationManager(self.config.get('adaptation_manager', {}))
        self.history_manager = ContextHistoryManager(self.config.get('history_manager', {}))
        self.event_bus = ContextEventBus(self.config.get('event_bus', {}))
        
        # Initialize each component
        self.provider_manager.initialize()
        self.rule_engine.initialize()
        self.adaptation_manager.initialize()
        self.history_manager.initialize()
        self.event_bus.initialize()
        
        # Load default context rules
        self._load_default_context_rules()
        
        # Register default context providers
        self._register_default_context_providers()
        
        # Subscribe to event bus
        self.event_bus.subscribe('context_updated', self._handle_context_updated)
        self.event_bus.subscribe('rule_triggered', self._handle_rule_triggered)
        self.event_bus.subscribe('adaptation_applied', self._handle_adaptation_applied)
        
        logger.info("Context Engine initialization complete")
        return True
    
    def _load_default_context_rules(self):
        """Load default context rules."""
        default_rules = self.config.get('default_rules', [])
        
        for rule in default_rules:
            self.register_context_rule(rule)
        
        logger.info("Loaded %d default context rules", len(default_rules))
    
    def _register_default_context_providers(self):
        """Register default context providers."""
        default_providers = self.config.get('default_providers', {})
        
        for provider_type, provider_config in default_providers.items():
            self.register_context_provider(provider_type, provider_config)
        
        logger.info("Registered %d default context providers", len(default_providers))
    
    def update_context(self, context_type: str, context_data: Dict[str, Any], 
                      source: str = "system", priority: str = "medium") -> bool:
        """
        Update context of a specific type.
        
        Args:
            context_type: Type of context to update
            context_data: Context data to update
            source: Source of the context update
            priority: Priority of the context update
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        logger.debug("Updating context: %s from %s with priority %s", 
                    context_type, source, priority)
        
        if context_type not in self.context_store:
            logger.warning("Unknown context type: %s", context_type)
            return False
        
        # Create context update object
        context_update = {
            'type': context_type,
            'data': context_data,
            'source': source,
            'priority': priority,
            'timestamp': self._get_current_timestamp()
        }
        
        # Store previous context for history
        previous_context = self.context_store[context_type].copy()
        
        # Update context store
        self.context_store[context_type].update(context_data)
        
        # Add to history
        if self.history_manager:
            self.history_manager.add_to_history(context_type, previous_context, 
                                              self.context_store[context_type], 
                                              source, priority)
        else:
            # Simple history tracking if history manager not available
            self.context_history[context_type].append({
                'previous': previous_context,
                'current': self.context_store[context_type].copy(),
                'source': source,
                'priority': priority,
                'timestamp': self._get_current_timestamp()
            })
            
            # Limit history size
            max_history = self.config.get('max_history_size', 100)
            if len(self.context_history[context_type]) > max_history:
                self.context_history[context_type] = self.context_history[context_type][-max_history:]
        
        # Publish event
        self.event_bus.publish('context_updated', context_update)
        
        # Evaluate rules
        if self.rule_engine:
            self.rule_engine.evaluate_rules(context_type, self.context_store)
        
        # Notify subscribers
        self._notify_context_subscribers(context_type, context_data)
        
        logger.debug("Context updated: %s", context_type)
        return True
    
    def get_context(self, context_type: str) -> Dict[str, Any]:
        """
        Get context of a specific type.
        
        Args:
            context_type: Type of context to get
        
        Returns:
            Dict[str, Any]: Context data
        """
        if context_type not in self.context_store:
            logger.warning("Unknown context type: %s", context_type)
            return {}
        
        return self.context_store[context_type].copy()
    
    def get_all_context(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all context data.
        
        Returns:
            Dict[str, Dict[str, Any]]: All context data
        """
        return {k: v.copy() for k, v in self.context_store.items()}
    
    def register_context_rule(self, rule: Dict[str, Any]) -> bool:
        """
        Register a context rule.
        
        Args:
            rule: Rule configuration
                - id: Unique identifier for the rule
                - name: Human-readable name for the rule
                - description: Description of the rule
                - context_type: Type of context this rule applies to
                - condition: Condition expression or function
                - actions: List of actions to take when condition is met
                - priority: Priority of the rule
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        rule_id = rule.get('id')
        if not rule_id:
            logger.warning("Rule must have an ID")
            return False
        
        logger.info("Registering context rule: %s", rule_id)
        
        # Register with rule engine
        if self.rule_engine:
            return self.rule_engine.register_rule(rule)
        
        # Simple rule storage if rule engine not available
        self.context_rules[rule_id] = rule
        return True
    
    def unregister_context_rule(self, rule_id: str) -> bool:
        """
        Unregister a context rule.
        
        Args:
            rule_id: Unique identifier for the rule
        
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        logger.info("Unregistering context rule: %s", rule_id)
        
        # Unregister from rule engine
        if self.rule_engine:
            return self.rule_engine.unregister_rule(rule_id)
        
        # Simple rule removal if rule engine not available
        if rule_id in self.context_rules:
            del self.context_rules[rule_id]
            return True
        
        logger.warning("Rule not found: %s", rule_id)
        return False
    
    def register_context_provider(self, provider_type: str, provider_config: Dict[str, Any]) -> bool:
        """
        Register a context provider.
        
        Args:
            provider_type: Type of context this provider supplies
            provider_config: Provider configuration
                - id: Unique identifier for the provider
                - name: Human-readable name for the provider
                - description: Description of the provider
                - update_interval: How often the provider should update (in ms)
                - enabled: Whether the provider is enabled
        
        Returns:
            bool: True if registration was successful, False otherwise
        """
        provider_id = provider_config.get('id')
        if not provider_id:
            logger.warning("Provider must have an ID")
            return False
        
        logger.info("Registering context provider: %s for type %s", provider_id, provider_type)
        
        # Register with provider manager
        if self.provider_manager:
            return self.provider_manager.register_provider(provider_type, provider_config)
        
        # Simple provider storage if provider manager not available
        if provider_type not in self.context_providers:
            self.context_providers[provider_type] = {}
        
        self.context_providers[provider_type][provider_id] = provider_config
        return True
    
    def unregister_context_provider(self, provider_type: str, provider_id: str) -> bool:
        """
        Unregister a context provider.
        
        Args:
            provider_type: Type of context this provider supplies
            provider_id: Unique identifier for the provider
        
        Returns:
            bool: True if unregistration was successful, False otherwise
        """
        logger.info("Unregistering context provider: %s for type %s", provider_id, provider_type)
        
        # Unregister from provider manager
        if self.provider_manager:
            return self.provider_manager.unregister_provider(provider_type, provider_id)
        
        # Simple provider removal if provider manager not available
        if provider_type in self.context_providers and provider_id in self.context_providers[provider_type]:
            del self.context_providers[provider_type][provider_id]
            return True
        
        logger.warning("Provider not found: %s for type %s", provider_id, provider_type)
        return False
    
    def subscribe_to_context(self, context_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to context updates of a specific type.
        
        Args:
            context_type: Type of context to subscribe to
            callback: Callback function to be called when context is updated
        
        Returns:
            bool: True if subscription was successful, False otherwise
        """
        logger.debug("Subscribing to context type: %s", context_type)
        
        if context_type not in self.context_subscribers:
            self.context_subscribers[context_type] = []
        
        self.context_subscribers[context_type].append(callback)
        return True
    
    def unsubscribe_from_context(self, context_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Unsubscribe from context updates of a specific type.
        
        Args:
            context_type: Type of context to unsubscribe from
            callback: Callback function to be removed
        
        Returns:
            bool: True if unsubscription was successful, False otherwise
        """
        logger.debug("Unsubscribing from context type: %s", context_type)
        
        if context_type in self.context_subscribers and callback in self.context_subscribers[context_type]:
            self.context_subscribers[context_type].remove(callback)
            return True
        
        return False
    
    def subscribe_to_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to context engine events.
        
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
        Unsubscribe from context engine events.
        
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
    
    def apply_adaptation(self, adaptation_id: str, target: str, 
                        adaptation_data: Dict[str, Any]) -> bool:
        """
        Apply an adaptation based on context.
        
        Args:
            adaptation_id: Unique identifier for the adaptation
            target: Target component or system for the adaptation
            adaptation_data: Adaptation data
        
        Returns:
            bool: True if adaptation was applied successfully, False otherwise
        """
        logger.info("Applying adaptation: %s to target %s", adaptation_id, target)
        
        # Apply adaptation using adaptation manager
        if self.adaptation_manager:
            return self.adaptation_manager.apply_adaptation(adaptation_id, target, adaptation_data)
        
        # Simple adaptation tracking if adaptation manager not available
        self.active_adaptations[adaptation_id] = {
            'target': target,
            'data': adaptation_data,
            'timestamp': self._get_current_timestamp()
        }
        
        # Notify subscribers
        self._notify_event_subscribers('adaptation_applied', {
            'adaptation_id': adaptation_id,
            'target': target,
            'data': adaptation_data
        })
        
        logger.info("Adaptation applied: %s", adaptation_id)
        return True
    
    def remove_adaptation(self, adaptation_id: str) -> bool:
        """
        Remove an applied adaptation.
        
        Args:
            adaptation_id: Unique identifier for the adaptation
        
        Returns:
            bool: True if adaptation was removed successfully, False otherwise
        """
        logger.info("Removing adaptation: %s", adaptation_id)
        
        # Remove adaptation using adaptation manager
        if self.adaptation_manager:
            return self.adaptation_manager.remove_adaptation(adaptation_id)
        
        # Simple adaptation removal if adaptation manager not available
        if adaptation_id in self.active_adaptations:
            del self.active_adaptations[adaptation_id]
            
            # Notify subscribers
            self._notify_event_subscribers('adaptation_removed', {
                'adaptation_id': adaptation_id
            })
            
            logger.info("Adaptation removed: %s", adaptation_id)
            return True
        
        logger.warning("Adaptation not found: %s", adaptation_id)
        return False
    
    def get_active_adaptations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active adaptations.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of active adaptations
        """
        if self.adaptation_manager:
            return self.adaptation_manager.get_active_adaptations()
        
        return self.active_adaptations.copy()
    
    def get_context_history(self, context_type: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get history for a specific context type.
        
        Args:
            context_type: Type of context to get history for
            limit: Maximum number of history entries to return
        
        Returns:
            List[Dict[str, Any]]: List of history entries
        """
        if self.history_manager:
            return self.history_manager.get_history(context_type, limit)
        
        if context_type not in self.context_history:
            return []
        
        return self.context_history[context_type][-limit:]
    
    def _handle_context_updated(self, event_data: Dict[str, Any]):
        """
        Handle context updated event.
        
        Args:
            event_data: Event data
        """
        context_type = event_data.get('type')
        context_data = event_data.get('data', {})
        
        logger.debug("Handling context updated event for type: %s", context_type)
        
        # Notify subscribers
        self._notify_event_subscribers('context_updated', event_data)
    
    def _handle_rule_triggered(self, event_data: Dict[str, Any]):
        """
        Handle rule triggered event.
        
        Args:
            event_data: Event data
        """
        rule_id = event_data.get('rule_id')
        context_type = event_data.get('context_type')
        
        logger.debug("Handling rule triggered event: %s for context type %s", 
                    rule_id, context_type)
        
        # Notify subscribers
        self._notify_event_subscribers('rule_triggered', event_data)
    
    def _handle_adaptation_applied(self, event_data: Dict[str, Any]):
        """
        Handle adaptation applied event.
        
        Args:
            event_data: Event data
        """
        adaptation_id = event_data.get('adaptation_id')
        target = event_data.get('target')
        
        logger.debug("Handling adaptation applied event: %s for target %s", 
                    adaptation_id, target)
        
        # Notify subscribers
        self._notify_event_subscribers('adaptation_applied', event_data)
    
    def _notify_context_subscribers(self, context_type: str, context_data: Dict[str, Any]):
        """
        Notify subscribers of a context update.
        
        Args:
            context_type: Type of context that was updated
            context_data: Updated context data
        """
        if context_type in self.context_subscribers:
            for callback in self.context_subscribers[context_type]:
                try:
                    callback(context_data)
                except Exception as e:
                    logger.error("Error in context subscriber callback: %s", e)
    
    def _notify_event_subscribers(self, event_type: str, event_data: Dict[str, Any]):
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
        Serialize context engine state to JSON.
        
        Returns:
            str: JSON string representation of context engine state
        """
        state = {
            'context_store': self.context_store,
            'active_adaptations': self.active_adaptations
        }
        
        return json.dumps(state)
    
    def from_json(self, json_str: str) -> bool:
        """
        Deserialize context engine state from JSON.
        
        Args:
            json_str: JSON string representation of context engine state
        
        Returns:
            bool: True if deserialization was successful, False otherwise
        """
        try:
            state = json.loads(json_str)
            
            self.context_store = state.get('context_store', {})
            self.active_adaptations = state.get('active_adaptations', {})
            
            return True
        except Exception as e:
            logger.error("Error deserializing context engine state: %s", e)
            return False
