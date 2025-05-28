"""
Protocol Conflict Resolver Agent for Industriverse Core AI Layer

This module implements the protocol conflict resolver agent for detecting and resolving
inconsistencies between MCP and A2A protocols in the Core AI Layer.
"""

import logging
import json
import asyncio
from typing import Dict, Any, Optional, List, Set, Tuple
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProtocolConflictResolverAgent:
    """
    Implements the protocol conflict resolver agent for Core AI Layer.
    Detects and resolves inconsistencies between MCP and A2A protocols.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the protocol conflict resolver agent.
        
        Args:
            config_path: Path to the configuration file (optional)
        """
        self.config_path = config_path or "config/protocol_conflict_resolver.yaml"
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize state
        self.active_conflicts = {}
        self.conflict_history = []
        self.protocol_state = {
            "mcp": {},
            "a2a": {}
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load the configuration.
        
        Returns:
            The configuration as a dictionary
        """
        try:
            import yaml
            from pathlib import Path
            
            config_path = Path(self.config_path)
            if not config_path.exists():
                logger.warning(f"Config file not found: {config_path}")
                return {}
                
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                logger.info(f"Loaded config from {config_path}")
                return config
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    async def register_protocol_state(self, protocol: str, state_id: str, state_data: Dict[str, Any]) -> bool:
        """
        Register a protocol state.
        
        Args:
            protocol: Protocol name ('mcp' or 'a2a')
            state_id: State identifier
            state_data: State data
            
        Returns:
            True if successful, False otherwise
        """
        if protocol not in ["mcp", "a2a"]:
            logger.warning(f"Unknown protocol: {protocol}")
            return False
        
        # Register state
        self.protocol_state[protocol][state_id] = {
            "timestamp": datetime.utcnow().isoformat(),
            "data": state_data
        }
        
        logger.debug(f"Registered {protocol} state: {state_id}")
        
        # Check for conflicts
        await self._check_conflicts(protocol, state_id)
        
        return True
    
    async def _check_conflicts(self, updated_protocol: str, state_id: str) -> None:
        """
        Check for conflicts after a protocol state update.
        
        Args:
            updated_protocol: Protocol that was updated
            state_id: State identifier that was updated
        """
        # Get the other protocol
        other_protocol = "a2a" if updated_protocol == "mcp" else "mcp"
        
        # Get updated state
        updated_state = self.protocol_state[updated_protocol].get(state_id)
        
        if not updated_state:
            logger.warning(f"State not found: {updated_protocol}/{state_id}")
            return
        
        # Find corresponding state in other protocol
        corresponding_id = self._find_corresponding_state(updated_protocol, state_id, other_protocol)
        
        if not corresponding_id:
            logger.debug(f"No corresponding state found for {updated_protocol}/{state_id}")
            return
            
        other_state = self.protocol_state[other_protocol].get(corresponding_id)
        
        if not other_state:
            logger.warning(f"Corresponding state not found: {other_protocol}/{corresponding_id}")
            return
        
        # Check for conflicts
        conflicts = self._detect_conflicts(
            updated_protocol, state_id, updated_state["data"],
            other_protocol, corresponding_id, other_state["data"]
        )
        
        if conflicts:
            logger.warning(f"Detected {len(conflicts)} conflicts between {updated_protocol}/{state_id} and {other_protocol}/{corresponding_id}")
            
            # Create conflict entry
            conflict_id = f"conflict-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            
            conflict = {
                "conflict_id": conflict_id,
                "timestamp": datetime.utcnow().isoformat(),
                "protocols": [updated_protocol, other_protocol],
                "states": [state_id, corresponding_id],
                "conflicts": conflicts,
                "status": "detected",
                "resolution": None
            }
            
            # Add to active conflicts
            self.active_conflicts[conflict_id] = conflict
            
            # Attempt to resolve
            await self._resolve_conflict(conflict_id)
    
    def _find_corresponding_state(self, source_protocol: str, source_id: str, target_protocol: str) -> Optional[str]:
        """
        Find the corresponding state ID in another protocol.
        
        Args:
            source_protocol: Source protocol
            source_id: Source state ID
            target_protocol: Target protocol
            
        Returns:
            Corresponding state ID, or None if not found
        """
        # In a real implementation, this would use metadata and context
        # to find the corresponding state
        
        # For now, we'll use a simple heuristic based on timestamps
        source_state = self.protocol_state[source_protocol].get(source_id)
        
        if not source_state:
            return None
            
        source_time = datetime.fromisoformat(source_state["timestamp"])
        
        # Find the closest state by timestamp
        closest_id = None
        min_diff = float('inf')
        
        for tid, state in self.protocol_state[target_protocol].items():
            target_time = datetime.fromisoformat(state["timestamp"])
            diff = abs((target_time - source_time).total_seconds())
            
            if diff < min_diff:
                min_diff = diff
                closest_id = tid
        
        # Only return if within threshold
        threshold = self.config.get("timestamp_threshold_seconds", 5)
        
        if min_diff <= threshold:
            return closest_id
            
        return None
    
    def _detect_conflicts(self, protocol1: str, id1: str, data1: Dict[str, Any],
                         protocol2: str, id2: str, data2: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect conflicts between two protocol states.
        
        Args:
            protocol1: First protocol
            id1: First state ID
            data1: First state data
            protocol2: Second protocol
            id2: Second state ID
            data2: Second state data
            
        Returns:
            List of detected conflicts
        """
        conflicts = []
        
        # Check for common fields with different values
        if protocol1 == "mcp" and protocol2 == "a2a":
            # MCP to A2A field mappings
            field_mappings = {
                "event_type": "state",
                "source": "agent.id",
                "context.conversation_id": "task_id"
            }
            
            for mcp_field, a2a_field in field_mappings.items():
                mcp_value = self._get_nested_value(data1, mcp_field)
                a2a_value = self._get_nested_value(data2, a2a_field)
                
                if mcp_value is not None and a2a_value is not None:
                    # Apply field-specific transformations
                    if mcp_field == "event_type":
                        # Map MCP event types to A2A states
                        mcp_to_a2a = {
                            "observe": "submitted",
                            "simulate": "working",
                            "recommend": "working",
                            "act": "completed"
                        }
                        transformed_mcp = mcp_to_a2a.get(mcp_value, mcp_value)
                        
                        if transformed_mcp != a2a_value:
                            conflicts.append({
                                "field": mcp_field,
                                "mcp_value": mcp_value,
                                "a2a_field": a2a_field,
                                "a2a_value": a2a_value,
                                "severity": "high" if mcp_field == "context.conversation_id" else "medium"
                            })
                    else:
                        # Direct comparison
                        if mcp_value != a2a_value:
                            conflicts.append({
                                "field": mcp_field,
                                "mcp_value": mcp_value,
                                "a2a_field": a2a_field,
                                "a2a_value": a2a_value,
                                "severity": "high" if mcp_field == "context.conversation_id" else "medium"
                            })
        
        return conflicts
    
    def _get_nested_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """
        Get a nested value from a dictionary using dot notation.
        
        Args:
            data: Dictionary to get value from
            field_path: Field path in dot notation
            
        Returns:
            Field value, or None if not found
        """
        parts = field_path.split('.')
        current = data
        
        for part in parts:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return None
                
        return current
    
    async def _resolve_conflict(self, conflict_id: str) -> None:
        """
        Attempt to resolve a conflict.
        
        Args:
            conflict_id: ID of the conflict to resolve
        """
        if conflict_id not in self.active_conflicts:
            logger.warning(f"Conflict not found: {conflict_id}")
            return
            
        conflict = self.active_conflicts[conflict_id]
        
        logger.info(f"Attempting to resolve conflict {conflict_id}")
        
        # Get resolution strategy
        strategy = self.config.get("resolution_strategy", "mcp_priority")
        
        # Apply resolution strategy
        if strategy == "mcp_priority":
            resolution = await self._resolve_with_mcp_priority(conflict)
        elif strategy == "a2a_priority":
            resolution = await self._resolve_with_a2a_priority(conflict)
        elif strategy == "timestamp_priority":
            resolution = await self._resolve_with_timestamp_priority(conflict)
        else:
            logger.warning(f"Unknown resolution strategy: {strategy}")
            resolution = {"error": f"Unknown resolution strategy: {strategy}"}
        
        # Update conflict
        conflict["status"] = "resolved" if "error" not in resolution else "failed"
        conflict["resolution"] = resolution
        conflict["resolution_timestamp"] = datetime.utcnow().isoformat()
        
        # Move to history
        self.conflict_history.append(conflict)
        del self.active_conflicts[conflict_id]
        
        logger.info(f"Conflict {conflict_id} {conflict['status']}")
        
        # Apply resolution if successful
        if conflict["status"] == "resolved":
            await self._apply_resolution(conflict)
    
    async def _resolve_with_mcp_priority(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a conflict by prioritizing MCP values.
        
        Args:
            conflict: Conflict data
            
        Returns:
            Resolution data
        """
        resolutions = []
        
        for c in conflict["conflicts"]:
            resolutions.append({
                "field": c["field"],
                "a2a_field": c["a2a_field"],
                "original_value": c["a2a_value"],
                "new_value": c["mcp_value"],
                "action": "update_a2a"
            })
        
        return {
            "strategy": "mcp_priority",
            "resolutions": resolutions
        }
    
    async def _resolve_with_a2a_priority(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a conflict by prioritizing A2A values.
        
        Args:
            conflict: Conflict data
            
        Returns:
            Resolution data
        """
        resolutions = []
        
        for c in conflict["conflicts"]:
            resolutions.append({
                "field": c["field"],
                "original_value": c["mcp_value"],
                "new_value": c["a2a_value"],
                "action": "update_mcp"
            })
        
        return {
            "strategy": "a2a_priority",
            "resolutions": resolutions
        }
    
    async def _resolve_with_timestamp_priority(self, conflict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a conflict by prioritizing the most recent value.
        
        Args:
            conflict: Conflict data
            
        Returns:
            Resolution data
        """
        protocols = conflict["protocols"]
        states = conflict["states"]
        
        # Get timestamps
        timestamps = []
        
        for i in range(len(protocols)):
            protocol = protocols[i]
            state_id = states[i]
            
            if state_id in self.protocol_state[protocol]:
                timestamp = self.protocol_state[protocol][state_id]["timestamp"]
                timestamps.append((protocol, datetime.fromisoformat(timestamp)))
        
        if len(timestamps) < 2:
            return {"error": "Insufficient timestamp data"}
        
        # Find most recent
        most_recent = max(timestamps, key=lambda x: x[1])
        most_recent_protocol = most_recent[0]
        
        resolutions = []
        
        for c in conflict["conflicts"]:
            if most_recent_protocol == "mcp":
                resolutions.append({
                    "field": c["field"],
                    "a2a_field": c["a2a_field"],
                    "original_value": c["a2a_value"],
                    "new_value": c["mcp_value"],
                    "action": "update_a2a"
                })
            else:
                resolutions.append({
                    "field": c["field"],
                    "original_value": c["mcp_value"],
                    "new_value": c["a2a_value"],
                    "action": "update_mcp"
                })
        
        return {
            "strategy": "timestamp_priority",
            "most_recent_protocol": most_recent_protocol,
            "resolutions": resolutions
        }
    
    async def _apply_resolution(self, conflict: Dict[str, Any]) -> None:
        """
        Apply a conflict resolution.
        
        Args:
            conflict: Resolved conflict data
        """
        resolution = conflict["resolution"]
        
        if not resolution or "resolutions" not in resolution:
            logger.warning(f"Invalid resolution for conflict {conflict['conflict_id']}")
            return
        
        # In a real implementation, this would:
        # 1. Update the protocol state in the appropriate adapters
        # 2. Notify affected agents
        
        logger.info(f"Applied resolution for conflict {conflict['conflict_id']} using {resolution['strategy']} strategy")
    
    def get_active_conflicts(self) -> List[Dict[str, Any]]:
        """
        Get all active conflicts.
        
        Returns:
            List of active conflicts
        """
        return list(self.active_conflicts.values())
    
    def get_conflict_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get conflict history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of historical conflicts
        """
        return self.conflict_history[-limit:]
    
    def get_protocol_state(self, protocol: str) -> Dict[str, Any]:
        """
        Get the current state of a protocol.
        
        Args:
            protocol: Protocol name ('mcp' or 'a2a')
            
        Returns:
            Protocol state
        """
        if protocol not in ["mcp", "a2a"]:
            logger.warning(f"Unknown protocol: {protocol}")
            return {}
            
        return self.protocol_state[protocol]


# Example usage
if __name__ == "__main__":
    async def main():
        # Create a protocol conflict resolver agent
        resolver = ProtocolConflictResolverAgent()
        
        # Register some protocol states
        await resolver.register_protocol_state("mcp", "event1", {
            "event_type": "observe",
            "source": "core-ai-llm-agent",
            "context": {
                "conversation_id": "conv-123"
            }
        })
        
        await resolver.register_protocol_state("a2a", "task1", {
            "task_id": "conv-123",
            "state": "submitted",
            "agent": {
                "id": "core-ai-llm-agent"
            }
        })
        
        # Register conflicting state
        await resolver.register_protocol_state("a2a", "task2", {
            "task_id": "conv-456",  # Conflict with conversation_id
            "state": "working",     # Conflict with event_type
            "agent": {
                "id": "core-ai-llm-agent"
            }
        })
        
        # Wait for conflict resolution
        await asyncio.sleep(1)
        
        # Get conflict history
        conflicts = resolver.get_conflict_history()
        
        if conflicts:
            print(f"Resolved conflicts: {len(conflicts)}")
            print(f"First conflict resolution: {conflicts[0]['resolution']['strategy']}")
        else:
            print("No conflicts detected")
    
    asyncio.run(main())
