"""
Industrial Dataset Connector Base Class for Industriverse Data Layer

This module provides the base class for all industrial dataset connectors,
implementing protocol-native ingestion with MCP/A2A support.
"""

import json
import logging
import os
import time
from typing import Dict, Any, Optional, List, Union, Callable
import pandas as pd
import numpy as np

from ..protocols.agent_core import AgentCore
from ..protocols.well_known_endpoint import WellKnownEndpoint
from ..protocols.mesh_boot_lifecycle import MeshBootLifecycle
from ..governance.secrets_manager_agent import SecretsManagerAgent

logger = logging.getLogger(__name__)

class DatasetConnectorBase(AgentCore):
    """
    Base class for all industrial dataset connectors.
    
    This class provides common functionality for dataset connectors,
    including protocol-native ingestion, validation, and transformation.
    """
    
    def __init__(
        self,
        connector_id: str,
        dataset_name: str,
        dataset_type: str,
        config: Optional[Dict[str, Any]] = None,
        secrets_manager: Optional[SecretsManagerAgent] = None,
        manifest_path: Optional[str] = None,
        base_dir: Optional[str] = None
    ):
        """
        Initialize the dataset connector.
        
        Args:
            connector_id: Unique identifier for this connector
            dataset_name: Name of the dataset
            dataset_type: Type of dataset (e.g., timeseries, image, text)
            config: Optional configuration dictionary
            secrets_manager: Optional secrets manager instance
            manifest_path: Path to the agent manifest file
            base_dir: Base directory for connector files
        """
        # Initialize agent core
        super().__init__(
            agent_id=connector_id,
            agent_type="dataset_connector",
            config=config
        )
        
        self.dataset_name = dataset_name
        self.dataset_type = dataset_type
        self.config = config or {}
        
        # Set up base directory
        if base_dir:
            self.base_dir = base_dir
        else:
            self.base_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "data"
            )
        
        # Create data directories
        self.raw_dir = os.path.join(self.base_dir, "raw", dataset_name)
        self.processed_dir = os.path.join(self.base_dir, "processed", dataset_name)
        self.metadata_dir = os.path.join(self.base_dir, "metadata", dataset_name)
        
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
        
        # Set up secrets manager
        self.secrets_manager = secrets_manager
        
        # Set up protocol components
        self.well_known = WellKnownEndpoint(
            agent_id=connector_id,
            component_name=f"{dataset_name}_connector",
            manifest_path=manifest_path
        )
        
        self.mesh_boot = MeshBootLifecycle(
            agent_id=connector_id,
            component_name=f"{dataset_name}_connector",
            on_ready_callback=self._on_connector_ready
        )
        
        # Initialize metadata
        self.metadata = {
            "connector_id": connector_id,
            "dataset_name": dataset_name,
            "dataset_type": dataset_type,
            "created_at": self._get_timestamp(),
            "updated_at": self._get_timestamp(),
            "status": "initialized",
            "statistics": {},
            "schema": {},
            "protocol_info": {
                "mcp_enabled": True,
                "a2a_enabled": True,
                "intelligence_type": "stateless",
                "industry_tags": self.config.get("industry_tags", [])
            }
        }
        
        # Save initial metadata
        self._save_metadata()
        
        logger.info(f"Initialized dataset connector for {dataset_name}")
    
    def initialize(self) -> bool:
        """
        Initialize the connector with protocol-native setup.
        
        Returns:
            True if initialization was successful, False otherwise
        """
        try:
            # Expose .well-known endpoints
            self.well_known.expose_all_endpoints()
            
            # Run mesh boot sequence
            self.mesh_boot.run_boot_sequence()
            
            # Update metadata
            self.metadata["status"] = "ready"
            self.metadata["updated_at"] = self._get_timestamp()
            self._save_metadata()
            
            logger.info(f"Initialized connector for {self.dataset_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize connector: {str(e)}")
            return False
    
    def ingest_data(
        self,
        source_path: str,
        validate: bool = True,
        transform: bool = True,
        emit_events: bool = True
    ) -> Dict[str, Any]:
        """
        Ingest data from source into the connector.
        
        Args:
            source_path: Path to the source data
            validate: Whether to validate the data
            transform: Whether to transform the data
            emit_events: Whether to emit protocol events
            
        Returns:
            Ingestion result information
        """
        try:
            # Start ingestion
            start_time = time.time()
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "ingestion_started",
                        "dataset": self.dataset_name,
                        "source": source_path
                    }
                )
            
            # Load data
            raw_data = self._load_data(source_path)
            
            # Save raw data
            raw_path = self._save_raw_data(raw_data, source_path)
            
            # Validate data if requested
            validation_result = None
            if validate:
                validation_result = self._validate_data(raw_data)
                if not validation_result["valid"]:
                    logger.warning(f"Data validation failed: {validation_result['errors']}")
                    
                    if emit_events:
                        self.emit_event(
                            event_type="observe",
                            payload={
                                "status": "validation_failed",
                                "dataset": self.dataset_name,
                                "errors": validation_result["errors"]
                            }
                        )
                    
                    return {
                        "success": False,
                        "status": "validation_failed",
                        "errors": validation_result["errors"],
                        "raw_path": raw_path,
                        "processed_path": None,
                        "duration": time.time() - start_time
                    }
            
            # Transform data if requested
            processed_data = raw_data
            processed_path = None
            if transform:
                processed_data = self._transform_data(raw_data)
                processed_path = self._save_processed_data(processed_data)
            
            # Update metadata
            self._update_statistics(raw_data, processed_data)
            self._update_schema(processed_data)
            
            # Complete ingestion
            end_time = time.time()
            duration = end_time - start_time
            
            result = {
                "success": True,
                "status": "ingestion_completed",
                "raw_path": raw_path,
                "processed_path": processed_path,
                "validation": validation_result,
                "statistics": self.metadata["statistics"],
                "duration": duration
            }
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "ingestion_completed",
                        "dataset": self.dataset_name,
                        "statistics": self.metadata["statistics"],
                        "duration": duration
                    }
                )
            
            logger.info(f"Completed ingestion for {self.dataset_name} in {duration:.2f}s")
            return result
        except Exception as e:
            logger.error(f"Failed to ingest data: {str(e)}")
            
            if emit_events:
                self.emit_event(
                    event_type="observe",
                    payload={
                        "status": "ingestion_failed",
                        "dataset": self.dataset_name,
                        "error": str(e)
                    }
                )
            
            return {
                "success": False,
                "status": "ingestion_failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get information about the dataset.
        
        Returns:
            Dataset information dictionary
        """
        return {
            "name": self.dataset_name,
            "type": self.dataset_type,
            "connector_id": self.metadata["connector_id"],
            "status": self.metadata["status"],
            "statistics": self.metadata["statistics"],
            "schema": self.metadata["schema"],
            "protocol_info": self.metadata["protocol_info"]
        }
    
    def emit_event(
        self,
        event_type: str,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Emit a protocol event.
        
        Args:
            event_type: Type of event (observe, recommend, simulate, act)
            payload: Event payload
            context: Optional event context
            
        Returns:
            The emitted event
        """
        # Create event
        event_id = f"{self.agent_id}_{event_type}_{int(time.time())}"
        event = {
            "id": event_id,
            "type": event_type,
            "source": self.agent_id,
            "payload": payload,
            "context": context or {
                "dataset": self.dataset_name,
                "dataset_type": self.dataset_type,
                "event_time": self._get_timestamp()
            }
        }
        
        # Emit event through agent core
        self.handle_event(event)
        
        return event
    
    def _load_data(self, source_path: str) -> Any:
        """
        Load data from source path.
        
        Args:
            source_path: Path to the source data
            
        Returns:
            Loaded data
        """
        # This is a base implementation that should be overridden by subclasses
        if not os.path.exists(source_path):
            raise FileNotFoundError(f"Source path not found: {source_path}")
        
        # Determine file type and load accordingly
        if source_path.endswith('.csv'):
            return pd.read_csv(source_path)
        elif source_path.endswith('.json'):
            with open(source_path, 'r') as f:
                return json.load(f)
        elif source_path.endswith('.npy'):
            return np.load(source_path)
        elif source_path.endswith('.txt'):
            with open(source_path, 'r') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
    
    def _save_raw_data(self, data: Any, source_path: str) -> str:
        """
        Save raw data to the raw directory.
        
        Args:
            data: Data to save
            source_path: Original source path
            
        Returns:
            Path to the saved raw data
        """
        # Determine filename from source path
        filename = os.path.basename(source_path)
        raw_path = os.path.join(self.raw_dir, filename)
        
        # Save based on data type
        if isinstance(data, pd.DataFrame):
            if filename.endswith('.csv'):
                data.to_csv(raw_path, index=False)
            else:
                data.to_csv(raw_path, index=False)
        elif isinstance(data, (dict, list)):
            with open(raw_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif isinstance(data, np.ndarray):
            np.save(raw_path, data)
        elif isinstance(data, str):
            with open(raw_path, 'w') as f:
                f.write(data)
        else:
            # For other types, save as pickle
            import pickle
            with open(raw_path, 'wb') as f:
                pickle.dump(data, f)
        
        logger.info(f"Saved raw data to {raw_path}")
        return raw_path
    
    def _validate_data(self, data: Any) -> Dict[str, Any]:
        """
        Validate the data.
        
        Args:
            data: Data to validate
            
        Returns:
            Validation result
        """
        # This is a base implementation that should be overridden by subclasses
        # Default implementation performs basic validation
        
        errors = []
        
        # Check if data is empty
        if isinstance(data, pd.DataFrame):
            if data.empty:
                errors.append("DataFrame is empty")
            
            # Check for missing values
            missing_count = data.isna().sum().sum()
            if missing_count > 0:
                errors.append(f"Data contains {missing_count} missing values")
        elif isinstance(data, (list, dict)):
            if not data:
                errors.append("Data is empty")
        elif isinstance(data, np.ndarray):
            if data.size == 0:
                errors.append("Array is empty")
            
            # Check for NaN values
            if np.issubdtype(data.dtype, np.number) and np.isnan(data).any():
                errors.append("Array contains NaN values")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _transform_data(self, data: Any) -> Any:
        """
        Transform the data.
        
        Args:
            data: Data to transform
            
        Returns:
            Transformed data
        """
        # This is a base implementation that should be overridden by subclasses
        # Default implementation returns the data unchanged
        return data
    
    def _save_processed_data(self, data: Any) -> str:
        """
        Save processed data to the processed directory.
        
        Args:
            data: Data to save
            
        Returns:
            Path to the saved processed data
        """
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        if isinstance(data, pd.DataFrame):
            filename = f"{self.dataset_name}_processed_{timestamp}.csv"
            processed_path = os.path.join(self.processed_dir, filename)
            data.to_csv(processed_path, index=False)
        elif isinstance(data, (dict, list)):
            filename = f"{self.dataset_name}_processed_{timestamp}.json"
            processed_path = os.path.join(self.processed_dir, filename)
            with open(processed_path, 'w') as f:
                json.dump(data, f, indent=2)
        elif isinstance(data, np.ndarray):
            filename = f"{self.dataset_name}_processed_{timestamp}.npy"
            processed_path = os.path.join(self.processed_dir, filename)
            np.save(processed_path, data)
        elif isinstance(data, str):
            filename = f"{self.dataset_name}_processed_{timestamp}.txt"
            processed_path = os.path.join(self.processed_dir, filename)
            with open(processed_path, 'w') as f:
                f.write(data)
        else:
            # For other types, save as pickle
            import pickle
            filename = f"{self.dataset_name}_processed_{timestamp}.pkl"
            processed_path = os.path.join(self.processed_dir, filename)
            with open(processed_path, 'wb') as f:
                pickle.dump(data, f)
        
        logger.info(f"Saved processed data to {processed_path}")
        return processed_path
    
    def _update_statistics(self, raw_data: Any, processed_data: Any) -> None:
        """
        Update dataset statistics in metadata.
        
        Args:
            raw_data: Raw data
            processed_data: Processed data
        """
        stats = {}
        
        # Calculate statistics based on data type
        if isinstance(processed_data, pd.DataFrame):
            stats["row_count"] = len(processed_data)
            stats["column_count"] = len(processed_data.columns)
            stats["columns"] = list(processed_data.columns)
            
            # Calculate numeric column statistics
            numeric_stats = {}
            for col in processed_data.select_dtypes(include=[np.number]).columns:
                col_stats = {
                    "min": float(processed_data[col].min()),
                    "max": float(processed_data[col].max()),
                    "mean": float(processed_data[col].mean()),
                    "median": float(processed_data[col].median()),
                    "std": float(processed_data[col].std())
                }
                numeric_stats[col] = col_stats
            
            stats["numeric_stats"] = numeric_stats
            
            # Calculate categorical column statistics
            categorical_stats = {}
            for col in processed_data.select_dtypes(include=["object", "category"]).columns:
                value_counts = processed_data[col].value_counts().to_dict()
                unique_count = len(value_counts)
                
                col_stats = {
                    "unique_count": unique_count,
                    "top_values": dict(list(value_counts.items())[:5])
                }
                categorical_stats[col] = col_stats
            
            stats["categorical_stats"] = categorical_stats
        elif isinstance(processed_data, np.ndarray):
            stats["shape"] = processed_data.shape
            stats["dtype"] = str(processed_data.dtype)
            
            if np.issubdtype(processed_data.dtype, np.number):
                stats["min"] = float(np.min(processed_data))
                stats["max"] = float(np.max(processed_data))
                stats["mean"] = float(np.mean(processed_data))
                stats["std"] = float(np.std(processed_data))
        elif isinstance(processed_data, (list, dict)):
            if isinstance(processed_data, list):
                stats["count"] = len(processed_data)
                
                # Sample statistics for list of dictionaries
                if processed_data and isinstance(processed_data[0], dict):
                    sample_keys = list(processed_data[0].keys())
                    stats["sample_keys"] = sample_keys
            else:
                stats["key_count"] = len(processed_data)
                stats["keys"] = list(processed_data.keys())
        
        # Update metadata
        self.metadata["statistics"] = stats
        self.metadata["updated_at"] = self._get_timestamp()
        self._save_metadata()
    
    def _update_schema(self, data: Any) -> None:
        """
        Update dataset schema in metadata.
        
        Args:
            data: Data to extract schema from
        """
        schema = {}
        
        # Extract schema based on data type
        if isinstance(data, pd.DataFrame):
            for col in data.columns:
                col_type = str(data[col].dtype)
                
                # Map pandas dtypes to more general types
                if col_type.startswith("int"):
                    schema_type = "integer"
                elif col_type.startswith("float"):
                    schema_type = "number"
                elif col_type == "bool":
                    schema_type = "boolean"
                elif col_type == "datetime64[ns]":
                    schema_type = "datetime"
                else:
                    schema_type = "string"
                
                schema[col] = {
                    "type": schema_type,
                    "nullable": data[col].isna().any()
                }
        elif isinstance(data, np.ndarray):
            schema["type"] = "array"
            schema["shape"] = list(data.shape)
            schema["dtype"] = str(data.dtype)
        elif isinstance(data, list):
            schema["type"] = "array"
            schema["length"] = len(data)
            
            # Sample item schema for list of dictionaries
            if data and isinstance(data[0], dict):
                item_schema = {}
                for key, value in data[0].items():
                    item_schema[key] = {
                        "type": type(value).__name__
                    }
                schema["items"] = item_schema
        elif isinstance(data, dict):
            schema["type"] = "object"
            
            # Extract property schemas
            properties = {}
            for key, value in data.items():
                properties[key] = {
                    "type": type(value).__name__
                }
            schema["properties"] = properties
        
        # Update metadata
        self.metadata["schema"] = schema
        self.metadata["updated_at"] = self._get_timestamp()
        self._save_metadata()
    
    def _save_metadata(self) -> None:
        """
        Save metadata to file.
        """
        metadata_path = os.path.join(self.metadata_dir, "metadata.json")
        try:
            with open(metadata_path, 'w') as f:
                json.dump(self.metadata, f, indent=2)
            logger.info(f"Saved metadata to {metadata_path}")
        except Exception as e:
            logger.error(f"Failed to save metadata: {str(e)}")
    
    def _on_connector_ready(self) -> None:
        """
        Callback function when connector is ready.
        """
        logger.info(f"Connector {self.dataset_name} is ready")
        
        # Emit ready event
        self.emit_event(
            event_type="observe",
            payload={
                "status": "connector_ready",
                "dataset": self.dataset_name,
                "connector_id": self.agent_id
            }
        )
    
    def _get_timestamp(self) -> str:
        """
        Get the current timestamp in ISO format.
        
        Returns:
            Current timestamp string
        """
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# Example usage
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create dataset connector
    connector = DatasetConnectorBase(
        connector_id="example-connector",
        dataset_name="example_dataset",
        dataset_type="timeseries"
    )
    
    # Initialize connector
    connector.initialize()
    
    # Ingest data
    result = connector.ingest_data(
        source_path="path/to/data.csv",
        validate=True,
        transform=True
    )
    
    print(f"Ingestion result: {json.dumps(result, indent=2)}")
