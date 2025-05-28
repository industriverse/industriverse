"""
Capsule Memory Viewer Component for the Workflow Automation Layer.

This module implements the capsule memory viewer UI component that provides
visualization and interaction capabilities for the memory of Dynamic Agent Capsules.
It allows users to explore, analyze, and manage the different types of memory
(short-term, long-term, episodic, semantic) used by workflow agents.

Key features:
- Memory type visualization (short-term, long-term, episodic, semantic)
- Memory timeline exploration
- Memory search and filtering
- Memory relationship visualization
- Memory persistence management
- Memory transfer visualization
- Integration with Workflow Canvas and Debug Panel
"""

import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional, Tuple, Callable
from datetime import datetime, timedelta

class MemoryItem:
    """
    Represents a single memory item in a capsule's memory.
    
    A memory item contains data stored by an agent during workflow execution.
    """
    
    def __init__(self, 
                memory_id: str,
                memory_type: str,
                content: Any,
                timestamp: float,
                agent_id: str,
                workflow_id: str,
                task_id: Optional[str] = None,
                tags: List[str] = None,
                ttl: Optional[float] = None,
                importance: float = 0.5,
                relationships: List[str] = None):
        """
        Initialize a memory item.
        
        Args:
            memory_id: Unique identifier for the memory item
            memory_type: Type of memory (short_term, long_term, episodic, semantic)
            content: Content of the memory
            timestamp: Creation timestamp
            agent_id: ID of the agent that created the memory
            workflow_id: ID of the workflow context
            task_id: Optional ID of the task context
            tags: Optional tags for categorization
            ttl: Optional time-to-live in seconds (None means permanent)
            importance: Importance score (0.0 to 1.0)
            relationships: Optional list of related memory IDs
        """
        self.memory_id = memory_id
        self.memory_type = memory_type
        self.content = content
        self.timestamp = timestamp
        self.agent_id = agent_id
        self.workflow_id = workflow_id
        self.task_id = task_id
        self.tags = tags or []
        self.ttl = ttl
        self.importance = importance
        self.relationships = relationships or []
        self.last_accessed = timestamp
        self.access_count = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory item to a dictionary.
        
        Returns:
            Dictionary representation of the memory item
        """
        return {
            "memory_id": self.memory_id,
            "memory_type": self.memory_type,
            "content": self.content,
            "timestamp": self.timestamp,
            "agent_id": self.agent_id,
            "workflow_id": self.workflow_id,
            "task_id": self.task_id,
            "tags": self.tags,
            "ttl": self.ttl,
            "importance": self.importance,
            "relationships": self.relationships,
            "last_accessed": self.last_accessed,
            "access_count": self.access_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryItem':
        """
        Create a memory item from a dictionary.
        
        Args:
            data: Dictionary representation of the memory item
            
        Returns:
            MemoryItem instance
        """
        item = cls(
            memory_id=data["memory_id"],
            memory_type=data["memory_type"],
            content=data["content"],
            timestamp=data["timestamp"],
            agent_id=data["agent_id"],
            workflow_id=data["workflow_id"],
            task_id=data.get("task_id"),
            tags=data.get("tags", []),
            ttl=data.get("ttl"),
            importance=data.get("importance", 0.5),
            relationships=data.get("relationships", [])
        )
        item.last_accessed = data.get("last_accessed", data["timestamp"])
        item.access_count = data.get("access_count", 0)
        return item
    
    def access(self):
        """
        Record an access to this memory item.
        """
        self.last_accessed = time.time()
        self.access_count += 1
    
    def is_expired(self) -> bool:
        """
        Check if the memory item has expired.
        
        Returns:
            True if expired, False otherwise
        """
        if self.ttl is None:
            return False
        
        return time.time() > (self.timestamp + self.ttl)


class MemoryGroup:
    """
    Represents a group of related memory items.
    
    A memory group organizes memory items by a common attribute.
    """
    
    def __init__(self, 
                group_id: str,
                name: str,
                group_type: str,
                items: List[str] = None):
        """
        Initialize a memory group.
        
        Args:
            group_id: Unique identifier for the group
            name: Name of the group
            group_type: Type of grouping (e.g., "agent", "workflow", "task", "tag")
            items: Optional list of memory item IDs in the group
        """
        self.group_id = group_id
        self.name = name
        self.group_type = group_type
        self.items = items or []
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory group to a dictionary.
        
        Returns:
            Dictionary representation of the memory group
        """
        return {
            "group_id": self.group_id,
            "name": self.name,
            "group_type": self.group_type,
            "items": self.items
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryGroup':
        """
        Create a memory group from a dictionary.
        
        Args:
            data: Dictionary representation of the memory group
            
        Returns:
            MemoryGroup instance
        """
        return cls(
            group_id=data["group_id"],
            name=data["name"],
            group_type=data["group_type"],
            items=data.get("items", [])
        )
    
    def add_item(self, memory_id: str):
        """
        Add a memory item to the group.
        
        Args:
            memory_id: ID of the memory item to add
        """
        if memory_id not in self.items:
            self.items.append(memory_id)
    
    def remove_item(self, memory_id: str) -> bool:
        """
        Remove a memory item from the group.
        
        Args:
            memory_id: ID of the memory item to remove
            
        Returns:
            True if successful, False otherwise
        """
        if memory_id in self.items:
            self.items.remove(memory_id)
            return True
        return False


class MemoryTransfer:
    """
    Represents a memory transfer between agents.
    
    A memory transfer records the movement of memory items between agents.
    """
    
    def __init__(self, 
                transfer_id: str,
                source_agent_id: str,
                target_agent_id: str,
                memory_ids: List[str],
                timestamp: float,
                workflow_id: str,
                status: str = "completed",
                reason: Optional[str] = None):
        """
        Initialize a memory transfer.
        
        Args:
            transfer_id: Unique identifier for the transfer
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            memory_ids: List of memory item IDs transferred
            timestamp: Transfer timestamp
            workflow_id: ID of the workflow context
            status: Status of the transfer (e.g., "completed", "failed", "in_progress")
            reason: Optional reason for the transfer
        """
        self.transfer_id = transfer_id
        self.source_agent_id = source_agent_id
        self.target_agent_id = target_agent_id
        self.memory_ids = memory_ids
        self.timestamp = timestamp
        self.workflow_id = workflow_id
        self.status = status
        self.reason = reason
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory transfer to a dictionary.
        
        Returns:
            Dictionary representation of the memory transfer
        """
        return {
            "transfer_id": self.transfer_id,
            "source_agent_id": self.source_agent_id,
            "target_agent_id": self.target_agent_id,
            "memory_ids": self.memory_ids,
            "timestamp": self.timestamp,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "reason": self.reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryTransfer':
        """
        Create a memory transfer from a dictionary.
        
        Args:
            data: Dictionary representation of the memory transfer
            
        Returns:
            MemoryTransfer instance
        """
        return cls(
            transfer_id=data["transfer_id"],
            source_agent_id=data["source_agent_id"],
            target_agent_id=data["target_agent_id"],
            memory_ids=data["memory_ids"],
            timestamp=data["timestamp"],
            workflow_id=data["workflow_id"],
            status=data.get("status", "completed"),
            reason=data.get("reason")
        )


class CapsuleMemoryViewer:
    """
    Represents the capsule memory viewer UI component.
    
    Provides visualization and interaction capabilities for the memory of
    Dynamic Agent Capsules.
    """
    
    def __init__(self, viewer_id: Optional[str] = None):
        """
        Initialize a capsule memory viewer.
        
        Args:
            viewer_id: Optional unique identifier for the viewer
        """
        self.viewer_id = viewer_id or f"memory-viewer-{uuid.uuid4()}"
        self.memory_items: Dict[str, MemoryItem] = {}
        self.memory_groups: Dict[str, MemoryGroup] = {}
        self.memory_transfers: Dict[str, MemoryTransfer] = {}
        self.filters = {
            "memory_type": [],
            "agent_id": [],
            "workflow_id": [],
            "task_id": [],
            "tags": [],
            "time_range": {
                "start": None,
                "end": None
            },
            "importance_min": 0.0,
            "importance_max": 1.0
        }
        self.sort_by = "timestamp"
        self.sort_order = "desc"
        self.view_mode = "list"
        self.selected_memory_id: Optional[str] = None
        self.metadata = {
            "name": "Capsule Memory Viewer",
            "description": "Visualization of Dynamic Agent Capsule memory",
            "created": time.time(),
            "modified": time.time(),
            "version": "1.0"
        }
        
    def add_memory_item(self, item: MemoryItem):
        """
        Add a memory item to the viewer.
        
        Args:
            item: Memory item to add
        """
        self.memory_items[item.memory_id] = item
        self.metadata["modified"] = time.time()
        
        # Auto-create groups based on attributes
        self._auto_create_groups(item)
        
    def _auto_create_groups(self, item: MemoryItem):
        """
        Automatically create groups based on memory item attributes.
        
        Args:
            item: Memory item to create groups for
        """
        # Agent group
        agent_group_id = f"agent-{item.agent_id}"
        if agent_group_id not in self.memory_groups:
            self.memory_groups[agent_group_id] = MemoryGroup(
                group_id=agent_group_id,
                name=f"Agent: {item.agent_id}",
                group_type="agent"
            )
        self.memory_groups[agent_group_id].add_item(item.memory_id)
        
        # Workflow group
        workflow_group_id = f"workflow-{item.workflow_id}"
        if workflow_group_id not in self.memory_groups:
            self.memory_groups[workflow_group_id] = MemoryGroup(
                group_id=workflow_group_id,
                name=f"Workflow: {item.workflow_id}",
                group_type="workflow"
            )
        self.memory_groups[workflow_group_id].add_item(item.memory_id)
        
        # Task group (if applicable)
        if item.task_id:
            task_group_id = f"task-{item.task_id}"
            if task_group_id not in self.memory_groups:
                self.memory_groups[task_group_id] = MemoryGroup(
                    group_id=task_group_id,
                    name=f"Task: {item.task_id}",
                    group_type="task"
                )
            self.memory_groups[task_group_id].add_item(item.memory_id)
        
        # Memory type group
        type_group_id = f"type-{item.memory_type}"
        if type_group_id not in self.memory_groups:
            self.memory_groups[type_group_id] = MemoryGroup(
                group_id=type_group_id,
                name=f"Type: {item.memory_type}",
                group_type="memory_type"
            )
        self.memory_groups[type_group_id].add_item(item.memory_id)
        
        # Tag groups
        for tag in item.tags:
            tag_group_id = f"tag-{tag}"
            if tag_group_id not in self.memory_groups:
                self.memory_groups[tag_group_id] = MemoryGroup(
                    group_id=tag_group_id,
                    name=f"Tag: {tag}",
                    group_type="tag"
                )
            self.memory_groups[tag_group_id].add_item(item.memory_id)
    
    def remove_memory_item(self, memory_id: str) -> bool:
        """
        Remove a memory item from the viewer.
        
        Args:
            memory_id: ID of the memory item to remove
            
        Returns:
            True if successful, False otherwise
        """
        if memory_id not in self.memory_items:
            return False
        
        # Remove from groups
        for group in self.memory_groups.values():
            group.remove_item(memory_id)
        
        # Remove the item
        del self.memory_items[memory_id]
        self.metadata["modified"] = time.time()
        
        # Update selected memory if needed
        if self.selected_memory_id == memory_id:
            self.selected_memory_id = None
        
        return True
    
    def add_memory_group(self, group: MemoryGroup):
        """
        Add a memory group to the viewer.
        
        Args:
            group: Memory group to add
        """
        self.memory_groups[group.group_id] = group
        self.metadata["modified"] = time.time()
    
    def remove_memory_group(self, group_id: str) -> bool:
        """
        Remove a memory group from the viewer.
        
        Args:
            group_id: ID of the memory group to remove
            
        Returns:
            True if successful, False otherwise
        """
        if group_id not in self.memory_groups:
            return False
        
        del self.memory_groups[group_id]
        self.metadata["modified"] = time.time()
        
        return True
    
    def add_memory_transfer(self, transfer: MemoryTransfer):
        """
        Add a memory transfer to the viewer.
        
        Args:
            transfer: Memory transfer to add
        """
        self.memory_transfers[transfer.transfer_id] = transfer
        self.metadata["modified"] = time.time()
    
    def remove_memory_transfer(self, transfer_id: str) -> bool:
        """
        Remove a memory transfer from the viewer.
        
        Args:
            transfer_id: ID of the memory transfer to remove
            
        Returns:
            True if successful, False otherwise
        """
        if transfer_id not in self.memory_transfers:
            return False
        
        del self.memory_transfers[transfer_id]
        self.metadata["modified"] = time.time()
        
        return True
    
    def set_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Set the viewer filters.
        
        Args:
            filters: New filter settings
            
        Returns:
            The updated filters
        """
        self.filters.update(filters)
        self.metadata["modified"] = time.time()
        
        return self.filters
    
    def set_sort(self, sort_by: str, sort_order: str = "desc") -> Dict[str, str]:
        """
        Set the viewer sorting.
        
        Args:
            sort_by: Field to sort by
            sort_order: Sort order ("asc" or "desc")
            
        Returns:
            The updated sorting settings
        """
        self.sort_by = sort_by
        self.sort_order = sort_order
        self.metadata["modified"] = time.time()
        
        return {
            "sort_by": self.sort_by,
            "sort_order": self.sort_order
        }
    
    def set_view_mode(self, view_mode: str) -> str:
        """
        Set the viewer view mode.
        
        Args:
            view_mode: View mode ("list", "grid", "timeline", "graph")
            
        Returns:
            The updated view mode
        """
        self.view_mode = view_mode
        self.metadata["modified"] = time.time()
        
        return self.view_mode
    
    def select_memory_item(self, memory_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """
        Select a memory item for detailed view.
        
        Args:
            memory_id: ID of the memory item to select, or None to deselect
            
        Returns:
            The selected memory item as a dictionary if found, None otherwise
        """
        if memory_id is None:
            self.selected_memory_id = None
            self.metadata["modified"] = time.time()
            return None
        
        if memory_id in self.memory_items:
            self.selected_memory_id = memory_id
            self.memory_items[memory_id].access()
            self.metadata["modified"] = time.time()
            return self.memory_items[memory_id].to_dict()
        
        return None
    
    def get_filtered_memory_items(self) -> List[Dict[str, Any]]:
        """
        Get memory items filtered by the current filters.
        
        Returns:
            List of filtered memory item dictionaries
        """
        filtered = list(self.memory_items.values())
        
        # Apply memory type filter
        if self.filters["memory_type"]:
            filtered = [item for item in filtered if item.memory_type in self.filters["memory_type"]]
        
        # Apply agent filter
        if self.filters["agent_id"]:
            filtered = [item for item in filtered if item.agent_id in self.filters["agent_id"]]
        
        # Apply workflow filter
        if self.filters["workflow_id"]:
            filtered = [item for item in filtered if item.workflow_id in self.filters["workflow_id"]]
        
        # Apply task filter
        if self.filters["task_id"]:
            filtered = [item for item in filtered if item.task_id and item.task_id in self.filters["task_id"]]
        
        # Apply tags filter
        if self.filters["tags"]:
            filtered = [item for item in filtered if any(tag in item.tags for tag in self.filters["tags"])]
        
        # Apply time range filter
        if self.filters["time_range"]["start"]:
            filtered = [item for item in filtered if item.timestamp >= self.filters["time_range"]["start"]]
        
        if self.filters["time_range"]["end"]:
            filtered = [item for item in filtered if item.timestamp <= self.filters["time_range"]["end"]]
        
        # Apply importance filter
        filtered = [item for item in filtered if 
                   self.filters["importance_min"] <= item.importance <= self.filters["importance_max"]]
        
        # Apply sorting
        reverse = self.sort_order == "desc"
        
        if self.sort_by == "timestamp":
            filtered.sort(key=lambda item: item.timestamp, reverse=reverse)
        elif self.sort_by == "importance":
            filtered.sort(key=lambda item: item.importance, reverse=reverse)
        elif self.sort_by == "last_accessed":
            filtered.sort(key=lambda item: item.last_accessed, reverse=reverse)
        elif self.sort_by == "access_count":
            filtered.sort(key=lambda item: item.access_count, reverse=reverse)
        
        return [item.to_dict() for item in filtered]
    
    def get_memory_groups_by_type(self, group_type: str) -> List[Dict[str, Any]]:
        """
        Get memory groups filtered by type.
        
        Args:
            group_type: Type of groups to retrieve
            
        Returns:
            List of filtered memory group dictionaries
        """
        filtered = [group for group in self.memory_groups.values() if group.group_type == group_type]
        
        # Sort by name
        filtered.sort(key=lambda group: group.name)
        
        return [group.to_dict() for group in filtered]
    
    def get_memory_transfers_for_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get memory transfers involving a specific agent.
        
        Args:
            agent_id: ID of the agent
            
        Returns:
            List of memory transfer dictionaries
        """
        filtered = [transfer for transfer in self.memory_transfers.values() 
                   if transfer.source_agent_id == agent_id or transfer.target_agent_id == agent_id]
        
        # Sort by timestamp (descending)
        filtered.sort(key=lambda transfer: transfer.timestamp, reverse=True)
        
        return [transfer.to_dict() for transfer in filtered]
    
    def get_memory_item_relationships(self, memory_id: str) -> Dict[str, Any]:
        """
        Get relationships for a specific memory item.
        
        Args:
            memory_id: ID of the memory item
            
        Returns:
            Dictionary containing related memory items and relationship information
        """
        if memory_id not in self.memory_items:
            return {
                "memory_id": memory_id,
                "error": "Memory item not found",
                "related_items": []
            }
        
        item = self.memory_items[memory_id]
        related_items = []
        
        # Get directly related items
        for related_id in item.relationships:
            if related_id in self.memory_items:
                related_items.append({
                    "memory_id": related_id,
                    "relationship_type": "direct",
                    "item": self.memory_items[related_id].to_dict()
                })
        
        # Get items that reference this item
        for other_id, other_item in self.memory_items.items():
            if memory_id in other_item.relationships and other_id != memory_id:
                related_items.append({
                    "memory_id": other_id,
                    "relationship_type": "referenced_by",
                    "item": other_item.to_dict()
                })
        
        # Get items in the same groups
        item_groups = [group_id for group_id, group in self.memory_groups.items() 
                      if memory_id in group.items]
        
        for group_id in item_groups:
            group = self.memory_groups[group_id]
            for other_id in group.items:
                if other_id != memory_id and other_id in self.memory_items:
                    # Check if already included
                    if not any(r["memory_id"] == other_id for r in related_items):
                        related_items.append({
                            "memory_id": other_id,
                            "relationship_type": f"same_{group.group_type}",
                            "group_id": group_id,
                            "item": self.memory_items[other_id].to_dict()
                        })
        
        return {
            "memory_id": memory_id,
            "item": item.to_dict(),
            "related_items": related_items
        }
    
    def get_memory_timeline(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get a timeline of memory events.
        
        Args:
            workflow_id: Optional workflow ID to filter by
            
        Returns:
            List of timeline events
        """
        timeline = []
        
        # Add memory items to timeline
        for item in self.memory_items.values():
            if workflow_id is None or item.workflow_id == workflow_id:
                timeline.append({
                    "event_type": "memory_created",
                    "timestamp": item.timestamp,
                    "memory_id": item.memory_id,
                    "agent_id": item.agent_id,
                    "workflow_id": item.workflow_id,
                    "memory_type": item.memory_type,
                    "item": item.to_dict()
                })
        
        # Add memory transfers to timeline
        for transfer in self.memory_transfers.values():
            if workflow_id is None or transfer.workflow_id == workflow_id:
                timeline.append({
                    "event_type": "memory_transfer",
                    "timestamp": transfer.timestamp,
                    "transfer_id": transfer.transfer_id,
                    "source_agent_id": transfer.source_agent_id,
                    "target_agent_id": transfer.target_agent_id,
                    "memory_ids": transfer.memory_ids,
                    "workflow_id": transfer.workflow_id,
                    "transfer": transfer.to_dict()
                })
        
        # Sort by timestamp
        timeline.sort(key=lambda event: event["timestamp"])
        
        return timeline
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the memory items.
        
        Returns:
            Dictionary containing memory statistics
        """
        stats = {
            "total_items": len(self.memory_items),
            "total_transfers": len(self.memory_transfers),
            "memory_type_distribution": {},
            "agent_distribution": {},
            "workflow_distribution": {},
            "tag_distribution": {},
            "importance_distribution": {
                "very_high": 0,  # 0.8 - 1.0
                "high": 0,       # 0.6 - 0.8
                "medium": 0,     # 0.4 - 0.6
                "low": 0,        # 0.2 - 0.4
                "very_low": 0    # 0.0 - 0.2
            },
            "time_distribution": {
                "last_hour": 0,
                "last_day": 0,
                "last_week": 0,
                "older": 0
            }
        }
        
        now = time.time()
        hour_ago = now - 3600
        day_ago = now - 86400
        week_ago = now - 604800
        
        for item in self.memory_items.values():
            # Memory type distribution
            if item.memory_type not in stats["memory_type_distribution"]:
                stats["memory_type_distribution"][item.memory_type] = 0
            stats["memory_type_distribution"][item.memory_type] += 1
            
            # Agent distribution
            if item.agent_id not in stats["agent_distribution"]:
                stats["agent_distribution"][item.agent_id] = 0
            stats["agent_distribution"][item.agent_id] += 1
            
            # Workflow distribution
            if item.workflow_id not in stats["workflow_distribution"]:
                stats["workflow_distribution"][item.workflow_id] = 0
            stats["workflow_distribution"][item.workflow_id] += 1
            
            # Tag distribution
            for tag in item.tags:
                if tag not in stats["tag_distribution"]:
                    stats["tag_distribution"][tag] = 0
                stats["tag_distribution"][tag] += 1
            
            # Importance distribution
            if item.importance >= 0.8:
                stats["importance_distribution"]["very_high"] += 1
            elif item.importance >= 0.6:
                stats["importance_distribution"]["high"] += 1
            elif item.importance >= 0.4:
                stats["importance_distribution"]["medium"] += 1
            elif item.importance >= 0.2:
                stats["importance_distribution"]["low"] += 1
            else:
                stats["importance_distribution"]["very_low"] += 1
            
            # Time distribution
            if item.timestamp >= hour_ago:
                stats["time_distribution"]["last_hour"] += 1
            elif item.timestamp >= day_ago:
                stats["time_distribution"]["last_day"] += 1
            elif item.timestamp >= week_ago:
                stats["time_distribution"]["last_week"] += 1
            else:
                stats["time_distribution"]["older"] += 1
        
        return stats
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the memory viewer state to a dictionary.
        
        Returns:
            Dictionary representation of the memory viewer state
        """
        return {
            "viewer_id": self.viewer_id,
            "memory_items": {m_id: item.to_dict() for m_id, item in self.memory_items.items()},
            "memory_groups": {g_id: group.to_dict() for g_id, group in self.memory_groups.items()},
            "memory_transfers": {t_id: transfer.to_dict() for t_id, transfer in self.memory_transfers.items()},
            "filters": self.filters,
            "sort_by": self.sort_by,
            "sort_order": self.sort_order,
            "view_mode": self.view_mode,
            "selected_memory_id": self.selected_memory_id,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CapsuleMemoryViewer':
        """
        Create a memory viewer from a dictionary.
        
        Args:
            data: Dictionary representation of the memory viewer
            
        Returns:
            CapsuleMemoryViewer instance
        """
        viewer = cls(viewer_id=data.get("viewer_id"))
        
        # Set metadata
        if "metadata" in data:
            viewer.metadata = data["metadata"]
        
        # Set filters and sorting
        if "filters" in data:
            viewer.filters = data["filters"]
        
        if "sort_by" in data:
            viewer.sort_by = data["sort_by"]
        
        if "sort_order" in data:
            viewer.sort_order = data["sort_order"]
        
        if "view_mode" in data:
            viewer.view_mode = data["view_mode"]
        
        if "selected_memory_id" in data:
            viewer.selected_memory_id = data["selected_memory_id"]
        
        # Add memory items
        for m_id, item_data in data.get("memory_items", {}).items():
            viewer.memory_items[m_id] = MemoryItem.from_dict(item_data)
        
        # Add memory groups
        for g_id, group_data in data.get("memory_groups", {}).items():
            viewer.memory_groups[g_id] = MemoryGroup.from_dict(group_data)
        
        # Add memory transfers
        for t_id, transfer_data in data.get("memory_transfers", {}).items():
            viewer.memory_transfers[t_id] = MemoryTransfer.from_dict(transfer_data)
        
        return viewer


class CapsuleMemoryViewerManager:
    """
    Manages capsule memory viewers for the Workflow Automation Layer.
    
    This class provides methods for creating, managing, and persisting
    capsule memory viewers.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the Capsule Memory Viewer Manager.
        
        Args:
            storage_path: Optional path for storing viewers
        """
        self.storage_path = storage_path or "/data/capsule_memory_viewers"
        self.viewers: Dict[str, CapsuleMemoryViewer] = {}
        self._load_viewers()
        
    def _load_viewers(self):
        """Load viewers from persistent storage."""
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
            return
        
        for filename in os.listdir(self.storage_path):
            if filename.endswith(".json"):
                try:
                    with open(os.path.join(self.storage_path, filename), 'r') as f:
                        viewer_data = json.load(f)
                        viewer = CapsuleMemoryViewer.from_dict(viewer_data)
                        self.viewers[viewer.viewer_id] = viewer
                except Exception as e:
                    print(f"Error loading viewer {filename}: {e}")
    
    def _store_viewer(self, viewer: CapsuleMemoryViewer):
        """
        Store a viewer to persistent storage.
        
        Args:
            viewer: The viewer to store
        """
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
        
        file_path = os.path.join(self.storage_path, f"{viewer.viewer_id}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(viewer.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error storing viewer: {e}")
    
    def create_viewer(self, 
                     name: str = "Capsule Memory Viewer",
                     description: str = "",
                     viewer_id: Optional[str] = None) -> CapsuleMemoryViewer:
        """
        Create a new capsule memory viewer.
        
        Args:
            name: Name for the viewer
            description: Description for the viewer
            viewer_id: Optional unique identifier for the viewer
            
        Returns:
            The created viewer
        """
        viewer = CapsuleMemoryViewer(viewer_id=viewer_id)
        viewer.metadata["name"] = name
        viewer.metadata["description"] = description
        
        self.viewers[viewer.viewer_id] = viewer
        self._store_viewer(viewer)
        
        return viewer
    
    def get_viewer(self, viewer_id: str) -> Optional[CapsuleMemoryViewer]:
        """
        Get a viewer by its identifier.
        
        Args:
            viewer_id: Identifier for the viewer
            
        Returns:
            The viewer if found, None otherwise
        """
        return self.viewers.get(viewer_id)
    
    def list_viewers(self) -> List[Dict[str, Any]]:
        """
        List all available viewers.
        
        Returns:
            List of viewer metadata
        """
        return [
            {
                "id": viewer.viewer_id,
                "name": viewer.metadata.get("name", "Capsule Memory Viewer"),
                "description": viewer.metadata.get("description", ""),
                "created": viewer.metadata.get("created", 0),
                "modified": viewer.metadata.get("modified", 0),
                "version": viewer.metadata.get("version", "1.0"),
                "memory_count": len(viewer.memory_items)
            }
            for viewer in self.viewers.values()
        ]
    
    def update_viewer(self, viewer_id: str, updates: Dict[str, Any]) -> Optional[CapsuleMemoryViewer]:
        """
        Update a viewer.
        
        Args:
            viewer_id: Identifier for the viewer
            updates: Updates to apply to the viewer
            
        Returns:
            The updated viewer if successful, None otherwise
        """
        viewer = self.get_viewer(viewer_id)
        if not viewer:
            return None
        
        # Apply updates
        if "metadata" in updates:
            viewer.metadata.update(updates["metadata"])
            viewer.metadata["modified"] = time.time()
        
        if "filters" in updates:
            viewer.set_filters(updates["filters"])
        
        if "sort" in updates:
            sort_by = updates["sort"].get("sort_by", viewer.sort_by)
            sort_order = updates["sort"].get("sort_order", viewer.sort_order)
            viewer.set_sort(sort_by, sort_order)
        
        if "view_mode" in updates:
            viewer.set_view_mode(updates["view_mode"])
        
        if "selected_memory_id" in updates:
            viewer.select_memory_item(updates["selected_memory_id"])
        
        # Add/update memory items
        if "memory_items" in updates:
            for item_data in updates["memory_items"]:
                if "memory_id" in item_data:
                    memory_id = item_data["memory_id"]
                    if memory_id in viewer.memory_items:
                        # Update existing item (not implemented in the viewer class)
                        # For now, just replace it
                        viewer.memory_items[memory_id] = MemoryItem.from_dict(item_data)
                    else:
                        # Add new item
                        viewer.add_memory_item(MemoryItem.from_dict(item_data))
        
        # Add/update memory groups
        if "memory_groups" in updates:
            for group_data in updates["memory_groups"]:
                if "group_id" in group_data:
                    group_id = group_data["group_id"]
                    if group_id in viewer.memory_groups:
                        # Update existing group (not implemented in the viewer class)
                        # For now, just replace it
                        viewer.memory_groups[group_id] = MemoryGroup.from_dict(group_data)
                    else:
                        # Add new group
                        viewer.add_memory_group(MemoryGroup.from_dict(group_data))
        
        # Add/update memory transfers
        if "memory_transfers" in updates:
            for transfer_data in updates["memory_transfers"]:
                if "transfer_id" in transfer_data:
                    transfer_id = transfer_data["transfer_id"]
                    if transfer_id in viewer.memory_transfers:
                        # Update existing transfer (not implemented in the viewer class)
                        # For now, just replace it
                        viewer.memory_transfers[transfer_id] = MemoryTransfer.from_dict(transfer_data)
                    else:
                        # Add new transfer
                        viewer.add_memory_transfer(MemoryTransfer.from_dict(transfer_data))
        
        # Remove memory items
        if "remove_memory_items" in updates:
            for memory_id in updates["remove_memory_items"]:
                viewer.remove_memory_item(memory_id)
        
        # Remove memory groups
        if "remove_memory_groups" in updates:
            for group_id in updates["remove_memory_groups"]:
                viewer.remove_memory_group(group_id)
        
        # Remove memory transfers
        if "remove_memory_transfers" in updates:
            for transfer_id in updates["remove_memory_transfers"]:
                viewer.remove_memory_transfer(transfer_id)
        
        # Store the updated viewer
        self._store_viewer(viewer)
        
        return viewer
    
    def delete_viewer(self, viewer_id: str) -> bool:
        """
        Delete a viewer.
        
        Args:
            viewer_id: Identifier for the viewer
            
        Returns:
            True if successful, False otherwise
        """
        if viewer_id not in self.viewers:
            return False
        
        # Remove from memory
        del self.viewers[viewer_id]
        
        # Remove from storage
        file_path = os.path.join(self.storage_path, f"{viewer_id}.json")
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error deleting viewer: {e}")
            return False


class CapsuleMemoryViewerService:
    """
    Service for integrating the capsule memory viewer with the Workflow Automation Layer.
    
    This class provides methods for updating the viewer with memory data and
    handling user interactions.
    """
    
    def __init__(self, viewer_manager: CapsuleMemoryViewerManager):
        """
        Initialize the Capsule Memory Viewer Service.
        
        Args:
            viewer_manager: Capsule Memory Viewer Manager instance
        """
        self.viewer_manager = viewer_manager
        self.update_callbacks: Dict[str, List[Callable]] = {}
        
    def register_update_callback(self, viewer_id: str, callback: Callable):
        """
        Register a callback for viewer updates.
        
        Args:
            viewer_id: Identifier for the viewer
            callback: Callback function
        """
        if viewer_id not in self.update_callbacks:
            self.update_callbacks[viewer_id] = []
            
        self.update_callbacks[viewer_id].append(callback)
    
    def unregister_update_callback(self, viewer_id: str, callback: Callable) -> bool:
        """
        Unregister a callback for viewer updates.
        
        Args:
            viewer_id: Identifier for the viewer
            callback: Callback function
            
        Returns:
            True if successful, False otherwise
        """
        if viewer_id not in self.update_callbacks:
            return False
        
        if callback in self.update_callbacks[viewer_id]:
            self.update_callbacks[viewer_id].remove(callback)
            return True
        
        return False
    
    def notify_update(self, 
                     viewer_id: str,
                     update_type: str,
                     update_data: Dict[str, Any]):
        """
        Notify update callbacks of a viewer update.
        
        Args:
            viewer_id: Identifier for the viewer
            update_type: Type of the update
            update_data: Update data
        """
        if viewer_id in self.update_callbacks:
            for callback in self.update_callbacks[viewer_id]:
                try:
                    callback(update_type, update_data)
                except Exception as e:
                    print(f"Error in update callback: {e}")
    
    def add_memory_item(self, 
                       viewer_id: str,
                       memory_type: str,
                       content: Any,
                       agent_id: str,
                       workflow_id: str,
                       task_id: Optional[str] = None,
                       tags: List[str] = None,
                       ttl: Optional[float] = None,
                       importance: float = 0.5,
                       relationships: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Add a memory item to the viewer.
        
        Args:
            viewer_id: Identifier for the viewer
            memory_type: Type of memory
            content: Content of the memory
            agent_id: ID of the agent
            workflow_id: ID of the workflow
            task_id: Optional ID of the task
            tags: Optional tags for the memory
            ttl: Optional time-to-live in seconds
            importance: Importance score (0.0 to 1.0)
            relationships: Optional list of related memory IDs
            
        Returns:
            The added memory item as a dictionary if successful, None otherwise
        """
        viewer = self.viewer_manager.get_viewer(viewer_id)
        if not viewer:
            return None
        
        # Create the memory item
        memory_id = f"memory-{uuid.uuid4()}"
        item = MemoryItem(
            memory_id=memory_id,
            memory_type=memory_type,
            content=content,
            timestamp=time.time(),
            agent_id=agent_id,
            workflow_id=workflow_id,
            task_id=task_id,
            tags=tags,
            ttl=ttl,
            importance=importance,
            relationships=relationships
        )
        
        # Add to the viewer
        viewer.add_memory_item(item)
        
        # Store the updated viewer
        self.viewer_manager._store_viewer(viewer)
        
        # Notify update
        self.notify_update(
            viewer_id=viewer_id,
            update_type="memory_item_added",
            update_data={
                "memory_id": memory_id,
                "item": item.to_dict()
            }
        )
        
        return item.to_dict()
    
    def add_memory_transfer(self, 
                          viewer_id: str,
                          source_agent_id: str,
                          target_agent_id: str,
                          memory_ids: List[str],
                          workflow_id: str,
                          reason: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Add a memory transfer to the viewer.
        
        Args:
            viewer_id: Identifier for the viewer
            source_agent_id: ID of the source agent
            target_agent_id: ID of the target agent
            memory_ids: List of memory item IDs transferred
            workflow_id: ID of the workflow
            reason: Optional reason for the transfer
            
        Returns:
            The added memory transfer as a dictionary if successful, None otherwise
        """
        viewer = self.viewer_manager.get_viewer(viewer_id)
        if not viewer:
            return None
        
        # Create the memory transfer
        transfer_id = f"transfer-{uuid.uuid4()}"
        transfer = MemoryTransfer(
            transfer_id=transfer_id,
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            memory_ids=memory_ids,
            timestamp=time.time(),
            workflow_id=workflow_id,
            status="completed",
            reason=reason
        )
        
        # Add to the viewer
        viewer.add_memory_transfer(transfer)
        
        # Store the updated viewer
        self.viewer_manager._store_viewer(viewer)
        
        # Notify update
        self.notify_update(
            viewer_id=viewer_id,
            update_type="memory_transfer_added",
            update_data={
                "transfer_id": transfer_id,
                "transfer": transfer.to_dict()
            }
        )
        
        return transfer.to_dict()
    
    def handle_user_interaction(self, 
                              viewer_id: str,
                              interaction_type: str,
                              interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle user interaction with the viewer.
        
        Args:
            viewer_id: Identifier for the viewer
            interaction_type: Type of the interaction
            interaction_data: Interaction data
            
        Returns:
            Response data
        """
        viewer = self.viewer_manager.get_viewer(viewer_id)
        if not viewer:
            return {"success": False, "error": "Viewer not found"}
        
        if interaction_type == "set_filters":
            filters = interaction_data.get("filters", {})
            
            updated_filters = viewer.set_filters(filters)
            self.viewer_manager._store_viewer(viewer)
            
            return {
                "success": True,
                "filters": updated_filters
            }
            
        elif interaction_type == "set_sort":
            sort_by = interaction_data.get("sort_by")
            sort_order = interaction_data.get("sort_order", "desc")
            
            if sort_by:
                updated_sort = viewer.set_sort(sort_by, sort_order)
                self.viewer_manager._store_viewer(viewer)
                
                return {
                    "success": True,
                    "sort": updated_sort
                }
            else:
                return {
                    "success": False,
                    "error": "Missing sort_by parameter"
                }
                
        elif interaction_type == "set_view_mode":
            view_mode = interaction_data.get("view_mode")
            
            if view_mode:
                updated_view_mode = viewer.set_view_mode(view_mode)
                self.viewer_manager._store_viewer(viewer)
                
                return {
                    "success": True,
                    "view_mode": updated_view_mode
                }
            else:
                return {
                    "success": False,
                    "error": "Missing view_mode parameter"
                }
                
        elif interaction_type == "select_memory_item":
            memory_id = interaction_data.get("memory_id")
            
            selected_item = viewer.select_memory_item(memory_id)
            self.viewer_manager._store_viewer(viewer)
            
            return {
                "success": True,
                "selected_item": selected_item
            }
            
        elif interaction_type == "get_filtered_memory_items":
            filtered_items = viewer.get_filtered_memory_items()
            
            return {
                "success": True,
                "items": filtered_items
            }
            
        elif interaction_type == "get_memory_groups_by_type":
            group_type = interaction_data.get("group_type")
            
            if group_type:
                groups = viewer.get_memory_groups_by_type(group_type)
                
                return {
                    "success": True,
                    "groups": groups
                }
            else:
                return {
                    "success": False,
                    "error": "Missing group_type parameter"
                }
                
        elif interaction_type == "get_memory_transfers_for_agent":
            agent_id = interaction_data.get("agent_id")
            
            if agent_id:
                transfers = viewer.get_memory_transfers_for_agent(agent_id)
                
                return {
                    "success": True,
                    "transfers": transfers
                }
            else:
                return {
                    "success": False,
                    "error": "Missing agent_id parameter"
                }
                
        elif interaction_type == "get_memory_item_relationships":
            memory_id = interaction_data.get("memory_id")
            
            if memory_id:
                relationships = viewer.get_memory_item_relationships(memory_id)
                
                return {
                    "success": True,
                    "relationships": relationships
                }
            else:
                return {
                    "success": False,
                    "error": "Missing memory_id parameter"
                }
                
        elif interaction_type == "get_memory_timeline":
            workflow_id = interaction_data.get("workflow_id")
            
            timeline = viewer.get_memory_timeline(workflow_id)
            
            return {
                "success": True,
                "timeline": timeline
            }
            
        elif interaction_type == "get_memory_stats":
            stats = viewer.get_memory_stats()
            
            return {
                "success": True,
                "stats": stats
            }
            
        else:
            return {
                "success": False,
                "error": f"Unknown interaction type: {interaction_type}"
            }


# Example usage
if __name__ == "__main__":
    # Initialize the viewer manager
    viewer_manager = CapsuleMemoryViewerManager()
    
    # Create a viewer
    viewer = viewer_manager.create_viewer(
        name="Example Viewer",
        description="An example memory viewer for testing"
    )
    
    # Initialize the viewer service
    viewer_service = CapsuleMemoryViewerService(viewer_manager)
    
    # Register an update callback
    def update_callback(update_type, update_data):
        print(f"Viewer update: {update_type}")
        print(f"Update data: {update_data}")
    
    viewer_service.register_update_callback(viewer.viewer_id, update_callback)
    
    # Add some memory items
    item1 = viewer_service.add_memory_item(
        viewer_id=viewer.viewer_id,
        memory_type="short_term",
        content={"task_data": {"input": "example", "status": "processing"}},
        agent_id="agent-1",
        workflow_id="workflow-1",
        task_id="task-1",
        tags=["example", "test"],
        importance=0.7
    )
    
    item2 = viewer_service.add_memory_item(
        viewer_id=viewer.viewer_id,
        memory_type="long_term",
        content={"knowledge": "This is an important fact to remember."},
        agent_id="agent-1",
        workflow_id="workflow-1",
        tags=["knowledge", "important"],
        importance=0.9,
        relationships=[item1["memory_id"]]
    )
    
    # Add a memory transfer
    transfer = viewer_service.add_memory_transfer(
        viewer_id=viewer.viewer_id,
        source_agent_id="agent-1",
        target_agent_id="agent-2",
        memory_ids=[item2["memory_id"]],
        workflow_id="workflow-1",
        reason="Knowledge sharing"
    )
    
    # Handle user interaction
    response = viewer_service.handle_user_interaction(
        viewer_id=viewer.viewer_id,
        interaction_type="get_memory_stats",
        interaction_data={}
    )
    
    print(f"Memory stats: {response['stats']}")
"""
