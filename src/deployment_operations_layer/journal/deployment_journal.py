"""
Deployment Journal for the Deployment Operations Layer.

This module provides journaling capabilities for deployment operations
across the Industriverse ecosystem.
"""

import os
import json
import logging
import requests
import time
import uuid
import yaml
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DeploymentJournal:
    """
    Journal for deployment operations.
    
    This class provides methods for recording, retrieving, and analyzing
    deployment operations across the Industriverse ecosystem.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the Deployment Journal.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.journal_id = config.get("journal_id", f"deployment-journal-{uuid.uuid4().hex[:8]}")
        self.storage_type = config.get("storage_type", "file")
        self.storage_path = config.get("storage_path", "/tmp/deployment_journal")
        self.retention_days = config.get("retention_days", 90)
        self.max_entries = config.get("max_entries", 10000)
        self.compression_enabled = config.get("compression_enabled", True)
        
        # Initialize blockchain integration for immutable records
        from ..blockchain.blockchain_integration import BlockchainIntegration
        self.blockchain = BlockchainIntegration(config.get("blockchain", {}))
        
        # Initialize analytics manager for journal metrics
        from ..analytics.analytics_manager import AnalyticsManager
        self.analytics = AnalyticsManager(config.get("analytics", {}))
        
        # Initialize security integration
        from ..security.security_integration import SecurityIntegration
        self.security = SecurityIntegration(config.get("security", {}))
        
        # Create storage directory if it doesn't exist
        if self.storage_type == "file":
            os.makedirs(self.storage_path, exist_ok=True)
        
        logger.info(f"Deployment Journal {self.journal_id} initialized")
    
    def record_entry(self, entry_data: Dict) -> Dict:
        """
        Record a journal entry.
        
        Args:
            entry_data: Entry data
            
        Returns:
            Dict: Recording results
        """
        try:
            # Generate entry ID if not provided
            entry_id = entry_data.get("entry_id")
            if not entry_id:
                entry_id = f"entry-{uuid.uuid4().hex}"
                entry_data["entry_id"] = entry_id
            
            # Add timestamp if not provided
            if "timestamp" not in entry_data:
                entry_data["timestamp"] = datetime.now().isoformat()
            
            # Add journal ID
            entry_data["journal_id"] = self.journal_id
            
            # Add entry type if not provided
            if "type" not in entry_data:
                entry_data["type"] = "generic"
            
            # Add security context if available
            security_context = self.security.get_current_context()
            if security_context:
                entry_data["security_context"] = security_context
            
            # Save entry to storage
            self._save_entry(entry_id, entry_data)
            
            # Record entry in blockchain if enabled
            blockchain_result = None
            if self.config.get("blockchain_enabled", False):
                blockchain_result = self.blockchain.record_data({
                    "type": "journal_entry",
                    "entry_id": entry_id,
                    "timestamp": entry_data["timestamp"],
                    "hash": self._calculate_entry_hash(entry_data)
                })
            
            # Track journal metrics
            self._track_journal_metrics("record", entry_data)
            
            return {
                "status": "success",
                "message": "Journal entry recorded successfully",
                "entry_id": entry_id,
                "timestamp": entry_data["timestamp"],
                "blockchain_result": blockchain_result
            }
        except Exception as e:
            logger.error(f"Error recording journal entry: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_entry(self, entry_id: str) -> Optional[Dict]:
        """
        Get a journal entry by ID.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Optional[Dict]: Entry data or None if not found
        """
        try:
            # Load entry from storage
            entry_data = self._load_entry(entry_id)
            
            # Track journal metrics
            if entry_data:
                self._track_journal_metrics("get", {"entry_id": entry_id})
            
            return entry_data
        except Exception as e:
            logger.error(f"Error getting journal entry: {e}")
            return None
    
    def search_entries(self, filters: Dict = None, sort_by: str = "timestamp", sort_order: str = "desc", limit: int = 100, offset: int = 0) -> Dict:
        """
        Search journal entries.
        
        Args:
            filters: Filter criteria
            sort_by: Field to sort by
            sort_order: Sort order (asc or desc)
            limit: Maximum number of entries to return
            offset: Offset for pagination
            
        Returns:
            Dict: Search results
        """
        try:
            # Initialize filters
            if not filters:
                filters = {}
            
            # Get all entry IDs
            entry_ids = self._get_all_entry_ids()
            
            # Load entries
            entries = []
            for entry_id in entry_ids:
                entry_data = self._load_entry(entry_id)
                if entry_data:
                    # Apply filters
                    match = True
                    for key, value in filters.items():
                        if key not in entry_data or entry_data[key] != value:
                            match = False
                            break
                    
                    if match:
                        entries.append(entry_data)
            
            # Sort entries
            if sort_by in ["timestamp", "type", "entry_id"]:
                reverse = sort_order.lower() == "desc"
                entries.sort(key=lambda x: x.get(sort_by, ""), reverse=reverse)
            
            # Apply pagination
            total_entries = len(entries)
            entries = entries[offset:offset + limit]
            
            # Track journal metrics
            self._track_journal_metrics("search", {
                "filters": filters,
                "sort_by": sort_by,
                "sort_order": sort_order,
                "limit": limit,
                "offset": offset,
                "total_entries": total_entries,
                "returned_entries": len(entries)
            })
            
            return {
                "status": "success",
                "message": "Journal entries retrieved successfully",
                "total_entries": total_entries,
                "returned_entries": len(entries),
                "entries": entries
            }
        except Exception as e:
            logger.error(f"Error searching journal entries: {e}")
            return {"status": "error", "message": str(e)}
    
    def delete_entry(self, entry_id: str) -> Dict:
        """
        Delete a journal entry.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Dict: Deletion results
        """
        try:
            # Check if entry exists
            entry_data = self._load_entry(entry_id)
            if not entry_data:
                return {
                    "status": "error",
                    "message": f"Journal entry not found: {entry_id}"
                }
            
            # Delete entry from storage
            self._delete_entry(entry_id)
            
            # Track journal metrics
            self._track_journal_metrics("delete", {"entry_id": entry_id})
            
            return {
                "status": "success",
                "message": "Journal entry deleted successfully",
                "entry_id": entry_id
            }
        except Exception as e:
            logger.error(f"Error deleting journal entry: {e}")
            return {"status": "error", "message": str(e)}
    
    def purge_old_entries(self, days: int = None) -> Dict:
        """
        Purge old journal entries.
        
        Args:
            days: Number of days to retain entries
            
        Returns:
            Dict: Purge results
        """
        try:
            # Get retention days
            retention_days = days if days is not None else self.retention_days
            
            # Calculate cutoff timestamp
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_timestamp = cutoff_date.isoformat()
            
            # Get all entry IDs
            entry_ids = self._get_all_entry_ids()
            
            # Initialize counters
            total_entries = len(entry_ids)
            deleted_entries = 0
            
            # Delete old entries
            for entry_id in entry_ids:
                entry_data = self._load_entry(entry_id)
                if entry_data and entry_data.get("timestamp", "") < cutoff_timestamp:
                    self._delete_entry(entry_id)
                    deleted_entries += 1
            
            # Track journal metrics
            self._track_journal_metrics("purge", {
                "retention_days": retention_days,
                "cutoff_timestamp": cutoff_timestamp,
                "total_entries": total_entries,
                "deleted_entries": deleted_entries
            })
            
            return {
                "status": "success",
                "message": "Old journal entries purged successfully",
                "retention_days": retention_days,
                "cutoff_timestamp": cutoff_timestamp,
                "total_entries": total_entries,
                "deleted_entries": deleted_entries
            }
        except Exception as e:
            logger.error(f"Error purging old journal entries: {e}")
            return {"status": "error", "message": str(e)}
    
    def export_entries(self, filters: Dict = None, format: str = "json") -> Dict:
        """
        Export journal entries.
        
        Args:
            filters: Filter criteria
            format: Export format
            
        Returns:
            Dict: Export results
        """
        try:
            # Search entries
            search_result = self.search_entries(filters, limit=self.max_entries)
            
            if search_result.get("status") != "success":
                return search_result
            
            entries = search_result.get("entries", [])
            
            # Export based on format
            if format == "json":
                # Export as JSON
                export_data = json.dumps(entries, indent=2)
                export_mime_type = "application/json"
            elif format == "yaml":
                # Export as YAML
                export_data = yaml.dump(entries)
                export_mime_type = "application/yaml"
            elif format == "csv":
                # Export as CSV
                import csv
                import io
                
                output = io.StringIO()
                if entries:
                    # Get all possible fields
                    fields = set()
                    for entry in entries:
                        fields.update(entry.keys())
                    
                    # Sort fields for consistent output
                    fields = sorted(fields)
                    
                    # Write CSV
                    writer = csv.DictWriter(output, fieldnames=fields)
                    writer.writeheader()
                    for entry in entries:
                        writer.writerow(entry)
                
                export_data = output.getvalue()
                export_mime_type = "text/csv"
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported export format: {format}"
                }
            
            # Generate export file
            export_id = uuid.uuid4().hex
            export_file = os.path.join(self.storage_path, f"export-{export_id}.{format}")
            with open(export_file, "w") as f:
                f.write(export_data)
            
            # Track journal metrics
            self._track_journal_metrics("export", {
                "filters": filters,
                "format": format,
                "entries": len(entries),
                "export_id": export_id,
                "export_file": export_file
            })
            
            return {
                "status": "success",
                "message": "Journal entries exported successfully",
                "entries": len(entries),
                "format": format,
                "mime_type": export_mime_type,
                "export_id": export_id,
                "export_file": export_file,
                "export_data": export_data
            }
        except Exception as e:
            logger.error(f"Error exporting journal entries: {e}")
            return {"status": "error", "message": str(e)}
    
    def analyze_entries(self, filters: Dict = None, metrics: List[str] = None) -> Dict:
        """
        Analyze journal entries.
        
        Args:
            filters: Filter criteria
            metrics: Metrics to calculate
            
        Returns:
            Dict: Analysis results
        """
        try:
            # Initialize metrics
            if not metrics:
                metrics = ["count", "types", "timeline"]
            
            # Search entries
            search_result = self.search_entries(filters, limit=self.max_entries)
            
            if search_result.get("status") != "success":
                return search_result
            
            entries = search_result.get("entries", [])
            
            # Initialize results
            results = {
                "total_entries": len(entries)
            }
            
            # Calculate metrics
            if "count" in metrics:
                results["count"] = len(entries)
            
            if "types" in metrics:
                # Count entries by type
                types = {}
                for entry in entries:
                    entry_type = entry.get("type", "generic")
                    types[entry_type] = types.get(entry_type, 0) + 1
                
                results["types"] = types
            
            if "timeline" in metrics:
                # Group entries by day
                timeline = {}
                for entry in entries:
                    timestamp = entry.get("timestamp", "")
                    if timestamp:
                        # Extract date part
                        date_part = timestamp.split("T")[0]
                        timeline[date_part] = timeline.get(date_part, 0) + 1
                
                # Sort timeline
                timeline = {k: timeline[k] for k in sorted(timeline.keys())}
                
                results["timeline"] = timeline
            
            if "status" in metrics:
                # Count entries by status
                status_counts = {}
                for entry in entries:
                    status = entry.get("status", "unknown")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                results["status"] = status_counts
            
            if "users" in metrics:
                # Count entries by user
                user_counts = {}
                for entry in entries:
                    user = entry.get("user", "unknown")
                    user_counts[user] = user_counts.get(user, 0) + 1
                
                results["users"] = user_counts
            
            if "components" in metrics:
                # Count entries by component
                component_counts = {}
                for entry in entries:
                    component = entry.get("component", "unknown")
                    component_counts[component] = component_counts.get(component, 0) + 1
                
                results["components"] = component_counts
            
            # Track journal metrics
            self._track_journal_metrics("analyze", {
                "filters": filters,
                "metrics": metrics,
                "entries": len(entries)
            })
            
            return {
                "status": "success",
                "message": "Journal entries analyzed successfully",
                "entries": len(entries),
                "metrics": metrics,
                "results": results
            }
        except Exception as e:
            logger.error(f"Error analyzing journal entries: {e}")
            return {"status": "error", "message": str(e)}
    
    def verify_entry(self, entry_id: str) -> Dict:
        """
        Verify a journal entry against blockchain record.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Dict: Verification results
        """
        try:
            # Check if blockchain integration is enabled
            if not self.config.get("blockchain_enabled", False):
                return {
                    "status": "error",
                    "message": "Blockchain integration is not enabled"
                }
            
            # Load entry from storage
            entry_data = self._load_entry(entry_id)
            if not entry_data:
                return {
                    "status": "error",
                    "message": f"Journal entry not found: {entry_id}"
                }
            
            # Calculate entry hash
            entry_hash = self._calculate_entry_hash(entry_data)
            
            # Verify entry in blockchain
            verification_result = self.blockchain.verify_data({
                "type": "journal_entry",
                "entry_id": entry_id,
                "hash": entry_hash
            })
            
            # Track journal metrics
            self._track_journal_metrics("verify", {
                "entry_id": entry_id,
                "verification_result": verification_result
            })
            
            if verification_result.get("status") == "success":
                return {
                    "status": "success",
                    "message": "Journal entry verified successfully",
                    "entry_id": entry_id,
                    "verification_result": verification_result
                }
            else:
                return {
                    "status": "error",
                    "message": "Journal entry verification failed",
                    "entry_id": entry_id,
                    "verification_result": verification_result
                }
        except Exception as e:
            logger.error(f"Error verifying journal entry: {e}")
            return {"status": "error", "message": str(e)}
    
    def _save_entry(self, entry_id: str, entry_data: Dict) -> None:
        """
        Save a journal entry to storage.
        
        Args:
            entry_id: Entry ID
            entry_data: Entry data
        """
        try:
            if self.storage_type == "file":
                # Save entry to file
                entry_file = os.path.join(self.storage_path, f"{entry_id}.json")
                
                # Compress if enabled
                if self.compression_enabled:
                    import gzip
                    with gzip.open(f"{entry_file}.gz", "wt") as f:
                        json.dump(entry_data, f)
                else:
                    with open(entry_file, "w") as f:
                        json.dump(entry_data, f)
        except Exception as e:
            logger.error(f"Error saving journal entry: {e}")
            raise
    
    def _load_entry(self, entry_id: str) -> Optional[Dict]:
        """
        Load a journal entry from storage.
        
        Args:
            entry_id: Entry ID
            
        Returns:
            Optional[Dict]: Entry data or None if not found
        """
        try:
            if self.storage_type == "file":
                # Check for compressed file first
                entry_file_gz = os.path.join(self.storage_path, f"{entry_id}.json.gz")
                if os.path.exists(entry_file_gz):
                    # Load from compressed file
                    import gzip
                    with gzip.open(entry_file_gz, "rt") as f:
                        return json.load(f)
                
                # Check for uncompressed file
                entry_file = os.path.join(self.storage_path, f"{entry_id}.json")
                if os.path.exists(entry_file):
                    # Load from uncompressed file
                    with open(entry_file, "r") as f:
                        return json.load(f)
            
            return None
        except Exception as e:
            logger.error(f"Error loading journal entry: {e}")
            return None
    
    def _delete_entry(self, entry_id: str) -> None:
        """
        Delete a journal entry from storage.
        
        Args:
            entry_id: Entry ID
        """
        try:
            if self.storage_type == "file":
                # Check for compressed file
                entry_file_gz = os.path.join(self.storage_path, f"{entry_id}.json.gz")
                if os.path.exists(entry_file_gz):
                    os.remove(entry_file_gz)
                
                # Check for uncompressed file
                entry_file = os.path.join(self.storage_path, f"{entry_id}.json")
                if os.path.exists(entry_file):
                    os.remove(entry_file)
        except Exception as e:
            logger.error(f"Error deleting journal entry: {e}")
            raise
    
    def _get_all_entry_ids(self) -> List[str]:
        """
        Get all entry IDs.
        
        Returns:
            List[str]: List of entry IDs
        """
        try:
            entry_ids = []
            
            if self.storage_type == "file":
                # Get all files in storage directory
                for file in os.listdir(self.storage_path):
                    # Check if file is a journal entry
                    if file.endswith(".json") or file.endswith(".json.gz"):
                        # Extract entry ID
                        entry_id = file.replace(".json", "").replace(".gz", "")
                        entry_ids.append(entry_id)
            
            return entry_ids
        except Exception as e:
            logger.error(f"Error getting all entry IDs: {e}")
            return []
    
    def _calculate_entry_hash(self, entry_data: Dict) -> str:
        """
        Calculate hash for a journal entry.
        
        Args:
            entry_data: Entry data
            
        Returns:
            str: Entry hash
        """
        try:
            # Convert entry data to JSON string
            entry_json = json.dumps(entry_data, sort_keys=True)
            
            # Calculate SHA-256 hash
            import hashlib
            entry_hash = hashlib.sha256(entry_json.encode()).hexdigest()
            
            return entry_hash
        except Exception as e:
            logger.error(f"Error calculating entry hash: {e}")
            raise
    
    def _track_journal_metrics(self, operation: str, data: Dict) -> None:
        """
        Track journal metrics.
        
        Args:
            operation: Operation name
            data: Operation data
        """
        try:
            # Prepare metrics
            metrics = {
                "type": f"journal_{operation}",
                "timestamp": datetime.now().isoformat(),
                "journal_id": self.journal_id
            }
            
            # Add operation data
            metrics.update(data)
            
            # Track metrics
            self.analytics.track_metrics(metrics)
        except Exception as e:
            logger.error(f"Error tracking journal metrics: {e}")
    
    def configure(self, config: Dict) -> Dict:
        """
        Configure the Deployment Journal.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Dict: Configuration results
        """
        try:
            # Update local configuration
            if "storage_type" in config:
                self.storage_type = config["storage_type"]
            
            if "storage_path" in config:
                self.storage_path = config["storage_path"]
                
                # Create storage directory if it doesn't exist
                if self.storage_type == "file":
                    os.makedirs(self.storage_path, exist_ok=True)
            
            if "retention_days" in config:
                self.retention_days = config["retention_days"]
            
            if "max_entries" in config:
                self.max_entries = config["max_entries"]
            
            if "compression_enabled" in config:
                self.compression_enabled = config["compression_enabled"]
            
            # Configure blockchain integration
            blockchain_result = None
            if "blockchain" in config:
                blockchain_result = self.blockchain.configure(config["blockchain"])
            
            # Configure analytics manager
            analytics_result = None
            if "analytics" in config:
                analytics_result = self.analytics.configure(config["analytics"])
            
            # Configure security integration
            security_result = None
            if "security" in config:
                security_result = self.security.configure(config["security"])
            
            return {
                "status": "success",
                "message": "Deployment Journal configured successfully",
                "journal_id": self.journal_id,
                "blockchain_result": blockchain_result,
                "analytics_result": analytics_result,
                "security_result": security_result
            }
        except Exception as e:
            logger.error(f"Error configuring Deployment Journal: {e}")
            return {"status": "error", "message": str(e)}
