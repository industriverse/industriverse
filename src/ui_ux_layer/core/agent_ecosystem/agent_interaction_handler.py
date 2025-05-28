"""
Agent Interaction Handler Module for the UI/UX Layer of Industriverse

This module handles interactions between agents and users in the UI/UX Layer,
providing a comprehensive set of interaction patterns, event handling, and
response management for agent-based interfaces.

The Agent Interaction Handler is responsible for:
1. Processing user inputs directed at agents
2. Managing agent responses and feedback
3. Coordinating multi-agent interactions
4. Handling interaction context and history
5. Providing interaction analytics and insights

This module works closely with the Agent Interaction Protocol to ensure
consistent and intuitive agent interactions across the UI/UX Layer.
"""

import logging
import uuid
import time
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import json

from ..universal_skin.shell_state_manager import ShellStateManager
from ..universal_skin.interaction_mode_manager import InteractionModeManager
from ..context_engine.context_awareness_engine import ContextAwarenessEngine
from .avatar_expression_engine import AvatarExpressionEngine
from .agent_interaction_protocol import AgentInteractionProtocol, InteractionType, InteractionPriority
from .avatar_personality_engine import AvatarPersonalityEngine
from .agent_state_visualizer import AgentStateVisualizer

logger = logging.getLogger(__name__)

class InteractionState(Enum):
    """Enumeration of possible interaction states."""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    ERROR = "error"
    WAITING = "waiting"
    COMPLETED = "completed"


class InteractionMode(Enum):
    """Enumeration of possible interaction modes."""
    TEXT = "text"
    VOICE = "voice"
    GESTURE = "gesture"
    MIXED = "mixed"
    AMBIENT = "ambient"
    HAPTIC = "haptic"
    AR = "ar"
    VR = "vr"


