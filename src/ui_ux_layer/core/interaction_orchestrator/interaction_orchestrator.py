"""
Interaction Orchestrator for the Industriverse UI/UX Layer.

This module provides orchestration of interactions between users, agents, and the system,
enabling seamless and intuitive interaction experiences across different modalities.

Author: Manus
"""

import logging
import json
import time
import threading
import queue
from typing import Dict, List, Optional, Any, Callable, Union, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field

class InteractionMode(Enum):
    """Enumeration of interaction modes."""
    DIRECT = "direct"  # Direct manipulation
    CONVERSATIONAL = "conversational"  # Voice/text conversation
    AMBIENT = "ambient"  # Ambient/peripheral interaction
    GESTURE = "gesture"  # Gesture-based interaction
    MIXED = "mixed"  # Mixed-mode interaction

class InteractionModality(Enum):
    """Enumeration of interaction modalities."""
    TOUCH = "touch"
    VOICE = "voice"
    GESTURE = "gesture"
    GAZE = "gaze"
    TEXT = "text"
    HAPTIC = "haptic"
    AR = "ar"
    VR = "vr"
    AMBIENT = "ambient"

class InteractionContext(Enum):
    """Enumeration of interaction contexts."""
    INDUSTRIAL = "industrial"
    OFFICE = "office"
    FIELD = "field"
    MOBILE = "mobile"
    HOME = "home"
    MEETING = "meeting"
    EMERGENCY = "emergency"

