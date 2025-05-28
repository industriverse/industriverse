"""
Manifest Manager - Manages deployment manifests

This module manages deployment manifests, providing storage, retrieval,
and validation capabilities for manifests.
"""

import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os
import uuid
import yaml

logger = logging.getLogger(__name__)

class ManifestManager:
    """
    Manages deployment manifests.
    
    This component is responsible for managing deployment manifests, providing
    storage, retrieval, and validation capabilities for manifests.
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Manifest Manager.
        
        Args:
            config: Configuration dictionary for the manager
        """
        self.config = config or {}
        self.manifests = {}  # Manifest ID -> Manifest
        self.manifest_index = {}  # Index for searching manifests
        self.manifest_categories = {}  # Category -> List of manifest IDs
        self.manifest_tags = {}  # Tag -> List of manifest IDs
        self.manifest_history = {}  # Manifest ID -> List of history events
        self.max_history_length = self.config.get("max_history_length", 100)
        
        logger.info("Initializing Manifest Manager")
    
    def initialize(self):
        """Initialize the manager and load manifests."""
        logger.info("Initializing Manifest Manager")
        
        # Load manifests
        self._load_manifests()
        
        # Build indexes
        self._build_indexes()
        
        logger.info(f"Loaded {len(self.manifests)} manifests")
        return True
    
    def create_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new manifest.
        
        Args:
            manifest: Manifest definition
            
        Returns:
            Dictionary with creation result
        """
        logger.info("Creating new manifest")
        
        # Validate manifest
        if not self._validate_manifest(manifest):
            logger.error("Invalid manifest")
            return {"success": False, "error": "Invalid manifest"}
        
        # Generate manifest ID if not provided
        manifest_id = manifest.get("id")
        if not manifest_id:
            manifest_id = str(uuid.uuid4())
            manifest["id"] = manifest_id
        
        # Check if manifest already exists
        if manifest_id in self.manifests:
            logger.warning(f"Manifest {manifest_id} already exists")
            return {"success": False, "error": "Manifest already exists"}
        
        # Add timestamps if not provided
        if "created" not in manifest:
            manifest["created"] = datetime.now().isoformat()
        
        if "updated" not in manifest:
            manifest["updated"] = manifest["created"]
        
        # Create manifest
        self.manifests[manifest_id] = manifest
        
        # Update indexes
        self._update_indexes(manifest_id, manifest)
        
        # Initialize history
        self.manifest_history[manifest_id] = []
        
        # Record creation event
        self._record_history_event(manifest_id, "create", "Manifest created")
        
        # Save manifests
        self._save_manifests()
        
        logger.info(f"Created manifest {manifest_id}")
        
        return {
            "success": True,
            "manifest_id": manifest_id
        }
    
    def get_manifest(self, manifest_id: str) -> Dict[str, Any]:
        """
        Get a manifest.
        
        Args:
            manifest_id: ID of the manifest
            
        Returns:
            Dictionary with manifest retrieval result
        """
        # Check if manifest exists
        if manifest_id not in self.manifests:
            logger.warning(f"Manifest {manifest_id} not found")
            return {"success": False, "error": "Manifest not found"}
        
        # Get manifest
        manifest = self.manifests[manifest_id]
        
        logger.info(f"Retrieved manifest {manifest_id}")
        
        return {
            "success": True,
            "manifest": manifest
        }
    
    def update_manifest(self, manifest_id: str, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a manifest.
        
        Args:
            manifest_id: ID of the manifest
            manifest: Updated manifest definition
            
        Returns:
            Dictionary with update result
        """
        logger.info(f"Updating manifest {manifest_id}")
        
        # Check if manifest exists
        if manifest_id not in self.manifests:
            logger.warning(f"Manifest {manifest_id} not found")
            return {"success": False, "error": "Manifest not found"}
        
        # Validate manifest
        if not self._validate_manifest(manifest):
            logger.error("Invalid manifest")
            return {"success": False, "error": "Invalid manifest"}
        
        # Ensure manifest ID is correct
        if "id" in manifest and manifest["id"] != manifest_id:
            logger.error("Manifest ID mismatch")
            return {"success": False, "error": "Manifest ID mismatch"}
        
        manifest["id"] = manifest_id
        
        # Update timestamp
        manifest["updated"] = datetime.now().isoformat()
        
        # Preserve creation timestamp
        if "created" not in manifest:
            manifest["created"] = self.manifests[manifest_id].get("created")
        
        # Get old manifest
        old_manifest = self.manifests[manifest_id]
        
        # Update manifest
        self.manifests[manifest_id] = manifest
        
        # Update indexes
        self._remove_from_indexes(manifest_id, old_manifest)
        self._update_indexes(manifest_id, manifest)
        
        # Record update event
        self._record_history_event(manifest_id, "update", "Manifest updated")
        
        # Save manifests
        self._save_manifests()
        
        logger.info(f"Updated manifest {manifest_id}")
        
        return {
            "success": True,
            "manifest_id": manifest_id
        }
    
    def delete_manifest(self, manifest_id: str) -> Dict[str, Any]:
        """
        Delete a manifest.
        
        Args:
            manifest_id: ID of the manifest
            
        Returns:
            Dictionary with deletion result
        """
        logger.info(f"Deleting manifest {manifest_id}")
        
        # Check if manifest exists
        if manifest_id not in self.manifests:
            logger.warning(f"Manifest {manifest_id} not found")
            return {"success": False, "error": "Manifest not found"}
        
        # Get manifest
        manifest = self.manifests[manifest_id]
        
        # Delete manifest
        del self.manifests[manifest_id]
        
        # Update indexes
        self._remove_from_indexes(manifest_id, manifest)
        
        # Record deletion event
        self._record_history_event(manifest_id, "delete", "Manifest deleted")
        
        # Save manifests
        self._save_manifests()
        
        logger.info(f"Deleted manifest {manifest_id}")
        
        return {
            "success": True,
            "manifest_id": manifest_id
        }
    
    def search_manifests(self, query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search for manifests.
        
        Args:
            query: Search query
            
        Returns:
            Dictionary with search results
        """
        logger.info("Searching manifests")
        
        # Initialize result set with all manifest IDs
        result_set = set(self.manifests.keys())
        
        # Apply filters
        if "category" in query:
            category = query["category"]
            if category in self.manifest_categories:
                category_manifests = set(self.manifest_categories[category])
                result_set = result_set.intersection(category_manifests)
            else:
                # No manifests in this category
                result_set = set()
        
        if "tags" in query and query["tags"]:
            tags = query["tags"]
            for tag in tags:
                if tag in self.manifest_tags:
                    tag_manifests = set(self.manifest_tags[tag])
                    result_set = result_set.intersection(tag_manifests)
                else:
                    # No manifests with this tag
                    result_set = set()
                    break
        
        if "text" in query and query["text"]:
            text = query["text"].lower()
            text_results = set()
            
            # Search in manifest index
            for manifest_id, indexed_text in self.manifest_index.items():
                if text in indexed_text:
                    text_results.add(manifest_id)
            
            result_set = result_set.intersection(text_results)
        
        # Get manifests
        results = []
        for manifest_id in result_set:
            manifest = self.manifests[manifest_id]
            results.append(manifest)
        
        # Sort results
        if "sort_by" in query:
            sort_by = query["sort_by"]
            reverse = query.get("sort_order", "asc").lower() == "desc"
            
            if sort_by in ["name", "created", "updated", "category"]:
                results.sort(key=lambda m: m.get(sort_by, ""), reverse=reverse)
        
        # Apply pagination
        page = query.get("page", 1)
        page_size = query.get("page_size", 10)
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        paginated_results = results[start_index:end_index]
        
        logger.info(f"Found {len(results)} manifests, returning {len(paginated_results)} for page {page}")
        
        return {
            "success": True,
            "total": len(results),
            "page": page,
            "page_size": page_size,
            "manifests": paginated_results
        }
    
    def get_manifest_history(self, manifest_id: str) -> Dict[str, Any]:
        """
        Get history for a manifest.
        
        Args:
            manifest_id: ID of the manifest
            
        Returns:
            Dictionary with history retrieval result
        """
        # Check if manifest exists
        if manifest_id not in self.manifest_history:
            logger.warning(f"Manifest {manifest_id} not found")
            return {"success": False, "error": "Manifest not found"}
        
        # Get history
        history = self.manifest_history[manifest_id]
        
        logger.info(f"Retrieved history for manifest {manifest_id}")
        
        return {
            "success": True,
            "manifest_id": manifest_id,
            "history": history
        }
    
    def get_manifest_categories(self) -> Dict[str, Any]:
        """
        Get all manifest categories.
        
        Returns:
            Dictionary with categories
        """
        categories = []
        
        for category, manifest_ids in self.manifest_categories.items():
            categories.append({
                "name": category,
                "count": len(manifest_ids)
            })
        
        # Sort categories by name
        categories.sort(key=lambda c: c["name"])
        
        logger.info(f"Retrieved {len(categories)} categories")
        
        return {
            "success": True,
            "categories": categories
        }
    
    def get_manifest_tags(self) -> Dict[str, Any]:
        """
        Get all manifest tags.
        
        Returns:
            Dictionary with tags
        """
        tags = []
        
        for tag, manifest_ids in self.manifest_tags.items():
            tags.append({
                "name": tag,
                "count": len(manifest_ids)
            })
        
        # Sort tags by name
        tags.sort(key=lambda t: t["name"])
        
        logger.info(f"Retrieved {len(tags)} tags")
        
        return {
            "success": True,
            "tags": tags
        }
    
    def export_manifest(self, manifest_id: str, format: str, output_path: str) -> Dict[str, Any]:
        """
        Export a manifest to a file.
        
        Args:
            manifest_id: ID of the manifest
            format: Export format (json, yaml)
            output_path: Path to write the exported manifest to
            
        Returns:
            Dictionary with export result
        """
        logger.info(f"Exporting manifest {manifest_id} to {format} format")
        
        # Check if manifest exists
        if manifest_id not in self.manifests:
            logger.warning(f"Manifest {manifest_id} not found")
            return {"success": False, "error": "Manifest not found"}
        
        # Get manifest
        manifest = self.manifests[manifest_id]
        
        # Validate format
        if format not in ["json", "yaml"]:
            logger.error(f"Unsupported format: {format}")
            return {"success": False, "error": f"Unsupported format: {format}"}
        
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Export based on format
            if format == "json":
                with open(output_path, "w") as f:
                    json.dump(manifest, f, indent=2)
            elif format == "yaml":
                with open(output_path, "w") as f:
                    yaml.dump(manifest, f, default_flow_style=False)
            
            # Record export event
            self._record_history_event(manifest_id, "export", f"Manifest exported to {format} format")
            
            logger.info(f"Exported manifest {manifest_id} to {output_path}")
            
            return {
                "success": True,
                "manifest_id": manifest_id,
                "format": format,
                "output_path": output_path
            }
        except Exception as e:
            logger.error(f"Failed to export manifest: {str(e)}")
            return {"success": False, "error": f"Failed to export manifest: {str(e)}"}
    
    def import_manifest(self, input_path: str, format: str = None) -> Dict[str, Any]:
        """
        Import a manifest from a file.
        
        Args:
            input_path: Path to the file to import
            format: Import format (json, yaml, auto)
            
        Returns:
            Dictionary with import result
        """
        logger.info(f"Importing manifest from {input_path}")
        
        try:
            # Determine format if not provided
            if not format or format == "auto":
                _, ext = os.path.splitext(input_path)
                if ext.lower() == ".json":
                    format = "json"
                elif ext.lower() in [".yaml", ".yml"]:
                    format = "yaml"
                else:
                    # Try to determine format by content
                    with open(input_path, "r") as f:
                        content = f.read(100)  # Read first 100 characters
                        
                        if content.strip().startswith("{"):
                            format = "json"
                        elif content.strip().startswith("---") or ":" in content:
                            format = "yaml"
                        else:
                            logger.error("Could not determine format")
                            return {"success": False, "error": "Could not determine format"}
            
            # Validate format
            if format not in ["json", "yaml"]:
                logger.error(f"Unsupported format: {format}")
                return {"success": False, "error": f"Unsupported format: {format}"}
            
            # Import based on format
            if format == "json":
                with open(input_path, "r") as f:
                    manifest = json.load(f)
            elif format == "yaml":
                with open(input_path, "r") as f:
                    manifest = yaml.safe_load(f)
            
            # Validate imported manifest
            if not self._validate_manifest(manifest):
                logger.error("Invalid imported manifest")
                return {"success": False, "error": "Invalid imported manifest"}
            
            # Create manifest
            create_result = self.create_manifest(manifest)
            
            if not create_result["success"]:
                logger.error(f"Failed to create manifest: {create_result.get('error', '')}")
                return create_result
            
            # Record import event
            manifest_id = create_result["manifest_id"]
            self._record_history_event(manifest_id, "import", f"Manifest imported from {format} format")
            
            logger.info(f"Imported manifest {manifest_id} from {input_path}")
            
            return {
                "success": True,
                "manifest_id": manifest_id,
                "format": format
            }
        except Exception as e:
            logger.error(f"Failed to import manifest: {str(e)}")
            return {"success": False, "error": f"Failed to import manifest: {str(e)}"}
    
    def validate_manifest(self, manifest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a manifest.
        
        Args:
            manifest: Manifest to validate
            
        Returns:
            Dictionary with validation result
        """
        logger.info("Validating manifest")
        
        # Validate manifest
        if not self._validate_manifest(manifest):
            logger.error("Invalid manifest")
            return {"valid": False, "errors": ["Invalid manifest"]}
        
        logger.info("Manifest is valid")
        
        return {
            "valid": True
        }
    
    def _validate_manifest(self, manifest: Dict[str, Any]) -> bool:
        """
        Validate a manifest.
        
        Args:
            manifest: Manifest to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required_fields = ["name", "description", "manifest_type", "content"]
        for field in required_fields:
            if field not in manifest:
                logger.error(f"Missing required field in manifest: {field}")
                return False
        
        # Check manifest type
        manifest_type = manifest.get("manifest_type")
        valid_types = ["deployment", "service", "configmap", "secret", "ingress", "volume"]
        if manifest_type not in valid_types:
            logger.error(f"Invalid manifest type: {manifest_type}")
            return False
        
        # Check content
        content = manifest.get("content")
        if not isinstance(content, dict):
            logger.error("Manifest content must be a dictionary")
            return False
        
        # Additional validation could be added here
        
        return True
    
    def _update_indexes(self, manifest_id: str, manifest: Dict[str, Any]):
        """
        Update indexes for a manifest.
        
        Args:
            manifest_id: ID of the manifest
            manifest: Manifest definition
        """
        # Update category index
        if "category" in manifest and manifest["category"]:
            category = manifest["category"]
            if category not in self.manifest_categories:
                self.manifest_categories[category] = []
            
            if manifest_id not in self.manifest_categories[category]:
                self.manifest_categories[category].append(manifest_id)
        
        # Update tag index
        if "tags" in manifest and manifest["tags"]:
            for tag in manifest["tags"]:
                if tag not in self.manifest_tags:
                    self.manifest_tags[tag] = []
                
                if manifest_id not in self.manifest_tags[tag]:
                    self.manifest_tags[tag].append(manifest_id)
        
        # Update text index
        indexed_text = self._create_indexed_text(manifest)
        self.manifest_index[manifest_id] = indexed_text
    
    def _remove_from_indexes(self, manifest_id: str, manifest: Dict[str, Any]):
        """
        Remove a manifest from indexes.
        
        Args:
            manifest_id: ID of the manifest
            manifest: Manifest definition
        """
        # Remove from category index
        if "category" in manifest and manifest["category"]:
            category = manifest["category"]
            if category in self.manifest_categories and manifest_id in self.manifest_categories[category]:
                self.manifest_categories[category].remove(manifest_id)
                
                # Remove category if empty
                if not self.manifest_categories[category]:
                    del self.manifest_categories[category]
        
        # Remove from tag index
        if "tags" in manifest and manifest["tags"]:
            for tag in manifest["tags"]:
                if tag in self.manifest_tags and manifest_id in self.manifest_tags[tag]:
                    self.manifest_tags[tag].remove(manifest_id)
                    
                    # Remove tag if empty
                    if not self.manifest_tags[tag]:
                        del self.manifest_tags[tag]
        
        # Remove from text index
        if manifest_id in self.manifest_index:
            del self.manifest_index[manifest_id]
    
    def _create_indexed_text(self, manifest: Dict[str, Any]) -> str:
        """
        Create indexed text for a manifest.
        
        Args:
            manifest: Manifest definition
            
        Returns:
            Indexed text
        """
        # Combine searchable fields
        searchable_fields = ["name", "description", "category", "manifest_type"]
        text_parts = []
        
        for field in searchable_fields:
            if field in manifest and manifest[field]:
                text_parts.append(str(manifest[field]))
        
        # Add tags
        if "tags" in manifest and manifest["tags"]:
            text_parts.extend(manifest["tags"])
        
        # Combine and normalize
        indexed_text = " ".join(text_parts).lower()
        
        return indexed_text
    
    def _build_indexes(self):
        """Build indexes for all manifests."""
        logger.info("Building manifest indexes")
        
        # Clear indexes
        self.manifest_index = {}
        self.manifest_categories = {}
        self.manifest_tags = {}
        
        # Build indexes
        for manifest_id, manifest in self.manifests.items():
            self._update_indexes(manifest_id, manifest)
        
        logger.info(f"Built indexes with {len(self.manifest_categories)} categories and {len(self.manifest_tags)} tags")
    
    def _record_history_event(self, manifest_id: str, event_type: str, description: str):
        """
        Record a history event for a manifest.
        
        Args:
            manifest_id: ID of the manifest
            event_type: Type of event
            description: Description of the event
        """
        # Create event
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description
        }
        
        # Initialize history for this manifest if it doesn't exist
        if manifest_id not in self.manifest_history:
            self.manifest_history[manifest_id] = []
        
        # Add event to history
        self.manifest_history[manifest_id].append(event)
        
        # Trim history if it exceeds max length
        if len(self.manifest_history[manifest_id]) > self.max_history_length:
            self.manifest_history[manifest_id] = self.manifest_history[manifest_id][-self.max_history_length:]
        
        logger.info(f"Recorded {event_type} event for manifest {manifest_id}")
    
    def _load_manifests(self):
        """Load manifests from storage."""
        try:
            # In a real implementation, this would load from a database or file
            # For now, we'll just initialize with empty data
            self.manifests = {}
            self.manifest_history = {}
            logger.info("Loaded manifests")
        except Exception as e:
            logger.error(f"Failed to load manifests: {str(e)}")
    
    def _save_manifests(self):
        """Save manifests to storage."""
        try:
            # In a real implementation, this would save to a database or file
            # For now, we'll just log it
            logger.info(f"Saved {len(self.manifests)} manifests")
        except Exception as e:
            logger.error(f"Failed to save manifests: {str(e)}")
    
    def get_manifest_count(self) -> int:
        """
        Get the number of manifests.
        
        Returns:
            Number of manifests
        """
        return len(self.manifests)
    
    def get_all_manifests(self) -> Dict[str, Any]:
        """
        Get all manifests.
        
        Returns:
            Dictionary with all manifests
        """
        return {
            "success": True,
            "manifests": list(self.manifests.values())
        }
    
    def get_manifests_by_category(self, category: str) -> Dict[str, Any]:
        """
        Get manifests by category.
        
        Args:
            category: Category to filter by
            
        Returns:
            Dictionary with manifests in the category
        """
        if category not in self.manifest_categories:
            return {
                "success": True,
                "manifests": []
            }
        
        manifests = []
        for manifest_id in self.manifest_categories[category]:
            if manifest_id in self.manifests:
                manifests.append(self.manifests[manifest_id])
        
        return {
            "success": True,
            "manifests": manifests
        }
    
    def get_manifests_by_tag(self, tag: str) -> Dict[str, Any]:
        """
        Get manifests by tag.
        
        Args:
            tag: Tag to filter by
            
        Returns:
            Dictionary with manifests with the tag
        """
        if tag not in self.manifest_tags:
            return {
                "success": True,
                "manifests": []
            }
        
        manifests = []
        for manifest_id in self.manifest_tags[tag]:
            if manifest_id in self.manifests:
                manifests.append(self.manifests[manifest_id])
        
        return {
            "success": True,
            "manifests": manifests
        }
