"""
Storage Management System for Industriverse Data Layer

This module implements a protocol-native storage management system that handles
data persistence, retrieval, and lifecycle management for industrial datasets.
"""

import json
import logging
import os
import time
import shutil
import hashlib
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
import sqlite3
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class StorageManagementSystem:
    """
    Protocol-native storage management system for industrial datasets.
    
    This system provides data persistence, retrieval, and lifecycle management
    capabilities for industrial datasets, with full MCP/A2A protocol integration.
    """
    
    def __init__(
        self,
        system_id: str = "storage-management-system",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the storage management system.
        
        Args:
            system_id: Unique identifier for this system
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for storage files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["manufacturing", "process_industry", "energy"],
            "intelligence_type": "data_storage",
            "storage_modes": ["file", "database", "blob"],
            "default_mode": "file",
            "compression": {
                "enable_compression": True,
                "compression_method": "gzip",  # gzip, zip, none
                "compression_level": 6
            },
            "encryption": {
                "enable_encryption": False,
                "encryption_method": "aes256",
                "key_rotation_days": 90
            },
            "retention": {
                "enable_retention_policy": True,
                "default_retention_days": 365,
                "archive_after_days": 180
            },
            "versioning": {
                "enable_versioning": True,
                "max_versions": 5,
                "version_naming": "timestamp"  # timestamp, sequential, semantic
            },
            "database": {
                "type": "sqlite",  # sqlite, postgres, mysql
                "connection_string": "",
                "pool_size": 5,
                "timeout": 30
            }
        }
        
        # Merge with provided config
        self.config = default_config.copy()
        if config:
            self.config.update(config)
        
        self.system_id = system_id
        self.secrets_manager = secrets_manager
        
        # Set up base directory
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.join(os.getcwd(), "data_storage")
        
        # Set up subdirectories
        self.raw_dir = os.path.join(self.base_dir, "raw")
        self.processed_dir = os.path.join(self.base_dir, "processed")
        self.archive_dir = os.path.join(self.base_dir, "archive")
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        self.temp_dir = os.path.join(self.base_dir, "temp")
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.archive_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Set up agent manifest
        self.manifest_path = manifest_path
        if not self.manifest_path:
            self.manifest_path = os.path.join(self.base_dir, "agent_manifest.yaml")
        
        # Initialize protocol integration
        self._initialize_protocol_integration()
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"Initialized storage management system: {self.system_id}")
    
    def _initialize_protocol_integration(self):
        """Initialize protocol integration for MCP/A2A compatibility."""
        try:
            # Import protocol modules
            import sys
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "protocols"))
            
            from agent_core import AgentCore
            from protocol_translator import ProtocolTranslator
            from mesh_boot_lifecycle import MeshBootLifecycle
            
            # Initialize agent core
            self.agent_core = AgentCore(
                agent_id=self.system_id,
                agent_type="storage_management_system",
                manifest_path=self.manifest_path,
                intelligence_type=self.config["intelligence_type"],
                industry_tags=self.config["industry_tags"]
            )
            
            # Initialize protocol translator
            self.protocol_translator = ProtocolTranslator(
                agent_id=self.system_id,
                supported_protocols=["mcp", "a2a"]
            )
            
            # Initialize mesh boot lifecycle
            self.mesh_lifecycle = MeshBootLifecycle(
                agent_id=self.system_id,
                agent_core=self.agent_core
            )
            
            # Register with mesh
            self.mesh_lifecycle.register()
            
            # Initialize event handlers
            self._initialize_event_handlers()
            
            logger.info(f"Protocol integration initialized for {self.system_id}")
        except Exception as e:
            logger.error(f"Failed to initialize protocol integration: {str(e)}")
            # Continue with limited functionality
            self.agent_core = None
            self.protocol_translator = None
            self.mesh_lifecycle = None
    
    def _initialize_event_handlers(self):
        """Initialize event handlers for protocol events."""
        if not self.agent_core:
            return
        
        # Register event handlers
        self.agent_core.register_handler("observe", self._handle_observe_event)
        self.agent_core.register_handler("simulate", self._handle_simulate_event)
        self.agent_core.register_handler("recommend", self._handle_recommend_event)
        self.agent_core.register_handler("act", self._handle_act_event)
    
    def _handle_observe_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle observe events from other agents.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        try:
            if "dataset_processing_completed" in event.get("status", ""):
                # New dataset processed, store it
                dataset_name = event.get("dataset", "")
                output_path = event.get("output_path", "")
                
                if dataset_name and output_path and os.path.exists(output_path):
                    logger.info(f"Observed new dataset processing completion: {dataset_name}")
                    # Schedule storage
                    return {
                        "status": "storage_scheduled",
                        "dataset": dataset_name,
                        "system_id": self.system_id
                    }
            
            return {"status": "observed", "system_id": self.system_id}
        except Exception as e:
            logger.error(f"Error handling observe event: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _handle_simulate_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle simulate events from other agents.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        try:
            if "storage_requirements" in event:
                # Simulate storage requirements
                dataset_name = event.get("dataset", "")
                dataset_size = event.get("dataset_size", 0)
                retention_days = event.get("retention_days", self.config["retention"]["default_retention_days"])
                
                if dataset_name:
                    logger.info(f"Simulating storage requirements for {dataset_name}")
                    # Calculate storage requirements
                    compression_ratio = 0.5 if self.config["compression"]["enable_compression"] else 1.0
                    versioning_factor = self.config["versioning"]["max_versions"] if self.config["versioning"]["enable_versioning"] else 1
                    
                    total_storage = dataset_size * compression_ratio * versioning_factor
                    
                    # Return simulated metrics
                    return {
                        "status": "simulation_completed",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "simulated_metrics": {
                            "storage_required": f"{total_storage:.2f} bytes",
                            "retention_period": f"{retention_days} days",
                            "versions_kept": self.config["versioning"]["max_versions"] if self.config["versioning"]["enable_versioning"] else 1,
                            "compression_enabled": self.config["compression"]["enable_compression"],
                            "encryption_enabled": self.config["encryption"]["enable_encryption"]
                        }
                    }
            
            return {"status": "simulated", "system_id": self.system_id}
        except Exception as e:
            logger.error(f"Error handling simulate event: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _handle_recommend_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle recommend events from other agents.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        try:
            if "dataset" in event:
                # Recommend storage strategy
                dataset_name = event.get("dataset", "")
                dataset_type = event.get("dataset_type", "")
                
                if dataset_name:
                    logger.info(f"Recommending storage strategy for {dataset_name}")
                    # Return recommended strategy
                    return {
                        "status": "recommendation_provided",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "recommended_strategy": self._get_storage_strategy_for_dataset_type(dataset_type)
                    }
            
            return {"status": "recommendation_provided", "system_id": self.system_id}
        except Exception as e:
            logger.error(f"Error handling recommend event: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _handle_act_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle act events from other agents.
        
        Args:
            event: Event data
            
        Returns:
            Response data
        """
        try:
            if "store_dataset" in event.get("action", ""):
                # Store dataset
                dataset_name = event.get("dataset", "")
                dataset_path = event.get("dataset_path", "")
                dataset_type = event.get("dataset_type", "")
                metadata = event.get("metadata", {})
                
                if dataset_path and os.path.exists(dataset_path):
                    logger.info(f"Storing dataset: {dataset_name}")
                    # Store dataset
                    result = self.store_dataset(
                        dataset_path=dataset_path,
                        dataset_name=dataset_name,
                        dataset_type=dataset_type,
                        metadata=metadata
                    )
                    
                    return {
                        "status": "storage_completed" if result["success"] else "storage_failed",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "result": result
                    }
            elif "retrieve_dataset" in event.get("action", ""):
                # Retrieve dataset
                dataset_name = event.get("dataset", "")
                version = event.get("version", "latest")
                
                if dataset_name:
                    logger.info(f"Retrieving dataset: {dataset_name}, version: {version}")
                    # Retrieve dataset
                    result = self.retrieve_dataset(
                        dataset_name=dataset_name,
                        version=version
                    )
                    
                    return {
                        "status": "retrieval_completed" if result["success"] else "retrieval_failed",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "result": result
                    }
            elif "delete_dataset" in event.get("action", ""):
                # Delete dataset
                dataset_name = event.get("dataset", "")
                version = event.get("version", "all")
                
                if dataset_name:
                    logger.info(f"Deleting dataset: {dataset_name}, version: {version}")
                    # Delete dataset
                    result = self.delete_dataset(
                        dataset_name=dataset_name,
                        version=version
                    )
                    
                    return {
                        "status": "deletion_completed" if result["success"] else "deletion_failed",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "result": result
                    }
            
            return {"status": "action_completed", "system_id": self.system_id}
        except Exception as e:
            logger.error(f"Error handling act event: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _initialize_database(self):
        """Initialize the metadata database."""
        try:
            # Create database file
            db_path = os.path.join(self.metadata_dir, "storage_metadata.db")
            
            # Connect to database
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            
            # Create tables if they don't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    size INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    retention_days INTEGER NOT NULL,
                    is_archived INTEGER NOT NULL DEFAULT 0,
                    UNIQUE(name)
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS dataset_versions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    version TEXT NOT NULL,
                    path TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    size INTEGER NOT NULL,
                    hash TEXT NOT NULL,
                    is_compressed INTEGER NOT NULL DEFAULT 0,
                    is_encrypted INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id),
                    UNIQUE(dataset_id, version)
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS dataset_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id),
                    UNIQUE(dataset_id, key)
                )
            ''')
            
            self.conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            self.conn = None
            self.cursor = None
    
    def emit_event(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Emit protocol event.
        
        Args:
            event_type: Type of event (observe, simulate, recommend, act)
            payload: Event payload
            
        Returns:
            Success status
        """
        if not self.agent_core:
            logger.warning("Protocol integration not initialized, event not emitted")
            return False
        
        try:
            # Add system ID to payload
            payload["system_id"] = self.system_id
            
            # Add timestamp
            payload["timestamp"] = datetime.now().isoformat()
            
            # Emit event
            self.agent_core.emit_event(event_type, payload)
            return True
        except Exception as e:
            logger.error(f"Failed to emit event: {str(e)}")
            return False
    
    def _get_storage_strategy_for_dataset_type(self, dataset_type: str) -> Dict[str, Any]:
        """
        Get storage strategy for a specific dataset type.
        
        Args:
            dataset_type: Type of dataset
            
        Returns:
            Storage strategy configuration
        """
        # Default strategy
        default_strategy = {
            "storage_mode": self.config["default_mode"],
            "compression": self.config["compression"]["enable_compression"],
            "compression_method": self.config["compression"]["compression_method"],
            "encryption": self.config["encryption"]["enable_encryption"],
            "versioning": self.config["versioning"]["enable_versioning"],
            "retention_days": self.config["retention"]["default_retention_days"]
        }
        
        # Customize based on dataset type
        if dataset_type == "timeseries":
            return {
                **default_strategy,
                "storage_mode": "database",
                "compression": True,
                "compression_method": "gzip",
                "index_columns": ["timestamp"]
            }
        elif dataset_type == "tabular":
            return {
                **default_strategy,
                "storage_mode": "file",
                "compression": True,
                "compression_method": "gzip"
            }
        elif dataset_type == "image":
            return {
                **default_strategy,
                "storage_mode": "file",
                "compression": False,
                "versioning": True
            }
        else:
            return default_strategy
    
    def store_dataset(
        self,
        dataset_path: str,
        dataset_name: str,
        dataset_type: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        storage_strategy: Optional[Dict[str, Any]] = None,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Store a dataset.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            metadata: Additional metadata
            storage_strategy: Storage strategy configuration
            emit_events: Whether to emit protocol events
            
        Returns:
            Storage result
        """
        try:
            # Start storage
            start_time = time.time()
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_storage_started",
                        "dataset": dataset_name,
                        "dataset_path": dataset_path
                    }
                )
            
            # Determine dataset type if not provided
            if not dataset_type:
                dataset_type = self._determine_dataset_type(dataset_path)
            
            # Get storage strategy
            if not storage_strategy:
                storage_strategy = self._get_storage_strategy_for_dataset_type(dataset_type)
            
            # Calculate file hash
            file_hash = self._calculate_file_hash(dataset_path)
            
            # Get file size
            file_size = os.path.getsize(dataset_path)
            
            # Generate version
            version = self._generate_version(dataset_name, storage_strategy)
            
            # Store dataset
            storage_mode = storage_strategy.get("storage_mode", self.config["default_mode"])
            
            if storage_mode == "file":
                result = self._store_file_dataset(
                    dataset_path=dataset_path,
                    dataset_name=dataset_name,
                    version=version,
                    storage_strategy=storage_strategy
                )
            elif storage_mode == "database":
                result = self._store_database_dataset(
                    dataset_path=dataset_path,
                    dataset_name=dataset_name,
                    version=version,
                    storage_strategy=storage_strategy
                )
            else:
                raise ValueError(f"Unsupported storage mode: {storage_mode}")
            
            # Update database
            self._update_dataset_metadata(
                dataset_name=dataset_name,
                dataset_type=dataset_type,
                version=version,
                file_hash=file_hash,
                file_size=file_size,
                storage_path=result["storage_path"],
                is_compressed=result.get("is_compressed", False),
                is_encrypted=result.get("is_encrypted", False),
                metadata=metadata
            )
            
            # Apply retention policy
            self._apply_retention_policy(dataset_name, storage_strategy)
            
            # Complete storage
            end_time = time.time()
            duration = end_time - start_time
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_storage_completed",
                        "dataset": dataset_name,
                        "storage_time": duration,
                        "storage_path": result["storage_path"],
                        "version": version
                    }
                )
            
            logger.info(f"Completed dataset storage for {dataset_name} in {duration:.2f}s")
            return {
                "success": True,
                "dataset": dataset_name,
                "storage_path": result["storage_path"],
                "version": version,
                "storage_time": duration,
                "file_size": file_size,
                "file_hash": file_hash
            }
        except Exception as e:
            logger.error(f"Failed to store dataset: {str(e)}")
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_storage_failed",
                        "dataset": dataset_name,
                        "error": str(e)
                    }
                )
            
            return {
                "success": False,
                "dataset": dataset_name,
                "error": str(e)
            }
    
    def _determine_dataset_type(self, dataset_path: str) -> str:
        """
        Determine the type of dataset.
        
        Args:
            dataset_path: Path to the dataset file
            
        Returns:
            Dataset type (timeseries, tabular, image, etc.)
        """
        # Check file extension
        if dataset_path.endswith(('.csv', '.xlsx', '.xls')):
            # Load a small sample to check for datetime columns
            if dataset_path.endswith('.csv'):
                sample_df = pd.read_csv(dataset_path, nrows=100)
            else:
                sample_df = pd.read_excel(dataset_path, nrows=100)
            
            # Check for datetime columns
            datetime_cols = []
            for col in sample_df.columns:
                try:
                    pd.to_datetime(sample_df[col])
                    datetime_cols.append(col)
                except (ValueError, TypeError, KeyError):
                    # ValueError: invalid date format
                    # TypeError: incompatible type for datetime conversion
                    # KeyError: column doesn't exist
                    pass
            
            if datetime_cols:
                return "timeseries"
            else:
                return "tabular"
        elif dataset_path.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
            return "image"
        elif dataset_path.endswith('.json'):
            # Check if it's an image dataset index
            try:
                with open(dataset_path, 'r') as f:
                    data = json.load(f)
                
                if isinstance(data, list) and len(data) > 0 and "image_path" in data[0]:
                    return "image"
                else:
                    return "json"
            except (json.JSONDecodeError, FileNotFoundError, PermissionError, KeyError, TypeError):
                # JSONDecodeError: invalid JSON format
                # FileNotFoundError: file doesn't exist
                # PermissionError: can't read file
                # KeyError: unexpected data structure
                # TypeError: data is not indexable
                return "json"
        else:
            return "unknown"
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """
        Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File hash
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            # Read and update hash in chunks
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _generate_version(self, dataset_name: str, storage_strategy: Dict[str, Any]) -> str:
        """
        Generate a version string for a dataset.
        
        Args:
            dataset_name: Name of the dataset
            storage_strategy: Storage strategy configuration
            
        Returns:
            Version string
        """
        version_naming = storage_strategy.get("version_naming", self.config["versioning"]["version_naming"])
        
        if version_naming == "timestamp":
            # Use timestamp
            return datetime.now().strftime("%Y%m%d%H%M%S")
        elif version_naming == "sequential":
            # Use sequential numbering
            try:
                # Get latest version
                self.cursor.execute(
                    "SELECT MAX(CAST(version AS INTEGER)) FROM dataset_versions "
                    "JOIN datasets ON dataset_versions.dataset_id = datasets.id "
                    "WHERE datasets.name = ?",
                    (dataset_name,)
                )
                result = self.cursor.fetchone()
                
                if result and result[0] is not None:
                    return str(int(result[0]) + 1)
                else:
                    return "1"
            except (sqlite3.Error, TypeError, ValueError, IndexError):
                # sqlite3.Error: database error
                # TypeError: result[0] is None
                # ValueError: can't cast to int
                # IndexError: result is empty
                # Fallback to timestamp
                return datetime.now().strftime("%Y%m%d%H%M%S")
        elif version_naming == "semantic":
            # Use semantic versioning
            try:
                # Get latest version
                self.cursor.execute(
                    "SELECT version FROM dataset_versions "
                    "JOIN datasets ON dataset_versions.dataset_id = datasets.id "
                    "WHERE datasets.name = ? "
                    "ORDER BY id DESC LIMIT 1",
                    (dataset_name,)
                )
                result = self.cursor.fetchone()
                
                if result and result[0]:
                    # Parse semantic version
                    parts = result[0].split('.')
                    if len(parts) == 3:
                        major, minor, patch = map(int, parts)
                        # Increment patch version
                        patch += 1
                        return f"{major}.{minor}.{patch}"
                
                # Default to 0.1.0
                return "0.1.0"
            except (sqlite3.Error, IndexError, TypeError):
                # sqlite3.Error: database error
                # IndexError: result is empty
                # TypeError: invalid type conversion
                # Fallback to 0.1.0
                return "0.1.0"
        else:
            # Fallback to timestamp
            return datetime.now().strftime("%Y%m%d%H%M%S")
    
    def _store_file_dataset(
        self,
        dataset_path: str,
        dataset_name: str,
        version: str,
        storage_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store a dataset as a file.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_name: Name of the dataset
            version: Version string
            storage_strategy: Storage strategy configuration
            
        Returns:
            Storage result
        """
        # Create storage directory
        storage_dir = os.path.join(self.processed_dir, dataset_name)
        os.makedirs(storage_dir, exist_ok=True)
        
        # Determine file extension
        _, file_ext = os.path.splitext(dataset_path)
        
        # Generate storage path
        storage_path = os.path.join(storage_dir, f"{dataset_name}_v{version}{file_ext}")
        
        # Check if compression is enabled
        is_compressed = storage_strategy.get("compression", self.config["compression"]["enable_compression"])
        compression_method = storage_strategy.get("compression_method", self.config["compression"]["compression_method"])
        
        if is_compressed and compression_method == "gzip" and not file_ext.endswith('.gz'):
            storage_path += '.gz'
            
            # Compress file
            import gzip
            with open(dataset_path, 'rb') as f_in:
                with gzip.open(storage_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        elif is_compressed and compression_method == "zip" and not file_ext.endswith('.zip'):
            storage_path += '.zip'
            
            # Compress file
            import zipfile
            with zipfile.ZipFile(storage_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(dataset_path, os.path.basename(dataset_path))
        else:
            # Just copy the file
            shutil.copy2(dataset_path, storage_path)
        
        # Check if encryption is enabled
        is_encrypted = storage_strategy.get("encryption", self.config["encryption"]["enable_encryption"])
        
        if is_encrypted:
            # Encrypt file (placeholder for actual encryption)
            logger.warning("File encryption not implemented yet")
        
        return {
            "storage_path": storage_path,
            "is_compressed": is_compressed,
            "is_encrypted": is_encrypted
        }
    
    def _store_database_dataset(
        self,
        dataset_path: str,
        dataset_name: str,
        version: str,
        storage_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Store a dataset in a database.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_name: Name of the dataset
            version: Version string
            storage_strategy: Storage strategy configuration
            
        Returns:
            Storage result
        """
        # Create storage directory
        storage_dir = os.path.join(self.processed_dir, dataset_name)
        os.makedirs(storage_dir, exist_ok=True)
        
        # Generate storage path (SQLite database)
        storage_path = os.path.join(storage_dir, f"{dataset_name}_v{version}.db")
        
        # Load dataset
        if dataset_path.endswith('.csv'):
            df = pd.read_csv(dataset_path)
        elif dataset_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(dataset_path)
        else:
            raise ValueError(f"Unsupported file format for database storage: {dataset_path}")
        
        # Connect to SQLite database
        conn = sqlite3.connect(storage_path)
        
        # Store dataset
        table_name = f"{dataset_name}_v{version}"
        df.to_sql(table_name, conn, index=False, if_exists='replace')
        
        # Create index if needed
        index_columns = storage_strategy.get("index_columns", [])
        if index_columns:
            for column in index_columns:
                if column in df.columns:
                    conn.execute(f"CREATE INDEX idx_{table_name}_{column} ON {table_name}({column})")
        
        # Close connection
        conn.close()
        
        # Check if compression is enabled
        is_compressed = storage_strategy.get("compression", self.config["compression"]["enable_compression"])
        compression_method = storage_strategy.get("compression_method", self.config["compression"]["compression_method"])
        
        if is_compressed and compression_method == "gzip":
            compressed_path = storage_path + '.gz'
            
            # Compress file
            import gzip
            with open(storage_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file
            os.remove(storage_path)
            storage_path = compressed_path
        
        # Check if encryption is enabled
        is_encrypted = storage_strategy.get("encryption", self.config["encryption"]["enable_encryption"])
        
        if is_encrypted:
            # Encrypt file (placeholder for actual encryption)
            logger.warning("File encryption not implemented yet")
        
        return {
            "storage_path": storage_path,
            "is_compressed": is_compressed,
            "is_encrypted": is_encrypted
        }
    
    def _update_dataset_metadata(
        self,
        dataset_name: str,
        dataset_type: str,
        version: str,
        file_hash: str,
        file_size: int,
        storage_path: str,
        is_compressed: bool,
        is_encrypted: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Update dataset metadata in the database.
        
        Args:
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            version: Version string
            file_hash: File hash
            file_size: File size in bytes
            storage_path: Path to the stored dataset
            is_compressed: Whether the dataset is compressed
            is_encrypted: Whether the dataset is encrypted
            metadata: Additional metadata
        """
        if not self.conn:
            logger.warning("Database not initialized, metadata not updated")
            return
        
        try:
            # Check if dataset exists
            self.cursor.execute(
                "SELECT id FROM datasets WHERE name = ?",
                (dataset_name,)
            )
            result = self.cursor.fetchone()
            
            now = datetime.now().isoformat()
            
            if result:
                # Update existing dataset
                dataset_id = result[0]
                
                self.cursor.execute(
                    "UPDATE datasets SET type = ?, updated_at = ?, size = ?, hash = ? WHERE id = ?",
                    (dataset_type, now, file_size, file_hash, dataset_id)
                )
            else:
                # Insert new dataset
                retention_days = self.config["retention"]["default_retention_days"]
                
                self.cursor.execute(
                    "INSERT INTO datasets (name, type, created_at, updated_at, size, hash, retention_days, is_archived) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
                    (dataset_name, dataset_type, now, now, file_size, file_hash, retention_days)
                )
                
                dataset_id = self.cursor.lastrowid
            
            # Insert version
            self.cursor.execute(
                "INSERT INTO dataset_versions (dataset_id, version, path, created_at, size, hash, is_compressed, is_encrypted) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (dataset_id, version, storage_path, now, file_size, file_hash, int(is_compressed), int(is_encrypted))
            )
            
            # Insert metadata
            if metadata:
                for key, value in metadata.items():
                    # Convert value to string if needed
                    if not isinstance(value, str):
                        value = json.dumps(value)
                    
                    # Check if metadata exists
                    self.cursor.execute(
                        "SELECT id FROM dataset_metadata WHERE dataset_id = ? AND key = ?",
                        (dataset_id, key)
                    )
                    result = self.cursor.fetchone()
                    
                    if result:
                        # Update existing metadata
                        self.cursor.execute(
                            "UPDATE dataset_metadata SET value = ? WHERE dataset_id = ? AND key = ?",
                            (value, dataset_id, key)
                        )
                    else:
                        # Insert new metadata
                        self.cursor.execute(
                            "INSERT INTO dataset_metadata (dataset_id, key, value) VALUES (?, ?, ?)",
                            (dataset_id, key, value)
                        )
            
            # Commit changes
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update dataset metadata: {str(e)}")
            self.conn.rollback()
    
    def _apply_retention_policy(self, dataset_name: str, storage_strategy: Dict[str, Any]):
        """
        Apply retention policy to a dataset.
        
        Args:
            dataset_name: Name of the dataset
            storage_strategy: Storage strategy configuration
        """
        if not self.conn:
            logger.warning("Database not initialized, retention policy not applied")
            return
        
        try:
            # Check if retention policy is enabled
            enable_retention = storage_strategy.get(
                "enable_retention_policy",
                self.config["retention"]["enable_retention_policy"]
            )
            
            if not enable_retention:
                return
            
            # Check if versioning is enabled
            enable_versioning = storage_strategy.get(
                "versioning",
                self.config["versioning"]["enable_versioning"]
            )
            
            if enable_versioning:
                # Get max versions
                max_versions = storage_strategy.get(
                    "max_versions",
                    self.config["versioning"]["max_versions"]
                )
                
                # Get dataset ID
                self.cursor.execute(
                    "SELECT id FROM datasets WHERE name = ?",
                    (dataset_name,)
                )
                result = self.cursor.fetchone()
                
                if not result:
                    return
                
                dataset_id = result[0]
                
                # Get versions to delete
                self.cursor.execute(
                    "SELECT id, path FROM dataset_versions "
                    "WHERE dataset_id = ? "
                    "ORDER BY created_at DESC",
                    (dataset_id,)
                )
                versions = self.cursor.fetchall()
                
                if len(versions) > max_versions:
                    # Delete old versions
                    for version_id, path in versions[max_versions:]:
                        # Delete file
                        if os.path.exists(path):
                            os.remove(path)
                        
                        # Delete from database
                        self.cursor.execute(
                            "DELETE FROM dataset_versions WHERE id = ?",
                            (version_id,)
                        )
            
            # Check for archiving
            archive_after_days = storage_strategy.get(
                "archive_after_days",
                self.config["retention"]["archive_after_days"]
            )
            
            if archive_after_days > 0:
                # Get datasets to archive
                archive_date = (datetime.now() - pd.Timedelta(days=archive_after_days)).isoformat()
                
                self.cursor.execute(
                    "SELECT id, name FROM datasets "
                    "WHERE updated_at < ? AND is_archived = 0",
                    (archive_date,)
                )
                datasets_to_archive = self.cursor.fetchall()
                
                for dataset_id, name in datasets_to_archive:
                    # Archive dataset
                    logger.info(f"Archiving dataset: {name}")
                    
                    # Get all versions
                    self.cursor.execute(
                        "SELECT path FROM dataset_versions WHERE dataset_id = ?",
                        (dataset_id,)
                    )
                    paths = [row[0] for row in self.cursor.fetchall()]
                    
                    # Create archive directory
                    archive_dir = os.path.join(self.archive_dir, name)
                    os.makedirs(archive_dir, exist_ok=True)
                    
                    # Move files to archive
                    for path in paths:
                        if os.path.exists(path):
                            archive_path = os.path.join(archive_dir, os.path.basename(path))
                            shutil.move(path, archive_path)
                            
                            # Update path in database
                            self.cursor.execute(
                                "UPDATE dataset_versions SET path = ? WHERE path = ?",
                                (archive_path, path)
                            )
                    
                    # Mark as archived
                    self.cursor.execute(
                        "UPDATE datasets SET is_archived = 1 WHERE id = ?",
                        (dataset_id,)
                    )
            
            # Commit changes
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to apply retention policy: {str(e)}")
            self.conn.rollback()
    
    def retrieve_dataset(
        self,
        dataset_name: str,
        version: str = "latest",
        output_path: Optional[str] = None,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Retrieve a dataset.
        
        Args:
            dataset_name: Name of the dataset
            version: Version to retrieve (latest, all, or specific version)
            output_path: Path to save the dataset
            emit_events: Whether to emit protocol events
            
        Returns:
            Retrieval result
        """
        try:
            # Start retrieval
            start_time = time.time()
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_retrieval_started",
                        "dataset": dataset_name,
                        "version": version
                    }
                )
            
            if not self.conn:
                raise ValueError("Database not initialized")
            
            # Get dataset ID
            self.cursor.execute(
                "SELECT id, type FROM datasets WHERE name = ?",
                (dataset_name,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                raise ValueError(f"Dataset not found: {dataset_name}")
            
            dataset_id, dataset_type = result
            
            # Get version
            if version == "latest":
                self.cursor.execute(
                    "SELECT version, path, is_compressed, is_encrypted FROM dataset_versions "
                    "WHERE dataset_id = ? "
                    "ORDER BY created_at DESC LIMIT 1",
                    (dataset_id,)
                )
                result = self.cursor.fetchone()
                
                if not result:
                    raise ValueError(f"No versions found for dataset: {dataset_name}")
                
                version_str, path, is_compressed, is_encrypted = result
                paths = [(version_str, path, bool(is_compressed), bool(is_encrypted))]
            elif version == "all":
                self.cursor.execute(
                    "SELECT version, path, is_compressed, is_encrypted FROM dataset_versions "
                    "WHERE dataset_id = ? "
                    "ORDER BY created_at DESC",
                    (dataset_id,)
                )
                paths = [(row[0], row[1], bool(row[2]), bool(row[3])) for row in self.cursor.fetchall()]
                
                if not paths:
                    raise ValueError(f"No versions found for dataset: {dataset_name}")
            else:
                self.cursor.execute(
                    "SELECT version, path, is_compressed, is_encrypted FROM dataset_versions "
                    "WHERE dataset_id = ? AND version = ?",
                    (dataset_id, version)
                )
                result = self.cursor.fetchone()
                
                if not result:
                    raise ValueError(f"Version not found: {version} for dataset: {dataset_name}")
                
                version_str, path, is_compressed, is_encrypted = result
                paths = [(version_str, path, bool(is_compressed), bool(is_encrypted))]
            
            # Create output directory if needed
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            else:
                output_path = os.path.join(self.temp_dir, dataset_name)
                os.makedirs(output_path, exist_ok=True)
            
            # Retrieve files
            retrieved_paths = []
            
            for version_str, path, is_compressed, is_encrypted in paths:
                if not os.path.exists(path):
                    logger.warning(f"File not found: {path}")
                    continue
                
                # Generate output file path
                if os.path.isdir(output_path):
                    output_file = os.path.join(output_path, f"{dataset_name}_v{version_str}{os.path.splitext(path)[1]}")
                else:
                    output_file = output_path
                
                # Decrypt if needed
                if is_encrypted:
                    # Decrypt file (placeholder for actual decryption)
                    logger.warning("File decryption not implemented yet")
                
                # Decompress if needed
                if is_compressed and path.endswith('.gz'):
                    import gzip
                    
                    # Remove .gz extension from output file
                    if output_file.endswith('.gz'):
                        output_file = output_file[:-3]
                    
                    with gzip.open(path, 'rb') as f_in:
                        with open(output_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                elif is_compressed and path.endswith('.zip'):
                    import zipfile
                    
                    # Remove .zip extension from output file
                    if output_file.endswith('.zip'):
                        output_file = output_file[:-4]
                    
                    with zipfile.ZipFile(path, 'r') as zipf:
                        # Extract first file
                        zipf.extractall(os.path.dirname(output_file))
                        
                        # Rename extracted file
                        extracted_file = zipf.namelist()[0]
                        extracted_path = os.path.join(os.path.dirname(output_file), extracted_file)
                        
                        if os.path.exists(extracted_path) and extracted_path != output_file:
                            shutil.move(extracted_path, output_file)
                else:
                    # Just copy the file
                    shutil.copy2(path, output_file)
                
                retrieved_paths.append(output_file)
            
            # Complete retrieval
            end_time = time.time()
            duration = end_time - start_time
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_retrieval_completed",
                        "dataset": dataset_name,
                        "retrieval_time": duration,
                        "output_paths": retrieved_paths
                    }
                )
            
            logger.info(f"Completed dataset retrieval for {dataset_name} in {duration:.2f}s")
            return {
                "success": True,
                "dataset": dataset_name,
                "output_paths": retrieved_paths,
                "retrieval_time": duration,
                "version": version
            }
        except Exception as e:
            logger.error(f"Failed to retrieve dataset: {str(e)}")
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_retrieval_failed",
                        "dataset": dataset_name,
                        "error": str(e)
                    }
                )
            
            return {
                "success": False,
                "dataset": dataset_name,
                "error": str(e)
            }
    
    def delete_dataset(
        self,
        dataset_name: str,
        version: str = "all",
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Delete a dataset.
        
        Args:
            dataset_name: Name of the dataset
            version: Version to delete (all or specific version)
            emit_events: Whether to emit protocol events
            
        Returns:
            Deletion result
        """
        try:
            # Start deletion
            start_time = time.time()
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_deletion_started",
                        "dataset": dataset_name,
                        "version": version
                    }
                )
            
            if not self.conn:
                raise ValueError("Database not initialized")
            
            # Get dataset ID
            self.cursor.execute(
                "SELECT id FROM datasets WHERE name = ?",
                (dataset_name,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                raise ValueError(f"Dataset not found: {dataset_name}")
            
            dataset_id = result[0]
            
            # Get versions to delete
            if version == "all":
                self.cursor.execute(
                    "SELECT id, path FROM dataset_versions WHERE dataset_id = ?",
                    (dataset_id,)
                )
                versions_to_delete = self.cursor.fetchall()
                
                # Delete dataset
                self.cursor.execute(
                    "DELETE FROM datasets WHERE id = ?",
                    (dataset_id,)
                )
                
                # Delete metadata
                self.cursor.execute(
                    "DELETE FROM dataset_metadata WHERE dataset_id = ?",
                    (dataset_id,)
                )
            else:
                self.cursor.execute(
                    "SELECT id, path FROM dataset_versions WHERE dataset_id = ? AND version = ?",
                    (dataset_id, version)
                )
                versions_to_delete = self.cursor.fetchall()
                
                if not versions_to_delete:
                    raise ValueError(f"Version not found: {version} for dataset: {dataset_name}")
                
                # Delete version
                self.cursor.execute(
                    "DELETE FROM dataset_versions WHERE dataset_id = ? AND version = ?",
                    (dataset_id, version)
                )
            
            # Delete files
            deleted_paths = []
            
            for version_id, path in versions_to_delete:
                if os.path.exists(path):
                    os.remove(path)
                    deleted_paths.append(path)
            
            # Commit changes
            self.conn.commit()
            
            # Complete deletion
            end_time = time.time()
            duration = end_time - start_time
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_deletion_completed",
                        "dataset": dataset_name,
                        "deletion_time": duration,
                        "deleted_paths": deleted_paths
                    }
                )
            
            logger.info(f"Completed dataset deletion for {dataset_name} in {duration:.2f}s")
            return {
                "success": True,
                "dataset": dataset_name,
                "deleted_paths": deleted_paths,
                "deletion_time": duration,
                "version": version
            }
        except Exception as e:
            logger.error(f"Failed to delete dataset: {str(e)}")
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_deletion_failed",
                        "dataset": dataset_name,
                        "error": str(e)
                    }
                )
            
            return {
                "success": False,
                "dataset": dataset_name,
                "error": str(e)
            }
    
    def list_datasets(
        self,
        dataset_type: Optional[str] = None,
        include_archived: bool = False,
        include_metadata: bool = False
    ) -> Dict[str, Any]:
        """
        List available datasets.
        
        Args:
            dataset_type: Filter by dataset type
            include_archived: Whether to include archived datasets
            include_metadata: Whether to include metadata
            
        Returns:
            List of datasets
        """
        try:
            if not self.conn:
                raise ValueError("Database not initialized")
            
            # Build query
            query = "SELECT id, name, type, created_at, updated_at, size, is_archived FROM datasets"
            params = []
            
            conditions = []
            
            if dataset_type:
                conditions.append("type = ?")
                params.append(dataset_type)
            
            if not include_archived:
                conditions.append("is_archived = 0")
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            # Execute query
            self.cursor.execute(query, params)
            datasets = []
            
            for row in self.cursor.fetchall():
                dataset_id, name, type_, created_at, updated_at, size, is_archived = row
                
                dataset_info = {
                    "id": dataset_id,
                    "name": name,
                    "type": type_,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "size": size,
                    "is_archived": bool(is_archived)
                }
                
                # Get versions
                self.cursor.execute(
                    "SELECT version, created_at, size FROM dataset_versions "
                    "WHERE dataset_id = ? "
                    "ORDER BY created_at DESC",
                    (dataset_id,)
                )
                
                dataset_info["versions"] = [
                    {
                        "version": version,
                        "created_at": created_at,
                        "size": size
                    }
                    for version, created_at, size in self.cursor.fetchall()
                ]
                
                # Get metadata if requested
                if include_metadata:
                    self.cursor.execute(
                        "SELECT key, value FROM dataset_metadata WHERE dataset_id = ?",
                        (dataset_id,)
                    )
                    
                    metadata = {}
                    for key, value in self.cursor.fetchall():
                        try:
                            # Try to parse JSON
                            metadata[key] = json.loads(value)
                        except (json.JSONDecodeError, TypeError):
                            # JSONDecodeError: invalid JSON
                            # TypeError: value is not a string
                            metadata[key] = value
                    
                    dataset_info["metadata"] = metadata
                
                datasets.append(dataset_info)
            
            return {
                "success": True,
                "datasets": datasets,
                "count": len(datasets)
            }
        except Exception as e:
            logger.error(f"Failed to list datasets: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_storage_strategy_for_offer(
        self,
        offer_id: str,
        dataset_name: str,
        dataset_type: str
    ) -> Dict[str, Any]:
        """
        Get storage strategy configuration for a specific offer.
        
        Args:
            offer_id: ID of the offer
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            
        Returns:
            Storage strategy configuration
        """
        # Map offer IDs to specific storage configurations
        offer_mappings = {
            "predictive_maintenance": {
                "storage_mode": "database",
                "compression": True,
                "compression_method": "gzip",
                "encryption": False,
                "versioning": True,
                "max_versions": 10,
                "retention_days": 730  # 2 years
            },
            "anomaly_detection": {
                "storage_mode": "database",
                "compression": True,
                "compression_method": "gzip",
                "encryption": False,
                "versioning": True,
                "max_versions": 5,
                "retention_days": 365  # 1 year
            },
            "energy_optimization": {
                "storage_mode": "database",
                "compression": True,
                "compression_method": "gzip",
                "encryption": False,
                "versioning": True,
                "max_versions": 12,
                "retention_days": 1095  # 3 years
            },
            "quality_control": {
                "storage_mode": "file",
                "compression": True,
                "compression_method": "gzip",
                "encryption": False,
                "versioning": True,
                "max_versions": 3,
                "retention_days": 180  # 6 months
            },
            "safety_monitoring": {
                "storage_mode": "file",
                "compression": True,
                "compression_method": "gzip",
                "encryption": True,
                "versioning": True,
                "max_versions": 10,
                "retention_days": 1825  # 5 years
            }
        }
        
        # Find matching offer prefix
        storage_strategy = None
        for prefix, config in offer_mappings.items():
            if offer_id.startswith(prefix):
                storage_strategy = config
                break
        
        # Use default config if no match found
        if storage_strategy is None:
            storage_strategy = {
                "storage_mode": self.config["default_mode"],
                "compression": self.config["compression"]["enable_compression"],
                "compression_method": self.config["compression"]["compression_method"],
                "encryption": self.config["encryption"]["enable_encryption"],
                "versioning": self.config["versioning"]["enable_versioning"],
                "max_versions": self.config["versioning"]["max_versions"],
                "retention_days": self.config["retention"]["default_retention_days"]
            }
        
        # Adjust based on dataset type
        if dataset_type == "image":
            # Minimal compression for image datasets
            storage_strategy["compression"] = False
        
        # Add metadata
        storage_strategy["offer_id"] = offer_id
        storage_strategy["dataset_name"] = dataset_name
        storage_strategy["dataset_type"] = dataset_type
        storage_strategy["created_at"] = datetime.now().isoformat()
        
        return storage_strategy


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create storage management system
    storage_system = StorageManagementSystem()
    
    # Store a dataset
    result = storage_system.store_dataset(
        dataset_path="path/to/dataset.csv",
        dataset_name="example_dataset"
    )
    
    print(f"Storage result: {json.dumps(result, indent=2)}")
    
    # Retrieve a dataset
    result = storage_system.retrieve_dataset(
        dataset_name="example_dataset"
    )
    
    print(f"Retrieval result: {json.dumps(result, indent=2)}")
    
    # List datasets
    result = storage_system.list_datasets()
    
    print(f"Datasets: {json.dumps(result, indent=2)}")
