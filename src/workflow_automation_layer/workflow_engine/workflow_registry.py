"""
Workflow Registry Module for Industriverse Workflow Automation Layer

This module is responsible for registering, storing, and retrieving workflow
manifests. It provides a central registry for all workflows in the system,
with versioning, search, and metadata management capabilities.

The WorkflowRegistry class is the central component that manages the lifecycle
of workflow definitions across the Industriverse ecosystem.
"""

import logging
import os
import json
import uuid
from enum import Enum
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import yaml
from pydantic import BaseModel, Field

# Local imports
from .workflow_manifest_parser import WorkflowManifest, WorkflowManifestParser

# Configure logging
logger = logging.getLogger(__name__)


class RegistryStorageType(str, Enum):
    """Enum representing the storage types for the workflow registry."""
    MEMORY = "memory"
    FILE = "file"
    DATABASE = "database"


class WorkflowMetadata(BaseModel):
    """Model representing metadata for a workflow in the registry."""
    id: str
    name: str
    description: Optional[str] = None
    version: str
    created_at: datetime
    updated_at: datetime
    author: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    industry: Optional[str] = None
    status: str = "active"
    execution_count: int = 0
    average_execution_time_ms: Optional[float] = None
    success_rate: Optional[float] = None
    last_executed: Optional[datetime] = None


