"""
Avatar Registry Module for the UI/UX Layer of Industriverse

This module provides a centralized registry for all avatars in the UI/UX Layer,
managing avatar registration, retrieval, and lifecycle management. It serves as
the authoritative source for avatar information across the system.

The Avatar Registry is responsible for:
1. Registering and deregistering avatars
2. Storing and retrieving avatar metadata
3. Managing avatar relationships and groupings
4. Providing avatar discovery and search capabilities
5. Enforcing avatar uniqueness and validation

This module works closely with the Avatar Manager and other avatar-related
components to ensure a consistent and reliable avatar ecosystem.
"""

import logging
import time
import uuid
from typing import Dict, List, Any, Optional, Callable, Union
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AvatarType(Enum):
    """Enumeration of avatar types."""
    AGENT = "agent"
    LAYER = "layer"
    SYSTEM = "system"
    USER = "user"
    DIGITAL_TWIN = "digital_twin"
    SWARM = "swarm"
    CAPSULE = "capsule"


class AvatarStatus(Enum):
    """Enumeration of avatar statuses."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"
    DELETED = "deleted"


class AvatarRegistry:
    """
    Centralized registry for all avatars in the UI/UX Layer.
    
    This class provides methods for registering, retrieving, and managing avatars,
    as well as enforcing avatar uniqueness and validation.
    """

    def __init__(self):
        """Initialize the AvatarRegistry."""
        self.avatars = {}
        self.avatar_types = {}
        self.avatar_groups = {}
        self.avatar_relationships = {}
        self.avatar_metadata = {}
        self.avatar_status = {}
        self.avatar_history = {}
        self.avatar_search_index = {}
        
        logger.info("AvatarRegistry initialized")

    def register_avatar(
        self,
        avatar_id: str,
        avatar_type: AvatarType,
        name: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None,
        groups: Optional[List[str]] = None,
        relationships: Optional[Dict[str, List[str]]] = None
    ) -> bool:
        """
        Register an avatar in the registry.
        
        Args:
            avatar_id: Unique identifier for the avatar
            avatar_type: Type of avatar
            name: Display name for the avatar
            description: Description of the avatar
            metadata: Additional metadata for the avatar
            groups: Groups the avatar belongs to
            relationships: Relationships with other avatars
            
        Returns:
            True if registration was successful, False otherwise
        """
        if avatar_id in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} already exists")
            return False
        
        # Create avatar record
        avatar = {
            "id": avatar_id,
            "type": avatar_type.value,
            "name": name,
            "description": description,
            "created_at": time.time(),
            "updated_at": time.time()
        }
        
        # Store avatar
        self.avatars[avatar_id] = avatar
        
        # Store avatar type
        if avatar_type.value not in self.avatar_types:
            self.avatar_types[avatar_type.value] = []
        self.avatar_types[avatar_type.value].append(avatar_id)
        
        # Store metadata if provided
        if metadata:
            self.avatar_metadata[avatar_id] = metadata
        else:
            self.avatar_metadata[avatar_id] = {}
        
        # Store groups if provided
        if groups:
            for group in groups:
                if group not in self.avatar_groups:
                    self.avatar_groups[group] = []
                self.avatar_groups[group].append(avatar_id)
        
        # Store relationships if provided
        if relationships:
            self.avatar_relationships[avatar_id] = relationships
        else:
            self.avatar_relationships[avatar_id] = {}
        
        # Set initial status
        self.avatar_status[avatar_id] = AvatarStatus.ACTIVE.value
        
        # Initialize history
        self.avatar_history[avatar_id] = [{
            "action": "registered",
            "timestamp": time.time(),
            "details": {
                "type": avatar_type.value,
                "name": name,
                "description": description
            }
        }]
        
        # Update search index
        self._update_search_index(avatar_id, avatar, metadata)
        
        logger.info(f"Registered avatar {avatar_id} of type {avatar_type.value}")
        return True

    def deregister_avatar(self, avatar_id: str) -> bool:
        """
        Deregister an avatar from the registry.
        
        Args:
            avatar_id: ID of the avatar to deregister
            
        Returns:
            True if deregistration was successful, False otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} does not exist")
            return False
        
        # Get avatar type
        avatar_type = self.avatars[avatar_id]["type"]
        
        # Remove from avatar types
        if avatar_type in self.avatar_types and avatar_id in self.avatar_types[avatar_type]:
            self.avatar_types[avatar_type].remove(avatar_id)
        
        # Remove from groups
        for group, avatars in self.avatar_groups.items():
            if avatar_id in avatars:
                avatars.remove(avatar_id)
        
        # Remove relationships
        if avatar_id in self.avatar_relationships:
            del self.avatar_relationships[avatar_id]
        
        # Remove from other avatars' relationships
        for other_id, relationships in self.avatar_relationships.items():
            for rel_type, rel_ids in relationships.items():
                if avatar_id in rel_ids:
                    rel_ids.remove(avatar_id)
        
        # Update history
        if avatar_id in self.avatar_history:
            self.avatar_history[avatar_id].append({
                "action": "deregistered",
                "timestamp": time.time(),
                "details": {}
            })
        
        # Set status to deleted
        self.avatar_status[avatar_id] = AvatarStatus.DELETED.value
        
        # Remove from search index
        if avatar_id in self.avatar_search_index:
            del self.avatar_search_index[avatar_id]
        
        # Remove avatar
        del self.avatars[avatar_id]
        
        logger.info(f"Deregistered avatar {avatar_id}")
        return True

    def get_avatar(self, avatar_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an avatar by ID.
        
        Args:
            avatar_id: ID of the avatar to retrieve
            
        Returns:
            Avatar record if found, None otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} does not exist")
            return None
        
        # Get avatar record
        avatar = self.avatars[avatar_id].copy()
        
        # Add metadata
        if avatar_id in self.avatar_metadata:
            avatar["metadata"] = self.avatar_metadata[avatar_id]
        
        # Add status
        if avatar_id in self.avatar_status:
            avatar["status"] = self.avatar_status[avatar_id]
        
        return avatar

    def get_avatars_by_type(self, avatar_type: AvatarType) -> List[Dict[str, Any]]:
        """
        Get all avatars of a specific type.
        
        Args:
            avatar_type: Type of avatars to retrieve
            
        Returns:
            List of avatar records
        """
        if avatar_type.value not in self.avatar_types:
            return []
        
        avatar_ids = self.avatar_types[avatar_type.value]
        avatars = []
        
        for avatar_id in avatar_ids:
            avatar = self.get_avatar(avatar_id)
            if avatar:
                avatars.append(avatar)
        
        return avatars

    def get_avatars_by_group(self, group: str) -> List[Dict[str, Any]]:
        """
        Get all avatars in a specific group.
        
        Args:
            group: Group to retrieve avatars from
            
        Returns:
            List of avatar records
        """
        if group not in self.avatar_groups:
            return []
        
        avatar_ids = self.avatar_groups[group]
        avatars = []
        
        for avatar_id in avatar_ids:
            avatar = self.get_avatar(avatar_id)
            if avatar:
                avatars.append(avatar)
        
        return avatars

    def get_related_avatars(
        self,
        avatar_id: str,
        relationship_type: Optional[str] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get avatars related to a specific avatar.
        
        Args:
            avatar_id: ID of the avatar to get related avatars for
            relationship_type: Optional type of relationship to filter by
            
        Returns:
            Dictionary mapping relationship types to lists of avatar records
        """
        if avatar_id not in self.avatar_relationships:
            return {}
        
        relationships = self.avatar_relationships[avatar_id]
        
        if relationship_type:
            if relationship_type not in relationships:
                return {}
            
            relationship_types = {relationship_type: relationships[relationship_type]}
        else:
            relationship_types = relationships
        
        result = {}
        
        for rel_type, rel_ids in relationship_types.items():
            result[rel_type] = []
            
            for rel_id in rel_ids:
                avatar = self.get_avatar(rel_id)
                if avatar:
                    result[rel_type].append(avatar)
        
        return result

    def update_avatar(
        self,
        avatar_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        groups: Optional[List[str]] = None,
        relationships: Optional[Dict[str, List[str]]] = None
    ) -> bool:
        """
        Update an avatar in the registry.
        
        Args:
            avatar_id: ID of the avatar to update
            name: New display name for the avatar
            description: New description of the avatar
            metadata: New metadata for the avatar
            groups: New groups the avatar belongs to
            relationships: New relationships with other avatars
            
        Returns:
            True if update was successful, False otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} does not exist")
            return False
        
        # Get avatar record
        avatar = self.avatars[avatar_id]
        
        # Update fields if provided
        if name:
            avatar["name"] = name
        
        if description:
            avatar["description"] = description
        
        # Update metadata if provided
        if metadata:
            if avatar_id not in self.avatar_metadata:
                self.avatar_metadata[avatar_id] = {}
            
            self.avatar_metadata[avatar_id].update(metadata)
        
        # Update groups if provided
        if groups:
            # Remove from existing groups
            for group, avatars in self.avatar_groups.items():
                if avatar_id in avatars:
                    avatars.remove(avatar_id)
            
            # Add to new groups
            for group in groups:
                if group not in self.avatar_groups:
                    self.avatar_groups[group] = []
                self.avatar_groups[group].append(avatar_id)
        
        # Update relationships if provided
        if relationships:
            self.avatar_relationships[avatar_id] = relationships
        
        # Update timestamp
        avatar["updated_at"] = time.time()
        
        # Update history
        self.avatar_history[avatar_id].append({
            "action": "updated",
            "timestamp": time.time(),
            "details": {
                "name": name,
                "description": description,
                "metadata_updated": metadata is not None,
                "groups_updated": groups is not None,
                "relationships_updated": relationships is not None
            }
        })
        
        # Update search index
        self._update_search_index(avatar_id, avatar, self.avatar_metadata.get(avatar_id, {}))
        
        logger.info(f"Updated avatar {avatar_id}")
        return True

    def update_avatar_status(
        self,
        avatar_id: str,
        status: AvatarStatus,
        reason: Optional[str] = None
    ) -> bool:
        """
        Update the status of an avatar.
        
        Args:
            avatar_id: ID of the avatar to update
            status: New status for the avatar
            reason: Optional reason for the status change
            
        Returns:
            True if update was successful, False otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} does not exist")
            return False
        
        # Get current status
        current_status = self.avatar_status.get(avatar_id, AvatarStatus.ACTIVE.value)
        
        # Update status
        self.avatar_status[avatar_id] = status.value
        
        # Update history
        self.avatar_history[avatar_id].append({
            "action": "status_changed",
            "timestamp": time.time(),
            "details": {
                "from_status": current_status,
                "to_status": status.value,
                "reason": reason
            }
        })
        
        logger.info(f"Updated status of avatar {avatar_id} to {status.value}")
        return True

    def add_avatar_to_group(self, avatar_id: str, group: str) -> bool:
        """
        Add an avatar to a group.
        
        Args:
            avatar_id: ID of the avatar to add
            group: Group to add the avatar to
            
        Returns:
            True if addition was successful, False otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} does not exist")
            return False
        
        # Create group if it doesn't exist
        if group not in self.avatar_groups:
            self.avatar_groups[group] = []
        
        # Add avatar to group if not already in it
        if avatar_id not in self.avatar_groups[group]:
            self.avatar_groups[group].append(avatar_id)
            
            # Update history
            self.avatar_history[avatar_id].append({
                "action": "added_to_group",
                "timestamp": time.time(),
                "details": {
                    "group": group
                }
            })
            
            logger.info(f"Added avatar {avatar_id} to group {group}")
            return True
        
        return False

    def remove_avatar_from_group(self, avatar_id: str, group: str) -> bool:
        """
        Remove an avatar from a group.
        
        Args:
            avatar_id: ID of the avatar to remove
            group: Group to remove the avatar from
            
        Returns:
            True if removal was successful, False otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} does not exist")
            return False
        
        if group not in self.avatar_groups:
            logger.warning(f"Group {group} does not exist")
            return False
        
        # Remove avatar from group if in it
        if avatar_id in self.avatar_groups[group]:
            self.avatar_groups[group].remove(avatar_id)
            
            # Update history
            self.avatar_history[avatar_id].append({
                "action": "removed_from_group",
                "timestamp": time.time(),
                "details": {
                    "group": group
                }
            })
            
            logger.info(f"Removed avatar {avatar_id} from group {group}")
            return True
        
        return False

    def add_avatar_relationship(
        self,
        avatar_id: str,
        related_avatar_id: str,
        relationship_type: str
    ) -> bool:
        """
        Add a relationship between avatars.
        
        Args:
            avatar_id: ID of the avatar to add relationship to
            related_avatar_id: ID of the related avatar
            relationship_type: Type of relationship
            
        Returns:
            True if addition was successful, False otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} does not exist")
            return False
        
        if related_avatar_id not in self.avatars:
            logger.warning(f"Related avatar with ID {related_avatar_id} does not exist")
            return False
        
        # Initialize relationships if needed
        if avatar_id not in self.avatar_relationships:
            self.avatar_relationships[avatar_id] = {}
        
        # Initialize relationship type if needed
        if relationship_type not in self.avatar_relationships[avatar_id]:
            self.avatar_relationships[avatar_id][relationship_type] = []
        
        # Add relationship if not already exists
        if related_avatar_id not in self.avatar_relationships[avatar_id][relationship_type]:
            self.avatar_relationships[avatar_id][relationship_type].append(related_avatar_id)
            
            # Update history
            self.avatar_history[avatar_id].append({
                "action": "relationship_added",
                "timestamp": time.time(),
                "details": {
                    "related_avatar_id": related_avatar_id,
                    "relationship_type": relationship_type
                }
            })
            
            logger.info(f"Added relationship {relationship_type} from avatar {avatar_id} to {related_avatar_id}")
            return True
        
        return False

    def remove_avatar_relationship(
        self,
        avatar_id: str,
        related_avatar_id: str,
        relationship_type: str
    ) -> bool:
        """
        Remove a relationship between avatars.
        
        Args:
            avatar_id: ID of the avatar to remove relationship from
            related_avatar_id: ID of the related avatar
            relationship_type: Type of relationship
            
        Returns:
            True if removal was successful, False otherwise
        """
        if avatar_id not in self.avatars:
            logger.warning(f"Avatar with ID {avatar_id} does not exist")
            return False
        
        if avatar_id not in self.avatar_relationships:
            logger.warning(f"Avatar with ID {avatar_id} has no relationships")
            return False
        
        if relationship_type not in self.avatar_relationships[avatar_id]:
            logger.warning(f"Avatar with ID {avatar_id} has no relationships of type {relationship_type}")
            return False
        
        # Remove relationship if exists
        if related_avatar_id in self.avatar_relationships[avatar_id][relationship_type]:
            self.avatar_relationships[avatar_id][relationship_type].remove(related_avatar_id)
            
            # Update history
            self.avatar_history[avatar_id].append({
                "action": "relationship_removed",
                "timestamp": time.time(),
                "details": {
                    "related_avatar_id": related_avatar_id,
                    "relationship_type": relationship_type
                }
            })
            
            logger.info(f"Removed relationship {relationship_type} from avatar {avatar_id} to {related_avatar_id}")
            return True
        
        return False

    def get_avatar_history(self, avatar_id: str) -> List[Dict[str, Any]]:
        """
        Get the history of an avatar.
        
        Args:
            avatar_id: ID of the avatar to get history for
            
        Returns:
            List of history records
        """
        if avatar_id not in self.avatar_history:
            logger.warning(f"Avatar with ID {avatar_id} has no history")
            return []
        
        return self.avatar_history[avatar_id]

    def search_avatars(
        self,
        query: str,
        avatar_type: Optional[AvatarType] = None,
        group: Optional[str] = None,
        status: Optional[AvatarStatus] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for avatars matching a query.
        
        Args:
            query: Search query
            avatar_type: Optional type of avatars to search
            group: Optional group to search in
            status: Optional status to filter by
            
        Returns:
            List of matching avatar records
        """
        # Convert query to lowercase for case-insensitive search
        query = query.lower()
        
        # Get all avatar IDs
        avatar_ids = set(self.avatars.keys())
        
        # Filter by type if provided
        if avatar_type:
            type_ids = set(self.avatar_types.get(avatar_type.value, []))
            avatar_ids = avatar_ids.intersection(type_ids)
        
        # Filter by group if provided
        if group:
            group_ids = set(self.avatar_groups.get(group, []))
            avatar_ids = avatar_ids.intersection(group_ids)
        
        # Filter by status if provided
        if status:
            status_ids = {
                avatar_id for avatar_id, avatar_status in self.avatar_status.items()
                if avatar_status == status.value
            }
            avatar_ids = avatar_ids.intersection(status_ids)
        
        # Search in index
        matching_ids = set()
        
        for avatar_id, index_data in self.avatar_search_index.items():
            if avatar_id not in avatar_ids:
                continue
            
            # Check if query matches any indexed field
            for field, value in index_data.items():
                if query in value:
                    matching_ids.add(avatar_id)
                    break
        
        # Get avatar records for matching IDs
        avatars = []
        
        for avatar_id in matching_ids:
            avatar = self.get_avatar(avatar_id)
            if avatar:
                avatars.append(avatar)
        
        return avatars

    def _update_search_index(
        self,
        avatar_id: str,
        avatar: Dict[str, Any],
        metadata: Dict[str, Any]
    ):
        """
        Update the search index for an avatar.
        
        Args:
            avatar_id: ID of the avatar to update
            avatar: Avatar record
            metadata: Avatar metadata
        """
        # Initialize index entry
        self.avatar_search_index[avatar_id] = {}
        
        # Index basic fields
        self.avatar_search_index[avatar_id]["id"] = avatar_id.lower()
        self.avatar_search_index[avatar_id]["type"] = avatar.get("type", "").lower()
        self.avatar_search_index[avatar_id]["name"] = avatar.get("name", "").lower()
        self.avatar_search_index[avatar_id]["description"] = avatar.get("description", "").lower()
        
        # Index metadata fields
        for key, value in metadata.items():
            if isinstance(value, (str, int, float, bool)):
                self.avatar_search_index[avatar_id][f"metadata.{key}"] = str(value).lower()

    def export_avatars(self, format: str = "json") -> str:
        """
        Export all avatars in specified format.
        
        Args:
            format: Export format ("json" or "csv")
            
        Returns:
            Exported avatars as string
        """
        if format.lower() == "json":
            # Export all avatars with metadata and status
            export_data = []
            
            for avatar_id, avatar in self.avatars.items():
                export_avatar = avatar.copy()
                
                # Add metadata
                if avatar_id in self.avatar_metadata:
                    export_avatar["metadata"] = self.avatar_metadata[avatar_id]
                
                # Add status
                if avatar_id in self.avatar_status:
                    export_avatar["status"] = self.avatar_status[avatar_id]
                
                # Add groups
                export_avatar["groups"] = []
                for group, avatars in self.avatar_groups.items():
                    if avatar_id in avatars:
                        export_avatar["groups"].append(group)
                
                # Add relationships
                if avatar_id in self.avatar_relationships:
                    export_avatar["relationships"] = self.avatar_relationships[avatar_id]
                
                export_data.append(export_avatar)
            
            return json.dumps(export_data, indent=2)
        
        elif format.lower() == "csv":
            # Create CSV header
            csv_lines = ["id,type,name,description,status,created_at,updated_at"]
            
            # Add data rows
            for avatar_id, avatar in self.avatars.items():
                avatar_id = avatar.get("id", "")
                avatar_type = avatar.get("type", "")
                name = avatar.get("name", "").replace(",", " ")
                description = avatar.get("description", "").replace(",", " ")
                status = self.avatar_status.get(avatar_id, "")
                created_at = avatar.get("created_at", "")
                updated_at = avatar.get("updated_at", "")
                
                csv_line = f"{avatar_id},{avatar_type},{name},{description},{status},{created_at},{updated_at}"
                csv_lines.append(csv_line)
            
            return "\n".join(csv_lines)
        
        else:
            raise ValueError(f"Unsupported export format: {format}")

    def import_avatars(self, data: str, format: str = "json") -> int:
        """
        Import avatars from specified format.
        
        Args:
            data: Data to import
            format: Import format ("json" or "csv")
            
        Returns:
            Number of avatars imported
        """
        imported_count = 0
        
        if format.lower() == "json":
            try:
                avatars = json.loads(data)
                
                for avatar_data in avatars:
                    avatar_id = avatar_data.get("id")
                    
                    if not avatar_id:
                        logger.warning("Skipping avatar with no ID")
                        continue
                    
                    # Extract basic fields
                    avatar_type_str = avatar_data.get("type")
                    try:
                        avatar_type = AvatarType(avatar_type_str)
                    except ValueError:
                        logger.warning(f"Skipping avatar with invalid type: {avatar_type_str}")
                        continue
                    
                    name = avatar_data.get("name", "")
                    description = avatar_data.get("description", "")
                    metadata = avatar_data.get("metadata", {})
                    groups = avatar_data.get("groups", [])
                    relationships = avatar_data.get("relationships", {})
                    
                    # Register avatar
                    if self.register_avatar(
                        avatar_id=avatar_id,
                        avatar_type=avatar_type,
                        name=name,
                        description=description,
                        metadata=metadata,
                        groups=groups,
                        relationships=relationships
                    ):
                        imported_count += 1
                        
                        # Set status if provided
                        if "status" in avatar_data:
                            try:
                                status = AvatarStatus(avatar_data["status"])
                                self.update_avatar_status(
                                    avatar_id=avatar_id,
                                    status=status,
                                    reason="Imported"
                                )
                            except ValueError:
                                logger.warning(f"Invalid status for avatar {avatar_id}: {avatar_data['status']}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding JSON: {e}")
                raise ValueError(f"Invalid JSON data: {e}")
        
        elif format.lower() == "csv":
            lines = data.strip().split("\n")
            
            if len(lines) < 2:
                logger.warning("CSV data has no records")
                return 0
            
            # Parse header
            header = lines[0].split(",")
            
            if len(header) < 3 or header[0] != "id" or header[1] != "type" or header[2] != "name":
                logger.warning("CSV header is invalid")
                raise ValueError("Invalid CSV header")
            
            # Parse records
            for i in range(1, len(lines)):
                fields = lines[i].split(",")
                
                if len(fields) < len(header):
                    logger.warning(f"Skipping record with insufficient fields: {lines[i]}")
                    continue
                
                # Extract fields
                record = {}
                for j in range(len(header)):
                    record[header[j]] = fields[j]
                
                avatar_id = record.get("id")
                avatar_type_str = record.get("type")
                
                if not avatar_id or not avatar_type_str:
                    logger.warning("Skipping record with no ID or type")
                    continue
                
                try:
                    avatar_type = AvatarType(avatar_type_str)
                except ValueError:
                    logger.warning(f"Skipping record with invalid type: {avatar_type_str}")
                    continue
                
                name = record.get("name", "")
                description = record.get("description", "")
                
                # Register avatar
                if self.register_avatar(
                    avatar_id=avatar_id,
                    avatar_type=avatar_type,
                    name=name,
                    description=description
                ):
                    imported_count += 1
                    
                    # Set status if provided
                    if "status" in record:
                        try:
                            status = AvatarStatus(record["status"])
                            self.update_avatar_status(
                                avatar_id=avatar_id,
                                status=status,
                                reason="Imported"
                            )
                        except ValueError:
                            logger.warning(f"Invalid status for avatar {avatar_id}: {record['status']}")
        
        else:
            raise ValueError(f"Unsupported import format: {format}")
        
        logger.info(f"Imported {imported_count} avatars")
        return imported_count

    def get_avatar_count(
        self,
        avatar_type: Optional[AvatarType] = None,
        group: Optional[str] = None,
        status: Optional[AvatarStatus] = None
    ) -> int:
        """
        Get the number of avatars, optionally filtered.
        
        Args:
            avatar_type: Optional type of avatars to count
            group: Optional group to count in
            status: Optional status to filter by
            
        Returns:
            Number of avatars
        """
        # Get all avatar IDs
        avatar_ids = set(self.avatars.keys())
        
        # Filter by type if provided
        if avatar_type:
            type_ids = set(self.avatar_types.get(avatar_type.value, []))
            avatar_ids = avatar_ids.intersection(type_ids)
        
        # Filter by group if provided
        if group:
            group_ids = set(self.avatar_groups.get(group, []))
            avatar_ids = avatar_ids.intersection(group_ids)
        
        # Filter by status if provided
        if status:
            status_ids = {
                avatar_id for avatar_id, avatar_status in self.avatar_status.items()
                if avatar_status == status.value
            }
            avatar_ids = avatar_ids.intersection(status_ids)
        
        return len(avatar_ids)

    def get_avatar_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about avatars in the registry.
        
        Returns:
            Dictionary of avatar statistics
        """
        # Count avatars by type
        type_counts = {}
        for avatar_type, avatar_ids in self.avatar_types.items():
            type_counts[avatar_type] = len(avatar_ids)
        
        # Count avatars by status
        status_counts = {}
        for avatar_id, status in self.avatar_status.items():
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count avatars by group
        group_counts = {}
        for group, avatar_ids in self.avatar_groups.items():
            group_counts[group] = len(avatar_ids)
        
        # Count relationships
        relationship_counts = {}
        for avatar_id, relationships in self.avatar_relationships.items():
            for rel_type, rel_ids in relationships.items():
                relationship_counts[rel_type] = relationship_counts.get(rel_type, 0) + len(rel_ids)
        
        return {
            "total_avatars": len(self.avatars),
            "by_type": type_counts,
            "by_status": status_counts,
            "by_group": group_counts,
            "relationships": relationship_counts
        }
