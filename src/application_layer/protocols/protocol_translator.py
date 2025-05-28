"""
Protocol Translator for Application Layer.

This module provides bidirectional translation between MCP and A2A protocols,
ensuring context preservation and consistent identity mapping.
"""

import logging
import json
import time
import uuid
from typing import Dict, Any, List, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProtocolTranslator:
    """
    Protocol translator for the Application Layer.
    """
    
    def __init__(self, agent_core):
        """
        Initialize the Protocol Translator.
        
        Args:
            agent_core: Reference to the agent core
        """
        self.agent_core = agent_core
        self.translation_history = []
        self.max_history = 100
        self.context_cache = {}
        
        logger.info("Protocol Translator initialized")
    
    def mcp_to_a2a(self, mcp_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate MCP event to A2A task.
        
        Args:
            mcp_event: MCP event
            
        Returns:
            A2A task
        """
        # Log translation
        logger.info(f"Translating MCP event to A2A task: {mcp_event.get('event_type', 'unknown')}")
        
        # Extract event information
        event_type = mcp_event.get("event_type", "")
        event_data = mcp_event.get("event_data", {})
        event_id = mcp_event.get("event_id", str(uuid.uuid4()))
        
        # Create context key for this translation
        context_key = f"mcp_to_a2a_{event_id}"
        
        # Store original event in context cache
        self.context_cache[context_key] = {
            "original_event": mcp_event,
            "timestamp": time.time()
        }
        
        # Map MCP event type to A2A task type
        task_type = self._map_mcp_event_to_a2a_task(event_type)
        
        # Transform event data to task data
        task_data = self._transform_mcp_data_to_a2a(event_type, event_data)
        
        # Add context reference
        task_data["_context_ref"] = context_key
        
        # Create A2A task
        a2a_task = {
            "task_type": task_type,
            "task_data": task_data,
            "task_id": f"task-{event_id}",
            "source_protocol": "mcp",
            "source_event_id": event_id,
            "timestamp": time.time()
        }
        
        # Add to translation history
        self._add_to_history("mcp_to_a2a", mcp_event, a2a_task)
        
        return a2a_task
    
    def a2a_to_mcp(self, a2a_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate A2A task to MCP event.
        
        Args:
            a2a_task: A2A task
            
        Returns:
            MCP event
        """
        # Log translation
        logger.info(f"Translating A2A task to MCP event: {a2a_task.get('task_type', 'unknown')}")
        
        # Extract task information
        task_type = a2a_task.get("task_type", "")
        task_data = a2a_task.get("task_data", {})
        task_id = a2a_task.get("task_id", "")
        
        # Create context key for this translation
        context_key = f"a2a_to_mcp_{task_id}"
        
        # Store original task in context cache
        self.context_cache[context_key] = {
            "original_task": a2a_task,
            "timestamp": time.time()
        }
        
        # Map A2A task type to MCP event type
        event_type = self._map_a2a_task_to_mcp_event(task_type)
        
        # Transform task data to event data
        event_data = self._transform_a2a_data_to_mcp(task_type, task_data)
        
        # Add context reference
        event_data["_context_ref"] = context_key
        
        # Create MCP event
        mcp_event = {
            "event_type": event_type,
            "event_data": event_data,
            "event_id": f"event-{task_id}",
            "source_protocol": "a2a",
            "source_task_id": task_id,
            "timestamp": time.time()
        }
        
        # Add to translation history
        self._add_to_history("a2a_to_mcp", a2a_task, mcp_event)
        
        return mcp_event
    
    def _map_mcp_event_to_a2a_task(self, event_type: str) -> str:
        """
        Map MCP event type to A2A task type.
        
        Args:
            event_type: MCP event type
            
        Returns:
            A2A task type
        """
        # Define mapping
        mapping = {
            "observe": "status_request",
            "simulate": "simulation_request",
            "recommend": "recommendation_request",
            "act": "action_request",
            "application/user_journey": "user_journey_request",
            "application_health/predict_issue": "health_prediction_request",
            "application/self_optimization": "optimization_request"
        }
        
        # Return mapped type or default
        return mapping.get(event_type, "generic_request")
    
    def _map_a2a_task_to_mcp_event(self, task_type: str) -> str:
        """
        Map A2A task type to MCP event type.
        
        Args:
            task_type: A2A task type
            
        Returns:
            MCP event type
        """
        # Define mapping
        mapping = {
            "status_request": "observe",
            "simulation_request": "simulate",
            "recommendation_request": "recommend",
            "action_request": "act",
            "user_journey_request": "application/user_journey",
            "health_prediction_request": "application_health/predict_issue",
            "optimization_request": "application/self_optimization",
            "workflow_execution": "application/workflow_execution",
            "data_request": "application/data_request",
            "ai_inference": "application/ai_inference",
            "generate_artifact": "application/generate_artifact"
        }
        
        # Return mapped type or default
        return mapping.get(task_type, "application/generic_request")
    
    def _transform_mcp_data_to_a2a(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform MCP event data to A2A task data.
        
        Args:
            event_type: MCP event type
            event_data: MCP event data
            
        Returns:
            A2A task data
        """
        # Create base task data
        task_data = {
            "source_event_type": event_type,
            "timestamp": time.time()
        }
        
        # Transform based on event type
        if event_type == "observe":
            task_data["target"] = event_data.get("target", "")
            task_data["parameters"] = event_data.get("parameters", {})
        elif event_type == "simulate":
            task_data["target"] = event_data.get("target", "")
            task_data["simulation_parameters"] = event_data.get("simulation_parameters", {})
        elif event_type == "recommend":
            task_data["target"] = event_data.get("target", "")
            task_data["context"] = event_data.get("context", {})
        elif event_type == "act":
            task_data["target"] = event_data.get("target", "")
            task_data["action_parameters"] = event_data.get("action_parameters", {})
        elif event_type == "application/user_journey":
            task_data["action"] = event_data.get("action", "")
            task_data["journey_parameters"] = {
                "journey_type": event_data.get("journey_type", ""),
                "user_id": event_data.get("user_id", ""),
                "context": event_data.get("context", {})
            }
        elif event_type == "application_health/predict_issue":
            task_data["component_id"] = event_data.get("component_id", "")
            task_data["expected_issue_type"] = event_data.get("expected_issue_type", "")
            task_data["confidence"] = event_data.get("confidence", 0.0)
        elif event_type == "application/self_optimization":
            task_data["target"] = event_data.get("target", "")
            task_data["optimization_parameters"] = event_data.get("params", {})
        else:
            # For unknown event types, pass through all data
            task_data.update(event_data)
        
        # Add metadata
        task_data["_metadata"] = {
            "source_protocol": "mcp",
            "translation_timestamp": time.time()
        }
        
        return task_data
    
    def _transform_a2a_data_to_mcp(self, task_type: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform A2A task data to MCP event data.
        
        Args:
            task_type: A2A task type
            task_data: A2A task data
            
        Returns:
            MCP event data
        """
        # Create base event data
        event_data = {
            "source_task_type": task_type,
            "timestamp": time.time()
        }
        
        # Transform based on task type
        if task_type == "status_request":
            event_data["target"] = task_data.get("target", "")
            event_data["parameters"] = task_data.get("parameters", {})
        elif task_type == "simulation_request":
            event_data["target"] = task_data.get("target", "")
            event_data["simulation_parameters"] = task_data.get("simulation_parameters", {})
        elif task_type == "recommendation_request":
            event_data["target"] = task_data.get("target", "")
            event_data["context"] = task_data.get("context", {})
        elif task_type == "action_request":
            event_data["target"] = task_data.get("target", "")
            event_data["action_parameters"] = task_data.get("action_parameters", {})
        elif task_type == "user_journey_request":
            event_data["action"] = task_data.get("action", "")
            journey_params = task_data.get("journey_parameters", {})
            event_data["journey_type"] = journey_params.get("journey_type", "")
            event_data["user_id"] = journey_params.get("user_id", "")
            event_data["context"] = journey_params.get("context", {})
        elif task_type == "health_prediction_request":
            event_data["component_id"] = task_data.get("component_id", "")
            event_data["expected_issue_type"] = task_data.get("expected_issue_type", "")
            event_data["confidence"] = task_data.get("confidence", 0.0)
        elif task_type == "optimization_request":
            event_data["target"] = task_data.get("target", "")
            event_data["params"] = task_data.get("optimization_parameters", {})
        elif task_type == "workflow_execution":
            event_data["target"] = "workflow"
            event_data["workflow_id"] = task_data.get("workflow_id", "")
            event_data["workflow_data"] = task_data.get("workflow_data", {})
        elif task_type == "data_request":
            event_data["target"] = "data"
            event_data["query"] = task_data.get("query", {})
        elif task_type == "ai_inference":
            event_data["target"] = "ai"
            event_data["inference_params"] = task_data.get("inference_params", {})
        elif task_type == "generate_artifact":
            event_data["target"] = "generative"
            event_data["generation_params"] = task_data.get("generation_params", {})
        else:
            # For unknown task types, pass through all data
            event_data.update(task_data)
        
        # Add metadata
        event_data["_metadata"] = {
            "source_protocol": "a2a",
            "translation_timestamp": time.time()
        }
        
        return event_data
    
    def _add_to_history(self, translation_type: str, source: Dict[str, Any], target: Dict[str, Any]):
        """
        Add translation to history.
        
        Args:
            translation_type: Translation type
            source: Source data
            target: Target data
        """
        # Create history entry
        entry = {
            "translation_type": translation_type,
            "source": source,
            "target": target,
            "timestamp": time.time()
        }
        
        # Add to history
        self.translation_history.append(entry)
        
        # Trim history if needed
        if len(self.translation_history) > self.max_history:
            self.translation_history = self.translation_history[-self.max_history:]
    
    def get_translation_history(self) -> List[Dict[str, Any]]:
        """
        Get translation history.
        
        Returns:
            Translation history
        """
        return self.translation_history
    
    def get_context(self, context_key: str) -> Optional[Dict[str, Any]]:
        """
        Get context by key.
        
        Args:
            context_key: Context key
            
        Returns:
            Context or None if not found
        """
        return self.context_cache.get(context_key)
    
    def cleanup_context_cache(self, max_age_seconds: int = 3600):
        """
        Clean up context cache.
        
        Args:
            max_age_seconds: Maximum age in seconds
        """
        current_time = time.time()
        keys_to_remove = []
        
        for key, context in self.context_cache.items():
            if current_time - context.get("timestamp", 0) > max_age_seconds:
                keys_to_remove.append(key)
        
        for key in keys_to_remove:
            del self.context_cache[key]
        
        logger.info(f"Cleaned up {len(keys_to_remove)} context entries")
    
    def snapshot_context(self) -> Dict[str, Any]:
        """
        Create a snapshot of the current context cache.
        
        Returns:
            Context snapshot
        """
        return {
            "context_cache": self.context_cache,
            "snapshot_timestamp": time.time()
        }
    
    def restore_context(self, snapshot: Dict[str, Any]):
        """
        Restore context from snapshot.
        
        Args:
            snapshot: Context snapshot
        """
        if "context_cache" in snapshot:
            self.context_cache = snapshot["context_cache"]
            logger.info(f"Restored context cache from snapshot (timestamp: {snapshot.get('snapshot_timestamp', 'unknown')})")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get translator status.
        
        Returns:
            Translator status
        """
        return {
            "status": "operational",
            "translations": len(self.translation_history),
            "context_entries": len(self.context_cache)
        }