class WorkflowRegistry:
    """
    Registry for workflow manifests.
    
    This class provides methods to register, retrieve, search, and manage
    workflow manifests across the Industriverse ecosystem.
    """
    
    def __init__(self, storage_type: RegistryStorageType = RegistryStorageType.MEMORY, storage_path: Optional[str] = None):
        """
        Initialize the WorkflowRegistry.
        
        Args:
            storage_type: The type of storage to use for the registry
            storage_path: The path to use for file storage (if applicable)
        """
        self.storage_type = storage_type
        self.storage_path = storage_path
        
        # In-memory storage
        self.workflows: Dict[str, WorkflowManifest] = {}
        self.metadata: Dict[str, WorkflowMetadata] = {}
        
        # Initialize storage
        if storage_type == RegistryStorageType.FILE and storage_path:
            os.makedirs(storage_path, exist_ok=True)
            
            # Load existing workflows from storage
            self._load_from_storage()
        
        logger.info(f"WorkflowRegistry initialized with {storage_type} storage")
    
    def _load_from_storage(self):
        """Load existing workflows from storage."""
        if self.storage_type != RegistryStorageType.FILE or not self.storage_path:
            return
        
        try:
            # Load metadata index
            metadata_path = os.path.join(self.storage_path, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    metadata_dict = json.load(f)
                    for workflow_id, meta in metadata_dict.items():
                        # Convert string dates to datetime
                        meta["created_at"] = datetime.fromisoformat(meta["created_at"])
                        meta["updated_at"] = datetime.fromisoformat(meta["updated_at"])
                        if meta.get("last_executed"):
                            meta["last_executed"] = datetime.fromisoformat(meta["last_executed"])
                        
                        self.metadata[workflow_id] = WorkflowMetadata(**meta)
            
            # Load workflow manifests
            workflows_dir = os.path.join(self.storage_path, "workflows")
            if os.path.exists(workflows_dir):
                for filename in os.listdir(workflows_dir):
                    if filename.endswith(".yaml") or filename.endswith(".yml"):
                        workflow_id = filename.split(".")[0]
                        workflow_path = os.path.join(workflows_dir, filename)
                        
                        with open(workflow_path, "r") as f:
                            yaml_str = f.read()
                            manifest = WorkflowManifestParser.parse_from_yaml(yaml_str)
                            self.workflows[workflow_id] = manifest
            
            logger.info(f"Loaded {len(self.workflows)} workflows from storage")
        except Exception as e:
            logger.error(f"Failed to load workflows from storage: {e}")
    
    def _save_to_storage(self, workflow_id: str):
        """
        Save a workflow to storage.
        
        Args:
            workflow_id: The ID of the workflow to save
        """
        if self.storage_type != RegistryStorageType.FILE or not self.storage_path:
            return
        
        try:
            # Create workflows directory if it doesn't exist
            workflows_dir = os.path.join(self.storage_path, "workflows")
            os.makedirs(workflows_dir, exist_ok=True)
            
            # Save workflow manifest
            workflow = self.workflows.get(workflow_id)
            if workflow:
                workflow_path = os.path.join(workflows_dir, f"{workflow_id}.yaml")
                with open(workflow_path, "w") as f:
                    f.write(WorkflowManifestParser.to_yaml(workflow))
            
            # Save metadata index
            metadata_dict = {}
            for wf_id, meta in self.metadata.items():
                # Convert datetime to string for JSON serialization
                meta_dict = meta.dict()
                meta_dict["created_at"] = meta_dict["created_at"].isoformat()
                meta_dict["updated_at"] = meta_dict["updated_at"].isoformat()
                if meta_dict.get("last_executed"):
                    meta_dict["last_executed"] = meta_dict["last_executed"].isoformat()
                
                metadata_dict[wf_id] = meta_dict
            
            metadata_path = os.path.join(self.storage_path, "metadata.json")
            with open(metadata_path, "w") as f:
                json.dump(metadata_dict, f, indent=2)
            
            logger.debug(f"Saved workflow {workflow_id} to storage")
        except Exception as e:
            logger.error(f"Failed to save workflow {workflow_id} to storage: {e}")
    
    def register_workflow(self, manifest: Union[str, Dict, WorkflowManifest]) -> str:
        """
        Register a new workflow manifest.
        
        Args:
            manifest: The workflow manifest as a YAML string, dict, or WorkflowManifest object
            
        Returns:
            The ID of the registered workflow
            
        Raises:
            ValueError: If the manifest is invalid
        """
        # Parse the manifest if it's not already a WorkflowManifest
        if isinstance(manifest, str):
            try:
                manifest = WorkflowManifestParser.parse_from_yaml(manifest)
            except Exception as e:
                logger.error(f"Failed to parse workflow manifest: {e}")
                raise ValueError(f"Invalid workflow manifest: {e}")
        elif isinstance(manifest, dict):
            try:
                manifest = WorkflowManifestParser.parse_from_dict(manifest)
            except Exception as e:
                logger.error(f"Failed to parse workflow manifest: {e}")
                raise ValueError(f"Invalid workflow manifest: {e}")
        
        # Validate the manifest
        errors = WorkflowManifestParser.validate(manifest)
        if errors:
            error_msg = "; ".join(errors)
            logger.error(f"Invalid workflow manifest: {error_msg}")
            raise ValueError(f"Invalid workflow manifest: {error_msg}")
        
        # Generate an ID if not provided
        workflow_id = manifest.id if hasattr(manifest, 'id') else str(uuid.uuid4())
        
        # Store the manifest
        self.workflows[workflow_id] = manifest
        
        # Create metadata
        metadata = WorkflowMetadata(
            id=workflow_id,
            name=manifest.name,
            description=manifest.description,
            version=manifest.version,
            created_at=manifest.created_at,
            updated_at=manifest.updated_at,
            author=manifest.author,
            tags=manifest.tags,
            industry=manifest.industry
        )
        self.metadata[workflow_id] = metadata
        
        # Save to storage
        self._save_to_storage(workflow_id)
        
        logger.info(f"Registered workflow {workflow_id}: {manifest.name}")
        return workflow_id
    
    def get_workflow(self, workflow_id: str) -> Optional[WorkflowManifest]:
        """
        Get a workflow manifest by ID.
        
        Args:
            workflow_id: The ID of the workflow to retrieve
            
        Returns:
            The WorkflowManifest if found, None otherwise
        """
        return self.workflows.get(workflow_id)
    
    def get_metadata(self, workflow_id: str) -> Optional[WorkflowMetadata]:
        """
        Get workflow metadata by ID.
        
        Args:
            workflow_id: The ID of the workflow to retrieve metadata for
            
        Returns:
            The WorkflowMetadata if found, None otherwise
        """
        return self.metadata.get(workflow_id)
    
    def update_workflow(self, workflow_id: str, manifest: Union[str, Dict, WorkflowManifest]) -> bool:
        """
        Update an existing workflow manifest.
        
        Args:
            workflow_id: The ID of the workflow to update
            manifest: The updated workflow manifest
            
        Returns:
            True if the workflow was updated, False if it wasn't found
            
        Raises:
            ValueError: If the manifest is invalid
        """
        if workflow_id not in self.workflows:
            logger.warning(f"Attempted to update non-existent workflow {workflow_id}")
            return False
        
        # Parse the manifest if it's not already a WorkflowManifest
        if isinstance(manifest, str):
            try:
                manifest = WorkflowManifestParser.parse_from_yaml(manifest)
            except Exception as e:
                logger.error(f"Failed to parse workflow manifest: {e}")
                raise ValueError(f"Invalid workflow manifest: {e}")
        elif isinstance(manifest, dict):
            try:
                manifest = WorkflowManifestParser.parse_from_dict(manifest)
            except Exception as e:
                logger.error(f"Failed to parse workflow manifest: {e}")
                raise ValueError(f"Invalid workflow manifest: {e}")
        
        # Validate the manifest
        errors = WorkflowManifestParser.validate(manifest)
        if errors:
            error_msg = "; ".join(errors)
            logger.error(f"Invalid workflow manifest: {error_msg}")
            raise ValueError(f"Invalid workflow manifest: {error_msg}")
        
        # Preserve the ID and created_at
        old_manifest = self.workflows[workflow_id]
        manifest.id = workflow_id
        manifest.created_at = old_manifest.created_at
        manifest.updated_at = datetime.now()
        
        # Update the manifest
        self.workflows[workflow_id] = manifest
        
        # Update metadata
        metadata = self.metadata[workflow_id]
        metadata.name = manifest.name
        metadata.description = manifest.description
        metadata.version = manifest.version
        metadata.updated_at = manifest.updated_at
        metadata.author = manifest.author
        metadata.tags = manifest.tags
        metadata.industry = manifest.industry
        
        # Save to storage
        self._save_to_storage(workflow_id)
        
        logger.info(f"Updated workflow {workflow_id}")
        return True
    
    def delete_workflow(self, workflow_id: str) -> bool:
        """
        Delete a workflow manifest.
        
        Args:
            workflow_id: The ID of the workflow to delete
            
        Returns:
            True if the workflow was deleted, False if it wasn't found
        """
        if workflow_id not in self.workflows:
            logger.warning(f"Attempted to delete non-existent workflow {workflow_id}")
            return False
        
        # Remove from memory
        del self.workflows[workflow_id]
        del self.metadata[workflow_id]
        
        # Remove from storage
        if self.storage_type == RegistryStorageType.FILE and self.storage_path:
            try:
                workflow_path = os.path.join(self.storage_path, "workflows", f"{workflow_id}.yaml")
                if os.path.exists(workflow_path):
                    os.remove(workflow_path)
                
                # Update metadata index
                self._save_to_storage("")  # Empty ID to just update the metadata index
            except Exception as e:
                logger.error(f"Failed to delete workflow {workflow_id} from storage: {e}")
        
        logger.info(f"Deleted workflow {workflow_id}")
        return True
    
    def list_workflows(self, 
                      tags: Optional[List[str]] = None,
                      industry: Optional[str] = None,
                      status: Optional[str] = None) -> List[WorkflowMetadata]:
        """
        List workflow metadata, optionally filtered by various criteria.
        
        Args:
            tags: Filter by tags (workflows must have all specified tags)
            industry: Filter by industry
            status: Filter by status
            
        Returns:
            A list of WorkflowMetadata objects matching the criteria
        """
        result = list(self.metadata.values())
        
        # Apply filters
        if tags:
            result = [m for m in result if all(tag in m.tags for tag in tags)]
        
        if industry:
            result = [m for m in result if m.industry == industry]
        
        if status:
            result = [m for m in result if m.status == status]
        
        return result
    
    def search_workflows(self, query: str) -> List[WorkflowMetadata]:
        """
        Search for workflows by name, description, or tags.
        
        Args:
            query: The search query
            
        Returns:
            A list of WorkflowMetadata objects matching the query
        """
        query = query.lower()
        result = []
        
        for metadata in self.metadata.values():
            # Check name
            if query in metadata.name.lower():
                result.append(metadata)
                continue
            
            # Check description
            if metadata.description and query in metadata.description.lower():
                result.append(metadata)
                continue
            
            # Check tags
            if any(query in tag.lower() for tag in metadata.tags):
                result.append(metadata)
                continue
        
        return result
    
    def update_execution_stats(self, workflow_id: str, execution_time_ms: float, success: bool):
        """
        Update execution statistics for a workflow.
        
        Args:
            workflow_id: The ID of the workflow
            execution_time_ms: The execution time in milliseconds
            success: Whether the execution was successful
            
        Returns:
            True if the stats were updated, False if the workflow wasn't found
        """
        if workflow_id not in self.metadata:
            logger.warning(f"Attempted to update stats for non-existent workflow {workflow_id}")
            return False
        
        metadata = self.metadata[workflow_id]
        
        # Update execution count
        metadata.execution_count += 1
        
        # Update average execution time
        if metadata.average_execution_time_ms is None:
            metadata.average_execution_time_ms = execution_time_ms
        else:
            # Weighted average (more weight to recent executions)
            metadata.average_execution_time_ms = (
                0.8 * metadata.average_execution_time_ms + 0.2 * execution_time_ms
            )
        
        # Update success rate
        if metadata.success_rate is None:
            metadata.success_rate = 100.0 if success else 0.0
        else:
            # Weighted success rate (more weight to recent executions)
            success_value = 100.0 if success else 0.0
            metadata.success_rate = 0.9 * metadata.success_rate + 0.1 * success_value
        
        # Update last executed
        metadata.last_executed = datetime.now()
        
        # Save to storage
        self._save_to_storage(workflow_id)
        
        return True
    
    def export_workflow(self, workflow_id: str, format: str = "yaml") -> str:
        """
        Export a workflow manifest to a specific format.
        
        Args:
            workflow_id: The ID of the workflow to export
            format: The format to export to ("yaml" or "json")
            
        Returns:
            The exported workflow as a string
            
        Raises:
            ValueError: If the workflow doesn't exist or the format is invalid
        """
        workflow = self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if format.lower() == "yaml":
            return WorkflowManifestParser.to_yaml(workflow)
        elif format.lower() == "json":
            # Convert to dict first to handle datetime serialization
            workflow_dict = workflow.dict()
            
            # Convert datetime objects to ISO format strings
            workflow_dict['created_at'] = workflow_dict['created_at'].isoformat()
            workflow_dict['updated_at'] = workflow_dict['updated_at'].isoformat()
            
            return json.dumps(workflow_dict, indent=2)
        else:
            raise ValueError(f"Invalid export format: {format}")
    
    def import_workflow(self, content: str, format: str = "yaml") -> str:
        """
        Import a workflow manifest from a specific format.
        
        Args:
            content: The workflow manifest content
            format: The format of the content ("yaml" or "json")
            
        Returns:
            The ID of the imported workflow
            
        Raises:
            ValueError: If the content is invalid or the format is invalid
        """
        if format.lower() == "yaml":
            try:
                manifest = WorkflowManifestParser.parse_from_yaml(content)
            except Exception as e:
                logger.error(f"Failed to parse YAML: {e}")
                raise ValueError(f"Invalid YAML: {e}")
        elif format.lower() == "json":
            try:
                manifest_dict = json.loads(content)
                manifest = WorkflowManifestParser.parse_from_dict(manifest_dict)
            except Exception as e:
                logger.error(f"Failed to parse JSON: {e}")
                raise ValueError(f"Invalid JSON: {e}")
        else:
            raise ValueError(f"Invalid import format: {format}")
        
        return self.register_workflow(manifest)