class AgentInteractionHandler:
    """
    Handles interactions between agents and users in the UI/UX Layer.
    
    This class provides methods for processing user inputs, managing agent responses,
    coordinating multi-agent interactions, and handling interaction context and history.
    """

    def __init__(
        self,
        agent_interaction_protocol: AgentInteractionProtocol,
        avatar_expression_engine: AvatarExpressionEngine,
        avatar_personality_engine: AvatarPersonalityEngine,
        agent_state_visualizer: AgentStateVisualizer,
        context_awareness_engine: ContextAwarenessEngine,
        shell_state_manager: ShellStateManager,
        interaction_mode_manager: InteractionModeManager
    ):
        """
        Initialize the AgentInteractionHandler.
        
        Args:
            agent_interaction_protocol: Protocol for agent interactions
            avatar_expression_engine: Engine for avatar expressions
            avatar_personality_engine: Engine for avatar personalities
            agent_state_visualizer: Visualizer for agent states
            context_awareness_engine: Engine for context awareness
            shell_state_manager: Manager for shell state
            interaction_mode_manager: Manager for interaction modes
        """
        self.agent_interaction_protocol = agent_interaction_protocol
        self.avatar_expression_engine = avatar_expression_engine
        self.avatar_personality_engine = avatar_personality_engine
        self.agent_state_visualizer = agent_state_visualizer
        self.context_awareness_engine = context_awareness_engine
        self.shell_state_manager = shell_state_manager
        self.interaction_mode_manager = interaction_mode_manager
        
        # Initialize interaction state and history
        self.interaction_state = InteractionState.IDLE
        self.interaction_history = []
        self.active_interactions = {}
        self.interaction_callbacks = {}
        self.interaction_handlers = {}
        
        # Register default interaction handlers
        self._register_default_handlers()
        
        logger.info("AgentInteractionHandler initialized")

    def _register_default_handlers(self):
        """Register default interaction handlers for different interaction types."""
        self.register_interaction_handler(InteractionType.QUERY, self._handle_query)
        self.register_interaction_handler(InteractionType.COMMAND, self._handle_command)
        self.register_interaction_handler(InteractionType.NOTIFICATION, self._handle_notification)
        self.register_interaction_handler(InteractionType.FEEDBACK, self._handle_feedback)
        self.register_interaction_handler(InteractionType.ERROR, self._handle_error)
        self.register_interaction_handler(InteractionType.STATUS, self._handle_status)
        self.register_interaction_handler(InteractionType.AMBIENT, self._handle_ambient)

    def register_interaction_handler(self, interaction_type: InteractionType, handler: Callable):
        """
        Register a handler for a specific interaction type.
        
        Args:
            interaction_type: Type of interaction to handle
            handler: Function to handle the interaction
        """
        self.interaction_handlers[interaction_type] = handler
        logger.debug(f"Registered handler for interaction type: {interaction_type}")

    def process_user_input(
        self,
        input_data: Any,
        agent_id: str,
        interaction_type: InteractionType = InteractionType.QUERY,
        interaction_mode: InteractionMode = InteractionMode.TEXT,
        context: Optional[Dict[str, Any]] = None,
        priority: InteractionPriority = InteractionPriority.NORMAL,
        callback: Optional[Callable] = None
    ) -> str:
        """
        Process user input directed at an agent.
        
        Args:
            input_data: User input data (text, voice, gesture, etc.)
            agent_id: ID of the target agent
            interaction_type: Type of interaction
            interaction_mode: Mode of interaction
            context: Additional context for the interaction
            priority: Priority of the interaction
            callback: Optional callback function to call when interaction completes
            
        Returns:
            Interaction ID for tracking
        """
        # Generate unique interaction ID
        interaction_id = str(uuid.uuid4())
        
        # Update interaction state
        self.interaction_state = InteractionState.PROCESSING
        
        # Create interaction context if not provided
        if context is None:
            context = {}
        
        # Enrich context with current user context
        user_context = self.context_awareness_engine.get_user_context()
        context.update(user_context)
        
        # Create interaction record
        interaction = {
            "id": interaction_id,
            "agent_id": agent_id,
            "input_data": input_data,
            "interaction_type": interaction_type,
            "interaction_mode": interaction_mode,
            "context": context,
            "priority": priority,
            "timestamp": time.time(),
            "state": InteractionState.PROCESSING,
            "response": None
        }
        
        # Store interaction in active interactions
        self.active_interactions[interaction_id] = interaction
        
        # Store callback if provided
        if callback:
            self.interaction_callbacks[interaction_id] = callback
        
        # Add to interaction history
        self.interaction_history.append(interaction)
        
        # Update agent state
        self.agent_state_visualizer.update_agent_state(agent_id, "processing_interaction", {
            "interaction_id": interaction_id,
            "interaction_type": interaction_type.value
        })
        
        # Update avatar expression based on interaction
        self.avatar_expression_engine.express_emotion(
            agent_id,
            "attentive",
            intensity=0.7,
            duration=2.0
        )
        
        # Process interaction based on type
        if interaction_type in self.interaction_handlers:
            self.interaction_handlers[interaction_type](interaction)
        else:
            logger.warning(f"No handler registered for interaction type: {interaction_type}")
            self._handle_unknown(interaction)
        
        return interaction_id

    def _handle_query(self, interaction: Dict[str, Any]):
        """
        Handle query interaction type.
        
        Args:
            interaction: Interaction data
        """
        agent_id = interaction["agent_id"]
        input_data = interaction["input_data"]
        interaction_id = interaction["id"]
        
        # Forward query to agent interaction protocol
        self.agent_interaction_protocol.send_interaction(
            agent_id=agent_id,
            interaction_type=InteractionType.QUERY,
            content=input_data,
            context=interaction["context"],
            priority=interaction["priority"],
            callback=lambda response: self._process_response(interaction_id, response)
        )

    def _handle_command(self, interaction: Dict[str, Any]):
        """
        Handle command interaction type.
        
        Args:
            interaction: Interaction data
        """
        agent_id = interaction["agent_id"]
        input_data = interaction["input_data"]
        interaction_id = interaction["id"]
        
        # Forward command to agent interaction protocol
        self.agent_interaction_protocol.send_interaction(
            agent_id=agent_id,
            interaction_type=InteractionType.COMMAND,
            content=input_data,
            context=interaction["context"],
            priority=interaction["priority"],
            callback=lambda response: self._process_response(interaction_id, response)
        )

    def _handle_notification(self, interaction: Dict[str, Any]):
        """
        Handle notification interaction type.
        
        Args:
            interaction: Interaction data
        """
        agent_id = interaction["agent_id"]
        input_data = interaction["input_data"]
        interaction_id = interaction["id"]
        
        # Forward notification to agent interaction protocol
        self.agent_interaction_protocol.send_interaction(
            agent_id=agent_id,
            interaction_type=InteractionType.NOTIFICATION,
            content=input_data,
            context=interaction["context"],
            priority=interaction["priority"],
            callback=lambda response: self._process_response(interaction_id, response)
        )

    def _handle_feedback(self, interaction: Dict[str, Any]):
        """
        Handle feedback interaction type.
        
        Args:
            interaction: Interaction data
        """
        agent_id = interaction["agent_id"]
        input_data = interaction["input_data"]
        interaction_id = interaction["id"]
        
        # Forward feedback to agent interaction protocol
        self.agent_interaction_protocol.send_interaction(
            agent_id=agent_id,
            interaction_type=InteractionType.FEEDBACK,
            content=input_data,
            context=interaction["context"],
            priority=interaction["priority"],
            callback=lambda response: self._process_response(interaction_id, response)
        )

    def _handle_error(self, interaction: Dict[str, Any]):
        """
        Handle error interaction type.
        
        Args:
            interaction: Interaction data
        """
        agent_id = interaction["agent_id"]
        input_data = interaction["input_data"]
        interaction_id = interaction["id"]
        
        # Update avatar expression to show concern
        self.avatar_expression_engine.express_emotion(
            agent_id,
            "concerned",
            intensity=0.8,
            duration=3.0
        )
        
        # Forward error to agent interaction protocol
        self.agent_interaction_protocol.send_interaction(
            agent_id=agent_id,
            interaction_type=InteractionType.ERROR,
            content=input_data,
            context=interaction["context"],
            priority=interaction["priority"],
            callback=lambda response: self._process_response(interaction_id, response)
        )

    def _handle_status(self, interaction: Dict[str, Any]):
        """
        Handle status interaction type.
        
        Args:
            interaction: Interaction data
        """
        agent_id = interaction["agent_id"]
        interaction_id = interaction["id"]
        
        # Get agent status
        agent_status = self.agent_state_visualizer.get_agent_state(agent_id)
        
        # Process response immediately
        self._process_response(interaction_id, {
            "status": "success",
            "agent_status": agent_status
        })

    def _handle_ambient(self, interaction: Dict[str, Any]):
        """
        Handle ambient interaction type.
        
        Args:
            interaction: Interaction data
        """
        agent_id = interaction["agent_id"]
        input_data = interaction["input_data"]
        interaction_id = interaction["id"]
        
        # Forward ambient interaction to agent interaction protocol
        self.agent_interaction_protocol.send_interaction(
            agent_id=agent_id,
            interaction_type=InteractionType.AMBIENT,
            content=input_data,
            context=interaction["context"],
            priority=interaction["priority"],
            callback=lambda response: self._process_response(interaction_id, response)
        )

    def _handle_unknown(self, interaction: Dict[str, Any]):
        """
        Handle unknown interaction type.
        
        Args:
            interaction: Interaction data
        """
        interaction_id = interaction["id"]
        agent_id = interaction["agent_id"]
        
        # Update avatar expression to show confusion
        self.avatar_expression_engine.express_emotion(
            agent_id,
            "confused",
            intensity=0.6,
            duration=2.0
        )
        
        # Process response with error
        self._process_response(interaction_id, {
            "status": "error",
            "message": f"Unknown interaction type: {interaction['interaction_type']}"
        })

    def _process_response(self, interaction_id: str, response: Dict[str, Any]):
        """
        Process agent response to an interaction.
        
        Args:
            interaction_id: ID of the interaction
            response: Response data from the agent
        """
        if interaction_id not in self.active_interactions:
            logger.warning(f"Received response for unknown interaction: {interaction_id}")
            return
        
        # Get interaction data
        interaction = self.active_interactions[interaction_id]
        agent_id = interaction["agent_id"]
        
        # Update interaction with response
        interaction["response"] = response
        interaction["state"] = InteractionState.COMPLETED
        
        # Update agent state
        self.agent_state_visualizer.update_agent_state(agent_id, "interaction_completed", {
            "interaction_id": interaction_id,
            "response_status": response.get("status", "unknown")
        })
        
        # Update avatar expression based on response
        if response.get("status") == "success":
            self.avatar_expression_engine.express_emotion(
                agent_id,
                "satisfied",
                intensity=0.6,
                duration=1.5
            )
        elif response.get("status") == "error":
            self.avatar_expression_engine.express_emotion(
                agent_id,
                "apologetic",
                intensity=0.7,
                duration=2.0
            )
        
        # Call callback if registered
        if interaction_id in self.interaction_callbacks:
            callback = self.interaction_callbacks[interaction_id]
            try:
                callback(response)
            except Exception as e:
                logger.error(f"Error in interaction callback: {e}")
            
            # Remove callback after calling
            del self.interaction_callbacks[interaction_id]
        
        # Remove from active interactions
        del self.active_interactions[interaction_id]
        
        # Update interaction state if no active interactions
        if not self.active_interactions:
            self.interaction_state = InteractionState.IDLE

    def get_interaction_history(
        self,
        agent_id: Optional[str] = None,
        limit: int = 10,
        interaction_type: Optional[InteractionType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get interaction history, optionally filtered by agent ID and interaction type.
        
        Args:
            agent_id: Optional agent ID to filter by
            limit: Maximum number of interactions to return
            interaction_type: Optional interaction type to filter by
            
        Returns:
            List of interaction records
        """
        # Filter history by agent ID if provided
        filtered_history = self.interaction_history
        
        if agent_id:
            filtered_history = [i for i in filtered_history if i["agent_id"] == agent_id]
        
        if interaction_type:
            filtered_history = [i for i in filtered_history if i["interaction_type"] == interaction_type]
        
        # Sort by timestamp (newest first) and limit
        sorted_history = sorted(filtered_history, key=lambda i: i["timestamp"], reverse=True)
        limited_history = sorted_history[:limit]
        
        return limited_history

    def get_interaction_state(self) -> InteractionState:
        """
        Get the current interaction state.
        
        Returns:
            Current interaction state
        """
        return self.interaction_state

    def get_active_interactions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active interactions.
        
        Returns:
            Dictionary of active interactions
        """
        return self.active_interactions

    def cancel_interaction(self, interaction_id: str) -> bool:
        """
        Cancel an active interaction.
        
        Args:
            interaction_id: ID of the interaction to cancel
            
        Returns:
            True if interaction was cancelled, False otherwise
        """
        if interaction_id not in self.active_interactions:
            logger.warning(f"Cannot cancel unknown interaction: {interaction_id}")
            return False
        
        # Get interaction data
        interaction = self.active_interactions[interaction_id]
        agent_id = interaction["agent_id"]
        
        # Update interaction state
        interaction["state"] = InteractionState.COMPLETED
        interaction["response"] = {
            "status": "cancelled",
            "message": "Interaction cancelled by user"
        }
        
        # Update agent state
        self.agent_state_visualizer.update_agent_state(agent_id, "interaction_cancelled", {
            "interaction_id": interaction_id
        })
        
        # Update avatar expression
        self.avatar_expression_engine.express_emotion(
            agent_id,
            "neutral",
            intensity=0.5,
            duration=1.0
        )
        
        # Remove from active interactions
        del self.active_interactions[interaction_id]
        
        # Update interaction state if no active interactions
        if not self.active_interactions:
            self.interaction_state = InteractionState.IDLE
        
        return True

    def process_multi_agent_interaction(
        self,
        input_data: Any,
        agent_ids: List[str],
        interaction_type: InteractionType = InteractionType.QUERY,
        interaction_mode: InteractionMode = InteractionMode.TEXT,
        context: Optional[Dict[str, Any]] = None,
        priority: InteractionPriority = InteractionPriority.NORMAL,
        callback: Optional[Callable] = None
    ) -> Dict[str, str]:
        """
        Process user input directed at multiple agents.
        
        Args:
            input_data: User input data (text, voice, gesture, etc.)
            agent_ids: List of target agent IDs
            interaction_type: Type of interaction
            interaction_mode: Mode of interaction
            context: Additional context for the interaction
            priority: Priority of the interaction
            callback: Optional callback function to call when all interactions complete
            
        Returns:
            Dictionary mapping agent IDs to interaction IDs
        """
        interaction_ids = {}
        multi_interaction_id = str(uuid.uuid4())
        
        # Create a counter for tracking completed interactions
        completed_count = 0
        total_count = len(agent_ids)
        responses = {}
        
        # Define callback for individual interactions
        def individual_callback(agent_id, response):
            nonlocal completed_count
            responses[agent_id] = response
            completed_count += 1
            
            # If all interactions are complete, call the main callback
            if completed_count == total_count and callback:
                callback(responses)
        
        # Process interaction for each agent
        for agent_id in agent_ids:
            # Create individual callback for this agent
            agent_callback = lambda response, aid=agent_id: individual_callback(aid, response)
            
            # Process input for this agent
            interaction_id = self.process_user_input(
                input_data=input_data,
                agent_id=agent_id,
                interaction_type=interaction_type,
                interaction_mode=interaction_mode,
                context=context,
                priority=priority,
                callback=agent_callback
            )
            
            interaction_ids[agent_id] = interaction_id
        
        return interaction_ids

    def get_interaction_analytics(
        self,
        agent_id: Optional[str] = None,
        time_range: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Get analytics for interactions.
        
        Args:
            agent_id: Optional agent ID to filter by
            time_range: Optional time range (start_time, end_time) to filter by
            
        Returns:
            Dictionary of interaction analytics
        """
        # Filter history by agent ID if provided
        filtered_history = self.interaction_history
        
        if agent_id:
            filtered_history = [i for i in filtered_history if i["agent_id"] == agent_id]
        
        if time_range:
            start_time, end_time = time_range
            filtered_history = [
                i for i in filtered_history 
                if start_time <= i["timestamp"] <= end_time
            ]
        
        # Calculate analytics
        total_interactions = len(filtered_history)
        
        if total_interactions == 0:
            return {
                "total_interactions": 0,
                "interaction_types": {},
                "interaction_modes": {},
                "response_statuses": {},
                "average_response_time": 0
            }
        
        # Count interaction types
        interaction_types = {}
        for interaction in filtered_history:
            interaction_type = interaction["interaction_type"].value
            interaction_types[interaction_type] = interaction_types.get(interaction_type, 0) + 1
        
        # Count interaction modes
        interaction_modes = {}
        for interaction in filtered_history:
            interaction_mode = interaction["interaction_mode"].value
            interaction_modes[interaction_mode] = interaction_modes.get(interaction_mode, 0) + 1
        
        # Count response statuses
        response_statuses = {}
        response_times = []
        
        for interaction in filtered_history:
            if "response" in interaction and interaction["response"]:
                status = interaction["response"].get("status", "unknown")
                response_statuses[status] = response_statuses.get(status, 0) + 1
                
                # Calculate response time if timestamp is available
                if "timestamp" in interaction and "response_timestamp" in interaction:
                    response_time = interaction["response_timestamp"] - interaction["timestamp"]
                    response_times.append(response_time)
        
        # Calculate average response time
        average_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "total_interactions": total_interactions,
            "interaction_types": interaction_types,
            "interaction_modes": interaction_modes,
            "response_statuses": response_statuses,
            "average_response_time": average_response_time
        }

    def export_interaction_history(
        self,
        format: str = "json",
        agent_id: Optional[str] = None,
        time_range: Optional[tuple] = None
    ) -> str:
        """
        Export interaction history in specified format.
        
        Args:
            format: Export format ("json" or "csv")
            agent_id: Optional agent ID to filter by
            time_range: Optional time range (start_time, end_time) to filter by
            
        Returns:
            Exported interaction history as string
        """
        # Filter history by agent ID if provided
        filtered_history = self.interaction_history
        
        if agent_id:
            filtered_history = [i for i in filtered_history if i["agent_id"] == agent_id]
        
        if time_range:
            start_time, end_time = time_range
            filtered_history = [
                i for i in filtered_history 
                if start_time <= i["timestamp"] <= end_time
            ]
        
        # Export in specified format
        if format.lower() == "json":
            # Convert enum values to strings for JSON serialization
            serializable_history = []
            for interaction in filtered_history:
                serializable_interaction = interaction.copy()
                
                if "interaction_type" in serializable_interaction:
                    serializable_interaction["interaction_type"] = serializable_interaction["interaction_type"].value
                
                if "interaction_mode" in serializable_interaction:
                    serializable_interaction["interaction_mode"] = serializable_interaction["interaction_mode"].value
                
                if "state" in serializable_interaction:
                    serializable_interaction["state"] = serializable_interaction["state"].value
                
                if "priority" in serializable_interaction:
                    serializable_interaction["priority"] = serializable_interaction["priority"].value
                
                serializable_history.append(serializable_interaction)
            
            return json.dumps(serializable_history, indent=2)
        
        elif format.lower() == "csv":
            # Create CSV header
            csv_lines = ["id,agent_id,interaction_type,interaction_mode,timestamp,state,response_status"]
            
            # Add data rows
            for interaction in filtered_history:
                interaction_id = interaction.get("id", "")
                agent_id = interaction.get("agent_id", "")
                interaction_type = interaction.get("interaction_type", "").value if interaction.get("interaction_type") else ""
                interaction_mode = interaction.get("interaction_mode", "").value if interaction.get("interaction_mode") else ""
                timestamp = interaction.get("timestamp", "")
                state = interaction.get("state", "").value if interaction.get("state") else ""
                
                response_status = ""
                if "response" in interaction and interaction["response"]:
                    response_status = interaction["response"].get("status", "")
                
                csv_line = f"{interaction_id},{agent_id},{interaction_type},{interaction_mode},{timestamp},{state},{response_status}"
                csv_lines.append(csv_line)
            
            return "\n".join(csv_lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")
