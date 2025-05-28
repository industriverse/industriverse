"""
Capsule Manager - Manages the lifecycle of Dynamic Agent Capsules

This module implements the core functionality for managing Dynamic Agent Capsules,
including creation, updating, and removal of capsules. It serves as the central
coordination point for capsule-based interactions and morphology.
"""

import logging
import json
from typing import Dict, List, Any, Optional, Callable

# Initialize logger
logger = logging.getLogger(__name__)

class CapsuleManager:
    """
    Manages the lifecycle of capsules, including creation, updating, and removal.
    """
    
    # Capsule type constants
    TYPE_WORKFLOW = "workflow"
    TYPE_AGENT = "agent"
    TYPE_TASK = "task"
    TYPE_DECISION = "decision"
    TYPE_MONITOR = "monitor"
    TYPE_ALERT = "alert"
    TYPE_CONTROL = "control"
    
    # Capsule state constants
    STATE_IDLE = "idle"
    STATE_ACTIVE = "active"
    STATE_PROCESSING = "processing"
    STATE_WAITING = "waiting"
    STATE_COMPLETE = "complete"
    STATE_ERROR = "error"
    STATE_PAUSED = "paused"
    
    # Capsule confidence levels
    CONFIDENCE_HIGH = "high"
    CONFIDENCE_MEDIUM = "medium"
    CONFIDENCE_LOW = "low"
    CONFIDENCE_UNKNOWN = "unknown"
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Capsule Manager with optional configuration."""
        self.config = config or {}
        self.capsules = {}
        self.morphology_engine = None
        self.memory_manager = None
        self.interaction_handler = None
        self.composer = None
        self.registry = None
        self.state_machine = None
        self.event_bus = None
        self.event_subscribers = {}
        
        logger.info("Capsule Manager initialized with config: %s", self.config)
    
    def initialize(self):
        """Initialize the Capsule Manager and all its components."""
        logger.info("Initializing Capsule Manager components")
        
        # Import dependencies here to avoid circular imports
        from .capsule_morphology_engine import CapsuleMorphologyEngine
        from .capsule_memory_manager import CapsuleMemoryManager
        from .capsule_interaction_handler import CapsuleInteractionHandler
        from .capsule_composer import CapsuleComposer
        from .capsule_registry import CapsuleRegistry
        from .capsule_state_machine import CapsuleStateMachine
        from .capsule_event_bus import CapsuleEventBus
        
        # Initialize components
        self.morphology_engine = CapsuleMorphologyEngine(self.config.get('morphology_engine', {}))
        self.memory_manager = CapsuleMemoryManager(self.config.get('memory_manager', {}))
        self.interaction_handler = CapsuleInteractionHandler(self.config.get('interaction_handler', {}))
        self.composer = CapsuleComposer(self.config.get('composer', {}))
        self.registry = CapsuleRegistry(self.config.get('registry', {}))
        self.state_machine = CapsuleStateMachine(self.config.get('state_machine', {}))
        self.event_bus = CapsuleEventBus(self.config.get('event_bus', {}))
        
        # Initialize each component
        self.morphology_engine.initialize()
        self.memory_manager.initialize()
        self.interaction_handler.initialize()
        self.composer.initialize()
        self.registry.initialize()
        self.state_machine.initialize()
        self.event_bus.initialize()
        
        # Subscribe to event bus
        self.event_bus.subscribe('capsule_state_changed', self._handle_state_changed)
        self.event_bus.subscribe('capsule_confidence_changed', self._handle_confidence_changed)
        self.event_bus.subscribe('capsule_memory_updated', self._handle_memory_updated)
        
        logger.info("Capsule Manager initialization complete")
        return True
    
    def create_capsule(self, capsule_config: Dict[str, Any]) -> str:
        """
        Create a new capsule with the given configuration.
        
        Args:
            capsule_config: Configuration for the capsule
        
        Returns:
            str: Unique identifier for the created capsule
        """
        logger.info("Creating capsule with config: %s", capsule_config)
        
        # Generate capsule ID if not provided
        capsule_id = capsule_config.get('id')
        if not capsule_id:
            capsule_id = self._generate_capsule_id(capsule_config)
            capsule_config['id'] = capsule_id
        
        # Check if capsule already exists
        if capsule_id in self.capsules:
            logger.warning("Capsule already exists: %s", capsule_id)
            return ""
        
        # Create capsule entry
        capsule = {
            'id': capsule_id,
            'config': capsule_config,
            'state': capsule_config.get('initial_state', self.STATE_IDLE),
            'confidence': capsule_config.get('initial_confidence', self.CONFIDENCE_UNKNOWN),
            'created_at': self._get_current_timestamp(),
            'updated_at': self._get_current_timestamp(),
            'memory': {},
            'interactions': [],
            'events': []
        }
        
        # Store capsule
        self.capsules[capsule_id] = capsule
        
        # Register with registry
        if self.registry:
            self.registry.register_capsule(capsule_id, capsule_config)
        
        # Initialize morphology
        if self.morphology_engine:
            self.morphology_engine.initialize_morphology(capsule_id, capsule_config)
        
        # Initialize memory
        if self.memory_manager:
            initial_memory = capsule_config.get('initial_memory', {})
            self.memory_manager.initialize_memory(capsule_id, initial_memory)
        
        # Initialize state machine
        if self.state_machine:
            self.state_machine.initialize_state(capsule_id, capsule['state'])
        
        # Publish event
        self.event_bus.publish('capsule_created', {
            'capsule_id': capsule_id,
            'config': capsule_config
        })
        
        # Notify subscribers
        self._notify_subscribers('capsule_created', {
            'capsule_id': capsule_id,
            'config': capsule_config
        })
        
        logger.info("Capsule created: %s", capsule_id)
        return capsule_id
    
    def update_capsule(self, capsule_id: str, state_update: Dict[str, Any]) -> bool:
        """
        Update the state of an existing capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
            state_update: State update information
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        logger.debug("Updating capsule: %s", capsule_id)
        
        if capsule_id not in self.capsules:
            logger.warning("Capsule not found: %s", capsule_id)
            return False
        
        capsule = self.capsules[capsule_id]
        
        # Update state if provided
        if 'state' in state_update:
            new_state = state_update['state']
            old_state = capsule['state']
            
            # Use state machine to validate transition
            if self.state_machine and not self.state_machine.can_transition(capsule_id, old_state, new_state):
                logger.warning("Invalid state transition: %s -> %s for capsule %s", 
                              old_state, new_state, capsule_id)
                return False
            
            capsule['state'] = new_state
            
            # Publish state changed event
            self.event_bus.publish('capsule_state_changed', {
                'capsule_id': capsule_id,
                'old_state': old_state,
                'new_state': new_state
            })
        
        # Update confidence if provided
        if 'confidence' in state_update:
            old_confidence = capsule['confidence']
            new_confidence = state_update['confidence']
            capsule['confidence'] = new_confidence
            
            # Publish confidence changed event
            self.event_bus.publish('capsule_confidence_changed', {
                'capsule_id': capsule_id,
                'old_confidence': old_confidence,
                'new_confidence': new_confidence
            })
        
        # Update config if provided
        if 'config' in state_update:
            capsule['config'].update(state_update['config'])
        
        # Update memory if provided
        if 'memory' in state_update:
            if self.memory_manager:
                self.memory_manager.update_memory(capsule_id, state_update['memory'])
            else:
                # Direct memory update if memory manager not available
                for key, value in state_update['memory'].items():
                    capsule['memory'][key] = value
                
                # Publish memory updated event
                self.event_bus.publish('capsule_memory_updated', {
                    'capsule_id': capsule_id,
                    'updates': state_update['memory']
                })
        
        # Add interaction if provided
        if 'interaction' in state_update:
            interaction = {
                'timestamp': self._get_current_timestamp(),
                'interaction': state_update['interaction']
            }
            
            capsule['interactions'].append(interaction)
            
            # Limit interactions history
            max_interactions = self.config.get('max_interactions_history', 100)
            if len(capsule['interactions']) > max_interactions:
                capsule['interactions'] = capsule['interactions'][-max_interactions:]
            
            # Process interaction
            if self.interaction_handler:
                self.interaction_handler.handle_interaction(capsule_id, state_update['interaction'])
        
        # Add event if provided
        if 'event' in state_update:
            event = {
                'timestamp': self._get_current_timestamp(),
                'event': state_update['event']
            }
            
            capsule['events'].append(event)
            
            # Limit events history
            max_events = self.config.get('max_events_history', 100)
            if len(capsule['events']) > max_events:
                capsule['events'] = capsule['events'][-max_events:]
        
        # Update morphology if needed
        if self.morphology_engine:
            morphology_update = {}
            
            if 'state' in state_update:
                morphology_update['state'] = state_update['state']
            
            if 'confidence' in state_update:
                morphology_update['confidence'] = state_update['confidence']
            
            if 'config' in state_update and 'appearance' in state_update['config']:
                morphology_update['appearance'] = state_update['config']['appearance']
            
            if morphology_update:
                self.morphology_engine.update_morphology(capsule_id, morphology_update)
        
        # Update timestamp
        capsule['updated_at'] = self._get_current_timestamp()
        
        # Publish event
        self.event_bus.publish('capsule_updated', {
            'capsule_id': capsule_id,
            'update': state_update
        })
        
        # Notify subscribers
        self._notify_subscribers('capsule_updated', {
            'capsule_id': capsule_id,
            'update': state_update
        })
        
        logger.debug("Capsule updated: %s", capsule_id)
        return True
    
    def remove_capsule(self, capsule_id: str) -> bool:
        """
        Remove a capsule from the system.
        
        Args:
            capsule_id: Unique identifier for the capsule
        
        Returns:
            bool: True if removal was successful, False otherwise
        """
        logger.info("Removing capsule: %s", capsule_id)
        
        if capsule_id not in self.capsules:
            logger.warning("Capsule not found: %s", capsule_id)
            return False
        
        # Unregister from registry
        if self.registry:
            self.registry.unregister_capsule(capsule_id)
        
        # Clean up morphology
        if self.morphology_engine:
            self.morphology_engine.remove_morphology(capsule_id)
        
        # Clean up memory
        if self.memory_manager:
            self.memory_manager.remove_memory(capsule_id)
        
        # Clean up state machine
        if self.state_machine:
            self.state_machine.remove_state(capsule_id)
        
        # Remove from capsules
        del self.capsules[capsule_id]
        
        # Publish event
        self.event_bus.publish('capsule_removed', {
            'capsule_id': capsule_id
        })
        
        # Notify subscribers
        self._notify_subscribers('capsule_removed', {
            'capsule_id': capsule_id
        })
        
        logger.info("Capsule removed: %s", capsule_id)
        return True
    
    def get_capsule(self, capsule_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a capsule by ID.
        
        Args:
            capsule_id: Unique identifier for the capsule
        
        Returns:
            Optional[Dict[str, Any]]: Capsule information or None if not found
        """
        return self.capsules.get(capsule_id)
    
    def get_all_capsules(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active capsules.
        
        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of all capsules
        """
        return self.capsules.copy()
    
    def handle_capsule_interaction(self, capsule_id: str, interaction: Dict[str, Any]) -> bool:
        """
        Handle an interaction with a capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
            interaction: Interaction information
        
        Returns:
            bool: True if interaction was handled successfully, False otherwise
        """
        logger.info("Handling capsule interaction: %s", capsule_id)
        
        if capsule_id not in self.capsules:
            logger.warning("Capsule not found: %s", capsule_id)
            return False
        
        # Add interaction to capsule
        update = {
            'interaction': interaction
        }
        
        # Update capsule
        self.update_capsule(capsule_id, update)
        
        # Process interaction
        if self.interaction_handler:
            result = self.interaction_handler.handle_interaction(capsule_id, interaction)
            
            # Update capsule state based on interaction result
            if result and 'state_update' in result:
                self.update_capsule(capsule_id, result['state_update'])
            
            return True
        
        logger.warning("Interaction handler not initialized")
        return False
    
    def compose_capsules(self, capsule_ids: List[str], composition_config: Dict[str, Any]) -> str:
        """
        Compose multiple capsules into a new capsule.
        
        Args:
            capsule_ids: List of capsule IDs to compose
            composition_config: Configuration for the composition
        
        Returns:
            str: ID of the composed capsule, or empty string if composition failed
        """
        logger.info("Composing capsules: %s", capsule_ids)
        
        if not self.composer:
            logger.warning("Capsule composer not initialized")
            return ""
        
        # Check if all capsules exist
        for capsule_id in capsule_ids:
            if capsule_id not in self.capsules:
                logger.warning("Capsule not found: %s", capsule_id)
                return ""
        
        # Compose capsules
        result = self.composer.compose(capsule_ids, composition_config)
        
        if not result or 'capsule_config' not in result:
            logger.warning("Composition failed")
            return ""
        
        # Create new capsule from composition result
        new_capsule_id = self.create_capsule(result['capsule_config'])
        
        logger.info("Capsules composed into new capsule: %s", new_capsule_id)
        return new_capsule_id
    
    def get_capsules_by_type(self, capsule_type: str) -> List[str]:
        """
        Get capsules by type.
        
        Args:
            capsule_type: Type of capsules to get
        
        Returns:
            List[str]: List of capsule IDs with the specified type
        """
        result = []
        
        for capsule_id, capsule in self.capsules.items():
            if capsule['config'].get('type') == capsule_type:
                result.append(capsule_id)
        
        return result
    
    def get_capsules_by_state(self, state: str) -> List[str]:
        """
        Get capsules by state.
        
        Args:
            state: State of capsules to get
        
        Returns:
            List[str]: List of capsule IDs with the specified state
        """
        result = []
        
        for capsule_id, capsule in self.capsules.items():
            if capsule['state'] == state:
                result.append(capsule_id)
        
        return result
    
    def get_capsules_by_confidence(self, confidence: str) -> List[str]:
        """
        Get capsules by confidence level.
        
        Args:
            confidence: Confidence level of capsules to get
        
        Returns:
            List[str]: List of capsule IDs with the specified confidence level
        """
        result = []
        
        for capsule_id, capsule in self.capsules.items():
            if capsule['confidence'] == confidence:
                result.append(capsule_id)
        
        return result
    
    def get_capsule_memory(self, capsule_id: str) -> Dict[str, Any]:
        """
        Get memory for a specific capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
        
        Returns:
            Dict[str, Any]: Capsule memory
        """
        if capsule_id not in self.capsules:
            logger.warning("Capsule not found: %s", capsule_id)
            return {}
        
        if self.memory_manager:
            return self.memory_manager.get_memory(capsule_id)
        
        return self.capsules[capsule_id].get('memory', {})
    
    def update_capsule_memory(self, capsule_id: str, memory_update: Dict[str, Any]) -> bool:
        """
        Update memory for a specific capsule.
        
        Args:
            capsule_id: Unique identifier for the capsule
            memory_update: Memory update information
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        if capsule_id not in self.capsules:
            logger.warning("Capsule not found: %s", capsule_id)
            return False
        
        update = {
            'memory': memory_update
        }
        
        return self.update_capsule(capsule_id, update)
    
    def subscribe_to_events(self, event_type: str, callback: Callable[[Dict[str, Any]], None]) -> bool:
        """
        Subscribe to capsule events.
        
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
        Unsubscribe from capsule events.
        
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
    
    def _handle_state_changed(self, event_data: Dict[str, Any]):
        """
        Handle capsule state changed event.
        
        Args:
            event_data: Event data
        """
        capsule_id = event_data.get('capsule_id')
        old_state = event_data.get('old_state')
        new_state = event_data.get('new_state')
        
        logger.debug("Capsule state changed: %s -> %s for capsule %s", 
                    old_state, new_state, capsule_id)
        
        # Update morphology based on state change
        if self.morphology_engine:
            self.morphology_engine.update_morphology(capsule_id, {'state': new_state})
    
    def _handle_confidence_changed(self, event_data: Dict[str, Any]):
        """
        Handle capsule confidence changed event.
        
        Args:
            event_data: Event data
        """
        capsule_id = event_data.get('capsule_id')
        old_confidence = event_data.get('old_confidence')
        new_confidence = event_data.get('new_confidence')
        
        logger.debug("Capsule confidence changed: %s -> %s for capsule %s", 
                    old_confidence, new_confidence, capsule_id)
        
        # Update morphology based on confidence change
        if self.morphology_engine:
            self.morphology_engine.update_morphology(capsule_id, {'confidence': new_confidence})
    
    def _handle_memory_updated(self, event_data: Dict[str, Any]):
        """
        Handle capsule memory updated event.
        
        Args:
            event_data: Event data
        """
        capsule_id = event_data.get('capsule_id')
        updates = event_data.get('updates', {})
        
        logger.debug("Capsule memory updated for capsule %s: %s", capsule_id, updates)
        
        # Update capsule memory
        if capsule_id in self.capsules:
            for key, value in updates.items():
                self.capsules[capsule_id]['memory'][key] = value
    
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
    
    def _generate_capsule_id(self, capsule_config: Dict[str, Any]) -> str:
        """
        Generate a unique capsule ID.
        
        Args:
            capsule_config: Capsule configuration
        
        Returns:
            str: Unique capsule ID
        """
        import uuid
        import hashlib
        
        # Use name and type if available
        name = capsule_config.get('name', '')
        capsule_type = capsule_config.get('type', '')
        
        if name and capsule_type:
            # Create a deterministic ID based on name and type
            hash_input = f"{name}:{capsule_type}:{uuid.uuid4()}"
            return f"capsule-{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"
        
        # Otherwise, generate a random ID
        return f"capsule-{uuid.uuid4().hex[:8]}"
    
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
        Serialize capsule manager state to JSON.
        
        Returns:
            str: JSON string representation of capsule manager state
        """
        state = {
            'capsules': self.capsules
        }
        
        return json.dumps(state)
    
    def from_json(self, json_str: str) -> bool:
        """
        Deserialize capsule manager state from JSON.
        
        Args:
            json_str: JSON string representation of capsule manager state
        
        Returns:
            bool: True if deserialization was successful, False otherwise
        """
        try:
            state = json.loads(json_str)
            
            self.capsules = state.get('capsules', {})
            
            # Reinitialize components with loaded state
            if self.registry:
                for capsule_id, capsule in self.capsules.items():
                    self.registry.register_capsule(capsule_id, capsule['config'])
            
            if self.morphology_engine:
                for capsule_id, capsule in self.capsules.items():
                    self.morphology_engine.initialize_morphology(capsule_id, capsule['config'])
            
            if self.memory_manager:
                for capsule_id, capsule in self.capsules.items():
                    self.memory_manager.initialize_memory(capsule_id, capsule['memory'])
            
            if self.state_machine:
                for capsule_id, capsule in self.capsules.items():
                    self.state_machine.initialize_state(capsule_id, capsule['state'])
            
            return True
        except Exception as e:
            logger.error("Error deserializing capsule manager state: %s", e)
            return False