@dataclass
class InteractionEvent:
    """Data class representing an interaction event."""
    id: str
    type: str
    source: str
    target: str
    data: Dict[str, Any]
    mode: InteractionMode
    modality: InteractionModality
    context: InteractionContext
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the interaction event to a dictionary."""
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "target": self.target,
            "data": self.data,
            "mode": self.mode.value,
            "modality": self.modality.value,
            "context": self.context.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionEvent':
        """Create interaction event from a dictionary."""
        return cls(
            id=data["id"],
            type=data["type"],
            source=data["source"],
            target=data["target"],
            data=data["data"],
            mode=InteractionMode(data["mode"]),
            modality=InteractionModality(data["modality"]),
            context=InteractionContext(data["context"]),
            timestamp=data.get("timestamp", time.time()),
            metadata=data.get("metadata", {})
        )

class InteractionOrchestrator:
    """
    Provides orchestration of interactions between users, agents, and the system.
    
    This class provides:
    - Multi-modal interaction handling
    - Context-aware interaction routing
    - Interaction mode switching
    - Interaction history tracking
    - Interaction event dispatching
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the Interaction Orchestrator.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        self.event_handlers: Dict[str, List[Callable[[InteractionEvent], None]]] = {}
        self.interaction_history: List[InteractionEvent] = []
        self.current_mode: InteractionMode = InteractionMode.DIRECT
        self.current_modality: InteractionModality = InteractionModality.TOUCH
        self.current_context: InteractionContext = InteractionContext.INDUSTRIAL
        self.running = False
        self.worker_thread = None
        self.event_queue = queue.Queue()
        
        # Initialize from config if provided
        if config:
            self.current_mode = InteractionMode(config.get("default_mode", InteractionMode.DIRECT.value))
            self.current_modality = InteractionModality(config.get("default_modality", InteractionModality.TOUCH.value))
            self.current_context = InteractionContext(config.get("default_context", InteractionContext.INDUSTRIAL.value))
            
        self.logger.info("Interaction Orchestrator initialized")
        
    def start(self) -> bool:
        """
        Start the Interaction Orchestrator.
        
        Returns:
            True if started successfully, False otherwise
        """
        if self.running:
            self.logger.warning("Interaction Orchestrator already running")
            return False
            
        self.running = True
        self.worker_thread = threading.Thread(target=self._event_worker, daemon=True)
        self.worker_thread.start()
        
        self.logger.info("Interaction Orchestrator started")
        return True
        
    def stop(self) -> bool:
        """
        Stop the Interaction Orchestrator.
        
        Returns:
            True if stopped successfully, False otherwise
        """
        if not self.running:
            self.logger.warning("Interaction Orchestrator not running")
            return False
            
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
            
        self.logger.info("Interaction Orchestrator stopped")
        return True
        
    def _event_worker(self) -> None:
        """
        Worker thread for processing interaction events.
        """
        self.logger.info("Event worker thread started")
        
        while self.running:
            try:
                event = self.event_queue.get(timeout=1.0)
                self._process_event(event)
                self.event_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                self.logger.error(f"Error processing event: {e}")
                
        self.logger.info("Event worker thread stopped")
        
    def _process_event(self, event: InteractionEvent) -> None:
        """
        Process interaction event.
        
        Args:
            event: Interaction event to process
        """
        # Add to history
        self.interaction_history.append(event)
        
        # Limit history size
        max_history = self.config.get("max_history_size", 1000)
        if len(self.interaction_history) > max_history:
            self.interaction_history = self.interaction_history[-max_history:]
            
        # Notify event handlers
        event_type = event.type
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error in event handler for {event_type}: {e}")
                    
        # Notify wildcard handlers
        if "*" in self.event_handlers:
            for handler in self.event_handlers["*"]:
                try:
                    handler(event)
                except Exception as e:
                    self.logger.error(f"Error in wildcard event handler: {e}")
                    
    def register_event_handler(self, event_type: str, handler: Callable[[InteractionEvent], None]) -> bool:
        """
        Register an event handler.
        
        Args:
            event_type: Event type to handle, or "*" for all events
            handler: Handler function
            
        Returns:
            True if the handler was registered, False otherwise
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
            
        self.event_handlers[event_type].append(handler)
        self.logger.debug(f"Registered event handler for {event_type}")
        
        return True
        
    def unregister_event_handler(self, event_type: str, handler: Callable[[InteractionEvent], None]) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event_type: Event type the handler was registered for, or "*" for all events
            handler: Handler function to unregister
            
        Returns:
            True if the handler was unregistered, False otherwise
        """
        if event_type not in self.event_handlers:
            return False
            
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
            self.logger.debug(f"Unregistered event handler for {event_type}")
            
            # Clean up empty handler lists
            if not self.event_handlers[event_type]:
                del self.event_handlers[event_type]
                
            return True
            
        return False
        
    def dispatch_event(self, event_type: str, source: str, target: str, data: Dict[str, Any],
                     mode: Optional[InteractionMode] = None,
                     modality: Optional[InteractionModality] = None,
                     context: Optional[InteractionContext] = None,
                     metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Dispatch an interaction event.
        
        Args:
            event_type: Event type
            source: Event source
            target: Event target
            data: Event data
            mode: Interaction mode, or None to use current mode
            modality: Interaction modality, or None to use current modality
            context: Interaction context, or None to use current context
            metadata: Optional metadata
            
        Returns:
            Event ID
        """
        event_id = f"evt_{int(time.time() * 1000)}_{source}_{target}_{event_type}"
        
        # Create interaction event
        event = InteractionEvent(
            id=event_id,
            type=event_type,
            source=source,
            target=target,
            data=data,
            mode=mode or self.current_mode,
            modality=modality or self.current_modality,
            context=context or self.current_context,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        
        # Queue for processing
        self.event_queue.put(event)
        
        return event_id
        
    def set_interaction_mode(self, mode: InteractionMode) -> None:
        """
        Set the current interaction mode.
        
        Args:
            mode: Interaction mode
        """
        old_mode = self.current_mode
        self.current_mode = mode
        
        # Dispatch mode change event
        self.dispatch_event(
            event_type="interaction.mode.changed",
            source="system",
            target="*",
            data={
                "old_mode": old_mode.value,
                "new_mode": mode.value
            }
        )
        
        self.logger.info(f"Interaction mode changed from {old_mode.value} to {mode.value}")
        
    def set_interaction_modality(self, modality: InteractionModality) -> None:
        """
        Set the current interaction modality.
        
        Args:
            modality: Interaction modality
        """
        old_modality = self.current_modality
        self.current_modality = modality
        
        # Dispatch modality change event
        self.dispatch_event(
            event_type="interaction.modality.changed",
            source="system",
            target="*",
            data={
                "old_modality": old_modality.value,
                "new_modality": modality.value
            }
        )
        
        self.logger.info(f"Interaction modality changed from {old_modality.value} to {modality.value}")
        
    def set_interaction_context(self, context: InteractionContext) -> None:
        """
        Set the current interaction context.
        
        Args:
            context: Interaction context
        """
        old_context = self.current_context
        self.current_context = context
        
        # Dispatch context change event
        self.dispatch_event(
            event_type="interaction.context.changed",
            source="system",
            target="*",
            data={
                "old_context": old_context.value,
                "new_context": context.value
            }
        )
        
        self.logger.info(f"Interaction context changed from {old_context.value} to {context.value}")
        
    def get_interaction_mode(self) -> InteractionMode:
        """
        Get the current interaction mode.
        
        Returns:
            Current interaction mode
        """
        return self.current_mode
        
    def get_interaction_modality(self) -> InteractionModality:
        """
        Get the current interaction modality.
        
        Returns:
            Current interaction modality
        """
        return self.current_modality
        
    def get_interaction_context(self) -> InteractionContext:
        """
        Get the current interaction context.
        
        Returns:
            Current interaction context
        """
        return self.current_context
        
    def get_interaction_history(self, limit: Optional[int] = None) -> List[InteractionEvent]:
        """
        Get interaction history.
        
        Args:
            limit: Optional limit on number of events to return
            
        Returns:
            List of interaction events
        """
        if limit is None:
            return list(self.interaction_history)
            
        return list(self.interaction_history[-limit:])
        
    def get_interaction_history_for_source(self, source: str, limit: Optional[int] = None) -> List[InteractionEvent]:
        """
        Get interaction history for a specific source.
        
        Args:
            source: Source to filter by
            limit: Optional limit on number of events to return
            
        Returns:
            List of interaction events
        """
        events = [event for event in self.interaction_history if event.source == source]
        
        if limit is None:
            return events
            
        return events[-limit:]
        
    def get_interaction_history_for_target(self, target: str, limit: Optional[int] = None) -> List[InteractionEvent]:
        """
        Get interaction history for a specific target.
        
        Args:
            target: Target to filter by
            limit: Optional limit on number of events to return
            
        Returns:
            List of interaction events
        """
        events = [event for event in self.interaction_history if event.target == target]
        
        if limit is None:
            return events
            
        return events[-limit:]
        
    def get_interaction_history_for_type(self, event_type: str, limit: Optional[int] = None) -> List[InteractionEvent]:
        """
        Get interaction history for a specific event type.
        
        Args:
            event_type: Event type to filter by
            limit: Optional limit on number of events to return
            
        Returns:
            List of interaction events
        """
        events = [event for event in self.interaction_history if event.type == event_type]
        
        if limit is None:
            return events
            
        return events[-limit:]
        
    def clear_interaction_history(self) -> None:
        """
        Clear interaction history.
        """
        self.interaction_history = []
        self.logger.info("Interaction history cleared")
        
    def get_recommended_interaction_mode(self, context: Optional[InteractionContext] = None) -> InteractionMode:
        """
        Get the recommended interaction mode for the current or specified context.
        
        Args:
            context: Optional context to get recommendation for
            
        Returns:
            Recommended interaction mode
        """
        ctx = context or self.current_context
        
        # These are example recommendations based on context
        # In a real implementation, this would be more sophisticated
        if ctx == InteractionContext.INDUSTRIAL:
            return InteractionMode.DIRECT
        elif ctx == InteractionContext.FIELD:
            return InteractionMode.MIXED
        elif ctx == InteractionContext.MOBILE:
            return InteractionMode.CONVERSATIONAL
        elif ctx == InteractionContext.EMERGENCY:
            return InteractionMode.AMBIENT
        else:
            return InteractionMode.DIRECT
            
    def get_recommended_interaction_modality(self, context: Optional[InteractionContext] = None,
                                          mode: Optional[InteractionMode] = None) -> InteractionModality:
        """
        Get the recommended interaction modality for the current or specified context and mode.
        
        Args:
            context: Optional context to get recommendation for
            mode: Optional mode to get recommendation for
            
        Returns:
            Recommended interaction modality
        """
        ctx = context or self.current_context
        md = mode or self.current_mode
        
        # These are example recommendations based on context and mode
        # In a real implementation, this would be more sophisticated
        if ctx == InteractionContext.INDUSTRIAL:
            if md == InteractionMode.DIRECT:
                return InteractionModality.TOUCH
            elif md == InteractionMode.CONVERSATIONAL:
                return InteractionModality.VOICE
            else:
                return InteractionModality.TOUCH
        elif ctx == InteractionContext.FIELD:
            if md == InteractionMode.DIRECT:
                return InteractionModality.TOUCH
            elif md == InteractionMode.CONVERSATIONAL:
                return InteractionModality.VOICE
            elif md == InteractionMode.AMBIENT:
                return InteractionModality.AR
            else:
                return InteractionModality.MIXED
        elif ctx == InteractionContext.MOBILE:
            if md == InteractionMode.DIRECT:
                return InteractionModality.TOUCH
            elif md == InteractionMode.CONVERSATIONAL:
                return InteractionModality.VOICE
            else:
                return InteractionModality.TOUCH
        elif ctx == InteractionContext.EMERGENCY:
            return InteractionModality.VOICE
        else:
            return InteractionModality.TOUCH

# Example Usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create Interaction Orchestrator
    orchestrator = InteractionOrchestrator()
    orchestrator.start()
    
    # Register event handler
    def handle_interaction(event):
        print(f"Received interaction event: {event.type} from {event.source} to {event.target}")
        
    orchestrator.register_event_handler("user.input", handle_interaction)
    
    # Dispatch event
    orchestrator.dispatch_event(
        event_type="user.input",
        source="user123",
        target="system",
        data={
            "input_type": "button_press",
            "button_id": "submit",
            "screen": "login"
        }
    )
    
    # Change interaction mode
    orchestrator.set_interaction_mode(InteractionMode.CONVERSATIONAL)
    
    # Get interaction history
    history = orchestrator.get_interaction_history(limit=10)
    print(f"Interaction history: {len(history)} events")
    
    # Clean up
    orchestrator.stop()
