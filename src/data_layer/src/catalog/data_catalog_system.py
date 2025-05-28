"""
Data Catalog System for Industriverse Data Layer

This module implements a protocol-native data catalog system that provides
discovery, metadata management, and governance capabilities for industrial datasets.
"""

import json
import logging
import os
import time
from typing import Dict, Any, Optional, List, Union, Tuple
from datetime import datetime
import sqlite3
import pandas as pd
import yaml

logger = logging.getLogger(__name__)

class DataCatalogSystem:
    """
    Protocol-native data catalog system for industrial datasets.
    
    This system provides dataset discovery, metadata management, and governance
    capabilities, with full MCP/A2A protocol integration.
    """
    
    def __init__(
        self,
        system_id: str = "data-catalog-system",
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[Any] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the data catalog system.
        
        Args:
            system_id: Unique identifier for this system
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for catalog files
        """
        # Default configuration
        default_config = {
            "industry_tags": ["manufacturing", "process_industry", "energy"],
            "intelligence_type": "data_catalog",
            "catalog_modes": ["local", "distributed"],
            "default_mode": "local",
            "search": {
                "enable_full_text_search": True,
                "index_metadata": True,
                "index_content": False
            },
            "governance": {
                "enable_lineage_tracking": True,
                "enable_access_control": True,
                "enable_data_quality_tracking": True
            },
            "metadata": {
                "schema_validation": True,
                "auto_tagging": True,
                "custom_metadata_fields": []
            },
            "discovery": {
                "auto_discovery_interval": 3600,  # seconds
                "scan_directories": [],
                "scan_databases": []
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
            self.base_dir = os.path.join(os.getcwd(), "data_catalog")
        
        # Set up subdirectories
        self.metadata_dir = os.path.join(self.base_dir, "metadata")
        self.schema_dir = os.path.join(self.base_dir, "schemas")
        self.index_dir = os.path.join(self.base_dir, "index")
        self.lineage_dir = os.path.join(self.base_dir, "lineage")
        
        os.makedirs(self.metadata_dir, exist_ok=True)
        os.makedirs(self.schema_dir, exist_ok=True)
        os.makedirs(self.index_dir, exist_ok=True)
        os.makedirs(self.lineage_dir, exist_ok=True)
        
        # Set up agent manifest
        self.manifest_path = manifest_path
        if not self.manifest_path:
            self.manifest_path = os.path.join(self.base_dir, "agent_manifest.yaml")
        
        # Initialize protocol integration
        self._initialize_protocol_integration()
        
        # Initialize database
        self._initialize_database()
        
        logger.info(f"Initialized data catalog system: {self.system_id}")
    
    def _initialize_protocol_integration(self):
        """Initialize protocol integration for MCP/A2A compatibility."""
        try:
            # Import protocol modules
            import sys
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "protocols"))
            
            from agent_core import AgentCore
            from protocol_translator import ProtocolTranslator
            from mesh_boot_lifecycle import MeshBootLifecycle
            from mesh_agent_intent_graph import MeshAgentIntentGraph
            
            # Initialize agent core
            self.agent_core = AgentCore(
                agent_id=self.system_id,
                agent_type="data_catalog_system",
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
            
            # Initialize mesh agent intent graph
            self.mesh_intent_graph = MeshAgentIntentGraph(
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
            self.mesh_intent_graph = None
    
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
            if "dataset_storage_completed" in event.get("status", ""):
                # New dataset stored, catalog it
                dataset_name = event.get("dataset", "")
                storage_path = event.get("storage_path", "")
                version = event.get("version", "")
                
                if dataset_name and storage_path:
                    logger.info(f"Observed new dataset storage completion: {dataset_name}")
                    # Schedule cataloging
                    self.catalog_dataset(
                        dataset_name=dataset_name,
                        dataset_path=storage_path,
                        version=version,
                        metadata=event.get("metadata", {})
                    )
                    
                    return {
                        "status": "cataloging_scheduled",
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
            if "catalog_requirements" in event:
                # Simulate catalog requirements
                dataset_name = event.get("dataset", "")
                dataset_type = event.get("dataset_type", "")
                
                if dataset_name:
                    logger.info(f"Simulating catalog requirements for {dataset_name}")
                    # Return simulated metrics
                    return {
                        "status": "simulation_completed",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "simulated_metrics": {
                            "metadata_fields": self._get_metadata_fields_for_dataset_type(dataset_type),
                            "governance_requirements": self._get_governance_requirements_for_dataset_type(dataset_type),
                            "discovery_methods": ["api", "search", "browse"],
                            "lineage_tracking": self.config["governance"]["enable_lineage_tracking"]
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
                # Recommend catalog strategy
                dataset_name = event.get("dataset", "")
                dataset_type = event.get("dataset_type", "")
                
                if dataset_name:
                    logger.info(f"Recommending catalog strategy for {dataset_name}")
                    # Return recommended strategy
                    return {
                        "status": "recommendation_provided",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "recommended_strategy": self._get_catalog_strategy_for_dataset_type(dataset_type)
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
            if "catalog_dataset" in event.get("action", ""):
                # Catalog dataset
                dataset_name = event.get("dataset", "")
                dataset_path = event.get("dataset_path", "")
                dataset_type = event.get("dataset_type", "")
                metadata = event.get("metadata", {})
                
                if dataset_name and dataset_path:
                    logger.info(f"Cataloging dataset: {dataset_name}")
                    # Catalog dataset
                    result = self.catalog_dataset(
                        dataset_name=dataset_name,
                        dataset_path=dataset_path,
                        dataset_type=dataset_type,
                        metadata=metadata
                    )
                    
                    return {
                        "status": "cataloging_completed" if result["success"] else "cataloging_failed",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "result": result
                    }
            elif "search_datasets" in event.get("action", ""):
                # Search datasets
                query = event.get("query", "")
                dataset_type = event.get("dataset_type", "")
                
                if query:
                    logger.info(f"Searching datasets with query: {query}")
                    # Search datasets
                    result = self.search_datasets(
                        query=query,
                        dataset_type=dataset_type
                    )
                    
                    return {
                        "status": "search_completed" if result["success"] else "search_failed",
                        "query": query,
                        "system_id": self.system_id,
                        "result": result
                    }
            elif "get_dataset_lineage" in event.get("action", ""):
                # Get dataset lineage
                dataset_name = event.get("dataset", "")
                
                if dataset_name:
                    logger.info(f"Getting lineage for dataset: {dataset_name}")
                    # Get lineage
                    result = self.get_dataset_lineage(
                        dataset_name=dataset_name
                    )
                    
                    return {
                        "status": "lineage_retrieval_completed" if result["success"] else "lineage_retrieval_failed",
                        "dataset": dataset_name,
                        "system_id": self.system_id,
                        "result": result
                    }
            
            return {"status": "action_completed", "system_id": self.system_id}
        except Exception as e:
            logger.error(f"Error handling act event: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _initialize_database(self):
        """Initialize the catalog database."""
        try:
            # Create database file
            db_path = os.path.join(self.metadata_dir, "catalog_metadata.db")
            
            # Connect to database
            self.conn = sqlite3.connect(db_path)
            self.cursor = self.conn.cursor()
            
            # Create tables if they don't exist
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS datasets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP NOT NULL,
                    updated_at TIMESTAMP NOT NULL,
                    owner TEXT,
                    source TEXT,
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
                    schema_path TEXT,
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
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS dataset_lineage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    parent_dataset_id INTEGER,
                    transformation TEXT,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id),
                    FOREIGN KEY (parent_dataset_id) REFERENCES datasets(id)
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS dataset_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id),
                    UNIQUE(dataset_id, tag)
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS dataset_quality (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    dataset_id INTEGER NOT NULL,
                    version TEXT NOT NULL,
                    metric TEXT NOT NULL,
                    value REAL NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (dataset_id) REFERENCES datasets(id)
                )
            ''')
            
            # Create full-text search virtual table if enabled
            if self.config["search"]["enable_full_text_search"]:
                self.cursor.execute('''
                    CREATE VIRTUAL TABLE IF NOT EXISTS dataset_search USING fts5(
                        name, description, type, tags, metadata,
                        content='datasets',
                        content_rowid='id'
                    )
                ''')
                
                # Create triggers to keep FTS index updated
                self.cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS datasets_ai AFTER INSERT ON datasets BEGIN
                        INSERT INTO dataset_search(rowid, name, description, type, tags, metadata)
                        VALUES (new.id, new.name, new.description, new.type, '', '');
                    END;
                ''')
                
                self.cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS datasets_ad AFTER DELETE ON datasets BEGIN
                        DELETE FROM dataset_search WHERE rowid = old.id;
                    END;
                ''')
                
                self.cursor.execute('''
                    CREATE TRIGGER IF NOT EXISTS datasets_au AFTER UPDATE ON datasets BEGIN
                        UPDATE dataset_search SET
                            name = new.name,
                            description = new.description,
                            type = new.type
                        WHERE rowid = new.id;
                    END;
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
    
    def _get_metadata_fields_for_dataset_type(self, dataset_type: str) -> List[str]:
        """
        Get metadata fields for a specific dataset type.
        
        Args:
            dataset_type: Type of dataset
            
        Returns:
            List of metadata fields
        """
        # Common fields
        common_fields = [
            "name", "description", "owner", "created_at", "updated_at",
            "version", "source", "license", "tags"
        ]
        
        # Type-specific fields
        if dataset_type == "timeseries":
            return common_fields + [
                "frequency", "start_date", "end_date", "num_records",
                "time_column", "value_columns", "categorical_columns"
            ]
        elif dataset_type == "tabular":
            return common_fields + [
                "num_rows", "num_columns", "column_names", "column_types",
                "categorical_columns", "numerical_columns", "primary_key"
            ]
        elif dataset_type == "image":
            return common_fields + [
                "num_images", "image_format", "resolution", "color_mode",
                "annotations", "classes", "preprocessing"
            ]
        else:
            return common_fields
    
    def _get_governance_requirements_for_dataset_type(self, dataset_type: str) -> Dict[str, Any]:
        """
        Get governance requirements for a specific dataset type.
        
        Args:
            dataset_type: Type of dataset
            
        Returns:
            Governance requirements
        """
        # Common requirements
        common_requirements = {
            "lineage_tracking": self.config["governance"]["enable_lineage_tracking"],
            "access_control": self.config["governance"]["enable_access_control"],
            "data_quality_tracking": self.config["governance"]["enable_data_quality_tracking"]
        }
        
        # Type-specific requirements
        if dataset_type == "timeseries":
            return {
                **common_requirements,
                "completeness_check": True,
                "anomaly_detection": True,
                "seasonality_analysis": True
            }
        elif dataset_type == "tabular":
            return {
                **common_requirements,
                "schema_validation": True,
                "null_value_check": True,
                "duplicate_check": True,
                "range_check": True
            }
        elif dataset_type == "image":
            return {
                **common_requirements,
                "format_validation": True,
                "resolution_check": True,
                "annotation_validation": True
            }
        else:
            return common_requirements
    
    def _get_catalog_strategy_for_dataset_type(self, dataset_type: str) -> Dict[str, Any]:
        """
        Get catalog strategy for a specific dataset type.
        
        Args:
            dataset_type: Type of dataset
            
        Returns:
            Catalog strategy configuration
        """
        # Default strategy
        default_strategy = {
            "catalog_mode": self.config["default_mode"],
            "metadata_fields": self._get_metadata_fields_for_dataset_type(dataset_type),
            "governance_requirements": self._get_governance_requirements_for_dataset_type(dataset_type),
            "schema_validation": self.config["metadata"]["schema_validation"],
            "auto_tagging": self.config["metadata"]["auto_tagging"],
            "full_text_search": self.config["search"]["enable_full_text_search"]
        }
        
        # Customize based on dataset type
        if dataset_type == "timeseries":
            return {
                **default_strategy,
                "auto_tagging": True,
                "time_series_profiling": True,
                "seasonality_detection": True
            }
        elif dataset_type == "tabular":
            return {
                **default_strategy,
                "auto_tagging": True,
                "schema_inference": True,
                "data_profiling": True
            }
        elif dataset_type == "image":
            return {
                **default_strategy,
                "auto_tagging": True,
                "image_preview": True,
                "annotation_tracking": True
            }
        else:
            return default_strategy
    
    def catalog_dataset(
        self,
        dataset_name: str,
        dataset_path: str,
        dataset_type: str = "",
        version: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        parent_datasets: Optional[List[Dict[str, Any]]] = None,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Catalog a dataset.
        
        Args:
            dataset_name: Name of the dataset
            dataset_path: Path to the dataset file
            dataset_type: Type of dataset
            version: Version of the dataset
            metadata: Additional metadata
            parent_datasets: Parent datasets for lineage tracking
            emit_events: Whether to emit protocol events
            
        Returns:
            Cataloging result
        """
        try:
            # Start cataloging
            start_time = time.time()
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_cataloging_started",
                        "dataset": dataset_name,
                        "dataset_path": dataset_path
                    }
                )
            
            # Determine dataset type if not provided
            if not dataset_type:
                dataset_type = self._determine_dataset_type(dataset_path)
            
            # Generate version if not provided
            if not version:
                version = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Get catalog strategy
            catalog_strategy = self._get_catalog_strategy_for_dataset_type(dataset_type)
            
            # Extract metadata if not provided
            if not metadata:
                metadata = self._extract_metadata(
                    dataset_path=dataset_path,
                    dataset_type=dataset_type,
                    catalog_strategy=catalog_strategy
                )
            
            # Merge with provided metadata
            if metadata:
                metadata.update(metadata)
            
            # Add basic metadata
            now = datetime.now().isoformat()
            
            if "created_at" not in metadata:
                metadata["created_at"] = now
            
            if "updated_at" not in metadata:
                metadata["updated_at"] = now
            
            if "source" not in metadata:
                metadata["source"] = dataset_path
            
            # Generate schema if enabled
            schema_path = None
            if catalog_strategy.get("schema_validation", False):
                schema_path = self._generate_schema(
                    dataset_path=dataset_path,
                    dataset_name=dataset_name,
                    dataset_type=dataset_type,
                    version=version
                )
            
            # Auto-generate tags if enabled
            tags = []
            if catalog_strategy.get("auto_tagging", False):
                tags = self._generate_tags(
                    dataset_path=dataset_path,
                    dataset_name=dataset_name,
                    dataset_type=dataset_type,
                    metadata=metadata
                )
            
            # Add to database
            self._add_to_database(
                dataset_name=dataset_name,
                dataset_type=dataset_type,
                dataset_path=dataset_path,
                version=version,
                schema_path=schema_path,
                metadata=metadata,
                tags=tags
            )
            
            # Add lineage if provided
            if parent_datasets:
                self._add_lineage(
                    dataset_name=dataset_name,
                    parent_datasets=parent_datasets
                )
            
            # Generate quality metrics if enabled
            if catalog_strategy.get("data_quality_tracking", False):
                self._generate_quality_metrics(
                    dataset_path=dataset_path,
                    dataset_name=dataset_name,
                    dataset_type=dataset_type,
                    version=version
                )
            
            # Update search index if enabled
            if catalog_strategy.get("full_text_search", False):
                self._update_search_index(
                    dataset_name=dataset_name,
                    metadata=metadata,
                    tags=tags
                )
            
            # Complete cataloging
            end_time = time.time()
            duration = end_time - start_time
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_cataloging_completed",
                        "dataset": dataset_name,
                        "cataloging_time": duration,
                        "dataset_type": dataset_type,
                        "version": version
                    }
                )
            
            logger.info(f"Completed dataset cataloging for {dataset_name} in {duration:.2f}s")
            return {
                "success": True,
                "dataset": dataset_name,
                "dataset_type": dataset_type,
                "version": version,
                "cataloging_time": duration,
                "schema_path": schema_path,
                "tags": tags
            }
        except Exception as e:
            logger.error(f"Failed to catalog dataset: {str(e)}")
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "dataset_cataloging_failed",
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
                try:
                    sample_df = pd.read_csv(dataset_path, nrows=100)
                except:
                    return "tabular"
            else:
                try:
                    sample_df = pd.read_excel(dataset_path, nrows=100)
                except:
                    return "tabular"
            
            # Check for datetime columns
            datetime_cols = []
            for col in sample_df.columns:
                try:
                    pd.to_datetime(sample_df[col])
                    datetime_cols.append(col)
                except:
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
            except:
                return "json"
        elif dataset_path.endswith('.db'):
            return "database"
        else:
            return "unknown"
    
    def _extract_metadata(
        self,
        dataset_path: str,
        dataset_type: str,
        catalog_strategy: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract metadata from a dataset.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_type: Type of dataset
            catalog_strategy: Catalog strategy configuration
            
        Returns:
            Extracted metadata
        """
        metadata = {}
        
        try:
            if dataset_type == "timeseries" or dataset_type == "tabular":
                # Load dataset
                if dataset_path.endswith('.csv'):
                    try:
                        df = pd.read_csv(dataset_path)
                    except:
                        return metadata
                elif dataset_path.endswith(('.xlsx', '.xls')):
                    try:
                        df = pd.read_excel(dataset_path)
                    except:
                        return metadata
                elif dataset_path.endswith('.db'):
                    try:
                        conn = sqlite3.connect(dataset_path)
                        # Get first table
                        cursor = conn.cursor()
                        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                        tables = cursor.fetchall()
                        if tables:
                            table_name = tables[0][0]
                            df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                        else:
                            return metadata
                    except:
                        return metadata
                else:
                    return metadata
                
                # Extract basic metadata
                metadata["num_rows"] = len(df)
                metadata["num_columns"] = len(df.columns)
                metadata["column_names"] = df.columns.tolist()
                
                # Extract column types
                column_types = {}
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        column_types[col] = "numeric"
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        column_types[col] = "datetime"
                    else:
                        column_types[col] = "string"
                
                metadata["column_types"] = column_types
                
                # Extract categorical and numerical columns
                categorical_columns = []
                numerical_columns = []
                
                for col in df.columns:
                    if pd.api.types.is_numeric_dtype(df[col]):
                        numerical_columns.append(col)
                    elif pd.api.types.is_categorical_dtype(df[col]) or df[col].nunique() < 20:
                        categorical_columns.append(col)
                
                metadata["categorical_columns"] = categorical_columns
                metadata["numerical_columns"] = numerical_columns
                
                # Extract time series specific metadata
                if dataset_type == "timeseries":
                    # Find datetime columns
                    datetime_cols = []
                    for col in df.columns:
                        try:
                            pd.to_datetime(df[col])
                            datetime_cols.append(col)
                        except:
                            pass
                    
                    if datetime_cols:
                        time_col = datetime_cols[0]
                        metadata["time_column"] = time_col
                        
                        # Convert to datetime
                        df[time_col] = pd.to_datetime(df[time_col])
                        
                        # Extract start and end dates
                        metadata["start_date"] = df[time_col].min().isoformat()
                        metadata["end_date"] = df[time_col].max().isoformat()
                        
                        # Extract frequency
                        try:
                            freq = pd.infer_freq(df[time_col])
                            if freq:
                                metadata["frequency"] = freq
                        except:
                            pass
                        
                        # Extract value columns (non-datetime, non-categorical)
                        value_columns = [col for col in numerical_columns if col != time_col]
                        metadata["value_columns"] = value_columns
            
            elif dataset_type == "image":
                # Check if it's a single image or a directory
                if os.path.isfile(dataset_path):
                    # Single image
                    metadata["num_images"] = 1
                    metadata["image_format"] = os.path.splitext(dataset_path)[1][1:]
                    
                    # Try to get image dimensions
                    try:
                        from PIL import Image
                        img = Image.open(dataset_path)
                        metadata["resolution"] = f"{img.width}x{img.height}"
                        metadata["color_mode"] = img.mode
                    except:
                        pass
                elif os.path.isdir(dataset_path):
                    # Directory of images
                    image_files = [f for f in os.listdir(dataset_path) if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                    metadata["num_images"] = len(image_files)
                    
                    # Get image formats
                    formats = set()
                    for f in image_files:
                        formats.add(os.path.splitext(f)[1][1:])
                    
                    metadata["image_format"] = list(formats)
                    
                    # Try to get dimensions of first image
                    if image_files:
                        try:
                            from PIL import Image
                            img = Image.open(os.path.join(dataset_path, image_files[0]))
                            metadata["resolution"] = f"{img.width}x{img.height}"
                            metadata["color_mode"] = img.mode
                        except:
                            pass
                
                # Check for annotations
                annotation_file = None
                if os.path.isdir(dataset_path):
                    # Look for annotation files
                    for f in os.listdir(dataset_path):
                        if f.endswith(('.json', '.xml', '.csv')) and ('annot' in f.lower() or 'label' in f.lower()):
                            annotation_file = os.path.join(dataset_path, f)
                            break
                
                if annotation_file:
                    metadata["annotations"] = annotation_file
                    
                    # Try to extract classes
                    try:
                        if annotation_file.endswith('.json'):
                            with open(annotation_file, 'r') as f:
                                annot_data = json.load(f)
                            
                            classes = set()
                            if isinstance(annot_data, list):
                                for item in annot_data:
                                    if "category" in item:
                                        classes.add(item["category"])
                                    elif "class" in item:
                                        classes.add(item["class"])
                                    elif "label" in item:
                                        classes.add(item["label"])
                            
                            if classes:
                                metadata["classes"] = list(classes)
                        elif annotation_file.endswith('.csv'):
                            df = pd.read_csv(annotation_file)
                            class_cols = [col for col in df.columns if "class" in col.lower() or "label" in col.lower() or "category" in col.lower()]
                            
                            if class_cols:
                                classes = set(df[class_cols[0]].unique())
                                metadata["classes"] = list(classes)
                    except:
                        pass
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
        
        return metadata
    
    def _generate_schema(
        self,
        dataset_path: str,
        dataset_name: str,
        dataset_type: str,
        version: str
    ) -> Optional[str]:
        """
        Generate schema for a dataset.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            version: Version of the dataset
            
        Returns:
            Path to the generated schema file
        """
        try:
            # Create schema directory
            schema_dir = os.path.join(self.schema_dir, dataset_name)
            os.makedirs(schema_dir, exist_ok=True)
            
            # Generate schema path
            schema_path = os.path.join(schema_dir, f"{dataset_name}_v{version}_schema.json")
            
            if dataset_type == "timeseries" or dataset_type == "tabular":
                # Load dataset
                if dataset_path.endswith('.csv'):
                    df = pd.read_csv(dataset_path)
                elif dataset_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(dataset_path)
                elif dataset_path.endswith('.db'):
                    conn = sqlite3.connect(dataset_path)
                    # Get first table
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    if tables:
                        table_name = tables[0][0]
                        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    else:
                        return None
                else:
                    return None
                
                # Generate schema
                schema = {
                    "type": "object",
                    "properties": {
                        "columns": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                }
                
                # Add column schemas
                for col in df.columns:
                    col_schema = {}
                    
                    if pd.api.types.is_numeric_dtype(df[col]):
                        if pd.api.types.is_integer_dtype(df[col]):
                            col_schema["type"] = "integer"
                        else:
                            col_schema["type"] = "number"
                        
                        # Add range
                        try:
                            col_schema["minimum"] = float(df[col].min())
                            col_schema["maximum"] = float(df[col].max())
                        except:
                            pass
                    elif pd.api.types.is_datetime64_any_dtype(df[col]):
                        col_schema["type"] = "string"
                        col_schema["format"] = "date-time"
                    else:
                        col_schema["type"] = "string"
                        
                        # Add enum for categorical columns with few unique values
                        if df[col].nunique() < 20:
                            try:
                                col_schema["enum"] = df[col].dropna().unique().tolist()
                            except:
                                pass
                    
                    schema["properties"]["columns"]["properties"][col] = col_schema
                
                # Save schema
                with open(schema_path, 'w') as f:
                    json.dump(schema, f, indent=2)
                
                return schema_path
            elif dataset_type == "image":
                # Generate image schema
                schema = {
                    "type": "object",
                    "properties": {
                        "image": {
                            "type": "object",
                            "properties": {
                                "format": {
                                    "type": "string",
                                    "enum": ["jpg", "jpeg", "png", "bmp"]
                                },
                                "width": {
                                    "type": "integer",
                                    "minimum": 1
                                },
                                "height": {
                                    "type": "integer",
                                    "minimum": 1
                                },
                                "channels": {
                                    "type": "integer",
                                    "enum": [1, 3, 4]
                                }
                            }
                        }
                    }
                }
                
                # Check for annotations
                annotation_file = None
                if os.path.isdir(dataset_path):
                    # Look for annotation files
                    for f in os.listdir(dataset_path):
                        if f.endswith(('.json', '.xml', '.csv')) and ('annot' in f.lower() or 'label' in f.lower()):
                            annotation_file = os.path.join(dataset_path, f)
                            break
                
                if annotation_file:
                    # Add annotation schema
                    schema["properties"]["annotations"] = {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "label": {
                                    "type": "string"
                                },
                                "bbox": {
                                    "type": "array",
                                    "items": {
                                        "type": "number"
                                    },
                                    "minItems": 4,
                                    "maxItems": 4
                                }
                            }
                        }
                    }
                
                # Save schema
                with open(schema_path, 'w') as f:
                    json.dump(schema, f, indent=2)
                
                return schema_path
            else:
                return None
        except Exception as e:
            logger.error(f"Error generating schema: {str(e)}")
            return None
    
    def _generate_tags(
        self,
        dataset_path: str,
        dataset_name: str,
        dataset_type: str,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Generate tags for a dataset.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            metadata: Dataset metadata
            
        Returns:
            List of tags
        """
        tags = []
        
        try:
            # Add dataset type tag
            tags.append(dataset_type)
            
            # Add industry tags
            for tag in self.config["industry_tags"]:
                tags.append(tag)
            
            # Add tags based on dataset name
            name_parts = dataset_name.replace('_', ' ').replace('-', ' ').lower().split()
            for part in name_parts:
                if len(part) > 3 and part not in tags:  # Avoid short words
                    tags.append(part)
            
            # Add tags based on metadata
            if dataset_type == "timeseries":
                tags.append("time-series")
                
                if "frequency" in metadata:
                    tags.append(f"freq-{metadata['frequency']}")
                
                if "value_columns" in metadata:
                    for col in metadata.get("value_columns", [])[:3]:  # Limit to first 3
                        col_tag = col.replace('_', '-').lower()
                        if col_tag not in tags:
                            tags.append(col_tag)
            
            elif dataset_type == "tabular":
                tags.append("tabular")
                
                if "num_rows" in metadata:
                    if metadata["num_rows"] < 1000:
                        tags.append("small-dataset")
                    elif metadata["num_rows"] < 100000:
                        tags.append("medium-dataset")
                    else:
                        tags.append("large-dataset")
            
            elif dataset_type == "image":
                tags.append("image")
                
                if "image_format" in metadata:
                    if isinstance(metadata["image_format"], list):
                        for fmt in metadata["image_format"]:
                            tags.append(f"format-{fmt}")
                    else:
                        tags.append(f"format-{metadata['image_format']}")
                
                if "color_mode" in metadata:
                    tags.append(f"mode-{metadata['color_mode']}")
                
                if "classes" in metadata:
                    for cls in metadata.get("classes", [])[:5]:  # Limit to first 5
                        cls_tag = cls.replace('_', '-').lower()
                        if cls_tag not in tags:
                            tags.append(cls_tag)
            
            # Limit to 20 tags
            return tags[:20]
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            return tags
    
    def _add_to_database(
        self,
        dataset_name: str,
        dataset_type: str,
        dataset_path: str,
        version: str,
        schema_path: Optional[str],
        metadata: Dict[str, Any],
        tags: List[str]
    ):
        """
        Add dataset to the database.
        
        Args:
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            dataset_path: Path to the dataset file
            version: Version of the dataset
            schema_path: Path to the schema file
            metadata: Dataset metadata
            tags: Dataset tags
        """
        if not self.conn:
            logger.warning("Database not initialized, dataset not added")
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
                    "UPDATE datasets SET type = ?, updated_at = ? WHERE id = ?",
                    (dataset_type, now, dataset_id)
                )
            else:
                # Insert new dataset
                description = metadata.get("description", "")
                owner = metadata.get("owner", "")
                source = metadata.get("source", "")
                
                self.cursor.execute(
                    "INSERT INTO datasets (name, type, description, created_at, updated_at, owner, source) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (dataset_name, dataset_type, description, now, now, owner, source)
                )
                
                dataset_id = self.cursor.lastrowid
            
            # Insert version
            self.cursor.execute(
                "INSERT INTO dataset_versions (dataset_id, version, path, created_at, schema_path) "
                "VALUES (?, ?, ?, ?, ?)",
                (dataset_id, version, dataset_path, now, schema_path)
            )
            
            # Insert metadata
            for key, value in metadata.items():
                # Skip certain keys that are stored in the datasets table
                if key in ["description", "owner", "source"]:
                    continue
                
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
            
            # Insert tags
            for tag in tags:
                # Check if tag exists
                self.cursor.execute(
                    "SELECT id FROM dataset_tags WHERE dataset_id = ? AND tag = ?",
                    (dataset_id, tag)
                )
                result = self.cursor.fetchone()
                
                if not result:
                    # Insert new tag
                    self.cursor.execute(
                        "INSERT INTO dataset_tags (dataset_id, tag) VALUES (?, ?)",
                        (dataset_id, tag)
                    )
            
            # Commit changes
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to add dataset to database: {str(e)}")
            self.conn.rollback()
    
    def _add_lineage(
        self,
        dataset_name: str,
        parent_datasets: List[Dict[str, Any]]
    ):
        """
        Add lineage information for a dataset.
        
        Args:
            dataset_name: Name of the dataset
            parent_datasets: List of parent datasets with transformation info
        """
        if not self.conn:
            logger.warning("Database not initialized, lineage not added")
            return
        
        try:
            # Get dataset ID
            self.cursor.execute(
                "SELECT id FROM datasets WHERE name = ?",
                (dataset_name,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                logger.warning(f"Dataset not found: {dataset_name}")
                return
            
            dataset_id = result[0]
            
            # Add lineage for each parent
            for parent in parent_datasets:
                parent_name = parent.get("name", "")
                transformation = parent.get("transformation", "")
                
                if not parent_name:
                    continue
                
                # Get parent dataset ID
                self.cursor.execute(
                    "SELECT id FROM datasets WHERE name = ?",
                    (parent_name,)
                )
                result = self.cursor.fetchone()
                
                if not result:
                    logger.warning(f"Parent dataset not found: {parent_name}")
                    continue
                
                parent_id = result[0]
                
                # Add lineage
                self.cursor.execute(
                    "INSERT INTO dataset_lineage (dataset_id, parent_dataset_id, transformation, created_at) "
                    "VALUES (?, ?, ?, ?)",
                    (dataset_id, parent_id, transformation, datetime.now().isoformat())
                )
            
            # Commit changes
            self.conn.commit()
            
            # Generate lineage graph
            self._generate_lineage_graph(dataset_name)
        except Exception as e:
            logger.error(f"Failed to add lineage: {str(e)}")
            self.conn.rollback()
    
    def _generate_lineage_graph(self, dataset_name: str):
        """
        Generate lineage graph for a dataset.
        
        Args:
            dataset_name: Name of the dataset
        """
        try:
            # Create lineage directory
            lineage_dir = os.path.join(self.lineage_dir, dataset_name)
            os.makedirs(lineage_dir, exist_ok=True)
            
            # Generate lineage graph path
            lineage_path = os.path.join(lineage_dir, f"{dataset_name}_lineage.json")
            
            # Get dataset ID
            self.cursor.execute(
                "SELECT id FROM datasets WHERE name = ?",
                (dataset_name,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                return
            
            dataset_id = result[0]
            
            # Get all lineage
            self.cursor.execute(
                "WITH RECURSIVE lineage_tree(id, parent_id, transformation, level) AS ("
                "  SELECT dataset_id, parent_dataset_id, transformation, 0 "
                "  FROM dataset_lineage "
                "  WHERE dataset_id = ? "
                "  UNION ALL "
                "  SELECT dl.dataset_id, dl.parent_dataset_id, dl.transformation, lt.level + 1 "
                "  FROM dataset_lineage dl "
                "  JOIN lineage_tree lt ON dl.dataset_id = lt.parent_id "
                "  WHERE lt.level < 10"  # Limit recursion depth
                ") "
                "SELECT d1.name, d2.name, lt.transformation, lt.level "
                "FROM lineage_tree lt "
                "JOIN datasets d1 ON lt.id = d1.id "
                "JOIN datasets d2 ON lt.parent_id = d2.id "
                "ORDER BY lt.level",
                (dataset_id,)
            )
            
            lineage_data = []
            for row in self.cursor.fetchall():
                dataset, parent, transformation, level = row
                lineage_data.append({
                    "dataset": dataset,
                    "parent": parent,
                    "transformation": transformation,
                    "level": level
                })
            
            # Generate graph
            graph = {
                "dataset": dataset_name,
                "generated_at": datetime.now().isoformat(),
                "lineage": lineage_data
            }
            
            # Save graph
            with open(lineage_path, 'w') as f:
                json.dump(graph, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to generate lineage graph: {str(e)}")
    
    def _generate_quality_metrics(
        self,
        dataset_path: str,
        dataset_name: str,
        dataset_type: str,
        version: str
    ):
        """
        Generate quality metrics for a dataset.
        
        Args:
            dataset_path: Path to the dataset file
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            version: Version of the dataset
        """
        if not self.conn:
            logger.warning("Database not initialized, quality metrics not generated")
            return
        
        try:
            # Get dataset ID
            self.cursor.execute(
                "SELECT id FROM datasets WHERE name = ?",
                (dataset_name,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                return
            
            dataset_id = result[0]
            
            # Generate metrics based on dataset type
            metrics = {}
            
            if dataset_type == "timeseries" or dataset_type == "tabular":
                # Load dataset
                if dataset_path.endswith('.csv'):
                    df = pd.read_csv(dataset_path)
                elif dataset_path.endswith(('.xlsx', '.xls')):
                    df = pd.read_excel(dataset_path)
                elif dataset_path.endswith('.db'):
                    conn = sqlite3.connect(dataset_path)
                    # Get first table
                    cursor = conn.cursor()
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    tables = cursor.fetchall()
                    if tables:
                        table_name = tables[0][0]
                        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                    else:
                        return
                else:
                    return
                
                # Calculate completeness (1 - percentage of missing values)
                missing_values = df.isnull().sum().sum()
                total_values = df.size
                completeness = 1.0 - (missing_values / total_values if total_values > 0 else 0)
                metrics["completeness"] = completeness
                
                # Calculate uniqueness (percentage of unique values)
                if dataset_type == "tabular":
                    unique_values = sum(df[col].nunique() for col in df.columns)
                    total_values = df.size
                    uniqueness = unique_values / total_values if total_values > 0 else 0
                    metrics["uniqueness"] = uniqueness
                
                # Calculate consistency (percentage of values within 3 standard deviations)
                if dataset_type == "timeseries":
                    consistency = 0.0
                    count = 0
                    
                    for col in df.columns:
                        if pd.api.types.is_numeric_dtype(df[col]):
                            mean = df[col].mean()
                            std = df[col].std()
                            
                            if std > 0:
                                within_3std = ((df[col] >= mean - 3 * std) & (df[col] <= mean + 3 * std)).mean()
                                consistency += within_3std
                                count += 1
                    
                    if count > 0:
                        consistency /= count
                    
                    metrics["consistency"] = consistency
            
            elif dataset_type == "image":
                # Calculate basic image metrics
                if os.path.isfile(dataset_path):
                    # Single image
                    metrics["file_exists"] = 1.0
                    
                    # Check if image can be opened
                    try:
                        from PIL import Image
                        img = Image.open(dataset_path)
                        img.verify()
                        metrics["image_validity"] = 1.0
                    except:
                        metrics["image_validity"] = 0.0
                
                elif os.path.isdir(dataset_path):
                    # Directory of images
                    image_files = [f for f in os.listdir(dataset_path) if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
                    
                    if not image_files:
                        metrics["file_exists"] = 0.0
                        metrics["image_validity"] = 0.0
                    else:
                        metrics["file_exists"] = 1.0
                        
                        # Check if images can be opened
                        valid_count = 0
                        for f in image_files[:100]:  # Limit to first 100 images
                            try:
                                from PIL import Image
                                img = Image.open(os.path.join(dataset_path, f))
                                img.verify()
                                valid_count += 1
                            except:
                                pass
                        
                        metrics["image_validity"] = valid_count / len(image_files[:100])
            
            # Add metrics to database
            now = datetime.now().isoformat()
            
            for metric, value in metrics.items():
                self.cursor.execute(
                    "INSERT INTO dataset_quality (dataset_id, version, metric, value, created_at) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (dataset_id, version, metric, value, now)
                )
            
            # Commit changes
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to generate quality metrics: {str(e)}")
            self.conn.rollback()
    
    def _update_search_index(
        self,
        dataset_name: str,
        metadata: Dict[str, Any],
        tags: List[str]
    ):
        """
        Update search index for a dataset.
        
        Args:
            dataset_name: Name of the dataset
            metadata: Dataset metadata
            tags: Dataset tags
        """
        if not self.conn or not self.config["search"]["enable_full_text_search"]:
            return
        
        try:
            # Get dataset ID
            self.cursor.execute(
                "SELECT id, type, description FROM datasets WHERE name = ?",
                (dataset_name,)
            )
            result = self.cursor.fetchone()
            
            if not result:
                return
            
            dataset_id, dataset_type, description = result
            
            # Convert tags to string
            tags_str = " ".join(tags)
            
            # Convert metadata to string
            metadata_str = ""
            for key, value in metadata.items():
                if isinstance(value, str):
                    metadata_str += f"{key}: {value} "
                elif isinstance(value, (list, dict)):
                    metadata_str += f"{key}: {json.dumps(value)} "
                else:
                    metadata_str += f"{key}: {str(value)} "
            
            # Update search index
            self.cursor.execute(
                "UPDATE dataset_search SET "
                "name = ?, description = ?, type = ?, tags = ?, metadata = ? "
                "WHERE rowid = ?",
                (dataset_name, description or "", dataset_type, tags_str, metadata_str, dataset_id)
            )
            
            # Commit changes
            self.conn.commit()
        except Exception as e:
            logger.error(f"Failed to update search index: {str(e)}")
            self.conn.rollback()
    
    def search_datasets(
        self,
        query: str,
        dataset_type: Optional[str] = None,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search for datasets.
        
        Args:
            query: Search query
            dataset_type: Filter by dataset type
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            Search results
        """
        try:
            if not self.conn:
                raise ValueError("Database not initialized")
            
            results = []
            
            if self.config["search"]["enable_full_text_search"]:
                # Use FTS virtual table
                search_query = query.replace('"', '""')  # Escape quotes
                
                if dataset_type:
                    self.cursor.execute(
                        "SELECT d.id, d.name, d.type, d.description, d.created_at, d.updated_at "
                        "FROM dataset_search s "
                        "JOIN datasets d ON s.rowid = d.id "
                        "WHERE dataset_search MATCH ? AND d.type = ? "
                        "ORDER BY rank "
                        "LIMIT ? OFFSET ?",
                        (search_query, dataset_type, limit, offset)
                    )
                else:
                    self.cursor.execute(
                        "SELECT d.id, d.name, d.type, d.description, d.created_at, d.updated_at "
                        "FROM dataset_search s "
                        "JOIN datasets d ON s.rowid = d.id "
                        "WHERE dataset_search MATCH ? "
                        "ORDER BY rank "
                        "LIMIT ? OFFSET ?",
                        (search_query, limit, offset)
                    )
            else:
                # Use LIKE queries
                search_terms = [f"%{term}%" for term in query.split()]
                
                if dataset_type:
                    for term in search_terms:
                        self.cursor.execute(
                            "SELECT id, name, type, description, created_at, updated_at "
                            "FROM datasets "
                            "WHERE (name LIKE ? OR description LIKE ?) AND type = ? "
                            "LIMIT ? OFFSET ?",
                            (term, term, dataset_type, limit, offset)
                        )
                        
                        results.extend(self.cursor.fetchall())
                else:
                    for term in search_terms:
                        self.cursor.execute(
                            "SELECT id, name, type, description, created_at, updated_at "
                            "FROM datasets "
                            "WHERE name LIKE ? OR description LIKE ? "
                            "LIMIT ? OFFSET ?",
                            (term, term, limit, offset)
                        )
                        
                        results.extend(self.cursor.fetchall())
            
            # Process results
            datasets = []
            seen_ids = set()
            
            for row in self.cursor.fetchall():
                dataset_id, name, type_, description, created_at, updated_at = row
                
                if dataset_id in seen_ids:
                    continue
                
                seen_ids.add(dataset_id)
                
                # Get tags
                self.cursor.execute(
                    "SELECT tag FROM dataset_tags WHERE dataset_id = ?",
                    (dataset_id,)
                )
                
                tags = [row[0] for row in self.cursor.fetchall()]
                
                # Get latest version
                self.cursor.execute(
                    "SELECT version, created_at FROM dataset_versions "
                    "WHERE dataset_id = ? "
                    "ORDER BY created_at DESC LIMIT 1",
                    (dataset_id,)
                )
                
                version_result = self.cursor.fetchone()
                version = version_result[0] if version_result else ""
                
                datasets.append({
                    "id": dataset_id,
                    "name": name,
                    "type": type_,
                    "description": description,
                    "created_at": created_at,
                    "updated_at": updated_at,
                    "tags": tags,
                    "latest_version": version
                })
            
            return {
                "success": True,
                "query": query,
                "results": datasets,
                "count": len(datasets)
            }
        except Exception as e:
            logger.error(f"Failed to search datasets: {str(e)}")
            return {
                "success": False,
                "query": query,
                "error": str(e)
            }
    
    def get_dataset_lineage(
        self,
        dataset_name: str
    ) -> Dict[str, Any]:
        """
        Get lineage for a dataset.
        
        Args:
            dataset_name: Name of the dataset
            
        Returns:
            Lineage information
        """
        try:
            if not self.conn:
                raise ValueError("Database not initialized")
            
            # Check if lineage graph exists
            lineage_path = os.path.join(self.lineage_dir, dataset_name, f"{dataset_name}_lineage.json")
            
            if os.path.exists(lineage_path):
                # Load existing lineage graph
                with open(lineage_path, 'r') as f:
                    lineage = json.load(f)
                
                return {
                    "success": True,
                    "dataset": dataset_name,
                    "lineage": lineage
                }
            
            # Generate lineage graph
            self._generate_lineage_graph(dataset_name)
            
            if os.path.exists(lineage_path):
                # Load generated lineage graph
                with open(lineage_path, 'r') as f:
                    lineage = json.load(f)
                
                return {
                    "success": True,
                    "dataset": dataset_name,
                    "lineage": lineage
                }
            else:
                # Get dataset ID
                self.cursor.execute(
                    "SELECT id FROM datasets WHERE name = ?",
                    (dataset_name,)
                )
                result = self.cursor.fetchone()
                
                if not result:
                    raise ValueError(f"Dataset not found: {dataset_name}")
                
                dataset_id = result[0]
                
                # Get direct lineage
                self.cursor.execute(
                    "SELECT d.name, dl.transformation "
                    "FROM dataset_lineage dl "
                    "JOIN datasets d ON dl.parent_dataset_id = d.id "
                    "WHERE dl.dataset_id = ?",
                    (dataset_id,)
                )
                
                parents = []
                for row in self.cursor.fetchall():
                    parent_name, transformation = row
                    parents.append({
                        "dataset": parent_name,
                        "transformation": transformation
                    })
                
                # Get children
                self.cursor.execute(
                    "SELECT d.name, dl.transformation "
                    "FROM dataset_lineage dl "
                    "JOIN datasets d ON dl.dataset_id = d.id "
                    "WHERE dl.parent_dataset_id = ?",
                    (dataset_id,)
                )
                
                children = []
                for row in self.cursor.fetchall():
                    child_name, transformation = row
                    children.append({
                        "dataset": child_name,
                        "transformation": transformation
                    })
                
                return {
                    "success": True,
                    "dataset": dataset_name,
                    "lineage": {
                        "parents": parents,
                        "children": children
                    }
                }
        except Exception as e:
            logger.error(f"Failed to get dataset lineage: {str(e)}")
            return {
                "success": False,
                "dataset": dataset_name,
                "error": str(e)
            }
    
    def get_catalog_strategy_for_offer(
        self,
        offer_id: str,
        dataset_name: str,
        dataset_type: str
    ) -> Dict[str, Any]:
        """
        Get catalog strategy configuration for a specific offer.
        
        Args:
            offer_id: ID of the offer
            dataset_name: Name of the dataset
            dataset_type: Type of dataset
            
        Returns:
            Catalog strategy configuration
        """
        # Map offer IDs to specific catalog configurations
        offer_mappings = {
            "predictive_maintenance": {
                "catalog_mode": "local",
                "schema_validation": True,
                "auto_tagging": True,
                "full_text_search": True,
                "lineage_tracking": True,
                "data_quality_tracking": True
            },
            "anomaly_detection": {
                "catalog_mode": "local",
                "schema_validation": True,
                "auto_tagging": True,
                "full_text_search": True,
                "lineage_tracking": True,
                "data_quality_tracking": True
            },
            "energy_optimization": {
                "catalog_mode": "local",
                "schema_validation": True,
                "auto_tagging": True,
                "full_text_search": True,
                "lineage_tracking": True,
                "data_quality_tracking": True
            },
            "quality_control": {
                "catalog_mode": "local",
                "schema_validation": True,
                "auto_tagging": True,
                "full_text_search": True,
                "lineage_tracking": True,
                "data_quality_tracking": True
            },
            "safety_monitoring": {
                "catalog_mode": "local",
                "schema_validation": True,
                "auto_tagging": True,
                "full_text_search": True,
                "lineage_tracking": True,
                "data_quality_tracking": True
            }
        }
        
        # Find matching offer prefix
        catalog_strategy = None
        for prefix, config in offer_mappings.items():
            if offer_id.startswith(prefix):
                catalog_strategy = config
                break
        
        # Use default config if no match found
        if catalog_strategy is None:
            catalog_strategy = {
                "catalog_mode": self.config["default_mode"],
                "schema_validation": self.config["metadata"]["schema_validation"],
                "auto_tagging": self.config["metadata"]["auto_tagging"],
                "full_text_search": self.config["search"]["enable_full_text_search"],
                "lineage_tracking": self.config["governance"]["enable_lineage_tracking"],
                "data_quality_tracking": self.config["governance"]["enable_data_quality_tracking"]
            }
        
        # Add metadata fields
        catalog_strategy["metadata_fields"] = self._get_metadata_fields_for_dataset_type(dataset_type)
        
        # Add governance requirements
        catalog_strategy["governance_requirements"] = self._get_governance_requirements_for_dataset_type(dataset_type)
        
        # Add metadata
        catalog_strategy["offer_id"] = offer_id
        catalog_strategy["dataset_name"] = dataset_name
        catalog_strategy["dataset_type"] = dataset_type
        catalog_strategy["created_at"] = datetime.now().isoformat()
        
        return catalog_strategy


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create data catalog system
    catalog_system = DataCatalogSystem()
    
    # Catalog a dataset
    result = catalog_system.catalog_dataset(
        dataset_name="example_dataset",
        dataset_path="path/to/dataset.csv"
    )
    
    print(f"Cataloging result: {json.dumps(result, indent=2)}")
    
    # Search datasets
    result = catalog_system.search_datasets(
        query="example"
    )
    
    print(f"Search result: {json.dumps(result, indent=2)}")
    
    # Get dataset lineage
    result = catalog_system.get_dataset_lineage(
        dataset_name="example_dataset"
    )
    
    print(f"Lineage result: {json.dumps(result, indent=2)}")
